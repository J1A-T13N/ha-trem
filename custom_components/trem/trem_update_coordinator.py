"""Common TREM Data class used by both sensor and entity."""

from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
from io import BytesIO
import json
import logging
import random
from typing import Any

from aiohttp import ClientSession, client_exceptions
from aiohttp.hdrs import ACCEPT, CONTENT_TYPE, METH_GET, USER_AGENT
import validators

from homeassistant.const import CONTENT_TYPE_JSON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URLS,
    BASE_WS,
    DEFAULT_SCAN_INTERVAL,
    HA_USER_AGENT,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class TremUpdateCoordinator(DataUpdateCoordinator):
    """Class for handling the data retrieval."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        base_info: str | list,
        region: int,
        update_interval: timedelta,
    ) -> None:
        """Initialize the data object."""

        self._hass: HomeAssistant = hass
        self._session: ClientSession = session
        self.username: str | None = None
        self.password: str | None = None
        self.region: int = region
        self.plan: str = "Free plan"
        self.map: BytesIO | None = None
        self.mapSerial: str = ""

        if base_info in BASE_URLS:
            station = base_info
            base_url = BASE_URLS[base_info]
        elif validators.url(base_info):
            station = base_info
            base_url = base_info
            self.plan = "Customize"
        elif isinstance(base_info, list):
            station, base_url = random.choice(list(BASE_WS.items()))
            self.plan = "Subscribe plan"
        else:
            station, base_url = random.choice(list(BASE_URLS.items()))
        self.station: str = station
        self._base_url: str = (
            base_url
            if self.plan == "Customize"
            else f"{base_url}/api/v1/eq/eew?type=cwa"
        )
        self.retry: int = 0
        self.earthquakeData: list = []

        super().__init__(
            hass,
            _LOGGER,
            name=self._base_url,
            update_interval=update_interval,
        )

        _LOGGER.debug(
            f"Fetching data from HTTP API ({self.station}), EEW({self.region}) Monitoring..."
        )

    async def _async_update_data(self) -> Any | None:
        """Poll earthquake data from http(s) api."""

        self.earthquakeData = []

        if self.retry > 5:
            raise UpdateFailed

        if self.retry > 0:
            self.switch_node()

        headers = {
            ACCEPT: CONTENT_TYPE_JSON,
            CONTENT_TYPE: CONTENT_TYPE_JSON,
            USER_AGENT: HA_USER_AGENT,
        }
        payload = {}
        response: ClientSession | None = None

        try:
            response = await self._session.request(
                METH_GET,
                url=self._base_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        except client_exceptions.ClientConnectorError as ex:
            self.retry = self.retry + 1
            self.update_interval = timedelta(seconds=60)
            _LOGGER.error(
                f"Failed fetching data from HTTP API({self.station}), {ex.strerror}. Retry {self.retry}/5..."
            )
            raise UpdateFailed(ex) from ex
        except Exception:
            _LOGGER.exception(
                f"An unexpected exception occurred fetching the data from HTTP API({self.station})."
            )
            raise UpdateFailed(Exception) from Exception
        else:
            if response.status == HTTPStatus.OK:
                self.retry = 0
                self.update_interval = DEFAULT_SCAN_INTERVAL

                self.earthquakeData = await response.json()
            else:
                self.retry = self.retry + 1
                self.update_interval = timedelta(seconds=30)

                _LOGGER.error(
                    f"Failed fetching data from HTTP API({self.station}), (HTTP Status Code = {response.status}). Retry {self.retry}/5..."
                )
                raise UpdateFailed

        return self

    async def switch_node(self) -> bool:
        """Switch the http(s) api node for fetching earthquake data."""

        if self.plan == "Customize":
            return False

        if self.plan == "Free plan":
            station, base_url = random.choice(list(BASE_URLS.items()))

        if self.plan == "Subscribe plan":
            station, base_url = random.choice(list(BASE_WS.items()))

        self.station = station
        self._base_url = base_url

        _LOGGER.warning(f"Try fetching data from HTTP API({station}).")

        return True
