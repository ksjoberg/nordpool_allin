"""Import and export all-in price sensors for nordpool_allin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.nordpool_allin.entity import NordpoolAllinEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

if TYPE_CHECKING:
    from custom_components.nordpool_allin.coordinator import NordpoolAllinDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="import_price",
        translation_key="import_price",
        icon="mdi:transmission-tower-import",
        suggested_display_precision=4,
        has_entity_name=True,
    ),
    SensorEntityDescription(
        key="export_price",
        translation_key="export_price",
        icon="mdi:transmission-tower-export",
        suggested_display_precision=4,
        has_entity_name=True,
    ),
)


class NordpoolAllinPriceSensor(SensorEntity, NordpoolAllinEntity):
    """Sensor that re-exports a NordPool spot price with all-in charges applied.

    State: current hour's all-in price (import or export).
    Attribute 'prices': dict mapping ISO slot datetime → all-in price for all available slots.
    """

    def __init__(
        self,
        coordinator: NordpoolAllinDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the price sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit from the source NordPool entity."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("unit")

    @property
    def native_value(self) -> float | None:
        """Return the current hour's all-in price."""
        if not self.coordinator.last_update_success or not self.coordinator.data:
            return None
        key = (
            "current_import_price"
            if self.entity_description.key == "import_price"
            else "current_export_price"
        )
        return self.coordinator.data.get(key)

    @property
    def extra_state_attributes(self) -> dict[str, dict[str, float | None]]:
        """Return all slot prices as a dict keyed by ISO slot datetime."""
        if not self.coordinator.data:
            return {}
        key = (
            "import_prices"
            if self.entity_description.key == "import_price"
            else "export_prices"
        )
        return {"prices": self.coordinator.data.get(key, {})}

    @property
    def available(self) -> bool:
        """Return whether the entity has data."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
