import * as THREE from "three/webgpu";
import {
  attribute, float, mx_noise_float, normalLocal,
  positionLocal, smoothstep, vec3, vec4,
} from "three/tsl";
import { snowCoverage, snowColor, snowEmissive } from "../World/SnowState.js";
import { worldLitOutput, worldShadowCatcher } from "../World/WorldLight.js";
import { snowTrailValueAt } from "./SnowTrail.js";

/**
 * SnowPiles — dome-shaped snow: open-ground DRIFTS plus a pool of SHED LUMPS.
 *
 * Drifts are seeded by App on open grass and grow in staggered (per-instance
 * threshold vs snowCoverage), like the ground patches. Lumps are spawned by
 * SnowShells when a snowed-over dynamic object (football, brick, animal)
 * moves: they drop from the object with a short fall animation, land on the
 * terrain and PERSIST until the melt drains them (low thresholds → they're
 * among the last snow to go).
 *
 * Conforming snow on props lives in SnowShells, NOT here — domes only ever
 * sit on open ground where a mound shape is what real drifts look like.
 */

const LUMP_POOL = 96;

function makeDomeGeometry(count, threshFn) {
  const geom = new THREE.SphereGeometry(1, 12, 7, 0, Math.PI * 2, 0, Math.PI / 2);
  geom.scale(1, 0.62, 1);
  const thresh = new Float32Array(count);
  for (let i = 0; i < count; i++) thresh[i] = threshFn(i);
  geom.setAttribute("aThresh", new THREE.InstancedBufferAttribute(thresh, 1));
  return geom;
}

function makeSnowDomeMaterial() {
  const mat = new THREE.MeshLambertNodeMaterial({ fog: false });
  mat.name = "snowPiles";

  const aThresh = attribute("aThresh", "float");
  const grow = smoothstep(aThresh, aThresh.add(0.35), snowCoverage);
  // Lumpy silhouette — noise keyed off local position + the per-instance
  // threshold (as a seed) so no two domes share a profile. positionWorld
  // can't be used inside positionNode (it would be self-referential).
  const lump = mx_noise_float(
    positionLocal.mul(2.2).add(aThresh.mul(53.0)),
  ).mul(0.5).add(0.5);
  const displaced = positionLocal.add(normalLocal.mul(lump.mul(0.35)));
  // Grow vertically from the contact plane; footprint widens with growth
  // too (0.55 → 1.0) so a young drift is a low wide dusting.
  const swell = grow.mul(0.45).add(0.55);
  mat.positionNode = displaced.mul(vec3(swell, grow.max(0.001), swell));

  const albedo = snowColor(vec3(1, 1, 1), float(1)); // mask 1 → pure shaded snow
  const emissive = snowEmissive(grow); // sparkle fades out with the dome
  const albedo4 = vec4(albedo, 1.0);
  mat.colorNode = albedo4;
  const catchedShadow = float(1).toVar();
  mat.receivedShadowNode = worldShadowCatcher(catchedShadow);
  mat.outputNode = worldLitOutput(albedo4, emissive, catchedShadow);
  return mat;
}

export class SnowPiles {
  /**
   * @param {THREE.Scene} scene
   * @param {Array<{x:number,y:number,z:number,r:number,h:number}>} anchors
   * @param {{ heightAt:(x:number,z:number)=>number }} [terrain] for lump landing
   */
  constructor(scene, anchors, terrain = null) {
    this.scene = scene;
    this.terrain = terrain;
    this._visible = false;
    this._falls = []; // active lump drop animations
    this._lumpCursor = 0;
    this.#buildDrifts(anchors);
    this.#buildLumps();
  }

  #buildDrifts(anchors) {
    const count = anchors.length;
    if (!count) {
      this._drifts = null;
      return;
    }
    const geom = makeDomeGeometry(count, () => 0.15 + Math.random() * 0.6);
    const mesh = new THREE.InstancedMesh(geom, makeSnowDomeMaterial(), count);
    // Instances span the whole island; per-instance culling doesn't exist, so
    // skip whole-mesh culling rather than risk it vanishing at screen edges.
    mesh.frustumCulled = false;
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    mesh.name = "snowDrifts";

    const m = new THREE.Matrix4();
    const q = new THREE.Quaternion();
    const up = new THREE.Vector3(0, 1, 0);
    const p = new THREE.Vector3();
    const s = new THREE.Vector3();
    // Per-drift base transform + crush state, so walking through a drift can
    // squash it down (trail-driven) and let it recover as snowfall refills.
    this._driftData = [];
    for (let i = 0; i < count; i++) {
      const a = anchors[i];
      const yaw = Math.random() * Math.PI * 2;
      q.setFromAxisAngle(up, yaw);
      // Sink slightly so the rim meets the surface instead of hovering.
      p.set(a.x, a.y - a.h * 0.12, a.z);
      s.set(a.r, a.h, a.r);
      m.compose(p, q, s);
      mesh.setMatrixAt(i, m);
      this._driftData.push({
        x: a.x, y: a.y - a.h * 0.12, z: a.z,
        r: a.r, h: a.h, yaw, crush: 0,
      });
    }
    mesh.instanceMatrix.needsUpdate = true;
    mesh.visible = false; // hidden until snow exists — zero cost while clear
    this._drifts = mesh;
    this.scene.add(mesh);
  }

  #buildLumps() {
    // Low thresholds: lumps stay solid through the storm and are among the
    // LAST snow to melt — shed snow lying on the ground outlives the blanket.
    const geom = makeDomeGeometry(LUMP_POOL, () => 0.03 + Math.random() * 0.09);
    const mesh = new THREE.InstancedMesh(geom, makeSnowDomeMaterial(), LUMP_POOL);
    mesh.frustumCulled = false;
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    mesh.name = "snowShedLumps";
    const zero = new THREE.Matrix4().makeScale(0, 0, 0);
    for (let i = 0; i < LUMP_POOL; i++) mesh.setMatrixAt(i, zero);
    mesh.instanceMatrix.needsUpdate = true;
    mesh.visible = false;
    this._lumps = mesh;
    this.scene.add(mesh);
  }

  /**
   * Shed snow off a moving object: spawn `count` small lumps around (x, z)
   * that fall from `yTop` to the terrain and persist until the melt.
   * @param {number} x
   * @param {number} z
   * @param {number} yTop  drop start height (object's snow line)
   * @param {{count?:number, spread?:number, size?:number}} [o]
   */
  dropLumps(x, z, yTop, { count = 4, spread = 0.4, size = 0.14 } = {}) {
    if (!this._lumps) return;
    for (let n = 0; n < count; n++) {
      const idx = this._lumpCursor;
      this._lumpCursor = (this._lumpCursor + 1) % LUMP_POOL;
      const ang = Math.random() * Math.PI * 2;
      const dist = Math.random() * spread;
      const lx = x + Math.cos(ang) * dist;
      const lz = z + Math.sin(ang) * dist;
      const groundY = this.terrain ? this.terrain.heightAt(lx, lz) : 0;
      const r = size * (0.6 + Math.random() * 0.8);
      // Drop the existing fall on this slot if the ring lapped it.
      this._falls = this._falls.filter((f) => f.idx !== idx);
      this._falls.push({
        idx,
        x: lx,
        z: lz,
        y0: yTop,
        y1: groundY + r * 0.05,
        r,
        h: r * (0.55 + Math.random() * 0.25),
        yaw: Math.random() * Math.PI * 2,
        t: 0,
        dur: 0.3 + Math.random() * 0.2,
      });
    }
    this._lumps.visible = true;
  }

  /** Per-frame: visibility gates, trample-crush, lump drop animations. */
  update(delta, coverage, playerPos = null) {
    if (this._drifts) {
      const visible = coverage > 0.01;
      if (visible !== this._visible) {
        this._visible = visible;
        this._drifts.visible = visible;
      }
      if (visible && playerPos) this.#crushDrifts(delta, playerPos);
    }
    if (this._lumps) {
      // Lumps render while any could still be visible (coverage above the
      // smallest threshold) or while a drop is mid-air.
      this._lumps.visible = coverage > 0.02 || this._falls.length > 0;
      if (this._falls.length) this.#advanceFalls(delta);
    }
  }

  /**
   * Walking through a drift must leave a TRACE: drifts near the player read
   * the pressed-snow trail under their footprint and squash toward the ground
   * where it's been stamped, recovering as the trail refills with snowfall.
   * Only drifts within a small radius of the player are sampled — far ones
   * can't be changing.
   */
  #crushDrifts(delta, playerPos) {
    let dirty = false;
    const k = Math.min(1, delta * 6); // smooth approach, no popping
    for (let i = 0; i < this._driftData.length; i++) {
      const d = this._driftData[i];
      const dx = d.x - playerPos.x;
      const dz = d.z - playerPos.z;
      const near = dx * dx + dz * dz < 144; // 12 m
      // Far drifts still need to RECOVER if they were crushed earlier.
      if (!near && d.crush < 0.005) continue;
      // Sample the trail across the drift footprint (centre + 4 spokes) so a
      // path clipping the edge still dents that side's worth of height.
      const e = d.r * 0.55;
      const t = Math.max(
        snowTrailValueAt(d.x, d.z),
        snowTrailValueAt(d.x + e, d.z),
        snowTrailValueAt(d.x - e, d.z),
        snowTrailValueAt(d.x, d.z + e),
        snowTrailValueAt(d.x, d.z - e),
      );
      const target = t * 0.85; // fully trampled → 15% height stub
      if (Math.abs(target - d.crush) < 0.005) continue;
      d.crush += (target - d.crush) * k;
      _q.setFromAxisAngle(_up, d.yaw);
      _p.set(d.x, d.y, d.z);
      const squash = 1 - d.crush;
      _s.set(d.r * (1 + d.crush * 0.18), d.h * squash, d.r * (1 + d.crush * 0.18));
      _m.compose(_p, _q, _s);
      this._drifts.setMatrixAt(i, _m);
      dirty = true;
    }
    if (dirty) this._drifts.instanceMatrix.needsUpdate = true;
  }

  #advanceFalls(delta) {
    const m = _m;
    const q = _q;
    const p = _p;
    const s = _s;
    for (let i = this._falls.length - 1; i >= 0; i--) {
      const f = this._falls[i];
      f.t = Math.min(f.t + delta, f.dur);
      const k = f.t / f.dur;
      const y = f.y0 + (f.y1 - f.y0) * k * k; // gravity ease-in
      // Squash on landing so the lump reads as soft snow, not a bouncing ball.
      const landed = k >= 1;
      const squashY = landed ? 0.8 : 1;
      const squashXZ = landed ? 1.15 : 1;
      q.setFromAxisAngle(_up, f.yaw);
      p.set(f.x, y, f.z);
      s.set(f.r * squashXZ, f.h * squashY, f.r * squashXZ);
      m.compose(p, q, s);
      this._lumps.setMatrixAt(f.idx, m);
      if (landed) this._falls.splice(i, 1);
    }
    this._lumps.instanceMatrix.needsUpdate = true;
  }
}

const _m = new THREE.Matrix4();
const _q = new THREE.Quaternion();
const _p = new THREE.Vector3();
const _s = new THREE.Vector3();
const _up = new THREE.Vector3(0, 1, 0);
