"""Sensor for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_REGION
from homeassistant.core import HomeAssistant, callback

from .const import (
    ATTR_AUTHOR,
    ATTR_DEPTH,
    ATTR_EST,
    ATTR_ID,
    ATTR_INT,
    ATTR_LAT,
    ATTR_LIST,
    ATTR_LNG,
    ATTR_LOC,
    ATTR_MAG,
    ATTR_NODE,
    ATTR_TIME,
    ATTRIBUTION,
    CONF_DRAW_MAP,
    CONF_PRESERVE_DATA,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    TREM_COORDINATOR,
    TREM_DATA,
)
from .earthquake.eew import EEW, EarthquakeData
from .earthquake.location import REGIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_devices: Callable
) -> None:
    """Set up the trem Sensor from config."""

    coordinator = hass.data[DOMAIN][config.entry_id][TREM_COORDINATOR]
    data = hass.data[DOMAIN][config.entry_id][TREM_DATA]

    devices = tremSensor(hass, config, coordinator, data)
    async_add_devices([devices], update_before_add=True)


class tremSensor(SensorEntity):
    """Defines a TREM sensor entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        coordinator: object,
        data: object,
    ) -> None:
        """Initialize the sensor."""

        self._coordinator: object = coordinator
        self._data: object = data
        self._hass: HomeAssistant = hass
        self._entry_id: str = config.entry_id

        self._eew: str | None = None
        self._simulator: str | None = None

        if config.data.get(CONF_REGION, None) is None:
            self._region: int = int(config.options[CONF_REGION])
        else:
            self._region: int = int(config.data[CONF_REGION])

        if config.data.get(CONF_PRESERVE_DATA, None) is None:
            self._preserve_data: bool = config.options[CONF_PRESERVE_DATA]
        else:
            self._preserve_data: bool = config.data[CONF_PRESERVE_DATA]

        if config.data.get(CONF_DRAW_MAP, None) is None:
            self._draw_map: bool = config.options[CONF_DRAW_MAP]
        else:
            self._draw_map: bool = config.data[CONF_DRAW_MAP]

        self._name: str = f"{DEFAULT_NAME} {self._region} Notification"
        self._unique_id: str = f"{DOMAIN}_{self._region}_notification"

        self._state: str = ""
        self._attributes = {}
        self._attr_value = {}
        for i in ATTR_LIST:
            self._attr_value[i] = ""

    async def async_update(self) -> None:
        """Schedule a custom update via the common entity update service."""

        if self._simulator is None:
            await self._coordinator.async_request_refresh()
            data = self._data.earthquakeData
        else:
            data = self._simulator
            self._simulator = None

        eew = None
        if data is not None and len(data) > 0:
            eew = EEW.from_dict(data[0])

        if eew is not None:
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

            if earthquakeSerial != old_earthquakeSerial:
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

            if self._draw_map:
                earthquake._expected_intensity = {
                    self._region: earthquake._expected_intensity.get(self._region)
                }
                earthquake.map.draw()
                waveSec = datetime.now() - earthquake.time
                earthquake.map.draw_wave(time=waveSec.total_seconds())
                self._data.map = earthquake.map.save()
                self._data.mapSerial = earthquakeSerial

        else:
            self._attr_value[ATTR_EST] = 0

        self._attr_value[ATTR_NODE] = self._data.station

        if self._preserve_data:
            return

        self._attr_value = {}
        for i in ATTR_LIST:
            self._attr_value[i] = ""
        self._state = ""

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""

        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )
        self._update_callback()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""

        return self._name

    @property
    def state(self) -> str:
        """Return the state of the sensor."""

        return self._state

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""

        return DEFAULT_ICON

    @property
    def unique_id(self) -> str:
        """Return the unique id."""

        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""

        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""

        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k in self._attr_value:
            self._attributes[k] = self._attr_value[k]
        return self._attributes

    @property
    def device_info(self):
        """Return device info."""

        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": f"{DEFAULT_NAME} {self._data.region} Monitoring",
            "manufacturer": MANUFACTURER,
            "model": f"HTTP API ({self._data.plan})",
        }

    @callback
    def _update_callback(self) -> None:
        """Load data from integration."""

        self.async_write_ha_state()
