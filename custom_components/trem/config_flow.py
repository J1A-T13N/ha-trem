"""Config flow to configure trem component."""

from http import HTTPStatus
import json
import logging
import os

import aiohttp
from aiohttp.hdrs import ACCEPT, CONTENT_TYPE, METH_GET, USER_AGENT
import validators
import voluptuous as vol

from homeassistant import core, exceptions
from homeassistant.config_entries import (
    CONN_CLASS_CLOUD_POLL,
    ConfigEntry,
    ConfigFlow,
    FlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
    CONTENT_TYPE_JSON,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BASE_URLS,
    CONF_DRAW_MAP,
    CONF_NODE,
    CONF_PRESERVE_DATA,
    DOMAIN,
    HA_USER_AGENT,
    REQUEST_TIMEOUT,
)
from .data import tremData

# ACTIONS = {
#    "customizing": "HTTP API (Free plan)",
#    "cloud": "WebSocket (Subscribe plan)",
# }

_LOGGER = logging.getLogger(__name__)


async def getRegionCode() -> dict:
    """Get the region options."""
    directory = os.path.dirname(os.path.realpath(__file__))
    region_path = os.path.join(directory, "asset/region.json")
    with open(
        region_path,
        encoding="utf-8",
    ) as f:
        CODES = {}
        data = json.load(f)
        for city, region in data.items():
            for town in region:
                area = region[town]["area"]
                if area not in CODES:
                    CODES[area] = f"===== {area} ====="
                CODES[region[town]["code"]] = f"{city}{town}"
    return CODES


async def validate_input(hass: core.HomeAssistant, user_input) -> bool:
    """Validate that the user input allows us to connect to DataPoint.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    if CONF_REGION in user_input:
        CODES = await getRegionCode()
        region = user_input[CONF_REGION]
        if region not in CODES:
            raise RegionInvalid

    if CONF_USERNAME in user_input:
        session = async_get_clientsession(hass)
        login_info = {
            CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
            CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
        }
        trem_data = tremData(hass, session, login_info)

        await trem_data.async_update_data()
        if trem_data.username is None:
            raise CannotConnect

        return True

    URL = user_input[CONF_NODE]
    if URL == "" or URL in BASE_URLS:
        return True

    if validators.url(URL):
        try:
            session = async_get_clientsession(hass, verify_ssl=False)
            payload = {}
            headers = {
                ACCEPT: CONTENT_TYPE_JSON,
                CONTENT_TYPE: CONTENT_TYPE_JSON,
                USER_AGENT: HA_USER_AGENT,
            }
            response = await session.request(
                METH_GET,
                url=URL,
                data=json.dumps(payload),
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status == HTTPStatus.OK:
                return True
        except aiohttp.ClientError as ex:
            _LOGGER.error(f"Failed fetching data from HTTP API({URL}), {ex.strerror}.")

        raise CannotConnect

    return True


class tremFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a TREM config flow."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize flow."""
        self._region: str | None = None
        self._node: str | None = None
        self._preserve_data: bool | None = None
        self._draw_map: bool | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get option flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        # if user_input is None:
        #    return self.async_show_form(
        #        step_id="user",
        #        data_schema=vol.Schema(
        #            {vol.Required("action", default="customizing"): vol.In(ACTIONS)}
        #        ),
        #    )

        # if user_input["action"] == "customizing":
        #    return await self.async_step_customizing()

        # return await self.async_step_cloud()
        return await self.async_step_customizing()

    async def async_step_customizing(
        self, user_input: dict | None = None, error=None
    ) -> FlowResult:
        """Handle a flow initialized by the customizing."""
        errors = {}
        if user_input is None:
            user_input = {}
        else:
            await self.async_set_unique_id(
                f"{DOMAIN}_{user_input[CONF_REGION]}_monitoring"
            )
            self._abort_if_unique_id_configured()

            try:
                valid = await validate_input(self.hass, user_input)
                if valid:
                    REGIONCODE = await getRegionCode()
                    title = (
                        user_input[CONF_USERNAME]
                        if user_input.get(CONF_USERNAME, "") != ""
                        else REGIONCODE[user_input[CONF_REGION]]
                    )

                    return self.async_create_entry(title=title, data=user_input)
            except RegionInvalid:
                errors["base"] = "region_invalid"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        self._region = user_input.get(CONF_REGION, "")
        self._preserve_data = user_input.get(CONF_PRESERVE_DATA, False)
        self._draw_map = user_input.get(CONF_DRAW_MAP, False)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_REGION, default=self._region): int,
                vol.Required(CONF_NODE, default="random"): str,
                vol.Optional(CONF_PRESERVE_DATA, default=self._preserve_data): bool,
                vol.Optional(CONF_DRAW_MAP, default=self._draw_map): bool,
            }
        )

        return self.async_show_form(
            step_id="customizing",
            data_schema=data_schema,
            errors=errors,
        )

    @property
    def _name(self):
        # pylint: disable=no-member
        # https://github.com/PyCQA/pylint/issues/3167
        return self.context.get(CONF_REGION)

    @_name.setter
    def _name(self, value):
        # pylint: disable=no-member
        # https://github.com/PyCQA/pylint/issues/3167
        self.context[CONF_REGION] = value
        self.context["title_placeholders"] = {"name": self._region}


class OptionsFlowHandler(OptionsFlow):
    """Handle options flow changes."""

    def __init__(self, config_entry) -> None:
        """Initialize flow."""

        self.config_entry = config_entry
        self._region: int | None = None
        self._node: str | None = None
        self._preserve_data: bool | None = None
        self._draw_map: bool | None = None

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Handle a Options Flow initialized by the user."""

        # if "customizing" in self.config_entry.options:
        #    return await self.async_step_customizing()

        # return await self.async_step_cloud()
        return await self.async_step_customizing()

    async def async_step_customizing(self, user_input=None) -> FlowResult:
        """Handle a Options Flow initialized by the customizing."""

        errors = {}
        if user_input is not None:
            try:
                REGION_CODE = self.config_entry.options.get(CONF_REGION, "")
                user_input[CONF_REGION] = REGION_CODE

                valid = await validate_input(self.hass, user_input)
                if valid:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=user_input,
                        options=self.config_entry.options,
                    )

                    return self.async_create_entry(title=None, data=None)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        self._node = self.config_entry.options.get(CONF_NODE, "random")
        self._preserve_data = self.config_entry.options.get(CONF_PRESERVE_DATA, False)
        self._draw_map = self.config_entry.options.get(CONF_DRAW_MAP, False)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NODE, default=self._node): str,
                vol.Optional(CONF_PRESERVE_DATA, default=self._preserve_data): bool,
                vol.Optional(CONF_DRAW_MAP, default=self._draw_map): bool,
            }
        )

        return self.async_show_form(
            step_id="customizing",
            data_schema=data_schema,
            errors=errors,
        )


class RegionInvalid(exceptions.HomeAssistantError):
    """Error to indicate we not found."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
