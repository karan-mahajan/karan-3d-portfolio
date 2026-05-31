import * as THREE from "three/webgpu";

// When the player lands on a fence rope, shove them sideways off the thin top
// instead of letting them balance. Speed × time must clear half-thickness +
// capsule radius (~0.12 + 0.3) so they actually fall off.
const FENCE_EJECT_SPEED = 2.5; // m/s sideways push
const FENCE_EJECT_TIME = 0.25; // seconds the push lasts (~0.6 m of travel)

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
    this.eventQueue = null;
    this.characterController = null;
    this._tmpVec = new THREE.Vector3();
  }

  async init() {
    const RAPIER = await import("@dimforge/rapier3d-compat");
    // Compat package ships WASM inlined as base64 — init() decodes + boots it.
    await RAPIER.init();
    this.RAPIER = RAPIER;
    this.world = new RAPIER.World({ x: 0, y: Physics.GRAVITY, z: 0 });
    this.eventQueue = new RAPIER.EventQueue(true);

    // Character controller — handles slope, autostep, snap-to-ground.
    // The 0.01 offset is the skin-width; keep it small to avoid floating.
    this.characterController = this.world.createCharacterController(0.01);
    this.characterController.setApplyImpulsesToDynamicBodies(true);
    this.characterController.setMaxSlopeClimbAngle((50 * Math.PI) / 180);
    this.characterController.setMinSlopeSlideAngle((30 * Math.PI) / 180);
    this.characterController.enableSnapToGround(0.5);
    this.characterController.enableAutostep(0.4, 0.2, true);
    this.characterController.setSlideEnabled(true);

    // Fence colliders keyed by handle → the wall's perpendicular axis + centre.
    // The player must be able to jump a fence but never balance on the rope, so
    // PlayerBody.move() refuses to ground on these and slides the player off.
    this.fenceColliders = new Map();

    this.ready = true;
    return true;
  }

  step(delta) {
    if (!this.ready) return;
    // Rapier uses a fixed step internally; we just call step() once per frame.
    // Override the integration parameters dt so step matches our frame delta —
    // keeps physics responsive at variable framerates.
    this.world.timestep = Math.min(delta, 1 / 30);
    this.world.step(this.eventQueue);
    this.#drainContactForceEvents();
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
      nrows,
      ncols,
      heights,
      { x: size, y: 1, z: size },
    );
    world.createCollider(colliderDesc, body);
    return body;
  }

  /** Vertical cylinder collider for trees, posts, bushes. */
  addStaticCylinder(x, y, z, radius, height) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(
      x,
      y + height / 2,
      z,
    );
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.cylinder(height / 2, radius);
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Kinematic vertical cylinder — a MOVING obstacle the character controller
   * collides with (e.g. a wandering animal). Unlike the fixed helpers the caller
   * drives it each frame with `body.setNextKinematicTranslation({x,y,z})`.
   * `(x, y, z)` is the cylinder CENTRE (no internal lift — caller positions it
   * at the visible bbox centre and follows the mesh). Returns the RigidBody.
   */
  addKinematicCylinder(x, y, z, radius, halfHeight) {
    const { RAPIER, world } = this;
    const bodyDesc =
      RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(x, y, z);
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.cylinder(halfHeight, radius);
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Box collider — used for rocks, billboard screens, signs.
   * `(x, y, z)` is the CENTRE of the box. `yaw` (radians) rotates around Y.
   * Caller passes the centre directly (no internal lift).
   */
  addStaticCuboid(x, y, z, hx, hy, hz, yaw = 0) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(x, y, z);
    if (yaw) {
      // Quaternion for rotation around Y by `yaw`.
      const half = yaw / 2;
      bodyDesc.setRotation({
        x: 0,
        y: Math.sin(half),
        z: 0,
        w: Math.cos(half),
      });
    }
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.cuboid(hx, hy, hz);
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Static convex hull from a flat `[x,y,z,…]` Float32Array of WORLD-space
   * points. The body sits at the origin so the hull lives directly in world
   * space. Rapier reduces the point set to its convex hull internally (pass every
   * mesh vertex — it keeps only the silhouette), giving a collider that hugs an
   * irregular prop far tighter than an AABB/oriented box, whose corners jut past
   * the mesh as an "invisible wall next to the rock". Use for rocks / boulders.
   * Returns null if the points are degenerate (< 4 non-coplanar).
   */
  addStaticConvexHull(worldPoints) {
    const { RAPIER, world } = this;
    const colliderDesc = RAPIER.ColliderDesc.convexHull(worldPoints);
    if (!colliderDesc) return null;
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Static triangle mesh collider from WORLD-space vertices. Use for sparse
   * props whose real silhouette matters more than an enclosing box.
   */
  addStaticTrimesh(worldPoints, indices) {
    const { RAPIER, world } = this;
    const colliderDesc = RAPIER.ColliderDesc.trimesh(worldPoints, indices);
    if (!colliderDesc) return null;
    const body = world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Thin wall capped by a sharp pitched ridge — used for rope-and-post fences.
   * The ridge keeps the silhouette tight, but a horizontal ridge LINE is still
   * balanceable, so a rope must not read as ground at all: this registers the
   * collider in `fenceColliders` and PlayerBody.move() refuses to stand on it
   * (you can jump the fence, but never perch on the rope). The wall below the
   * `shoulderY`→`topY` roof still blocks walking through.
   *
   * Local frame: length along X (±`halfLen`), thickness along Z (±`halfThick`),
   * ridge runs the length; `yaw` rotates it to the segment direction. Y is baked
   * absolute (yaw rotation preserves Y), so `(x, z)` is the wall's ground centre.
   */
  addStaticRidgeWall(
    x,
    z,
    baseY,
    shoulderY,
    topY,
    halfLen,
    halfThick,
    yaw = 0,
  ) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.fixed().setTranslation(x, 0, z);
    if (yaw) {
      const half = yaw / 2;
      bodyDesc.setRotation({
        x: 0,
        y: Math.sin(half),
        z: 0,
        w: Math.cos(half),
      });
    }
    const body = world.createRigidBody(bodyDesc);
    const pts = [];
    for (const sx of [-halfLen, halfLen]) {
      pts.push(sx, baseY, -halfThick, sx, baseY, halfThick); // wall foot
      pts.push(sx, shoulderY, -halfThick, sx, shoulderY, halfThick); // roof eaves
      pts.push(sx, topY, 0); // ridge apex
    }
    const colliderDesc = RAPIER.ColliderDesc.convexHull(new Float32Array(pts));
    if (!colliderDesc) return body;
    const collider = world.createCollider(colliderDesc, body);
    // Perpendicular (thin) axis of the wall = local +Z rotated by yaw → the
    // direction to slide the player off if they land on the rope.
    this.fenceColliders.set(collider.handle, {
      nx: Math.sin(yaw),
      nz: Math.cos(yaw),
      cx: x,
      cz: z,
    });
    return body;
  }

  /**
   * Dynamic ball — used for the kickable football. The player's character
   * controller has setApplyImpulsesToDynamicBodies(true), so the player can
   * push the ball just by walking into it. `kick(yaw, power)` applies a
   * forward+upward impulse; `respawn(x,y,z)` teleports it back.
   *
   * Linear damping (0.6) + Rapier's default contact friction bring the ball
   * to rest naturally over ~3-4 seconds, matching the old custom rolling
   * feel without needing per-frame friction math.
   */
  addDynamicBall(
    x,
    y,
    z,
    radius,
    { density = 0.6, restitution = 0.25, friction = 0.75 } = {},
  ) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(x, y, z)
      .setLinearDamping(0.6)
      .setAngularDamping(0.55)
      .setCcdEnabled(true);
    const body = world.createRigidBody(bodyDesc);
    const colliderDesc = RAPIER.ColliderDesc.ball(radius)
      .setDensity(density)
      .setRestitution(restitution)
      .setFriction(friction);
    world.createCollider(colliderDesc, body);
    return body;
  }

  /**
   * Dynamic cuboid — used for lightweight pushable props. `(x, y, z)` is the
   * collider centre; half-extents must match the visible mesh.
   */
  addDynamicCuboid(
    x,
    y,
    z,
    hx,
    hy,
    hz,
    rotation = { x: 0, y: 0, z: 0, w: 1 },
    {
      mass = 0.1,
      density = null,
      restitution = 0.15,
      friction = 0.7,
      linearDamping = 0.1,
      angularDamping = 0.1,
      canSleep = true,
      sleeping = true,
      contactThreshold = null,
      onCollision = null,
    } = {},
  ) {
    const { RAPIER, world } = this;
    const bodyDesc = RAPIER.RigidBodyDesc.dynamic()
      .setTranslation(x, y, z)
      .setRotation(rotation)
      .setLinearDamping(linearDamping)
      .setAngularDamping(angularDamping)
      .setCanSleep(canSleep)
      .setSleeping(sleeping)
      .setCcdEnabled(true);

    const body = world.createRigidBody(bodyDesc);
    let colliderDesc = RAPIER.ColliderDesc.cuboid(hx, hy, hz)
      .setRestitution(restitution)
      .setFriction(friction);
    colliderDesc =
      density === null
        ? colliderDesc.setMass(mass)
        : colliderDesc.setDensity(density);

    if (typeof onCollision === "function" || contactThreshold !== null) {
      colliderDesc = colliderDesc
        .setActiveEvents(RAPIER.ActiveEvents.CONTACT_FORCE_EVENTS)
        .setContactForceEventThreshold(contactThreshold ?? 15);
    }

    const collider = world.createCollider(colliderDesc, body);
    body.userData = { onCollision, collider };
    return body;
  }

  #drainContactForceEvents() {
    if (!this.eventQueue) return;
    this.eventQueue.drainContactForceEvents((event) => {
      const collider1 = this.world.getCollider(event.collider1());
      const collider2 = this.world.getCollider(event.collider2());
      const body1 = collider1?.parent();
      const body2 = collider2?.parent();
      const callback1 = body1?.userData?.onCollision;
      const callback2 = body2?.userData?.onCollision;
      if (typeof callback1 !== "function" && typeof callback2 !== "function")
        return;

      const mass = Math.max(
        (body1?.mass?.() ?? 0) + (body2?.mass?.() ?? 0),
        0.001,
      );
      const force = event.maxForceMagnitude() / mass;
      const p1 = body1?.translation?.();
      const p2 = body2?.translation?.();
      const position =
        p1 && p2
          ? {
              x: (p1.x + p2.x) * 0.5,
              y: (p1.y + p2.y) * 0.5,
              z: (p1.z + p2.z) * 0.5,
            }
          : (p1 ?? p2 ?? { x: 0, y: 0, z: 0 });

      if (typeof callback1 === "function") callback1(force, position);
      if (typeof callback2 === "function") callback2(force, position);
    });
  }

  /**
   * Swept-capsule clearance test. Returns true if an upright capsule of
   * (`radius`, `halfHeight`) cast from `origin` along `dir` for `distance`
   * metres encounters no static geometry. Pass the player's collider as
   * `excludeCollider` so the player's own body doesn't count as a hit.
   *
   * Used by ActionPrompts to gate body-sweeping animations (backflip,
   * cartwheel) so limbs don't clip walls, trees, signs, or rising slopes.
   * The caller chooses the cast direction(s) — a backflip casts
   * backward+up; a cartwheel casts ±sideways+up.
   *
   * `dir` is normalised internally; magnitude doesn't matter. The cast
   * uses stopAtPenetration=true so any initial overlap counts as blocked
   * (caller should lift the origin so the capsule's bottom hemisphere
   * sits just above the ground).
   */
  clearanceFor(
    origin,
    dir,
    distance,
    radius,
    halfHeight,
    excludeCollider = null,
  ) {
    if (!this.ready) return true;
    const { RAPIER, world } = this;
    const len = Math.hypot(dir.x, dir.y, dir.z) || 1;
    const shape = new RAPIER.Capsule(halfHeight, radius);
    const shapePos = { x: origin.x, y: origin.y, z: origin.z };
    const shapeRot = { x: 0, y: 0, z: 0, w: 1 };
    // With maxToi=1, shapeVel itself is the total displacement vector.
    const shapeVel = {
      x: (dir.x / len) * distance,
      y: (dir.y / len) * distance,
      z: (dir.z / len) * distance,
    };
    const hit = world.castShape(
      shapePos,
      shapeRot,
      shapeVel,
      shape,
      1.0,
      true,
      undefined,
      undefined,
      excludeCollider || undefined,
    );
    return hit === null;
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

    const bodyDesc =
      RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(
        spawnPos.x,
        spawnPos.y + height / 2,
        spawnPos.z,
      );
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
    // Sideways slide applied for a few frames after landing on a fence rope, to
    // shove the player off the thin top instead of letting them balance on it.
    this._fenceSlideX = 0;
    this._fenceSlideZ = 0;
    this._fenceSlideT = 0;
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

    // Carry an active fence-eject slide into this frame's desired motion.
    let slideX = 0;
    let slideZ = 0;
    if (this._fenceSlideT > 0) {
      slideX = this._fenceSlideX;
      slideZ = this._fenceSlideZ;
      this._fenceSlideT -= delta;
    }

    const desired = {
      x: (horizontal.x + slideX) * delta,
      y: this._verticalVelocity * delta,
      z: (horizontal.z + slideZ) * delta,
    };

    const cc = this.physics.characterController;
    cc.computeColliderMovement(this.collider, desired);
    const corrected = cc.computedMovement();

    this._grounded = cc.computedGrounded();
    // A rope is not standable: if the support this frame is a fence top, drop
    // grounded and kick the player sideways off the thin wall (they keep
    // falling, so they slide down a roof face and land beside the fence).
    if (this._grounded) this.#rejectFenceStanding(cc);
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

  /**
   * If the player is being supported FROM BELOW by a fence collider (rope top),
   * un-ground them and start a short sideways slide so they can't perch on it.
   * A side-on contact (walking into the fence) has a horizontal normal and is
   * ignored — only an upward support normal counts as "standing on it".
   */
  #rejectFenceStanding(cc) {
    const fences = this.physics.fenceColliders;
    if (!fences || fences.size === 0) return;

    const n = cc.numComputedCollisions();
    for (let i = 0; i < n; i++) {
      const col = cc.computedCollision(i);
      const handle = col?.collider?.handle;
      if (handle == null) continue;
      const info = fences.get(handle);
      if (!info) continue;
      if (!col.normal1 || col.normal1.y < 0.5) continue; // not supporting from below

      this._grounded = false;
      // Slide along the wall's thin axis, away from its centre line.
      const t = this.body.translation();
      const side =
        (t.x - info.cx) * info.nx + (t.z - info.cz) * info.nz >= 0 ? 1 : -1;
      this._fenceSlideX = info.nx * side * FENCE_EJECT_SPEED;
      this._fenceSlideZ = info.nz * side * FENCE_EJECT_SPEED;
      this._fenceSlideT = FENCE_EJECT_TIME;
      return;
    }
  }

  teleport(x, y, z) {
    this.body.setTranslation({ x, y: y + this.height / 2, z }, true);
    this._verticalVelocity = 0;
  }
}

export const Physics_GRAVITY = Physics.GRAVITY;
