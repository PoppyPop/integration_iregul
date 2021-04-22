"""Platform for sensor integration."""
from typing import Callable
from typing import Iterable

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_ENERGY
from homeassistant.const import DEVICE_CLASS_POWER
from homeassistant.const import DEVICE_CLASS_PRESSURE
from homeassistant.const import DEVICE_CLASS_TEMPERATURE
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.const import POWER_KILO_WATT
from homeassistant.const import POWER_WATT
from homeassistant.const import PRESSURE_BAR
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_USERNAME
from .const import DOMAIN
from .const import REMOTE_MEASURES_ID
from .const import REMOTE_OUTPUTS_ID
from .const import REMOTE_SENSORS_ID
from .coordinator import IRegulDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Verisure sensors based on a config entry."""
    coordinator: IRegulDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[Entity] = [
        IRegulSensor(coordinator, id, REMOTE_SENSORS_ID)
        for id in coordinator.data[REMOTE_SENSORS_ID].keys()
    ]

    sensors.extend(
        IRegulSensor(coordinator, id, REMOTE_MEASURES_ID)
        for id in coordinator.data[REMOTE_MEASURES_ID].keys()
    )

    sensors.extend(
        IRegulSensor(coordinator, id, REMOTE_OUTPUTS_ID)
        for id in coordinator.data[REMOTE_OUTPUTS_ID].keys()
    )

    async_add_entities(sensors)


class IRegulSensor(CoordinatorEntity, SensorEntity):
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
    def device_info(self):
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
    def state(self) -> str:
        """Return the state of the entity."""
        return self.coordinator.data[self.group][self.slug].value

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.slug in self.coordinator.data[self.group]

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        if self.coordinator.data[self.group][self.slug].unit == "°":
            return DEVICE_CLASS_TEMPERATURE

        if self.coordinator.data[self.group][self.slug].unit == "bar":
            return DEVICE_CLASS_PRESSURE

        if self.coordinator.data[self.group][self.slug].unit == "kWh":
            return DEVICE_CLASS_ENERGY

        if self.coordinator.data[self.group][self.slug].unit == "W":
            return DEVICE_CLASS_POWER

        if self.coordinator.data[self.group][self.slug].unit == "kW":
            return DEVICE_CLASS_POWER

        return None

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""

        if self.coordinator.data[self.group][self.slug].unit == "°":
            return TEMP_CELSIUS

        if self.coordinator.data[self.group][self.slug].unit == "bar":
            return PRESSURE_BAR

        if self.coordinator.data[self.group][self.slug].unit == "kWh":
            return ENERGY_KILO_WATT_HOUR

        if self.coordinator.data[self.group][self.slug].unit == "W":
            return POWER_WATT

        if self.coordinator.data[self.group][self.slug].unit == "kW":
            return POWER_KILO_WATT

        return self.coordinator.data[self.group][self.slug].unit
