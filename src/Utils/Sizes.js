export class Sizes extends EventTarget {
  constructor() {
    super();
    this.update();
    window.addEventListener('resize', () => {
      this.update();
      this.dispatchEvent(new Event('resize'));
    });
  }

  update() {
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.aspect = this.width / this.height;
    // Capped at 1.0 (was 1.5). On retina/high-DPI displays this is the
    // single biggest perf win: 1.5× ratio means 2.25× the pixel work per
    // frame vs 1.0×. The visual softening is barely noticeable on a
    // stylized scene; lighting/post-FX cost drops proportionally.
    this.pixelRatio = Math.min(window.devicePixelRatio, 1.0);
  }
}
