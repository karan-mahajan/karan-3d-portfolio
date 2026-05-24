import * as THREE from 'three';
import gsap from 'gsap';
import { Water as Water2 } from 'three/examples/jsm/objects/Water2.js';
import { Reflector } from 'three/examples/jsm/objects/Reflector.js';
import { Refractor } from 'three/examples/jsm/objects/Refractor.js';

/**
 * Multi-surface realistic water with SHARED planar reflection / refraction.
 *
 * Architecture:
 *   - One master Reflector + one master Refractor sit on an invisible
 *     horizontal plane (Y = MASTER_PLANE_Y). They render the scene into
 *     two render targets once per frame, called explicitly via
 *     `preRender(renderer, camera)` from App.js #tick.
 *   - Every pool / river surface uses the Water2 shader but with a custom
 *     ShaderMaterial that samples the SHARED RTs. Each material's
 *     textureMatrix is updated per-mesh in onBeforeRender so reflections
 *     line up with each surface's worldMatrix.
 *   - Shared flow timer ticks once per frame in update(), driving every
 *     material's `config` uniform (offsets, halfCycle, scale).
 *
 * Why shared instead of per-instance Water2:
 *   N Water2 instances → N reflection RT renders + N refraction RT renders
 *   per frame = 2N extra scene passes. With 4 pools + a river that's 10
 *   scene re-renders per frame, which crushed FPS to ~50. Sharing drops it
 *   to exactly 2 regardless of surface count.
 *
 * Accuracy trade-off:
 *   The shared reflection plane is at one Y (terrain-average around the
 *   surfaces). Pools at different Ys sample reflections as if mirrored
 *   across the master plane, not their own surface — small (<0.5m)
 *   shift in reflected position. The normal-map distortion masks it.
 *
 * Recursion safety:
 *   `preRender` hides every water mesh before invoking the master
 *   Reflector / Refractor, then restores. Without this, the shared RTs
 *   would feedback-render themselves.
 */

const NORMAL_MAP_0_URL = '/textures/water/Water_1_M_Normal.jpg';
const NORMAL_MAP_1_URL = '/textures/water/Water_2_M_Normal.jpg';
// 256² for the shared RTs — quartering pixel work over 512² recovers
// ~3-5ms / frame on the test machine. The flow-map normal distortion
// hides the resolution loss; Water2's own example uses 512 only because
// it's the default, not because it's needed for visual quality.
const RT_SIZE = 256;
const MASTER_PLANE_Y = 0.0;
const FLOW_DIRECTION = new THREE.Vector2(1, 1);
const FLOW_SPEED = 0.03;
const FLOW_CYCLE = 0.15;
const REFLECTIVITY = 0.4;
const DISTORTION_SCALE = 3.0; // Water2's `scale` — normal-map UV repeats.

const DEFAULT_DAY_COLOR = '#4a90c4';
const DEFAULT_NIGHT_COLOR = '#2a4a64';

const RIVER_SEGMENTS_DEFAULT = 40;
const RIVER_WIDTH_DEFAULT = 3.0;
const RIVER_EXCLUSION_SAMPLES = 30;
const RIVER_EXCLUSION_RADIUS = 1.8;
const POOL_Y_LIFT = 0.05;
const RIVER_Y_LIFT = 0.04;

// Player-water interaction tuning. Shader perturbation amounts deliberately
// kept low so the radial wavefronts read as soft surface motion, not the
// painted concentric rings the old code regressed into.
// HISTORY_COUNT dropped 8 → 4 for the FPS recovery — fewer per-fragment
// loop iterations across every water pixel. Trail is now 4 × 0.12 = 0.48s.
const HISTORY_COUNT = 4;
const HISTORY_SAMPLE_INTERVAL = 0.12;   // seconds between trail samples
const HISTORY_MAX_AGE = 1.0;            // seconds
const PERTURB_PLAYER = 0.4;             // shader main-wave strength
const PERTURB_HISTORY = 0.2;            // shader per-trail-entry strength
const SPLASH_MAX = 80;                  // max concurrent splash particles
const SPLASH_PER_ENTRY = 10;
const SPLASH_LIFE = 0.6;
const SPLASH_GRAVITY = -3.0;

/** Deterministic per-segment width jitter for the river ribbon. */
function seededJitter(i) {
  const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
  return (x - Math.floor(x)) - 0.5; // [-0.5, 0.5]
}

/**
 * Custom water shader = Water2's reflection/refraction shader with two
 * additions:
 *   - varying vec3 vWorldPos passed from vertex to fragment
 *   - player-driven radial wave perturbation injected right after the
 *     normal-map normal is decoded, before fresnel + UV distortion
 *
 * Why not piggyback onBeforeCompile: Water2's material is a plain
 * ShaderMaterial built from explicit strings, not StandardMaterial. We
 * already construct it manually (see #makeWaterMesh) so we can ship the
 * modified strings directly and keep the shader self-contained.
 */
const WATER_SHADER = {
  name: 'WaterPlayerInteractShader',
  uniforms: Water2.WaterShader.uniforms,   // referenced for default scalar set
  vertexShader: /* glsl */ `
    #include <common>
    #include <fog_pars_vertex>
    #include <logdepthbuf_pars_vertex>

    uniform mat4 textureMatrix;

    varying vec4 vCoord;
    varying vec2 vUv;
    varying vec3 vToEye;
    varying vec3 vWorldPos;

    void main() {
      vUv = uv;
      vCoord = textureMatrix * vec4( position, 1.0 );

      vec4 worldPosition = modelMatrix * vec4( position, 1.0 );
      vWorldPos = worldPosition.xyz;
      vToEye = cameraPosition - worldPosition.xyz;

      vec4 mvPosition = viewMatrix * worldPosition; // used by fog_vertex
      gl_Position = projectionMatrix * mvPosition;

      #include <logdepthbuf_vertex>
      #include <fog_vertex>
    }
  `,
  fragmentShader: /* glsl */ `
    #include <common>
    #include <fog_pars_fragment>
    #include <logdepthbuf_pars_fragment>

    #define HISTORY_COUNT ${HISTORY_COUNT}

    uniform sampler2D tReflectionMap;
    uniform sampler2D tRefractionMap;
    uniform sampler2D tNormalMap0;
    uniform sampler2D tNormalMap1;

    uniform vec2 flowDirection;

    uniform vec3  color;
    uniform float reflectivity;
    uniform vec4  config;

    // Player-interaction uniforms — driven from Water.update().
    uniform float uTime;
    uniform vec3  uPlayerPos;
    uniform float uPlayerInWater;       // 1.0 when player is over water
    uniform vec3  uPlayerHistory[HISTORY_COUNT];
    uniform float uPlayerHistoryAge[HISTORY_COUNT];
    uniform float uHistoryMaxAge;
    // JS-driven gate. 0 when neither the player nor any trail entry can
    // contribute (player far from any water + every history slot expired).
    // Skips the whole perturbation block per fragment so a calm pond
    // costs nothing extra in the fragment shader.
    uniform float uActivity;

    varying vec4 vCoord;
    varying vec2 vUv;
    varying vec3 vToEye;
    varying vec3 vWorldPos;

    void main() {
      #include <logdepthbuf_fragment>

      float flowMapOffset0 = config.x;
      float flowMapOffset1 = config.y;
      float halfCycle = config.z;
      float scale = config.w;

      vec3 toEye = normalize( vToEye );

      vec2 flow = flowDirection;
      flow.x *= -1.0;

      vec4 normalColor0 = texture2D( tNormalMap0, ( vUv * scale ) + flow * flowMapOffset0 );
      vec4 normalColor1 = texture2D( tNormalMap1, ( vUv * scale ) + flow * flowMapOffset1 );

      float flowLerp = abs( halfCycle - flowMapOffset0 ) / halfCycle;
      vec4 normalColor = mix( normalColor0, normalColor1, flowLerp );

      vec3 normal = normalize( vec3(
        normalColor.r * 2.0 - 1.0,
        normalColor.b,
        normalColor.g * 2.0 - 1.0
      ) );

      // ── Player-driven radial perturbation ────────────────────────────────
      // The current player position contributes a strong wavefront with
      // smooth distance falloff; the trail of previous positions adds
      // weaker rings that fade with age. Perturbation is added to the
      // HORIZONTAL (xz) components of the tangent-space normal — those
      // map to the screen-space UV distortion that bends reflections,
      // which is what reads as "the water is moving here".
      //
      // uActivity short-circuits the whole block when the player is far
      // from water AND every trail slot has expired. Most frames hit this
      // early-out so the per-fragment cost goes back to plain Water2.
      if (uActivity > 0.0) {
        vec2 toPlayer = vWorldPos.xz - uPlayerPos.xz;
        float distToPlayer = length(toPlayer);
        float falloff = exp(-distToPlayer * 0.35);
        float wave = sin(distToPlayer * 3.5 - uTime * 5.0)
                   * falloff * uPlayerInWater * ${PERTURB_PLAYER.toFixed(3)};
        vec2 dir = normalize(toPlayer + vec2(0.0001));
        normal.xz += dir * wave;

        for (int i = 0; i < HISTORY_COUNT; i++) {
          float age = uPlayerHistoryAge[i];
          if (age >= uHistoryMaxAge) continue;
          vec3  histPos = uPlayerHistory[i];
          vec2  toHist = vWorldPos.xz - histPos.xz;
          float histDist = length(toHist);
          float histFalloff = exp(-histDist * 0.4)
                            * (1.0 - age / uHistoryMaxAge);
          float histWave = sin(histDist * 3.5 - uTime * 5.0)
                         * histFalloff * ${PERTURB_HISTORY.toFixed(3)};
          vec2 histDir = normalize(toHist + vec2(0.0001));
          normal.xz += histDir * histWave;
        }
        normal = normalize(normal);
      }
      // ── end perturbation ────────────────────────────────────────────────

      float theta = max( dot( toEye, normal ), 0.0 );
      float reflectance = reflectivity + ( 1.0 - reflectivity ) * pow( ( 1.0 - theta ), 5.0 );

      vec3 coord = vCoord.xyz / vCoord.w;
      vec2 uv = coord.xy + coord.z * normal.xz * 0.05;

      vec4 reflectColor = texture2D( tReflectionMap, vec2( 1.0 - uv.x, uv.y ) );
      vec4 refractColor = texture2D( tRefractionMap, uv );

      gl_FragColor = vec4( color, 1.0 ) * mix( refractColor, reflectColor, reflectance );

      #include <tonemapping_fragment>
      #include <colorspace_fragment>
      #include <fog_fragment>
    }
  `,
};

export class Water {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../Utils/Loader.js').Loader|null} loader
   * @param {import('../World/Terrain.js').Terrain} terrain
   * @param {object} [opts]
   */
  constructor(scene, loader, terrain, {
    dayColor = DEFAULT_DAY_COLOR,
    nightColor = DEFAULT_NIGHT_COLOR,
    rtSize = RT_SIZE,
    masterPlaneY = MASTER_PLANE_Y,
  } = {}) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;

    this.dayColor = new THREE.Color(dayColor);
    this.nightColor = new THREE.Color(nightColor);
    this._currentColor = new THREE.Color().copy(this.dayColor);
    this._rtSize = rtSize;

    // Shared normal maps.
    const tl = new THREE.TextureLoader();
    this._normalMap0 = tl.load(NORMAL_MAP_0_URL);
    this._normalMap0.wrapS = this._normalMap0.wrapT = THREE.RepeatWrapping;
    this._normalMap1 = tl.load(NORMAL_MAP_1_URL);
    this._normalMap1.wrapS = this._normalMap1.wrapT = THREE.RepeatWrapping;

    // Shared flow state (Water2's internal logic, hoisted here so all
    // materials advance in lockstep with one timer).
    this._flowOffset0 = 0;
    this._flowOffset1 = FLOW_CYCLE * 0.5;
    this._lastElapsed = 0;
    // Materials managed here so update() can iterate them once.
    this._materials = [];

    /** @type {Array<{ mesh: THREE.Mesh, position?: THREE.Vector3, radius?: number, kind: 'pool'|'river' }>} */
    this.surfaces = [];

    /** [{x, z, r}] — fed to Grass / Terrain / Nature for exclusion + wet rim. */
    this.exclusionPoints = [];

    // Ecosystem (lily pads, frog, dock, …) — only attached to pool #1.
    this.lilyGroup = new THREE.Group();
    this.lilyGroup.name = 'water-ecosystem';
    scene.add(this.lilyGroup);

    // Main-pond compat fields, set by addPool({ isMainPond: true }).
    this.mainPondPosition = null;
    this.mainPondRadius = 0;

    // Player-interaction state. Shared by reference across every water
    // material's uniforms — one mutation here updates all surfaces.
    this._playerPos = new THREE.Vector3();
    this._playerInWater = 0;
    this._playerInWaterPrev = 0;
    this._playerHistory = Array.from({ length: HISTORY_COUNT }, () => new THREE.Vector3());
    this._playerHistoryAge = new Float32Array(HISTORY_COUNT);
    for (let i = 0; i < HISTORY_COUNT; i++) this._playerHistoryAge[i] = HISTORY_MAX_AGE + 1; // expired
    this._historySampleTimer = 0;
    this._historyWriteIdx = 0;

    // River centerlines for `playerOverWater` containment checks.
    // (exclusionPoints mixes pool + river entries; this list is river-only
    // so we don't have to disentangle.)
    this._riverCenterlines = [];

    this.#buildSharedReflectors(masterPlaneY);
    this.#buildSplashSystem();
  }

  /** Build the shared master Reflector + Refractor. NOT added to the scene
   *  — their onBeforeRender is invoked manually from preRender() so they
   *  run exactly once per frame regardless of how many surfaces exist. */
  #buildSharedReflectors(planeY) {
    // 200×200 plane covers the entire walkable world (terrain is 200×200).
    const geom = new THREE.PlaneGeometry(200, 200);
    // Default normal is +Z; mesh rotation -π/2 X maps that to +Y world up.
    this._masterReflector = new Reflector(geom, {
      textureWidth: this._rtSize,
      textureHeight: this._rtSize,
      clipBias: 0.003,
    });
    this._masterReflector.rotation.x = -Math.PI / 2;
    this._masterReflector.position.y = planeY;
    this._masterReflector.updateMatrixWorld(true);

    this._masterRefractor = new Refractor(geom, {
      textureWidth: this._rtSize,
      textureHeight: this._rtSize,
      clipBias: 0.003,
    });
    this._masterRefractor.rotation.x = -Math.PI / 2;
    this._masterRefractor.position.y = planeY;
    this._masterRefractor.updateMatrixWorld(true);

    this._masterPlaneY = planeY;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  addPool(position, radius, { isMainPond = false, withEcosystem = false, segments = 48 } = {}) {
    const baseY = this.terrain
      ? this.terrain.heightAt(position.x, position.z) + POOL_Y_LIFT
      : position.y;

    const geom = new THREE.CircleGeometry(radius, segments);
    // Rotate the MESH, not the geometry, so the Reflector-style normal math
    // (reading scope.matrixWorld) keeps the geometry-local +Z normal.
    const { mesh, material } = this.#makeWaterMesh(geom);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.set(position.x, baseY, position.z);
    mesh.name = `water-pool:${this.surfaces.length}`;
    mesh.receiveShadow = true;
    this.scene.add(mesh);

    const surface = {
      mesh,
      material,
      position: new THREE.Vector3(position.x, baseY, position.z),
      radius,
      kind: 'pool',
    };
    this.surfaces.push(surface);
    this.exclusionPoints.push({ x: position.x, z: position.z, r: radius + 0.3 });

    if (isMainPond) {
      this.mainPondPosition = surface.position.clone();
      this.mainPondRadius = radius;
    }
    if (withEcosystem && this.loader) {
      this.#buildPondEcosystem(surface).catch((err) => {
        console.warn('[Water] ecosystem failed', err);
      });
    }
    return surface;
  }

  /**
   * Meandering river along a CatmullRomCurve3. The ribbon follows the
   * terrain per-segment so it doesn't slice through hills.
   */
  addRiverFromCurve(curve, { width = RIVER_WIDTH_DEFAULT, segments = RIVER_SEGMENTS_DEFAULT, widthJitter = 1.0 } = {}) {
    const { geometry, avgY } = this.#buildRiverGeometry(curve, width, segments, widthJitter);
    const { mesh, material } = this.#makeWaterMesh(geometry);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.set(0, avgY, 0);
    mesh.name = 'water-river';
    mesh.receiveShadow = true;
    // Field-radius bounding sphere so frustum culling never drops us — the
    // ribbon spans ~100m, well past CircleGeometry's auto-computed sphere.
    geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);
    this.scene.add(mesh);

    const surface = { mesh, material, kind: 'river', curve, width };
    this.surfaces.push(surface);

    // Sample the spine for exclusion (grass + nature + terrain wet rim)
    // and again for the river-only containment test used by
    // playerOverWater().
    const centerline = { points: [], halfWidth: width * 0.55 };
    for (let i = 0; i < RIVER_EXCLUSION_SAMPLES; i++) {
      const t = i / (RIVER_EXCLUSION_SAMPLES - 1);
      const p = curve.getPointAt(t);
      this.exclusionPoints.push({ x: p.x, z: p.z, r: RIVER_EXCLUSION_RADIUS });
      centerline.points.push(new THREE.Vector2(p.x, p.z));
    }
    this._riverCenterlines.push(centerline);
    return surface;
  }

  /** [{x, z, r}] for every water footprint (pools + sampled river points). */
  getExclusionPoints() {
    return this.exclusionPoints;
  }

  /** Register no-spawn circles on Nature for every footprint (+1m buffer). */
  applyExclusionsToNature(nature) {
    for (const e of this.exclusionPoints) {
      nature.addExclusion(e.x, e.z, e.r + 1.0);
    }
  }

  /** True if (x, z) lies inside any pool. River is decorative — not counted. */
  contains(x, z) {
    for (const s of this.surfaces) {
      if (s.kind !== 'pool') continue;
      const dx = x - s.position.x;
      const dz = z - s.position.z;
      const r = s.radius - 0.2;
      if (dx * dx + dz * dz < r * r) return true;
    }
    return false;
  }

  /** True if (x, z) lies over any pool OR river (used by player-interaction
   *  shader to gate the wave perturbation + the splash trigger). */
  playerOverWater(x, z) {
    for (const s of this.surfaces) {
      if (s.kind !== 'pool') continue;
      const dx = x - s.position.x;
      const dz = z - s.position.z;
      if (dx * dx + dz * dz < s.radius * s.radius) return true;
    }
    for (const r of this._riverCenterlines) {
      const r2 = r.halfWidth * r.halfWidth;
      for (const p of r.points) {
        const dx = x - p.x;
        const dz = z - p.y;
        if (dx * dx + dz * dz < r2) return true;
      }
    }
    return false;
  }

  // ── Tint API ──────────────────────────────────────────────────────────────

  setColor(hex) {
    this._currentColor.set(hex);
    for (const m of this._materials) {
      m.uniforms.color.value.set(hex);
    }
  }

  tweenColor(hex, duration = 2.0, ease = 'sine.inOut') {
    const tmp = new THREE.Color(hex);
    this._currentColor.copy(tmp);
    for (const m of this._materials) {
      gsap.to(m.uniforms.color.value, {
        r: tmp.r, g: tmp.g, b: tmp.b, duration, ease,
      });
    }
  }

  applyTimeOfDay(mode, { tween = false, duration = 2.0, ease = 'sine.inOut' } = {}) {
    const target = mode === 'night' ? this.nightColor : this.dayColor;
    const hex = `#${target.getHexString()}`;
    if (tween) this.tweenColor(hex, duration, ease);
    else this.setColor(hex);
  }

  // ── Per-frame ─────────────────────────────────────────────────────────────

  /**
   * Animation-only update. Call once per tick, before preRender().
   *
   * @param {number} elapsed
   * @param {number} delta
   * @param {THREE.Vector3|null} playerPos
   */
  update(elapsed, delta = 0, playerPos = null) {
    // Advance shared flow offsets (Water2's internal logic). One update,
    // every material reads from the same config Vector4 instance.
    this._flowOffset0 += FLOW_SPEED * delta;
    const halfCycle = FLOW_CYCLE * 0.5;
    if (this._flowOffset0 >= FLOW_CYCLE) {
      this._flowOffset0 = 0;
      this._flowOffset1 = halfCycle;
    } else {
      this._flowOffset1 = this._flowOffset0 + halfCycle;
      if (this._flowOffset1 >= FLOW_CYCLE) this._flowOffset1 -= FLOW_CYCLE;
    }
    for (const m of this._materials) {
      const cfg = m.uniforms.config.value;
      cfg.x = this._flowOffset0;
      cfg.y = this._flowOffset1;
      cfg.z = halfCycle;
      // cfg.w (distortion scale) is constant.
    }

    if (this.lilyMeshes) {
      for (const lily of this.lilyMeshes) {
        const b = lily.userData.basePos;
        lily.position.y = b.baseY + Math.sin(elapsed * 1.5 + b.phase) * 0.04;
        lily.rotation.z = Math.sin(elapsed * 0.9 + b.phase) * 0.04;
      }
    }

    // ── Player position + over-water detection ──────────────────────────
    if (playerPos) this._playerPos.copy(playerPos);
    this._playerInWaterPrev = this._playerInWater;
    this._playerInWater = playerPos && this.playerOverWater(playerPos.x, playerPos.z) ? 1.0 : 0.0;

    // Splash on water-entry edge: 0 → 1 transition this frame.
    if (this._playerInWater > 0.5 && this._playerInWaterPrev < 0.5 && playerPos) {
      this.#spawnSplashAt(playerPos);
    }

    // Trail history — rotating buffer; one sample every HISTORY_SAMPLE_INTERVAL.
    // Ages tick every frame so already-stored samples fade off the shader.
    for (let i = 0; i < HISTORY_COUNT; i++) this._playerHistoryAge[i] += delta;
    if (playerPos && this._playerInWater > 0.5) {
      this._historySampleTimer += delta;
      if (this._historySampleTimer >= HISTORY_SAMPLE_INTERVAL) {
        this._historySampleTimer = 0;
        this._historyWriteIdx = (this._historyWriteIdx + 1) % HISTORY_COUNT;
        this._playerHistory[this._historyWriteIdx].copy(playerPos);
        this._playerHistoryAge[this._historyWriteIdx] = 0;
      }
    } else {
      // Player not in water — let history naturally age out, don't capture.
      this._historySampleTimer = 0;
    }

    // Compute activity gate — 1.0 if the player is over water OR any
    // history entry is still alive. When this is 0, the shader skips
    // the whole perturbation block (significant per-fragment savings).
    let anyTrailAlive = 0;
    for (let i = 0; i < HISTORY_COUNT; i++) {
      if (this._playerHistoryAge[i] < HISTORY_MAX_AGE) { anyTrailAlive = 1; break; }
    }
    const activity = (this._playerInWater > 0.5 || anyTrailAlive) ? 1.0 : 0.0;

    // Shader uniforms — uTime + uPlayerInWater + uActivity are scalars
    // (assigned per material); position + history arrays are shared by
    // reference so a single mutation above already updated every
    // material's value.
    for (const m of this._materials) {
      m.uniforms.uTime.value = elapsed;
      m.uniforms.uPlayerInWater.value = this._playerInWater;
      m.uniforms.uActivity.value = activity;
    }

    this.#updateSplashes(delta);
  }

  /**
   * Update the shared reflection + refraction RTs. Call once per frame
   * from App.js #tick, BEFORE the main composer render. All water meshes
   * are hidden during the master renders so the RTs don't feedback-sample.
   *
   * @param {THREE.WebGLRenderer} renderer
   * @param {THREE.Camera} camera
   */
  preRender(renderer, camera) {
    if (this.surfaces.length === 0) return;
    for (const s of this.surfaces) s.mesh.visible = false;
    try {
      this._masterReflector.onBeforeRender(renderer, this.scene, camera);
      this._masterRefractor.onBeforeRender(renderer, this.scene, camera);
    } finally {
      for (const s of this.surfaces) s.mesh.visible = true;
    }
  }

  // ── Internals ─────────────────────────────────────────────────────────────

  /**
   * Build a water mesh + material using Water2's shader but pointing at
   * the shared master RTs. The per-mesh textureMatrix uniform is updated
   * in onBeforeRender so each surface's reflection/refraction UVs map
   * correctly through the main camera and the surface's worldMatrix.
   */
  #makeWaterMesh(geometry) {
    const material = new THREE.ShaderMaterial({
      name: WATER_SHADER.name,
      uniforms: THREE.UniformsUtils.merge([
        THREE.UniformsLib['fog'],
        Water2.WaterShader.uniforms,
      ]),
      vertexShader: WATER_SHADER.vertexShader,
      fragmentShader: WATER_SHADER.fragmentShader,
      transparent: true,
      fog: true,
    });
    // Shared references — RTs + normal maps + the player-interaction state.
    material.uniforms.color.value = new THREE.Color().copy(this._currentColor);
    material.uniforms.reflectivity.value = REFLECTIVITY;
    material.uniforms.tReflectionMap.value = this._masterReflector.getRenderTarget().texture;
    material.uniforms.tRefractionMap.value = this._masterRefractor.getRenderTarget().texture;
    material.uniforms.tNormalMap0.value = this._normalMap0;
    material.uniforms.tNormalMap1.value = this._normalMap1;
    material.uniforms.textureMatrix.value = new THREE.Matrix4();
    material.uniforms.config.value = new THREE.Vector4(
      0, FLOW_CYCLE * 0.5, FLOW_CYCLE * 0.5, DISTORTION_SCALE,
    );
    material.uniforms.flowDirection = { value: FLOW_DIRECTION.clone() };
    // Player-interaction uniforms: scalar values are per-material, but the
    // Vector3 + array refs are shared so update() touches them once globally.
    material.uniforms.uTime = { value: 0 };
    material.uniforms.uPlayerPos = { value: this._playerPos };
    material.uniforms.uPlayerInWater = { value: 0 };
    material.uniforms.uPlayerHistory = { value: this._playerHistory };
    material.uniforms.uPlayerHistoryAge = { value: this._playerHistoryAge };
    material.uniforms.uHistoryMaxAge = { value: HISTORY_MAX_AGE };
    material.uniforms.uActivity = { value: 0 };

    const mesh = new THREE.Mesh(geometry, material);
    // Per-mesh textureMatrix update — relies on draw-order serialisation
    // so the uniform value we write is the one bound to this mesh's draw.
    const tm = material.uniforms.textureMatrix.value;
    mesh.onBeforeRender = (renderer, scene, camera) => {
      tm.set(
        0.5, 0.0, 0.0, 0.5,
        0.0, 0.5, 0.0, 0.5,
        0.0, 0.0, 0.5, 0.5,
        0.0, 0.0, 0.0, 1.0,
      );
      tm.multiply(camera.projectionMatrix);
      tm.multiply(camera.matrixWorldInverse);
      tm.multiply(mesh.matrixWorld);
    };

    this._materials.push(material);
    return { mesh, material };
  }

  /**
   * Per-vertex terrain-following ribbon. Local-space encoding chosen so
   * mesh rotation (-π/2 X) + mesh position (0, avgY, 0) produces the
   * correct world XYZ:
   *
   *   (lx, ly, lz) → world (lx, avgY - lz, ly)
   *
   * So for world (wx, wy, wz): local = (wx, wz, avgY - wy).
   */
  #buildRiverGeometry(curve, width, segments, widthJitter) {
    const positions = [];
    const uvs = [];
    const indices = [];

    // First pass: average Y so the mesh's matrixWorld translation sits
    // close to the surface's actual height, keeping the per-mesh texture
    // matrix accurate where the river concentrates.
    let ySum = 0;
    let yCount = 0;
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const p = curve.getPointAt(t);
      ySum += (this.terrain ? this.terrain.heightAt(p.x, p.z) : 0) + RIVER_Y_LIFT;
      yCount++;
    }
    const avgY = ySum / Math.max(1, yCount);

    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const centre = curve.getPointAt(t);
      const tangent = curve.getTangentAt(t);
      // Horizontal perpendicular (XZ-only).
      const px = -tangent.z;
      const pz = tangent.x;
      const plen = Math.hypot(px, pz) || 1;
      const perpX = px / plen;
      const perpZ = pz / plen;

      const halfW = (width + seededJitter(i) * widthJitter) * 0.5;
      const wy = (this.terrain ? this.terrain.heightAt(centre.x, centre.z) : 0) + RIVER_Y_LIFT;
      const localZ = avgY - wy;

      const lwx = centre.x - perpX * halfW;
      const lwz = centre.z - perpZ * halfW;
      const rwx = centre.x + perpX * halfW;
      const rwz = centre.z + perpZ * halfW;

      positions.push(lwx, lwz, localZ);
      positions.push(rwx, rwz, localZ);
      uvs.push(0, t * 10);
      uvs.push(1, t * 10);

      if (i > 0) {
        const a = (i - 1) * 2;
        const b = a + 1;
        const c = i * 2;
        const d = c + 1;
        indices.push(a, c, b);
        indices.push(b, c, d);
      }
    }

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geom.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geom.setIndex(indices);
    geom.computeVertexNormals();
    return { geometry: geom, avgY };
  }

  // ── Splash particles (water-entry feedback) ─────────────────────────────

  /**
   * Pre-allocate one THREE.Points particle pool with SPLASH_MAX particles.
   * Spawning rewrites the next ring of indices; physics + alpha advance
   * each frame in #updateSplashes. Points is the cheapest particle path
   * in three.js — no per-instance matrices, no quad geometry.
   */
  #buildSplashSystem() {
    const max = SPLASH_MAX;
    const positions = new Float32Array(max * 3);
    const velocities = new Float32Array(max * 3);
    const ages = new Float32Array(max);
    const lifes = new Float32Array(max);
    for (let i = 0; i < max; i++) {
      ages[i] = SPLASH_LIFE + 1; // dead
      lifes[i] = SPLASH_LIFE;
    }
    this._splash = { max, positions, velocities, ages, lifes, cursor: 0 };

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('aAge', new THREE.BufferAttribute(ages, 1));
    geom.setAttribute('aLife', new THREE.BufferAttribute(lifes, 1));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const mat = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        // Empirical px-per-meter at 1080p; gl_PointSize divided by viewZ
        // gives perspective scaling without per-particle scale attrs.
        uPxScale: { value: 60 },
      },
      vertexShader: /* glsl */ `
        attribute float aAge;
        attribute float aLife;
        uniform float uPxScale;
        varying float vAlpha;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mv;
          float t = clamp(aAge / aLife, 0.0, 1.0);
          // Fade in fast, out slow.
          vAlpha = (aAge >= aLife) ? 0.0 : pow(1.0 - t, 1.4);
          gl_PointSize = uPxScale * (vAlpha + 0.2) / max(0.5, -mv.z);
        }
      `,
      fragmentShader: /* glsl */ `
        varying float vAlpha;
        void main() {
          vec2 c = gl_PointCoord - vec2(0.5);
          float d = length(c);
          if (d > 0.5) discard;
          float core = smoothstep(0.5, 0.05, d);
          gl_FragColor = vec4(vec3(1.0, 0.98, 0.95), core * vAlpha);
        }
      `,
    });

    this._splashPoints = new THREE.Points(geom, mat);
    this._splashPoints.frustumCulled = false;
    this._splashPoints.name = 'water-splash';
    this._splashPoints.renderOrder = 6;
    this.scene.add(this._splashPoints);
  }

  /** Burst SPLASH_PER_ENTRY particles at the player's feet on water entry. */
  #spawnSplashAt(pos) {
    const s = this._splash;
    // Use the local water surface Y near the player so splashes start at
    // the actual surface, not the player's bone position.
    const waterY = (this.terrain ? this.terrain.heightAt(pos.x, pos.z) : 0) + POOL_Y_LIFT;
    for (let i = 0; i < SPLASH_PER_ENTRY; i++) {
      const idx = s.cursor;
      s.cursor = (s.cursor + 1) % s.max;

      s.positions[idx * 3 + 0] = pos.x;
      s.positions[idx * 3 + 1] = waterY;
      s.positions[idx * 3 + 2] = pos.z;

      const angle = Math.random() * Math.PI * 2;
      const horiz = 0.5 + Math.random() * 1.5; // 0.5–2.0 m/s outward
      s.velocities[idx * 3 + 0] = Math.cos(angle) * horiz;
      s.velocities[idx * 3 + 1] = 0.5 + Math.random();          // 0.5–1.5 m/s up
      s.velocities[idx * 3 + 2] = Math.sin(angle) * horiz;

      s.ages[idx] = 0;
    }
    this._splashPoints.geometry.attributes.position.needsUpdate = true;
    this._splashPoints.geometry.attributes.aAge.needsUpdate = true;
  }

  /** Integrate splash positions + ages; flag attribute uploads. */
  #updateSplashes(delta) {
    const s = this._splash;
    if (!s) return;
    let anyAlive = false;
    const dragHor = Math.exp(-2.0 * delta);
    const dragVer = Math.exp(-0.8 * delta);
    for (let i = 0; i < s.max; i++) {
      if (s.ages[i] >= s.lifes[i]) continue;
      anyAlive = true;
      s.ages[i] += delta;
      // Integrate velocity (gravity then drag) then position.
      s.velocities[i * 3 + 1] += SPLASH_GRAVITY * delta;
      s.velocities[i * 3 + 0] *= dragHor;
      s.velocities[i * 3 + 1] *= dragVer;
      s.velocities[i * 3 + 2] *= dragHor;
      s.positions[i * 3 + 0] += s.velocities[i * 3 + 0] * delta;
      s.positions[i * 3 + 1] += s.velocities[i * 3 + 1] * delta;
      s.positions[i * 3 + 2] += s.velocities[i * 3 + 2] * delta;
    }
    if (anyAlive) {
      this._splashPoints.geometry.attributes.position.needsUpdate = true;
      this._splashPoints.geometry.attributes.aAge.needsUpdate = true;
    }
  }

  // ── Legacy pond ecosystem (lily pads, frog, dock, rocks, reeds) ─────────

  async #buildPondEcosystem(surface) {
    const radius = surface.radius;
    const groupY = surface.position.y;
    const groupX = surface.position.x;
    const groupZ = surface.position.z;
    const subGroup = new THREE.Group();
    subGroup.position.set(groupX, groupY, groupZ);
    this.lilyGroup.add(subGroup);

    const safeLoad = (url) =>
      this.loader.loadGLTF(url).then((g) => g).catch(() => null);

    const [
      lilyLarge, lilySmall,
      rockA, rockB, rockC,
      reed, shortPlant,
      shoreGrass,
      mushroomTan,
      log,
      dock,
      frog,
    ] = await Promise.all([
      safeLoad('/models/nature/lily-large.glb'),
      safeLoad('/models/nature/lily-small.glb'),
      safeLoad('/models/nature/rock-largea.glb'),
      safeLoad('/models/nature/rock-largeb.glb'),
      safeLoad('/models/nature/rock-largec.glb'),
      safeLoad('/models/nature/plant-flattall.glb'),
      safeLoad('/models/nature/plant-flatshort.glb'),
      safeLoad('/models/nature/grass-leafslarge.glb'),
      safeLoad('/models/nature/mushroom-tan.glb'),
      safeLoad('/models/nature/log.glb'),
      safeLoad('/models/extras/dock-long.glb'),
      safeLoad('/models/wildlife/frog.glb'),
    ]);

    const measureSize = (obj) => {
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3();
      obj.traverse((c) => {
        if (c.isMesh && c.geometry) {
          if (!c.geometry.boundingBox) c.geometry.computeBoundingBox();
          const meshBox = c.geometry.boundingBox.clone();
          meshBox.applyMatrix4(c.matrixWorld);
          box.union(meshBox);
        }
      });
      if (box.isEmpty()) return new THREE.Vector3(1, 1, 1);
      return box.getSize(new THREE.Vector3());
    };

    const place = (src, dx, dy, dz, targetMax, yaw, opts = {}) => {
      if (!src) return null;
      const obj = src.scene.clone(true);
      const size = measureSize(obj);
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      obj.scale.setScalar(targetMax / maxDim);
      obj.position.set(dx, dy, dz);
      obj.rotation.y = yaw;
      obj.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = opts.castShadow ?? false;
          c.receiveShadow = true;
        }
      });
      subGroup.add(obj);
      return obj;
    };

    const rockVariants = [rockA, rockB, rockC].filter(Boolean);
    if (rockVariants.length) {
      for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2 + 0.18;
        const r = radius * (0.88 + Math.random() * 0.12);
        const variant = rockVariants[i % rockVariants.length];
        place(
          variant,
          Math.cos(angle) * r,
          -0.05 + Math.random() * 0.08,
          Math.sin(angle) * r,
          1.2 + Math.random() * 0.5,
          Math.random() * Math.PI * 2,
          { castShadow: true },
        );
      }
    }

    if (reed) {
      const reedAngles = [0.3, 1.1, 2.4, 3.5, 4.7, 5.6];
      for (const a of reedAngles) {
        for (let j = 0; j < 3; j++) {
          const jitterA = a + (j - 1) * 0.08;
          const jitterR = radius * (0.93 + Math.random() * 0.05);
          place(
            reed,
            Math.cos(jitterA) * jitterR + (Math.random() - 0.5) * 0.2,
            0.05,
            Math.sin(jitterA) * jitterR + (Math.random() - 0.5) * 0.2,
            0.9 + Math.random() * 0.3,
            Math.random() * Math.PI * 2,
          );
        }
      }
    }

    if (shortPlant) {
      for (let i = 0; i < 10; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = radius * (0.85 + Math.random() * 0.1);
        place(
          shortPlant,
          Math.cos(angle) * r,
          0.05,
          Math.sin(angle) * r,
          0.45 + Math.random() * 0.2,
          Math.random() * Math.PI * 2,
        );
      }
    }

    if (shoreGrass) {
      for (let i = 0; i < 14; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = radius * (0.92 + Math.random() * 0.06);
        place(
          shoreGrass,
          Math.cos(angle) * r,
          0.04,
          Math.sin(angle) * r,
          0.55 + Math.random() * 0.25,
          Math.random() * Math.PI * 2,
        );
      }
    }

    if (mushroomTan) {
      for (let i = 0; i < 3; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = radius * (0.97 + Math.random() * 0.06);
        place(
          mushroomTan,
          Math.cos(angle) * r,
          0.05,
          Math.sin(angle) * r,
          0.4 + Math.random() * 0.15,
          Math.random() * Math.PI * 2,
        );
      }
    }

    if (log) {
      const logA = 1.9;
      place(log, Math.cos(logA) * (radius - 0.6), 0.0, Math.sin(logA) * (radius - 0.6), 2.0, logA + Math.PI / 2, { castShadow: true });
    }

    const lilyPlacements = [
      { src: lilyLarge, dx: -1.8, dz:  1.2, targetMax: 0.95, yaw: 0.7 },
      { src: lilyLarge, dx:  2.1, dz: -0.6, targetMax: 0.85, yaw: 2.1 },
      { src: lilySmall, dx:  1.0, dz:  2.4, targetMax: 0.7,  yaw: 0.0 },
      { src: lilySmall, dx: -2.6, dz: -1.6, targetMax: 0.75, yaw: 1.4 },
      { src: lilySmall, dx:  0.4, dz: -2.8, targetMax: 0.65, yaw: 3.2 },
    ];
    this.lilyMeshes = this.lilyMeshes || [];
    for (const p of lilyPlacements) {
      const lily = place(p.src, p.dx, 0.05, p.dz, p.targetMax, p.yaw);
      if (lily) {
        lily.userData.basePos = { x: p.dx, z: p.dz, phase: Math.random() * Math.PI * 2, baseY: 0.05 };
        this.lilyMeshes.push(lily);
      }
    }

    if (frog && this.lilyMeshes.length) {
      const host = this.lilyMeshes[0];
      const f = frog.scene;
      f.scale.setScalar(0.18);
      f.position.set(host.userData.basePos.x, 0.18, host.userData.basePos.z);
      f.rotation.y = host.rotation.y;
      f.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = true;
          c.receiveShadow = true;
          c.frustumCulled = false;
        }
      });
      subGroup.add(f);
      this.frog = f;
    }

    if (dock) {
      const dockAngle = -1.0;
      const dockDist = radius - 0.4;
      place(
        dock,
        Math.cos(dockAngle) * dockDist,
        -0.05,
        Math.sin(dockAngle) * dockDist,
        2.8,
        dockAngle + Math.PI,
        { castShadow: true },
      );
    }
  }
}
