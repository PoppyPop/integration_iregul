"""Platform for sensor integration."""

from typing import Callable
from typing import Iterable

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import DEVICE_CLASS_POWER
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_USERNAME
from .const import DOMAIN
from .const import REMOTE_INPUTS_ID
from .coordinator import IRegulDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Verisure sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

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
        return self.coordinator.entry.data[CONF_USERNAME] + "-" + self.slug

    @property
    def force_update(self) -> bool:
        return True

    @property
    def device_info(self):
        """Return device information about this entity."""

        datas = self.coordinator.entry.data

        return {
            "name": datas[CONF_USERNAME] + " " + self.group,
            "manufacturer": "IRegul",
            "model": self.group,
            "identifiers": {(DOMAIN, self.group, datas[CONF_USERNAME])},
            "via_device": (DOMAIN, datas[CONF_USERNAME]),
        }

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on based on the state machine."""
        return self.coordinator.data[self.group][self.slug].value == 1

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        datas = self.coordinator.data
        return super().available and (self.slug in datas[self.group])

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        return DEVICE_CLASS_POWER
