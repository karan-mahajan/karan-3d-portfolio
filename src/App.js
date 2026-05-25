import * as THREE from 'three';
import { Sizes } from './Utils/Sizes.js';
import { Debug } from './Utils/Debug.js';
import { Loader } from './Utils/Loader.js';
import { World } from './World/World.js';
import { DUSK } from './World/Palette.js';
import { Wind } from './World/Wind.js';
import { Grass } from './World/Grass.js';
import { Sun } from './World/Sun.js';
import { TimeOfDay, detectAutoMode } from './World/TimeOfDay.js';
import { StreetLights } from './World/StreetLights.js';
import { DistantIslands } from './World/DistantIslands.js';
import { Player } from './Player/Player.js';
import { PlayerCamera } from './Player/PlayerCamera.js';
import { Physics } from './Physics/Physics.js';
import { Interaction } from './Portfolio/Interaction.js';
import { ActionPrompts } from './Portfolio/ActionPrompts.js';
import { Interactables } from './Portfolio/Interactables.js';
import { Fireflies } from './Effects/Fireflies.js';
// Water is constructed inside World.loadAssets so its exclusions reach
// Nature before scatter; App.js just grabs `this.world.water` in boot().
import { Rain } from './Effects/Rain.js';
import { Thunderstorm } from './Effects/Thunderstorm.js';
import { WindLines } from './Effects/WindLines.js';
import { Leaves } from './Effects/Leaves.js';
import { Footprints } from './Effects/Footprints.js';
import { PostFX } from './Effects/PostFX.js';
import { AudioManager } from './Audio/AudioManager.js';
import { UIController } from './UI/UIController.js';
import { Compass } from './UI/Compass.js';
import { Tutorial } from './UI/Tutorial.js';
import { TorchLight } from './Torch/TorchLight.js';
import { Achievements } from './Systems/Achievements.js';
import { DistanceGame } from './Systems/DistanceGame.js';
import { AchievementToast } from './UI/AchievementToast.js';
import { AchievementPanel } from './UI/AchievementPanel.js';

/**
 * Core application: scene, renderer, camera, render loop, async asset boot.
 */
export class App extends EventTarget {
  constructor() {
    super();
    this.canvas = document.getElementById('canvas');
    this.sizes = new Sizes();
    this.debug = new Debug();
    this.clock = new THREE.Clock();
    this.loader = new Loader();

    this.loader.addEventListener('progress', (e) => {
      this.dispatchEvent(new CustomEvent('progress', { detail: e.detail }));
    });

    this.#initRenderer();
    this.#initScene();
    this.#initCamera();
    this.#initLighting();

    this.physics = new Physics();
    this.world = new World(this.scene, this.loader);
    this.playerCamera = new PlayerCamera(this.camera, this.canvas);
    this.compass = new Compass({ playerCamera: this.playerCamera });
    this.player = null;

    // Shared wind source — drives the grass field today; future leaves /
    // water ripples / particle systems will read the same uniforms.
    this.wind = new Wind();
    // Grass is loaded inside boot() once paths, water, and tree placements
    // are known (it filters its placement against those exclusion lists).
    this.grass = new Grass(this.scene, this.loader, this.world.terrain, this.wind);

    // Atmospheric effects — added during construction so they exist on first
    // frame; they don't depend on async loaded assets.
    this.fireflies = new Fireflies(this.scene);
    if (this.fireflies.points) this.fireflies.points.userData.noTorchRaycast = true;
    // Sky dome is created in World ctor — flag it so the torch beam can
    // never land on the inside of the sky sphere when the mouse points
    // above the horizon line.
    if (this.world.sky?.mesh) this.world.sky.mesh.userData.noTorchRaycast = true;
    // Water (pools + river) is created during world.loadAssets so it can
    // register Nature exclusions before nature.load() scatters props. The
    // reference is grabbed in boot() once the world has loaded.
    this.water = null;
    this.rain = new Rain(this.scene, this.camera);
    if (this.rain.group) this.rain.group.userData.noTorchRaycast = true;
    this.windLines = new WindLines(this.scene, this.wind);
    if (this.windLines.mesh) this.windLines.mesh.userData.noTorchRaycast = true;
    this.leaves = new Leaves(this.scene, this.wind, this.world.terrain);
    if (this.leaves.mesh) this.leaves.mesh.userData.noTorchRaycast = true;
    // Footprints — persistent flat decals dropped on each footstep. Cadence
    // is driven by AudioManager.onStep (set up after boot) so visual prints
    // and audio steps stay aligned. Path tile positions are plumbed in
    // post-boot once World.paths exists.
    this.footprints = new Footprints(this.scene, this.world.terrain);

    // PostFX wraps the renderer. Created here so resize() can wire to it.
    this.postfx = new PostFX(this.renderer, this.scene, this.camera, this.sizes);

    this.audio = new AudioManager();
    // Rain's toggle button (built in its own constructor) plays a toggle
    // click when flipped — needs audio after construction, hence late-bind.
    if (this.rain) this.rain.audio = this.audio;

    // Thunderstorm — owns its own ⚡ button + flash overlay + message
    // element. Auto-strikes only fire while rain is enabled; the manual
    // button works at any time. setActive() is called below + on every
    // rain toggle so the auto-timer resumes/halts in lockstep.
    this.thunderstorm = new Thunderstorm(this.scene, this.camera, this.lights.ambient, this.audio);
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
      character: null,   // wired after player loads in boot()
    });

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
      this.achievementToast.show(a);
      this.audio?.playAchievement?.();
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
  }

  /** Wires the HTML toggle button (#tod-toggle) to setMode. */
  #bindTimeOfDayToggle() {
    const btn = document.getElementById('tod-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
      this.audio?.playToggle();
      this.timeOfDay.toggle();
      this.#syncTimeOfDayButton();
    });
    this.#syncTimeOfDayButton();
  }

  #syncTimeOfDayButton() {
    const btn = document.getElementById('tod-toggle');
    if (!btn) return;
    const mode = this.timeOfDay.mode;
    btn.dataset.mode = mode;
    // Flip a body data-attr so the WASD HUD, rain/audio/wind toggles, and
    // any other UI overlays can theme themselves to match the world mode.
    document.body.dataset.tod = mode;
    // Sun icon during day (click switches TO night) and a moon during
    // night (click switches TO day) — the icon shows the CURRENT state.
    btn.innerHTML = mode === 'day'
      ? '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
      : '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/></svg>';
    btn.setAttribute('aria-label', mode === 'day' ? 'Switch to night mode' : 'Switch to day mode');
    btn.setAttribute('title', mode === 'day' ? 'Switch to night' : 'Switch to day');
  }

  /**
   * Pre-compile shader programs for BOTH the day and night lighting
   * configurations. THREE's shader cache key includes the active light
   * count; when our visibility toggles flip the rim + 5 pool point lights
   * on/off, the count changes and every material's program has to be
   * fetched anew. The fetch is LAZY — programs are compiled the first
   * time a material is actually rendered with that light count. Without
   * pre-warm, the first toggle in each direction compiles materials
   * currently on screen, but subsequent player movement uncovers more
   * geometry whose materials then JIT-compile mid-walk → the lag spike.
   *
   * Strategy: snap to night, force visibility toggles to settle, call
   * compileAsync on the whole scene; snap back to the original mode,
   * settle, compile again. Both program variants now sit warm in the
   * cache. The user pays this cost once during the post-load window
   * (where waiting is expected) instead of during gameplay.
   */
  async #prewarmDayNightShaders() {
    if (!this.renderer || !this.scene || !this.camera) return;
    if (typeof this.renderer.compileAsync !== 'function') return; // r152+
    const original = this.timeOfDay.mode;
    const playerPos = this.player?.position ?? { x: 0, y: 0, z: 0 };

    // Hard-snap via reapply() (which calls #applyInstant) instead of
    // setMode(). setMode would kick off GSAP tweens that may not flush
    // synchronously across an `await`, leaving lighting state mid-tween
    // when compileAsync runs.
    const applyAndSettle = (mode) => {
      this.timeOfDay.mode = mode;
      this.timeOfDay.reapply();
      this.streetLights?.update(playerPos);
      this.timeOfDay.tick(playerPos, this.camera, 0);
    };

    try {
      applyAndSettle(original === 'day' ? 'night' : 'day');
      await this.renderer.compileAsync(this.scene, this.camera);
      applyAndSettle(original);
      await this.renderer.compileAsync(this.scene, this.camera);
    } catch (err) {
      console.warn('[App] shader prewarm failed:', err);
      applyAndSettle(original); // always restore original mode
    }
  }

  /** Loads characters / models; resolves to a summary the loader UI can use. */
  async boot() {
    await this.physics.init();
    this.physics.addStaticGround(this.world.terrain);

    this.player = new Player(
      this.scene,
      this.playerCamera,
      this.world.terrain,
      this.loader,
      this.physics,
    );
    this.playerCamera.follow(this.player.position, true);

    const [characterResult, worldResult] = await Promise.all([
      this.player.loadCharacter(),
      // Share Grass's player-bend uniforms — World constructs Nature inside
      // loadAssets() and passes them straight into its onBeforeCompile hook
      // so flowers / ferns / plants lean away from the player too (F5).
      this.world.loadAssets(this.loader, this.physics, {
        playerUniforms: this.grass.playerUniforms,
      }),
    ]);

    // Water is built inside world.loadAssets so its exclusions feed Nature.
    // Hook it up to the rain (pond ripple footprint) and TimeOfDay (day/
    // night tint). The grass field consumes its exclusion list below in the
    // grass.load() call.
    this.water = this.world.water;
    if (this.water) {
      this.timeOfDay.water = this.water;
      this.timeOfDay.reapply();
      // Give Water a handle on AudioManager so wading triggers WAV splashes
      // (entry one-shot + per-step variant). See Water.update.
      this.water.audio = this.audio;
      if (this.water.mesh) this.water.mesh.userData.noTorchRaycast = true;
    }

    // Procedural islands on the horizon. Pure decoration — no colliders, no
    // collision, fog handles the distance fade. Wired into TimeOfDay so the
    // rock + vegetation tints track day/night together with the rest of the
    // palette.
    this.distantIslands = new DistantIslands(this.scene);
    this.timeOfDay.distantIslands = this.distantIslands;
    this.distantIslands.setMode(this.timeOfDay.mode, 0);

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
      pathPositions: this.world.paths?.getTilePositions() ?? new Float32Array(0),
      pathCount: this.world.paths?.getTileCount() ?? 0,
      pathRadius: 1.4,
    });
    this.audio.onStep = (odd) => {
      this.footprints.onStep(this.player.position, this.player.group.rotation.y, !odd);
    };
    // Cache path arrays once for #surfaceAt() — picking grass/stone/sand
    // per-frame for footstep audio + landing.
    this._pathPositions = this.world.paths?.getTilePositions() ?? new Float32Array(0);
    this._pathCount = this.world.paths?.getTileCount() ?? 0;
    this._pathRadius2 = 1.4 * 1.4;

    // Build the grass field now that paths, water, and trees are placed —
    // tufts filter against those exclusions at load time. Trees' positions
    // come from Nature.pushSpots (only entries with type === 'tree').
    const treePositions = (this.world.nature?.pushSpots ?? [])
      .filter((s) => s.type === 'tree')
      .map((s) => ({ x: s.position.x, z: s.position.z }));
    await this.grass.load({
      pathPositions: this.world.paths?.getTilePositions() ?? new Float32Array(0),
      pathCount: this.world.paths?.getTileCount() ?? 0,
      pathRadius: 1.4,
      treePositions,
    });
    // Grass is thousands of instances per tuft species — skip them at the
    // raycast filter. They're not in the curated target list anyway, this
    // belt-and-braces flag covers any future change that adds them in.
    for (const inst of this.grass.instancedMeshes ?? []) {
      inst.userData.noTorchRaycast = true;
    }
    // Skip ourselves when the mouse points down at our own feet — otherwise
    // the spot beam lands on the avatar's torso and the decal sticks to the
    // shirt. Flag both the character.root group AND the inner mesh so the
    // raycast filter cuts the whole subtree regardless of which level the
    // ray traverses from.
    if (this.player?.character?.root) {
      this.player.character.root.userData.noTorchRaycast = true;
    }
    if (this.player?.character?.mesh) {
      this.player.character.mesh.userData.noTorchRaycast = true;
    }
    // The player.group also holds the placeholder + character — flag it so
    // the raycast never recurses into the avatar via the scene-root walk.
    if (this.player?.group) {
      this.player.group.userData.noTorchRaycast = true;
    }

    this.interaction = new Interaction({
      scene: this.scene,
      camera: this.camera,
      playerCamera: this.playerCamera,
      player: this.player,
      controller: this.player.controller,
      billboards: this.world.billboards,
      signs: this.world.signs,
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

    this.interactables = new Interactables(this.scene, this.loader, this.physics, this.actionPrompts, this.world.terrain);
    // Fire and forget — props load asynchronously and self-register triggers
    // as each one settles. No need to block the boot resolution on this.
    this.interactables.load().catch((err) => console.warn('[Interactables] load failed:', err));

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

    // First-visit tutorial coachmarks. Constructed eagerly so main.js can
    // call .start() at the right moment (after the welcome overlay clears
    // and the controller is unpaused). No-ops on repeat visits via the
    // localStorage flag inside Tutorial.
    this.tutorial = new Tutorial({
      controller: this.player.controller,
    });

    // Now that Signs + Billboards exist, wire the player ref so the
    // character spotlight / fill light can follow.
    this.timeOfDay.signs = this.world.signs;
    this.timeOfDay.billboards = this.world.billboards;
    this.timeOfDay.playerGroup = this.player.group;
    this.timeOfDay.character = this.player.character;
    // Re-apply current mode so freshly-loaded billboard boost picks up
    // the right intensity (TimeOfDay was built before they existed). This
    // also fires setTorchVisible() if we booted into night.
    this.timeOfDay.reapply();

    // Street lights — placed around the island so night mode reads. Each
    // pole has a Rapier collider so the player bumps into it; PointLights
    // are managed by proximity so only the closest few are ever active.
    this.streetLights = new StreetLights(
      this.scene,
      this.loader,
      this.world.terrain,
      this.physics,
    );
    // Block boot resolution until street lights are loaded AND shaders
    // for both day + night light-counts are pre-compiled. Without this,
    // the first in-session toggle hitches mid-walk as freshly-uncovered
    // geometry JIT-compiles its alternate program variant. The cost is
    // front-loaded into the loading screen where waiting is expected.
    try {
      // billboards + signs are loaded above; pass them so each lamp can
      // rotate its arm to face the nearest readable element within range.
      await this.streetLights.load({
        billboards: this.world.billboards,
        signs: this.world.signs,
      });
      this.timeOfDay.streetLights = this.streetLights;
      this.streetLights.setMode(this.timeOfDay.mode, 0);
      await this.#prewarmDayNightShaders();
    } catch (err) {
      console.warn('[StreetLights] load/prewarm failed:', err);
    }

    // Sync the current toggle-button icon to the auto-detected mode.
    this.#syncTimeOfDayButton();

    // Torch beam — constructed after the character exists. Per-frame
    // intersect uses scene.children filtered by noTorchRaycast (set above
    // on grass, leaves, fireflies, wind lines, rain, water, sky, character),
    // which keeps cost off the heavy InstancedMeshes and point clouds.
    this.torchLight = new TorchLight({
      scene: this.scene,
      camera: this.camera,
      character: this.player.character,
      timeOfDay: this.timeOfDay,
      terrain: this.world.terrain,
    });
    this.interaction.torchLight = this.torchLight;

    this.#tick();
    return { character: characterResult, world: worldResult };
  }

  #initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      powerPreference: 'high-performance',
      stencil: false,
      alpha: false,
    });
    this.renderer.setPixelRatio(this.sizes.pixelRatio);
    this.renderer.setSize(this.sizes.width, this.sizes.height);
    this.renderer.shadowMap.enabled = true;
    // PCFSoftShadowMap brings back the softer character shadow we had
    // before Sprint-11 — BasicShadowMap was visibly stair-stepped which
    // read as "shadows broken". PCFSoft is a few-percent slower but the
    // 144fps machine has plenty of headroom.
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    // 1.3 (was 1.2) — slight bump for the Quaternius nature overhaul so the
    // warmer painted greens/browns read brighter under the same warm-sun rig.
    this.renderer.toneMappingExposure = 1.3;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
  }

  #initScene() {
    this.scene = new THREE.Scene();
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
    const ambient = new THREE.AmbientLight(DUSK.ambientColor, 0.45);
    const hemi = new THREE.HemisphereLight(DUSK.hemiSky, DUSK.hemiGround, 0.55);
    const sun = new THREE.DirectionalLight(DUSK.sunColor, 2.4);
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
    const rim = new THREE.DirectionalLight('#ff6b3d', 0.5);
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
    this.sizes.addEventListener('resize', () => {
      this.camera.aspect = this.sizes.aspect;
      this.camera.updateProjectionMatrix();
      this.renderer.setPixelRatio(this.sizes.pixelRatio);
      this.renderer.setSize(this.sizes.width, this.sizes.height);
      this.postfx?.resize(this.sizes.width, this.sizes.height, this.sizes.pixelRatio);
    });
  }

  #tick = () => {
    const delta = Math.min(this.clock.getDelta(), 1 / 30);
    const elapsed = this.clock.getElapsedTime();

    this.physics.step(delta);
    const sample = this.player.update(delta);
    // Drive the camera's dynamic movement-zoom before update() reads it.
    this.playerCamera.setMovementState({
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
    });
    this.playerCamera.update(delta);
    if (this.compass) this.compass.update();
    this.world.update(elapsed, this.camera, delta);
    this.wind.update(delta);
    // Grass's wind sway is driven by uWindTime; the per-frame work is one
    // uniform write for the player-bend (F5) — blades within
    // uPlayerBendRadius lean away from the player.
    this.grass?.setPlayerPos(this.player.position);
    // ActionPrompts first so Interaction can read its candidate state and
    // suppress its own prompt in case of overlap (Dance tile near Contact).
    if (this.actionPrompts) this.actionPrompts.tick(this.player.position, delta);
    if (this.interaction) this.interaction.tick(this.player.position);
    if (this.interactables) this.interactables.update(delta);
    // UI sync — only does work on mobile (interact-pill label, push-button
    // enabled state, dance toggle teardown). On desktop this is a no-op.
    if (this.ui) this.ui.tick();
    this.fireflies.update(elapsed);
    if (this.water) this.water.update(elapsed, delta, this.player.position, sample);
    this.rain.update(delta);
    this.thunderstorm.update(delta, this.player.position);
    this.windLines.update(delta, this.player.position);
    this.leaves.update(delta, this.player.position);
    const _grounded = this.player._grounded !== false;
    this.footprints.update(delta);
    const px = this.player.position.x;
    const pz = this.player.position.z;
    const surface = this.#surfaceAt(px, pz);
    this.audio?.tick(delta, {
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
      grounded: _grounded, // default to true so we don't false-trigger on first frame
      surface,
      rainOn: !!this.rain?.enabled,
    });
    // Landing one-shot — pick the right surface sample.
    if (this.audio && this._wasGroundedApp === false && _grounded === true) {
      this.audio.playLand(surface);
    }
    // Jump achievement — count every air-out transition (same edge used
    // for the audio cue). Fires for both Space-jumps and any future
    // launch-into-air mechanic.
    if (this._wasGroundedApp === true && _grounded === false) {
      this.achievements?.onJump?.();
    }
    this._wasGroundedApp = _grounded;
    // Keep ambient bed in sync with day/night flips. Only push on change so
    // ad-hoc `audio.setMode(...)` calls (probes, debug) aren't stomped each
    // frame.
    if (this.audio && this.timeOfDay && this._lastAudioMode !== this.timeOfDay.mode) {
      this._lastAudioMode = this.timeOfDay.mode;
      this.audio.setMode(this.timeOfDay.mode);
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
    if (this.achievements) {
      const ppos = this.player.position;
      const r = Math.hypot(ppos.x, ppos.z);
      const inWater = r > Player.WATER_ENTRY_RADIUS;
      const waterDepth = inWater ? (r - Player.WATER_ENTRY_RADIUS) * 0.1 : 0;
      this.achievements.tick(delta, {
        playerPos: ppos,
        moving: !!sample?.moving,
        running: this.player.controller.isRunning,
        grounded: _grounded,
        inWater,
        waterDepth,
        isNight: this.timeOfDay?.mode === 'night',
        isRaining: !!this.rain?.enabled,
        mode: this.timeOfDay?.mode,
      });
      this.#tickAchievementProximity(ppos, inWater);
    }

    // Distance-guess mini-game — early-exits when the player isn't in the
    // shore zone, so the cost off-trigger is one hypot + branch per frame.
    if (this.distanceGame) {
      this.distanceGame.update(delta, this.player.position, {
        moving: !!sample?.moving,
        isNight: this.timeOfDay?.mode === 'night',
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
    this.sun.update(this.camera);
    this.timeOfDay.tick(p, this.camera, elapsed);
    this.streetLights?.update(p);
    if (this.torchLight) {
      const modalOpen = !!(this.interaction?.activeIndex !== -1
        || this.interaction?.contactOpen
        || this.interaction?.zooming);
      this.torchLight.setSuppressed(modalOpen);
      this.torchLight.tick(p, this.camera);
    }

    // Refresh the shared water reflection + refraction RTs once per frame
    // BEFORE the composer renders. With one master Reflector / Refractor
    // shared across every pool + the river, this is 2 scene re-renders per
    // frame total (vs. 10 if each surface owned its own pair).
    if (this.water) this.water.preRender(this.renderer, this.camera);

    this.debug.tick();
    this.postfx.render(delta);
    requestAnimationFrame(this.#tick);
  };

  /**
   * Cardinal section + experience-sign proximity, plus off-path detection.
   * Cheap enough to run every frame (handful of squared-distance checks);
   * the heavy off-path scan early-exits on water + on the first path tile
   * within range.
   */
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
        if (d < 14) ach.onSectionVisited('projects');
      }
    }
    if (this.world.signs) {
      const skills = this.world.signs.skillsPosition;
      const contact = this.world.signs.contactPosition;
      if (skills && Math.hypot(px - skills.x, pz - skills.z) < 10) {
        ach.onSectionVisited('skills');
      }
      if (contact && Math.hypot(px - contact.x, pz - contact.z) < 10) {
        ach.onSectionVisited('contact');
      }
      const expItems = this.world.signs.experienceItems;
      if (expItems && expItems.length) {
        // Visiting any experience sign also counts as visiting the section.
        let nearAny = false;
        for (let i = 0; i < expItems.length; i++) {
          const p = expItems[i].position;
          const dx = px - p.x;
          const dz = pz - p.z;
          if (dx * dx + dz * dz < 16) { // within 4m
            ach.onExperienceSignViewed(i);
            nearAny = true;
          }
        }
        if (nearAny) ach.onSectionVisited('experience');
      }
    }

    // Off-path: 15m+ from every path tile, on land. Skip when wading so
    // the open ocean doesn't trivially unlock this.
    if (!inWater && !ach.unlocked.has('off_script')) {
      const pos = this._pathPositions;
      const n = this._pathCount;
      if (pos && n > 0) {
        const minDist2 = 15 * 15;
        let anyWithin = false;
        for (let i = 0; i < n; i++) {
          const dx = px - pos[i * 2];
          const dz = pz - pos[i * 2 + 1];
          if (dx * dx + dz * dz < minDist2) { anyWithin = true; break; }
        }
        if (!anyWithin) ach.onOffPath();
      }
    }
  }

  /** Pick the surface category at (x, z) for footstep + landing audio.
   *  Mirrors the same rules Footprints uses for its surface guard:
   *  in water → 'water'; r ≥ 38 → 'sand' (shore); within radius of a path
   *  tile → 'stone'; otherwise grass. Cheap O(N) over path positions, but
   *  N is small (~tens) and only runs once per frame. */
  #surfaceAt(x, z) {
    if (this.water?.playerOverWater?.(x, z)) return 'water';
    if ((x * x + z * z) >= 38 * 38) return 'sand';
    const pos = this._pathPositions;
    const n = this._pathCount;
    const r2 = this._pathRadius2;
    if (pos && n > 0 && r2 > 0) {
      for (let i = 0; i < n; i++) {
        const dx = x - pos[i * 2];
        const dz = z - pos[i * 2 + 1];
        if (dx * dx + dz * dz < r2) return 'stone';
      }
    }
    return 'grass';
  }
}
