"""Sensor entities for Access Control Panel."""

import json
import logging
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AccessControlPanelCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: AccessControlPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AccessLogSensor(coordinator, entry),
        ArmedStatusSensor(coordinator, entry),
        AlarmStatusSensor(coordinator, entry),
        UserCountSensor(coordinator, entry),
    ]
    async_add_entities(entities)


class AccessLogSensor(CoordinatorEntity[AccessControlPanelCoordinator], SensorEntity):
    """Sensor for the recent access log."""

    _attr_name = "Access Log"
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_access_log"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self):
        """Return the most recent log entry."""
        data = self.coordinator.data
        if not data or "log" not in data or not data["log"]:
            return "No entries"
        last_entry = data["log"][-1]
        return last_entry.get("action", "unknown")

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        data = self.coordinator.data
        if not data or "log" not in data:
            return {"entries": []}
        entries = []
        for entry in data["log"][-10:]:
            ts = entry.get("time", 0)
            if isinstance(ts, (int, float)) and ts > 0:
                time_str = datetime.fromtimestamp(ts).isoformat()
            else:
                time_str = str(ts)
            entries.append(
                {
                    "time": time_str,
                    "code": f"****{entry.get('code', '')[-4:]}",
                    "granted": entry.get("granted", False),
                    "action": entry.get("action", ""),
                }
            )
        return {"entries": entries}


class ArmedStatusSensor(CoordinatorEntity[AccessControlPanelCoordinator], SensorEntity):
    """Sensor for the armed/disarmed status."""

    _attr_name = "Armed Status"
    _attr_icon = "mdi:shield"

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_armed_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self):
        """Return the armed status."""
        data = self.coordinator.data
        if not data or "status" not in data:
            return None
        return "Armed" if data["status"].get("armed") else "Disarmed"


class AlarmStatusSensor(CoordinatorEntity[AccessControlPanelCoordinator], SensorEntity):
    """Sensor for the alarm triggered status."""

    _attr_name = "Alarm Status"
    _attr_icon = "mdi:alarm-light"

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alarm_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self):
        """Return the alarm status."""
        data = self.coordinator.data
        if not data or "status" not in data:
            return None
        return "Triggered" if data["status"].get("alarm_triggered") else "Normal"


class UserCountSensor(CoordinatorEntity[AccessControlPanelCoordinator], SensorEntity):
    """Sensor for the number of registered users."""

    _attr_name = "Registered Users"
    _attr_icon = "mdi:account-group"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_user_count"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self):
        """Return the number of users."""
        data = self.coordinator.data
        if not data or "users" not in data:
            return 0
        return len(data["users"])

    @property
    def extra_state_attributes(self):
        """Return user list as attributes."""
        data = self.coordinator.data
        if not data or "users" not in data:
            return {"users": []}
        users = []
        for user in data["users"]:
            users.append(
                {
                    "user_id": user.get("user_id"),
                    "name": user.get("name"),
                    "access_level": user.get("access_level"),
                    "divisions": user.get("divisions", []),
                    "enabled": user.get("enabled", True),
                }
            )
        return {"users": users}
