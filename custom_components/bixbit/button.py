"""Button platform for Bixbit Miner."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BixbitConfigEntry
from .api import BixbitApi
from .coordinator import BixbitCoordinator
from .entity import BixbitEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BixbitButtonEntityDescription(ButtonEntityDescription):
    """Describe a Bixbit button entity."""

    press_fn: Callable[[BixbitApi], Coroutine[Any, Any, Any]]


BUTTON_DESCRIPTIONS: tuple[BixbitButtonEntityDescription, ...] = (
    BixbitButtonEntityDescription(
        key="delete_overclock",
        translation_key="delete_overclock",
        icon="mdi:delete",
        press_fn=lambda api: api.delete_overclock_info(),
    ),
    BixbitButtonEntityDescription(
        key="reset_recovery_reboots",
        translation_key="reset_recovery_reboots",
        icon="mdi:restart",
        press_fn=lambda api: api.reset_recovery_reboots(),
    ),
    BixbitButtonEntityDescription(
        key="delete_upfreq_results",
        translation_key="delete_upfreq_results",
        icon="mdi:delete-sweep",
        press_fn=lambda api: api.delete_upfreq_results(),
    ),
    BixbitButtonEntityDescription(
        key="generate_profiles",
        translation_key="generate_profiles",
        icon="mdi:auto-fix",
        press_fn=lambda api: api.generate_profiles(),
    ),
    BixbitButtonEntityDescription(
        key="stop_profiles_generation",
        translation_key="stop_profiles_generation",
        icon="mdi:stop",
        press_fn=lambda api: api.stop_profiles_generation(),
    ),
    BixbitButtonEntityDescription(
        key="delete_generated_profiles",
        translation_key="delete_generated_profiles",
        icon="mdi:delete-variant",
        press_fn=lambda api: api.delete_generated_profiles(),
    ),
    BixbitButtonEntityDescription(
        key="upgrade_psu_firmware",
        translation_key="upgrade_psu_firmware",
        icon="mdi:update",
        press_fn=lambda api: api.upgrade_psu_firmware(),
    ),
    BixbitButtonEntityDescription(
        key="reset_mac",
        translation_key="reset_mac",
        icon="mdi:ethernet",
        press_fn=lambda api: api.reset_mac(),
    ),
    BixbitButtonEntityDescription(
        key="ams_uninstall",
        translation_key="ams_uninstall",
        icon="mdi:cloud-off-outline",
        press_fn=lambda api: api.ams_uninstall(),
    ),
    BixbitButtonEntityDescription(
        key="deep_power_on",
        translation_key="deep_power_on",
        icon="mdi:power",
        press_fn=lambda api: api.deep_power_on(),
    ),
    BixbitButtonEntityDescription(
        key="deep_power_off",
        translation_key="deep_power_off",
        icon="mdi:power-off",
        press_fn=lambda api: api.deep_power_off(),
    ),
    BixbitButtonEntityDescription(
        key="overclock_low",
        translation_key="overclock_low",
        icon="mdi:speedometer-slow",
        press_fn=lambda api: api.apply_overclock_profile(
            board_temp_target=80, freq_target=450,
            power_limit=1300, power_max=1500,
            voltage_limit=1200, voltage_min=1050, voltage_target=1179,
            fan_mode=1, manual_fan_speed_percent=100,
            boards_cool_fan_percent=100,
            additional_psu=False, liquid_cooling=False,
        ),
    ),
    BixbitButtonEntityDescription(
        key="overclock_medium",
        translation_key="overclock_medium",
        icon="mdi:speedometer-medium",
        press_fn=lambda api: api.apply_overclock_profile(
            board_temp_target=80, freq_target=555,
            power_limit=2000, power_max=2300,
            voltage_limit=1300, voltage_min=1050, voltage_target=1190,
            fan_mode=1, manual_fan_speed_percent=100,
            boards_cool_fan_percent=100,
            additional_psu=False, liquid_cooling=False,
        ),
    ),
    BixbitButtonEntityDescription(
        key="overclock_medium_high",
        translation_key="overclock_medium_high",
        icon="mdi:speedometer",
        press_fn=lambda api: api.apply_overclock_profile(
            board_temp_target=80, freq_target=555,
            power_limit=2800, power_max=3000,
            voltage_limit=1300, voltage_min=1050, voltage_target=1190,
            fan_mode=1, manual_fan_speed_percent=100,
            boards_cool_fan_percent=100,
            additional_psu=False, liquid_cooling=False,
        ),
    ),
    BixbitButtonEntityDescription(
        key="overclock_high",
        translation_key="overclock_high",
        icon="mdi:speedometer",
        press_fn=lambda api: api.apply_overclock_profile(
            board_temp_target=80, freq_target=632,
            power_limit=3300, power_max=3600,
            voltage_limit=1420, voltage_min=1050, voltage_target=1190,
            fan_mode=1, manual_fan_speed_percent=100,
            boards_cool_fan_percent=100,
            additional_psu=False, liquid_cooling=False,
        ),
    ),
    BixbitButtonEntityDescription(
        key="overclock_very_high",
        translation_key="overclock_very_high",
        icon="mdi:flash-alert",
        press_fn=lambda api: api.apply_overclock_profile(
            board_temp_target=82, freq_target=665,
            power_limit=3600, power_max=3900,
            voltage_limit=1450, voltage_min=1050, voltage_target=1190,
            fan_mode=1, manual_fan_speed_percent=100,
            boards_cool_fan_percent=100,
            additional_psu=False, liquid_cooling=False,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BixbitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bixbit buttons."""
    coordinator = entry.runtime_data
    async_add_entities(
        BixbitButton(coordinator, desc) for desc in BUTTON_DESCRIPTIONS
    )


class BixbitButton(BixbitEntity, ButtonEntity):
    """Representation of a Bixbit button."""

    entity_description: BixbitButtonEntityDescription

    def __init__(
        self,
        coordinator: BixbitCoordinator,
        description: BixbitButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator.api)
        await self.coordinator.async_request_refresh()
