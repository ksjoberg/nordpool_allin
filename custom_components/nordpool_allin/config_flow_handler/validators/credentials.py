"""Validators for NordPool entity and price formula inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class NordPoolEntityNotFoundError(Exception):
    """Raised when the selected entity does not exist."""


class NordPoolEntityUnavailableError(Exception):
    """Raised when the selected entity is currently unavailable."""


class NordPoolEntityInvalidError(Exception):
    """Raised when the entity lacks NordPool price attributes."""


class NordPoolFormulaError(Exception):
    """Raised when a formula fails to render or does not produce a number."""


async def validate_nordpool_config(
    hass: HomeAssistant,
    entity_id: str,
    import_formula: str,
    export_formula: str,
) -> None:
    """Validate that the entity is a usable NordPool sensor and both formulas are valid.

    Raises:
        NordPoolEntityNotFoundError: Entity does not exist.
        NordPoolEntityUnavailableError: Entity state is unavailable/unknown.
        NordPoolEntityInvalidError: Entity has no recognised price attributes.
        NordPoolFormulaError: A formula is syntactically invalid or not numeric.

    """
    state = hass.states.get(entity_id)
    if state is None:
        raise NordPoolEntityNotFoundError(entity_id)
    if state.state in ("unavailable", "unknown"):
        raise NordPoolEntityUnavailableError(entity_id)

    attrs = state.attributes
    has_price_data = "raw_today" in attrs or "prices_today" in attrs
    if not has_price_data:
        raise NordPoolEntityInvalidError(
            f"Entity {entity_id!r} has no raw_today or prices_today attribute"
        )

    sample_dt = dt_util.now()
    for formula in (import_formula, export_formula):
        try:
            tmpl = Template(formula, hass)
            result = tmpl.async_render(variables={"datetime": sample_dt, "price": 0.1})
            float(result)
        except TemplateError as err:
            raise NordPoolFormulaError(str(err)) from err
        except (ValueError, TypeError) as err:
            raise NordPoolFormulaError(f"Formula result is not a number: {err}") from err


__all__ = [
    "NordPoolEntityInvalidError",
    "NordPoolEntityNotFoundError",
    "NordPoolEntityUnavailableError",
    "NordPoolFormulaError",
    "validate_nordpool_config",
]
