"""Config flow for IRegul integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_ID, CONF_DEVICE_KEY
from .const import CONF_UPDATE_INTERVAL
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .coordinator import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        CONF_HOST: str,
        vol.Optional(CONF_PORT, default=80): int,
        CONF_DEVICE_ID: str,
        CONF_DEVICE_KEY: str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input. For now, basic validation only."""
    # In absence of a device to contact during config, accept inputs.
    # Future enhancement: instantiate client and test `get_data`.
    if not data.get(CONF_HOST) or not data.get(CONF_DEVICE_ID) or not data.get(CONF_DEVICE_KEY):
        raise InvalidAuth
    return {"title": "IRegul"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IRegul."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors: dict[str, str] = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Avoid duplicates per device_id
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for iregul."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )

        optSchem = vol.Schema(
            {
                vol.Optional(CONF_UPDATE_INTERVAL, default=scan_interval): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=optSchem)

    async def async_step_abort(self, user_input=None):
        """Abort options flow."""
        return self.async_create_entry(title="", data=self.config_entry.options)
