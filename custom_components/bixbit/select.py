"""Select platform for Bixbit Miner."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BixbitConfigEntry
from .api import BixbitApi
from .coordinator import BixbitCoordinator
from .entity import BixbitEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BixbitSelectEntityDescription(SelectEntityDescription):
    """Describe a Bixbit select entity."""

    value_fn: Callable[[dict[str, Any]], str | None]
    set_fn: Callable[[BixbitApi, str], Coroutine[Any, Any, Any]]


SELECT_DESCRIPTIONS: tuple[BixbitSelectEntityDescription, ...] = (
    BixbitSelectEntityDescription(
        key="fan_mode",
        translation_key="fan_mode",
        icon="mdi:fan",
        options=["auto", "manual"],
        value_fn=lambda d: d.get("fan_mode", {}).get("fan_mode"),
        set_fn=lambda api, val: api.set_fan_mode(val),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BixbitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bixbit select entities."""
    coordinator = entry.runtime_data
    entities: list[SelectEntity] = [
        BixbitSelect(coordinator, desc) for desc in SELECT_DESCRIPTIONS
    ]
    entities.append(BixbitPowerModeSelect(coordinator))
    async_add_entities(entities)


class BixbitSelect(BixbitEntity, SelectEntity):
    """Representation of a Bixbit select entity."""

    entity_description: BixbitSelectEntityDescription

    def __init__(
        self,
        coordinator: BixbitCoordinator,
        description: BixbitSelectEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def current_option(self) -> str | None:
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        await self.entity_description.set_fn(self.coordinator.api, option)
        await self.coordinator.async_request_refresh()


class BixbitPowerModeSelect(BixbitEntity, SelectEntity):
    """Select entity for power mode that reads current power limit from coordinator."""

    _attr_icon = "mdi:lightning-bolt-circle"
    _attr_options = ["Low", "Normal", "High"]
    _attr_translation_key = "power_mode"

    def __init__(self, coordinator: BixbitCoordinator) -> None:
        super().__init__(coordinator, "power_mode")

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.get("power_limit", {}).get("powerMode")

    async def async_select_option(self, option: str) -> None:
        current_limit = self.coordinator.data.get("power_limit", {}).get("powerLimit", 0)
        await self.coordinator.api.set_user_power_limit(
            power_mode=option,
            power_limit=current_limit,
        )
        await self.coordinator.async_request_refresh()
