import logging
import time
import datetime
import json
import requests
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import UpdateFailed

from .data_fetcher import DataFetcher

from .const import (
    COORDINATOR,
    DOMAIN,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWD,
    CONF_PASSMD5,
    CONF_PORT,
    SWITCH_TYPES,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Add Switchentities from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    host = config_entry.data[CONF_HOST]
    username = config_entry.data[CONF_USERNAME]
    passwd = config_entry.data[CONF_PASSMD5]
    port = config_entry.data[CONF_PORT]
    switchs = []

    if SWITCH_TYPES:
        _LOGGER.debug("setup switchs")
        for switch in SWITCH_TYPES:  # pylint: disable=consider-using-dict-items
            switchs.append(UGREENSwitch(hass, switch, coordinator, host, port, username, passwd))
            _LOGGER.debug(SWITCH_TYPES[switch]["name"])
        async_add_entities(switchs, False)


class UGREENSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, kind: str, coordinator,  host, port, username, passwd) -> None:
        """Initialize."""
        super().__init__()
        self.kind = kind
        self.coordinator = coordinator
        self._state = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.coordinator.host + "_" + SWITCH_TYPES[self.kind]['device_Id'])},
            # "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": self.coordinator.data["device_name"],
            "manufacturer": "UGREEN",
            "model": self.coordinator.data["model"],
            "sw_version": self.coordinator.data["firmware_ver"],
        }
        self._attr_icon = SWITCH_TYPES[self.kind]['icon']
        self._attr_device_class = "switch"
        self._attr_entity_registry_enabled_default = True
        self._hass = hass
        self._token = ""
        self._token_expire_time = 0
        self._allow_login = True
        self._fetcher = DataFetcher(hass, host, port, username, passwd)
        self._host = host
        self._port = port
        self._name = SWITCH_TYPES[self.kind]['name']
        self._turn_on_body = SWITCH_TYPES[self.kind]['turn_on_body']
        self._turn_on_url = SWITCH_TYPES[self.kind]['turn_on_url']
        self._turn_off_body = SWITCH_TYPES[self.kind]['turn_off_body']
        self._turn_off_url = SWITCH_TYPES[self.kind]['turn_off_url']
        self._change = True
        self._switchonoff = None

        self._token_ = ""
        self._session_ = ""
        self._sysauth_ = ""

        self._header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36",
        }
        listswitch = self.coordinator.data.get("switch")

        for switchdata in listswitch:
            if switchdata["name"] == self._name:
                self._switchonoff = switchdata["onoff"]

        self._is_on = self._switchonoff == "on"
        self._state = "on" if self._is_on == True else "off"

    @property
    def name(self):
        """Return the name."""
        return f"{self._name}"

    @property
    def unique_id(self):
        return f"{DOMAIN}_switch_{self.coordinator.host}_{self._name}"

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def is_on(self):
        """Check if switch is on."""
        return self._is_on

    async def get_access_token(self):
        if time.time() < self._token_expire_time:
            return self._token
        else:
            if self._allow_login == True:
                self._token = await self._fetcher._login_offlineLogin()  # pylint: disable=protected-access
                if self._token == 10001:
                    self._allow_login = False
                self._token_expire_time = time.time() + 60*60*2
                return self._token
            else:
                return

    async def async_turn_on(self, **kwargs):
        """Turn switch on."""
        self._is_on = True
        self._change = False
        json_body = self._turn_on_url
        await self._switch(json_body)
        self._switchonoff = "on"

    async def async_turn_off(self, **kwargs):
        """Turn switch off."""
        self._is_on = False
        self._change = False
        json_body = self._turn_off_url
        await self._switch(json_body)
        self._switchonoff = "off"

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update entity."""
        await self.coordinator.async_request_refresh()

        listswitch = self.coordinator.data.get("switch")

        for switchdata in listswitch:
            if switchdata["name"] == self._name:
                self._switchonoff = switchdata["onoff"]

        self._is_on = self._switchonoff == "on"
        self._state = "on" if self._is_on == True else "off"
        self._change = True

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

    async def _check_status(self, switch):
        url = self._host + ":" + self._port + switch["show_url"].replace("{api_token}", self._token)
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

        if tmpb == switch["turn_on_body"]:
            return "on"
        else:
            return "off"
        return

    async def _switch(self, url):
        if self._allow_login == True:
            await self.get_access_token()
            # resdata = await self._check_status(SWITCH_TYPES[self.name])
            if url.find("|") > 0:
                postData = json.loads(url[url.find("|")+1:])
                url = url[0:url.find("|")]
                url = self._host + ":" + self._port + url.replace("{api_token}", self._token)
                _LOGGER.info("Current Function _switch, url = %s" % url)
                _LOGGER.info("Current Function _switch, data = %s" % postData)
                try:
                    async with timeout(10):
                        resdata = await self._hass.async_add_executor_job(self.requestpost_json, url, self._header, postData)
                except ClientConnectorError as error:
                    raise UpdateFailed(error)
            else:
                url = self._host + ":" + self._port + url.replace("{api_token}", self._token)
                _LOGGER.info("Current Function _switch, url = %s" % url)
                try:
                    async with timeout(10):
                        resdata = await self._hass.async_add_executor_job(self.requestget_data, url, self._header)
                except ClientConnectorError as error:
                    raise UpdateFailed(error)

            _LOGGER.info("Current Function _switch, %s" % resdata)

        _LOGGER.info("操作iyan nas Switch: %s")
        return "OK"
