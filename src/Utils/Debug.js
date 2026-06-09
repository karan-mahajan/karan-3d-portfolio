/**
 * Classify a renderable object into a "system" bucket for draw-call attribution.
 * Prefers the merge/instancer markers GlbV3World stamps (`system:<name>` /
 * `merged:<name>`); otherwise falls back to the top-level (direct child of
 * scene) group name, then the nearest named ancestor, then the object type.
 */
function classifySystem(object) {
  let node = object;
  let nearestNamed = "";
  let topName = "";
  while (node && node.parent) {
    // node.parent === null ⇒ node IS the scene; stop one short of it.
    const name = node.name || "";
    if (name.startsWith("system:")) return name.slice("system:".length);
    if (name.startsWith("merged:")) return name; // already "merged:<system>"
    if (name && !nearestNamed) nearestNamed = name;
    if (node.parent.parent === null && name) topName = name; // direct child of scene
    node = node.parent;
  }
  return topName || nearestNamed || object.type || "unknown";
}

export class Debug {
  constructor() {
    const params = new URLSearchParams(window.location.search);
    this.enabled = params.has("debug");
    // `?debug=calls` adds per-system draw-call attribution (Phase-0 perf tool).
    this.attribute = params.get("debug") === "calls";
    this.hud = document.getElementById("debug-hud");
    this.frames = 0;
    this.lastTick = performance.now();
    this.fps = 0;
    this.renderer = null;
    this.scene = null;
    this.startedAt = performance.now();
    this._baselineLogged = false;
    this._lastTableAt = 0;
    // CPU update cost per frame (ms), set from App.#tick. Smoothed for display.
    this.cpuMs = 0;
    this.cpuSim = 0;
    this.cpuWorld = 0;
    if (!this.enabled && this.hud) this.hud.style.display = "none";
  }

  setRenderer(renderer) {
    this.renderer = renderer;
  }

  setScene(scene) {
    this.scene = scene;
  }

  /**
   * Per-frame CPU update cost (ms) from App.#tick, excluding the GPU submit.
   * Exponentially smoothed so the HUD number is readable. `total` = all JS
   * update work; `sim` = physics+player substeps; `world` = world+effects+UI.
   */
  setCpuTiming(total, sim, world) {
    if (!this.enabled) return;
    const a = 0.1; // smoothing
    this.cpuMs += (total - this.cpuMs) * a;
    this.cpuSim += (sim - this.cpuSim) * a;
    this.cpuWorld += (world - this.cpuWorld) * a;
  }

  /**
   * Walk the scene once and tally draw calls per system. Note: this counts
   * SCENE draw POTENTIAL (every `visible` renderable, pre frustum-cull), which
   * is intentionally different from `renderer.info.render.calls` (post-cull,
   * actual). Comparing the two shows how much culling already buys and which
   * systems dominate before/after Phase-2 visibility gating.
   * @returns {{rows: Array<{system:string, calls:number, objects:number, instances:number}>, total:number, shadowCalls:number}}
   */
  attributeDrawCalls() {
    const bySystem = new Map();
    let total = 0;
    let shadowCalls = 0;
    this.scene.traverse((o) => {
      if (!o.visible) return;
      if (!(o.isMesh || o.isInstancedMesh || o.isPoints || o.isLine || o.isSprite)) return;
      // Multi-material meshes submit one draw per material group.
      const draws = Array.isArray(o.material) ? Math.max(1, o.material.length) : 1;
      const system = classifySystem(o);
      const entry = bySystem.get(system) || { calls: 0, objects: 0, instances: 0 };
      entry.calls += draws;
      entry.objects += 1;
      entry.instances += o.isInstancedMesh ? o.count : 1;
      bySystem.set(system, entry);
      total += draws;
      if (o.castShadow) shadowCalls += draws; // re-submitted in the shadow depth pass
    });
    const rows = [...bySystem.entries()]
      .map(([system, e]) => ({ system, ...e }))
      .sort((a, b) => b.calls - a.calls);
    return { rows, total, shadowCalls };
  }

  tick() {
    if (!this.enabled) return;
    this.frames += 1;
    const now = performance.now();
    if (now - this.lastTick >= 500) {
      this.fps = Math.round((this.frames * 1000) / (now - this.lastTick));
      this.frames = 0;
      this.lastTick = now;
      if (this.hud) {
        if (this.renderer) {
          const r = this.renderer.info.render;
          const m = this.renderer.info.memory;
          const q = window.__quality?.name ?? "unknown";
          // r.drawCalls = THIS FRAME's draw calls (reset() zeroes it each
          // frame). r.calls is a LIFETIME cumulative counter (only zeroed on
          // dispose) — do NOT use it as a per-frame metric. r.frameCalls =
          // render() invocations this frame (main + shadow + water RTs + post).
          let text =
            `${this.fps} fps\n` +
            `quality ${q}\n` +
            `tris ${r.triangles.toLocaleString()}\n` +
            `draws ${r.drawCalls}/frame  (passes ${r.frameCalls})\n` +
            `cpu ${this.cpuMs.toFixed(1)}ms (sim ${this.cpuSim.toFixed(1)} world ${this.cpuWorld.toFixed(1)})\n` +
            `geos ${m.geometries}  tex ${m.textures}`;
          if (this.attribute && this.scene) {
            const { rows, total, shadowCalls } = this.attributeDrawCalls();
            const top = rows
              .slice(0, 5)
              .map((row) => `  ${row.calls} ${row.system}`)
              .join("\n");
            text +=
              `\n— scene draws ${total} (shadow ${shadowCalls}) —\n${top}`;
          }
          this.hud.textContent = text;
        } else {
          this.hud.textContent = `${this.fps} fps`;
        }
      }
      // Full sorted table to the console every ~2s in attribution mode.
      if (this.attribute && this.scene && now - this._lastTableAt >= 2000) {
        this._lastTableAt = now;
        const { rows, total, shadowCalls } = this.attributeDrawCalls();
        const r = this.renderer?.info.render;
        console.log(
          `=== DRAW-CALL ATTRIBUTION (scene potential ${total}, shadow re-submits ${shadowCalls}, actual ${r?.drawCalls}/frame across ${r?.frameCalls} passes) ===`,
        );
        console.table(rows);
      }
    }
    if (!this._baselineLogged && this.renderer && now - this.startedAt >= 3000) {
      this._baselineLogged = true;
      const r = this.renderer.info.render;
      const m = this.renderer.info.memory;
      console.log("=== PERFORMANCE BASELINE ===");
      console.log("Quality:", window.__quality?.name ?? "unknown");
      console.log("Triangles (this frame):", r.triangles);
      console.log("Draw calls (this frame):", r.drawCalls);
      console.log("Render passes (this frame):", r.frameCalls);
      console.log("Lifetime render.calls (cumulative — NOT per-frame):", r.calls);
      console.log("Points:", r.points);
      console.log("Textures:", m.textures);
      console.log("Geometries:", m.geometries);
      if (this.scene) {
        const { rows, total, shadowCalls } = this.attributeDrawCalls();
        console.log(
          `Scene draw potential: ${total} (shadow re-submits: ${shadowCalls})`,
        );
        console.table(rows);
      }
    }
  }
}
