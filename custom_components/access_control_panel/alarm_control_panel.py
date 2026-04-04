"""Alarm Control Panel entity for Access Control Panel."""

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelState,
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
    """Set up the alarm control panel platform."""
    coordinator: AccessControlPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AccessControlPanelAlarmEntity(coordinator, entry)])


class AccessControlPanelAlarmEntity(
    CoordinatorEntity[AccessControlPanelCoordinator], AlarmControlPanelEntity
):
    """Representation of the Access Control Panel alarm."""

    _attr_name = None
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.DISARM
        | AlarmControlPanelEntityFeature.TRIGGER
    )

    def __init__(self, coordinator, entry):
        """Initialize the alarm entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alarm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="BOS Keyboard",
            model="Access Control Panel",
        )

    @property
    def alarm_state(self):
        """Return the state of the alarm."""
        data = self.coordinator.data
        if not data or "status" not in data:
            return None

        status = data["status"]
        if status.get("alarm_triggered"):
            return AlarmControlPanelState.TRIGGERED
        if status.get("armed"):
            return AlarmControlPanelState.ARMED_HOME
        return AlarmControlPanelState.DISARMED

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm the alarm."""
        await self.coordinator.arm_alarm()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm the alarm."""
        await self.coordinator.disarm_alarm(code or "")

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Trigger the alarm."""
        await self.coordinator.trigger_alarm()
