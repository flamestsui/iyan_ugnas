"""iYan_UGNas Entities"""
import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
)

from homeassistant.helpers import device_registry as dr
from .const import (
    COORDINATOR,
    DOMAIN,
    SENSOR_TYPES,
    SENSOR_TYPES_DISK,
    SENSOR_TYPES_STORAGES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Add iYan_UGNas entities from a config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    sensors = []
    for sensor in SENSOR_TYPES:
        try:
            coordinator.data[sensor]  # pylint:disable=pointless-statement
            sensors.append(UGREENSensor(sensor, coordinator))
        except KeyError:
            _LOGGER.error(f"Const文件“%s”错误，请检查！" % sensor)

    async_add_entities(sensors)

    sensors = []
    for sensor in SENSOR_TYPES_DISK:  # pylint: disable=consider-using-dict-items
        try:
            coordinator.data[sensor]  # pylint:disable=pointless-statement
            sensors.append(UGREENSensorDisk(sensor, coordinator, SENSOR_TYPES_DISK[sensor]["device_Id"]))
        except KeyError:
            _LOGGER.error(f"Const文件“%s”错误，请检查！" % sensor)

    async_add_entities(sensors)

    sensors = []
    for sensor in SENSOR_TYPES_STORAGES:  # pylint: disable=consider-using-dict-items
        try:
            coordinator.data[sensor]  # pylint:disable=pointless-statement
            sensors.append(UGREENSensorStorage(sensor, coordinator, SENSOR_TYPES_STORAGES[sensor]["device_Id"]))
        except KeyError:
            _LOGGER.error(f"Const文件“%s”错误，请检查！" % sensor)

    async_add_entities(sensors)


class UGREENSensor(CoordinatorEntity):
    """Define an iYan_UGNas entity."""
    _attr_has_entity_name = True

    def __init__(self, kind, coordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.kind = kind
        self.coordinator = coordinator

    @property
    def name(self):
        """Return the name."""
        return f"{SENSOR_TYPES[self.kind]['name']}"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.kind}_{self.coordinator.host}"

    @property
    def entity_category(self):
        """Return the name."""
        if SENSOR_TYPES[self.kind].get("category"):
            if f"{SENSOR_TYPES[self.kind]['category']}" == "diagnostic":
                return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        """Return the device info."""
        ret = {
            "identifiers": {(DOMAIN, self.coordinator.host + "_" + SENSOR_TYPES[self.kind]['device_Id'])},
            "name": self.coordinator.data["device_name"],
            "manufacturer": "UGREEN",
            "model": self.coordinator.data["model"],
            "sw_version": self.coordinator.data["firmware_ver"],
        }
        return ret

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data[self.kind]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self.kind]["icon"]

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES[self.kind].get("unit_of_measurement"):
            return SENSOR_TYPES[self.kind]["unit_of_measurement"]

    @property
    def device_class(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES[self.kind].get("device_class"):
            return SENSOR_TYPES[self.kind]["device_class"]

    @property
    def state_class(self):
        if SENSOR_TYPES[self.kind].get("state_class"):
            return SENSOR_TYPES[self.kind]["state_class"]

    @property
    def state_attributes(self):
        attrs = {}
        data = self.coordinator.data
        if self.coordinator.data.get(self.kind + "_attrs"):
            attrs = self.coordinator.data[self.kind + "_attrs"]
        if data:
            attrs["querytime"] = data["querytime"]
        return attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update Bjtoon health code entity."""
        # await self.coordinator.async_request_refresh()


class UGREENSensorDisk(CoordinatorEntity):
    """Define an iYan_UGNas entity."""

    _attr_has_entity_name = True

    def __init__(self, kind, coordinator, diskNum) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.kind = kind
        self.coordinator = coordinator
        self.diskNum = diskNum

    @property
    def name(self):
        """Return the name."""
        return f"{SENSOR_TYPES_DISK[self.kind]['name']}"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.kind}_{self.coordinator.host}"

    @property
    def entity_category(self):
        """Return the name."""
        if SENSOR_TYPES_DISK[self.kind].get("category"):
            # _LOGGER.info(SENSOR_TYPES_DISK[self.kind].get("category"))
            if f"{SENSOR_TYPES_DISK[self.kind]['category']}" == "diagnostic":
                return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        """Return the device info."""
        ret = {
            "identifiers": {(DOMAIN, self.coordinator.host + "_" + SENSOR_TYPES_DISK[self.kind]['device_Id'])},
            "name": self.coordinator.data["device_name"] + " (" + SENSOR_TYPES_DISK[self.kind]['device_Id'].capitalize() + ")",
            "manufacturer": "UGREEN",
            "model": self.coordinator.data[self.diskNum + "_model"],
        }
        return ret

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the state."""
        try:
            return self.coordinator.data[self.kind]
        except KeyError:
            return ""

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES_DISK[self.kind]["icon"]

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES_DISK[self.kind].get("unit_of_measurement"):
            return SENSOR_TYPES_DISK[self.kind]["unit_of_measurement"]

    @property
    def device_class(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES_DISK[self.kind].get("device_class"):
            return SENSOR_TYPES_DISK[self.kind]["device_class"]

    @property
    def state_class(self):
        if SENSOR_TYPES_DISK[self.kind].get("state_class"):
            return SENSOR_TYPES_DISK[self.kind]["state_class"]

    @property
    def state_attributes(self):
        attrs = {}
        data = self.coordinator.data
        if self.coordinator.data.get(self.kind + "_attrs"):
            attrs = self.coordinator.data[self.kind + "_attrs"]
        if data:
            attrs["querytime"] = data["querytime"]
        return attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update Bjtoon health code entity."""
        # await self.coordinator.async_request_refresh()


class UGREENSensorStorage(CoordinatorEntity):
    """Define an iYan_UGNas entity."""

    _attr_has_entity_name = True

    def __init__(self, kind, coordinator, diskNum) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.kind = kind
        self.coordinator = coordinator
        self.diskNum = diskNum

    @property
    def name(self):
        """Return the name."""
        return f"{SENSOR_TYPES_STORAGES[self.kind]['name']}"

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.kind}_{self.coordinator.host}"

    @property
    def entity_category(self):
        """Return the name."""
        if SENSOR_TYPES_STORAGES[self.kind].get("category"):
            if f"{SENSOR_TYPES_STORAGES[self.kind]['category']}" == "diagnostic":
                return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        """Return the device info."""
        ret = {
            "identifiers": {(DOMAIN, self.coordinator.host + "_" + SENSOR_TYPES_STORAGES[self.kind]['device_Id'])},
            "name": self.coordinator.data["device_name"] + " (" + SENSOR_TYPES_STORAGES[self.kind]['device_Id'].capitalize() + ")",
            "manufacturer": "UGREEN",
            "model": self.coordinator.data[self.diskNum + "_label"],
        }
        return ret

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the state."""
        return self.coordinator.data[self.kind]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES_STORAGES[self.kind]["icon"]

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES_STORAGES[self.kind].get("unit_of_measurement"):
            return SENSOR_TYPES_STORAGES[self.kind]["unit_of_measurement"]

    @property
    def device_class(self):
        """Return the unit_of_measurement."""
        if SENSOR_TYPES_STORAGES[self.kind].get("device_class"):
            return SENSOR_TYPES_STORAGES[self.kind]["device_class"]

    @property
    def state_attributes(self):
        attrs = {}
        data = self.coordinator.data
        if self.coordinator.data.get(self.kind + "_attrs"):
            attrs = self.coordinator.data[self.kind + "_attrs"]
        if data:
            attrs["querytime"] = data["querytime"]
        return attrs

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_update(self):
        """Update Bjtoon health code entity."""
        # await self.coordinator.async_request_refresh()
