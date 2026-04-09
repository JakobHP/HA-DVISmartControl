"""Number platform for DVI Smart Control."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_HEATING_TEMP_OFFSET_VALUE,
    KEY_HOT_WATER_TEMP_SETPOINT,
    SETTING_HEATING_TEMP_OFFSET,
    SETTING_HOT_WATER_TEMP,
)
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator
from .entity import DviSmartControlEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DviSmartControlNumberEntityDescription(NumberEntityDescription):
    """Describe a DVI Smart Control number entity."""

    state_key: str
    setting_id: str


NUMBER_DESCRIPTIONS: tuple[DviSmartControlNumberEntityDescription, ...] = (
    DviSmartControlNumberEntityDescription(
        key="heating_temp_offset",
        translation_key="heating_temp_offset",
        icon="mdi:thermometer-plus",
        native_min_value=0,
        native_max_value=20,
        native_step=1,
        mode=NumberMode.SLIDER,
        state_key=KEY_HEATING_TEMP_OFFSET_VALUE,
        setting_id=SETTING_HEATING_TEMP_OFFSET,
    ),
    DviSmartControlNumberEntityDescription(
        key="hot_water_temp_setpoint",
        translation_key="hot_water_temp_setpoint",
        icon="mdi:water-thermometer",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=5,
        native_max_value=55,
        native_step=1,
        mode=NumberMode.SLIDER,
        state_key=KEY_HOT_WATER_TEMP_SETPOINT,
        setting_id=SETTING_HOT_WATER_TEMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DviSmartControlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DVI Smart Control number entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DviSmartControlNumber(coordinator, description)
        for description in NUMBER_DESCRIPTIONS
    )


class DviSmartControlNumber(DviSmartControlEntity, NumberEntity):
    """Representation of a DVI Smart Control number entity."""

    entity_description: DviSmartControlNumberEntityDescription

    def __init__(
        self,
        coordinator: DviSmartControlCoordinator,
        description: DviSmartControlNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self.entity_description.state_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        desc = self.entity_description
        await self.coordinator.client.async_set_user_setting(
            desc.setting_id, int(value)
        )
        await self.coordinator.async_request_refresh()
