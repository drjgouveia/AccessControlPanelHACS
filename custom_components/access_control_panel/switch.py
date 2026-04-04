"""Switch entities for lock control."""

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up the lock switch platform."""
    coordinator: AccessControlPanelCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            LockSwitch(coordinator, entry, div_id)
            for div_id in _get_divisions(coordinator)
        ],
        update_before_add=True,
    )


def _get_divisions(coordinator):
    """Get list of division IDs from coordinator data."""
    data = coordinator.data
    if not data or "locks" not in data:
        return []
    return list(data["locks"].keys())


class LockSwitch(CoordinatorEntity[AccessControlPanelCoordinator], SwitchEntity):
    """Representation of a lock switch."""

    _attr_icon = "mdi:lock"

    def __init__(self, coordinator, entry, division_id):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._division_id = division_id
        self._attr_unique_id = f"{entry.entry_id}_lock_{division_id}"
        self._attr_name = f"Lock {division_id.replace('_', ' ').title()}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def is_on(self):
        """Return true if the lock is locked."""
        data = self.coordinator.data
        if not data or "locks" not in data:
            return False
        lock_data = data["locks"].get(self._division_id, {})
        return lock_data.get("locked", False)

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        data = self.coordinator.data
        if not data or "locks" not in data:
            return {}
        lock_data = data["locks"].get(self._division_id, {})
        return {
            "division": self._division_id,
            "locking": lock_data.get("locking", False),
            "unlocking": lock_data.get("unlocking", False),
            "pin": lock_data.get("pin"),
        }

    async def async_turn_on(self, **kwargs):
        """Lock the door."""
        await self.coordinator.control_lock(self._division_id, "lock")

    async def async_turn_off(self, **kwargs):
        """Unlock the door."""
        await self.coordinator.control_lock(self._division_id, "unlock")
