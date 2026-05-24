import * as THREE from 'three';
import { PlayerController } from './PlayerController.js';
import { Character } from './Character.js';

/**
 * Player: capsule placeholder at first, swapped for the loaded
 * Mixamo character. Owns position + state machine + ground following.
 */
export class Player {
  static HEIGHT = 1.7;
  static RADIUS = 0.3;
  static GRAVITY = -25;
  static JUMP_VELOCITY = 8.5;
  static IDLE_LOOK_AROUND_SECONDS = 8;
  // Ocean interaction. Must mirror src/Effects/Water.js ISLAND_RADIUS /
  // WATER_ENTRY_RADIUS. Past WATER_ENTRY the character starts to slow down;
  // SLOWDOWN_PER_M controls how fast resistance ramps with depth.
  static WATER_ENTRY_RADIUS = 45;
  static WATER_SLOWDOWN_PER_M = 0.1;
  static WATER_SLOWDOWN_MIN = 0.15;
  // Soft clamp just past the wading band — island ends at r=45 and the
  // ocean floor hits y=-2 by r=57, so anything further lets the player
  // walk fully submerged with no swim animation. 52 lands the wall at
  // the beach lip; wading slowdown handles the last ~7m organically.
  static MAX_TRAVEL_RADIUS = 52;
  static RESPAWN_FALL_Y = -5;

  constructor(scene, playerCamera, terrain = null, loader = null, physics = null) {
    this.scene = scene;
    this.playerCamera = playerCamera;
    this.terrain = terrain;
    this.loader = loader;
    this.physics = physics;
    this.controller = new PlayerController(playerCamera);

    this.group = new THREE.Group();
    this.group.position.set(0, 0, 0);
    this.scene.add(this.group);

    this.placeholder = this.#buildPlaceholderMesh();
    this.group.add(this.placeholder);

    this.character = null;
    this._targetYaw = 0;
    this._currentYaw = 0;
    this._verticalVelocity = 0;
    this._grounded = true;
    this._jumpLatched = false;
    this._idleTimer = 0;
    this._state = 'spawn';

    // Build the kinematic capsule once physics is ready. The body's feet sit
    // at y=0 to match the visual group; gravity will be integrated by the
    // character controller helper.
    if (this.physics) {
      this.body = this.physics.createPlayer(
        { x: 0, y: 0, z: 0 },
        { height: Player.HEIGHT, radius: Player.RADIUS },
      );
    } else {
      this.body = null;
    }
  }

  #buildPlaceholderMesh() {
    const group = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.3, Player.HEIGHT - 0.6, 4, 12),
      new THREE.MeshStandardMaterial({ color: '#f5e6d3', roughness: 0.7 }),
    );
    body.position.y = Player.HEIGHT / 2;
    body.castShadow = true;
    body.receiveShadow = true;
    group.add(body);

    const arrow = new THREE.Mesh(
      new THREE.ConeGeometry(0.12, 0.3, 8),
      new THREE.MeshStandardMaterial({ color: '#ff9944' }),
    );
    arrow.rotation.x = Math.PI / 2;
    arrow.position.set(0, Player.HEIGHT * 0.75, 0.35);
    arrow.castShadow = true;
    group.add(arrow);
    return group;
  }

  /** Async character load — returns metadata or null on failure. */
  async loadCharacter() {
    if (!this.loader) return null;
    this.character = new Character(this.loader);
    const result = await this.character.load();
    if (!result.ok) {
      // Skin missing — keep the placeholder visible.
      this.character = null;
      return result;
    }
    this.group.remove(this.placeholder);
    this.placeholder = null;
    this.group.add(this.character.root);
    return result;
  }

  get position() {
    return this.group.position;
  }

  update(delta) {
    // Ocean wading slowdown — must be set before sample() so the velocity
    // it returns is already scaled. Distance is XZ-only; depth grows by
    // 0.1× per metre past the water entry radius and caps at 85% slowdown
    // (15% original speed) so the player can't get fully stuck.
    const dx = this.group.position.x;
    const dz = this.group.position.z;
    const distFromCenter = Math.hypot(dx, dz);
    if (distFromCenter > Player.WATER_ENTRY_RADIUS) {
      const depth = (distFromCenter - Player.WATER_ENTRY_RADIUS) * Player.WATER_SLOWDOWN_PER_M;
      this.controller.speedMultiplier = Math.max(Player.WATER_SLOWDOWN_MIN, 1.0 - depth);
    } else {
      this.controller.speedMultiplier = 1.0;
    }

    const sample = this.controller.sample(delta);

    // Soft wall at MAX_TRAVEL_RADIUS. Hard-teleporting here used to fight
    // the kinematic character controller (move() queues a next-translation
    // that overrides our setTranslation, and the capsule would oscillate
    // into the ocean-floor slope and stick). Instead, just cancel the
    // outward component of velocity — inward motion always passes so the
    // player can wade back to land.
    if (sample.moving && distFromCenter >= Player.MAX_TRAVEL_RADIUS) {
      const ox = dx / distFromCenter;
      const oz = dz / distFromCenter;
      const outward = sample.velocity.x * ox + sample.velocity.z * oz;
      if (outward > 0) {
        sample.velocity.x -= outward * ox;
        sample.velocity.z -= outward * oz;
        if (sample.velocity.lengthSq() < 1e-6) sample.moving = false;
      }
    }

    if (sample.moving) {
      // Always rotate to face the movement direction — A/D/S all rotate the
      // character so the legs match the visible direction. Strafe / backwards
      // animations remain loaded but aren't auto-triggered by WASD.
      this._targetYaw = sample.facing;
      this._idleTimer = 0;
    } else {
      this._idleTimer += delta;
    }

    // Smoothly rotate to face movement direction.
    const wrap = (a, b) => {
      let d = b - a;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      return d;
    };
    this._currentYaw += wrap(this._currentYaw, this._targetYaw) * PlayerController.TURN_LERP;
    // Use YXZ Euler order so the slope tilt below applies in the player's
    // post-yaw local frame (otherwise the lean direction would rotate with
    // the camera azimuth, which reads as wobble).
    this.group.rotation.order = 'YXZ';
    this.group.rotation.y = this._currentYaw;

    if (this.body) {
      this.#applyPhysicsMotion(sample, delta);
    } else {
      this.#applyKinematicMotion(sample, delta);
    }

    this.#enforceWorldBounds();

    this.#applySlopeTilt();

    this.#updateAnimationState(sample);

    if (this.character) this.character.update(delta);
    this.playerCamera.follow(this.group.position);

    return sample;
  }

  /**
   * Subtle visual tilt so the character leans into hills instead of skating
   * vertically up them. Samples the terrain gradient via finite differences
   * at the player's feet, projects onto the post-yaw forward/right axes,
   * then exponentially smooths toward the target to avoid jitter.
   *
   * Visual only — the kinematic capsule body stays upright so physics
   * collision response doesn't change.
   */
  #applySlopeTilt() {
    if (!this.terrain) return;
    const eps = 0.5;
    const x = this.group.position.x;
    const z = this.group.position.z;
    const hL = this.terrain.heightAt(x - eps, z);
    const hR = this.terrain.heightAt(x + eps, z);
    const hD = this.terrain.heightAt(x, z - eps);
    const hU = this.terrain.heightAt(x, z + eps);
    const dyDx = (hR - hL) / (2 * eps);
    const dyDz = (hU - hD) / (2 * eps);
    // Project the world gradient onto the post-yaw local axes.
    const cy = Math.cos(this._currentYaw);
    const sy = Math.sin(this._currentYaw);
    const forwardSlope = sy * dyDx + cy * dyDz;  // +Z (local forward)
    const rightSlope   = cy * dyDx - sy * dyDz;  // +X (local right)
    const TILT_SCALE = 0.35;       // keep subtle so it reads as lean, not lay
    const TILT_LERP = 0.15;        // 0 = no smoothing, 1 = snap
    const targetX = -Math.atan(forwardSlope) * TILT_SCALE;
    const targetZ = -Math.atan(rightSlope)   * TILT_SCALE;
    this._tiltX = (this._tiltX ?? 0) + (targetX - (this._tiltX ?? 0)) * TILT_LERP;
    this._tiltZ = (this._tiltZ ?? 0) + (targetZ - (this._tiltZ ?? 0)) * TILT_LERP;
    this.group.rotation.x = this._tiltX;
    this.group.rotation.z = this._tiltZ;
  }

  /**
   * Catch falls into the void (y < RESPAWN_FALL_Y → spawn). Horizontal
   * containment is handled in update() by cancelling outward velocity at
   * MAX_TRAVEL_RADIUS — see the note there about why a hard teleport here
   * fought the character controller.
   */
  #enforceWorldBounds() {
    const p = this.body ? this.body.position : this.group.position;
    if (p.y < Player.RESPAWN_FALL_Y) {
      if (this.body) this.body.teleport(0, 2, 0);
      this.group.position.set(0, 2, 0);
    }
  }

  /** Rapier path: capsule + character controller resolve movement against the world. */
  #applyPhysicsMotion(sample, delta) {
    const pressing = this.controller.isJumping;
    if (pressing && !this._jumpLatched && this.body.grounded) {
      this.body.jump(Player.JUMP_VELOCITY);
    }
    this._jumpLatched = pressing;

    const horizontal = sample.moving
      ? { x: sample.velocity.x, z: sample.velocity.z }
      : { x: 0, z: 0 };
    this.body.move(horizontal, delta);

    const p = this.body.position;
    this.group.position.set(p.x, p.y, p.z);
    this._grounded = this.body.grounded;
  }

  /** Fallback: original manual gravity + ground snap (used if physics is unavailable). */
  #applyKinematicMotion(sample, delta) {
    if (sample.moving) {
      this.group.position.x += sample.velocity.x * delta;
      this.group.position.z += sample.velocity.z * delta;
    }

    const groundY = this.terrain
      ? this.terrain.heightAt(this.group.position.x, this.group.position.z)
      : 0;

    const pressing = this.controller.isJumping;
    if (pressing && !this._jumpLatched && this._grounded) {
      this._verticalVelocity = Player.JUMP_VELOCITY;
      this._grounded = false;
    }
    this._jumpLatched = pressing;

    this._verticalVelocity += Player.GRAVITY * delta;
    this.group.position.y += this._verticalVelocity * delta;

    if (this.group.position.y <= groundY) {
      this.group.position.y = groundY;
      this._verticalVelocity = 0;
      this._grounded = true;
    } else {
      this._grounded = false;
    }
  }

  /**
   * State machine: idle, walking, running, walkingBackwards, standingWalkRight,
   * jump, lookingAround. startWalking is a brief one-shot bridge from idle.
   *
   * Critical one-shots (standingUp spawn) block all transitions. Cosmetic
   * one-shots (lookingAround / pointing / waving) are interrupted by movement
   * so the character can't slide while playing an idle gesture.
   */
  #updateAnimationState(sample) {
    if (!this.character) return;

    // ActionPrompts-driven loops (push, dance) lock the animation so the
    // state machine doesn't yank it back to walk/idle each frame.
    if (this._actionLocked) return;

    const wantsMove = sample.moving || !this._grounded;
    const oneShot = this.character._oneShot;
    if (oneShot) {
      if (oneShot.interruptible && wantsMove) {
        // Cancel the gesture so movement can take over this frame.
        this.character._oneShot = null;
      } else {
        return;
      }
    }

    let nextState;
    if (!this._grounded) {
      nextState = 'jump';
    } else if (sample.moving) {
      if (this.controller.isCrouching && this.character.actions.crouchWalk) nextState = 'crouchWalk';
      else if (this.controller.isRunning) nextState = 'running';
      else nextState = 'walking';
    } else if (this._idleTimer >= Player.IDLE_LOOK_AROUND_SECONDS) {
      this._idleTimer = 0;
      this.character.play('lookingAround', { once: true, then: 'idle', interruptible: true });
      this._state = 'lookingAround';
      return;
    } else {
      nextState = 'idle';
    }

    if (nextState !== this._state) {
      // Idle → walking: brief startWalking bridge for natural pickup.
      if (this._state === 'idle' && nextState === 'walking' && this.character.actions.startWalking) {
        this._state = 'walking'; // record the target so we don't re-trigger
        this.character.play('startWalking', { once: true, then: 'walking', interruptible: true });
        return;
      }
      this._state = nextState;
      this.character.play(nextState);
    }
  }

  /** Trigger context-specific gestures (called by Portfolio interactions). */
  point() {
    if (this.character) this.character.play('pointing', { once: true, then: 'idle', interruptible: true });
  }
  wave() {
    if (this.character) this.character.play('waving', { once: true, then: 'idle', interruptible: true });
  }

  /**
   * Entry point for ActionPrompts. Plays an arbitrary action by name; opts
   * are forwarded to Character.play. Returns true if the action existed.
   */
  performAction(name, opts = {}) {
    if (!this.character || !this.character.actions[name]) return false;
    // Lock the state machine to this clip while it's playing — the one-shot
    // path in #updateAnimationState already handles this when interruptible
    // is false. We mark it interruptible only if the caller asks.
    this.character.play(name, { once: true, then: 'idle', interruptible: false, ...opts });
    this._state = name;
    return true;
  }

  /** Play a looping action (e.g. dance, push) until stopAction is called. */
  startLoopAction(name) {
    if (!this.character || !this.character.actions[name]) return false;
    this._actionLocked = true;
    this.character.play(name, { fade: 0.2 });
    this._state = name;
    return true;
  }

  /** Switch the current loop to a different clip without unlocking. */
  swapLoopAction(name) {
    if (!this.character || !this.character.actions[name]) return false;
    this.character.play(name, { fade: 0.25 });
    this._state = name;
    return true;
  }

  /** Stop a loop started by startLoopAction; fades back to idle. */
  stopLoopAction() {
    if (!this.character) return;
    this._actionLocked = false;
    this.character.play('idle', { fade: 0.25 });
    this._state = 'idle';
  }
}
