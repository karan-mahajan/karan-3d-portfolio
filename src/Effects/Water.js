import * as THREE from 'three/webgpu';
import { MeshBasicNodeMaterial } from 'three/webgpu';
import {
  Fn, attribute, uniform, varying,
  positionLocal, positionGeometry, positionWorld,
  vec2, vec3, vec4, float, texture,
  clamp, mix, smoothstep, max, abs, sin, cos, pow, length, dot, cross, normalize, reflect,
  fract, floor,
  cameraPosition, cameraProjectionMatrix, cameraViewMatrix,
  viewportUV, viewportSafeUV, viewportSharedTexture,
  mx_noise_float, mx_fractal_noise_float,
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

// Water line matched to the Blender terrain material: displacement is R×-1.5m
// and water colour starts at B=0.10 → depth 0.10×1.5 = 0.15 m below the y=0
// plains. So the surface sits at -0.15 (and the 0…-0.15 band stays dry beach,
// exactly like Blender's B<0.10 "no water tint" zone). Still well below the
// grass lip so the opaque land occludes it and wave crests never poke through.
const WATER_LEVEL_Y = -0.15;
// Terrain half-extent (measured bbox ±62.5). Past this the plane is open ocean.
const ISLAND_HALF = 62.5;
// Plane reaches well past the island so the ocean fills to the fog horizon.
const PLANE_SIZE = 340;
const PLANE_SEGMENTS = 144; // dense enough to resolve the Gerstner wave crests
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

// Shallow/deep matched to karan's authored terrain-material RGB nodes (the
// blank-bruno colour overrides): RGB.002 shallow = (0.28,0.68,0.72) linear =
// #90D7DD, RGB.003 deep = (0.015,0.12,0.25) linear = #216189.
const DAY_PALETTE = Object.freeze({
  shallow: '#90d7dd',
  deep:    '#216189',
  foam:    '#e6f2f8',
  sky:     '#bfe0ea', // fresnel reflection tint (cyan-leaning to match the palette)
  sun:     [60, 55, 40],
});
const NIGHT_PALETTE = Object.freeze({
  shallow: '#1a3a5a',
  deep:    '#081826',
  foam:    '#3a4a5a',
  sky:     '#2a3c52',
  sun:     [-40, 45, -40],
});

// Coarse rolling waves — actual GEOMETRY displacement (Gerstner: vertices move
// in a circular orbit so crests sharpen and curve, the classic ocean-swell
// shape). Depth-damped (calm at the shoreline, rolling in the deep) so crests
// never poke above the y=0 grass lip and ponds stay gentle. They also feed the
// shading normal so the swell catches light. Each:
//   [dirX, dirZ (normalised), spatial frequency, height amp (m), speed, steepness]
// Σ amp ≈ 0.10 < the 0.15 headroom under the water line, so peaks stay sub-zero.
const WAVES = [
  [0.80, 0.60, 0.150, 0.064, 0.85, 0.95],
  [-0.55, 0.84, 0.260, 0.040, 1.15, 0.82],
  [0.30, -0.95, 0.430, 0.025, 1.55, 0.70],
];

// Fine ripple waves driving the animated normal ONLY (fragment-side, no
// geometry) — the small surface texture/shimmer riding on top of the swell.
// [dirX, dirZ (normalised), spatial frequency, slope amplitude, scroll speed].
const RIPPLES = [
  [0.95, 0.31, 0.9, 0.055, 1.15],
  [-0.45, 0.89, 1.7, 0.036, 1.70],
  [0.62, -0.78, 2.6, 0.022, 2.30],
  [-0.80, -0.60, 4.1, 0.014, 0.95],
];

const RIPPLE_SOURCE_COUNT = 4;

export class Water {
  /**
   * @param {THREE.Scene} scene
   * @param {{heights:Float32Array, segments:number, size:number, bboxMin:THREE.Vector3, heightAt:Function}} terrain
   * @param {object} [opts]
   */
  constructor(scene, terrain, opts = {}) {
    this.scene = scene;
    this.terrain = terrain;
    // Full surface detail (refraction / caustics / whitecaps / shoreline foam /
    // noise-broken normal). Dropped on medium/low tiers via quality.waterHighDetail
    // — those blocks are skipped at graph-build time, so the cheap shader never
    // compiles them in (zero runtime branch). Defaults true for safety.
    this.highDetail = opts.highDetail !== false;
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
    this.entryDisturbance = { x: 0, z: 0, age: 99, strength: 0 };
    // Rain wetness 0→1, smoothed toward rainTarget (App sets it from rain state)
    // so the surface sprouts rain-impact rings while it's raining.
    this.rainLevel = 0;
    this.rainTarget = 0;

    this.#buildHeightTexture();
    this.#scanRippleSources();
    this.#buildSurface();
    this.#buildSplashSystem();

    this._splashTimer = 0;
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

  #scanRippleSources() {
    const t = this.terrain;
    const sources = [];
    const verts = (t?.segments ?? 0) + 1;
    if (t?.heights && verts > 1 && t?.bboxMin && t?.size) {
      const candidates = [];
      const step = Math.max(1, Math.floor(verts / 72));
      for (let u = 0; u < verts; u += step) {
        for (let w = 0; w < verts; w += step) {
          const h = t.heights[u * verts + w];
          const x = t.bboxMin.x + (u / t.segments) * t.size;
          const z = t.bboxMin.z + (w / t.segments) * t.size;
          if (Math.max(Math.abs(x), Math.abs(z)) > ISLAND_HALF - 14) continue;
          if (h >= WATER_LEVEL_Y - 0.18) continue;
          const centerBias = Math.hypot(x, z) * 0.002;
          candidates.push({ x, z, h, score: h + centerBias });
        }
      }
      candidates.sort((a, b) => a.score - b.score);
      for (const c of candidates) {
        const point = new THREE.Vector2(c.x, c.z);
        if (sources.every((s) => s.distanceToSquared(point) > 28 * 28)) {
          sources.push(point);
          if (sources.length >= RIPPLE_SOURCE_COUNT) break;
        }
      }
    }
    while (sources.length < RIPPLE_SOURCE_COUNT) {
      sources.push(new THREE.Vector2(0, 0));
    }
    this.rippleSources = sources;
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
    this.uEntryPos = uniform(vec2(0, 0));
    this.uEntryAge = uniform(99);
    this.uEntryStrength = uniform(0);
    this.uRippleA = uniform(vec2(this.rippleSources[0].x, this.rippleSources[0].y));
    this.uRippleB = uniform(vec2(this.rippleSources[1].x, this.rippleSources[1].y));
    this.uRippleC = uniform(vec2(this.rippleSources[2].x, this.rippleSources[2].y));
    this.uRippleD = uniform(vec2(this.rippleSources[3].x, this.rippleSources[3].y));
    this.uRain = uniform(0);
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
    // Depth-based wave damping (0 at the shoreline → 1 in deep water/ocean),
    // computed in the vertex and reused by the fragment normal so the swell
    // shape and its shading agree.
    const vWaveScale = varying(float(0), 'vWaterWaveScale');
    // Actual rolling-swell height contribution at this vertex (post depth-damp),
    // reused by the fragment to paint whitecaps on the crests.
    const vSwell = varying(float(0), 'vWaterSwell');

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

      // Depth from the baked terrain height (clamped → ocean reads the slope
      // edge value, which is already below the water line). Sampled on the
      // ORIGINAL position so the wave damping is stable.
      const hUv = clamp(vec2(p.x, p.z).sub(this.uTerrainMin).div(this.uTerrainSpan), 0.0, 1.0);
      const terrH = this.heightTex ? texture(this.heightTex, hUv).r : float(-1.0);
      const depthTerrain = max(this.uWaterLevel.sub(terrH), 0.0);
      const distBeyond = max(max(abs(p.x), abs(p.z)).sub(this.uIslandHalf), 0.0);
      const depthCombined = depthTerrain.add(distBeyond.mul(0.06));
      const waveScale = smoothstep(0.12, 0.9, depthCombined).toVar();
      const oceanMask = smoothstep(0.0, 8.0, distBeyond);
      const inlandMask = oceanMask.oneMinus().mul(smoothstep(0.16, 0.55, depthTerrain));
      vDepthTerrain.assign(depthTerrain);
      vDepth.assign(depthCombined);
      vWaveScale.assign(waveScale);

      // Rolling Gerstner swell — each wave orbits the vertex (vertical sin +
      // horizontal cos along its direction) so crests sharpen into curved
      // ridges. Damped by waveScale so the shoreline stays calm and crests
      // never rise above the grass lip.
      const dispX = float(0).toVar();
      const dispZ = float(0).toVar();
      const dispY = float(0).toVar();
      for (const [dx, dz, freq, amp, speed, steep] of WAVES) {
        const phase = p.x.mul(dx).add(p.z.mul(dz)).mul(freq).add(t.mul(speed));
        dispY.addAssign(sin(phase).mul(amp));
        dispX.addAssign(cos(phase).mul(amp * steep * dx));
        dispZ.addAssign(cos(phase).mul(amp * steep * dz));
      }
      p.x.addAssign(dispX.mul(waveScale));
      p.z.addAssign(dispZ.mul(waveScale));
      p.y.addAssign(dispY.mul(waveScale));
      vSwell.assign(dispY.mul(waveScale));

      // Inland basins / river get a gentle non-directional slosh so the water
      // reads as alive WITHOUT the concentric "sonar ring" look (the old
      // source-centred traveling rings were removed — they read as bad).
      const currentRipple = sin(p.x.mul(0.38).add(p.z.mul(1.15)).sub(t.mul(1.9))).mul(0.012)
        .add(sin(p.x.mul(-0.72).add(p.z.mul(0.42)).add(t.mul(1.35))).mul(0.007))
        .mul(0.45);
      p.y.addAssign(currentRipple.mul(inlandMask));

      // Player wake — concentric rings expanding from the feet while wading.
      const d = length(vec2(p.x, p.z).sub(this.uPlayerPos));
      const wake = sin(d.mul(9.0).sub(t.mul(7.0))).mul(0.014)
        .mul(smoothstep(5.0, 0.35, d))
        .mul(this.uPlayerInWater)
        .mul(this.uPlayerSpeed.mul(0.85).add(0.15));
      p.y.addAssign(wake);
      const bodyClear = smoothstep(0.95, 0.18, d).mul(this.uPlayerInWater);
      p.y.subAssign(bodyClear.mul(0.034));

      const entryD = length(vec2(p.x, p.z).sub(this.uEntryPos));
      const entryClear = smoothstep(1.6, 0.15, entryD)
        .mul(this.uEntryStrength)
        .mul(sin(this.uEntryAge.mul(10.0)).mul(0.35).add(0.65));
      p.y.subAssign(entryClear.mul(0.030));

      return p;
    })();

    // Animated surface normal — analytic slope of the coarse swell (scaled by
    // the same depth damping) PLUS the fine scrolling ripples on top, so the
    // rolling waves and the surface texture both catch light and shimmer.
    const surfaceNormal = (p2, t, waveScale) => {
      const acc = vec2(0, 0).toVar();
      // Coarse swell slope (∂(sin phase)/∂xz = cos·amp·freq·dir), depth-damped.
      for (const [dx, dz, freq, amp, speed] of WAVES) {
        const phase = p2.x.mul(dx).add(p2.y.mul(dz)).mul(freq).add(t.mul(speed));
        const slope = cos(phase).mul(amp * freq).mul(waveScale);
        acc.addAssign(vec2(slope.mul(dx), slope.mul(dz)));
      }
      // Fine ripple slope.
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
      const N = surfaceNormal(p2, t, vWaveScale).toVar();
      if (this.highDetail) {
        // Organic break-up of the regular sine-ripple normal — a cheap value-noise
        // gradient (3 taps) so the shimmer reads as water, not a perfect grid.
        const nEps = 0.18;
        const nC = mx_noise_float(vec3(p2.mul(1.4), t.mul(0.35)));
        const nX = mx_noise_float(vec3(p2.add(vec2(nEps, 0)).mul(1.4), t.mul(0.35)));
        const nZ = mx_noise_float(vec3(p2.add(vec2(0, nEps)).mul(1.4), t.mul(0.35)));
        const nGrad = vec2(nX.sub(nC), nZ.sub(nC)).mul(0.5);
        N.assign(normalize(N.add(vec3(nGrad.x.negate(), 0.0, nGrad.y.negate()))));
      }

      const V = normalize(cameraPosition.sub(wp));
      const topDown = clamp(V.y, 0.0, 1.0);

      // Depth tint (shallow → deep). Pulled in from the old 0.30→1.35 so basin
      // centres actually commit to the deep blue instead of staying cyan, with a
      // mild extra darkening at full depth. The open-ocean distance term carries
      // the far sea past the threshold so it reads solid deep.
      const depthF = smoothstep(0.18, 0.95, vDepth).toVar();
      const col = mix(this.uShallow, this.uDeep, depthF).toVar();
      col.mulAssign(mix(float(1.0), float(0.82), depthF));
      const distBeyond = max(max(abs(p2.x), abs(p2.y)).sub(this.uIslandHalf), 0.0);
      const oceanMask = smoothstep(0.0, 8.0, distBeyond);
      const inlandMask = oceanMask.oneMinus().mul(smoothstep(0.16, 0.55, vDepthTerrain));
      // Shallow → 1, deep/ocean → 0. Gates refraction + caustics so only thin
      // water shows its floor; deep water and the open sea keep the solid tint.
      const shallowFactor = smoothstep(1.1, 0.06, vDepthTerrain).toVar();

      if (this.highDetail) {
        // Refraction — sample the opaque scene buffer behind the surface, offset by
        // the wave normal so the bottom wobbles. Blended in only where shallow AND
        // looking down; at grazing angles the Fresnel sky reflection (below) takes
        // over, which also hides screen-edge smear.
        const refrOffset = N.xz.mul(0.045).mul(topDown);
        const bottom = viewportSharedTexture(viewportSafeUV(viewportUV.add(refrOffset))).rgb;
        // Depth murk — the bottom shows clearly in the shallows and dissolves into
        // the water's own colour as it deepens, so the water reads as a volume
        // rather than a thin clear sheet.
        const murk = clamp(vDepthTerrain.mul(1.1), 0.0, 1.0);
        const waterTint = mix(this.uShallow, this.uDeep, murk);
        const refracted = mix(bottom, waterTint, murk.mul(0.55).add(0.25));
        const seeThrough = clamp(shallowFactor.mul(topDown), 0.0, 1.0).mul(0.72);
        col.assign(mix(col, refracted, seeThrough));

        // Caustics — veined light on the shallow floor: two scrolling fractal-noise
        // layers differenced into bright filaments, tinted by the sky colour so it
        // dims automatically at night. Sits on top of the refracted bottom.
        const cuv = p2.mul(0.55);
        const caA = mx_fractal_noise_float(vec3(cuv.add(vec2(t.mul(0.07), t.mul(0.05))), t.mul(0.12)), 2, 2.0, 0.5);
        const caB = mx_fractal_noise_float(vec3(cuv.mul(1.35).add(11.3).sub(vec2(t.mul(0.05), t.mul(0.06))), t.mul(0.1)), 2, 2.0, 0.5);
        const caustic = pow(clamp(float(1.0).sub(abs(caA.sub(caB)).mul(2.6)), 0.0, 1.0), 3.5);
        col.addAssign(this.uSky.mul(caustic.mul(shallowFactor).mul(topDown.mul(0.5).add(0.5)).mul(0.45)));
      }

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

      // Directional flow shimmer on the inland water (no concentric rings) +
      // a slow ocean glint + the broad rolling-wave highlight bands.
      const flowBands = pow(sin(p2.x.mul(0.9).add(p2.y.mul(2.2)).sub(t.mul(2.2))).mul(0.5).add(0.5), 5.0)
        .mul(inlandMask)
        .mul(0.025);
      const oceanGlint = pow(sin(p2.x.mul(0.22).add(p2.y.mul(0.48)).sub(t.mul(1.15))).mul(0.5).add(0.5), 6.0)
        .mul(oceanMask)
        .mul(0.10);
      const waveBands = pow(sin(p2.x.mul(0.46).add(p2.y.mul(0.24)).add(t.mul(1.05))).mul(0.5).add(0.5), 4.0)
        .mul(0.070)
        .add(pow(sin(p2.x.mul(-0.28).add(p2.y.mul(0.58)).sub(t.mul(0.85))).mul(0.5).add(0.5), 5.0).mul(0.045))
        .mul(smoothstep(0.18, 0.85, vDepth));
      col.addAssign(this.uSky.mul(waveBands));
      col.addAssign(this.uShallow.mul(flowBands));
      col.addAssign(this.uSky.mul(oceanGlint));

      if (this.highDetail) {
        // Whitecaps — foam on the upper tips of the rolling swells, patchy
        // (noise-broken) and only in the deeper water where swells actually roll,
        // so the open ocean reads as real moving sea rather than a tinted sheet.
        const capNoise = mx_noise_float(vec3(p2.mul(1.6), t.mul(0.6))).mul(0.5).add(0.5);
        const crest = smoothstep(0.035, 0.08, vSwell)
          .mul(smoothstep(0.35, 0.85, vWaveScale))
          .mul(capNoise.mul(0.7).add(0.3))
          .mul(0.6);
        col.assign(mix(col, this.uFoam, clamp(crest, 0.0, 1.0)));
      }

      // Rain-impact rings — while it's raining, expanding ringlets pop across the
      // whole surface (cellular grid, random phase per cell). Two scales for a
      // natural mix. Gated by uRain so it's invisible in dry weather.
      const rainPresence = max(oceanMask, smoothstep(0.05, 0.25, vDepthTerrain));
      const rainHash = (c) => fract(sin(dot(c, vec2(127.1, 311.7))).mul(43758.5453));
      const rainCells = (density, rate, thickness) => {
        const gp = p2.mul(density);
        const cell = floor(gp);
        const f = fract(gp);
        const r1 = rainHash(cell);
        const r2 = rainHash(cell.add(vec2(5.2, 1.3)));
        const center = vec2(r1.mul(0.6).add(0.2), r2.mul(0.6).add(0.2));
        const d = length(f.sub(center));
        const phase = fract(t.mul(rate).add(r1.mul(6.28)));
        const ring = smoothstep(thickness, 0.0, abs(d.sub(phase.mul(0.45))));
        return ring.mul(phase.oneMinus());
      };
      const rainRings = rainCells(0.8, 1.7, 0.05).add(rainCells(1.35, 2.2, 0.04).mul(0.8));
      col.assign(mix(col, this.uFoam, clamp(rainRings.mul(rainPresence).mul(this.uRain).mul(0.7), 0.0, 1.0)));

      if (this.highDetail) {
        // Shoreline foam — an irregular lacy band where the ground is just under
        // water, broken up by scrolling fractal noise (so it reads as foam, not a
        // clean ring) and breathing in/out like a tide.
        const shoreWave = sin(this.uTime.mul(0.8).add(p2.x.mul(0.25))).mul(0.05);
        const foamBand = smoothstep(0.34, 0.015, vDepthTerrain.add(shoreWave));
        const foamN = mx_fractal_noise_float(vec3(p2.mul(0.9), t.mul(0.22)), 3, 2.0, 0.5).mul(0.5).add(0.5);
        const foamTex = smoothstep(0.34, 0.74, foamN).mul(0.75).add(0.25);
        const foam = clamp(foamBand.mul(foamTex), 0.0, 1.0).mul(0.95);
        col.assign(mix(col, this.uFoam, foam));
      }

      // Water reacting to the body in it — foam that HUGS the waterline around
      // the body (present even standing still) plus churn when wading. No
      // concentric rings.
      const pd = length(p2.sub(this.uPlayerPos));
      // Foam collar at the body contact line — a noise-broken band hugging the
      // body radius, so the water visibly breaks around whatever is standing in
      // it. Hollow centre (the body occupies it), fading out by ~1 m.
      const bodyFoamN = mx_noise_float(vec3(p2.mul(4.0), t.mul(1.3))).mul(0.5).add(0.5);
      // Breathing radius so the waterline undulates with the surface instead of
      // sitting as a static disc — reads as foam lapping at the body.
      const ringR = float(0.42).add(sin(t.mul(2.0).add(pd.mul(6.0))).mul(0.04));
      const bodyFoam = smoothstep(0.16, ringR, pd).mul(smoothstep(0.92, ringR, pd))
        .mul(this.uPlayerInWater)
        .mul(bodyFoamN.mul(0.55).add(0.45))
        .mul(0.85);
      col.assign(mix(col, this.uFoam, clamp(bodyFoam, 0.0, 1.0)));

      // Churned foam trailing the wading player — noise-broken white water that
      // grows with speed.
      const trailNoise = mx_noise_float(vec3(p2.mul(2.6), t.mul(1.6))).mul(0.5).add(0.5);
      const trailFoam = smoothstep(1.7, 0.2, pd)
        .mul(this.uPlayerInWater)
        .mul(this.uPlayerSpeed.mul(0.9).add(0.1))
        .mul(trailNoise)
        .mul(0.55);
      col.assign(mix(col, this.uFoam, clamp(trailFoam, 0.0, 1.0)));

      const entryD = length(p2.sub(this.uEntryPos));
      const entryClear = smoothstep(1.55, 0.18, entryD)
        .mul(this.uEntryStrength)
        .mul(0.18);
      col.assign(mix(col, this.uSky.mul(1.2), entryClear));

      const clearWater = smoothstep(1.15, 0.2, pd).mul(this.uPlayerInWater);
      col.assign(mix(col, this.uSky.mul(1.15), clearWater.mul(0.22)));

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
      const depthOp = mix(float(0.62), float(0.96), smoothstep(0.0, 1.6, vDepth));
      const op = mix(depthOp, float(0.97), grazing.mul(0.75));
      const edge = smoothstep(0.0, 0.06, vDepth);
      const pd = length(vec2(positionWorld.x, positionWorld.z).sub(this.uPlayerPos));
      const clearWater = smoothstep(1.10, 0.18, pd).mul(this.uPlayerInWater);
      return op.mul(edge).mul(clearWater.mul(0.46).oneMinus());
    })();

    const geom = new THREE.PlaneGeometry(PLANE_SIZE, PLANE_SIZE, PLANE_SEGMENTS, PLANE_SEGMENTS);
    geom.rotateX(-Math.PI / 2);
    this.material = mat;
    this.mesh = new THREE.Mesh(geom, mat);
    this.mesh.position.y = WATER_LEVEL_Y;
    this.mesh.name = 'water';
    this.mesh.renderOrder = 2; // after opaque terrain + grass
    this.mesh.frustumCulled = false;
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
    // Ease rain wetness toward its target so rings fade in/out with the weather.
    this.rainLevel += (this.rainTarget - this.rainLevel) * (1 - Math.exp(-3 * delta));
    this.uRain.value = this.rainLevel;
    if (this.entryDisturbance.strength > 0) this.entryDisturbance.age += delta;
    this.uEntryPos.value.set(this.entryDisturbance.x, this.entryDisturbance.z);
    this.uEntryAge.value = this.entryDisturbance.age;
    this.uEntryStrength.value = this.entryDisturbance.strength;

    if (playerPos) {
      this.uPlayerPos.value.set(playerPos.x, playerPos.z);
      // "In water" only when the player is actually DOWN in it — feet at/below
      // the water surface. The XZ test alone fired on the bridges, whose decks
      // sit over the pond/river (terrain below the water line) while the player
      // is up on the planks: phantom splashes, ripples and wade slowdown.
      const submerged = playerPos.y <= this.waterLevel + 0.1;
      const inWater =
        submerged && this.playerOverWater(playerPos.x, playerPos.z) ? 1.0 : 0.0;
      this.uPlayerInWater.value = inWater;
      const rawSpeed = sample && sample.moving ? sample.speed : 0;
      this.uPlayerSpeed.value = Math.min(1, rawSpeed / 8.0);

      // Splash + disturbance on BOTH entering and leaving the water, so the
      // surface visibly reacts when the player crosses the shoreline either way.
      const crossedWater = (inWater > 0.5) !== (this._playerInWaterPrev > 0.5);
      this._playerInWaterPrev = inWater;
      if (crossedWater) {
        this.entryDisturbance.x = playerPos.x;
        this.entryDisturbance.z = playerPos.z;
        this.entryDisturbance.age = 0;
        this.entryDisturbance.strength = 1;
        gsap.killTweensOf(this.entryDisturbance);
        gsap.to(this.entryDisturbance, { strength: 0, duration: 0.85, ease: 'sine.out' });
        this.#spawnSplashBurst(playerPos, 14);
        // Entering the water → the big jump/drop splash. Leaving → a lighter
        // splash so the exit still reads. (Continuous wading audio is now the
        // footstep system's water step pool, not an auto-splash loop.)
        if (this.audio) {
          if (inWater > 0.5) this.audio.playWaterJump();
          else this.audio.playSplash({ entry: false, volume: 0.6 });
        }
      }

      this._splashTimer -= delta;
      const running = (sample?.speed ?? 0) > 5;
      if (inWater > 0.5 && sample && sample.moving && this._splashTimer <= 0) {
        this._splashTimer = SPLASH_SPAWN_INTERVAL;
        this.#spawnSplashBurst(playerPos, running ? SPLASH_PER_BURST_RUN : SPLASH_PER_BURST_WALK);
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
