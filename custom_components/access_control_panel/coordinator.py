"""DataUpdateCoordinator for Access Control Panel."""

import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENDPOINT_LOG,
    ENDPOINT_LOCKS,
    ENDPOINT_STATUS,
    ENDPOINT_USERS,
)

_LOGGER = logging.getLogger(__name__)


class AccessControlPanelCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data from the Access Control Panel."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize the coordinator."""
        self.host = config_entry.data[CONF_HOST]
        self.port = config_entry.data[CONF_PORT]
        scan_interval = config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )
        self.config_entry = config_entry
        self.session = async_get_clientsession(hass)
        self._base_url = f"http://{self.host}:{self.port}"

    async def _async_update_data(self):
        """Fetch data from the device."""
        data = {}
        try:
            data["status"] = await self._get(ENDPOINT_STATUS)
            data["log"] = await self._get(ENDPOINT_LOG)
            data["users"] = await self._get(ENDPOINT_USERS)
            data["locks"] = await self._get(ENDPOINT_LOCKS)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        return data

    async def _get(self, endpoint):
        """Perform a GET request."""
        url = f"{self._base_url}{endpoint}"
        async with self.session.get(
            url, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            raise UpdateFailed(f"GET {endpoint} returned {resp.status}")

    async def _post(self, endpoint, data=None):
        """Perform a POST request."""
        url = f"{self._base_url}{endpoint}"
        async with self.session.post(
            url, json=data, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            if resp.status in (200, 201):
                return await resp.json()
            raise UpdateFailed(f"POST {endpoint} returned {resp.status}")

    async def arm_alarm(self):
        """Arm the alarm."""
        result = await self._post(ENDPOINT_STATUS.replace("status", "alarm/arm"))
        await self.async_request_refresh()
        return result

    async def disarm_alarm(self, code=""):
        """Disarm the alarm."""
        result = await self._post(
            ENDPOINT_STATUS.replace("status", "alarm/disarm"), {"code": code}
        )
        await self.async_request_refresh()
        return result

    async def trigger_alarm(self):
        """Trigger the alarm (for testing)."""
        result = await self._post(ENDPOINT_STATUS.replace("status", "alarm/trigger"))
        await self.async_request_refresh()
        return result

    async def clear_alarm(self):
        """Clear the alarm triggered state."""
        result = await self._post(ENDPOINT_STATUS.replace("status", "alarm/clear"))
        await self.async_request_refresh()
        return result

    async def send_code(self, code):
        """Send a code to the keypad endpoint."""
        result = await self._post("/api/keypad", {"code": code})
        await self.async_request_refresh()
        return result

    async def add_user(
        self, user_id, name, user_code, passcode, access_level=1, divisions=None
    ):
        """Add a user."""
        result = await self._post(
            "/api/users",
            {
                "user_id": user_id,
                "name": name,
                "user_code": user_code,
                "passcode": passcode,
                "access_level": access_level,
                "divisions": divisions or [],
            },
        )
        await self.async_request_refresh()
        return result

    async def remove_user(self, user_id):
        """Remove a user."""
        result = await self._delete(f"/api/users/{user_id}")
        await self.async_request_refresh()
        return result

    async def update_user(self, user_id, **kwargs):
        """Update a user."""
        result = await self._put(f"/api/users/{user_id}", kwargs)
        await self.async_request_refresh()
        return result

    async def grant_division(self, user_id, division_id):
        """Grant a user access to a division."""
        result = await self._post(f"/api/users/{user_id}/divisions/{division_id}")
        await self.async_request_refresh()
        return result

    async def revoke_division(self, user_id, division_id):
        """Revoke a user access from a division."""
        result = await self._delete(f"/api/users/{user_id}/divisions/{division_id}")
        await self.async_request_refresh()
        return result

    async def control_lock(self, division_id, action):
        """Control a lock (lock/unlock/open)."""
        result = await self._post(f"/api/lock/{division_id}", {"action": action})
        await self.async_request_refresh()
        return result

    async def _delete(self, endpoint):
        """Perform a DELETE request."""
        url = f"{self._base_url}{endpoint}"
        async with self.session.delete(
            url, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            if resp.status in (200, 201, 204):
                return await resp.json()
            raise UpdateFailed(f"DELETE {endpoint} returned {resp.status}")

    async def _put(self, endpoint, data):
        """Perform a PUT request."""
        url = f"{self._base_url}{endpoint}"
        async with self.session.put(
            url, json=data, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            if resp.status in (200, 201):
                return await resp.json()
            raise UpdateFailed(f"PUT {endpoint} returned {resp.status}")
