import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import { Fn, positionWorld, texture, uv, vec2, vec3, mix, color, uniform, clamp } from 'three/tsl';

// Tree GLB systems that ship a solid low-poly GREEN canopy primitive (material
// `*_canopy_*`) alongside their trunk → foliage species key. ONLY oak does:
// verified from the GLBs, oakTrees has `oak_canopy_karan_*` (green) + `oak_trunk_
// karan` per `oakBody`; birch/cherry are trunk/branch-only and get their leaves
// from the treeLeaves ref empties instead. The canopy is just the placement
// GUIDE — we sample anchors across it (in its form), delete the green primitive,
// and grow SDF leaf blobs there, leaving the trunk. See #extractTreeFoliage.
const TREE_SYSTEMS = { oakTrees: 'oak' };
// Canopy → foliage-anchor sampling. Poisson-thin the canopy verts to this world
// spacing; each surviving point grows one SDF blob scaled to fill the gap.
const CANOPY_ANCHOR_SPACING = 1.25;   // m between blobs
const CANOPY_SCALE_FACTOR = 0.62;     // blob scale = spacing × this (× jitter)
const CANOPY_SCALE_JITTER = 0.2;      // ±fraction deterministic size variation
// Tree trunks need runtime Rapier colliders — the baked colliders.glb ships
// NONE for trees, so the player walks straight through them. Each tree is a
// separate mesh (oak_trunk_karan / birch_*_bark_karan / cherry_trunk_dark_brown),
// so we size one static cylinder per trunk mesh from its base slice (branch/leaf
// spread higher up must NOT fatten the cylinder).
const TREE_TRUNK_SYSTEMS = new Set(['oakTrees', 'birchTrees', 'cherryTrees']);
const TRUNK_MATERIAL_RE = /trunk|bark/i;   // trunk/bark mesh → gets a collider
const TRUNK_BASE_SLICE = 0.25;             // sample the bottom 25% for the radius
const TRUNK_RADIUS_MIN = 0.16;
const TRUNK_RADIUS_MAX = 0.7;
const TRUNK_RADIUS_SHRINK = 0.85;          // visible bark sits a touch inside bbox
const DYNAMIC_BRICK_SCALE = 0.5;
const DYNAMIC_BRICK_TEMPLATES = new Set(['brickKerbMesh', 'brickPileMesh']);

// Rope-and-post fences (fences.glb) ship no colliders. We rebuild thin wall
// segments at runtime by clustering the posts mesh into post centres and
// linking ADJACENT posts. Real spans run 3.1–4.5 m (projects is the widest);
// the next-closest non-adjacent pair is 6.8 m (a run's end-posts, already
// bridged by the middle post) — so FENCE_MAX_SPAN sits between the two.
const FENCE_MIN_POST_HEIGHT = 0.8;     // posts ~1.21 m tall; skips the ~0.46 m rope mesh
const FENCE_POST_CLUSTER_R2 = 0.35 * 0.35;  // XZ radius² grouping verts into one post
const FENCE_MAX_SPAN = 5.5;            // link posts ≤ this apart; bigger = opening/non-adjacent
const FENCE_POST_HALF = 0.15;          // extend each wall end to bury into its posts
const FENCE_HALF_THICK = 0.12;         // wall ~0.24 m thick — hugs the post line
const FENCE_RIDGE_RISE = 0.22;         // pitched-roof cap height; > ~1.2× halfThick so
                                       // the roof beats the 50° climb angle → not standable
// `*Footprint_*` collider proxies are full-height ZONE volumes (section/structure
// /misc areas), NOT visible props — baking them as boxes walls off the statue,
// sections, pool and small props so the player can't approach. They're skipped at
// load; the real meshes inside carry their own tight `cuboid_`/`tube_` proxies.
// The exception: solid BUILDINGS whose footprint IS the visible wall — kept (as a
// tight oriented box) so the player can't walk through them.
const SOLID_FOOTPRINT_RE = /Footprint_(cabin|outhouse)/i;
const TITLE_LETTER_COLOR = '#24345a';
const TITLE_LETTER_EMISSIVE = '#080d18';
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
 * Instanced systems (rocks/bricks/flowers) and foliage (bushes/treeLeaves) are
 * deferred to Phase E — this loader is monolithic-geometry + collision only.
 *
 * Exposes the same facade surface App.js + downstream read off the old GlbWorld
 * (terrain / nature / paths / billboards / signs / refs) so the rest of the app
 * boots unchanged; sections + interactions are rebuilt in Phase C.
 */
export class GlbV3World {
  static MANIFEST_PATH = '/world/manifest.json';
  static ASSET_BASE = '/world/';

  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;

    this.root = new THREE.Group();
    this.root.name = 'glb-v3-world';
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
    this.groundGrassColor = uniform(color('#ffffff'));
    this.dynamicBrickPiles = [];
    this.dynamicTitleLetters = [];
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
      byName: new Map(),       // name → { name, position, object3d, extras }
      sections: {},            // section key → entry (from sectionRef_*)
      markers: {},             // marker name → Object3D (areas section roots)
      all: [],                 // every ref entry, in load order
    };
  }

  /** Load + parse the world per the manifest, populate buckets, run assertions. */
  async load(physics, opts = {}) {
    this.audio = opts.audio ?? null;
    const manifest = await fetch(GlbV3World.MANIFEST_PATH).then((r) => {
      if (!r.ok) throw new Error(`GlbV3World: manifest fetch failed (${r.status})`);
      return r.json();
    });
    this.manifest = manifest;

    if (manifest.grassGrid?.bounds) this.grassGrid.bounds = manifest.grassGrid.bounds;

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
            console.warn('[GlbV3World] grass mask load failed:', err?.message || err);
          })
      : Promise.resolve();

    // 0b. Tile/slab art for the painted paths. Sampled by world XZ in the
    // terrain ground material; tolerate failure (paths fall back to flat stone).
    const tileFile = manifest.tileTexture ?? 'tiles.png';
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
        console.warn('[GlbV3World] tile texture load failed:', err?.message || err);
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
            console.warn(`[GlbV3World] failed to load ${entry.file}:`, err?.message || err);
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
          const obj = group.getObjectByName(markerName)
            ?? group.getObjectByName(`root_${markerName}`);
          if (obj) this.refs.markers[markerName] = obj;
        }
      }
      // Trees: strip the solid green canopy → SDF foliage anchors in its form.
      const treeSpecies = TREE_SYSTEMS[entry.system];
      if (treeSpecies) this.#extractTreeFoliage(group, treeSpecies);
      // Trees: give every trunk a static collider (colliders.glb has none).
      if (TREE_TRUNK_SYSTEMS.has(entry.system)) this._addTreeTrunkColliders(group, physics);
      if (entry.system === 'fences') this.#addFenceColliders(group, physics);
      if (entry.system === 'miscFx') this.#extractDynamicTitleLetters(group, physics);
    }

    if (physics?.ready) this.#registerBridgeColliders(physics);

    // 1b. Instanced bricks — the authored stone paving (pave/kerb/pile). Other
    // instanced systems (rocks/flowers) stay deferred; only bricks are wired so
    // the walkable path reads as paving + footsteps register stone zones.
    const bricksEntry = (manifest.instanced ?? []).find((e) => e.system === 'bricks');
    if (bricksEntry) {
      this._pathTilePositions = await this.#loadInstancedSystem(bricksEntry, physics);
    }

    // 2. Colliders — parse the proxy GLB, build Rapier shapes, discard meshes.
    if (manifest.colliders?.file && physics) {
      await this.#loadColliders(GlbV3World.ASSET_BASE + manifest.colliders.file, physics);
    }

    // 3. References — typed empties map (kept live under root for pivots).
    if (manifest.references?.file) {
      await this.#loadReferences(GlbV3World.ASSET_BASE + manifest.references.file);
    }

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
    const touchedLetter = playerPos ? this.#closestTouchedFloatingTitleLetter(playerPos) : null;
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
      const bobY = Math.sin(letter.floatTime * TITLE_LETTER_FLOAT_SPEED + letter.floatPhase)
        * TITLE_LETTER_FLOAT_AMPLITUDE;
      body.setTranslation({
        x: letter.startCenter.x,
        y: letter.startCenter.y + bobY,
        z: letter.startCenter.z,
      }, false);
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
    const radius = Math.hypot(letter.halfExtents.x, letter.halfExtents.z) + TITLE_LETTER_TOUCH_PADDING;
    if ((dx * dx + dz * dz) > radius * radius) return false;

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
    letter.body.applyImpulse({
      x: pushX * TITLE_LETTER_DROP_IMPULSE,
      y: 0.035,
      z: pushZ * TITLE_LETTER_DROP_IMPULSE,
    }, true);
    letter.body.applyTorqueImpulse?.({
      x: pushZ * 0.025,
      y: 0.018,
      z: -pushX * 0.025,
    }, true);
  }

  #isDroppedTitleLetterOnGround(letter) {
    const t = letter.body.translation();
    const groundY = this.terrain.heightAt(t.x, t.z);
    letter.mesh.updateMatrixWorld(true);
    letter._groundBox.setFromObject(letter.mesh);
    const bottomY = letter._groundBox.min.y;
    return bottomY <= groundY + 0.08 || (letter.body.isSleeping() && bottomY <= groundY + 0.18);
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
    const ease = t < 0.5
      ? 4 * t * t * t
      : 1 - ((-2 * t + 2) ** 3) / 2;
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
      if (obj.isMesh && (obj.name === 'terrain' || obj.name.startsWith('terrain'))) {
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
    if (!mesh) throw new Error('GlbV3World: terrain mesh missing from terrain.glb');

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
        Math.round(((vec.x - bboxMin.x) / sizeX) * segments), 0, segments);
      const w = THREE.MathUtils.clamp(
        Math.round(((vec.z - bboxMin.z) / sizeZ) * segments), 0, segments);
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
      return (1 - tu) * (1 - tw) * h00
           + tu       * (1 - tw) * h10
           + (1 - tu) * tw       * h01
           + tu       * tw       * h11;
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
    const olive = vec3(0.5, 0.54, 0.05);     // RGB.001 — bare/partial grass
    const midGreen = vec3(0.31, 0.39, 0.16); // RGB
    const darkGreen = vec3(0.07, 0.14, 0.06); // RGB.004 — densest grass
    const stone = color('#b3a489'); // warm fallback if the tile art fails to load
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
        const guv = vec2(positionWorld.x, positionWorld.z.negate()).mul(invSpan).add(0.5);
        // Blender's Mix nodes have clamp_factor=True; clamp G to match. G is fed
        // straight into both mix factors (no scaling) exactly as the .blend does.
        const g = clamp(texture(this.grassMask, guv).g, 0, 1);
        if (globalThis.__grassMaskDebug) return vec3(g, g, g);
        const grassGround = mix(mix(olive, midGreen, g), darkGreen, g)
          .mul(this.groundGrassColor);
        if (!furnMask) return grassGround;
        // terrainFurnitures.R (mesh UVs): 1 at path centre → 0 at edge.
        const pathR = clamp(texture(furnMask, uv()).r, 0, 1);
        // Paint the real tile art over the path, sampled by world XZ (Blender
        // parity). Fall back to the flat warm stone if the PNG didn't load.
        const paving = this.tileTexture
          ? texture(this.tileTexture, vec2(positionWorld.x, positionWorld.z.negate()).mul(TILE_SCALE)).rgb
          : stone;
        return mix(grassGround, paving, pathR);
      })();
    } else {
      mat.colorNode = olive;
    }
    mesh.material = mat;
    mesh.receiveShadow = true;
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

    let cyl = 0, box = 0, skipped = 0;
    const _pos = new THREE.Vector3();
    const _quat = new THREE.Quaternion();
    const _scl = new THREE.Vector3();
    const _euler = new THREE.Euler();

    for (const obj of meshes) {
      const name = obj.name || '';

      if (name.startsWith('tube_')) {
        // Upright cylinder — its world-AABB radius is yaw-invariant, so the box
        // measurement already hugs the trunk/post. Keep as-is.
        const wbox = new THREE.Box3().setFromObject(obj);
        const size = wbox.getSize(new THREE.Vector3());
        const center = wbox.getCenter(new THREE.Vector3());
        const radius = Math.max(size.x, size.z) / 2;
        const height = Math.max(size.y, 0.05);
        // addStaticCylinder lifts the body by height/2 internally; pass
        // center.y - height/2 so the cylinder centres on the bbox centre.
        physics.addStaticCylinder(center.x, center.y - height / 2, center.z, radius, height);
        cyl++;
        continue;
      }

      // `*Footprint_*` zone volumes → skip (see SOLID_FOOTPRINT_RE). Only solid
      // buildings keep a footprint collider; everything else is freed so the
      // player can walk right up to the real prop's own collider.
      if (name.includes('Footprint_') && !SOLID_FOOTPRINT_RE.test(name)) {
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
      const yaw = _euler.setFromQuaternion(_quat, 'YXZ').y;
      physics.addStaticCuboid(
        worldCenter.x, worldCenter.y, worldCenter.z,
        Math.max(Math.abs(localSize.x * _scl.x) / 2, 0.02),
        Math.max(Math.abs(localSize.y * _scl.y) / 2, 0.02),
        Math.max(Math.abs(localSize.z * _scl.z) / 2, 0.02),
        yaw,
      );
      box++;
    }

    // Proxy meshes are never added to the scene — physics owns them now.
    console.log(`[GlbV3World] colliders: ${cyl} cylinders, ${box} oriented boxes, ${skipped} footprint zones skipped`);
  }

  #registerBridgeColliders(physics) {
    const bridgeMeshes = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh) return;
      if (!this.#isBridgeColliderMesh(obj.name || '')) return;
      bridgeMeshes.push(obj);
    });

    let count = 0;
    for (const mesh of bridgeMeshes) {
      if (this.#addBridgeDeckCollider(physics, mesh)) count++;
    }
    if (count > 0) console.log(`[GlbV3World] bridge colliders: ${count} deck slabs`);
  }

  #isBridgeColliderMesh(name) {
    return name === 'bridge01'
      || name.startsWith('bridge02_deck_slats');
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

    const thickness = mesh.name === 'bridge01' ? 0.24 : 0.18;
    const deckTop = this.#meshWorldYPercentile(mesh, mesh.name === 'bridge01' ? 0.75 : 0.9);
    const yaw = new THREE.Euler().setFromQuaternion(quat, 'YXZ').y;

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
    const index = Math.min(ys.length - 1, Math.max(0, Math.floor((ys.length - 1) * percentile)));
    return ys[index];
  }

  // ── References ────────────────────────────────────────────────────────────

  async #loadReferences(url) {
    const gltf = await this.loader.loadGLTF(url);
    const refScene = gltf.scene;
    refScene.name = 'references';
    refScene.updateMatrixWorld(true);
    // Keep the empties live under root so Phase F can animate pivots by name.
    // Empties carry no geometry, so nothing renders.
    this.root.add(refScene);

    refScene.traverse((obj) => {
      const name = obj.name || '';
      if (!name || obj === refScene) return;
      // Refs are empties (no mesh). Skip any stray mesh children.
      if (obj.isMesh) return;

      const position = new THREE.Vector3();
      obj.getWorldPosition(position);
      const extras = obj.userData ? { ...obj.userData } : {};
      const entry = { name, position, object3d: obj, extras };

      this.refs.byName.set(name, entry);
      this.refs.all.push(entry);

      if (name.startsWith('sectionRef_')) {
        const key = extras.section || name.slice('sectionRef_'.length);
        this.refs.sections[key] = entry;
        // Surface the legacy positions the achievement/teleport code reads.
        if (key === 'skills') this.signs.skillsPosition = position;
        else if (key === 'contact') this.signs.contactPosition = position;
      }
    });
  }

  // ── Instanced systems ─────────────────────────────────────────────────────

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

    // Template meshes by name (brickPaveMesh / brickKerbMesh / brickPileMesh).
    const templates = new Map();
    visual.scene.traverse((obj) => {
      if (obj.isMesh) templates.set(obj.name, obj);
    });

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

    const PATH_TEMPLATES = new Set(['brickPaveMesh', 'brickKerbMesh']);
    const dynamicTemplates = entry.system === 'bricks' ? DYNAMIC_BRICK_TEMPLATES : new Set();
    const pathXZ = [];
    let total = 0;

    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    const m = new THREE.Matrix4();

    for (const [tmpl, placements] of byTemplate) {
      const proto = templates.get(tmpl);
      if (!proto) {
        console.warn(`[GlbV3World] ${entry.system}: no visual template "${tmpl}" — skipped`);
        continue;
      }
      if (dynamicTemplates.has(tmpl)) {
        const transforms = this.#buildScaledBrickPileTransforms(proto, placements);
        for (let i = 0; i < transforms.length; i++) {
          this.#createDynamicBrickPile(proto, transforms[i], physics, `${entry.system}_${tmpl}_${i}`);
          if (PATH_TEMPLATES.has(tmpl)) pathXZ.push(transforms[i].pos.x, transforms[i].pos.z);
        }
        total += placements.length;
        continue;
      }
      const inst = new THREE.InstancedMesh(proto.geometry, proto.material, placements.length);
      inst.name = `${entry.system}_${tmpl}`;
      inst.castShadow = true;
      inst.receiveShadow = true;
      const isPath = PATH_TEMPLATES.has(tmpl);
      for (let i = 0; i < placements.length; i++) {
        placements[i].matrixWorld.decompose(pos, quat, scl);
        m.compose(pos, quat, scl);
        inst.setMatrixAt(i, m);
        if (isPath) pathXZ.push(pos.x, pos.z);
      }
      inst.instanceMatrix.needsUpdate = true;
      this.root.add(inst);
      total += placements.length;
    }

    console.log(`[GlbV3World] ${entry.system}: ${total} instances across ${byTemplate.size} templates`);
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

      const key = (placement.name || '').replace(/_\d+$/u, '') || 'brickPile';
      const halfY = Math.abs(localSize.y * scl.y) / 2;
      const bottomY = pos.y - halfY;
      const item = { pos, quat, scl, key, bottomY };
      raw.push(item);

      const group = groups.get(key) ?? { count: 0, x: 0, z: 0, baseY: Infinity };
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
    if (item.kind === 'titleLetter') {
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
        kind: 'titleLetter',
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
      if (!o.isMesh || !TRUNK_MATERIAL_RE.test(o.material?.name || '')) return;
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
      let minX = Infinity; let maxX = -Infinity;
      let minZ = Infinity; let maxZ = -Infinity;
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
        TRUNK_RADIUS_MIN, TRUNK_RADIUS_MAX,
      );
      physics.addStaticCylinder(cx, ymin, cz, radius, height);
      count++;
    });
    if (count > 0) console.log(`[GlbV3World] ${group.name} trunk colliders: ${count}`);
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
        const y = v.fromBufferAttribute(posAttr, i).applyMatrix4(mesh.matrixWorld).y;
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
          if (dx * dx + dz * dz < FENCE_POST_CLUSTER_R2) { hit = p; break; }
        }
        if (hit) { hit.x += v.x; hit.z += v.z; hit.n++; }
        else posts.push({ x: v.x, z: v.z, n: 1 });
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
            (centres[a].x + centres[b].x) / 2, (centres[a].z + centres[b].z) / 2,
            ymin, shoulderY, ymax,
            len / 2 + FENCE_POST_HALF, FENCE_HALF_THICK,
            yaw,
          );
          walls++;
        }
      }
    });
    if (walls > 0) console.log(`[GlbV3World] ${group.name} fence walls: ${walls}`);
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
      if (o.isMesh && (o.material?.name || '').includes('canopy')) canopyMeshes.push(o);
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
            if (a.distanceToSquared(v) < spacing2) { ok = false; break; }
          }
          if (ok) accepted.push(v.clone());
        }
        if (accepted.length === 0 && posAttr.count > 0) {
          accepted.push(v.fromBufferAttribute(posAttr, 0).applyMatrix4(mesh.matrixWorld).clone());
        }
        for (const p of accepted) {
          // Deterministic ±jitter on blob size (hashed from rounded position) so
          // neighbouring blobs vary without breaking reload stability.
          const key = (Math.round(p.x * 13.1) ^ Math.round(p.y * 3.3) ^ Math.round(p.z * 7.7)) >>> 0;
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
    console.log(`[GlbV3World] tree foliage ${species}: ${anchors.length} canopy anchors (solid green canopy removed)`);
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
        gltf = await this.loader.loadGLTF(GlbV3World.ASSET_BASE + entry.references);
      } catch (err) {
        console.warn(`[GlbV3World] foliage "${entry.system}" load failed:`, err?.message || err);
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
      console.log(`[GlbV3World] foliage ${entry.system}: ${count} refs across`,
        [...groups.keys()]);
    }

    // Oak (and any tree with a baked solid green canopy): leaves grown "in the
    // form of the green part" — anchors sampled from the canopy geometry by
    // #extractTreeFoliage, which also deleted the green mesh. Emit them through
    // the SAME group shape so App's foliage loop builds an oak SDF cloud with no
    // special-casing. (treeLeaves refs above cover birch/cherry; oak isn't there.)
    if (this.treeCanopyAnchors.size > 0) {
      out.push({ system: 'treeCanopy', groups: this.treeCanopyAnchors });
      for (const [species, anchors] of this.treeCanopyAnchors) {
        console.log(`[GlbV3World] foliage treeCanopy: ${anchors.length} ${species} canopy anchors`);
      }
    }
    return out;
  }

  // ── Boot invariants ───────────────────────────────────────────────────────

  #assertBootInvariants() {
    const required = {
      'terrain mesh + heightfield': !!this.terrain.mesh && !!this.terrain.heights,
      'sectionRef_projects': !!this.refs.sections.projects,
      'sectionRef_skills': !!this.refs.sections.skills,
      'sectionRef_contact': !!this.refs.sections.contact,
    };
    const failures = Object.entries(required).filter(([, ok]) => !ok).map(([k]) => k);
    if (failures.length > 0) {
      throw new Error(`GlbV3World boot assertions failed:\n  - ${failures.join('\n  - ')}`);
    }
    console.log('[GlbV3World] load: OK', {
      heightfieldSize: this.terrain.size.toFixed(2),
      segments: this.terrain.segments,
      sections: Object.keys(this.refs.sections),
      markers: Object.keys(this.refs.markers),
      refs: this.refs.all.length,
    });
  }
}
