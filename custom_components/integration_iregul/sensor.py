"""Sensor platform for IRegul measurements."""

from __future__ import annotations

from datetime import datetime

from aioiregul.models import (
    AnalogSensor,
    Input,
    MappedFrame,
    Measurement,
    Output,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_DEVICE_ID, DOMAIN, canonicalize_unit, get_unit_config
from .coordinator import IRegulCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up IRegul sensors from a config entry."""

    coordinator: IRegulCoordinator = entry.runtime_data
    async_add_entities(
        [
            IRegulLastMessageSensor(
                coordinator=coordinator,
                entry=entry,
            )
        ]
    )
    known_measurement_ids: set[int] = set()
    known_input_ids: set[int] = set()
    known_output_ids: set[int] = set()
    known_analog_sensor_ids: set[int] = set()
    # Track merged measurement sensors using a key of alias + unit
    known_merged_measurements: set[str] = set()

    def _merge_key(alias: str, unit: str | None) -> str:
        """Build a stable merge key based on alias and canonical unit string."""
        canonical_unit, _ = canonicalize_unit(unit)
        unit_key = canonical_unit or ""
        return f"{alias.strip().lower()}|{unit_key}"

    @callback
    def _async_add_new_entities() -> None:
        """Add new sensors for any new measurements, inputs, outputs, and analog sensors."""

        new_entities: list[
            IRegulMeasurementSensor
            | IRegulInputSensor
            | IRegulOutputSensor
            | IRegulAnalogSensorSensor
            | IRegulMergedMeasurementSensor
        ] = []

        # Group measurements by alias and unit to detect duplicates
        measurements_by_alias: dict[str, dict[str | None, list[tuple[int, Measurement]]]] = {}
        for m_id, m in coordinator.data.measurements.items():
            alias = m.alias or f"Measurement {m.index}"
            canonical_unit, _ = canonicalize_unit(m.unit)
            measurements_by_alias.setdefault(alias, {}).setdefault(canonical_unit, []).append(
                (m_id, m)
            )

        # Create merged sensors for groups with duplicate alias+unit
        for alias, unit_groups in measurements_by_alias.items():
            for unit, items in unit_groups.items():
                if len(items) < 2:
                    continue
                key = _merge_key(alias, unit)
                # Avoid creating a merged sensor if any item already has an individual sensor
                if key in known_merged_measurements:
                    # Mark all measurements as known so we don't add individuals later
                    for m_id, _ in items:
                        known_measurement_ids.add(m_id)
                    continue
                if any(m_id in known_measurement_ids for m_id, _ in items):
                    # Some individuals already created earlier; skip merging to avoid duplicates
                    for m_id, _ in items:
                        known_measurement_ids.add(m_id)
                    continue

                known_merged_measurements.add(key)
                # Mark all indices as known to prevent individual sensors
                for m_id, _ in items:
                    known_measurement_ids.add(m_id)
                new_entities.append(
                    IRegulMergedMeasurementSensor(
                        coordinator=coordinator,
                        entry=entry,
                        alias=alias,
                        canonical_unit=unit,
                    )
                )

        # Add remaining individual measurement sensors
        for measurement_id, measurement in coordinator.data.measurements.items():
            if measurement_id in known_measurement_ids:
                continue

            known_measurement_ids.add(measurement_id)
            new_entities.append(
                IRegulMeasurementSensor(
                    coordinator=coordinator,
                    entry=entry,
                    measurement=measurement,
                )
            )

        # Add input sensors (type != 1)
        for input_id, input_sensor in coordinator.data.inputs.items():
            if input_id in known_input_ids:
                continue
            if input_sensor.type == 1:
                continue

            known_input_ids.add(input_id)
            new_entities.append(
                IRegulInputSensor(
                    coordinator=coordinator,
                    entry=entry,
                    input_sensor=input_sensor,
                )
            )

        # Add output sensors (type != 1)
        for output_id, output_sensor in coordinator.data.outputs.items():
            if output_id in known_output_ids:
                continue
            if output_sensor.type == 1:
                continue

            known_output_ids.add(output_id)
            new_entities.append(
                IRegulOutputSensor(
                    coordinator=coordinator,
                    entry=entry,
                    output_sensor=output_sensor,
                )
            )

        # Add analog sensor sensors (type != "1")
        for analog_sensor_id, analog_sensor in coordinator.data.analog_sensors.items():
            if analog_sensor_id in known_analog_sensor_ids:
                continue
            if analog_sensor.type == "1":
                continue

            known_analog_sensor_ids.add(analog_sensor_id)
            new_entities.append(
                IRegulAnalogSensorSensor(
                    coordinator=coordinator,
                    entry=entry,
                    analog_sensor=analog_sensor,
                )
            )

        if new_entities:
            async_add_entities(new_entities)

    _async_add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_entities))


class IRegulLastMessageSensor(CoordinatorEntity[IRegulCoordinator], SensorEntity):
    """Sensor showing the timestamp of the last received message."""

    _attr_has_entity_name = True
    _attr_translation_key = "last_message_received"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the last message sensor."""
        super().__init__(coordinator)
        device_id = entry.data[CONF_DEVICE_ID]
        self._attr_unique_id = f"{device_id}_last_message"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=entry.title,
            manufacturer="IRegul",
            serial_number=device_id,
        )
        self._attr_native_value = self._get_timestamp(coordinator.data)

    def _get_timestamp(self, frame: MappedFrame) -> datetime | None:
        """Return the most recent timestamp in UTC."""
        timestamp = frame.timestamp
        if timestamp is None:
            return None
        return dt_util.as_utc(timestamp)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self._get_timestamp(self.coordinator.data)
        self.async_write_ha_state()


class IRegulSensor(CoordinatorEntity[IRegulCoordinator], SensorEntity):
    """Base class for IRegul sensors with shared behavior."""

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
        """Initialize the base sensor."""
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


class IRegulMeasurementSensor(IRegulSensor):
    """Representation of an IRegul measurement sensor."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        measurement: Measurement,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=measurement.index,
            item_key="measurements",
            unique_prefix="measurement",
        )
        self._update(measurement)

    def _update(self, measurement: Measurement) -> None:
        """Refresh attributes from the latest measurement."""
        self._attr_name = measurement.alias or f"Measurement {measurement.index}"

        # Get device class, state class, and unit from configuration
        device_class, state_class, unit_of_measurement = get_unit_config(measurement.unit)
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement or measurement.unit
        self._attr_native_value = measurement.valeur


class IRegulMergedMeasurementSensor(CoordinatorEntity[IRegulCoordinator], SensorEntity):
    """Merged measurement sensor for duplicate aliases with compatible units."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        alias: str,
        canonical_unit: str | None,
    ) -> None:
        """Initialize the merged measurement sensor."""
        super().__init__(coordinator)
        device_id = entry.data[CONF_DEVICE_ID]
        # Unique ID based on device and alias+unit
        merge_key = f"{alias.strip().lower()}|{canonical_unit or ''}"
        self._attr_unique_id = f"{device_id}_measurement_merged_{merge_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=entry.title,
            manufacturer="IRegul",
            serial_number=device_id,
        )
        self._alias = alias
        self._canonical_unit = canonical_unit

        # Set name and unit configuration
        self._attr_name = alias
        device_class, state_class, unit_of_measurement = get_unit_config(canonical_unit)
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement or canonical_unit
        # Initialize value
        self._attr_native_value = self._compute_sum()

    def _compute_sum(self) -> float | int | None:
        """Compute the sum of measurements matching alias and unit."""
        total: float = 0.0
        found = False
        for m in self.coordinator.data.measurements.values():
            alias = m.alias or f"Measurement {m.index}"
            if alias != self._alias:
                continue
            c_unit, factor = canonicalize_unit(m.unit)
            if c_unit != self._canonical_unit:
                # Skip units that aren't compatible with this merged sensor
                continue
            if m.valeur is None:
                continue
            found = True
            total += float(m.valeur) * factor
        if not found:
            return None
        # If the values were integers, we can return int when appropriate
        return total

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator by recomputing the sum."""
        self._attr_native_value = self._compute_sum()
        self.async_write_ha_state()


class IRegulInputSensor(IRegulSensor):
    """Representation of an IRegul input sensor."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        input_sensor: Input,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=input_sensor.index,
            item_key="inputs",
            unique_prefix="input",
        )
        self._update(input_sensor)

    def _update(self, input_sensor: Input) -> None:
        """Refresh attributes from the latest input."""
        self._attr_name = input_sensor.alias or f"Input {input_sensor.index}"
        self._attr_native_value = input_sensor.valeur


class IRegulOutputSensor(IRegulSensor):
    """Representation of an IRegul output sensor."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        output_sensor: Output,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=output_sensor.index,
            item_key="outputs",
            unique_prefix="output",
        )
        self._update(output_sensor)

    def _update(self, output_sensor: Output) -> None:
        """Refresh attributes from the latest output."""
        self._attr_name = output_sensor.alias or f"Output {output_sensor.index}"
        self._attr_native_value = output_sensor.valeur


class IRegulAnalogSensorSensor(IRegulSensor):
    """Representation of an IRegul analog sensor."""

    def __init__(
        self,
        *,
        coordinator: IRegulCoordinator,
        entry: ConfigEntry,
        analog_sensor: AnalogSensor,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            item_index=analog_sensor.index,
            item_key="analog_sensors",
            unique_prefix="analog_sensor",
        )
        self._update(analog_sensor)

    def _update(self, analog_sensor: AnalogSensor) -> None:
        """Refresh attributes from the latest analog sensor."""
        self._attr_name = analog_sensor.alias or f"Analog Sensor {analog_sensor.index}"

        # Get device class, state class, and unit from configuration
        device_class, state_class, unit_of_measurement = get_unit_config(analog_sensor.unit)
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement or analog_sensor.unit
        self._attr_native_value = analog_sensor.valeur
