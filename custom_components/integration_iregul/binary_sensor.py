"""Binary sensor platform for IRegul inputs, outputs and analog sensors."""

from __future__ import annotations

from aioiregul.models import AnalogSensor, Input, Output
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import IRegulCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up IRegul binary sensors from a config entry."""

    coordinator: IRegulCoordinator = entry.runtime_data

    known_input_ids: set[int] = set()
    known_output_ids: set[int] = set()
    known_analog_ids: set[int] = set()

    @callback
    def _async_add_new_entities() -> None:
        """Add new binary sensors for inputs, outputs, and analog sensors of type 1."""

        new_entities: list[
            IRegulInputBinarySensor | IRegulOutputBinarySensor | IRegulAnalogBinarySensor
        ] = []

        # Inputs: type == 1
        for input_id, input_sensor in coordinator.data.inputs.items():
            if input_id in known_input_ids:
                continue
            if input_sensor.type != 1:
                continue

            known_input_ids.add(input_id)
            new_entities.append(
                IRegulInputBinarySensor(
                    coordinator=coordinator,
                    entry=entry,
                    input_sensor=input_sensor,
                )
            )

        # Outputs: type == 1
        for output_id, output_sensor in coordinator.data.outputs.items():
            if output_id in known_output_ids:
                continue
            if output_sensor.type != 1:
                continue

            known_output_ids.add(output_id)
            new_entities.append(
                IRegulOutputBinarySensor(
                    coordinator=coordinator,
                    entry=entry,
                    output_sensor=output_sensor,
                )
            )

        # Analog sensors: type == "1"
        for analog_id, analog_sensor in coordinator.data.analog_sensors.items():
            if analog_id in known_analog_ids:
                continue
            if analog_sensor.type != "1":
                continue

            known_analog_ids.add(analog_id)
            new_entities.append(
                IRegulAnalogBinarySensor(
                    coordinator=coordinator,
                    entry=entry,
                    analog_sensor=analog_sensor,
                )
            )

        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_entities))


class IRegulBinarySensor(CoordinatorEntity[IRegulCoordinator], BinarySensorEntity):
    """Base binary sensor for IRegul data with shared behavior."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        item_index: int,
        item_key: str,
        unique_prefix: str,
    ) -> None:
        """Initialize the base binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._item_id = item_index
        self._item_key = item_key

        device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}_{unique_prefix}_{item_index}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=entry.title,
            manufacturer="IRegul",
            serial_number=device_id,
        )

    def _get_items(self) -> dict[int, object]:
        """Return the mapping of items for this sensor type."""
        return getattr(self.coordinator.data, self._item_key)

    @property
    def available(self) -> bool:
        """Return true if the item is available in coordinator data."""
        return super().available and self._item_id in self._get_items()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        items = self._get_items()
        item = items.get(self._item_id)
        if item is None:
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._update(item)
        self.async_write_ha_state()

    def _update(self, item: object) -> None:
        """Update entity attributes from the item.

        Must be implemented by subclasses.
        """
        raise NotImplementedError


class IRegulInputBinarySensor(IRegulBinarySensor):
    """Binary sensor entity for IRegul inputs of type 1."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        input_sensor: Input,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=input_sensor.index,
            item_key="inputs",
            unique_prefix="input",
        )
        self._update(input_sensor)

    def _update(self, input_sensor: Input) -> None:
        self._attr_name = input_sensor.alias or f"Input {input_sensor.index}"
        self._attr_is_on = bool(input_sensor.valeur)


class IRegulOutputBinarySensor(IRegulBinarySensor):
    """Binary sensor entity for IRegul outputs of type 1."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        output_sensor: Output,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=output_sensor.index,
            item_key="outputs",
            unique_prefix="output",
        )
        self._update(output_sensor)

    def _update(self, output_sensor: Output) -> None:
        self._attr_name = output_sensor.alias or f"Output {output_sensor.index}"
        self._attr_is_on = bool(output_sensor.valeur)


class IRegulAnalogBinarySensor(IRegulBinarySensor):
    """Binary sensor entity for IRegul analog sensors with type '1'."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        analog_sensor: AnalogSensor,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=analog_sensor.index,
            item_key="analog_sensors",
            unique_prefix="analog_sensor",
        )
        self._update(analog_sensor)

    def _update(self, analog_sensor: AnalogSensor) -> None:
        self._attr_name = analog_sensor.alias or f"Analog Sensor {analog_sensor.index}"
        # Prefer explicit state; fallback to threshold (valeur > 0)
        if analog_sensor.etat is not None:
            self._attr_is_on = bool(analog_sensor.etat)
        else:
            self._attr_is_on = bool(analog_sensor.valeur)
