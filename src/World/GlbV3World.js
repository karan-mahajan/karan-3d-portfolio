import * as THREE from 'three/webgpu';

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

    // paths facade — v3 has no path ribbons (decorative-paths sub-project is
    // deferred). Empty positions keep footstep-surface + grass-flatten happy.
    this.paths = {
      getTilePositions: () => new Float32Array(0),
      getTileCount: () => 0,
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
        this.#neutralizeTerrainMask();
      }
      if (entry.markers) {
        for (const markerName of entry.markers) {
          const obj = group.getObjectByName(markerName)
            ?? group.getObjectByName(`root_${markerName}`);
          if (obj) this.refs.markers[markerName] = obj;
        }
      }
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
   * The terrain's GLB material carries a red/black placement-MASK texture
   * (`terrainFurnitures`) as its baseColorTexture, which renders the ground as
   * a red mask. The real terrain colour comes from the Bruno grass-mask shader
   * in Phase D. Until then, strip the mask and apply a neutral ground colour so
   * the milestone reads as "unstyled ground", not "broken". Removed when the
   * Phase D terrain/grass shader installs the proper material.
   */
  #neutralizeTerrainMask() {
    const mesh = this.terrain.mesh;
    if (!mesh) return;
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const mat of mats) {
      if (!mat) continue;
      if (mat.map) { mat.map = null; }
      if (mat.color) mat.color.set('#6f7d52'); // muted grass-dirt placeholder
      if ('metalness' in mat) mat.metalness = 0;
      if ('roughness' in mat) mat.roughness = 1;
      mat.needsUpdate = true;
    }
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
