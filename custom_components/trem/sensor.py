"""Sensor for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_REGION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    ATTR_AUTHOR,
    ATTR_DEPTH,
    ATTR_EST,
    ATTR_ID,
    ATTR_INT,
    ATTR_LAT,
    ATTR_LNG,
    ATTR_LOC,
    ATTR_MAG,
    ATTR_NODE,
    ATTR_TIME,
    ATTRIBUTION,
    CLIENT_NAME,
    CONF_DRAW_MAP,
    CONF_PRESERVE_DATA,
    DEFAULT_ICON,
    DEFAULT_NAME,
    DOMAIN,
    EARTHQUAKE_ATTR,
    MANUFACTURER,
    TREM_COORDINATOR,
    TREM_NAME,
    TSUNAMI_ATTR,
)
from .earthquake.eew import EEW, EarthquakeData
from .earthquake.location import REGIONS
from .trem_update_coordinator import tremUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_devices: Callable
) -> None:
    """Set up the trem Sensor from config."""

    domain_data: dict = hass.data[DOMAIN][config.entry_id]
    name: str = domain_data[TREM_NAME]
    coordinator: tremUpdateCoordinator = domain_data[TREM_COORDINATOR]

    earthquake_device = earthquakeSensor(hass, name, config, coordinator)
    tsunami_device = tsunamiSensor(hass, name, config, coordinator)
    async_add_devices(
        [
            earthquake_device,
            tsunami_device,
        ],
        update_before_add=True,
    )


class earthquakeSensor(SensorEntity):
    """Defines a earthquake sensor entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        config: ConfigEntry,
        coordinator: tremUpdateCoordinator,
    ) -> None:
        """Initialize the sensor."""

        self._coordinator = coordinator
        self._hass = hass

        self._eew: EEW | None = None
        self.simulator: list | None = None
        self.simulatorTime: datetime | None = None

        self._region: int = _get_config_value(config, CONF_REGION)
        self._preserve_data: bool = _get_config_value(config, CONF_PRESERVE_DATA, False)
        self._draw_map: bool = _get_config_value(config, CONF_DRAW_MAP, False)

        modelInfo = (
            "WebSocket" if self._coordinator.plan == "Subscribe plan" else "HTTP API"
        )

        self._attr_name = f"{DEFAULT_NAME} {self._coordinator.region} Notification"
        self._attr_unique_id = f"{DEFAULT_NAME}_{self._coordinator.region}_notification"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config.entry_id)},
            name=name,
            manufacturer=MANUFACTURER,
            model=f"{modelInfo} ({self._coordinator.plan})",
        )

        self._state = ""
        self._attributes = {}
        self._attr_value = {}
        for i in EARTHQUAKE_ATTR:
            self._attr_value[i] = ""

    # async def async_update(self) -> None:
    def update(self) -> None:
        """Schedule a custom update via the common entity update service."""

        data: list = (
            self._coordinator.earthquakeData
            if isinstance(self._coordinator.earthquakeData, list)
            else []
        )
        if len(data) == 0 and isinstance(self.simulator, list):
            data = self.simulator
            if self.simulatorTime is None:
                self.simulatorTime = datetime.now()

            time = datetime.now() - self.simulatorTime
            if time.total_seconds() >= 240:
                self.simulator = None

        eew: EEW | None = None
        if len(data) > 0:
            eew = EEW.from_dict(data[0])

        if isinstance(eew, EEW):
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
                self._eew = eew

                tz_TW = timezone(timedelta(hours=8))
                earthquakeTime = earthquake.time.astimezone(tz_TW).strftime(
                    "%Y/%m/%d %H:%M:%S"
                )
                earthquakeProvider = (
                    f"{eew.provider.display_name} ({eew.provider.name})"
                )
                earthquakeLocation = f"{earthquake.location.display_name} ({earthquake.lon:.2f}, {earthquake.lat:.2f})"

                if _LOGGER.level <= 20:
                    message = "EEW alert updated\n"
                    "--------------------------------\n"
                    f"       ID: {earthquakeSerial}\n"
                    f" Provider: {earthquakeProvider}\n"
                    f" Location: {earthquakeLocation}\n"
                    f"Magnitude: {earthquake.mag}\n"
                    f"    Depth: {earthquake.depth}km\n"
                    f"     Time: {earthquakeTime}\n"
                    "--------------------------------"
                    _notify_message(
                        self._hass, f"{eew.id}_{eew.serial}", CLIENT_NAME, message
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
                self._coordinator.map = earthquake.map.save()
                self._coordinator.mapSerial = earthquakeSerial
        else:
            self._attr_value[ATTR_EST] = 0

        self._attr_value[ATTR_NODE] = self._coordinator.station

        if self._preserve_data:
            return

        self._attr_value = {}
        for i in EARTHQUAKE_ATTR:
            self._attr_value[i] = ""
        self._state = ""

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""

        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )

    @property
    def available(self):
        """Return True if entity is available."""

        if self._coordinator.retry > 1:
            return self._coordinator.last_update_success

        return True

    @property
    def state(self) -> str:
        """Return the state of the sensor."""

        return self._state

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""

        return DEFAULT_ICON

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""

        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k in self._attr_value:
            self._attributes[k] = self._attr_value[k]
        return self._attributes

    @callback
    def _update_callback(self) -> None:
        """Handle updated data from the coordinator."""

        self.async_write_ha_state()


class tsunamiSensor(SensorEntity):
    """Defines a tsunami sensor entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        config: ConfigEntry,
        coordinator: tremUpdateCoordinator,
    ) -> None:
        """Initialize the sensor."""

        self._coordinator = coordinator
        self._hass = hass

        self._tsunami: dict | None = None

        self._preserve_data: bool = _get_config_value(config, CONF_PRESERVE_DATA, False)

        self._attr_name = "Tsunami Notification"
        self._attr_unique_id = "tsunami_notification"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config.entry_id)},
            name=name,
            manufacturer=MANUFACTURER,
            model=f"WebSocket ({self._coordinator.plan})",
        )

        self._state = ""
        self._attributes = {}
        self._attr_value = {}
        for i in TSUNAMI_ATTR:
            self._attr_value[i] = ""

    def update(self) -> None:
        """Schedule a custom update via the common entity update service."""

        data: list = (
            self._coordinator.tsunamiData
            if isinstance(self._coordinator.tsunamiData, list)
            else []
        )
        if len(data) == 0:
            return

        tsunami = self._coordinator.tsunamiData

        tsunamiSerial = f"{tsunami["id"]} (Serial {tsunami["serial"]})"
        if self._tsunami is None:
            self._tsunami = tsunami
            old_tsunamiSerial = ""
        else:
            old_tsunami = self._tsunami
            old_tsunamiSerial = f"{old_tsunami["id"]} (Serial {old_tsunami["serial"]})"

        if tsunamiSerial != old_tsunamiSerial:
            self._tsunami = tsunami
            message = tsunami["content"]

            self._state = message
            self._attr_value[ATTR_AUTHOR] = tsunami["author"]
            self._attr_value[ATTR_ID] = tsunamiSerial

            _notify_message(
                self._hass, f"{tsunami["id"]}_{tsunami["serial"]}", CLIENT_NAME, message
            )

        self._attr_value[ATTR_NODE] = self._coordinator.station

        if self._preserve_data:
            return

        self._attr_value = {}
        for i in TSUNAMI_ATTR:
            self._attr_value[i] = ""
        self._state = ""

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""

        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )

    @property
    def available(self):
        """Return True if entity is available."""

        if self._coordinator.retry > 1:
            return self._coordinator.last_update_success

        return True

    @property
    def state(self) -> str:
        """Return the state of the sensor."""

        return self._state

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""

        return DEFAULT_ICON

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""

        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k in self._attr_value:
            self._attributes[k] = self._attr_value[k]
        return self._attributes

    @callback
    def _update_callback(self) -> None:
        """Handle updated data from the coordinator."""

        self.async_write_ha_state()


def _get_config_value(config_entry: ConfigEntry, key: str, default: Any | None = None):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)


def _notify_message(
    hass: HomeAssistant, notification_id: str, title: str, message: str
) -> None:
    """Notify user with persistent notification."""

    persistent_notification.async_create(
        hass, message, title, f"{DOMAIN}.{notification_id}"
    )
