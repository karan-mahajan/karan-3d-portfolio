import * as THREE from 'three';
import CameraControls from 'camera-controls';

// Tree-shake-safe subset for camera-controls.
const subsetOfTHREE = {
  Vector2: THREE.Vector2,
  Vector3: THREE.Vector3,
  Vector4: THREE.Vector4,
  Quaternion: THREE.Quaternion,
  Matrix4: THREE.Matrix4,
  Spherical: THREE.Spherical,
  Box3: THREE.Box3,
  Sphere: THREE.Sphere,
  Raycaster: THREE.Raycaster,
};
CameraControls.install({ THREE: subsetOfTHREE });

const HEAD_HEIGHT = 1.2;

/**
 * Smooth third-person orbital camera.
 *
 * Camera-controls is great at handling input + smoothing, but its built-in
 * "follow" semantics don't work the way we want — `setTarget` keeps the
 * camera in place (just rotates), and `moveTo` accumulates a focal offset.
 * Both feel wrong for a third-person rig.
 *
 * Instead we let camera-controls handle ONLY input (drag → azimuth/polar,
 * scroll → distance, with its own damping) and read those smoothed values
 * each frame. We compute the camera position ourselves from the player's
 * head + spherical offset — guaranteed to translate with the player.
 */
export class PlayerCamera {
  constructor(camera, canvas) {
    this.camera = camera;
    this.controls = new CameraControls(camera, canvas);

    this.controls.minDistance = 3.5;
    this.controls.maxDistance = 10;

    this.controls.azimuthRotateSpeed = 0.55;
    this.controls.polarRotateSpeed = 0.35;
    this.controls.minPolarAngle = Math.PI * 0.18;
    this.controls.maxPolarAngle = Math.PI * 0.48;

    this.controls.smoothTime = 0.16;
    this.controls.draggingSmoothTime = 0.1;

    this.controls.truckSpeed = 0;
    this.controls.dollyToCursor = false;

    // Seed initial state. Closer + lower than a pure top-down — behind the
    // player at roughly shoulder height so the sky shows above the billboards
    // and the character fills more of the frame.
    // distance≈5.6, polar≈77° (near-horizontal), azimuth=π (behind).
    this.controls.setLookAt(0, 2.45, -5.5, 0, HEAD_HEIGHT, 0, false);

    this._target = new THREE.Vector3(0, HEAD_HEIGHT, 0);
    this._tmpOffset = new THREE.Vector3();
    this.locked = false; // when true, update() doesn't move the camera (used by zoom)
  }

  /** Set the orbit pivot to the player's head. Camera position derives from this in update(). */
  follow(position) {
    this._target.set(position.x, position.y + HEAD_HEIGHT, position.z);
  }

  /** Forward vector on the ground plane, from camera azimuth. */
  getGroundForward(out = new THREE.Vector3()) {
    this.camera.getWorldDirection(out);
    out.y = 0;
    if (out.lengthSq() < 1e-6) out.set(0, 0, -1);
    else out.normalize();
    return out;
  }

  /** Right vector on the ground plane. */
  getGroundRight(out = new THREE.Vector3()) {
    this.getGroundForward(out);
    out.cross(new THREE.Vector3(0, 1, 0)).normalize();
    return out;
  }

  /**
   * 1. Let camera-controls process input → updates azimuth/polar/distance.
   * 2. Override camera.position = playerHead + sphericalToCartesian(d, az, polar).
   * 3. Look at playerHead.
   *
   * Camera-controls writes camera.position during step 1 — step 2 overrides it.
   * Internal target/sphericalEnd may drift from what we render, but we never
   * read those, so it doesn't matter.
   */
  update(delta) {
    if (this.locked) return; // GSAP zoom drives camera directly while locked.
    this.controls.update(delta);

    const distance = this.controls.distance;
    const azimuth = this.controls.azimuthAngle;
    const polar = this.controls.polarAngle;

    const sinPolar = Math.sin(polar);
    this._tmpOffset.set(
      distance * sinPolar * Math.sin(azimuth),
      distance * Math.cos(polar),
      distance * sinPolar * Math.cos(azimuth),
    );

    this.camera.position.copy(this._target).add(this._tmpOffset);
    this.camera.lookAt(this._target);
  }

  /**
   * Used after a GSAP zoom-out completes — re-derive the spherical state from
   * wherever the camera currently is, so the orbit picks up smoothly.
   */
  resync() {
    const offset = this.camera.position.clone().sub(this._target);
    const distance = offset.length();
    const polar = Math.acos(THREE.MathUtils.clamp(offset.y / distance, -1, 1));
    const azimuth = Math.atan2(offset.x, offset.z);
    this.controls.distance = distance;
    this.controls.azimuthAngle = azimuth;
    this.controls.polarAngle = polar;
  }
}
