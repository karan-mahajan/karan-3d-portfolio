import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { makeCelestialSprite } from './celestialSprite.js';

/**
 * Visible sun in the sky. A SINGLE camera-facing billboard with a soft glowing
 * profile (hot core → smooth edge → warm skirt, all one continuous gradient),
 * so it reads as a real glowing orb instead of a hard flat disc with a ring.
 * The group rides with the camera each frame and re-aligns to the shared
 * DirectionalLight's direction, locking the rendered sun to the shadow source.
 *
 * Additive + toneMapped:false so the core blooms to white-hot through the
 * bloom pass; the sprite texture is generated on the fly (no image load).
 */
export class Sun {
  // Sit inside the sky sphere (radius 250) but well past nearby props, so
  // local geometry can never occlude it from a normal player viewpoint.
  #distance = 240;
  #light;
  #group;
  #orb;
  #tmpDir = new THREE.Vector3();

  /**
   * @param {THREE.Scene} scene
   * @param {THREE.DirectionalLight} directionalLight - sun direction source
   */
  constructor(scene, directionalLight) {
    this.#light = directionalLight;
    this.#group = new THREE.Group();

    // Soft sun sprite: white-hot core, warm golden skirt.
    const tex = makeCelestialSprite({
      coreRadius: 0.24,
      feather: 0.16,
      glowPow: 2.6,
      glowStrength: 0.55,
      coreColor: [1.0, 0.98, 0.92],
      edgeColor: [1.0, 0.72, 0.42],
    });
    // HDR-ish colour boost so the core punches through the bloom threshold;
    // tone mapping is off here, so this reaches the bloom pass unsquashed.
    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      color: new THREE.Color(1.6, 1.5, 1.35),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
      side: THREE.DoubleSide,
    });
    this.#orb = new THREE.Mesh(new THREE.PlaneGeometry(34, 34), mat);
    this.#orb.frustumCulled = false;
    this.#orb.renderOrder = 9;

    this.#group.add(this.#orb);
    scene.add(this.#group);
  }

  /** Hard-set the orb alpha. Day = 1, night = 0. */
  setOpacity(value) {
    this.#orb.material.opacity = value;
    this.#group.visible = value > 0.001;
  }

  /** GSAP-tween the visible alpha. Used by TimeOfDay during mode transitions. */
  tweenOpacity(target, duration, ease = 'sine.inOut') {
    this.#group.visible = true;
    gsap.to(this.#orb.material, {
      opacity: target,
      duration,
      ease,
      onComplete: () => {
        if (target <= 0.001) this.#group.visible = false;
      },
    });
  }

  /**
   * Re-place the sun #distance units from the camera along `dir` (the sun-arc
   * display direction from TimeOfDay) so it follows its OWN arc independent of
   * the shadow light — at dusk the sun sets west while the moon rises east.
   * Falls back to the DirectionalLight direction if no dir is passed. The
   * billboard faces the camera each frame so it never edges-on.
   *
   * @param {THREE.Camera} camera
   * @param {THREE.Vector3} [dir] - normalised sun-disc direction
   */
  update(camera, dir = null) {
    if (dir) {
      this.#tmpDir.copy(dir).normalize();
    } else {
      this.#tmpDir
        .copy(this.#light.position)
        .sub(this.#light.target.position)
        .normalize();
    }
    this.#group.position
      .copy(camera.position)
      .addScaledVector(this.#tmpDir, this.#distance);
    this.#orb.quaternion.copy(camera.quaternion);
  }
}
