import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import {
  Fn, uniform, texture, uv, rotateUV, vec2, vec3, float, color,
  mix, normalWorld, normalLocal, positionGeometry, attribute,
  length, smoothstep, max, sin, cos, normalize, clamp,
} from 'three/tsl';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { snowMask, snowColor, snowEmissive } from './SnowState.js';

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
 *   2. SHELL — ~150 small alpha-cut leaf cards scattered on a slightly larger
 *      sphere (radius = 1 − rng³ so they clump toward the surface), each spun
 *      randomly in 3D with its normals lerped 85 % toward the outward sphere
 *      normal. The SDF cutout (UV rotated by the wind) gives the ragged leafy
 *      edge that breaks the core's smooth outline into foliage.
 *
 * Both layers are a `Mesh` over an `InstancedBufferGeometry` (NOT InstancedMesh)
 * so the vertex node can rebuild each leaf's world position from per-instance
 * attributes (aCenter / aScale / aRot) — the same trick Grass.js uses. That in
 * turn powers the player interaction: as the avatar moves through a bush the
 * near-side leaves push away and press down (you "part" it), and jumping up into
 * a low canopy makes those leaves flutter — a cheap shader-side "soft physics"
 * driven purely by the player's 3D distance to each leaf (no Rapier bodies; the
 * thousands of cards would be far too many to simulate). Bushes react because
 * they sit at walking height; canopies only react when you jump up near them,
 * because the test is full 3D distance including Y.
 *
 * Two-tone albedo (mix(colorA, colorB) by normal·sunDir) is lit by
 * MeshLambertNodeMaterial (scene sun/ambient/hemi + fog) so canopies darken at
 * night through the same rig as the trunks. Colliders already exist on trunks +
 * bushes, so this adds none.
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
// Gentle positional wind sway of the whole blob (m), sampled per-instance so
// each canopy/bush breathes a little out of phase with its neighbours.
const WIND_SWAY = 0.16;

// Player interaction ("soft physics"). The player is treated as a VERTICAL BODY
// COLUMN (feet→head), not a single point — leaves react wherever the body OR head
// brushes them, so on short trees you part the canopy just by walking through, no
// jump required (player.position is feet-height; spawn is y≈0.02). Reaction is
// the leaf's 3D distance to the NEAREST point on that column.
const BODY_BELOW = 0.3;          // column bottom below the feet anchor (m)
const BODY_ABOVE = 2.0;          // column top above the feet anchor (head + reach, m)
const REACT_RADIUS = 1.2;        // leaves within this of the body column react (m)
const REACT_INNER = 0.2;         // full strength once this close
const PART_STRENGTH = 0.5;       // how far leaves shove away from the body (m)
const PART_DOWN = 0.12;          // press the parted leaves down a touch (m)
const FLUTTER_FREQ = 6.0;        // shimmer speed of disturbed leaves
const FLUTTER_AMP = 0.09;        // shimmer amplitude (m)

export class Foliage {
  /**
   * @param {THREE.Scene} scene
   * @param {import('./Wind.js').Wind} wind
   * @param {THREE.Texture} sdfTexture  foliageSDF.png (Nearest, no mipmaps)
   * @param {Array<{key:string, refs:Array<{position:THREE.Vector3, scale:number}>,
   *                colorA:string, colorB:string}>} clouds
   */
  constructor(scene, wind, sdfTexture, clouds = [], { shell = true } = {}) {
    this.scene = scene;
    this.wind = wind;
    this.sdf = sdfTexture;
    this.clouds = [];
    // When false (medium/low tiers) the leaf-card shell overdraw pass is
    // skipped — foliage renders as just the opaque core blob to save fill-rate.
    this.shellEnabled = shell;

    // Two-tone lighting direction (lit vs shaded side of the blob), pushed each
    // frame from TimeOfDay.sunOffset via setSunDirection(). Seeded to a daytime
    // down-sun so the first frame isn't flat.
    this.sunDir = uniform(vec3(0.4, 0.7, 0.3));
    // Player world position (incl. Y) for the part/flutter interaction; pushed
    // each frame from App.tick via setPlayerPos(). Parked far below the world so
    // nothing reacts until the first real update.
    this.uPlayerPos = uniform(vec3(0, -9999, 0));

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
      const base = mix(colorANode, colorBNode, facing);
      // Snow settles on the upward leaf cards so canopies/bushes crown white.
      return snowColor(base, snowMask({ low: 0.25, high: 0.7 }));
    })();
  }

  // ── World-position vertex node shared by both layers ────────────────────────
  // Rebuilds each instance's leaf vertex in world space from aCenter/aScale/aRot
  // (the mesh itself sits at the origin with an identity transform, like Grass),
  // then layers wind sway + the player part/flutter on top.
  #positionNode() {
    const rotX = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x, p.y.mul(c).sub(p.z.mul(s)), p.y.mul(s).add(p.z.mul(c))); };
    const rotY = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).add(p.z.mul(s)), p.y, p.z.mul(c).sub(p.x.mul(s))); };
    const rotZ = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).sub(p.y.mul(s)), p.x.mul(s).add(p.y.mul(c)), p.z); };

    return Fn(() => {
      const local = positionGeometry;
      const center = attribute('aCenter');     // instance world position
      const scl = attribute('aScale');         // instance uniform scale
      const rot = attribute('aRot');           // instance spin (tiltX, yaw, tiltZ)

      // local → scale → spin (z,y,x to match Euler 'XYZ') → translate to center.
      let p = local.mul(scl);
      p = rotZ(p, rot.z);
      p = rotY(p, rot.y);
      p = rotX(p, rot.x);
      const world = center.add(p).toVar();

      // Gentle whole-blob wind sway, sampled at the instance center so blobs
      // breathe out of phase.
      const sway = this.wind.offsetNode(center.xz).mul(WIND_SWAY);
      world.x.addAssign(sway.x);
      world.z.addAssign(sway.y);

      // Player interaction: leaves react to the nearest point on the player's
      // vertical body column (feet→head), so a head/torso brush parts them just
      // like walking through a bush — no jump needed. Push the near-side leaves
      // away + down with a per-vertex flutter so they shimmer instead of sliding
      // as a slab; near-side verts get a stronger env than the far side, so the
      // blob squishes/parts rather than translating whole.
      const feet = this.uPlayerPos;
      const colY = clamp(world.y, feet.y.sub(BODY_BELOW), feet.y.add(BODY_ABOVE));
      const closest = vec3(feet.x, colY, feet.z);
      const delta = world.sub(closest).toVar();
      const dist = length(delta).toVar();
      const env = smoothstep(REACT_RADIUS, REACT_INNER, dist).toVar();
      const dir = delta.div(max(dist, 0.001));
      const phase = world.x.add(world.z).mul(2.3);
      const flutter = sin(this.wind.nodes.time.mul(FLUTTER_FREQ).add(phase)).mul(FLUTTER_AMP).mul(env);
      const part = env.mul(PART_STRENGTH);
      world.x.addAssign(dir.x.mul(part).add(flutter));
      world.z.addAssign(dir.z.mul(part).add(flutter.mul(0.6)));
      world.y.subAssign(env.mul(PART_DOWN));

      return world;
    })();
  }

  // ── Object-space normal node (spin the baked normal so lighting follows) ────
  #normalNode() {
    const rotX = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x, p.y.mul(c).sub(p.z.mul(s)), p.y.mul(s).add(p.z.mul(c))); };
    const rotY = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).add(p.z.mul(s)), p.y, p.z.mul(c).sub(p.x.mul(s))); };
    const rotZ = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).sub(p.y.mul(s)), p.x.mul(s).add(p.y.mul(c)), p.z); };
    return Fn(() => {
      const rot = attribute('aRot');
      let n = rotZ(normalLocal, rot.z);
      n = rotY(n, rot.y);
      n = rotX(n, rot.x);
      return normalize(n);
    })();
  }

  // ── One cloud = a solid core + a leaf-card shell, both instanced ────────────
  #buildCloud(cloud) {
    const refs = cloud.refs ?? [];
    if (refs.length === 0) return;

    const colorANode = uniform(color(cloud.colorA));
    const colorBNode = uniform(color(cloud.colorB));

    // Per-instance attributes (shared between core + shell so they stay glued).
    const attribs = this.#instanceAttribs(refs, cloud.key);
    const coreGeom = this.#instanced(this.coreGeometry, attribs, refs.length);

    // 1. Opaque core — fills the interior so the blob is never see-through.
    const coreMat = new MeshLambertNodeMaterial({ side: THREE.FrontSide });
    coreMat.positionNode = this.#positionNode();
    coreMat.normalNode = this.#normalNode();
    coreMat.colorNode = this.#colorNode(colorANode, colorBNode);
    coreMat.emissiveNode = snowEmissive(snowMask({ low: 0.25, high: 0.7 }));
    const core = new THREE.Mesh(coreGeom, coreMat);
    core.name = `foliage:${cloud.key}:core`;
    core.frustumCulled = false;
    core.castShadow = false;
    core.receiveShadow = true;
    this.scene.add(core);

    // 2. Leaf-card shell — ragged SDF edge over the core. Skipped on
    // medium/low tiers (this.shellEnabled === false) to save the overdraw pass.
    let shell = null;
    let shellGeom = null;
    let shellMat = null;
    if (this.shellEnabled) {
      shellGeom = this.#instanced(this.shellGeometry, attribs, refs.length);
      shellMat = new MeshLambertNodeMaterial({ side: THREE.DoubleSide });
      shellMat.positionNode = this.#positionNode();
      shellMat.normalNode = this.#normalNode();
      shellMat.opacityNode = Fn(() => {
        const angle = this.wind.offsetNode(attribute('aCenter').xz).length().mul(WIND_FLUTTER);
        const rotated = rotateUV(uv(), angle, vec2(0.5));
        return texture(this.sdf, rotated).r;
      })();
      shellMat.alphaTest = SDF_THRESHOLD;
      shellMat.colorNode = this.#colorNode(colorANode, colorBNode);
      shellMat.emissiveNode = snowEmissive(snowMask({ low: 0.25, high: 0.7 }));
      shell = new THREE.Mesh(shellGeom, shellMat);
      shell.name = `foliage:${cloud.key}`;
      shell.frustumCulled = false;
      shell.castShadow = false;
      shell.receiveShadow = true;
      this.scene.add(shell);
    }

    this.clouds.push({
      key: cloud.key, mesh: shell, core, coreGeom, shellGeom,
      material: shellMat, coreMat, colorANode, colorBNode,
    });
  }

  // InstancedBufferGeometry over a shared base (position/normal/uv/index by
  // reference) plus this cloud's per-instance attributes. Mirrors Grass.
  #instanced(base, attribs, count) {
    const geom = new THREE.InstancedBufferGeometry();
    geom.index = base.index;
    geom.attributes.position = base.attributes.position;
    geom.attributes.normal = base.attributes.normal;
    geom.attributes.uv = base.attributes.uv;
    geom.instanceCount = count;
    geom.setAttribute('aCenter', new THREE.InstancedBufferAttribute(attribs.center, 3));
    geom.setAttribute('aScale', new THREE.InstancedBufferAttribute(attribs.scale, 1));
    geom.setAttribute('aRot', new THREE.InstancedBufferAttribute(attribs.rot, 3));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);
    return geom;
  }

  // Per-instance transforms: ref world position + scale + deterministic spin
  // (refs carry no usable rotation of their own). Same RNG draw order as the
  // old #buildMatrices so blobs keep their established look.
  #instanceAttribs(refs, key) {
    const n = refs.length;
    const center = new Float32Array(n * 3);
    const scale = new Float32Array(n);
    const rot = new Float32Array(n * 3);
    const rng = mulberry32(0xc10d ^ this.#hashKey(key));
    for (let i = 0; i < n; i++) {
      const r = refs[i];
      center[i * 3] = r.position.x;
      center[i * 3 + 1] = r.position.y;
      center[i * 3 + 2] = r.position.z;
      // Match the prior euler.set((rng-0.5)*0.6, rng*2π, (rng-0.5)*0.6) order.
      rot[i * 3] = (rng() - 0.5) * 0.6;        // tilt X
      rot[i * 3 + 1] = rng() * Math.PI * 2;    // yaw
      rot[i * 3 + 2] = (rng() - 0.5) * 0.6;    // tilt Z
      scale[i] = r.scale || 1;
    }
    return { center, scale, rot };
  }

  #hashKey(key) {
    let h = 0;
    for (let i = 0; i < key.length; i++) h = (Math.imul(h, 31) + key.charCodeAt(i)) | 0;
    return h >>> 0;
  }

  // ── Public API (matches the hooks App.tick already calls) ───────────────────

  /** Two-tone lit/shaded mix follows the sun. App passes TimeOfDay.sunOffset. */
  setSunDirection(offset) {
    if (!offset) return;
    const len = Math.hypot(offset.x, offset.y, offset.z) || 1;
    this.sunDir.value.set(offset.x / len, offset.y / len, offset.z / len);
  }

  /** Player world position for the part/flutter interaction (App passes the
   *  player position each frame; the second arg is unused — kept so the call
   *  signature matches Grass.setPlayerPos). */
  setPlayerPos(pos) {
    if (!pos) return;
    this.uPlayerPos.value.set(pos.x, pos.y, pos.z);
  }

  /**
   * Show/hide the entire foliage layer. Visibility-only (no geometry/material
   * churn, no pipeline recompile), so it's safe to toggle at runtime — used by
   * the adaptive perf-shed ladder as a last resort on weak hardware.
   */
  setVisible(v) {
    for (const c of this.clouds) {
      if (c.core) c.core.visible = v;
      if (c.mesh) c.mesh.visible = v; // shell may be gated off (medium/low)
    }
  }

  dispose() {
    for (const c of this.clouds) {
      if (c.mesh) this.scene.remove(c.mesh); // shell may be gated off (medium/low)
      this.scene.remove(c.core);
      c.coreGeom?.dispose();
      c.shellGeom?.dispose();
      c.material?.dispose();
      c.coreMat.dispose();
    }
    this.shellGeometry?.dispose();
    this.coreGeometry?.dispose();
    this.clouds = [];
  }
}
