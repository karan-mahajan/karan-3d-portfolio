import { GlbV3World } from "./GlbV3World.js";
import { Sky } from "./Sky.js";

/**
 * Top-level world facade. Wraps the v3 manifest-driven GlbV3World + Sky and
 * re-exposes the attribute names App.js + downstream consumers read (terrain,
 * nature, paths, billboards, signs, water, sky).
 *
 * v3 (B0/Phase B): monolithic geometry + terrain collision only. The v2
 * interaction layer (PortfolioMounts / ProjectShowcase / Signs) and runtime
 * Foliage are retired — sections + interactions are rebuilt from the blend's
 * section contract in Phase C, instancing + foliage in Phase E.
 */
export class World {
  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;
    this.sky = new Sky(scene);

    // GlbV3World is constructed synchronously; loadAssets() runs the parse.
    this.glb = new GlbV3World(scene, loader);

    // Facade attributes — proxy into GlbV3World. billboards/signs are stubs
    // until Phase C; foliage/water are null until Phase E/F.
    this.terrain = this.glb.terrain;
    this.nature = this.glb.nature;
    this.paths = this.glb.paths;
    this.billboards = this.glb.billboards;
    this.signs = this.glb.signs;
    this.foliage = null;
    this.water = null;
    // Grass mask (terrainGrass.exr) — populated by GlbV3World.load(); the
    // runtime Grass field samples it. Null until loadAssets() resolves.
    this.grassMask = null;
    this.grassGrid = this.glb.grassGrid;
  }

  async loadAssets(loader, physics = null, opts = {}) {
    await this.glb.load(physics, opts);
    this.grassMask = this.glb.grassMask;

    return {
      sections: Object.keys(this.glb.refs.sections).length,
      markers: Object.keys(this.glb.refs.markers).length,
      refs: this.glb.refs.all.length,
      pushSpots: this.glb.nature.pushSpots.length,
      paths: this.glb.paths.getTileCount(),
    };
  }

  update(elapsed, camera = null, delta = 0, playerPos = null) {
    this.glb.update(delta, playerPos);
    if (camera) this.sky.update(camera.position);
    if (this.billboards?.update) this.billboards.update(elapsed, playerPos, delta);
  }
}
