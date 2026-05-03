"""Config flow for nordpool_allin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from slugify import slugify

from custom_components.nordpool_allin.config_flow_handler.schemas import (
    get_options_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.nordpool_allin.config_flow_handler.validators import (
    validate_nordpool_config,
)
from custom_components.nordpool_allin.const import (
    CONF_EXPORT_FORMULA,
    CONF_IMPORT_FORMULA,
    CONF_NORDPOOL_ENTITY,
    DOMAIN,
    LOGGER,
)
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.loader import async_get_loaded_integration

ERROR_MAP = {
    "NordPoolEntityNotFoundError": "entity_not_found",
    "NordPoolEntityUnavailableError": "entity_unavailable",
    "NordPoolEntityInvalidError": "entity_invalid",
    "NordPoolFormulaError": "formula_invalid",
}


def _map_exception_to_error(exception: Exception) -> str:
    LOGGER.warning("Error in config flow: %s", exception)
    return ERROR_MAP.get(type(exception).__name__, "unknown")


class NordpoolAllinConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for nordpool_allin."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_nordpool_config(
                    self.hass,
                    entity_id=user_input[CONF_NORDPOOL_ENTITY],
                    import_formula=user_input[CONF_IMPORT_FORMULA],
                    export_formula=user_input[CONF_EXPORT_FORMULA],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                await self.async_set_unique_id(slugify(user_input[CONF_NORDPOOL_ENTITY]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NORDPOOL_ENTITY],
                    data=user_input,
                )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={"documentation_url": integration.documentation},
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of entity or formulas."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_nordpool_config(
                    self.hass,
                    entity_id=user_input[CONF_NORDPOOL_ENTITY],
                    import_formula=user_input[CONF_IMPORT_FORMULA],
                    export_formula=user_input[CONF_EXPORT_FORMULA],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(entry.data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "NordpoolAllinOptionsFlowHandler":
        """Return the options flow handler."""
        return NordpoolAllinOptionsFlowHandler()

    def _map_exception_to_error(self, exception: Exception) -> str:
        return _map_exception_to_error(exception)


class NordpoolAllinOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for editing import/export price formulas."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle formula editing."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_nordpool_config(
                    self.hass,
                    entity_id=self.config_entry.data[CONF_NORDPOOL_ENTITY],
                    import_formula=user_input[CONF_IMPORT_FORMULA],
                    export_formula=user_input[CONF_EXPORT_FORMULA],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = _map_exception_to_error(exception)
            else:
                return self.async_create_entry(data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(current),
            errors=errors,
        )


__all__ = ["NordpoolAllinConfigFlowHandler", "NordpoolAllinOptionsFlowHandler"]
