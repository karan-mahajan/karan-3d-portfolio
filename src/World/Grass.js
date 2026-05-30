import * as THREE from 'three/webgpu';
import { patchShadowTint } from './Palette.js';

/**
 * Quaternius GLB grass field.
 *
 * InstancedMesh per grass type. Placement is deterministic (seeded RNG)
 * and filtered against paths, water surfaces, and tree trunks at load
 * time — no per-frame work.
 *
 * Per-type counts (post-exclusion):
 *   grass.glb        — short base tufts
 *   grass-wispy-1/2  — wispy fans for variation
 *   tall-grass.glb   — taller clumps, ring 20–50 only (forest edge / water)
 *
 * Wind: each material's onBeforeCompile injects a tip-bend vertex
 * displacement keyed to the shared `uWindTime` from the Wind class.
 *
 * Day/night cycle: TimeOfDay calls `setColor(hex)` (instant) or tweens
 * `baseColor` and calls `syncColor()` per onUpdate to propagate to materials.
 */

// Capped at 40 so grass tufts stop before the sandy shore band (r ≈ 40–45)
// and never spawn on the beach or in the surf.
const FIELD_RADIUS = 40;
// Each Quaternius tuft is ~260 triangles (a tuft = several blade meshes).
// The prompt's 3500+600+600+300 = 5000 totals ≈ 1.3M tris just for grass —
// 66% of the scene budget at the time, dragging real-GPU FPS to 40-50.
// These reduced counts keep coverage dense-looking without busting that
// budget: ~1700 instances ≈ 440k tris (~3× the trees, manageable).
const SHORT_COUNT  = 1200;
const WISPY1_COUNT = 220;
const WISPY2_COUNT = 220;
const TALL_COUNT   = 100;
// Tall grass only spawns in the outer ring — keeps it away from the spawn
// plaza and reads as "forest edge" rather than ankle-deep clutter at spawn.
const TALL_RING_INNER = 20;
const TALL_RING_OUTER = FIELD_RADIUS;
const TREE_EXCLUSION_R = 1.5;
const GROUND_LIFT = 0.01;

const GRASS_DAY = '#5aa033';

function makeRng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export class Grass {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../Utils/Loader.js').Loader} loader
   * @param {import('./Terrain.js').Terrain}      terrain
   * @param {import('./Wind.js').Wind}            wind
   */
  constructor(scene, loader, terrain, wind) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    this.wind = wind;
    this.rng = makeRng(0xfeedface);
    this.materials = [];
    this.instancedMeshes = [];
    /** Shared base colour — TimeOfDay tweens this; syncColor() pushes to materials. */
    this.baseColor = new THREE.Color(GRASS_DAY);
    // Shared player-bend uniforms — every grass material's onBeforeCompile
    // assigns these into shader.uniforms by reference, so updates from
    // setPlayerPos() propagate to all layers without iterating materials.
    // uPlayerBendRadius: blades closer than this lean away from the player.
    // uPlayerBendStrength: meters of horizontal displacement at the tip.
    this.playerUniforms = {
      uPlayerPos:           { value: new THREE.Vector2(1e6, 1e6) },
      uPlayerBendRadius:    { value: 1.4 },
      uPlayerBendStrength:  { value: 0.35 },
    };
  }

  /**
   * Load grass GLBs and place all instances. Must run AFTER paths, water,
   * and Nature have loaded so exclusion lists are populated.
   *
   * @param {object} opts
   * @param {Float32Array} [opts.pathPositions]   packed [x0,z0,x1,z1,…]
   * @param {number}       [opts.pathCount]
   * @param {number}       [opts.pathRadius=1.4]
   * @param {Array<{x:number,z:number}>}          [opts.treePositions]
   * @param {Array<{x:number,z:number,r:number}>} [opts.exclusionCircles]
   */
  async load({
    pathPositions = new Float32Array(0),
    pathCount = 0,
    pathRadius = 1.4,
    treePositions = [],
    exclusionCircles = [],
    multiplier = 1,
  } = {}) {
    const layers = [
      { url: '/models/nature/quaternius/grass.glb',         count: SHORT_COUNT,  scale: [0.7, 1.1],   ring: [3, FIELD_RADIUS] },
      { url: '/models/nature/quaternius/grass-wispy-1.glb', count: WISPY1_COUNT, scale: [0.7, 1.2],   ring: [3, FIELD_RADIUS] },
      { url: '/models/nature/quaternius/grass-wispy-2.glb', count: WISPY2_COUNT, scale: [0.7, 1.2],   ring: [3, FIELD_RADIUS] },
      { url: '/models/nature/quaternius/tall-grass.glb',    count: TALL_COUNT,   scale: [0.75, 1.15], ring: [TALL_RING_INNER, TALL_RING_OUTER] },
    ];
    multiplier = Math.max(0.05, Math.min(1, multiplier));
    const tunedLayers = layers.map((cfg) => ({
      ...cfg,
      count: Math.max(1, Math.round(cfg.count * multiplier)),
    }));

    const ex = { pathPositions, pathCount, pathRadius, treePositions, exclusionCircles };
    const results = await Promise.allSettled(tunedLayers.map((cfg) => this.#buildLayer(cfg, ex)));

    let placed = 0;
    let failed = 0;
    for (const r of results) {
      if (r.status === 'fulfilled') placed += r.value;
      else { failed += 1; console.warn('[Grass] layer failed', r.reason); }
    }
    return { placed, failed };
  }

  async #buildLayer(cfg, ex) {
    const gltf = await this.loader.loadGLTF(cfg.url);
    const root = gltf.scene;
    root.updateMatrixWorld(true);

    const protos = [];
    root.traverse((child) => { if (child.isMesh) protos.push(child); });
    if (protos.length === 0) return 0;

    // Build placement transforms once; all sub-meshes of this GLB reuse them.
    const transforms = [];
    const dummy = new THREE.Object3D();
    const [minR, maxR] = cfg.ring;
    // Worst case the filter rejects every sample; cap retries so a fully-
    // blocked layer doesn't spin forever. 6× target is generous given the
    // typical exclusion area is < 20% of the disc.
    const ATTEMPT_CAP = cfg.count * 6;
    let attempts = 0;
    while (transforms.length < cfg.count && attempts < ATTEMPT_CAP) {
      attempts++;
      const angle = this.rng() * Math.PI * 2;
      const r = Math.sqrt(this.rng() * (maxR * maxR - minR * minR) + minR * minR);
      const x = Math.cos(angle) * r;
      const z = Math.sin(angle) * r;
      if (this.#isExcluded(x, z, ex)) continue;
      const y = this.terrain ? this.terrain.heightAt(x, z) : 0;
      const scale = cfg.scale[0] + this.rng() * (cfg.scale[1] - cfg.scale[0]);

      dummy.position.set(x, y + GROUND_LIFT, z);
      dummy.rotation.y = this.rng() * Math.PI * 2;
      dummy.scale.setScalar(scale);
      dummy.updateMatrix();
      transforms.push(dummy.matrix.clone());
    }

    if (transforms.length === 0) return 0;

    const finalMatrix = new THREE.Matrix4();
    let total = 0;

    for (const proto of protos) {
      const src = Array.isArray(proto.material) ? proto.material[0] : proto.material;
      const material = src.clone();
      material.metalness = 0;
      if (material.roughness !== undefined) material.roughness = Math.max(material.roughness, 0.9);
      // Override Quaternius's painted green so the day/night cycle can drive
      // colour from a single uniform. Per-instance jitter (instanceColor)
      // multiplies this — keep base at GRASS_DAY so day mode reads correctly
      // without any tween having run.
      material.color.copy(this.baseColor);

      this.#applyWindHook(material);
      if (material.isMeshStandardMaterial) patchShadowTint(material);

      const inst = new THREE.InstancedMesh(proto.geometry, material, transforms.length);
      inst.castShadow = false;
      inst.receiveShadow = true;
      inst.name = `grass:${cfg.url.split('/').pop()}:${proto.name || 'mesh'}`;

      for (let i = 0; i < transforms.length; i++) {
        finalMatrix.multiplyMatrices(transforms[i], proto.matrixWorld);
        inst.setMatrixAt(i, finalMatrix);
      }
      inst.instanceMatrix.needsUpdate = true;

      // Per-instance brightness jitter (±10% multiplier on RGB).
      const tmpColor = new THREE.Color();
      for (let i = 0; i < transforms.length; i++) {
        const j = 0.9 + this.rng() * 0.2;
        tmpColor.setRGB(j, j, j);
        inst.setColorAt(i, tmpColor);
      }
      if (inst.instanceColor) inst.instanceColor.needsUpdate = true;

      this.scene.add(inst);
      this.instancedMeshes.push(inst);
      this.materials.push(material);
      total += transforms.length;
    }
    return total;
  }

  /**
   * Vertex displacement that bends the tip of each tuft using the shared
   * uWindTime. Anchored bases stay put — `windFactor = smoothstep(0, 0.5,
   * position.y)` only opens up above ~0.5m of mesh height. Per-instance
   * phase comes from instanceMatrix[3].xz so adjacent tufts sway out of
   * sync (no monolithic wave).
   *
   * Hook chains BEFORE patchShadowTint, which wraps prevHook itself.
   */
  #applyWindHook(material) {
    const windUniforms = this.wind?.uniforms;
    const playerUniforms = this.playerUniforms;
    material.onBeforeCompile = (shader) => {
      if (windUniforms) Object.assign(shader.uniforms, windUniforms);
      Object.assign(shader.uniforms, playerUniforms);
      shader.vertexShader = shader.vertexShader
        .replace(
          '#include <common>',
          `#include <common>
           uniform float uWindTime;
           uniform vec2 uPlayerPos;
           uniform float uPlayerBendRadius;
           uniform float uPlayerBendStrength;`,
        )
        .replace(
          '#include <begin_vertex>',
          `#include <begin_vertex>
           float windFactor = smoothstep(0.0, 0.5, position.y);
           transformed.x += sin(uWindTime * 1.5 + position.x * 0.5 + instanceMatrix[3][0] * 0.3) * 0.08 * windFactor;
           transformed.z += cos(uWindTime * 1.2 + position.z * 0.5 + instanceMatrix[3][2] * 0.3) * 0.05 * windFactor;
           // Player bend — push the tip of each blade away from the player.
           // Per-instance world XZ comes from instanceMatrix[3].xz; only the
           // upper half of each blade bends (windFactor already gates by Y).
           vec2 instWorldXZ = vec2(instanceMatrix[3][0], instanceMatrix[3][2]);
           vec2 fromPlayer = instWorldXZ - uPlayerPos;
           float distToPlayer = length(fromPlayer);
           float bendFalloff = 1.0 - smoothstep(0.0, uPlayerBendRadius, distToPlayer);
           if (bendFalloff > 0.0) {
             vec2 bendDir = (distToPlayer > 0.0001) ? fromPlayer / distToPlayer : vec2(0.0);
             float bendAmt = uPlayerBendStrength * bendFalloff * windFactor;
             transformed.x += bendDir.x * bendAmt;
             transformed.z += bendDir.y * bendAmt;
           }`,
        );
    };
  }

  #isExcluded(x, z, ex) {
    for (let i = 0; i < ex.pathCount; i++) {
      const dx = x - ex.pathPositions[i * 2 + 0];
      const dz = z - ex.pathPositions[i * 2 + 1];
      if (dx * dx + dz * dz < ex.pathRadius * ex.pathRadius) return true;
    }
    for (const t of ex.treePositions) {
      const dx = x - t.x;
      const dz = z - t.z;
      if (dx * dx + dz * dz < TREE_EXCLUSION_R * TREE_EXCLUSION_R) return true;
    }
    for (const e of ex.exclusionCircles) {
      const dx = x - e.x;
      const dz = z - e.z;
      if (dx * dx + dz * dz < e.r * e.r) return true;
    }
    return false;
  }

  /**
   * Update the shared player-bend uniform. Cheap: it's a single Vector2
   * already shared across every grass material via onBeforeCompile.
   */
  setPlayerPos(playerPos) {
    this.playerUniforms.uPlayerPos.value.set(playerPos.x, playerPos.z);
  }

  /** Hard-set the base colour. Called by TimeOfDay on instant mode apply. */
  setColor(hex) {
    this.baseColor.set(hex);
    this.syncColor();
  }

  /**
   * Push the current baseColor onto every material. Used as a GSAP onUpdate
   * during day/night transitions — the tween mutates `this.baseColor` and
   * this method propagates to per-layer materials.
   */
  syncColor() {
    for (const m of this.materials) m.color.copy(this.baseColor);
  }
}
