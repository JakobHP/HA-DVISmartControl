"""Base entity for DVI Smart Control."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DviSmartControlCoordinator


class DviSmartControlEntity(CoordinatorEntity[DviSmartControlCoordinator]):
    """Base entity for DVI Smart Control integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DviSmartControlCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="DVI Heat Pump",
            manufacturer="DVI Energi",
            model="SmartControl",
            sw_version=coordinator.data.get("software_version"),
        )
