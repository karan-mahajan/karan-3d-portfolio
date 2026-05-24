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
import { Lamps } from './World/Lamps.js';
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
import { WindLines } from './Effects/WindLines.js';
import { Leaves } from './Effects/Leaves.js';
import { Footprints } from './Effects/Footprints.js';
import { PostFX } from './Effects/PostFX.js';
import { AudioManager } from './Audio/AudioManager.js';

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
    // Water (pools + river) is created during world.loadAssets so it can
    // register Nature exclusions before nature.load() scatters props. The
    // reference is grabbed in boot() once the world has loaded.
    this.water = null;
    this.rain = new Rain(this.scene, this.camera);
    this.windLines = new WindLines(this.scene, this.wind);
    this.leaves = new Leaves(this.scene, this.wind, this.world.terrain);
    // Footprints — persistent flat decals dropped on each footstep. Cadence
    // is driven by AudioManager.onStep (set up after boot) so visual prints
    // and audio steps stay aligned. Path tile positions are plumbed in
    // post-boot once World.paths exists.
    this.footprints = new Footprints(this.scene, this.world.terrain);

    // PostFX wraps the renderer. Created here so resize() can wire to it.
    this.postfx = new PostFX(this.renderer, this.scene, this.camera, this.sizes);

    this.audio = new AudioManager();

    // Day / night cycle. Built now so it can drive lights + sky immediately
    // — billboards / signs are still loading at this point, so the lanterns
    // they need are attached after boot() completes the world load.
    // Static lantern fixtures at every readable board, with their bulb
    // emissive + PointLight intensity driven by TimeOfDay. Terrain is
    // passed so each lamp's base sits on the heightfield instead of y=0.
    this.lamps = new Lamps(this.scene, this.loader, this.world.terrain);

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
    });

    this.#bindResize();
    this.#bindTimeOfDayToggle();
  }

  /** Wires the HTML toggle button (#tod-toggle) to setMode. */
  #bindTimeOfDayToggle() {
    const btn = document.getElementById('tod-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
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
    }

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

    this.interaction = new Interaction({
      scene: this.scene,
      camera: this.camera,
      playerCamera: this.playerCamera,
      player: this.player,
      controller: this.player.controller,
      billboards: this.world.billboards,
      signs: this.world.signs,
      audio: this.audio,
    });

    this.actionPrompts = new ActionPrompts({
      player: this.player,
      controller: this.player.controller,
      audio: this.audio,
      playerCamera: this.playerCamera,
      billboardInteraction: this.interaction,
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

    // Now that Signs + Billboards exist, plant sign lanterns and wire the
    // player ref so the character spotlight / fill light can follow.
    this.timeOfDay.signs = this.world.signs;
    this.timeOfDay.billboards = this.world.billboards;
    this.timeOfDay.playerGroup = this.player.group;
    this.timeOfDay.attachLanterns();
    // Re-apply current mode so freshly-loaded lanterns + billboard boost
    // pick up the right intensity (TimeOfDay was built before they existed).
    this.timeOfDay.reapply();

    // Build physical lamps now that the signs + billboards exist.
    // Don't block boot resolution on this — lamps are visual sugar.
    this.lamps.load({ signs: this.world.signs, billboards: this.world.billboards })
      .then(() => {
        this.timeOfDay.lamps = this.lamps;
        // Re-apply the current mode so the freshly-loaded lamps pick up
        // the right intensity without a visible step.
        this.timeOfDay.reapply();
      })
      .catch((err) => console.warn('[Lamps] load failed:', err));

    // Sync the current toggle-button icon to the auto-detected mode.
    this.#syncTimeOfDayButton();

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
    this.fireflies.update(elapsed);
    if (this.water) this.water.update(elapsed, delta, this.player.position, sample);
    this.rain.update(delta);
    this.windLines.update(delta, this.player.position);
    this.leaves.update(delta, this.player.position);
    const _grounded = this.player._grounded !== false;
    this.footprints.update(delta);
    this.audio?.tick(delta, {
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
      grounded: _grounded, // default to true so we don't false-trigger on first frame
    });
    // Ocean ambience volume rides player proximity to the shoreline. Inside
    // the island it falls off with distance; in the water it's at full level.
    if (this.audio && this.water) {
      const px = this.player.position.x;
      const pz = this.player.position.z;
      this.audio.setOceanProximity(Math.hypot(px, pz), this.water.islandRadius);
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

    // Refresh the shared water reflection + refraction RTs once per frame
    // BEFORE the composer renders. With one master Reflector / Refractor
    // shared across every pool + the river, this is 2 scene re-renders per
    // frame total (vs. 10 if each surface owned its own pair).
    if (this.water) this.water.preRender(this.renderer, this.camera);

    this.debug.tick();
    this.postfx.render(delta);
    requestAnimationFrame(this.#tick);
  };
}
