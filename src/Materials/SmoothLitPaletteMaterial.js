import * as THREE from 'three';

/**
 * Master material for world props. Phase 1: thin MeshLambertMaterial wrapper.
 * Phase 5: extended to ShaderMaterial with palette sample, smooth Lambert,
 * 3-band fog, wind displacement, reveal-wipe (world-design §10.1).
 *
 * Phase 1 keeps it cheap so the MVS swap is bisectable against shader bugs.
 */
export class SmoothLitPaletteMaterial extends THREE.MeshLambertMaterial {
  constructor(opts = {}) {
    super({
      color: 0xffffff,
      ...opts,
    });
    this.userData = this.userData || {};
    this.userData.isPaletteMaster = true;
  }

  setPlayerUniforms(_uniforms) {
    // Phase 5 wires this through onBeforeCompile.
  }
}
