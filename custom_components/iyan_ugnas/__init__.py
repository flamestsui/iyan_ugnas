"""The iYan_UGNas integration."""
from __future__ import annotations
from async_timeout import timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .data_fetcher import DataFetcher
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWD,
    CONF_PASSMD5,
    CONF_HOST,
    CONF_UPDATE_INTERVAL,
    COORDINATOR,
    UNDO_UPDATE_LISTENER,
    CONF_PORT,
)
from homeassistant.exceptions import ConfigEntryNotReady

import time
import datetime
import logging
import asyncio


_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.UPDATE,
]


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured iYan-UGNas."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iYan-UGNas from a config entry."""
    host = entry.data[CONF_HOST]
    _LOGGER.debug("host: %s", host)
    username = entry.data[CONF_USERNAME]
    passwd = entry.data[CONF_PASSWD]
    passmd5 = entry.data[CONF_PASSMD5]
    port = entry.data[CONF_PORT]

    update_interval_seconds = entry.options.get(CONF_UPDATE_INTERVAL, 10)
    coordinator = UGREENDataUpdateCoordinator(hass, host, port, username, passmd5, update_interval_seconds)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(update_listener)

    hass.data[DOMAIN][entry.entry_id] = {COORDINATOR: coordinator, UNDO_UPDATE_LISTENER: undo_listener, }

    for component in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, component))

    return True


async def async_unload_entry(hass: HomeAssistant,  entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant,  entry: ConfigEntry):
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


class UGREENDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching iYan-UGNas data."""

    def __init__(self, hass: HomeAssistant, host: str, port: str, username: str, passwdmd5: str, update_interval_seconds: int) -> None:
        """Initialize."""
        update_interval = datetime.timedelta(seconds=update_interval_seconds)
        _LOGGER.debug("%s Data will be update every %s", host, update_interval)

        self._token = ""
        self._token_expire_time = 0
        self._allow_login = True
        self._port = port

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

        self._fetcher = DataFetcher(hass, host, port, username, passwdmd5)
        self.host = host

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
                _LOGGER.error("The username or password has been incorrect, please reconfigure the UGREEN integration.")  # pylint: disable=W7401
                return

    async def _async_update_data(self):
        """Update data via DataFetcher."""
        _LOGGER.debug("token_expire_time=%s", self._token_expire_time)
        if self._allow_login == True:
            api_token = await self.get_access_token()
            _LOGGER.debug("api_token = " + api_token)

            try:
                async with timeout(10):
                    data = await self._fetcher.get_data(api_token)
                    if data == 401:
                        self._token_expire_time = 0
                        return
                    if not data:
                        raise UpdateFailed("failed in getting data")
                    return data
            except Exception as error:
                raise UpdateFailed(error) from error
