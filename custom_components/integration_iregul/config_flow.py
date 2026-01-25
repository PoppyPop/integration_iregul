"""Config flow for IRegul integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback

from .const import (
    API_VERSION_V1,
    API_VERSION_V2,
    CONF_API_VERSION,
    CONF_DEVICE_ID,
    CONF_DEVICE_PASSWORD,
    CONF_SERIAL_NUMBER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_API_VERSION,
    DEFAULT_UPDATE_INTERVAL_V1,
    DEFAULT_UPDATE_INTERVAL_V2,
    DOMAIN,
)
from .coordinator import CannotConnect, InvalidAuth, IRegulCoordinator

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_VERSION, default=DEFAULT_API_VERSION): vol.In(
            [API_VERSION_V1, API_VERSION_V2]
        ),
        vol.Required(CONF_SERIAL_NUMBER): str,
    }
)

STEP_CREDENTIALS_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input by testing connection to device."""
    device_id = data.get(CONF_DEVICE_ID) or data.get(CONF_SERIAL_NUMBER)
    password = data.get(CONF_DEVICE_PASSWORD)
    api_version = data.get(CONF_API_VERSION, DEFAULT_API_VERSION)

    if not device_id or not password:
        raise InvalidAuth

    # Test the connection by creating client and fetching data
    try:
        client = IRegulCoordinator.create_client(
            hass,
            device_id,
            password,
            api_version,
        )
        # Test the connection by fetching data
        await client.check_auth()
    except Exception as err:
        _LOGGER.error("Failed to validate credentials: %s", err)
        raise CannotConnect from err

    return {"title": "IRegul"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IRegul."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow state."""
        self._device_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        self._device_data = user_input

        await self.async_set_unique_id(user_input[CONF_SERIAL_NUMBER])
        self._abort_if_unique_id_configured()

        return await self.async_step_credentials()

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the credentials step."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="credentials",
                data_schema=STEP_CREDENTIALS_SCHEMA,
            )

        full_input = {**self._device_data, **user_input}
        full_input[CONF_DEVICE_ID] = full_input.pop(CONF_SERIAL_NUMBER)
        full_input[CONF_DEVICE_PASSWORD] = full_input[CONF_PASSWORD]

        # Set default update interval based on API version
        api_version = full_input.get(CONF_API_VERSION, API_VERSION_V2)
        full_input[CONF_UPDATE_INTERVAL] = (
            DEFAULT_UPDATE_INTERVAL_V1
            if api_version == API_VERSION_V1
            else DEFAULT_UPDATE_INTERVAL_V2
        )

        try:
            info = await validate_input(self.hass, full_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=full_input)

        return self.async_show_form(
            step_id="credentials", data_schema=STEP_CREDENTIALS_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry[Any],
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for iregul."""

    def __init__(self, config_entry: config_entries.ConfigEntry[Any]) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Handle options flow."""
        if user_input is not None:
            new_data = {
                **self.config_entry.data,
                CONF_DEVICE_PASSWORD: user_input[CONF_PASSWORD],
                CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
            }
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(
                title="",
                data={
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                },
            )

        current_password = self.config_entry.options.get(
            CONF_PASSWORD, self.config_entry.data.get(CONF_DEVICE_PASSWORD, "")
        )

        # Get current update interval or use default based on API version
        api_version = self.config_entry.data.get(CONF_API_VERSION, API_VERSION_V2)
        default_interval = (
            DEFAULT_UPDATE_INTERVAL_V1
            if api_version == API_VERSION_V1
            else DEFAULT_UPDATE_INTERVAL_V2
        )
        current_interval = self.config_entry.data.get(CONF_UPDATE_INTERVAL, default_interval)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD, default=current_password): str,
                    vol.Required(CONF_UPDATE_INTERVAL, default=current_interval): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=1440)
                    ),
                }
            ),
        )

    async def async_step_abort(self, user_input: dict[str, Any] | None = None):
        """Abort options flow."""
        return self.async_create_entry(title="", data=self.config_entry.options)
