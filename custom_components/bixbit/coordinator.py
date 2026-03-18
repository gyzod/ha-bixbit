"""DataUpdateCoordinator for Bixbit miner."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BixbitApi, BixbitApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BixbitCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls a Bixbit miner for data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: BixbitApi,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{api.host}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    @staticmethod
    def _extract_msg(response: Any) -> dict[str, Any]:
        """Extract the payload from an API response.

        Most commands return {"STATUS": "S", "Msg": {…}}.
        The summary command returns {"STATUS": [...], "SUMMARY": [{…}]}.
        """
        if not isinstance(response, dict):
            return {}

        # summary-style: {"SUMMARY": [{…}]}
        summary = response.get("SUMMARY")
        if isinstance(summary, list) and summary:
            return summary[0] if isinstance(summary[0], dict) else {}

        # standard: {"Msg": {…}} or {"Msg": [{…}]}
        msg = response.get("Msg")
        if isinstance(msg, dict):
            return msg
        if isinstance(msg, list) and msg:
            return msg[0] if isinstance(msg[0], dict) else {}

        return response

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data from the miner."""
        try:
            summary_raw = await self.api.get_summary()
            fan_mode_raw = await self.api.get_fan_mode()
            power_limit_raw = await self.api.get_user_power_limit()
            power_status_raw = await self.api.get_power_status()
            firmware_raw = await self.api.get_firmware_version()
            liquid_cooling_raw = await self.api.get_liquid_cooling()

            return {
                "summary": self._extract_msg(summary_raw),
                "fan_mode": self._extract_msg(fan_mode_raw),
                "power_limit": self._extract_msg(power_limit_raw),
                "power_status": self._extract_msg(power_status_raw),
                "firmware": self._extract_msg(firmware_raw),
                "liquid_cooling": self._extract_msg(liquid_cooling_raw),
            }
        except BixbitApiError as err:
            raise UpdateFailed(f"Error communicating with Bixbit miner: {err}") from err
