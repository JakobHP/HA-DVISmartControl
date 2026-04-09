"""Switch platform for DVI Smart Control."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_COMPRESSOR_RUNNING,
    KEY_FAN_RUNNING,
    KEY_HEATING_SYSTEM_STATE,
    KEY_HOT_WATER_STATE,
    SETTING_HEATING_SYSTEM,
    SETTING_HOT_WATER,
)
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator
from .entity import DviSmartControlEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DviSmartControlSwitchEntityDescription(SwitchEntityDescription):
    """Describe a DVI Smart Control switch."""

    state_key: str
    setting_id: str
    on_value: str
    off_value: str


SWITCH_DESCRIPTIONS: tuple[DviSmartControlSwitchEntityDescription, ...] = (
    DviSmartControlSwitchEntityDescription(
        key="heating_system",
        translation_key="heating_system",
        icon="mdi:radiator",
        state_key=KEY_HEATING_SYSTEM_STATE,
        setting_id=SETTING_HEATING_SYSTEM,
        on_value="1",
        off_value="0",
    ),
    DviSmartControlSwitchEntityDescription(
        key="hot_water",
        translation_key="hot_water",
        icon="mdi:water-boiler",
        state_key=KEY_HOT_WATER_STATE,
        setting_id=SETTING_HOT_WATER,
        on_value="1",
        off_value="0",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DviSmartControlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DVI Smart Control switches."""
    coordinator = entry.runtime_data
    entities: list[SwitchEntity] = [
        DviSmartControlSwitch(coordinator, description)
        for description in SWITCH_DESCRIPTIONS
    ]
    entities.append(DviSmartControlPumpPowerSwitch(coordinator))
    async_add_entities(entities)


class DviSmartControlSwitch(DviSmartControlEntity, SwitchEntity):
    """Representation of a DVI Smart Control setting switch."""

    entity_description: DviSmartControlSwitchEntityDescription

    def __init__(
        self,
        coordinator: DviSmartControlCoordinator,
        description: DviSmartControlSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        return self.coordinator.data.get(self.entity_description.state_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        desc = self.entity_description
        await self.coordinator.client.async_set_user_setting(
            desc.setting_id, desc.on_value
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        desc = self.entity_description
        await self.coordinator.client.async_set_user_setting(
            desc.setting_id, desc.off_value
        )
        await self.coordinator.async_request_refresh()


class DviSmartControlPumpPowerSwitch(DviSmartControlEntity, SwitchEntity):
    """Switch to control the heat pump power on/off."""

    _attr_translation_key = "pump_power"
    _attr_icon = "mdi:heat-pump-outline"
    _attr_assumed_state = True

    def __init__(self, coordinator: DviSmartControlCoordinator) -> None:
        """Initialize the pump power switch."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pump_power"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if pump appears to be running.

        Since there is no direct on/off state endpoint, we infer from
        whether the compressor or fan data indicates activity. This is
        an approximation — assumed_state is True.
        """
        data = self.coordinator.data
        compressor = data.get(KEY_COMPRESSOR_RUNNING)
        fan = data.get(KEY_FAN_RUNNING)
        # If either is True the pump is definitely on.
        # If both are False we can't be sure (it could be idle but on).
        # Return None if we have no data at all.
        if compressor is None and fan is None:
            return None
        return bool(compressor) or bool(fan)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the pump on."""
        await self.coordinator.client.async_turn_pump_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the pump off."""
        await self.coordinator.client.async_turn_pump_off()
        await self.coordinator.async_request_refresh()
