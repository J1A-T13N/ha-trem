"""Config flow to configure trem component."""

from __future__ import annotations

from http import HTTPStatus
import json
import logging
import os
from typing import Any

from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.hdrs import ACCEPT, CONTENT_TYPE, METH_GET, METH_POST, USER_AGENT
import validators
import voluptuous as vol

from homeassistant import core
from homeassistant.config_entries import (
    CONN_CLASS_CLOUD_POLL,
    ConfigEntry,
    ConfigFlow,
    FlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    APPLICATION_NAME,
    CONF_EMAIL,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_REGION,
    CONTENT_TYPE_JSON,
    __version__ as HAVERSION,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    BASE_URLS,
    CLIENT_NAME,
    CONF_DRAW_MAP,
    CONF_NODE,
    CONF_PASS,
    CONF_PRESERVE_DATA,
    DOMAIN,
    FREE_PLAN,
    HA_USER_AGENT,
    LOGIN_URLS,
    REQUEST_TIMEOUT,
    SUBSCRIBE_PLAN,
    __version__,
)
from .exceptions import AccountInvalid, CannotConnect, RegionInvalid

ACTIONS = {
    "customizing": FREE_PLAN,
    "cloud": SUBSCRIBE_PLAN,
}

_LOGGER = logging.getLogger(__name__)


async def getRegionCode() -> dict:
    """Get the region options."""

    directory = os.path.dirname(os.path.realpath(__file__))
    region_path = os.path.join(directory, "asset/region.json")
    with open(
        region_path,
        encoding="utf-8",
    ) as f:
        codes: dict = {}
        data: dict = json.load(f)
        for city, region in data.items():
            for town in region:
                area = region[town]["area"]
                if area not in codes:
                    codes[area] = f"===== {area} ====="
                codes[region[town]["code"]] = f"{city}{town}"
    return codes


async def validate_input(
    hass: core.HomeAssistant, user_input: dict[str, Any] | None
) -> bool:
    """Validate that the user input allows us to connect to DataPoint.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    if CONF_EMAIL in user_input:
        try:
            account: str = user_input[CONF_EMAIL]
            password: str = user_input[CONF_PASSWORD]
            session = async_get_clientsession(hass, verify_ssl=False)
            payload = {
                CONF_EMAIL: account,
                CONF_PASS: password,
                CONF_NAME: f"{APPLICATION_NAME}/{CLIENT_NAME}/{__version__}/{HAVERSION}",
            }
            headers = {
                ACCEPT: CONTENT_TYPE_JSON,
                CONTENT_TYPE: CONTENT_TYPE_JSON,
                USER_AGENT: HA_USER_AGENT,
            }
            response = await session.request(
                method=METH_POST,
                url=LOGIN_URLS,
                data=json.dumps(payload),
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status == HTTPStatus.BAD_REQUEST:
                raise AccountInvalid
        except ClientConnectorError as ex:
            _LOGGER.error(f"Unable to login to account, server error. {ex}")

    if CONF_NODE in user_input:
        uri: str = user_input[CONF_NODE]
        if uri == "" or uri in BASE_URLS:
            return True

        if validators.url(uri):
            try:
                session = async_get_clientsession(hass, verify_ssl=False)
                payload = {}
                headers = {
                    ACCEPT: CONTENT_TYPE_JSON,
                    CONTENT_TYPE: CONTENT_TYPE_JSON,
                    USER_AGENT: HA_USER_AGENT,
                }
                response = await session.request(
                    method=METH_GET,
                    url=uri,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )

                if response.status == HTTPStatus.OK:
                    return True
            except ClientConnectorError as ex:
                _LOGGER.error(
                    f"Failed fetching data from HTTP API({uri}), {ex.strerror}."
                )

            raise CannotConnect

    if CONF_REGION in user_input:
        codes = await getRegionCode()
        region: int = user_input[CONF_REGION]
        if region not in codes:
            raise RegionInvalid
    else:
        raise RegionInvalid

    return True


class tremFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a TREM config flow."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize flow."""

        self._region: int | None = None
        self._node: str | None = None
        self._email: str | None = None
        self._password: str | None = None
        self._preserve_data: bool | None = None
        self._draw_map: bool | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config: ConfigEntry):
        """Get option flow."""

        return OptionsFlowHandler(config)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {vol.Required("action", default="customizing"): vol.In(ACTIONS)}
                ),
            )

        if user_input["action"] == "customizing":
            return await self.async_step_customizing()

        return await self.async_step_cloud()

    async def async_step_customizing(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the customizing."""

        errors = {}
        if user_input is None:
            user_input = {}
        else:
            region_code: str = user_input.get(CONF_REGION, "")

            await self.async_set_unique_id(f"{DOMAIN}_{region_code}_monitoring")
            self._abort_if_unique_id_configured()

            try:
                valid = await validate_input(self.hass, user_input)
                if valid:
                    codes: dict = await getRegionCode()
                    title: str = codes[region_code]

                    return self.async_create_entry(title=title, data=user_input)
            except RegionInvalid:
                errors["base"] = "region_invalid"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
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

    async def async_step_cloud(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the cloud."""

        errors = {}
        if user_input is None:
            user_input = {}
        else:
            email: str = user_input.get(CONF_EMAIL, "")
            region_code: str = user_input.get(CONF_REGION, "")

            await self.async_set_unique_id(f"{DOMAIN}_{email}_monitoring")
            self._abort_if_unique_id_configured()

            try:
                valid = await validate_input(self.hass, user_input)
                if valid:
                    codes = await getRegionCode()
                    title: str = codes[region_code]

                    return self.async_create_entry(title=title, data=user_input)
            except AccountInvalid:
                errors["base"] = "account_invalid"
            except RegionInvalid:
                errors["base"] = "region_invalid"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        self._region = user_input.get(CONF_REGION, "")
        self._email = user_input.get(CONF_EMAIL, False)
        self._password = user_input.get(CONF_PASSWORD, False)
        self._preserve_data = user_input.get(CONF_PRESERVE_DATA, False)
        self._draw_map = user_input.get(CONF_DRAW_MAP, False)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_REGION, default=self._region): int,
                vol.Required(CONF_EMAIL, default=self._email): str,
                vol.Required(CONF_PASSWORD, default=self._password): str,
                vol.Optional(CONF_PRESERVE_DATA, default=self._preserve_data): bool,
                vol.Optional(CONF_DRAW_MAP, default=self._draw_map): bool,
            }
        )

        return self.async_show_form(
            step_id="cloud",
            data_schema=data_schema,
            errors=errors,
        )


class OptionsFlowHandler(OptionsFlow):
    """Handle options flow changes."""

    def __init__(self, config: ConfigEntry) -> None:
        """Initialize flow."""

        self._config = config
        self._region: int | None = None
        self._node: str | None = None
        self._email: str | None = None
        self._password: str | None = None
        self._preserve_data: bool | None = None
        self._draw_map: bool | None = None

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Handle a Options Flow initialized by the user."""

        if CONF_EMAIL in self._config.options:
            return await self.async_step_cloud()

        return await self.async_step_customizing()

    async def async_step_customizing(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a Options Flow initialized by the customizing."""

        errors = {}
        if user_input is not None:
            try:
                region_code = self._config.options.get(CONF_REGION, "")
                user_input[CONF_REGION] = region_code

                valid = await validate_input(self.hass, user_input)
                if valid:
                    self.hass.config_entries.async_update_entry(
                        self._config,
                        data=user_input,
                        options=self._config.options,
                    )

                    return self.async_create_entry(title=None, data=None)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception(
                    "An unexpected exception occurred during the configuration flow"
                )
                errors["base"] = "unknown"

        self._region = self._config.options.get(CONF_REGION, "")
        self._node = self._config.options.get(CONF_NODE, "random")
        self._preserve_data = self._config.options.get(CONF_PRESERVE_DATA, False)
        self._draw_map = self._config.options.get(CONF_DRAW_MAP, False)

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

    async def async_step_cloud(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the cloud."""

        errors = {}
        if user_input is not None:
            try:
                region_code = self._config.options.get(CONF_REGION, "")
                user_input[CONF_REGION] = region_code

                valid = await validate_input(self.hass, user_input)
                if valid:
                    self.hass.config_entries.async_update_entry(
                        self._config,
                        data=user_input,
                        options=self._config.options,
                    )

                    return self.async_create_entry(title=None, data=None)
            except AccountInvalid:
                errors["base"] = "account_invalid"
            except RegionInvalid:
                errors["base"] = "region_invalid"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        self._region = self._config.options.get(CONF_REGION, "")
        self._email = self._config.options.get(CONF_EMAIL, False)
        self._password = self._config.options.get(CONF_PASSWORD, False)
        self._preserve_data = self._config.options.get(CONF_PRESERVE_DATA, False)
        self._draw_map = self._config.options.get(CONF_DRAW_MAP, False)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_REGION, default=self._region): int,
                vol.Required(CONF_EMAIL, default=self._email): str,
                vol.Required(CONF_PASSWORD, default=self._password): str,
                vol.Optional(CONF_PRESERVE_DATA, default=self._preserve_data): bool,
                vol.Optional(CONF_DRAW_MAP, default=self._draw_map): bool,
            }
        )

        return self.async_show_form(
            step_id="cloud",
            data_schema=data_schema,
            errors=errors,
        )
