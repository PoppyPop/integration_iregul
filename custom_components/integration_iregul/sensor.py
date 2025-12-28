"""Platform for sensor integration."""

from typing import Callable, Iterable

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
    POWER_WATT,
    PRESSURE_BAR,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID
from .const import DOMAIN
from .const import REMOTE_MEASUREMENTS_ID, REMOTE_OUTPUTS_ID, REMOTE_ANALOG_SENSORS_ID
from .coordinator import IRegulDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Iterable[Entity]], None],
) -> None:
    """Set up Verisure sensors based on a config entry."""
    coordinator: IRegulDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    frame = coordinator.data
    sensors: list[Entity] = []

    if hasattr(frame, REMOTE_ANALOG_SENSORS_ID):
        sensors.extend(
            IRegulSensor(coordinator, idx, REMOTE_ANALOG_SENSORS_ID)
            for idx in getattr(frame, REMOTE_ANALOG_SENSORS_ID).keys()
        )

    if hasattr(frame, REMOTE_MEASUREMENTS_ID):
        sensors.extend(
            IRegulSensor(coordinator, idx, REMOTE_MEASUREMENTS_ID)
            for idx in getattr(frame, REMOTE_MEASUREMENTS_ID).keys()
        )

    if hasattr(frame, REMOTE_OUTPUTS_ID):
        sensors.extend(
            IRegulSensor(coordinator, idx, REMOTE_OUTPUTS_ID)
            for idx in getattr(frame, REMOTE_OUTPUTS_ID).keys()
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
        obj = getattr(self.coordinator.data, self.group)[self.slug]
        # alias is the human-readable name
        return getattr(obj, "alias", str(self.slug))

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return f"{self.coordinator.entry.data[CONF_DEVICE_ID]}-{self.group}-{self.slug}"

    @property
    def force_update(self) -> bool:
        return True

    @property
    def device_info(self):
        """Return device information about this entity."""
        datas = self.coordinator.entry.data
        return {
            "name": f"{datas[CONF_DEVICE_ID]} {self.group}",
            "manufacturer": "IRegul",
            "model": self.group,
            "identifiers": {(DOMAIN, self.group, datas[CONF_DEVICE_ID])},
            "via_device": (DOMAIN, datas[CONF_DEVICE_ID]),
        }

    @property
    def native_value(self) -> str:
        """Return the state of the entity."""
        obj = getattr(self.coordinator.data, self.group)[self.slug]
        return getattr(obj, "valeur", None)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        datas = getattr(self.coordinator.data, self.group)
        return super().available and self.slug in datas

    @property
    def device_class(self) -> str:
        """Return the class of this entity."""
        obj = getattr(self.coordinator.data, self.group)[self.slug]
        if getattr(obj, "unit", "") == "°":
            return DEVICE_CLASS_TEMPERATURE

        if getattr(obj, "unit", "") == "bar":
            return DEVICE_CLASS_PRESSURE

        if getattr(obj, "unit", "") == "kWh":
            return DEVICE_CLASS_ENERGY

        if getattr(obj, "unit", "") == "W":
            return DEVICE_CLASS_POWER

        if getattr(obj, "unit", "") == "kW":
            return DEVICE_CLASS_POWER

        return None

    @property
    def state_class(self):
        """Return the device class."""

        obj = getattr(self.coordinator.data, self.group)[self.slug]
        if getattr(obj, "unit", "") == "kWh":
            return STATE_CLASS_TOTAL

        if getattr(obj, "unit", "") == "W":
            return STATE_CLASS_MEASUREMENT

        if getattr(obj, "unit", "") == "kW":
            return STATE_CLASS_MEASUREMENT

        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity."""

        obj = getattr(self.coordinator.data, self.group)[self.slug]
        if getattr(obj, "unit", "") == "°":
            return TEMP_CELSIUS

        if getattr(obj, "unit", "") == "bar":
            return PRESSURE_BAR

        if getattr(obj, "unit", "") == "kWh":
            return ENERGY_KILO_WATT_HOUR

        if getattr(obj, "unit", "") == "W":
            return POWER_WATT

        if getattr(obj, "unit", "") == "kW":
            return POWER_KILO_WATT
        return getattr(obj, "unit", None)
