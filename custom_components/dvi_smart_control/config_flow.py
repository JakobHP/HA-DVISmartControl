"""Config flow for DVI Smart Control."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    DviSmartControlApiClient,
    DviSmartControlAuthError,
    DviSmartControlConnectionError,
)
from .const import DEFAULT_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class DviSmartControlConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DVI Smart Control."""

    VERSION = 1

    async def _validate_credentials(
        self, email: str, password: str
    ) -> dict[str, str]:
        """Validate credentials and return errors dict (empty on success)."""
        session = async_get_clientsession(self.hass)
        client = DviSmartControlApiClient(session, DEFAULT_URL, email, password)

        try:
            await client.authenticate()
        except DviSmartControlAuthError:
            return {"base": "invalid_auth"}
        except DviSmartControlConnectionError:
            return {"base": "cannot_connect"}
        except Exception:
            _LOGGER.exception("Unexpected error during validation")
            return {"base": "unknown"}

        return {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            await self.async_set_unique_id(email.lower())
            self._abort_if_unique_id_configured()

            errors = await self._validate_credentials(email, password)
            if not errors:
                return self.async_create_entry(
                    title="DVI Smart Control",
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauth triggered by ConfigEntryAuthFailed."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauth confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            errors = await self._validate_credentials(email, password)
            if not errors:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=USER_SCHEMA,
            errors=errors,
        )
