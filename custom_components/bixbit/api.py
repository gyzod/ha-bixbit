"""Bixbit miner API client using async TCP sockets."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .const import RECV_BUFFER_SIZE, SOCKET_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class BixbitApiError(Exception):
    """Base exception for Bixbit API errors."""


class BixbitConnectionError(BixbitApiError):
    """Connection error."""


class BixbitCommandError(BixbitApiError):
    """Command execution error."""


class BixbitApi:
    """Async client for communicating with a Bixbit miner over TCP."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    async def _send_command(
        self, cmd: str, payload: dict[str, Any] | None = None
    ) -> Any:
        """Send a command to the miner and return the parsed JSON response."""
        command: dict[str, Any] = {"cmd": cmd}
        if payload:
            command.update(payload)

        message = json.dumps(command) + "\n"
        _LOGGER.debug("Sending to %s:%s: %s", self._host, self._port, message.strip())

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=SOCKET_TIMEOUT,
            )
        except (OSError, asyncio.TimeoutError) as err:
            raise BixbitConnectionError(
                f"Cannot connect to {self._host}:{self._port}: {err}"
            ) from err

        try:
            writer.write(message.encode("utf-8"))
            await writer.drain()

            response = b""
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        reader.read(RECV_BUFFER_SIZE),
                        timeout=SOCKET_TIMEOUT,
                    )
                except asyncio.TimeoutError:
                    break

                if not chunk:
                    break
                response += chunk

                try:
                    json.loads(response.decode("utf-8"))
                    break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

            response_str = response.decode("utf-8")
            _LOGGER.debug("Received from %s: %s", self._host, response_str[:500])
            return json.loads(response_str)

        except json.JSONDecodeError as err:
            raise BixbitCommandError(
                f"Invalid JSON response from {self._host}: {err}"
            ) from err
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

    def _check_status(self, response: Any) -> None:
        """Check if a command response indicates an error."""
        if isinstance(response, dict):
            status = response.get("STATUS")
            if status == "E":
                msg = response.get("Msg", "Unknown error")
                raise BixbitCommandError(f"Command failed: {msg}")

    # ─── Read commands ──────────────────────────────────────────────

    async def get_summary(self) -> dict[str, Any]:
        return await self._send_command("summary")

    async def get_stats(self) -> Any:
        return await self._send_command("stats")

    async def get_user_power_limit(self) -> dict[str, Any]:
        return await self._send_command("get_user_power_limit")

    async def get_fan_mode(self) -> dict[str, Any]:
        return await self._send_command("get_fan_mode")

    async def get_overclock_info(self) -> dict[str, Any]:
        return await self._send_command("get_overclock_info")

    async def get_board_slots_state(self) -> dict[str, Any]:
        return await self._send_command("get_board_slots_state")

    async def get_firmware_version(self) -> dict[str, Any]:
        return await self._send_command("get_firmware_version")

    async def get_power_status(self) -> dict[str, Any]:
        return await self._send_command("power_status")

    async def get_cool_temp(self) -> dict[str, Any]:
        return await self._send_command("get_cool_temp")

    async def get_env_temp_limit(self) -> dict[str, Any]:
        return await self._send_command("get_env_temp_limit")

    async def get_ams_install_data(self) -> dict[str, Any]:
        return await self._send_command("get_ams_install_data")

    async def get_upfreq_save_params(self) -> dict[str, Any]:
        return await self._send_command("get_upfreq_save_params")

    async def get_profiles_generation_status(self) -> dict[str, Any]:
        return await self._send_command("get_profiles_generation_status")

    async def get_profile_switcher(self) -> dict[str, Any]:
        return await self._send_command("get_profile_switcher")

    async def has_upfreq_results(self) -> dict[str, Any]:
        return await self._send_command("has_upfreq_results")

    async def get_liquid_cooling(self) -> dict[str, Any]:
        return await self._send_command("get_liquid_cooling")

    async def get_lower_profile_if_autotune_failed(self) -> dict[str, Any]:
        return await self._send_command("get_lower_profile_if_autotune_failed")

    async def get_additional_psu(self) -> dict[str, Any]:
        return await self._send_command("get_additional_psu")

    async def get_allowed_pools(self) -> dict[str, Any]:
        return await self._send_command("get_allowed_pools")

    async def get_stratum_off(self) -> dict[str, Any]:
        return await self._send_command("get_stratum_off")

    async def get_proxy_info(self) -> dict[str, Any]:
        return await self._send_command("get_proxy_info")

    async def get_compute_info(self) -> dict[str, Any]:
        return await self._send_command("get_compute_info")

    async def get_generate_profiles_params(self) -> dict[str, Any]:
        return await self._send_command("get_generate_profiles_params")

    async def get_advanced_fan_mode(self) -> dict[str, Any]:
        return await self._send_command("get_advanced_fan_mode")

    # ─── Write commands ─────────────────────────────────────────────

    async def set_user_power_limit(
        self,
        power_mode: str | int,
        power_limit: int,
        soft_restart: bool = True,
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_user_power_limit",
            {
                "softRestart": soft_restart,
                "powerMode": power_mode,
                "powerLimit": power_limit,
            },
        )
        self._check_status(resp)
        return resp

    async def set_fan_mode(
        self, fan_mode: str, manual_fan_speed_percent: int | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"fan_mode": fan_mode}
        if manual_fan_speed_percent is not None:
            payload["manual_fan_speed_percent"] = str(manual_fan_speed_percent)
        resp = await self._send_command("set_fan_mode", payload)
        self._check_status(resp)
        return resp

    async def set_overclock_info(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_overclock_info", kwargs)
        self._check_status(resp)
        return resp

    async def delete_overclock_info(self) -> dict[str, Any]:
        resp = await self._send_command("delete_overclock_info")
        self._check_status(resp)
        return resp

    async def set_board_slots_state(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_board_slots_state", kwargs)
        self._check_status(resp)
        return resp

    async def reset_recovery_reboots(self) -> dict[str, Any]:
        resp = await self._send_command(
            "reset_failed_to_power_on_hashboard_reboots"
        )
        self._check_status(resp)
        return resp

    async def set_boards_cool_fan_percent(
        self, percent: int
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_boards_cool_fan_percent",
            {"boards_cool_fan_percent": str(percent)},
        )
        self._check_status(resp)
        return resp

    async def deep_power_off(self) -> dict[str, Any]:
        resp = await self._send_command("deep_power_off")
        self._check_status(resp)
        return resp

    async def deep_power_on(self) -> dict[str, Any]:
        resp = await self._send_command("deep_power_on")
        self._check_status(resp)
        return resp

    async def delete_upfreq_results(self) -> dict[str, Any]:
        resp = await self._send_command("delete_upfreq_results")
        self._check_status(resp)
        return resp

    async def set_cool_temp(
        self, temp_type: str, manual_temp: int
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_cool_temp",
            {"type": temp_type, "manual_temp": manual_temp},
        )
        self._check_status(resp)
        return resp

    async def set_env_temp_limit(
        self,
        enabled: bool,
        resume_env_temp: str,
        suspend_env_temp: str,
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_env_temp_limit",
            {
                "enabled": str(enabled).lower(),
                "resume_env_temp": resume_env_temp,
                "suspend_env_temp": suspend_env_temp,
            },
        )
        self._check_status(resp)
        return resp

    async def ams_install(
        self, api_key: str, update_interval: int = 5
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "ams_install",
            {"api_key": api_key, "update_interval": update_interval},
        )
        self._check_status(resp)
        return resp

    async def ams_uninstall(self) -> dict[str, Any]:
        resp = await self._send_command("ams_uninstall")
        self._check_status(resp)
        return resp

    async def set_upfreq_save_params(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_upfreq_save_params", kwargs)
        self._check_status(resp)
        return resp

    async def generate_profiles(self) -> dict[str, Any]:
        resp = await self._send_command("generate_profiles")
        self._check_status(resp)
        return resp

    async def stop_profiles_generation(self) -> dict[str, Any]:
        resp = await self._send_command("stop_profiles_generation")
        self._check_status(resp)
        return resp

    async def delete_generated_profiles(self) -> dict[str, Any]:
        resp = await self._send_command("delete_generated_profiles")
        self._check_status(resp)
        return resp

    async def set_profile_switcher(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_profile_switcher", kwargs)
        self._check_status(resp)
        return resp

    async def set_psu_fan(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_command(
            "set_psu_fan", {"enabled": str(enabled).lower()}
        )
        self._check_status(resp)
        return resp

    async def set_liquid_cooling(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_command(
            "set_liquid_cooling",
            {"liquid_cooling": str(enabled).lower()},
        )
        self._check_status(resp)
        return resp

    async def set_lower_profile_if_autotune_failed(
        self, enabled: bool
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_lower_profile_if_autotune_failed",
            {"enabled": str(enabled).lower()},
        )
        self._check_status(resp)
        return resp

    async def set_additional_psu(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_command(
            "set_additional_psu", {"enabled": str(enabled).lower()}
        )
        self._check_status(resp)
        return resp

    async def upgrade_psu_firmware(self) -> dict[str, Any]:
        resp = await self._send_command("upgrade_psu_firmware")
        self._check_status(resp)
        return resp

    async def set_allowed_pools(self, pools: list[str]) -> dict[str, Any]:
        resp = await self._send_command(
            "set_allowed_pools", {"pools": pools}
        )
        self._check_status(resp)
        return resp

    async def set_stratum_off(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_stratum_off", kwargs)
        self._check_status(resp)
        return resp

    async def set_proxy_info(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_proxy_info", kwargs)
        self._check_status(resp)
        return resp

    async def set_compute_info(self, wmt_port: str) -> dict[str, Any]:
        resp = await self._send_command(
            "set_compute_info", {"wmt_port": wmt_port}
        )
        self._check_status(resp)
        return resp

    async def set_generate_profiles_params(
        self, **kwargs: Any
    ) -> dict[str, Any]:
        resp = await self._send_command(
            "set_generate_profiles_params", kwargs
        )
        self._check_status(resp)
        return resp

    async def set_advanced_fan_mode(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_command("set_advanced_fan_mode", kwargs)
        self._check_status(resp)
        return resp

    async def reset_mac(self, mac: str | None = None) -> dict[str, Any]:
        payload = {"mac": mac} if mac else {}
        resp = await self._send_command("reset_mac", payload or None)
        self._check_status(resp)
        return resp

    # ─── Utility ────────────────────────────────────────────────────

    async def test_connection(self) -> dict[str, Any]:
        """Test connection by fetching firmware version."""
        return await self.get_firmware_version()
