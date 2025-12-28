"""Constants for the IRegul integration."""

from __future__ import annotations

import logging
from typing import TypedDict

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    CONF_HOST as HA_CONF_HOST,
)
from homeassistant.const import (
    CONF_PASSWORD,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.const import (
    CONF_PORT as HA_CONF_PORT,
)

DOMAIN = "integration_iregul"

# Connection details for aioiregul client
CONF_HOST = HA_CONF_HOST  # standard HA key
CONF_PORT = HA_CONF_PORT  # standard HA key
CONF_SERIAL_NUMBER = "serial_number"
CONF_API_VERSION = "api_version"
API_VERSION_V1 = "v1"
API_VERSION_V2 = "v2"
DEFAULT_API_VERSION = API_VERSION_V2

# The library expects a device id/key; keep aliases for compatibility across modules.
CONF_DEVICE_ID = CONF_SERIAL_NUMBER
CONF_DEVICE_PASSWORD = CONF_PASSWORD

# Options
CONF_UPDATE_INTERVAL = "upd_int"
DEFAULT_UPDATE_INTERVAL = 15
DEFAULT_UPDATE_INTERVAL_V1 = 15
DEFAULT_UPDATE_INTERVAL_V2 = 5

LOGGER = logging.getLogger(__package__)

# Data groups from aioiregul v2 mapped frame
REMOTE_OUTPUTS_ID = "outputs"
REMOTE_ANALOG_SENSORS_ID = "analog_sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASUREMENTS_ID = "measurements"


# --------------------
# Units configuration
# --------------------


class UnitInfo(TypedDict, total=False):
    """Unit metadata for sensors and canonicalization.

    Fields:
    - device_class/state_class/native_unit: HA presentation
    - canonical_unit/factor: conversion to canonical unit when aggregating
    """

    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None
    native_unit: str | None
    canonical_unit: str | None
    factor: float


# Default configuration for unknown units
DEFAULT_UNIT_CONFIG: tuple[SensorDeviceClass | None, SensorStateClass | None, str | None] = (
    None,
    SensorStateClass.MEASUREMENT,
    None,
)


# Unified unit map: original unit -> UnitInfo
UNIT_MAP: dict[str, UnitInfo] = {
    # Temperature
    "°": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTemperature.CELSIUS,
        "canonical_unit": "°C",
        "factor": 1.0,
    },
    "°C": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTemperature.CELSIUS,
        "canonical_unit": "°C",
        "factor": 1.0,
    },
    "°F": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTemperature.FAHRENHEIT,
        # Intentionally omit canonicalization to avoid meaningless sums
    },
    "K": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTemperature.KELVIN,
        # No canonicalization to Celsius to avoid aggregation pitfalls
    },
    # Pressure
    "bar": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.BAR,
        "canonical_unit": "bar",
        "factor": 1.0,
    },
    "mbar": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.MBAR,
        "canonical_unit": "bar",
        "factor": 0.001,
    },
    "Pa": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.PA,
        "canonical_unit": "bar",
        "factor": 1e-5,
    },
    "hPa": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.HPA,
        "canonical_unit": "bar",
        "factor": 0.001,
    },
    "kPa": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.KPA,
        "canonical_unit": "bar",
        "factor": 0.01,
    },
    "psi": {
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPressure.PSI,
        "canonical_unit": "bar",
        "factor": 0.0689475729,
    },
    # Power
    "W": {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPower.WATT,
        "canonical_unit": "W",
        "factor": 1.0,
    },
    "kW": {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPower.KILO_WATT,
        "canonical_unit": "W",
        "factor": 1000.0,
    },
    "MW": {
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfPower.MEGA_WATT,
        "canonical_unit": "W",
        "factor": 1_000_000.0,
    },
    # Energy
    "Wh": {
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfEnergy.WATT_HOUR,
        "canonical_unit": "Wh",
        "factor": 1.0,
    },
    "kWh": {
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfEnergy.KILO_WATT_HOUR,
        "canonical_unit": "Wh",
        "factor": 1000.0,
    },
    "MWh": {
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfEnergy.MEGA_WATT_HOUR,
        "canonical_unit": "Wh",
        "factor": 1_000_000.0,
    },
    # Voltage
    "V": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfElectricPotential.VOLT,
        "canonical_unit": "V",
        "factor": 1.0,
    },
    "mV": {
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfElectricPotential.MILLIVOLT,
        "canonical_unit": "V",
        "factor": 0.001,
    },
    # Current
    "A": {
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfElectricCurrent.AMPERE,
        "canonical_unit": "A",
        "factor": 1.0,
    },
    "mA": {
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfElectricCurrent.MILLIAMPERE,
        "canonical_unit": "A",
        "factor": 0.001,
    },
    # Frequency
    "Hz": {
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfFrequency.HERTZ,
        "canonical_unit": "Hz",
        "factor": 1.0,
    },
    "kHz": {
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfFrequency.KILOHERTZ,
        "canonical_unit": "Hz",
        "factor": 1000.0,
    },
    "MHz": {
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfFrequency.MEGAHERTZ,
        "canonical_unit": "Hz",
        "factor": 1_000_000.0,
    },
    "GHz": {
        "device_class": SensorDeviceClass.FREQUENCY,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfFrequency.GIGAHERTZ,
        "canonical_unit": "Hz",
        "factor": 1_000_000_000.0,
    },
    # Volume
    "L": {
        "device_class": SensorDeviceClass.VOLUME,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfVolume.LITERS,
        "canonical_unit": "L",
        "factor": 1.0,
    },
    "mL": {
        "device_class": SensorDeviceClass.VOLUME,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfVolume.MILLILITERS,
        "canonical_unit": "L",
        "factor": 0.001,
    },
    "m³": {
        "device_class": SensorDeviceClass.VOLUME,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "native_unit": UnitOfVolume.CUBIC_METERS,
        "canonical_unit": "L",
        "factor": 1000.0,
    },
    # Flow rate
    "L/min": {
        "device_class": SensorDeviceClass.VOLUME_FLOW_RATE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        "canonical_unit": "L/min",
        "factor": 1.0,
    },
    "m³/h": {
        "device_class": SensorDeviceClass.VOLUME_FLOW_RATE,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        "canonical_unit": "L/min",
        "factor": 1000.0 / 60.0,
    },
    # Speed
    "m/s": {
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfSpeed.METERS_PER_SECOND,
        "canonical_unit": "m/s",
        "factor": 1.0,
    },
    "km/h": {
        "device_class": SensorDeviceClass.SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "canonical_unit": "m/s",
        "factor": 1000.0 / 3600.0,
    },
    # Time
    "s": {
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTime.SECONDS,
        "canonical_unit": "s",
        "factor": 1.0,
    },
    "min": {
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTime.MINUTES,
        "canonical_unit": "s",
        "factor": 60.0,
    },
    "h": {
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": UnitOfTime.HOURS,
        "canonical_unit": "s",
        "factor": 3600.0,
    },
    # Percentage
    "%": {
        "state_class": SensorStateClass.MEASUREMENT,
        "native_unit": PERCENTAGE,
        "canonical_unit": "%",
        "factor": 1.0,
    },
}


def get_unit_config(
    unit: str | None,
) -> tuple[SensorDeviceClass | None, SensorStateClass | None, str | None]:
    """Return device class, state class and display unit for a given unit string.

    Falls back to DEFAULT_UNIT_CONFIG when unit is None or unknown.
    """
    if unit is None:
        return DEFAULT_UNIT_CONFIG
    info = UNIT_MAP.get(unit)
    if info is None:
        return DEFAULT_UNIT_CONFIG
    return (
        info.get("device_class"),
        info.get("state_class", SensorStateClass.MEASUREMENT),
        info.get("native_unit"),
    )


def canonicalize_unit(unit: str | None) -> tuple[str | None, float]:
    """Return canonical unit string and factor for aggregation.

    If the unit isn't recognized or has no canonicalization, returns (unit, 1.0).
    """
    if unit is None:
        return None, 1.0
    info = UNIT_MAP.get(unit)
    if info is None:
        return unit, 1.0
    canonical = info.get("canonical_unit")
    factor = info.get("factor", 1.0)
    if canonical is None:
        return unit, 1.0
    return canonical, factor
