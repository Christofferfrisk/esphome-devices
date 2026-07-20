# Radiola — Home Assistant dial card

A custom Lovelace card that mirrors the physical radio: vintage dial
face with station names and a gliding needle (live from the AS5600
encoder), mode badge (radio / lp / standby), current station or
now-playing title, and a play/pause button for the Sonos.

The needle position comes from `Dial Position Percent`, the mode from
`Radiola Mode`, and the tuned station from `Dial Mode` — all published
by `radiola1.yaml`. If the dial isn't calibrated the card says so
instead of showing a needle.

## Install

1. Copy `radiola-card.js` to your HA config: `/config/www/radiola-card.js`
2. Add it as a dashboard resource (Settings → Dashboards → ⋮ →
   Resources → Add):
   - URL: `/local/radiola-card.js`
   - Type: JavaScript module
3. Add the card to a dashboard (YAML mode or manual card):

```yaml
type: custom:radiola-card
title: Radiola
position_entity: sensor.radiola1_dial_position_percent
mode_entity: sensor.radiola1_radiola_mode
dial_mode_entity: sensor.radiola1_dial_mode
media_entity: media_player.kitchen
stations:
  - pct: 20
    name: "Station 1"
  - pct: 40
    name: "Station 2"
  - pct: 60
    name: "Station 3"
  - pct: 80
    name: "Station 4"
```

`stations` percentages should match the `station_*_pct` substitutions in
`radiola1.yaml`; the names are whatever you want printed on the glass.

By default the glass carries a script "Radiola" wordmark with an
underline swash. For the real logo, save your scan (transparent PNG
works best) as `/config/www/radiola-logo.png` and add:

```yaml
logo_url: /local/radiola-logo.png
```

The image is tinted toward the glass's gold automatically.
Entity ids may differ slightly depending on how HA named them — check
under the ESPHome device page.
