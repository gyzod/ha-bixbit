"""Base entity for Bixbit integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BixbitCoordinator


class BixbitEntity(CoordinatorEntity[BixbitCoordinator]):
    """Base class for Bixbit entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BixbitCoordinator, key: str) -> None:
        super().__init__(coordinator)
        host = coordinator.api.host
        self._attr_unique_id = f"{host}_{key}"
        firmware = coordinator.data.get("firmware", {})
        fw_version = firmware.get("firmware_version", "unknown")
        custom_version = firmware.get("custom_version", "")
        summary = coordinator.data.get("summary", {})
        miner_type = summary.get("Miner Type", "Bixbit Miner")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=f"Bixbit {host}",
            manufacturer="Bixbit",
            model=miner_type,
            sw_version=fw_version,
            hw_version=custom_version or None,
        )
