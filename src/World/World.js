import { Terrain } from './Terrain.js';
import { Nature } from './Nature.js';
import { Sky } from './Sky.js';
import { Birds } from './Birds.js';
import { Billboards, PROJECTS_CENTER } from '../Portfolio/Billboards.js';
import { Signs, SECTION_POSITIONS } from '../Portfolio/Signs.js';
import { Furniture } from '../Portfolio/Furniture.js';

/**
 * Top-level world. Grass-green terrain plane + sky are synchronous; nature
 * props (trees, rocks, real grass tufts, bushes, flowers, mushrooms, logs)
 * load async via loadAssets.
 *
 * Note: the shader-cone Grass class has been removed in favor of actual
 * Kenney grass-tuft models, placed via Nature.
 */
export class World {
  constructor(scene, loader) {
    this.scene = scene;
    this.terrain = new Terrain(scene, loader);
    this.sky = new Sky(scene);
    this.nature = null;
    this.billboards = null;
  }

  async loadAssets(loader, physics = null) {
    this.billboards = new Billboards(this.scene, physics, loader);
    this.signs = new Signs(this.scene, physics);
    this.nature = new Nature(this.scene, loader, this.terrain, physics);

    // Per-prop exclusions so trees never spawn right on top of a sign.
    for (const item of this.billboards.items) {
      this.nature.addExclusion(item.position.x, item.position.z, 3.5);
    }
    for (const item of this.signs.experienceItems) {
      this.nature.addExclusion(item.position.x, item.position.z, 2.5);
    }
    if (this.signs.skillsPosition) {
      this.nature.addExclusion(this.signs.skillsPosition.x, this.signs.skillsPosition.z, 4.5);
    }
    if (this.signs.contactPosition) {
      this.nature.addExclusion(this.signs.contactPosition.x, this.signs.contactPosition.z, 4.5);
    }

    // Larger zone-wide clearings so each cardinal section has breathing room
    // (the player approaches a section through a thinned-out grove rather
    // than a wall of trunks).
    this.nature.addExclusion(PROJECTS_CENTER.x, PROJECTS_CENTER.z, 12);
    this.nature.addExclusion(SECTION_POSITIONS.skills.x, SECTION_POSITIONS.skills.z, 9);
    this.nature.addExclusion(SECTION_POSITIONS.contact.x, SECTION_POSITIONS.contact.z, 8);
    // Spawn clearing.
    this.nature.addExclusion(0, 0, 9);
    // Water pond clearing.
    this.nature.addExclusion(-12, 18, 7);
    // Thin corridor along the experience trail going north — exclude trees
    // within 2.5u of the chain of sign positions, plus the segments between.
    for (let i = 0; i < SECTION_POSITIONS.experiencePath.length; i++) {
      const a = SECTION_POSITIONS.experiencePath[i];
      this.nature.addExclusion(a.x, a.z, 3);
    }

    const result = await this.nature.load();

    // Furniture loads after Nature so we know where the billboards are and
    // can register colliders alongside the rest of the world.
    this.furniture = new Furniture(this.scene, loader, physics, this.billboards);
    const furniturePlaced = await this.furniture.load().catch((err) => {
      console.warn('[Furniture] load failed', err);
      return 0;
    });

    // Birds — try to load a real GLB, fall back to procedural body.
    this.birds = new Birds(this.scene, loader);
    await this.birds.load(this.billboards, this.signs);

    return {
      nature: result,
      billboards: this.billboards.items.length,
      experience: this.signs.experienceItems.length,
      furniture: furniturePlaced,
    };
  }

  update(elapsed, camera = null, delta = 0) {
    if (camera) this.sky.update(camera.position);
    if (this.billboards) this.billboards.update(elapsed);
    if (this.birds) this.birds.update(delta, elapsed);
  }
}
