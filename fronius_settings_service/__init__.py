import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from .const import DOMAIN, CONF_PASSWORD, CONF_BASE_URL, CONF_REFERER_URL
from .script import set_time_of_use, set_password, set_base_url, set_referer_url

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_BASE_URL): cv.string,
        vol.Required(CONF_REFERER_URL): cv.string,
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
        password = hass.data[DOMAIN][CONF_PASSWORD]
        base_url = hass.data[DOMAIN][CONF_BASE_URL]
        referer_url = hass.data[DOMAIN][CONF_REFERER_URL]
        set_password(password)
        set_base_url(base_url)
        set_referer_url(referer_url)
        if remove:
            _LOGGER.info("Removing Time of Use settings.")
        else:
            _LOGGER.info(f"Setting Time of Use power to {power}.")
        set_time_of_use(power=power, remove=remove)

    try:
        password = config[DOMAIN][CONF_PASSWORD]
        base_url = config[DOMAIN][CONF_BASE_URL]
        referer_url = config[DOMAIN][CONF_REFERER_URL]
        hass.data[DOMAIN] = {
            CONF_PASSWORD: password,
            CONF_BASE_URL: base_url,
            CONF_REFERER_URL: referer_url
        }

        hass.services.register(DOMAIN, "set_time_of_use", handle_set_time_of_use, schema=SERVICE_SET_TIME_OF_USE_SCHEMA)
        _LOGGER.info("Fronius Settings Service component set up successfully")
        return True
    except Exception as e:
        _LOGGER.error(f"Error setting up Fronius Settings Service component: {e}")
        return False
