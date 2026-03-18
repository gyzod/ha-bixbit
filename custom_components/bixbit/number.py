"""Number platform for Bixbit Miner."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BixbitConfigEntry
from .api import BixbitApi
from .coordinator import BixbitCoordinator
from .entity import BixbitEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BixbitNumberEntityDescription(NumberEntityDescription):
    """Describe a Bixbit number entity."""

    value_fn: Callable[[dict[str, Any]], float | None]
    set_fn: Callable[[BixbitApi, float], Coroutine[Any, Any, Any]]


NUMBER_DESCRIPTIONS: tuple[BixbitNumberEntityDescription, ...] = (
    BixbitNumberEntityDescription(
        key="manual_fan_speed",
        translation_key="manual_fan_speed_control",
        icon="mdi:fan",
        native_min_value=10,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        value_fn=lambda d: _to_float(
            d.get("fan_mode", {}).get("manual_fan_speed_percent")
        ),
        set_fn=lambda api, val: api.set_fan_mode("manual", int(val)),
    ),
)


def _to_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BixbitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bixbit number entities."""
    coordinator = entry.runtime_data
    entities: list[NumberEntity] = [
        BixbitNumber(coordinator, desc) for desc in NUMBER_DESCRIPTIONS
    ]
    entities.append(BixbitPowerLimitNumber(coordinator))
    async_add_entities(entities)


class BixbitNumber(BixbitEntity, NumberEntity):
    """Representation of a Bixbit number entity."""

    entity_description: BixbitNumberEntityDescription

    def __init__(
        self,
        coordinator: BixbitCoordinator,
        description: BixbitNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        await self.entity_description.set_fn(self.coordinator.api, value)
        await self.coordinator.async_request_refresh()


class BixbitPowerLimitNumber(BixbitEntity, NumberEntity):
    """Number entity for the user power limit that reads current power mode from coordinator."""

    _attr_icon = "mdi:lightning-bolt"
    _attr_native_min_value = 0
    _attr_native_max_value = 10000
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.BOX
    _attr_translation_key = "user_power_limit"

    def __init__(self, coordinator: BixbitCoordinator) -> None:
        super().__init__(coordinator, "user_power_limit")

    @property
    def native_value(self) -> float | None:
        return _to_float(self.coordinator.data.get("power_limit", {}).get("powerLimit"))

    async def async_set_native_value(self, value: float) -> None:
        current_mode = self.coordinator.data.get("power_limit", {}).get("powerMode", "Normal")
        await self.coordinator.api.set_user_power_limit(
            power_mode=current_mode,
            power_limit=int(value),
        )
        await self.coordinator.async_request_refresh()
