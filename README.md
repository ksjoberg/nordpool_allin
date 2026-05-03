# NordPool All-In

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

A Home Assistant helper integration that wraps a [NordPool](https://www.nordpoolgroup.com/) price entity and applies user-defined formulas to produce **all-in import and export electricity prices** for every hour slot.

Spot prices alone don't reflect what you actually pay or earn. Import prices include VAT, energy taxes, and grid fees — and those charges often vary by time of day (e.g. energy tax is halved between 22:00 and 06:00 in Sweden). Export prices similarly have buy-back deductions. This integration lets you express those rules as simple Jinja2 templates.

## Features

- **Supports both NordPool integrations** — works with the [custom-components/nordpool](https://github.com/custom-components/nordpool) HACS integration and the built-in HA core NordPool integration
- **Import price sensor** — current hour's all-in import price as state; full 24–48 hour price schedule as an attribute
- **Export price sensor** — same for export/sell price
- **Flexible Jinja2 formulas** — templates receive `price` (spot price) and `datetime` (slot start) so you can express any tariff structure
- **Live updates** — reacts immediately when the NordPool entity changes (new hour, tomorrow's prices published around 13:00 CET)

## Platforms

| Platform | Description |
| -------- | ----------- |
| `sensor` | **Import Price** — all-in import price for the current hour |
| `sensor` | **Export Price** — all-in export price for the current hour |

Both sensors expose a `prices` attribute with a dict mapping each slot's ISO start datetime to its all-in price, covering today and tomorrow (when available).

## Prerequisites

- Home Assistant with either:
  - [custom-components/nordpool](https://github.com/custom-components/nordpool) installed via HACS, **or**
  - The built-in HA NordPool integration (available from HA 2024.x)
- The NordPool sensor must be configured and have price data loaded before setting up this integration

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click **+ Explore & Download Repositories** and search for **NordPool All-In**
4. Download and restart Home Assistant

<details>
<summary><strong>Manual Installation</strong></summary>

1. Download the `custom_components/nordpool_allin/` folder from this repository
2. Copy it to your Home Assistant `custom_components/` directory
3. Restart Home Assistant

</details>

## Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=nordpool_allin)

Or go to **Settings** → **Devices & Services** → **+ Add Integration** → search for **NordPool All-In**.

### Configuration fields

| Field | Description |
| ----- | ----------- |
| **NordPool sensor entity** | The NordPool sensor that provides hourly spot prices (e.g. `sensor.nordpool_kwh_se3_sek_3_10_025`) |
| **Import price formula** | Jinja2 template evaluated for each slot; receives `price` and `datetime` |
| **Export price formula** | Jinja2 template evaluated for each slot; receives `price` and `datetime` |

### Formula variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `price` | `float` | Spot price for the slot, in the NordPool entity's unit (e.g. SEK/kWh) |
| `datetime` | `datetime` | Timezone-aware start datetime of the slot |

Both formulas must evaluate to a number. The result inherits the same unit as the source NordPool entity.

### Example formulas

**Swedish import price** — spot + 25 % VAT + energy tax (halved 22:00–06:00):

```jinja2
{{ price * 1.25 + (0.054 if datetime.hour >= 22 or datetime.hour < 6 else 0.107) }}
```

**Simple export price** — spot minus a small transmission fee:

```jinja2
{{ price - 0.02 }}
```

**Peak/off-peak grid surcharge:**

```jinja2
{{ price * 1.25 + (0.08 if 7 <= datetime.hour < 22 else 0.04) }}
```

### Reconfiguration

To change the NordPool entity or update formulas after initial setup:

1. Go to **Settings** → **Devices & Services**
2. Find **NordPool All-In**
3. Click the **3-dot menu** → **Reconfigure**

## Entities

### Import Price (`sensor.<name>_import_price`)

- **State:** All-in import price for the current hour
- **Unit:** Inherited from the source NordPool entity (e.g. `SEK/kWh`)
- **Attribute `prices`:** Dict of `{ISO datetime string: all-in price}` for all available slots

### Export Price (`sensor.<name>_export_price`)

- **State:** All-in export price for the current hour
- **Unit:** Inherited from the source NordPool entity
- **Attribute `prices`:** Same structure as Import Price

### Example attribute value

```yaml
prices:
  "2024-06-15T00:00:00+02:00": 0.643
  "2024-06-15T01:00:00+02:00": 0.601
  "2024-06-15T02:00:00+02:00": 0.589
  # … 24–48 entries total
```

## Troubleshooting

### Entity not found

Make sure the NordPool integration is configured and the sensor entity exists in Home Assistant before setting up this integration.

### Entity unavailable

The NordPool sensor is currently in an unavailable or unknown state. This happens at startup before the NordPool integration has fetched its first data. The import/export sensors will become available automatically once the NordPool entity has data.

### Entity invalid

The selected sensor does not have a `raw_today` or `prices_today` attribute. Verify that the correct NordPool sensor entity was selected.

### Formula invalid

The formula contains a syntax error or evaluates to something that is not a number. Test your formula in the Home Assistant **Developer Tools → Template** editor using:

```jinja2
{{ price * 1.25 + 0.107 }}
```

substituting `price` with a literal number.

### Enable debug logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nordpool_allin: debug
```

## Contributing

Contributions are welcome. Please open an issue or pull request on [GitHub](https://github.com/ksjoberg/nordpool_allin).

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@ksjoberg][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/ksjoberg/nordpool_allin.svg?style=for-the-badge
[commits]: https://github.com/ksjoberg/nordpool_allin/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/ksjoberg/nordpool_allin.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40ksjoberg-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/ksjoberg/nordpool_allin.svg?style=for-the-badge
[releases]: https://github.com/ksjoberg/nordpool_allin/releases
[user_profile]: https://github.com/ksjoberg
