"""Diagnostics support for nordpool_allin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NordpoolAllinConfigEntry

TO_REDACT: set[str] = set()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: NordpoolAllinConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    integration = entry.runtime_data.integration

    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

    devices = dr.async_entries_for_config_entry(device_reg, entry.entry_id)
    device_info = []
    for device in devices:
        entities = er.async_entries_for_device(entity_reg, device.id)
        device_info.append(
            {
                "id": device.id,
                "name": device.name,
                "model": device.model,
                "entity_count": len(entities),
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "platform": entity.platform,
                        "original_name": entity.original_name,
                        "disabled": entity.disabled,
                    }
                    for entity in entities
                ],
            }
        )

    coordinator_info = {
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "data_keys": list(coordinator.data.keys()) if isinstance(coordinator.data, dict) else None,
    }

    integration_info = {
        "name": integration.name,
        "version": integration.version,
        "domain": integration.domain,
        "documentation": integration.documentation,
    }

    entry_info = {
        "entry_id": entry.entry_id,
        "version": entry.version,
        "domain": entry.domain,
        "title": entry.title,
        "state": str(entry.state),
        "unique_id": entry.unique_id,
        "data": async_redact_data(entry.data, TO_REDACT),
    }

    data_sample: dict[str, Any] = {}
    if coordinator.data:
        data_sample = {
            "current_import_price": coordinator.data.get("current_import_price"),
            "current_export_price": coordinator.data.get("current_export_price"),
            "import_slots_count": len(coordinator.data.get("import_prices", {})),
            "export_slots_count": len(coordinator.data.get("export_prices", {})),
            "unit": coordinator.data.get("unit"),
        }

    error_info = {
        "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        "last_exception_type": (type(coordinator.last_exception).__name__ if coordinator.last_exception else None),
    }

    return {
        "entry": entry_info,
        "integration": integration_info,
        "coordinator": coordinator_info,
        "devices": device_info,
        "data_sample": data_sample,
        "error": error_info,
    }
