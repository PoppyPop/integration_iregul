"""Coordinator for IRegul integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from types import MappingProxyType
from typing import Any

from aioiregul.iregulapi import IRegulApiInterface
from aioiregul.models import MappedFrame
from aioiregul.v1 import Device
from aioiregul.v2.client import IRegulClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_VERSION_V1,
    API_VERSION_V2,
    CONF_API_VERSION,
    CONF_DEVICE_ID,
    CONF_DEVICE_PASSWORD,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect to the device."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid authentication."""


class IRegulCoordinator(DataUpdateCoordinator[MappingProxyType[str, Any]]):
    """Coordinator for IRegul integration."""

    def __init__(
        self,
        hass: HomeAssistant,
        data: MappingProxyType[str, Any],
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            ),
        )
        self.hass = hass
        self.data_config = data
        self.client: IRegulApiInterface | None = None
        self._api_version = data.get(CONF_API_VERSION, API_VERSION_V2)

    async def async_setup(self) -> None:
        """Set up the coordinator by initializing the API client."""
        try:
            if self._api_version == API_VERSION_V1:
                self.client = Device(
                    http_session=async_create_clientsession(self.hass),
                    device_id=self.data_config[CONF_DEVICE_ID],
                    password=self.data_config[CONF_DEVICE_PASSWORD],
                )
            else:
                self.client = IRegulClient(
                    device_id=self.data_config[CONF_DEVICE_ID],
                    password=self.data_config[CONF_DEVICE_PASSWORD],
                )

            # Test the connection by fetching data
            await self._async_update_data()
        except InvalidAuth as err:
            raise InvalidAuth from err
        except Exception as err:
            raise CannotConnect from err

    async def _async_update_data(self) -> MappedFrame | None:
        """Fetch data from the API."""
        if self.client is None:
            raise UpdateFailed("Client not initialized")

        try:
            data = await self.client.get_data()
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
