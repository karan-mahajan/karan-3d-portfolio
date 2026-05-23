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
    this.pixelRatio = Math.min(window.devicePixelRatio, 1.5);
  }
}
