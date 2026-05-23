import * as THREE from 'three';
import { Sizes } from './Utils/Sizes.js';
import { Debug } from './Utils/Debug.js';
import { Loader } from './Utils/Loader.js';
import { World } from './World/World.js';
import { DUSK } from './World/Palette.js';
import { Wind } from './World/Wind.js';
import { Grass } from './World/Grass.js';
import { Sun } from './World/Sun.js';
import { Player } from './Player/Player.js';
import { PlayerCamera } from './Player/PlayerCamera.js';
import { Physics } from './Physics/Physics.js';
import { Interaction } from './Portfolio/Interaction.js';
import { Fireflies } from './Effects/Fireflies.js';
import { Water } from './Effects/Water.js';
import { Rain } from './Effects/Rain.js';
import { WindLines } from './Effects/WindLines.js';
import { Leaves } from './Effects/Leaves.js';
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
    this.grass = new Grass(this.scene, this.wind);

    // Atmospheric effects — added during construction so they exist on first
    // frame; they don't depend on async loaded assets.
    this.fireflies = new Fireflies(this.scene);
    // Pond northwest of spawn. Loader is passed so lily-pad GLBs can be
    // placed on the surface.
    this.waterPos = new THREE.Vector3(-12, 0.05, 18);
    this.water = new Water(this.scene, { position: this.waterPos, radius: 5.5, loader: this.loader });
    this.rain = new Rain(this.scene, this.camera);
    this.windLines = new WindLines(this.scene, this.wind);
    this.leaves = new Leaves(this.scene, this.wind);

    // PostFX wraps the renderer. Created here so resize() can wire to it.
    this.postfx = new PostFX(this.renderer, this.scene, this.camera, this.sizes);

    this.audio = new AudioManager();

    this.#bindResize();
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
      this.world.loadAssets(this.loader, this.physics),
    ]);

    // Push path-tile XZ centres into the grass shader once after load —
    // suppresses blades growing through tile faces. Static, so no per-frame
    // update needed.
    if (this.world.paths) {
      this.grass.setPathExclusions(
        this.world.paths.getTilePositions(),
        this.world.paths.getTileCount(),
      );
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
    });

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
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
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
    // Low ~15° elevation so the sun sits within the third-person camera's
    // pitch range (maxPolarAngle caps view at ~19° above horizon). Long
    // shadows are the intended sunset look.
    this.sunOffset = new THREE.Vector3(36, 11, 22);
    sun.position.copy(this.sunOffset);
    sun.target.position.set(0, 0, 0);
    this.scene.add(sun.target);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.near = 1;
    sun.shadow.camera.far = 90;
    sun.shadow.camera.left = -28;
    sun.shadow.camera.right = 28;
    sun.shadow.camera.top = 28;
    sun.shadow.camera.bottom = -28;
    sun.shadow.bias = -0.00015;
    sun.shadow.normalBias = 0.04;
    sun.shadow.radius = 4;

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
    this.playerCamera.update(delta);
    this.world.update(elapsed, this.camera, delta);
    this.wind.update(delta);
    this.grass.update(this.camera, this.player.position);
    if (this.interaction) this.interaction.tick(this.player.position);
    this.fireflies.update(elapsed);
    this.water.update(elapsed, delta, this.player.position);
    this.rain.update(delta);
    this.windLines.update(delta, this.player.position);
    this.leaves.update(delta, this.player.position);
    this.audio?.tick(delta, {
      moving: !!sample?.moving,
      running: this.player.controller.isRunning,
      grounded: this.player._grounded !== false, // default to true so we don't false-trigger on first frame
    });

    // Sun + shadow camera follow the player so shadows stay sharp wherever they walk.
    const p = this.player.position;
    this.lights.sun.position.set(p.x + this.sunOffset.x, p.y + this.sunOffset.y, p.z + this.sunOffset.z);
    this.lights.sun.target.position.set(p.x, p.y, p.z);
    this.lights.sun.target.updateMatrixWorld();
    this.sun.update(this.camera);

    this.debug.tick();
    this.postfx.render(delta);
    requestAnimationFrame(this.#tick);
  };
}
