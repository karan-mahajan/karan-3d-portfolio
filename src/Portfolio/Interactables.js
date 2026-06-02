import * as THREE from 'three/webgpu';

// Kept only so the (optional) grass-flatten exclusion import in App.js keeps
// resolving. v3 keeps a single interactable — the kickable football — and
// everything else (props, paving, lights) comes from the Blender world.
export const INTERACTABLE_PROP_EXCLUSIONS = [
  { x: 7, z: -8, r: 1.2 }, // football
];

/**
 * World-object props the player can interact with via ActionPrompts.
 *
 * v3: the v2 prop set (stuck crate, punching bag, dance tile, chalk circle,
 * dock + backflip, disappointed sign + trophy) was removed — those were placed
 * at hardcoded v2-world coordinates and dropped phantom colliders that blocked
 * movement in the Blender-authored world. Only the **football** remains: a
 * kickable dynamic ball with no static blocker (walking into it just nudges it).
 */
export class Interactables {
  constructor(scene, loader, physics, actionPrompts, terrain = null) {
    this.scene = scene;
    this.loader = loader;
    this.physics = physics;
    this.prompts = actionPrompts;
    // Terrain heightfield (Terrain.heightAt) — props sample heightAt(x,z) so
    // they sit ON the ground; also used by the football's rolling clamp.
    this.terrain = terrain;

    this.football = null; // { mesh, kick(yaw), update(delta) }
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
  }

  async load() {
    await Promise.allSettled([this.#buildFootball()]);
  }

  update(delta) {
    if (this.football) this.football.update(delta);
  }

  // ── Football (kick) ──────────────────────────────────────────────────────

  async #buildFootball() {
    const url = '/models/extras/soccer-ball/scene.gltf';
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(url);
    } catch (e) {
      console.warn('[Interactables] football missing — skipping');
      return;
    }
    const obj = gltf.scene;

    // Scale up to ~0.5m diameter — a real-world soccer ball (0.22m) reads as a
    // pebble at game scale; this is closer to a beach ball and unmistakable
    // from a distance.
    obj.updateMatrixWorld(true);
    const rawBox = new THREE.Box3().setFromObject(obj);
    const rawSize = rawBox.getSize(new THREE.Vector3());
    const targetDiameter = 0.5;
    const rawMax = Math.max(rawSize.x, rawSize.y, rawSize.z) || 0.22;
    obj.scale.setScalar(targetDiameter / rawMax);

    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.x, size.y, size.z) / 2 || 0.25;

    const spawnX = 7, spawnZ = -8;
    const spawnGround = this.#groundY(spawnX, spawnZ);
    const startPos = new THREE.Vector3(spawnX, spawnGround + radius, spawnZ);
    obj.position.copy(startPos);
    obj.traverse((c) => {
      if (!c.isMesh) return;
      c.castShadow = true;
      c.receiveShadow = true;
      const materials = Array.isArray(c.material) ? c.material : [c.material];
      materials.forEach((material) => {
        if (!material?.isMeshStandardMaterial) return;
        material.emissive = new THREE.Color('#f8f2df');
        material.emissiveMap = material.map || material.emissiveMap;
        material.emissiveIntensity = Math.max(material.emissiveIntensity || 0, material.map ? 0.162 : 0.027);
        material.roughness = Math.min(material.roughness ?? 0.65, 0.55);
        material.needsUpdate = true;
      });
    });
    this.scene.add(obj);

    // Rapier dynamic body — the player's character controller has
    // setApplyImpulsesToDynamicBodies(true), so just walking into the ball
    // nudges it. Kick applies a forward+upward impulse.
    const physics = this.physics;
    const terrain = this.terrain;
    const WATER_SURFACE_Y = -0.15;     // matches Water.WATER_LEVEL_Y
    const GRAVITY = 25;                 // matches Physics.GRAVITY magnitude
    const RECOVERY_RADIUS = 50;        // ball further than this → respawn
    const RECOVERY_Y = -2.5;           // truly lost (sank past the ocean) → respawn
    const KICK_POWER = 6.0;            // forward impulse magnitude
    const KICK_LIFT = 2.2;             // upward impulse so the ball arcs
    const _tmpQ = new THREE.Quaternion();
    let body = null;
    if (physics) {
      body = physics.addDynamicBall(startPos.x, startPos.y, startPos.z, radius);
    }

    const respawn = () => {
      if (!body) return;
      const gy = this.#groundY(spawnX, spawnZ);
      body.setTranslation({ x: spawnX, y: gy + radius, z: spawnZ }, true);
      body.setLinvel({ x: 0, y: 0, z: 0 }, true);
      body.setAngvel({ x: 0, y: 0, z: 0 }, true);
    };

    const football = {
      mesh: obj,
      body,
      kick(yaw) {
        if (!body) return;
        const mass = body.mass();
        body.applyImpulse({
          x: Math.sin(yaw) * KICK_POWER * mass,
          y: KICK_LIFT * mass,
          z: Math.cos(yaw) * KICK_POWER * mass,
        }, true);
        body.applyTorqueImpulse({
          x: Math.cos(yaw) * KICK_POWER * mass * 0.15,
          y: 0,
          z: -Math.sin(yaw) * KICK_POWER * mass * 0.15,
        }, true);
      },
      respawn,
      update(_delta) {
        if (!body) return;
        const t = body.translation();
        // Buoyancy — when the ball is over water and dips below the surface,
        // push it back up (slightly more than gravity) with heavy damping so it
        // bobs on the surface instead of sinking. Outside water, restore the
        // default damping so it rolls normally.
        const overWater = terrain ? terrain.heightAt(t.x, t.z) < WATER_SURFACE_Y : false;
        const submersion = WATER_SURFACE_Y - (t.y - radius);
        if (overWater && submersion > 0) {
          const mass = body.mass();
          const sub = Math.min(submersion / (radius * 2), 1);
          const buoy = mass * GRAVITY * sub * 1.15;
          body.applyImpulse({ x: 0, y: buoy * _delta, z: 0 }, true);
          body.setLinearDamping(2.2);
          body.setAngularDamping(1.6);
        } else {
          body.setLinearDamping(0.6);
          body.setAngularDamping(0.55);
        }
        if (t.y < RECOVERY_Y || (t.x * t.x + t.z * t.z) > RECOVERY_RADIUS * RECOVERY_RADIUS) {
          respawn();
          return;
        }
        obj.position.set(t.x, t.y, t.z);
        const r = body.rotation();
        _tmpQ.set(r.x, r.y, r.z, r.w);
        obj.quaternion.copy(_tmpQ);
      },
    };
    this.football = football;

    // Pass `obj.position` (live, mutated each frame) so the kick prompt follows
    // the ball as it rolls.
    this.prompts.add({
      id: 'football',
      position: obj.position,
      radius: 1.8,
      label: 'Kick (E)',
      mode: 'oneShot',
      action: 'kickFootball',
      onActivate: () => {
        const yaw = this.prompts.player.group.rotation.y;
        this.prompts.achievements?.onFootballKick?.();
        setTimeout(() => {
          football.kick(yaw);
          this.prompts.audio?.playKick();
        }, 350);
      },
    });
  }
}
