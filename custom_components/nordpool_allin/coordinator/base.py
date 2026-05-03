"""Core DataUpdateCoordinator for nordpool_allin.

Reads NordPool hourly price data from the HA state machine and evaluates
user-defined Jinja2 formulas to produce all-in import and export prices.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.core import Event, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.template import Template
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from ..const import CONF_EXPORT_FORMULA, CONF_IMPORT_FORMULA, CONF_NORDPOOL_ENTITY, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity import State

    from ..data import NordpoolAllinConfigEntry


class NordpoolAllinDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator that reads NordPool price slots and applies tax/charge formulas."""

    config_entry: NordpoolAllinConfigEntry

    @callback
    def handle_nordpool_state_change(self, event: Event) -> None:
        """Trigger a coordinator refresh when the NordPool entity state changes.

        async_request_refresh() routes through a Debouncer that does not fire
        when update_interval is None.  Scheduling async_refresh() directly as a
        task bypasses the debouncer and mirrors how the periodic poller calls it.
        """
        LOGGER.debug("NordPool state changed, scheduling refresh")
        self.hass.async_create_task(self.async_refresh())

    async def _async_update_data(self) -> dict[str, Any]:
        """Read NordPool entity, evaluate formulas, and return computed prices."""
        merged = {**self.config_entry.data, **self.config_entry.options}
        entity_id: str = merged[CONF_NORDPOOL_ENTITY]
        import_formula: str = merged[CONF_IMPORT_FORMULA]
        export_formula: str = merged[CONF_EXPORT_FORMULA]

        state = self.hass.states.get(entity_id)
        if state is None:
            raise UpdateFailed(
                translation_domain="nordpool_allin",
                translation_key="update_failed",
            )
        if state.state in ("unavailable", "unknown", ""):
            raise UpdateFailed(
                translation_domain="nordpool_allin",
                translation_key="update_failed",
            )

        slots = self._parse_price_slots(state)
        if not slots:
            raise UpdateFailed(
                translation_domain="nordpool_allin",
                translation_key="update_failed",
            )

        import_prices: dict[str, float | None] = {}
        export_prices: dict[str, float | None] = {}
        for iso_dt, price in slots.items():
            dt_obj = datetime.fromisoformat(iso_dt)
            import_prices[iso_dt] = self._evaluate_formula(import_formula, dt_obj, price)
            export_prices[iso_dt] = self._evaluate_formula(export_formula, dt_obj, price)

        now = dt_util.now()
        current_iso = self._find_current_slot(slots, now)

        unit = (
            state.attributes.get("unit_of_measurement")
            or state.attributes.get("currency")
        )

        return {
            "import_prices": import_prices,
            "export_prices": export_prices,
            "current_import_price": import_prices.get(current_iso) if current_iso else None,
            "current_export_price": export_prices.get(current_iso) if current_iso else None,
            "unit": unit,
        }

    def _parse_price_slots(self, state: State) -> dict[str, float]:
        """Return {iso_datetime_str: spot_price} for all available hour slots.

        Supports both custom-components/nordpool (raw_today/raw_tomorrow)
        and the HA core NordPool integration (prices_today/prices_tomorrow).
        """
        attrs = state.attributes
        slots: dict[str, float] = {}

        raw_today = attrs.get("raw_today")
        if raw_today is not None:
            for entry in raw_today:
                if isinstance(entry, dict) and "start" in entry and "value" in entry:
                    slots[str(entry["start"])] = float(entry["value"])
            raw_tomorrow = attrs.get("raw_tomorrow") or []
            for entry in raw_tomorrow:
                if isinstance(entry, dict) and "start" in entry and "value" in entry:
                    slots[str(entry["start"])] = float(entry["value"])
            return slots

        prices_today = attrs.get("prices_today")
        if prices_today is not None:
            if isinstance(prices_today, list):
                for entry in prices_today:
                    if isinstance(entry, dict):
                        start = entry.get("start") or entry.get("datetime")
                        value = entry.get("price") or entry.get("value")
                        if start and value is not None:
                            slots[str(start)] = float(value)
            prices_tomorrow = attrs.get("prices_tomorrow") or []
            if isinstance(prices_tomorrow, list):
                for entry in prices_tomorrow:
                    if isinstance(entry, dict):
                        start = entry.get("start") or entry.get("datetime")
                        value = entry.get("price") or entry.get("value")
                        if start and value is not None:
                            slots[str(start)] = float(value)
            return slots

        LOGGER.warning(
            "NordPool entity %s has no recognised price attributes (expected raw_today or prices_today)",
            self.config_entry.data[CONF_NORDPOOL_ENTITY],
        )
        return slots

    def _evaluate_formula(
        self,
        formula_str: str,
        dt_obj: datetime,
        price: float,
    ) -> float | None:
        """Render a Jinja2 formula with datetime and price variables."""
        try:
            tmpl = Template(formula_str, self.hass)
            result = tmpl.async_render(variables={"datetime": dt_obj, "price": price})
            return float(result)
        except TemplateError as err:
            LOGGER.warning("Formula template error: %s", err)
        except (ValueError, TypeError) as err:
            LOGGER.warning("Formula result is not a number: %s", err)
        return None

    def _find_current_slot(
        self,
        slots: dict[str, float],
        now: datetime,
    ) -> str | None:
        """Return the ISO datetime key for the slot that contains *now*.

        Slot duration is derived from the gap between consecutive slot starts so
        this works correctly regardless of whether slots are 15-minute or 1-hour.
        """
        parsed: list[tuple[datetime, str]] = []
        for iso_dt in slots:
            try:
                parsed.append((datetime.fromisoformat(iso_dt), iso_dt))
            except ValueError:
                continue
        parsed.sort()

        for i, (slot_start, iso_dt) in enumerate(parsed):
            if i + 1 < len(parsed):
                slot_end = parsed[i + 1][0]
            elif len(parsed) >= 2:
                slot_end = slot_start + (parsed[-1][0] - parsed[-2][0])
            else:
                slot_end = slot_start + timedelta(hours=1)
            if slot_start <= now < slot_end:
                return iso_dt
        return None
