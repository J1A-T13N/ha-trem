"""The Taiwan Real-Time Earthquake Monitoring integration."""

import asyncio
import logging
from typing import Any

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant

# from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_NODE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    TREM_COORDINATOR,
    TREM_NAME,
    UPDATE_LISTENER,
)
from .services import register_services
from .trem_update_coordinator import TremUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up a trem entry."""
    node: str | dict = _get_config_value(config, CONF_NODE, "")
    region: int = _get_config_value(config, CONF_REGION, None)

    # migrate data (also after first setup) to options
    if config.data:
        hass.config_entries.async_update_entry(config, data={}, options=config.data)

    session: ClientSession = async_get_clientsession(hass)
    trem_coordinator: TremUpdateCoordinator = TremUpdateCoordinator(
        hass,
        session,
        node,
        region,
        DEFAULT_SCAN_INTERVAL,
    )

    # Fetch initial data so we have data when entities subscribe
    await trem_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config.entry_id] = {
        TREM_COORDINATOR: trem_coordinator,
        TREM_NAME: f"{DEFAULT_NAME} {region} Monitoring",
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, platform)
        )

    update_listener = config.add_update_listener(async_update_options)
    hass.data[DOMAIN][config.entry_id][UPDATE_LISTENER] = update_listener

    register_services(hass)
    return True


async def async_update_options(hass: HomeAssistant, config: ConfigEntry):
    """Handle options update."""

    await hass.config_entries.async_reload(config.entry_id)


async def async_unload_entry(hass: HomeAssistant, config: ConfigEntry):
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        update_listener = hass.data[DOMAIN][config.entry_id][UPDATE_LISTENER]
        update_listener()
        hass.data[DOMAIN].pop(config.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config: ConfigEntry) -> None:
    """Reload the HACS config entry."""

    await async_unload_entry(hass, config)
    await async_setup_entry(hass, config)


def _get_config_value(config_entry: ConfigEntry, key: str, default: Any | None = None):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)
