"""The iYan_UGNas Entities"""
import logging
import time
import datetime
import json
import re
import requests
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import HomeAssistant, Config
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.button import ButtonEntity

from .const import (
    COORDINATOR,
    DOMAIN,
    BUTTON_TYPES,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSMD5,
    CONF_PORT,
)

from .data_fetcher import DataFetcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Add iYan-UGNas entities from a config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    host = config_entry.data[CONF_HOST]
    username = config_entry.data[CONF_USERNAME]
    passwd = config_entry.data[CONF_PASSMD5]
    port = config_entry.data[CONF_PORT]

    buttons = []
    for button in BUTTON_TYPES:
        buttons.append(UGREENButton(hass, button, coordinator, host, port, username, passwd))

    async_add_entities(buttons)


class UGREENButton(ButtonEntity):
    """Define an iYan-UGNas entity."""
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, kind, coordinator, host, port, username, passwd) -> None:
        """Initialize."""
        super().__init__()
        self.kind = kind
        self.coordinator = coordinator
        self._state = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.coordinator.host + "_" + BUTTON_TYPES[self.kind]['device_Id'])},
            "name": self.coordinator.data["device_name"],
            "manufacturer": "UGREEN",
            "model": self.coordinator.data["model"],
            "sw_version": self.coordinator.data["firmware_ver"],
        }
        self._attr_device_class = "restart"
        self._attr_entity_registry_enabled_default = True
        self._hass = hass
        self._token = ""
        self._token_expire_time = 0
        self._allow_login = True
        self._fetcher = DataFetcher(hass, host, port, username, passwd)
        self._host = host
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

    @property
    def name(self):
        """Return the name."""
        return f"{BUTTON_TYPES[self.kind]['name']}"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.kind}_{self.coordinator.host}"

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return True

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def device_class(self):
        """Return the unit_of_measurement."""
        if BUTTON_TYPES[self.kind].get("device_class"):
            return BUTTON_TYPES[self.kind]["device_class"]

    def press(self) -> None:
        """Handle the button press."""

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._action(BUTTON_TYPES[self.kind]["name"])

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update iYan-UGNas entity."""
        # await self.coordinator.async_request_refresh()

    def requestpost_json(self, url, headerstr, json_body):
        responsedata = requests.post(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode('utf-8')
        resdata = json.loads(json_text)
        return resdata

    def requestput(self, url, headerstr, json_body):
        if json_body == None:
            responsedata = requests.put(url, headers=headerstr, verify=False)  # pylint: disable=missing-timeout
        else:
            responsedata = requests.put(url, headers=headerstr, json=json_body, verify=False)  # pylint: disable=missing-timeout
        if responsedata.status_code != 200:
            return responsedata.status_code
        json_text = responsedata.content.decode('utf-8')
        return json_text

    async def _action(self, action):
        if self._allow_login == True:
            token = await self.get_access_token()
            header = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36",
            }
            if action == "sleep":
                url = self._host + ":" + self._port + "/setting/v1/sys/enterPowerSaving" + "?api_token=" + token
            elif action == "reboot":
                url = self._host + ":" + self._port + "/setting/v1/sys/reboot" + "?api_token=" + token
            elif action == "shutdown":
                url = self._host + ":" + self._port + "/setting/v1/sys/shutdown" + "?api_token=" + token
            elif action == "lighton":
                url = self._host + ":" + self._port + "/setting/v1/sys/indicator_light/set?indicator_light=1" + "&api_token=" + token
            elif action == "lightoff":
                url = self._host + ":" + self._port + "/setting/v1/sys/indicator_light/set?indicator_light=0" + "&api_token=" + token

            _LOGGER.debug("Requests remaining: %s", url)
            try:
                async with timeout(10):
                    # if action == "lighton" or action == "lightoff":
                    #     resdata = await self._hass.async_add_executor_job(self.requestpost_json, url, header)
                    # else:
                    # resdata = await self._hass.async_add_executor_job(self.requestput, url, header)
                    resdata = await self._hass.async_add_executor_job(self.requestpost_json, url, header, "{}")
            except (
                ClientConnectorError
            ) as error:
                raise UpdateFailed(error)
            _LOGGER.debug("Requests remaining: %s", url)
            _LOGGER.debug(resdata)

        self._state = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _LOGGER.info("操作UGREEN: %s ", action)
        return "OK"
