"""Services for Access Control Panel integration."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    SERVICE_ADD_USER,
    SERVICE_CONTROL_LOCK,
    SERVICE_GRANT_DIVISION,
    SERVICE_REMOVE_USER,
    SERVICE_REVOKE_DIVISION,
    SERVICE_SEND_CODE,
    SERVICE_UPDATE_USER,
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Access Control Panel."""

    async def _get_coordinator(service: ServiceCall):
        """Get the coordinator from the service call."""
        entry_id = service.data.get("entry_id")
        if not entry_id:
            entries = hass.config_entries.async_entries(DOMAIN)
            if not entries:
                raise HomeAssistantError("No Access Control Panel configured")
            entry = entries[0]
        else:
            entry = hass.config_entries.async_get_entry(entry_id)
            if not entry:
                raise HomeAssistantError(f"Config entry {entry_id} not found")

        if entry.state != ConfigEntryState.LOADED:
            raise HomeAssistantError("Access Control Panel is not loaded")

        return hass.data[DOMAIN][entry.entry_id]

    async def handle_send_code(service: ServiceCall) -> None:
        """Send a code to the keypad."""
        coordinator = await _get_coordinator(service)
        code = service.data["code"]
        result = await coordinator.send_code(code)
        if not result.get("granted"):
            raise HomeAssistantError(f"Code not granted: {result}")

    async def handle_add_user(service: ServiceCall) -> None:
        """Add a user."""
        coordinator = await _get_coordinator(service)
        await coordinator.add_user(
            user_id=service.data["user_id"],
            name=service.data.get("name", service.data["user_id"]),
            user_code=service.data["user_code"],
            passcode=service.data.get("passcode", ""),
            access_level=service.data.get("access_level", 1),
            divisions=service.data.get("divisions", []),
        )

    async def handle_remove_user(service: ServiceCall) -> None:
        """Remove a user."""
        coordinator = await _get_coordinator(service)
        await coordinator.remove_user(service.data["user_id"])

    async def handle_update_user(service: ServiceCall) -> None:
        """Update a user."""
        coordinator = await _get_coordinator(service)
        user_id = service.data["user_id"]
        updates = {
            k: v for k, v in service.data.items() if k not in ("user_id", "entry_id")
        }
        await coordinator.update_user(user_id, **updates)

    async def handle_grant_division(service: ServiceCall) -> None:
        """Grant division access to a user."""
        coordinator = await _get_coordinator(service)
        await coordinator.grant_division(
            service.data["user_id"], service.data["division"]
        )

    async def handle_revoke_division(service: ServiceCall) -> None:
        """Revoke division access from a user."""
        coordinator = await _get_coordinator(service)
        await coordinator.revoke_division(
            service.data["user_id"], service.data["division"]
        )

    async def handle_control_lock(service: ServiceCall) -> None:
        """Control a lock."""
        coordinator = await _get_coordinator(service)
        await coordinator.control_lock(service.data["division"], service.data["action"])

    hass.services.async_register(DOMAIN, SERVICE_SEND_CODE, handle_send_code)
    hass.services.async_register(DOMAIN, SERVICE_ADD_USER, handle_add_user)
    hass.services.async_register(DOMAIN, SERVICE_REMOVE_USER, handle_remove_user)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_USER, handle_update_user)
    hass.services.async_register(DOMAIN, SERVICE_GRANT_DIVISION, handle_grant_division)
    hass.services.async_register(
        DOMAIN, SERVICE_REVOKE_DIVISION, handle_revoke_division
    )
    hass.services.async_register(DOMAIN, SERVICE_CONTROL_LOCK, handle_control_lock)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Access Control Panel services."""
    for service in [
        SERVICE_SEND_CODE,
        SERVICE_ADD_USER,
        SERVICE_REMOVE_USER,
        SERVICE_UPDATE_USER,
        SERVICE_GRANT_DIVISION,
        SERVICE_REVOKE_DIVISION,
        SERVICE_CONTROL_LOCK,
    ]:
        hass.services.async_remove(DOMAIN, service)
