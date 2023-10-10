"""
get iYan_UGNas info by token
"""

import logging
import requests
import re
import asyncio
import json
import time
import datetime
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

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
    """fetch the iYan-UGNas data"""

    def __init__(self, hass: HomeAssistant, host: str, port: str, username: str, passwd: str) -> None:
        self._host = host
        self._username = username
        self._passwd = passwd
        self._hass = hass
        self._port = port
        self._session_client = async_create_clientsession(hass)
        self._data = {}
        self._datatracker = {}
        self._datarefreshtimes = {}

        self._header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36",
        }

    def is_json(self, jsonstr):
        try:
            json.loads(jsonstr)
        except ValueError:
            return False
        return True

    def requestget_data(self, url, headerstr):
        responsedata = requests.get(url, headers=headerstr)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode("utf-8")
        if self.is_json(json_text):
            resdata = json.loads(json_text)
        else:
            resdata = json_text
        return resdata

    def requestpost_data(self, url, headerstr, datastr):
        responsedata = requests.post(url, headers=headerstr, data=datastr, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode("utf-8")
        if self.is_json(json_text):
            resdata = json.loads(json_text)
        else:
            resdata = json_text
        return resdata

    def requestpost_json(self, url, headerstr, json_body):
        responsedata = requests.post(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        _LOGGER.debug(responsedata)
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode("utf-8")
        if self.is_json(json_text):
            resdata = json.loads(json_text)
        else:
            resdata = json_text
        return resdata

    def requestpost_cookies(self, url, headerstr, json_body):
        responsedata = requests.post(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        resdata = responsedata.cookies["sess_key"]
        return resdata

    def requestpost_token(self, url, headerstr, json_body):
        responsedata = requests.post(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        if responsedata.json()["code"] == 200:
            api_token = responsedata.json()["data"]["api_token"]
            refresh_token = responsedata.json()["data"]["refresh_token"]
        else:
            api_token = ""
            refresh_token = ""
        return [api_token, refresh_token]

    async def _login_offlineLogin(self):
        hass = self._hass
        host = self._host
        port = self._port
        username = self._username
        passwd = self._passwd
        header = {"Content-Type": "application/json;charset=UTF-8"}
        json_body = {
            "platform": 0,
            "offline_username": username,
            "offline_password": passwd
        }
        url = host + ":" + port + LOGIN_URL

        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestpost_token, url, header, json_body)
                _LOGGER.debug(resdata)  # list [api_token, refresh_token]
                # if isinstance(resdata, list):
                #     _LOGGER.debug("UGNas Username or Password is wrong，please reconfig!")
                #     return 8066
                # else:
                #     _LOGGER.debug("login_successfully for UGNas")
        except ClientConnectorError as error:
            raise UpdateFailed(error)

        return resdata[0]

    async def _get_sys_info(self, token):
        url = self._host + ":" + self._port + SYS_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        self._data = {}

        self._data["auto_time"] = resdata["data"]["auto_time"]
        self._data["auto_timezone"] = resdata["data"]["auto_timezone"]
        self._data["boot_time"] = str(resdata["data"]["boot_time"])
        self._data["build_date"] = resdata["data"]["build_date"]
        self._data["build_utc"] = resdata["data"]["build_utc"]
        self._data["cpu"] = resdata["data"]["cpu"]
        self._data["device_id"] = resdata["data"]["device_id"]
        self._data["device_name"] = resdata["data"]["device_name"]
        self._data["firmware_ver"] = resdata["data"]["firmware_ver"]
        self._data["language"] = resdata["data"]["language"]
        self._data["mac1"] = resdata["data"]["mac"]
        self._data["mac2"] = resdata["data"]["mac2"]
        self._data["memory"] = resdata["data"]["memory"]
        self._data["model"] = resdata["data"]["model"]
        self._data["nas_server_ver"] = resdata["data"]["nas_server_ver"]
        self._data["nas_server_ver_no"] = resdata["data"]["nas_server_ver_no"]
        self._data["sn"] = resdata["data"]["sn"]
        self._data["time"] = resdata["data"]["time"]
        self._data["timezone"] = resdata["data"]["timezone"]
        self._data["wifi_mac"] = resdata["data"]["wifi_mac"]
        self._data["fan_mode"] = str(resdata["data"]["fan_mode"])
        self._data["indicator_light"] = "on" if resdata["data"]["indicator_light"] == 1 else "off"
        self._data["power_on_automatically"] = str(resdata["data"]["power_on_automatically"])
        self._data["webui_ver"] = resdata["data"]["webui_ver"]
        self._data["weblauncher_ver"] = resdata["data"]["weblauncher_ver"]
        self._data["bios_ver"] = str(resdata["data"]["bios_ver"])

        self._data["firmware_ver"] = resdata["data"]["firmware_ver"]
        self._data["webui_ver"] = str(resdata["data"]["webui_ver"])
        self._data["bios_ver"] = str(resdata["data"]["bios_ver"])

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_cpu_info(self, token):
        url = self._host + ":" + self._port + CPU_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        self._data["cpu_used"] = str(resdata["data"]["cpu"]["cpu_used"])

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_disks_info(self, token):
        url = self._host + ":" + self._port + DISK_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        diskNums = len(resdata["data"]["disks"])
        HardDisk_Type = ["", "", "", "HDD", "", "外置硬盘", "", "", "SSD"]
        HardDisk_smartStatus = ["不支持", "良好", "警告", "危险", "未检测"]
        HardDisk_Status = ["正常", "未初始化", "已经初始化,正在同步", "该磁盘正在重建，正在从主盘上获取数据", "该磁盘正在格式化或者切换工作模式", "正在检测磁盘状态", "外置磁盘/usb设备正在进行弹出操作", "外置磁盘/usb设备弹出操作失败", "作为缓存使用"]

        for diskNum in range(1, diskNums+1):
            self._data["disk" + str(diskNum) + "_" + "ihmStatus"] = resdata["data"]["disks"][diskNum-1]["ihmStatus"]
            self._data["disk" + str(diskNum) + "_" + "interface"] = resdata["data"]["disks"][diskNum-1]["interface"]
            self._data["disk" + str(diskNum) + "_" + "model"] = resdata["data"]["disks"][diskNum-1]["model"]
            self._data["disk" + str(diskNum) + "_" + "serial"] = resdata["data"]["disks"][diskNum-1]["serial"]
            self._data["disk" + str(diskNum) + "_" + "status"] = HardDisk_Status[resdata["data"]["disks"][diskNum-1]["status"]]
            self._data["disk" + str(diskNum) + "_" + "temp"] = resdata["data"]["disks"][diskNum-1]["temp"]
            self._data["disk" + str(diskNum) + "_" + "time"] = resdata["data"]["disks"][diskNum-1]["time"]
            self._data["disk" + str(diskNum) + "_" + "type"] = HardDisk_Type[resdata["data"]["disks"][diskNum-1]["type"]-1]

            sizes = self.convert_size(resdata["data"]["disks"][diskNum-1]["size"])
            self._data["disk" + str(diskNum) + "_" + "size"] = sizes[0]
            self._data["disk" + str(diskNum) + "_" + "size_attrs"] = {"unit_of_measurement": sizes[1]}
            # st_power
            self._data["disk" + str(diskNum) + "_" + "stpower"] = "运行" if (resdata["data"]["disks"][diskNum-1].get("st_power") == 0) else "休眠"
            # smartStatus
            self._data["disk" + str(diskNum) + "_" + "smartStatus"] = HardDisk_smartStatus[resdata["data"]["disks"][diskNum-1]["smartStatus"]]

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_storages_info(self, token):
        url = self._host + ":" + self._port + STORAGES_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        HardDisk_Type = ["", "", "", "", "HDD", "", "外置硬盘", "", "", "SSD"]
        storages = len(resdata["data"]["storages"])

        for storage in range(1, storages + 1):
            if resdata["data"]["storages"][storage-1].get("label"):
                self._data["storage" + str(storage) + "_" + "label"] = resdata["data"]["storages"][storage-1]["label"]

            if resdata["data"]["storages"][storage-1].get("host"):
                self._data["storage" + str(storage) + "_" + "host"] = resdata["data"]["storages"][storage-1].get("host")

            if resdata["data"]["storages"][storage-1].get("mode"):
                self._data["storage" + str(storage) + "_" + "mode"] = resdata["data"]["storages"][storage-1].get("mode")

            if resdata["data"]["storages"][storage-1].get("name"):
                self._data["storage" + str(storage) + "_" + "name"] = resdata["data"]["storages"][storage-1].get("name")

            if resdata["data"]["storages"][storage-1].get("size"):
                sizes = self.convert_size(resdata["data"]["storages"][storage-1]["size"])
                self._data["storage" + str(storage) + "_" + "size"] = sizes[0]
                self._data["storage" + str(storage) + "_" + "size_attrs"] = {"unit_of_measurement": sizes[1]}

            if resdata["data"]["storages"][storage-1].get("used"):
                sizes = self.convert_size(resdata["data"]["storages"][storage-1]["used"])
                self._data["storage" + str(storage) + "_" + "used"] = sizes[0]
                self._data["storage" + str(storage) + "_" + "used_attrs"] = {"unit_of_measurement": sizes[1]}

            self._data["storage" + str(storage) + "_" + "used_gb"] = resdata["data"]["storages"][storage-1].get("used")/1024/1024/1024/1024
            self._data["storage" + str(storage) + "_" + "used_gb_attrs"] = {"unit_of_measurement": "GB"}
            self._data["storage" + str(storage) + "_" + "used_tb"] = resdata["data"]["storages"][storage-1].get("used")/1024/1024/1024/1024/1024
            self._data["storage" + str(storage) + "_" + "used_tb_attrs"] = {"unit_of_measurement": "TB"}

            if resdata["data"]["storages"][storage-1].get("type"):
                self._data["storage" + str(storage) + "_" + "type"] = HardDisk_Type[resdata["data"]["storages"][storage-1].get("type")]

            # _LOGGER.error(resdata["data"]["storages"][storage-1])
            if resdata["data"]["storages"][storage-1].get("status"):
                self._data["storage" + str(storage) + "_" + "status"] = resdata["data"]["storages"][storage-1].get("status")
            # 预计剩余健康度
            if resdata["data"]["storages"][storage-1].get("lifetime"):
                self._data["storage" + str(storage) + "_" + "lifetime"] = resdata["data"]["storages"][storage-1].get("lifetime")

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_status_info(self, token):
        url = self._host + ":" + self._port + STATUS_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        # CPU温度
        self._data["cpu_temp"] = resdata["data"]["cpu"]["cpu_temp"]
        # 内存
        self._data["memory_used"] = resdata["data"]["memory"]["mem_used"]

        memory = self.convert_size(resdata["data"]["memory"]["mem_used_size"])
        self._data["memory_used_size"] = memory[0]
        self._data["memory_used_size_attrs"] = {"unit_of_measurement": memory[1]}

        memory = self.convert_size(resdata["data"]["memory"]["mem_total"])
        self._data["memory_total"] = memory[0]
        self._data["memory_total_attrs"] = {"unit_of_measurement": memory[1]}

        self._data["memory_size"] = resdata["data"]["memory"]["mem_size"]
        # 风扇
        self._data["fan_speed"] = resdata["data"]["fan"]["fan_speed"]
        self._data["cpu_fan_speed"] = resdata["data"]["fan"]["cpu_fan_speed"]
        self._data["board_fan_speed"] = resdata["data"]["fan"]["board_fan_speed"]
        # swap
        self._data["swap_total"] = resdata["data"]["swap"]["swap_total"]
        self._data["swap_used"] = resdata["data"]["swap"]["swap_used"]

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_harddisk_info(self, token):
        url = self._host + ":" + self._port + STATUS_HARDDISK_TEMP_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata1 = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata1)

        url = self._host + ":" + self._port + STATUS_HARDDISK_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata2 = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata2)

        harddisks = len(resdata1["data"]["harddisk"])

        for harddisk in range(1, harddisks + 1):
            self._data["disk" + str(harddisk) + "_" + "interface"] = resdata1["data"]["harddisk"][harddisk-1]["interface"]
            self._data["disk" + str(harddisk) + "_" + "diskplace"] = resdata1["data"]["harddisk"][harddisk-1]["disk_place"]
            self._data["disk" + str(harddisk) + "_" + "disktemp"] = resdata1["data"]["harddisk"][harddisk-1]["disk_temp"]

            read_speed = self.convert_speed(resdata2["data"]["harddisk"][harddisk-1]["read_speed"])
            self._data["disk" + str(harddisk) + "_" + "readspeed"] = read_speed[0]
            self._data["disk" + str(harddisk) + "_" + "readspeed_attrs"] = {"unit_of_measurement": read_speed[1]}

            write_speed = self.convert_speed(resdata2["data"]["harddisk"][harddisk-1]["write_speed"])
            self._data["disk" + str(harddisk) + "_" + "writespeed"] = write_speed[0]
            self._data["disk" + str(harddisk) + "_" + "writespeed_attrs"] = {"unit_of_measurement": write_speed[1]}

            self._data["disk" + str(harddisk) + "_" + "checkstatus"] = resdata2["data"]["harddisk"][harddisk-1]["check_status"]
            self._data["disk" + str(harddisk) + "_" + "diskplace"] = "第" + str(resdata2["data"]["harddisk"][harddisk-1]["disk_place"]) + "槽位"

        if resdata1["data"].get("ssd"):
            diskname = self.checkvalue(self._data, "nvme1")
            ssds = len(resdata1["data"]["ssd"])
            for ssd in range(1, ssds + 1):
                self._data[diskname + "_" + "interface"] = resdata1["data"]["ssd"][ssd-1]["interface"]
                self._data[diskname + "_" + "diskplace"] = resdata1["data"]["ssd"][ssd-1]["disk_place"]
                self._data[diskname + "_" + "disktemp"] = resdata1["data"]["ssd"][ssd-1]["disk_temp"]

                read_speed = self.convert_speed(resdata2["data"]["ssd"][ssd-1]["read_speed"])
                self._data[diskname + "_" + "readspeed"] = read_speed[0]
                self._data[diskname + "_" + "readspeed_attrs"] = {"unit_of_measurement": read_speed[1]}

                write_speed = self.convert_speed(resdata2["data"]["ssd"][ssd-1]["write_speed"])
                self._data[diskname + "_" + "writespeed"] = write_speed[0]
                self._data[diskname + "_" + "writespeed_attrs"] = {"unit_of_measurement": write_speed[1]}

                self._data[diskname + "_" + "checkstatus"] = resdata2["data"]["ssd"][ssd-1]["check_status"]
                self._data[diskname + "_" + "diskplace"] = "第" + str(resdata2["data"]["ssd"][ssd-1]["disk_place"]) + "槽位"

        # harddisks = len(resdata2["data"]["harddisk"])

        # for harddisk in range(1, harddisks + 1):
        #     read_speed = self.convert_speed(resdata2["data"]["harddisk"][harddisk-1]["read_speed"])
        #     self._data["disk" + str(harddisk) + "_" + "readspeed"] = read_speed[0]
        #     self._data["disk" + str(harddisk) + "_" + "readspeed_attrs"] = {"unit_of_measurement": read_speed[1]}

        #     write_speed = self.convert_speed(resdata2["data"]["harddisk"][harddisk-1]["write_speed"])
        #     self._data["disk" + str(harddisk) + "_" + "writespeed"] = write_speed[0]
        #     self._data["disk" + str(harddisk) + "_" + "writespeed_attrs"] = {"unit_of_measurement": write_speed[1]}

        #     self._data["disk" + str(harddisk) + "_" + "checkstatus"] = resdata2["data"]["harddisk"][harddisk-1]["check_status"]
        #     self._data["disk" + str(harddisk) + "_" + "diskplace"] = resdata2["data"]["harddisk"][harddisk-1]["disk_place"]

        # if resdata2["data"].get("ssd"):
        #     ssds = len(resdata2["data"]["ssd"])
        #     for ssd in range(1, ssds + 1):
        #         self._data["ssd" + str(ssd) + "_" + "readspeed"] = resdata2["data"]["ssd"][ssd-1]["read_speed"]
        #         self._data["ssd" + str(ssd) + "_" + "writespeed"] = resdata2["data"]["ssd"][ssd-1]["write_speed"]
        #         self._data["ssd" + str(ssd) + "_" + "checkstatus"] = resdata2["data"]["ssd"][ssd-1]["check_status"]
        #         self._data["ssd" + str(ssd) + "_" + "diskplace"] = resdata2["data"]["ssd"][ssd-1]["disk_place"]

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    async def _get_network_info(self, token):
        url = self._host + ":" + self._port + STATUS_NETWORK_INFO + "?api_token=" + token
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        uploadspeed = self.convert_speed(resdata["data"]["network"]["upload_speed"])
        self._data["upload_speed"] = uploadspeed[0]
        self._data["upload_speed_attrs"] = {"unit_of_measurement": uploadspeed[1]}

        downspeed = self.convert_speed(resdata["data"]["network"]["download_speed"])
        self._data["download_speed"] = downspeed[0]
        self._data["download_speed_attrs"] = {"unit_of_measurement": downspeed[1]}

        querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._data["querytime"] = querytime

        return

    def checkvalue(self, myjson: json, value: str) -> str:
        i = 0
        currnum = 0
        currkey = ""

        for tmpvalue in myjson.values():
            if tmpvalue == value:
                currnum = i
                break
            i += 1

        i = 0
        for tmpkey in myjson.keys():
            if i == currnum:
                currkey = tmpkey
                break
            i += 1

        return currkey[:currkey.find("_")]

    def seconds_to_dhms(self, seconds):
        days = seconds // (3600 * 24)
        hours = (seconds // 3600) % 24
        minutes = (seconds // 60) % 60
        seconds = seconds % 60
        if days > 0:
            return "{0}天{1}小时{2}分钟".format(days, hours, minutes)
        if hours > 0:
            return "{0}小时{1}分钟".format(hours, minutes)
        if minutes > 0:
            return "{0}分钟{1}秒".format(minutes, seconds)
        return "{0}秒".format(seconds)

    def convert_size(self, size_bytes):
        # 定义存储大小单位
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        if type(size_bytes) != int:
            size_bytes = int(size_bytes)
        # 获取对应单位的索引
        index = 0
        while size_bytes >= 1024 and index < len(units) - 1:
            size_bytes /= 1024
            index += 1

        # 格式化输出
        return [f"{size_bytes:.2f}", f"{units[index]}"]

    def convert_speed(self, value):
        # 定义存储大小单位
        units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s"]
        # 获取对应单位的索引
        index = 0
        while value >= 1024 and index < len(units) - 1:
            value /= 1024
            index += 1

        # 格式化输出
        return [f"{value:.2f}", f"{units[index]}"]

    async def _get_ugreen_switch(self, token: str, switch):
        url = self._host + ":" + self._port + switch["show_url"].replace("{api_token}", token)
        _LOGGER.debug("Requests remaining: %s", url)
        try:
            async with timeout(10):
                resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
        except ClientConnectorError as error:
            raise UpdateFailed(error)
        _LOGGER.debug(resdata)

        # 会话超时
        if resdata["code"] == 8013:
            _LOGGER.error(resdata["msg"])

        tmp = switch["show_body"]
        tmps = tmp.split(".")
        tmpb = resdata[tmps[0]][tmps[1]]
        # _LOGGER.info("Current Function _get_ugreen_switch, %s Switch Status is %s" % (switch["name"], tmpb))

        if str(tmpb) == str(switch["turn_on_body"]):
            self._data["switch"].append({"name": switch["name"], "onoff": "on"})
        else:
            self._data["switch"].append({"name": switch["name"], "onoff": "off"})
        return

    async def get_data(self, token):
        tasks = [
            asyncio.create_task(self._get_sys_info(token)),
        ]
        await asyncio.gather(*tasks)

        tasks = [
            asyncio.create_task(self._get_cpu_info(token)),
            asyncio.create_task(self._get_disks_info(token)),
            asyncio.create_task(self._get_storages_info(token)),
            asyncio.create_task(self._get_status_info(token)),
            asyncio.create_task(self._get_harddisk_info(token)),
            asyncio.create_task(self._get_network_info(token)),
        ]
        await asyncio.gather(*tasks)

        self._data["switch"] = []
        tasks = []
        for switch in SWITCH_TYPES:  # pylint: disable=consider-using-dict-items
            tasks = [
                asyncio.create_task(self._get_ugreen_switch(token, SWITCH_TYPES[switch],)),
            ]
            await asyncio.gather(*tasks)

        _LOGGER.debug(self._data)
        return self._data


class GetDataError(Exception):
    """request error or response data is unexpected"""
