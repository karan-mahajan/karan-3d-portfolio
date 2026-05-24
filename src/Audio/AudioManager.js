/**
 * Procedural audio using Web Audio API — no external files required, so
 * everything works out of the box. Sounds:
 *
 *   playStep()      - quiet pink-noise click while walking/running
 *   playJump()      - short rising sine sweep
 *   playInteract()  - two-note ascending chime when opening a project / contact
 *   playWelcome()   - three-note arpeggio when the journey begins
 *   startAmbient()  - very-quiet sine drone for forest atmosphere
 *
 * Master gain is kept low (≤0.18) so nothing startles. The mute toggle
 * persists to localStorage.
 */

function randIn([min, max]) {
  return min + Math.random() * (max - min);
}

const STORAGE_KEY = 'karan-portfolio:muted';
// Tuned so the experience reads at ~30–50% browser volume. Mute toggle and
// the browser's own volume slider remain available.
const MASTER_LEVEL = 0.72;          // +10% from previous tuning
const FOOTSTEP_INTERVAL_WALK = 0.42;
const FOOTSTEP_INTERVAL_RUN = 0.28;
const BIRD_INTERVAL_RANGE = [3.5, 9]; // seconds between random bird chirps

// Mixkit CC0 WAV files in /static/sounds/. `splash-light` is the per-step
// wading splash, `splash-entry` is the louder one-shot when the player
// first hits the water; the ocean loop is a single bed whose gain rides
// the player's proximity to the shoreline (driven from App.js each tick).
const SPLASH_LIGHT_URL = '/sounds/splash-light.wav';
const SPLASH_ENTRY_URL = '/sounds/splash-entry.wav';
const OCEAN_LOOP_URL = '/sounds/ocean-loop.wav';
// Volume caps for the new water layers — kept relative to the master so
// muting still kills everything cleanly.
const SPLASH_STEP_VOL = 0.32;
const SPLASH_ENTRY_VOL = 0.55;
const OCEAN_AT_SHORE_VOL = 0.32;   // shore ambience when standing right on the beach
const OCEAN_IN_WATER_VOL = 0.50;   // bumped when the player is actually wading
const OCEAN_FALLOFF_M = 30;        // beyond this distance from the shore the ocean is silent

export class AudioManager {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.ambientGain = null;
    this.muted = localStorage.getItem(STORAGE_KEY) === '1';
    this._stepTimer = 0;
    this._stepOdd = false;
    this._wasStepping = false;
    this._wasGrounded = true;
    this._birdTimer = randIn(BIRD_INTERVAL_RANGE);
    /**
     * Optional callback fired once per step at the same instant the audio
     * step would play. Visual footprints subscribe here so the print drops
     * are perfectly synced to the (possibly silent) step cadence — even
     * when audio is muted, the cadence still ticks and prints still spawn.
     * Signature: `(odd: boolean) => void` — odd flips each step.
     */
    this.onStep = null;

    this.#installButton();
  }

  #ensureContext() {
    if (this.ctx) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = this.muted ? 0 : MASTER_LEVEL;
    this.master.connect(this.ctx.destination);
  }

  /** Called from main.js on the first user gesture (Start button / first key). */
  start() {
    this.#ensureContext();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();
    this.playWelcome();
    this.startAmbient();
    // Fire-and-forget — splash/ocean play methods no-op until buffers land.
    this.#loadWaterAudio();
  }

  /**
   * Decode the three WAV files dropped under /sounds and start the looping
   * ocean bed at zero gain. App.js drives gain from player proximity each
   * tick via setOceanProximity; splash one-shots are triggered by Water.js.
   */
  async #loadWaterAudio() {
    if (!this.ctx || this._waterAudioLoaded) return;
    this._waterAudioLoaded = true;
    const fetchBuffer = async (url) => {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status} ${url}`);
        const ab = await res.arrayBuffer();
        return await this.ctx.decodeAudioData(ab);
      } catch (err) {
        console.warn(`[Audio] failed to load ${url}`, err);
        return null;
      }
    };
    const [light, entry, ocean] = await Promise.all([
      fetchBuffer(SPLASH_LIGHT_URL),
      fetchBuffer(SPLASH_ENTRY_URL),
      fetchBuffer(OCEAN_LOOP_URL),
    ]);
    this._splashLight = light;
    this._splashEntry = entry;
    if (ocean) {
      const src = this.ctx.createBufferSource();
      src.buffer = ocean;
      src.loop = true;
      const gain = this.ctx.createGain();
      gain.gain.value = 0;
      src.connect(gain).connect(this.master);
      src.start();
      this.oceanSource = src;
      this.oceanGain = gain;
    }
  }

  /** One-shot splash. `entry` switches to the louder jump-in clip. */
  playSplash({ entry = false, volume = 1.0 } = {}) {
    if (!this.ctx || this.muted) return;
    const buf = entry ? this._splashEntry : this._splashLight;
    if (!buf) return; // buffer not loaded yet
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    // Small random pitch wobble so consecutive splashes don't feel sampled.
    src.playbackRate.value = 0.92 + Math.random() * 0.16;
    const gain = this.ctx.createGain();
    gain.gain.value = volume * (entry ? SPLASH_ENTRY_VOL : SPLASH_STEP_VOL);
    src.connect(gain).connect(this.master);
    src.start();
  }

  /**
   * Ride the ocean loop's gain off the player's distance from the shoreline.
   * Inside the island it falls to silent over OCEAN_FALLOFF_M; once the
   * player is actually wading we bump up to OCEAN_IN_WATER_VOL. Called from
   * App.js once per frame; smooth-ramps so the gain change isn't audible.
   */
  setOceanProximity(distFromCenter, shoreRadius = 45) {
    if (!this.ctx || !this.oceanGain) return;
    let target;
    if (distFromCenter > shoreRadius) {
      target = OCEAN_IN_WATER_VOL;
    } else {
      const distToShore = shoreRadius - distFromCenter;
      const proximity = Math.max(0, 1 - distToShore / OCEAN_FALLOFF_M);
      target = proximity * OCEAN_AT_SHORE_VOL;
    }
    const now = this.ctx.currentTime;
    this.oceanGain.gain.cancelScheduledValues(now);
    this.oceanGain.gain.linearRampToValueAtTime(target, now + 0.4);
  }

  setMuted(value) {
    this.muted = value;
    localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
    if (this.master) {
      const target = value ? 0 : MASTER_LEVEL;
      this.master.gain.cancelScheduledValues(this.ctx.currentTime);
      this.master.gain.linearRampToValueAtTime(target, this.ctx.currentTime + 0.15);
    }
    this.#updateButton();
  }

  // ── Per-frame: step cadence + jump detection + bird chirps ───────────────
  tick(delta, { moving, running, grounded }) {
    // Step cadence runs FIRST and regardless of audio context / mute state
    // so visual listeners (Footprints) stay in sync with the silent cadence
    // when the user mutes audio. Audio playback is gated separately below.
    if (moving && grounded) {
      const interval = running ? FOOTSTEP_INTERVAL_RUN : FOOTSTEP_INTERVAL_WALK;
      if (!this._wasStepping) {
        this._stepTimer = interval;
        this._wasStepping = true;
      } else {
        this._stepTimer += delta;
      }
      if (this._stepTimer >= interval) {
        this._stepTimer = 0;
        this._stepOdd = !this._stepOdd;
        if (this.ctx && !this.muted) this.playStep(this._stepOdd);
        this.onStep?.(this._stepOdd);
      }
    } else {
      this._stepTimer = 0;
      this._wasStepping = false;
    }

    if (!this.ctx || this.muted) return;

    // Detect grounded → airborne transition as a jump.
    if (this._wasGrounded === true && grounded === false) {
      this.playJump();
    }
    this._wasGrounded = grounded;

    // Sporadic bird chirps so the forest never feels empty.
    this._birdTimer -= delta;
    if (this._birdTimer <= 0) {
      this.playBird();
      this._birdTimer = randIn(BIRD_INTERVAL_RANGE);
    }
  }

  // ── Procedural sounds ────────────────────────────────────────────────────

  playStep(alt = false) {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    // Short pink-noise burst through a low-pass filter — sounds like a soft
    // footfall on grass. Alternating between two filter cutoffs simulates L/R.
    const buffer = this.#noiseBuffer(0.08);
    const src = this.ctx.createBufferSource();
    src.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = alt ? 700 : 600;
    filter.Q.value = 0.7;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.0, now);
    gain.gain.linearRampToValueAtTime(0.22, now + 0.005);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(this.master);
    src.start(now);
    src.stop(now + 0.1);
  }

  playJump() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(220, now);
    osc.frequency.exponentialRampToValueAtTime(540, now + 0.18);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.0, now);
    gain.gain.linearRampToValueAtTime(0.40, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

    osc.connect(gain);
    gain.connect(this.master);
    osc.start(now);
    osc.stop(now + 0.25);
  }

  playInteract() {
    if (!this.ctx || this.muted) return;
    this.#ensureContext();
    if (this.ctx.state === 'suspended') this.ctx.resume();
    const now = this.ctx.currentTime;

    // Two-note ascending chime — soft sine, gentle attack.
    [{ freq: 660, t: 0 }, { freq: 880, t: 0.12 }].forEach(({ freq, t }) => {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = freq;
      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.35, now + t + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.35);
      osc.connect(gain);
      gain.connect(this.master);
      osc.start(now + t);
      osc.stop(now + t + 0.4);
    });
  }

  playWelcome() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    // Warm three-note arpeggio (C-E-G major triad), low and quiet.
    const notes = [
      { freq: 523.25, t: 0.00 }, // C5
      { freq: 659.25, t: 0.20 }, // E5
      { freq: 783.99, t: 0.40 }, // G5
    ];
    for (const { freq, t } of notes) {
      const osc = this.ctx.createOscillator();
      osc.type = 'triangle';
      osc.frequency.value = freq;
      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.30, now + t + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.65);
      osc.connect(gain);
      gain.connect(this.master);
      osc.start(now + t);
      osc.stop(now + t + 0.7);
    }
  }

  /** Short cheerful bird chirp — 2-3 quick descending tones, slight stereo-ish detune. */
  playBird() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    const baseFreq = 1800 + Math.random() * 1200;       // 1.8–3.0 kHz
    const noteCount = 2 + Math.floor(Math.random() * 2); // 2 or 3 chirps
    for (let i = 0; i < noteCount; i++) {
      const t = i * 0.09;
      const f0 = baseFreq * (1 - i * 0.06);
      const osc = this.ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(f0 * 1.02, now + t);
      osc.frequency.exponentialRampToValueAtTime(f0 * 0.85, now + t + 0.06);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.06, now + t + 0.008);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.08);

      osc.connect(gain);
      gain.connect(this.master);
      osc.start(now + t);
      osc.stop(now + t + 0.1);
    }
  }

  startAmbient() {
    if (!this.ctx || this.ambientGain) return;

    // Layered low-pass filtered noise = wind / forest hush. Very quiet.
    const buffer = this.#noiseBuffer(2.0);
    const src = this.ctx.createBufferSource();
    src.buffer = buffer;
    src.loop = true;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 380;
    filter.Q.value = 0.5;

    // Slow LFO on filter cutoff for subtle motion.
    const lfo = this.ctx.createOscillator();
    lfo.frequency.value = 0.07;
    const lfoGain = this.ctx.createGain();
    lfoGain.gain.value = 80;
    lfo.connect(lfoGain).connect(filter.frequency);

    const gain = this.ctx.createGain();
    gain.gain.value = 0;

    src.connect(filter);
    filter.connect(gain);
    gain.connect(this.master);

    const now = this.ctx.currentTime;
    gain.gain.linearRampToValueAtTime(0.11, now + 2.0);

    src.start();
    lfo.start();

    this.ambientGain = gain;
  }

  #noiseBuffer(durationSec) {
    const sampleRate = this.ctx.sampleRate;
    const length = Math.round(sampleRate * durationSec);
    const buffer = this.ctx.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);
    // Very basic pink-ish noise (Voss-McCartney approximation).
    let b0 = 0, b1 = 0, b2 = 0;
    for (let i = 0; i < length; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99765 * b0 + white * 0.0990460;
      b1 = 0.96300 * b1 + white * 0.2965164;
      b2 = 0.57000 * b2 + white * 1.0526913;
      data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.15;
    }
    return buffer;
  }

  // ── DOM toggle button ────────────────────────────────────────────────────
  #installButton() {
    const btn = document.createElement('button');
    btn.className = 'audio-toggle';
    btn.setAttribute('aria-label', 'Toggle audio');
    btn.innerHTML = this.muted ? SPEAKER_OFF : SPEAKER_ON;
    btn.addEventListener('click', () => {
      this.#ensureContext();
      if (this.ctx?.state === 'suspended') this.ctx.resume();
      this.setMuted(!this.muted);
    });
    document.body.appendChild(btn);
    this._btn = btn;
  }
  #updateButton() {
    if (this._btn) this._btn.innerHTML = this.muted ? SPEAKER_OFF : SPEAKER_ON;
  }
}

const SPEAKER_ON = `
<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
  <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
  <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
</svg>`;
const SPEAKER_OFF = `
<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
  <line x1="23" y1="9" x2="17" y2="15"/>
  <line x1="17" y1="9" x2="23" y2="15"/>
</svg>`;
