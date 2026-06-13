import * as THREE from "three/webgpu";
import {
  float, mix, mx_noise_float, normalLocal, normalWorld,
  positionLocal, smoothstep, uniform, vec3, vec4,
} from "three/tsl";
import { snowCoverage, snowGrowAt, snowColor, snowEmissive } from "../World/SnowState.js";
import { worldLitOutput, worldShadowCatcher } from "../World/WorldLight.js";

/**
 * SnowShells — CONFORMING snow crusts. Each target's real geometry is drawn a
 * second time, inflated along its normals, with a live normalWorld.y cutout so
 * only world-up fragments survive. The crust therefore hugs the actual shape
 * (bench slats, backrest edges, rock crowns, the football's curve) instead of
 * being a blob at the bounding box — and because the mask is evaluated per
 * fragment against the CURRENT world normal, snow always reforms on whatever
 * face points up after an object is moved or rolled.
 *
 * Static targets (bench meshes, boulder instances) are baked to world space
 * and merged into ONE mesh/draw; their growth is patch-staggered via
 * snowGrowAt, in sync with the ground blanket.
 *
 * Dynamic targets (football, pushable bricks, wandering animals) each get
 * their own shell with a per-object `accum` uniform: snow builds while the
 * object rests in snowfall, and SHEDS when it moves — the crust vanishes and
 * SnowPiles.dropLumps() spawns persistent lumps falling to the ground.
 * Movement is detected from horizontal world-position deltas (works for
 * physics bodies and CPU-animated rigs alike; animals' idle bob is vertical
 * so it never triggers a shed).
 */

const SHED_SPEED = 0.55;    // m/s horizontal — faster than this sheds the crust
const REST_SPEED = 0.12;    // m/s — slower than this counts as "at rest"
const ACCUM_SECONDS = 9;    // rest time in snowfall for a full crust
const SHED_MIN_ACCUM = 0.3; // thinner crusts than this just wipe, no lumps
const SHED_COOLDOWN = 1.5;  // s between lump bursts from one object

/** Bake a source geometry (position+normal+index only) through a matrix. */
function bakeGeometry(geometry, matrix, out) {
  const posA = geometry.attributes.position;
  const norA = geometry.attributes.normal;
  if (!posA || !norA) return;
  const nm = _nm.getNormalMatrix(matrix);
  const base = out.positions.length / 3;
  const v = _v;
  for (let i = 0; i < posA.count; i++) {
    v.set(posA.getX(i), posA.getY(i), posA.getZ(i)).applyMatrix4(matrix);
    out.positions.push(v.x, v.y, v.z);
    v.set(norA.getX(i), norA.getY(i), norA.getZ(i)).applyMatrix3(nm).normalize();
    out.normals.push(v.x, v.y, v.z);
  }
  const idx = geometry.index;
  if (idx) {
    for (let i = 0; i < idx.count; i++) out.indices.push(base + idx.getX(i));
  } else {
    for (let i = 0; i < posA.count; i++) out.indices.push(base + i);
  }
}

function buildMergedGeometry(out) {
  const geom = new THREE.BufferGeometry();
  geom.setAttribute(
    "position",
    new THREE.BufferAttribute(new Float32Array(out.positions), 3),
  );
  geom.setAttribute(
    "normal",
    new THREE.BufferAttribute(new Float32Array(out.normals), 3),
  );
  geom.setIndex(out.indices);
  return geom;
}

/**
 * Shared shell node wiring. `grow` 0→1 drives both the inflation depth and
 * the fragment cutout, so the crust thickens in and breaks up organically at
 * its edges (alphaTest cutout — no transparency sorting).
 * @param {*} grow TSL node 0..1
 * @param {number} depth max crust thickness in LOCAL units
 */
function applyShellNodes(mat, grow, depth) {
  const lump = mx_noise_float(positionLocal.mul(2.4)).mul(0.5).add(0.5);
  const thickness = grow.mul(mix(float(0.55), float(1.0), lump)).mul(depth);
  mat.positionNode = positionLocal.add(
    normalLocal.mul(thickness.add(0.012)),
  );

  // Live world-up cutout: only top-facing fragments survive, with noisy
  // edges so the crust line is ragged like settled snow, not a hard contour.
  const facing = smoothstep(0.18, 0.5, normalWorld.y);
  const breakup = mx_noise_float(positionLocal.mul(1.9)).mul(0.5).add(0.5);
  const cover = facing.mul(grow).mul(breakup.mul(0.5).add(0.75));
  mat.opacityNode = cover;
  mat.alphaTest = 0.42;

  const albedo = snowColor(vec3(1, 1, 1), float(1)); // pure shaded snow
  const albedo4 = vec4(albedo, 1.0);
  mat.colorNode = albedo4;
  const catchedShadow = float(1).toVar();
  mat.receivedShadowNode = worldShadowCatcher(catchedShadow);
  mat.outputNode = worldLitOutput(albedo4, snowEmissive(cover), catchedShadow);
}

export class SnowShells {
  /**
   * @param {THREE.Scene} scene
   * @param {{
   *   staticSources?: Array<{geometry: THREE.BufferGeometry, matrix: THREE.Matrix4}>,
   *   piles?: import('./SnowPiles.js').SnowPiles,
   * }} o
   */
  constructor(scene, { staticSources = [], piles = null } = {}) {
    this.scene = scene;
    this.piles = piles;
    this._dynamics = [];
    this._staticVisible = false;
    this.#buildStatic(staticSources);
  }

  #buildStatic(sources) {
    if (!sources.length) {
      this._static = null;
      return;
    }
    const out = { positions: [], normals: [], indices: [] };
    for (const s of sources) bakeGeometry(s.geometry, s.matrix, out);
    if (!out.indices.length) {
      this._static = null;
      return;
    }
    const geom = buildMergedGeometry(out);
    const mat = new THREE.MeshLambertNodeMaterial({ fog: false });
    mat.name = "snowShellsStatic";
    // Patch-staggered growth, slightly ahead of the ground (props collect a
    // touch early) — geometry is baked to world space so positionLocal IS the
    // world position here.
    applyShellNodes(mat, snowGrowAt(positionLocal.xz, 0.08), 0.07);

    const mesh = new THREE.Mesh(geom, mat);
    mesh.frustumCulled = false; // spans the island
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    mesh.name = "snowShellsStatic";
    mesh.visible = false;
    this._static = mesh;
    this.scene.add(mesh);
    console.log(
      `[SnowShells] static crust: ${sources.length} sources, ${out.positions.length / 3} verts`,
    );
  }

  /** Per-object material — own accum uniform, melt-gated by coverage. */
  #makeDynamicMaterial(depth) {
    const accumU = uniform(0);
    const mat = new THREE.MeshLambertNodeMaterial({ fog: false });
    mat.name = "snowShellDynamic";
    const grow = accumU.mul(smoothstep(float(0.1), float(0.35), snowCoverage));
    applyShellNodes(mat, grow, depth);
    return { mat, accumU };
  }

  #addDynamic(object, shellMesh, accumU, {
    footRadius,
    lumpY,
    shedSpeed = SHED_SPEED,
    accumSeconds = ACCUM_SECONDS,
  }) {
    shellMesh.castShadow = false;
    shellMesh.receiveShadow = false;
    shellMesh.frustumCulled = false;
    shellMesh.visible = false;
    object.getWorldPosition(_v);
    this._dynamics.push({
      object,
      shell: shellMesh,
      accumU,
      accum: 0,
      cooldown: 0,
      lastX: _v.x,
      lastZ: _v.z,
      footRadius,
      lumpY,
      shedSpeed,
      accumSeconds,
    });
  }

  /**
   * Track the football: a sphere shell synced (not parented) to the rolling
   * group — parenting would inherit the GLB's import scale.
   * @param {THREE.Object3D} object the ball group (world transform)
   * @param {number} radius world radius of the ball
   */
  trackBall(object, radius) {
    const { mat, accumU } = this.#makeDynamicMaterial(0.05);
    const geom = new THREE.SphereGeometry(radius * 1.01, 18, 12);
    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = "snowShell_ball";
    this.scene.add(mesh);
    this.#addDynamic(object, mesh, accumU, {
      footRadius: radius * 0.9,
      lumpY: radius,
    });
    const entry = this._dynamics[this._dynamics.length - 1];
    entry.sync = true; // copy position+quaternion from the object each frame
  }

  /**
   * Track a rigid dynamic mesh (pushable brick pile): the shell reuses the
   * mesh's own geometry as a child, so it inherits the placement scale and
   * matches the visible prop exactly.
   * @param {THREE.Mesh} mesh
   */
  trackMesh(mesh) {
    const { mat, accumU } = this.#makeDynamicMaterial(0.06);
    const shell = new THREE.Mesh(mesh.geometry, mat);
    shell.name = `snowShell_${mesh.name}`;
    mesh.add(shell);
    mesh.geometry.computeBoundingBox?.();
    const bb = mesh.geometry.boundingBox;
    const sx = (bb ? bb.max.x - bb.min.x : 0.6) * (mesh.scale?.x ?? 1);
    const sy = (bb ? bb.max.y - bb.min.y : 0.4) * (mesh.scale?.y ?? 1);
    this.#addDynamic(mesh, shell, accumU, {
      footRadius: Math.max(0.25, sx * 0.4),
      lumpY: Math.max(0.2, sy * 0.8),
    });
  }

  /**
   * Track wandering animals: parts are rigid within the rig group (whole-group
   * wander + bob), so all part geometries bake into ONE rig-local shell.
   * @param {Array<{group: THREE.Group}>} animals AnimatedProps.animals
   */
  trackAnimalRigs(animals) {
    for (const a of animals) {
      const group = a?.group;
      if (!group) continue;
      group.updateMatrixWorld(true);
      _inv.copy(group.matrixWorld).invert();
      const out = { positions: [], normals: [], indices: [] };
      group.traverse((o) => {
        if (!o.isMesh) return;
        _m.multiplyMatrices(_inv, o.matrixWorld); // part → rig-local
        bakeGeometry(o.geometry, _m, out);
      });
      if (!out.indices.length) continue;
      const { mat, accumU } = this.#makeDynamicMaterial(0.04);
      const shell = new THREE.Mesh(buildMergedGeometry(out), mat);
      shell.name = `snowShell_${group.name}`;
      group.add(shell);
      // Animals pause only a few seconds between wanders — a fast dusting
      // (else snow never shows) that sheds at walking speed.
      this.#addDynamic(group, shell, accumU, {
        footRadius: 0.35,
        lumpY: 0.4,
        shedSpeed: 0.25,
        accumSeconds: 3.5,
      });
    }
  }

  /** Per-frame: static visibility, dynamic accumulate/shed state machines. */
  update(delta, coverage) {
    if (this._static) {
      const visible = coverage > 0.01;
      if (visible !== this._staticVisible) {
        this._staticVisible = visible;
        this._static.visible = visible;
      }
    }
    if (!this._dynamics.length || delta <= 0) return;
    const snowing = coverage > 0.3;
    for (const d of this._dynamics) {
      d.object.getWorldPosition(_v);
      if (d.sync) {
        d.shell.position.copy(_v);
        d.object.getWorldQuaternion(d.shell.quaternion);
      }
      const dx = _v.x - d.lastX;
      const dz = _v.z - d.lastZ;
      d.lastX = _v.x;
      d.lastZ = _v.z;
      const speed = Math.hypot(dx, dz) / delta;
      d.cooldown = Math.max(0, d.cooldown - delta);

      if (speed > d.shedSpeed && d.accum > 0) {
        // Moving fast: shed. A thick crust bursts into ground lumps once per
        // cooldown; whatever remains wipes off quickly as the object keeps
        // moving (a rolling ball trails its snow away).
        if (d.accum >= SHED_MIN_ACCUM && d.cooldown <= 0 && this.piles) {
          this.piles.dropLumps(_v.x, _v.z, _v.y + d.lumpY, {
            count: 3 + Math.round(d.accum * 4),
            spread: d.footRadius + 0.25,
            size: 0.1 + d.accum * 0.08,
          });
          d.cooldown = SHED_COOLDOWN;
        }
        d.accum = Math.max(0, d.accum - delta * 2.5);
      } else if (snowing && speed < REST_SPEED) {
        d.accum = Math.min(1, d.accum + delta / d.accumSeconds);
      } else if (speed > REST_SPEED) {
        // Nudged around below shed speed: snow slowly dusts off.
        d.accum = Math.max(0, d.accum - delta * 0.4);
      }
      d.accumU.value = d.accum;
      d.shell.visible = d.accum > 0.02 && coverage > 0.05;
    }
  }
}

const _v = new THREE.Vector3();
const _m = new THREE.Matrix4();
const _inv = new THREE.Matrix4();
const _nm = new THREE.Matrix3();
