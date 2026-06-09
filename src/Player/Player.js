import * as THREE from 'three/webgpu';
import { PlayerController } from './PlayerController.js';

/**
 * Player: capsule placeholder at first, swapped for the loaded
 * Mixamo character. Owns position + state machine + ground following.
 */
export class Player {
  static HEIGHT = 1.7;
  static RADIUS = 0.38;
  static GRAVITY = -25;
  static JUMP_VELOCITY = 8.5;
  static IDLE_LOOK_AROUND_SECONDS = 8;
  // Ocean/pond interaction. Wading is gated on actual terrain water-depth
  // (ground dipping below the water surface), NOT a radial ring — the v3
  // island is r≈60 and the legacy r=120 ring never triggered, so ponds/river
  // read as dry to gameplay. WATER_SURFACE_Y mirrors Water.WATER_LEVEL_Y.
  static WATER_SURFACE_Y = -0.15;
  // Speed falloff per metre of water depth, clamped so the player can always
  // wade back out. Ankle-deep shore (~0.2 m) barely slows; a full 1.35 m basin
  // drops to ~40% speed.
  static WATER_SLOWDOWN_PER_M = 0.45;
  static WATER_SLOWDOWN_MIN = 0.15;

  // Natural foot-speed of each locomotion clip in m/s (estimated from typical
  // Mixamo / Avaturn pacing; the position track was stripped on import so we
  // can't measure at runtime). Used as `timeScale = currentSpeed / natural`
  // so feet plant on the ground instead of skating. Tune in-game if the foot
  // still slides — increase the value if feet move too fast, decrease if too
  // slow. See CLAUDE.md / fix-character-movement notes.
  static ANIM_NATURAL_SPEED = {
    walking: 2.3,
    running: 5.2,
    crouchWalk: 1.35,
  };
  // Soft clamp at the far edge of the world.glb terrain. TODO Phase 5:
  // tighten this once WorldWater can identify the actual ocean meshes.
  // Original v1 island used 52 (island ended at r=45, ocean floor at r=57).
  static MAX_TRAVEL_RADIUS = 150;
  static RESPAWN_FALL_Y = -5;

  constructor(scene, playerCamera, terrain = null, loader = null, physics = null) {
    this.scene = scene;
    this.playerCamera = playerCamera;
    this.terrain = terrain;
    this.loader = loader;
    this.physics = physics;
    this.controller = new PlayerController(playerCamera);

    const spawnY = this.terrain ? this.terrain.heightAt(0, 0) : 0;
    this.group = new THREE.Group();
    this.group.position.set(0, spawnY, 0);
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
    // Most recent physics sample; updateVisual() reads it for animation state
    // since it runs decoupled from (and possibly without) a physics substep.
    this._lastSample = null;
    // Set by markTeleported() whenever an external system snaps group.position
    // directly (map travel, respawn, mini-game placement, push reposition). The
    // App tick reads + clears it to drop the render-interpolation snapshots so
    // the character doesn't smear/pull toward the pre-snap position for a frame.
    this._teleported = false;

    // Build the kinematic capsule once physics is ready. The body's feet sit
    // at y=0 to match the visual group; gravity will be integrated by the
    // character controller helper.
    if (this.physics) {
      this.body = this.physics.createPlayer(
        { x: 0, y: spawnY, z: 0 },
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

  /**
   * Attach an already-loaded Character (its GLB is parsed off the critical
   * path in App.boot, concurrently with the world parse). On a failed load the
   * placeholder capsule stays visible. Returns the same load `result` the
   * caller passed, for boot-summary symmetry.
   */
  attachCharacter(character, result) {
    if (!result || !result.ok) {
      // Skin missing — keep the placeholder visible.
      this.character = null;
      return result ?? null;
    }
    this.character = character;
    this.group.remove(this.placeholder);
    this.placeholder = null;
    this.group.add(this.character.root);
    return result;
  }

  get position() {
    return this.group.position;
  }

  /**
   * Advance the player simulation by one FIXED physics substep. Called 0–N
   * times per frame from the App tick's fixed-timestep loop. Handles ONLY
   * state that must run at the physics rate: input sampling, wading slowdown,
   * world-bound clamping, jump, and the kinematic capsule move. Visual-rate
   * work (yaw smoothing, slope tilt, animation, the mixer) lives in
   * updateVisual() so it runs exactly once per rendered frame — at 120Hz some
   * frames run 0 substeps, and advancing the mixer here would freeze the
   * animation on those frames; at 30fps it would advance it twice.
   */
  stepPhysics(delta) {
    // While frozen (e.g. the lava sink sequence) an external system drives the
    // group transform — skip input + motion entirely. updateVisual() still
    // advances the character animation and keeps the camera following.
    if (this._frozen) return;

    // Wading slowdown — must be set before sample() so the velocity it returns
    // is already scaled. Depth is the terrain dipping below the water surface
    // (ponds, river, ocean falloff), so it engages wherever the water visibly
    // shows, capped at 85% slowdown (15% speed) so the player can't get stuck.
    const dx = this.group.position.x;
    const dz = this.group.position.z;
    const distFromCenter = Math.hypot(dx, dz);
    const groundY = this.terrain ? this.terrain.heightAt(dx, dz) : 0;
    const waterDepth = Player.WATER_SURFACE_Y - groundY;
    // Only wade-slow when actually down in the water — feet at/below the
    // surface. On a bridge deck over the river the feet are up on the planks
    // (the deck collider, not the terrain, is the floor), so skip the slowdown.
    const submergedFeet = this.group.position.y <= Player.WATER_SURFACE_Y + 0.1;
    if (waterDepth > 0 && submergedFeet) {
      const slow = waterDepth * Player.WATER_SLOWDOWN_PER_M;
      this.controller.speedMultiplier = Math.max(Player.WATER_SLOWDOWN_MIN, 1.0 - slow);
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
      // animations remain loaded but aren't auto-triggered by WASD. Only the
      // TARGET is set here; updateVisual() smooths toward it once per frame.
      this._targetYaw = sample.facing;
      this._idleTimer = 0;
    } else {
      this._idleTimer += delta;
    }

    if (this.body) {
      this.#applyPhysicsMotion(sample, delta);
    } else {
      this.#applyKinematicMotion(sample, delta);
    }

    this.#enforceWorldBounds();

    this._lastSample = sample;
    return sample;
  }

  /**
   * Visual-rate update — runs once per rendered frame on the real frame delta,
   * AFTER the App tick has interpolated group.position between the last two
   * physics states. Smooths facing, applies the slope lean, drives the
   * animation state machine, and advances the mixer. Reads the most recent
   * physics sample (this._lastSample) for animation decisions.
   */
  updateVisual(frameDelta) {
    // While frozen, still advance the animation and keep the camera following
    // the externally-driven transform (App skips its own follow when frozen).
    if (this._frozen) {
      this.character?.update?.(frameDelta);
      this.playerCamera?.follow?.(this.group.position);
      return;
    }

    // Smoothly rotate to face movement direction. Delta-time turn-rate
    // (rad/s) so 60fps and 144fps both reach the target in the same wall
    // time — a fixed per-frame lerp factor doesn't.
    const wrap = (a, b) => {
      let d = b - a;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      return d;
    };
    const yawDiff = wrap(this._currentYaw, this._targetYaw);
    const maxTurn = PlayerController.TURN_SPEED * frameDelta;
    this._currentYaw += Math.sign(yawDiff) * Math.min(Math.abs(yawDiff), maxTurn);
    // Use YXZ Euler order so the slope tilt below applies in the player's
    // post-yaw local frame (otherwise the lean direction would rotate with
    // the camera azimuth, which reads as wobble).
    this.group.rotation.order = 'YXZ';
    this.group.rotation.y = this._currentYaw;

    this.#applySlopeTilt();

    if (this._lastSample) this.#updateAnimationState(this._lastSample);

    if (this.character) this.character.update(frameDelta);
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
      const y = (this.terrain ? this.terrain.heightAt(0, 0) : 0) + 0.1;
      if (this.body) this.body.teleport(0, y, 0);
      this.group.position.set(0, y, 0);
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
   * Non-interruptible one-shots block all transitions. Cosmetic one-shots
   * (lookingAround / pointing / waving) are interrupted by movement so the
   * character can't slide while playing an idle gesture.
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
        this.character.play('startWalking', {
          once: true,
          then: 'walking',
          interruptible: true,
          fade: 0.15,
        });
        return;
      }
      // Locomotion → idle reads smoother with a slightly longer crossfade;
      // the walk clip's timeScale is also approaching zero by this point,
      // so the longer fade hides the last-frame freeze.
      const exitingLoco = (this._state === 'walking' || this._state === 'running' || this._state === 'crouchWalk')
        && nextState === 'idle';
      this._state = nextState;
      this.character.play(nextState, exitingLoco ? { fade: 0.3 } : undefined);
    }

    // Per-frame timeScale on the active locomotion clip so foot speed
    // tracks ground speed (no skating). Wading slows the player → the walk
    // anim slows in lockstep. During the decel tail, speed → 0 and timeScale
    // → 0, so the walk visually freezes just before the crossfade to idle.
    const naturalSpeed = Player.ANIM_NATURAL_SPEED[this._state];
    if (naturalSpeed) {
      const clip = this.character.actions[this._state];
      if (clip) clip.timeScale = sample.speed / naturalSpeed;
    }
  }

  /** Suspend input + normal motion so an external system can drive the group. */
  freeze() {
    this._frozen = true;
    if (this.controller) this.controller.paused = true;
  }

  /** Resume normal player control after a freeze(). */
  unfreeze() {
    this._frozen = false;
    if (this.controller) this.controller.paused = false;
  }

  /**
   * Flag a direct group.position snap so the App tick drops its render-
   * interpolation snapshots next frame (no smear/pull-back from the old spot).
   * Call after ANY external move that bypasses the kinematic controller —
   * placeAt/respawn do it internally; map teleport + push reposition call it.
   */
  markTeleported() {
    this._teleported = true;
  }

  /**
   * Snap the player (physics body + group + facing) to a fixed spot. Used when
   * a mini-game stations the player at a known throwing position.
   */
  placeAt(x, y, z, yaw = 0) {
    if (this.body?.teleport) this.body.teleport(x, y, z);
    this.group.position.set(x, y, z);
    this._currentYaw = yaw;
    this._targetYaw = yaw;
    this._verticalVelocity = 0;
    this.markTeleported();
  }

  /** Aim the body toward a yaw without moving — update() smooths the turn. */
  setFacing(yaw) {
    this._targetYaw = yaw;
  }

  /** Teleport back to spawn and reset facing/tilt (lava death, etc.). */
  respawn() {
    const y = (this.terrain ? this.terrain.heightAt(0, 0) : 0) + 0.1;
    if (this.body?.teleport) this.body.teleport(0, y, 0);
    this.group.position.set(0, y, 0);
    this.group.rotation.set(0, 0, 0);
    this._currentYaw = 0;
    this._targetYaw = 0;
    this._tiltX = 0;
    this._tiltZ = 0;
    this._verticalVelocity = 0;
    this.markTeleported();
  }

  /** Trigger context-specific gestures (called by Portfolio interactions). */
  point() {
    if (this.character) this.character.play('pointing', { once: true, then: 'idle', interruptible: true });
  }
  wave() {
    if (this.character) this.character.play('waving', { once: true, then: 'idle', interruptible: true });
  }

  /**
   * Colour Garden charge-throw. Plays the blended pickup→wind-up→throw clip,
   * frozen at `holdFrac` of the clip (the cocked wind-up frame) until
   * releaseChargedAction(). Returns false if the clip isn't loaded so the
   * caller can fall back to a stand-in. The clip is a non-interruptible
   * one-shot, so #updateAnimationState leaves it alone while it runs.
   */
  playChargedAction(name, holdFrac, rate = 1) {
    if (!this.character || !this.character.actions[name]) return false;
    const action = this.character.actions[name];
    const dur = action.getClip()?.duration ?? 0;
    const ok = this.character.playCharged(name, dur * holdFrac, { then: 'idle', fade: 0.2 });
    if (ok) {
      this._state = name;
      action.timeScale = rate; // play() reset it to 1; speed the throw clip up
    }
    return ok;
  }

  /** Release the held wind-up so the throw swing completes. */
  releaseChargedAction() {
    this.character?.releaseHold?.();
  }

  /**
   * Force a deferred character clip to load (e.g. before a mini-game that uses a
   * charged clip with no lazy fallback). Safe no-op if the character isn't
   * loaded yet. Returns the load promise or undefined.
   */
  ensureAction(name) {
    return this.character?.ensureAction?.(name);
  }

  /** Normalised 0..1 playhead of a character action (for release timing). */
  actionProgress(name) {
    return this.character?.actionProgress?.(name) ?? 0;
  }

  /** World position of the character's right wrist (the orb tracks it). */
  getHandWorldPosition(out) {
    return this.character?.getHandWorldPosition?.(out) ?? null;
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
