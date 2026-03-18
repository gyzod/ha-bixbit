"""Config flow for Bixbit Miner integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .api import BixbitApi, BixbitApiError
from .const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class BixbitConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bixbit Miner."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            self._async_abort_if_unique_id_configured()
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            api = BixbitApi(host=host, port=port)
            try:
                firmware = await api.test_connection()
                msg = firmware.get("Msg", firmware)
                if isinstance(msg, dict):
                    fw_version = msg.get("firmware_version", "unknown")
                else:
                    fw_version = "unknown"
            except BixbitApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Bixbit Miner ({host})",
                    data=user_input,
                    description_placeholders={"firmware": fw_version},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
