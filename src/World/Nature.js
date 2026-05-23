import * as THREE from 'three';
import { patchShadowTint } from './Palette.js';

/**
 * Nature props with material overrides + per-instance color variation.
 *
 * - Flowers: petal materials overridden to vivid red/yellow/purple;
 *   any green stem materials in the model are preserved.
 * - Trees: ring tightened to [12, 60] so they feel close and surrounding,
 *   not distant.
 *
 * Grass tufts are no longer placed from GLBs — the shader-driven blade
 * field in src/World/Grass.js covers the meadow now.
 */

const PROPS = [
  // ─── TREES — 8 models, ~67 total, ring brought in to [12, 60] ───────────
  { url: '/models/nature/tree-oak.glb',           count: 9, scale: [2.8, 4.55], ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-oak-fall.glb',      count: 8, scale: [2.8, 4.55], ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-detailed.glb',      count: 9, scale: [3.2, 5.2],  ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-detailed-fall.glb', count: 8, scale: [3.2, 5.2],  ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-fat.glb',           count: 8, scale: [2.8, 4.55], ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-tall.glb',          count: 8, scale: [3.6, 5.85], ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-pinetalla.glb',     count: 9, scale: [4.0, 6.5],  ring: [14, 60], kind: 'tree' },
  { url: '/models/nature/tree-pineroundb.glb',    count: 8, scale: [2.8, 4.55], ring: [14, 60], kind: 'tree' },

  // ─── FLOWERS — petal color overrides, stems preserved ───────────────────
  { url: '/models/nature/flower-reda.glb',    count: 12, scale: [0.5, 0.8], ring: [3, 20], kind: 'accent', petalColor: '#cc3344' },
  { url: '/models/nature/flower-yellowa.glb', count: 12, scale: [0.5, 0.8], ring: [3, 20], kind: 'accent', petalColor: '#ddaa22' },
  { url: '/models/nature/flower-purplea.glb', count: 12, scale: [0.5, 0.8], ring: [3, 20], kind: 'accent', petalColor: '#8833aa' },

  // ─── BUSHES ─────────────────────────────────────────────────────────────
  { url: '/models/nature/plant-bush.glb',         count: 8, scale: [1.2, 2.0], ring: [10, 55], kind: 'bush' },
  { url: '/models/nature/plant-bushdetailed.glb', count: 8, scale: [1.2, 2.0], ring: [10, 55], kind: 'bush' },
  { url: '/models/nature/plant-bushsmall.glb',    count: 9, scale: [0.8, 1.5], ring: [10, 50], kind: 'bush' },

  // ─── MUSHROOMS ──────────────────────────────────────────────────────────
  { url: '/models/nature/mushroom-red.glb', count: 7, scale: [1.0, 1.8], ring: [14, 50], kind: 'accent' },
  { url: '/models/nature/mushroom-tan.glb', count: 6, scale: [1.0, 1.8], ring: [14, 50], kind: 'accent' },

  // ─── ROCKS ──────────────────────────────────────────────────────────────
  { url: '/models/nature/rock-smalla.glb', count: 6, scale: [0.7, 1.3], ring: [10, 55], kind: 'rock' },
  { url: '/models/nature/rock-smallb.glb', count: 6, scale: [0.7, 1.3], ring: [10, 55], kind: 'rock' },
  { url: '/models/nature/rock-largea.glb', count: 5, scale: [1.6, 2.6], ring: [16, 60], kind: 'rock' },

  // ─── STUMPS + LOGS ──────────────────────────────────────────────────────
  { url: '/models/nature/stump-round.glb', count: 2, scale: [1.0, 1.6], ring: [14, 55], kind: 'log' },
  { url: '/models/nature/log.glb',         count: 3, scale: [1.0, 1.6], ring: [14, 55], kind: 'log' },
  { url: '/models/nature/log-stack.glb',   count: 2, scale: [1.0, 1.6], ring: [18, 60], kind: 'log' },
];

// Seeded mulberry32 RNG — placement deterministic across reloads.
function makeRng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function ringPosition(rng, minR, maxR) {
  const angle = rng() * Math.PI * 2;
  const r = Math.sqrt(rng() * (maxR * maxR - minR * minR) + minR * minR);
  return [Math.cos(angle) * r, Math.sin(angle) * r];
}

/** Is this material color green-ish? Used to preserve flower stems. */
function isGreenMaterial(color) {
  const hsl = { h: 0, s: 0, l: 0 };
  color.getHSL(hsl);
  // Green hue band 80-160° → 0.22-0.44 in normalized [0,1]
  return hsl.h > 0.20 && hsl.h < 0.45 && hsl.s > 0.15;
}

/** Is this material teal/cyan? KayKit foliage materials arrive in this range. */
function isFoliageMaterial(color) {
  const hsl = { h: 0, s: 0, l: 0 };
  color.getHSL(hsl);
  // Cyan/teal hue band ~144-216° → 0.4-0.6 in normalized [0,1]
  return hsl.h >= 0.4 && hsl.h <= 0.6;
}

const AUTUMN_PALETTE = ['#cc7722', '#dd8833', '#bb5511'];

/** Deterministic per-URL autumn shade so each fall tree has a stable color. */
function pickAutumnColor(url) {
  let hash = 0;
  for (let i = 0; i < url.length; i++) hash = (hash * 31 + url.charCodeAt(i)) | 0;
  return AUTUMN_PALETTE[Math.abs(hash) % AUTUMN_PALETTE.length];
}

/**
 * Unit-space collider footprints per kind. Multiplied by per-instance scale.
 * Grass / accent (flowers, mushrooms) have no collider — those should be
 * walk-through. Rocks use a cuboid; everything else cylindrical.
 */
const COLLIDERS = {
  tree: { type: 'cylinder', radius: 0.25, height: 2.5 },
  bush: { type: 'cylinder', radius: 0.45, height: 0.7 },
  rock: { type: 'cuboid', half: [0.45, 0.4, 0.45] },
  log:  { type: 'cuboid', half: [0.6, 0.3, 0.3] },
};

export class Nature {
  constructor(scene, loader, terrain, physics = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    this.physics = physics;
    this.rng = makeRng(0xc0ffee);
    this.instancedMeshes = [];
    /** [{x, z, r}] zones where solid props (trees/bushes/rocks/logs) won't spawn. */
    this.exclusions = [];
  }

  /** Register a no-spawn circle. Call before load(). */
  addExclusion(x, z, r) {
    this.exclusions.push({ x, z, r });
  }

  #isExcluded(x, z, kind) {
    if (kind === 'grass' || kind === 'accent') return false; // grass/flowers OK
    for (const e of this.exclusions) {
      const dx = x - e.x;
      const dz = z - e.z;
      if (dx * dx + dz * dz < e.r * e.r) return true;
    }
    return false;
  }

  async load() {
    const results = await Promise.allSettled(
      PROPS.map(async (cfg) => {
        const gltf = await this.loader.loadGLTF(cfg.url);
        return { cfg, gltf };
      }),
    );

    let placed = 0;
    let failed = 0;
    for (const r of results) {
      if (r.status !== 'fulfilled') {
        failed += 1;
        console.warn('[Nature] failed to load', r.reason);
        continue;
      }
      placed += this.#placeInstances(r.value.gltf.scene, r.value.cfg);
    }
    return { placed, failed };
  }

  #placeInstances(root, cfg) {
    root.updateMatrixWorld(true);

    const protos = [];
    root.traverse((child) => {
      if (child.isMesh) protos.push(child);
    });
    if (protos.length === 0) return 0;

    // Compute per-instance world transforms (shared by all sub-meshes).
    const instanceTransforms = [];
    const dummy = new THREE.Object3D();
    const [minR, maxR] = cfg.ring;
    const colliderShape = this.physics ? COLLIDERS[cfg.kind] : null;

    for (let i = 0; i < cfg.count; i++) {
      let x, z, tries = 0;
      do {
        [x, z] = ringPosition(this.rng, minR, maxR);
        tries++;
      } while (this.#isExcluded(x, z, cfg.kind) && tries < 8);
      if (tries === 8 && this.#isExcluded(x, z, cfg.kind)) continue; // give up this slot
      const y = this.terrain ? this.terrain.heightAt(x, z) : 0;
      const scale = cfg.scale[0] + this.rng() * (cfg.scale[1] - cfg.scale[0]);

      dummy.position.set(x, y, z);
      dummy.rotation.y = this.rng() * Math.PI * 2;
      dummy.scale.setScalar(scale);
      dummy.updateMatrix();
      instanceTransforms.push(dummy.matrix.clone());

      // Register per-instance static collider for solid props.
      if (colliderShape) {
        if (colliderShape.type === 'cylinder') {
          this.physics.addStaticCylinder(
            x, y, z,
            colliderShape.radius * scale,
            colliderShape.height * scale,
          );
        } else if (colliderShape.type === 'cuboid') {
          const [hx, hy, hz] = colliderShape.half;
          this.physics.addStaticCuboid(
            x, y, z,
            hx * scale, hy * scale, hz * scale,
          );
        }
      }
    }

    // Pre-compute per-instance color jitter for grass (variation R/G/B per blade).
    let instanceColors = null;
    if (cfg.instanceColors && cfg.instanceColors.length > 0) {
      const palette = cfg.instanceColors.map((hex) => new THREE.Color(hex));
      instanceColors = [];
      for (let i = 0; i < cfg.count; i++) {
        instanceColors.push(palette[Math.floor(this.rng() * palette.length)]);
      }
    }

    const finalMatrix = new THREE.Matrix4();
    const isCheap = cfg.kind === 'grass' || cfg.kind === 'accent';

    for (const proto of protos) {
      // Clone material so overrides don't leak across instances.
      const sourceMaterial = Array.isArray(proto.material) ? proto.material[0] : proto.material;
      const material = sourceMaterial.clone();
      material.metalness = 0;
      if (material.roughness !== undefined) {
        material.roughness = Math.max(material.roughness, 0.85);
      }

      // ── Color overrides ──────────────────────────────────────────────────
      if (cfg.baseColor) {
        // Grass: force ALL materials to the base color. Per-instance jitter
        // (instanceColor) will multiply this — so we set base WHITE so the
        // instance color shows through unaltered.
        if (instanceColors) {
          material.color.set('#ffffff');
        } else {
          material.color.set(cfg.baseColor);
        }
      } else if (cfg.petalColor) {
        // Flowers: override only non-green materials (petals). Keep stems.
        if (!isGreenMaterial(material.color)) {
          material.color.set(cfg.petalColor);
        }
      } else if (cfg.kind === 'tree') {
        // KayKit trees ship with teal/cyan foliage materials. Detect those
        // and recolor to green (or autumn for -fall.glb variants). Brown
        // trunks (low hue / low saturation) are left untouched.
        if (isFoliageMaterial(material.color)) {
          if (cfg.url.includes('-fall.glb')) {
            material.color.set(pickAutumnColor(cfg.url));
          } else {
            material.color.set('#3a8a25');
          }
        }
      }

      // Tint shadowed sides toward magenta-purple instead of going black.
      // MeshStandardMaterial only — KayKit packs ship Standard so this is safe,
      // but guard in case a future model brings a different material type.
      if (material.isMeshStandardMaterial) patchShadowTint(material);

      const actualCount = instanceTransforms.length;
      const inst = new THREE.InstancedMesh(proto.geometry, material, actualCount);
      inst.castShadow = !isCheap;
      inst.receiveShadow = true;
      inst.name = `nature:${cfg.url.split('/').pop()}:${proto.name || 'mesh'}`;

      for (let i = 0; i < actualCount; i++) {
        finalMatrix.multiplyMatrices(instanceTransforms[i], proto.matrixWorld);
        inst.setMatrixAt(i, finalMatrix);
      }
      inst.instanceMatrix.needsUpdate = true;

      // Per-instance color variation for grass.
      if (instanceColors) {
        for (let i = 0; i < actualCount; i++) {
          inst.setColorAt(i, instanceColors[i]);
        }
        if (inst.instanceColor) inst.instanceColor.needsUpdate = true;
      }

      this.scene.add(inst);
      this.instancedMeshes.push(inst);
    }

    return instanceTransforms.length;
  }
}
