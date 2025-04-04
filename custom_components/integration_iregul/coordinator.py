"""DataUpdateCoordinator for the IRegul integration."""

from datetime import timedelta

import aioiregul
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_PASSWORD
from .const import CONF_UPDATE_INTERVAL
from .const import CONF_USERNAME
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import LOGGER


class IRegulDataUpdateCoordinator(DataUpdateCoordinator):
    """A IRegul Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the IRegul hub."""

        self.entry = entry

        scan_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        connOpt = aioiregul.ConnectionOptions(
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            refresh_rate=timedelta(minutes=scan_interval),
        )

        self.session = async_create_clientsession(hass)

        self.iregul = aioiregul.Device(connOpt)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    async def defrost(self) -> bool:
        """Fetch data from IRegul."""
        try:
            return await self.iregul.defrost(self.session)

        except aioiregul.CannotConnect:
            LOGGER.error("Could not connect")
            raise CannotConnect()

        except aioiregul.InvalidAuth:
            LOGGER.error("Invalid Auth")
            raise InvalidAuth()

    async def _async_update_data(self) -> dict:
        """Fetch data from IRegul."""
        try:
            return await self.iregul.collect(self.session, False)

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
