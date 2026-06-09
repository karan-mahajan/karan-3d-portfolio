import gsap from "gsap";
import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import { DUSK } from "./Palette.js";
import { shadowTintColor } from "./ShadowTint.js";
import { fogNear, fogFar } from "./FogState.js";
import { sunDir, sunRadiance } from "./WorldLight.js";

// Maps the real DirectionalLight intensity (tuned for PBR, e.g. day 2.1) into
// the faked-light radiance range the world material expects (Bruno ~1.0).
const FAKE_SUN_SCALE = 0.52;
const FAKE_SUN_FLOOR = 0.18;
import { makeMoonSprite, randomMoonPhaseAngle } from "./celestialSprite.js";
import {
  Fn, attribute, uniform, varying, vec3, vec4, float,
  positionGeometry, positionLocal, uv, sin, cos, length, smoothstep, pow, max,
  modelViewMatrix, cameraProjectionMatrix,
} from "three/tsl";

/**
 * Day / night cycle driver. Owns:
 *   - day + night palettes (colors, intensities, sun position, etc.)
 *   - the night-only visuals: starfield, moon disc + halo
 *   - the character-following lights: a soft fill (always on) and a magical
 *     overhead spotlight that turns on at night
 *   - lanterns next to each sign / billboard so text stays readable at night
 *
 * Every value that differs between modes is lerped via GSAP over `duration`
 * seconds — colors via Color.r/g/b, positions via Vector3.x/y/z, scalars
 * directly. The current mode auto-detects from the user's local clock; the
 * toggle button (wired in App.js) flips between modes.
 */

const TRANSITION_SECONDS = 2.0;
const STAR_COUNT = 280;
const STAR_DOME_RADIUS = 230;
// World-size factor for the billboarded star quads (per-instance aSize is
// multiplied by this). Replaces the old GLSL gl_PointSize since WebGPU points
// render at 1px — see #buildStars.
const STAR_QUAD_SIZE = 0.7;

export const DAY_PALETTE = Object.freeze({
  sunColor: "#ffeedd",
  // Dominant key (was 1.3). With sky-derived IBL now providing fill, the sun
  // should clearly out-power the ambient/hemi so surfaces read with form
  // (key:fill ≈ 3:1) instead of a flat even wash.
  sunIntensity: 2.1,
  // Position chosen so the visible Sun.js disc falls inside the default
  // third-person camera frame (player at spawn, camera at -Z facing +Z,
  // FOV 45° vertical / ~67° horizontal). Direction (15, 9, 35) gives:
  //   horizontal ≈ 23° right of camera (within ±33° half-FOV)
  //   elevation  ≈ 13° above horizon  (within +15° upper-frame edge)
  // Shadow direction is fine at this elevation; cast length is moderate.
  sunOffset: new THREE.Vector3(15, 9, 35),
  rimColor: "#ff8855",
  // Faint edge separation only (was 0.35) — IBL + hemi now carry the fill, so
  // a strong rim would just flatten contrast.
  rimIntensity: 0.18,
  // Cool sky-blue ambient: physically the shadow side of a sunlit object is
  // filled by blue skylight, so a cool fill reads as real daylight (the old
  // muddy purple #b59bb0 flattened it). The chromatic-shadow look is now
  // carried properly by ShadowTint.js (real coloured shadows), so ambient no
  // longer has to fake it.
  ambientColor: "#a7b4d2",
  ambientIntensity: 0.28,
  hemiSky: "#8fc4f0",
  // Warm-neutral ground bounce — sunlit earth kicking light back up.
  hemiGround: "#9a8472",
  hemiIntensity: 0.32,
  // Rich-but-clean zenith → soft mid → pale airy horizon. The earlier flat
  // steel-blue horizon (#88aabb) made midday read murky; lifting the horizon to
  // a bright haze gives the sky depth and air.
  skyTop: "#3f86d4",
  skyMid: "#7eb6ea",
  // Horizon === fog colour so the ocean fades seamlessly into the sky band —
  // no visible ring where the water plane ends. Pale warm-cyan haze: bright
  // enough to read as a real horizon, still bridging the deep ocean tint.
  skyHorizon: "#aac6d2",
  skyGround: "#4a3528",
  fogColor: "#aac6d2",
  // Cool periwinkle daytime shadows (realistic sky-fill hue, faint violet).
  shadowTint: "#6a78c4",
  // Pulled tighter than the old 65→165 so the ocean plane (extending 150 m
  // from the island centre) fully dissolves into fog before its edge.
  fogNear: 50,
  fogFar: 130,
  grassColor: "#5aa033",
  grassShadowStrength: 0.75,
  fireflyIntensity: 0,
  starsOpacity: 0,
  moonOpacity: 0,
  // Subtle 0.6 fill from above in day mode so the character's face has a
  // neutral top-light counter to the warm sun — keeps the skin from
  // reading yellow. Night cranks it up to 9 for an obvious stage-light
  // pool on the ground around the character. The numbers look high
  // because three.js's physical lighting model + linear decay over 10u
  // dilutes the light a lot — spec's "2" wasn't visible.
  spotlightIntensity: 0.6,
  fillColor: "#ffffff",
  // Day face fill — counters the warm directional sun on the face so
  // the skin doesn't read yellow. 1.5 was OK but with the camera-side
  // anchored fill now actually pointing at the face, 1.8 is what reads
  // best across both modes.
  fillIntensity: 1.8,
  sunMeshOpacity: 1,
  billboardEmissiveBoost: 1.0,
  // Street lamps are dark during the day — the model is visible (physical
  // structure) but the bulb glow + PointLight are off. StreetLights.js reads
  // these values in setMode().
  streetLightIntensity: 0,
  streetLightBulbEmissive: 0,
  // Warm daylight tint on the water — sky-fresh reads as a brighter blue
  // because the Water2 shader multiplies the reflected colour by this tint.
  waterColor: "#4a90c4",
});

export const NIGHT_PALETTE = Object.freeze({
  // Moonlight: cooler + a touch brighter than the old steel-blue so the moon
  // actually shapes surfaces instead of leaving them flat-dark.
  sunColor: "#8fa6d6",
  sunIntensity: 0.4,
  sunOffset: new THREE.Vector3(-30, 25, -20),
  rimColor: "#46608f",
  rimIntensity: 0.0,
  ambientColor: "#0e1a30",
  // Lifted from 0.18 so the world between street lamps isn't pitch black —
  // first-time visitors should be able to see paths + trees as silhouettes.
  ambientIntensity: 0.25,
  hemiSky: "#163052",
  hemiGround: "#0a0e1c",
  hemiIntensity: 0.12,
  // Lifted from near-black so the night sky still reads as a sky band
  // rather than the void around the canvas. Bands kept in a deep cobalt-blue
  // family (less murky than the old grey-navy) so stars + moon still stand out.
  // Horizon === fog so the night ocean dissolves into the sky band.
  skyTop: "#0a1230",
  skyMid: "#13224a",
  skyHorizon: "#16263f",
  skyGround: "#08080f",
  fogColor: "#16263f",
  // Deep indigo shadows — cohesive with the cobalt night sky.
  shadowTint: "#1f3270",
  fogNear: 30,
  fogFar: 95,
  grassColor: "#1f3a2a",
  grassShadowStrength: 0.25,
  fireflyIntensity: 2.2,
  starsOpacity: 1,
  moonOpacity: 1,
  spotlightIntensity: 9.0,
  // Cool-neutral fill that DOMINATES the near-black night ambient so
  // the character's face stays clearly readable. 0.45 was an anaemic
  // top-up; 2.5 with decay=1.4 over the 1.5u face distance gives ≈ 1.5
  // effective intensity at the face — enough to actually see skin
  // detail against the dark world.
  fillColor: "#ccd6ec",
  fillIntensity: 2.5,
  sunMeshOpacity: 0,
  billboardEmissiveBoost: 3.0,
  // Night street lamps + bulb emissive: the primary light source for
  // navigation. Five closest lights are active at a time (see StreetLights).
  streetLightIntensity: 1.5,
  streetLightBulbEmissive: 2.0,
  // Cooler, deeper night water — moon + street lamps + stars reflect against
  // a darker blue-grey base so the night scene reads as cold water.
  waterColor: "#2a4a64",
});

/**
 * DUSK keyframe — golden hour. Colours are the user's authored dusk palette
 * (Palette.DUSK), the warm sunset look the whole project is themed around. The
 * intensities/opacities sit between DAY and NIGHT so the cycle reads as a real
 * sunset: sun still warm and low, stars + lamps just beginning to appear.
 * DAWN reuses the same warm colours (a sunrise looks like a sunset) — the EAST
 * vs WEST sun position from the arc is what distinguishes them visually.
 */
export const DUSK_PALETTE = Object.freeze({
  sunColor: DUSK.sunColor,          // #ffd58a
  sunIntensity: 1.55,
  rimColor: "#ff7a45",
  rimIntensity: 0.3,
  ambientColor: DUSK.ambientColor,  // #ffb088
  ambientIntensity: 0.34,
  hemiSky: "#b3a6dc",              // warm lavender skylight
  hemiGround: DUSK.hemiGround,      // #d4845a
  hemiIntensity: 0.34,
  // Deeper blue-violet zenith → warm coral mid → golden horizon. The deeper top
  // gives the sunset real vertical range instead of washing the whole dome warm.
  skyTop: "#4a568f",
  skyMid: "#c98a72",               // warm coral band between zenith + horizon
  skyHorizon: DUSK.skyHorizon,     // #ffb084
  skyGround: DUSK.skyGround,       // #4a3528
  fogColor: DUSK.fogColor,         // #ffb084 (=== skyHorizon)
  fogNear: 45,
  fogFar: 120,
  grassColor: "#4a8a3a",
  grassShadowStrength: 0.6,
  fireflyIntensity: 0.7,
  starsOpacity: 0.18,
  moonOpacity: 0.3,
  spotlightIntensity: 2.5,
  fillColor: "#ffd9c0",
  fillIntensity: 1.6,
  sunMeshOpacity: 0.9,
  billboardEmissiveBoost: 1.8,
  streetLightIntensity: 0.6,
  streetLightBulbEmissive: 0.9,
  waterColor: "#3a6a8a",
  // Magenta-rose dusk shadows — the authored warm-sunset chromatic shadow.
  shadowTint: "#9a3f86",
});

/** DAWN keyframe — sunrise. Same warm dusk colours, slightly cooler sun + the
 *  stars/moon/lamps a touch dimmer than dusk (night is ending, not starting). */
export const DAWN_PALETTE = Object.freeze({
  ...DUSK_PALETTE,
  sunColor: "#ffd9b0",
  rimColor: "#ff8a5a",
  // Sunrise reads COOLER than sunset: a cool morning-blue dome with a soft peach
  // glow at the horizon, lavender in between — distinct from dusk's hot orange.
  ambientColor: "#9a93b8",
  hemiSky: "#a9c2e8",
  skyTop: "#54709f",
  skyMid: "#b89fb4",
  skyHorizon: "#ffc59a",
  fogColor: "#ffc59a",
  // Cool morning violet shadows (vs dusk's warmer magenta-rose).
  shadowTint: "#7a5fb0",
  starsOpacity: 0.1,
  moonOpacity: 0.18,
  streetLightIntensity: 0.4,
  streetLightBulbEmissive: 0.6,
});

// ── Continuous day/night cycle ────────────────────────────────────────────
// One full revolution every CYCLE_SECONDS. progress 0..1 maps to a synthetic
// clock via hoursFromProgress: p=0 → 06:00 (dawn), 0.30 → ~13:00 (day), 0.58
// → ~20:00 (dusk), 0.75 → 00:00 (night), wrapping back to dawn at 1.0.
const CYCLE_SECONDS = 150; // 2.5-minute full cycle
// progress at which mode flips day↔night (hours 20:00 → (20-6)/24).
const NIGHT_THRESHOLD = 0.5833;
// Night should pass quickly — the dark arc (NIGHT_THRESHOLD→1.0 ≈ 42% of the
// cycle ≈ 62s at the base rate) is fast-forwarded to NIGHT_SECONDS wall-clock.
// Day keeps the slow base rate, so we get long days + short nights. The night
// arc is split into ~12s dusk→night + ~10s dark hold + ~12s night→dawn
// (CYCLE_STOPS 0.73 / 0.853), so NIGHT_SECONDS ≈ that sum; no sub-phase < 10s.
const NIGHT_SECONDS = 34;
const NIGHT_SPEEDUP = ((1 - NIGHT_THRESHOLD) * CYCLE_SECONDS) / NIGHT_SECONDS;
// The four selectable phases and the cycle position each one peaks at. The UI
// lets the visitor jump to any of these; the cycle then keeps advancing.
const PHASE_PROGRESS = Object.freeze({ dawn: 0.0, day: 0.3, dusk: 0.58, night: 0.75 });
const PHASE_ORDER = ["dawn", "day", "dusk", "night"];
// Keyframe stops around the cycle (sorted; DAWN repeats at 1.0 for the wrap).
const CYCLE_STOPS = [
  { at: 0.0, palette: DAWN_PALETTE },
  // DAWN is likewise held flat (0.0→0.06) so the sunrise lingers instead of
  // immediately lerping toward day. This stretch runs at the base day rate
  // (1/CYCLE_SECONDS progress/s), so 0.06 span ≈ 9s of held dawn.
  { at: 0.06, palette: DAWN_PALETTE },
  // DAY is held flat across a plateau (0.2→0.45) so bright, clean daytime
  // actually LINGERS. Previously day was a single instantaneous keyframe at 0.3
  // — the cycle reached full day for one frame and immediately ramped back
  // toward dusk, so the world read as permanently mid-transition and never
  // settled into a stable bright day (dawn/dusk/night all had plateaus; day
  // didn't). 0.3 (day phase peak) sits inside the plateau; ~37s of held day at
  // the base rate, delivering the intended long-day/short-night cadence.
  { at: 0.2, palette: DAY_PALETTE },
  { at: 0.45, palette: DAY_PALETTE },
  // DUSK is held flat (0.513→0.58) too, so golden hour lingers instead of
  // peaking for an instant and then being rushed into night by the speed-up
  // that kicks in at NIGHT_THRESHOLD (0.5833). This plateau sits entirely on
  // the slow base-rate side, so its 0.067 span ≈ 10s of held dusk. 0.58 (dusk
  // phase peak) is the plateau's end, so jumping to "dusk" lands in full dusk.
  { at: 0.513, palette: DUSK_PALETTE },
  { at: 0.58, palette: DUSK_PALETTE },
  // NIGHT is held flat across a plateau (0.73→0.853) rather than touched at a
  // single instant, so the dark phase actually lingers instead of ramping
  // dusk→night→dawn straight through. Plateau width × NIGHT_SECONDS sets how
  // long it reads as truly dark (≈10s here); 0.75 (night phase peak) sits
  // inside it so jumping to "night" lands in full dark. The wider dusk→night
  // (0.5833→0.73) and night→dawn (0.853→1.0) spans give ~12s twilight ramps.
  { at: 0.73, palette: NIGHT_PALETTE },
  { at: 0.853, palette: NIGHT_PALETTE },
  { at: 1.0, palette: DAWN_PALETTE },
];
// Palette fields interpolated each frame: colours (lerped in RGB) + scalars.
const CYCLE_COLOR_FIELDS = [
  "sunColor", "rimColor", "ambientColor", "hemiSky", "hemiGround",
  "skyTop", "skyMid", "skyHorizon", "skyGround", "fogColor", "grassColor", "fillColor",
  "shadowTint",
];
const CYCLE_SCALAR_FIELDS = [
  "sunIntensity", "rimIntensity", "ambientIntensity", "hemiIntensity",
  "fogNear", "fogFar", "fireflyIntensity", "starsOpacity", "moonOpacity",
  "spotlightIntensity", "fillIntensity", "sunMeshOpacity", "billboardEmissiveBoost",
];

/** Synthetic clock hours [0,24) for a cycle progress. p=0 → 06:00. */
function hoursFromProgress(progress) {
  return (progress * 24 + 6) % 24;
}

/** Inverse: cycle progress for the real local clock, so first load matches
 *  the actual time of day before the cycle takes over. */
function progressFromClock() {
  const now = new Date();
  const hours = now.getHours() + now.getMinutes() / 60;
  return (((hours - 6) % 24) + 24) % 24 / 24;
}

/**
 * Returns 'day' between 06:00 and 19:59, 'night' otherwise.
 * Boundary matches SUNSET in #calcSunPosition — keeps the moon-arc
 * domain continuous with the day-arc domain so a clock-driven mode
 * flip never lands on a gap.
 */
export function detectAutoMode() {
  const hour = new Date().getHours();
  return hour >= 20 || hour < 6 ? "night" : "day";
}

export class TimeOfDay {
  /**
   * @param {object} opts
   * @param {THREE.Scene} opts.scene
   * @param {THREE.Fog}   opts.fog
   * @param {THREE.DirectionalLight} opts.sun
   * @param {THREE.DirectionalLight} opts.rim
   * @param {THREE.AmbientLight}     opts.ambient
   * @param {THREE.HemisphereLight}  opts.hemi
   * @param {import('./Sky.js').Sky} opts.sky
   * @param {import('./Sun.js').Sun} opts.sunMesh
   * @param {import('./Grass.js').Grass} opts.grass
   * @param {import('../Effects/Fireflies.js').Fireflies} opts.fireflies
   * @param {import('../Portfolio/Billboards.js').Billboards} opts.billboards
   * @param {import('../Portfolio/Signs.js').Signs}           opts.signs
   * @param {THREE.Object3D} opts.playerGroup - the visual player root (rotates with character)
   * @param {import('../Player/Character.js').Character} [opts.character] - wired post-boot
   */
  constructor({
    scene,
    fog,
    sun,
    rim,
    ambient,
    hemi,
    sky,
    sunMesh,
    grass,
    fireflies,
    water = null,
    billboards = null,
    signs = null,
    playerGroup,
    character = null,
  }) {
    this.scene = scene;
    this.fog = fog;
    this.sun = sun;
    this.rim = rim;
    this.ambient = ambient;
    this.hemi = hemi;
    this.sky = sky;
    this.sunMesh = sunMesh;
    this.grass = grass;
    this.fireflies = fireflies;
    this.water = water;
    this.billboards = billboards;
    this.signs = signs;
    this.playerGroup = playerGroup;
    this.character = character;

    // ── Continuous-cycle state ──
    // `_raw` is the raw progress accumulator (may run past 1.0 mid-tween); the
    // public `progress` getter normalises it to [0,1). FIRST LOAD ALWAYS OPENS
    // ON DAY: visitors should land in a bright, readable world regardless of
    // their local time. `paused` holds the cycle on the day peak until
    // easeToClock() (scheduled ~12s after spawn) settles to the real local time
    // and resumes the automatic cycle.
    this._raw = 0.3; // day peak
    this.paused = true; // hold day until easeToClock() runs
    this._mode = this.#modeAt(this.progress);
    this._tween = null;

    // Precompute per-keyframe Colors + the reusable "live" sampled palette.
    this.#prepareCycle();

    this.#buildCharacterLights();
    this.#buildStars();
    this.#buildMoon();

    // Sample + apply the starting palette so the first frame is correct, and
    // snap the sun/moon direction to the synthetic clock.
    this.#sampleCycle(this.progress);
    this.#applyContinuous();
    this.sunOffset = this.#calcOffset();
    sunDir.value.copy(this.sunOffset).normalize();
    // Separate DISPLAY directions for the sun disc (sun arc) and the moon
    // (moon arc), so at dawn/dusk the sun sits WEST while the moon rises EAST —
    // they never stack on top of each other the way they did when both used
    // sunOffset. (sunOffset still drives the shadow-casting DirectionalLight.)
    const hours = hoursFromProgress(this.progress);
    this.sunDiscDir = this.#calcSunPosition(hours).normalize();
    this.moonOffset = this.#calcMoonPosition(hours).normalize();
  }

  // ── Public API ────────────────────────────────────────────────────────────
  /** Normalised cycle position in [0,1). 0 = dawn, 0.3 = day, 0.58 = dusk,
   *  0.75 = night. */
  get progress() {
    return ((this._raw % 1) + 1) % 1;
  }

  set progress(value) {
    this._raw = value;
  }

  /** 'day' | 'night', derived from progress. Settable from outside (the shader
   *  prewarm sets it to force a lighting config) — a write jumps the cycle to
   *  that phase's peak and applies it instantly. */
  get mode() {
    return this._mode;
  }

  set mode(value) {
    if (value !== "day" && value !== "night") return;
    this._raw = value === "night" ? 0.75 : 0.3;
    this._mode = value;
    this.#sampleCycle(this.progress);
    this.#applyContinuous();
  }

  /** Continuous 0 (full day) → 1 (deep night) factor. Read by Lava for its
   *  night glow. Tracks the interpolated moon opacity so it ramps with dusk. */
  get nightFactor() {
    return this._live.moonOpacity;
  }

  /** Current phase name ('dawn' | 'day' | 'dusk' | 'night') from progress —
   *  drives the UI button icon. Boundaries sit midway between phase peaks. */
  get phase() {
    const p = this.progress;
    if (p < 0.15 || p >= 0.85) return "dawn";
    if (p < 0.44) return "day";
    if (p < 0.665) return "dusk";
    return "night";
  }

  /**
   * Jump the cycle to a specific phase (dawn/day/dusk/night), easing FORWARD
   * through time so the sky animates naturally (never runs backwards), then
   * RESUME auto-advancing from there. This is what the UI selector calls — the
   * visitor picks a starting mood and the 2-minute cycle carries on.
   */
  selectPhase(phase, duration = 2.0) {
    const target = PHASE_PROGRESS[phase];
    if (target === undefined) return;
    this.paused = true; // hold auto-advance while the ease tween drives _raw
    this._tween?.kill?.();
    let to = target;
    while (to <= this._raw) to += 1; // always forward in time
    this._tween = gsap.to(this, {
      _raw: to,
      duration,
      ease: "sine.inOut",
      onComplete: () => {
        this._raw = ((this._raw % 1) + 1) % 1;
        this._tween = null;
        this.paused = false; // resume the automatic cycle
      },
    });
    if (phase === "night" || phase === "dusk") this.achievements?.onToggleNight?.();
    else this.achievements?.onToggleDay?.();
  }

  /**
   * Ease from the forced day-start to the REAL local-clock time, then resume
   * the automatic cycle. Called ~12s after spawn so visitors always open on a
   * bright day, which then settles to the actual time of day.
   *
   * Eases via the SHORTEST direction (nearest path), NOT always-forward: a
   * forward-only wrap could traverse nearly a full cycle — e.g. day-peak (0.3)
   * settling to a morning clock (~0.2) is +0.9 forward, which timelapses through
   * dusk→night→dawn and back to day in a few seconds (a jarring flash). The
   * nearest path (−0.1 here) stays inside the flat day plateau and is
   * imperceptible. A backward step within day never reads as "sky running
   * backwards" because the day colours barely change across the plateau.
   */
  easeToClock(duration = 4.0) {
    this._tween?.kill?.();
    const target = progressFromClock();
    // Signed shortest distance in [-0.5, 0.5).
    const signed = ((((target - this.progress + 0.5) % 1) + 1) % 1) - 0.5;
    if (Math.abs(signed) < 0.04) {
      // Real time is already ~day — just hand back to the automatic cycle.
      this.paused = false;
      return;
    }
    this.paused = true;
    this._tween = gsap.to(this, {
      _raw: this._raw + signed,
      duration,
      ease: "sine.inOut",
      onComplete: () => {
        this._raw = ((this._raw % 1) + 1) % 1;
        this._tween = null;
        this.paused = false;
      },
    });
  }

  /** Advance the selector to the next phase in order (dawn→day→dusk→night→…). */
  cyclePhase(duration = 2.0) {
    const next = PHASE_ORDER[(PHASE_ORDER.indexOf(this.phase) + 1) % PHASE_ORDER.length];
    this.selectPhase(next, duration);
    return next;
  }

  /** Back-compat: a binary day/night request maps to the day or night phase. */
  setMode(mode, duration = 2.0) {
    this.selectPhase(mode === "night" ? "night" : "day", duration);
  }

  toggle(duration = 2.0) {
    this.cyclePhase(duration);
  }

  /** Resume the automatic cycle (e.g. if something paused it). */
  resumeCycle() {
    this._tween?.kill?.();
    this._tween = null;
    this.paused = false;
  }

  /** Re-apply the current sampled palette to every consumer. Called by App.js
   *  after async loads (Signs / Billboards / Water) so freshly created scene
   *  objects pick up the correct values. */
  reapply() {
    this.#sampleCycle(this.progress);
    this.#applyContinuous();
    if (this.water) this.water.applyTimeOfDay(this._mode);
    if (this.distantIslands) this.distantIslands.setMode(this._mode, 0);
  }

  /** Snap the sun/moon direction to the current cycle position, skipping the
   *  per-frame lerp. */
  snapToClock() {
    if (this.sunOffset) this.sunOffset.copy(this.#calcOffset());
  }

  /** Mode for a given cycle progress (mirrors detectAutoMode's 06:00–20:00). */
  #modeAt(progress) {
    return progress < NIGHT_THRESHOLD ? "day" : "night";
  }

  /**
   * Update per-frame state — advance the day/night cycle, then track the
   * player-following lights + camera-following stars/moon.
   * @param {number} [frameDelta=0] seconds since last frame (0 = no advance,
   *   used by the shader prewarm to settle a forced phase without moving time).
   */
  tick(playerPos, camera, elapsed, frameDelta = 0) {
    // ── Advance the cycle + apply the sampled palette ──
    if (!this.paused && frameDelta > 0) {
      // Fast-forward through the night arc so the dark phase only lasts
      // ~NIGHT_SECONDS while daytime keeps the slow base rate.
      const speed = this.progress >= NIGHT_THRESHOLD ? NIGHT_SPEEDUP : 1;
      this._raw += (frameDelta / CYCLE_SECONDS) * speed;
    }
    this.#sampleCycle(this.progress);
    this.#applyContinuous();
    // Discrete day↔night flip drives water / islands / audio / achievements.
    const mode = this.#modeAt(this.progress);
    if (mode !== this._mode) {
      this._mode = mode;
      if (this.water) this.water.applyTimeOfDay(mode, { tween: true, duration: 1.5 });
      if (this.distantIslands) this.distantIslands.setMode(mode, 1.5);
      if (mode === "night") {
        // Each nightfall shows a fresh, randomly-chosen moon phase.
        this.setMoonPhase();
        this.achievements?.onToggleNight?.();
      } else {
        this.achievements?.onToggleDay?.();
      }
    }

    // Keep the rim light visible even at zero intensity. Toggling
    // Light.visible changes the shader light count and can trigger a
    // noticeable compile hitch when switching day/night modes.
    if (this.fillLight && playerGroupExists(this.playerGroup) && camera) {
      // Position the fill BETWEEN the camera and the player so it always
      // lights whichever side of the character the camera is seeing.
      // Anchoring to the player's own facing direction was wrong: the
      // Avaturn model's face is on the side opposite to the player's
      // "forward" yaw, so the previous offset put the fill behind the
      // head and the face read as completely dark at night.
      const cx = camera.position.x - playerPos.x;
      const cz = camera.position.z - playerPos.z;
      const cl = Math.max(0.001, Math.hypot(cx, cz));
      this.fillLight.position.set(
        playerPos.x + (cx / cl) * 1.5,
        playerPos.y + 1.7,
        playerPos.z + (cz / cl) * 1.5,
      );
    }
    if (this.spotLight && playerGroupExists(this.playerGroup)) {
      this.spotLight.position.set(playerPos.x, playerPos.y + 10, playerPos.z);
      this.spotTarget.position.set(playerPos.x, playerPos.y, playerPos.z);
      this.spotTarget.updateMatrixWorld();
      // Visible shaft: cone (height=9) is centered at origin, so position
      // its center at player.y + 4.5 so apex sits ≈ y+9 and base ≈ y+0.
      if (this.spotShaft) {
        this.spotShaft.position.set(
          playerPos.x,
          playerPos.y + 4.5,
          playerPos.z,
        );
        // Opacity tracks live spotlight intensity so the shaft fades
        // in / out with the day-night transition automatically. Lower
        // peak (0.35) than before so the cone reads as a hint, not a
        // floodlight.
        const peak = NIGHT_PALETTE.spotlightIntensity;
        this.spotShaftMat.uniforms.uOpacity.value =
          (Math.max(
            0,
            this.spotLight.intensity - DAY_PALETTE.spotlightIntensity,
          ) /
            Math.max(0.001, peak - DAY_PALETTE.spotlightIntensity)) *
          0.35;
        this.spotShaft.visible =
          this.spotShaftMat.uniforms.uOpacity.value > 0.005;
      }
    }
    if (this.starGroup && camera) {
      this.starGroup.position.copy(camera.position);
      this.starMaterial.uniforms.uTime.value = elapsed;
      // Visibility tracks live uniform so a partially-faded starfield
      // mid-transition still renders, but a fully-faded one is skipped.
      this.starGroup.visible =
        this.starMaterial.uniforms.uOpacity.value > 0.001;
    }
    // Shadow-light direction (mode-based arc). Lerped so transitions are smooth.
    this.sunOffset.lerp(this.#calcOffset(), 0.06);
    // Feed the faked-light world material the same sun direction.
    sunDir.value.copy(this.sunOffset).normalize();
    // Independent sun-disc + moon display directions (separate arcs → opposite
    // sides of the sky at dawn/dusk, never stacked). Snap is fine: both are
    // continuous functions of progress and only visible when their opacity > 0.
    const hours = hoursFromProgress(this.progress);
    this.sunDiscDir.copy(this.#calcSunPosition(hours)).normalize();
    this.moonOffset.copy(this.#calcMoonPosition(hours)).normalize();

    if (this.moonGroup && camera) {
      this.#updateMoonPosition(camera);
      this.moonGroup.visible = this.moonMat.opacity > 0.001;
    }
  }

  // ── Build helpers ─────────────────────────────────────────────────────────
  #buildCharacterLights() {
    // Face fill — placed in front of the character (rotates with him)
    // so it actually lights the face rather than sitting on a fixed
    // world axis offset. Decay=1.4 keeps it tight to the head; intensity
    // is high because three.js's physical lighting model dilutes
    // PointLight contribution fast over the head-height distance.
    this.fillLight = new THREE.PointLight(0xffffff, 1.5, 6, 1.4);
    this.fillLight.castShadow = false;
    this.scene.add(this.fillLight);

    // Magical overhead spotlight — day=subtle fill, night=bright cone.
    // castShadow stays FALSE: shadows from a second light kill FPS, and the
    // sun already shadows the character correctly from above.
    this.spotLight = new THREE.SpotLight(
      0xddeeff,
      0, // intensity (set by mode)
      20, // distance
      Math.PI / 4, // 45° cone (half-angle) — wider than PI/5 so the ground
                   // pool around the player at night is large enough to read
                   // surroundings, not just the character.
      0.6, // penumbra (soft edges)
      1, // linear decay (decay=2 dilutes too aggressively at this distance)
    );
    this.spotLight.castShadow = false;
    this.spotTarget = new THREE.Object3D();
    this.scene.add(this.spotTarget);
    this.spotLight.target = this.spotTarget;
    this.scene.add(this.spotLight);

    // Visible light shaft — three.js SpotLight only lights surfaces it
    // hits, the volumetric cone is invisible without a custom mesh. This
    // additive-blended open cone gives the "stage spotlight" look: bright
    // at the apex, fading toward the ground.
    // Radius 1.2 at the ground = tightly framed around the character; the
    // 2.5 base was too wide and read as a stadium floodlight.
    const shaftGeom = new THREE.ConeGeometry(1.2, 9, 24, 1, true);
    // B0/WebGPU: ported from the raw-GLSL ShaderMaterial to a
    // MeshBasicNodeMaterial. The volumetric falloff is a TSL graph over the
    // cone's object-space position (vUp = base→apex, vEdge = axis→silhouette).
    const shaftColor = uniform(vec3(0.8, 0.8667, 1.0)); // #ccddff
    const shaftOpacity = uniform(0);
    this.spotShaftMat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      fog: false,
    });
    {
      // Cone is 9 tall, centered at origin → y in [-4.5, 4.5].
      const vUp = positionLocal.y.add(4.5).div(9.0);
      const vEdge = length(positionLocal.xz).div(max(float(1.2).mul(vUp.oneMinus()), 0.001));
      const fall = pow(vUp, 1.6).mul(float(1.0).sub(vEdge.mul(0.4)));
      this.spotShaftMat.colorNode = shaftColor;
      this.spotShaftMat.opacityNode = fall.mul(shaftOpacity);
    }
    // Legacy `.uniforms` shape so tick() can keep writing uOpacity.value.
    this.spotShaftMat.uniforms = { uColor: shaftColor, uOpacity: shaftOpacity };
    this.spotShaft = new THREE.Mesh(shaftGeom, this.spotShaftMat);
    this.spotShaft.frustumCulled = false;
    this.spotShaft.renderOrder = 5;
    this.scene.add(this.spotShaft);
  }

  #buildStars() {
    // B0/WebGPU: WebGPU renders THREE.Points as 1px PointList primitives (no
    // point size), so the old GLSL star cloud can't survive the backend. Built
    // as instanced billboarded quads (same technique as Fireflies): a tiny quad
    // per star, billboarded in the vertex node by offsetting the corner in VIEW
    // space, twinkle + radial disc as TSL node graphs. The `.uniforms` shape is
    // preserved so #applyContinuous / tick() drive it unchanged.
    const bases = new Float32Array(STAR_COUNT * 3);
    const sizes = new Float32Array(STAR_COUNT);
    const phases = new Float32Array(STAR_COUNT);
    for (let i = 0; i < STAR_COUNT; i++) {
      // Sample in the upper hemisphere only so we don't waste points below
      // the horizon (player can never look past −15° down anyway).
      const u = Math.random();
      const v = Math.random() * 0.7 + 0.15;
      const theta = u * Math.PI * 2;
      const phi = Math.acos(v); // v in [0.15, 0.85] → phi in [~0.55, ~1.42]
      const r = STAR_DOME_RADIUS;
      bases[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      bases[i * 3 + 1] = r * Math.cos(phi);
      bases[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
      sizes[i] = 0.5 + Math.random() * 1.5;
      phases[i] = Math.random() * Math.PI * 2;
    }

    const baseGeom = new THREE.BufferGeometry();
    const quad = new Float32Array([-0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0]);
    const quadUv = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    baseGeom.setAttribute("position", new THREE.BufferAttribute(quad, 3));
    baseGeom.setAttribute("uv", new THREE.BufferAttribute(quadUv, 2));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    const geom = new THREE.InstancedBufferGeometry();
    geom.setAttribute("position", baseGeom.attributes.position);
    geom.setAttribute("uv", baseGeom.attributes.uv);
    geom.setIndex(baseGeom.index);
    geom.instanceCount = STAR_COUNT;
    geom.setAttribute("aBase", new THREE.InstancedBufferAttribute(bases, 3));
    geom.setAttribute("aSize", new THREE.InstancedBufferAttribute(sizes, 1));
    geom.setAttribute("aPhase", new THREE.InstancedBufferAttribute(phases, 1));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const uTime = uniform(0);
    const uOpacity = uniform(0);
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    });
    const vTwinkle = varying(float(0), "vStarTwinkle");
    mat.vertexNode = Fn(() => {
      const base = attribute("aBase");
      const size = attribute("aSize");
      const phase = attribute("aPhase");
      // 0.3 + 0.7 * (0.5 + 0.5 * sin(...))
      vTwinkle.assign(
        float(0.3).add(float(0.5).add(sin(uTime.mul(1.6).add(phase.mul(5.0))).mul(0.5)).mul(0.7)),
      );
      const view = modelViewMatrix.mul(vec4(base, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(size.mul(STAR_QUAD_SIZE)));
      return cameraProjectionMatrix.mul(view);
    })();
    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = vec3(1.0, 1.0, 1.0);
    mat.opacityNode = core.mul(vTwinkle).mul(uOpacity);
    mat.uniforms = { uTime, uOpacity };
    this.starMaterial = mat;

    this.starGroup = new THREE.Group();
    const mesh = new THREE.Mesh(geom, mat);
    mesh.frustumCulled = false;
    this.starGroup.add(mesh);
    this.starGroup.renderOrder = -1; // draw with the sky
    this.scene.add(this.starGroup);
  }

  #buildMoon() {
    this.moonGroup = new THREE.Group();
    this.moonGroup.renderOrder = -1;

    // Phase-shaded moon billboard — a real crescent/quarter/gibbous/full shape
    // (random each night). Additive + toneMapped:false so only the LIT limb
    // shows over the night sky and the core blooms to a soft glow. Replaces the
    // old hard sphere disc + ring that read as a flat 2-tone circle.
    this._moonPhaseAngle = randomMoonPhaseAngle();
    this.moonMat = new THREE.MeshBasicMaterial({
      map: makeMoonSprite({ phaseAngle: this._moonPhaseAngle }),
      // Slight HDR-ish boost so the lit limb crosses the bloom threshold.
      color: new THREE.Color(1.35, 1.45, 1.65),
      transparent: true,
      opacity: 0,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
      side: THREE.DoubleSide,
    });
    this.moonMesh = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), this.moonMat);
    this.moonMesh.frustumCulled = false;
    this.moonMesh.renderOrder = 9;
    this.moonGroup.add(this.moonMesh);

    this.scene.add(this.moonGroup);
  }

  /** Re-roll the moon phase (called when night begins so each night can show a
   *  different crescent/half/full). Rebuilds the sprite texture. */
  setMoonPhase(phaseAngle = randomMoonPhaseAngle()) {
    this._moonPhaseAngle = phaseAngle;
    const old = this.moonMat?.map;
    if (!this.moonMat) return;
    this.moonMat.map = makeMoonSprite({ phaseAngle });
    this.moonMat.needsUpdate = true;
    old?.dispose?.();
  }

  #updateMoonPosition(camera) {
    // The moon rides the same direction as the (night) DirectionalLight that
    // casts shadows — i.e. whatever sunOffset is at night. Camera-anchored at
    // STAR_DOME_RADIUS * 0.7 so it sits inside the star dome, past nearby props.
    this.moonGroup.position
      .copy(camera.position)
      .addScaledVector(this.moonOffset, STAR_DOME_RADIUS * 0.7);
    // Billboard toward the camera so the phase shape always faces the viewer.
    this.moonMesh.quaternion.copy(camera.quaternion);
  }

  // ── Real-time sun/moon position ───────────────────────────────────────────
  /** Fractional hours since midnight, system local clock. */
  #getCurrentHours() {
    const now = new Date();
    return now.getHours() + now.getMinutes() / 60 + now.getSeconds() / 3600;
  }

  // Arc shape parameters — tuned so the disc stays inside the default
  // third-person camera's view frustum at every hour. The default camera
  // sits ~6.7° below horizontal looking north (PlayerCamera initial
  // setLookAt) with FOV 45°v / 67°h, which means the upper frame edge
  // sees only ~16° above horizon. After normalize-to-magnitude, we need
  // y / z < tan(16°) ≈ 0.28 at noon, which is what the values below
  // give. Earlier attempts with a y peak of 42 + z bias 0.6×distance
  // put the sun at ~56° elevation — well above the frame.
  static #ARC = Object.freeze({
    X_SWING: 15,    // east at moon/sunrise → west at moon/sunset
    Y_BASE: 7,      // altitude at horizon (low but above the visible ground)
    Y_SWING: 6,     // y peak at noon = Y_BASE + Y_SWING = 13
    Z_FORWARD: 50,  // dominant forward (+Z) component so the disc is
                    // always in front of the north-facing camera
  });

  /**
   * Sun offset for a daytime hour. Traces an arc from EAST (+X) at
   * SUNRISE to WEST (−X) at SUNSET, with a strong forward (+Z) bias
   * and gentle altitude peak so the visible disc stays inside the
   * default camera frame. Trades a chunk of real-world geometric
   * purity for a sun that's actually visible without the user
   * spinning the camera — the alternative (pure east-west arc) puts
   * the disc 60-80° off-axis from camera-forward at sunrise / noon /
   * sunset and was the bug behind the "I don't see the sun anywhere"
   * report on 2026-05-24.
   *
   * Magnitude is normalized to 40 by #calcOffset so the shadow camera
   * frustum (set in App.js #initLighting) stays inside its far plane.
   */
  #calcSunPosition(hours) {
    const SUNRISE = 6.0;
    const SUNSET = 20.0;
    const DAY_LENGTH = SUNSET - SUNRISE;
    const t = Math.max(0, Math.min(1, (hours - SUNRISE) / DAY_LENGTH));
    const angle = t * Math.PI;            // 0 east → π west
    const elevation = Math.sin(angle);    // 0 horizon, 1 noon
    const A = TimeOfDay.#ARC;
    return new THREE.Vector3(
      Math.cos(angle) * A.X_SWING,
      A.Y_BASE + elevation * A.Y_SWING,
      A.Z_FORWARD,
    );
  }

  /**
   * Moon offset for a night-time hour. Like the real moon, it rises
   * in the east at sunset, peaks near midnight, and sets in the west
   * at sunrise — same X direction as the sun arc, just shifted in
   * time. The t-mapping wraps midnight: 20:00→0, 00:00→0.4, 06:00→1.
   * Earlier code (and the original spec) had it traverse west→east,
   * which placed the moon disc behind the camera at midnight.
   */
  #calcMoonPosition(hours) {
    let t;
    if (hours >= 20) t = (hours - 20) / 10;
    else if (hours < 6) t = (hours + 4) / 10;
    else t = 0;
    t = Math.max(0, Math.min(1, t));
    const angle = t * Math.PI;
    const elevation = Math.sin(angle);
    const A = TimeOfDay.#ARC;
    return new THREE.Vector3(
      Math.cos(angle) * A.X_SWING,
      A.Y_BASE + elevation * A.Y_SWING,
      A.Z_FORWARD,
    );
  }

  /**
   * Sun/moon direction for the current cycle position. Converts progress to a
   * synthetic clock, then reuses the day-arc (sun) or night-arc (moon) shape.
   * Only the *direction* varies; magnitude is locked so the shadow-camera
   * frustum (App.js #initLighting) stays valid across the whole arc. Returns a
   * fresh Vector3 the caller can lerp toward or copy from freely.
   */
  #calcOffset() {
    const hours = hoursFromProgress(this.progress);
    const off = this._mode === "day"
      ? this.#calcSunPosition(hours)
      : this.#calcMoonPosition(hours);
    const FIXED_MAG = this._mode === "day" ? 40 : 35;
    return off.normalize().multiplyScalar(FIXED_MAG);
  }

  // ── Cycle sampling + application ──────────────────────────────────────────
  /** Precompute a THREE.Color per keyframe colour field, plus the reusable
   *  `_live` palette (mutated in place each frame by #sampleCycle so the hot
   *  path allocates nothing). */
  #prepareCycle() {
    this._stopColors = CYCLE_STOPS.map((stop) => {
      const colors = {};
      for (const field of CYCLE_COLOR_FIELDS) {
        colors[field] = new THREE.Color(stop.palette[field]);
      }
      return colors;
    });
    this._live = {};
    for (const field of CYCLE_COLOR_FIELDS) this._live[field] = new THREE.Color();
    for (const field of CYCLE_SCALAR_FIELDS) this._live[field] = 0;
  }

  /** Interpolate every palette field into `_live` for the given progress,
   *  smoothstepping between the two bracketing keyframes (colours in RGB). */
  #sampleCycle(progress) {
    const stops = CYCLE_STOPS;
    let i = 0;
    while (i < stops.length - 2 && progress >= stops[i + 1].at) i++;
    const a = stops[i];
    const b = stops[i + 1];
    const span = Math.max(1e-6, b.at - a.at);
    const t = Math.min(1, Math.max(0, (progress - a.at) / span));
    const st = t * t * (3 - 2 * t); // smoothstep
    const ca = this._stopColors[i];
    const cb = this._stopColors[i + 1];
    for (const field of CYCLE_COLOR_FIELDS) {
      this._live[field].lerpColors(ca[field], cb[field], st);
    }
    for (const field of CYCLE_SCALAR_FIELDS) {
      this._live[field] = a.palette[field] + (b.palette[field] - a.palette[field]) * st;
    }
  }

  /** Push the current `_live` palette into every per-frame consumer. All cheap
   *  uniform / scalar / colour writes — no rebuilds. Water + distant islands
   *  ride the discrete day↔night flip instead (tick / reapply). */
  #applyContinuous() {
    const p = this._live;
    this.sun.color.copy(p.sunColor);
    this.sun.intensity = p.sunIntensity;
    this.rim.color.copy(p.rimColor);
    this.rim.intensity = p.rimIntensity;
    this.ambient.color.copy(p.ambientColor);
    this.ambient.intensity = p.ambientIntensity;
    this.hemi.color.copy(p.hemiSky);
    this.hemi.groundColor.copy(p.hemiGround);
    this.hemi.intensity = p.hemiIntensity;

    // Coloured-shadow tint (ShadowTint.js) — the world material's shadow ambient.
    shadowTintColor.value.copy(p.shadowTint);
    // Faked sun radiance for the world material (WorldLight) — sun colour scaled
    // from the PBR intensity into Bruno's ~1.0 range.
    sunRadiance.value
      .copy(p.sunColor)
      .multiplyScalar(Math.max(FAKE_SUN_FLOOR, p.sunIntensity * FAKE_SUN_SCALE));

    this.sky.material.uniforms.uTop.value.copy(p.skyTop);
    this.sky.material.uniforms.uMid.value.copy(p.skyMid);
    this.sky.material.uniforms.uHorizon.value.copy(p.skyHorizon);
    this.sky.material.uniforms.uGround.value.copy(p.skyGround);

    this.fog.color.copy(p.fogColor);
    this.fog.near = p.fogNear;
    this.fog.far = p.fogFar;
    // Drive the view-direction scene fog node (FogState) — its COLOUR comes from
    // the sky gradient automatically; only the range needs feeding per phase.
    fogNear.value = p.fogNear;
    fogFar.value = p.fogFar;

    if (this.grass) {
      this.grass.baseColor.copy(p.grassColor);
      this.grass.syncColor();
    }
    if (this.fireflies) {
      this.fireflies.material.uniforms.uIntensity.value = p.fireflyIntensity;
    }
    this.sunMesh?.setOpacity?.(p.sunMeshOpacity);

    this.fillLight.color.copy(p.fillColor);
    this.fillLight.intensity = p.fillIntensity;
    this.spotLight.intensity = p.spotlightIntensity;

    // Gate the moon by how visible the sun is — the moon only appears once the
    // sun has nearly set, so you never see a bright sun and a moon at the same
    // time (they're also on opposite sides of the sky now).
    const sunGate = Math.max(0, 1 - p.sunMeshOpacity * 2);
    const moonOpacity = p.moonOpacity * sunGate;
    this.moonMat.opacity = moonOpacity;
    this.moonGroup.visible = moonOpacity > 0.001;

    this.starMaterial.uniforms.uOpacity.value = p.starsOpacity;
    this.starGroup.visible = p.starsOpacity > 0.001;

    if (this.billboards) this.billboards.emissiveBoost = p.billboardEmissiveBoost;
  }
}

function playerGroupExists(g) {
  return !!g;
}
