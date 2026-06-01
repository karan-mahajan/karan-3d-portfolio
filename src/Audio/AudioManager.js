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
// beds (day/night/birds/wind/water/rain) trimmed four times on user
// feedback (2026-05-24): −10%, then −12%, then −18%, then a −50% pass
// on the pure background beds only (day/night/birds/wind/rain),
// followed by a +10% nudge back up after the −50% sat a touch too quiet.
// Proximity-gated water + foreground SFX (thunder, steps, jumps,
// push/kick/punch, UI) were left untouched throughout.
const VOL = {
  ambientDay: 0.151,
  ambientNight: 0.197,
  birdsDay: 0.114,
  windTrees: 0.1,
  waterWavesMax: 0.369,
  waterWavesFalloffM: 18,
  oceanAtShore: 0.262,
  oceanInWater: 0.41,
  oceanFalloffM: 30,
  splashLight: 0.32,
  splashEntry: 0.55,
  // Peak thunder volume before Howler master (0.72). Held back from 0.85
  // to 1.0 after the third volume report (user still couldn't hear it
  // over the ambient stack). With the −18% ambient pass above, this
  // sits well above any background bed.
  thunder: 1.0,
  jump: 0.45,
  bump: 0.5,
  landingImpact: 1.0,
  landWater: 0.55,
  landGrass: 0.45,
  landStone: 0.55,
  push: 0.55,
  objectSlide: 0.4,
  // Continuous scrape loop volume during a sustained push hold.
  pushHold: 0.35,
  brickHit: 0.6,
  kick: 0.9,
  punchBag: 0.75,
  flip: 0.55,
  rainAmbient: 0.248,
  // Rain-on-water layer is gated by player water-proximity (see
  // setOceanProximity) and only audible while rain is on.
  rainWaterMax: 0.303,
  // Per-step footstep volume (multiplied by per-surface trim below).
  footstep: 0.45,
  // Water clips are a touch quieter at source (soft recording) so they get a
  // small lift; wood planks are crisp so they sit at unity.
  footstepSurfaceTrim: { grass: 1.0, stone: 0.85, sand: 0.95, water: 1.15, wood: 1.0, snow: 1.05, snowRun: 1.05 },
  // Big splash when jumping / landing in water (replaces splashEntry as the
  // water-entry one-shot).
  waterJump: 0.6,
  // UI clicks — kept gentle so they don't punch through the ambient bed.
  click: 0.45,
  toggle: 0.45,
  menuOpen: 0.15,
  menuClose: 0.15,
  mapOpen: 0.2,
  mapClose: 0.18,
  markerHover: 0.16,
  markerClick: 0.32,
  teleportWoosh: 0.45,
  teleportArrive: 0.34,
  nope: 0.28,
  flagDrop: 0.25,
};

const AMBIENT_CROSSFADE_S = 3.0;
const PROX_RAMP_S = 0.4;
// Thunder timing now lives in src/Effects/Thunderstorm.js — it drives both
// the visual strike and this manager's playThunder(delay, intensity) so
// flash + audio stay in sync. The old per-frame timer here was removed.

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
  // Weather — thunder uses the real recorded sample (set per-call by
  // Thunderstorm with delay + intensity). The procedural noise fallback
  // inside playThunder only fires if the sample failed to load.
  thunder: { src: "/sounds/thunder.mp3", loop: false, vol: 0 },
  rainAmbient: { src: "/sounds/rain-ambient.mp3", loop: true, vol: 0 },
  rainWater: { src: "/sounds/rain-water.mp3", loop: true, vol: 0 },
  flip: { src: "/sounds/flip.mp3", loop: false, vol: VOL.flip },
  // Character SFX
  jump: { src: "/sounds/jump.mp3", loop: false, vol: VOL.jump },
  bump: { src: "/sounds/bump.mp3", loop: false, vol: VOL.bump },
  landWater: { src: "/sounds/land-water.mp3", loop: false, vol: VOL.landWater },
  landGrass: { src: "/sounds/land-grass.mp3", loop: false, vol: VOL.landGrass },
  landStone: { src: "/sounds/land-stone.mp3", loop: false, vol: VOL.landStone },
  // Intro cinematic — the superhero ground-impact hit (CC0). Loud: it's the
  // dramatic beat the whole arrival builds to.
  landingImpact: { src: "/sounds/landing-impact.mp3", loop: false, vol: VOL.landingImpact },
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
  // Wading footsteps — walking IN water (replaces the old auto wading-splash
  // cadence in Water.js). User-recorded, sliced + peak-normalized.
  stepWater1: { src: "/sounds/step-water-1.mp3", loop: false, vol: VOL.footstep },
  stepWater2: { src: "/sounds/step-water-2.mp3", loop: false, vol: VOL.footstep },
  stepWater3: { src: "/sounds/step-water-3.mp3", loop: false, vol: VOL.footstep },
  stepWater4: { src: "/sounds/step-water-4.mp3", loop: false, vol: VOL.footstep },
  // Bridge-deck footsteps — fire when the player is on bridge01/bridge02.
  stepWood1: { src: "/sounds/step-wood-1.mp3", loop: false, vol: VOL.footstep },
  stepWood2: { src: "/sounds/step-wood-2.mp3", loop: false, vol: VOL.footstep },
  stepWood3: { src: "/sounds/step-wood-3.mp3", loop: false, vol: VOL.footstep },
  stepWood4: { src: "/sounds/step-wood-4.mp3", loop: false, vol: VOL.footstep },
  // Snow footsteps — discrete crunches cut from the snow-walk / snow-run clips.
  stepSnow1: { src: "/sounds/step-snow-1.mp3", loop: false, vol: VOL.footstep },
  stepSnow2: { src: "/sounds/step-snow-2.mp3", loop: false, vol: VOL.footstep },
  stepSnow3: { src: "/sounds/step-snow-3.mp3", loop: false, vol: VOL.footstep },
  stepSnow4: { src: "/sounds/step-snow-4.mp3", loop: false, vol: VOL.footstep },
  stepSnowRun1: { src: "/sounds/step-snowrun-1.mp3", loop: false, vol: VOL.footstep },
  stepSnowRun2: { src: "/sounds/step-snowrun-2.mp3", loop: false, vol: VOL.footstep },
  stepSnowRun3: { src: "/sounds/step-snowrun-3.mp3", loop: false, vol: VOL.footstep },
  stepSnowRun4: { src: "/sounds/step-snowrun-4.mp3", loop: false, vol: VOL.footstep },
  // Splash one-shot when the player jumps / lands in the water.
  splashJump: { src: "/sounds/splash-jump.mp3", loop: false, vol: VOL.waterJump },
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
  brickHit1: {
    src: "/sounds/hits/bricks/24445%20brick%20light%20hitting-full-2.mp3",
    loop: false,
    vol: VOL.brickHit,
  },
  brickHit2: {
    src: "/sounds/hits/bricks/41559%20Stone%20brick%20fall%20hit%2001-full-1.mp3",
    loop: false,
    vol: VOL.brickHit,
  },
  brickHit3: {
    src: "/sounds/hits/bricks/41563%20Stone%20brick%20fall%20hit%2005-full-1.mp3",
    loop: false,
    vol: VOL.brickHit,
  },
  brickHit4: {
    src: "/sounds/hits/bricks/BrickSetDown_BW.5803-1.mp3",
    loop: false,
    vol: VOL.brickHit,
  },
  click: { src: "/sounds/interact-click.mp3", loop: false, vol: VOL.click },
  toggleClick: { src: "/sounds/toggle.mp3", loop: false, vol: VOL.toggle },
  menuOpen: { src: "/sounds/menu-open.mp3", loop: false, vol: VOL.menuOpen },
  menuClose: { src: "/sounds/menu-close.mp3", loop: false, vol: VOL.menuClose },
  // Map SFX placeholders are 100ms silence until sourced:
  // map_open ~300ms paper rustle.
  mapOpen: { src: "/sounds/map-open.mp3", loop: false, vol: VOL.mapOpen },
  // map_close ~250ms paper fold/close.
  mapClose: { src: "/sounds/map-close.mp3", loop: false, vol: VOL.mapClose },
  // marker_hover ~80-120ms gentle tick; pitch varies per section.
  markerHover: { src: "/sounds/marker-hover.mp3", loop: false, vol: VOL.markerHover },
  // marker_click ~150ms solid parchment/wood thunk.
  markerClick: { src: "/sounds/marker-click.mp3", loop: false, vol: VOL.markerClick },
  // teleport_woosh ~400ms reversed reverb sweep.
  teleportWoosh: { src: "/sounds/teleport-woosh.mp3", loop: false, vol: VOL.teleportWoosh },
  // teleport_arrive ~600ms soft chime plus breath of air.
  teleportArrive: { src: "/sounds/teleport-arrive.mp3", loop: false, vol: VOL.teleportArrive },
  // nope ~200ms short low buzz for invalid map clicks.
  nope: { src: "/sounds/nope.mp3", loop: false, vol: VOL.nope },
  // flag_drop ~150ms small wooden tap.
  flagDrop: { src: "/sounds/flag-drop.mp3", loop: false, vol: VOL.flagDrop },
};

// Footstep pool keys per surface — random pick per step.
const STEP_POOLS = {
  grass: ["stepGrass1", "stepGrass2", "stepGrass3", "stepGrass4"],
  stone: ["stepStone1", "stepStone2", "stepStone3", "stepStone4"],
  sand: ["stepSand1", "stepSand2", "stepSand3"],
  water: ["stepWater1", "stepWater2", "stepWater3", "stepWater4"],
  wood: ["stepWood1", "stepWood2", "stepWood3", "stepWood4"],
  // Snow crunch — only used while a storm has covered the ground (App swaps the
  // surface to snow/snowRun). Separate walk vs run packs from the source clips.
  snow: ["stepSnow1", "stepSnow2", "stepSnow3", "stepSnow4"],
  snowRun: ["stepSnowRun1", "stepSnowRun2", "stepSnowRun3", "stepSnowRun4"],
};

const BRICK_HIT_KEYS = ["brickHit1", "brickHit2", "brickHit3", "brickHit4"];

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
    this._wasRainOn = false;
    this._rainOn = false;
    this._ambientDuck = 1;
    this._lastBrickHitKey = -1;
    this._lastBrickHitAt = -Infinity;

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
      wind.fade(0, VOL.windTrees * this._ambientDuck, 1500);
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
    const targetDay = mode === "day" ? VOL.ambientDay * this._ambientDuck : 0;
    const targetNight = mode === "night" ? VOL.ambientNight * this._ambientDuck : 0;
    const targetBirds = mode === "day" ? VOL.birdsDay * this._ambientDuck : 0;
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
    // ground) is known. Here we only track the jump leg. Jumping from water
    // skips the dry jump grunt — the water-entry splash (playWaterJump) takes
    // preference for anything in/over the water.
    if (this._wasGrounded === true && grounded === false && surface !== "water")
      this.playJump();
    this._wasGrounded = grounded;

    // Rain layer + thunder. _rainOn is cached so setOceanProximity can gate
    // the rain-on-water layer without needing rainOn passed separately.
    this._rainOn = rainOn;
    if (rainOn && !this._wasRainOn) this.#startRain();
    else if (!rainOn && this._wasRainOn) this.#stopRain();
    this._wasRainOn = rainOn;
  }

  #startRain() {
    const amb = this.howls.rainAmbient;
    const water = this.howls.rainWater;
    if (amb && amb.state() === "loaded") {
      if (!amb.playing()) {
        amb.volume(0);
        amb.play();
      }
      amb.fade(amb.volume(), VOL.rainAmbient, 1000);
    }
    if (water && water.state() === "loaded") {
      if (!water.playing()) {
        water.volume(0);
        water.play();
      }
      // Volume is then driven by setOceanProximity each frame.
    }
  }

  #stopRain() {
    const amb = this.howls.rainAmbient;
    const water = this.howls.rainWater;
    if (amb && amb.playing()) {
      amb.fade(amb.volume(), 0, 2000);
      setTimeout(() => {
        if (amb.volume() < 0.005 && amb.playing()) amb.pause();
      }, 2200);
    }
    if (water && water.playing()) {
      water.fade(water.volume(), 0, 2000);
      setTimeout(() => {
        if (water.volume() < 0.005 && water.playing()) water.pause();
      }, 2200);
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

  /** Landing on any surface. Maps surface → land sample. Water is handled by
   *  playWaterJump (fired on water-entry from Water.js), so a water landing
   *  here is skipped to avoid double-splashing. */
  playLand(surface = "grass") {
    if (surface === "water") return;
    const key =
      surface === "stone" || surface === "wood" ? "landStone" : "landGrass";
    const h = this.howls[key];
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.94 + Math.random() * 0.12, id);
    }
  }

  /** Big splash one-shot for jumping / dropping into the water. Fired from
   *  Water.js the moment the player's feet cross below the water line (covers
   *  jumping in from land and re-entering after a jump while wading). Falls
   *  back to the lighter entry splash if the dedicated sample is missing. */
  playWaterJump() {
    if (this.muted || this._focusLost) return;
    const h = this.howls.splashJump;
    if (h && h.state() === "loaded") {
      const id = h.play();
      h.rate(0.96 + Math.random() * 0.08, id);
      return;
    }
    this.playSplash({ entry: true });
  }

  /** Intro-cinematic ground impact — the big superhero landing hit. */
  playLandingImpact() {
    const h = this.howls.landingImpact;
    if (h && h.state() === "loaded") h.play();
  }

  /** Picks a random sample from the surface's footstep pool. Water steps
   *  re-use the existing wading splash so we don't double-up. */
  playFootstep(surface = "grass", alt = false) {
    if (this.muted || this._focusLost) return;
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

  /**
   * Thunder one-shot, driven by Thunderstorm. Plays the recorded
   * /sounds/thunder.mp3 sample (real distant-thunder timbre) at a volume
   * scaled by `intensity`, scheduled `delay` seconds in the future via
   * setTimeout (light reaches the player before sound).
   *
   * Falls back to a 3-layer procedural noise burst (CRACK + RUMBLE +
   * ECHO via Web Audio) only when the sample failed to load — the user
   * still hears something instead of silence.
   *
   * @param {number} delay     seconds before the thunder fires. Caller
   *                           passes ≈ boltDistance / 40 for real-world
   *                           spacing.
   * @param {number} intensity 0..1 — scales final volume. Clamped to 0.8
   *                           so even at 100% browser vol the strike is
   *                           audible but not startling.
   */
  playThunder(delay = 0, intensity = 1.0) {
    if (this.muted || this._focusLost) return;
    intensity = Math.min(Math.max(intensity, 0), 0.8);
    const delayMs = Math.max(0, delay) * 1000;

    const h = this.howls.thunder;
    if (h && h.state() === "loaded") {
      // Sample path. Scheduled via setTimeout so the visual flash leads
      // the audio by ~delay seconds. Each play gets its own id so volume
      // + rate apply per-instance (the sample is not loop:true).
      setTimeout(() => {
        if (this.muted || this._focusLost) return;
        const id = h.play();
        h.volume(VOL.thunder * intensity, id);
        // Mild pitch wobble so back-to-back strikes don't sound identical.
        h.rate(0.92 + Math.random() * 0.16, id);
      }, delayMs);
      return;
    }

    // Procedural fallback ── only reached if /sounds/thunder.mp3 didn't
    // load. Three layers: CRACK (short bandpass noise burst), RUMBLE
    // (long lowpass tail), ECHO (delayed deeper second rumble).
    const ctx = this.#ctx();
    const dest = this.#dest();
    if (!ctx || !dest) return;
    const now = ctx.currentTime + Math.max(0, delay);

    const crackBuf = this.#noiseBuffer(ctx, 0.15);
    const crack = ctx.createBufferSource();
    crack.buffer = crackBuf;
    const crackFilter = ctx.createBiquadFilter();
    crackFilter.type = "bandpass";
    crackFilter.frequency.value = 800;
    crackFilter.Q.value = 1.5;
    const crackGain = ctx.createGain();
    crackGain.gain.setValueAtTime(0, now);
    crackGain.gain.linearRampToValueAtTime(0.35 * intensity, now + 0.01);
    crackGain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
    crack.connect(crackFilter).connect(crackGain).connect(dest);
    crack.start(now);
    crack.stop(now + 0.2);

    const rumbleBuf = this.#noiseBuffer(ctx, 3.0);
    const rumble = ctx.createBufferSource();
    rumble.buffer = rumbleBuf;
    const rumbleFilter = ctx.createBiquadFilter();
    rumbleFilter.type = "lowpass";
    rumbleFilter.frequency.value = 200;
    rumbleFilter.Q.value = 0.5;
    const rumbleGain = ctx.createGain();
    rumbleGain.gain.setValueAtTime(0, now + 0.05);
    rumbleGain.gain.linearRampToValueAtTime(0.25 * intensity, now + 0.2);
    rumbleGain.gain.exponentialRampToValueAtTime(0.08 * intensity, now + 1.5);
    rumbleGain.gain.exponentialRampToValueAtTime(0.001, now + 3.0);
    rumble.connect(rumbleFilter).connect(rumbleGain).connect(dest);
    rumble.start(now);
    rumble.stop(now + 3.5);

    const echoBuf = this.#noiseBuffer(ctx, 2.0);
    const echo = ctx.createBufferSource();
    echo.buffer = echoBuf;
    const echoFilter = ctx.createBiquadFilter();
    echoFilter.type = "lowpass";
    echoFilter.frequency.value = 120;
    const echoGain = ctx.createGain();
    echoGain.gain.setValueAtTime(0, now + 0.8);
    echoGain.gain.linearRampToValueAtTime(0.12 * intensity, now + 1.2);
    echoGain.gain.exponentialRampToValueAtTime(0.001, now + 3.5);
    echo.connect(echoFilter).connect(echoGain).connect(dest);
    echo.start(now + 0.8);
    echo.stop(now + 4.0);
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

  playMapOpen() {
    this.#playOneShot("mapOpen");
  }

  playMapClose() {
    this.#playOneShot("mapClose");
  }

  playMarkerHover(sectionId = "projects") {
    if (this.muted || this._focusLost) return;
    const h = this.howls.markerHover;
    if (!h || h.state() !== "loaded") return;
    const rates = { projects: 1.0, experience: 1.1, skills: 0.9, contact: 1.2 };
    const id = h.play();
    h.rate(rates[sectionId] ?? 1.0, id);
  }

  playMarkerClick() {
    this.#playOneShot("markerClick");
  }

  playTeleportWoosh() {
    this.#playOneShot("teleportWoosh");
  }

  playTeleportArrive() {
    this.#playOneShot("teleportArrive");
  }

  playNope() {
    this.#playOneShot("nope");
  }

  playFlagDrop() {
    this.#playOneShot("flagDrop");
  }

  duckAmbient(level = 1, durationMs = 250) {
    this._ambientDuck = Math.max(0, Math.min(1, level));
    if (!this._started) return;
    this.#applyMode(this.mode, durationMs / 1000);
    this.#fadeTo(this.howls.windTrees, VOL.windTrees * this._ambientDuck, durationMs, true);
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

  /** Bruno-style brick impact: random non-repeating sample, force-shaped gain. */
  playBrickHit(force = 0, _position = null) {
    if (this.muted || this._focusLost) return;
    const now = performance.now();
    if (now - this._lastBrickHitAt < 100) return;

    const forceVolume = Math.max(0, Math.min(1, (force - 5) / 15)) ** 2;
    if (forceVolume <= 0.001) return;

    const delta = 1 + Math.floor(Math.random() * Math.max(1, BRICK_HIT_KEYS.length - 1));
    this._lastBrickHitKey = (this._lastBrickHitKey + delta) % BRICK_HIT_KEYS.length;
    this._lastBrickHitAt = now;

    const h = this.howls[BRICK_HIT_KEYS[this._lastBrickHitKey]];
    if (!h || h.state() !== "loaded") return;
    const id = h.play();
    h.volume(VOL.brickHit * forceVolume, id);
    h.rate(0.9 + Math.random() * 0.2, id);
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

  #playOneShot(key) {
    if (this.muted || this._focusLost) return;
    const h = this.howls[key];
    if (h && h.state() === "loaded") h.play();
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

  /** Rising 3-note triangle chime fired when an Achievement unlocks. Uses
   *  Howler.ctx so it inherits mute + focus loss like the other procedural
   *  fallbacks. */
  playAchievement() {
    const ctx = this.#ctx();
    const dest = this.#dest();
    if (!ctx || !dest || this.muted || this._focusLost) return;
    const now = ctx.currentTime;
    [
      { f: 880, t: 0.0 }, // A5
      { f: 1109, t: 0.12 }, // C#6
      { f: 1319, t: 0.24 }, // E6
    ].forEach(({ f, t }) => {
      const osc = ctx.createOscillator();
      osc.type = "triangle";
      osc.frequency.value = f;
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0, now + t);
      gain.gain.linearRampToValueAtTime(0.25, now + t + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.001, now + t + 0.5);
      osc.connect(gain);
      gain.connect(dest);
      osc.start(now + t);
      osc.stop(now + t + 0.55);
    });
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
