"""Image for the Taiwan Real-time Earthquake Monitoring."""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
import logging
import os
from typing import Any

from PIL import Image

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_REGION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_ID,
    ATTRIBUTION,
    CONF_DRAW_MAP,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    TREM_COORDINATOR,
    TREM_NAME,
)
from .trem_update_coordinator import tremUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_devices: Callable
) -> None:
    """Set up the TREM Image from config."""

    draw_map: bool = _get_config_value(config, CONF_DRAW_MAP, False)

    if draw_map:
        domain_data: dict = hass.data[DOMAIN][config.entry_id]
        name: str = domain_data[TREM_NAME]
        coordinator: tremUpdateCoordinator = domain_data[TREM_COORDINATOR]

        device = earthquakeImage(hass, name, config, coordinator)
        async_add_devices([device], update_before_add=True)


class earthquakeImage(ImageEntity):
    """Defines a TREM image entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        config: ConfigEntry,
        coordinator: tremUpdateCoordinator,
    ) -> None:
        """Initialize the image."""

        super().__init__(hass)

        self._coordinator = coordinator
        self._hass = hass

        self._first_draw: bool = False
        self._region: int | None = _get_config_value(config, CONF_REGION, None)

        self._attr_name = f"{DEFAULT_NAME} {self._coordinator.region} Isoseismal Map"
        self._attr_unique_id = (
            f"{DEFAULT_NAME}_{self._coordinator.region}_isoseismal_map"
        )
        self._attr_content_type: str = "image/png"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config.entry_id)},
            name=name,
            manufacturer=MANUFACTURER,
            model=f"HTTP API ({self._coordinator.plan})",
        )

        self.image: BytesIO = BytesIO()
        self._attributes = {}
        self._attr_value = {}

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""

        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""

        return self.image.getvalue()

    @callback
    def _update_callback(self):
        """Handle updated data from the coordinator."""

        if self._coordinator.map is None:
            if not self._first_draw:
                self._first_draw = True
                directory = os.path.dirname(os.path.realpath(__file__))
                image_path = os.path.join(directory, "asset/default.png")

                default_img = Image.open(image_path, mode="r")
                default_img.save(self.image, format="PNG")
            else:
                return
        elif self.image == self._coordinator.map:
            return
        else:
            self.image = self._coordinator.map

        self._attr_value[ATTR_ID] = self._coordinator.mapSerial
        self._attr_image_last_updated = dt_util.utcnow()

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""

        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        for k in self._attr_value:
            self._attributes[k] = self._attr_value[k]
        return self._attributes


def _get_config_value(config_entry: ConfigEntry, key: str, default: Any | None = None):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)
