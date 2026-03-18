"""Bixbit miner API client using async TCP sockets."""

from __future__ import annotations

import asyncio
import base64
import hashlib
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


class BixbitAuthError(BixbitApiError):
    """Authentication error."""


def _aes_encrypt(data: bytes, key: bytes) -> bytes:
    """AES-ECB encrypt with PKCS7 padding (no external dependency)."""
    # PKCS7 padding
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)
    # AES-ECB encrypt block by block
    from .aes import aes_ecb_encrypt
    return aes_ecb_encrypt(data, key)


def _aes_decrypt(data: bytes, key: bytes) -> bytes:
    """AES-ECB decrypt with PKCS7 unpadding."""
    from .aes import aes_ecb_decrypt
    decrypted = aes_ecb_decrypt(data, key)
    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    if 1 <= pad_len <= 16 and all(b == pad_len for b in decrypted[-pad_len:]):
        return decrypted[:-pad_len]
    return decrypted


class BixbitApi:
    """Async client for communicating with a Bixbit miner over TCP."""

    def __init__(self, host: str, port: int, password: str = "admin") -> None:
        self._host = host
        self._port = port
        self._password = password

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    async def _send_raw(self, message: str) -> Any:
        """Send a raw message string and return parsed JSON."""
        _LOGGER.debug("Sending to %s:%s: %s", self._host, self._port, message[:200])

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

    async def _send_command(
        self, cmd: str, payload: dict[str, Any] | None = None
    ) -> Any:
        """Send a read command (unencrypted)."""
        command: dict[str, Any] = {"cmd": cmd}
        if payload:
            command.update(payload)
        message = json.dumps(command) + "\n"
        return await self._send_raw(message)

    async def _get_aes_key(self) -> bytes:
        """Get a fresh AES key via the get_token handshake."""
        token_resp = await self._send_command("get_token")
        msg = token_resp.get("Msg", token_resp)
        if isinstance(msg, str):
            raise BixbitAuthError(f"Token error: {msg}")
        salt = msg.get("salt", "")
        newsalt = msg.get("newsalt", "")
        if not salt or not newsalt:
            raise BixbitAuthError("Missing salt in token response")

        # WhatsMiner key derivation:
        # step1 = MD5(password + salt).hexdigest()
        # aes_key = MD5(newsalt + step1).digest()  (16 bytes)
        step1 = hashlib.md5(
            (self._password + salt).encode()
        ).hexdigest()
        return hashlib.md5((newsalt + step1).encode()).digest()

    async def _send_write_command(
        self, cmd: str, payload: dict[str, Any] | None = None
    ) -> Any:
        """Send a write command using AES-encrypted protocol."""
        aes_key = await self._get_aes_key()

        command: dict[str, Any] = {"cmd": cmd}
        if payload:
            command.update(payload)

        plaintext = json.dumps(command).encode("utf-8")
        encrypted = _aes_encrypt(plaintext, aes_key)
        enc_b64 = base64.b64encode(encrypted).decode("ascii")

        enc_msg = json.dumps({"enc": 1, "data": enc_b64}) + "\n"
        resp = await self._send_raw(enc_msg)

        if not isinstance(resp, dict):
            raise BixbitCommandError(f"Unexpected response: {resp}")

        # Check for token/enc errors
        if resp.get("STATUS") == "E":
            error_msg = resp.get("Msg", "")
            if "enc" in str(error_msg).lower() or "token" in str(error_msg).lower():
                raise BixbitAuthError(
                    f"Authentication failed (wrong password?): {error_msg}"
                )
            raise BixbitCommandError(f"Command failed: {error_msg}")

        # Decrypt response if it's encrypted
        if "data" in resp and "enc" in resp:
            try:
                enc_data = base64.b64decode(resp["data"])
                decrypted = _aes_decrypt(enc_data, aes_key)
                return json.loads(decrypted.decode("utf-8"))
            except Exception as err:
                _LOGGER.warning("Could not decrypt response: %s", err)
                return resp

        return resp

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
        resp = await self._send_write_command(
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
        resp = await self._send_write_command("set_fan_mode", payload)
        self._check_status(resp)
        return resp

    async def set_overclock_info(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_overclock_info", kwargs)
        self._check_status(resp)
        return resp

    async def delete_overclock_info(self) -> dict[str, Any]:
        resp = await self._send_write_command("delete_overclock_info")
        self._check_status(resp)
        return resp

    async def set_board_slots_state(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_board_slots_state", kwargs)
        self._check_status(resp)
        return resp

    async def reset_recovery_reboots(self) -> dict[str, Any]:
        resp = await self._send_write_command(
            "reset_failed_to_power_on_hashboard_reboots"
        )
        self._check_status(resp)
        return resp

    async def set_boards_cool_fan_percent(
        self, percent: int
    ) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_boards_cool_fan_percent",
            {"boards_cool_fan_percent": str(percent)},
        )
        self._check_status(resp)
        return resp

    async def deep_power_off(self) -> dict[str, Any]:
        resp = await self._send_write_command("deep_power_off")
        self._check_status(resp)
        return resp

    async def deep_power_on(self) -> dict[str, Any]:
        resp = await self._send_write_command("deep_power_on")
        self._check_status(resp)
        return resp

    async def delete_upfreq_results(self) -> dict[str, Any]:
        resp = await self._send_write_command("delete_upfreq_results")
        self._check_status(resp)
        return resp

    async def set_cool_temp(
        self, temp_type: str, manual_temp: int
    ) -> dict[str, Any]:
        resp = await self._send_write_command(
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
        resp = await self._send_write_command(
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
        resp = await self._send_write_command(
            "ams_install",
            {"api_key": api_key, "update_interval": update_interval},
        )
        self._check_status(resp)
        return resp

    async def ams_uninstall(self) -> dict[str, Any]:
        resp = await self._send_write_command("ams_uninstall")
        self._check_status(resp)
        return resp

    async def set_upfreq_save_params(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_upfreq_save_params", kwargs)
        self._check_status(resp)
        return resp

    async def generate_profiles(self) -> dict[str, Any]:
        resp = await self._send_write_command("generate_profiles")
        self._check_status(resp)
        return resp

    async def stop_profiles_generation(self) -> dict[str, Any]:
        resp = await self._send_write_command("stop_profiles_generation")
        self._check_status(resp)
        return resp

    async def delete_generated_profiles(self) -> dict[str, Any]:
        resp = await self._send_write_command("delete_generated_profiles")
        self._check_status(resp)
        return resp

    async def set_profile_switcher(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_profile_switcher", kwargs)
        self._check_status(resp)
        return resp

    async def set_psu_fan(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_psu_fan", {"enabled": str(enabled).lower()}
        )
        self._check_status(resp)
        return resp

    async def set_liquid_cooling(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_liquid_cooling",
            {"liquid_cooling": str(enabled).lower()},
        )
        self._check_status(resp)
        return resp

    async def set_lower_profile_if_autotune_failed(
        self, enabled: bool
    ) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_lower_profile_if_autotune_failed",
            {"enabled": str(enabled).lower()},
        )
        self._check_status(resp)
        return resp

    async def set_additional_psu(self, enabled: bool) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_additional_psu", {"enabled": str(enabled).lower()}
        )
        self._check_status(resp)
        return resp

    async def upgrade_psu_firmware(self) -> dict[str, Any]:
        resp = await self._send_write_command("upgrade_psu_firmware")
        self._check_status(resp)
        return resp

    async def set_allowed_pools(self, pools: list[str]) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_allowed_pools", {"pools": pools}
        )
        self._check_status(resp)
        return resp

    async def set_stratum_off(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_stratum_off", kwargs)
        self._check_status(resp)
        return resp

    async def set_proxy_info(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_proxy_info", kwargs)
        self._check_status(resp)
        return resp

    async def set_compute_info(self, wmt_port: str) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_compute_info", {"wmt_port": wmt_port}
        )
        self._check_status(resp)
        return resp

    async def set_generate_profiles_params(
        self, **kwargs: Any
    ) -> dict[str, Any]:
        resp = await self._send_write_command(
            "set_generate_profiles_params", kwargs
        )
        self._check_status(resp)
        return resp

    async def set_advanced_fan_mode(self, **kwargs: Any) -> dict[str, Any]:
        resp = await self._send_write_command("set_advanced_fan_mode", kwargs)
        self._check_status(resp)
        return resp

    async def reset_mac(self, mac: str | None = None) -> dict[str, Any]:
        payload = {"mac": mac} if mac else {}
        resp = await self._send_write_command("reset_mac", payload or None)
        self._check_status(resp)
        return resp

    # ─── Utility ────────────────────────────────────────────────────

    async def test_connection(self) -> dict[str, Any]:
        """Test connection by fetching firmware version."""
        return await self.get_firmware_version()
