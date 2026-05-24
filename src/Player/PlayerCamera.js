import CameraControls from "camera-controls";
import * as THREE from "three";

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

    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 12;

    this.controls.azimuthRotateSpeed = 0.55;
    this.controls.polarRotateSpeed = 0.35;
    this.controls.minPolarAngle = Math.PI * 0.18;
    this.controls.maxPolarAngle = Math.PI * 0.48;

    this.controls.smoothTime = 0.16;
    this.controls.draggingSmoothTime = 0.1;

    this.controls.truckSpeed = 0;
    this.controls.dollyToCursor = false;

    // Seed initial state. Pinned to the minimum zoom distance and the most
    // horizontal polar angle — but azimuth=0 places the camera in FRONT of
    // the player so we see the character's face, with the welcome board
    // behind the camera (out of frame).
    // distance≈2.5, polar≈85° (nearly flat), azimuth=0 (in front).
    this.controls.setLookAt(0, 1.66, -3.94, 0, HEAD_HEIGHT, 0, false);

    this._target = new THREE.Vector3(0, HEAD_HEIGHT, 0);
    this._tmpOffset = new THREE.Vector3();
    this.locked = false; // when true, update() doesn't move the camera (used by zoom)

    // Dynamic movement-zoom multiplier — applied on top of the user's
    // own controls.distance (preserved). 1.0 = idle, 1.10 = walking,
    // 1.18 = running. THREE.MathUtils.damp gives a frame-rate-independent
    // exponential smoothing with a time-constant of `1/lambda` seconds.
    // Lambda = 3 → ~95% convergence in 1 second, which matches the
    // cinematic "weighted but not slow" feel.
    this._movementZoomFactor = 1.0;
    this._movementZoomTarget = 1.0;

    // Sprint polar tilt — adds a small extra pitch-down when running so
    // the character is framed slightly higher on screen during a sprint.
    // Same 1-second damping as the zoom.
    this._polarTilt = 0;
    this._polarTiltTarget = 0;
  }

  /** Tell the camera what the player is doing this frame so we can
   *  smoothly zoom out a bit while moving (and a bit more while running). */
  setMovementState({ moving = false, running = false } = {}) {
    if (running && moving) {
      this._movementZoomTarget = 1.18;
      this._polarTiltTarget = 0.03;
    } else if (moving) {
      this._movementZoomTarget = 1.10;
      this._polarTiltTarget = 0;
    } else {
      this._movementZoomTarget = 1.0;
      this._polarTiltTarget = 0;
    }
  }

  /** Set the orbit pivot to the player's head. Camera position derives from this in update(). */
  follow(position) {
    // Clamp the orbit target above the water surface (WATER_LEVEL_Y=0).
    // Without this, wading drops target.y below sea level and certain
    // azimuths push the camera through the back of the double-sided
    // transparent ocean plane (Effects/Water.js).
    this._target.set(
      position.x,
      Math.max(position.y + HEAD_HEIGHT, 0.4),
      position.z,
    );
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

    // Cinematic zoom: lambda=3 → ~95% convergence in 1 second, so the
    // zoom-out feels smooth and gradual when starting to walk / sprint
    // and slowly relaxes back when stopping. damp() is frame-rate
    // independent so this looks identical at 60 / 120 / 144 fps.
    this._movementZoomFactor = THREE.MathUtils.damp(
      this._movementZoomFactor, this._movementZoomTarget, 3, delta,
    );
    this._polarTilt = THREE.MathUtils.damp(this._polarTilt, this._polarTiltTarget, 3, delta);

    const distance = this.controls.distance * this._movementZoomFactor;
    const azimuth = this.controls.azimuthAngle;
    // Clamp the tilted polar to the orbit's own min/max so the sprint
    // pitch can't push the camera through the ground or up past zenith.
    const polar = THREE.MathUtils.clamp(
      this.controls.polarAngle + this._polarTilt,
      this.controls.minPolarAngle,
      this.controls.maxPolarAngle,
    );

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
   * Temporarily zoom the orbit out by `factor` (1.10 = 10% farther). Called
   * by ActionPrompts when a performance animation starts so the player can
   * see the character do the thing. Re-entrant safe.
   */
  applyActionZoom(factor = 1.1) {
    if (this._actionZoomActive) return;
    this._actionZoomActive = true;
    this._savedActionDistance = this.controls.distance;
    const target = Math.min(this.controls.distance * factor, this.controls.maxDistance);
    this.controls.dollyTo(target, true);
  }

  releaseActionZoom() {
    if (!this._actionZoomActive) return;
    this._actionZoomActive = false;
    if (this._savedActionDistance !== undefined) {
      this.controls.dollyTo(this._savedActionDistance, true);
      this._savedActionDistance = undefined;
    }
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
