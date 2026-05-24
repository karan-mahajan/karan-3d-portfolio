/**
 * Layered audio:
 *
 *   Sample-based (Howler):
 *     ambient-day / ambient-night    – crossfaded by setMode()
 *     birds-day                      – plays under day ambient only
 *     wind-trees                     – constant low layer
 *     water-waves                    – pond proximity (setPondProximity)
 *     ocean-loop                     – shore + wading proximity (setOceanProximity)
 *     splash-light / splash-entry    – wading + jump-in one-shots
 *     thunder                        – random one-shot while rain is on
 *     jump / bump / land-water       – character SFX
 *
 *   Procedural (Web Audio via Howler.ctx so they inherit mute/focus):
 *     playStep                       – footsteps (pink-noise burst; placeholder
 *                                       until real footstep packs are added)
 *     playInteract / playWelcome     – UI chimes (placeholder until real UI
 *                                       sounds are added)
 *
 * Focus loss: visibilitychange + window.blur/focus suspend Howler's
 * AudioContext (kills CPU) and ramp master volume to 0. The user's mute
 * toggle (localStorage) is preserved across focus changes.
 *
 * Missing files are tolerated — each Howl logs a warning on load error and
 * `play*` methods no-op when their buffer isn't ready.
 */

import { Howl, Howler } from "howler";

function randIn([min, max]) {
  return min + Math.random() * (max - min);
}

const STORAGE_KEY = "karan-portfolio:muted";
const MASTER_LEVEL = 0.72;
const FOOTSTEP_INTERVAL_WALK = 0.42;
const FOOTSTEP_INTERVAL_RUN = 0.28;

// Layered ambient volumes — kept low because they all stack. Background
// beds (day/night/birds/wind) were trimmed twice on user feedback
// (2026-05-24): first −10%, then another −12% after the stack still
// read as too present.
const VOL = {
  ambientDay: 0.333,
  ambientNight: 0.436,
  birdsDay: 0.253,
  windTrees: 0.222,
  waterWavesMax: 0.45,
  waterWavesFalloffM: 18,
  oceanAtShore: 0.32,
  oceanInWater: 0.5,
  oceanFalloffM: 30,
  splashLight: 0.32,
  splashEntry: 0.55,
  thunder: 0.65,
  jump: 0.55,
  bump: 0.5,
  landWater: 0.55,
  landGrass: 0.45,
  landStone: 0.55,
  push: 0.55,
  objectSlide: 0.4,
  // Continuous scrape loop volume during a sustained push hold.
  pushHold: 0.35,
  kick: 0.9,
  punchBag: 0.75,
  flip: 0.55,
  rainAmbient: 0.45,
  // Rain-on-water layer is gated by player water-proximity (see
  // setOceanProximity) and only audible while rain is on.
  rainWaterMax: 0.55,
  // Per-step footstep volume (multiplied by per-surface trim below).
  footstep: 0.45,
  footstepSurfaceTrim: { grass: 1.0, stone: 0.85, sand: 0.95 },
  // UI clicks — kept gentle so they don't punch through the ambient bed.
  click: 0.45,
  toggle: 0.45,
  menuOpen: 0.55,
  menuClose: 0.55,
};

const AMBIENT_CROSSFADE_S = 3.0;
const PROX_RAMP_S = 0.4;
const THUNDER_INTERVAL = [30, 60]; // sec between strikes while rain is on

// Files that exist in static/sounds. Anything still missing (rain ambient,
// rain-on-water, flip whoosh, zoom-in / zoom-out whooshes) is intentionally
// absent — when the user drops them in, add the entry here and wire a play
// method.
const SOUND_FILES = {
  // Ambient beds + spatial loops
  ambientDay: { src: "/sounds/ambient-day.mp3", loop: true, vol: 0 },
  ambientNight: { src: "/sounds/ambient-night.mp3", loop: true, vol: 0 },
  birdsDay: { src: "/sounds/birds-day.mp3", loop: true, vol: 0 },
  windTrees: { src: "/sounds/wind-trees.mp3", loop: true, vol: VOL.windTrees },
  waterWaves: { src: "/sounds/water-waves.mp3", loop: true, vol: 0 },
  oceanLoop: { src: "/sounds/ocean-loop.mp3", loop: true, vol: 0 },
  // Water one-shots (wading + entry)
  splashLight: {
    src: "/sounds/splash-light.mp3",
    loop: false,
    vol: VOL.splashLight,
  },
  splashEntry: {
    src: "/sounds/splash-entry.mp3",
    loop: false,
    vol: VOL.splashEntry,
  },
  // Weather
  thunder: { src: "/sounds/thunder.mp3", loop: false, vol: VOL.thunder },
  rainAmbient: { src: "/sounds/rain-ambient.mp3", loop: true, vol: 0 },
  rainWater: { src: "/sounds/rain-water.mp3", loop: true, vol: 0 },
  flip: { src: "/sounds/flip.mp3", loop: false, vol: VOL.flip },
  // Character SFX
  jump: { src: "/sounds/jump.mp3", loop: false, vol: VOL.jump },
  bump: { src: "/sounds/bump.mp3", loop: false, vol: VOL.bump },
  landWater: { src: "/sounds/land-water.mp3", loop: false, vol: VOL.landWater },
  landGrass: { src: "/sounds/land-grass.mp3", loop: false, vol: VOL.landGrass },
  landStone: { src: "/sounds/land-stone.mp3", loop: false, vol: VOL.landStone },
  // Footstep variants — picked at random per step. Pool size per surface
  // determined by what's in the Kenney pack: grass 4, stone 4, sand 3.
  stepGrass1: {
    src: "/sounds/step-grass-1.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepGrass2: {
    src: "/sounds/step-grass-2.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepGrass3: {
    src: "/sounds/step-grass-3.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepGrass4: {
    src: "/sounds/step-grass-4.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepStone1: {
    src: "/sounds/step-stone-1.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepStone2: {
    src: "/sounds/step-stone-2.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepStone3: {
    src: "/sounds/step-stone-3.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepStone4: {
    src: "/sounds/step-stone-4.mp3",
    loop: false,
    vol: VOL.footstep,
  },
  stepSand1: { src: "/sounds/step-sand-1.mp3", loop: false, vol: VOL.footstep },
  stepSand2: { src: "/sounds/step-sand-2.mp3", loop: false, vol: VOL.footstep },
  stepSand3: { src: "/sounds/step-sand-3.mp3", loop: false, vol: VOL.footstep },
  // Interaction / UI
  push: { src: "/sounds/push.mp3", loop: false, vol: VOL.push },
  objectSlide: {
    src: "/sounds/object-slide.mp3",
    loop: false,
    vol: VOL.objectSlide,
  },
  kickFootball: {
    src: "/sounds/kick-football.mp3",
    loop: false,
    vol: VOL.kick,
  },
  punchBag: {
    src: "/sounds/punch-bag.mp3",
    loop: false,
    vol: VOL.punchBag,
  },
  // object-slide doubles as the continuous push-hold loop (see startPush).
  pushHoldLoop: {
    src: "/sounds/object-slide.mp3",
    loop: true,
    vol: 0,
  },
  click: { src: "/sounds/interact-click.mp3", loop: false, vol: VOL.click },
  toggleClick: { src: "/sounds/toggle.mp3", loop: false, vol: VOL.toggle },
  menuOpen: { src: "/sounds/menu-open.mp3", loop: false, vol: VOL.menuOpen },
  menuClose: { src: "/sounds/menu-close.mp3", loop: false, vol: VOL.menuClose },
};

// Footstep pool keys per surface — random pick per step.
const STEP_POOLS = {
  grass: ["stepGrass1", "stepGrass2", "stepGrass3", "stepGrass4"],
  stone: ["stepStone1", "stepStone2", "stepStone3", "stepStone4"],
  sand: ["stepSand1", "stepSand2", "stepSand3"],
  // 'water' surface re-uses the existing splash-light wading sound (handled
  // in playFootstep) so a single pool is enough.
};

export class AudioManager {
  constructor() {
    this.muted = localStorage.getItem(STORAGE_KEY) === "1";
    this._started = false;
    this._focusLost = false;
    this.howls = {};
    this.mode = "day";

    this._stepTimer = 0;
    this._stepOdd = false;
    this._wasStepping = false;
    this._wasGrounded = true;
    this._thunderTimer = randIn(THUNDER_INTERVAL);
    this._wasRainOn = false;
    this._rainOn = false;

    /** Visual footprint cadence hook — see header comment in old version. */
    this.onStep = null;

    Howler.volume(this.muted ? 0 : MASTER_LEVEL);
    this.#installButton();
    this.#installFocusGuard();
  }

  /** First user gesture: kick off Howler context, preload, start ambient. */
  start() {
    if (this._started) return;
    this._started = true;
    this.#preload();
    this.#startAmbientBeds();
    this.playWelcome();
  }

  #preload() {
    for (const [key, cfg] of Object.entries(SOUND_FILES)) {
      this.howls[key] = new Howl({
        src: [cfg.src],
        loop: cfg.loop,
        volume: cfg.vol,
        // html5: false (default) so they decode via Web Audio and inherit
        // Howler.ctx suspend on focus loss.
        onloaderror: (_id, err) => {
          console.warn(`[Audio] failed to load ${cfg.src}`, err);
        },
      });
    }
  }

  /** Bring up the ambient bed appropriate to the current mode + the constant
   *  wind layer. Re-callable; idempotent per-howl via internal `playing()`. */
  #startAmbientBeds() {
    const wind = this.howls.windTrees;
    if (wind && !wind.playing()) {
      wind.play();
      wind.fade(0, VOL.windTrees, 1500);
    }
    // Ocean + water-waves play at vol=0 from the start; setOcean/Pond ride
    // their gain so they're always "running" and ready to be audible.
    for (const k of ["oceanLoop", "waterWaves"]) {
      const h = this.howls[k];
      if (h && !h.playing()) h.play();
    }
    this.#applyMode(this.mode, /*duration=*/ 0);
  }

  /** Public: switch ambient bed to day or night. Crossfades over `duration`. */
  setMode(mode, duration = AMBIENT_CROSSFADE_S) {
    if (mode !== "day" && mode !== "night") return;
    if (mode === this.mode && this._started) return;
    this.mode = mode;
    if (this._started) this.#applyMode(mode, duration);
  }

  #applyMode(mode, duration) {
    const ms = Math.max(0, duration * 1000);
    const day = this.howls.ambientDay;
    const night = this.howls.ambientNight;
    const birds = this.howls.birdsDay;
    const targetDay = mode === "day" ? VOL.ambientDay : 0;
    const targetNight = mode === "night" ? VOL.ambientNight : 0;
    const targetBirds = mode === "day" ? VOL.birdsDay : 0;
    this.#fadeTo(day, targetDay, ms, /*startIfSilent=*/ mode === "day");
    this.#fadeTo(night, targetNight, ms, /*startIfSilent=*/ mode === "night");
    this.#fadeTo(birds, targetBirds, ms, /*startIfSilent=*/ mode === "day");
  }

  #fadeTo(howl, target, ms, startIfSilent = true) {
    if (!howl) return;
    const cur = howl.volume();
    if (!howl.playing()) {
      if (target <= 0 || !startIfSilent) return;
      howl.volume(0);
      howl.play();
    }
    if (ms <= 0) {
      howl.volume(target);
    } else {
      howl.fade(cur, target, ms);
    }
  }

  // ── Per-frame ────────────────────────────────────────────────────────────
  tick(
    delta,
    { moving, running, grounded, surface = "grass", rainOn = false } = {},
  ) {
    // Step cadence (drives visual footprints even when muted).
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
        if (!this.muted && !this._focusLost)
          this.playFootstep(surface, this._stepOdd);
        this.onStep?.(this._stepOdd);
      }
    } else {
      this._stepTimer = 0;
      this._wasStepping = false;
    }

    if (!this._started || this.muted || this._focusLost) return;

    // Landing audio is dispatched from App.js so the surface (water vs.
    // ground) is known. Here we only track the jump leg.
    if (this._wasGrounded === true && grounded === false) this.playJump();
    this._wasGrounded = grounded;

    // Rain layer + thunder. _rainOn is cached so setOceanProximity can gate
    // the rain-on-water layer without needing rainOn passed separately.
    this._rainOn = rainOn;
    if (rainOn && !this._wasRainOn) this.#startRain();
    else if (!rainOn && this._wasRainOn) this.#stopRain();
    this._wasRainOn = rainOn;

    if (rainOn) {
      this._thunderTimer -= delta;
      if (this._thunderTimer <= 0) {
        this.playThunder();
        this._thunderTimer = randIn(THUNDER_INTERVAL);
      }
    } else {
      this._thunderTimer = randIn(THUNDER_INTERVAL);
    }
  }

  #startRain() {
    const amb = this.howls.rainAmbient;
    const water = this.howls.rainWater;
    if (amb && amb.state() === "loaded") {
      if (!amb.playing()) { amb.volume(0); amb.play(); }
      amb.fade(amb.volume(), VOL.rainAmbient, 1000);
    }
    if (water && water.state() === "loaded") {
      if (!water.playing()) { water.volume(0); water.play(); }
      // Volume is then driven by setOceanProximity each frame.
    }
  }

  #stopRain() {
    const amb = this.howls.rainAmbient;
    const water = this.howls.rainWater;
    if (amb && amb.playing()) {
      amb.fade(amb.volume(), 0, 2000);
      setTimeout(() => { if (amb.volume() < 0.005 && amb.playing()) amb.pause(); }, 2200);
    }
    if (water && water.playing()) {
      water.fade(water.volume(), 0, 2000);
      setTimeout(() => { if (water.volume() < 0.005 && water.playing()) water.pause(); }, 2200);
    }
  }

  // ── Spatial proximity gains ──────────────────────────────────────────────
  /** Ocean-loop sits in the background; water-waves layers on top for the
   *  in-water "crashing" texture. Both rise with proximity to the shore.
   *  When rain is on, rain-on-water rides the same proximity curve. */
  setOceanProximity(distFromCenter, shoreRadius = 45) {
    const ocean = this.howls.oceanLoop;
    const waves = this.howls.waterWaves;
    const rainWater = this.howls.rainWater;
    let oceanTarget;
    let wavesTarget;
    let prox;
    if (distFromCenter > shoreRadius) {
      oceanTarget = VOL.oceanInWater;
      wavesTarget = VOL.waterWavesMax;
      prox = 1;
    } else {
      const distToShore = shoreRadius - distFromCenter;
      prox = Math.max(0, 1 - distToShore / VOL.oceanFalloffM);
      oceanTarget = prox * VOL.oceanAtShore;
      wavesTarget = prox * VOL.waterWavesMax * 0.5; // softer at the shore
    }
    this.#rampHowlVolume(ocean, oceanTarget, PROX_RAMP_S);
    this.#rampHowlVolume(waves, wavesTarget, PROX_RAMP_S);
    // Rain on water rides the same proximity but is silenced when rain is off.
    if (rainWater && rainWater.playing()) {
      const target = this._rainOn ? prox * VOL.rainWaterMax : 0;
      this.#rampHowlVolume(rainWater, target, PROX_RAMP_S);
    }
  }

  #rampHowlVolume(howl, target, durationSec) {
    if (!howl) return;
    const cur = howl.volume();
    if (Math.abs(cur - target) < 0.005) return;
    howl.fade(cur, target, Math.max(50, durationSec * 1000));
  }

  // ── Sample one-shots ─────────────────────────────────────────────────────
  playSplash({ entry = false, volume = 1.0 } = {}) {
    if (this.muted || this._focusLost) return;
    const h = entry ? this.howls.splashEntry : this.howls.splashLight;
    if (!h || h.state() !== "loaded") return;
    const id = h.play();
    h.rate(0.92 + Math.random() * 0.16, id);
    h.volume(volume * (entry ? VOL.splashEntry : VOL.splashLight), id);
  }

  playJump() {
    const h = this.howls.jump;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.96 + Math.random() * 0.08, id);
      return;
    }
    this.#proceduralJump();
  }

  /** Landing on any surface. Maps surface → land sample. */
  playLand(surface = "grass") {
    const key =
      surface === "water"
        ? "landWater"
        : surface === "stone"
          ? "landStone"
          : "landGrass";
    const h = this.howls[key];
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.94 + Math.random() * 0.12, id);
    }
  }

  /** Picks a random sample from the surface's footstep pool. Water steps
   *  re-use the existing wading splash so we don't double-up. */
  playFootstep(surface = "grass", alt = false) {
    if (this.muted || this._focusLost) return;
    if (surface === "water") {
      // The wading splash audio is already triggered by Water.js per its own
      // cadence; emitting a step here would double-up. Skip.
      return;
    }
    const pool = STEP_POOLS[surface] || STEP_POOLS.grass;
    const key = pool[Math.floor(Math.random() * pool.length)];
    const h = this.howls[key];
    if (!h || h.state() !== "loaded") {
      // Fall back to the procedural pink-noise step if the sample is still
      // loading or missing.
      this.playStep(alt);
      return;
    }
    const id = h.play();
    h.rate(0.92 + Math.random() * 0.16, id);
    const trim = VOL.footstepSurfaceTrim[surface] ?? 1.0;
    h.volume(VOL.footstep * trim, id);
  }

  /** Bump into something at speed. Wire from collision sites with a velocity
   *  gate. Currently unused by App; ready for future wiring. */
  playBump() {
    const h = this.howls.bump;
    if (h && h.state() === "loaded") h.play();
  }

  playThunder() {
    const h = this.howls.thunder;
    if (h && h.state() === "loaded") h.play();
  }

  /** Generic UI click — press E, confirm an action. */
  playClick() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.click;
    if (h && h.state() === "loaded") h.play();
  }

  /** Toggle click — day/night, rain on/off, sound mute. */
  playToggle() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.toggleClick;
    if (h && h.state() === "loaded") h.play();
  }

  /** Billboard zoom-in / info panel open. */
  playMenuOpen() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.menuOpen;
    if (h && h.state() === "loaded") h.play();
  }

  /** Billboard zoom-out / info panel close. */
  playMenuClose() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.menuClose;
    if (h && h.state() === "loaded") h.play();
  }

  /** Kick the football — meaty soft impact, plays on the foot-meets-ball
   *  beat (Interactables.js fires this with the same delay it uses to start
   *  the ball's physics impulse). */
  playKick() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.kickFootball;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.94 + Math.random() * 0.12, id);
    }
  }

  /** Start a sustained push: initial impact thud + a low scrape loop that
   *  keeps playing for as long as the player holds P. Pair with endPush()
   *  on key-up (and on blur/focus-loss in ActionPrompts). */
  startPush() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.push;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.94 + Math.random() * 0.12, id);
    }
    const loop = this.howls.pushHoldLoop;
    if (loop && loop.state() === "loaded") {
      if (!loop.playing()) loop.play();
      // Fade in so the scrape doesn't pop on top of the impact thud.
      loop.fade(loop.volume(), VOL.pushHold, 180);
    }
  }

  /** End a sustained push — fades the scrape loop out over ~200ms. */
  endPush() {
    const loop = this.howls.pushHoldLoop;
    if (!loop) return;
    if (!loop.playing()) return;
    const cur = loop.volume();
    loop.fade(cur, 0, 220);
    // Pause after the fade so we don't keep the buffer hot indefinitely.
    setTimeout(() => {
      if (loop.volume() < 0.005 && loop.playing()) loop.pause();
    }, 280);
  }

  /** Flip whoosh — fires on backflip or cartwheel. */
  playFlip() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.flip;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.94 + Math.random() * 0.12, id);
    }
  }

  /** Punch the bag — heavier impact than push (impactPunch_heavy). */
  playPunch() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.punchBag;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.92 + Math.random() * 0.16, id);
    }
  }

  // ── Procedural fallbacks (use Howler.ctx so mute/focus inherit) ──────────
  #ctx() {
    return Howler.ctx ?? null;
  }
  #dest() {
    return Howler.masterGain ?? Howler.ctx?.destination ?? null;
  }

  playStep(alt = false) {
    const ctx = this.#ctx();
    const dest = this.#dest();
    if (!ctx || !dest || this.muted || this._focusLost) return;
    const now = ctx.currentTime;
    const buffer = this.#noiseBuffer(ctx, 0.08);
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = alt ? 700 : 600;
    filter.Q.value = 0.7;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.22, now + 0.005);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    src.connect(filter);
    filter.connect(gain);
    gain.connect(dest);
    src.start(now);
    src.stop(now + 0.1);
  }

  #proceduralJump() {
    const ctx = this.#ctx();
    const dest = this.#dest();
    if (!ctx || !dest || this.muted || this._focusLost) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.setValueAtTime(220, now);
    osc.frequency.exponentialRampToValueAtTime(540, now + 0.18);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.4, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
    osc.connect(gain);
    gain.connect(dest);
    osc.start(now);
    osc.stop(now + 0.25);
  }

  /** Back-compat alias — old call sites (Interaction.js, ActionPrompts.js)
   *  use playInteract() generically for "press E to engage" feedback. The
   *  real click sample sounds better than the procedural two-note chime
   *  that used to live here. */
  playInteract() {
    this.playClick();
  }

  playWelcome() {
    const ctx = this.#ctx();
    const dest = this.#dest();
    if (!ctx || !dest || this.muted || this._focusLost) return;
    const now = ctx.currentTime;
    [
      { f: 523.25, t: 0 },
      { f: 659.25, t: 0.2 },
      { f: 783.99, t: 0.4 },
    ].forEach(({ f, t }) => {
      const osc = ctx.createOscillator();
      osc.type = "triangle";
      osc.frequency.value = f;
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.26, now + t + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.65);
      osc.connect(gain);
      gain.connect(dest);
      osc.start(now + t);
      osc.stop(now + t + 0.7);
    });
  }

  /** Kept as a public no-op for backwards compat — procedural chirps were
   *  removed once we got a real birds-day ambient bed. */
  playBird() {}

  /** Kept as a public no-op for backwards compat — replaced by ambient beds. */
  startAmbient() {}

  #noiseBuffer(ctx, durationSec) {
    const sr = ctx.sampleRate;
    const length = Math.round(sr * durationSec);
    const buffer = ctx.createBuffer(1, length, sr);
    const data = buffer.getChannelData(0);
    let b0 = 0,
      b1 = 0,
      b2 = 0;
    for (let i = 0; i < length; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99765 * b0 + white * 0.099046;
      b1 = 0.963 * b1 + white * 0.2965164;
      b2 = 0.57 * b2 + white * 1.0526913;
      data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.15;
    }
    return buffer;
  }

  // ── Mute toggle (user-controlled) ────────────────────────────────────────
  setMuted(value) {
    this.muted = value;
    localStorage.setItem(STORAGE_KEY, value ? "1" : "0");
    if (!this._focusLost) Howler.volume(value ? 0 : MASTER_LEVEL);
    this.#updateButton();
  }

  // ── Focus loss: pause everything while tab/window is hidden ──────────────
  #installFocusGuard() {
    const onLost = () => {
      if (this._focusLost) return;
      this._focusLost = true;
      // Ramp to 0 first (avoid a click), then suspend the context for CPU.
      try {
        Howler.volume(0);
      } catch {}
      try {
        Howler.ctx?.suspend?.();
      } catch {}
    };
    const onGained = () => {
      if (!this._focusLost) return;
      this._focusLost = false;
      try {
        Howler.ctx?.resume?.();
      } catch {}
      // Honour the user's mute toggle when restoring.
      Howler.volume(this.muted ? 0 : MASTER_LEVEL);
    };
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) onLost();
      else onGained();
    });
    // window.blur/focus catches macOS app-switch cases that visibilitychange
    // sometimes misses (Cmd+Tab away while the tab stays "visible").
    window.addEventListener("blur", onLost);
    window.addEventListener("focus", onGained);
    // pageshow/pagehide cover bfcache restore on Safari.
    window.addEventListener("pagehide", onLost);
    window.addEventListener("pageshow", onGained);
  }

  // ── DOM toggle button ────────────────────────────────────────────────────
  #installButton() {
    const btn = document.createElement("button");
    btn.className = "audio-toggle";
    btn.setAttribute("aria-label", "Toggle audio");
    btn.innerHTML = this.muted ? SPEAKER_OFF : SPEAKER_ON;
    btn.addEventListener("click", () => {
      // First click kickstarts everything if the user hasn't gestured yet.
      if (!this._started) this.start();
      this.setMuted(!this.muted);
    });
    document.body.appendChild(btn);
    this._btn = btn;
  }
  #updateButton() {
    if (this._btn) this._btn.innerHTML = this.muted ? SPEAKER_OFF : SPEAKER_ON;
  }

  // Legacy compat — old code referenced `audio.ctx`; expose Howler's so
  // anything reaching in still works.
  get ctx() {
    return Howler.ctx;
  }
  get master() {
    return Howler.masterGain;
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
