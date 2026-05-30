import * as THREE from 'three/webgpu';
import gsap from 'gsap';

/**
 * Ocean — a single shader-driven plane that surrounds the island. Replaces
 * the Sprint-12 multi-pool + river system; no Reflector/Refractor render
 * targets. The sun glint, depth tint, foam line, sparkle and player wake
 * are all fragment-shader fakes, so the surface costs roughly one extra
 * draw call per frame.
 *
 * Layout assumptions (must match Terrain.js):
 *   - Island centred at world origin (0, 0)
 *   - Playable land radius ≈ ISLAND_RADIUS (45)
 *   - Water surface at y = 0
 *   - The terrain rises above y=0 inside the island and slopes down through
 *     a sandy shore to roughly y=-2 (ocean floor) by the time it reaches
 *     the water-plane edge — see Terrain.#displaceVertices.
 *
 * Public API:
 *   - contains(x, z) / playerOverWater  → XZ distance vs WATER_ENTRY_RADIUS
 *   - setColor(hex) / tweenColor(hex, …) → sets the shallow tint only
 *   - applyTimeOfDay(mode, opts)        → animates shallow + deep + foam + sun
 *   - update(elapsed, delta, playerPos, sample)
 *   - preRender(renderer, camera)       → no-op (no reflection pass)
 */

const PLANE_SIZE = 300;
const PLANE_SEGMENTS = 48;
const WATER_LEVEL_Y = 0;
const ISLAND_RADIUS = 45;
// Match ISLAND_RADIUS so wading slowdown + splashes only trigger once the
// player has actually stepped off the visible shore. Earlier we kept this
// 2 m inside the radius, but the fragment-shader discard above hides any
// water inside the island, so a separate trigger zone there has no payoff.
const WATER_ENTRY_RADIUS = 45;

// Splash particles — pre-allocated Points pool, ring-buffer writes.
const SPLASH_MAX = 80;
const SPLASH_SPAWN_INTERVAL = 0.15; // seconds between bursts while moving
const SPLASH_PER_BURST_WALK = 5;
const SPLASH_PER_BURST_RUN = 8;
const SPLASH_LIFE = 0.45;
const SPLASH_GRAVITY = -9.8;
// Audio splashes are sparser than visual splashes — one .wav playing every
// 0.55 s reads as footsteps in water; faster than that turns into a smear.
const SPLASH_AUDIO_INTERVAL = 0.55;

/** Deterministic [0, 1) RNG so shore decor placement is reproducible. */
function mulberry(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** World-space bounding box size for a freshly cloned GLB scene. */
function measureSize(obj) {
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
}

const DAY_PALETTE = Object.freeze({
  shallow: '#4a9aba',
  deep:    '#1a4a6a',
  foam:    '#ddeef5',
  sun:     new THREE.Vector3(60, 55, 40),
});
const NIGHT_PALETTE = Object.freeze({
  shallow: '#1a3a5a',
  deep:    '#0a1a2a',
  foam:    '#3a4a5a',
  sun:     new THREE.Vector3(-40, 45, -40),
});

// The plane geometry is rotated -π/2 around X at construction (below), so
// after rotation a vertex's local-space x,z span the water surface and y
// is the vertical axis. Waves modify pos.y; ripples sample pos.xz against
// the world-space player XZ.
const VERTEX_SHADER = /* glsl */ `
  #include <common>
  #include <fog_pars_vertex>

  uniform float uTime;
  uniform vec2  uPlayerPos;
  uniform float uPlayerInWater;
  uniform float uPlayerSpeed;

  varying vec3  vWorldPos;
  varying float vElevation;

  void main() {
    vec3 pos = position;

    float wave1 = sin(pos.x * 0.30 + uTime * 0.8) * 0.15;
    float wave2 = sin(pos.z * 0.40 + uTime * 0.6) * 0.10;
    float wave3 = sin((pos.x + pos.z) * 0.20 + uTime * 1.0) * 0.08;
    float wave4 = sin(pos.x * 0.80 - uTime * 1.2) * 0.04;
    float wave5 = cos(pos.z * 0.60 + uTime * 0.9) * 0.05;
    pos.y += wave1 + wave2 + wave3 + wave4 + wave5;

    // Player wake — concentric rings expanding from feet, only when in water.
    if (uPlayerInWater > 0.5) {
      float distToPlayer = distance(pos.xz, uPlayerPos);
      float ripple = sin(distToPlayer * 6.0 - uTime * 4.0) * 0.04;
      ripple *= smoothstep(8.0, 0.5, distToPlayer);
      ripple *= (0.3 + uPlayerSpeed * 0.7);
      pos.y += ripple;
    }

    vElevation = pos.y;
    vWorldPos = (modelMatrix * vec4(pos, 1.0)).xyz;
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    #include <fog_vertex>
  }
`;

const FRAGMENT_SHADER = /* glsl */ `
  #include <common>
  #include <fog_pars_fragment>

  uniform float uTime;
  uniform vec3  uShallowColor;
  uniform vec3  uDeepColor;
  uniform vec3  uFoamColor;
  uniform vec2  uIslandCenter;
  uniform float uIslandRadius;
  uniform vec3  uSunPosition;
  uniform float uPlayerInWater;
  uniform vec2  uPlayerPos;

  varying vec3  vWorldPos;
  varying float vElevation;

  void main() {
    float dist = distance(vWorldPos.xz, uIslandCenter);
    // Inside the island the terrain sits above the water plane (~y=0.02),
    // but our vertex waves displace the surface by up to ±0.42 m — without
    // this discard the wave peaks bleed up through the grass and read as
    // blue patches on the lawn. Discarding here also saves fragment work
    // over the entire island disc.
    if (dist < uIslandRadius) discard;
    float depthFactor = smoothstep(uIslandRadius, uIslandRadius + 30.0, dist);
    vec3 color = mix(uShallowColor, uDeepColor, depthFactor);

    float distFromShore = dist - uIslandRadius;
    float opacity = mix(0.45, 0.9, smoothstep(0.0, 20.0, distFromShore));

    // Shoreline foam band — animates in/out like tides, with a trailing line.
    float shoreWave = sin(uTime * 0.8) * 2.0;
    float shoreDist = distFromShore - shoreWave;
    float foam = 0.0;
    if (distFromShore > -5.0 && distFromShore < 10.0) {
      foam  = smoothstep(1.5, 0.0, abs(shoreDist)) * 0.5;
      foam += smoothstep(1.0, 0.0, abs(shoreDist - 3.0)) * 0.25;
    }
    color = mix(color, uFoamColor, foam);

    if (uPlayerInWater > 0.5) {
      float distToPlayer = distance(vWorldPos.xz, uPlayerPos);
      float playerFoam = smoothstep(2.0, 0.3, distToPlayer) * 0.3;
      color = mix(color, uFoamColor, playerFoam);
    }

    // Fake sun/moon glint — pixels under the sun direction read brightest.
    vec3 toSun = normalize(uSunPosition - vWorldPos);
    float sunGlint = pow(max(dot(toSun, vec3(0.0, 1.0, 0.0)), 0.0), 128.0);
    color += vec3(1.0, 0.95, 0.85) * sunGlint * 0.4;

    float sparkle = sin(vWorldPos.x * 25.0 + uTime * 3.0)
                  * sin(vWorldPos.z * 25.0 + uTime * 2.0);
    sparkle = smoothstep(0.93, 1.0, sparkle) * 0.12;
    color += sparkle;

    float highlight = smoothstep(0.03, 0.08, vElevation) * 0.15;
    color += highlight;

    gl_FragColor = vec4(color, opacity);
    #include <fog_fragment>
  }
`;

export class Water {
  constructor(scene, loader, terrain, _opts = {}) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    this.islandCenter = new THREE.Vector2(0, 0);
    this.islandRadius = ISLAND_RADIUS;
    this.waterEntryRadius = WATER_ENTRY_RADIUS;

    this.uniforms = {
      uTime:          { value: 0 },
      uShallowColor:  { value: new THREE.Color(DAY_PALETTE.shallow) },
      uDeepColor:     { value: new THREE.Color(DAY_PALETTE.deep) },
      uFoamColor:     { value: new THREE.Color(DAY_PALETTE.foam) },
      uIslandCenter:  { value: this.islandCenter.clone() },
      uIslandRadius:  { value: this.islandRadius },
      uPlayerPos:     { value: new THREE.Vector2(0, 0) },
      uPlayerInWater: { value: 0 },
      uPlayerSpeed:   { value: 0 },
      uSunPosition:   { value: DAY_PALETTE.sun.clone() },
    };
    this.material = new THREE.ShaderMaterial({
      // Merge fog uniforms in so the <fog_*> includes find what they expect.
      uniforms: THREE.UniformsUtils.merge([
        THREE.UniformsLib.fog,
        this.uniforms,
      ]),
      vertexShader: VERTEX_SHADER,
      fragmentShader: FRAGMENT_SHADER,
      transparent: true,
      side: THREE.DoubleSide,
      depthWrite: false,
      fog: true,
    });
    // UniformsUtils.merge clones our uniform objects, so reassign refs we
    // need to mutate directly each frame.
    this.uniforms = this.material.uniforms;

    const geom = new THREE.PlaneGeometry(PLANE_SIZE, PLANE_SIZE, PLANE_SEGMENTS, PLANE_SEGMENTS);
    // Bake the rotation into the geometry so the shader's pos.x/pos.z map
    // directly to world XZ — see uPlayerPos sampling in the vertex shader.
    geom.rotateX(-Math.PI / 2);
    this.mesh = new THREE.Mesh(geom, this.material);
    this.mesh.position.y = WATER_LEVEL_Y;
    this.mesh.name = 'ocean';
    this.mesh.renderOrder = 1;
    this.scene.add(this.mesh);

    this.#buildSplashSystem();
    this._splashTimer = 0;
    this._audioSplashTimer = 0;
    this._playerInWaterPrev = 0;
    // App.js sets this after boot — kept null until then so splashes during
    // the loading screen are silent.
    this.audio = null;

    // Shore decor group — lily pads, half-submerged rocks, reeds. Populated
    // asynchronously by loadShoreDecor() once the loader is available; lives
    // here so update() can bob the lily pads each frame.
    this.shoreGroup = new THREE.Group();
    this.shoreGroup.name = 'ocean-shore-decor';
    this.scene.add(this.shoreGroup);
    /** @type {Array<{mesh:THREE.Object3D, baseY:number, phase:number, amp:number}>} */
    this.lilyPads = [];
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /** True when the XZ point is past the water entry radius. */
  contains(x, z) {
    const dx = x - this.islandCenter.x;
    const dz = z - this.islandCenter.y;
    return Math.hypot(dx, dz) > this.waterEntryRadius;
  }
  playerOverWater(x, z) { return this.contains(x, z); }

  /** Single-color compat for callers that only set one hex. */
  setColor(hex) { this.uniforms.uShallowColor.value.set(hex); }
  tweenColor(hex, duration = 2.0, ease = 'sine.inOut') {
    const tmp = new THREE.Color(hex);
    gsap.to(this.uniforms.uShallowColor.value, {
      r: tmp.r, g: tmp.g, b: tmp.b, duration, ease,
    });
  }

  /** Drives the full day/night palette at once — TimeOfDay calls this. */
  applyTimeOfDay(mode, { tween = false, duration = 2.0, ease = 'sine.inOut' } = {}) {
    const p = mode === 'night' ? NIGHT_PALETTE : DAY_PALETTE;
    const shallow = new THREE.Color(p.shallow);
    const deep    = new THREE.Color(p.deep);
    const foam    = new THREE.Color(p.foam);
    if (tween) {
      gsap.to(this.uniforms.uShallowColor.value, { r: shallow.r, g: shallow.g, b: shallow.b, duration, ease });
      gsap.to(this.uniforms.uDeepColor.value,    { r: deep.r,    g: deep.g,    b: deep.b,    duration, ease });
      gsap.to(this.uniforms.uFoamColor.value,    { r: foam.r,    g: foam.g,    b: foam.b,    duration, ease });
      gsap.to(this.uniforms.uSunPosition.value,  { x: p.sun.x,   y: p.sun.y,   z: p.sun.z,   duration, ease });
    } else {
      this.uniforms.uShallowColor.value.copy(shallow);
      this.uniforms.uDeepColor.value.copy(deep);
      this.uniforms.uFoamColor.value.copy(foam);
      this.uniforms.uSunPosition.value.copy(p.sun);
    }
  }

  // ── Per-frame ─────────────────────────────────────────────────────────────

  /**
   * @param {number} elapsed
   * @param {number} delta
   * @param {THREE.Vector3|null} playerPos
   * @param {{moving:boolean, speed:number}|null} sample - PlayerController.sample()
   */
  update(elapsed, delta, playerPos, sample = null) {
    this.uniforms.uTime.value = elapsed;
    if (playerPos) {
      this.uniforms.uPlayerPos.value.set(playerPos.x, playerPos.z);
      const inWater = this.playerOverWater(playerPos.x, playerPos.z) ? 1.0 : 0.0;
      this.uniforms.uPlayerInWater.value = inWater;

      const rawSpeed = sample && sample.moving ? sample.speed : 0;
      this.uniforms.uPlayerSpeed.value = Math.min(1, rawSpeed / 8.0);

      // Entry: one big visual burst + the louder jump-into-water clip.
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
        this.#spawnSplashBurst(
          playerPos,
          running ? SPLASH_PER_BURST_RUN : SPLASH_PER_BURST_WALK,
        );
      }
      // Footstep splash audio runs on its own slower cadence — playing one
      // .wav every visual burst (~7/s) smears into noise; ~2/s reads as steps.
      if (inWater > 0.5 && sample && sample.moving && this._audioSplashTimer <= 0) {
        this._audioSplashTimer = SPLASH_AUDIO_INTERVAL;
        if (this.audio) this.audio.playSplash({ volume: running ? 1.0 : 0.7 });
      }
    } else {
      this.uniforms.uPlayerInWater.value = 0;
      this.uniforms.uPlayerSpeed.value = 0;
    }
    this.#updateSplashes(delta);

    // Lily-pad bob — soft vertical oscillation around the resting water Y.
    // Phase per lily so they don't bob in unison.
    if (this.lilyPads.length) {
      for (const l of this.lilyPads) {
        l.mesh.position.y = l.baseY + Math.sin(elapsed * 1.5 + l.phase) * l.amp;
        l.mesh.rotation.z = Math.sin(elapsed * 0.9 + l.phase) * 0.04;
      }
    }
  }

  /** No-op — App.js still calls this once per frame; kept for compatibility. */
  preRender() {}

  // ── Shore decor (lily pads, half-submerged rocks, reeds) ──────────────────

  /**
   * Place a scatter of decor along the island shoreline. Safe to call
   * fire-and-forget from World.loadAssets — missing GLBs are skipped
   * silently so a single 404 doesn't blow up the whole boot.
   */
  /**
   * Register a Rapier collider for a shore decoration. Optional — only
   * passed in by World for the rock decor; lily pads / reeds stay
   * walk-through. Set on the instance so loadShoreDecor() can use it
   * without a constructor refactor.
   */
  setPhysics(physics) {
    this.physics = physics;
  }

  async loadShoreDecor() {
    if (!this.loader) return;

    const safe = (url) => this.loader.loadGLTF(url).then((g) => g).catch(() => null);
    const [
      lilyLarge, lilySmall,
      rockLargeA, rockLargeB,
      rockSmallA, rockSmallB,
      reed,
    ] = await Promise.all([
      safe('/models/nature/lily-large.glb'),
      safe('/models/nature/lily-small.glb'),
      safe('/models/nature/rock-largea.glb'),
      safe('/models/nature/rock-largeb.glb'),
      safe('/models/nature/rock-smalla.glb'),
      safe('/models/nature/rock-smallb.glb'),
      safe('/models/nature/plant-flattall.glb'),
    ]);

    const place = (src, x, y, z, targetMax, yaw, opts = {}) => {
      if (!src) return null;
      const obj = src.scene.clone(true);
      const size = measureSize(obj);
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      const s = targetMax / maxDim;
      obj.scale.setScalar(s);
      obj.position.set(x, y, z);
      obj.rotation.y = yaw;
      obj.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = opts.castShadow ?? false;
          c.receiveShadow = true;
          c.frustumCulled = true;
        }
      });
      this.shoreGroup.add(obj);
      // Optional collider for solid shore decor (rocks). Reeds + lily pads
      // are intentionally walk-through so the player can wade past them.
      if (opts.collide && this.physics) {
        const scaledSize = size.clone().multiplyScalar(s);
        const hx = Math.max(scaledSize.x / 2, 0.18);
        const hz = Math.max(scaledSize.z / 2, 0.18);
        const hy = Math.max(scaledSize.y / 2, 0.12);
        // Cuboid sized to the scaled bounding box. y arg is the CENTRE; the
        // rock GLB origin is at its bbox bottom, so we lift by hy to place
        // the collider centre at the bbox midpoint.
        this.physics.addStaticCuboid(x, y + hy, z, hx, hy, hz, yaw);
      }
      return obj;
    };

    // ── Shore rocks (12–15 around the waterline) ───────────────────────────
    // Clusters of 1–3 with gaps between, half-submerged y in [-0.3, 0.3].
    const largeRocks = [rockLargeA, rockLargeB].filter(Boolean);
    const smallRocks = [rockSmallA, rockSmallB].filter(Boolean);
    const seed = mulberry(0xfedcba);
    const rockClusters = 7;
    for (let i = 0; i < rockClusters; i++) {
      const baseAngle = (i / rockClusters) * Math.PI * 2 + seed() * 0.4;
      const cluster = 1 + Math.floor(seed() * 3); // 1–3
      for (let j = 0; j < cluster; j++) {
        const angle = baseAngle + (j - 1) * 0.06 + (seed() - 0.5) * 0.04;
        const radius = 42 + seed() * 6;            // 42 → 48
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        const y = this.terrain ? this.terrain.heightAt(x, z) : 0;
        // Drop bigger rocks farther out (half-submerged), smaller pebbles closer in.
        const big = j === 0 && largeRocks.length;
        const src = big
          ? largeRocks[Math.floor(seed() * largeRocks.length)]
          : (smallRocks[Math.floor(seed() * smallRocks.length)] || largeRocks[0]);
        const targetMax = big ? 1.6 + seed() * 0.5 : 0.7 + seed() * 0.4;
        // collide:true so the player can't walk through shore boulders.
        place(src, x, y, z, targetMax, seed() * Math.PI * 2, { castShadow: big, collide: true });
      }
    }

    // ── Shore reeds / tall grass (10–14 above the waterline) ───────────────
    if (reed) {
      const reedCount = 14;
      for (let i = 0; i < reedCount; i++) {
        const angle = (i / reedCount) * Math.PI * 2 + seed() * 0.18;
        const radius = 42 + seed() * 2.5; // 42 → 44.5
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        const y = this.terrain ? this.terrain.heightAt(x, z) : 0;
        place(reed, x, y, z, 0.9 + seed() * 0.3, seed() * Math.PI * 2);
      }
    }

    // ── Lily pads (4–5 in the shallow water just past shore) ──────────────
    // Cluster near a calm bay rather than scattered evenly — feels intentional.
    const lilyAnchorAngle = Math.PI * 0.7; // somewhere north-west of spawn
    const lilyVariants = [lilyLarge, lilySmall, lilySmall, lilyLarge, lilySmall];
    for (let i = 0; i < 5; i++) {
      const src = lilyVariants[i];
      if (!src) continue;
      const angle = lilyAnchorAngle + (i - 2) * 0.10 + (seed() - 0.5) * 0.04;
      const radius = 46 + seed() * 3;     // 46 → 49 (in the water, past shore)
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const baseY = WATER_LEVEL_Y + 0.05;
      const targetMax = i % 2 === 0 ? 0.95 : 0.70;
      const obj = place(src, x, baseY, z, targetMax, seed() * Math.PI * 2);
      if (obj) {
        this.lilyPads.push({
          mesh: obj,
          baseY,
          phase: seed() * Math.PI * 2,
          amp: 0.025 + seed() * 0.02,
        });
      }
    }
  }

  // ── Splash particles ──────────────────────────────────────────────────────

  #buildSplashSystem() {
    const positions = new Float32Array(SPLASH_MAX * 3);
    const ages = new Float32Array(SPLASH_MAX);
    const lifes = new Float32Array(SPLASH_MAX);
    for (let i = 0; i < SPLASH_MAX; i++) {
      ages[i] = SPLASH_LIFE + 1; // dead
      lifes[i] = SPLASH_LIFE;
    }
    this._splash = {
      positions, ages, lifes,
      velocities: new Float32Array(SPLASH_MAX * 3),
      cursor: 0,
    };

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('aAge', new THREE.BufferAttribute(ages, 1));
    geom.setAttribute('aLife', new THREE.BufferAttribute(lifes, 1));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const mat = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: { uPxScale: { value: 60 } },
      vertexShader: /* glsl */ `
        attribute float aAge;
        attribute float aLife;
        uniform float uPxScale;
        varying float vAlpha;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mv;
          float t = clamp(aAge / aLife, 0.0, 1.0);
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
    this._splashPoints.geometry.attributes.position.needsUpdate = true;
    this._splashPoints.geometry.attributes.aAge.needsUpdate = true;
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
      if (s.positions[i * 3 + 1] < WATER_LEVEL_Y - 0.1) {
        s.ages[i] = s.lifes[i];
      }
    }
    if (anyAlive) {
      this._splashPoints.geometry.attributes.position.needsUpdate = true;
      this._splashPoints.geometry.attributes.aAge.needsUpdate = true;
    }
  }
}
