import * as THREE from 'three/webgpu';
import { MeshStandardNodeMaterial, MeshBasicNodeMaterial } from 'three/webgpu';
import {
  Fn, uniform, varying, vec2, vec3, vec4, float, attribute, uv,
  positionGeometry, positionWorld, modelViewMatrix, cameraProjectionMatrix,
  sin, cos, length, smoothstep, fract, mix, max, texture, mx_fractal_noise_float,
} from 'three/tsl';

/**
 * Lava pool — re-materialises the Blender-authored `lavaSurface_pool` /
 * `lavaSurface_core` meshes with the real photo-scanned lava texture set
 * (CC-BY-4.0 "Lava" by Beccasaurus, Sketchfab) and dresses the pool with
 * rising embers + drifting smoke.
 *
 * The look: a dark basalt **crust** (albedo, kept dim) with bright molten
 * **veins** that flow underneath it (emissive map, scrolled in two layers and
 * pulsed). Driven by a single `uTime` uniform; the emissive intensity also
 * tracks the day/night factor so it reads warm in daylight and blooms at
 * night. Textures are sampled by WORLD-XZ planar projection — the surface is a
 * flat horizontal disc, so this tiles seamlessly with no UVs and stays
 * continuous between the pool and the inner core.
 *
 * Also owns: static colliders for the rim rocks (so the player can walk around
 * the basalt but still step down into the molten centre), and the pool
 * geometry exposed for the LavaHazard sink/respawn system.
 */

const TEX_BASE = '/textures/lava/';
const TILE = 0.34;          // world-metres → UV scale (≈3 m per crust tile)

const EMBER_LIFE = 2.6;     // seconds per ember rise loop
const EMBER_RISE = 3.4;     // how high an ember climbs (m)
const EMBER_SIZE = 0.13;    // billboard world size

const SMOKE_LIFE = 4.2;     // seconds per smoke rise loop
const SMOKE_RISE = 5.2;     // how high smoke climbs (m)
const SMOKE_SIZE = 1.1;     // billboard world size

// Rim props that should become solid (walk-around) colliders. Surface discs
// (lavaSurface_*) are deliberately excluded so the player can step into the pool.
const ROCK_NAME_RE = /^(lavaCrust_|lavaRock_|shoreRock\d+\.001$)/;

export class Lava {
  /**
   * @param {THREE.Scene} scene
   * @param {import('./Wind.js').Wind} wind
   * @param {{ byName: Map<string, any> }} refs
   * @param {import('../Physics/Physics.js').Physics} [physics] when given, rim
   *        rocks get static colliders.
   */
  constructor(scene, wind, refs, physics) {
    this.scene = scene;
    this.wind = wind;
    this.uTime = uniform(0);
    this.embers = null;
    this.smoke = null;

    // Pool geometry the hazard system reads — null until a ref is found.
    this.center = null;   // { x, z } world
    this.radius = 0;      // walkable molten radius (m)
    this.surfaceY = 0;    // world Y of the lava surface

    // One day/night-aware glow multiplier shared by both surfaces.
    this.uGlowScale = uniform(1);

    const ref = refs?.byName?.get('lavaRef_pool');
    if (!ref) return;
    const ex = ref.extras ?? ref.object3d?.userData ?? {};
    const p = ref.position ?? ref.object3d?.position ?? { x: 0, y: 0, z: 0 };

    const surfaceName = ex.surfaceObject ?? 'lavaSurface_pool';
    const coreName = ex.coreObject ?? 'lavaSurface_core';
    const glow = ex.glowStrength ?? 2.6;
    const pulse = ex.pulseSpeed ?? 0.6;
    const flow = ex.flowDir ?? [1, 0];
    const radius = ex.radius ?? 3;
    const emberRate = ex.emberRate ?? 12;

    // Pool geometry (set BEFORE styling — #styleSurface reads this.center for
    // its radial ripple).
    const surfaceY = this.scene.getObjectByName(surfaceName)
      ? this.#worldY(surfaceName, p.y)
      : p.y;
    this.center = { x: p.x, z: p.z };
    this.radius = radius;
    this.surfaceY = surfaceY;

    // Shared texture set (loaded once, reused by both surfaces).
    const tex = this.#loadTextures();

    // Pool surface — broad, slightly dimmer crust.
    this.#styleSurface(surfaceName, tex, { glow: glow * 0.62, pulse, flow });
    // Core — brighter, faster churn so the centre reads hotter.
    this.#styleSurface(coreName, tex, { glow: glow * 0.95, pulse: pulse * 1.7, flow });

    this.#buildEmbers(p.x, surfaceY + 0.1, p.z, radius, Math.max(8, Math.round(emberRate * EMBER_LIFE)));
    this.#buildSmoke(p.x, surfaceY + 0.15, p.z, radius);
    this.#buildFlames(p.x, surfaceY + 0.04, p.z, radius, 22);
    // Red scorched-earth ring replacing the green ground halo around the pool.
    this.#buildScorchRing(p.x, surfaceY + 0.03, p.z, radius * 0.9, radius + 1.6);

    if (physics) this.addRockColliders(physics);
  }

  /** True when world XZ is over the molten pool (used by LavaHazard). */
  containsPoint(x, z) {
    if (!this.center) return false;
    const dx = x - this.center.x;
    const dz = z - this.center.z;
    return (dx * dx + dz * dz) <= (this.radius * 1.05) * (this.radius * 1.05);
  }

  #worldY(name, fallback) {
    const o = this.scene.getObjectByName(name);
    if (!o) return fallback;
    const v = new THREE.Vector3();
    o.getWorldPosition(v);
    return v.y;
  }

  #loadTextures() {
    const loader = new THREE.TextureLoader();
    const albedo = loader.load(`${TEX_BASE}lava_albedo.jpg`);
    const emissive = loader.load(`${TEX_BASE}lava_emissive.jpg`);
    for (const t of [albedo, emissive]) {
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 4;
    }
    return { albedo, emissive };
  }

  // ── Textured emissive surface (replaces the baked GLB material) ─────────────
  #styleSurface(name, tex, opts) {
    const mesh = this.scene.getObjectByName(name);
    if (!mesh || !mesh.isMesh) return;

    const uGlow = uniform(opts.glow);
    const uPulse = float(opts.pulse);
    const fdir = vec2(opts.flow[0], opts.flow[1]);
    const t = this.uTime;
    const glowScale = this.uGlowScale;

    const mat = new MeshStandardNodeMaterial({ metalness: 0, roughness: 0.72 });

    // World-XZ planar UVs → seamless tiling, no mesh UVs needed.
    const wp = positionWorld.xz;
    const baseUv = wp.mul(TILE);

    // Cool the lava toward the rim so the disc blends into the surrounding
    // basalt instead of reading as a flat image pasted on the ground.
    const ctr = vec2(this.center?.x ?? 0, this.center?.z ?? 0);
    const tEdge = length(wp.sub(ctr)).div(this.radius || 3);
    const rimFade = smoothstep(1.05, 0.45, tEdge);   // 1 molten core → 0 cooled rim

    // Dark cooled crust as the albedo, darker still at the rim so the edge melts
    // into the crust ring rather than ending on a hard texture seam.
    const crust = texture(tex.albedo, baseUv).rgb;
    mat.colorNode = crust.mul(mix(0.18, 0.5, rimFade));

    // Two emissive layers scrolling along the flow at different speeds/scales so
    // the molten veins churn instead of sliding as one sheet.
    const uvA = baseUv.add(fdir.mul(t.mul(0.012)));
    const uvB = baseUv.mul(1.7).add(fdir.mul(t.mul(-0.02)));
    const veins = max(texture(tex.emissive, uvA).rgb, texture(tex.emissive, uvB).rgb);

    // Slow ripple from the centre + a breathing pulse, both subtle.
    const ripple = sin(length(wp.sub(vec2(this.center?.x ?? 0, this.center?.z ?? 0))).mul(2.0).sub(t.mul(1.1)))
      .mul(0.08).add(1.0);
    const pulseAmt = sin(t.mul(uPulse)).mul(0.14).add(0.95);

    // The emissive map already carries the authored black→orange→yellow, so keep
    // its colour and only drive intensity (glow × day/night × pulse × ripple).
    mat.emissiveNode = veins.mul(uGlow).mul(glowScale).mul(pulseAmt).mul(ripple).mul(rimFade);

    mesh.material = mat;
    mesh.castShadow = false;
    mesh.receiveShadow = false;
  }

  // ── Static colliders for the rim basalt (walk-around, not walk-through) ──────
  addRockColliders(physics) {
    if (!physics?.addStaticCuboid) return 0;
    const box = new THREE.Box3();
    const size = new THREE.Vector3();
    let placed = 0;
    this.scene.traverse((o) => {
      if (!o.isMesh || !ROCK_NAME_RE.test(o.name)) return;
      box.setFromObject(o);
      if (!isFinite(box.min.x) || box.isEmpty()) return;
      box.getSize(size);
      const cx = (box.min.x + box.max.x) / 2;
      const cy = (box.min.y + box.max.y) / 2;
      const cz = (box.min.z + box.max.z) / 2;
      // Pull the XZ half-extents in slightly so the player doesn't bump the
      // empty corners of a rounded boulder's bounding box.
      physics.addStaticCuboid(cx, cy, cz, (size.x / 2) * 0.82, size.y / 2, (size.z / 2) * 0.82);
      placed++;
    });
    return placed;
  }

  // ── GPU billboards (looping rise, wind drift) ───────────────────────────────
  #particleGeom(count, cx, cz, radius, radiusScale) {
    const seeds = new Float32Array(count);
    const angles = new Float32Array(count);
    const radii = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      seeds[i] = i / count;                       // even phase spread
      angles[i] = Math.random() * Math.PI * 2;
      radii[i] = Math.sqrt(Math.random()) * radius * radiusScale;
    }
    const quad = new Float32Array([-0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0]);
    const quadUv = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    const geom = new THREE.InstancedBufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(quad, 3));
    geom.setAttribute('uv', new THREE.BufferAttribute(quadUv, 2));
    geom.setIndex([0, 1, 2, 0, 2, 3]);
    geom.instanceCount = count;
    geom.setAttribute('aSeed', new THREE.InstancedBufferAttribute(seeds, 1));
    geom.setAttribute('aAngle', new THREE.InstancedBufferAttribute(angles, 1));
    geom.setAttribute('aRadius', new THREE.InstancedBufferAttribute(radii, 1));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(cx, 0, cz), 1e6);
    return geom;
  }

  #buildEmbers(cx, cy, cz, radius, count) {
    const geom = this.#particleGeom(count, cx, cz, radius, 0.85);
    const t = this.uTime;
    const wind = this.wind;
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
    });

    const vFade = varying(float(0), 'vEmberFade');
    mat.vertexNode = Fn(() => {
      const seed = attribute('aSeed');
      const ang = attribute('aAngle');
      const rad = attribute('aRadius');
      const phase = fract(t.div(EMBER_LIFE).add(seed));          // 0..1 loop
      const fade = phase.oneMinus().mul(smoothstep(0, 0.12, phase));
      vFade.assign(fade);

      const bx = float(cx).add(cos(ang).mul(rad));
      const bz = float(cz).add(sin(ang).mul(rad));
      const drift = wind.offsetNode(vec2(bx, bz)).mul(0.6).mul(phase);
      const world = vec3(bx.add(drift.x), float(cy).add(phase.mul(EMBER_RISE)), bz.add(drift.y));

      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      const size = float(EMBER_SIZE).mul(fade.mul(0.6).add(0.4));
      view.xy.addAssign(positionGeometry.xy.mul(size));
      return cameraProjectionMatrix.mul(view);
    })();

    const disc = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.35, 0.05), vec3(1.0, 0.8, 0.3), vFade);
    mat.opacityNode = disc.mul(vFade);

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = 'lava:embers';
    mesh.frustumCulled = false;
    mesh.renderOrder = 6;
    this.scene.add(mesh);
    this.embers = { mesh, geom, mat };
  }

  #buildSmoke(cx, cy, cz, radius) {
    const count = 14;
    const geom = this.#particleGeom(count, cx, cz, radius, 0.7);
    const t = this.uTime;
    const wind = this.wind;
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false, blending: THREE.NormalBlending, fog: true,
    });

    const vFade = varying(float(0), 'vSmokeFade');
    mat.vertexNode = Fn(() => {
      const seed = attribute('aSeed');
      const ang = attribute('aAngle');
      const rad = attribute('aRadius');
      const phase = fract(t.div(SMOKE_LIFE).add(seed));
      // Smoke fades in, then thins out as it rises and expands.
      const fade = smoothstep(0, 0.18, phase).mul(smoothstep(1.0, 0.4, phase));
      vFade.assign(fade);

      const bx = float(cx).add(cos(ang).mul(rad));
      const bz = float(cz).add(sin(ang).mul(rad));
      const drift = wind.offsetNode(vec2(bx, bz)).mul(1.4).mul(phase);
      const world = vec3(bx.add(drift.x), float(cy).add(phase.mul(SMOKE_RISE)), bz.add(drift.y));

      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      const size = float(SMOKE_SIZE).mul(phase.mul(1.4).add(0.5));   // expands as it climbs
      view.xy.addAssign(positionGeometry.xy.mul(size));
      return cameraProjectionMatrix.mul(view);
    })();

    const disc = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    // Dark grey near the surface, lightening as it dissipates.
    mat.colorNode = mix(vec3(0.07, 0.06, 0.06), vec3(0.22, 0.2, 0.19), vFade);
    mat.opacityNode = disc.mul(vFade).mul(0.42);

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = 'lava:smoke';
    mesh.frustumCulled = false;
    mesh.renderOrder = 5;
    this.scene.add(mesh);
    this.smoke = { mesh, geom, mat };
  }

  // ── Flickering flame tongues licking up around the pool ─────────────────────
  #buildFlames(cx, cy, cz, radius, count) {
    const geom = this.#particleGeom(count, cx, cz, radius, 0.95);  // spread toward the rim
    const t = this.uTime;
    const wind = this.wind;
    const glowScale = this.uGlowScale;
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: true,
    });

    const FLAME_H = 1.35;       // base flame height (m)
    const FLAME_W = 0.8;        // base flame width (m)
    const vFlick = varying(float(0), 'vFlameFlicker');
    const vSeed = varying(float(0), 'vFlameSeed');
    mat.vertexNode = Fn(() => {
      const seed = attribute('aSeed');
      const ang = attribute('aAngle');
      const rad = attribute('aRadius');
      vSeed.assign(seed);
      // Slow rise/fall loop + a fast jitter so each tongue dances independently.
      const slow = sin(t.mul(1.3).add(seed.mul(6.283))).mul(0.5).add(0.5);
      const fast = sin(t.mul(6.0).add(seed.mul(11.0))).mul(0.5).add(0.5);
      const life = slow.mul(0.6).add(fast.mul(0.4));   // 0..1
      vFlick.assign(life);

      const bx = float(cx).add(cos(ang).mul(rad));
      const bz = float(cz).add(sin(ang).mul(rad));
      const sway = wind.offsetNode(vec2(bx, bz)).mul(0.4);
      const world = vec3(bx.add(sway.x), float(cy), bz.add(sway.y));

      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      const sizeVar = seed.mul(0.7).add(0.65);                // 0.65..1.35 per flame
      const h = float(FLAME_H).mul(life.mul(0.55).add(0.6)).mul(sizeVar);
      const w = float(FLAME_W).mul(life.mul(0.2).add(0.85)).mul(seed.mul(0.4).add(0.8));
      const pg = positionGeometry;
      view.x.addAssign(pg.x.mul(w));
      view.y.addAssign(pg.y.add(0.5).mul(h));                 // bottom seated at the surface
      return cameraProjectionMatrix.mul(view);
    })();

    // ── Procedural fire: animated fbm noise erodes a flame gradient, then a
    //    heat→colour ramp (deep red → orange → yellow → white-hot core). Reads
    //    as licking flames with ragged flickering edges, not a solid cone.
    const u = uv().x;
    const v = uv().y;
    // Animated fractal noise (the same GPU node the water caustics use),
    // scrolling UPWARD so the fire licks. Full 0..1 range so it genuinely
    // CARVES the silhouette into separate tongues — not just dimming a triangle.
    const off = vSeed.mul(9.7);
    const np = vec3(
      u.mul(2.3).add(off),
      v.mul(2.6).sub(t.mul(1.1)),
      off.add(t.mul(0.15)),
    );
    const noise = mx_fractal_noise_float(np, 3, 2.0, 0.5).mul(0.5).add(0.5);  // 0..1

    // Flame envelope: narrows toward the tip, hottest at the base.
    const halfW = v.oneMinus().pow(0.6).mul(0.5);
    const body = smoothstep(halfW, halfW.sub(0.16), u.sub(0.5).abs());
    const env = body.mul(v.oneMinus().mul(0.7).add(0.3));

    // Noise carves the envelope — low-noise pockets punch ragged holes/edges.
    const heat = env.mul(noise).mul(1.7);
    const baseFade = smoothstep(0.0, 0.05, v);             // hide the hard quad bottom
    const alpha = smoothstep(0.16, 0.46, heat)
      .mul(baseFade)
      .mul(vFlick.mul(0.3).add(0.7));

    // Heat → colour ramp.
    const ember = vec3(0.5, 0.03, 0.0);
    const orange = vec3(1.0, 0.27, 0.02);
    const yellow = vec3(1.0, 0.62, 0.12);
    const core = vec3(1.0, 0.88, 0.55);
    let col = mix(orange, yellow, smoothstep(0.3, 0.6, heat));
    col = mix(col, core, smoothstep(0.7, 1.1, heat));
    col = mix(ember, col, smoothstep(0.12, 0.32, heat));

    mat.colorNode = col.mul(glowScale.mul(0.3).add(0.72));
    mat.opacityNode = alpha;

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = 'lava:flames';
    mesh.frustumCulled = false;
    mesh.renderOrder = 6;
    this.scene.add(mesh);
    this.flames = { mesh, geom, mat };
  }

  /** Tiling fbm value-noise (DataTexture) for the flame turbulence — generated
   *  at runtime so no image asset is needed (same spirit as TimeOfDay's canvas
   *  textures). Wrap-indexed lattices keep it seamless under RepeatWrapping. */
  #makeNoiseTexture(size = 128) {
    const lerp = (a, b, k) => a + (b - a) * k;
    const smooth = (k) => k * k * (3 - 2 * k);
    const octaves = [
      { P: 8, amp: 0.5 },
      { P: 16, amp: 0.3 },
      { P: 32, amp: 0.2 },
    ].map((o) => {
      const g = new Float32Array(o.P * o.P);
      for (let i = 0; i < g.length; i++) g[i] = Math.random();
      return { ...o, g };
    });
    const data = new Uint8Array(size * size * 4);
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        let val = 0;
        for (const { P, amp, g } of octaves) {
          const fx = (x / size) * P;
          const fy = (y / size) * P;
          const x0 = Math.floor(fx) % P;
          const y0 = Math.floor(fy) % P;
          const x1 = (x0 + 1) % P;
          const y1 = (y0 + 1) % P;
          const tx = smooth(fx - Math.floor(fx));
          const ty = smooth(fy - Math.floor(fy));
          const top = lerp(g[y0 * P + x0], g[y0 * P + x1], tx);
          const bot = lerp(g[y1 * P + x0], g[y1 * P + x1], tx);
          val += lerp(top, bot, ty) * amp;
        }
        const c = Math.max(0, Math.min(255, Math.round(val * 255)));
        const idx = (y * size + x) * 4;
        data[idx] = c; data[idx + 1] = c; data[idx + 2] = c; data[idx + 3] = 255;
      }
    }
    const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.magFilter = THREE.LinearFilter;
    tex.minFilter = THREE.LinearFilter;
    tex.colorSpace = THREE.NoColorSpace;
    tex.needsUpdate = true;
    return tex;
  }

  // ── Red scorched-earth ring (replaces the green ground halo) ─────────────────
  #buildScorchRing(cx, cy, cz, innerR, outerR) {
    const geom = new THREE.RingGeometry(innerR, outerR, 56, 1);
    geom.rotateX(-Math.PI / 2);                              // lay flat on the ground
    const t = this.uTime;
    const glowScale = this.uGlowScale;
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false, blending: THREE.NormalBlending, fog: true,
    });

    const wp = positionWorld.xz;
    const tr = length(wp.sub(vec2(cx, cz))).sub(innerR).div(Math.max(0.001, outerR - innerR));
    // Glowing red at the rim, cooling to dark scorch, fading out at the edge so
    // it reads as burnt ground rather than a hard ring.
    const col = mix(vec3(0.95, 0.2, 0.04), vec3(0.16, 0.03, 0.02), smoothstep(0.0, 0.7, tr));
    const flick = sin(t.mul(1.6)).mul(0.06).add(1.0);
    mat.colorNode = col.mul(flick).mul(glowScale.mul(0.3).add(0.85));
    mat.opacityNode = smoothstep(1.0, 0.12, tr).mul(0.9);

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = 'lava:scorch';
    mesh.position.set(cx, cy, cz);
    mesh.frustumCulled = false;
    mesh.renderOrder = 4;                                    // over ground, under lava/embers
    this.scene.add(mesh);
    this.scorch = { mesh, geom, mat };
  }

  /**
   * @param {number} elapsed seconds
   * @param {number} [night] 0 (day) → 1 (night); brightens the glow at night.
   */
  update(elapsed, night = 0) {
    this.uTime.value = elapsed;
    // Visible-but-warm in daylight, blooming at night.
    this.uGlowScale.value = 0.85 + night * 1.25;
  }

  dispose() {
    for (const part of [this.embers, this.smoke, this.flames, this.scorch]) {
      if (!part) continue;
      this.scene.remove(part.mesh);
      part.geom?.dispose();
      part.mat?.dispose();
    }
    this.embers = null;
    this.smoke = null;
    this.flames = null;
    this.scorch = null;
    this._noiseTex?.dispose();
    this._noiseTex = null;
  }
}
