import * as THREE from 'three/webgpu';

/**
 * Phase F animated decorations driven by CPU transforms (cheap — 4 animals +
 * 2 air dancers). Both read their config from references.glb empties; the
 * GEOMETRY already loaded with the monolithic miscFx GLB, so this class locates
 * the meshes by name and animates them in place.
 *
 * Animals (`animalPivot_{cat,dog,deer,rabbit}`): each animal is a flat set of
 * loose body-part meshes named `animal_<species>_*` parented to the scene root
 * (NOT to the pivot). They're re-parented into one runtime group per animal
 * (group.attach preserves world transform), which then wanders within
 * wanderRadius of its home and bobs idly, grounded on the terrain heightfield.
 *
 * Air dancers (`airDancerPivot_00/01`): the inflatable tube is 5 segment meshes
 * in a parent→child CHAIN (`airDancerSeg_NN_1..4`, each +0.64 m in Y). Applying
 * an incremental rotation per segment makes the chain whip cumulatively — base
 * segment _0 stays planted. Sway params come from the pivot extras.
 */

const DEG2RAD = Math.PI / 180;

const ANIMAL_SPECIES = ['cat', 'dog', 'deer', 'rabbit'];

export class AnimatedProps {
  /**
   * @param {THREE.Scene} scene
   * @param {{ heightAt:(x:number,z:number)=>number }} terrain
   * @param {{ byName: Map<string, any> }} refs
   * @param {import('../Physics/Physics.js').Physics} physics
   */
  constructor(scene, terrain, refs, physics) {
    this.scene = scene;
    this.terrain = terrain;
    this.physics = physics;
    this._playerPos = null;
    this.animals = [];
    this.dancers = [];

    for (const species of ANIMAL_SPECIES) this.#buildAnimal(species, refs);
    for (const id of ['00', '01']) this.#buildDancer(id, refs);
  }

  // ── Animals ─────────────────────────────────────────────────────────────────
  #buildAnimal(species, refs) {
    // Collect every loose part mesh first — re-parenting mutates the tree.
    const prefix = `animal_${species}_`;
    const parts = [];
    let body = null;
    this.scene.traverse((o) => {
      if (o.isMesh && o.name.startsWith(prefix)) {
        parts.push(o);
        if (o.name === `${prefix}body`) body = o;
      }
    });
    if (!parts.length) return;

    const anchorSrc = body ?? parts[0];
    const w = new THREE.Vector3();
    anchorSrc.getWorldPosition(w);
    const groundY = this.#groundY(w.x, w.z);

    const group = new THREE.Group();
    group.name = `animalRig_${species}`;
    group.position.set(w.x, groundY, w.z);
    this.scene.add(group);
    // attach() keeps each part's world transform → they stay exactly where the
    // Blender export placed them, now expressed relative to the rig origin.
    for (const part of parts) group.attach(part);

    const ref = refs?.byName?.get(`animalPivot_${species}`);
    const ex = ref?.extras ?? ref?.object3d?.userData ?? {};
    const wanderRadius = ex.wanderRadius ?? 3;

    // Solid collider that FOLLOWS the wandering animal so the player can't walk
    // through it. Kinematic cylinder sized from the assembled body bbox; driven
    // each frame in #updateAnimal via setNextKinematicTranslation.
    let colBody = null;
    let colOffsetY = 0;
    if (this.physics?.addKinematicCylinder) {
      const box = new THREE.Box3().setFromObject(group);
      const size = box.getSize(new THREE.Vector3());
      const center = box.getCenter(new THREE.Vector3());
      const radius = Math.max(0.2, Math.max(size.x, size.z) / 2);
      const halfHeight = Math.max(0.15, size.y / 2);
      colOffsetY = center.y - group.position.y; // rig-origin → bbox-centre lift
      colBody = this.physics.addKinematicCylinder(center.x, center.y, center.z, radius, halfHeight);
    }

    this.animals.push({
      group,
      body: colBody,
      colOffsetY,
      home: new THREE.Vector2(w.x, w.z),
      wanderRadius,
      // gentle per-species pacing
      speed: species === 'deer' ? 1.1 : species === 'dog' ? 0.9 : 0.6,
      bobAmp: species === 'rabbit' ? 0.07 : 0.04,
      bobFreq: species === 'rabbit' ? 5.0 : 2.2,
      phase: Math.random() * Math.PI * 2,
      target: new THREE.Vector2(w.x, w.z),
      pauseT: Math.random() * 2,
      heading: 0,
    });
  }

  #groundY(x, z) {
    const h = this.terrain?.heightAt?.(x, z);
    return Number.isFinite(h) ? h : 0;
  }

  #updateAnimal(a, dt, elapsed) {
    const g = a.group;
    a.pauseT -= dt;

    // Pick a fresh wander target when paused-out or arrived.
    const dx = a.target.x - g.position.x;
    const dz = a.target.y - g.position.z;
    const dist = Math.hypot(dx, dz);
    if (a.pauseT <= 0 && dist < 0.15) {
      // Steer away from the player if they're crowding the animal, otherwise
      // pick a random spot inside the home circle.
      const pp = this._playerPos;
      const fleeing = pp && Math.hypot(g.position.x - pp.x, g.position.z - pp.z) < 2.0;
      let ang;
      let r;
      if (fleeing) {
        ang = Math.atan2(g.position.z - pp.z, g.position.x - pp.x); // directly away
        r = a.wanderRadius;
        a.pauseT = 0.3;
      } else {
        ang = Math.random() * Math.PI * 2;
        r = Math.sqrt(Math.random()) * a.wanderRadius;
        a.pauseT = 1.5 + Math.random() * 3; // idle a beat after arriving
      }
      a.target.set(a.home.x + Math.cos(ang) * r, a.home.y + Math.sin(ang) * r);
    }

    let moving = false;
    if (dist > 0.15) {
      const step = Math.min(a.speed * dt, dist);
      g.position.x += (dx / dist) * step;
      g.position.z += (dz / dist) * step;
      moving = true;
      // Turn smoothly to face travel direction.
      const want = Math.atan2(dx, dz);
      let d = want - a.heading;
      d = Math.atan2(Math.sin(d), Math.cos(d)); // wrap to [-π,π]
      a.heading += d * Math.min(1, dt * 6);
      g.rotation.y = a.heading;
    }

    // Ground-follow + idle/hop bob.
    const bob = Math.sin(elapsed * a.bobFreq + a.phase) * a.bobAmp * (moving ? 1.4 : 1);
    g.position.y = this.#groundY(g.position.x, g.position.z) + Math.max(0, bob);

    // Drag the kinematic collider along so it stays centred on the animal.
    if (a.body) {
      a.body.setNextKinematicTranslation({
        x: g.position.x,
        y: g.position.y + a.colOffsetY,
        z: g.position.z,
      });
    }
  }

  // ── Air dancers ──────────────────────────────────────────────────────────────
  #buildDancer(id, refs) {
    const segs = [];
    for (let i = 1; i <= 4; i++) {
      const seg = this.scene.getObjectByName(`airDancerSeg_${id}_${i}`);
      if (seg) segs.push(seg);
    }
    if (!segs.length) return;

    // Static pole collider at the base so the player can't walk through the
    // dancer (the tube only sways in place — it never translates).
    const base = this.scene.getObjectByName(`airDancerSeg_${id}_0`);
    if (this.physics?.addStaticCylinder && base) {
      const w = new THREE.Vector3();
      base.getWorldPosition(w);
      this.physics.addStaticCylinder(w.x, this.#groundY(w.x, w.z), w.z, 0.35, 2.6);
    }

    const ref = refs?.byName?.get(`airDancerPivot_${id}`);
    const ex = ref?.extras ?? ref?.object3d?.userData ?? {};
    this.dancers.push({
      segs,
      amp: (ex.swayAmplitudeDeg ?? 22) * DEG2RAD,
      speed: ex.swaySpeed ?? 1.6,
      flail: ex.flail !== false,
      phase: id === '01' ? Math.PI : 0, // desync the two dancers
    });
  }

  #updateDancer(d, elapsed) {
    const t = elapsed * d.speed + d.phase;
    for (let i = 0; i < d.segs.length; i++) {
      const seg = d.segs[i];
      // Higher segments swing more (the tube whips at the top). Because the
      // segments are chained, each rotation compounds onto its parent's.
      const w = (i + 1) / d.segs.length;
      const wob = d.flail ? (1 + 0.4 * Math.sin(t * 3.3 + i)) : 1;
      seg.rotation.x = Math.sin(t + i * 0.7) * d.amp * w * wob;
      seg.rotation.z = Math.cos(t * 0.9 + i * 0.5) * d.amp * w * 0.8 * wob;
    }
  }

  /** Player world position for the animals' light avoidance (App feeds it each frame). */
  setPlayerPos(pos) {
    if (pos) this._playerPos = pos;
  }

  update(elapsed, delta) {
    for (const a of this.animals) this.#updateAnimal(a, delta, elapsed);
    for (const d of this.dancers) this.#updateDancer(d, elapsed);
  }

  dispose() {
    for (const a of this.animals) this.scene.remove(a.group);
    this.animals = [];
    this.dancers = [];
  }
}
