"""Constants for the IRegul integration."""

import logging

DOMAIN = "integration_iregul"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL = "upd_int"
DEFAULT_UPDATE_INTERVAL = 15

LOGGER = logging.getLogger(__package__)

REMOTE_OUTPUTS_ID = "outputs"
REMOTE_SENSORS_ID = "sensors"
REMOTE_INPUTS_ID = "inputs"
REMOTE_MEASURES_ID = "measures"
