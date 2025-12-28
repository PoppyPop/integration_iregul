"""DataUpdateCoordinator for the IRegul integration."""

from datetime import timedelta

from aioiregul.v2.client import IRegulClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_DEVICE_ID, CONF_DEVICE_KEY, CONF_HOST, CONF_PORT
from .const import CONF_UPDATE_INTERVAL
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import LOGGER


class IRegulDataUpdateCoordinator(DataUpdateCoordinator):
    """A IRegul Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the IRegul client and coordinator."""

        self.entry = entry

        scan_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

        self.client = IRegulClient(
            host=entry.data.get(CONF_HOST),
            port=entry.data.get(CONF_PORT),
            device_id=entry.data.get(CONF_DEVICE_ID),
            device_key=entry.data.get(CONF_DEVICE_KEY),
            timeout=60.0,
        )

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    async def defrost(self) -> bool:
        """Trigger a defrost on the device."""
        try:
            return await self.hass.async_add_executor_job(self.client.defrost)
        except Exception as err:  # pragma: no cover
            LOGGER.error("Defrost failed: %s", err)
            raise CannotConnect() from err

    async def _async_update_data(self):
        """Fetch mapped data from IRegul."""
        try:
            # IRegulClient is synchronous; run in executor
            frame = await self.hass.async_add_executor_job(self.client.get_data)
            return frame
        except Exception as err:
            LOGGER.error("Update failed: %s", err)
            raise CannotConnect() from err


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
