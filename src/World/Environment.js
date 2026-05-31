import * as THREE from 'three/webgpu';

/**
 * Sky-derived image-based lighting (IBL).
 *
 * Renders the gradient {@link Sky} into a PMREM so `scene.environment` carries
 * the world's OWN sky colours. Without this, the consolidated
 * `MeshStandardNodeMaterial` props receive zero indirect light and read flat /
 * "pasted-on". Deriving the env from the sky (rather than a foreign HDRI) means
 * the ambient tone always matches the current sky — cohesion for free, and it
 * re-colours automatically through the day/night cycle.
 *
 * Applied GLOBALLY via `scene.environmentIntensity` (kept low so it adds form,
 * not wash). This is rule-safe: it touches NO material — node materials read
 * `scene.environment` automatically, so the consolidated / name-looked-up
 * animated meshes (skillSphere/lava/miscFx/bonfire/terrain) are untouched.
 */
export class Environment {
  #renderer;
  #scene;
  #pmrem;
  #skyScene;
  #skyMat;
  #rt = null;
  // Regen throttle: only rebuild when the sky colours actually moved, and at
  // most once every N frames so a continuous cycle doesn't rebuild every frame.
  #lastSum = -1;
  #framesSinceRegen = 1e6;

  /**
   * @param {THREE.WebGPURenderer} renderer
   * @param {THREE.Scene} scene - the main scene whose `.environment` we drive
   * @param {THREE.Material} skyMaterial - the live Sky gradient material (shared
   *   so the PMREM re-colours with the cycle)
   * @param {object} [opts]
   * @param {number} [opts.intensity=0.35] - global environmentIntensity
   * @param {number} [opts.size=128] - PMREM cube size (128 is plenty for soft IBL)
   * @param {number} [opts.minRegenInterval=12] - min frames between rebuilds
   */
  constructor(renderer, scene, skyMaterial, { intensity = 0.35, size = 128, minRegenInterval = 12 } = {}) {
    this.#renderer = renderer;
    this.#scene = scene;
    this.#skyMat = skyMaterial;
    this.size = size;
    this.minRegenInterval = minRegenInterval;
    this._intensity = intensity;

    this.#pmrem = new THREE.PMREMGenerator(renderer);

    // Dedicated tiny scene: a BackSide sky sphere centred at the origin sharing
    // the live Sky material. PMREM's cube camera renders from the origin, so a
    // fragment's view direction = normalize(positionWorld) → the gradient is
    // captured by direction exactly like an env map should be.
    this.#skyScene = new THREE.Scene();
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(10, 24, 12), skyMaterial);
    this.#skyScene.add(mesh);

    scene.environmentIntensity = intensity;
  }

  /** Global IBL strength. Lower it at night so the dark sky doesn't over-fill. */
  set intensity(value) {
    this._intensity = value;
    this.#scene.environmentIntensity = value;
  }

  get intensity() {
    return this._intensity;
  }

  /** Cheap signature of the current sky colours — sum of all four stops' rgb. */
  #skySum() {
    const u = this.#skyMat?.uniforms;
    if (!u) return 0;
    let s = 0;
    for (const key of ['uTop', 'uMid', 'uHorizon', 'uGround']) {
      const c = u[key]?.value;
      if (c) s += c.r + c.g + c.b;
    }
    return s;
  }

  /**
   * Regenerate the PMREM if the sky moved (or `force`). Call once per frame from
   * the tick at a safe point (before the post pass). Synchronous on an
   * initialized WebGPU backend; reuses one render target to avoid churn.
   */
  update(force = false) {
    this.#framesSinceRegen++;
    const sum = this.#skySum();
    const moved = Math.abs(sum - this.#lastSum) > 0.01;
    if (!force && !moved) return;
    if (!force && this.#framesSinceRegen < this.minRegenInterval) return;

    // fromScene is sync once renderer.init() has run (it has, post-boot). It
    // saves/restores the renderer's active render target internally, so it's
    // safe to call mid-tick. Reuse #rt across rebuilds.
    const rt = this.#pmrem.fromScene(this.#skyScene, 0.04, 0.1, 100, {
      size: this.size,
      renderTarget: this.#rt ?? undefined,
    });
    this.#rt = rt;
    this.#scene.environment = rt.texture;
    this.#lastSum = sum;
    this.#framesSinceRegen = 0;
  }

  dispose() {
    this.#rt?.dispose?.();
    this.#pmrem?.dispose?.();
  }
}
