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
    const sample = this.controller.sample(delta);

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
    this.group.rotation.y = this._currentYaw;

    if (this.body) {
      this.#applyPhysicsMotion(sample, delta);
    } else {
      this.#applyKinematicMotion(sample, delta);
    }
    this.#updateAnimationState(sample);

    if (this.character) this.character.update(delta);
    this.playerCamera.follow(this.group.position);

    this.#logFeetVsTerrain(delta);
    return sample;
  }

  // Sprint 9 investigation: is the player visually below the displaced terrain?
  // Logs once per second (player_y, terrain_y_at_xz, delta). Static ground in
  // Physics.js is a flat slab at y=0; terrain mesh has a sine-wave displacement
  // that only kicks in past r≈22 from spawn, so a non-zero delta at distance is
  // expected. Remove once the question is settled.
  #logFeetVsTerrain(delta) {
    this._debugAccum = (this._debugAccum || 0) + delta;
    if (this._debugAccum < 1.0) return;
    this._debugAccum = 0;
    const { x, y, z } = this.group.position;
    const ty = this.terrain ? this.terrain.heightAt(x, z) : 0;
    const d = y - ty;
    console.log(
      `[Player] pos=(${x.toFixed(2)}, ${y.toFixed(3)}, ${z.toFixed(2)})  terrainY=${ty.toFixed(3)}  Δ=${d.toFixed(3)}m`,
    );
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
      nextState = this.controller.isRunning ? 'running' : 'walking';
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
}
