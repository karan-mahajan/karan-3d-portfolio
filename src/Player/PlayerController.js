import * as THREE from 'three/webgpu';

/**
 * Keyboard input + camera-relative movement intent.
 * Pure logic — no physics yet (Rapier lands in Step 7).
 */
export class PlayerController {
  // Tuned to sit just above the locomotion clips' measured natural paces
  // (walk 1.65 m/s, run 4.43 m/s — see Player.ANIM_NATURAL_SPEED) so the
  // animations play near 1× instead of being overdriven into a frantic
  // scramble. Raising these is fine, but keep them within ~20% of natural.
  static WALK_SPEED = 1.9;
  static RUN_SPEED = 5.0;
  // Speed ramps instead of snapping. The numbers keep controls responsive
  // while leaving enough pickup / release time for the animation blend to
  // read as weight instead of a hard velocity step.
  static ACCELERATION = 14;
  static DECELERATION = 18;
  // Extra authority while input direction changes, so W→A / W→S arcs feel
  // controlled without snapping the velocity vector sideways in one frame.
  static DIRECTION_CHANGE_ACCELERATION = 30;
  // Delta-based turn rate (rad/s). Replaces a fixed per-frame lerp factor so
  // turn smoothness is identical at 60 / 144 fps.
  static TURN_SPEED = 12;

  constructor(playerCamera) {
    this.playerCamera = playerCamera;
    this.keys = new Set();
    this.intent = new THREE.Vector3();
    this.forward = new THREE.Vector3();
    this.right = new THREE.Vector3();
    this.paused = false; // when true, sample() returns a "no movement" reading
    this._locked = false;
    this._virtualInput = null;
    this._virtualCancelledThisFrame = false;
    this._manualOverrideUntil = 0;
    // Player.update writes this each frame so wading through ocean water
    // slows the character down without forking the speed constants.
    this.speedMultiplier = 1.0;
    this.actionSpeedMultiplier = 1.0;

    // Smoothed speed magnitude (m/s). Ramped toward the target speed at
    // ACCEL / DECEL each frame so velocity has inertia.
    this._currentSpeed = 0;
    this._currentVelocity = new THREE.Vector3();
    this._targetVelocity = new THREE.Vector3();
    this._velocityDelta = new THREE.Vector3();
    // Last non-zero movement direction. Used during the deceleration tail
    // (input released, but _currentSpeed still > 0) so the character glides
    // forward in their last facing direction instead of dropping velocity
    // to zero the instant keys release.
    this._lastDirection = new THREE.Vector3(0, 0, 1);

    // Mobile joystick intent. UI/UIController writes this every move event;
    // sample() reads it as an alternative to WASD. `active` is true while
    // the joystick thumb is offset from centre (any non-zero direction).
    this.mobileIntent = { x: 0, z: 0, active: false };
    this.mobileRunning = false;

    this._onDown = (e) => {
      if (e.repeat) return;
      this.keys.add(e.code);
      if (this._virtualInput && isMovementCode(e.code)) {
        this.clearVirtualInput();
        this._virtualCancelledThisFrame = true;
        this._manualOverrideUntil = performance.now() + 300;
      }
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

  setVirtualInput({ forward = 0, strafe = 0, worldAngle = 0 } = {}) {
    this._virtualInput = { forward, strafe, worldAngle };
  }

  clearVirtualInput() {
    this._virtualInput = null;
  }

  lock() {
    this._locked = true;
    this.clearVirtualInput();
  }

  unlock() {
    this._locked = false;
  }

  get hasVirtualInput() {
    return this._virtualInput !== null;
  }

  get virtualInputCancelledThisFrame() {
    return this._virtualCancelledThisFrame || performance.now() < this._manualOverrideUntil;
  }

  get hasManualMovementInput() {
    return this.#hasManualMovementInput();
  }

  get isRunning() {
    if (this.paused || this._locked || this.isCrouching || this._virtualInput) return false;
    if (this.mobileRunning) return true;
    return this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
  }

  get isJumping() {
    return !this.paused && !this._locked && this.keys.has('Space');
  }

  get isCrouching() {
    // Z chosen over Ctrl: Ctrl+W closes the browser tab, which made the
    // intended crouch-walk-forward combo destructive.
    return !this.paused && !this._locked && this.keys.has('KeyZ');
  }

  /**
   * Computes desired velocity in world space, given the camera orientation.
   * Returns { velocity, speed, moving, facing } — caller integrates position.
   */
  sample(delta) {
    this._virtualCancelledThisFrame = false;
    let x = 0;
    let z = 0;
    let w = false, s = false, a = false, d = false;
    if (this.paused || this._locked) return this.#zeroSample(delta);

    w = this.keys.has('KeyW') || this.keys.has('ArrowUp');
    s = this.keys.has('KeyS') || this.keys.has('ArrowDown');
    a = this.keys.has('KeyA') || this.keys.has('ArrowLeft');
    d = this.keys.has('KeyD') || this.keys.has('ArrowRight');

    if (this._virtualInput && (w || s || a || d || this.mobileIntent.active)) {
      this.clearVirtualInput();
      this._virtualCancelledThisFrame = true;
      this._manualOverrideUntil = performance.now() + 300;
    }

    if (this._virtualInput) {
      const { forward, strafe, worldAngle } = this._virtualInput;
      const fs = Math.sin(worldAngle);
      const fc = Math.cos(worldAngle);
      this.intent.set(
        fs * forward + fc * strafe,
        0,
        fc * forward - fs * strafe,
      );
      const inputAmount = Math.min(1, this.intent.length());
      if (inputAmount > 1e-6) this.intent.normalize();
      return this.#resolveVelocity({
        delta,
        inputAmount,
        pureBackward: false,
        pureRight: false,
        pureLeft: false,
      });
    }

    if (w) z += 1;
    if (s) z -= 1;
    if (a) x -= 1;
    if (d) x += 1;
    // Joystick takes precedence when keyboard intent is zero. Preserve its
    // fractional magnitude so small thumb offsets produce a careful walk
    // instead of instantly normalizing to full speed.
    let inputAmount = Math.min(1, Math.hypot(x, z));
    if (this.mobileIntent.active && x === 0 && z === 0) {
      x = this.mobileIntent.x;
      z = this.mobileIntent.z;
      inputAmount = Math.min(1, Math.hypot(x, z));
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

    return this.#resolveVelocity({
      delta,
      inputAmount,
      pureBackward,
      pureRight,
      pureLeft,
    });
  }

  #resolveVelocity({ delta, inputAmount, pureBackward, pureRight, pureLeft }) {
    const baseSpeed = this.isCrouching
      ? PlayerController.WALK_SPEED * 0.45
      : this.isRunning
      ? PlayerController.RUN_SPEED
      : PlayerController.WALK_SPEED;

    // Ramp the whole velocity vector toward the target, not just the scalar
    // speed. That gives direction changes a short, readable arc instead of
    // instantly swapping the movement vector while the mesh yaw catches up.
    const hasInput = this.intent.lengthSq() > 1e-6;
    if (hasInput) this._lastDirection.copy(this.intent);

    const targetSpeed = hasInput
      ? baseSpeed * this.speedMultiplier * this.actionSpeedMultiplier * inputAmount
      : 0;
    this._targetVelocity.copy(this.intent).multiplyScalar(targetSpeed);

    const currentSpeed = this._currentVelocity.length();
    const changingDirection = hasInput
      && currentSpeed > 0.05
      && this._currentVelocity.dot(this._targetVelocity) < currentSpeed * targetSpeed * 0.65;
    const rate = hasInput
      ? changingDirection
        ? PlayerController.DIRECTION_CHANGE_ACCELERATION
        : PlayerController.ACCELERATION
      : PlayerController.DECELERATION;
    this._velocityDelta.copy(this._targetVelocity).sub(this._currentVelocity);
    const velocityDeltaLength = this._velocityDelta.length();
    const maxVelocityStep = rate * delta;
    if (velocityDeltaLength <= maxVelocityStep || velocityDeltaLength < 1e-6) {
      this._currentVelocity.copy(this._targetVelocity);
    } else {
      this._currentVelocity.addScaledVector(this._velocityDelta, maxVelocityStep / velocityDeltaLength);
    }

    const speed = this._currentVelocity.length();
    this._currentSpeed = speed;
    const direction = speed > 1e-6
      ? this._currentVelocity.clone().normalize()
      : this._lastDirection;
    // Threshold so the deceleration tail eventually flips to idle.
    const moving = speed > 0.05;

    return {
      velocity: this._currentVelocity.clone(),
      speed,
      moving,
      facing: moving ? Math.atan2(direction.x, direction.z) : null,
      pureBackward,
      pureRight,
      pureLeft,
      delta,
    };
  }

  #zeroSample(delta) {
    this._currentSpeed = 0;
    this._currentVelocity.set(0, 0, 0);
    return {
      velocity: this._currentVelocity.clone(),
      speed: 0,
      moving: false,
      facing: null,
      pureBackward: false,
      pureRight: false,
      pureLeft: false,
      delta,
    };
  }

  #hasManualMovementInput() {
    return this.keys.has('KeyW') || this.keys.has('ArrowUp')
      || this.keys.has('KeyS') || this.keys.has('ArrowDown')
      || this.keys.has('KeyA') || this.keys.has('ArrowLeft')
      || this.keys.has('KeyD') || this.keys.has('ArrowRight')
      || this.mobileIntent.active;
  }

  dispose() {
    window.removeEventListener('keydown', this._onDown);
    window.removeEventListener('keyup', this._onUp);
  }
}

function isMovementCode(code) {
  return code === 'KeyW' || code === 'ArrowUp'
    || code === 'KeyS' || code === 'ArrowDown'
    || code === 'KeyA' || code === 'ArrowLeft'
    || code === 'KeyD' || code === 'ArrowRight';
}
