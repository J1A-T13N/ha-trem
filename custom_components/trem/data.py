"""Common TREM Data class used by both sensor and entity."""

from __future__ import annotations

from http import HTTPStatus
from io import BytesIO
import json
import logging
import random

from aiohttp import ClientSession
from aiohttp.hdrs import ACCEPT, CONTENT_TYPE, METH_GET, USER_AGENT
from requests import exceptions
import validators

from homeassistant.const import CONTENT_TYPE_JSON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import BASE_URLS, BASE_WS, HA_USER_AGENT, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class tremData:
    """Class for handling the data retrieval."""

    def __init__(
        self, hass: HomeAssistant, session: ClientSession, node: str, region: int
    ) -> None:
        """Initialize the data object."""

        self._hass: HomeAssistant = hass
        self._session: ClientSession = session
        self.region: int = region
        self.plan: str = "Free plan"
        self.map: BytesIO = None
        self.mapSerial: str = ""

        if node in BASE_URLS:
            station = node
            base_url = BASE_URLS[node]
        elif node in BASE_WS:
            station = node
            base_url = BASE_WS[node]
            self.plan = "Subscribe plan"
        elif validators.url(node):
            station = "Customize"
            base_url = node
            self.plan = "Customize"
        else:
            station, base_url = random.choice(list(BASE_URLS.items()))
        self.station = station
        self._base_url = (
            node if station == "Customize" else f"{base_url}/api/v1/eq/eew?type=cwa"
        )
        self._retry = 0
        self.earthquakeData = None

        _LOGGER.debug(
            f"Fetching data from HTTP API ({self.station}), EEW({self.region}) Monitoring..."
        )

    async def async_fetch_data(self) -> dict:
        """Get the latest data for TREM API from REST service."""

        payload = {}
        headers = {
            ACCEPT: CONTENT_TYPE_JSON,
            CONTENT_TYPE: CONTENT_TYPE_JSON,
            USER_AGENT: HA_USER_AGENT,
        }
        try:
            response = await self._session.request(
                METH_GET,
                url=self._base_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

        except exceptions.RequestException as ex:
            self._retry = self._retry + 1
            _LOGGER.error(
                f"Failed fetching data from HTTP API({self.station}), {ex.strerror}. Retry {self._retry}/5..."
            )
            return None

        if response.status == HTTPStatus.OK:
            self._retry = 0
            res = await response.json()
        else:
            self._retry = self._retry + 1
            res = None
            _LOGGER.error(
                f"Failed fetching data from HTTP API({self.station}), (HTTP Status Code = {response.status}). Retry {self._retry}/5..."
            )

        return res

    async def async_update_data(self) -> bool:
        """Get the latest data for TREM API from async_fetch_data."""

        self.earthquakeData = None

        if self._retry >= 5:
            return False

        try:
            self.earthquakeData = await self.async_fetch_data()
        except exceptions as error:
            raise UpdateFailed(error) from error

        return True
