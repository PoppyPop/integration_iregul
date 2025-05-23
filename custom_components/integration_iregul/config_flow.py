"""Config flow for IRegul integration."""

from __future__ import annotations

import logging
from typing import Any

import aioiregul
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import CONF_PASSWORD
from .const import CONF_UPDATE_INTERVAL
from .const import CONF_USERNAME
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .coordinator import CannotConnect
from .coordinator import InvalidAuth

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        CONF_USERNAME: str,
        CONF_PASSWORD: str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values
    provided by the user.
    """

    connOpt = aioiregul.ConnectionOptions(data[CONF_USERNAME], data[CONF_PASSWORD])
    aioiregul.Device(connOpt)

    hub = aioiregul.Device(connOpt)
    session = async_create_clientsession(hass)

    if not await hub.authenticate(session):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "IRegul"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IRegul."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

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
