import * as THREE from 'three';

/**
 * Keyboard input + camera-relative movement intent.
 * Pure logic — no physics yet (Rapier lands in Step 7).
 */
export class PlayerController {
  static WALK_SPEED = 4;
  static RUN_SPEED = 8;
  static TURN_LERP = 0.18;

  constructor(playerCamera) {
    this.playerCamera = playerCamera;
    this.keys = new Set();
    this.intent = new THREE.Vector3();
    this.forward = new THREE.Vector3();
    this.right = new THREE.Vector3();
    this.paused = false; // when true, sample() returns a "no movement" reading

    this._onDown = (e) => {
      if (e.repeat) return;
      this.keys.add(e.code);
    };
    this._onUp = (e) => this.keys.delete(e.code);
    window.addEventListener('keydown', this._onDown);
    window.addEventListener('keyup', this._onUp);
    window.addEventListener('blur', () => this.keys.clear());
  }

  get isRunning() {
    return !this.paused && (this.keys.has('ShiftLeft') || this.keys.has('ShiftRight'));
  }

  get isJumping() {
    return !this.paused && this.keys.has('Space');
  }

  /**
   * Computes desired velocity in world space, given the camera orientation.
   * Returns { velocity, speed, moving, facing } — caller integrates position.
   */
  sample(delta) {
    let x = 0;
    let z = 0;
    let w = false, s = false, a = false, d = false;
    if (!this.paused) {
      w = this.keys.has('KeyW') || this.keys.has('ArrowUp');
      s = this.keys.has('KeyS') || this.keys.has('ArrowDown');
      a = this.keys.has('KeyA') || this.keys.has('ArrowLeft');
      d = this.keys.has('KeyD') || this.keys.has('ArrowRight');
      if (w) z += 1;
      if (s) z -= 1;
      if (a) x -= 1;
      if (d) x += 1;
    }

    // Single-direction tags so the animation state machine can choose a
    // matching clip (backwards walk, sidestep) and skip the yaw turn.
    const pureBackward = s && !w && !a && !d;
    const pureRight = d && !w && !s && !a;
    const pureLeft  = a && !w && !s && !d;

    this.playerCamera.getGroundForward(this.forward);
    this.playerCamera.getGroundRight(this.right);

    this.intent.set(0, 0, 0);
    if (x !== 0 || z !== 0) {
      this.intent
        .copy(this.forward)
        .multiplyScalar(z)
        .addScaledVector(this.right, x)
        .normalize();
    }

    const speed = this.isRunning
      ? PlayerController.RUN_SPEED
      : PlayerController.WALK_SPEED;

    return {
      velocity: this.intent.clone().multiplyScalar(speed),
      speed,
      moving: this.intent.lengthSq() > 1e-6,
      facing: this.intent.lengthSq() > 1e-6 ? Math.atan2(this.intent.x, this.intent.z) : null,
      pureBackward,
      pureRight,
      pureLeft,
      delta,
    };
  }

  dispose() {
    window.removeEventListener('keydown', this._onDown);
    window.removeEventListener('keyup', this._onUp);
  }
}
