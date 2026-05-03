"""Sensor platform for nordpool_allin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.nordpool_allin.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .price import ENTITY_DESCRIPTIONS, NordpoolAllinPriceSensor

if TYPE_CHECKING:
    from custom_components.nordpool_allin.data import NordpoolAllinConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NordpoolAllinConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up import and export price sensors."""
    async_add_entities(
        NordpoolAllinPriceSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )
