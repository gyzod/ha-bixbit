"""Switch platform for Bixbit Miner."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BixbitConfigEntry
from .api import BixbitApi
from .coordinator import BixbitCoordinator
from .entity import BixbitEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BixbitSwitchEntityDescription(SwitchEntityDescription):
    """Describe a Bixbit switch."""

    is_on_fn: Callable[[dict[str, Any]], bool | None]
    turn_on_fn: Callable[[BixbitApi], Coroutine[Any, Any, Any]]
    turn_off_fn: Callable[[BixbitApi], Coroutine[Any, Any, Any]]


def _str_to_bool(val: Any) -> bool | None:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    return str(val).lower() == "true"


SWITCH_DESCRIPTIONS: tuple[BixbitSwitchEntityDescription, ...] = (
    BixbitSwitchEntityDescription(
        key="deep_power",
        translation_key="deep_power",
        icon="mdi:power",
        is_on_fn=lambda d: not _str_to_bool(
            d.get("power_status", {}).get("deep_suspend")
        ),
        turn_on_fn=lambda api: api.deep_power_on(),
        turn_off_fn=lambda api: api.deep_power_off(),
    ),
    BixbitSwitchEntityDescription(
        key="liquid_cooling",
        translation_key="liquid_cooling",
        icon="mdi:coolant-temperature",
        is_on_fn=lambda d: _str_to_bool(
            d.get("liquid_cooling", {}).get("liquid_cooling")
        ),
        turn_on_fn=lambda api: api.set_liquid_cooling(True),
        turn_off_fn=lambda api: api.set_liquid_cooling(False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BixbitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bixbit switches."""
    coordinator = entry.runtime_data
    async_add_entities(
        BixbitSwitch(coordinator, desc) for desc in SWITCH_DESCRIPTIONS
    )


class BixbitSwitch(BixbitEntity, SwitchEntity):
    """Representation of a Bixbit switch."""

    entity_description: BixbitSwitchEntityDescription

    def __init__(
        self,
        coordinator: BixbitCoordinator,
        description: BixbitSwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.entity_description.turn_on_fn(self.coordinator.api)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.entity_description.turn_off_fn(self.coordinator.api)
        await self.coordinator.async_request_refresh()
