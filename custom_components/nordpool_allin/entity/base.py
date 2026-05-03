"""Base entity class for nordpool_allin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.nordpool_allin.coordinator import NordpoolAllinDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class NordpoolAllinEntity(CoordinatorEntity[NordpoolAllinDataUpdateCoordinator]):
    """Base entity class providing coordinator integration, unique IDs, and device info."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NordpoolAllinDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.title,
            manufacturer=coordinator.config_entry.domain,
            model="NordPool All-In Prices",
        )
