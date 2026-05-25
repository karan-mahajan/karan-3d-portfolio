import * as THREE from 'three';
import { patchShadowTint, DUSK } from './Palette.js';
import { PROJECTS_CENTER } from '../Portfolio/Billboards.js';
import { SECTION_POSITIONS } from '../Portfolio/Signs.js';

/**
 * Walkable path tiles connecting spawn (0,0) to each cardinal section.
 *
 *   Stone tiles  → Projects (E) + Experience (N)  — "professional" sections.
 *   Wood tiles   → Skills   (S) + Contact   (W)  — "personal"     sections.
 *
 * Per direction we lay {TILE_COUNT} tiles in a straight line from spawn to
 * the section endpoint, with ±5° yaw jitter and ±0.15 m perpendicular offset
 * (seeded → layout stable across reloads), then drop a small ring of tiles
 * around the endpoint to form a clearing.
 *
 * Tile positions are planned synchronously in the constructor so callers can
 * register Nature no-spawn circles via `addExclusionsTo(nature)` BEFORE
 * Nature's async scatter runs. Actual GLB loads are deferred to `load()`.
 */

const TILE_LIFT = 0.02;             // Y above terrain to avoid Z-fighting
const TILE_SCALE = 1.4;
const TILE_COUNT = 12;              // ~12 tiles per radial path
const TILE_JITTER_OFFSET = 0.15;    // perpendicular ± metres
const TILE_JITTER_YAW = Math.PI / 36; // ±5°
const CLEARING_TILE_COUNT = 6;
const CLEARING_RADIUS_OUTER = 3.0;
const CLEARING_RADIUS_INNER = 1.8;
const EXCLUSION_RADIUS = 1.4;
const PATH_START_OFFSET = 2.5;      // first tile this far from spawn
const PATH_END_OFFSET = 2.5;        // last tile this far before endpoint
// Default patchShadowTint strength (0.65) blew out the path-tile materials —
// stone read pink and wood read neon magenta. 0.35 keeps a subtle dusk-warm
// tint in shadow without overriding the natural stone/wood albedo.
const SHADOW_TINT_STRENGTH = 0.35;
// Cap fed to the grass-flatten uniform array. If a future bump pushes the
// total above this we downsample evenly — Grass.glsl can't size its uniform
// array dynamically (must be compile-time constant), and shader uniform array
// sizes >96 start to compile-fail on weaker GPUs.
const MAX_GRASS_FLATTEN_TILES = 96;

// Stone paths use Quaternius's round rock-path tiles — smoother / more
// organic than the blocky KayKit stone tiles they replaced. The wide/thin
// pair is the visual mainstream, the three small variants give per-tile
// variety so the radial run doesn't read as a stamped line.
const STONE_VARIANTS = [
  '/models/nature/quaternius/rock-path-round-wide.glb',
  '/models/nature/quaternius/rock-path-round-thin.glb',
  '/models/nature/quaternius/rock-path-round-small-1.glb',
  '/models/nature/quaternius/rock-path-round-small-2.glb',
  '/models/nature/quaternius/rock-path-round-small-3.glb',
];
// Wood paths stay on KayKit — preserves the "professional vs personal"
// material story (stone for Projects/Experience, wood for Skills/Contact).
const WOOD_VARIANTS = [
  '/models/nature/path-wood.glb',
  '/models/nature/path-woodcorner.glb',
  '/models/nature/path-woodend.glb',
];

// Seeded mulberry32 — matches the style used by Nature.js.
function makeRng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// FNV-1a-ish hash so per-direction seeds are deterministic.
function hashSeed(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function lastOf(arr) {
  return arr[arr.length - 1];
}

export class Paths {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../Utils/Loader.js').Loader} loader
   * @param {import('./Terrain.js').Terrain} terrain
   */
  constructor(scene, loader, terrain, physics = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    // Optional — when provided, each placed tile gets a thin static cuboid
    // collider sized to its scaled bbox so the player walks ON the visible
    // stone surface (not through it and into the terrain heightfield).
    // Without this the character's feet sink visually into the top face of
    // each tile because the heightfield is a flat plane underneath.
    this.physics = physics;

    /** Planned tile placements (synchronous, used for exclusions + later mesh build). */
    this.tilePlans = [];

    this.group = new THREE.Group();
    this.group.name = 'paths';
    this.scene.add(this.group);

    const lastExp = lastOf(SECTION_POSITIONS.experiencePath);
    this.routes = [
      { key: 'projects',   endpoint: { x: PROJECTS_CENTER.x,           z: PROJECTS_CENTER.z },           material: 'stone' },
      { key: 'experience', endpoint: { x: lastExp.x,                   z: lastExp.z },                   material: 'stone' },
      { key: 'skills',     endpoint: { x: SECTION_POSITIONS.skills.x,  z: SECTION_POSITIONS.skills.z },  material: 'wood'  },
      { key: 'contact',    endpoint: { x: SECTION_POSITIONS.contact.x, z: SECTION_POSITIONS.contact.z }, material: 'wood'  },
    ];

    for (const route of this.routes) {
      console.log(`[Paths] ${route.key} → ${route.material}  endpoint=(${route.endpoint.x.toFixed(1)}, ${route.endpoint.z.toFixed(1)})`);
      this.#planRoute(route);
    }
    this.#buildFlattenArray();
  }

  // Packed [x0, z0, x1, z1, …] of tile centres, capped at MAX_GRASS_FLATTEN_TILES
  // and downsampled evenly if the plan exceeds the cap. Consumed by Grass.js
  // via setPathExclusions() to suppress blades growing through tile faces.
  #buildFlattenArray() {
    const total = this.tilePlans.length;
    const count = Math.min(total, MAX_GRASS_FLATTEN_TILES);
    const stride = total > count ? total / count : 1;
    const arr = new Float32Array(count * 2);
    for (let i = 0; i < count; i++) {
      const idx = Math.min(Math.floor(i * stride), total - 1);
      arr[i * 2 + 0] = this.tilePlans[idx].x;
      arr[i * 2 + 1] = this.tilePlans[idx].z;
    }
    this._flattenPositions = arr;
    this._flattenCount = count;
  }

  /** Packed Float32Array of [x, z, x, z, …] tile centres for grass flattening. */
  getTilePositions() {
    return this._flattenPositions;
  }

  /** Number of tile entries packed into the array returned by getTilePositions(). */
  getTileCount() {
    return this._flattenCount;
  }

  /** Register a no-spawn circle on Nature at every planned tile centre. */
  addExclusionsTo(nature) {
    for (const t of this.tilePlans) {
      nature.addExclusion(t.x, t.z, EXCLUSION_RADIUS);
    }
  }

  async load() {
    const variants = {
      stone: await this.#loadVariants(STONE_VARIANTS),
      wood:  await this.#loadVariants(WOOD_VARIANTS),
    };
    if (variants.stone.length === 0) console.warn('[Paths] no stone tile GLBs loaded — stone directions empty');
    if (variants.wood.length === 0)  console.warn('[Paths] no wood tile GLBs loaded — wood directions empty');

    // Bucket plans by (material, variantIndex) so each bucket maps to one
    // proto scene. Each bucket becomes ONE InstancedMesh per proto-mesh
    // (typically one mesh per tile GLB), collapsing ~60 individual cloned
    // groups → ~8 instanced draw calls. Per-tile colliders are still
    // registered one-per-plan inside #placeBucket.
    const buckets = new Map();
    for (const plan of this.tilePlans) {
      const protos = variants[plan.material];
      if (!protos || protos.length === 0) continue;
      const variantIndex = plan.variantIdx % protos.length;
      const key = `${plan.material}:${variantIndex}`;
      let bucket = buckets.get(key);
      if (!bucket) {
        bucket = { proto: protos[variantIndex], plans: [], material: plan.material };
        buckets.set(key, bucket);
      }
      bucket.plans.push(plan);
    }

    let placed = 0;
    for (const bucket of buckets.values()) {
      placed += this.#placeBucket(bucket);
    }
    return { placed };
  }

  async #loadVariants(urls) {
    const out = [];
    for (const url of urls) {
      try {
        const gltf = await this.loader.loadGLTF(url);
        out.push(gltf.scene);
      } catch (err) {
        console.warn('[Paths] failed to load', url, err);
      }
    }
    return out;
  }

  #planRoute(route) {
    const { x: ex, z: ez } = route.endpoint;
    const length = Math.hypot(ex, ez);
    if (length < 0.001) return;

    const dirX = ex / length;
    const dirZ = ez / length;
    const perpX = -dirZ;
    const perpZ = dirX;
    // Yaw so tile +Z (default forward) aligns with the path direction.
    const yawForward = Math.atan2(dirX, dirZ);

    const rng = makeRng(hashSeed(`path:${route.key}`));

    // Row along the path.
    const usable = Math.max(0, length - PATH_START_OFFSET - PATH_END_OFFSET);
    for (let i = 0; i < TILE_COUNT; i++) {
      const t = TILE_COUNT === 1 ? 0 : i / (TILE_COUNT - 1);
      const along = PATH_START_OFFSET + t * usable;
      const jitterOff = (rng() * 2 - 1) * TILE_JITTER_OFFSET;
      const yawJ = (rng() * 2 - 1) * TILE_JITTER_YAW;
      const variantIdx = Math.floor(rng() * 1000);
      this.tilePlans.push({
        x: dirX * along + perpX * jitterOff,
        z: dirZ * along + perpZ * jitterOff,
        yaw: yawForward + yawJ,
        material: route.material,
        variantIdx,
      });
    }

    // Clearing cluster around the endpoint.
    for (let i = 0; i < CLEARING_TILE_COUNT; i++) {
      const baseAngle = (i / CLEARING_TILE_COUNT) * Math.PI * 2;
      const angle = baseAngle + (rng() - 0.5) * 0.6;
      const r = CLEARING_RADIUS_INNER + rng() * (CLEARING_RADIUS_OUTER - CLEARING_RADIUS_INNER);
      const yawJ = (rng() * 2 - 1) * TILE_JITTER_YAW;
      const variantIdx = Math.floor(rng() * 1000);
      this.tilePlans.push({
        x: ex + Math.cos(angle) * r,
        z: ez + Math.sin(angle) * r,
        yaw: yawForward + yawJ,
        material: route.material,
        variantIdx,
      });
    }
  }

  // Builds one InstancedMesh per mesh inside the bucket's proto scene, plus
  // one static cuboid collider per plan so the character controller still
  // walks on top of each tile (autostep 0.4 m needs a physical surface).
  // Mirrors Nature.js's instancing pattern: per-proto material cloned once,
  // per-instance world matrix = tileTransform × proto.matrixWorld.
  #placeBucket({ proto, plans, material }) {
    proto.updateMatrixWorld(true);

    const meshProtos = [];
    proto.traverse((child) => {
      if (child.isMesh) meshProtos.push(child);
    });
    if (meshProtos.length === 0) return 0;

    // Proto-local bbox (in proto root frame) drives both collider sizing
    // and tile Y placement so the visible mesh sits flush with the terrain
    // sample + TILE_LIFT.
    const protoBox = new THREE.Box3().setFromObject(proto);
    const protoSize = protoBox.getSize(new THREE.Vector3());
    const protoCenter = protoBox.getCenter(new THREE.Vector3());

    // Pre-compute per-plan tile world matrices (shared across every mesh in
    // this bucket).
    const _pos = new THREE.Vector3();
    const _quat = new THREE.Quaternion();
    const _scale = new THREE.Vector3(TILE_SCALE, TILE_SCALE, TILE_SCALE);
    const _euler = new THREE.Euler();
    const tileMatrices = new Array(plans.length);
    for (let i = 0; i < plans.length; i++) {
      const plan = plans[i];
      const y = (this.terrain ? this.terrain.heightAt(plan.x, plan.z) : 0) + TILE_LIFT;
      _pos.set(plan.x, y, plan.z);
      _euler.set(0, plan.yaw, 0);
      _quat.setFromEuler(_euler);
      tileMatrices[i] = new THREE.Matrix4().compose(_pos, _quat, _scale);
    }

    const finalMatrix = new THREE.Matrix4();
    for (const meshProto of meshProtos) {
      const src = Array.isArray(meshProto.material) ? meshProto.material[0] : meshProto.material;
      const mat = src.clone();
      mat.metalness = 0;
      if (mat.roughness !== undefined) mat.roughness = Math.max(mat.roughness, 0.85);
      if (mat.isMeshStandardMaterial) patchShadowTint(mat, DUSK, SHADOW_TINT_STRENGTH);

      const inst = new THREE.InstancedMesh(meshProto.geometry, mat, plans.length);
      inst.castShadow = false;
      inst.receiveShadow = true;
      inst.name = `path:${material}:${meshProto.name || 'mesh'}`;
      for (let i = 0; i < plans.length; i++) {
        finalMatrix.multiplyMatrices(tileMatrices[i], meshProto.matrixWorld);
        inst.setMatrixAt(i, finalMatrix);
      }
      inst.instanceMatrix.needsUpdate = true;
      this.group.add(inst);
    }

    // Per-tile colliders preserve the existing autostep-friendly walk-on-top
    // behaviour. Compute yaw-aware AABB once from the precomputed protoSize
    // instead of building a temp scene + Box3.setFromObject per plan.
    if (this.physics) {
      const halfX = (protoSize.x * TILE_SCALE) / 2;
      const halfY = (protoSize.y * TILE_SCALE) / 2;
      const halfZ = (protoSize.z * TILE_SCALE) / 2;
      const centerYOffset = protoCenter.y * TILE_SCALE;
      for (const plan of plans) {
        const y = (this.terrain ? this.terrain.heightAt(plan.x, plan.z) : 0) + TILE_LIFT;
        const cy = y + centerYOffset;
        const absCos = Math.abs(Math.cos(plan.yaw));
        const absSin = Math.abs(Math.sin(plan.yaw));
        const worldHalfX = halfX * absCos + halfZ * absSin;
        const worldHalfZ = halfX * absSin + halfZ * absCos;
        this.physics.addStaticCuboid(plan.x, cy, plan.z, worldHalfX, halfY, worldHalfZ);
      }
    }

    return plans.length;
  }
}
