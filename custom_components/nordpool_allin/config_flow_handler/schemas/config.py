"""Config flow schemas for nordpool_allin."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.helpers import selector

from ...const import (
    CONF_EXPORT_FORMULA,
    CONF_IMPORT_FORMULA,
    CONF_NORDPOOL_ENTITY,
    DEFAULT_EXPORT_FORMULA,
    DEFAULT_IMPORT_FORMULA,
)


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """Schema for initial setup: NordPool entity + import/export formulas."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_NORDPOOL_ENTITY,
                default=defaults.get(CONF_NORDPOOL_ENTITY, vol.UNDEFINED),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor"),
            ),
            vol.Required(
                CONF_IMPORT_FORMULA,
                default=defaults.get(CONF_IMPORT_FORMULA, DEFAULT_IMPORT_FORMULA),
            ): selector.TemplateSelector(),
            vol.Required(
                CONF_EXPORT_FORMULA,
                default=defaults.get(CONF_EXPORT_FORMULA, DEFAULT_EXPORT_FORMULA),
            ): selector.TemplateSelector(),
        }
    )


def get_reconfigure_schema(current_data: Mapping[str, Any]) -> vol.Schema:
    """Schema for reconfiguration, pre-filled with current values."""
    return get_user_schema(current_data)


def get_options_schema(current_data: Mapping[str, Any]) -> vol.Schema:
    """Schema for options flow: formula fields only, no entity selector."""
    return vol.Schema(
        {
            vol.Required(
                CONF_IMPORT_FORMULA,
                default=current_data.get(CONF_IMPORT_FORMULA, DEFAULT_IMPORT_FORMULA),
            ): selector.TemplateSelector(),
            vol.Required(
                CONF_EXPORT_FORMULA,
                default=current_data.get(CONF_EXPORT_FORMULA, DEFAULT_EXPORT_FORMULA),
            ): selector.TemplateSelector(),
        }
    )


__all__ = [
    "get_reconfigure_schema",
    "get_user_schema",
]
