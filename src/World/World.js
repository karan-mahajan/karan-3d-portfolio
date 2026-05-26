import { GlbWorld } from './GlbWorld.js';
import { Sky } from './Sky.js';
import { setSectionPositions } from './SectionPositions.js';

/**
 * Top-level world facade. Wraps GlbWorld + Sky and (in later phases)
 * PortfolioMounts + ProjectShowcase + WorldLights + WorldWater. Re-exposes
 * the legacy attribute names (terrain, nature, paths, billboards, signs,
 * water, sky) so App.js + downstream consumers don't need rewriting.
 */
export class World {
  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;
    this.sky = new Sky(scene);

    // GlbWorld is constructed synchronously; loadAssets() runs the parse.
    this.glb = new GlbWorld(scene, loader);

    // Facade attributes — referenced by App.js and downstream. They proxy
    // into GlbWorld today; later phases swap in real PortfolioMounts /
    // ProjectShowcase / WorldLights / WorldWater objects.
    this.terrain     = this.glb.terrain;
    this.nature      = this.glb.nature;
    this.paths       = this.glb.paths;
    this.billboards  = this.glb.billboards;
    this.signs       = this.glb.signs;
    this.water       = null; // assigned in Phase 5
  }

  async loadAssets(loader, physics = null, { playerUniforms = null } = {}) {
    await this.glb.load(physics);
    setSectionPositions(this.glb.refs);

    if (playerUniforms) this.glb.nature.setPlayerUniforms(playerUniforms);

    return {
      nature:     this.glb.nature.pushSpots.length,
      billboards: 0,                              // populated in Phase 3
      experience: 0,                              // populated in Phase 2
      paths:      this.glb.paths.getTileCount(),
    };
  }

  update(elapsed, camera = null, delta = 0, playerPos = null) {
    if (camera) this.sky.update(camera.position);
    // billboards.update is wired in Phase 3 once ProjectShowcase exists.
    if (this.billboards?.update) this.billboards.update(elapsed, playerPos, delta);
  }
}
