"""Constants for the IRegul integration."""

import logging

from homeassistant.const import CONF_HOST as HA_CONF_HOST, CONF_PORT as HA_CONF_PORT

DOMAIN = "integration_iregul"

# Connection details for aioiregul v2 client
CONF_HOST = HA_CONF_HOST  # standard HA key
CONF_PORT = HA_CONF_PORT  # standard HA key
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_KEY = "device_key"

# Options
CONF_UPDATE_INTERVAL = "upd_int"
DEFAULT_UPDATE_INTERVAL = 15

LOGGER = logging.getLogger(__package__)

# Data groups from aioiregul v2 mapped frame
REMOTE_OUTPUTS_ID = "outputs"
REMOTE_ANALOG_SENSORS_ID = "analog_sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASUREMENTS_ID = "measurements"
