import * as THREE from 'three';
import { DUSK } from './Palette.js';

/**
 * Visible sun in the sky. A bright opaque disc plus an additive billboard
 * corona that always faces the camera. The whole group rides with the camera
 * each frame and re-aligns to whatever direction the shared DirectionalLight
 * is shining from, so the rendered sun is locked to the shadow source.
 *
 * Pipeline notes:
 *   - Disc uses MeshBasicMaterial with toneMapped:false and a >1 HDR colour so
 *     the UnrealBloomPass (threshold 0.85 in linear space) picks it up.
 *   - Disc is opaque (renderOrder 10) and the corona is additive-blended
 *     (renderOrder 9, in transparent queue). Sky has renderOrder -1, so the
 *     sun draws over the sky sphere even though it sits inside it.
 *   - The corona texture is generated on the fly — no external image load.
 */
export class Sun {
  // Sit inside the sky sphere (radius 250) but well past nearby props, so
  // local geometry can never occlude it from a normal player viewpoint.
  #distance = 240;
  #light;
  #group;
  #disc;
  #corona;
  #tmpDir = new THREE.Vector3();

  /**
   * @param {THREE.Scene} scene
   * @param {THREE.DirectionalLight} directionalLight - sun direction source
   */
  constructor(scene, directionalLight) {
    this.#light = directionalLight;
    this.#group = new THREE.Group();

    // HDR-boost the disc colour so it punches through the bloom threshold
    // (0.85 linear). Tonemapping is off so this value reaches the bloom pass
    // unsquashed; OutputPass tonemaps the composite at the end.
    const discColor = new THREE.Color(DUSK.sunColor).multiplyScalar(1.8);
    const discMat = new THREE.MeshBasicMaterial({
      color: discColor,
      transparent: false,
      fog: false,
      depthWrite: false,
      toneMapped: false,
    });
    this.#disc = new THREE.Mesh(new THREE.SphereGeometry(2.5, 32, 32), discMat);
    this.#disc.frustumCulled = false;
    this.#disc.renderOrder = 10;

    const coronaTex = this.#buildCoronaTexture();
    const coronaMat = new THREE.MeshBasicMaterial({
      map: coronaTex,
      color: new THREE.Color(DUSK.sunColor),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
      side: THREE.DoubleSide,
    });
    this.#corona = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), coronaMat);
    this.#corona.frustumCulled = false;
    this.#corona.renderOrder = 9;

    this.#group.add(this.#corona, this.#disc);
    scene.add(this.#group);
  }

  /**
   * Procedural 256² halo: white centre fading to transparent at the edge with
   * a pow(1-d, 2.5) curve — sharp hot core, long soft skirt.
   */
  #buildCoronaTexture() {
    const size = 256;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(size, size);
    const half = size / 2;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const dx = (x - half) / half;
        const dy = (y - half) / half;
        const d = Math.min(Math.sqrt(dx * dx + dy * dy), 1);
        const a = Math.pow(1 - d, 2.5);
        const i = (y * size + x) * 4;
        img.data[i] = 255;
        img.data[i + 1] = 255;
        img.data[i + 2] = 255;
        img.data[i + 3] = Math.round(a * 255);
      }
    }
    ctx.putImageData(img, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.generateMipmaps = false;
    tex.needsUpdate = true;
    return tex;
  }

  /**
   * Re-place the sun in the direction of the DirectionalLight (relative to its
   * target) and push it #distance units from the camera. Corona quaternion is
   * snapped to the camera each frame so the halo plane never edges-on.
   *
   * @param {THREE.Camera} camera
   */
  update(camera) {
    this.#tmpDir
      .copy(this.#light.position)
      .sub(this.#light.target.position)
      .normalize();
    this.#group.position
      .copy(camera.position)
      .addScaledVector(this.#tmpDir, this.#distance);
    this.#corona.quaternion.copy(camera.quaternion);
  }
}
