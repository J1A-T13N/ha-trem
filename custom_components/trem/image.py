"""Image for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
import logging
import os

from PIL import Image

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    ATTR_ID,
    CONF_DRAW_MAP,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    TREM_COORDINATOR,
    TREM_DATA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_devices: Callable
) -> None:
    """Set up the TREM Image from config."""

    if config.data.get(CONF_DRAW_MAP, None) is None:
        draw_map = config.options[CONF_DRAW_MAP]
    else:
        draw_map = config.data[CONF_DRAW_MAP]

    if draw_map:
        coordinator = hass.data[DOMAIN][config.entry_id][TREM_COORDINATOR]
        data = hass.data[DOMAIN][config.entry_id][TREM_DATA]
        device = tremImage(hass, config, coordinator, data)
        async_add_devices([device], update_before_add=True)


class tremImage(ImageEntity):
    """Defines a TREM image entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        coordinator: object,
        data: object,
    ) -> None:
        """Initialize the image."""

        super().__init__(hass)

        self._coordinator: object = coordinator
        self._data: object = data
        self._hass: HomeAssistant = hass
        self._entry_id: str = config.entry_id
        self._first_draw: bool = False

        self.image: BytesIO = BytesIO()
        self._attr_name: str = f"{DEFAULT_NAME} {data.region} Isoseismal Map"
        self._attr_unique_id: str = f"{DOMAIN}_{data.region}_isoseismal_map"
        self._attr_content_type: str = "image/png"
        self._attributes = {}
        self._attr_value = {}

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""

        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )
        self._update_callback()

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""

        return self.image.getvalue()

    @callback
    def _update_callback(self):
        """Create the TREM Image."""

        if self._data.map is None:
            if not self._first_draw:
                self._first_draw = True
                directory = os.path.dirname(os.path.realpath(__file__))
                image_path = os.path.join(directory, "asset/default.png")

                DEFAULT_IMG = Image.open(image_path, mode="r")
                DEFAULT_IMG.save(self.image, format="PNG")
            else:
                return
        elif self.image == self._data.map:
            return
        else:
            self.image = self._data.map

        self._attr_value[ATTR_ID] = self._data.mapSerial
        self._attr_image_last_updated = dt_util.utcnow()
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device info."""

        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": f"{DEFAULT_NAME} {self._data.region} Monitoring",
            "manufacturer": MANUFACTURER,
            "model": f"HTTP API ({self._data.plan})",
        }

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""

        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k in self._attr_value:
            self._attributes[k] = self._attr_value[k]
        return self._attributes
