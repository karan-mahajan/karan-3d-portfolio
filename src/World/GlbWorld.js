import * as THREE from 'three/webgpu';
import { SmoothLitPaletteMaterial } from '../Materials/SmoothLitPaletteMaterial.js';

/**
 * Single source of truth for the world geometry. Loads static/world/world.glb,
 * walks the scene graph once, and dispatches meshes into 5 buckets:
 *
 *   1. Terrain submesh   → baked 193×193 heightfield + Physics ground
 *   2. Named colliders   → cuboid_* / tube_* / trimesh_* → Rapier statics
 *   3. Ref empties       → typed refs map (sections, lights, particles, …)
 *   4. Material tokens   → *water* / *waterfall* / *ocean* / *mountain* /
 *                          *beam* / *glass* → special shaders (Phase 5 swaps;
 *                          Phase 1 leaves the default palette material)
 *   5. Push-spots        → pine_*, birch_*, hero_tree_*, cairn_*, sign_*,
 *                          waystone_*, bench_*, boulder_*
 *
 * Public API (matches what 18 downstream consumers already read):
 *   .terrain.heightAt(x, z)              — bilinear lookup against baked grid
 *   .terrain.size / .terrain.segments    — for Physics.addStaticGround
 *   .nature.pushSpots                    — [{ position, type, surfaceRadius, colliderRadius }]
 *   .nature.addExclusion(x, z, r)        — no-op (foliage baked)
 *   .nature.setPlayerUniforms(uniforms)  — forward to instanced foliage materials
 *   .paths.getTilePositions()            — Float32Array sampled along baked ribbons
 *   .paths.getTileCount()                — matches above
 *   .refs                                — typed accessor (see below)
 */
export class GlbWorld {
  static GLB_PATH = '/world/world.glb';
  static TERRAIN_GRID = 193;          // matches Blender Phase 2 authoring
  // Path-ribbon name patterns — sampled into XZ tile positions for the
  // grass-flatten and footstep-surface lookups.
  static PATH_NAME_REGEX = /^(spawn_path|experience_trail|experience_stepping_stone|trail_perimeter|trail_detour|stepping_stone|bridge)/;
  // Push-spot patterns. Each [regex, type] entry classifies a mesh-name into
  // one of the categories the downstream code (ActionPrompts, MiniMap nav
  // blockers, push joke pool) reads. Regexes are tried in order — first
  // match wins.
  static PUSH_NAME_PATTERNS = [
    [/^tree_pine_/,            'tree'],
    [/^tree_birch_/,           'tree'],
    [/^tree_/,                 'tree'],
    [/^hero_tree_/,            'tree'],
    [/^hero_/,                 'tree'],
    [/^gc_boulder_/,           'rock'],
    [/^boulder_/,              'rock'],
    [/^experience_cairn_\d+$/, 'rock'],
    [/^waystone_/,             'sign'],
    [/^bench_/,                'sign'],
    [/^sign_/,                 'sign'],
    [/^cluster_/,              'tree'],
  ];
  static MATERIAL_TOKEN_ORDER = [
    'waterfall', 'water', 'ocean', 'mountain', 'beam', 'glass',
  ]; // order matters — 'waterfall' must beat 'water'

  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;

    // Buckets populated by load(). Names match what downstream code reads.
    this.root = new THREE.Group();
    this.root.name = 'glb-world';
    this.scene.add(this.root);

    this.terrain = {
      mesh: null,
      size: 0,
      segments: 0,
      heights: null,            // Float32Array, length (segments+1)^2
      heightAt: (_x, _z) => 0,  // replaced by bake() at load
    };
    this.nature = {
      pushSpots: [],
      _exclusionNoop: (_x, _z, _r) => {},
      _playerUniforms: null,
    };
    this.nature.addExclusion = this.nature._exclusionNoop;
    this.nature.setPlayerUniforms = (u) => {
      this.nature._playerUniforms = u;
      for (const mat of this._foliageMaterials) {
        if (mat.userData?.setPlayerUniforms) mat.userData.setPlayerUniforms(u);
      }
    };
    this.paths = {
      _positions: new Float32Array(0),
      _count: 0,
      getTilePositions: () => this.paths._positions,
      getTileCount: () => this.paths._count,
    };

    this.refs = {
      section: {},              // refZoneBounding_<key> → THREE.Vector3 (+ .radius)
      sectionFrustum: {},       // refZoneFrustum_<key> → Vector3 (+ .radius)
      interactivePoint: {},     // refInteractivePoint_<key>
      respawn: {},              // refRespawn_<key>
      lights: { cairnLantern: [], forge: null, brazier: null, lighthouseLamp: null },
      beam: { lighthousePivot: null },
      particles: { forgeSmoke: null, brazierFlame: null, waterfallSpray: null },
      interaction: { resumeLectern: null, showcaseMount: null },
      viewpoint: {},            // refViewpoint_<key>
      foliage: { heroTree: [], bench: [], leaves: [], bushes: [] },
      raw: new Map(),           // name → Object3D for any ref we didn't classify
    };

    this._materialTokenMeshes = {
      waterfall: [], water: [], ocean: [], mountain: [], beam: [], glass: [],
    };
    this._emissiveMeshes = [];
    this._foliageMaterials = [];

    // billboards/signs sub-objects are populated by PortfolioMounts (Phase 2)
    // and ProjectShowcase (Phase 3). Phase 1 leaves empty stubs so the
    // facade can expose them without nulls.
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
      nearContact: () => null,
    };
  }

  /** Load + parse the .glb, populate buckets, run assertions. */
  async load(physics) {
    const gltf = await this.loader.loadGLTF(GlbWorld.GLB_PATH);
    const scene = gltf.scene;
    this.root.add(scene);

    // Walk once, classify by name + material.
    scene.traverse((obj) => this.#classify(obj));

    // 1. Bake heightfield from terrain submesh.
    this.#bakeHeightfield();

    // 2. Register colliders with physics.
    if (physics) this.#registerColliders(physics);

    // 3. Apply materials. Phase 1: default palette material for all visible;
    //    Phase 5 will swap special shaders.
    this.#applyDefaultMaterials();

    // 4. Sample path ribbons → tile positions for grass flatten.
    this.#samplePathRibbons();

    // 5. Auto-detect push spots by mesh-name regex. MUST run BEFORE
    //    #instanceSharedMeshes() — otherwise the per-instance Mesh nodes get
    //    collapsed into a single InstancedMesh and the push-spot count
    //    collapses with them. (149 trees → 1 push-spot is exactly the bug
    //    this ordering avoids.)
    this.#detectPushSpots();

    // 6. Detect instancing (shared bpy.data.meshes → InstancedMesh).
    this.#instanceSharedMeshes();

    // 7. Boot assertions — halt loudly if anything's missing.
    this.#assertBootInvariants();

    return this;
  }

  // ── Classification ──────────────────────────────────────────────────────

  #classify(obj) {
    const name = obj.name || '';

    // Empties (refs).
    if (obj.isObject3D && !obj.isMesh && name.startsWith('ref')) {
      this.refs.raw.set(name, obj);
      this.#classifyRef(name, obj);
      return;
    }

    // Meshes.
    if (!obj.isMesh) return;

    // Terrain. The Blender export names this 'terrain_mesh' (with optional
    // suffixing if multiple are present); accept either bare 'terrain' or
    // the 'terrain_mesh' prefix to be resilient to re-exports.
    if (name === 'terrain' || name === 'terrain_mesh' || name.startsWith('terrain_mesh')) {
      this.terrain.mesh = obj;
      return;
    }

    // Collider meshes — keep, hide, register later.
    if (name.startsWith('cuboid_') || name.startsWith('tube_') || name.startsWith('trimesh_')) {
      obj.visible = false;
      obj.userData.collider = true;
      return;
    }

    // Material-token meshes.
    const matName = obj.material?.name?.toLowerCase() || '';
    for (const token of GlbWorld.MATERIAL_TOKEN_ORDER) {
      if (matName.includes(token)) {
        this._materialTokenMeshes[token].push(obj);
        obj.userData.materialToken = token;
        break;
      }
    }

    // Emissive suffix.
    if (name.endsWith('_emissive')) {
      this._emissiveMeshes.push(obj);
      obj.userData.emissive = true;
    }
  }

  #classifyRef(name, obj) {
    // Resolve worldspace transform once — Blender export often nests refs
    // under collection groups. Refs may be deep — capture worldspace pos.
    obj.updateMatrixWorld(true);
    const wpos = new THREE.Vector3();
    obj.getWorldPosition(wpos);
    const pos = wpos.clone();
    const radius = Math.max(obj.scale.x, obj.scale.z); // scale-as-radius

    if (name.startsWith('refZoneBounding_')) {
      const key = name.slice('refZoneBounding_'.length);
      this.refs.section[key] = Object.assign(pos, { radius });
    } else if (name.startsWith('refZoneFrustum_')) {
      const key = name.slice('refZoneFrustum_'.length);
      this.refs.sectionFrustum[key] = Object.assign(pos, { radius });
    } else if (name.startsWith('refInteractivePoint_')) {
      const key = name.slice('refInteractivePoint_'.length);
      this.refs.interactivePoint[key] = pos;
    } else if (name.startsWith('refRespawn_')) {
      const key = name.slice('refRespawn_'.length);
      this.refs.respawn[key] = pos;
    } else if (name.startsWith('refCairnLantern_')) {
      this.refs.lights.cairnLantern.push({ name, position: pos });
    } else if (name === 'refForge') {
      this.refs.lights.forge = pos;
      this.refs.particles.forgeSmoke = pos.clone();
    } else if (name === 'refBrazier') {
      this.refs.lights.brazier = pos;
      this.refs.particles.brazierFlame = pos.clone();
    } else if (name === 'refLighthouseBeamPivot') {
      this.refs.beam.lighthousePivot = obj;     // KEEP the Object3D — we rotate it
    } else if (name === 'refLighthouseLamp') {
      this.refs.lights.lighthouseLamp = pos;
    } else if (name === 'refWaterfallSpray') {
      this.refs.particles.waterfallSpray = pos;
    } else if (name === 'refResumeInteractivePoint') {
      this.refs.interaction.resumeLectern = pos;
    } else if (name === 'refShowcaseMount') {
      this.refs.interaction.showcaseMount = { position: pos, rotation: obj.rotation.clone() };
    } else if (name.startsWith('refViewpoint_')) {
      const key = name.slice('refViewpoint_'.length);
      this.refs.viewpoint[key] = Object.assign(pos, { userData: { ...obj.userData } });
    } else if (name.startsWith('refHeroTree_')) {
      this.refs.foliage.heroTree.push({ name, position: pos });
    } else if (name.startsWith('refBench_')) {
      this.refs.foliage.bench.push({ name, position: pos });
    } else if (name.startsWith('refTreeLeaves_')) {
      // Phase-11c canopy anchor. `radius` carries the canopy size; the
      // species custom property drives which color pair the runtime uses.
      const species = obj.userData?.species || 'pine';
      this.refs.foliage.leaves.push({
        name, position: pos, radius: obj.scale.x || 1, species,
      });
    } else if (name.startsWith('refBushLeaves_')) {
      this.refs.foliage.bushes.push({
        name, position: pos, radius: obj.scale.x || 0.42, species: 'bush',
      });
    }
  }

  // ── Heightfield bake ────────────────────────────────────────────────────

  #bakeHeightfield() {
    const mesh = this.terrain.mesh;
    if (!mesh) throw new Error('GlbWorld: terrain submesh missing from world.glb');

    // The Blender terrain is authored as a 193×193 sculpted grid (Phase 2 of
    // the build). Walk its vertex array, sort into a regular XZ grid, store
    // the Y values in a Float32Array for bilinear lookup.
    const geometry = mesh.geometry;
    const pos = geometry.attributes.position;
    geometry.computeBoundingBox();
    const bbox = geometry.boundingBox;
    const sizeX = bbox.max.x - bbox.min.x;
    const sizeZ = bbox.max.z - bbox.min.z;
    const size = Math.max(sizeX, sizeZ);
    const segments = GlbWorld.TERRAIN_GRID - 1;
    const verts = segments + 1;
    const heights = new Float32Array(verts * verts);

    // Worldspace transform of the terrain mesh (in case Blender export added
    // any root transform we didn't strip).
    mesh.updateMatrixWorld(true);
    const vec = new THREE.Vector3();

    // For a sculpted-grid heightfield, vertices are in regular order. We
    // tolerate non-regular ordering by bucketing into the grid.
    for (let i = 0; i < pos.count; i++) {
      vec.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
      const u = THREE.MathUtils.clamp(
        Math.round(((vec.x - bbox.min.x) / sizeX) * segments), 0, segments);
      const w = THREE.MathUtils.clamp(
        Math.round(((vec.z - bbox.min.z) / sizeZ) * segments), 0, segments);
      heights[u * verts + w] = vec.y;
    }

    this.terrain.size = size;
    this.terrain.segments = segments;
    this.terrain.heights = heights;
    this.terrain.bboxMin = bbox.min.clone();

    // Bilinear lookup. Mirrors Physics.addStaticGround's expectation of
    // heightAt(x, z) returning the worldspace Y at the given XZ.
    this.terrain.heightAt = (x, z) => {
      const fu = ((x - bbox.min.x) / sizeX) * segments;
      const fw = ((z - bbox.min.z) / sizeZ) * segments;
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

  // ── Colliders ───────────────────────────────────────────────────────────

  #registerColliders(physics) {
    const colliderMeshes = [];
    this.root.traverse((obj) => {
      if (obj.isMesh && obj.userData.collider) colliderMeshes.push(obj);
    });

    for (const obj of colliderMeshes) {
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const yaw = obj.rotation.y;

      if (obj.name.startsWith('cuboid_')) {
        physics.addStaticCuboid(
          center.x, center.y, center.z,
          size.x / 2, size.y / 2, size.z / 2,
          yaw,
        );
      } else if (obj.name.startsWith('tube_')) {
        const radius = Math.max(size.x, size.z) / 2;
        const height = size.y;
        physics.addStaticCylinder(center.x, center.y - height / 2, center.z, radius, height);
      }
      // trimesh_* — Rapier supports trimesh colliders via
      // ColliderDesc.trimesh; defer to a later phase if any are present.
      // The world's terrain is the only trimesh today and uses the
      // heightfield path above.
    }
  }

  // ── Materials ───────────────────────────────────────────────────────────

  #applyDefaultMaterials() {
    this.root.traverse((obj) => {
      if (!obj.isMesh || obj.userData.collider) return;
      if (obj === this.terrain.mesh) return; // terrain keeps its GLB material
      // Phase 1: special-token meshes still get the GLB material (palette
      // sample baked in). Phase 5 swaps these for ShaderMaterial variants.
      // Default meshes also keep the GLB material — the master shader is
      // attached in Phase 5 too.
      // We DO collect foliage materials so Phase 5 can flip a uniform later.
      if (this.#isFoliageMesh(obj) && obj.material) {
        this._foliageMaterials.push(obj.material);
      }
    });
    // Keep SmoothLitPaletteMaterial referenced so Phase 5 can import it from
    // here without a stale-side-effect-free warning.
    void SmoothLitPaletteMaterial;
  }

  #isFoliageMesh(obj) {
    return /^(pine|birch|hero_tree|bush|fern|flower|boulder)_/.test(obj.name || '');
  }

  // ── Instancing ──────────────────────────────────────────────────────────

  #instanceSharedMeshes() {
    // Group meshes by shared geometry datablock.
    const buckets = new Map(); // geometry.uuid → [obj…]
    this.root.traverse((obj) => {
      if (!obj.isMesh || obj.userData.collider) return;
      if (obj === this.terrain.mesh) return;
      const id = obj.geometry?.uuid;
      if (!id) return;
      const arr = buckets.get(id) || [];
      arr.push(obj);
      buckets.set(id, arr);
    });
    for (const [, list] of buckets) {
      if (list.length < 2) continue;
      this.#collapseToInstancedMesh(list);
    }
  }

  #collapseToInstancedMesh(meshes) {
    const source = meshes[0];
    const count = meshes.length;
    const inst = new THREE.InstancedMesh(source.geometry, source.material, count);
    inst.name = `${source.name}__inst`;
    inst.castShadow = source.castShadow;
    inst.receiveShadow = source.receiveShadow;
    const m = new THREE.Matrix4();
    for (let i = 0; i < count; i++) {
      meshes[i].updateMatrixWorld(true);
      m.copy(meshes[i].matrixWorld);
      inst.setMatrixAt(i, m);
      meshes[i].visible = false;
      meshes[i].parent?.remove(meshes[i]);
    }
    inst.instanceMatrix.needsUpdate = true;
    this.root.add(inst);
  }

  // ── Path-ribbon sampling ────────────────────────────────────────────────

  #samplePathRibbons() {
    const points = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh) return;
      if (obj.userData.collider) return;
      if (obj === this.terrain.mesh) return;
      if (!GlbWorld.PATH_NAME_REGEX.test(obj.name)) return;
      const geom = obj.geometry;
      const pos = geom.attributes.position;
      if (!pos) return;
      obj.updateMatrixWorld(true);
      const v = new THREE.Vector3();
      const stride = Math.max(1, Math.floor(pos.count / 40)); // ~40 samples per ribbon
      for (let i = 0; i < pos.count; i += stride) {
        v.fromBufferAttribute(pos, i).applyMatrix4(obj.matrixWorld);
        points.push(v.x, v.z);
      }
    });
    this.paths._positions = new Float32Array(points);
    this.paths._count = points.length / 2;
  }

  // ── Push spots ──────────────────────────────────────────────────────────

  #detectPushSpots() {
    const found = [];
    this.root.traverse((obj) => {
      if (!obj.isMesh && !obj.isInstancedMesh) return;
      if (obj.userData?.collider) return;
      const name = obj.name || '';
      const matched = GlbWorld.PUSH_NAME_PATTERNS.find(([re]) => re.test(name));
      if (!matched) return;
      const [, type] = matched;
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const half = Math.max(size.x, size.z) / 2;
      found.push({
        position: center,
        type,
        surfaceRadius: half + 0.2,
        colliderRadius: half,
      });
    });
    this.nature.pushSpots = found;
  }

  // ── Boot invariant assertions ───────────────────────────────────────────

  #assertBootInvariants() {
    const required = {
      'terrain submesh': !!this.terrain.mesh && !!this.terrain.heights,
      'refZoneBounding_spawn': !!this.refs.section.spawn,
      'refZoneBounding_projects': !!this.refs.section.projects,
      'refZoneBounding_experience': !!this.refs.section.experience,
      'refZoneBounding_skills': !!this.refs.section.skills,
      'refZoneBounding_contact': !!this.refs.section.contact,
      'refShowcaseMount': !!this.refs.interaction.showcaseMount,
      'refResumeInteractivePoint': !!this.refs.interaction.resumeLectern,
      'refLighthouseBeamPivot': !!this.refs.beam.lighthousePivot,
      'refForge': !!this.refs.lights.forge,
      'refBrazier': !!this.refs.lights.brazier,
      'refCairnLantern_* ≥4': this.refs.lights.cairnLantern.length >= 4,
      'push-spots ≥50': this.nature.pushSpots.length >= 50,
    };
    const failures = Object.entries(required).filter(([, ok]) => !ok).map(([k]) => k);
    if (failures.length > 0) {
      throw new Error(
        `GlbWorld boot assertions failed:\n  - ${failures.join('\n  - ')}`,
      );
    }
    console.log('[GlbWorld] load: OK', {
      heightfieldSize: this.terrain.size.toFixed(2),
      cairnLanterns: this.refs.lights.cairnLantern.length,
      pushSpots: this.nature.pushSpots.length,
      sections: Object.keys(this.refs.section),
    });
  }
}
