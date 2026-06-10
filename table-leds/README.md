# Table LEDs

ESP32 WROOM driving a BTF-Lighting **SK6812 RGBW** addressable strip
(5 V, GRBW, 60 LED/m, 5 m = 300 LEDs), exposed to Home Assistant as a single
RGBW light with brightness + effects.

## Wiring

| Strip wire | Connects to |
| --- | --- |
| **+5V** | Dedicated 5 V PSU **+** (not the ESP32) |
| **GND** | PSU **−** *and* an ESP32 **GND** (common ground required) |
| **DATA** | ESP32 **GPIO14** to the strip's *input* end (optional ~330 Ω series resistor) |

Power notes:
- 300 RGBW LEDs draw up to ~18 A at full white — size the PSU accordingly
  (maker recommends DC5V/20A/100W).
- Inject 5 V at both ends to avoid brightness drop / color shift.
- Add a ~1000 µF cap across +5V/GND near the strip input.

If you cut the strip, update `num_leds` in `table-leds.yaml`.

## Flash

Needs a sibling `secrets.yaml` (git-ignored) with `wifi_ssid`, `wifi_password`,
`api_encryption_key`, `ota_password`, `fallback_ap_password`. Generate the API
key with `openssl rand -base64 32`.

```bash
esphome run table-leds/table-leds.yaml
```

USB for the first flash, OTA after. Home Assistant auto-discovers it via the
ESPHome integration; the light entity is `light.table_leds_strip`.

## Tuning

- `data_pin` / `num_leds` are in the `substitutions:` block at the top of the YAML.
- Wrong colors → try `rgb_order: RGB` or `GBR`. Plain WS2812B → `chipset: WS2812`.
