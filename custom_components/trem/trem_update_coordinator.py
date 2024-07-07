"""Common TREM Data class used by both sensor and entity."""

from __future__ import annotations

import asyncio
from asyncio.exceptions import TimeoutError
from datetime import timedelta
from io import BytesIO
import json
import logging
import random
from typing import Any

from aiohttp import ClientResponse, WebSocketError
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.hdrs import ACCEPT, CONTENT_TYPE, METH_GET, USER_AGENT
import validators

from homeassistant.components import persistent_notification
from homeassistant.const import CONF_EMAIL, CONTENT_TYPE_JSON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URLS,
    BASE_WS,
    CLIENT_NAME,
    CONF_PASS,
    DOMAIN,
    HA_USER_AGENT,
    REQUEST_TIMEOUT,
)
from .exceptions import (
    AuthorizationFailed,
    AuthorizationLimit,
    MembershipExpired,
    RateLimitExceeded,
    WebSocketClosure,
)
from .session import WebSocketClient

_LOGGER = logging.getLogger(__name__)


class tremUpdateCoordinator(DataUpdateCoordinator):
    """Class for handling the data retrieval."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_info: str | dict,
        region: int,
        update_interval: timedelta,
    ) -> None:
        """Initialize the data object."""

        self._hass = hass
        self._update_interval = update_interval

        self._connection: WebSocketClient | None = None
        self.session = async_get_clientsession(hass)
        self._credentials: dict | None = None
        self.plan: str = "Free plan"

        self.region = region
        self.map: BytesIO | None = None
        self.mapSerial = ""

        if isinstance(base_info, dict):
            station, base_url = random.choice(list(BASE_WS.items()))
            self.plan = "Subscribe plan"
            self._credentials = {
                CONF_EMAIL: base_info[CONF_EMAIL],
                CONF_PASS: base_info[CONF_PASS],
            }
        elif base_info in BASE_URLS:
            station = base_info
            base_url = BASE_URLS[base_info]
        elif validators.url(base_info):
            station = base_info
            base_url = base_info
            self.plan = "Customize"
        else:
            station, base_url = random.choice(list(BASE_URLS.items()))
        self.station: str = station
        self._base_url: str = (
            base_url
            if self.plan == "Customize"
            else f"{base_url}/api/v1/eq/eew?type=cwa"
        )
        self._protocol = "WebSocket" if self.plan == "Subscribe plan" else "Http(s) API"
        self.retry: int = 0
        self.earthquakeData: list = []

        super().__init__(
            hass,
            _LOGGER,
            name=self._protocol,
            update_interval=self._update_interval,
        )

        if self.plan == "Subscribe plan":
            _LOGGER.debug(
                f"Fetching data from Websocket ({self.station}), EEW({self.region}) Monitoring..."
            )
        else:
            _LOGGER.debug(
                f"Fetching data from Http(s) API({self.station}), EEW({self.region}) Monitoring..."
            )

    async def _async_update_data(self) -> Any | None:
        """Poll earthquake data from Http(s) or WS api."""

        self.earthquakeData = []

        if self.retry >= 5:
            self.update_interval = timedelta(seconds=300)
            raise UpdateFailed

        if self.retry > 0:
            await self.switch_node()

        response: ClientResponse | None = None
        if self._credentials is None:
            payload = {}
            headers = {
                ACCEPT: CONTENT_TYPE_JSON,
                CONTENT_TYPE: CONTENT_TYPE_JSON,
                USER_AGENT: HA_USER_AGENT,
            }

            try:
                response = await self.session.request(
                    method=METH_GET,
                    url=self._base_url,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )
            except ClientConnectorError as ex:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                _LOGGER.error(
                    f"Failed fetching data from Http(s) API({self.station}), {ex.strerror}. Retry {self.retry}/5..."
                )
                raise UpdateFailed(ex) from ex
            except TimeoutError as ex:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                _LOGGER.error(
                    f"Failed fetching data from Http(s) API({self.station}), {ex.strerror}. Retry {self.retry}/5..."
                )
                raise UpdateFailed(ex) from ex
            except Exception as ex:
                _LOGGER.exception(
                    f"An unexpected exception occurred fetching the data from Http(s) API({self.station})."
                )
                raise UpdateFailed(ex) from ex
            else:
                if response.ok:
                    self.retry = 0
                    self.update_interval = self._update_interval

                    self.earthquakeData = await response.json()
                else:
                    self.retry = self.retry + 1
                    self.update_interval = timedelta(seconds=30)

                    _LOGGER.error(
                        f"Failed fetching data from Http(s) API({self.station}), (HTTP Status Code = {response.status}). Retry {self.retry}/5..."
                    )
                    raise UpdateFailed
        else:
            errCLS: Any | None = None
            errMSG: str | None = None

            try:
                if self._connection is None:
                    self._connection = WebSocketClient(
                        self._hass, self._base_url, self._credentials
                    )
                    await asyncio.gather(*[self._connection.connect()])

            except AuthorizationFailed as ex:  # 401
                self.retry = 5
                errMSG = "The account does not exist or password is invalid."
                errCLS = ex

            except AuthorizationLimit as ex:  # 400
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                errMSG = (
                    "The number of available authorization has reached the upper limit."
                )
                errCLS = ex

            except MembershipExpired as ex:  # 403
                self.retry = 5
                errMSG = "Your VIP membership has expired, Please re-subscribe."
                errCLS = ex

            except RateLimitExceeded as ex:  # 429
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                errMSG = "Too many requests in a given time."
                errCLS = ex

            except WebSocketClosure as ex:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                errMSG = "The websocket server has closed the connection."
                errCLS = ex

            except WebSocketError as ex:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                errMSG = f"Websocket connection had an error: {ex}."
                errCLS = ex

            except TypeError as ex:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=60)
                errMSG = ex.__str__
                errCLS = ex

            else:
                if len(self._connection.subscrib_service) > 0:
                    self.retry = 0
                    self.update_interval = self._update_interval
                    self.earthquakeData = self._connection.earthquakeData

            if errMSG is not None:
                await _notify_message(
                    self._hass, errCLS.__class__.__name__, CLIENT_NAME, errMSG
                )
                _LOGGER.error(errMSG)

            if errCLS is not None:
                raise UpdateFailed(errCLS) from errCLS

        return self

    async def switch_node(self) -> str | None:
        """Switch the Http(s) api node for fetching earthquake data."""

        if self.plan == "Customize":
            return None

        if self.plan == "Free plan":
            station, base_url = random.choice(list(BASE_URLS.items()))
            _LOGGER.warning(
                f"Switch Http(s) API {self.station} to {station}, Try to fetching data..."
            )

        if self.plan == "Subscribe plan":
            station, base_url = random.choice(list(BASE_WS.items()))
            _LOGGER.warning(
                f"Switch WebSocket API {self.station} to {station}, Try to fetching data..."
            )

        self.station = station
        self._base_url = base_url

        return station


async def _notify_message(
    hass: HomeAssistant, notification_id: str, title: str, message: str
) -> None:
    """Notify user with persistent notification."""

    persistent_notification.async_create(
        hass, message, title, f"{DOMAIN}.{notification_id}"
    )
