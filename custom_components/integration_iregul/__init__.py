"""IRegul integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import InvalidAuth, IRegulCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IRegul from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = IRegulCoordinator(hass, entry.data)
    try:
        await coordinator.async_setup()
    except InvalidAuth:
        _LOGGER.error("Invalid authentication for IRegul")
        return False

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
