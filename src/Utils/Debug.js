export class Debug {
  constructor() {
    this.enabled = new URLSearchParams(window.location.search).has('debug');
    this.hud = document.getElementById('debug-hud');
    this.frames = 0;
    this.lastTick = performance.now();
    this.fps = 0;
    if (!this.enabled && this.hud) this.hud.style.display = 'none';
  }

  tick() {
    if (!this.enabled) return;
    this.frames += 1;
    const now = performance.now();
    if (now - this.lastTick >= 500) {
      this.fps = Math.round((this.frames * 1000) / (now - this.lastTick));
      this.frames = 0;
      this.lastTick = now;
      if (this.hud) this.hud.textContent = `${this.fps} fps`;
    }
  }
}
