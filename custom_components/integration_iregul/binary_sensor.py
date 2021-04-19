"""Platform for sensor integration."""
from homeassistant.components.binary_sensor import BinarySensorEntity, DEVICE_CLASS_POWER

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from typing import Any, Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    REMOTE_INPUTS_ID,
    CONF_USERNAME,
)
from .coordinator import IRegulDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Verisure sensors based on a config entry."""
    coordinator: IRegulDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[Entity] = [
        IRegulSensor(coordinator, id, REMOTE_INPUTS_ID)
        for id in coordinator.data[REMOTE_INPUTS_ID].keys()
    ]

    async_add_entities(sensors)

class IRegulSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a IRegul sensor."""

    coordinator: IRegulDataUpdateCoordinator

    def __init__(
        self, coordinator: IRegulDataUpdateCoordinator, slug: str, group: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.slug = slug
        self.group = group

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = self.coordinator.data[self.group][self.slug].name
        return name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.slug

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""

        return {
            "name": self.coordinator.entry.data[CONF_USERNAME] + " " + self.group,
            "manufacturer": "IRegul",
            "model": self.group,
            "identifiers": {
                (DOMAIN, self.group, self.coordinator.entry.data[CONF_USERNAME])
            },
            "via_device": (DOMAIN, self.coordinator.entry.data[CONF_USERNAME]),
        }

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on based on the state machine."""
        return self.coordinator.data[self.group][self.slug].value == "1"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.slug in self.coordinator.data[self.group]

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        return DEVICE_CLASS_POWER
