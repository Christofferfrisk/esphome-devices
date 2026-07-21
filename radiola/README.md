# radiola

A DIY internet radio in an old radio chassis, built around an ESP32
running ESPHome and integrated with Home Assistant. Tuning works like
the original set: a knob drives a linear dial pointer, stations sit at
fixed positions on the band, and static hisses between them.

## Hardware

- **MCU:** ESP32 dev board (`esp32dev`)
- **Dial:** knob-driven linear pointer on a dial cord, with
  - AS5600 magnetic rotary encoder (I2C, `0x36`) for absolute position
  - NEMA17 stepper + DRV8825 driver so the radio can also move the dial
    itself (seek, snap-to-station, standby park, LP progress)
- **Audio:** DFPlayer Mini (UART) with static/chime WAVs on microSD;
  music playback happens on a Sonos (`media_player.kitchen`) via HA
- **Volume:** potentiometer on ADS1115 (I2C, `0x48`), channel A1
- **LP mode:** PN532 NFC reader (I2C) — placing a tagged "record" on the
  radio plays that album on the Sonos
- **Indicators:** 5× dimmable LEDs (LEDC via MOSFETs) for startup /
  shutdown sequences and calibration feedback
- **Controls:** 4 latching piano-key buttons (mechanical interlock, one
  at a time) + a standby contact plate on GPIO4
- **Power:** PMOS-switched 12V rail (GPIO14, on/off only — never PWM);
  the AS5600 must be fed from the always-on 3.3V rail so the dial keeps
  being tracked in standby

## How the dial works

The AS5600 is polled every 50 ms and accumulated into a multi-turn
position (`dial_pos`, persisted to flash every 20 s). Everything else
derives from it:

- **Soft endstops** — `dial_min`/`dial_max` are set by calibration. In a
  guard band near either limit the motor energizes and *springs back*
  toward the safe span: turning inward is assisted, outward is resisted,
  and the pointer is never locked out of range.
- **Stations** — four positions at 20/40/60/80 % of the usable span
  (`station_*_pct` substitutions), each with a ±5 % capture zone.
- **Snap-to-station** — once the hand-turned dial settles near a
  station, the motor pulls it to dead center.
- **Seek** — Button 3 (in radio mode) sweeps to the next station with
  static hissing until arrival.
- **Static swim** — between stations the DFPlayer hiss scales with both
  distance from the nearest station and the volume knob.
- **Preload** — while tuning through noise, a text sensor names the
  station the dial is heading toward (direction-aware, with jitter
  hysteresis) so HA can start its playlist muted before arrival.
- **Standby park** — entering standby glides the pointer to the left
  end while the shutdown sound plays, then cuts the 12V rail.
- **Failsafe** — if the encoder goes silent for >1 s the motor is
  disabled and moves are locked out until recalibrated.

## Calibration (dial limits)

Limits live in flash and survive reboots. To (re)set them — needed on
first flash, or if the pointer was moved while unplugged:

1. Press **Button 4 five times within 3 s** — LED 1 blinks, coils release
2. Turn the dial by hand to the **left** stop, press **Button 3** — LED 5 blinks
3. Turn to the **right** stop, press **Button 3** — limits saved, done

If the boot log says the motor is disabled (`dial_needs_cal`), this
sequence clears it.

## Home Assistant side

The ESP exposes `Dial Mode` (station_1..4 / noise), `Radiola Preload
Station`, `LP Progress` (number), the volume knob, and the dial
position. HA automations are expected to: start the preloaded playlist
muted, ramp volume on station arrival, mute on leaving a station, and
feed `LP Progress` from the Sonos media position. Spotify URIs for the
stations and NFC albums are still placeholders in the config.

## First-hardware checklist

1. Set real DRV8825 pins in `substitutions` (`dial_step_pin` etc. are
   placeholders)
2. `esphome config radiola1.yaml` — validates the `as5600`/`stepper`
   schemas against your ESPHome version
3. Measure `dial_counts_per_step` (command N steps, read encoder delta)
4. Set the DRV8825 Vref as low as reliably moves the pointer — this caps
   the force the motor can ever exert on the dial cord
5. Tune `dial_max_speed` / `dial_accel` (values are in steps/s at the
   DRV8825 MODE0-2 microstep setting)
6. Run the limit calibration (above)

### DRV8825 essentials

- `EN` is active-low; the firmware's `Dial Motor Coils` switch already
  accounts for this.
- Tie `nSLEEP` and `nRESET` high (normally together) or the driver will
  ignore STEP pulses. Leave `FAULT` unconnected unless a spare, protected
  ESP32 input is available for it.
- Put at least a 100 uF electrolytic capacitor directly across `VMOT` and
  motor GND. Do not plug or unplug the NEMA17 while the driver has power.
- The usual Pololu-style DRV8825 carrier with 0.1-ohm sense resistors uses
  `current limit = 2 x Vref`. Verify your board's documentation before
  setting it, then start at the lowest current that moves the dial reliably.

## Build

```bash
esphome run radiola1.yaml
```

Requires a `secrets.yaml` in this folder with `wifi_ssid` and
`wifi_password`.

## Files

- `radiola1.yaml` — ESPHome device configuration
