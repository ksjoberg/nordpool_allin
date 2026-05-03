"""Constants for nordpool_allin."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "nordpool_allin"

PARALLEL_UPDATES = 1

CONF_NORDPOOL_ENTITY = "nordpool_entity_id"
CONF_IMPORT_FORMULA = "import_formula"
CONF_EXPORT_FORMULA = "export_formula"

DEFAULT_IMPORT_FORMULA = "{{ price }}"
DEFAULT_EXPORT_FORMULA = "{{ price }}"
