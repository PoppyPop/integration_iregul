"""Constants for the IRegul integration."""

import logging

from homeassistant.const import (
    CONF_HOST as HA_CONF_HOST,
)
from homeassistant.const import (
    CONF_PASSWORD,
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

LOGGER = logging.getLogger(__package__)

# Data groups from aioiregul v2 mapped frame
REMOTE_OUTPUTS_ID = "outputs"
REMOTE_ANALOG_SENSORS_ID = "analog_sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASUREMENTS_ID = "measurements"
