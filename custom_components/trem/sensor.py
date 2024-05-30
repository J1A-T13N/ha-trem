"""Sensor for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations


from .earthquake.eew import EEW
from .earthquake.model import calculate_expected_intensity_and_travel_time

import logging
import random
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, CONF_REGION
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
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    HA_USER_AGENT,
    BASE_URLS,
    DEFAULT_ICON,
)

# from .services import register_services
from requests import request
from datetime import timedelta, timezone


RETRY_SCAN_INTERVAL = None
_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = (
    DEFAULT_SCAN_INTERVAL if RETRY_SCAN_INTERVAL == None else RETRY_SCAN_INTERVAL
)
REQUIREMENTS = ["geopandas", "matplotlib"]


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_REGION): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # add_entities([TremSensor(name=config[CONF_NAME], region=config[CONF_REGION], token=config[CONF_TOKEN])], True)
    add_entities(
        [
            TremSensor(
                name=config[CONF_NAME],
                region=config[CONF_REGION],
            )
        ],
        True,
    )
    # register_services(hass)


class TremSensor(SensorEntity):
    # def __init__(self, name: str, region: int, token: str):
    def __init__(self, name: str, region: int):
        station, base_url = random.choice(list(BASE_URLS.items()))
        self._station = station
        self._name = name
        self._region = int(region)
        # self._token = token
        self._state = None
        self._attr_value = {}
        self._base_url = f"{base_url}/api/v1/eq/eew?type=cwa"
        self._eew = None
        self._simulator = None
        self._retry = 0
        _LOGGER.info(
            f"Fetching data from HTTP API ({self._station}), EEW({self._region}) Monitoring..."
        )

    def update(self):
        try:
            if self._simulator == None:
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
                    RETRY_SCAN_INTERVAL = None
                    self._retry = 0
                    earthquakeData = resp.json()
                else:
                    RETRY_SCAN_INTERVAL = timedelta(seconds=60)
                    self._retry = self._retry + 1
                    _LOGGER.warning(
                        f"{resp.status_code} Unable to get data from HTTP API ({self._station}), Retry {self._retry}/5..."
                    )
            else:
                earthquakeData = self._simulator
                self._simulator = None

            if not earthquakeData == []:
                eew = EEW.from_dict(earthquakeData[0])
                eew_serial = f"{eew.id}_{eew.serial}"
                if self._eew == None:
                    self._eew = EEW.from_dict(earthquakeData[0])
                    old_eew_serial = ""
                else:
                    old_eew_serial = f"{self._eew.id}_{self._eew.serial}"

                intensities = calculate_expected_intensity_and_travel_time(
                    eew.earthquake
                )
                if not old_eew_serial == eew_serial:
                    tz_tw = timezone(timedelta(hours=8))
                    earthquakeTime = eew.earthquake.time.astimezone(tz_tw).strftime(
                        "%Y/%m/%d %H:%M:%S"
                    )
                    _LOGGER.debug(
                        "EEW alert updated\n"
                        "--------------------------------\n"
                        f"       ID: {eew.id} (Serial {eew.serial})\n"
                        f" Location: {eew.earthquake.location.display_name}({eew.earthquake.lon:.2f}, {eew.earthquake.lat:.2f})\n"
                        f"Magnitude: {eew.earthquake.mag}\n"
                        f"    Depth: {eew.earthquake.depth}km\n"
                        f"     Time: {earthquakeTime}\n"
                        "--------------------------------"
                    )
                    self._state = intensities[self._region].intensity
                    self._attr_value[ATTR_INT] = intensities[
                        self._region
                    ].intensity.value
                    self._attr_value[ATTR_AUTHOR] = (
                        f"{eew.provider.display_name} ({eew.provider.name})"
                    )
                    self._attr_value[ATTR_ID] = f"{eew.id} (Serial {eew.serial})"
                    self._attr_value[ATTR_LOC] = (
                        f"{eew.earthquake.location.display_name} ({eew.earthquake.lon:.2f}, {eew.earthquake.lat:.2f})"
                    )
                    self._attr_value[ATTR_LNG] = f"{eew.earthquake.lon:.2f}"
                    self._attr_value[ATTR_LAT] = f"{eew.earthquake.lat:.2f}"
                    self._attr_value[ATTR_MAG] = eew.earthquake.mag
                    self._attr_value[ATTR_DEPTH] = f"{eew.earthquake.depth}"
                    self._attr_value[ATTR_TIME] = f"{earthquakeTime}"
                self._attr_value[ATTR_EST] = round(
                    intensities[self._region].distance.s_left_time().total_seconds(),
                    0,
                )
            else:
                self._attr_value = {}
                for i in ATTR_LIST:
                    self._attr_value[i] = ""
                self._state = 0
        except Exception as ex:
            RETRY_SCAN_INTERVAL = timedelta(seconds=60)
            self._retry = self._retry + 1
            _LOGGER.error(
                f"Unable to get data from HTTP API (%s), Retry {self._retry}/5...",
                repr(ex),
            )

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return DEFAULT_ICON

    @property
    def unique_id(self):
        alias = self._name.replace(" ", "_")
        return f"trem_{alias}"

    @property
    def extra_state_attributes(self):
        self._attributes = {}
        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k, _ in self._attr_value.items():
            self._attributes[k] = self._attr_value[k]
        return self._attributes
