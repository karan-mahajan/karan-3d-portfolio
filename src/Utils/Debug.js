export class Debug {
  constructor() {
    this.enabled = new URLSearchParams(window.location.search).has('debug');
    this.hud = document.getElementById('debug-hud');
    this.frames = 0;
    this.lastTick = performance.now();
    this.fps = 0;
    this.renderer = null;
    this.startedAt = performance.now();
    this._baselineLogged = false;
    if (!this.enabled && this.hud) this.hud.style.display = 'none';
  }

  setRenderer(renderer) {
    this.renderer = renderer;
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
          const q = window.__quality?.name ?? 'unknown';
          this.hud.textContent =
            `${this.fps} fps\n` +
            `quality ${q}\n` +
            `tris ${r.triangles.toLocaleString()}\n` +
            `calls ${r.calls}\n` +
            `geos ${m.geometries}  tex ${m.textures}`;
        } else {
          this.hud.textContent = `${this.fps} fps`;
        }
      }
    }
    if (!this._baselineLogged && this.renderer && now - this.startedAt >= 3000) {
      this._baselineLogged = true;
      const r = this.renderer.info.render;
      const m = this.renderer.info.memory;
      console.log('=== PERFORMANCE BASELINE ===');
      console.log('Quality:', window.__quality?.name ?? 'unknown');
      console.log('Triangles:', r.triangles);
      console.log('Draw calls:', r.calls);
      console.log('Points:', r.points);
      console.log('Textures:', m.textures);
      console.log('Geometries:', m.geometries);
    }
  }
}
