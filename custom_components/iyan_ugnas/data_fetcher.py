from __future__ import annotations
import logging
import json
import datetime
from typing import Any, Dict, List, Tuple, Callable, Optional
from urllib.parse import urljoin, urlencode
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import asyncio  # 确保这行存在

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import (
    LOGIN_URL,
    SYS_INFO,
    CPU_INFO,
    DISK_INFO,
    STORAGES_INFO,
    STATUS_INFO,
    STATUS_CPU_INFO,
    STATUS_HARDDISK_INFO,
    STATUS_HARDDISK_TEMP_INFO,
    STATUS_NETWORK_INFO,
    SWITCH_TYPES,
    CHECK_OFFLINE,
    GET_OFFLINE,
)

_LOGGER = logging.getLogger(__name__)


class DataFetcher:
    """Fetch iYan-UGNas device data with robust error handling and async support."""

    def __init__(self, hass: HomeAssistant, host: str, port: str, username: str, passwd: str) -> None:
        self._hass = hass
        self._host = host
        self._port = port
        self._username = username
        self._passwd = passwd
        self._session_client = async_create_clientsession(hass)  # 保留aiohttp客户端（未来可迁移）
        self._data: Dict[str, Any] = {}
        self._datatracker: Dict[str, Any] = {}
        self._datarefreshtimes: Dict[str, Any] = {}

        # 统一请求头
        self._headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36",
        }

        # 初始化带重试的requests会话（解决临时网络问题）
        self._requests_session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self._requests_session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self._requests_session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    @staticmethod
    def is_json(json_str: str) -> bool:
        """Check if a string is valid JSON."""
        try:
            json.loads(json_str)
            return True
        except ValueError:
            return False

    def _build_url(self, path: str, params: Optional[Dict[str, str]] = None) -> str:
        """Build a valid URL with proper path joining and parameter encoding."""
        # 清理host中的协议前缀（如http://、https://）
        cleaned_host = self._host.strip()
        for proto in ["http://", "https://"]:
            if cleaned_host.startswith(proto):
                cleaned_host = cleaned_host[len(proto):]
        
        # 构建基础URL（确保不重复添加协议）
        base_url = f"http://{cleaned_host}:{self._port}"  # 若设备支持HTTPS，可改为https
        full_path = urljoin(base_url, path)
        
        if params:
            full_path += "?" + urlencode(params)
        
        # 调试日志：输出最终构建的URL，帮助排查问题
        _LOGGER.debug(f"Built URL: {full_path}")
        return full_path

    def _sync_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        verify_ssl: bool = False  # 允许配置SSL验证（默认保持原有行为）
    ) -> Any:
        """Unified synchronous request handler with error handling."""
        try:
            # 设置超时（避免请求无限挂起）
            timeout_seconds = 10
            kwargs = {
                "headers": headers or self._headers,
                "timeout": timeout_seconds,
                "verify": verify_ssl
            }

            if method.lower() == "get":
                response = self._requests_session.get(url, **kwargs)
            elif method.lower() == "post":
                if json_body:
                    kwargs["json"] = json_body
                else:
                    kwargs["data"] = data
                response = self._requests_session.post(url,** kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # 触发4xx/5xx状态码异常
            content = response.content.decode("utf-8")

            if self.is_json(content):
                return json.loads(content)
            return content

        except requests.exceptions.HTTPError as e:
            _LOGGER.error(f"HTTP error {e.response.status_code} for URL: {url}")
            raise UpdateFailed(f"HTTP error: {str(e)}") from e
        except requests.exceptions.Timeout:
            _LOGGER.error(f"Request timed out for URL: {url}")
            raise UpdateFailed(f"Request timed out after {timeout_seconds}s")
        except Exception as e:
            _LOGGER.error(f"Request failed for URL {url}: {str(e)}")
            raise UpdateFailed(f"Request failed: {str(e)}") from e

    async def _async_fetch(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        method: str = "get",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        process_func: Optional[Callable[[Any], None]] = None
    ) -> Any:
        """Async wrapper for sync requests with timeout and result processing."""
        url = self._build_url(path, params)
        _LOGGER.debug(f"Fetching data from: {url}")

        try:
            async with timeout(15):  # 总超时（含重试）
                # 同步请求放入线程池执行
                response_data = await self._hass.async_add_executor_job(
                    self._sync_request,
                    method,
                    url,
                    headers,
                    data,
                    json_body
                )

            # 执行数据处理函数（如解析并更新_data）
            if process_func:
                process_func(response_data)
            return response_data

        except ClientConnectorError as e:
            raise UpdateFailed(f"Connection failed to {url}: {str(e)}") from e
        except Exception as e:
            raise UpdateFailed(f"Failed to fetch {url}: {str(e)}") from e

    async def _login_offlineLogin(self) -> str:
        """Login and return API token."""
        login_params = {
            "platform": 0,
            "offline_username": self._username,
            "offline_password": self._passwd
        }
        response_data = await self._async_fetch(
            path=LOGIN_URL,
            method="post",
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json_body=login_params
        )

        if not isinstance(response_data, dict) or response_data.get("code") != 200:
            raise UpdateFailed("Login failed: Invalid credentials or response")

        api_token = response_data["data"].get("api_token", "")
        if not api_token:
            raise UpdateFailed("Login failed: No API token received")
        return api_token

    # ------------------------------
    # 数据处理函数（分离请求与处理逻辑）
    # ------------------------------
    def _process_sys_info(self, response_data: Dict[str, Any]) -> None:
        """Process system info response into _data."""
        data = response_data.get("data", {})
        self._data.update({
            "auto_time": data.get("auto_time"),
            "auto_timezone": data.get("auto_timezone"),
            "boot_time": str(data.get("boot_time", "")),
            "build_date": data.get("build_date"),
            "build_utc": data.get("build_utc"),
            "cpu": data.get("cpu"),
            "device_id": data.get("device_id"),
            "device_name": data.get("device_name"),
            "firmware_ver": data.get("firmware_ver"),
            "language": data.get("language"),
            "mac1": data.get("mac"),
            "mac2": data.get("mac2"),
            "memory": data.get("memory"),
            "model": data.get("model"),
            "nas_server_ver": data.get("nas_server_ver"),
            "nas_server_ver_no": data.get("nas_server_ver_no"),
            "sn": data.get("sn"),
            "time": data.get("time"),
            "timezone": data.get("timezone"),
            "wifi_mac": data.get("wifi_mac"),
            "fan_mode": str(data.get("fan_mode", "")),
            "indicator_light": "on" if data.get("indicator_light") == 1 else "off",
            "power_on_automatically": str(data.get("power_on_automatically", "")),
            "webui_ver": str(data.get("webui_ver", "")),
            "weblauncher_ver": data.get("weblauncher_ver"),
            "bios_ver": str(data.get("bios_ver", "")),
            "querytime": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })

    def _process_cpu_info(self, response_data: Dict[str, Any]) -> None:
        """Process CPU info response into _data."""
        cpu_data = response_data.get("data", {}).get("cpu", {})
        self._data.update({
            "cpu_used": str(cpu_data.get("cpu_used", "")),
            "querytime": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })

    def _process_disks_info(self, response_data: Dict[str, Any]) -> None:
        """Process disks info response into _data."""
        disks = response_data.get("data", {}).get("disks", [])
        hard_disk_type = ["", "", "", "HDD", "", "外置硬盘", "", "", "SSD"]
        hard_disk_smart_status = ["不支持", "良好", "警告", "危险", "未检测"]
        hard_disk_status = [
            "正常", "未初始化", "已经初始化,正在同步", 
            "该磁盘正在重建，正在从主盘上获取数据", "该磁盘正在格式化或者切换工作模式",
            "正在检测磁盘状态", "外置磁盘/usb设备正在进行弹出操作", 
            "外置磁盘/usb设备弹出操作失败", "作为缓存使用"
        ]

        for idx, disk in enumerate(disks, 1):
            disk_key = f"disk{idx}_"
            size = disk.get("size", 0)
            converted_size = self.convert_size(size)
            
            self._data.update({
                f"{disk_key}ihmStatus": disk.get("ihmStatus"),
                f"{disk_key}interface": disk.get("interface"),
                f"{disk_key}model": disk.get("model"),
                f"{disk_key}serial": disk.get("serial"),
                f"{disk_key}status": hard_disk_status[disk.get("status", 0)],
                f"{disk_key}temp": disk.get("temp"),
                f"{disk_key}time": disk.get("time"),
                f"{disk_key}type": hard_disk_type[disk.get("type", 0) - 1],
                f"{disk_key}size": converted_size[0],
                f"{disk_key}size_attrs": {"unit_of_measurement": converted_size[1]},
                f"{disk_key}stpower": "运行" if disk.get("st_power") == 0 else "休眠",
                f"{disk_key}smartStatus": hard_disk_smart_status[disk.get("smartStatus", 0)]
            })

        self._data["querytime"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _process_storages_info(self, response_data: Dict[str, Any]) -> None:
        """Process storages info response into _data."""
        storages = response_data.get("data", {}).get("storages", [])
        hard_disk_type = ["", "", "", "", "HDD", "", "外置硬盘", "", "", "SSD"]

        for idx, storage in enumerate(storages, 1):
            storage_key = f"storage{idx}_"
            
            if "label" in storage:
                self._data[f"{storage_key}label"] = storage["label"]
            if "host" in storage:
                self._data[f"{storage_key}host"] = storage["host"]
            if "mode" in storage:
                self._data[f"{storage_key}mode"] = storage["mode"]
            if "name" in storage:
                self._data[f"{storage_key}name"] = storage["name"]
            
            # 处理存储大小
            if "size" in storage:
                size = self.convert_size(storage["size"])
                self._data[f"{storage_key}size"] = size[0]
                self._data[f"{storage_key}size_attrs"] = {"unit_of_measurement": size[1]}
            
            # 处理已使用空间
            if "used" in storage:
                used = self.convert_size(storage["used"])
                self._data[f"{storage_key}used"] = used[0]
                self._data[f"{storage_key}used_attrs"] = {"unit_of_measurement": used[1]}
                
                # 额外计算GB/TB（优化精度）
                used_bytes = storage["used"]
                self._data[f"{storage_key}used_gb"] = round(used_bytes / (1024 ** 3), 2)
                self._data[f"{storage_key}used_gb_attrs"] = {"unit_of_measurement": "GB"}
                self._data[f"{storage_key}used_tb"] = round(used_bytes / (1024 **4), 2)
                self._data[f"{storage_key}used_tb_attrs"] = {"unit_of_measurement": "TB"}
            
            if "type" in storage:
                self._data[f"{storage_key}type"] = hard_disk_type[storage["type"]]
            if "status" in storage:
                self._data[f"{storage_key}status"] = storage["status"]
            if "lifetime" in storage:
                self._data[f"{storage_key}lifetime"] = storage["lifetime"]

        self._data["querytime"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _process_status_info(self, response_data: Dict[str, Any]) -> None:
        """Process status info response into _data."""
        data = response_data.get("data", {})
        cpu_data = data.get("cpu", {})
        memory_data = data.get("memory", {})
        fan_data = data.get("fan", {})
        swap_data = data.get("swap", {})

        # CPU温度
        self._data["cpu_temp"] = cpu_data.get("cpu_temp")
        
        # 内存信息
        self._data["memory_used"] = memory_data.get("mem_used")
        
        # 内存大小转换（复用逻辑）
        def convert_memory(key: str) -> Tuple[str, Dict[str, str]]:
            value = memory_data.get(key, 0)
            converted = self.convert_size(value)
            return converted[0], {"unit_of_measurement": converted[1]}
        
        self._data["memory_used_size"], self._data["memory_used_size_attrs"] = convert_memory("mem_used_size")
        self._data["memory_total"], self._data["memory_total_attrs"] = convert_memory("mem_total")
        self._data["memory_size"] = memory_data.get("mem_size")
        
        # 风扇信息
        self._data["fan_speed"] = fan_data.get("fan_speed")
        self._data["cpu_fan_speed"] = fan_data.get("cpu_fan_speed")
        self._data["board_fan_speed"] = fan_data.get("board_fan_speed")
        
        # 交换分区信息
        self._data["swap_total"] = swap_data.get("swap_total")
        self._data["swap_used"] = swap_data.get("swap_used")

        self._data["querytime"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _process_harddisk_info(self, temp_data: Dict[str, Any], speed_data: Dict[str, Any]) -> None:
        """Process harddisk temperature and speed info into _data."""
        # 处理硬盘温度和基本信息
        harddisks = temp_data.get("data", {}).get("harddisk", [])
        for idx, disk in enumerate(harddisks, 1):
            disk_key = f"disk{idx}_"
            self._data.update({
                f"{disk_key}interface": disk.get("interface"),
                f"{disk_key}diskplace": disk.get("disk_place"),
                f"{disk_key}disktemp": disk.get("disk_temp")
            })

        # 处理硬盘读写速度
        harddisks_speed = speed_data.get("data", {}).get("harddisk", [])
        for idx, disk in enumerate(harddisks_speed, 1):
            disk_key = f"disk{idx}_"
            read_speed = self.convert_speed(disk.get("read_speed", 0))
            write_speed = self.convert_speed(disk.get("write_speed", 0))
            self._data.update({
                f"{disk_key}readspeed": read_speed[0],
                f"{disk_key}readspeed_attrs": {"unit_of_measurement": read_speed[1]},
                f"{disk_key}writespeed": write_speed[0],
                f"{disk_key}writespeed_attrs": {"unit_of_measurement": write_speed[1]},
                f"{disk_key}checkstatus": disk.get("check_status"),
                f"{disk_key}diskplace": f"第{disk.get('disk_place', '')}槽位"
            })

        # 处理SSD信息（若存在）
        ssds_temp = temp_data.get("data", {}).get("ssd", [])
        ssds_speed = speed_data.get("data", {}).get("ssd", [])
        if ssds_temp and ssds_speed:
            diskname = self.checkvalue(self._data, "nvme1")  # 复用原有逻辑
            for idx, (ssd_temp, ssd_speed) in enumerate(zip(ssds_temp, ssds_speed), 1):
                ssd_key = f"{diskname}_" if idx == 1 else f"{diskname}{idx}_"
                read_speed = self.convert_speed(ssd_speed.get("read_speed", 0))
                write_speed = self.convert_speed(ssd_speed.get("write_speed", 0))
                self._data.update({
                    f"{ssd_key}interface": ssd_temp.get("interface"),
                    f"{ssd_key}diskplace": ssd_temp.get("disk_place"),
                    f"{ssd_key}disktemp": ssd_temp.get("disk_temp"),
                    f"{ssd_key}readspeed": read_speed[0],
                    f"{ssd_key}readspeed_attrs": {"unit_of_measurement": read_speed[1]},
                    f"{ssd_key}writespeed": write_speed[0],
                    f"{ssd_key}writespeed_attrs": {"unit_of_measurement": write_speed[1]},
                    f"{ssd_key}checkstatus": ssd_speed.get("check_status"),
                    f"{ssd_key}diskplace": f"第{ssd_speed.get('disk_place', '')}槽位"
                })

        self._data["querytime"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _process_network_info(self, response_data: Dict[str, Any]) -> None:
        """Process network info response into _data."""
        network_data = response_data.get("data", {}).get("network", {})
        upload_speed = self.convert_speed(network_data.get("upload_speed", 0))
        download_speed = self.convert_speed(network_data.get("download_speed", 0))
        
        self._data.update({
            "upload_speed": upload_speed[0],
            "upload_speed_attrs": {"unit_of_measurement": upload_speed[1]},
            "download_speed": download_speed[0],
            "download_speed_attrs": {"unit_of_measurement": download_speed[1]},
            "querytime": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        })

    async def _get_harddisk_info(self, token: str) -> None:
        """Fetch and process harddisk info (temp + speed)."""
        # 并行获取温度和速度数据
        temp_data, speed_data = await asyncio.gather(
            self._async_fetch(STATUS_HARDDISK_TEMP_INFO, params={"api_token": token}),
            self._async_fetch(STATUS_HARDDISK_INFO, params={"api_token": token})
        )
        self._process_harddisk_info(temp_data, speed_data)

    async def _get_ugreen_switch(self, token: str, switch: Dict[str, Any]) -> None:
        """Fetch and process switch status."""
        url_path = switch["show_url"].replace("{api_token}", token)
        response_data = await self._async_fetch(url_path)

        # 处理会话超时
        if response_data.get("code") == 8013:
            _LOGGER.error(f"Switch {switch['name']} error: {response_data.get('msg')}")
            return

        # 解析开关状态
        try:
            body_path = switch["show_body"].split(".")
            status_value = response_data[body_path[0]][body_path[1]]
            is_on = str(status_value) == str(switch["turn_on_body"])
            self._data["switch"].append({"name": switch["name"], "onoff": "on" if is_on else "off"})
        except (KeyError, IndexError) as e:
            _LOGGER.warning(f"Failed to parse switch {switch['name']} status: {str(e)}")

    # ------------------------------
    # 公共工具方法
    # ------------------------------
    def checkvalue(self, myjson: Dict[str, Any], value: str) -> str:
        """Find key prefix by value (保留原有逻辑，优化变量名)."""
        target_index = -1
        for idx, val in enumerate(myjson.values()):
            if val == value:
                target_index = idx
                break
        if target_index == -1:
            return ""
        
        for idx, key in enumerate(myjson.keys()):
            if idx == target_index:
                return key[:key.find("_")]
        return ""

    @staticmethod
    def seconds_to_dhms(seconds: int) -> str:
        """Convert seconds to days/hours/minutes/seconds string."""
        days = seconds // (3600 * 24)
        hours = (seconds // 3600) % 24
        minutes = (seconds // 60) % 60
        seconds = seconds % 60

        if days > 0:
            return f"{days}天{hours}小时{minutes}分钟"
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        if minutes > 0:
            return f"{minutes}分钟{seconds}秒"
        return f"{seconds}秒"

    @staticmethod
    def convert_size(size_bytes: Any) -> Tuple[str, str]:
        """Convert bytes to human-readable size."""
        try:
            size = int(size_bytes)
        except (TypeError, ValueError):
            return "0.00", "B"

        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f"{size:.2f}", units[index]

    @staticmethod
    def convert_speed(speed: Any) -> Tuple[str, str]:
        """Convert bytes/second to human-readable speed."""
        try:
            speed_val = float(speed)
        except (TypeError, ValueError):
            return "0.00", "B/s"

        units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s"]
        index = 0
        while speed_val >= 1024 and index < len(units) - 1:
            speed_val /= 1024
            index += 1
        return f"{speed_val:.2f}", units[index]

    # ------------------------------
    # 主数据获取入口
    # ------------------------------
    async def get_data(self, token: str) -> Dict[str, Any]:
        """Fetch all device data and return merged result."""
        self._data = {}  # 重置数据存储

        # 分阶段并行获取数据（减少总耗时）
        # 第一阶段：系统信息（基础数据）
        await self._async_fetch(SYS_INFO, params={"api_token": token}, process_func=self._process_sys_info)

        # 第二阶段：并行获取其他核心数据
        await asyncio.gather(
            self._async_fetch(CPU_INFO, params={"api_token": token}, process_func=self._process_cpu_info),
            self._async_fetch(DISK_INFO, params={"api_token": token}, process_func=self._process_disks_info),
            self._async_fetch(STORAGES_INFO, params={"api_token": token}, process_func=self._process_storages_info),
            self._async_fetch(STATUS_INFO, params={"api_token": token}, process_func=self._process_status_info),
            self._get_harddisk_info(token),
            self._async_fetch(STATUS_NETWORK_INFO, params={"api_token": token}, process_func=self._process_network_info)
        )

        # 第三阶段：获取开关状态
        self._data["switch"] = []
        switch_tasks = [
            self._get_ugreen_switch(token, switch)
            for switch in SWITCH_TYPES.values()
        ]
        await asyncio.gather(*switch_tasks)

        _LOGGER.debug("Fetched all data: %s", self._data)
        return self._data


class GetDataError(Exception):
    """Raised when data fetching fails or response is invalid."""