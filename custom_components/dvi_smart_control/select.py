"""Select platform for DVI Smart Control."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_HOT_WATER_CLOCK_STATE,
    KEY_SUPPLEMENTARY_HEATING_STATE,
    SETTING_HOT_WATER_CLOCK,
    SETTING_SUPPLEMENTARY_HEATING,
)
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator
from .entity import DviSmartControlEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DviSmartControlSelectEntityDescription(SelectEntityDescription):
    """Describe a DVI Smart Control select entity."""

    state_key: str
    setting_id: str
    # Map portal value (str) -> HA option label
    value_to_option: dict[str, str]
    # Map HA option label -> portal value (str)
    option_to_value: dict[str, str]


SUPPLEMENTARY_VALUE_TO_OPTION = {"0": "off", "1": "automatic", "2": "reserve"}
SUPPLEMENTARY_OPTION_TO_VALUE = {v: k for k, v in SUPPLEMENTARY_VALUE_TO_OPTION.items()}

HOT_WATER_CLOCK_VALUE_TO_OPTION = {
    "0": "clock",
    "1": "constant_on",
    "2": "constant_off",
}
HOT_WATER_CLOCK_OPTION_TO_VALUE = {
    v: k for k, v in HOT_WATER_CLOCK_VALUE_TO_OPTION.items()
}

SELECT_DESCRIPTIONS: tuple[DviSmartControlSelectEntityDescription, ...] = (
    DviSmartControlSelectEntityDescription(
        key="supplementary_heating_mode",
        translation_key="supplementary_heating_mode",
        icon="mdi:heating-coil",
        options=list(SUPPLEMENTARY_VALUE_TO_OPTION.values()),
        state_key=KEY_SUPPLEMENTARY_HEATING_STATE,
        setting_id=SETTING_SUPPLEMENTARY_HEATING,
        value_to_option=SUPPLEMENTARY_VALUE_TO_OPTION,
        option_to_value=SUPPLEMENTARY_OPTION_TO_VALUE,
    ),
    DviSmartControlSelectEntityDescription(
        key="hot_water_clock_mode",
        translation_key="hot_water_clock_mode",
        icon="mdi:clock-outline",
        options=list(HOT_WATER_CLOCK_VALUE_TO_OPTION.values()),
        state_key=KEY_HOT_WATER_CLOCK_STATE,
        setting_id=SETTING_HOT_WATER_CLOCK,
        value_to_option=HOT_WATER_CLOCK_VALUE_TO_OPTION,
        option_to_value=HOT_WATER_CLOCK_OPTION_TO_VALUE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DviSmartControlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DVI Smart Control select entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DviSmartControlSelect(coordinator, description)
        for description in SELECT_DESCRIPTIONS
    )


class DviSmartControlSelect(DviSmartControlEntity, SelectEntity):
    """Representation of a DVI Smart Control select entity."""

    entity_description: DviSmartControlSelectEntityDescription

    def __init__(
        self,
        coordinator: DviSmartControlCoordinator,
        description: DviSmartControlSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        value = self.coordinator.data.get(self.entity_description.state_key)
        if value is None:
            return None
        return self.entity_description.value_to_option.get(str(value))

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        desc = self.entity_description
        value = desc.option_to_value.get(option)
        if value is None:
            _LOGGER.error("Unknown option %s for %s", option, desc.key)
            return
        await self.coordinator.client.async_set_user_setting(
            desc.setting_id, value
        )
        await self.coordinator.async_request_refresh()
