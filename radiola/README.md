# radiola

A standalone DIY internet radio built around an ESP32 running ESPHome.

## Hardware

- **MCU:** ESP32 dev board (`esp32dev`)
- **Audio:** DFPlayer Mini (UART) with a microSD card holding startup
  sounds and station chimes
- **Indicators:** 5× addressable LEDs (`radiola_led_1..5`) for a
  startup "wake-up" animation and status / VU display
- **Input:** AS5600 magnetic rotary encoder mounted on a NEMA17
  stepper-motor holder
- **Network:** Static IP on the home subnet, integrated with Home
  Assistant via the ESPHome API

## Behaviour

On boot the device checks a `standby_mode` flag. If standby is off it
plays a startup chime via DFPlayer and runs an LED sweep animation
before going into normal operation; if standby is on it skips both.

## Build

```bash
esphome run radiola1.yaml
```

Requires a `secrets.yaml` in this folder with `wifi_ssid` and
`wifi_password` (and any other `!secret` keys referenced by the YAML).

## Files

- `radiola1.yaml` — ESPHome device configuration
