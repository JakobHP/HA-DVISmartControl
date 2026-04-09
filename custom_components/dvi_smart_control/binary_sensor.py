"""Binary sensor platform for DVI Smart Control."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_COMPRESSOR_RUNNING,
    KEY_CURRENT_ERRORS,
    KEY_FAN_RUNNING,
    KEY_SUPPLEMENTARY_HEATER_RUNNING,
)
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator
from .entity import DviSmartControlEntity


@dataclass(frozen=True, kw_only=True)
class DviSmartControlBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a DVI Smart Control binary sensor."""

    is_on_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[
    DviSmartControlBinarySensorEntityDescription, ...
] = (
    DviSmartControlBinarySensorEntityDescription(
        key="compressor_running",
        translation_key="compressor_running",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.get(KEY_COMPRESSOR_RUNNING),
    ),
    DviSmartControlBinarySensorEntityDescription(
        key="fan_running",
        translation_key="fan_running",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.get(KEY_FAN_RUNNING),
    ),
    DviSmartControlBinarySensorEntityDescription(
        key="supplementary_heater_running",
        translation_key="supplementary_heater_running",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: data.get(KEY_SUPPLEMENTARY_HEATER_RUNNING),
    ),
    DviSmartControlBinarySensorEntityDescription(
        key="has_errors",
        translation_key="has_errors",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: bool(data.get(KEY_CURRENT_ERRORS)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DviSmartControlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DVI Smart Control binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        DviSmartControlBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class DviSmartControlBinarySensor(DviSmartControlEntity, BinarySensorEntity):
    """Representation of a DVI Smart Control binary sensor."""

    entity_description: DviSmartControlBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DviSmartControlCoordinator,
        description: DviSmartControlBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self.coordinator.data)
