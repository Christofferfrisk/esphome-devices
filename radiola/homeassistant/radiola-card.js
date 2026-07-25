/* Radiola dial card — a skeuomorphic Lovelace card mirroring the physical
 * motorized dial. See homeassistant/README.md for install and config. */

class RadiolaCard extends HTMLElement {
  setConfig(config) {
    if (!config.position_entity) throw new Error("radiola-card: position_entity is required");
    this._config = Object.assign(
      {
        mode_entity: "sensor.radiola_radiola_mode",
        dial_mode_entity: "sensor.radiola_dial_mode",
        station_set_entity: "input_select.radiola_station_set",
        media_entity: "media_player.kitchen",
        volume_entity: "input_number.radiola_card_volume",
        lp_loaded_entity: "input_boolean.radiola_lp_loaded",
        title: "Radiola",
        stations: [
          { pct: 10, name: "Station 1" },
          { pct: 36.7, name: "Station 2" },
          { pct: 63.3, name: "Station 3" },
          { pct: 90, name: "Station 4" },
        ],
        station_sets: {
          "Original Mix": [
            { pct: 10, name: "Station 1" },
            { pct: 36.7, name: "Jazz" },
            { pct: 63.3, name: "Wine Dinner" },
            { pct: 90, name: "Random" },
          ],
          "Discovery Radio": [
            { pct: 10, name: "Midnight Velocity" },
            { pct: 36.7, name: "Neon Indie" },
            { pct: 63.3, name: "Open Road Folk" },
            { pct: 90, name: "Modern Metalcore" },
          ],
        },
      },
      config
    );
    if (config.stations && !config.station_sets) {
      this._config.station_sets["Original Mix"] = config.stations;
    }
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

  _activeSetName() {
    const sets = this._config.station_sets || {};
    const selected = this._state(this._config.station_set_entity);
    if (selected && sets[selected]) return selected;
    return Object.keys(sets)[0];
  }

  _activeStations() {
    const name = this._activeSetName();
    return (name && this._config.station_sets[name]) || this._config.stations || [];
  }

  _build() {
    const c = this._config;
    const X0 = 34, X1 = 366; // dial band extent in the 400-wide viewBox
    const BAND_Y = 95;
    const stationMarks = this._activeStations()
      .map((st, i) => {
        const x = X0 + (st.pct / 100) * (X1 - X0);
        const below = i % 2 === 1;
        const lineY1 = below ? BAND_Y + 1 : BAND_Y - 14;
        const lineY2 = below ? BAND_Y + 9 : BAND_Y - 1;
        const labelY = below ? BAND_Y + 22 : BAND_Y - 18;
        return `
          <g class="rc-stationmark ${below ? "below" : "above"}" data-index="${i}">
            <line x1="${x}" y1="${lineY1}" x2="${x}" y2="${lineY2}" class="rc-stationline"/>
            <text x="${x}" y="${labelY}" class="rc-stationname" text-anchor="middle">${st.name}</text>
          </g>`;
      })
      .join("");
    const stationSetOptions = Object.keys(c.station_sets || {})
      .map((name) => `<option value="${name}">${name}</option>`)
      .join("");
    let ticks = "";
    for (let p = 0; p <= 100; p += 5) {
      const x = X0 + (p / 100) * (X1 - X0);
      const h = p % 20 === 0 ? 10 : 5;
      ticks += `<line x1="${x}" y1="${BAND_Y - h}" x2="${x}" y2="${BAND_Y}" class="rc-tick"/>`;
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
          .rc-bank {
            min-width: 120px; max-width: 160px; padding: 5px 8px;
            border: 1px solid rgba(216,185,106,0.55); border-radius: 7px;
            background: #2b2115; color: #ead9a5; font: inherit;
          }
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
            flex: 0 0 auto; cursor: pointer;
            border: 1px solid rgba(216,185,106,0.55); border-radius: 7px;
            width: 38px; height: 38px; font-size: 1.05em; line-height: 1;
            background: #2b2115; color: #ead9a5;
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
          .rc-lpdeck {
            display: none; position: relative; overflow: hidden; border-radius: 10px;
            background: radial-gradient(ellipse at 50% 0%, #3d2f1e 0%, #221a10 75%);
            box-shadow: inset 0 0 18px rgba(0,0,0,0.8);
          }
          .rc-lpdeck svg { display: block; width: 100%; }
          .rc-lp-mode .rc-dial { display: none; }
          .rc-lp-mode .rc-lpdeck { display: block; }
          .rc-record {
            transform-origin: 112px 62px;
            filter: drop-shadow(0 3px 5px rgba(0,0,0,0.65));
          }
          .rc-record.playing { animation: rc-record-spin 2.8s linear infinite; }
          @keyframes rc-record-spin { to { transform: rotate(360deg); } }
          .rc-tonearm-group {
            transform-origin: 213px 25px;
            transform: rotate(-9deg);
            transition: transform 0.45s ease;
          }
          .rc-tonearm-group.playing { transform: rotate(0deg); }
          .rc-vinyl { fill: #11100e; stroke: #d8b96a; stroke-width: 1; }
          .rc-groove { fill: none; stroke: #6d6043; stroke-width: 0.65; opacity: 0.6; }
          .rc-record-label { fill: #a95b24; stroke: #e8d49a; stroke-width: 0.8; }
          .rc-record-label-ring { fill: none; stroke: #f0dfa8; stroke-width: 0.7; opacity: 0.8; }
          .rc-spindle { fill: #ead9a5; }
          .rc-tonearm { fill: none; stroke: #d8b96a; stroke-width: 4;
            stroke-linecap: round; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.6)); }
          .rc-tonearm-base { fill: #352717; stroke: #e8d49a; stroke-width: 2; }
          .rc-stylus { fill: #e04b30; stroke: #f0dfa8; stroke-width: 0.7; }
          .rc-cover-frame {
            fill: #17120d; stroke: #d8b96a; stroke-width: 1.5;
            filter: drop-shadow(0 3px 5px rgba(0,0,0,0.65));
          }
          .rc-cover-placeholder { fill: #2b2115; stroke: #6f5a32; stroke-width: 1; }
          .rc-cover-placeholder-text {
            fill: #d8b96a; font: italic 20px Georgia, 'Times New Roman', serif;
          }
          .rc-lpdeck-brand {
            fill: #f0dfa8; font: italic 14px 'Brush Script MT', 'Segoe Script', cursive;
          }
          .rc-spotify-attribution {
            fill: #b9a777; font: 7px Arial, sans-serif; letter-spacing: 0.08em;
          }
          .rc-lpmeta {
            position: absolute; left: 5%; right: 5%; top: 80%;
            color: #e8d49a; font-family: Georgia, 'Times New Roman', serif;
            text-align: center; min-width: 0;
          }
          .rc-lptitle, .rc-lpartist {
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
          }
          .rc-lptitle { font-weight: 700; color: #ffdf80; }
          .rc-lpartist { margin-top: 3px; font-size: 0.86em; opacity: 0.8; }
          .rc-nocal { fill: #b98; font-size: 12px; }
          .rc-standby .rc-dial { filter: brightness(0.45) saturate(0.5); }
          .rc-standby .rc-lpdeck { filter: brightness(0.45) saturate(0.5); }
          .rc-lp-controls {
            display: none; align-items: center; justify-content: center;
            flex-wrap: wrap; gap: 7px; margin-top: 9px;
          }
          .rc-lp-mode .rc-lp-controls { display: flex; }
          .rc-lp-mode .rc-bank,
          .rc-lp-mode .rc-radio-next,
          .rc-lp-mode #rc-play { display: none; }
          .rc-transportbtn {
            cursor: pointer; padding: 6px 10px;
            border: 1px solid rgba(216,185,106,0.55); border-radius: 7px;
            background: #2b2115; color: #ead9a5; font: inherit;
          }
          .rc-transportbtn:disabled { opacity: 0.42; cursor: default; }
          .rc-controls {
            display: flex; align-items: center; gap: 9px; margin-top: 9px;
            color: var(--secondary-text-color); font-size: 0.88em;
          }
          .rc-volume {
            flex: 1 1 auto; min-width: 80px; accent-color: #c98232;
            cursor: pointer;
          }
          .rc-volume-value {
            flex: 0 0 34px; text-align: right; font-variant-numeric: tabular-nums;
          }
          .rc-nextbtn {
            flex: 0 0 auto; cursor: pointer; padding: 6px 11px;
            border: 1px solid rgba(216,185,106,0.55); border-radius: 7px;
            background: #2b2115; color: #ead9a5; font: inherit;
          }
        </style>
        <div class="rc-wrap">
          <div class="rc-head">
            <span class="rc-title">${c.title}</span>
            <select class="rc-bank" id="rc-bank" title="Station set">${stationSetOptions}</select>
            <span class="rc-badge" id="rc-badge">—</span>
            <span class="rc-station" id="rc-station"></span>
            <button class="rc-playbtn" id="rc-play" title="Play / Pause">▶</button>
          </div>
          <svg class="rc-dial" viewBox="0 0 400 124" id="rc-svg">
            <rect x="20" y="12" width="360" height="108" rx="6" class="rc-glass"/>
            ${logo}
            <line x1="${X0}" y1="${BAND_Y}" x2="${X1}" y2="${BAND_Y}" class="rc-band"/>
            ${ticks}
            ${stationMarks}
            <line x1="0" y1="14" x2="0" y2="120" class="rc-needle" id="rc-needle"
                  transform="translate(${X0},0)"/>
            <text x="200" y="68" text-anchor="middle" class="rc-nocal" id="rc-nocal"
                  style="display:none">dial not calibrated</text>
          </svg>
          <div class="rc-lpdeck" id="rc-lpdeck">
            <svg viewBox="0 0 400 150" role="img" aria-label="Radiola record player">
              <rect x="20" y="12" width="360" height="134" rx="6" class="rc-glass"/>
              <circle cx="112" cy="62" r="49" fill="#1b1711" stroke="#6f5a32" stroke-width="2"/>
              <g class="rc-record" id="rc-record">
                <circle cx="112" cy="62" r="44" class="rc-vinyl"/>
                <circle cx="112" cy="62" r="37" class="rc-groove"/>
                <circle cx="112" cy="62" r="31" class="rc-groove"/>
                <circle cx="112" cy="62" r="25" class="rc-groove"/>
                <circle cx="112" cy="62" r="18" class="rc-groove"/>
                <circle cx="112" cy="62" r="12" class="rc-record-label"/>
                <circle cx="112" cy="62" r="8" class="rc-record-label-ring"/>
                <path d="M104 62 Q112 56 120 62 Q112 68 104 62 Z" fill="#f0dfa8" opacity="0.8"/>
                <circle cx="112" cy="62" r="2.2" class="rc-spindle"/>
              </g>
              <g class="rc-tonearm-group" id="rc-tonearm">
                <circle cx="213" cy="25" r="11" class="rc-tonearm-base"/>
                <circle cx="213" cy="25" r="4" fill="#d8b96a"/>
                <path d="M213 30 C205 47, 183 59, 157 69" class="rc-tonearm"/>
                <path d="M151 67 L160 70 L157 77 L149 74 Z" class="rc-stylus"/>
              </g>
              <text x="247" y="24" text-anchor="middle" class="rc-lpdeck-brand">Radiola LP</text>
              <rect x="276" y="15" width="90" height="90" rx="2" class="rc-cover-frame"/>
              <g id="rc-cover-placeholder">
                <rect x="281" y="20" width="80" height="80" class="rc-cover-placeholder"/>
                <text x="321" y="67" text-anchor="middle" class="rc-cover-placeholder-text">LP</text>
              </g>
              <a id="rc-cover-link" target="_blank" rel="noopener">
                <image id="rc-lp-cover" x="281" y="20" width="80" height="80"
                       preserveAspectRatio="xMidYMid meet" style="display:none"/>
              </a>
              <text x="321" y="114" text-anchor="middle" class="rc-spotify-attribution">
                SPOTIFY
              </text>
            </svg>
            <div class="rc-lpmeta">
              <div class="rc-lptitle" id="rc-lptitle">Waiting for a record</div>
              <div class="rc-lpartist" id="rc-lpartist">Present an NFC album</div>
            </div>
          </div>
          <div class="rc-lp-controls">
            <button class="rc-transportbtn" id="rc-lp-prev" title="Previous track">⏮ Previous</button>
            <button class="rc-transportbtn" id="rc-lp-play" title="Play">▶ Play</button>
            <button class="rc-transportbtn" id="rc-lp-pause" title="Pause">❚❚ Pause</button>
            <button class="rc-transportbtn" id="rc-lp-next" title="Next track">Next ⏭</button>
          </div>
          <div class="rc-controls">
            <span aria-hidden="true">🔊</span>
            <input class="rc-volume" id="rc-volume" type="range" min="0" max="100"
                   step="1" aria-label="Playback volume"/>
            <span class="rc-volume-value" id="rc-volume-value">—</span>
            <button class="rc-nextbtn rc-radio-next" id="rc-next" title="Next track">Next ⏭</button>
          </div>
        </div>
      </ha-card>`;

    this._X0 = X0;
    this._X1 = X1;
    this.querySelector("#rc-play").addEventListener("click", () => {
      this._hass.callService("media_player", "media_play_pause", {
        entity_id: this._config.media_entity,
      });
    });
    const volume = this.querySelector("#rc-volume");
    volume.addEventListener("pointerdown", () => {
      this._volumeDragging = true;
    });
    volume.addEventListener("input", (event) => {
      this.querySelector("#rc-volume-value").textContent = `${event.target.value}%`;
    });
    volume.addEventListener("change", (event) => {
      this._volumeDragging = false;
      const pct = Number(event.target.value);
      this._hass.callService("input_number", "set_value", {
        entity_id: this._config.volume_entity,
        value: pct,
      });
      // Sonos uses real mute during station preload, so its retained volume can
      // safely be changed here without making the preload audible.
      this._hass.callService("media_player", "volume_set", {
        entity_id: this._config.media_entity,
        volume_level: pct / 100,
      });
    });
    volume.addEventListener("pointercancel", () => {
      this._volumeDragging = false;
    });
    this.querySelector("#rc-next").addEventListener("click", () => {
      this._hass.callService("media_player", "media_next_track", {
        entity_id: this._config.media_entity,
      });
    });
    this.querySelector("#rc-lp-prev").addEventListener("click", () => {
      this._hass.callService("media_player", "media_previous_track", {
        entity_id: this._config.media_entity,
      });
    });
    this.querySelector("#rc-lp-play").addEventListener("click", () => {
      this._hass.callService("media_player", "media_play", {
        entity_id: this._config.media_entity,
      });
    });
    this.querySelector("#rc-lp-pause").addEventListener("click", () => {
      this._hass.callService("media_player", "media_pause", {
        entity_id: this._config.media_entity,
      });
    });
    this.querySelector("#rc-lp-next").addEventListener("click", () => {
      this._hass.callService("media_player", "media_next_track", {
        entity_id: this._config.media_entity,
      });
    });
    this.querySelector("#rc-bank").addEventListener("change", (event) => {
      this._hass.callService("input_select", "select_option", {
        entity_id: this._config.station_set_entity,
        option: event.target.value,
      });
    });
    this._built = true;
  }

  _update() {
    const c = this._config;
    const mode = this._state(c.mode_entity) || "idle";
    const dialMode = this._state(c.dial_mode_entity) || "unknown";
    const setName = this._activeSetName();
    const stations = this._activeStations();
    const pos = parseFloat(this._state(c.position_entity));
    const media = this._hass.states[c.media_entity];
    const lpLoaded = this._state(c.lp_loaded_entity) === "on";

    const badge = this.querySelector("#rc-badge");
    badge.textContent = mode;
    badge.className = "rc-badge " + mode;
    const wrap = this.querySelector(".rc-wrap");
    wrap.classList.toggle("rc-standby", mode === "standby");
    wrap.classList.toggle("rc-lp-mode", mode === "lp");
    const bank = this.querySelector("#rc-bank");
    if (setName && bank.value !== setName) bank.value = setName;

    this.querySelectorAll(".rc-stationmark").forEach((mark, i) => {
      const st = stations[i];
      if (!st) return;
      const x = this._X0 + (st.pct / 100) * (this._X1 - this._X0);
      const line = mark.querySelector("line");
      const text = mark.querySelector("text");
      line.setAttribute("x1", x);
      line.setAttribute("x2", x);
      text.setAttribute("x", x);
      text.textContent = st.name;
    });

    // Station / now-playing line
    let label = "";
    if (mode === "lp") {
      label = media && media.attributes.media_title
        ? `♪ ${media.attributes.media_title}` : "record on";
    } else if (mode === "radio") {
      const m = dialMode.match(/^station_(\d)$/);
      if (m) {
        const st = stations[parseInt(m[1]) - 1];
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

    // Player state drives both the compact radio button and the LP deck.
    const isPlaying = !!media && media.state === "playing";
    const lpIsPlaying = mode === "lp" && lpLoaded && isPlaying;
    this.querySelector("#rc-play").textContent =
      isPlaying ? "❚❚" : "▶";
    this.querySelector("#rc-record").classList.toggle("playing", lpIsPlaying);
    this.querySelector("#rc-tonearm").classList.toggle("playing", lpIsPlaying);
    this.querySelector("#rc-lptitle").textContent =
      lpLoaded && media && (media.attributes.media_album_name || media.attributes.media_title)
        ? (media.attributes.media_album_name || media.attributes.media_title)
        : "Scan an LP to begin";
    this.querySelector("#rc-lpartist").textContent =
      lpLoaded && media && media.attributes.media_artist
        ? media.attributes.media_artist
        : "Transport controls are locked";

    // Sonos normally proxies Spotify artwork through entity_picture; some
    // media players expose the original URL as media_image_url instead.
    const rawCover = lpLoaded && media
      ? (media.attributes.entity_picture || media.attributes.media_image_url || "")
      : "";
    const coverUrl = rawCover && rawCover.startsWith("/")
      ? this._hass.hassUrl(rawCover)
      : rawCover;
    const cover = this.querySelector("#rc-lp-cover");
    const coverPlaceholder = this.querySelector("#rc-cover-placeholder");
    cover.style.display = coverUrl ? "" : "none";
    coverPlaceholder.style.display = coverUrl ? "none" : "";
    if (coverUrl) cover.setAttribute("href", coverUrl);
    else cover.removeAttribute("href");

    // Link the unmodified artwork back to the applicable Spotify item when
    // Sonos exposes a Spotify URI (plain or URL-encoded) as media_content_id.
    const contentId = media && media.attributes.media_content_id
      ? String(media.attributes.media_content_id)
      : "";
    const spotifyMatch = contentId.match(
      /spotify(?::|%3a)(album|track)(?::|%3a)([a-z0-9]+)/i
    );
    const coverLink = this.querySelector("#rc-cover-link");
    if (spotifyMatch) {
      coverLink.setAttribute(
        "href",
        `https://open.spotify.com/${spotifyMatch[1].toLowerCase()}/${spotifyMatch[2]}`
      );
      coverLink.style.pointerEvents = "auto";
    } else {
      coverLink.removeAttribute("href");
      coverLink.style.pointerEvents = "none";
    }
    this.querySelector("#rc-lp-prev").disabled = !lpLoaded;
    this.querySelector("#rc-lp-next").disabled = !lpLoaded;
    this.querySelector("#rc-lp-play").disabled = !lpLoaded || lpIsPlaying;
    this.querySelector("#rc-lp-pause").disabled = !lpLoaded || !lpIsPlaying;

    // Sonos retains its actual volume while muted between stations. Prefer
    // that live level; use the helper only if the player does not report one.
    const volume = this.querySelector("#rc-volume");
    const volumeValue = this.querySelector("#rc-volume-value");
    const savedState = this._state(c.volume_entity);
    const savedPct = savedState === null ? NaN : Number(savedState);
    const mediaLevel = media && Number(media.attributes.volume_level);
    const pct = Number.isFinite(mediaLevel)
      ? Math.round(mediaLevel * 100)
      : (Number.isFinite(savedPct) ? Math.round(savedPct) : NaN);
    if (Number.isFinite(pct)) {
      if (!this._volumeDragging) volume.value = pct;
      if (!this._volumeDragging) volumeValue.textContent = `${pct}%`;
      volume.disabled = false;
    } else {
      volume.disabled = true;
      volumeValue.textContent = "—";
    }
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("radiola-card", RadiolaCard);
