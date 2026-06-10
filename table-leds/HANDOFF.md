# Handoff prompt — flash from another computer

Paste the block below into Claude Code (or any assistant) on the other
computer to continue this project.

---

**Project: ESP32 table LED controller (ESPHome + Home Assistant)**

I'm building an ESPHome firmware for table LED lights and want to flash it from
this computer.

**Hardware:**
- Board: ESP32 WROOM dev board (`board: esp32dev`), USB-to-UART chip is
  **Silicon Labs CP2102** (`VID_10C4 / PID_EA60`) — needs the CP210x VCP driver
  on Windows to show up as a COM port.
- LEDs: BTF-Lighting **SK6812 RGBW** addressable strip, 5V, color order
  **GRBW**, 60 LED/m, 5m = **300 LEDs**.
- Wiring: strip **DATA → ESP32 GPIO14** (no series resistor — fine for short
  leads). Strip powered by a **separate 5V supply** (300 RGBW LEDs draw up to
  ~18A at full white); ESP32 GND and PSU GND **must share a common ground**.

**Project files** live in a git repo: `esphome-devices/table-leds/` containing
`table-leds.yaml` and `README.md`. The config uses `esp32_rmt_led_strip` with
`chipset: SK6812`, `rgb_order: GRB`, `is_rgbw: true`, `num_leds: 300`,
`pin: GPIO14`, plus HA API (encrypted), OTA, WiFi with fallback AP, and several
addressable effects. It expects a sibling `secrets.yaml` (git-ignored) with
`wifi_ssid`, `wifi_password`, `api_encryption_key`, `ota_password`,
`fallback_ap_password`.

If I don't already have the repo on this machine, recreate the `table-leds.yaml`
from the spec above.

**What I need help with now:**
1. Confirm the CP2102/CP210x driver is installed and the ESP32 enumerates as a
   COM port (it failed on my other machine with driver problem code 28 /
   `CM_PROB_FAILED_INSTALL`).
2. Create `secrets.yaml` from my values.
3. Flash over USB the first time with `esphome run table-leds/table-leds.yaml`,
   then it auto-discovers in Home Assistant via the ESPHome integration as
   `light.table_leds_strip`. After the first flash, updates go over WiFi (OTA).

---

## Notes / current state (2026-06-10)

- The original machine has the CP2102 board attached but the CP210x driver
  won't install (not running as admin). Windows Update *does* offer the driver:
  "Silicon Laboratories Inc. - Ports - 11.2.0.167". Installing from an elevated
  prompt or via Device Manager → Update driver → Search automatically fixes it.
- Two copies of this repo exist in Nextcloud: the git repo under
  `Nextcloud2/ssd/projects/esphome-devices` and a plain copy under
  `Nextcloud/ssd/projects/esphome-devices`. This file is in the `Nextcloud`
  (no-2) copy so it syncs.
