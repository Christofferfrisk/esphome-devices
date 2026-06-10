# ESPHome devices

A collection of personal ESPHome / Home Assistant device configs. Each
subfolder is a self-contained device with its own YAML and notes.

## Devices

| Folder | Device | Hardware | What it does |
| --- | --- | --- | --- |
| [`radiola/`](radiola/) | Internet radio | ESP32 + DFPlayer Mini + WS2812 LEDs + AS5600 rotary encoder | Standalone "retro" internet radio: encoder volume/station selection, animated LED VU/status ring, startup sounds via DFPlayer. |
| [`firebeetle/`](firebeetle/) | Weather e-ink display | DFRobot FireBeetle ESP32 + e-ink panel | Low-power deep-sleep weather display pulling forecasts directly from the SMHI open data API for Uppsala. |
| [`table-leds/`](table-leds/) | Table LED lights | ESP32 WROOM + SK6812 RGBW strip (300 LEDs) | Addressable RGBW table lighting exposed to Home Assistant as a single light with brightness + effects. |

## Usage

Each device YAML expects a sibling `secrets.yaml` with at least
`wifi_ssid` and `wifi_password`. `secrets.yaml` is git-ignored — create
your own. Flash with:

```bash
esphome run radiola/radiola1.yaml
esphome run firebeetle/firebeetle-display.yaml
esphome run table-leds/table-leds.yaml
```

## Author

Christoffer Frisk — https://github.com/Christofferfrisk
