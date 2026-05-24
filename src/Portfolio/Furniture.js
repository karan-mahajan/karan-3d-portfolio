import * as THREE from 'three';

/**
 * Workstation props placed in front of each project billboard so the cluster
 * reads as a "developer's desk" the player walks up to. Each billboard gets a
 * unique combination of desk + screen + chair + accent so the line doesn't
 * feel like a copy/paste.
 *
 * Layout per billboard (positions in local frame, then transformed to world
 * by the billboard's yaw — billboard faces origin, so "in front" means
 * toward the player approach):
 *
 *   billboard
 *      │
 *      ▼ (desk, monitor on top)        ← forward 2.0 units
 *      ▼ (chair)                       ← forward 3.4 units (faces billboard)
 *      ▼ (player approach)
 */

// targetMax: the longest dimension the model should occupy in world units. If
// the loaded GLB exceeds that, it gets auto-scaled down (some Kenney items
// arrive at 5–10× the expected scale and would otherwise dwarf the scene).
const SETS = [
  {
    desk:   { url: '/models/furniture/desk.glb',          targetMax: 1.6, y: 0 },
    screen: { url: '/models/furniture/monitor.glb',       targetMax: 0.7, y: 0.74 },
    chair:  { url: '/models/furniture/office-chair.glb',  targetMax: 1.2, y: 0 },
    accent: { url: '/models/furniture/standing-lamp.glb', targetMax: 1.7, y: 0, side: -1, offset: 1.4 },
  },
  {
    desk:   { url: '/models/furniture/desk-1.glb',           targetMax: 1.6, y: 0 },
    screen: { url: '/models/furniture/laptop.glb',           targetMax: 0.6, y: 0.74 },
    chair:  { url: '/models/furniture/chair.glb',            targetMax: 1.1, y: 0 },
    accent: { url: '/models/furniture/lampsquarefloor.glb',  targetMax: 1.6, y: 0, side:  1, offset: 1.4 },
  },
  {
    desk:   { url: '/models/furniture/table.glb',           targetMax: 1.6, y: 0 },
    screen: { url: '/models/furniture/computerscreen.glb',  targetMax: 0.7, y: 0.74 },
    chair:  { url: '/models/furniture/stool.glb',           targetMax: 0.8, y: 0 },
    accent: { url: '/models/furniture/pottedplant.glb',     targetMax: 0.9, y: 0, side: -1, offset: 1.4 },
  },
  {
    desk:   { url: '/models/furniture/desk-2.glb',          targetMax: 1.6, y: 0 },
    screen: { url: '/models/furniture/screen-flat.glb',     targetMax: 0.8, y: 0.74 },
    chair:  { url: '/models/furniture/office-chair-1.glb',  targetMax: 1.2, y: 0 },
    accent: { url: '/models/furniture/plantsmall1.glb',     targetMax: 0.7, y: 0, side:  1, offset: 1.4 },
  },
  {
    desk:   { url: '/models/furniture/deskcorner.glb',          targetMax: 1.8, y: 0 },
    screen: { url: '/models/furniture/televisionmodern.glb',    targetMax: 0.9, y: 0.74 },
    chair:  { url: '/models/furniture/chaircushion.glb',        targetMax: 1.1, y: 0 },
    accent: { url: '/models/furniture/speaker.glb',             targetMax: 0.5, y: 0, side: -1, offset: 1.4 },
  },
];

// Forward offsets from the billboard (in the direction it faces, which is
// also the player-approach direction).
const DESK_FORWARD = 2.4;
const CHAIR_FORWARD = 3.8;

export class Furniture {
  constructor(scene, loader, physics, billboards, terrain = null) {
    this.scene = scene;
    this.loader = loader;
    this.physics = physics;
    this.billboards = billboards;
    // Desks sit in front of the billboards (distance ~36 from spawn); terrain
    // there is ~0.46m above y=0, so without this they float / sink relative
    // to the visible ground.
    this.terrain = terrain;
    this.placed = [];
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
  }

  async load() {
    if (!this.billboards || this.billboards.items.length === 0) return 0;
    const tasks = [];
    for (let i = 0; i < this.billboards.items.length; i++) {
      const billboard = this.billboards.items[i];
      const set = SETS[i % SETS.length];
      tasks.push(this.#placeOne(billboard, set, i));
    }
    const results = await Promise.allSettled(tasks);
    return results.filter((r) => r.status === 'fulfilled').length;
  }

  async #placeOne(billboard, set, index) {
    // Direction the billboard faces (toward origin) → "forward" for furniture.
    const bx = billboard.position.x;
    const bz = billboard.position.z;
    const len = Math.hypot(bx, bz) || 1;
    const fx = -bx / len;
    const fz = -bz / len;
    // Sideways vector (perpendicular, right-hand).
    const sx = -fz;
    const sz =  fx;
    // The billboard's local +Z faces origin → yaw used so far.
    const billYaw = Math.atan2(-bx, -bz);

    // ── Desk ─────────────────────────────────────────────────────────────
    const deskX = bx + fx * DESK_FORWARD;
    const deskZ = bz + fz * DESK_FORWARD;
    const deskGround = this.#groundY(deskX, deskZ);
    const desk = await this.#loadAt(set.desk, {
      x: deskX,
      y: deskGround + set.desk.y,
      z: deskZ,
      yaw: billYaw,
    });

    // Measure desk's top so the screen sits on it cleanly. deskBox is in world
    // coords, so deskTopY is already lifted by deskGround above.
    const deskBox = new THREE.Box3().setFromObject(desk);
    const deskTopY = deskBox.max.y;

    // ── Screen on desk ───────────────────────────────────────────────────
    const screen = await this.#loadAt(set.screen, {
      x: deskX,
      y: deskTopY,
      z: deskZ,
      // Screen faces the chair (away from billboard) → yaw rotated 180°.
      yaw: billYaw + Math.PI,
    });

    // ── Chair behind desk ────────────────────────────────────────────────
    const chairX = bx + fx * CHAIR_FORWARD;
    const chairZ = bz + fz * CHAIR_FORWARD;
    const chairGround = this.#groundY(chairX, chairZ);
    const chair = await this.#loadAt(set.chair, {
      x: chairX,
      y: chairGround + set.chair.y,
      z: chairZ,
      // Chair faces the billboard (its occupant looks toward the screen).
      yaw: billYaw,
    });

    // ── Accent prop (lamp / plant / speaker) ─────────────────────────────
    const acc = set.accent;
    const accSide = acc.side ?? 1;
    const accOffset = acc.offset ?? 1.2;
    const accX = deskX + sx * accSide * accOffset;
    const accZ = deskZ + sz * accSide * accOffset;
    await this.#loadAt(acc, {
      x: accX,
      y: this.#groundY(accX, accZ) + acc.y,
      z: accZ,
      yaw: billYaw,
    });

    // ── Physics colliders for the chunky items ───────────────────────────
    // Desk: a cuboid the size of its bounding box. Centre = midpoint of the
    // bbox in Y (deskGround + deskHy).
    if (this.physics) {
      const deskSize = deskBox.getSize(new THREE.Vector3());
      const deskHy = (deskTopY - deskGround) / 2;
      this.physics.addStaticCuboid(
        deskX, deskGround + deskHy, deskZ,
        deskSize.x / 2, deskHy, deskSize.z / 2,
        billYaw,
      );
      // Chair: smaller cuboid (so the player can lean against it). Half-height
      // 0.45 → centre = chairGround + 0.45.
      this.physics.addStaticCuboid(
        chairX, chairGround + 0.45, chairZ,
        0.35, 0.45, 0.35,
        billYaw,
      );
    }

    this.placed.push({ billboard, desk, screen, chair });
  }

  async #loadAt(modelDef, { x, y, z, yaw }) {
    const gltf = await this.loader.loadGLTF(modelDef.url);
    const obj = gltf.scene;

    // First measure the model at its native scale, then scale-to-fit a
    // sensible per-category target. Kenney's furniture pack has wildly
    // inconsistent native scales (some at 1m, some at 5m+).
    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z) || 1;
    const target = modelDef.targetMax ?? 1.2;
    const fitScale = target / maxDim;
    obj.scale.setScalar(fitScale);

    obj.position.set(x, y, z);
    obj.rotation.y = yaw;
    obj.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    this.scene.add(obj);
    return obj;
  }
}
