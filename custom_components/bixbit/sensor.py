"""Sensor platform for Bixbit Miner."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BixbitConfigEntry
from .coordinator import BixbitCoordinator
from .entity import BixbitEntity


def _get_summary(data: dict[str, Any], key: str) -> Any:
    """Get a value from the normalized summary data."""
    return data.get("summary", {}).get(key)


@dataclass(frozen=True, kw_only=True)
class BixbitSensorEntityDescription(SensorEntityDescription):
    """Describe a Bixbit sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[BixbitSensorEntityDescription, ...] = (
    # ─── Power & Hashrate ───────────────────────────────────────
    BixbitSensorEntityDescription(
        key="hashrate_ghs",
        translation_key="hashrate_ghs",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda d: _get_summary(d, "GHS 5s"),
    ),
    BixbitSensorEntityDescription(
        key="hashrate_avg",
        translation_key="hashrate_avg",
        native_unit_of_measurement="GH/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda d: _get_summary(d, "GHS av"),
    ),
    BixbitSensorEntityDescription(
        key="factory_ghs",
        translation_key="factory_ghs",
        native_unit_of_measurement="GH/s",
        icon="mdi:speedometer",
        value_fn=lambda d: _get_summary(d, "Factory GHS"),
    ),
    BixbitSensorEntityDescription(
        key="power_realtime",
        translation_key="power_realtime",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "Power Realtime"),
    ),
    # ─── Temperatures ───────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="temp_chip_protect",
        translation_key="temp_chip_protect",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-alert",
        value_fn=lambda d: _get_summary(d, "Chip Temp Protect"),
    ),
    BixbitSensorEntityDescription(
        key="temp_chip_target",
        translation_key="temp_chip_target",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        value_fn=lambda d: _get_summary(d, "Chip Temp Target"),
    ),
    BixbitSensorEntityDescription(
        key="psu_temp0",
        translation_key="psu_temp0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Temp0"),
    ),
    BixbitSensorEntityDescription(
        key="psu_temp1",
        translation_key="psu_temp1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Temp1"),
    ),
    # ─── PSU ────────────────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="psu_vout",
        translation_key="psu_vout",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Vout"),
    ),
    BixbitSensorEntityDescription(
        key="psu_iout",
        translation_key="psu_iout",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Iout"),
    ),
    BixbitSensorEntityDescription(
        key="psu_vin0",
        translation_key="psu_vin0",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Vin0"),
    ),
    BixbitSensorEntityDescription(
        key="psu_iin0",
        translation_key="psu_iin0",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "PSU Iin0"),
    ),
    BixbitSensorEntityDescription(
        key="psu_fan_speed",
        translation_key="psu_fan_speed",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="RPM",
        value_fn=lambda d: _get_summary(d, "PSU Fan Speed"),
    ),
    BixbitSensorEntityDescription(
        key="psu_serial",
        translation_key="psu_serial",
        icon="mdi:identifier",
        value_fn=lambda d: _get_summary(d, "PSU Serial No"),
    ),
    BixbitSensorEntityDescription(
        key="psu_name",
        translation_key="psu_name",
        icon="mdi:power-plug",
        value_fn=lambda d: _get_summary(d, "PSU Name"),
    ),
    # ─── Device Info ────────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:information",
        value_fn=lambda d: _get_summary(d, "Status"),
    ),
    BixbitSensorEntityDescription(
        key="miner_type",
        translation_key="miner_type",
        icon="mdi:chip",
        value_fn=lambda d: _get_summary(d, "Miner Type"),
    ),
    BixbitSensorEntityDescription(
        key="miner_memory_usage",
        translation_key="miner_memory_usage",
        icon="mdi:memory",
        native_unit_of_measurement="MB",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_summary(d, "Miner Memory Usage"),
    ),
    BixbitSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        icon="mdi:update",
        value_fn=lambda d: d.get("firmware", {}).get("firmware_version"),
    ),
    BixbitSensorEntityDescription(
        key="custom_version",
        translation_key="custom_version",
        icon="mdi:update",
        value_fn=lambda d: d.get("firmware", {}).get("custom_version"),
    ),
    # ─── Fan ────────────────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="fan_mode",
        translation_key="fan_mode_sensor",
        icon="mdi:fan",
        value_fn=lambda d: d.get("fan_mode", {}).get("fan_mode"),
    ),
    BixbitSensorEntityDescription(
        key="manual_fan_speed",
        translation_key="manual_fan_speed",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("fan_mode", {}).get("manual_fan_speed_percent"),
    ),
    # ─── Power Mode ─────────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="power_mode",
        translation_key="power_mode_sensor",
        icon="mdi:lightning-bolt",
        value_fn=lambda d: d.get("power_limit", {}).get("powerMode"),
    ),
    BixbitSensorEntityDescription(
        key="power_limit",
        translation_key="power_limit_sensor",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("power_limit", {}).get("powerLimit"),
    ),
    # ─── Power Status ───────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="suspended",
        translation_key="suspended",
        icon="mdi:pause-circle",
        value_fn=lambda d: d.get("power_status", {}).get("suspend"),
    ),
    BixbitSensorEntityDescription(
        key="deep_suspended",
        translation_key="deep_suspended",
        icon="mdi:sleep",
        value_fn=lambda d: d.get("power_status", {}).get("deep_suspend"),
    ),
    # ─── Cooling Mode ───────────────────────────────────────────
    BixbitSensorEntityDescription(
        key="cool_mode",
        translation_key="cool_mode",
        icon="mdi:snowflake",
        value_fn=lambda d: d.get("liquid_cooling", {}).get("cool_mode"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BixbitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bixbit sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        BixbitSensor(coordinator, desc) for desc in SENSOR_DESCRIPTIONS
    )


class BixbitSensor(BixbitEntity, SensorEntity):
    """Representation of a Bixbit sensor."""

    entity_description: BixbitSensorEntityDescription

    def __init__(
        self,
        coordinator: BixbitCoordinator,
        description: BixbitSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
