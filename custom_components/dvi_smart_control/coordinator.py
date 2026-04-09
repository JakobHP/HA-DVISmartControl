"""DataUpdateCoordinator for DVI Smart Control."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    DviSmartControlApiClient,
    DviSmartControlAuthError,
    DviSmartControlConnectionError,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

type DviSmartControlConfigEntry = ConfigEntry[DviSmartControlCoordinator]


class DviSmartControlCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that manages data polling from the DVI portal."""

    config_entry: DviSmartControlConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: DviSmartControlConfigEntry,
        client: DviSmartControlApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data from the portal."""
        try:
            data = await self.client.async_get_all_data()
        except DviSmartControlAuthError as err:
            # Auth errors should trigger re-configuration
            raise ConfigEntryAuthFailed(
                f"Authentication failed: {err}"
            ) from err
        except DviSmartControlConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"HTTP error: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout fetching data: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        return data
