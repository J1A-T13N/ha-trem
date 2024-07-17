"""WebSocket Client for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations

import asyncio
from enum import Enum
import json
import logging

from aiohttp import ClientWebSocketResponse, WebSocketError, WSMsgType
from aiohttp.client_exceptions import (
    ClientConnectorError,
    ServerTimeoutError,
    TooManyRedirects,
)
from aiohttp.hdrs import CONTENT_TYPE, METH_POST, USER_AGENT

from homeassistant.const import (
    APPLICATION_NAME,
    CONF_NAME,
    CONTENT_TYPE_JSON,
    EVENT_HOMEASSISTANT_STOP,
    __version__ as HAVERSION,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CLIENT_NAME,
    DEFAULT_MAX_MSG_SIZE,
    HA_USER_AGENT,
    LOGIN_URLS,
    REQUEST_TIMEOUT,
    __version__,
)
from .exceptions import (
    AuthorizationFailed,
    AuthorizationLimit,
    CannotConnect,
    MembershipExpired,
    RateLimitExceeded,
    WebSocketClosure,
)

_LOGGER = logging.getLogger(__name__)


class WebSocketEvent(Enum):
    """Represent the websocket event."""

    EEW = "eew"
    INFO = "info"
    NTP = "ntp"
    REPORT = "report"
    RTS = "rts"
    RTW = "rtw"
    VERIFY = "verify"
    CLOSE = "close"
    ERROR = "error"


class WebSocketService(Enum):
    """Represent the supported websokcet service."""

    REALTIME_STATION = "trem.rts"
    REALTIME_WAVE = "trem.rtw"
    EEW = "websocket.eew"
    TREM_EEW = "trem.eew"
    REPORT = "websocket.report"
    TSUNAMI = "websocket.tsunami"
    CWA_INTENSITY = "cwa.intensity"
    TREM_INTENSITY = "trem.intensity"


class WebSocketClient:
    """A Websocket connection to a TREM service."""

    def __init__(self, hass: HomeAssistant, url: str, credentials: list) -> None:
        """Initialize the connection."""

        self._hass = hass

        self._connection: ClientWebSocketResponse | None = None
        self._session = async_get_clientsession(hass)
        self._is_stopping = False

        self._url = url
        self._credentials = credentials
        self._access_token: str = "c0d30WNER$JTGAO"

        self.subscrib_service: list = []
        self._register_service: list[WebSocketService] = [
            WebSocketService.EEW.value,
            # WebSocketService.TSUNAMI.value,
        ]
        self.earthquakeData: list = []

    async def connect(self):
        """Connect to TREM websocket..."""

        async def _async_stop_handler(event):
            await asyncio.gather(*[self.close()])

        _LOGGER.info("Connecting to WebSocket...")

        session = self._session
        self._connection = await session.ws_connect(
            self._url, max_msg_size=DEFAULT_MAX_MSG_SIZE
        )

        self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop_handler)
        await asyncio.gather(*[self._recv()])

    async def close(self):
        """Close connection."""

        self._is_stopping = True
        if self._connection is not None:
            await self._connection.close()

    async def _disconnected(self):
        if not self._is_stopping:
            asyncio.gather(*[self.connect()])

    async def _recv(self):
        while self.ready:
            msg = await self._connection.receive()
            if msg:
                msg_data: dict = json.loads(msg.data)
                msg_type: WSMsgType = msg.type
            else:
                continue

            message = msg.json()
            _LOGGER.debug(f"Received: {message}.")

            if msg_type in (
                WSMsgType.CLOSE,
                WSMsgType.CLOSED,
                WSMsgType.CLOSING,
            ):
                raise WebSocketClosure

            if msg_type == WSMsgType.ERROR:
                handle_error = await self._handle_error(msg_data)
                if not handle_error:
                    raise WebSocketError(msg)

            data_type = msg_data.get("type")
            if data_type == WebSocketEvent.VERIFY.value:
                self._access_token = await self._fetchToken(
                    credentials=self._credentials
                )
                payload: dict = {
                    "key": self._access_token,
                    "service": self._register_service,
                }
                payload["type"] = "start"
                await self._connection.send_json(payload)

                _LOGGER.debug("Sent: %s.", json.dumps(payload))

                data = await asyncio.wait_for(self.wait_for_verify(), timeout=60)
                self.subscrib_service = data["list"]
                if len(self.subscrib_service) == 0:
                    raise MembershipExpired

            if data_type == WebSocketEvent.EEW.value:
                if msg_data["author"] != "cwa":
                    continue
                self.earthquakeData = msg_data

        await self._disconnected()

    async def wait_for_verify(self):
        """Return websocket message data if verify successfully."""

        while True:
            msg = await self._connection.receive()
            if msg:
                msg_data: dict = json.loads(msg.data)
                # msg_type: WSMsgType = msg.type
            else:
                continue

            message = msg.json()
            _LOGGER.debug(f"Received: {message}.")

            data_type = msg_data.get("type")
            if data_type != WebSocketEvent.INFO.value:
                continue

            data: dict = msg_data.get("data")
            data_code = data.get("code")
            if data_code == 200:
                return data

            await self._handle_error(msg_data)

    def ready(self) -> bool:
        """Whether the websocket is ready."""

        return self._connection is not None and not self._connection.closed

    async def _fetchToken(self, credentials: list) -> str:
        """Fetch token from Exptech Membership."""

        if self._access_token == "c0d30WNER$JTGAO":
            try:
                payload = credentials
                payload[CONF_NAME] = (
                    f"{APPLICATION_NAME}/{CLIENT_NAME}/{__version__}/{HAVERSION}"
                )
                headers = {
                    USER_AGENT: HA_USER_AGENT,
                    CONTENT_TYPE: CONTENT_TYPE_JSON,
                }
                response = await self._session.request(
                    method=METH_POST,
                    url=LOGIN_URLS,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )

                if not response.ok:
                    message = response.json()
                    _LOGGER.error(
                        f"""
                        Failed fetching token from Exptech Membership API, \n
                        {message['message']} (HTTP Status Code = {response.status})."""
                    )
                else:
                    token = await response.text()
                    self._access_token = token

                    return token
            except ClientConnectorError as ex:
                _LOGGER.error(
                    f"Failed fetching token from Exptech Membership API, {ex.strerror}."
                )
            except TooManyRedirects:
                _LOGGER.error(
                    "Failed fetching token from Exptech Membership API, Too many redirects."
                )
            except ServerTimeoutError:
                _LOGGER.error(
                    "Failed fetching token from Exptech Membership API, Time out."
                )
        else:
            return self._access_token

        raise CannotConnect

    async def _handle_error(self, msg_data: dict) -> bool:
        status_code = msg_data.get("data").get("code")
        if status_code == 400:
            raise AuthorizationLimit

        if status_code == 401:
            raise AuthorizationFailed

        if status_code == 403:
            raise MembershipExpired

        if status_code == 429:
            raise RateLimitExceeded

        return False
