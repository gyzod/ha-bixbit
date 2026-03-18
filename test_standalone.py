#!/usr/bin/env python3
"""Standalone test script for the Bixbit API client (no Home Assistant needed)."""

import asyncio
import json
import sys

# Import the API client directly - bypass package imports
import importlib.util

# Load const module first
const_spec = importlib.util.spec_from_file_location(
    "bixbit.const", "custom_components/bixbit/const.py"
)
const_mod = importlib.util.module_from_spec(const_spec)
sys.modules["bixbit.const"] = const_mod
const_spec.loader.exec_module(const_mod)

# Load api module
api_spec = importlib.util.spec_from_file_location(
    "bixbit.api", "custom_components/bixbit/api.py",
    submodule_search_locations=[]
)
api_mod = importlib.util.module_from_spec(api_spec)
# Patch the relative import
sys.modules["bixbit.api"] = api_mod
api_spec.loader.exec_module(api_mod)

BixbitApi = api_mod.BixbitApi
BixbitApiError = api_mod.BixbitApiError

# ─── Configuration ──────────────────────────────────────────────
HOST = "192.168.3.51"
PORT = 4028
# ────────────────────────────────────────────────────────────────


async def main() -> None:
    api = BixbitApi(host=HOST, port=PORT)
    print(f"🔌 Connexion au mineur Bixbit à {HOST}:{PORT}\n")

    # All read-only commands to test
    commands: list[tuple[str, str]] = [
        ("get_firmware_version", "Firmware"),
        ("get_summary", "Summary"),
        ("get_user_power_limit", "Power Limit"),
        ("get_fan_mode", "Fan Mode"),
        ("get_power_status", "Power Status"),
        ("get_liquid_cooling", "Liquid Cooling"),
        ("get_overclock_info", "Overclock Info"),
        ("get_board_slots_state", "Board Slots"),
        ("get_cool_temp", "Cool Temp"),
        ("get_env_temp_limit", "Env Temp Limit"),
        ("get_ams_install_data", "AMS Install Data"),
        ("get_profiles_generation_status", "Profiles Generation Status"),
        ("get_profile_switcher", "Profile Switcher"),
        ("has_upfreq_results", "Upfreq Results"),
        ("get_lower_profile_if_autotune_failed", "Lower Profile if Autotune Failed"),
        ("get_additional_psu", "Additional PSU"),
        ("get_allowed_pools", "Allowed Pools"),
        ("get_stratum_off", "Stratum Off"),
        ("get_proxy_info", "Proxy Info"),
        ("get_compute_info", "Compute Info"),
        ("get_generate_profiles_params", "Generate Profiles Params"),
        ("get_advanced_fan_mode", "Advanced Fan Mode"),
        ("get_upfreq_save_params", "Upfreq Save Params"),
        ("get_stats", "Stats"),
    ]

    passed = 0
    failed = 0

    for method_name, label in commands:
        try:
            method = getattr(api, method_name)
            result = await method()
            print(f"✅ {label}")
            print(f"   {json.dumps(result, indent=2, default=str)[:500]}")
            print()
            passed += 1
        except BixbitApiError as err:
            print(f"❌ {label}: {err}")
            print()
            failed += 1
        except Exception as err:
            print(f"❌ {label}: {type(err).__name__}: {err}")
            print()
            failed += 1

    print("─" * 50)
    print(f"Résultats: {passed} OK, {failed} erreurs sur {len(commands)} commandes")


if __name__ == "__main__":
    asyncio.run(main())
