import * as THREE from "three/webgpu";
import { AudioManager } from "./Audio/AudioManager.js";
import { Fireflies } from "./Effects/Fireflies.js";
import { Footprints } from "./Effects/Footprints.js";
import { GroundBreak } from "./Effects/GroundBreak.js";
import { Leaves } from "./Effects/Leaves.js";
import { LikeLights } from "./Effects/LikeLights.js";
import { PostFX } from "./Effects/PostFX.js";
import { Rain } from "./Effects/Rain.js";
import { Snow } from "./Effects/Snow.js";
import { Thunderstorm } from "./Effects/Thunderstorm.js";
import { Water } from "./Effects/Water.js";
import { WindLines } from "./Effects/WindLines.js";
import { Physics } from "./Physics/Physics.js";
import { Character } from "./Player/Character.js";
import { Player } from "./Player/Player.js";
import { PlayerCamera } from "./Player/PlayerCamera.js";
import { ActionPrompts } from "./Portfolio/ActionPrompts.js";
import { ContactBoard } from "./Portfolio/ContactBoard.js";
import { Experience } from "./Portfolio/Experience.js";
import { GuestbookTree } from "./Portfolio/GuestbookTree.js";
import { Interactables } from "./Portfolio/Interactables.js";
import { Interaction } from "./Portfolio/Interaction.js";
import { ProjectsHut } from "./Portfolio/ProjectsHut.js";
import { ResumeBook } from "./Portfolio/ResumeBook.js";
import { SkillSphere } from "./Portfolio/SkillSphere.js";
import {
  BLOCKERS,
  LAMPS,
  SECTIONS,
  WORLD_BOUNDS,
} from "./Portfolio/WorldMap.js";
import { Achievements } from "./Systems/Achievements.js";
import { ControlHints } from "./Systems/ControlHints.js";
import { DistanceGame } from "./Systems/DistanceGame.js";
import { LavaHazard } from "./Systems/LavaHazard.js";
import { SocialBackend } from "./Systems/SocialBackend.js";
import { ClickToMove } from "./Travel/ClickToMove.js";
import { IntroCinematic } from "./Travel/IntroCinematic.js";
import { Navmask } from "./Travel/Navmask.js";
import { Teleport } from "./Travel/Teleport.js";
import { TransitionFX } from "./Travel/TransitionFX.js";
import { AchievementPanel } from "./UI/AchievementPanel.js";
import { AchievementToast } from "./UI/AchievementToast.js";
import { Compass } from "./UI/Compass.js";
import { assertCoordRoundTrip } from "./UI/coords.js";
import { Discovery } from "./UI/Discovery.js";
import { MapOverlay } from "./UI/MapOverlay.js";
import { MapSnapshot } from "./UI/MapSnapshot.js";
import { MiniMap } from "./UI/MiniMap.js";
import { SocialHud } from "./UI/SocialHud.js";
import { Tutorial } from "./UI/Tutorial.js";
import { UIController } from "./UI/UIController.js";
import { Wasted } from "./UI/Wasted.js";
import { Debug } from "./Utils/Debug.js";
import { Loader } from "./Utils/Loader.js";
import { detectQuality } from "./Utils/Quality.js";
import { Sizes } from "./Utils/Sizes.js";
import { AnimatedProps } from "./World/AnimatedProps.js";
import { Bonfires } from "./World/Bonfires.js";
import { Environment } from "./World/Environment.js";
import { Flowers } from "./World/Flowers.js";
import { buildSceneFogNode, initFog } from "./World/FogState.js";
import { Foliage } from "./World/Foliage.js";
import { Grass } from "./World/Grass.js";
import { Lava } from "./World/Lava.js";
import { Lights } from "./World/Lights.js";
import { DUSK } from "./World/Palette.js";
import { Sun } from "./World/Sun.js";
import { TimeOfDay } from "./World/TimeOfDay.js";
import { WeatherDirector } from "./World/WeatherDirector.js";
import { Wind } from "./World/Wind.js";
import { World } from "./World/World.js";

/**
 * Core application: scene, renderer, camera, render loop, async asset boot.
 */
export class App extends EventTarget {
  // Per-tab counter of stalled WebGPU init attempts (sessionStorage). After two
  // stalls the renderer is rebuilt on WebGL2 (#initRenderer); a clean init
  // clears it so the next visit tries WebGPU again.
  static GPU_RETRY_KEY = "karan-portfolio:gpu-init-retry";

  constructor() {
    super();
    this.canvas = document.getElementById("canvas");
    this.sizes = new Sizes();
    this.debug = new Debug();
    this.clock = new THREE.Clock();
    this.loader = new Loader();
    this.quality = detectQuality();
    // Render-resolution ceiling from the quality tier (capable → Retina/2.0,
    // weak → 1.0). Set on Sizes BEFORE #initRenderer's first setPixelRatio; the
    // adaptive DPR controller then scales below it under load. Backend (WebGPU
    // vs WebGL2) is deliberately NOT a capability signal — a strong Mac with no
    // WebGPU runs WebGL2 fine, so we don't downgrade it for the backend alone.
    this.sizes.maxPixelRatio = this.quality.dprCap ?? 1.0;
    this.sizes.update();
    window.__quality = this.quality;

    this.loader.addEventListener("progress", (e) => {
      this.dispatchEvent(new CustomEvent("progress", { detail: e.detail }));
    });

    this.#initRenderer();
    this.#initScene();
    this.#initCamera();
    this.#initLighting();

    this.debug.setRenderer(this.renderer);

    this.physics = new Physics();
    this.world = new World(this.scene, this.loader);
    this.playerCamera = new PlayerCamera(this.camera, this.canvas);
    this.compass = new Compass({ playerCamera: this.playerCamera });
    this.player = null;
    this.skillSphere = null;
    this.colourGarden = null;
    this.discovery = null;

    // Global slow-motion (Colour Garden paint payoff). timeScale eases toward
    // _timeScaleTarget; while _slowMoLeft > 0 the sim runs on a scaled delta.
    this.timeScale = 1;
    this._timeScaleTarget = 1;
    this._slowMoLeft = 0;
    this.miniMap = null;
    this.mapOverlay = null;
    this.navmask = null;
    this.clickToMove = null;
    this.teleport = null;
    this.transitionFx = null;

    // Shared wind source — drives the grass field + wind lines today; future
    // leaves / water ripples read the same uniforms (GLSL) / nodes (TSL).
    this.wind = new Wind();
    // Grass is a v3 runtime TSL blade field driven by the Blender grass mask +
    // terrain heightfield — both only exist after world.loadAssets(), so it's
    // constructed in boot() (and wired into TimeOfDay) once the world is loaded.
    this.grass = null;
    this.bonfires = null;
    // Fireflies are a NIGHT effect and first load always opens on day (see
    // TimeOfDay), so they're constructed with the other deferred world systems
    // after spawn — invisible at launch anyway, and one less first-frame shader.
    this.fireflies = null;

    // Atmospheric effects — added during construction so they exist on first
    // frame; they don't depend on async loaded assets. All ported to TSL node
    // materials (B0-finish) so they render natively on the WebGPU backend.
    // Water (pools + river) is created during world.loadAssets so it can
    // register Nature exclusions before nature.load() scatters props. The
    // reference is grabbed in boot() once the world has loaded.
    this.water = null;
    this.rain = new Rain(this.scene, this.camera, {
      count: this.quality.rainCount,
      splashBudget: this.quality.rainSplashBudget,
    });
    // Don't rain ON the spawn — the first frames should be clear. Remember the
    // intended state (default on, unless the visitor disabled it before) and
    // force rain off WITHOUT persisting; ~5s after launch it switches on if it
    // was wanted. Thunderstorm.setActive() below reads this, so it stays calm
    // at spawn too. See the deferred re-enable in boot().
    this._rainWanted = this.rain.enabled;
    this.rain.enabled = false;
    this.rain.group.visible = false;
    // Automatic snow cycle: falling flakes + accumulation on every snow-aware
    // material, driven by the shared snowCoverage/snowFall uniforms. Independent
    // of the manual rain toggle and of time-of-day.
    this.snow = new Snow(this.scene, this.camera, {
      count: Math.round((this.quality.rainCount || 1200) * 3.84),
    });
    this.weather = new WeatherDirector({ fog: this.scene.fog });
    // Snow pacing. First-timers (and anyone who already caught snow) wait a full
    // day/night cycle so the first flakes read as a cinematic beat. But a visitor
    // who came before and left BEFORE snow ever showed gets a short delay this
    // time so they finally see it. snow-seen is stamped in the tick once snow is
    // actually visible.
    const visitedBefore =
      localStorage.getItem("karan-portfolio:visited") === "1";
    const snowSeen = localStorage.getItem("karan-portfolio:snow-seen") === "1";
    localStorage.setItem("karan-portfolio:visited", "1");
    this._snowSeenPersisted = snowSeen;
    // 12s (not 15) so snow is firmly active before the 15s rain timer fires —
    // otherwise rain would blip on for a frame before snow suppresses it.
    if (visitedBefore && !snowSeen) this.weather.setFirstDelay(12);
    this.windLines = new WindLines(this.scene, this.wind, {
      count: this.quality.windLineCount,
    });
    this.leaves = new Leaves(this.scene, this.wind, this.world.terrain, {
      count: this.quality.leafCount,
      maxSettled: this.quality.maxSettledLeaves,
      loader: this.loader,
    });
    // Leaves used to rain down the instant the world appeared. Hold them off the
    // spawn frame; the boot tail releases them ~8s in, after which the tick
    // gates them against snow (the two weather looks never overlap).
    this._leavesUnlocked = false;
    this.leaves.setActive(false);
    // Footprints — persistent flat decals dropped on each footstep. Cadence
    // is driven by AudioManager.onStep (set up after boot) so visual prints
    // and audio steps stay aligned. Path tile positions are plumbed in
    // post-boot once World.paths exists.
    this.footprints = new Footprints(this.scene, this.world.terrain, {
      loader: this.loader,
    });

    // PostFX wraps the renderer. Created here so resize() can wire to it.
    this.postfx = new PostFX(
      this.renderer,
      this.scene,
      this.camera,
      this.sizes,
      this.quality.postfx,
    );

    // Sky-derived image-based lighting. Generates a PMREM from the gradient
    // Sky so props get soft indirect light keyed to the world's own sky colours
    // (fixes the flat, "pasted-on" look). update() is called each tick and
    // rebuilds only when the sky colours actually move.
    this.environment = new Environment(
      this.renderer,
      this.scene,
      this.world.sky.material,
      { intensity: 0.35 },
    );

    this.audio = new AudioManager();
    // Rain's toggle button (built in its own constructor) plays a toggle
    // click when flipped — needs audio after construction, hence late-bind.
    if (this.rain) this.rain.audio = this.audio;

    // Thunderstorm — owns its own ⚡ button + flash overlay + message
    // element. Auto-strikes only fire while rain is enabled; the manual
    // button works at any time. setActive() is called below + on every
    // rain toggle so the auto-timer resumes/halts in lockstep.
    this.thunderstorm = new Thunderstorm(
      this.scene,
      this.camera,
      this.lights.ambient,
      this.audio,
    );
    this.thunderstorm.setActive(this.rain.enabled);
    // Wrap Rain.setEnabled so the auto-storm follows the toggle without
    // needing Rain to know about Thunderstorm.
    const _setRainEnabled = this.rain.setEnabled.bind(this.rain);
    this.rain.setEnabled = (value) => {
      _setRainEnabled(value);
      this.thunderstorm.setActive(value);
    };

    // Day / night cycle. Built now so it can drive lights + sky immediately
    // — billboards / signs are still loading at this point, so they are
    // wired into TimeOfDay after boot() completes the world load.
    this.timeOfDay = new TimeOfDay({
      scene: this.scene,
      fog: this.scene.fog,
      sun: this.lights.sun,
      rim: this.lights.rim,
      ambient: this.lights.ambient,
      hemi: this.lights.hemi,
      sky: this.world.sky,
      sunMesh: this.sun,
      grass: this.grass,
      fireflies: this.fireflies,
      // water is wired in boot() once world.loadAssets has created it.
      water: null,
      playerGroup: null, // wired after player loads in boot()
      character: null, // wired after player loads in boot()
    });

    // View-direction scene fog (FogState): overrides the flat THREE.Fog so
    // distant geometry dissolves into the actual sky-gradient band behind it.
    // initFog must run BEFORE the world materials are built (in boot → world
    // load), because the faked-light world material reads the fog colour node at
    // build time. THREE.Fog is kept on the scene only as a typed reference for
    // code that reads scene.fog; the node is what renders.
    initFog(this.world.sky.material.uniforms);
    this.scene.fogNode = buildSceneFogNode();

    // Achievements — persistent counter system + toast + side panel. Built
    // here so all modules already exist (Rain, Thunderstorm, TimeOfDay,
    // Footprints) and can pick up a back-reference for their triggers.
    this.achievements = new Achievements();
    this.achievementToast = new AchievementToast();
    this.achievementPanel = new AchievementPanel({
      achievements: this.achievements,
      audio: this.audio,
    });
    this.achievements.onUnlock((a) => {
      // Toast + chime only. The old camera-punch / slow-mo "felt" beat moved
      // the whole screen on unlock, which read as a jarring shake — dropped so
      // an achievement is a clean notification, not a screen event.
      this.achievementToast.show(a);
      this.audio?.playAchievement?.(a.rarity || "common");
    });
    // Wrap Rain.setEnabled one more time so the on-edge fires onToggleRain.
    // The thunderstorm wrap above already chained an outer wrapper; this
    // adds a third layer that still ends up calling the original setEnabled
    // followed by thunderstorm.setActive followed by the achievement hook.
    if (this.rain) {
      const _prevSetEnabled = this.rain.setEnabled.bind(this.rain);
      this.rain.setEnabled = (value) => {
        const wasOff = !this.rain.enabled;
        _prevSetEnabled(value);
        if (value && wasOff) this.achievements?.onToggleRain?.();
      };
    }
    if (this.timeOfDay) this.timeOfDay.achievements = this.achievements;
    if (this.thunderstorm) this.thunderstorm.achievements = this.achievements;
    if (this.footprints) this.footprints.achievements = this.achievements;

    this.#bindResize();
    this.#bindTimeOfDayToggle();

    // Tab-hidden frame throttle — when the tab is backgrounded, drop to
    // 1/6 the normal cadence (browsers already throttle rAF to ~1 Hz when
    // hidden anyway, but this saves CPU+GPU on machines where rAF still
    // ticks). Pairs with the audio-on-blur pause already in place; the
    // visible state of the tab is the single source of truth.
    this._backgroundMode = false;
    this._bgFrame = 0;
    this._fixedAccumulator = this.quality.physicsStep ?? 1 / 60;
    this._lastPlayerSample = null;
    // Render interpolation between fixed physics substeps. The sim advances in
    // fixed 1/60 increments but frames arrive at the display's cadence (often
    // not a multiple of 60, e.g. 120Hz ProMotion, or an unstable 45fps), so
    // some frames run 0 substeps and others run 1–2. Rendering the raw latest
    // body position then judders against the smoothly-lerped camera. We snapshot
    // the body's pre/post-step position each substep and, after the loop, render
    // the character at lerp(prev, curr, accumulator/dt) — the standard "fix your
    // timestep" remainder. Costs ~half a step of visual latency (~8ms @60Hz),
    // imperceptible for walking, in exchange for a stutter-free character.
    this._physPrevPos = new THREE.Vector3();
    this._physCurrPos = new THREE.Vector3();
    this._physInterpReady = false;
    // Adaptive DPR — base is the original cap set in Sizes (typically 1.0);
    // factor scales between 1.0 and quality.dprFloor under load. Reapplied
    // only when factor changes (setPixelRatio reallocates the framebuffer).
    this._dprBase = this.sizes.pixelRatio;
    this._dprFactor = 1.0;
    this._dprFrameAccum = 0;
    this._dprFrameCount = 0;
    this._dprFastWindows = 0;
    // Windows to wait after any pixelRatio change before the next one may
    // fire. setPixelRatio + postfx.resize each reallocate GPU framebuffers
    // (a one-frame stall), so back-to-back adjustments read as stutter when
    // the player walks in/out of a heavy view. The cooldown + the stickier
    // recovery below keep adjustments rare instead of oscillating.
    this._dprCooldown = 0;
    // Adaptive feature shedding — the rung BELOW the DPR floor. When a machine
    // is still over budget at the lowest resolution we start turning expensive
    // systems off (resolution is the cheapest-looking lever, so it goes first).
    // 0 = full, 1 = grass field hidden, 2 = + foliage canopy hidden.
    // Recovery is conservative + LIFO: features come back only with real
    // headroom and only once DPR is already maxed, so we don't flap a feature
    // on/off. `_perfManual` latches once the debug key (P) is used so the auto
    // controller stops fighting a hand-set level during verification.
    this._perfShedLevel = 0;
    this._perfShedMax = 2;
    this._perfBadWindows = 0;
    this._perfGoodWindows = 0;
    this._perfManual = false;
    document.addEventListener("visibilitychange", () => {
      this._backgroundMode = document.hidden;
      this._bgFrame = 0;
    });
  }

  /** Wires the #tod-toggle button. The world runs a continuous 2-minute cycle
   *  (dawn→day→dusk→night); clicking jumps the cycle FORWARD to the next phase
   *  and the auto-advance carries on from there. The icon tracks the live
   *  phase (updated from #tick), so it also changes on its own as time passes. */
  #bindTimeOfDayToggle() {
    const btn = document.getElementById("tod-toggle");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      this.audio?.playToggle();
      // Shader variants for the other phases are only warm once the deferred
      // prewarm resolves. If the user clicks before then, await it so jumping
      // phases doesn't JIT-compile materials on screen (the night/morning hitch).
      if (!this._shaderReady && this.shaderPrewarmPromise) {
        await this.shaderPrewarmPromise;
      }
      this.timeOfDay.cyclePhase();
      this.#syncTimeOfDayButton();
    });
    this.#syncTimeOfDayButton();
  }

  // Per-phase button icon (feather-style) + accent colour data-attr.
  static #TOD_ICONS = {
    day: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    night:
      '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/></svg>',
    dawn: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 18a5 5 0 0 0-10 0"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="4.22" y1="10.22" x2="5.64" y2="11.64"/><line x1="1" y1="18" x2="3" y2="18"/><line x1="21" y1="18" x2="23" y2="18"/><line x1="18.36" y1="11.64" x2="19.78" y2="10.22"/><line x1="23" y1="22" x2="1" y2="22"/><polyline points="8 6 12 2 16 6"/></svg>',
    dusk: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 18a5 5 0 0 0-10 0"/><line x1="12" y1="9" x2="12" y2="2"/><line x1="4.22" y1="10.22" x2="5.64" y2="11.64"/><line x1="1" y1="18" x2="3" y2="18"/><line x1="21" y1="18" x2="23" y2="18"/><line x1="18.36" y1="11.64" x2="19.78" y2="10.22"/><line x1="23" y1="22" x2="1" y2="22"/><polyline points="16 5 12 9 8 5"/></svg>',
  };

  static #TOD_LABELS = {
    dawn: "Dawn — click for day",
    day: "Day — click for dusk",
    dusk: "Dusk — click for night",
    night: "Night — click for dawn",
  };

  #syncTimeOfDayButton() {
    const btn = document.getElementById("tod-toggle");
    if (!btn) return;
    const phase = this.timeOfDay.phase;
    btn.dataset.phase = phase;
    // Body data-attr (day|night) still themes the WASD HUD + other overlays;
    // dawn reads as day, dusk as night for that coarse light/dark split.
    document.body.dataset.tod = this.timeOfDay.mode;
    btn.innerHTML = App.#TOD_ICONS[phase] ?? App.#TOD_ICONS.day;
    const label = App.#TOD_LABELS[phase] ?? "Change time of day";
    btn.setAttribute("aria-label", label);
    btn.setAttribute("title", label);
  }

  /**
   * Background shader warm. compileAsync compiles pipelines off the main thread
   * (KHR_parallel_shader_compile on WebGL2, async pipeline creation on WebGPU),
   * so firing it un-awaited after the reveal warms the scene's programs while
   * the intro cinematic plays — shrinking the per-frame lazy-compile hitches
   * without ever blocking the loader. Best-effort: a failure just means the
   * first frames pay the lazy compile, which the cinematic already tolerates.
   *
   * NOTE: deliberately NOT awaited in boot(). An awaited / synchronous compile
   * is what froze the tab at "stuck at 90%" on the WebGL2 fallback — see boot().
   */
  async #warmShadersInBackground() {
    if (!this.renderer || !this.scene || !this.camera) return;
    if (typeof this.renderer.compileAsync !== "function") return; // r152+
    await this.renderer.compileAsync(this.scene, this.camera);
  }

  /**
   * Defer the one-time top-down map snapshot off the reveal path. It renders
   * ~the whole scene, so on a cold cache it triggers a synchronous compile that
   * would re-freeze the loader if run inline. An idle callback lets the reveal
   * and the cinematic's opening beats happen first.
   */
  #scheduleMapSnapshot() {
    const run = () => {
      this.#captureMapSnapshot();
    };
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback(run, { timeout: 3000 });
    } else {
      setTimeout(run, 1500);
    }
  }

  /** Loads characters / models; resolves to a summary the loader UI can use. */
  async boot() {
    const bootStart = performance.now();
    // Boot-phase timing — gated behind ?timing=1 (pairs with the finer-grained
    // breakdown inside GlbV3World.load). Shows how much of total boot is the
    // world parse vs renderer/physics init vs character vs portfolio wiring.
    // Stashed INCREMENTALLY on window.__bootTiming (initialised here, before the
    // first await) so it survives a partial/failed boot — the last entry shows
    // exactly which phase was reached before it stopped. Read with `__bootTiming`
    // in the console. `undefined` there means a stale bundle (this code never
    // ran); `[]` means boot died before even renderer.init finished.
    const timing = window.location?.search?.includes("timing");
    let _tBoot = bootStart;
    window.__bootTiming = [];
    const bootMark = (label) => {
      const now = performance.now();
      const ms = now - _tBoot;
      _tBoot = now;
      window.__bootTiming.push(`${ms.toFixed(1)}ms  ${label}`);
      if (timing) console.log(`[boot] ${ms.toFixed(1)}ms  ${label}`);
    };
    // User-facing phase labels (distinct from the dev-only bootMark timings) so
    // the loading screen shows TRUTHFUL progress instead of a random rotation —
    // the long opaque shader-compile phase in particular has to read as
    // "working", not "stuck at 90%". main.js listens for 'phase' events.
    const phase = (label) =>
      this.dispatchEvent(new CustomEvent("phase", { detail: { label } }));
    phase("Starting the 3D engine…");
    // WebGPURenderer is constructed synchronously but must finish its async
    // device/adapter handshake before any render/compute runs. That handshake
    // can stall for tens of seconds under GPU-process contention, so guard it
    // with a timeout + auto-reload + WebGL2 fallback instead of hanging at 5%.
    // Kick Rapier's WASM boot off NOW so its ~3.7s compile hides under the
    // renderer handshake below and the world parse further down. We only block
    // on it at the world's collider seam (GlbV3World awaits physics.whenReady).
    const physicsPromise = this.physics.init();
    physicsPromise.catch(() => {}); // real error still surfaces at the await below

    await this.#initRendererWithFallback();
    // WebGPURenderer silently falls back to WebGL2 where WebGPU is missing; log
    // which backend we got (the slow first-visit compile differs between them).
    this._isWebGPU = this.renderer.backend?.isWebGPUBackend === true;
    console.log(
      `[App] render backend: ${this._isWebGPU ? "WebGPU" : "WebGL2 fallback"}`,
    );
    // KTX2 format detection needs the live backend (hasFeature) — safe only
    // after init(), so the transcoder picks the right compressed-format path.
    this.loader.attachRenderer(this.renderer);
    bootMark("renderer.init (physics booting underneath)");
    // WebGPU runs the TSL shaders natively; the WebGL2 fallback (no dedicated
    // GPU) must compile hundreds of variants and is the slow first-visit path —
    // tell the visitor we're adapting rather than leaving them guessing.
    phase(
      this._isWebGPU
        ? "Loading the world…"
        : "Optimizing graphics for your device…",
    );

    // Character GLB parse (~5s) — independent of world + physics. Start it now
    // so it runs UNDER the world parse. Needs only the loader (renderer already
    // attached for KTX2). Attached to the Player after the world resolves.
    const character = new Character(this.loader);
    const characterPromise = character.load();
    characterPromise.catch(() => {}); // real error still surfaces at the await below

    // Phase 1 of World v2: the heightfield is now baked from world.glb so
    // physics.addStaticGround MUST run after world.loadAssets — the terrain
    // object's heightAt/size/segments only get populated by GlbWorld.bake().
    // The Player needs the world.terrain reference for spawn-Y sampling but
    // can be constructed lazily once the world has loaded; we still kick its
    // character GLBs off in parallel with the world parse so total boot time
    // doesn't regress.
    const worldLoadPromise = this.world.loadAssets(this.loader, this.physics, {
      audio: this.audio,
      playerUniforms: this.grass?.playerUniforms ?? null,
      wind: this.wind,
    });

    const worldResult = await worldLoadPromise;
    bootMark("world.loadAssets (physics + character overlapped)");
    phase("Shaping the island…");
    await physicsPromise; // ensure fully ready before addStaticGround (usually already resolved)
    this.physics.addStaticGround(this.world.terrain);

    // Grass — v3 runtime TSL blade field. Built now that the terrain
    // heightfield + Blender grass mask exist. Blade count scales with the
    // quality tier (√multiplier keeps the per-blade area roughly constant).
    // Base 280 → 280² ≈ 78k blades at high tier (matched to Bruno's count).
    // Density is TIER-only: backend (WebGPU vs WebGL2) is not a capability
    // signal, so grass isn't thinned just for being on WebGL2. The real
    // per-blade cost (our 3-triangle arch vs Bruno's 1-triangle billboard) is
    // a separate lever to tackle if full density needs to run lighter.
    const grassSub = Math.max(
      64,
      Math.round(340 * Math.sqrt(this.quality.grassMultiplier ?? 1)),
    );
    this.grass = new Grass(
      this.scene,
      this.world.terrain,
      this.wind,
      this.world.glb.grassMask,
      {
        subdivisions: grassSub,
        gridBounds: this.world.grassGrid?.bounds ?? 96,
      },
    );
    // Wire grass into the day/night cycle (it was null at TimeOfDay
    // construction) and snap it to the current mode's grass tint via reapply().
    this.timeOfDay.grass = this.grass;
    this.timeOfDay.reapply();

    this.player = new Player(
      this.scene,
      this.playerCamera,
      this.world.terrain,
      this.loader,
      this.physics,
    );
    this.playerCamera.follow(this.player.position, true);

    bootMark("grass + player");
    phase("Planting the world…");
    // Character GLB was loading since just after renderer.init — by now it has
    // almost always resolved, so this await is typically free.
    const characterResult = await characterPromise;
    this.player.attachCharacter(character, characterResult);
    bootMark("character attach");
    phase("Waking the character…");

    // Intro cinematic — the first-arrival fall-from-sky sequence. GroundBreak
    // owns the procedural impact FX; both run as a pre-gameplay layer. main.js
    // drives intro.play() off the "Enter Karan's World" button tap. onLanded
    // flashes the compass cardinal labels once the character touches down.
    this.groundBreak = new GroundBreak(this.scene);
    this.intro = new IntroCinematic({
      player: this.player,
      playerCamera: this.playerCamera,
      terrain: this.world.terrain,
      groundBreak: this.groundBreak,
      audio: this.audio,
      onLanded: () => this.compass?.revealCardinals?.(),
    });

    // Water — v3 runtime TSL surface covering the Blender-carved basins (ponds /
    // river) AND the ocean ring beyond the island. Built here (like grass) now
    // that the terrain heightfield exists; its depth/visibility derive from it.
    // Hook it into TimeOfDay (day/night tint) and AudioManager (wade splashes).
    this.water = new Water(this.scene, this.world.terrain, {
      highDetail: this.quality.waterHighDetail !== false,
    });
    this.world.water = this.water;
    this.timeOfDay.water = this.water;
    this.timeOfDay.reapply();
    this.water.audio = this.audio;
    this.water.setPhysics(this.physics);

    // Foliage — tree canopies + bushes grown as Bruno-style SDF leaf clouds.
    // Birch + cherry leaves come from their baked treeLeaves ref empties; OAK has
    // a solid low-poly green canopy mesh instead, so GlbV3World samples leaf
    // anchors in its form, deletes the green mesh, and emits them as the
    // `treeCanopy` group (species 'oak'). One cloud per (system, species) with a
    // two-tone palette: birch summer-green, cherry pink-blossom, oak green,
    // bushes yellow-green (user-chosen).
    const FOLIAGE_PALETTE = {
      birch: { colorA: "#4c7a2a", colorB: "#9ec25a" }, // summer green, shaded → lit
      cherry: { colorA: "#e0556a", colorB: "#ff9990" }, // blossom pink
      oak: { colorA: "#3f6b22", colorB: "#7ba23e" }, // natural oak green
      bushes: { colorA: "#9aa02f", colorB: "#d8cf3b" }, // yellow-green
    };
    const DEFAULT_FOLIAGE_COLORS = { colorA: "#4c7a2a", colorB: "#9ec25a" };
    const [foliageGroups, foliageSDF] = await Promise.all([
      this.world.glb.loadFoliageGroups(),
      this.loader
        .loadTexture("/textures/foliage/foliageSDF.png", {
          ktx2Url: "/textures/foliage/foliageSDF.ktx2",
        })
        .then((tex) => {
          tex.minFilter = THREE.NearestFilter;
          tex.magFilter = THREE.NearestFilter;
          tex.generateMipmaps = false;
          tex.wrapS = THREE.ClampToEdgeWrapping;
          tex.wrapT = THREE.ClampToEdgeWrapping;
          tex.colorSpace = THREE.NoColorSpace;
          tex.needsUpdate = true;
          return tex;
        })
        .catch(() => null),
    ]);
    const foliageClouds = [];
    for (const { system, groups } of foliageGroups) {
      for (const [species, refs] of groups) {
        const pal =
          FOLIAGE_PALETTE[species] ??
          FOLIAGE_PALETTE[system] ??
          DEFAULT_FOLIAGE_COLORS;
        foliageClouds.push({ key: `${system}:${species}`, refs, ...pal });
      }
    }
    if (foliageSDF && foliageClouds.length > 0) {
      this.foliage = new Foliage(
        this.scene,
        this.wind,
        foliageSDF,
        foliageClouds,
        { shell: this.quality.foliageShell !== false },
      );
      this.foliage.setSunDirection(this.timeOfDay.sunOffset);
      this.world.foliage = this.foliage;
    }

    // Flowers — authored flower clumps as wind-swaying, player-parting fields
    // (walk-through, no collider; soft-physics like the foliage). Built from the
    // groups GlbV3World collected during load (needs the shared Wind).
    if (this.world.glb?.flowerGroups?.length) {
      this.flowers = new Flowers(
        this.scene,
        this.wind,
        this.world.glb.flowerGroups,
      );
      this.world.flowers = this.flowers;
    }

    // The point-light RIG is built NOW (not deferred) even though its lamps sit
    // away from spawn: it adds PointLights to the scene, and adding lights later
    // changes the shader light-count → every lit material (incl. the character)
    // recompiles → a one-frame "character flickers invisible" pop. Built here at
    // intensity 0 (no visual cost, no asset load) the count is final before the
    // character first compiles behind the loader. The HEAVY visuals (bonfire
    // meshes, lava textures, animals) still defer — they add no lights.
    const v3lightRefs = this.world?.glb?.refs;
    if (v3lightRefs) this.worldLights = new Lights(this.scene, v3lightRefs);

    // Remaining Phase F (bonfire visuals, lava glow + hazard, animated props)
    // sits away from spawn and loads assets, so it's deferred to after launch
    // in #scheduleDeferredWorldSystems(); the tick null-guards every consumer.

    // Phase 1 of the World v2 swap: DistantIslands has been removed. The
    // Blender-authored world.glb will eventually provide horizon mountain
    // bands (already authored in Phase 12) so a procedural islands ring is no
    // longer needed. DistanceGame gets a stub islands provider — Phase 7 will
    // wire it to refViewpoint_* refs.
    this.distantIslands = { getIslands: () => [] };

    // Street lights are gone — all lamps/posts come from the Blender world
    // (poleLights GLB; point lights wired from refPoleLight_* in a later phase).
    // The v2 StreetLights system placed duplicate lamps + phantom colliders at
    // hardcoded cardinal coords, so it was removed entirely.

    // Distance-guess mini-game wired against the islands above. Constructed
    // before the player is loaded — its update() is a no-op until the
    // player position starts flowing into the tick loop.
    this.distanceGame = new DistanceGame({
      scene: this.scene,
      camera: this.camera,
      playerCamera: this.playerCamera,
      islands: this.distantIslands,
      achievements: this.achievements,
      audio: this.audio,
    });

    // Wire footprints: path positions for surface-guard, and the audio step
    // callback so prints drop at the exact moment a step would sound. Read
    // the player's world yaw from group.rotation.y at step time.
    this.footprints.setPaths({
      pathPositions:
        this.world.paths?.getTilePositions() ?? new Float32Array(0),
      pathCount: this.world.paths?.getTileCount() ?? 0,
      pathRadius: 1.4,
    });
    this.audio.onStep = (odd) => {
      // Only grass gets a print — `_printable` is set each tick from the same
      // surface result the footstep AUDIO uses, so prints never land in
      // water/ponds/river, on bridge decks, or on stone slabs/paths.
      if (!this._printable) return;
      this.footprints.onStep(
        this.player.position,
        this.player.group.rotation.y,
        !odd,
        this._snowPrint,
      );
    };
    // Cache path arrays once for #surfaceAt() — picking grass/stone/sand
    // per-frame for footstep audio + landing.
    this._pathPositions =
      this.world.paths?.getTilePositions() ?? new Float32Array(0);
    this._pathCount = this.world.paths?.getTileCount() ?? 0;
    this._pathRadius2 = 1.4 * 1.4;

    // Grass disabled — see ctor. Skipping the load() call leaves no tufts
    // in the scene. The blocks below remain so re-enable is a one-shot
    // uncomment.
    // const treePositions = (this.world.nature?.pushSpots ?? [])
    //   .filter((s) => s.type === 'tree')
    //   .map((s) => ({ x: s.position.x, z: s.position.z }));
    // await this.grass.load({
    //   pathPositions: this.world.paths?.getTilePositions() ?? new Float32Array(0),
    //   pathCount: this.world.paths?.getTileCount() ?? 0,
    //   pathRadius: 1.4,
    //   treePositions,
    //   exclusionCircles: INTERACTABLE_PROP_EXCLUSIONS,
    //   multiplier: this.quality.grassMultiplier,
    // });
    this.skillSphere = new SkillSphere({
      scene: this.scene,
      camera: this.camera,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      refs: this.world.glb.refs,
      audio: this.audio,
      achievements: this.achievements,
      timeOfDay: this.timeOfDay,
    });

    this.projectsHut = new ProjectsHut({
      scene: this.scene,
      camera: this.camera,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      refs: this.world.glb.refs,
      physics: this.physics,
      postfx: this.postfx,
      audio: this.audio,
      achievements: this.achievements,
    });

    this.contactBoard = new ContactBoard({
      scene: this.scene,
      camera: this.camera,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      audio: this.audio,
      achievements: this.achievements,
      timeOfDay: this.timeOfDay,
      postfx: this.postfx,
    });

    // Colour Garden — Blender-authored paint-throw toy loaded from its own GLB
    // (kept out of the world prop-merge so each statue stays paintable). Awaited
    // so its static colliders register before gameplay; the GLB is tiny.
    const { ColourGarden } = await import("./Portfolio/ColourGarden.js");
    this.colourGarden = new ColourGarden({
      scene: this.scene,
      physics: this.physics,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      audio: this.audio,
      app: this,
      loader: this.loader,
      timeOfDay: this.timeOfDay,
      achievements: this.achievements,
    });
    await this.colourGarden.load();

    // Career Ascent — runtime holo text + interaction for the 5 bridge stations
    // (geometry ships in experience.glb; this adds the readable/interactive layer).
    this.experience = new Experience({
      scene: this.scene,
      refs: this.world.glb.refs,
      audio: this.audio,
    });

    // Floating magical resume book — the new home for the resume (replaces the
    // old E-lectern flat panel). Placed in the NW quadrant; hovers, glows and
    // throws a light-shaft beacon so it reads as a "go here" attraction.
    this.resumeBook = new ResumeBook({
      scene: this.scene,
      terrain: this.world.terrain,
      physics: this.physics,
      x: -22,
      z: -20,
    });

    // ── Social backend: persisted likes / whispers / visitor count ──────────
    // Talks to the /api serverless functions (Upstash Redis); credentials live
    // server-side, never in this bundle. loadState() fires un-awaited so a slow
    // or unconfigured backend never delays the reveal — consumers react via
    // onChange and stay hidden until real data arrives.
    this.social = new SocialBackend();
    this.likeLights = new LikeLights(this.scene);
    this.social.onChange(() => this.likeLights.setCount(this.social.likes));
    this.social.loadState();
    this.socialHud = new SocialHud({
      social: this.social,
      likeLights: this.likeLights,
      player: this.player,
      audio: this.audio,
      controller: this.player.controller,
    });
    this.socialHud.start();

    // The Guestbook Tree — land-based note landmark (north of spawn). Its
    // beacon/light are built now (light count final before first compile); the
    // tree GLB loads un-awaited so it pops in just after spawn like the football.
    this.guestbookTree = new GuestbookTree({
      scene: this.scene,
      camera: this.camera,
      playerCamera: this.playerCamera,
      player: this.player,
      controller: this.player.controller,
      terrain: this.world.terrain,
      physics: this.physics,
      audio: this.audio,
      social: this.social,
      loader: this.loader,
      wind: this.wind,
      timeOfDay: this.timeOfDay,
      x: -2,
      z: 18,
    });
    this.guestbookTree
      .load()
      .catch((err) => console.warn("[App] guestbook tree load failed:", err));

    this.interaction = new Interaction({
      scene: this.scene,
      camera: this.camera,
      playerCamera: this.playerCamera,
      player: this.player,
      controller: this.player.controller,
      billboards: this.world.billboards,
      signs: this.world.signs,
      resumeBook: this.resumeBook,
      skillSphere: this.skillSphere,
      projectsHut: this.projectsHut,
      contactBoard: this.contactBoard,
      experience: this.experience,
      audio: this.audio,
      timeOfDay: this.timeOfDay,
      achievements: this.achievements,
    });

    this.actionPrompts = new ActionPrompts({
      player: this.player,
      controller: this.player.controller,
      audio: this.audio,
      playerCamera: this.playerCamera,
      billboardInteraction: this.interaction,
      achievements: this.achievements,
    });
    // Back-reference so Interaction can defer to ActionPrompts when both
    // would show a prompt at the same spot (e.g. Dance tile vs Contact).
    this.interaction.actionPrompts = this.actionPrompts;
    // Pre-populate push spots from the loaded world.
    this.actionPrompts.discoverPushSpots(this.world);

    this.interactables = new Interactables(
      this.scene,
      this.loader,
      this.physics,
      this.actionPrompts,
      this.world.terrain,
    );
    // The football is never visible at spawn (it sits out in a field), so its
    // GLB shouldn't compete with the world's assets during the critical load.
    // Defer the load to an idle callback after launch; it self-registers its
    // kick trigger once it settles. Fire-and-forget — never blocks boot.
    const loadInteractables = () =>
      this.interactables
        .load()
        // Warm the football's pipeline off-thread once it's in the scene, so it
        // doesn't compile the first time the player turns to look at it.
        .then(() => this.#warmShadersInBackground())
        .catch((err) => console.warn("[Interactables] load failed:", err));
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback(loadInteractables, { timeout: 4000 });
    } else {
      setTimeout(loadInteractables, 2000);
    }

    // UI redesign controller — owns desktop layout (top-left + bottom-left
    // stacks, bottom-right controls panel) and, on touch devices, the
    // mobile joystick + interact pill + action grid. Constructed here so
    // all module-owned buttons (audio/rain/wind/leaves/lightning) already
    // exist in the DOM and can be re-parented into the new containers.
    this.ui = new UIController({
      audio: this.audio,
      rain: this.rain,
      windLines: this.windLines,
      leaves: this.leaves,
      thunderstorm: this.thunderstorm,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      actionPrompts: this.actionPrompts,
      interaction: this.interaction,
    });

    this.#initMapSystems();

    // First-visit tutorial coachmarks. Constructed eagerly so main.js can
    // call .start() at the right moment (after the welcome overlay clears
    // and the controller is unpaused). No-ops on repeat visits via the
    // localStorage flag inside Tutorial.
    this.tutorial = new Tutorial({
      controller: this.player.controller,
    });

    // Contextual control nudges (Shift-to-run after ~11s walking, Space-to-jump
    // after ~15s) for players who haven't found them. Desktop-only, self-gated
    // by localStorage (twice ever / once per session / never once used).
    this.controlHints = new ControlHints();

    // Now that Signs + Billboards exist, wire the player ref so the
    // character spotlight / fill light can follow.
    this.timeOfDay.signs = this.world.signs;
    this.timeOfDay.billboards = this.world.billboards;
    this.timeOfDay.playerGroup = this.player.group;
    this.timeOfDay.character = this.player.character;
    // Re-apply current mode so freshly-loaded billboard boost picks up
    // the right intensity (TimeOfDay was built before they existed).
    this.timeOfDay.reapply();

    // Sync the current toggle-button icon to the auto-detected mode.
    this.#syncTimeOfDayButton();

    // Reveal is NOT gated on shader compilation. A synchronous compile freezes
    // the tab — on the WebGL2 fallback the whole-scene compile blocks the main
    // thread for many seconds (the "stuck at 90%, can't interact" report), and
    // even a cold WebGPU first frame stalls. So we start the loop and let the
    // world reveal behind the moving intro cinematic, where pipelines compile
    // across frames and the camera motion masks the brief hitches — instead of
    // a frozen loading bar. boot() now resolves as soon as the world is built.
    this._shaderReady = true;

    bootMark("water + foliage + portfolio + map wiring");
    phase("Warming up the lights…");

    // setAnimationLoop self-repeats and drives the WebGPU frame; #tick no
    // longer re-schedules itself via requestAnimationFrame.
    this.renderer.setAnimationLoop(this.#tick);

    // The loop is now live but the loading screen still covers the canvas.
    // Hold the loading screen while the cold-cache pipelines compile BEHIND it,
    // so the reveal isn't a visible 1–2s glitch. Two things warm CONCURRENTLY:
    //   (a) #waitFrames advances the live loop, compiling the scene/post-FX pass
    //       as real frames render;
    //   (b) #warmShadersInBackground() runs compileAsync off-thread.
    // Both are kicked off together and awaited under ONE cap (was two sequential
    // holds, up to 6.5s). The render loop is already live here, so (a) and (b)
    // already coexisted — this only drops the sequential pre-wait. Budget is
    // tier-gated: strong GPUs hold longer for a fully hitch-free reveal; weak
    // GPUs (low tier, or the WebGL2 fallback which lacks a parallel-compile path)
    // reveal sooner and pay any remainder lazily, the cinematic's motion masking
    // the brief hitch. Deferred away-from-spawn systems re-warm themselves when
    // added (see #scheduleDeferredWorldSystems).
    phase("Preparing graphics — almost ready…");
    const prewarm = this._isWebGPU
      ? this.quality.prewarm
      : { frames: 3, capMs: 2000 };
    this.shaderPrewarmPromise = this.#warmShadersInBackground().catch((err) =>
      console.warn("[App] background shader warm failed:", err),
    );
    await Promise.race([
      Promise.all([
        this.#waitFrames(prewarm.frames),
        this.shaderPrewarmPromise,
      ]),
      new Promise((r) => setTimeout(r, prewarm.capMs)),
    ]);

    this.#scheduleDeferredAnimationWarmup();
    // The one-time top-down map render compiles ~the whole scene synchronously,
    // so running it inline would re-freeze the loader. Defer it behind the
    // cinematic (idle callback); the map overlay tolerates a not-yet-ready
    // snapshot for the first second or two.
    this.#scheduleMapSnapshot();
    // Distant world systems (lava + hazard, bonfires, animals/air dancers,
    // world point lights) all sit away from the spawn pad — stream them in
    // after the first frame so they don't delay the reveal. Tick guards each.
    this.#scheduleDeferredWorldSystems();
    if (this.debug?.enabled) {
      console.log(
        `[App] boot resolved in ${Math.round(performance.now() - bootStart)} ms`,
      );
    }
    const _bootTotal = performance.now() - bootStart;
    window.__bootTiming.push(
      `=== total ${_bootTotal.toFixed(0)}ms (backend: ${this._isWebGPU ? "WebGPU" : "WebGL2 fallback"}) ===`,
    );
    if (timing) console.log(`[boot] DONE total ${_bootTotal.toFixed(0)}ms`);
    return { character: characterResult, world: worldResult };
  }

  /**
   * Construct the away-from-spawn world systems after launch (lava + hazard,
   * bonfires, animated animals/dancers, world point lights). Extracted from the
   * old inline "Phase F" so the reveal isn't blocked on their meshes/textures/
   * light-count shader recompiles. Idempotent-ish: only runs once. Every
   * consumer null-guards these, so they simply appear a beat after spawn.
   */
  #scheduleDeferredWorldSystems() {
    const run = async () => {
      const v3refs = this.world?.glb?.refs;
      if (!v3refs || this.lava || this.bonfires) return; // already done / no refs
      try {
        // worldLights is built at boot (not here) — adding lights post-reveal
        // recompiles every lit material → character flicker. See boot().
        this.bonfires = await new Bonfires(
          this.scene,
          v3refs,
          this.wind,
        ).load();
        this.lava = new Lava(this.scene, this.wind, v3refs, this.physics);
        // Hazard reads player.character lazily at sink time, so wiring it now is fine.
        if (this.player) {
          this.wasted = new Wasted();
          this.lavaHazard = new LavaHazard({
            player: this.player,
            lava: this.lava,
            wasted: this.wasted,
            achievements: this.achievements,
          });
        }
        this.animatedProps = new AnimatedProps(
          this.scene,
          this.world.terrain,
          v3refs,
          this.physics,
        );
        // Fireflies are a night-only effect — build them now (post-spawn) and
        // wire them into the day/night driver so they light up when night
        // arrives. Invisible during the forced day-start, so no rush.
        if (!this.fireflies) {
          this.fireflies = new Fireflies(this.scene, {
            count: this.quality.fireflyCount,
          });
          if (this.timeOfDay) this.timeOfDay.fireflies = this.fireflies;
        }
        // These were added to the scene AFTER the reveal-time warm ran, so
        // their pipelines are still cold — re-warm off-thread now, before the
        // player walks into bonfire/lava/animal view and pays the lazy compile.
        this.#warmShadersInBackground();
      } catch (err) {
        console.warn("[App] deferred world systems failed:", err);
      }
    };
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback(() => run(), { timeout: 2500 });
    } else {
      setTimeout(run, 1200);
    }

    // First load always opens on DAY; ~12s after spawn, ease to the visitor's
    // real local time and resume the automatic day/night cycle.
    setTimeout(() => this.timeOfDay?.easeToClock?.(), 12000);

    // Rain was forced off so the spawn is clear — switch it on ~15s after launch
    // (only if it was wanted; a visitor who'd disabled it stays dry). setEnabled
    // is the wrapped version, so the auto-storm + button sync in lockstep.
    if (this._rainWanted) {
      setTimeout(() => {
        this.rain?.setEnabled?.(true);
        // Warm the rain/splash pipelines off-thread once enabled, so the first
        // raindrop frame doesn't compile under the player.
        this.#warmShadersInBackground();
      }, 15000);
    }

    // Leaves were held off the spawn frame — release them ~8s after launch.
    // From here the tick keeps them suppressed whenever it's snowing.
    setTimeout(() => {
      this._leavesUnlocked = true;
    }, 8000);
  }

  #scheduleDeferredAnimationWarmup() {
    const warm = () => this.player?.character?.preloadDeferredAnimations?.();
    if (typeof window.requestIdleCallback === "function") {
      window.requestIdleCallback(warm, { timeout: 5000 });
    } else {
      window.setTimeout(warm, 2500);
    }
  }

  // Adaptive DPR controller — samples frame time over 60-frame windows.
  // When average exceeds the drop threshold, scales effective pixelRatio
  // down by 0.15 (to the quality-tier floor). Recovery is deliberately
  // SLOW (six comfortable windows, asymmetric vs. the single bad window
  // that drops) so the factor settles instead of ping-ponging around the
  // threshold as the player walks in/out of a heavy view — every change
  // costs a framebuffer realloc, which is the stutter we're avoiding. A
  // post-change cooldown further spaces adjustments out.
  #updateAdaptiveDpr(frameDelta) {
    this._dprFrameAccum += frameDelta;
    this._dprFrameCount++;
    if (this._dprFrameCount < 60) return;
    const avg = this._dprFrameAccum / this._dprFrameCount;
    this._dprFrameAccum = 0;
    this._dprFrameCount = 0;

    const floor = this.quality.dprFloor ?? 0.7;
    const atFloor = this._dprFactor <= floor + 0.001;
    const struggling = avg > 0.022;
    const comfortable = avg < 0.014;

    // ── Stage 2: feature shedding (below the DPR floor) ─────────────────────
    // Only shed once resolution is already pinned at the floor and we're STILL
    // over budget. Restore is stricter: requires LOTS of headroom (so adding a
    // feature back won't immediately re-overload) AND that DPR has already
    // climbed back to max — i.e. undo shedding in reverse order. Skipped once
    // the debug key has hand-set a level.
    if (!this._perfManual) {
      if (atFloor && struggling && this._perfShedLevel < this._perfShedMax) {
        this._perfBadWindows++;
        this._perfGoodWindows = 0;
        if (this._perfBadWindows >= 3) {
          this.#applyPerfShed(this._perfShedLevel + 1);
          this._perfBadWindows = 0;
        }
      } else if (comfortable && this._perfShedLevel > 0) {
        // Recover a rung after a long, stable run of headroom. Now that the
        // rungs only THIN (not hide), re-adding a step of density back is low
        // risk, so recovery no longer waits for DPR to climb all the way back to
        // max first — a weak machine that found a calm patch can re-thicken the
        // world without first clawing resolution back (which it may never do).
        // The 8-window gate + cooldown still guard against ping-pong.
        this._perfGoodWindows++;
        this._perfBadWindows = 0;
        if (this._perfGoodWindows >= 8) {
          this.#applyPerfShed(this._perfShedLevel - 1);
          this._perfGoodWindows = 0;
        }
      } else {
        this._perfBadWindows = 0;
        this._perfGoodWindows = 0;
      }
    }

    // ── Stage 1: adaptive DPR ───────────────────────────────────────────────
    // Hold steady while a recent change is still cooling down — never two
    // reallocs in quick succession.
    if (this._dprCooldown > 0) {
      this._dprCooldown--;
      this._dprFastWindows = 0;
      return;
    }

    let next = this._dprFactor;
    if (avg > 0.022) {
      // Under load — drop a notch toward the tier floor.
      next = Math.max(floor, this._dprFactor - 0.15);
      this._dprFastWindows = 0;
    } else if (avg < 0.014) {
      // Comfortable — bank a fast window. Recover only after a long, stable
      // run of headroom so a brief lull doesn't bounce us back up.
      this._dprFastWindows++;
      if (this._dprFastWindows >= 6) {
        next = Math.min(1.0, this._dprFactor + 0.15);
        this._dprFastWindows = 0;
      }
    } else {
      // Hysteresis band — neither stress nor headroom, hold.
      this._dprFastWindows = 0;
    }

    if (Math.abs(next - this._dprFactor) < 0.01) return;
    // A change is firing — block the next one for a few windows.
    this._dprCooldown = 3;
    this._dprFactor = next;
    const eff = this._dprBase * next;
    this.renderer.setPixelRatio(eff);
    this.postfx?.resize(this.sizes.width, this.sizes.height, eff);
    if (this.debug?.enabled) {
      console.log(
        `[DPR] avg ${(avg * 1000).toFixed(1)}ms → factor ${next.toFixed(2)} (effective ${eff.toFixed(2)})`,
      );
    }
  }

  /**
   * Apply a feature-shed rung (see _perfShedLevel). Each rung is a draw-count /
   * visibility-only change — NO pipeline/material recompile and NO render-path
   * switch, so it's fully reversible and safe on WebGPU (toggling the post chain
   * or renderer.toneMapping at runtime invalidates the bind groups the
   * consolidated materials are bound to → black screen).
   *
   * The ladder THINS instead of hiding — the old rungs hid the whole grass
   * field then every tree, which read as a broken bare-terrain desert on weak
   * hardware. Now grass drops to a sparse floor and foliage sheds its leaf-card
   * shell then thins, but cores + a sparse grass field ALWAYS remain, so the
   * world still looks populated at the worst rung:
   *   0 → full grass, full foliage (+ shell on tiers that built one)
   *   1 → grass ~60%, foliage shell dropped (priciest overdraw), cores full
   *   2 → grass ~35% (floor), foliage cores ~65%
   * Post-FX is intentionally NOT shed here for the bind-group reason above;
   * user-toggleable ambient effects (rain/leaves/wind-lines) are left alone too
   * — those persist a player preference we mustn't overwrite.
   */
  #applyPerfShed(level) {
    level = Math.max(0, Math.min(this._perfShedMax, level));
    if (level === this._perfShedLevel) return;
    this._perfShedLevel = level;
    const grassFactor = [1.0, 0.6, 0.35][level];
    const foliageFactor = [1.0, 1.0, 0.65][level];
    this.grass?.setDensityFactor?.(grassFactor);
    this.foliage?.setDensityFactor?.(foliageFactor);
    this.foliage?.setShellVisible?.(level < 1);
    if (this.debug?.enabled) console.log(`[perf] shed level → ${level}`);
  }

  #initMapSystems() {
    assertCoordRoundTrip(WORLD_BOUNDS);
    const solidPushSpots =
      this.actionPrompts?.pushSpots ?? this.world.nature?.pushSpots ?? [];
    const runtimeBlockers = solidPushSpots
      .filter((spot) => spot.type !== "log")
      .map((spot) => ({
        type: "circle",
        center: [spot.position.x, spot.position.z],
        radius: this.#navBlockerRadius(spot),
        label: spot.type ?? "solid",
      }));
    const lampBlockers = LAMPS.map(([x, z]) => ({
      type: "circle",
      center: [x, z],
      radius: 1.15,
      label: "lamp",
    }));

    // Resolve the three sections from their live world features (real coords +
    // correct facing) so the map markers and teleport match the actual world,
    // not the stale hardcoded positions.
    this.mapSections = this.#buildMapSections();

    this.discovery = new Discovery({ sections: this.mapSections });
    this.navmask = new Navmask({
      bounds: WORLD_BOUNDS,
      blockers: [...BLOCKERS, ...runtimeBlockers, ...lampBlockers],
    });
    this.transitionFx = new TransitionFX(
      document.getElementById("transition-root"),
    );
    this.teleport = new Teleport({
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      terrain: this.world.terrain,
      navmask: this.navmask,
      transitionFx: this.transitionFx,
      audio: this.audio,
      discovery: this.discovery,
      achievements: this.achievements,
      sections: this.mapSections,
      world: this.world,
    });
    this.clickToMove = new ClickToMove({
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      navmask: this.navmask,
      scene: this.scene,
      terrain: this.world.terrain,
      audio: this.audio,
      sections: this.mapSections,
    });
    this.mapSnapshot = new MapSnapshot({
      renderer: this.renderer,
      scene: this.scene,
      bounds: WORLD_BOUNDS,
      hideDuringCapture: [this.player.group],
    });
    this.miniMap = new MiniMap({
      player: this.player,
      discovery: this.discovery,
      snapshot: this.mapSnapshot,
      sections: this.mapSections,
      audio: this.audio,
      onExpand: (rect) => this.mapOverlay?.open(rect),
    });
    this.mapOverlay = new MapOverlay({
      player: this.player,
      controller: this.player.controller,
      discovery: this.discovery,
      teleport: this.teleport,
      clickToMove: this.clickToMove,
      navmask: this.navmask,
      audio: this.audio,
      miniMap: this.miniMap,
      snapshot: this.mapSnapshot,
      sections: this.mapSections,
    });
    this.discovery.onDiscover((id) => {
      if (id) this.audio?.playMarkerClick?.();
    });
    this.#bindMapKeys();
  }

  /**
   * Render the world top-down for the map exactly once, forced to DAY lighting
   * so the map reads the same regardless of the live time of day (and so the
   * single render never has to be repeated for day/night — opening the map
   * stays a zero-cost canvas blit). Runs during boot behind the loading screen;
   * forces day, captures, then restores the real clock-based cycle position.
   */
  async #captureMapSnapshot() {
    if (!this.mapSnapshot || !this.timeOfDay) return;
    const tod = this.timeOfDay;
    const origProgress = tod.progress;
    const origPaused = tod.paused;
    try {
      // Jump to the day peak and freeze the cycle so the live tick loop holds
      // every lighting system at day for the frames before the snapshot — not
      // just the palette (which is all `mode = "day"` applies synchronously).
      tod.mode = "day";
      tod.paused = true;
      await this.#waitFrames(2);
      await this.mapSnapshot.capture();
    } catch (err) {
      console.warn("[App] map snapshot capture failed:", err);
    } finally {
      tod.progress = origProgress;
      tod.paused = origPaused;
      tod.reapply();
    }
  }

  /** Resolve after `n` animation frames (the live render loop drives them). */
  #waitFrames(n) {
    return new Promise((resolve) => {
      let i = 0;
      const step = () => (++i >= n ? resolve() : requestAnimationFrame(step));
      requestAnimationFrame(step);
    });
  }

  /**
   * Resolve the three portfolio sections from their live world features so the
   * map markers + teleport use real coordinates and face the right way:
   *   - Projects → stand just outside the hut door, facing into the hut.
   *   - Skills   → stand at the pond edge (spawn-ward side), facing the sphere.
   *   - Contact  → stand in front of the readable board face, facing the board.
   * Each entry carries an explicit `landing` { x, z, facing } the teleport
   * lands on. Falls back to WorldMap metadata if a feature didn't resolve.
   */
  #buildMapSections() {
    const meta = Object.fromEntries(SECTIONS.map((s) => [s.id, s]));
    const out = [];
    const add = (id, center, landing) => {
      const m = meta[id] ?? { id, name: id, color: "#d4a017" };
      out.push({
        id,
        name: m.name,
        color: m.color,
        position: [center.x, 0, center.z],
        landing,
      });
    };

    const hut = this.projectsHut;
    if (hut?.ready && hut.doorPoint && hut.boardNormal) {
      const n = hut.boardNormal; // points outward through the door arch
      const stand = {
        x: hut.doorPoint.x + n.x * 3.2,
        z: hut.doorPoint.z + n.z * 3.2,
        facing: Math.atan2(-n.x, -n.z), // look back toward the hut interior
      };
      add("projects", hut.doorPoint, stand);
    }

    const sph = this.skillSphere;
    if (sph?.ready && sph.center) {
      const c = sph.center;
      const len = Math.hypot(c.x, c.z) || 1;
      const dx = -c.x / len; // unit vector from sphere toward spawn
      const dz = -c.z / len;
      const dist = (sph.radius ?? 6) + 8;
      const stand = {
        x: c.x + dx * dist,
        z: c.z + dz * dist,
        facing: Math.atan2(-dx, -dz), // look back toward the sphere centre
      };
      add("skills", c, stand);
    }

    const brd = this.contactBoard;
    if (brd?.ready && brd.faceCenter && brd.faceNormal) {
      const n = brd.faceNormal; // points toward spawn (the readable side)
      const fc = brd.faceCenter;
      const stand = {
        x: fc.x + n.x * 3.2,
        z: fc.z + n.z * 3.2,
        facing: Math.atan2(-n.x, -n.z), // look back toward the board face
      };
      add("contact", fc, stand);
    }

    // Experience — resolved from the live Career-Ascent stations (NE bridge).
    // Marker sits at the average deck anchor; the teleport lands on the deck.
    const exp = this.experience;
    if (exp?.center && exp.items?.length) {
      const c = exp.center;
      const land = exp.landing ?? { x: c.x, z: c.z, facing: 0 };
      out.push({
        id: "experience",
        name: "Experience",
        color: "#e8b54a",
        position: [c.x, 0, c.z],
        // y is the deck-surface height — Teleport uses it so the bridge landing
        // doesn't sample the riverbed and drop the player under the deck.
        landing: { x: land.x, z: land.z, facing: land.facing, y: land.y },
      });
    }

    // Keep any section that failed to resolve so its marker still shows.
    for (const s of SECTIONS) {
      if (!out.some((o) => o.id === s.id)) out.push({ ...s });
    }
    return out;
  }

  #navBlockerRadius(spot) {
    if (spot.type === "tree") return 0.6;
    if (spot.type === "rock")
      return Math.max(0.8, Math.min(1.4, spot.colliderRadius ?? 1.0));
    if (spot.type === "board") return 3.2;
    if (spot.type === "section") return 3.4;
    if (spot.type === "sign") return 1.8;
    return Math.max(0.6, Math.min(1.2, spot.colliderRadius ?? 0.8));
  }

  #bindMapKeys() {
    if (this._mapKeysBound) return;
    this._mapKeysBound = true;
    window.addEventListener("keydown", (e) => {
      if (document.body.classList.contains("booting")) return;
      if (e.code === "KeyM") {
        e.preventDefault();
        this.mapOverlay?.toggle?.();
      } else if (e.code === "Escape" && this.mapOverlay?.isOpen) {
        e.preventDefault();
        this.mapOverlay.close();
      } else if (e.code === "Backquote" && this.navmask) {
        this.#toggleNavmaskDebug();
      } else if (e.code === "KeyK") {
        this.#toggleColliderDebug();
      } else if (e.code === "KeyT") {
        // Debug: cycle the tone-mapping operator (Neutral → AgX → ACES) so the
        // look can be compared live, then locked in.
        const label = this.postfx?.cycleToneMapping?.();
        if (label) console.info(`[postfx] tone mapping → ${label}`);
      } else if (e.code === "KeyP") {
        // Debug: step the adaptive perf-shed ladder so each degraded rung can
        // be eyeballed without throttling the GPU. Latches manual mode so the
        // auto controller stops adjusting features (DPR still adapts).
        this._perfManual = true;
        const nextLevel = (this._perfShedLevel + 1) % (this._perfShedMax + 1);
        this.#applyPerfShed(nextLevel);
        console.info(
          `[perf] shed level → ${this._perfShedLevel} (0=full, 1=thinned + shell off, 2=min density)`,
        );
      }
    });
    // Console helper: dump every Rapier collider (translation + half-extents),
    // sorted by footprint width and by distance to the player, to spot oversized
    // proxies. Available any time as window.__dumpColliders().
    window.__dumpColliders = () => this.#dumpColliders();
  }

  // ── Collider debug overlay (press K) ──────────────────────────────────────

  #toggleColliderDebug() {
    if (this._colliderDebugLines) {
      this.scene.remove(this._colliderDebugLines);
      this._colliderDebugLines.geometry.dispose();
      this._colliderDebugLines.material.dispose();
      this._colliderDebugLines = null;
      return;
    }
    const geometry = new THREE.BufferGeometry();
    const lines = new THREE.LineSegments(
      geometry,
      new THREE.LineBasicMaterial({
        vertexColors: true,
        depthTest: false,
        depthWrite: false,
        transparent: true,
        toneMapped: false,
      }),
    );
    lines.name = "collider-debug";
    lines.renderOrder = 999;
    lines.frustumCulled = false;
    this.scene.add(lines);
    this._colliderDebugLines = lines;
    this.#updateColliderDebug();
    this.#dumpColliders();
  }

  /** Rebuild the wireframe from Rapier's debug buffers (called per-frame while on). */
  #updateColliderDebug() {
    const lines = this._colliderDebugLines;
    if (!lines || !this.physics?.world) return;
    const { vertices, colors } = this.physics.world.debugRender();
    lines.geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(vertices, 3),
    );
    lines.geometry.setAttribute("color", new THREE.BufferAttribute(colors, 4));
  }

  #dumpColliders() {
    const world = this.physics?.world;
    if (!world) return;
    const ppos = this.player?.position ?? { x: 0, y: 0, z: 0 };
    const rows = [];
    world.forEachCollider((c) => {
      const t = c.translation();
      const he = c.halfExtents?.(); // cuboids only
      const radius = c.radius?.(); // cylinders/balls
      const footprint = he ? Math.max(he.x, he.z) : (radius ?? null);
      rows.push({
        shape: he ? "cuboid" : radius != null ? "cylinder" : "other",
        x: +t.x.toFixed(2),
        y: +t.y.toFixed(2),
        z: +t.z.toFixed(2),
        hx: he ? +he.x.toFixed(2) : null,
        hy: he
          ? +he.y.toFixed(2)
          : c.halfHeight?.() != null
            ? +c.halfHeight().toFixed(2)
            : null,
        hz: he ? +he.z.toFixed(2) : null,
        radius: radius != null ? +radius.toFixed(2) : null,
        footprint: footprint != null ? +footprint.toFixed(2) : null,
        dist: +Math.hypot(t.x - ppos.x, t.z - ppos.z).toFixed(2),
      });
    });
    console.log(
      `[colliders] ${rows.length} total — player at`,
      `(${ppos.x.toFixed(1)}, ${ppos.z.toFixed(1)})`,
    );
    console.groupCollapsed("[colliders] by footprint width (widest first)");
    console.table(
      [...rows].sort((a, b) => (b.footprint ?? -1) - (a.footprint ?? -1)),
    );
    console.groupEnd();
    console.groupCollapsed("[colliders] by distance to player (nearest first)");
    console.table([...rows].sort((a, b) => a.dist - b.dist));
    console.groupEnd();
  }

  #toggleNavmaskDebug() {
    if (this._navmaskCanvas?.isConnected) {
      this._navmaskCanvas.remove();
      this._navmaskCanvas = null;
      return;
    }
    this._navmaskCanvas = this.navmask.getDebugCanvas();
    document.body.appendChild(this._navmaskCanvas);
  }

  #initRenderer() {
    // Force the WebGL2 backend when either: (a) ?forceWebGL=1 is set (manual
    // repro/measure), or (b) two prior WebGPU init attempts this tab session
    // stalled (see #initRendererWithFallback) — WebGPU device acquisition was
    // observed hanging up to ~60s in Chrome, so the third load drops to the
    // mature WebGL2 path rather than gambling on another stall.
    const forceWebGL =
      window.location?.search?.includes("forceWebGL") ||
      Number(sessionStorage.getItem(App.GPU_RETRY_KEY) || 0) >= 2;
    this.renderer = new THREE.WebGPURenderer({
      canvas: this.canvas,
      antialias: this.sizes.pixelRatio < 2,
      powerPreference: "high-performance",
      alpha: false,
      forceWebGL,
    });
    this.renderer.setPixelRatio(this.sizes.pixelRatio);
    this.renderer.setSize(this.sizes.width, this.sizes.height);
    this.renderer.shadowMap.enabled = true;
    // PCFSoftShadowMap brings back the softer character shadow we had
    // before Sprint-11 — BasicShadowMap was visibly stair-stepped which
    // read as "shadows broken". PCFSoft is a few-percent slower but the
    // 144fps machine has plenty of headroom.
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    // Tone mapping is applied explicitly in PostFX's output node (switchable
    // operator, default Khronos PBR Neutral) so the renderer must NOT also
    // apply one — NoToneMapping prevents double application. The exposure is
    // still read by PostFX's .toneMapping() node from renderer.toneMappingExposure.
    this.renderer.toneMapping = THREE.NoToneMapping;
    // 1.05 under PBR Neutral — Neutral darkens midtones vs ACES, so a small
    // lift keeps the painted greens/browns reading bright without blowing the
    // warm sun. (ACES@1.3 was washing out the authored palette.)
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    // Perf: skip Three's per-frame painter sort. The default distance sort
    // projects every renderable's bounding-sphere centre through the proj
    // matrix AND Array.sorts the whole render list every frame — pure CPU on
    // the (submission-bound) bottleneck axis with our large object count.
    // NOTE (three r184 / WebGPU): sortObjects=false skips the sort AND the
    // per-object z projection entirely (Renderer.js gates both on
    // sortObjects===true), so renderOrder is NOT honoured and any
    // setOpaqueSort/setTransparentSort comparators never run. Opaque order is
    // depth-tested (visually unaffected); opaque-before-transparent is still
    // enforced by separate render lists. Only ordering WITHIN the transparent
    // list changes — it now follows scene-graph traversal order. Verify
    // water-edge/particle blending after this change.
    this.renderer.sortObjects = false;
    // Disable per-render auto-reset so renderer.info accumulates across the
    // frame's water pre-render + every composer pass. #tick resets once at
    // frame start; the debug HUD reads the full per-frame totals.
    this.renderer.info.autoReset = false;
    // KTX2 format detection is deferred to boot() — on WebGPURenderer,
    // detectSupport() calls renderer.hasFeature(), which throws until the
    // backend finishes its async init(). See boot().
  }

  /**
   * Await renderer.init() without ever hanging forever on it. WebGPU is much
   * faster at runtime than the WebGL2 fallback (it runs the TSL shaders
   * natively), so we want WebGPU whenever the machine can do it — a first-time
   * visitor dropped onto laggy WebGL2 doesn't come back. A COLD GPU process
   * (incognito, first launch) can take several seconds to hand over a WebGPU
   * device, so we deliberately WAIT for it (behind the loading screen) rather
   * than bail early to WebGL2. (An earlier 3s adapter probe was downgrading
   * cold-but-capable machines — notably incognito — to WebGL2 unnecessarily.)
   * Only a genuine stall (>12s — the wedged ~60s case) triggers a reload; the
   * first two reloads retry WebGPU (the GPU process often warms between
   * attempts), the third forces WebGL2 as a true last resort (#initRenderer
   * reads the counter). A clean init clears the counter so the next visit tries
   * WebGPU again — and __bootTiming stays [] only if it's still mid-stall.
   */
  async #initRendererWithFallback() {
    const attempts = Number(sessionStorage.getItem(App.GPU_RETRY_KEY) || 0);
    try {
      await Promise.race([
        this.renderer.init(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("renderer.init timeout")), 12000),
        ),
      ]);
      // Success — reset the counter so a future flaky session starts on WebGPU.
      sessionStorage.removeItem(App.GPU_RETRY_KEY);
    } catch (err) {
      if (attempts < 2) {
        sessionStorage.setItem(App.GPU_RETRY_KEY, String(attempts + 1));
        console.warn(
          `[App] ${err.message} (attempt ${attempts + 1}/2) — reloading ${
            attempts + 1 >= 2 ? "on the WebGL2 fallback" : "to retry WebGPU"
          }`,
        );
        location.reload();
        await new Promise(() => {}); // halt boot; the reload re-enters cleanly
      }
      // Retries exhausted (even WebGL2 init failed) — re-throw so main.js shows
      // its "Failed to load" message instead of a silent 5% hang.
      throw err;
    }
  }

  #initScene() {
    this.scene = new THREE.Scene();
    // Give the debug overlay the scene so `?debug=calls` can attribute draw
    // calls per system (Phase-0 instrumentation).
    this.debug?.setScene(this.scene);
    // Background = null because the Sky sphere paints the gradient itself.
    this.scene.background = null;
    // Fog tinted to the warm horizon, pushed farther so it doesn't smother
    // the world in orange. Trees fade subtly, sky still reads as sky.
    // DUSK.fogColor === DUSK.skyHorizon — see Palette.js.
    this.scene.fog = new THREE.Fog(DUSK.fogColor, 65, 165);
  }

  #initCamera() {
    this.camera = new THREE.PerspectiveCamera(45, this.sizes.aspect, 0.1, 300);
    // PlayerCamera.setLookAt overrides this on construction — value here just
    // keeps the first frame sane before camera-controls takes over.
    this.camera.position.set(0, 2.45, -5.5);
    this.camera.lookAt(0, 1.2, 0);
    this.scene.add(this.camera);
  }

  /** Warm sunset rig — directional sun + warm ambient + hemisphere fill. */
  #initLighting() {
    // Seeds only — TimeOfDay overwrites these from its palette on construction.
    // Tuned low (ambient/hemi) so the sun stays the dominant key once IBL adds
    // the sky-coloured fill (see Environment.js + DAY_PALETTE).
    const ambient = new THREE.AmbientLight(DUSK.ambientColor, 0.28);
    const hemi = new THREE.HemisphereLight(DUSK.hemiSky, DUSK.hemiGround, 0.32);
    const sun = new THREE.DirectionalLight(DUSK.sunColor, 2.1);
    // Initial position is overwritten by TimeOfDay on construction; this
    // just keeps the matrix sane for the first physics + shadow init.
    sun.position.set(36, 11, 22);
    sun.target.position.set(0, 0, 0);
    this.scene.add(sun.target);
    sun.castShadow = true;
    // 512² shadow map + ±18u frustum — tightened after the Quaternius
    // overhaul (more geometry per shadow pass made 1024² too costly).
    // Character + nearby props still read sharp; distant trees fade to
    // fog before their shadows would matter anyway.
    sun.shadow.mapSize.set(512, 512);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 50;
    sun.shadow.camera.left = -18;
    sun.shadow.camera.right = 18;
    sun.shadow.camera.top = 18;
    sun.shadow.camera.bottom = -18;
    sun.shadow.bias = -0.00015;
    sun.shadow.normalBias = 0.04;

    // Soft warm rim from the opposite side so trees aren't black silhouettes.
    const rim = new THREE.DirectionalLight("#ff6b3d", 0.18);
    rim.position.set(-30, 12, -20);
    rim.target.position.set(0, 0, 0);
    this.scene.add(rim.target, rim);

    this.scene.add(ambient, hemi, sun);
    this.lights = { ambient, hemi, sun, rim };

    // Visible sun mesh — reads the DirectionalLight's direction each frame so
    // the rendered disc stays locked to the shadow source.
    this.sun = new Sun(this.scene, sun);
  }

  #bindResize() {
    this.sizes.addEventListener("resize", () => {
      this.camera.aspect = this.sizes.aspect;
      this.camera.updateProjectionMatrix();
      this.renderer.setPixelRatio(this.sizes.pixelRatio);
      this.renderer.setSize(this.sizes.width, this.sizes.height);
      this.postfx?.resize(
        this.sizes.width,
        this.sizes.height,
        this.sizes.pixelRatio,
      );
    });
  }

  /** Briefly slow the simulation for a payoff beat (Colour Garden paint hit).
   *  `scale` is the target timeScale (0.32 ≈ a third speed), `duration` seconds
   *  of real time before easing back to 1. */
  triggerSlowMo(scale = 0.32, duration = 1.2) {
    this._timeScaleTarget = scale;
    this._slowMoLeft = duration;
  }

  #tick = () => {
    // Skip 5 of every 6 frames while the tab is hidden. Don't burn the
    // clock's delta on the skipped frames — getDelta() is only called on
    // frames we actually process, so the player doesn't teleport on resume.
    if (this._backgroundMode && ++this._bgFrame % 6 !== 0) {
      // setAnimationLoop re-fires on its own next frame — just skip work.
      return;
    }

    const frameDelta = Math.min(this.clock.getDelta(), 0.1);
    const elapsed = this.clock.getElapsedTime();

    // Global slow-mo: ease timeScale toward its target and derive a scaled
    // delta for the simulation (physics + player + world FX). Camera, UI and
    // audio stay on the real frameDelta so the framerate feels responsive.
    if (this._slowMoLeft > 0) {
      this._slowMoLeft -= frameDelta;
      if (this._slowMoLeft <= 0) this._timeScaleTarget = 1;
    }
    this.timeScale +=
      (this._timeScaleTarget - this.timeScale) * Math.min(1, frameDelta * 6);
    const scaledDelta = frameDelta * this.timeScale;

    this.renderer.info.reset();
    // CPU-cost instrumentation (?debug): time the JS update work per frame,
    // split sim vs world/effects, excluding the GPU render submit. Decides
    // GPU-bound vs CPU-bound — see Debug HUD `cpu` line.
    const _cpuStart = performance.now();
    this.#updateAdaptiveDpr(frameDelta);

    const fixedDelta = this.quality.physicsStep ?? 1 / 60;
    const maxSteps = this.quality.maxPhysicsSteps ?? 5;
    this._fixedAccumulator = Math.min(
      this._fixedAccumulator + scaledDelta,
      fixedDelta * maxSteps,
    );

    // An external system snapped group.position directly this frame (map
    // teleport, lava respawn, mini-game placement, push reposition). Invalidate
    // the interpolation snapshots so the seed below re-reads the NEW position
    // instead of lerping a smear/pull-back from the old one. The >2m substep
    // guard below only catches large jumps on frames that run a substep; this
    // also covers sub-metre snaps and 0-substep frames (common at 120Hz).
    if (this.player._teleported) {
      this._physInterpReady = false;
      this.player._teleported = false;
    }

    // Seed the interpolation snapshots from the current body position on the
    // first tick so the very first frame doesn't lerp from the origin.
    if (!this._physInterpReady) {
      this._physPrevPos.copy(this.player.group.position);
      this._physCurrPos.copy(this.player.group.position);
      this._physInterpReady = true;
    }

    let sample = this._lastPlayerSample;
    let steps = 0;
    while (this._fixedAccumulator >= fixedDelta && steps < maxSteps) {
      // Shift the previous snapshot, advance the sim, capture the new position.
      this._physPrevPos.copy(this._physCurrPos);
      this.physics.step(fixedDelta);
      sample = this.player.stepPhysics(fixedDelta) ?? sample;
      this._physCurrPos.copy(this.player.group.position);
      // A single 1/60 step can't move the player more than a metre or so; a
      // larger jump means a teleport/respawn (map travel, lava death, world
      // bounds) snapped the body. Collapse prev→curr so the character doesn't
      // streak across the world for one interpolated frame.
      if (this._physPrevPos.distanceToSquared(this._physCurrPos) > 4) {
        this._physPrevPos.copy(this._physCurrPos);
      }
      this._fixedAccumulator -= fixedDelta;
      steps++;
    }
    if (!sample)
      sample = this._lastPlayerSample ?? {
        moving: false,
        velocity: { x: 0, y: 0, z: 0 },
        speed: 0,
      };
    this._lastPlayerSample = sample;
    const _cpuAfterSim = performance.now();

    // Render the character at the interpolated position between the last two
    // simulated states. With 0 substeps this frame, prev/curr are unchanged and
    // the growing accumulator slides the character smoothly toward curr; with
    // 1+ substeps it renders the leftover fraction past the latest step. Skip
    // while frozen — an external system (lava sink, intro) owns the transform.
    if (!this.player._frozen) {
      const alpha = Math.min(1, this._fixedAccumulator / fixedDelta);
      this.player.group.position.lerpVectors(
        this._physPrevPos,
        this._physCurrPos,
        alpha,
      );
      // Re-aim the follow cam at the interpolated position so it tracks the same
      // smoothed point the character is drawn at (stepPhysics aimed nothing —
      // facing/camera are visual-rate now).
      this.playerCamera.follow(this.player.group.position);
    }

    // Visual-rate update: facing smoothing, slope lean, animation state, and
    // the mixer — once per frame on the real delta, after group.position has
    // been interpolated above. Decoupled from the physics substeps so the
    // animation advances every rendered frame (even on 0-substep 120Hz frames).
    this.player.updateVisual(frameDelta);

    // Drive the camera's dynamic movement-zoom before update() reads it.
    this.playerCamera.setMovementState({
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
    });
    this.playerCamera.update(frameDelta);
    // Intro cinematic drives the camera + character descent directly while the
    // orbit cam is locked; no-op once control has handed off.
    if (this.intro?.active) this.intro.update(frameDelta);
    if (this.discovery)
      this.discovery.update(this.player.position.x, this.player.position.z);
    // While the Colour Garden game mode owns the camera + locks movement,
    // suppress click-to-move so canvas clicks don't drop walk-flags behind it.
    const inGarden = this.colourGarden?.inGameMode === true;
    if (this.clickToMove && !inGarden) this.clickToMove.update(frameDelta);
    if (this.miniMap) this.miniMap.update();
    if (this.mapOverlay) this.mapOverlay.update();
    if (this.compass) this.compass.update();
    // World + ambient motion run on the SCALED delta so the whole scene visibly
    // slows during the Colour Garden paint payoff (snow drift, grass/wind sway,
    // leaves, orb arc + bloom). Camera/UI/audio + the weather schedule stay on
    // real time. scaledDelta === frameDelta outside slow-mo → normal play same.
    this.world.update(elapsed, this.camera, scaledDelta, this.player.position, {
      nightFactor: this.timeOfDay?.nightFactor ?? 0,
      snowCoverage: this.weather?.coverage ?? 0,
    });
    this.colourGarden?.update(scaledDelta, this.player.position);
    if (this._colliderDebugLines) this.#updateColliderDebug();
    this.wind.update(scaledDelta);
    // Grass's wind sway is driven by the shared Wind clock; the per-frame work
    // here is feeding player position/speed so blades bend while walking and
    // ripple locally around the legs while running.
    const camFwd = (this._camFwd ??= new THREE.Vector3());
    this.camera.getWorldDirection(camFwd);
    this.grass?.setPlayerPos(this.player.position, {
      velocity: sample?.velocity,
      speed: sample?.speed ?? 0,
      running: this.player.controller.isRunning,
      camDir: { x: camFwd.x, z: camFwd.z },
      camPos: { x: this.camera.position.x, z: this.camera.position.z },
    });
    // Foliage parts/flutters around the player (bushes at walking height,
    // canopies when jumped into) — driven by the player's 3D position.
    if (this.world.foliage)
      this.world.foliage.setPlayerPos(this.player.position);
    if (this.world.flowers)
      this.world.flowers.setPlayerPos(this.player.position);
    // Phase F — day/night lamp + bonfire intensity, lava glow, animated props.
    if (this.worldLights)
      this.worldLights.update(frameDelta, this.timeOfDay.mode, elapsed);
    if (this.bonfires)
      this.bonfires.update(
        elapsed,
        frameDelta,
        this.player.position,
        this.timeOfDay.mode,
      );
    if (this.lava) this.lava.update(elapsed, this.timeOfDay?.nightFactor ?? 0);
    if (this.lavaHazard) this.lavaHazard.update(frameDelta);
    if (this.animatedProps) {
      this.animatedProps.setPlayerPos(this.player.position);
      this.animatedProps.update(elapsed, frameDelta);
    }
    // ActionPrompts first so Interaction can read its candidate state and
    // suppress its own prompt in case of overlap (Dance tile near Contact).
    // Both are suppressed inside the Colour Garden game mode so stray prop
    // prompts don't appear over the mini-game HUD.
    if (this.actionPrompts && !inGarden)
      this.actionPrompts.tick(this.player.position, frameDelta);
    if (this.interaction && !inGarden)
      this.interaction.tick(this.player.position);
    if (
      this.skillSphere &&
      this.#shouldTickSection("skills", this.skillSphere)
    ) {
      this.skillSphere.update(frameDelta);
    }
    if (
      this.projectsHut &&
      this.#shouldTickSection("projects", this.projectsHut)
    ) {
      this.projectsHut.update(frameDelta);
    }
    if (
      this.contactBoard &&
      this.#shouldTickSection("contact", this.contactBoard)
    ) {
      this.contactBoard.update(elapsed);
    }
    if (
      this.experience &&
      this.#shouldTickSection("experience", this.experience, 58)
    )
      this.experience.update(
        frameDelta,
        this.player.position,
        this.timeOfDay?.nightFactor ?? 0,
      );
    if (this.interactables) this.interactables.update(frameDelta);
    // UI sync — only does work on mobile (interact-pill label, push-button
    // enabled state, dance toggle teardown). On desktop this is a no-op.
    if (this.ui) this.ui.tick();
    if (this.fireflies) this.fireflies.update(elapsed);
    if (this.resumeBook) this.resumeBook.update(elapsed);
    if (this.likeLights) {
      this.likeLights.update(elapsed);
      this.likeLights.setNightFactor(this.timeOfDay?.nightFactor ?? 0);
    }
    if (this.guestbookTree)
      this.guestbookTree.update(elapsed, frameDelta, this.player.position);
    if (this.groundBreak) this.groundBreak.update(frameDelta);
    // Snow and rain never share the sky. While any snow phase is active
    // (onset/storm/melt) the manual rain is fully suppressed — no drops, no
    // splashes, no rain ambient, no auto-thunder — so snow falls in quiet. This
    // never touches the user's rain toggle preference; rain resumes once it
    // clears. (Uses last frame's snow phase — a 1-frame lag on a 30s ramp.)
    const snowActive = !!this.weather?.isActive;
    const rainActive = !!this.rain?.enabled && !snowActive;
    if (this.water) {
      // Rain wetness drives the water's rain-impact rings.
      this.water.rainTarget = rainActive ? 1 : 0;
      this.water.update(elapsed, frameDelta, this.player.position, sample);
    }
    this.rain.setSuppressed(snowActive);
    this.rain.update(scaledDelta);
    // Weather director advances the snow cycle + writes the shared uniforms;
    // Snow reads them this same frame for its falling flakes. The director runs
    // on real time (don't slow the storm schedule); only the flake FALL slows.
    this.weather.update(frameDelta);
    this.snow.update(scaledDelta);
    // Auto-thunder only fires while rain is genuinely active (and never during
    // snow). The manual ⚡ button stays live regardless — it's user-initiated.
    this.thunderstorm.setActive(rainActive);
    this.thunderstorm.update(frameDelta, this.player.position);
    // Stamp snow-seen the first time flakes are actually visible, so a returning
    // visitor who caught it keeps the full-cycle pacing (see boot).
    if (!this._snowSeenPersisted && this.weather?.isSnowing) {
      this._snowSeenPersisted = true;
      localStorage.setItem("karan-portfolio:snow-seen", "1");
    }
    this.windLines.update(scaledDelta, this.player.position);
    // Leaves only fall once released (~8s post-spawn) and never while it snows —
    // autumn drift and a snowstorm can't share the sky.
    this.leaves.setActive(this._leavesUnlocked && !this.weather.isSnowing);
    this.leaves.update(scaledDelta, this.player.position);
    const _grounded = this.player._grounded !== false;
    this.footprints.update(frameDelta);
    const px = this.player.position.x;
    const py = this.player.position.y;
    const pz = this.player.position.z;
    let surface = this.#surfaceAt(px, py, pz);
    // Prints only drop on grass; the snow look kicks in once the same storm
    // coverage that swaps the crunch audio (>0.55) has blanketed the ground.
    const coverage = this.weather?.coverage ?? 0;
    this._printable = surface === "grass";
    this._snowPrint = this._printable && coverage > 0.55;
    // Once a storm has blanketed the ground, footsteps crunch through snow
    // (separate walk vs run packs). Water wading keeps its own steps.
    if (surface !== "water" && coverage > 0.55) {
      surface = this.player.controller.isRunning ? "snowRun" : "snow";
    }
    this.audio?.tick(frameDelta, {
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
      grounded: _grounded, // default to true so we don't false-trigger on first frame
      surface,
      rainOn: rainActive, // false while it snows → no rain ambient over a snowfall
    });
    // Landing one-shot — pick the right surface sample.
    if (this.audio && this._wasGroundedApp === false && _grounded === true) {
      this.audio.playLand(surface);
    }
    // Jump achievement — count every air-out transition (same edge used
    // for the audio cue). Fires for both Space-jumps and any future
    // launch-into-air mechanic.
    const airedOut = this._wasGroundedApp === true && _grounded === false;
    if (airedOut) {
      this.achievements?.onJump?.();
    }
    this._wasGroundedApp = _grounded;
    // Contextual control nudges — reads moving/running + the jump edge above.
    this.controlHints?.update(frameDelta, {
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
      jumped: airedOut,
      paused: this.player.controller.paused,
    });
    // Keep ambient bed in sync with day/night flips. Only push on change so
    // ad-hoc `audio.setMode(...)` calls (probes, debug) aren't stomped each
    // frame.
    if (
      this.audio &&
      this.timeOfDay &&
      this._lastAudioMode !== this.timeOfDay.mode
    ) {
      this._lastAudioMode = this.timeOfDay.mode;
      this.audio.setMode(this.timeOfDay.mode);
    }
    // Keep the time-of-day button icon in sync as the cycle drifts on its own.
    if (this.timeOfDay && this._lastTodPhase !== this.timeOfDay.phase) {
      this._lastTodPhase = this.timeOfDay.phase;
      this.#syncTimeOfDayButton();
    }
    // Ocean ambience volume rides player proximity to the shoreline. Inside
    // the island it falls off with distance; in the water it's at full level.
    if (this.audio && this.water) {
      this.audio.setOceanProximity(Math.hypot(px, pz), this.water.islandRadius);
    }

    // Achievements — drive per-frame timers (sprint, AFK, rain) + edges +
    // distance + water-state unlocks. Section + experience-sign proximity
    // and off-path detection are computed here too because we already have
    // the relevant world state cached on App.
    // Hold ALL achievement tracking until the intro cinematic has handed off.
    // During the sky-fall the player is moved programmatically (so movement /
    // distance / edge unlocks would fire before they've touched a key) and
    // spawn-state unlocks (snow, water) would all pop at once — then queue up
    // and play for half a minute. Gameplay-driven unlocks only.
    if (this.achievements && !this.intro?.active) {
      const ppos = this.player.position;
      // In-water state from the actual terrain water-depth (ponds/river/ocean),
      // matching Water.playerOverWater so visuals, slowdown, and unlocks agree.
      const groundY = this.world.terrain
        ? this.world.terrain.heightAt(ppos.x, ppos.z)
        : 0;
      const waterDepth = Math.max(0, Player.WATER_SURFACE_Y - groundY);
      // Gate on the player's feet height (ppos.y is feet) so standing on a
      // bridge deck over the pond/river doesn't register as in-water.
      const inWater = waterDepth > 0 && ppos.y <= Player.WATER_SURFACE_Y + 0.1;
      this.achievements.tick(frameDelta, {
        playerPos: ppos,
        moving: !!sample?.moving,
        running: this.player.controller.isRunning,
        grounded: _grounded,
        inWater,
        waterDepth,
        isNight: this.timeOfDay?.mode === "night",
        isRaining: rainActive,
        isSnowing: !!this.weather?.isSnowing,
        mode: this.timeOfDay?.mode,
      });
      this.#tickAchievementProximity(ppos, inWater);
    }

    // Distance-guess mini-game — early-exits when the player isn't in the
    // shore zone, so the cost off-trigger is one hypot + branch per frame.
    if (this.distanceGame) {
      this.distanceGame.update(frameDelta, this.player.position, {
        moving: !!sample?.moving,
        isNight: this.timeOfDay?.mode === "night",
      });
    }

    // Sun + shadow camera follow the player so shadows stay sharp wherever
    // they walk. TimeOfDay owns the offset so it can be lerped between
    // day-sun and night-moon positions during the transition.
    const p = this.player.position;
    const off = this.timeOfDay.sunOffset;
    this.lights.sun.position.set(p.x + off.x, p.y + off.y, p.z + off.z);
    this.lights.sun.target.position.set(p.x, p.y, p.z);
    this.lights.sun.target.updateMatrixWorld();
    // Foliage two-tone blend follows the sun: direction = (light - target).
    if (this.world.foliage) {
      this.world.foliage.setSunDirection(off);
    }
    this.timeOfDay.tick(p, this.camera, elapsed, frameDelta);
    // Sun disc follows its OWN arc (set by TimeOfDay), not the shadow light, so
    // it sets in the west while the moon rises in the east.
    this.sun.update(this.camera, this.timeOfDay.sunDiscDir);

    // Rebuild the sky-derived IBL when the sky colours move (no-op most frames).
    if (this.environment) this.environment.update();

    // Water no longer owns reflection/refraction render targets; this stays as a
    // stable hook for any future pre-render work the water system may need.
    if (this.water) this.water.preRender(this.renderer, this.camera);

    // Defensive: the off-screen map snapshot binds a render target and may be
    // mid-flight (its async render/readback can straddle this frame). Force the
    // on-screen frame back to the default framebuffer so it never lands in the
    // map's texture.
    this.renderer.setRenderTarget(null);
    // Mark the end of CPU update work (everything above) before the GPU submit.
    const _cpuEnd = performance.now();
    this.debug.setCpuTiming(
      _cpuEnd - _cpuStart,
      _cpuAfterSim - _cpuStart,
      _cpuEnd - _cpuAfterSim,
    );
    this.postfx.render(frameDelta);
    this.debug.tick();
  };

  /**
   * Whether a cardinal section's per-frame update() should run this tick.
   * Skipping it saves CPU for sections the player isn't at — but these are
   * VISIBLE animated landmarks (the skill sphere's orbiting cards, etc.), so
   * we must never freeze one that's on screen. Gate only when the section is
   * BOTH far AND behind the camera (outside the forward hemisphere), where a
   * frozen animation can't be seen. `this._camFwd` is refreshed earlier in the
   * tick (grass needs it) so this is a couple of squared-distance + dot ops.
   */
  #shouldTickSection(key, module, radius = 46) {
    if (!module) return false;
    if (module.active || module.zooming || module.transitioning) return true;
    if (module._near || module.inGameMode) return true;
    const ref = this.world?.glb?.refs?.sections?.[key]?.position;
    const p = this.player?.position;
    if (!ref || !p) return true;
    const dx = p.x - ref.x;
    const dz = p.z - ref.z;
    if (dx * dx + dz * dz <= radius * radius) return true; // near → always tick
    // Far: keep ticking unless the section is behind the camera (can't be seen).
    const fwd = this._camFwd;
    if (!fwd) return true;
    const toX = ref.x - this.camera.position.x;
    const toZ = ref.z - this.camera.position.z;
    return fwd.x * toX + fwd.z * toZ > 0; // in front → tick, behind → skip
  }

  #tickAchievementProximity(playerPos, inWater) {
    const ach = this.achievements;
    if (!ach) return;
    const px = playerPos.x;
    const pz = playerPos.z;

    // Section detection — uses the same cardinal slots Signs.js + Billboards
    // exposes. Radii are tuned generously so a normal stroll into the area
    // counts as "visited" without forcing the player to brush every sign.
    if (this.world.billboards) {
      // Projects centre is exposed from Billboards.PROJECTS_CENTER; the
      // billboards are scattered around it within a ~6m ring, so 14m clears
      // the whole cluster.
      const projects = this.world.billboards.items?.[0]?.position;
      if (projects) {
        const cx = projects.x; // any item is close enough to read "near projects"
        // Detect cluster centre by averaging is overkill — just compare to
        // whatever sign is closest within 10m.
        const d = Math.hypot(px - cx, pz - projects.z);
        if (d < 14) ach.onSectionVisited("projects");
      }
    }
    if (this.world.signs) {
      const skills = this.world.signs.skillsPosition;
      const contact = this.world.signs.contactPosition;
      if (skills && Math.hypot(px - skills.x, pz - skills.z) < 10) {
        ach.onSectionVisited("skills");
      }
      if (contact && Math.hypot(px - contact.x, pz - contact.z) < 10) {
        ach.onSectionVisited("contact");
      }
    }

    // Experience — the Career Ascent stations along the NE bridge. Walking
    // within ~4m of a station's deck anchor counts it viewed (due_diligence)
    // and the section visited.
    const expItems = this.experience?.items;
    if (expItems && expItems.length) {
      let nearAny = false;
      for (const st of expItems) {
        const dx = px - st.position.x;
        const dz = pz - st.position.z;
        if (dx * dx + dz * dz < 16) {
          ach.onExperienceSignViewed(st.index);
          nearAny = true;
        }
      }
      if (nearAny) ach.onSectionVisited("experience");
    }

    // Off-path: 15m+ from every path tile, on land. Skip when wading so
    // the open ocean doesn't trivially unlock this.
    if (!inWater && !ach.unlocked.has("off_script")) {
      const pos = this._pathPositions;
      const n = this._pathCount;
      if (pos && n > 0) {
        const minDist2 = 15 * 15;
        let anyWithin = false;
        for (let i = 0; i < n; i++) {
          const dx = px - pos[i * 2];
          const dz = pz - pos[i * 2 + 1];
          if (dx * dx + dz * dz < minDist2) {
            anyWithin = true;
            break;
          }
        }
        if (!anyWithin) ach.onOffPath();
      }
    }
  }

  /** Pick the surface category at (x, y, z) for footstep + landing audio.
   *  Bridges are checked first (their decks sit over water, so the water
   *  test below would otherwise win): on a deck → 'wood'. Then mirrors the
   *  rules Footprints uses: in water → 'water'; r ≥ 38 → 'sand' (shore);
   *  within radius of a path tile → 'stone'; otherwise grass. Cheap O(N)
   *  over path positions, but N is small (~tens) and runs once per frame. */
  #surfaceAt(x, y, z) {
    if (this.world?.glb?.playerOnBridge?.(x, y, z, this.water?.waterLevel))
      return "wood";
    if (this.water?.playerOverWater?.(x, z)) return "water";
    // Flat stone props (slabs / flagstones / stepping stones) read as stone,
    // not grass — checked ahead of the shore/path tests so a slab beyond the
    // sand radius still sounds like stone.
    if (this.world?.glb?.playerOnStone?.(x, y, z)) return "stone";
    if (x * x + z * z >= 38 * 38) return "sand";
    const pos = this._pathPositions;
    const n = this._pathCount;
    const r2 = this._pathRadius2;
    if (pos && n > 0 && r2 > 0) {
      for (let i = 0; i < n; i++) {
        const dx = x - pos[i * 2];
        const dz = z - pos[i * 2 + 1];
        if (dx * dx + dz * dz < r2) return "stone";
      }
    }
    return "grass";
  }
}
