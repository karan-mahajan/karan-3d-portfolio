import * as THREE from 'three/webgpu';

/**
 * FootIK — analytic two-bone IK that plants each foot vertically onto the
 * terrain so the character reads as standing ON the ground rather than hovering
 * a few cm above it (the animation clips leave the feet ~0.6cm/6.5cm/21cm high
 * for walk/run/crouch after the in-place root pin). Phase 2 of the grounding
 * work; the contact shadow (Effects/ContactShadow.js) is Phase 1.
 *
 * Scope (deliberately conservative): the ankle target only moves VERTICALLY
 * (no x/z change → introduces no horizontal foot slide), the hips stay pinned
 * (no pelvis drop), and the foot bone tilts toward the slope normal within a
 * clamped angle. Driven by an external `weight` so it fades out when airborne.
 *
 * Math: reconstruct the desired knee position on the CURRENT bend side (so the
 * knee can never pop backward regardless of leg), then align the upper leg to
 * the new knee and the lower leg to the target with shortest-arc rotations
 * (setFromUnitVectors) — no manual angle-sign bookkeeping.
 *
 * Avaturn rig = bare Mixamo bone names (see Character.js retarget). If any leg
 * bone is missing, `valid` stays false and solve() is a no-op — the character
 * animates exactly as before.
 */

const EPS = 1e-4;
// Keep the lowest foot point this far above the sampled ground — small, so the
// sole reads planted without clipping into terrain micro-noise.
const CONTACT_LIFT = 0.02;
// Snow surface rise the ground shader applies (terrainSnowDrift in GlbV3World).
// Exported: Character lifts the whole body by the same amount so the player
// stands ON the blanket — feet-only lift folds the knees by exactly this.
export const SNOW_RISE = 0.16;
// Cap how far the foot tilts toward a slope normal, so steep ground doesn't
// twist the ankle into a break.
const MAX_FOOT_TILT = THREE.MathUtils.degToRad(20);
const UP = new THREE.Vector3(0, 1, 0);

const LEGS = [
  { up: 'LeftUpLeg', lo: 'LeftLeg', foot: 'LeftFoot', toe: 'LeftToeBase' },
  { up: 'RightUpLeg', lo: 'RightLeg', foot: 'RightFoot', toe: 'RightToeBase' },
];

// Module scratch — solve() runs every frame, so avoid per-frame allocation.
const _a = new THREE.Vector3();
const _b = new THREE.Vector3();
const _c = new THREE.Vector3();
const _toe = new THREE.Vector3();
const _t = new THREE.Vector3();
const _u = new THREE.Vector3();
const _bend = new THREE.Vector3();
const _n = new THREE.Vector3();
const _bp = new THREE.Vector3();
const _v1 = new THREE.Vector3();
const _v2 = new THREE.Vector3();
const _dirOld = new THREE.Vector3();
const _dirNew = new THREE.Vector3();
const _normal = new THREE.Vector3();
const _qDelta = new THREE.Quaternion();
const _qFull = new THREE.Quaternion();
const _qWorld = new THREE.Quaternion();
const _qParent = new THREE.Quaternion();

export class FootIK {
  /** @param {THREE.Object3D} meshRoot  the avatar root holding the skeleton */
  constructor(meshRoot) {
    this.valid = false;
    this.legs = [];
    this.meshRoot = meshRoot ?? null;
    if (!meshRoot) return;

    for (const spec of LEGS) {
      const hip = meshRoot.getObjectByName(spec.up);
      const knee = meshRoot.getObjectByName(spec.lo);
      const ankle = meshRoot.getObjectByName(spec.foot);
      const toe = meshRoot.getObjectByName(spec.toe);
      if (!hip || !knee || !ankle) {
        console.warn('[FootIK] leg chain not resolved — IK disabled:', spec);
        return;
      }
      this.legs.push({ hip, knee, ankle, toe: toe ?? ankle });
    }
    this.valid = true;
  }

  /**
   * @param {{ heightAt:(x:number,z:number)=>number }} terrain
   * @param {number} snowCoverage  0..1 — adds the snow surface rise
   * @param {number} weight        0..1 — overall blend (fade to 0 airborne)
   */
  solve(terrain, snowCoverage = 0, weight = 1) {
    if (!this.valid || !terrain || weight <= 0.001) return;
    // The mixer set bone LOCAL transforms this frame but the renderer hasn't
    // refreshed world matrices yet — do it so the reads below are current.
    this.meshRoot.updateWorldMatrix(true, true);
    const snowLift = snowCoverage * SNOW_RISE;
    for (const leg of this.legs) this.#solveLeg(leg, terrain, snowLift, weight);
  }

  #solveLeg(leg, terrain, snowLift, weight) {
    const { hip, knee, ankle, toe } = leg;
    hip.getWorldPosition(_a);
    knee.getWorldPosition(_b);
    ankle.getWorldPosition(_c);
    toe.getWorldPosition(_toe);

    // How far the lowest foot point must move to sit on the ground beneath it.
    const footLowY = Math.min(_c.y, _toe.y);
    const groundY = terrain.heightAt(_c.x, _c.z) + snowLift + CONTACT_LIFT;
    const deltaY = (groundY - footLowY) * weight;
    if (Math.abs(deltaY) < EPS) return;

    _t.copy(_c);
    _t.y += deltaY; // purely vertical ankle target

    const lab = _a.distanceTo(_b);
    const lcb = _b.distanceTo(_c);
    let d = _a.distanceTo(_t);
    d = Math.min(Math.max(d, EPS), lab + lcb - EPS);

    // Bend-plane normal from the CURRENT pose, so the reconstructed knee stays
    // on the side the leg already bends (no back-knee).
    _v1.copy(_b).sub(_a); // a->b
    _v2.copy(_c).sub(_a); // a->c
    _n.crossVectors(_v1, _v2);
    if (_n.lengthSq() < 1e-8) return; // straight leg — nothing to solve
    _n.normalize();

    _u.copy(_t).sub(_a).divideScalar(d); // unit a->t
    _bend.crossVectors(_n, _u);
    if (_bend.lengthSq() < 1e-8) return;
    _bend.normalize();
    if (_bend.dot(_v1) < 0) _bend.negate(); // point toward current knee

    // Desired knee position b' (law of cosines along a->t).
    const x = (d * d + lab * lab - lcb * lcb) / (2 * d);
    const h = Math.sqrt(Math.max(0, lab * lab - x * x));
    _bp.copy(_a).addScaledVector(_u, x).addScaledVector(_bend, h);

    // Hip: rotate upper leg from (a->b) onto (a->b').
    _dirOld.copy(_b).sub(_a).normalize();
    _dirNew.copy(_bp).sub(_a).normalize();
    _qDelta.setFromUnitVectors(_dirOld, _dirNew);
    this.#applyWorldDelta(hip, _qDelta);
    hip.updateWorldMatrix(false, true); // refresh knee + ankle

    // Knee: rotate lower leg from (b->c) onto (b->t); lands the ankle on t.
    knee.getWorldPosition(_b);
    ankle.getWorldPosition(_c);
    _dirOld.copy(_c).sub(_b).normalize();
    _dirNew.copy(_t).sub(_b).normalize();
    _qDelta.setFromUnitVectors(_dirOld, _dirNew);
    this.#applyWorldDelta(knee, _qDelta);
    knee.updateWorldMatrix(false, true);

    // Foot: tilt the sole toward the slope normal (clamped, weighted).
    this.#tiltFoot(ankle, terrain, weight);
    ankle.updateWorldMatrix(false, true);
  }

  #tiltFoot(ankle, terrain, weight) {
    ankle.getWorldPosition(_c);
    const e = 0.3;
    _normal
      .set(
        terrain.heightAt(_c.x - e, _c.z) - terrain.heightAt(_c.x + e, _c.z),
        2 * e,
        terrain.heightAt(_c.x, _c.z - e) - terrain.heightAt(_c.x, _c.z + e),
      )
      .normalize();

    _qFull.setFromUnitVectors(UP, _normal);
    const angle = 2 * Math.acos(Math.min(1, Math.abs(_qFull.w)));
    if (angle < 1e-4) return;
    let s = weight;
    if (angle > MAX_FOOT_TILT) s *= MAX_FOOT_TILT / angle;
    _qDelta.identity().slerp(_qFull, s);
    this.#applyWorldDelta(ankle, _qDelta);
  }

  /** Apply a world-space rotation delta to a bone, written back as local. */
  #applyWorldDelta(bone, qDelta) {
    bone.getWorldQuaternion(_qWorld);
    _qWorld.premultiply(qDelta); // newWorld = qDelta * oldWorld
    bone.parent.getWorldQuaternion(_qParent).invert();
    bone.quaternion.copy(_qParent).multiply(_qWorld); // local = parent⁻¹·world
  }
}
