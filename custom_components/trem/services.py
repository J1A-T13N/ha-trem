from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall

from custom_components.trem import DOMAIN
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from custom_components.trem.sensor import TremSensor
from custom_components.trem.const import ATTR_EQDATA


def register_services(hass: HomeAssistant) -> None:
    """Register the services."""

    async def simulator(service_call: ServiceCall) -> None:
        TremSensor._simulator = service_call.data[ATTR_EQDATA]

    async def reload(service_call: ServiceCall) -> None:
        return

    hass.services.async_register(
        DOMAIN,
        "simulator",
        simulator,
        vol.Schema({vol.Required(ATTR_EQDATA): cv.string}),
    )

    hass.services.async_register(
        DOMAIN,
        "reload",
        reload,
        vol.Schema({vol.Required(ATTR_ENTITY_ID): cv.entity_id}),
    )
