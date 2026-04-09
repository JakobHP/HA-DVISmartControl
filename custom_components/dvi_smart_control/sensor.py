"""Sensor platform for DVI Smart Control."""
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
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_COMPRESSOR_HOURS,
    KEY_CURRENT_ERRORS,
    KEY_ENERGY_CONSUMED_KW,
    KEY_ENERGY_CONSUMED_KWH,
    KEY_ENERGY_DELIVERED_KW,
    KEY_ENERGY_DELIVERED_KWH,
    KEY_FLOW_RATE,
    KEY_HEATING_FLOW_TEMP,
    KEY_HEATING_RETURN_TEMP,
    KEY_HOT_WATER_HOURS,
    KEY_HOT_WATER_TEMP,
    KEY_LAST_UPDATE,
    KEY_OUTDOOR_TEMP,
    KEY_ROOM_TEMP,
    KEY_SUPPLEMENTARY_HEAT_HOURS,
    KEY_TANK_TEMP,
)
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator
from .entity import DviSmartControlEntity


@dataclass(frozen=True, kw_only=True)
class DviSmartControlSensorEntityDescription(SensorEntityDescription):
    """Describe a DVI Smart Control sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


def _format_errors(data: dict[str, Any]) -> str | None:
    """Format error list as a string."""
    errors = data.get(KEY_CURRENT_ERRORS)
    if errors is None:
        return None
    if not errors:
        return "No errors"
    return ", ".join(errors)


SENSOR_DESCRIPTIONS: tuple[DviSmartControlSensorEntityDescription, ...] = (
    # ── Temperatures ──
    DviSmartControlSensorEntityDescription(
        key=KEY_OUTDOOR_TEMP,
        translation_key="outdoor_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_OUTDOOR_TEMP),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_TANK_TEMP,
        translation_key="tank_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_TANK_TEMP),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_HOT_WATER_TEMP,
        translation_key="hot_water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_HOT_WATER_TEMP),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_HEATING_FLOW_TEMP,
        translation_key="heating_flow_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_HEATING_FLOW_TEMP),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_HEATING_RETURN_TEMP,
        translation_key="heating_return_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_HEATING_RETURN_TEMP),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_ROOM_TEMP,
        translation_key="room_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_ROOM_TEMP),
    ),
    # ── Hour counters ──
    DviSmartControlSensorEntityDescription(
        key=KEY_COMPRESSOR_HOURS,
        translation_key="compressor_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer",
        value_fn=lambda data: data.get(KEY_COMPRESSOR_HOURS),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_HOT_WATER_HOURS,
        translation_key="hot_water_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer",
        value_fn=lambda data: data.get(KEY_HOT_WATER_HOURS),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_SUPPLEMENTARY_HEAT_HOURS,
        translation_key="supplementary_heat_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer",
        value_fn=lambda data: data.get(KEY_SUPPLEMENTARY_HEAT_HOURS),
    ),
    # ── Energy meters ──
    DviSmartControlSensorEntityDescription(
        key=KEY_ENERGY_CONSUMED_KWH,
        translation_key="energy_consumed_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(KEY_ENERGY_CONSUMED_KWH),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_ENERGY_CONSUMED_KW,
        translation_key="energy_consumed_kw",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_ENERGY_CONSUMED_KW),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_ENERGY_DELIVERED_KWH,
        translation_key="energy_delivered_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(KEY_ENERGY_DELIVERED_KWH),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_ENERGY_DELIVERED_KW,
        translation_key="energy_delivered_kw",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(KEY_ENERGY_DELIVERED_KW),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_FLOW_RATE,
        translation_key="flow_rate",
        native_unit_of_measurement="L/h",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-pump",
        value_fn=lambda data: data.get(KEY_FLOW_RATE),
    ),
    # ── Other ──
    DviSmartControlSensorEntityDescription(
        key=KEY_LAST_UPDATE,
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.get(KEY_LAST_UPDATE),
    ),
    DviSmartControlSensorEntityDescription(
        key=KEY_CURRENT_ERRORS,
        translation_key="current_errors",
        icon="mdi:alert-circle",
        value_fn=_format_errors,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DviSmartControlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DVI Smart Control sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        DviSmartControlSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class DviSmartControlSensor(DviSmartControlEntity, SensorEntity):
    """Representation of a DVI Smart Control sensor."""

    entity_description: DviSmartControlSensorEntityDescription

    def __init__(
        self,
        coordinator: DviSmartControlCoordinator,
        description: DviSmartControlSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
