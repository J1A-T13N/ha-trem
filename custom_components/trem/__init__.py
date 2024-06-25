"""The Taiwan Real-Time Earthquake Monitoring integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_NODE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    TREM_COORDINATOR,
    TREM_DATA,
    TREM_NAME,
    UPDATE_LISTENER,
)
from .data import tremData
from .services import register_services

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a trem entry."""

    node = _get_config_value(entry, CONF_NODE, "")
    region = _get_config_value(entry, CONF_REGION, None)
    # migrate data (also after first setup) to options
    if entry.data:
        hass.config_entries.async_update_entry(entry, data={}, options=entry.data)

    session = async_get_clientsession(hass)

    trem_data = tremData(
        hass,
        session,
        node,
        region,
    )

    trem_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"trem {region}",
        update_method=trem_data.async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    trem_hass_data = hass.data.setdefault(DOMAIN, {})
    trem_hass_data[entry.entry_id] = {
        TREM_DATA: trem_data,
        TREM_COORDINATOR: trem_coordinator,
        TREM_NAME: f"trem {region}",
    }

    # Fetch initial data so we have data when entities subscribe
    await trem_coordinator.async_refresh()
    if trem_data.region is None:
        raise ConfigEntryNotReady

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    register_services(hass)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        update_listener = hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER]
        update_listener()
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


def _get_config_value(config_entry, key, default):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)
