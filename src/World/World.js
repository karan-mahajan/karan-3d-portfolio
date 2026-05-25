import { Terrain } from './Terrain.js';
import { Nature } from './Nature.js';
import { Paths } from './Paths.js';
import { Sky } from './Sky.js';
import { Billboards, PROJECTS_CENTER } from '../Portfolio/Billboards.js';
import { Signs, SECTION_POSITIONS } from '../Portfolio/Signs.js';
import { INTERACTABLE_PROP_EXCLUSIONS } from '../Portfolio/Interactables.js';
import { Water } from '../Effects/Water.js';

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

  async loadAssets(loader, physics = null, { playerUniforms = null } = {}) {
    this.billboards = new Billboards(this.scene, physics, loader, this.terrain);
    this.signs = new Signs(this.scene, physics, this.terrain);
    this.nature = new Nature(this.scene, loader, this.terrain, physics);
    if (playerUniforms) this.nature.setPlayerUniforms(playerUniforms);

    // Plan path tiles synchronously and register their no-spawn circles on
    // Nature BEFORE its scatter runs. Actual tile GLBs load below. Physics
    // is passed so each loaded tile gets a thin static collider — without
    // it the player's feet sink visually into the top of every path stone.
    this.paths = new Paths(this.scene, loader, this.terrain, physics);
    this.paths.addExclusionsTo(this.nature);

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
    // Thin corridor along the experience trail going north — exclude trees
    // within 2.5u of the chain of sign positions, plus the segments between.
    for (let i = 0; i < SECTION_POSITIONS.experiencePath.length; i++) {
      const a = SECTION_POSITIONS.experiencePath[i];
      this.nature.addExclusion(a.x, a.z, 3);
    }

    // ── Ocean ───────────────────────────────────────────────────────────────
    // Single shader-driven plane surrounding the island. The land mass
    // itself rises above the water; see Terrain.#displaceVertices for the
    // island shape (radius ~45 with a sandy shore slope to y=-2 by ~r=60).
    this.water = new Water(this.scene, loader, this.terrain);
    // Hand the physics world to Water so loadShoreDecor() can register
    // colliders for solid shore rocks (lily pads + reeds remain walk-through).
    if (physics) this.water.setPhysics(physics);

    // Interactable prop spots — keep trees clear so the player can see them
    // and the prompts have room to read. Coordinates mirror Interactables.js.
    for (const e of INTERACTABLE_PROP_EXCLUSIONS) {
      this.nature.addExclusion(e.x, e.z, Math.max(e.r, 3));
    }

    const result = await this.nature.load();

    const pathsResult = await this.paths.load().catch((err) => {
      console.warn('[Paths] load failed', err);
      return { placed: 0 };
    });

    // Shore decor (lily pads, half-submerged rocks, reeds) along the
    // island waterline. Fire-and-forget — missing GLBs are skipped per-file
    // inside loadShoreDecor() so a single 404 doesn't block boot.
    this.water.loadShoreDecor().catch((err) => {
      console.warn('[Water] shore decor failed', err);
    });

    return {
      nature: result,
      billboards: this.billboards.items.length,
      experience: this.signs.experienceItems.length,
      paths: pathsResult.placed,
    };
  }

  update(elapsed, camera = null, delta = 0, playerPos = null) {
    if (camera) this.sky.update(camera.position);
    if (this.billboards) this.billboards.update(elapsed, playerPos, delta);
  }
}
