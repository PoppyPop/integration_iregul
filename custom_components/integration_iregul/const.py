"""Constants for the IRegul integration."""
from datetime import timedelta
import logging

DOMAIN = "iregul"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "upd_int"
DEFAULT_UPDATE_INTERVAL = 5

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

REMOTE_OUTPUTS_ID = "outputs"
REMOTE_SENSORS_ID = "sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASURES_ID = "measures"
