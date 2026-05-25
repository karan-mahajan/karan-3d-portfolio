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
    // Player.update writes this each frame so wading through ocean water
    // slows the character down without forking the speed constants.
    this.speedMultiplier = 1.0;

    // Mobile joystick intent. UI/UIController writes this every move event;
    // sample() reads it as an alternative to WASD. `active` is true while
    // the joystick thumb is offset from centre (any non-zero direction).
    this.mobileIntent = { x: 0, z: 0, active: false };
    this.mobileRunning = false;

    this._onDown = (e) => {
      if (e.repeat) return;
      this.keys.add(e.code);
    };
    this._onUp = (e) => this.keys.delete(e.code);
    window.addEventListener('keydown', this._onDown);
    window.addEventListener('keyup', this._onUp);
    window.addEventListener('blur', () => this.keys.clear());
  }

  /** Touch UI writes the joystick state here. `x` is right-positive, `z` is
   *  forward-positive (already negated from screen-Y by the caller). The
   *  flag is checked by sample() — when active, joystick overrides WASD. */
  setMobileIntent({ x = 0, z = 0, running = false } = {}) {
    this.mobileIntent.x = x;
    this.mobileIntent.z = z;
    this.mobileIntent.active = (x !== 0 || z !== 0);
    this.mobileRunning = !!running && this.mobileIntent.active;
  }

  get isRunning() {
    if (this.paused || this.isCrouching) return false;
    if (this.mobileRunning) return true;
    return this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
  }

  get isJumping() {
    return !this.paused && this.keys.has('Space');
  }

  get isCrouching() {
    // Z chosen over Ctrl: Ctrl+W closes the browser tab, which made the
    // intended crouch-walk-forward combo destructive.
    return !this.paused && this.keys.has('KeyZ');
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
      // Joystick takes precedence when keyboard intent is zero. The intent
      // vector is later normalized, so passing the raw fractional joystick
      // values is fine — direction is preserved, magnitude is discarded.
      if (this.mobileIntent.active && x === 0 && z === 0) {
        x = this.mobileIntent.x;
        z = this.mobileIntent.z;
      }
    }

    // Single-direction tags so the animation state machine can choose a
    // matching clip (backwards walk, sidestep) and skip the yaw turn.
    // Mobile joystick is continuous direction — these stay false unless
    // the player is using WASD.
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

    const baseSpeed = this.isCrouching
      ? PlayerController.WALK_SPEED * 0.45
      : this.isRunning
      ? PlayerController.RUN_SPEED
      : PlayerController.WALK_SPEED;
    const speed = baseSpeed * this.speedMultiplier;

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
