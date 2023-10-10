"""iYan_UGNas update entities."""
from __future__ import annotations

import asyncio
from typing import Any
import time
import json
import requests
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError
import datetime

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import UpdateFailed

from .data_fetcher import DataFetcher

from .const import (
    COORDINATOR,
    DOMAIN,
    BUTTON_TYPES,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSMD5,
    CONF_PORT,
    UPDATE_WEB,
    UPDATE_ROM,
    UPDATE_BIOS,
    SYS_INFO,
    UPDATE_TYPES,
)

import logging
FAKE_INSTALL_SLEEP_TIME = 0.5


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback,) -> None:
    """Set up demo update platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    host = config_entry.data[CONF_HOST]
    username = config_entry.data[CONF_USERNAME]
    passwd = config_entry.data[CONF_PASSMD5]
    port = config_entry.data[CONF_PORT]

    UGREENUpdateInfos = UGREENUpdateInfo(hass, coordinator, host, port, username, passwd)
    await UGREENUpdateInfos.version()
    versions = UGREENUpdateInfos.resdata

    async_add_entities([
        UGREENUpdate(
            unique_id=f"{DOMAIN}_firmware_{coordinator.host}",
            kind="firmware",
            device_name=coordinator.data["device_name"] + "_firmware",
            title=coordinator.data["device_name"] + " " + "Firmware",
            installed_version=versions["firmware_ver"],
            latest_version=versions["firmware_ver_New"],
            release_summary=versions["firmware_ver_Desc"],
            # release_url="",
            coordinator=coordinator,
            device_class=UpdateDeviceClass.FIRMWARE,
        ),
        UGREENUpdate(
            unique_id=f"{DOMAIN}_nas_server_{coordinator.host}",
            kind="webui",
            device_name=coordinator.data["device_name"] + "_webui",
            title=coordinator.data["device_name"] + " " + "WebUI",
            installed_version=versions["nas_server_ver"],
            latest_version=versions["webUI_New"],
            release_summary=versions["webUI_Desc"],
            # release_url="https://www.ikuai8.com/index.php?option=com_content&view=article&id=331",
            coordinator=coordinator,
            device_class=UpdateDeviceClass.FIRMWARE,
        ),
        UGREENUpdate(
            unique_id=f"{DOMAIN}_bios_{coordinator.host}",
            kind="bios",
            device_name=coordinator.data["device_name"] + "_bios",
            title=coordinator.data["device_name"] + " " + "BIOS",
            installed_version=versions["bios_ver"],
            latest_version=versions["bios_New"],
            release_summary=versions["bios_Desc"],
            # release_url="https://www.ikuai8.com/index.php?option=com_content&view=article&id=331",
            coordinator=coordinator,
            device_class=UpdateDeviceClass.FIRMWARE,
        ),
    ])


async def _fake_install() -> None:
    """Fake install an update."""
    await asyncio.sleep(FAKE_INSTALL_SLEEP_TIME)


class UGREENUpdateInfo():
    def __init__(self, hass: HomeAssistant, coordinator, host: str, port: str, username: str, passwd: str) -> None:
        self._token = ""
        self._token_expire_time = 0
        self._allow_login = True
        self._fetcher = DataFetcher(hass, host, port, username, passwd)
        self._host = host
        self._hass = hass
        self._data = ""
        self._port = port

    async def get_access_token(self):
        if time.time() < self._token_expire_time:
            return self._token
        else:
            if self._allow_login == True:
                self._token = await self._fetcher._login_offlineLogin()  # pylint: disable=protected-access
                if self._token == 10001:
                    self._allow_login = False
                self._token_expire_time = time.time() + 60 * 60 * 2
                return self._token
            else:
                return

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

    def requestpost_json(self, url, headerstr, json_body):
        responsedata = requests.post(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode('utf-8')
        resdata = json.loads(json_text)
        return resdata

    async def version(self):
        if self._allow_login == True:
            token = await self.get_access_token()
            header = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36",
            }

            url = self._host + ":" + self._port + SYS_INFO + "?api_token=" + token
            _LOGGER.debug("Requests remaining: %s", url)
            try:
                async with timeout(10):
                    resdata = await self._hass.async_add_executor_job(self.requestget_data, url, header)
            except ClientConnectorError as error:
                raise UpdateFailed(error)
            _LOGGER.debug(resdata)

            self._data = {}

            self._data["firmware_ver"] = resdata["data"]["firmware_ver"]
            self._data["nas_server_ver"] = resdata["data"]["nas_server_ver"]
            self._data["nas_server_ver_no"] = resdata["data"]["nas_server_ver_no"]
            self._data["webui_ver"] = resdata["data"]["webui_ver"]
            self._data["weblauncher_ver"] = resdata["data"]["weblauncher_ver"]
            self._data["bios_ver"] = resdata["data"]["bios_ver"]

            # webUI
            url = self._host + ":" + self._port + UPDATE_WEB + "?api_token=" + token
            try:
                async with timeout(10):
                    resdata = await self._hass.async_add_executor_job(self.requestget_data, url, header)
            except (ClientConnectorError) as error:
                raise UpdateFailed(error)

            try:
                self._data["webUI_New"] = resdata["data"]["versionName"] + resdata["data"]["versionNo"]
                self._data["webUI_Desc"] = resdata["data"]["desc"]
            except KeyError:
                self._data["webUI_New"] = self._data["nas_server_ver"]
                self._data["webUI_Desc"] = ""
                _LOGGER.info("No webUI UPDate")

            # ROM
            url = self._host + ":" + self._port + UPDATE_ROM + "?api_token=" + token
            try:
                async with timeout(10):
                    resdata = await self._hass.async_add_executor_job(self.requestget_data, url, header)
            except (ClientConnectorError) as error:
                raise UpdateFailed(error)

            try:
                self._data["firmware_ver_New"] = resdata["data"]["versionName"] + resdata["data"]["versionNo"]
                self._data["firmware_ver_Desc"] = resdata["data"]["desc"]
            except KeyError:
                self._data["firmware_ver_New"] = self._data["firmware_ver"]
                self._data["firmware_ver_Desc"] = ""
                _LOGGER.info("No ROM UPDate")

            # BIOS
            url = self._host + ":" + self._port + UPDATE_BIOS + "?api_token=" + token
            try:
                async with timeout(10):
                    resdata = await self._hass.async_add_executor_job(self.requestget_data, url, header)
            except (ClientConnectorError) as error:
                raise UpdateFailed(error)

            try:
                self._data["bios_New"] = resdata["data"]["versionName"] + resdata["data"]["versionNo"]
                self._data["bios_Desc"] = resdata["data"]["desc"]
            except KeyError:
                self._data["bios_New"] = self._data["bios_ver"]
                self._data["bios_Desc"] = ""
                _LOGGER.info("No BIOS UPDate")

            _LOGGER.debug("Requests remaining: %s", url)
            _LOGGER.debug(resdata)

        _LOGGER.info("操作UGREEN: %s ", )
        return "OK"

    @property
    def resdata(self):
        """Return the name."""
        return self._data


class UGREENUpdate(UpdateEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(
        self,
        *,
        unique_id: str,
        device_name: str,
        title: str | None,
        installed_version: str | None,
        latest_version: str | None,
        release_summary: str | None = None,
        release_url: str | None = None,
        support_progress: bool = False,
        support_install: bool = True,
        support_release_notes: bool = False,
        device_class: UpdateDeviceClass | None = None,
        coordinator,
        kind,
    ) -> None:
        self.kind = kind
        """Initialize the Demo select entity."""
        self._attr_installed_version = installed_version
        self._attr_device_class = device_class
        self._attr_latest_version = latest_version
        self._attr_release_summary = release_summary
        self._attr_release_url = release_url
        self._attr_title = title
        self._attr_unique_id = unique_id

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host + "_device")},
            name=coordinator.data["device_name"],
            manufacturer="UGREEN",
            model=coordinator.data["model"],
        )

        if support_install:
            self._attr_supported_features |= (
                UpdateEntityFeature.INSTALL
                | UpdateEntityFeature.BACKUP
                | UpdateEntityFeature.SPECIFIC_VERSION
            )
        if support_progress:
            self._attr_supported_features |= UpdateEntityFeature.PROGRESS

        if support_release_notes:
            self._attr_supported_features |= UpdateEntityFeature.RELEASE_NOTES

    @property
    def name(self):
        """Return the name."""
        # return self._attr_title
        return f"{UPDATE_TYPES[self.kind]['friendly_name']}"

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        """Install an update."""
        if self.supported_features & UpdateEntityFeature.PROGRESS:
            for progress in range(0, 100, 10):
                self._attr_in_progress = progress
                self.async_write_ha_state()
                await _fake_install()

        self._attr_in_progress = False
        self._attr_installed_version = (
            version if version is not None else self.latest_version
        )
        self.async_write_ha_state()

    def release_notes(self) -> str | None:
        """Return the release notes."""
        return (
            "Long release notes.\n\n**With** "
            f"markdown support!\n\n***\n\n{self.release_summary}"
        )
