import { PortfolioMounts } from "../Portfolio/PortfolioMounts.js";
import { ProjectShowcase } from "../Portfolio/ProjectShowcase.js";
import { Foliage } from "./Foliage.js";
import { GlbWorld } from "./GlbWorld.js";
import { SECTION_POSITIONS, setSectionPositions } from "./SectionPositions.js";
import { Sky } from "./Sky.js";

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
    this.terrain = this.glb.terrain;
    this.nature = this.glb.nature;
    this.paths = this.glb.paths;
    this.billboards = this.glb.billboards;
    this.signs = this.glb.signs;
    this.water = null; // assigned in Phase 5
  }

  async loadAssets(
    loader,
    physics = null,
    { playerUniforms = null, wind = null } = {},
  ) {
    await this.glb.load(physics);
    setSectionPositions(this.glb.refs);

    if (playerUniforms) this.glb.nature.setPlayerUniforms(playerUniforms);

    // Phase 2 — PortfolioMounts replaces the Signs.js stub. Mounts panels
    // onto Blender artifact meshes via refs collected during glb.load().
    this.portfolioMounts = new PortfolioMounts(
      this.scene,
      this.glb.refs,
      SECTION_POSITIONS,
    );
    this.signs = this.portfolioMounts;

    // Phase 3 — ProjectShowcase replaces the GlbWorld billboards stub. The
    // showcase mesh is anchored to refShowcaseMount (Blender Phase 4
    // workshop pavilion), not to hardcoded XZ constants.
    this.projectShowcase = new ProjectShowcase(
      this.scene,
      this.glb.refs,
      loader,
      this.glb.terrain,
    );
    this.billboards = this.projectShowcase;

    // Phase 4 — Foliage replaces baked canopies (stripped by phase-11c) with
    // runtime SDF-quad clouds. Needs the shared wind so its UV-rotation
    // shimmer stays in lockstep with grass / wind-lines.
    try {
      const sdf = await loader.loadTexture("/textures/foliage/foliageSDF.png");
      this.foliage = new Foliage(this.scene, this.glb.refs.foliage, sdf, wind);
    } catch (err) {
      console.warn("[World] Foliage init skipped:", err?.message || err);
      this.foliage = null;
    }

    return {
      nature: this.glb.nature.pushSpots.length,
      billboards: this.projectShowcase.items.length,
      experience: this.portfolioMounts.experienceItems.length,
      paths: this.glb.paths.getTileCount(),
      foliage: this.foliage?.meshes?.length ?? 0,
    };
  }

  update(elapsed, camera = null, delta = 0, playerPos = null) {
    if (camera) this.sky.update(camera.position);
    // billboards.update is wired in Phase 3 once ProjectShowcase exists.
    if (this.billboards?.update)
      this.billboards.update(elapsed, playerPos, delta);
  }
}
