"""Constants for the IRegul integration."""
import logging
from datetime import timedelta

DOMAIN = "integration_iregul"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "upd_int"
DEFAULT_UPDATE_INTERVAL = 5

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)

REMOTE_OUTPUTS_ID = "outputs"
REMOTE_SENSORS_ID = "sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASURES_ID = "measures"
