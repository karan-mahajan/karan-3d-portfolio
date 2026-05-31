import {
  attribute,
  clamp,
  color,
  dot,
  float,
  Fn,
  mix,
  positionWorld,
  texture,
  uniform,
  uv,
  vertexColor,
  vec2,
  vec3,
} from "three/tsl";
import * as THREE from "three/webgpu";
import {
  MeshLambertNodeMaterial,
  MeshStandardNodeMaterial,
} from "three/webgpu";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

// Tree GLB systems that ship a solid low-poly GREEN canopy primitive (material
// `*_canopy_*`) alongside their trunk → foliage species key. ONLY oak does:
// verified from the GLBs, oakTrees has `oak_canopy_karan_*` (green) + `oak_trunk_
// karan` per `oakBody`; birch/cherry are trunk/branch-only and get their leaves
// from the treeLeaves ref empties instead. The canopy is just the placement
// GUIDE — we sample anchors across it (in its form), delete the green primitive,
// and grow SDF leaf blobs there, leaving the trunk. See #extractTreeFoliage.
const TREE_SYSTEMS = { oakTrees: "oak" };
// Canopy → foliage-anchor sampling. Poisson-thin the canopy verts to this world
// spacing; each surviving point grows one SDF blob scaled to fill the gap.
const CANOPY_ANCHOR_SPACING = 1.25; // m between blobs
const CANOPY_SCALE_FACTOR = 0.62; // blob scale = spacing × this (× jitter)
const CANOPY_SCALE_JITTER = 0.2; // ±fraction deterministic size variation
// Tree trunks need runtime Rapier colliders — the baked colliders.glb ships
// NONE for trees, so the player walks straight through them. Each tree is a
// separate mesh (oak_trunk_karan / birch_*_bark_karan / cherry_trunk_dark_brown),
// so we size one static cylinder per trunk mesh from its base slice (branch/leaf
// spread higher up must NOT fatten the cylinder).
const TREE_TRUNK_SYSTEMS = new Set(["oakTrees", "birchTrees", "cherryTrees"]);
const TRUNK_MATERIAL_RE = /trunk|bark/i; // trunk/bark mesh → gets a collider
const TRUNK_BASE_SLICE = 0.25; // sample the bottom 25% for the radius
const TRUNK_RADIUS_MIN = 0.16;
const TRUNK_RADIUS_MAX = 0.7;
const TRUNK_RADIUS_SHRINK = 0.85; // visible bark sits a touch inside bbox
const DYNAMIC_BRICK_SCALE = 0.5;
const DYNAMIC_BRICK_TEMPLATES = new Set(["brickKerbMesh", "brickPileMesh"]);
const MATERIAL_CONSOLIDATION_SKIP_SYSTEMS = new Set(["terrain", "bonfires"]);
const MATERIAL_CONSOLIDATION_SKIP_MATERIAL_RE = /^(bonfire_|skill_base_)/i;
const MATERIAL_CONSOLIDATION_SKIP_OBJECT_RE = /^skillSphere_/i;
const WORLD_EMISSIVE_ATTR = "worldEmissive";
const WORLD_ROUGHNESS_ATTR = "worldRoughness";

// Spatial-chunk geometry merge (runs after material consolidation). Static
// decorative props that already carry a shared world material are bucketed by
// (coarse world grid cell × material) and merged into one mesh per bucket → one
// draw call. Bucketing by a grid (rather than a blanket per-system merge) keeps
// each merged mesh's AABB bounded, so per-mesh frustum culling still skips
// off-screen chunks. ALLOW-LIST ONLY: systems with no runtime name lookup, no
// animation, and no later re-materialisation. Deliberately OUT: trees
// (push/foliage-sensitive), lava (re-materialised by name), areas (section
// markers looked up by name), miscFx (animated air dancers/animals + dynamic
// title letters), bonfires (styled at runtime).
//
// Trees ARE included: v3 has no procedural push spots (nature.pushSpots is empty
// — see ctor), oak's green canopy is already stripped into foliage anchors
// before this runs (#extractTreeFoliage), birch/cherry leaves come from the
// separate instanced treeLeaves system, and trunk colliders are built earlier in
// load(). So only static trunk/branch geometry survives to merge here, and
// nothing looks it up by name.
const MERGE_SAFE_SYSTEMS = new Set([
  "structures",
  "scenery",
  "fences",
  "benches",
  "lanterns",
  "poleLights",
  "statue",
  "birchTrees",
  "cherryTrees",
  "oakTrees",
  "areas",
]);
// `areas` is the interactive portfolio core, so it's the one system that needs a
// name guard on top of the shared-material check. Auto-excluded already:
// `skillSphere_*` (skipped from consolidation → no shared material → never
// merged), which covers the animated orbit rings + core that SkillSphere.js
// spins/recolours by name. This regex additionally protects content/decal/
// animatable surfaces the half-wired portfolio layer mounts onto (PortfolioMounts
// reads `contact_inscription_plinth`; signs/board-face/mailbox are likely future
// mount or motion targets). Everything else in `areas` — projectHut_* shells,
// contactBoard_* structure — is inert decoration referenced nowhere in src/.
const AREAS_MERGE_EXCLUDE_RE =
  /(inscription|_sign|mailbox|board_face|board_text|artifact)/i;
const MERGE_CHUNK_SIZE = 28; // m — grid cell for the spatial bucket
const MERGE_KEEP_ATTRS = [
  "position",
  "normal",
  "color",
  WORLD_EMISSIVE_ATTR,
  WORLD_ROUGHNESS_ATTR,
];

// Instanced systems whose templates are SOLID props the player must not walk
// through → one static box per instance, sized to the visible world AABB
// (CLAUDE.md rule 5). colliders.glb ships NO rock proxies (verified: 67 tube_ +
// 6 cuboid_ + 10 Footprint_, zero rock/basalt), so rocks collide at runtime.
// Flowers are walk-through accents (not in this set) → no collider.
const SOLID_INSTANCE_SYSTEMS = new Set(["rocks"]);
const INSTANCE_COLLIDER_HALF_MIN = 0.05;
const BENCH_MESH_RE = /^bench_/i;
const BENCH_PROXY_RE = /^cuboid_bench_/i;
const SHADOW_RECEIVER_RE = /slab|foundation|path|pave|stone|brick/i;

// Rope-and-post fences (fences.glb) ship no colliders. We rebuild thin wall
// segments at runtime by clustering the posts mesh into post centres and
// linking ADJACENT posts. Real spans run 3.1–4.5 m (projects is the widest);
// the next-closest non-adjacent pair is 6.8 m (a run's end-posts, already
// bridged by the middle post) — so FENCE_MAX_SPAN sits between the two.
const FENCE_MIN_POST_HEIGHT = 0.8; // posts ~1.21 m tall; skips the ~0.46 m rope mesh
const FENCE_POST_CLUSTER_R2 = 0.35 * 0.35; // XZ radius² grouping verts into one post
const FENCE_MAX_SPAN = 5.5; // link posts ≤ this apart; bigger = opening/non-adjacent
const FENCE_POST_HALF = 0.15; // extend each wall end to bury into its posts
const FENCE_HALF_THICK = 0.12; // wall ~0.24 m thick — hugs the post line
const FENCE_RIDGE_RISE = 0.22; // pitched-roof cap height; > ~1.2× halfThick so
// the roof beats the 50° climb angle → not standable
// `*Footprint_*` collider proxies are full-height ZONE volumes (section/structure
// /misc areas), NOT visible props — baking them as boxes walls off the statue,
// sections, pool and small props so the player can't approach. They're skipped at
// load; the real meshes inside carry their own tight `cuboid_`/`tube_` proxies.
// The exception: solid BUILDINGS whose footprint IS the visible wall — kept (as a
// tight oriented box) so the player can't walk through them.
const SOLID_FOOTPRINT_RE = /Footprint_(cabin|outhouse)/i;
const TITLE_LETTER_COLOR = "#24345a";
const TITLE_LETTER_EMISSIVE = "#080d18";
const TITLE_LETTER_FLOAT_CLEARANCE = 1.15;
const TITLE_LETTER_FLOAT_AMPLITUDE = 0.12;
const TITLE_LETTER_FLOAT_SPEED = 1.6;
const TITLE_LETTER_TOUCH_PADDING = 0.32;
const TITLE_LETTER_DROP_IMPULSE = 0.16;
const TITLE_LETTER_RETURN_DELAY = 5;
const TITLE_LETTER_RETURN_DURATION = 1.25;

/**
 * v3 blend-driven world loader (Bruno-style, manifest-driven).
 *
 * Reads `static/world/manifest.json` (produced by the split exporter) and:
 *   1. Loads every **monolithic** GLB into the scene as-is (terrain, structures,
 *      scenery, statue, lava, miscFx, trees, fences, benches, lanterns,
 *      poleLights, areas) — they keep their baked GLB materials, which the
 *      WebGPURenderer auto-converts to node materials.
 *   2. Bakes the terrain heightfield from `terrain/terrain.glb` (the `terrain`
 *      node carries scale 0.65 → world half-extent ±62.4; local mesh ±96) into a
 *      world-space bilinear `heightAt(x, z)` for Physics + spawn-Y sampling.
 *   3. Builds Rapier static colliders from `colliders/colliders.glb`
 *      (`tube_`→cylinder, `cuboid_`→box, `*Footprint_`→flat walkable pad;
 *      bbox→size), then discards the proxy meshes (never added to the scene).
 *   4. Collects `references.glb` empties into a typed refs map (name→entry with
 *      worldspace position + extras), keeping the live Object3D so later phases
 *      can animate pivots by name.
 *
 * Instanced systems (bricks paving, rocks, flowers) are built via
 * #loadInstancedSystem (one InstancedMesh per template from a Visual+References
 * GLB pair); rocks also get one static box collider each (solid props). Foliage
 * clouds (bushes/treeLeaves) load via loadFoliageGroups (Phase E).
 *
 * Exposes the same facade surface App.js + downstream read off the old GlbWorld
 * (terrain / nature / paths / billboards / signs / refs) so the rest of the app
 * boots unchanged; sections + interactions are rebuilt in Phase C.
 */
export class GlbV3World {
  static MANIFEST_PATH = "/world/manifest.json";
  static ASSET_BASE = "/world/";

  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;

    this.root = new THREE.Group();
    this.root.name = "glb-v3-world";
    this.scene.add(this.root);

    this.manifest = null;

    // Terrain grass mask (terrainGrass.exr). Channel G = grass density / ground
    // tint (verified: R/B empty, A=1). Loaded in load(); consumed by the
    // terrain ground material here and by the runtime Grass field. ±96 grid
    // (Plane.003) → world UV = worldXZ / (2*bounds) + 0.5.
    this.grassMask = null;
    this.grassGrid = { bounds: 96 };
    // Painted tile/slab art (Karan's resources/tiles.png, exported to
    // static/world/). Blends over the terrain wherever terrainFurnitures.R marks
    // a path. Mirrors the Blender terrain material: slabs datablock sampled by
    // world XZ × 0.2 (≈5 m repeat) into the path-mask blend. Loaded in load().
    this.tileTexture = null;
    // Tint multiplier over the whole grass-ground colour chain — defaults to
    // white (no-op) so the runtime matches the Blender material exactly; kept as
    // a uniform so day/night can later dim the ground alongside the blades.
    this.groundGrassColor = uniform(color("#ffffff"));
    this.dynamicBrickPiles = [];
    this.dynamicTitleLetters = [];
    this.materialConsolidation = null;
    this._sharedWorldMaterials = new Map();
    // Flower template geometry + colours + baked placements, collected during
    // load(); App.boot builds the swaying/player-parting Flowers field from these.
    this.flowerGroups = [];
    this.audio = null;

    // Foliage anchors sampled from each tree's green canopy (then the canopy is
    // deleted). species ('oak'|'birch'|'cherry') → [{position, scale}]. App grows
    // one SDF leaf blob per anchor. Populated by #extractTreeFoliage during load.
    this.treeCanopyAnchors = new Map();

    this.terrain = {
      mesh: null,
      size: 0,
      segments: 0,
      heights: null,
      bboxMin: null,
      heightAt: (_x, _z) => 0,
    };

    // nature facade — v3 has no procedural scatter; pushSpots stays empty until
    // Phase C/E wire real interactables. addExclusion / setPlayerUniforms are
    // no-ops kept for API parity with the v2 consumers.
    this.nature = {
      pushSpots: [],
      addExclusion: (_x, _z, _r) => {},
      setPlayerUniforms: (_u) => {},
    };

    // paths facade — packed [x,z,x,z,…] world-space centres of the path-forming
    // bricks (pave + kerb), filled by #loadInstancedSystem. App's footstep
    // surface + Footprints query these at radius 1.4 to read "stone" zones.
    // Mutate the backing field, never reassign `this.paths` (World.paths aliases
    // this object).
    this._pathTilePositions = new Float32Array(0);
    this.paths = {
      getTilePositions: () => this._pathTilePositions,
      getTileCount: () => this._pathTilePositions.length / 2,
    };

    // Interaction-layer stubs (Phase C swaps in real section interactables).
    this.billboards = {
      items: [],
      emissiveBoost: 1.0,
      update() {},
      setIndex() {},
      setFocused() {},
      closestWithin: () => null,
    };
    this.signs = {
      experienceItems: [],
      skillsPosition: null,
      contactPosition: null,
      compassPosition: null,
      resumePosition: null,
      nearContact: () => null,
    };

    // Typed refs map. `byName` holds every reference entry; `sections` indexes
    // the sectionRef_* interaction contract by section key; `markers` holds the
    // areas/* section-structure roots (projectsHut/skillsSphere/contactBoard).
    this.refs = {
      byName: new Map(), // name → { name, position, object3d, extras }
      sections: {}, // section key → entry (from sectionRef_*)
      markers: {}, // marker name → Object3D (areas section roots)
      all: [], // every ref entry, in load order
    };

    this._runtimeBenchCollidersAdded = false;
  }

  /** Load + parse the world per the manifest, populate buckets, run assertions. */
  async load(physics, opts = {}) {
    this.audio = opts.audio ?? null;
    const manifest = await fetch(GlbV3World.MANIFEST_PATH).then((r) => {
      if (!r.ok)
        throw new Error(`GlbV3World: manifest fetch failed (${r.status})`);
      return r.json();
    });
    this.manifest = manifest;

    if (manifest.grassGrid?.bounds)
      this.grassGrid.bounds = manifest.grassGrid.bounds;

    // 0. Grass mask (EXR) — needed by the terrain ground material below + the
    // runtime Grass field. Load in parallel with geometry; tolerate failure
    // (falls back to a flat placeholder ground colour).
    const maskPromise = manifest.grassMask
      ? this.loader
          .loadEXR(GlbV3World.ASSET_BASE + manifest.grassMask)
          .then((tex) => {
            tex.wrapS = THREE.ClampToEdgeWrapping;
            tex.wrapT = THREE.ClampToEdgeWrapping;
            tex.minFilter = THREE.LinearFilter;
            tex.magFilter = THREE.LinearFilter;
            tex.generateMipmaps = false;
            tex.colorSpace = THREE.NoColorSpace;
            tex.flipY = false; // EXR data is bottom-up already; match GN authoring
            tex.needsUpdate = true;
            this.grassMask = tex;
          })
          .catch((err) => {
            console.warn(
              "[GlbV3World] grass mask load failed:",
              err?.message || err,
            );
          })
      : Promise.resolve();

    // 0b. Tile/slab art for the painted paths. Sampled by world XZ in the
    // terrain ground material; tolerate failure (paths fall back to flat stone).
    const tileFile = manifest.tileTexture ?? "tiles.png";
    const tilePromise = this.loader
      .loadTexture(GlbV3World.ASSET_BASE + tileFile)
      .then((tex) => {
        tex.wrapS = THREE.RepeatWrapping;
        tex.wrapT = THREE.RepeatWrapping;
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = 4;
        tex.needsUpdate = true;
        this.tileTexture = tex;
      })
      .catch((err) => {
        console.warn(
          "[GlbV3World] tile texture load failed:",
          err?.message || err,
        );
      });

    await Promise.all([maskPromise, tilePromise]);

    // 1. Monolithic geometry — load all in parallel, add to the scene.
    const monolithic = manifest.monolithic ?? [];
    const loaded = await Promise.all(
      monolithic.map((entry) =>
        this.loader
          .loadGLTF(GlbV3World.ASSET_BASE + entry.file)
          .then((gltf) => ({ entry, gltf }))
          .catch((err) => {
            console.warn(
              `[GlbV3World] failed to load ${entry.file}:`,
              err?.message || err,
            );
            return null;
          }),
      ),
    );

    for (const item of loaded) {
      if (!item) continue;
      const { entry, gltf } = item;
      const group = gltf.scene;
      group.name = `system:${entry.system}`;
      this.root.add(group);

      if (entry.heightfield) {
        this.#findTerrainMesh(group);
        this.#bakeHeightfield();
        this.#applyTerrainGroundMaterial();
      }
      if (entry.markers) {
        for (const markerName of entry.markers) {
          const obj =
            group.getObjectByName(markerName) ??
            group.getObjectByName(`root_${markerName}`);
          if (obj) this.refs.markers[markerName] = obj;
        }
      }
      if (entry.system === "benches") {
        this.#configureBenchShadows(group);
        this.#addBenchColliders(group, physics);
      }
      if (entry.system === "scenery" || entry.system === "areas") {
        this.#configureShadowReceivers(group);
      }
      // Trees: strip the solid green canopy → SDF foliage anchors in its form.
      const treeSpecies = TREE_SYSTEMS[entry.system];
      if (treeSpecies) this.#extractTreeFoliage(group, treeSpecies);
      // Trees: give every trunk a static collider (colliders.glb has none).
      if (TREE_TRUNK_SYSTEMS.has(entry.system))
        this._addTreeTrunkColliders(group, physics);
      if (entry.system === "fences") this.#addFenceColliders(group, physics);
      if (entry.system === "miscFx")
        this.#extractDynamicTitleLetters(group, physics);
    }

    if (physics?.ready) this.#registerBridgeColliders(physics);

    // 1b. Instanced bricks — the authored stone paving (pave/kerb/pile). Other
    // instanced systems (rocks/flowers) stay deferred; only bricks are wired so
    // the walkable path reads as paving + footsteps register stone zones.
    const bricksEntry = (manifest.instanced ?? []).find(
      (e) => e.system === "bricks",
    );
    if (bricksEntry) {
      this._pathTilePositions = await this.#loadInstancedSystem(
        bricksEntry,
        physics,
      );
    }

    // 1c. Instanced rocks (SOLID — exact trimesh colliders added inside
    // #loadInstancedSystem). The reference empties carry baked world matrices, so
    // the decomposed transforms land at the authored Blender positions + height —
    // no terrain.heightAt re-grounding needed.
    const rocksEntry = (manifest.instanced ?? []).find(
      (e) => e.system === "rocks",
    );
    if (rocksEntry) await this.#loadInstancedSystem(rocksEntry, physics);

    // Flowers are NOT static InstancedMeshes — the Flowers class (App.boot, needs
    // the shared Wind) builds them as wind-swaying, player-parting clumps. Collect
    // their geometry + colours + baked placements here for App to consume.
    const flowersEntry = (manifest.instanced ?? []).find(
      (e) => e.system === "flowers",
    );
    if (flowersEntry)
      this.flowerGroups = await this.#collectFlowerGroups(flowersEntry);

    // 2. Colliders — parse the proxy GLB, build Rapier shapes, discard meshes.
    if (manifest.colliders?.file && physics) {
      await this.#loadColliders(
        GlbV3World.ASSET_BASE + manifest.colliders.file,
        physics,
      );
    }

    // 3. References — typed empties map (kept live under root for pivots).
    if (manifest.references?.file) {
      await this.#loadReferences(
        GlbV3World.ASSET_BASE + manifest.references.file,
      );
    }

    this.#consolidateBakedWorldMaterials();
    this.#mergeStaticWorldChunks();
    this.#assertBootInvariants();
    return this;
  }

  update(delta = 0, playerPos = null) {
    this.#updateFloatingTitleLetters(delta, playerPos);
    this.#syncDynamicItems(this.dynamicBrickPiles);
    this.#syncDynamicItems(this.dynamicTitleLetters);
  }

  #updateFloatingTitleLetters(delta, playerPos) {
    const dt = Math.min(Math.max(delta || 1 / 60, 0), 1 / 30);
    const touchedLetter = playerPos
      ? this.#closestTouchedFloatingTitleLetter(playerPos)
      : null;
    for (const letter of this.dynamicTitleLetters) {
      const { body } = letter;
      if (!body) continue;

      if (letter.returning) {
        this.#animateTitleLetterReturn(letter, dt);
        continue;
      }

      if (!letter.floating) {
        if (this.#isDroppedTitleLetterOnGround(letter)) {
          letter.groundedTime += dt;
        } else {
          letter.groundedTime = 0;
        }
        if (letter.groundedTime >= TITLE_LETTER_RETURN_DELAY) {
          this.#startTitleLetterReturn(letter);
        }
        continue;
      }

      const t = body.translation();
      if (playerPos && letter === touchedLetter) {
        this.#dropFloatingTitleLetter(letter, playerPos, t);
        continue;
      }

      letter.floatTime += dt;
      const bobY =
        Math.sin(
          letter.floatTime * TITLE_LETTER_FLOAT_SPEED + letter.floatPhase,
        ) * TITLE_LETTER_FLOAT_AMPLITUDE;
      body.setTranslation(
        {
          x: letter.startCenter.x,
          y: letter.startCenter.y + bobY,
          z: letter.startCenter.z,
        },
        false,
      );
      body.setRotation(letter.startRotation, false);
      body.setLinvel({ x: 0, y: 0, z: 0 }, false);
      body.setAngvel({ x: 0, y: 0, z: 0 }, false);
      body.sleep();
    }
  }

  #closestTouchedFloatingTitleLetter(playerPos) {
    let closest = null;
    let closestD2 = Infinity;
    for (const letter of this.dynamicTitleLetters) {
      if (!letter.floating || !letter.body) continue;
      const t = letter.body.translation();
      if (!this.#isPlayerTouchingFloatingLetter(letter, playerPos, t)) continue;
      const dx = playerPos.x - t.x;
      const dz = playerPos.z - t.z;
      const d2 = dx * dx + dz * dz;
      if (d2 < closestD2) {
        closest = letter;
        closestD2 = d2;
      }
    }
    return closest;
  }

  #isPlayerTouchingFloatingLetter(letter, playerPos, bodyPos) {
    const dx = playerPos.x - bodyPos.x;
    const dz = playerPos.z - bodyPos.z;
    const radius =
      Math.hypot(letter.halfExtents.x, letter.halfExtents.z) +
      TITLE_LETTER_TOUCH_PADDING;
    if (dx * dx + dz * dz > radius * radius) return false;

    const playerBottom = playerPos.y ?? 0;
    const playerTop = playerBottom + 1.7;
    const letterBottom = bodyPos.y - letter.halfExtents.y;
    const letterTop = bodyPos.y + letter.halfExtents.y;
    return playerTop >= letterBottom && playerBottom <= letterTop + 0.25;
  }

  #dropFloatingTitleLetter(letter, playerPos, bodyPos) {
    letter.floating = false;
    letter.groundedTime = 0;
    const dx = bodyPos.x - playerPos.x;
    const dz = bodyPos.z - playerPos.z;
    const len = Math.hypot(dx, dz) || 1;
    const pushX = dx / len;
    const pushZ = dz / len;
    letter.body.wakeUp();
    letter.body.applyImpulse(
      {
        x: pushX * TITLE_LETTER_DROP_IMPULSE,
        y: 0.035,
        z: pushZ * TITLE_LETTER_DROP_IMPULSE,
      },
      true,
    );
    letter.body.applyTorqueImpulse?.(
      {
        x: pushZ * 0.025,
        y: 0.018,
        z: -pushX * 0.025,
      },
      true,
    );
  }

  #isDroppedTitleLetterOnGround(letter) {
    const t = letter.body.translation();
    const groundY = this.terrain.heightAt(t.x, t.z);
    letter.mesh.updateMatrixWorld(true);
    letter._groundBox.setFromObject(letter.mesh);
    const bottomY = letter._groundBox.min.y;
    return (
      bottomY <= groundY + 0.08 ||
      (letter.body.isSleeping() && bottomY <= groundY + 0.18)
    );
  }

  #startTitleLetterReturn(letter) {
    const t = letter.body.translation();
    const r = letter.body.rotation();
    letter.returning = true;
    letter.returnTime = 0;
    letter.returnFromCenter.set(t.x, t.y, t.z);
    letter.returnFromRotation.set(r.x, r.y, r.z, r.w).normalize();
    letter.body.setLinvel({ x: 0, y: 0, z: 0 }, false);
    letter.body.setAngvel({ x: 0, y: 0, z: 0 }, false);
    letter.body.wakeUp();
  }

  #animateTitleLetterReturn(letter, dt) {
    letter.returnTime += dt;
    const t = Math.min(1, letter.returnTime / TITLE_LETTER_RETURN_DURATION);
    const ease = t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
    const center = letter._returnCenter
      .copy(letter.returnFromCenter)
      .lerp(letter.startCenter, ease);
    const rotation = letter._returnRotation
      .copy(letter.returnFromRotation)
      .slerp(letter.startRotation, ease);

    letter.body.setTranslation(center, false);
    letter.body.setRotation(rotation, false);
    letter.body.setLinvel({ x: 0, y: 0, z: 0 }, false);
    letter.body.setAngvel({ x: 0, y: 0, z: 0 }, false);

    if (t >= 1) {
      letter.returning = false;
      letter.floating = true;
      letter.groundedTime = 0;
      letter.floatTime = 0;
      letter.body.setTranslation(letter.startCenter, false);
      letter.body.setRotation(letter.startRotation, false);
      letter.body.sleep();
    }
  }

  #syncDynamicItems(items) {
    for (const item of items) {
      const { body, mesh } = item;
      if (!body || !mesh) continue;

      const t = body.translation();
      if (t.y < -8 || Math.hypot(t.x, t.z) > 95) {
        this.#resetDynamicItem(item);
        continue;
      }

      const r = body.rotation();
      item._quat.set(r.x, r.y, r.z, r.w);
      item._offset.copy(item.centerOffset).applyQuaternion(item._quat);
      mesh.position.set(t.x, t.y, t.z).sub(item._offset);
      mesh.quaternion.copy(item._quat);
    }
  }

  // ── Terrain heightfield ───────────────────────────────────────────────────

  #findTerrainMesh(group) {
    group.traverse((obj) => {
      if (
        obj.isMesh &&
        (obj.name === "terrain" || obj.name.startsWith("terrain"))
      ) {
        this.terrain.mesh = obj;
      }
    });
  }

  /**
   * Bake the visual terrain into a world-space height grid. The terrain mesh is
   * a regular subdivided plane (16641 verts = 129×129); after the node's 0.65
   * scale the grid still maps 1:1 to world XZ, so we bucket each world-space
   * vertex into a 129×129 array and read it back bilinearly.
   */
  #bakeHeightfield() {
    const mesh = this.terrain.mesh;
    if (!mesh)
      throw new Error("GlbV3World: terrain mesh missing from terrain.glb");

    mesh.updateMatrixWorld(true);
    const geometry = mesh.geometry;
    const pos = geometry.attributes.position;

    // World-space bbox (apply the mesh matrix — captures the 0.65 node scale).
    const wbox = new THREE.Box3().setFromObject(mesh);
    const bboxMin = wbox.min.clone();
    const sizeX = wbox.max.x - wbox.min.x;
    const sizeZ = wbox.max.z - wbox.min.z;
    const size = Math.max(sizeX, sizeZ);

    // 129×129 verts → 128 segments. Derive from the vertex count so a re-export
    // at a different resolution stays correct.
    const verts = Math.round(Math.sqrt(pos.count));
    const segments = verts - 1;
    const heights = new Float32Array(verts * verts);

    const vec = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      vec.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
      const u = THREE.MathUtils.clamp(
        Math.round(((vec.x - bboxMin.x) / sizeX) * segments),
        0,
        segments,
      );
      const w = THREE.MathUtils.clamp(
        Math.round(((vec.z - bboxMin.z) / sizeZ) * segments),
        0,
        segments,
      );
      heights[u * verts + w] = vec.y;
    }

    this.terrain.size = size;
    this.terrain.segments = segments;
    this.terrain.heights = heights;
    this.terrain.bboxMin = bboxMin;

    // The grass grid (Plane.003) spans the SAME world extent as the terrain:
    // a 192m GN grid × 0.651 object scale = 125m = the terrain's footprint. The
    // exporter wrote grassGrid.bounds=96 (the UN-scaled GN half-size), so the
    // runtime sampled the mask 1.5× too wide and grass landed mis-scaled all
    // over. Derive the true half-extent from the baked terrain instead.
    this.grassGrid.bounds = size / 2;

    this.terrain.heightAt = (x, z) => {
      const fu = ((x - bboxMin.x) / sizeX) * segments;
      const fw = ((z - bboxMin.z) / sizeZ) * segments;
      const u0 = THREE.MathUtils.clamp(Math.floor(fu), 0, segments);
      const w0 = THREE.MathUtils.clamp(Math.floor(fw), 0, segments);
      const u1 = THREE.MathUtils.clamp(u0 + 1, 0, segments);
      const w1 = THREE.MathUtils.clamp(w0 + 1, 0, segments);
      const tu = THREE.MathUtils.clamp(fu - u0, 0, 1);
      const tw = THREE.MathUtils.clamp(fw - w0, 0, 1);
      const h00 = heights[u0 * verts + w0];
      const h10 = heights[u1 * verts + w0];
      const h01 = heights[u0 * verts + w1];
      const h11 = heights[u1 * verts + w1];
      return (
        (1 - tu) * (1 - tw) * h00 +
        tu * (1 - tw) * h10 +
        (1 - tu) * tw * h01 +
        tu * tw * h11
      );
    };
  }

  /**
   * Install the real terrain ground material (Phase D). The GLB material's
   * baseColorTexture is the red/black `terrainFurnitures` placement mask — not
   * a colour. We replace the whole material with a node material that mirrors
   * the Blender `terrain` material's grass-ground colour chain, driven by the
   * grass mask G channel (sampled by world XZ over the ±96 grass grid,
   * `uv = worldXZ / (2*bounds) + 0.5`, matching the Blender GN + runtime Grass
   * field so blades and ground line up exactly).
   *
   * Blender chain (verified against world-v3-karan.blend, material "terrain"):
   *   Mix     = mix(olive,        midGreen,  factor = terrainGrass.G)
   *   Mix.003 = mix(Mix.Result,   darkGreen, factor = terrainGrass.G)
   * The three colours are the RGB-node default_values (scene-linear), used here
   * as linear node literals. Crucially there is **no brown dirt base**: at G→0
   * the ground is light OLIVE (RGB.001), and G only tops out ~0.64 so it settles
   * to a muted green at full grass — never pure dark green. This is why partial
   * grass halos must read olive/light-green, not the old dirt→green brown.
   *
   * MeshLambertNodeMaterial keeps the sun/shadow/fog response, so the ground
   * dims at night through the same light rig as everything else. The exported
   * GLB's `terrainFurnitures` mask (the original baseColorTexture, R channel,
   * sampled by the mesh's own UVs) then paints the tile texture (`tiles.png`,
   * sampled by world XZ × 0.2 to match the Blender slabs node's Geometry
   * Position × 0.2) over the path zones — Blender's `Mix.004`. Falls back to a
   * flat warm stone colour if the tile art failed to load, and to flat olive if
   * the grass mask failed to load.
   */
  #applyTerrainGroundMaterial() {
    const mesh = this.terrain.mesh;
    if (!mesh) return;

    // Blender RGB-node default_values (scene-linear) from the terrain material.
    const olive = vec3(0.5, 0.54, 0.05); // RGB.001 — bare/partial grass
    const midGreen = vec3(0.31, 0.39, 0.16); // RGB
    const darkGreen = vec3(0.07, 0.14, 0.06); // RGB.004 — densest grass
    const stone = color("#b3a489"); // warm fallback if the tile art fails to load
    // Blender samples the slabs image off a Geometry Position × 0.2 vector under
    // FLAT projection (world X/Y). Blender Y → runtime -Z, so the runtime UV is
    // (worldX, -worldZ) × 0.2 → ~5 m tile repeat, matching the .blend exactly.
    const TILE_SCALE = 0.2;

    // The exported terrain material's baseColorTexture IS the red/black
    // `terrainFurnitures` path mask. Capture it before we swap the material and
    // read it raw (R is a factor, not sRGB colour). Keep wrap/filter as baked.
    const furnMask = mesh.material?.map ?? null;
    if (furnMask) {
      furnMask.colorSpace = THREE.NoColorSpace;
      furnMask.needsUpdate = true;
    }

    const mat = new MeshLambertNodeMaterial();
    if (this.grassMask) {
      const invSpan = 1 / (this.grassGrid.bounds * 2);
      mat.colorNode = Fn(() => {
        // Mask is authored in Blender XY; Blender Y → runtime -Z, so negate Z
        // (same as the slabs sampling below). Without this the grass mask reads
        // Z-mirrored — grass/clears land on the opposite side from authoring.
        const guv = vec2(positionWorld.x, positionWorld.z.negate())
          .mul(invSpan)
          .add(0.5);
        // Blender's Mix nodes have clamp_factor=True; clamp G to match. G is fed
        // straight into both mix factors (no scaling) exactly as the .blend does.
        const g = clamp(texture(this.grassMask, guv).g, 0, 1);
        if (globalThis.__grassMaskDebug) return vec3(g, g, g);
        const grassGround = mix(mix(olive, midGreen, g), darkGreen, g).mul(
          this.groundGrassColor,
        );
        if (!furnMask) return grassGround;
        // terrainFurnitures.R (mesh UVs): 1 at path centre → 0 at edge.
        const pathR = clamp(texture(furnMask, uv()).r, 0, 1);
        // Paint the real tile art over the path, sampled by world XZ (Blender
        // parity). Fall back to the flat warm stone if the PNG didn't load.
        // The painted slab art reads flat/dull under Lambert (no normals), so
        // punch it up: richer saturation + a gentle contrast curve about
        // mid-grey deepens the cracks and lifts the tile faces. Hue-preserving
        // so the authored slab palette is kept, just less muddy.
        let paving;
        if (this.tileTexture) {
          const raw = texture(
            this.tileTexture,
            vec2(positionWorld.x, positionWorld.z.negate()).mul(TILE_SCALE),
          ).rgb;
          const luma = dot(raw, vec3(0.2126, 0.7152, 0.0722));
          const saturated = mix(vec3(luma), raw, float(1.35));
          paving = clamp(saturated.sub(0.5).mul(1.16).add(0.5), 0, 1.5);
        } else {
          paving = stone;
        }
        return mix(grassGround, paving, pathR);
      })();
    } else {
      mat.colorNode = olive;
    }
    mesh.material = mat;
    mesh.receiveShadow = true;
  }

  #configureBenchShadows(group) {
    let count = 0;
    group.traverse((obj) => {
      if (!obj.isMesh || !BENCH_MESH_RE.test(obj.name || "")) return;
      obj.castShadow = true;
      obj.receiveShadow = true;
      count++;
    });
    if (count > 0)
      console.log(`[GlbV3World] benches: ${count} mesh shadows enabled`);
  }

  #configureShadowReceivers(group) {
    group.traverse((obj) => {
      if (!obj.isMesh || !SHADOW_RECEIVER_RE.test(obj.name || "")) return;
      obj.receiveShadow = true;
    });
  }

  getShaderPrewarmMaterials() {
    return [...this._sharedWorldMaterials.values()];
  }

  #consolidateBakedWorldMaterials() {
    const stats = {
      meshes: 0,
      sourceMaterials: new Set(),
      skippedTexture: 0,
      skippedMixed: 0,
      skippedUnsupported: 0,
    };

    this.root.traverse((mesh) => {
      if (!mesh.isMesh) return;
      if (this.#shouldSkipMaterialConsolidation(mesh)) return;

      const materials = this.#meshMaterials(mesh);
      if (!materials.length) return;
      for (const mat of materials) stats.sourceMaterials.add(mat.uuid);

      if (materials.some((mat) => this.#materialHasTexture(mat))) {
        stats.skippedTexture++;
        return;
      }
      if (materials.some((mat) => !this.#canConsolidateMaterial(mat))) {
        stats.skippedUnsupported++;
        return;
      }

      const transparent = materials.map((mat) =>
        this.#isTransparentMaterial(mat),
      );
      if (transparent.some(Boolean) && transparent.some((value) => !value)) {
        stats.skippedMixed++;
        return;
      }

      const side = materials[0].side ?? THREE.FrontSide;
      if (materials.some((mat) => (mat.side ?? THREE.FrontSide) !== side)) {
        stats.skippedMixed++;
        return;
      }

      if (!this.#bakeWorldMaterialAttributes(mesh.geometry, mesh.material)) {
        stats.skippedUnsupported++;
        return;
      }

      mesh.material = this.#sharedWorldMaterial(
        transparent[0] ? "transparent" : "opaque",
        side,
      );
      stats.meshes++;
    });

    this.materialConsolidation = {
      meshes: stats.meshes,
      sourceMaterials: stats.sourceMaterials.size,
      sharedMaterials: this._sharedWorldMaterials.size,
      skippedTexture: stats.skippedTexture,
      skippedMixed: stats.skippedMixed,
      skippedUnsupported: stats.skippedUnsupported,
    };

    if (stats.meshes > 0) {
      console.log(
        `[GlbV3World] material consolidation: ${stats.sourceMaterials.size} baked materials on ${stats.meshes} meshes -> ${this._sharedWorldMaterials.size} shared materials`,
      );
    }
  }

  #shouldSkipMaterialConsolidation(mesh) {
    const system = this.#systemNameForObject(mesh);
    if (MATERIAL_CONSOLIDATION_SKIP_SYSTEMS.has(system)) return true;
    if ((mesh.name || "").startsWith("dynamic_titleLetter_")) return true;
    if (this.#hasAncestorMatching(mesh, MATERIAL_CONSOLIDATION_SKIP_OBJECT_RE))
      return true;
    return this.#meshMaterials(mesh).some((mat) => {
      if (!mat) return true;
      if (mat.userData?.worldSharedMaterial) return true;
      if (mat.isNodeMaterial) return true;
      return MATERIAL_CONSOLIDATION_SKIP_MATERIAL_RE.test(mat.name || "");
    });
  }

  #systemNameForObject(object) {
    let node = object;
    while (node) {
      const name = node.name || "";
      if (name.startsWith("system:")) return name.slice("system:".length);
      node = node.parent;
    }
    return "";
  }

  #hasAncestorMatching(object, re) {
    let node = object;
    while (node) {
      if (re.test(node.name || "")) return true;
      node = node.parent;
    }
    return false;
  }

  #meshMaterials(mesh) {
    if (!mesh.material) return [];
    return Array.isArray(mesh.material)
      ? mesh.material.filter(Boolean)
      : [mesh.material];
  }

  #materialHasTexture(material) {
    return !!(
      material.map ||
      material.alphaMap ||
      material.aoMap ||
      material.bumpMap ||
      material.displacementMap ||
      material.emissiveMap ||
      material.lightMap ||
      material.metalnessMap ||
      material.normalMap ||
      material.roughnessMap
    );
  }

  #canConsolidateMaterial(material) {
    if (!material?.isMaterial) return false;
    if (!material.color?.isColor) return false;
    if (material.alphaTest && material.alphaTest > 0) return false;
    if (
      material.blending !== undefined &&
      material.blending !== THREE.NormalBlending
    )
      return false;
    return true;
  }

  #isTransparentMaterial(material) {
    return material.transparent === true || (material.opacity ?? 1) < 0.999;
  }

  #bakeWorldMaterialAttributes(geometry, material) {
    const pos = geometry?.attributes?.position;
    if (!pos) return false;

    const count = pos.count;
    const colors = new Float32Array(count * 4);
    const emissive = new Float32Array(count * 3);
    const roughness = new Float32Array(count);

    if (Array.isArray(material)) {
      const groups = geometry.groups ?? [];
      if (!groups.length) return false;
      for (const group of groups) {
        const mat = material[group.materialIndex ?? 0];
        if (!mat) return false;
        this.#writeWorldMaterialRange(
          geometry,
          group.start,
          group.count,
          mat,
          colors,
          emissive,
          roughness,
        );
      }
    } else {
      const rangeCount = geometry.index?.count ?? count;
      this.#writeWorldMaterialRange(
        geometry,
        0,
        rangeCount,
        material,
        colors,
        emissive,
        roughness,
      );
    }

    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 4));
    geometry.setAttribute(
      WORLD_EMISSIVE_ATTR,
      new THREE.Float32BufferAttribute(emissive, 3),
    );
    geometry.setAttribute(
      WORLD_ROUGHNESS_ATTR,
      new THREE.Float32BufferAttribute(roughness, 1),
    );
    return true;
  }

  #writeWorldMaterialRange(
    geometry,
    start,
    count,
    material,
    colors,
    emissive,
    roughness,
  ) {
    const index = geometry.index;
    const c = material.color ?? new THREE.Color(0xffffff);
    const opacity = material.opacity ?? 1;
    const e = material.emissive ?? null;
    const emissiveIntensity = material.emissiveIntensity ?? 1;
    const r = material.roughness ?? 1;
    const end = start + count;

    for (let i = start; i < end; i++) {
      const vi = index ? index.getX(i) : i;
      colors[vi * 4] = c.r;
      colors[vi * 4 + 1] = c.g;
      colors[vi * 4 + 2] = c.b;
      colors[vi * 4 + 3] = opacity;
      emissive[vi * 3] = (e?.r ?? 0) * emissiveIntensity;
      emissive[vi * 3 + 1] = (e?.g ?? 0) * emissiveIntensity;
      emissive[vi * 3 + 2] = (e?.b ?? 0) * emissiveIntensity;
      roughness[vi] = r;
    }
  }

  #sharedWorldMaterial(kind, side) {
    const key = `${kind}:${side}`;
    const existing = this._sharedWorldMaterials.get(key);
    if (existing) return existing;

    const transparent = kind === "transparent";
    const mat = new MeshStandardNodeMaterial({
      side,
      transparent,
      depthWrite: !transparent,
      roughness: 1,
      metalness: 0,
      opacity: 1,
    });
    mat.name = `worldShared:${kind}:${this.#sideName(side)}`;
    mat.colorNode = vertexColor();
    mat.emissiveNode = attribute(WORLD_EMISSIVE_ATTR, "vec3");
    mat.roughnessNode = attribute(WORLD_ROUGHNESS_ATTR, "float");
    mat.userData.worldSharedMaterial = true;
    this._sharedWorldMaterials.set(key, mat);
    return mat;
  }

  #sideName(side) {
    if (side === THREE.DoubleSide) return "double";
    if (side === THREE.BackSide) return "back";
    return "front";
  }

  /**
   * Spatial-chunk merge of the consolidated static props. Buckets allow-listed
   * meshes by (world grid cell × shared material) and merges each bucket into a
   * single mesh → one draw call, with a bounded per-chunk AABB so frustum
   * culling still skips off-screen chunks. Safe to run here: it follows
   * #consolidateBakedWorldMaterials (meshes already carry the shared material +
   * baked color/emissive/roughness) and all collider building (colliders are
   * independent Rapier shapes), and the allow-list excludes anything looked up
   * by name, animated, or re-materialised later.
   */
  #mergeStaticWorldChunks() {
    this.root.updateMatrixWorld(true);
    const rootInverse = new THREE.Matrix4().copy(this.root.matrixWorld).invert();

    const buckets = new Map();
    const center = new THREE.Vector3();
    this.root.traverse((mesh) => {
      if (!mesh.isMesh || mesh.isInstancedMesh) return;
      const system = this.#systemNameForObject(mesh);
      if (!MERGE_SAFE_SYSTEMS.has(system)) return;
      // Within the portfolio-core `areas` system, keep mount/motion targets
      // individually addressable (skillSphere_* is already material-excluded).
      if (system === "areas" && this.#hasAncestorMatching(mesh, AREAS_MERGE_EXCLUDE_RE))
        return;
      const mat = mesh.material;
      if (Array.isArray(mat) || !mat?.userData?.worldSharedMaterial) return;
      if (!mesh.geometry?.attributes?.position) return;

      mesh.getWorldPosition(center);
      const cx = Math.floor(center.x / MERGE_CHUNK_SIZE);
      const cz = Math.floor(center.z / MERGE_CHUNK_SIZE);
      const key = `${cx}|${cz}|${mat.uuid}`;
      let bucket = buckets.get(key);
      if (!bucket) {
        bucket = { material: mat, meshes: [] };
        buckets.set(key, bucket);
      }
      bucket.meshes.push(mesh);
    });

    let mergedCount = 0;
    let removedCount = 0;
    const rel = new THREE.Matrix4();
    for (const { material, meshes } of buckets.values()) {
      if (meshes.length < 2) continue; // a lone mesh is already one draw call

      const geometries = [];
      const contributing = [];
      let castShadow = false;
      let receiveShadow = false;
      for (const mesh of meshes) {
        mesh.updateWorldMatrix(true, false);
        const geometry = this.#prepareMergeGeometry(mesh.geometry);
        if (!geometry) continue; // missing an attribute → leave this mesh alone
        // Bake into root-local space so re-parenting under root doesn't double
        // the root transform.
        rel.multiplyMatrices(rootInverse, mesh.matrixWorld);
        geometry.applyMatrix4(rel);
        geometries.push(geometry);
        contributing.push(mesh);
        castShadow ||= mesh.castShadow;
        receiveShadow ||= mesh.receiveShadow;
      }
      if (geometries.length < 2) {
        geometries.forEach((g) => g.dispose());
        continue;
      }

      const merged = mergeGeometries(geometries, false);
      geometries.forEach((g) => g.dispose());
      if (!merged) continue;
      merged.computeBoundingBox();
      merged.computeBoundingSphere();

      const mergedMesh = new THREE.Mesh(merged, material);
      mergedMesh.name = `merged:${this.#systemNameForObject(contributing[0])}`;
      mergedMesh.castShadow = castShadow;
      mergedMesh.receiveShadow = receiveShadow;
      this.root.add(mergedMesh);

      for (const mesh of contributing) {
        mesh.removeFromParent();
        mesh.geometry.dispose();
        removedCount++;
      }
      mergedCount++;
    }

    if (mergedCount > 0) {
      console.log(
        `[GlbV3World] static chunk merge: ${removedCount} meshes -> ${mergedCount} merged draw calls`,
      );
    }
  }

  /**
   * Clone a geometry down to exactly the attributes the shared world material
   * reads, non-indexed, so a heterogeneous set merges cleanly. Returns null if
   * any required attribute is missing (caller then skips that mesh).
   */
  #prepareMergeGeometry(source) {
    const base = source.index ? source.toNonIndexed() : source.clone();
    const geometry = new THREE.BufferGeometry();
    for (const name of MERGE_KEEP_ATTRS) {
      const attr = base.getAttribute(name);
      if (!attr) {
        base.dispose();
        geometry.dispose();
        return null;
      }
      geometry.setAttribute(name, attr.clone());
    }
    base.dispose();
    return geometry;
  }

  #addBenchColliders(group, physics) {
    if (!physics?.ready) return;

    group.updateMatrixWorld(true);
    const meshes = [];
    group.traverse((obj) => {
      if (obj.isMesh && BENCH_MESH_RE.test(obj.name || "")) meshes.push(obj);
    });

    let count = 0;
    for (const mesh of meshes) {
      if (this.#addMeshTrimeshCollider(mesh, physics)) count++;
    }

    if (count > 0) {
      this._runtimeBenchCollidersAdded = true;
      console.log(
        `[GlbV3World] benches: ${count} visible-mesh trimesh colliders`,
      );
    }
  }

  #addMeshTrimeshCollider(mesh, physics) {
    const geometry = mesh.geometry;
    const posAttr = geometry?.attributes?.position;
    if (!posAttr || posAttr.count < 3) return false;

    mesh.updateMatrixWorld(true);
    const points = new Float32Array(posAttr.count * 3);
    const v = new THREE.Vector3();
    for (let i = 0; i < posAttr.count; i++) {
      v.fromBufferAttribute(posAttr, i).applyMatrix4(mesh.matrixWorld);
      points[i * 3] = v.x;
      points[i * 3 + 1] = v.y;
      points[i * 3 + 2] = v.z;
    }

    let indices;
    if (geometry.index) {
      indices = new Uint32Array(geometry.index.count);
      for (let i = 0; i < geometry.index.count; i++)
        indices[i] = geometry.index.getX(i);
    } else {
      indices = new Uint32Array(posAttr.count);
      for (let i = 0; i < posAttr.count; i++) indices[i] = i;
    }

    return !!physics.addStaticTrimesh(points, indices);
  }

  // ── Colliders ─────────────────────────────────────────────────────────────

  async #loadColliders(url, physics) {
    const gltf = await this.loader.loadGLTF(url);
    const proxyScene = gltf.scene;
    proxyScene.updateMatrixWorld(true);

    const meshes = [];
    proxyScene.traverse((obj) => {
      if (obj.isMesh) meshes.push(obj);
    });

    let cyl = 0,
      box = 0,
      skipped = 0;
    const _pos = new THREE.Vector3();
    const _quat = new THREE.Quaternion();
    const _scl = new THREE.Vector3();
    const _euler = new THREE.Euler();

    for (const obj of meshes) {
      const name = obj.name || "";

      if (name.startsWith("tube_")) {
        // Upright cylinder — its world-AABB radius is yaw-invariant, so the box
        // measurement already hugs the trunk/post. Keep as-is.
        const wbox = new THREE.Box3().setFromObject(obj);
        const size = wbox.getSize(new THREE.Vector3());
        const center = wbox.getCenter(new THREE.Vector3());
        const radius = Math.max(size.x, size.z) / 2;
        const height = Math.max(size.y, 0.05);
        // addStaticCylinder lifts the body by height/2 internally; pass
        // center.y - height/2 so the cylinder centres on the bbox centre.
        physics.addStaticCylinder(
          center.x,
          center.y - height / 2,
          center.z,
          radius,
          height,
        );
        cyl++;
        continue;
      }

      if (this._runtimeBenchCollidersAdded && BENCH_PROXY_RE.test(name)) {
        skipped++;
        continue;
      }

      // `*Footprint_*` zone volumes → skip (see SOLID_FOOTPRINT_RE). Only solid
      // buildings keep a footprint collider; everything else is freed so the
      // player can walk right up to the real prop's own collider.
      if (name.includes("Footprint_") && !SOLID_FOOTPRINT_RE.test(name)) {
        skipped++;
        continue;
      }

      // cuboid_* props + solid-building footprints → ORIENTED box hugging the
      // proxy. `setFromObject`'s world AABB inflates every yaw-rotated proxy (a
      // turned bench gains ~85% depth; the cabin ~33% width) which reads as an
      // invisible wall well past the mesh. Decompose the proxy's world matrix
      // instead: half-extents from the LOCAL bbox × scale, centre from the local
      // bbox centre, and pass the yaw — same oriented-box recipe the bridge decks
      // use (#addBridgeDeckCollider).
      obj.geometry.computeBoundingBox();
      const lbb = obj.geometry.boundingBox;
      const localCenter = lbb.getCenter(new THREE.Vector3());
      const localSize = lbb.getSize(new THREE.Vector3());
      obj.matrixWorld.decompose(_pos, _quat, _scl);
      const worldCenter = localCenter.applyMatrix4(obj.matrixWorld);
      const yaw = _euler.setFromQuaternion(_quat, "YXZ").y;
      physics.addStaticCuboid(
        worldCenter.x,
        worldCenter.y,
        worldCenter.z,
        Math.max(Math.abs(localSize.x * _scl.x) / 2, 0.02),
        Math.max(Math.abs(localSize.y * _scl.y) / 2, 0.02),
        Math.max(Math.abs(localSize.z * _scl.z) / 2, 0.02),
        yaw,
      );
      box++;
    }

    // Proxy meshes are never added to the scene — physics owns them now.
    console.log(
      `[GlbV3World] colliders: ${cyl} cylinders, ${box} oriented boxes, ${skipped} footprint zones skipped`,
    );
  }

  #registerBridgeColliders(physics) {
    const bridgeMeshes = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh) return;
      if (!this.#isBridgeColliderMesh(obj.name || "")) return;
      bridgeMeshes.push(obj);
    });

    let count = 0;
    for (const mesh of bridgeMeshes) {
      if (this.#addBridgeDeckCollider(physics, mesh)) count++;
    }
    if (count > 0)
      console.log(`[GlbV3World] bridge colliders: ${count} deck slabs`);
  }

  #isBridgeColliderMesh(name) {
    return name === "bridge01" || name.startsWith("bridge02_deck_slats");
  }

  #addBridgeDeckCollider(physics, mesh) {
    const pos = mesh.geometry?.attributes?.position;
    if (!pos) return false;

    mesh.updateMatrixWorld(true);
    mesh.geometry.computeBoundingBox();
    const bbox = mesh.geometry.boundingBox;
    const localCenter = bbox.getCenter(new THREE.Vector3());
    const localSize = bbox.getSize(new THREE.Vector3());
    const worldCenter = localCenter.clone().applyMatrix4(mesh.matrixWorld);
    const _pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    mesh.matrixWorld.decompose(_pos, quat, scl);

    const thickness = mesh.name === "bridge01" ? 0.24 : 0.18;
    const deckTop = this.#meshWorldYPercentile(
      mesh,
      mesh.name === "bridge01" ? 0.75 : 0.9,
    );
    const yaw = new THREE.Euler().setFromQuaternion(quat, "YXZ").y;

    physics.addStaticCuboid(
      worldCenter.x,
      deckTop - thickness / 2,
      worldCenter.z,
      Math.max(Math.abs(localSize.x * scl.x) / 2, 0.05),
      thickness / 2,
      Math.max(Math.abs(localSize.z * scl.z) / 2, 0.05),
      yaw,
    );
    return true;
  }

  #meshWorldYPercentile(mesh, percentile) {
    const pos = mesh.geometry?.attributes?.position;
    if (!pos) return mesh.position.y;
    const ys = [];
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
      ys.push(v.y);
    }
    ys.sort((a, b) => a - b);
    const index = Math.min(
      ys.length - 1,
      Math.max(0, Math.floor((ys.length - 1) * percentile)),
    );
    return ys[index];
  }

  // ── References ────────────────────────────────────────────────────────────

  async #loadReferences(url) {
    const gltf = await this.loader.loadGLTF(url);
    const refScene = gltf.scene;
    refScene.name = "references";
    refScene.updateMatrixWorld(true);
    // Keep the empties live under root so Phase F can animate pivots by name.
    // Empties carry no geometry, so nothing renders.
    this.root.add(refScene);

    refScene.traverse((obj) => {
      const name = obj.name || "";
      if (!name || obj === refScene) return;
      // Refs are empties (no mesh). Skip any stray mesh children.
      if (obj.isMesh) return;

      const position = new THREE.Vector3();
      obj.getWorldPosition(position);
      const extras = obj.userData ? { ...obj.userData } : {};
      const entry = { name, position, object3d: obj, extras };

      this.refs.byName.set(name, entry);
      this.refs.all.push(entry);

      if (name.startsWith("sectionRef_")) {
        const key = extras.section || name.slice("sectionRef_".length);
        this.refs.sections[key] = entry;
        // Surface the legacy positions the achievement/teleport code reads.
        if (key === "skills") this.signs.skillsPosition = position;
        else if (key === "contact") this.signs.contactPosition = position;
      }
    });
  }

  // ── Instanced systems ─────────────────────────────────────────────────────

  /**
   * Collect flower template geometry + colours + baked placements. Flowers are
   * NOT built as static meshes here — the Flowers class (App.boot, with the
   * shared Wind) instances them as swaying, player-parting clumps. One group per
   * zone template; `clumpHeight` (local bbox max-Y across its primitives) drives
   * the height-weighted bend. Each primitive keeps its GLB material colour.
   */
  async #collectFlowerGroups(entry) {
    const [visual, refs] = await Promise.all([
      this.loader.loadGLTF(GlbV3World.ASSET_BASE + entry.visual),
      this.loader.loadGLTF(GlbV3World.ASSET_BASE + entry.references),
    ]);
    visual.scene.updateMatrixWorld(true);
    const protoMeshesFor = (name) => {
      const node = visual.scene.getObjectByName(name);
      if (!node) return [];
      const meshes = [];
      node.traverse((o) => {
        if (o.isMesh) meshes.push(o);
      });
      return meshes;
    };

    refs.scene.updateMatrixWorld(true);
    const byTemplate = new Map();
    refs.scene.traverse((obj) => {
      if (obj.isMesh) return;
      const tmpl = obj.userData?.template;
      if (!tmpl) return;
      if (!byTemplate.has(tmpl)) byTemplate.set(tmpl, []);
      byTemplate.get(tmpl).push(obj);
    });

    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    const euler = new THREE.Euler();
    const groups = [];
    for (const [tmpl, placements] of byTemplate) {
      const protos = protoMeshesFor(tmpl);
      if (!protos.length) continue;
      let clumpHeight = 0.1;
      const primitives = protos.map((p) => {
        p.geometry.computeBoundingBox();
        clumpHeight = Math.max(clumpHeight, p.geometry.boundingBox.max.y);
        const color = p.material?.color
          ? p.material.color.clone()
          : new THREE.Color(0xffffff);
        return { geometry: p.geometry, color };
      });
      const placed = placements.map((o) => {
        o.matrixWorld.decompose(pos, quat, scl);
        return {
          x: pos.x,
          y: pos.y,
          z: pos.z,
          yaw: euler.setFromQuaternion(quat, "YXZ").y,
          scale: scl.x,
        };
      });
      groups.push({ key: tmpl, clumpHeight, primitives, placements: placed });
    }
    const total = groups.reduce((s, g) => s + g.placements.length, 0);
    console.log(
      `[GlbV3World] flowers: ${groups.length} groups, ${total} placements (Flowers builds these)`,
    );
    return groups;
  }

  /**
   * Load one `instanced` manifest entry into per-template InstancedMeshes.
   *
   * The split exporter writes a *visual* GLB (one mesh per template at identity,
   * named e.g. `brickPaveMesh`) and a *references* GLB (one empty per placement,
   * carrying a world-space transform + `userData.template` naming its mesh). We
   * group the empties by template, then build one InstancedMesh per template
   * reusing the visual mesh's geometry + baked material (the WebGPURenderer
   * auto-converts it to a node material, exactly like the monolithic GLBs).
   *
   * Returns a packed Float32Array of `[x,z,x,z,…]` world centres for the
   * path-forming bricks (pave + kerb) so the paths facade can flag stone
   * footstep/footprint zones. Stacked brick piles are split into individual
   * dynamic meshes + Rapier bodies, following Bruno's folio-2025 Bricks.js
   * pattern; flat paving stays instanced/static.
   */
  async #loadInstancedSystem(entry, physics = null) {
    const [visual, refs] = await Promise.all([
      this.loader.loadGLTF(GlbV3World.ASSET_BASE + entry.visual),
      this.loader.loadGLTF(GlbV3World.ASSET_BASE + entry.references),
    ]);

    // Prototype mesh(es) per template, keyed by the template node name. The
    // visual GLB holds each template at identity. Single-primitive templates
    // (bricks, rocks) load as one Mesh named after the template. MULTI-primitive
    // templates (flowers: 3 prims / 3 materials each) load as a GROUP named after
    // the template with one child Mesh per primitive — so a template yields
    // several proto meshes, each → its own InstancedMesh (own geometry+material).
    // The flowers visual also carries many redundant identity-stacked nodes that
    // all point at the same template mesh; getObjectByName returns the first, and
    // the authoritative placements come from the references GLB regardless.
    visual.scene.updateMatrixWorld(true);
    const protoMeshesFor = (name) => {
      const node = visual.scene.getObjectByName(name);
      if (!node) return [];
      const meshes = [];
      node.traverse((o) => {
        if (o.isMesh) meshes.push(o);
      });
      return meshes;
    };

    // Reference empties grouped by their target template.
    refs.scene.updateMatrixWorld(true);
    const byTemplate = new Map();
    refs.scene.traverse((obj) => {
      if (obj.isMesh) return;
      const tmpl = obj.userData?.template;
      if (!tmpl) return;
      if (!byTemplate.has(tmpl)) byTemplate.set(tmpl, []);
      byTemplate.get(tmpl).push(obj);
    });

    const PATH_TEMPLATES = new Set(["brickPaveMesh", "brickKerbMesh"]);
    const dynamicTemplates =
      entry.system === "bricks" ? DYNAMIC_BRICK_TEMPLATES : new Set();
    const pathXZ = [];
    let total = 0;

    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    const _c = new THREE.Vector3();
    const solidColliders =
      SOLID_INSTANCE_SYSTEMS.has(entry.system) && !!physics?.ready;
    let colliderCount = 0;

    for (const [tmpl, placements] of byTemplate) {
      const protos = protoMeshesFor(tmpl);
      if (!protos.length) {
        console.warn(
          `[GlbV3World] ${entry.system}: no visual template "${tmpl}" — skipped`,
        );
        continue;
      }
      total += placements.length;

      if (dynamicTemplates.has(tmpl)) {
        // Dynamic templates (brick piles) are single-primitive — use protos[0].
        const proto = protos[0];
        const transforms = this.#buildScaledBrickPileTransforms(
          proto,
          placements,
        );
        for (let i = 0; i < transforms.length; i++) {
          this.#createDynamicBrickPile(
            proto,
            transforms[i],
            physics,
            `${entry.system}_${tmpl}_${i}`,
          );
          if (PATH_TEMPLATES.has(tmpl))
            pathXZ.push(transforms[i].pos.x, transforms[i].pos.z);
        }
        continue;
      }

      const isPath = PATH_TEMPLATES.has(tmpl);

      // Solid systems (rocks): precompute the template's LOCAL vertices + index
      // once so each instance can register an EXACT triangle-mesh collider — the
      // player walks into every crevice with no convex bridging and no box
      // phantom walls beside the rock. Rocks are single-primitive (protos[0]).
      // Walk-through systems (flowers) skip this entirely.
      let localVerts = null;
      let solidIndices = null;
      if (solidColliders) {
        const geom = protos[0].geometry;
        const a = geom.attributes.position;
        localVerts = new Float32Array(a.count * 3);
        for (let v = 0; v < a.count; v++) {
          localVerts[v * 3] = a.getX(v);
          localVerts[v * 3 + 1] = a.getY(v);
          localVerts[v * 3 + 2] = a.getZ(v);
        }
        const idx = geom.index;
        solidIndices = idx
          ? idx.array instanceof Uint32Array
            ? idx.array
            : new Uint32Array(idx.array)
          : Uint32Array.from({ length: a.count }, (_, n) => n);
      }

      // Per-instance world matrices, shared across this template's primitives.
      const matrices = new Array(placements.length);
      for (let i = 0; i < placements.length; i++) {
        placements[i].matrixWorld.decompose(pos, quat, scl);
        matrices[i] = new THREE.Matrix4().compose(pos, quat, scl);
        if (isPath) pathXZ.push(pos.x, pos.z);
        if (solidColliders) {
          // Transform this instance's verts to world space → EXACT trimesh
          // collider (shares the template index). Hugs the real rock surface so
          // there is no invisible wall and the player can get right up to it.
          const verts = new Float32Array(localVerts.length);
          for (let j = 0; j < localVerts.length; j += 3) {
            _c.set(
              localVerts[j],
              localVerts[j + 1],
              localVerts[j + 2],
            ).applyMatrix4(matrices[i]);
            verts[j] = _c.x;
            verts[j + 1] = _c.y;
            verts[j + 2] = _c.z;
          }
          if (physics.addStaticTrimesh(verts, solidIndices)) colliderCount++;
        }
      }

      // One InstancedMesh per primitive (each its own geometry + material).
      for (let pi = 0; pi < protos.length; pi++) {
        const proto = protos[pi];
        const inst = new THREE.InstancedMesh(
          proto.geometry,
          proto.material,
          placements.length,
        );
        inst.name =
          protos.length > 1
            ? `${entry.system}_${tmpl}_${pi}`
            : `${entry.system}_${tmpl}`;
        inst.castShadow = true;
        inst.receiveShadow = true;
        for (let i = 0; i < placements.length; i++)
          inst.setMatrixAt(i, matrices[i]);
        inst.instanceMatrix.needsUpdate = true;
        this.root.add(inst);
      }
    }

    console.log(
      `[GlbV3World] ${entry.system}: ${total} instances across ${byTemplate.size} templates` +
        (solidColliders ? `, ${colliderCount} colliders` : ""),
    );
    return new Float32Array(pathXZ);
  }

  #buildScaledBrickPileTransforms(proto, placements) {
    proto.geometry.computeBoundingBox();
    const bbox = proto.geometry.boundingBox;
    const localSize = bbox.getSize(new THREE.Vector3());
    const raw = [];
    const groups = new Map();

    for (const placement of placements) {
      const pos = new THREE.Vector3();
      const quat = new THREE.Quaternion();
      const scl = new THREE.Vector3();
      placement.matrixWorld.decompose(pos, quat, scl);

      const key = (placement.name || "").replace(/_\d+$/u, "") || "brickPile";
      const halfY = Math.abs(localSize.y * scl.y) / 2;
      const bottomY = pos.y - halfY;
      const item = { pos, quat, scl, key, bottomY };
      raw.push(item);

      const group = groups.get(key) ?? {
        count: 0,
        x: 0,
        z: 0,
        baseY: Infinity,
      };
      group.count++;
      group.x += pos.x;
      group.z += pos.z;
      group.baseY = Math.min(group.baseY, bottomY);
      groups.set(key, group);
    }

    for (const group of groups.values()) {
      group.x /= group.count;
      group.z /= group.count;
    }

    return raw.map((item) => {
      const group = groups.get(item.key);
      const scaledPos = new THREE.Vector3(
        group.x + (item.pos.x - group.x) * DYNAMIC_BRICK_SCALE,
        group.baseY + (item.pos.y - group.baseY) * DYNAMIC_BRICK_SCALE,
        group.z + (item.pos.z - group.z) * DYNAMIC_BRICK_SCALE,
      );
      return {
        pos: scaledPos,
        quat: item.quat,
        scl: item.scl.multiplyScalar(DYNAMIC_BRICK_SCALE),
      };
    });
  }

  #createDynamicBrickPile(proto, transform, physics, name) {
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    pos.copy(transform.pos);
    quat.copy(transform.quat);
    scl.copy(transform.scl);

    const mesh = new THREE.Mesh(proto.geometry, proto.material);
    mesh.name = name;
    mesh.position.copy(pos);
    mesh.quaternion.copy(quat);
    mesh.scale.copy(scl);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.root.add(mesh);

    proto.geometry.computeBoundingBox();
    const bbox = proto.geometry.boundingBox;
    const localSize = bbox.getSize(new THREE.Vector3());
    const localCenter = bbox.getCenter(new THREE.Vector3());
    const halfExtents = new THREE.Vector3(
      Math.max(Math.abs(localSize.x * scl.x) / 2, 0.02),
      Math.max(Math.abs(localSize.y * scl.y) / 2, 0.02),
      Math.max(Math.abs(localSize.z * scl.z) / 2, 0.02),
    );
    const centerOffset = localCenter.clone().multiply(scl);
    const bodyCenter = centerOffset.clone().applyQuaternion(quat).add(pos);

    let body = null;
    if (physics?.ready) {
      body = physics.addDynamicCuboid(
        bodyCenter.x,
        bodyCenter.y,
        bodyCenter.z,
        halfExtents.x,
        halfExtents.y,
        halfExtents.z,
        { x: quat.x, y: quat.y, z: quat.z, w: quat.w },
        {
          mass: 0.1,
          friction: 0.7,
          restitution: 0.15,
          linearDamping: 0.1,
          angularDamping: 0.1,
          sleeping: true,
          contactThreshold: 15,
          onCollision: (force, position) => {
            this.audio?.playBrickHit?.(force, position);
          },
        },
      );
    }

    this.dynamicBrickPiles.push({
      mesh,
      body,
      centerOffset,
      startPosition: pos.clone(),
      startCenter: bodyCenter.clone(),
      startRotation: quat.clone(),
      _quat: new THREE.Quaternion(),
      _offset: new THREE.Vector3(),
    });
  }

  #resetDynamicBrick(brick) {
    this.#resetDynamicItem(brick);
  }

  #resetDynamicItem(item) {
    const { body, mesh } = item;
    if (body) {
      body.setTranslation(item.startCenter, false);
      body.setRotation(item.startRotation, false);
      body.setLinvel({ x: 0, y: 0, z: 0 }, false);
      body.setAngvel({ x: 0, y: 0, z: 0 }, false);
      body.resetForces?.(false);
      body.resetTorques?.(false);
      body.sleep();
    }
    if (item.kind === "titleLetter") {
      item.floating = true;
      item.floatTime = 0;
      item.groundedTime = 0;
      item.returning = false;
      item.returnTime = 0;
    }
    mesh.position.copy(item.startPosition);
    mesh.quaternion.copy(item.startRotation);
  }

  #extractDynamicTitleLetters(group, physics) {
    group.updateMatrixWorld(true);
    const letters = [];
    group.traverse((obj) => {
      if (obj.isMesh && /^titleLetter_\d+_/i.test(obj.name)) letters.push(obj);
    });

    const material = new THREE.MeshStandardMaterial({
      color: TITLE_LETTER_COLOR,
      roughness: 0.72,
      metalness: 0,
      emissive: TITLE_LETTER_EMISSIVE,
      emissiveIntensity: 0.1,
    });

    for (let i = 0; i < letters.length; i++) {
      const source = letters[i];
      const pos = new THREE.Vector3();
      const quat = new THREE.Quaternion();
      const scl = new THREE.Vector3();
      source.matrixWorld.decompose(pos, quat, scl);

      const mesh = new THREE.Mesh(source.geometry, material);
      mesh.name = `dynamic_${source.name}`;
      mesh.position.copy(pos);
      mesh.quaternion.copy(quat);
      mesh.scale.copy(scl);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.root.add(mesh);
      source.removeFromParent();

      source.geometry.computeBoundingBox();
      const bbox = source.geometry.boundingBox;
      const localSize = bbox.getSize(new THREE.Vector3());
      const localCenter = bbox.getCenter(new THREE.Vector3());
      const halfExtents = new THREE.Vector3(
        Math.max(Math.abs(localSize.x * scl.x) / 2, 0.02),
        Math.max(Math.abs(localSize.y * scl.y) / 2, 0.02),
        Math.max(Math.abs(localSize.z * scl.z) / 2, 0.02),
      );
      const centerOffset = localCenter.clone().multiply(scl);
      const bodyCenter = centerOffset.clone().applyQuaternion(quat).add(pos);
      const groundY = this.terrain.heightAt(bodyCenter.x, bodyCenter.z);
      const targetBottomY = groundY + TITLE_LETTER_FLOAT_CLEARANCE;
      const currentBottomY = bodyCenter.y - halfExtents.y;
      const liftY = Math.max(0, targetBottomY - currentBottomY);
      pos.y += liftY;
      bodyCenter.y += liftY;
      mesh.position.y = pos.y;

      let body = null;
      if (physics?.ready) {
        body = physics.addDynamicCuboid(
          bodyCenter.x,
          bodyCenter.y,
          bodyCenter.z,
          halfExtents.x,
          halfExtents.y,
          halfExtents.z,
          { x: quat.x, y: quat.y, z: quat.z, w: quat.w },
          {
            mass: 0.1,
            friction: 0.7,
            restitution: 0.15,
            linearDamping: 0.1,
            angularDamping: 0.1,
            sleeping: true,
            contactThreshold: 5,
            onCollision: (force, position) => {
              this.audio?.playBrickHit?.(force, position);
            },
          },
        );
      }

      this.dynamicTitleLetters.push({
        kind: "titleLetter",
        mesh,
        body,
        centerOffset,
        halfExtents,
        startPosition: pos.clone(),
        startCenter: bodyCenter.clone(),
        startRotation: quat.clone(),
        floating: true,
        floatTime: 0,
        floatPhase: i * 0.9,
        groundedTime: 0,
        returning: false,
        returnTime: 0,
        returnFromCenter: new THREE.Vector3(),
        returnFromRotation: new THREE.Quaternion(),
        _groundBox: new THREE.Box3(),
        _returnCenter: new THREE.Vector3(),
        _returnRotation: new THREE.Quaternion(),
        _quat: new THREE.Quaternion(),
        _offset: new THREE.Vector3(),
      });
    }

    if (letters.length) {
      console.log(`[GlbV3World] dynamic title letters: ${letters.length}`);
    }
  }

  // ── Tree trunk colliders (runtime — colliders.glb ships none for trees) ─────

  /**
   * Add one static cylinder collider per trunk/bark mesh in a tree group so the
   * player can't walk through trees. The baked colliders.glb only covers
   * structures/statue/props — every oak/birch/cherry trunk was left
   * non-collidable. Each tree is its own mesh, so we size a cylinder from the
   * trunk's BASE SLICE (bottom TRUNK_BASE_SLICE of its height): branch + leaf
   * spread higher up must not fatten the cylinder into an invisible wall. Uses
   * the same y-convention as #loadColliders (pass bbox-bottom; the helper lifts
   * the body by height/2 so it spans [ymin, ymax]).
   */
  _addTreeTrunkColliders(group, physics) {
    if (!physics?.ready) return;
    group.updateMatrixWorld(true);
    const v = new THREE.Vector3();
    let count = 0;
    group.traverse((o) => {
      if (!o.isMesh || !TRUNK_MATERIAL_RE.test(o.material?.name || "")) return;
      const posAttr = o.geometry?.attributes?.position;
      if (!posAttr) return;

      // Pass 1 — world-space vertical extent.
      let ymin = Infinity;
      let ymax = -Infinity;
      for (let i = 0; i < posAttr.count; i++) {
        v.fromBufferAttribute(posAttr, i).applyMatrix4(o.matrixWorld);
        if (v.y < ymin) ymin = v.y;
        if (v.y > ymax) ymax = v.y;
      }
      const height = Math.max(ymax - ymin, 0.1);

      // Pass 2 — XZ spread of the base slice only → trunk radius + centre.
      const sliceTop = ymin + height * TRUNK_BASE_SLICE;
      let minX = Infinity;
      let maxX = -Infinity;
      let minZ = Infinity;
      let maxZ = -Infinity;
      for (let i = 0; i < posAttr.count; i++) {
        v.fromBufferAttribute(posAttr, i).applyMatrix4(o.matrixWorld);
        if (v.y > sliceTop) continue;
        if (v.x < minX) minX = v.x;
        if (v.x > maxX) maxX = v.x;
        if (v.z < minZ) minZ = v.z;
        if (v.z > maxZ) maxZ = v.z;
      }
      if (minX === Infinity) return; // degenerate slice

      const cx = (minX + maxX) / 2;
      const cz = (minZ + maxZ) / 2;
      const radius = THREE.MathUtils.clamp(
        (Math.max(maxX - minX, maxZ - minZ) / 2) * TRUNK_RADIUS_SHRINK,
        TRUNK_RADIUS_MIN,
        TRUNK_RADIUS_MAX,
      );
      physics.addStaticCylinder(cx, ymin, cz, radius, height);
      count++;
    });
    if (count > 0)
      console.log(`[GlbV3World] ${group.name} trunk colliders: ${count}`);
  }

  // ── Fence colliders (runtime — fences.glb ships none) ───────────────────────

  /**
   * Build thin "knee-wall" colliders along each rope-and-post fence so the
   * player can't walk through it (fences.glb bakes no collider). Each fence is
   * one merged group holding a tall posts mesh + a slung rope mesh forming a
   * short run/L of evenly-spaced posts. We pick the posts mesh (the tall one),
   * cluster its verts into post centres, then drop one thin oriented box
   * between every pair of ADJACENT posts (≤ FENCE_MAX_SPAN). Larger gaps are
   * the intentional openings facing each section's entrance → no wall there.
   *
   * Box height = the fence's real world height (post base→top), so a jump can
   * clear it; the box is thin across the line and buried a touch into each post
   * so the run reads as one continuous barrier.
   */
  #addFenceColliders(group, physics) {
    if (!physics?.ready) return;
    group.updateMatrixWorld(true);
    const v = new THREE.Vector3();
    let walls = 0;

    group.traverse((mesh) => {
      if (!mesh.isMesh) return;
      const posAttr = mesh.geometry?.attributes?.position;
      if (!posAttr) return;

      // World-space vertical extent — the posts mesh is the tall one; the short
      // slung-rope mesh fails the height gate and is skipped (posts define the run).
      let ymin = Infinity;
      let ymax = -Infinity;
      for (let i = 0; i < posAttr.count; i++) {
        const y = v
          .fromBufferAttribute(posAttr, i)
          .applyMatrix4(mesh.matrixWorld).y;
        if (y < ymin) ymin = y;
        if (y > ymax) ymax = y;
      }
      if (ymax - ymin < FENCE_MIN_POST_HEIGHT) return;

      // Cluster verts into post centres by XZ proximity (running mean).
      const posts = [];
      for (let i = 0; i < posAttr.count; i++) {
        v.fromBufferAttribute(posAttr, i).applyMatrix4(mesh.matrixWorld);
        let hit = null;
        for (const p of posts) {
          const dx = p.x / p.n - v.x;
          const dz = p.z / p.n - v.z;
          if (dx * dx + dz * dz < FENCE_POST_CLUSTER_R2) {
            hit = p;
            break;
          }
        }
        if (hit) {
          hit.x += v.x;
          hit.z += v.z;
          hit.n++;
        } else posts.push({ x: v.x, z: v.z, n: 1 });
      }
      const centres = posts.map((p) => ({ x: p.x / p.n, z: p.z / p.n }));

      // One ridge-capped wall per adjacent post pair within span. The roof
      // ridge sits at the real fence top; its shoulder is RIDGE_RISE below, so
      // the cap is too steep to stand on but the wall below still blocks walking.
      const shoulderY = ymax - FENCE_RIDGE_RISE;
      for (let a = 0; a < centres.length; a++) {
        for (let b = a + 1; b < centres.length; b++) {
          const dx = centres[b].x - centres[a].x;
          const dz = centres[b].z - centres[a].z;
          const len = Math.hypot(dx, dz);
          if (len > FENCE_MAX_SPAN) continue;
          // Rapier yaw about +Y maps local +X → (cos, 0, -sin); align it with
          // the segment direction so the wall's length runs post-to-post.
          const yaw = Math.atan2(-dz, dx);
          physics.addStaticRidgeWall(
            (centres[a].x + centres[b].x) / 2,
            (centres[a].z + centres[b].z) / 2,
            ymin,
            shoulderY,
            ymax,
            len / 2 + FENCE_POST_HALF,
            FENCE_HALF_THICK,
            yaw,
          );
          walls++;
        }
      }
    });
    if (walls > 0)
      console.log(`[GlbV3World] ${group.name} fence walls: ${walls}`);
  }

  // ── Tree foliage from the green canopy (Phase E) ────────────────────────────

  /**
   * Strip a tree group's solid low-poly green canopy and turn it into SDF foliage
   * anchors "in the form of the green part" (user directive 2026-05-31).
   *
   * Each oak mesh ships an `oak_canopy_karan_*` canopy primitive (solid green,
   * base ~0.19,0.38,0.16) + an `oak_trunk_karan` trunk. The green canopy reads as
   * faceted low-poly and only exists to mark where leaves belong — so we sample
   * anchors across it (Poisson-thinned to CANOPY_ANCHOR_SPACING in world units),
   * DELETE the green primitive (the trunk stays), and App grows one SDF leaf blob
   * per anchor, reproducing the canopy's shape as fluff. Only oak hits this path
   * (birch/cherry have no green canopy → they keep the treeLeaves ref empties).
   */
  #extractTreeFoliage(group, species) {
    group.updateMatrixWorld(true);
    const canopyMeshes = [];
    group.traverse((o) => {
      if (o.isMesh && (o.material?.name || "").includes("canopy"))
        canopyMeshes.push(o);
    });

    const anchors = this.treeCanopyAnchors.get(species) ?? [];
    const spacing2 = CANOPY_ANCHOR_SPACING * CANOPY_ANCHOR_SPACING;
    const v = new THREE.Vector3();

    for (const mesh of canopyMeshes) {
      const posAttr = mesh.geometry?.attributes?.position;
      if (posAttr) {
        // Greedy Poisson thinning over the canopy's world-space verts: accept a
        // vertex only if it's ≥ spacing from every accepted one → even coverage.
        const accepted = [];
        for (let i = 0; i < posAttr.count; i++) {
          v.fromBufferAttribute(posAttr, i).applyMatrix4(mesh.matrixWorld);
          let ok = true;
          for (const a of accepted) {
            if (a.distanceToSquared(v) < spacing2) {
              ok = false;
              break;
            }
          }
          if (ok) accepted.push(v.clone());
        }
        if (accepted.length === 0 && posAttr.count > 0) {
          accepted.push(
            v
              .fromBufferAttribute(posAttr, 0)
              .applyMatrix4(mesh.matrixWorld)
              .clone(),
          );
        }
        for (const p of accepted) {
          // Deterministic ±jitter on blob size (hashed from rounded position) so
          // neighbouring blobs vary without breaking reload stability.
          const key =
            (Math.round(p.x * 13.1) ^
              Math.round(p.y * 3.3) ^
              Math.round(p.z * 7.7)) >>>
            0;
          const h = (Math.imul(key | 1, 2654435761) >>> 0) / 4294967296;
          const jitter = 1 + (h - 0.5) * 2 * CANOPY_SCALE_JITTER;
          anchors.push({
            position: p,
            scale: CANOPY_ANCHOR_SPACING * CANOPY_SCALE_FACTOR * jitter,
          });
        }
      }
      // Drop the solid green canopy — the trunk (bark_*) stays in the scene.
      mesh.removeFromParent();
      mesh.geometry?.dispose();
    }

    this.treeCanopyAnchors.set(species, anchors);
    console.log(
      `[GlbV3World] tree foliage ${species}: ${anchors.length} canopy anchors (solid green canopy removed)`,
    );
  }

  // ── Foliage references (Phase E) ────────────────────────────────────────────

  /**
   * Load the `foliage` manifest entries (treeLeaves / bushes) and return their
   * placement empties grouped by species, for the runtime Foliage SDF clouds.
   *
   * Each References GLB holds *empties only* (no geometry) carrying a baked
   * world TRS + `extras.species` (birch/cherry for treeLeaves; bushes have one
   * implicit group). We read each empty's world position + uniform scale and
   * bucket by species so App can build one Foliage cloud per (system, species)
   * with the right palette. Trunks + bush colliders already exist — nothing is
   * added to physics here.
   *
   * @returns {Promise<Array<{system:string, groups:Map<string, Array<{position:THREE.Vector3, scale:number}>>}>>}
   */
  async loadFoliageGroups() {
    const out = [];
    const entries = this.manifest?.foliage ?? [];
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();

    for (const entry of entries) {
      if (!entry.references) continue;
      // treeLeaves refs (birch + cherry — oak isn't in them) AND bushes load here.
      // Oak's leaves come from its green canopy geometry instead (#extractTreeFoliage).
      let gltf;
      try {
        gltf = await this.loader.loadGLTF(
          GlbV3World.ASSET_BASE + entry.references,
        );
      } catch (err) {
        console.warn(
          `[GlbV3World] foliage "${entry.system}" load failed:`,
          err?.message || err,
        );
        continue;
      }
      gltf.scene.updateMatrixWorld(true);

      const groups = new Map();
      let count = 0;
      gltf.scene.traverse((obj) => {
        if (obj.isMesh || obj === gltf.scene || !obj.name) return;
        obj.matrixWorld.decompose(pos, quat, scl);
        const species = obj.userData?.species ?? entry.system;
        if (!groups.has(species)) groups.set(species, []);
        groups.get(species).push({ position: pos.clone(), scale: scl.x });
        count++;
      });

      out.push({ system: entry.system, groups });
      console.log(
        `[GlbV3World] foliage ${entry.system}: ${count} refs across`,
        [...groups.keys()],
      );
    }

    // Oak (and any tree with a baked solid green canopy): leaves grown "in the
    // form of the green part" — anchors sampled from the canopy geometry by
    // #extractTreeFoliage, which also deleted the green mesh. Emit them through
    // the SAME group shape so App's foliage loop builds an oak SDF cloud with no
    // special-casing. (treeLeaves refs above cover birch/cherry; oak isn't there.)
    if (this.treeCanopyAnchors.size > 0) {
      out.push({ system: "treeCanopy", groups: this.treeCanopyAnchors });
      for (const [species, anchors] of this.treeCanopyAnchors) {
        console.log(
          `[GlbV3World] foliage treeCanopy: ${anchors.length} ${species} canopy anchors`,
        );
      }
    }
    return out;
  }

  // ── Boot invariants ───────────────────────────────────────────────────────

  #assertBootInvariants() {
    const required = {
      "terrain mesh + heightfield":
        !!this.terrain.mesh && !!this.terrain.heights,
      sectionRef_projects: !!this.refs.sections.projects,
      sectionRef_skills: !!this.refs.sections.skills,
      sectionRef_contact: !!this.refs.sections.contact,
    };
    const failures = Object.entries(required)
      .filter(([, ok]) => !ok)
      .map(([k]) => k);
    if (failures.length > 0) {
      throw new Error(
        `GlbV3World boot assertions failed:\n  - ${failures.join("\n  - ")}`,
      );
    }
    console.log("[GlbV3World] load: OK", {
      heightfieldSize: this.terrain.size.toFixed(2),
      segments: this.terrain.segments,
      sections: Object.keys(this.refs.sections),
      markers: Object.keys(this.refs.markers),
      refs: this.refs.all.length,
    });
  }
}
