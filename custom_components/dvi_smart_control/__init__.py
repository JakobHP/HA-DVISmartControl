"""DVI Smart Control integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DviSmartControlApiClient
from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_URL, DOMAIN
from .coordinator import DviSmartControlConfigEntry, DviSmartControlCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: DviSmartControlConfigEntry
) -> bool:
    """Set up DVI Smart Control from a config entry."""
    session = async_get_clientsession(hass)
    client = DviSmartControlApiClient(
        session=session,
        base_url=DEFAULT_URL,
        username=entry.data["email"],
        password=entry.data["password"],
    )

    coordinator = DviSmartControlCoordinator(
        hass=hass,
        entry=entry,
        client=client,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DviSmartControlConfigEntry
) -> bool:
    """Unload a DVI Smart Control config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
