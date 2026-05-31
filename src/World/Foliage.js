import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import {
  Fn, uniform, texture, uv, rotateUV, vec2, vec3, color,
  mix, normalWorld, positionLocal,
} from 'three/tsl';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/**
 * Runtime tree-canopy + bush foliage — Bruno's SDF "leaf cloud" ported to the
 * WebGPU/TSL backend (folio-2025 sources/Game/World/Foliage.js + Trees.js).
 *
 * Trunks (birch/cherry/oakTrees.glb) ship without fluffy canopies; leaves are
 * grown here at runtime. Each blob is TWO layered instanced meshes so it reads
 * as a solid rounded cloud from every angle (not see-through flat cards):
 *
 *   1. CORE — an opaque low-poly icosphere, two-tone lit. Guarantees a rounded
 *      filled silhouette with no see-through and no "edge-on flat card = thin
 *      line" artefact (the bug the leaf-cards-only version showed from the side).
 *   2. SHELL — ~110 small alpha-cut leaf cards scattered on a slightly larger
 *      sphere (radius = 1 − rng³ so they clump toward the surface), each spun
 *      randomly with its normals lerped 85 % toward the outward sphere normal.
 *      The SDF cutout (UV rotated by the wind) gives the ragged leafy edge that
 *      breaks the core's smooth outline into foliage.
 *
 * Both layers share the same two-tone mix(colorA, colorB) by normal·sunDir, lit
 * by MeshLambertNodeMaterial (scene sun/ambient/hemi + fog) so canopies darken
 * at night through the same rig as the trunks. One InstancedMesh per layer per
 * cloud, one instance per reference (world position + scale + deterministic
 * spin). Bruno's see-through-near-vehicle fade is dropped (no vehicle); colliders
 * already exist on trunks + bushes, so this adds none.
 */

// Deterministic RNG (mulberry32) so the blob + per-instance spins are stable
// across reloads — replaces Bruno's seedrandom 'alea'. (See Water.js.)
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Many small cards, RANDOMLY ORIENTED IN 3D. Bruno only `rotateZ`s his cards so
// they all keep the same +Z facing — fine for his top-down camera, but in a
// third-person side view every card goes edge-on at once and the blob reads as a
// fan of thin vertical lines (the bug). Random full-3D orientation means a good
// fraction of cards face the camera from ANY angle; the rest are short fuzz
// backed by the opaque core. Smaller cards keep edge-on slivers short.
const SHELL_PLANES = 150;        // leaf cards per blob (dense → continuous fuzz)
const PLANE_SIZE = 0.55;         // smaller → edge-on cards read as fuzz, not streaks
const NORMAL_SPHERE_MIX = 0.85;  // how far each card's normals bend to the blob normal
// SDF alpha cutout. foliageSDF.png R: mean 0.25; ~45 % of texels > 0.3, ~60 %
// > 0.1. Bruno keeps where sdf > 0.4 — too holey for an isolated blob, so we cut
// lower (fuller cards) and rely on the opaque core for the silhouette.
const SDF_THRESHOLD = 0.18;
// Cards hug the core surface: scatter radius in [SHELL_MIN, 1] × blob scale, so
// they form a tight fuzzy rim instead of a wide halo of lines sticking out.
const SHELL_MIN_RADIUS = 0.55;
// Opaque inner core — the guaranteed rounded silhouette. detail 2 = puffier,
// still cheap. Sized so the leaf rim sits just proud of it (no see-through).
const CORE_RADIUS = 0.82;
const CORE_DETAIL = 2;
// Wind-driven UV rotation strength (Bruno: wind.offset.length() × 2.2).
const WIND_FLUTTER = 2.2;

export class Foliage {
  /**
   * @param {THREE.Scene} scene
   * @param {import('./Wind.js').Wind} wind
   * @param {THREE.Texture} sdfTexture  foliageSDF.png (Nearest, no mipmaps)
   * @param {Array<{key:string, refs:Array<{position:THREE.Vector3, scale:number}>,
   *                colorA:string, colorB:string}>} clouds
   */
  constructor(scene, wind, sdfTexture, clouds = []) {
    this.scene = scene;
    this.wind = wind;
    this.sdf = sdfTexture;
    this.clouds = [];

    // Two-tone lighting direction (lit vs shaded side of the blob), pushed each
    // frame from TimeOfDay.sunOffset via setSunDirection(). Seeded to a daytime
    // down-sun so the first frame isn't flat.
    this.sunDir = uniform(vec3(0.4, 0.7, 0.3));

    this.#buildShellGeometry();
    this.#buildCoreGeometry();
    for (const cloud of clouds) this.#buildCloud(cloud);
  }

  // ── Leaf-card shell geometry (built once, reused by every cloud) ────────────
  #buildShellGeometry() {
    const rng = mulberry32(0xf01ace);
    const planes = [];
    const tmpPos = new THREE.Vector3();
    const sphereNormal = new THREE.Vector3();
    const spherical = new THREE.Spherical();

    for (let i = 0; i < SHELL_PLANES; i++) {
      const plane = new THREE.PlaneGeometry(PLANE_SIZE, PLANE_SIZE);

      // Scatter on a sphere, clumped toward the surface but never inside the
      // core (radius in [SHELL_MIN_RADIUS, 1]) so cards form a tight rim.
      const radius = SHELL_MIN_RADIUS + (1 - SHELL_MIN_RADIUS) * (1 - Math.pow(rng(), 3));
      spherical.set(radius, Math.PI * 2 * rng(), Math.PI * rng());
      const position = new THREE.Vector3().setFromSpherical(spherical);

      // Random FULL 3D orientation (not just rotateZ) so cards face every
      // direction → the blob looks leafy from any camera angle, never a fan of
      // parallel edge-on lines.
      plane.rotateX(rng() * Math.PI * 2);
      plane.rotateY(rng() * Math.PI * 2);
      plane.rotateZ(rng() * Math.PI * 2);
      plane.translate(position.x, position.y, position.z);

      // Bend each vertex normal toward the outward blob normal so the flat cards
      // shade as one rounded mass (Bruno: lerp(vertexPos, sphereNormal, 0.85),
      // used un-normalised exactly like the source).
      sphereNormal.copy(position).normalize();
      const posAttr = plane.attributes.position.array;
      const normalArray = new Float32Array(posAttr.length);
      for (let v = 0; v < 4; v++) {
        const v3 = v * 3;
        tmpPos.set(posAttr[v3], posAttr[v3 + 1], posAttr[v3 + 2]);
        tmpPos.lerp(sphereNormal, NORMAL_SPHERE_MIX);
        normalArray[v3] = tmpPos.x;
        normalArray[v3 + 1] = tmpPos.y;
        normalArray[v3 + 2] = tmpPos.z;
      }
      plane.setAttribute('normal', new THREE.BufferAttribute(normalArray, 3));
      planes.push(plane);
    }

    this.shellGeometry = mergeGeometries(planes);
    for (const p of planes) p.dispose();
  }

  // ── Opaque inner core geometry ──────────────────────────────────────────────
  #buildCoreGeometry() {
    this.coreGeometry = new THREE.IcosahedronGeometry(CORE_RADIUS, CORE_DETAIL);
  }

  // ── Two-tone albedo node shared by both layers ──────────────────────────────
  #colorNode(colorANode, colorBNode) {
    return Fn(() => {
      const facing = normalWorld.dot(this.sunDir).smoothstep(-0.2, 1.0);
      return mix(colorANode, colorBNode, facing);
    })();
  }

  // ── One cloud = a solid core + a leaf-card shell, both instanced ────────────
  #buildCloud(cloud) {
    const refs = cloud.refs ?? [];
    if (refs.length === 0) return;

    const colorANode = uniform(color(cloud.colorA));
    const colorBNode = uniform(color(cloud.colorB));

    // Per-instance matrices (shared by core + shell so they stay co-located).
    const matrices = this.#buildMatrices(refs, cloud.key);

    // 1. Opaque core — fills the interior so the blob is never see-through.
    const coreMat = new MeshLambertNodeMaterial({ side: THREE.FrontSide });
    coreMat.colorNode = this.#colorNode(colorANode, colorBNode);
    const core = new THREE.InstancedMesh(this.coreGeometry, coreMat, refs.length);
    core.name = `foliage:${cloud.key}:core`;
    core.frustumCulled = false;
    core.castShadow = false;
    core.receiveShadow = true;
    core.userData.noTorchRaycast = true;

    // 2. Leaf-card shell — ragged SDF edge over the core.
    const shellMat = new MeshLambertNodeMaterial({ side: THREE.DoubleSide });
    shellMat.opacityNode = Fn(() => {
      const angle = this.wind.offsetNode(positionLocal.xz).length().mul(WIND_FLUTTER);
      const rotated = rotateUV(uv(), angle, vec2(0.5));
      return texture(this.sdf, rotated).r;
    })();
    shellMat.alphaTest = SDF_THRESHOLD;
    shellMat.colorNode = this.#colorNode(colorANode, colorBNode);
    const shell = new THREE.InstancedMesh(this.shellGeometry, shellMat, refs.length);
    shell.name = `foliage:${cloud.key}`;
    shell.frustumCulled = false;
    shell.castShadow = false;
    shell.receiveShadow = true;
    shell.userData.noTorchRaycast = true;

    for (let i = 0; i < refs.length; i++) {
      core.setMatrixAt(i, matrices[i]);
      shell.setMatrixAt(i, matrices[i]);
    }
    core.instanceMatrix.needsUpdate = true;
    shell.instanceMatrix.needsUpdate = true;
    this.scene.add(core);
    this.scene.add(shell);

    this.clouds.push({
      key: cloud.key, mesh: shell, core, material: shellMat, coreMat,
      colorANode, colorBNode,
    });
  }

  // Per-instance transforms: ref world position + scale + deterministic spin
  // (refs carry no usable rotation of their own).
  #buildMatrices(refs, key) {
    const out = [];
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    const euler = new THREE.Euler();
    const rng = mulberry32(0xc10d ^ this.#hashKey(key));
    for (const r of refs) {
      pos.copy(r.position);
      euler.set((rng() - 0.5) * 0.6, rng() * Math.PI * 2, (rng() - 0.5) * 0.6);
      quat.setFromEuler(euler);
      scl.setScalar(r.scale || 1);
      out.push(new THREE.Matrix4().compose(pos, quat, scl));
    }
    return out;
  }

  #hashKey(key) {
    let h = 0;
    for (let i = 0; i < key.length; i++) h = (Math.imul(h, 31) + key.charCodeAt(i)) | 0;
    return h >>> 0;
  }

  // ── Public API (matches the hook App.tick already calls) ────────────────────

  /** Two-tone lit/shaded mix follows the sun. App passes TimeOfDay.sunOffset. */
  setSunDirection(offset) {
    if (!offset) return;
    const len = Math.hypot(offset.x, offset.y, offset.z) || 1;
    this.sunDir.value.set(offset.x / len, offset.y / len, offset.z / len);
  }

  dispose() {
    for (const c of this.clouds) {
      this.scene.remove(c.mesh);
      this.scene.remove(c.core);
      c.material.dispose();
      c.coreMat.dispose();
    }
    this.shellGeometry?.dispose();
    this.coreGeometry?.dispose();
    this.clouds = [];
  }
}
