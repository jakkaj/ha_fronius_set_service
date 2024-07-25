import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN
from .script import set_time_of_use, set_password

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required("password"): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

SERVICE_SET_TIME_OF_USE_SCHEMA = vol.Schema({
    vol.Optional("power"): vol.Coerce(int),
    vol.Optional("remove", default=False): cv.boolean,
})

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Fronius Settings Service component."""
    _LOGGER.info("Setting up Fronius Settings Service component")

    def handle_set_time_of_use(call):
        """Handle the service call."""
        _LOGGER.info("Handling set_time_of_use service call")
        power = call.data.get("power")
        remove = call.data.get("remove", False)
        password = hass.data[DOMAIN]["password"]
        set_password(password)
        if remove:
            _LOGGER.info("Removing Time of Use settings.")
        else:
            _LOGGER.info(f"Setting Time of Use power to {power}.")
        set_time_of_use(power=power, remove=remove)

    try:
        password = config[DOMAIN]["password"]
        hass.data[DOMAIN] = {"password": password}

        hass.services.register(DOMAIN, "set_time_of_use", handle_set_time_of_use, schema=SERVICE_SET_TIME_OF_USE_SCHEMA)
        _LOGGER.info("Fronius Settings Service component set up successfully")
        return True
    except Exception as e:
        _LOGGER.error(f"Error setting up Fronius Settings Service component: {e}")
        return False
