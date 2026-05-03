"""Custom types for nordpool_allin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import NordpoolAllinDataUpdateCoordinator


type NordpoolAllinConfigEntry = ConfigEntry[NordpoolAllinData]


@dataclass
class NordpoolAllinData:
    """Runtime data for nordpool_allin config entries."""

    coordinator: NordpoolAllinDataUpdateCoordinator
    integration: Integration
