<p align="center">
  <img src="images/logo.png" alt="Bixbit Logo" width="150">
</p>

<h1 align="center">Bixbit Miner – Home Assistant Integration</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS"></a>
  <a href="https://github.com/gyzod/ha-bixbit/releases"><img src="https://img.shields.io/github/v/release/gyzod/ha-bixbit" alt="Release"></a>
  <a href="https://github.com/gyzod/ha-bixbit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/gyzod/ha-bixbit" alt="License"></a>
</p>

<p align="center">
  Custom Home Assistant integration for <strong>Bixbit</strong> (WhatsMiner-based) ASIC miners.<br>
  Communicates directly with the miner over TCP (port 4028) — no cloud, no extra dependencies.
</p>

---

**Author:** [Gyzod](https://github.com/gyzod)

## Features

### Sensors (27)
| Category | Sensors |
|---|---|
| **Hashrate** | Hashrate (5s), Hashrate (avg), Factory hashrate |
| **Power** | Power (realtime), Power limit, Power mode |
| **Temperatures** | Chip temp protect, Chip temp target, PSU temp 1 & 2 |
| **PSU** | Voltage in/out, Current in/out, Fan speed, Serial, Model |
| **Device** | Status, Miner type, Memory usage, Firmware version, Custom version |
| **Fan** | Fan mode, Manual fan speed |
| **Status** | Suspended, Deep suspended, Cooling mode |

### Controls
| Type | Entities |
|---|---|
| **Switches** | Mining power (deep power on/off), Liquid cooling |
| **Numbers** | Fan speed (slider 10–100%), Power limit (W) |
| **Selects** | Power mode (Low / Normal / High), Fan mode (auto / manual) |
| **Buttons** | Delete overclock, Reset recovery reboots, Delete autotune results, Generate profiles, Stop profile generation, Delete generated profiles, Upgrade PSU firmware, Reset MAC address, Uninstall AMS, Deep power on, Deep power off |

### API Coverage
The integration implements **all 40+ commands** from the Bixbit API v1.7.0 / v2.0.4, including:
- Power management (suspend, deep suspend, power limits, modes)
- Fan control (auto/manual, speed, advanced fan algorithms)
- Overclock management (get/set/delete)
- Board slot management (enable/disable, auto-disable, recovery)
- Temperature management (cool temp, env temp limits)
- Profile management (generate, switch, delete)
- Pool management (allowed pools, stratum off)
- Network (proxy, compute info, MAC reset)
- AMS (install/uninstall)

## Installation

### HACS (recommended)
1. Open HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add this repository URL and select **Integration**
3. Install **Bixbit Miner**
4. Restart Home Assistant

### Manual
1. Copy the `custom_components/bixbit` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Bixbit Miner**
3. Enter the miner's IP address, port (default `4028`), and polling interval (default `30s`)
4. The integration will test the connection before saving

## Standalone Testing (no Home Assistant)

You can test the API client directly without Home Assistant:

```bash
# Clone the repo
git clone <this-repo-url>
cd bixbit

# Create a venv (Python 3.12+)
python3 -m venv venv
source venv/bin/activate

# Edit the HOST in test_standalone.py to match your miner's IP
# Then run:
python test_standalone.py
```

This will execute all 24 read-only API commands and display the results.

## Project Structure

```
custom_components/bixbit/
├── __init__.py          # Integration setup & platforms
├── api.py               # Async TCP API client (all 40+ commands)
├── button.py            # Button entities (11 actions)
├── config_flow.py       # UI configuration flow
├── const.py             # Constants
├── coordinator.py       # DataUpdateCoordinator (polling)
├── entity.py            # Base entity with DeviceInfo
├── manifest.json        # HA integration manifest
├── number.py            # Number entities (fan speed, power limit)
├── select.py            # Select entities (power mode, fan mode)
├── sensor.py            # Sensor entities (27 sensors)
├── strings.json         # Default strings
├── switch.py            # Switch entities (mining power, liquid cooling)
└── translations/
    ├── en.json           # English
    └── fr.json           # Français
```

## Compatibility

Tested with:
- **Miner**: M30S++_VG31
- **PSU**: P221B
- **Firmware**: 20240930.11.Rel.AMS
- **API**: WM_API v1.7.0 / v2.0.4

Should work with all WhatsMiner-based Bixbit miners that expose the TCP API on port 4028.

## API Documentation

See [API.md](API.md) for the full API reference (converted from the official Word document).

## Author

Made with ❤️ by [Gyzod](https://github.com/gyzod)

## License

MIT
