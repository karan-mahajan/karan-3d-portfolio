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

  // ── Swimming ──────────────────────────────────────────────────────────
  // Deep-water locomotion. Enter when the water is deeper than a wade
  // (river center is only ~0.9 m below the surface, so the threshold must
  // sit under that), exit shallower with hysteresis so the boundary never
  // flickers. Small ponds + the lava basin are deny-listed by App via
  // setNoSwimZones() — depth alone can't exclude them (some are deeper
  // than the river).
  static SWIM_ENTER_DEPTH = 0.85;
  static SWIM_EXIT_DEPTH = 0.70;
  static SWIM_SPEED = 1.5;       // m/s, slower than walking
  static SWIM_FAST_SPEED = 2.5;  // m/s while Shift is held
  // How far the group origin (the standing character's FEET) sits below the
  // water surface while floating. The hips bone is pinned ~0.95 m above the
  // origin, so these put the hips just under the waterline: prone stroke
  // rides higher (back/head break the surface), treading hangs lower
  // (head + shoulders out). Pure visual tuning knobs.
  static SWIM_BODY_SINK = 1.05;
  static TREAD_BODY_SINK = 1.25;
  // Buoyancy: exponential approach rate to the float height, velocity-
  // clamped so plunging in reads as a settle, not a snap.
  static SWIM_SURFACE_LERP = 6;     // 1/s
  static SWIM_MAX_VERTICAL = 3;     // m/s
  // Don't let the player swim past the terrain mesh (±96.85) into
  // undefined heightfield samples.
  static SWIM_MAX_RADIUS = 90;
  // Small ponds where swimming must never trigger (the player wades
  // instead). World-space circles derived from the v3 authoring mask
  // (tools/blender/scripts/v3/karan/02-ground-grass-base.py ORGANIC_PONDS,
  // 512 px ≈ 125 m). The skills pond + lava pool are appended at runtime
  // from live GLB refs in App.#scheduleDeferredWorldSystems.
  static NO_SWIM_PONDS = [
    { x: 2.4,  z: 11.0,  r: 10 },  // center spawn-side pond
    { x: 45.7, z: 35.2,  r: 10 },  // lower-left curl pool
    { x: 38.1, z: -47.9, r: 10 },  // lower-right puddle splash
  ];
  // ── Edge-grab exit (swimming-to-edge clip) ────────────────────────────
  // Measured on the avatar (.verify/scripts/measure-swim-edge-reach.mjs):
  // prone strokes until ~1.6s, a vertical reach, then a stable two-handed
  // hold with the hands planted ~1.10m above the group origin and ~0.5m
  // ahead. The clip authors NO climb-up, so after the hold the body is
  // boosted onto the bank procedurally while crossfading to idle.
  //
  // The terrain has NO underwater cliffs (steepest carved bank ≈30°,
  // measured by .verify/scripts/debug-edge-grab-geometry.mjs — dry ground
  // is never closer than ~1.5m to swim-deep water). So the trigger probes a
  // fan of distances for the nearest dry lip and the clip's authored
  // approach strokes glide the body up to it; the hang then reads as
  // "chest at the waterline, hands on the edge" because the body-bank
  // intersection below the hold stays underwater.
  static EDGE_PROBE_MIN = 0.5;      // m — fan start (hand reach)
  // Fan end. Scanned (debug-edge-grab-geometry.mjs): at ≤2.75m dry lips
  // exist ONLY on river/lagoon banks — ocean beaches keep dry ground
  // farther out, so they can never trigger a grab. 2.25 covers the river
  // and both lagoons densely.
  static EDGE_PROBE_MAX = 2.25;
  static EDGE_PROBE_STEP = 0.25;
  static EDGE_BANK_MAX_Y = 0.55;    // lips above this are beyond arm reach — no grab
  static EDGE_HANDS_ABOVE_ORIGIN = 1.10; // measured hold-pose hand height over the feet origin
  static EDGE_HOLD_REACH = 0.55;    // hands plant this far ahead of the held body
  // Ground under the hold spot must stay submerged so the buried legs are
  // hidden by water. Carved banks flatten into a shoulder right at the
  // waterline (~-0.19 on the steepest profile), so "submerged" can only
  // mean a couple of cm under the -0.15 surface — any stricter and no bank
  // on the island qualifies.
  static EDGE_HOLD_MAX_GROUND = Player.WATER_SURFACE_Y - 0.02;
  static EDGE_MIN_SWIM_TIME = 0.4;  // s in swim mode before a grab can trigger (kills entry plunges)
  static EDGE_APPROACH_TIME = 1.6;  // s — the clip's authored approach strokes
  static EDGE_GRAB_RISE_TIME = 0.5; // s to lift the body to the hold height
  static EDGE_GRAB_HOLD_TIME = 1.5; // s from grab start until the boost begins (reach completes)
  static EDGE_CLIMB_TIME = 0.55;    // s for the boost onto the bank
  static EDGE_CLIMB_FORWARD = 0.35; // m beyond the lip the landing point sits

  // Natural foot-speed of each locomotion clip in m/s, MEASURED from the
  // source clips' hip root-motion (forward travel / duration) before the
  // position tracks are stripped on import: walking 1.7m over 1.03s, running
  // 3.1m over 0.70s. Used as `timeScale = currentSpeed / natural` so feet
  // plant on the ground instead of skating. PlayerController WALK/RUN speeds
  // are tuned to sit near these so playback stays close to 1× (the old
  // 3.6/7.2 m/s speeds overdrove the clips ~1.5× and read as frantic).
  static ANIM_NATURAL_SPEED = {
    walking: 1.65,
    running: 4.43,
    crouchWalk: 1.35,
    // Stroke cadence tuned so the clip plays ~0.85× at SWIM_SPEED and ~1.4×
    // at SWIM_FAST_SPEED (in-place Mixamo clip — no measured ground pace).
    swimming: 1.8,
  };
  // Jump clips are full authored arcs (crouch→launch→air→land, ~2s) while the
  // physics arc is snappy (~0.7s airborne). startAt skips the anticipation
  // crouch (the impulse already happened); timeScale compresses the rest so
  // the clip's airborne stretch roughly matches the physics airtime. Landing
  // crossfades back to locomotion the moment physics touches down.
  static JUMP_ANIM = {
    jumpStanding: { startAt: 0.45, timeScale: 1.35 },
    jumpMoving:   { startAt: 0.40, timeScale: 1.35 },
  };
  // Ground speed at takeoff above which the running-style jump plays.
  static JUMP_MOVING_SPEED = 2.5;
  // Stopping from a RUN plays the heavier breathing idle this long (catching
  // breath), then settles into the calm base idle. Stopping from a walk goes
  // straight to the calm idle.
  static BREATH_AFTER_RUN_SECONDS = 4;
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
    // Which jump clip this jump uses — latched at takeoff (so mid-air speed
    // changes can't flip the animation) and cleared on landing.
    this._jumpClip = null;
    // Continuous airborne seconds; brief ground-contact blips (stepping off
    // rocks) stay under the falling-clip threshold so the pose doesn't flicker.
    this._airTime = 0;
    // Seconds spent in the post-run catch-breath idle.
    this._breathTimer = 0;
    this._state = 'spawn';
    // Most recent physics sample; updateVisual() reads it for animation state
    // since it runs decoupled from (and possibly without) a physics substep.
    this._lastSample = null;
    // Set by markTeleported() whenever an external system snaps group.position
    // directly (map travel, respawn, mini-game placement, push reposition). The
    // App tick reads + clears it to drop the render-interpolation snapshots so
    // the character doesn't smear/pull toward the pre-snap position for a frame.
    this._teleported = false;
    // Deep-water swim mode — set per substep in stepPhysics with hysteresis.
    this._swimming = false;
    this._noSwimZones = [...Player.NO_SWIM_PONDS];
    // Continuous seconds in swim mode (edge-grab trigger guard) and the
    // active edge-grab sequence ({phase, t, ...} while grabbing/climbing).
    this._swimTime = 0;
    this._edgeGrab = null;

    // Museum interior: skip the terrain-coupled effects (wading slowdown,
    // slope tilt) and swap the void-fall respawn — the basement sits at
    // y≈−45, far below RESPAWN_FALL_Y, and its x/z overlaps outdoor ponds.
    this.interiorMode = false;
    this.respawnFallY = Player.RESPAWN_FALL_Y;
    this.respawnPoint = null; // {x,y,z} override while inside the museum

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

    // Edge-grab sequence owns the body (rise to the hold, then boost onto the
    // bank) — input and normal swim motion are paused until it completes.
    if (this._edgeGrab) {
      this.#updateEdgeGrab(delta);
      this._lastSample = this.#stationarySample(delta);
      return this._lastSample;
    }

    // Wading slowdown — must be set before sample() so the velocity it returns
    // is already scaled. Depth is the terrain dipping below the water surface
    // (ponds, river, ocean falloff), so it engages wherever the water visibly
    // shows, capped at 85% slowdown (15% speed) so the player can't get stuck.
    const dx = this.group.position.x;
    const dz = this.group.position.z;
    const distFromCenter = Math.hypot(dx, dz);
    if (this.interiorMode) {
      // Museum floors are dry — the terrain sampled here is the OUTDOOR
      // surface 45m above the player's actual floor (and may dip into ponds).
      this._swimming = false;
      this.controller.swimMode = false;
      this.controller.speedMultiplier = 1.0;
    } else {
      const groundY = this.terrain ? this.terrain.heightAt(dx, dz) : 0;
      const waterDepth = Player.WATER_SURFACE_Y - groundY;
      // Only wade-slow when actually down in the water — feet at/below the
      // surface. On a bridge deck over the river the feet are up on the planks
      // (the deck collider, not the terrain, is the floor), so skip the slowdown.
      const submergedFeet = this.group.position.y <= Player.WATER_SURFACE_Y + 0.1;
      const overWater = waterDepth > 0 && submergedFeet;

      // Swim mode: deep water engages it, hysteresis releases it. The same
      // feet gate that protects bridges from wade-slow protects them here.
      if (this._swimming) {
        // Lift-exit: ground support carrying the body above the exit-depth
        // float line means the player is standing in the shallows or has
        // ridden up a bank. The x/z depth sample misses this (steep banks
        // read "deep" right at the wall), which left the stroke playing on
        // dry-looking edges.
        const lifted = (this.body ? this.body.swimSupported : true)
          && this.group.position.y > Player.WATER_SURFACE_Y - Player.SWIM_EXIT_DEPTH;
        if (!overWater || waterDepth < Player.SWIM_EXIT_DEPTH || lifted) this._swimming = false;
      } else if (
        overWater
        && waterDepth >= Player.SWIM_ENTER_DEPTH
        // Mirror of the lift-exit: standing supported above the exit float
        // line (steep banks, submerged props) must not re-enter swim on the
        // very next substep — that would thrash the swim↔walk crossfade.
        // Beach wading (feet down at the deep ground) and jump-ins (airborne)
        // pass untouched.
        && !(this.body?.grounded
          && this.group.position.y > Player.WATER_SURFACE_Y - Player.SWIM_EXIT_DEPTH)
        && !this.#inNoSwimZone(dx, dz)
      ) {
        this._swimming = true;
        // A jump that splashed down mid-arc must not resume its clip later.
        this._jumpClip = null;
        this._verticalVelocity = 0;
      }
      this.controller.swimMode = this._swimming;

      if (this._swimming) {
        // Swim pace replaces the wade slowdown (depth-scaled slowdown would
        // floor a deep-water swimmer at 15% speed).
        this.controller.speedMultiplier = this.controller.isRunning
          ? Player.SWIM_FAST_SPEED / PlayerController.RUN_SPEED
          : Player.SWIM_SPEED / PlayerController.WALK_SPEED;
      } else if (overWater) {
        const slow = waterDepth * Player.WATER_SLOWDOWN_PER_M;
        this.controller.speedMultiplier = Math.max(Player.WATER_SLOWDOWN_MIN, 1.0 - slow);
      } else {
        this.controller.speedMultiplier = 1.0;
      }
    }
    this._swimTime = this._swimming ? this._swimTime + delta : 0;

    const sample = this.controller.sample(delta);

    // Swimming into a grabbable bank edge starts the edge-grab exit. Checked
    // after sampling (the trigger needs the movement direction) and before
    // motion is applied so the sequence owns the body from its first substep.
    if (
      this._swimming
      && sample.moving
      && this._swimTime >= Player.EDGE_MIN_SWIM_TIME
    ) {
      this.#maybeStartEdgeGrab(sample);
      if (this._edgeGrab) {
        this._lastSample = this.#stationarySample(delta);
        return this._lastSample;
      }
    }

    // Soft wall at MAX_TRAVEL_RADIUS. Hard-teleporting here used to fight
    // the kinematic character controller (move() queues a next-translation
    // that overrides our setTranslation, and the capsule would oscillate
    // into the ocean-floor slope and stick). Instead, just cancel the
    // outward component of velocity — inward motion always passes so the
    // player can wade back to land.
    const travelRadius = this._swimming ? Player.SWIM_MAX_RADIUS : Player.MAX_TRAVEL_RADIUS;
    if (sample.moving && distFromCenter >= travelRadius) {
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

    // Swimming reports ungrounded but is NOT airborne — keep the timer at
    // zero so a one-frame ungrounded shore exit can't read as a minutes-long
    // fall and flash the falling clip.
    this._airTime = (this._grounded || this._swimming) ? 0 : this._airTime + frameDelta;
    if (this._state === 'breathingIdle') this._breathTimer += frameDelta;
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
    if (this.interiorMode) {
      // Level out smoothly — interior floors are flat; outdoor gradients here
      // are phantom (sampled 45m above the player's actual floor).
      this._tiltX = (this._tiltX ?? 0) * 0.85;
      this._tiltZ = (this._tiltZ ?? 0) * 0.85;
      this.group.rotation.x = this._tiltX;
      this.group.rotation.z = this._tiltZ;
      return;
    }
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
    if (p.y < this.respawnFallY) {
      const rp = this.respawnPoint;
      const x = rp ? rp.x : 0;
      const z = rp ? rp.z : 0;
      const y = rp ? rp.y : (this.terrain ? this.terrain.heightAt(0, 0) : 0) + 0.1;
      if (this.body) this.body.teleport(x, y, z);
      this.group.position.set(x, y, z);
      this.markTeleported();
    }
  }

  /** Rapier path: capsule + character controller resolve movement against the world. */
  #applyPhysicsMotion(sample, delta) {
    if (this._swimming) {
      // Buoyancy: velocity-clamped exponential approach to the float height.
      // Routed through the controller (PlayerBody.swim) so shores still block.
      const sink = sample.moving ? Player.SWIM_BODY_SINK : Player.TREAD_BODY_SINK;
      const targetY = Player.WATER_SURFACE_Y - sink;
      // Error term reads the BODY y, not group y — App overwrites the group
      // with the render interpolation after the fixed loop, so on the first
      // substep of a frame the group is up to one substep stale.
      const vy = THREE.MathUtils.clamp(
        (targetY - this.body.position.y) * Player.SWIM_SURFACE_LERP,
        -Player.SWIM_MAX_VERTICAL,
        Player.SWIM_MAX_VERTICAL,
      );
      const horizontal = sample.moving
        ? { x: sample.velocity.x, z: sample.velocity.z }
        : { x: 0, z: 0 };
      this.body.swim(horizontal, vy, delta);
      const p = this.body.position;
      this.group.position.set(p.x, p.y, p.z);
      this._grounded = false;
      // Treat a held Space as consumed: without this, holding the (no-op)
      // jump key while swimming fires a surprise hop on the first substep
      // that grounds at the shore.
      this._jumpLatched = true;
      return;
    }
    const pressing = this.controller.isJumping;
    if (pressing && !this._jumpLatched && this.body.grounded) {
      this.body.jump(Player.JUMP_VELOCITY);
      this.#latchJumpClip(sample);
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
    if (this._swimming) {
      if (sample.moving) {
        this.group.position.x += sample.velocity.x * delta;
        this.group.position.z += sample.velocity.z * delta;
      }
      const sink = sample.moving ? Player.SWIM_BODY_SINK : Player.TREAD_BODY_SINK;
      // No collider on this path — clamp the float target to the seabed so
      // the legs can't bury where the water is shallower than the sink depth.
      const groundY = this.terrain
        ? this.terrain.heightAt(this.group.position.x, this.group.position.z)
        : 0;
      const targetY = Math.max(groundY, Player.WATER_SURFACE_Y - sink);
      const vy = THREE.MathUtils.clamp(
        (targetY - this.group.position.y) * Player.SWIM_SURFACE_LERP,
        -Player.SWIM_MAX_VERTICAL,
        Player.SWIM_MAX_VERTICAL,
      );
      this.group.position.y += vy * delta;
      this._verticalVelocity = 0;
      this._grounded = false;
      // Held Space is consumed (see #applyPhysicsMotion) — no shore-exit hop.
      this._jumpLatched = true;
      return;
    }
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
      this.#latchJumpClip(sample);
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
   * Latch the jump animation for this takeoff: a running-style leap when
   * moving, a vertical hop from standstill. Called at the exact frame the
   * jump impulse fires so the choice can't flip mid-air.
   */
  #latchJumpClip(sample) {
    this._jumpClip = (sample?.speed ?? 0) >= Player.JUMP_MOVING_SPEED
      ? 'jumpMoving'
      : 'jumpStanding';
  }

  /**
   * State machine: idle, walking, running, walkingBackwards, crouchWalk,
   * jumpStanding/jumpMoving (latched at takeoff), falling. The idle is ONLY
   * the breathing clip — no periodic look-around gesture and no startWalking
   * bridge (both removed 2026-06-09: the gesture read as a second restless
   * idle, the bridge foot-slid against the fast physics acceleration).
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
    if (this._swimming) {
      // Surface locomotion: stroke while moving, tread while idle. The
      // vertical float is physics-driven, so both clips play in place.
      nextState = sample.moving ? 'swimming' : 'treadingWater';
    } else if (!this._grounded) {
      if (this._jumpClip) {
        // Deliberate jump — play the latched arc.
        nextState = this._jumpClip;
      } else if (this._airTime > 0.3) {
        // Walked off a ledge and genuinely falling.
        nextState = 'falling';
      } else {
        // Sub-300ms airborne blip (stepping off a rock) — hold the current
        // pose instead of flashing a jump/fall clip.
        return;
      }
    } else if (sample.moving) {
      if (this.controller.isCrouching && this.character.actions.crouchWalk) nextState = 'crouchWalk';
      else if (this.controller.isRunning) nextState = 'running';
      else nextState = 'walking';
    } else if (this._state === 'running' && this.character.actions.breathingIdle) {
      // Fresh stop from a RUN — catch breath before settling to the calm idle.
      nextState = 'breathingIdle';
      this._breathTimer = 0;
    } else if (this._state === 'breathingIdle'
      && this._breathTimer < Player.BREATH_AFTER_RUN_SECONDS) {
      nextState = 'breathingIdle'; // still catching breath
    } else {
      nextState = 'idle';
    }

    // Landed — release the takeoff latch so the next airborne frame without a
    // jump press reads as a fall, and so jump→locomotion can crossfade now.
    if (this._grounded && this._jumpClip && nextState !== this._jumpClip) {
      this._jumpClip = null;
    }

    if (nextState !== this._state) {
      // Jump takeoff: skip the clip's authored anticipation crouch and
      // compress the arc to the physics airtime, then let landing crossfade
      // straight back into whatever locomotion the player is holding.
      const jumpCfg = Player.JUMP_ANIM[nextState];
      if (jumpCfg) {
        this._state = nextState;
        this.character.play(nextState, { fade: 0.12, startAt: jumpCfg.startAt });
        const action = this.character.actions[nextState];
        if (action) action.timeScale = jumpCfg.timeScale;
        return;
      }
      // NO startWalking bridge from idle — the clip is a slow authored
      // acceleration while the body reaches full speed in ~0.15s, so it foot-
      // slides badly. A direct crossfade + the per-frame timeScale ramp below
      // gives the same pickup as the (good) run→walk transition.
      // Locomotion → idle reads smoother with a slightly longer crossfade;
      // the walk clip's timeScale is also approaching zero by this point,
      // so the longer fade hides the last-frame freeze. The breath → calm-idle
      // settle is slower still so the wind-down feels gradual.
      const swimBlend = nextState === 'swimming' || nextState === 'treadingWater'
        || this._state === 'swimming' || this._state === 'treadingWater';
      const exitingLoco = (this._state === 'walking' || this._state === 'running' || this._state === 'crouchWalk')
        && (nextState === 'idle' || nextState === 'breathingIdle');
      const settling = this._state === 'breathingIdle' && nextState === 'idle';
      this._state = nextState;
      this.character.play(
        nextState,
        swimBlend ? { fade: 0.35 } : settling ? { fade: 0.6 } : exitingLoco ? { fade: 0.3 } : undefined,
      );
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
    // Any external snap invalidates an in-flight edge grab — its cached bank
    // point is at the OLD location, so letting it run would pin the player
    // under the destination terrain and then drag them back across the world.
    if (this._edgeGrab) this.#abortEdgeGrab();
  }

  /** True while deep-water swim mode drives locomotion (App reads this). */
  get isSwimming() {
    return this._swimming;
  }

  /**
   * Replace the no-swim circles. App calls this once the GLB-ref-resolved
   * features exist (skills pond, lava pool) — see NO_SWIM_PONDS for the
   * mask-derived defaults active until then.
   */
  setNoSwimZones(zones) {
    this._noSwimZones = zones;
  }

  #inNoSwimZone(x, z) {
    for (const zone of this._noSwimZones) {
      const ddx = x - zone.x;
      const ddz = z - zone.z;
      if (ddx * ddx + ddz * ddz <= zone.r * zone.r) return true;
    }
    return false;
  }

  /** Zeroed controller sample for substeps where a sequence owns the body. */
  #stationarySample(delta) {
    return {
      velocity: new THREE.Vector3(),
      speed: 0,
      moving: false,
      facing: null,
      pureBackward: false,
      pureRight: false,
      pureLeft: false,
      delta,
    };
  }

  /**
   * Probe a fan of distances along the swim direction for the nearest dry
   * lip: ground at/above the waterline, low enough for the measured hold
   * pose, with the hold spot's own ground still submerged (so the hang
   * reads chest-at-the-waterline instead of arms floating over a slope).
   * Gentle beaches never qualify — their dry ground sits several metres
   * past swim-deep water, beyond the fan.
   */
  #maybeStartEdgeGrab(sample) {
    if (!this.terrain || !this.character?.actions?.swimmingToEdge) return;
    const sp = sample.speed;
    if (sp < 0.3) return;
    const dirX = sample.velocity.x / sp;
    const dirZ = sample.velocity.z / sp;
    let lipD = 0;
    let bankY = 0;
    for (
      let d = Player.EDGE_PROBE_MIN;
      d <= Player.EDGE_PROBE_MAX + 1e-6;
      d += Player.EDGE_PROBE_STEP
    ) {
      const b = this.terrain.heightAt(
        this.group.position.x + dirX * d,
        this.group.position.z + dirZ * d,
      );
      if (b >= Player.WATER_SURFACE_Y + 0.05) {
        if (b > Player.EDGE_BANK_MAX_Y) return; // wall too tall to grab
        lipD = d;
        bankY = b;
        break;
      }
    }
    if (!lipD) return;
    const lipX = this.group.position.x + dirX * lipD;
    const lipZ = this.group.position.z + dirZ * lipD;
    const holdX = lipX - dirX * Player.EDGE_HOLD_REACH;
    const holdZ = lipZ - dirZ * Player.EDGE_HOLD_REACH;
    if (this.terrain.heightAt(holdX, holdZ) > Player.EDGE_HOLD_MAX_GROUND) return;

    this._edgeGrab = {
      phase: 'approach',
      t: 0,
      fromX: this.group.position.x,
      fromZ: this.group.position.z,
      startY: this.group.position.y,
      holdX,
      holdZ,
      // Hold height puts the planted hands exactly on the bank lip; never
      // sink below the treading float to get there.
      grabY: Math.max(
        bankY - Player.EDGE_HANDS_ABOVE_ORIGIN,
        Player.WATER_SURFACE_Y - Player.TREAD_BODY_SINK,
      ),
      landX: lipX + dirX * Player.EDGE_CLIMB_FORWARD,
      landZ: lipZ + dirZ * Player.EDGE_CLIMB_FORWARD,
      // The validated lip — the climb falls back to it when the farther
      // landing spot turns out wet (thin wall) or a steep pop-up.
      probeX: lipX,
      probeZ: lipZ,
      bankY,
    };
    this._targetYaw = Math.atan2(dirX, dirZ); // square up to the bank
    this.controller.lock();
    this._actionLocked = true;
    this._state = 'swimmingToEdge';
    // Full clip from t=0 — the authored approach strokes cover the glide
    // up to the hold spot.
    this.character.play('swimmingToEdge', { fade: 0.3 });
  }

  /** Advance the approach → grab → boost sequence; called per substep instead of motion. */
  #updateEdgeGrab(delta) {
    const eg = this._edgeGrab;
    eg.t += delta;
    if (eg.phase === 'approach') {
      // Glide to the hold spot at the float height while the clip's authored
      // strokes play — speed varies with trigger distance, which reads as a
      // last reaching stroke rather than locomotion, so no timeScale sync.
      const f = Math.min(1, eg.t / Player.EDGE_APPROACH_TIME);
      this.#driveBodyTo(
        eg.fromX + (eg.holdX - eg.fromX) * f,
        eg.startY,
        eg.fromZ + (eg.holdZ - eg.fromZ) * f,
      );
      if (eg.t >= Player.EDGE_APPROACH_TIME) {
        eg.phase = 'grab';
        eg.t = 0;
      }
    } else if (eg.phase === 'grab') {
      const f = Math.min(1, eg.t / Player.EDGE_GRAB_RISE_TIME);
      const ease = f * (2 - f); // easeOutQuad — settle onto the hold
      this.#driveBodyTo(
        this.group.position.x,
        eg.startY + (eg.grabY - eg.startY) * ease,
        this.group.position.z,
      );
      if (eg.t >= Player.EDGE_GRAB_HOLD_TIME) {
        eg.phase = 'climb';
        eg.t = 0;
        eg.fromX = this.group.position.x;
        eg.fromY = this.group.position.y;
        eg.fromZ = this.group.position.z;
        eg.landY = this.terrain.heightAt(eg.landX, eg.landZ) + 0.02;
        // Thin spit / sharp rise beyond the probed lip — land on the
        // validated probe point instead of vaulting into water or popping up.
        if (
          eg.landY < Player.WATER_SURFACE_Y + 0.05
          || eg.landY > Player.EDGE_BANK_MAX_Y + 0.3
        ) {
          eg.landX = eg.probeX;
          eg.landZ = eg.probeZ;
          eg.landY = eg.bankY + 0.02;
        }
        // No authored climb-up exists — the idle crossfade over the short
        // boost arc reads as the pull-up.
        this.character.play('idle', { fade: 0.35 });
      }
    } else {
      const f = Math.min(1, eg.t / Player.EDGE_CLIMB_TIME);
      const s = f * f * (3 - 2 * f); // smoothstep
      const fy = Math.min(1, s * 1.6); // vertical leads — the arc reads up-then-over
      this.#driveBodyTo(
        eg.fromX + (eg.landX - eg.fromX) * s,
        eg.fromY + (eg.landY - eg.fromY) * fy,
        eg.fromZ + (eg.landZ - eg.fromZ) * s,
      );
      if (f >= 1) this.#endEdgeGrab();
    }
  }

  #driveBodyTo(x, y, z) {
    if (this.body?.teleport) this.body.teleport(x, y, z);
    this.group.position.set(x, y, z);
  }

  #endEdgeGrab() {
    this._edgeGrab = null;
    this._swimming = false;
    this._swimTime = 0;
    this.controller.swimMode = false;
    this.controller.unlock();
    this._actionLocked = false;
    this._grounded = true;
    this._verticalVelocity = 0;
    this._state = 'idle';
  }

  /** Cancel mid-sequence when an external system snaps the player away. */
  #abortEdgeGrab() {
    this._edgeGrab = null;
    this.controller.unlock();
    this._actionLocked = false;
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
    // No backflips/cartwheels/kicks while floating — the clips assume ground.
    if (this._swimming) return false;
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
