# firebeetle weather display

A low-power e-ink weather display driven by a DFRobot FireBeetle ESP32
running ESPHome, pulling forecasts directly from the Swedish SMHI open
data API.

## Hardware

- **MCU:** DFRobot FireBeetle ESP32 (`firebeetle32`)
- **Display:** e-ink panel
- **Power:** Battery-friendly — uses ESPHome `deep_sleep` between
  refreshes with a 90 s safe window after every boot for HA control
  and OTA updates

## How it works

- **`firebeetle-display.yaml`** — the device configuration. On boot
  the firmware stays awake 90 s to allow Home Assistant to push state
  and OTA updates to land, then either keeps running (if the HA
  `stay_awake_flag` switch is on) or schedules deep sleep until the
  next scheduled wake. Honours quiet hours.

- **`smhi_direct.yaml`** — a Home Assistant package that fetches the
  SMHI open-data point forecast for Uppsala (lat 59.8586, lon 17.6389)
  every 30 minutes via `rest:` sensors. Drop into HA via
  `homeassistant: packages: smhi: !include smhi_direct.yaml`. Decodes
  the SMHI `Wsymb2` weather codes into temperature, humidity, and
  symbol sensors that the FireBeetle then renders.

## Build

```bash
esphome run firebeetle-display.yaml
```

Requires a `secrets.yaml` in this folder with `wifi_ssid` and
`wifi_password`.

## Notes

- Coordinates are hard-coded to Uppsala — change `lat`/`lon` in
  `smhi_direct.yaml` for other locations.
- The Watchdog timeout is raised to 60 s
  (`CONFIG_ESP_TASK_WDT_TIMEOUT_S`) to tolerate slow e-ink refreshes.
