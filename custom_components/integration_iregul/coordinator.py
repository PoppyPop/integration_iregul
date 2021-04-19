"""DataUpdateCoordinator for the IRegul integration."""
from .const import (
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
    LOGGER,
    DEFAULT_SCAN_INTERVAL,
)

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

import aioiregul


class IRegulDataUpdateCoordinator(DataUpdateCoordinator):
    """A IRegul Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the IRegul hub."""

        self.entry = entry

        connOpt = aioiregul.ConnectionOptions(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            refresh_rate=timedelta(minutes=entry.data[CONF_UPDATE_INTERVAL]),
        )

        self.iregul = aioiregul.Device(connOpt)

        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from IRegul."""
        try:
            return await self.iregul.collect(False)

        except aioiregul.CannotConnect:
            LOGGER.error("Could not connect")
            raise CannotConnect()

        except aioiregul.InvalidAuth:
            LOGGER.error("Invalid Auth")
            raise InvalidAuth()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
