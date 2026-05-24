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

// All ring outer-radii capped at ≤ 40 so trees / bushes / rocks stay clear of
// the sandy shore (r≈40–45) and the ocean beyond it. Shore decor (half-
// submerged rocks, reeds, lily pads) is placed separately by Water.loadShoreDecor.
const PROPS = [
  // ─── QUATERNIUS TREES — Ghibli-style, native foliage colours preserved ──
  // 35 total (down from 68 after the perf pass — each Quaternius tree is
  // ~6.9k triangles, so 68 trees = 469k tris and a 1024² shadow pass over
  // all of them at once. 35 keeps the forest feeling dense around the
  // play area without busting the budget.
  // Tree (main fluffy) — 5 × 4 = 20
  { url: '/models/nature/quaternius/tree-1.glb',         count: 4, scale: [0.85, 1.35], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/tree-2.glb',         count: 4, scale: [0.85, 1.35], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/tree-3.glb',         count: 4, scale: [0.85, 1.35], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/tree-4.glb',         count: 4, scale: [0.85, 1.35], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/tree-5.glb',         count: 4, scale: [0.85, 1.35], ring: [14, 38], kind: 'tree' },
  // Twisted Tree — 5 × 2 = 10
  { url: '/models/nature/quaternius/twisted-tree-1.glb', count: 2, scale: [0.85, 1.25], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/twisted-tree-2.glb', count: 2, scale: [0.85, 1.25], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/twisted-tree-3.glb', count: 2, scale: [0.85, 1.25], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/twisted-tree-4.glb', count: 2, scale: [0.85, 1.25], ring: [14, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/twisted-tree-5.glb', count: 2, scale: [0.85, 1.25], ring: [14, 38], kind: 'tree' },
  // Pine — 5 × 1 = 5
  { url: '/models/nature/quaternius/pine-1.glb',         count: 1, scale: [0.9, 1.4],   ring: [16, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/pine-2.glb',         count: 1, scale: [0.9, 1.4],   ring: [16, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/pine-3.glb',         count: 1, scale: [0.9, 1.4],   ring: [16, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/pine-4.glb',         count: 1, scale: [0.9, 1.4],   ring: [16, 38], kind: 'tree' },
  { url: '/models/nature/quaternius/pine-5.glb',         count: 1, scale: [0.9, 1.4],   ring: [16, 38], kind: 'tree' },

  // ─── FLOWERS — Quaternius, native painted colours preserved ─────────────
  // Groups in the inner ring (cluster look), singles spread wider, petals
  // sprinkled across both rings as low-detail accent fill.
  { url: '/models/nature/quaternius/flower-group-1.glb',  count: 8, scale: [0.8, 1.2], ring: [4, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-group-2.glb',  count: 8, scale: [0.8, 1.2], ring: [4, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-single-1.glb', count: 12, scale: [0.7, 1.0], ring: [3, 25], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-single-2.glb', count: 12, scale: [0.7, 1.0], ring: [3, 25], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-petal-1.glb',  count: 6, scale: [0.6, 0.9], ring: [3, 28], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-petal-2.glb',  count: 6, scale: [0.6, 0.9], ring: [3, 28], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-petal-3.glb',  count: 6, scale: [0.6, 0.9], ring: [3, 28], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-petal-4.glb',  count: 6, scale: [0.6, 0.9], ring: [3, 28], kind: 'accent' },
  { url: '/models/nature/quaternius/flower-petal-5.glb',  count: 6, scale: [0.6, 0.9], ring: [3, 28], kind: 'accent' },

  // ─── BUSHES ─────────────────────────────────────────────────────────────
  // Bushes get colliders; ferns and plants are walk-through accents.
  { url: '/models/nature/quaternius/bush.glb',              count: 12, scale: [0.85, 1.3], ring: [10, 38], kind: 'bush' },
  { url: '/models/nature/quaternius/bush-with-flowers.glb', count: 6,  scale: [0.85, 1.2], ring: [6, 30],  kind: 'bush' },
  { url: '/models/nature/quaternius/fern.glb',              count: 12, scale: [0.7, 1.1],  ring: [10, 38], kind: 'accent' },
  { url: '/models/nature/quaternius/plant-1.glb',           count: 4,  scale: [0.7, 1.1],  ring: [6, 38],  kind: 'accent' },
  { url: '/models/nature/quaternius/plant-2.glb',           count: 4,  scale: [0.7, 1.1],  ring: [6, 38],  kind: 'accent' },
  { url: '/models/nature/quaternius/plant-big-1.glb',       count: 4,  scale: [0.9, 1.3],  ring: [8, 38],  kind: 'accent' },
  { url: '/models/nature/quaternius/plant-big-2.glb',       count: 4,  scale: [0.9, 1.3],  ring: [8, 38],  kind: 'accent' },

  // ─── MUSHROOMS ──────────────────────────────────────────────────────────
  { url: '/models/nature/quaternius/mushroom.glb',             count: 5, scale: [0.6, 1.0], ring: [12, 38], kind: 'accent' },
  { url: '/models/nature/quaternius/mushroom-laetiporus.glb',  count: 4, scale: [0.6, 1.0], ring: [14, 38], kind: 'accent' },

  // ─── ROCKS ──────────────────────────────────────────────────────────────
  // 3 medium variants placed throughout — some near trees, some standalone.
  { url: '/models/nature/quaternius/rock-medium-1.glb', count: 4, scale: [0.8, 1.3], ring: [8, 38], kind: 'rock' },
  { url: '/models/nature/quaternius/rock-medium-2.glb', count: 4, scale: [0.8, 1.3], ring: [8, 38], kind: 'rock' },
  { url: '/models/nature/quaternius/rock-medium-3.glb', count: 4, scale: [0.8, 1.3], ring: [8, 38], kind: 'rock' },

  // ─── PEBBLES ────────────────────────────────────────────────────────────
  // Small surface detail concentrated in the inner ring where paths run.
  // Walk-through (kind='accent') so the player never bumps into one.
  { url: '/models/nature/quaternius/pebble-round-1.glb',  count: 4, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-round-2.glb',  count: 4, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-round-3.glb',  count: 4, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-round-4.glb',  count: 4, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-round-5.glb',  count: 4, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-1.glb', count: 3, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-2.glb', count: 3, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-3.glb', count: 3, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-4.glb', count: 3, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-5.glb', count: 2, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },
  { url: '/models/nature/quaternius/pebble-square-6.glb', count: 2, scale: [0.7, 1.2], ring: [3, 22], kind: 'accent' },

  // ─── CLOVER ─────────────────────────────────────────────────────────────
  // Low ground cover near the spawn plaza / path edges. Walk-through.
  { url: '/models/nature/quaternius/clover-1.glb', count: 6, scale: [0.8, 1.2], ring: [3, 18], kind: 'accent' },
  { url: '/models/nature/quaternius/clover-2.glb', count: 6, scale: [0.8, 1.2], ring: [3, 18], kind: 'accent' },

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

/** Is this material pink / magenta? One of the KayKit tree GLBs ships with
 *  a stray #ff00ff material on its trunk — detect any high-saturation
 *  magenta and rewrite it to brown. */
function isMagentaMaterial(color) {
  const hsl = { h: 0, s: 0, l: 0 };
  color.getHSL(hsl);
  // Magenta hue band 280-340° → 0.78-0.94 in normalized [0,1]
  return hsl.h >= 0.78 && hsl.h <= 0.94 && hsl.s > 0.4;
}

const AUTUMN_PALETTE = ['#cc7722', '#dd8833', '#bb5511'];

/** Deterministic per-URL autumn shade so each fall tree has a stable color. */
function pickAutumnColor(url) {
  let hash = 0;
  for (let i = 0; i < url.length; i++) hash = (hash * 31 + url.charCodeAt(i)) | 0;
  return AUTUMN_PALETTE[Math.abs(hash) % AUTUMN_PALETTE.length];
}

/**
 * Quaternius tree trunks vary widely: straight pines vs sprawling twisted
 * variants whose trunks curve out 0.8–1.2m at character height. Sample the
 * unit-scale GLB at chest height and return the real XZ half-extent + centre
 * so the cylinder collider matches the visible trunk instead of a fixed
 * one-size-fits-all 0.45m. Returns null if no geometry sits in the slice
 * (caller falls back to COLLIDERS default).
 */
function measureTrunkSlice(root) {
  root.updateMatrixWorld(true);
  let minX = Infinity, maxX = -Infinity;
  let minZ = Infinity, maxZ = -Infinity;
  let count = 0;
  const v = new THREE.Vector3();
  const SLICE_LO = 0.5, SLICE_HI = 1.5;
  root.traverse((child) => {
    if (!child.isMesh || !child.geometry) return;
    const pos = child.geometry.attributes.position;
    if (!pos) return;
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      child.localToWorld(v);
      if (v.y < SLICE_LO || v.y > SLICE_HI) continue;
      if (v.x < minX) minX = v.x;
      if (v.x > maxX) maxX = v.x;
      if (v.z < minZ) minZ = v.z;
      if (v.z > maxZ) maxZ = v.z;
      count++;
    }
  });
  if (count === 0) return null;
  return {
    radius: Math.max(maxX - minX, maxZ - minZ) / 2,
    cx: (minX + maxX) / 2,
    cz: (minZ + maxZ) / 2,
  };
}

/**
 * Per-kind collider config. Two sizing strategies:
 *  - 'fixed'    : use the half/radius/height below × per-instance scale.
 *                 Right for trees (trunk is narrow, foliage shouldn't block
 *                 the player) and bushes (round-ish, easier to tune).
 *  - 'bbox'     : measure the source GLB's bounding box at unit scale,
 *                 then per-instance-scale it. Right for rocks and logs
 *                 where the player should collide with the visible mesh
 *                 outline (fixed footprints left visible mesh hanging
 *                 30-50 cm past the collider on the bigger Quaternius
 *                 rocks — player could slide into the painted rock and
 *                 end up visually inside it).
 *
 * Grass / accent (flowers, mushrooms, pebbles, clover, ferns) have no
 * collider — those should be walk-through.
 */
const COLLIDERS = {
  // Trunk radius bumped from 0.35 → 0.45 (audit item #7) so the pine
  // variants at scale 1.4 collide out to 0.63 m, covering their painted base.
  tree: { type: 'cylinder', sizing: 'fixed', radius: 0.45, height: 3.0 },
  bush: { type: 'cylinder', sizing: 'fixed', radius: 0.45, height: 0.7 },
  rock: { type: 'cuboid',   sizing: 'bbox' },
  log:  { type: 'cuboid',   sizing: 'bbox' },
};

export class Nature {
  constructor(scene, loader, terrain, physics = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    this.physics = physics;
    this.rng = makeRng(0xc0ffee);
    this.instancedMeshes = [];
    /** [{position, type, surfaceRadius}] entries for proximity-based push prompts. */
    this.pushSpots = [];

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

    // Source GLB bbox at unit scale — used for 'bbox'-sized colliders so the
    // collider fills the actual visible mesh. protoSize × per-instance scale
    // gives the per-instance footprint; protoCenter lets us align the
    // collider centre to the visible mesh centre regardless of where the
    // GLB's origin sits (some Quaternius props are origin-at-base, some
    // origin-at-centre).
    const protoBox = new THREE.Box3().setFromObject(root);
    const protoSize = protoBox.getSize(new THREE.Vector3());
    const protoCenter = protoBox.getCenter(new THREE.Vector3());

    // Compute per-instance world transforms (shared by all sub-meshes).
    const instanceTransforms = [];
    const dummy = new THREE.Object3D();
    const [minR, maxR] = cfg.ring;
    const colliderShape = this.physics ? COLLIDERS[cfg.kind] : null;
    // Trees: measure the actual trunk XZ extent at character height so the
    // cylinder collider matches the visible mesh (twisted trees curve well
    // past the 0.45m default and the player could stand inside the painted
    // trunk). Computed once per prop and reused across instances.
    const trunkMeasure = (cfg.kind === 'tree') ? measureTrunkSlice(root) : null;

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
      // 'fixed' (trees/bushes): use the tuned half/radius constants × scale.
      // 'bbox'  (rocks/logs)  : derive half-extents from the measured scaled
      //   bbox, and shift the collider centre to match the visible mesh
      //   centre so the player can't stand inside the painted rock.
      // colliderOuter is the distance from the spot centre to the visible
      // mesh surface — used by ActionPrompts._snapToPushDistance to position
      // the player so the push animation's hand at apex just touches the
      // surface. Captured per-shape below.
      let instanceColliderOuter = null;
      if (colliderShape) {
        if (colliderShape.type === 'cylinder') {
          let trunkR = colliderShape.radius;
          let trunkCx = x, trunkCz = z;
          if (trunkMeasure) {
            // Never shrink below the tuned default — a measured slice that
            // misses (very thin trunk) shouldn't drop us under it.
            trunkR = Math.max(colliderShape.radius, trunkMeasure.radius);
            // Apply the instance yaw so leaning trunks collide on the side
            // they actually lean toward, not the GLB-origin point.
            const cy = Math.cos(dummy.rotation.y);
            const sy = Math.sin(dummy.rotation.y);
            trunkCx = x + scale * (cy * trunkMeasure.cx + sy * trunkMeasure.cz);
            trunkCz = z + scale * (-sy * trunkMeasure.cx + cy * trunkMeasure.cz);
          }
          this.physics.addStaticCylinder(
            trunkCx, y, trunkCz,
            trunkR * scale,
            colliderShape.height * scale,
          );
          instanceColliderOuter = trunkR * scale;
        } else if (colliderShape.type === 'cuboid') {
          let hx, hy, hz, yBottom, cx, cz;
          if (colliderShape.sizing === 'bbox') {
            hx = (protoSize.x / 2) * scale;
            hy = (protoSize.y / 2) * scale;
            hz = (protoSize.z / 2) * scale;
            // Some Quaternius rock GLBs have their geometry origin offset
            // ~1 m from the painted mesh's XZ centre. Apply Y-rotation to
            // the proto-local centre and shift the collider so it lands on
            // the visible mesh rather than alongside it (otherwise player
            // walks into the painted rock on the offset side).
            const cy = Math.cos(dummy.rotation.y);
            const sy = Math.sin(dummy.rotation.y);
            cx = x + scale * (cy * protoCenter.x + sy * protoCenter.z);
            cz = z + scale * (-sy * protoCenter.x + cy * protoCenter.z);
            yBottom = y + protoCenter.y * scale - hy;
          } else {
            [hx, hy, hz] = colliderShape.half;
            hx *= scale; hy *= scale; hz *= scale;
            cx = x; cz = z;
            yBottom = y;
          }
          // Rotate the collider with the visible mesh — without this the
          // axis-aligned cuboid leaves the painted rock corners poking
          // 30-50 cm past the collider at ~45° yaws.
          this.physics.addStaticCuboid(cx, yBottom, cz, hx, hy, hz, dummy.rotation.y);
          // Player can hit the cuboid at any face — use the larger XZ
          // half-extent as a reasonable "outer radius" for the push snap.
          instanceColliderOuter = Math.max(hx, hz);
        }
      }

      // Record push-spot for trees/rocks/logs above a usefulness threshold.
      // Bushes / small accents are skipped so the hint doesn't spam in low
      // shrubbery. The surfaceRadius below = collider half-width × scale +
      // a small "near" buffer the player can stand within before the chip
      // fires.
      if (colliderShape && cfg.kind !== 'bush') {
        const buffer = cfg.kind === 'tree' ? 1.8 : 1.2;
        let surfaceRadius, spotX = x, spotZ = z;
        if (colliderShape.type === 'cylinder') {
          surfaceRadius = colliderShape.radius * scale + buffer;
        } else if (colliderShape.sizing === 'bbox') {
          surfaceRadius = Math.max(protoSize.x, protoSize.z) * 0.5 * scale + buffer;
          // Match the collider's XZ shift so the prompt fires off the
          // visible mesh, not the GLB-origin point (which can be ~1 m
          // away from the painted centre on some Quaternius rocks).
          const cy = Math.cos(dummy.rotation.y);
          const sy = Math.sin(dummy.rotation.y);
          spotX = x + scale * (cy * protoCenter.x + sy * protoCenter.z);
          spotZ = z + scale * (-sy * protoCenter.x + cy * protoCenter.z);
        } else {
          surfaceRadius = Math.max(colliderShape.half[0], colliderShape.half[2]) * scale + buffer;
        }
        if (surfaceRadius >= 1.2) {
          this.pushSpots.push({
            position: new THREE.Vector3(spotX, y, spotZ),
            type: cfg.kind,           // 'tree' | 'rock' | 'log'
            surfaceRadius,
            colliderRadius: instanceColliderOuter,
          });
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
      } else if (cfg.kind === 'tree' && !cfg.url.includes('/quaternius/')) {
        // KayKit trees ship with teal/cyan foliage materials. Detect those
        // and recolor to green (or autumn for -fall.glb variants). Brown
        // trunks (low hue / low saturation) are left untouched.
        // Quaternius trees ship with correct PBR colours baked in, so the
        // override is skipped for those — guard by the URL substring above.
        if (isFoliageMaterial(material.color)) {
          if (cfg.url.includes('-fall.glb')) {
            material.color.set(pickAutumnColor(cfg.url));
          } else {
            material.color.set('#3a8a25');
          }
        }
        // One tree GLB ships with a stray magenta trunk material —
        // override to a standard wood brown wherever it appears.
        if (isMagentaMaterial(material.color)) {
          material.color.set('#6b4226');
        }
      }

      // Tint shadowed sides toward magenta-purple instead of going black.
      // MeshStandardMaterial only — KayKit packs ship Standard so this is safe,
      // but guard in case a future model brings a different material type.
      if (material.isMeshStandardMaterial) patchShadowTint(material);

      const actualCount = instanceTransforms.length;
      const inst = new THREE.InstancedMesh(proto.geometry, material, actualCount);
      // Trees / bushes / rocks all live in rings 10–60u from spawn; the
      // sun's shadow frustum is only ±15u around the player. They'd never
      // actually appear in the shadow map, but the renderer still
      // submits them — disable shadow casting outright. Receive stays on
      // so the player's own shadow can land on them when close.
      inst.castShadow = false;
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
