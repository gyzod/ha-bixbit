"""Bixbit miner API client using async TCP sockets."""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import logging
import time
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


def _null_pad(s: str) -> bytes:
    """Pad string with null bytes to 16-byte boundary."""
    while len(s) % 16 != 0:
        s += "\x00"
    return s.encode("utf-8")


def _aes_encrypt(data: bytes, key: bytes) -> bytes:
    """AES-ECB encrypt (data must already be padded to 16-byte blocks)."""
    from .aes import aes_ecb_encrypt
    return aes_ecb_encrypt(data, key)


def _aes_decrypt(data: bytes, key: bytes) -> bytes:
    """AES-ECB decrypt and strip null-byte padding."""
    from .aes import aes_ecb_decrypt
    decrypted = aes_ecb_decrypt(data, key)
    return decrypted.split(b"\x00")[0]


class BixbitApi:
    """Async client for communicating with a Bixbit miner over TCP."""

    _AES_KEY_TTL = 25  # seconds – token is valid for 30s on the miner
    _MAX_RETRIES = 3
    _RETRY_DELAY = 1.5  # seconds between retries on "over max connect"
    _CMD_DELAY = 1.0  # seconds between sequential commands

    def __init__(self, host: str, port: int, password: str = "admin") -> None:
        self._host = host
        self._port = port
        self._password = password
        self._aes_key: bytes | None = None
        self._sign: str | None = None
        self._aes_key_time: float = 0.0
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    async def _send_raw(self, message: str) -> Any:
        """Send a raw message string and return parsed JSON."""
        async with self._lock:
            return await self._send_raw_unlocked(message)

    async def _send_raw_unlocked(self, message: str) -> Any:
        """Send a raw message (must be called with _lock held)."""
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
        """Send a read command (unencrypted) with retry on connection limit."""
        command: dict[str, Any] = {"cmd": cmd}
        if payload:
            command.update(payload)
        message = json.dumps(command) + "\n"
        last_err: Exception | None = None
        for attempt in range(self._MAX_RETRIES):
            try:
                resp = await self._send_raw(message)
                # Check for "over max connect" in response
                if isinstance(resp, dict):
                    msg = resp.get("Msg", "")
                    if isinstance(msg, str) and "over max connect" in msg:
                        raise BixbitConnectionError(msg)
                return resp
            except BixbitConnectionError as err:
                last_err = err
                if attempt < self._MAX_RETRIES - 1:
                    _LOGGER.debug(
                        "Connection limited, retry %d/%d in %.1fs",
                        attempt + 1, self._MAX_RETRIES, self._RETRY_DELAY,
                    )
                    await asyncio.sleep(self._RETRY_DELAY)
        raise last_err  # type: ignore[misc]

    async def _get_aes_key(self) -> tuple[bytes, str]:
        """Get AES-256 key and sign token, reusing cached values if valid.

        WhatsMiner key derivation (reference implementation):
        1. pwd = md5_crypt(password, salt)   → $1$salt$hash
        2. key = hash part of pwd
        3. aes_key = unhexlify(sha256(key).hexdigest())  → 32 bytes (AES-256)
        4. sign = md5_crypt(key + time, newsalt).split('$')[3]
        """
        now = time.monotonic()
        if (
            self._aes_key is not None
            and self._sign is not None
            and (now - self._aes_key_time) < self._AES_KEY_TTL
        ):
            return self._aes_key, self._sign

        token_resp = await self._send_command("get_token")
        msg = token_resp.get("Msg", token_resp)
        if isinstance(msg, str):
            raise BixbitAuthError(f"Token error: {msg}")
        salt = msg.get("salt", "")
        newsalt = msg.get("newsalt", "")
        time_val = msg.get("time", "")
        if not salt or not newsalt:
            raise BixbitAuthError("Missing salt in token response")

        from .md5_crypt import md5_crypt

        # Step 1: md5_crypt(password, salt) → extract hash
        pwd_hash = md5_crypt(self._password, salt)
        key = pwd_hash.split("$")[3]

        # Step 2: SHA-256 of key → 32-byte AES key
        aes_key_hex = hashlib.sha256(key.encode()).hexdigest()
        self._aes_key = binascii.unhexlify(aes_key_hex.encode())

        # Step 3: Derive the sign token
        sign_hash = md5_crypt(key + time_val, newsalt)
        self._sign = sign_hash.split("$")[3]

        self._aes_key_time = time.monotonic()
        return self._aes_key, self._sign

    async def _send_write_command(
        self, cmd: str, payload: dict[str, Any] | None = None
    ) -> Any:
        """Send a write command using WhatsMiner AES-256-ECB encrypted protocol.

        Protocol:
        1. Get token (salt, newsalt, time) from miner
        2. Derive AES-256 key and sign via md5_crypt + SHA-256
        3. Build JSON command with 'token' field
        4. Null-pad and encrypt with AES-256-ECB
        5. Base64 encode and send as {"enc": 1, "data": "..."}
        """
        last_err: Exception | None = None
        for attempt in range(self._MAX_RETRIES):
            try:
                aes_key, sign = await self._get_aes_key()

                command: dict[str, Any] = {"cmd": cmd, "token": sign}
                if payload:
                    command.update(payload)

                plaintext = _null_pad(json.dumps(command))
                encrypted = _aes_encrypt(plaintext, aes_key)
                enc_b64 = base64.encodebytes(encrypted).decode().replace("\n", "")

                enc_msg = json.dumps({"enc": 1, "data": enc_b64})
                resp = await self._send_raw(enc_msg)

                if not isinstance(resp, dict):
                    raise BixbitCommandError(f"Unexpected response: {resp}")

                # Check for plain-text error responses
                if resp.get("STATUS") == "E":
                    error_msg = resp.get("Msg", "")
                    if "enc" in str(error_msg).lower() or "token" in str(error_msg).lower():
                        self._aes_key = None
                        self._sign = None
                        raise BixbitAuthError(
                            f"Authentication failed (wrong password?): {error_msg}"
                        )
                    raise BixbitCommandError(f"Command failed: {error_msg}")

                # Decrypt encrypted response
                if "enc" in resp:
                    try:
                        enc_data = base64.b64decode(resp["enc"])
                        decrypted = _aes_decrypt(enc_data, aes_key)
                        return json.loads(decrypted.decode("utf-8"))
                    except Exception:
                        pass
                if "data" in resp:
                    try:
                        enc_data = base64.b64decode(resp["data"])
                        decrypted = _aes_decrypt(enc_data, aes_key)
                        return json.loads(decrypted.decode("utf-8"))
                    except Exception as err:
                        _LOGGER.warning("Could not decrypt response: %s", err)
                        return resp

                return resp

            except (BixbitConnectionError, BixbitAuthError) as err:
                last_err = err
                self._aes_key = None
                self._sign = None
                if attempt < self._MAX_RETRIES - 1:
                    _LOGGER.debug(
                        "Write cmd '%s' failed (%s), retry %d/%d in %.1fs",
                        cmd, err, attempt + 1, self._MAX_RETRIES,
                        self._RETRY_DELAY,
                    )
                    await asyncio.sleep(self._RETRY_DELAY)
        raise last_err  # type: ignore[misc]

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

    async def apply_overclock_profile(
        self,
        *,
        board_temp_target: int,
        freq_target: int,
        power_limit: int,
        power_max: int,
        voltage_limit: int,
        voltage_min: int,
        voltage_target: int,
        fan_mode: int = 1,
        manual_fan_speed_percent: int = 100,
        boards_cool_fan_percent: int = 100,
        additional_psu: bool = False,
        liquid_cooling: bool = False,
        soft_restart: bool = True,
    ) -> None:
        """Apply a full overclock profile using local API commands."""
        await self.set_overclock_info(
            board_temp_target=board_temp_target,
            freq_target=freq_target,
            power_limit=power_limit,
            power_max=power_max,
            voltage_limit=voltage_limit,
            voltage_min=voltage_min,
            voltage_target=voltage_target,
            soft_restart=soft_restart,
        )
        await asyncio.sleep(self._CMD_DELAY)
        await self.set_fan_mode(
            fan_mode=str(fan_mode),
            manual_fan_speed_percent=manual_fan_speed_percent,
        )
        await asyncio.sleep(self._CMD_DELAY)
        await self.set_boards_cool_fan_percent(boards_cool_fan_percent)
        await asyncio.sleep(self._CMD_DELAY)
        await self.set_additional_psu(additional_psu)
        await asyncio.sleep(self._CMD_DELAY)
        await self.set_liquid_cooling(liquid_cooling)

    async def test_connection(self) -> dict[str, Any]:
        """Test connection by fetching firmware version."""
        return await self.get_firmware_version()
