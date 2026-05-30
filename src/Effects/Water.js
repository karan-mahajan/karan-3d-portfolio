import * as THREE from 'three/webgpu';
import { MeshBasicNodeMaterial } from 'three/webgpu';
import {
  Fn, attribute, uniform, varying,
  positionLocal, positionGeometry, positionWorld,
  vec2, vec3, vec4, float, texture,
  clamp, mix, smoothstep, max, abs, sin, cos, pow, length, dot, cross, normalize, reflect,
  cameraPosition, cameraProjectionMatrix, cameraViewMatrix,
} from 'three/tsl';
import gsap from 'gsap';

/**
 * v3 runtime water — a single TSL node-material surface that covers BOTH the
 * inland basins (ponds / river carved into the terrain) AND the ocean ring
 * beyond the island, with no Reflector/Refractor render targets (those are
 * WebGL-only; this is the WebGPU/TSL backend).
 *
 * How the one plane covers both:
 *   - The Blender terrain is flat at y=0 on the walkable plains and dips to
 *     y=-1.5 in the ponds/river, and its whole perimeter slopes below 0 into
 *     the beach falloff (measured: height range exactly -1.5 → 0.0, bbox ±62.5).
 *   - A flat translucent plane sits at y=WATER_LEVEL_Y (just below the plains).
 *     The OPAQUE terrain at y=0 naturally occludes it via the depth buffer over
 *     dry land, so water only shows through where the ground drops below the
 *     surface: the basins, the shore falloff, and everything past the island
 *     edge (the open ocean). No fragment discard needed for visibility.
 *   - Colour/opacity come from a baked terrain-height texture (depth-based
 *     shallow→deep tint + a soft shoreline fade + foam), plus a distance term
 *     so the open ocean darkens as it runs out toward the fog.
 *
 * Public API (unchanged from the v2 GLSL Water so App/TimeOfDay/Audio bind
 * without edits):
 *   - contains(x,z) / playerOverWater(x,z) → terrain dips below the water line
 *   - setColor(hex) / tweenColor(hex,…)    → shallow tint only
 *   - applyTimeOfDay(mode, opts)           → shallow + deep + foam + sun palette
 *   - update(elapsed, delta, playerPos, sample)
 *   - preRender()                          → no-op (no reflection pass)
 *   - setPhysics(physics)                  → kept for parity (water is non-solid)
 *   - mesh / islandRadius / level          → read by App + section disc mounts
 */

// Surface a touch below the y=0 plains so the opaque land occludes it and the
// wave crests never poke up through the grass (peak displacement ≈ +0.07).
const WATER_LEVEL_Y = -0.08;
// Terrain half-extent (measured bbox ±62.5). Past this the plane is open ocean.
const ISLAND_HALF = 62.5;
// Plane reaches well past the island so the ocean fills to the fog horizon.
const PLANE_SIZE = 340;
const PLANE_SEGMENTS = 72;
// Scalar shore radius handed to AudioManager.setOceanProximity — roughly where
// the dry plains give way to the perimeter falloff.
const AUDIO_SHORE_RADIUS = 52;

// Splash particles — instanced camera-facing quads (ported from the v2 GL
// Points so it runs on the WebGPU backend), ring-buffer writes.
const SPLASH_MAX = 80;
const SPLASH_SPAWN_INTERVAL = 0.15;
const SPLASH_PER_BURST_WALK = 5;
const SPLASH_PER_BURST_RUN = 8;
const SPLASH_LIFE = 0.45;
const SPLASH_GRAVITY = -9.8;
const SPLASH_AUDIO_INTERVAL = 0.55;

const DAY_PALETTE = Object.freeze({
  shallow: '#3f9ab8',
  deep:    '#0b3147',
  foam:    '#e6f2f8',
  sky:     '#a6c8df', // fresnel reflection tint
  sun:     [60, 55, 40],
});
const NIGHT_PALETTE = Object.freeze({
  shallow: '#1a3a5a',
  deep:    '#081826',
  foam:    '#3a4a5a',
  sky:     '#2a3c52',
  sun:     [-40, 45, -40],
});

// Fine ripple waves driving the animated normal (NOT geometry — fragment only,
// so they shimmer without poking the surface above the y=0 grass lip). Each:
// [dirX, dirZ (normalised), spatial frequency, slope amplitude, scroll speed].
const RIPPLES = [
  [0.95, 0.31, 0.9, 0.050, 1.15],
  [-0.45, 0.89, 1.7, 0.032, 1.70],
  [0.62, -0.78, 2.6, 0.020, 2.30],
  [-0.80, -0.60, 4.1, 0.012, 0.95],
];

export class Water {
  /**
   * @param {THREE.Scene} scene
   * @param {{heights:Float32Array, segments:number, size:number, bboxMin:THREE.Vector3, heightAt:Function}} terrain
   * @param {object} [opts]
   */
  constructor(scene, terrain, _opts = {}) {
    this.scene = scene;
    this.terrain = terrain;
    this.islandCenter = new THREE.Vector2(0, 0);
    this.islandRadius = AUDIO_SHORE_RADIUS;
    this.level = WATER_LEVEL_Y;
    this.waterLevel = WATER_LEVEL_Y;
    // App.js sets these post-boot.
    this.audio = null;
    this.physics = null;

    // Plain THREE.Color/Vector3 state that gsap tweens; pushed into the GPU
    // uniforms each frame in update() (keeps gsap off the node internals).
    this.shallowColor = new THREE.Color(DAY_PALETTE.shallow);
    this.deepColor = new THREE.Color(DAY_PALETTE.deep);
    this.foamColor = new THREE.Color(DAY_PALETTE.foam);
    this.skyColor = new THREE.Color(DAY_PALETTE.sky);
    this.sunPos = new THREE.Vector3(...DAY_PALETTE.sun);

    this.#buildHeightTexture();
    this.#buildSurface();
    this.#buildSplashSystem();

    this._splashTimer = 0;
    this._audioSplashTimer = 0;
    this._playerInWaterPrev = 0;
  }

  // ── Terrain depth grounding (half-float so it's linearly filterable) ────────
  #buildHeightTexture() {
    const t = this.terrain;
    const verts = (t?.segments ?? 0) + 1;
    if (!t?.heights || verts < 2) {
      this.heightTex = null;
      this.terrainMin = new THREE.Vector2(-ISLAND_HALF, -ISLAND_HALF);
      this.terrainSpan = new THREE.Vector2(ISLAND_HALF * 2, ISLAND_HALF * 2);
      return;
    }
    // src[u*verts + w] (u = X index, w = Z index). Transpose into row-major
    // (w outer) so the DataTexture's U axis is X and V axis is Z.
    const src = t.heights;
    const data = new Uint16Array(verts * verts);
    for (let u = 0; u < verts; u++) {
      for (let w = 0; w < verts; w++) {
        data[w * verts + u] = THREE.DataUtils.toHalfFloat(src[u * verts + w]);
      }
    }
    const tex = new THREE.DataTexture(data, verts, verts, THREE.RedFormat, THREE.HalfFloatType);
    tex.wrapS = THREE.ClampToEdgeWrapping;
    tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.generateMipmaps = false;
    tex.needsUpdate = true;
    this.heightTex = tex;
    this.terrainMin = new THREE.Vector2(t.bboxMin.x, t.bboxMin.z);
    this.terrainSpan = new THREE.Vector2(t.size, t.size);
  }

  // ── Water surface ───────────────────────────────────────────────────────────
  #buildSurface() {
    this.uTime = uniform(0);
    this.uShallow = uniform(vec3(this.shallowColor.r, this.shallowColor.g, this.shallowColor.b));
    this.uDeep = uniform(vec3(this.deepColor.r, this.deepColor.g, this.deepColor.b));
    this.uFoam = uniform(vec3(this.foamColor.r, this.foamColor.g, this.foamColor.b));
    this.uSky = uniform(vec3(this.skyColor.r, this.skyColor.g, this.skyColor.b));
    this.uSunPos = uniform(vec3(this.sunPos.x, this.sunPos.y, this.sunPos.z));
    this.uPlayerPos = uniform(vec2(0, 0));
    this.uPlayerInWater = uniform(0);
    this.uPlayerSpeed = uniform(0);
    this.uWaterLevel = uniform(WATER_LEVEL_Y);
    this.uIslandHalf = uniform(ISLAND_HALF);
    this.uTerrainMin = uniform(vec2(this.terrainMin.x, this.terrainMin.y));
    this.uTerrainSpan = uniform(vec2(this.terrainSpan.x, this.terrainSpan.y));

    // Depth below the surface (basin/ocean), passed vertex→fragment so colour +
    // opacity share one height-texture sample. vDepthTerrain is the pure
    // ground-relative depth (drives the shoreline foam/fade); vDepth folds in
    // the open-ocean distance term so the sea darkens outward.
    const vDepthTerrain = varying(float(0), 'vWaterDepthT');
    const vDepth = varying(float(0), 'vWaterDepth');

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

    mat.positionNode = Fn(() => {
      // After the geometry's -π/2 X rotation, local x,z span the surface and
      // y is vertical; the mesh sits at the origin in XZ so local xz == world xz.
      const p = positionLocal.toVar();
      const t = this.uTime;

      // Gentle low-frequency swell — small amplitude so crests stay below the
      // y=0 grass lip (sum ≤ 0.05; the lively shimmer comes from the fragment
      // ripple NORMAL, not from displacing the geometry).
      const w1 = sin(p.x.mul(0.18).add(t.mul(0.70))).mul(0.022);
      const w2 = sin(p.z.mul(0.25).add(t.mul(0.55))).mul(0.016);
      const w3 = sin(p.x.add(p.z).mul(0.13).add(t.mul(0.90))).mul(0.012);
      p.y.addAssign(w1.add(w2).add(w3));

      // Player wake — concentric rings expanding from the feet while wading.
      const d = length(vec2(p.x, p.z).sub(this.uPlayerPos));
      const ripple = sin(d.mul(6.0).sub(t.mul(4.0))).mul(0.020)
        .mul(smoothstep(8.0, 0.5, d))
        .mul(this.uPlayerInWater)
        .mul(this.uPlayerSpeed.mul(0.7).add(0.3));
      p.y.addAssign(ripple);

      // Depth from the baked terrain height (clamped → ocean reads the slope
      // edge value, which is already below the water line).
      const hUv = clamp(vec2(p.x, p.z).sub(this.uTerrainMin).div(this.uTerrainSpan), 0.0, 1.0);
      const terrH = this.heightTex ? texture(this.heightTex, hUv).r : float(-1.0);
      const depthTerrain = max(this.uWaterLevel.sub(terrH), 0.0);
      const distBeyond = max(max(abs(p.x), abs(p.z)).sub(this.uIslandHalf), 0.0);
      vDepthTerrain.assign(depthTerrain);
      vDepth.assign(depthTerrain.add(distBeyond.mul(0.06)));
      return p;
    })();

    // Animated surface normal — sum of scrolling directional ripples, normal
    // taken from the analytic slope (∂h/∂x, ∂h/∂z). Fragment-only, so it adds
    // fine motion/shimmer without displacing geometry into the grass.
    const rippleNormal = (p2, t) => {
      const acc = vec2(0, 0).toVar();
      for (const [dx, dz, freq, amp, speed] of RIPPLES) {
        const phase = p2.x.mul(dx).add(p2.y.mul(dz)).mul(freq).add(t.mul(speed));
        const slope = cos(phase).mul(amp * freq);
        acc.addAssign(vec2(slope.mul(dx), slope.mul(dz)));
      }
      return normalize(vec3(acc.x.negate(), 1.0, acc.y.negate()));
    };

    mat.colorNode = Fn(() => {
      const wp = positionWorld;
      const p2 = vec2(wp.x, wp.z);
      const t = this.uTime;
      const N = rippleNormal(p2, t).toVar();
      const V = normalize(cameraPosition.sub(wp));

      // Depth tint (shallow → deep). Basins only reach ~1.4 m, so the ramp
      // tops out near 1.3 m for ponds to read their deep core; the open-ocean
      // distance term in vDepth carries the sea the rest of the way to deep.
      const depthF = smoothstep(0.0, 1.3, vDepth);
      const col = mix(this.uShallow, this.uDeep, depthF).toVar();

      // Fresnel — looking straight down shows the water body; at grazing angles
      // the surface turns reflective. Reflect a time-of-day sky tint, brighter
      // toward the (reflected) sky.
      const fres = pow(clamp(float(1.0).sub(max(dot(N, V), 0.0)), 0.0, 1.0), 4.0);
      const refl = reflect(V.negate(), N);
      const skyTint = mix(this.uSky.mul(0.55), this.uSky.mul(1.2), clamp(refl.y, 0.0, 1.0));
      col.assign(mix(col, skyTint, fres.mul(0.6)));

      // Moving specular sun/moon glint off the rippled normal — the twinkle.
      const L = normalize(this.uSunPos.sub(wp));
      const specR = reflect(L.negate(), N);
      const spec = pow(max(dot(specR, V), 0.0), 140.0).mul(0.9);
      col.addAssign(vec3(1.0, 0.96, 0.86).mul(spec));

      // Shoreline foam band — bright line where the ground is just under water,
      // breathing in/out like a tide.
      const shoreWave = sin(this.uTime.mul(0.8)).mul(0.05);
      const foam = smoothstep(0.30, 0.05, vDepthTerrain.add(shoreWave)).mul(0.5);
      col.assign(mix(col, this.uFoam, foam));

      // Player foam ring while wading.
      const pd = length(p2.sub(this.uPlayerPos));
      const playerFoam = smoothstep(2.0, 0.3, pd).mul(this.uPlayerInWater).mul(0.3);
      col.assign(mix(col, this.uFoam, playerFoam));

      return col;
    })();

    mat.opacityNode = Fn(() => {
      // Deeper water is more opaque; at grazing angles the surface turns fully
      // reflective (Fresnel) so the far ocean reads solid while shallow water
      // viewed from above stays see-through. Fade to nothing right at the
      // waterline so the shore meets the sand with a soft edge (and the wave
      // crest tips that brush y=0 don't draw a hard rim on the grass).
      const V = normalize(cameraPosition.sub(positionWorld));
      const grazing = pow(clamp(float(1.0).sub(max(V.y, 0.0)), 0.0, 1.0), 3.0);
      const depthOp = mix(float(0.50), float(0.90), smoothstep(0.0, 2.0, vDepth));
      const op = mix(depthOp, float(0.97), grazing.mul(0.75));
      const edge = smoothstep(0.0, 0.06, vDepth);
      return op.mul(edge);
    })();

    const geom = new THREE.PlaneGeometry(PLANE_SIZE, PLANE_SIZE, PLANE_SEGMENTS, PLANE_SEGMENTS);
    geom.rotateX(-Math.PI / 2);
    this.material = mat;
    this.mesh = new THREE.Mesh(geom, mat);
    this.mesh.position.y = WATER_LEVEL_Y;
    this.mesh.name = 'water';
    this.mesh.renderOrder = 2; // after opaque terrain + grass
    this.mesh.frustumCulled = false;
    this.mesh.userData.noTorchRaycast = true;
    this.scene.add(this.mesh);
  }

  // ── Public API ──────────────────────────────────────────────────────────────

  /** True when the ground at (x,z) dips below the water line (basin or ocean). */
  contains(x, z) {
    if (!this.terrain?.heightAt) return false;
    return this.terrain.heightAt(x, z) < this.waterLevel;
  }
  playerOverWater(x, z) { return this.contains(x, z); }

  setColor(hex) { this.shallowColor.set(hex); }
  tweenColor(hex, duration = 2.0, ease = 'sine.inOut') {
    const tmp = new THREE.Color(hex);
    gsap.to(this.shallowColor, { r: tmp.r, g: tmp.g, b: tmp.b, duration, ease });
  }

  /** Drives the full day/night palette — TimeOfDay calls this. */
  applyTimeOfDay(mode, { tween = false, duration = 2.0, ease = 'sine.inOut' } = {}) {
    const p = mode === 'night' ? NIGHT_PALETTE : DAY_PALETTE;
    const shallow = new THREE.Color(p.shallow);
    const deep = new THREE.Color(p.deep);
    const foam = new THREE.Color(p.foam);
    const sky = new THREE.Color(p.sky);
    if (tween) {
      gsap.to(this.shallowColor, { r: shallow.r, g: shallow.g, b: shallow.b, duration, ease });
      gsap.to(this.deepColor, { r: deep.r, g: deep.g, b: deep.b, duration, ease });
      gsap.to(this.foamColor, { r: foam.r, g: foam.g, b: foam.b, duration, ease });
      gsap.to(this.skyColor, { r: sky.r, g: sky.g, b: sky.b, duration, ease });
      gsap.to(this.sunPos, { x: p.sun[0], y: p.sun[1], z: p.sun[2], duration, ease });
    } else {
      this.shallowColor.copy(shallow);
      this.deepColor.copy(deep);
      this.foamColor.copy(foam);
      this.skyColor.copy(sky);
      this.sunPos.set(p.sun[0], p.sun[1], p.sun[2]);
    }
  }

  setPhysics(physics) { this.physics = physics; }

  // ── Per-frame ───────────────────────────────────────────────────────────────
  /**
   * @param {number} elapsed
   * @param {number} delta
   * @param {THREE.Vector3|null} playerPos
   * @param {{moving:boolean, speed:number}|null} sample
   */
  update(elapsed, delta, playerPos, sample = null) {
    this.uTime.value = elapsed;
    // Push tweened colour/sun state into the GPU uniforms.
    this.uShallow.value.set(this.shallowColor.r, this.shallowColor.g, this.shallowColor.b);
    this.uDeep.value.set(this.deepColor.r, this.deepColor.g, this.deepColor.b);
    this.uFoam.value.set(this.foamColor.r, this.foamColor.g, this.foamColor.b);
    this.uSky.value.set(this.skyColor.r, this.skyColor.g, this.skyColor.b);
    this.uSunPos.value.set(this.sunPos.x, this.sunPos.y, this.sunPos.z);

    if (playerPos) {
      this.uPlayerPos.value.set(playerPos.x, playerPos.z);
      const inWater = this.playerOverWater(playerPos.x, playerPos.z) ? 1.0 : 0.0;
      this.uPlayerInWater.value = inWater;
      const rawSpeed = sample && sample.moving ? sample.speed : 0;
      this.uPlayerSpeed.value = Math.min(1, rawSpeed / 8.0);

      const justEntered = inWater > 0.5 && this._playerInWaterPrev < 0.5;
      this._playerInWaterPrev = inWater;
      if (justEntered) {
        this.#spawnSplashBurst(playerPos, 14);
        if (this.audio) this.audio.playSplash({ entry: true });
        this._audioSplashTimer = SPLASH_AUDIO_INTERVAL;
      }

      this._splashTimer -= delta;
      this._audioSplashTimer -= delta;
      const running = (sample?.speed ?? 0) > 5;
      if (inWater > 0.5 && sample && sample.moving && this._splashTimer <= 0) {
        this._splashTimer = SPLASH_SPAWN_INTERVAL;
        this.#spawnSplashBurst(playerPos, running ? SPLASH_PER_BURST_RUN : SPLASH_PER_BURST_WALK);
      }
      if (inWater > 0.5 && sample && sample.moving && this._audioSplashTimer <= 0) {
        this._audioSplashTimer = SPLASH_AUDIO_INTERVAL;
        if (this.audio) this.audio.playSplash({ volume: running ? 1.0 : 0.7 });
      }
    } else {
      this.uPlayerInWater.value = 0;
      this.uPlayerSpeed.value = 0;
    }
    this.#updateSplashes(delta);
  }

  /** No-op — App.js still calls this once per frame; no reflection RT. */
  preRender() {}

  // ── Splash particles (instanced camera-facing quads) ────────────────────────
  #buildSplashSystem() {
    // Base quad: 4 corners in [-0.5, 0.5], two triangles.
    const base = new THREE.BufferGeometry();
    base.setAttribute('position', new THREE.Float32BufferAttribute([
      -0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0,
    ], 3));
    base.setIndex([0, 1, 2, 0, 2, 3]);

    const geom = new THREE.InstancedBufferGeometry();
    geom.index = base.index;
    geom.attributes.position = base.attributes.position;
    geom.instanceCount = SPLASH_MAX;
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const positions = new Float32Array(SPLASH_MAX * 3);
    const ages = new Float32Array(SPLASH_MAX);
    const lifes = new Float32Array(SPLASH_MAX);
    for (let i = 0; i < SPLASH_MAX; i++) { ages[i] = SPLASH_LIFE + 1; lifes[i] = SPLASH_LIFE; }
    geom.setAttribute('aPos', new THREE.InstancedBufferAttribute(positions, 3));
    geom.setAttribute('aAge', new THREE.InstancedBufferAttribute(ages, 1));
    geom.setAttribute('aLife', new THREE.InstancedBufferAttribute(lifes, 1));

    this._splash = { positions, ages, lifes, velocities: new Float32Array(SPLASH_MAX * 3), cursor: 0 };

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const vAlpha = varying(float(0), 'vSplashAlpha');
    const vCorner = varying(vec2(0, 0), 'vSplashCorner');
    mat.vertexNode = Fn(() => {
      const center = attribute('aPos');
      const age = attribute('aAge');
      const life = attribute('aLife');
      const t = clamp(age.div(life), 0.0, 1.0);
      // Dead particles carry age >= life → t = 1 → (1-t) = 0 → alpha 0 (no
      // branch needed). Live droplets shrink + fade as they age.
      const size = float(0.16).mul(t.oneMinus().mul(0.8).add(0.2));
      const corner = positionGeometry.xy;
      vCorner.assign(corner);
      vAlpha.assign(pow(clamp(t.oneMinus(), 0.0, 1.0), 1.4));

      const toCam = normalize(cameraPosition.sub(center));
      const right = normalize(cross(vec3(0, 1, 0), toCam));
      const up = cross(toCam, right);
      const worldPos = center
        .add(right.mul(corner.x.mul(size)))
        .add(up.mul(corner.y.mul(size)));
      return cameraProjectionMatrix.mul(cameraViewMatrix.mul(vec4(worldPos, 1.0)));
    })();
    mat.colorNode = vec3(1.0, 0.98, 0.95);
    // Round the quad into a soft dot.
    mat.opacityNode = vAlpha.mul(smoothstep(0.5, 0.08, length(vCorner)));

    this._splashMesh = new THREE.Mesh(geom, mat);
    this._splashMesh.frustumCulled = false;
    this._splashMesh.name = 'water-splash';
    this._splashMesh.renderOrder = 6;
    this._splashMesh.userData.noTorchRaycast = true;
    this.scene.add(this._splashMesh);
    this._splashGeom = geom;
  }

  #spawnSplashBurst(pos, count) {
    const s = this._splash;
    for (let i = 0; i < count; i++) {
      const idx = s.cursor;
      s.cursor = (s.cursor + 1) % SPLASH_MAX;
      s.positions[idx * 3 + 0] = pos.x + (Math.random() - 0.5) * 0.5;
      s.positions[idx * 3 + 1] = WATER_LEVEL_Y + 0.05;
      s.positions[idx * 3 + 2] = pos.z + (Math.random() - 0.5) * 0.5;
      const angle = Math.random() * Math.PI * 2;
      const horiz = 0.5 + Math.random() * 1.5;
      s.velocities[idx * 3 + 0] = Math.cos(angle) * horiz;
      s.velocities[idx * 3 + 1] = 1.5 + Math.random() * 1.5;
      s.velocities[idx * 3 + 2] = Math.sin(angle) * horiz;
      s.ages[idx] = 0;
    }
    this._splashGeom.attributes.aPos.needsUpdate = true;
    this._splashGeom.attributes.aAge.needsUpdate = true;
  }

  #updateSplashes(delta) {
    const s = this._splash;
    let anyAlive = false;
    const dragHor = Math.exp(-2.0 * delta);
    const dragVer = Math.exp(-0.8 * delta);
    for (let i = 0; i < SPLASH_MAX; i++) {
      if (s.ages[i] >= s.lifes[i]) continue;
      anyAlive = true;
      s.ages[i] += delta;
      s.velocities[i * 3 + 1] += SPLASH_GRAVITY * delta;
      s.velocities[i * 3 + 0] *= dragHor;
      s.velocities[i * 3 + 1] *= dragVer;
      s.velocities[i * 3 + 2] *= dragHor;
      s.positions[i * 3 + 0] += s.velocities[i * 3 + 0] * delta;
      s.positions[i * 3 + 1] += s.velocities[i * 3 + 1] * delta;
      s.positions[i * 3 + 2] += s.velocities[i * 3 + 2] * delta;
      if (s.positions[i * 3 + 1] < WATER_LEVEL_Y - 0.1) s.ages[i] = s.lifes[i];
    }
    if (anyAlive) {
      this._splashGeom.attributes.aPos.needsUpdate = true;
      this._splashGeom.attributes.aAge.needsUpdate = true;
    }
  }

  dispose() {
    this.scene.remove(this.mesh);
    this.scene.remove(this._splashMesh);
    this.mesh?.geometry?.dispose();
    this.material?.dispose();
    this.heightTex?.dispose();
    this._splashGeom?.dispose();
  }
}
