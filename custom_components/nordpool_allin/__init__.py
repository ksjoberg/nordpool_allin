"""NordPool All-In Price integration for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
from homeassistant.const import Platform
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.loader import async_get_loaded_integration

from .const import CONF_NORDPOOL_ENTITY, DOMAIN, LOGGER
from .coordinator import NordpoolAllinDataUpdateCoordinator
from .data import NordpoolAllinData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NordpoolAllinConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NordpoolAllinConfigEntry,
) -> bool:
    """Set up config entry."""
    coordinator = NordpoolAllinDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=None,
        always_update=True,
    )

    nordpool_entity_id: str = entry.data[CONF_NORDPOOL_ENTITY]

    # React immediately to any state change on the source NordPool entity.
    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            nordpool_entity_id,
            coordinator.handle_nordpool_state_change,
        )
    )
    LOGGER.debug("Subscribed to NordPool state changes for %s", nordpool_entity_id)

    entry.runtime_data = NordpoolAllinData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: NordpoolAllinConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: NordpoolAllinConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
