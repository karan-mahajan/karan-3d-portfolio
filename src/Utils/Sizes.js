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
    // Render-resolution ceiling. On retina/high-DPI this is the single biggest
    // sharpness lever (Bruno renders at 2.0) AND the biggest pixel cost (2.0 =
    // 4× the work of 1.0). App sets maxPixelRatio from the quality tier after
    // detection (capable → 2.0 Retina, weak → 1.0); the adaptive DPR controller
    // scales BELOW it under load. Defaults to 1.0 until the tier is applied.
    this.pixelRatio = Math.min(window.devicePixelRatio, this.maxPixelRatio ?? 1.0);
  }
}
