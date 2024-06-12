"""Sensor for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations


from .earthquake.eew import EEW, EarthquakeData
from .earthquake.location import REGIONS

import logging
import random, validators
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import ATTR_ATTRIBUTION, CONF_FRIENDLY_NAME, CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import (
    ATTRIBUTION,
    ATTR_ID,
    ATTR_AUTHOR,
    ATTR_LNG,
    ATTR_LAT,
    ATTR_DEPTH,
    ATTR_MAG,
    ATTR_LOC,
    ATTR_TIME,
    ATTR_EST,
    ATTR_INT,
    ATTR_LIST,
    DEFAULT_FRIENDLY_NAME,
    DEFAULT_SCAN_INTERVAL,
    HA_USER_AGENT,
    BASE_URLS,
    CONF_NODE,
    CONF_KEEP_ALIVE,
    DEFAULT_ICON,
)

from requests import request
from datetime import timedelta, timezone

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = DEFAULT_SCAN_INTERVAL


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_REGION): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME, default=DEFAULT_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_NODE, default=""): cv.string,
        vol.Optional(CONF_KEEP_ALIVE, default=False): cv.boolean,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    add_entities(
        [
            TremSensor(
                region=config[CONF_REGION],
                friendly_name=config[CONF_FRIENDLY_NAME],
                node=config[CONF_NODE],
                keep_alive=config[CONF_KEEP_ALIVE],
            )
        ],
        True,
    )


class TremSensor(SensorEntity):
    def __init__(self, region: str, friendly_name: str, node: str, keep_alive: bool):
        self._region = int(region)
        self._friendly_name = (
            f"{friendly_name} ({region})"
            if friendly_name == DEFAULT_FRIENDLY_NAME
            else friendly_name
        )
        if node in BASE_URLS:
            station = node
            base_url = BASE_URLS[node]
        elif validators.url(node):
            station = "User designate"
            base_url = node
        else:
            station, base_url = random.choice(list(BASE_URLS.items()))
        self._station = station
        self._base_url = (
            node
            if station == "User designate"
            else f"{base_url}/api/v1/eq/eew?type=cwa"
        )
        self._retry = 0
        # self._token = token

        self._eew = None
        self._simulator = None

        self._state = 0
        self._attr_value = {}
        for i in ATTR_LIST:
            self._attr_value[i] = ""
        self._keep_alive = keep_alive

        _LOGGER.debug(
            f"Fetching data from HTTP API ({self._station}), EEW({self._region}) Monitoring..."
        )

    def update(self):
        try:
            if self._simulator is None:
                if self._retry >= 5:
                    return

                header = {"Accept": "application/json", "User-Agent": HA_USER_AGENT}
                resp = request(
                    "GET",
                    self._base_url,
                    headers=header,
                )
                resp.encoding = "utf-8"
                if resp.ok:
                    self._retry = 0
                    data = resp.json()
                else:
                    self._retry = self._retry + 1
                    _LOGGER.warning(
                        f"{resp.status_code} Unable to get data from HTTP API ({self._station}), Retry {self._retry}/5..."
                    )
            else:
                data = self._simulator
                self._simulator = None

            if not data == []:
                eew = EEW.from_dict(data[0])
                earthquakeSerial = f"{eew.id} (Serial {eew.serial})"
                if self._eew is None:
                    self._eew = eew
                    old_earthquakeSerial = ""
                else:
                    old_eew = self._eew
                    old_earthquakeSerial = f"{old_eew.id} (Serial {old_eew.serial})"

                earthquake = eew.earthquake
                earthquakeForecast = EarthquakeData.calc_expected_intensity(
                    earthquake, [REGIONS[self._region]]
                ).get(self._region)

                if not earthquakeSerial == old_earthquakeSerial:
                    tz_TW = timezone(timedelta(hours=8))
                    earthquakeTime = earthquake.time.astimezone(tz_TW).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    )
                    earthquakeProvider = (
                        f"{eew.provider.display_name} ({eew.provider.name})"
                    )
                    earthquakeLocation = f"{earthquake.location.display_name} ({earthquake.lon:.2f}, {earthquake.lat:.2f})"

                    _LOGGER.debug(
                        "EEW alert updated\n"
                        "--------------------------------\n"
                        f"       ID: {earthquakeSerial}\n"
                        f" Provider: {earthquakeProvider}\n"
                        f" Location: {earthquakeLocation}\n"
                        f"Magnitude: {earthquake.mag}\n"
                        f"    Depth: {earthquake.depth}km\n"
                        f"     Time: {earthquakeTime}\n"
                        "--------------------------------"
                    )

                    self._state = earthquakeForecast.intensity
                    self._attr_value[ATTR_INT] = earthquakeForecast.intensity.value
                    self._attr_value[ATTR_AUTHOR] = earthquakeProvider
                    self._attr_value[ATTR_ID] = earthquakeSerial
                    self._attr_value[ATTR_LOC] = earthquakeLocation
                    self._attr_value[ATTR_LNG] = f"{earthquake.lon:.2f}"
                    self._attr_value[ATTR_LAT] = f"{earthquake.lat:.2f}"
                    self._attr_value[ATTR_MAG] = earthquake.mag
                    self._attr_value[ATTR_DEPTH] = earthquake.depth
                    self._attr_value[ATTR_TIME] = earthquakeTime
                earthquakeEst = int(
                    earthquakeForecast.distance.s_left_time().total_seconds()
                )
                self._attr_value[ATTR_EST] = earthquakeEst if earthquakeEst > 0 else 0
            else:
                self._attr_value[ATTR_EST] = 0

            if self._keep_alive:
                return

            self._attr_value = {}
            for i in ATTR_LIST:
                self._attr_value[i] = ""
            self._state = 0
        except Exception as ex:
            self._retry = self._retry + 1
            _LOGGER.error(
                f"({self._station}) Unable to get data from HTTP API, %s, Retry {self._retry}/5...",
                repr(ex),
            )

    @property
    def name(self):
        return self._friendly_name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return DEFAULT_ICON

    @property
    def unique_id(self):
        alias = self._friendly_name.replace(" ", "_")
        return f"trem_{alias}"

    @property
    def extra_state_attributes(self):
        self._attributes = {}
        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k, _ in self._attr_value.items():
            self._attributes[k] = self._attr_value[k]
        return self._attributes
