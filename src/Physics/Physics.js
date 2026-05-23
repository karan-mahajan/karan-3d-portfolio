import * as THREE from 'three';

/**
 * Rapier physics manager.
 *
 * Lifecycle:
 *   const physics = new Physics();
 *   await physics.init();           // loads WASM, builds World
 *   physics.addStaticGround(size);  // big flat ground
 *   physics.addStaticCylinder(x, y, z, radius, height);  // trees, posts, ...
 *   const player = physics.createPlayer(spawnPos, height, radius);
 *   // each tick:
 *   physics.step(delta);
 *
 * The character controller is shared — one per player is fine. We use
 * kinematicPositionBased bodies and compute movement against world
 * geometry via Rapier's KinematicCharacterController helper.
 */
export class Physics {
  static GRAVITY = -25;

  constructor() {
    this.ready = false;
    this.RAPIER = null;
    this.world = null;
    this.characterController = null;
    this._tmpVec = new THREE.Vector3();
  }

  async init() {
    const RAPIER = await import('@dimforge/rapier3d-compat');
    // Compat package ships WASM inlined as base64 — init() decodes + boots it.
    await RAPIER.init();
    this.RAPIER = RAPIER;
    this.world = new RAPIER.World({ x: 0, y: Physics.GRAVITY, z: 0 });

    // Character controller — handles slope, autostep, snap-to-ground.
    // The 0.01 offset is the skin-width; keep it small to avoid floating.
    this.characterController = this.world.createCharacterController(0.01);
    this.characterController.setApplyImpulsesToDynamicBodies(true);
    this.characterController.setMaxSlopeClimbAngle((50 * Math.PI) / 180);
    this.characterController.setMinSlopeSlideAngle((30 * Math.PI) / 180);
    this.characterController.enableSnapToGround(0.5);
    this.characterController.enableAutostep(0.4, 0.2, true);
    this.characterController.setSlideEnabled(true);

    this.ready = true;
    return true;
  }

  step(delta) {
    if (!this.ready) return;
    // Rapier uses a fixed step internally; we just call step() once per frame.
    // Override the integration parameters dt so step matches our frame delta —
    // keeps physics responsive at variable framerates.
    this.world.timestep = Math.min(delta, 1 / 30);
    this.world.step();
  }

  // ── Static colliders ─────────────────────────────────────────────────────

  /**
   * Build the ground collider from the visual terrain's displacement. The
   * collider is a Rapier heightfield sampled from `terrain.heightAt` at the
   * same grid resolution the visual mesh uses, so the player walks on the
   * exact surface the renderer draws. Previously this was a flat slab at
   * y=0, which left the player's feet up to ±0.65m off from the visual
   * surface past r≈22 from spawn.
   *
   * @param {{ size:number, segments:number, heightAt:(x:number,z:number)=>number }} terrain
   */
  addStaticGround(terrain) {
    const { RAPIER, world } = this;
    const size = terrain.size;
    // Per Rapier/parry: column index ↔ local X axis, row index ↔ local Z axis.
    // ncols counts cells along X, nrows along Z. Heights matrix is column-major
    // with (nrows+1) × (ncols+1) values: heights[col*(nrows+1) + row].
    // Earlier I had rows↔X / cols↔Z and the heightfield rendered transposed,
    // burying the player up to ~46cm at +X section endpoints.
    const nrows = terrain.segments; // cells along Z
    const ncols = terrain.segments; // cells along X
    const rowVerts = nrows + 1;
    const colVerts = ncols + 1;

    const heights = new Float32Array(rowVerts * colVerts);
    for (let ix = 0; ix < colVerts; ix++) {
      const x = -size / 2 + (ix / ncols) * size;
      for (let iz = 0; iz < rowVerts; iz++) {
        const z = -size / 2 + (iz / nrows) * size;
        heights[ix * rowVerts + iz] = terrain.heightAt(x, z);
      }
    }

    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(0, 0, 0);
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.heightfield(
      nrows, ncols, heights,
      { x: size, y: 1, z: size },
    );
    world.createCollider(colliderDesc, body);
    return body;
  }

  /** Vertical cylinder collider for trees, posts, bushes. */
  addStaticCylinder(x, y, z, radius, height) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(x, y + height / 2, z);
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.cylinder(height / 2, radius);
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Box collider — used for rocks, billboard screens, signs.
   * `yaw` (radians) rotates the box around the Y axis. Default 0 = axis-aligned.
   */
  addStaticCuboid(x, y, z, hx, hy, hz, yaw = 0) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(x, y + hy, z);
    if (yaw) {
      // Quaternion for rotation around Y by `yaw`.
      const half = yaw / 2;
      bodyDesc.setRotation({ x: 0, y: Math.sin(half), z: 0, w: Math.cos(half) });
    }
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.cuboid(hx, hy, hz);
    world.createCollider(colliderDesc, body);
    return body;
  }

  // ── Player ───────────────────────────────────────────────────────────────

  /**
   * Build a kinematic capsule for the player. Returns a tiny controller
   * object the Player class can use to move + read position back.
   */
  createPlayer(spawnPos, { height = 1.7, radius = 0.3 } = {}) {
    const { RAPIER, world } = this;

    // Capsule half-height excludes the two hemispherical caps.
    const halfHeight = Math.max(0.001, (height - radius * 2) / 2);

    const bodyDesc = RAPIER.RigidBodyDesc.kinematicPositionBased()
      .setTranslation(spawnPos.x, spawnPos.y + height / 2, spawnPos.z);
    const body = world.createRigidBody(bodyDesc);

    const colliderDesc = RAPIER.ColliderDesc.capsule(halfHeight, radius);
    const collider = world.createCollider(colliderDesc, body);

    return new PlayerBody(this, body, collider, { height, radius });
  }
}

/**
 * Thin wrapper around a kinematic capsule rigid body. The Player class drives
 * desired translation each frame; this resolves it against world geometry
 * via Rapier's character controller and updates the body.
 */
class PlayerBody {
  constructor(physics, body, collider, { height, radius }) {
    this.physics = physics;
    this.body = body;
    this.collider = collider;
    this.height = height;
    this.radius = radius;
    this._verticalVelocity = 0;
    this._grounded = true;
  }

  get position() {
    // Body position is at capsule center → feet are halfHeight below.
    const t = this.body.translation();
    return { x: t.x, y: t.y - this.height / 2, z: t.z };
  }

  get grounded() {
    return this._grounded;
  }

  jump(impulse) {
    if (this._grounded) {
      this._verticalVelocity = impulse;
      this._grounded = false;
    }
  }

  /**
   * Move the player. `horizontal` is a Vector3-shaped {x,z} desired velocity;
   * gravity + jump are integrated internally. Call once per frame.
   */
  move(horizontal, delta) {
    // Integrate vertical velocity (gravity + jump impulse).
    this._verticalVelocity += Physics.GRAVITY * delta;

    const desired = {
      x: horizontal.x * delta,
      y: this._verticalVelocity * delta,
      z: horizontal.z * delta,
    };

    const cc = this.physics.characterController;
    cc.computeColliderMovement(this.collider, desired);
    const corrected = cc.computedMovement();

    this._grounded = cc.computedGrounded();
    if (this._grounded && this._verticalVelocity < 0) {
      this._verticalVelocity = 0;
    }

    const t = this.body.translation();
    this.body.setNextKinematicTranslation({
      x: t.x + corrected.x,
      y: t.y + corrected.y,
      z: t.z + corrected.z,
    });
  }

  teleport(x, y, z) {
    this.body.setTranslation({ x, y: y + this.height / 2, z }, true);
    this._verticalVelocity = 0;
  }
}

export const Physics_GRAVITY = Physics.GRAVITY;
