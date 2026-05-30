import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import { Fn, positionWorld, texture, uv, vec2, vec3, mix, color, uniform, clamp } from 'three/tsl';

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
    // Uniform exposed so day/night can tint the ground grass colour alongside
    // the blades (TimeOfDay drives it through Grass.syncColor in Phase D).
    this.groundGrassColor = uniform(color('#5f7a39'));

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
  async load(physics) {
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
    }

    // 1b. Instanced bricks — the authored stone paving (pave/kerb/pile). Other
    // instanced systems (rocks/flowers) stay deferred; only bricks are wired so
    // the walkable path reads as paving + footsteps register stone zones.
    const bricksEntry = (manifest.instanced ?? []).find((e) => e.system === 'bricks');
    if (bricksEntry) {
      this._pathTilePositions = await this.#loadInstancedSystem(bricksEntry);
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
   * a colour. We replace the whole material with a Bruno-style node material
   * that derives the ground colour from the grass mask: the G channel (grass
   * density) blends a dirt base toward grass green, sampled by world XZ over the
   * ±96 grass grid (`uv = worldXZ / (2*bounds) + 0.5`, matching the Blender GN
   * + the runtime Grass field so blades and ground line up exactly).
   *
   * MeshLambertNodeMaterial keeps the sun/shadow/fog response, so the ground
   * dims at night through the same light rig as everything else. Where the
   * grass mask is 0 (water basins, paths) the ground stays dirt; the exported
   * GLB's `terrainFurnitures` mask (the original baseColorTexture, R channel =
   * path/slab overlay, sampled by the mesh's own UVs) then paints the painted
   * tile texture (`tiles.png`, sampled by world XZ × 0.2 to match the Blender
   * terrain material's slabs node) over the path zones so they read as real
   * paving, not bare dirt. Falls back to a flat warm stone colour if the tile
   * texture failed to load, and to flat dirt if the grass mask failed to load.
   */
  #applyTerrainGroundMaterial() {
    const mesh = this.terrain.mesh;
    if (!mesh) return;

    const dirt = color('#8f7d54');
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
        const guv = vec2(positionWorld.x, positionWorld.z).mul(invSpan).add(0.5);
        const g = texture(this.grassMask, guv).g;
        if (globalThis.__grassMaskDebug) return vec3(g, g, g);
        // Mask G tops out ~0.5 on full grass; lift so grassy land reads clearly
        // green while paths/basins (G≈0) stay dirt.
        const blend = clamp(g.mul(1.8), 0, 1);
        const ground = mix(dirt, this.groundGrassColor, blend);
        if (!furnMask) return ground;
        // terrainFurnitures.R (mesh UVs): 1 at path centre → 0 at edge.
        const pathR = clamp(texture(furnMask, uv()).r, 0, 1);
        // Paint the real tile art over the path, sampled by world XZ (Blender
        // parity). Fall back to the flat warm stone if the PNG didn't load.
        const paving = this.tileTexture
          ? texture(this.tileTexture, vec2(positionWorld.x, positionWorld.z.negate()).mul(TILE_SCALE)).rgb
          : stone;
        return mix(ground, paving, pathR);
      })();
    } else {
      mat.colorNode = dirt;
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

    let cyl = 0, box = 0, pad = 0;
    for (const obj of meshes) {
      const name = obj.name || '';
      const wbox = new THREE.Box3().setFromObject(obj);
      const size = wbox.getSize(new THREE.Vector3());
      const center = wbox.getCenter(new THREE.Vector3());

      if (name.startsWith('tube_')) {
        const radius = Math.max(size.x, size.z) / 2;
        const height = Math.max(size.y, 0.05);
        // addStaticCylinder lifts the body by height/2 internally; pass
        // center.y - height/2 so the cylinder centres on the bbox centre.
        physics.addStaticCylinder(center.x, center.y - height / 2, center.z, radius, height);
        cyl++;
      } else {
        // cuboid_* (props/statue) and *Footprint_* (flat walkable pads) — both
        // map to an axis-aligned box from the world bbox. Footprints are thin
        // slabs the player can stand on; props are full-height blockers.
        physics.addStaticCuboid(
          center.x, center.y, center.z,
          Math.max(size.x / 2, 0.02),
          Math.max(size.y / 2, 0.02),
          Math.max(size.z / 2, 0.02),
        );
        if (name.endsWith('Footprint_') || name.includes('Footprint_')) pad++;
        else box++;
      }
    }

    // Proxy meshes are never added to the scene — physics owns them now.
    console.log(`[GlbV3World] colliders: ${cyl} cylinders, ${box} boxes, ${pad} pads`);
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
   * path-forming bricks (pave + kerb; piles are decorative) so the paths facade
   * can flag stone footstep/footprint zones. No colliders are added — the bricks
   * are flat paving on the terrain heightfield (colliders.glb is authoritative).
   */
  async #loadInstancedSystem(entry) {
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
