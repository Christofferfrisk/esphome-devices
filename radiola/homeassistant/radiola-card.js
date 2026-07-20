/* Radiola dial card — a skeuomorphic Lovelace card mirroring the physical
 * motorized dial. See homeassistant/README.md for install and config. */

class RadiolaCard extends HTMLElement {
  setConfig(config) {
    if (!config.position_entity) throw new Error("radiola-card: position_entity is required");
    this._config = Object.assign(
      {
        mode_entity: "sensor.radiola1_radiola_mode",
        dial_mode_entity: "sensor.radiola1_dial_mode",
        media_entity: "media_player.kitchen",
        title: "Radiola",
        stations: [
          { pct: 20, name: "Station 1" },
          { pct: 40, name: "Station 2" },
          { pct: 60, name: "Station 3" },
          { pct: 80, name: "Station 4" },
        ],
      },
      config
    );
    this._built = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._built) this._build();
    this._update();
  }

  _state(entityId) {
    const s = this._hass.states[entityId];
    return s ? s.state : null;
  }

  _build() {
    const c = this._config;
    const X0 = 34, X1 = 366; // dial band extent in the 400-wide viewBox
    const stationMarks = c.stations
      .map((st) => {
        const x = X0 + (st.pct / 100) * (X1 - X0);
        return `
          <line x1="${x}" y1="82" x2="${x}" y2="106" class="rc-stationline"/>
          <text x="${x}" y="74" class="rc-stationname" text-anchor="middle">${st.name}</text>`;
      })
      .join("");
    let ticks = "";
    for (let p = 0; p <= 100; p += 5) {
      const x = X0 + (p / 100) * (X1 - X0);
      const h = p % 20 === 0 ? 10 : 5;
      ticks += `<line x1="${x}" y1="${107 - h}" x2="${x}" y2="107" class="rc-tick"/>`;
    }
    // Brand on the glass: the user's logo image if configured, otherwise a
    // script wordmark with an underline swash in the same engraved gold
    const logo = c.logo_url
      ? `<image href="${c.logo_url}" x="130" y="18" width="140" height="38"
           preserveAspectRatio="xMidYMid meet" class="rc-logoimg"/>`
      : `<text x="200" y="46" text-anchor="middle" class="rc-logo">Radiola</text>
         <path class="rc-swash"
           d="M128,55 Q200,66 270,42 Q215,62 130,57 Z"/>`;

    this.innerHTML = `
      <ha-card>
        <style>
          .rc-wrap { padding: 12px 16px 16px; }
          .rc-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
          .rc-title { font-weight: 600; font-size: 1.05em; flex: 0 0 auto; }
          .rc-badge {
            font-size: 0.72em; font-weight: 700; letter-spacing: 0.08em;
            padding: 2px 8px; border-radius: 10px; text-transform: uppercase;
            background: #555; color: #fff; flex: 0 0 auto;
          }
          .rc-badge.radio { background: #b5651d; }
          .rc-badge.lp { background: #6d4c8f; }
          .rc-badge.standby { background: #444; }
          .rc-station { flex: 1 1 auto; text-align: center; font-size: 0.95em;
            color: var(--secondary-text-color); overflow: hidden;
            text-overflow: ellipsis; white-space: nowrap; }
          .rc-playbtn {
            flex: 0 0 auto; cursor: pointer; border: none; border-radius: 50%;
            width: 38px; height: 38px; font-size: 1.05em; line-height: 1;
            background: var(--primary-color); color: var(--text-primary-color, #fff);
          }
          .rc-dial { display: block; width: 100%; border-radius: 10px;
            background: radial-gradient(ellipse at 50% 0%, #3d2f1e 0%, #221a10 75%);
            box-shadow: inset 0 0 18px rgba(0,0,0,0.8); }
          .rc-glass { fill: #f3e3b8; opacity: 0.08; }
          .rc-band { stroke: #d8b96a; stroke-width: 1.4; }
          .rc-tick { stroke: #d8b96a; stroke-width: 1; opacity: 0.7; }
          .rc-stationline { stroke: #e8d49a; stroke-width: 1.2; opacity: 0.9; }
          .rc-stationname { fill: #e8d49a; font-size: 12px;
            font-family: Georgia, 'Times New Roman', serif; }
          .rc-stationname.active { fill: #ffdf80; font-weight: bold; }
          .rc-logo {
            fill: #f0dfa8; opacity: 0.9; font-size: 34px; font-style: italic;
            font-family: 'Brush Script MT', 'Segoe Script', 'Lucida Handwriting', cursive;
          }
          .rc-swash { fill: #f0dfa8; opacity: 0.75; }
          .rc-logoimg { opacity: 0.85; filter: sepia(1) saturate(0.6) brightness(1.4); }
          .rc-needle { stroke: #e04b30; stroke-width: 2.5;
            filter: drop-shadow(0 0 3px rgba(224,75,48,0.8));
            transition: transform 0.35s ease-out; }
          .rc-nocal { fill: #b98; font-size: 12px; }
          .rc-standby .rc-dial { filter: brightness(0.45) saturate(0.5); }
        </style>
        <div class="rc-wrap">
          <div class="rc-head">
            <span class="rc-title">${c.title}</span>
            <span class="rc-badge" id="rc-badge">—</span>
            <span class="rc-station" id="rc-station"></span>
            <button class="rc-playbtn" id="rc-play" title="Play / Pause">▶</button>
          </div>
          <svg class="rc-dial" viewBox="0 0 400 130" id="rc-svg">
            <rect x="20" y="12" width="360" height="106" rx="6" class="rc-glass"/>
            ${logo}
            <line x1="${X0}" y1="107" x2="${X1}" y2="107" class="rc-band"/>
            ${ticks}
            ${stationMarks}
            <line x1="0" y1="14" x2="0" y2="112" class="rc-needle" id="rc-needle"
                  transform="translate(${X0},0)"/>
            <text x="200" y="92" text-anchor="middle" class="rc-nocal" id="rc-nocal"
                  style="display:none">dial not calibrated</text>
          </svg>
        </div>
      </ha-card>`;

    this._X0 = X0;
    this._X1 = X1;
    this.querySelector("#rc-play").addEventListener("click", () => {
      this._hass.callService("media_player", "media_play_pause", {
        entity_id: this._config.media_entity,
      });
    });
    this._built = true;
  }

  _update() {
    const c = this._config;
    const mode = this._state(c.mode_entity) || "idle";
    const dialMode = this._state(c.dial_mode_entity) || "unknown";
    const pos = parseFloat(this._state(c.position_entity));
    const media = this._hass.states[c.media_entity];

    const badge = this.querySelector("#rc-badge");
    badge.textContent = mode;
    badge.className = "rc-badge " + mode;
    this.querySelector(".rc-wrap").classList.toggle("rc-standby", mode === "standby");

    // Station / now-playing line
    let label = "";
    if (mode === "lp") {
      label = media && media.attributes.media_title
        ? `♪ ${media.attributes.media_title}` : "record on";
    } else if (mode === "radio") {
      const m = dialMode.match(/^station_(\d)$/);
      if (m) {
        const st = c.stations[parseInt(m[1]) - 1];
        label = st ? st.name : dialMode;
      } else if (dialMode === "noise") {
        label = "· · · tuning · · ·";
      }
    } else if (mode === "standby") {
      label = "standby";
    }
    this.querySelector("#rc-station").textContent = label;

    // Highlight the active station name on the glass
    const m = dialMode.match(/^station_(\d)$/);
    this.querySelectorAll(".rc-stationname").forEach((el, i) => {
      el.classList.toggle("active", !!m && i === parseInt(m[1]) - 1);
    });

    // Needle
    const needle = this.querySelector("#rc-needle");
    const nocal = this.querySelector("#rc-nocal");
    if (isNaN(pos)) {
      needle.style.display = "none";
      nocal.style.display = "";
    } else {
      needle.style.display = "";
      nocal.style.display = "none";
      const x = this._X0 + (pos / 100) * (this._X1 - this._X0);
      needle.setAttribute("transform", `translate(${x},0)`);
    }

    // Play / pause button reflects the media player
    this.querySelector("#rc-play").textContent =
      media && media.state === "playing" ? "❚❚" : "▶";
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("radiola-card", RadiolaCard);
