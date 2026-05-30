import * as THREE from 'three/webgpu';
import { uniform, texture, vec2 } from 'three/tsl';

/**
 * Global wind source. Owns shared uniforms (time, direction, strength) and a
 * generated low-frequency noise DataTexture.
 *
 * Two consumer paths share the SAME live values so the whole scene reads as
 * one wind, not many:
 *   - GLSL (legacy): spread `wind.uniforms` into a ShaderMaterial + paste
 *     `Wind.windOffsetGLSL` into its vertex shader.
 *   - TSL (WebGPU): call `wind.offsetNode(worldXZ)` inside a node material's
 *     positionNode — returns a vec2 sway offset in world XZ, sampling the same
 *     noise texture and driven by the same time/direction/strength, exposed as
 *     TSL `uniform` nodes (`this.nodes`) synced from `uniforms` each frame.
 */
export class Wind {
  /**
   * @param {object} [opts]
   * @param {[number, number]} [opts.direction] - 2D wind direction in xz, auto-normalized.
   * @param {number} [opts.strength] - Sway magnitude in world units (0..~1).
   */
  constructor({ direction = [1, 0.35], strength = 0.35 } = {}) {
    const dir = new THREE.Vector2(direction[0], direction[1]).normalize();
    const noise = this.#createNoiseTexture(64);
    this.uniforms = {
      uWindTime: { value: 0 },
      uWindDir: { value: dir },
      uWindStrength: { value: strength },
      uWindNoise: { value: noise },
    };

    // TSL mirror of the same values for WebGPU node-material consumers
    // (grass, …). Synced from `uniforms` in update() so GLSL + TSL paths read
    // one identical wind. `texNode` samples the shared noise DataTexture.
    this.nodes = {
      time: uniform(0),
      dir: uniform(vec2(dir.x, dir.y)),
      strength: uniform(strength),
    };
    this._noiseTex = noise;
  }

  /**
   * TSL equivalent of `windOffset(vec2)` — returns a vec2 world-XZ sway offset
   * for a node material's positionNode. Mirrors the GLSL two-octave sample
   * (low-frequency drift + faster gust) so TSL grass sways in lockstep with any
   * legacy GLSL consumer. Pass the blade's world XZ as a TSL node.
   */
  offsetNode(worldXZ) {
    const dir = this.nodes.dir;
    const t = this.nodes.time;
    const uvA = worldXZ.mul(0.03).add(dir.mul(t).mul(0.04));
    const nA = texture(this._noiseTex, uvA).r.sub(0.5);
    const uvB = worldXZ.mul(0.11).add(dir.mul(t).mul(0.22));
    const nB = texture(this._noiseTex, uvB).r.sub(0.5);
    const sway = nA.mul(2.0).add(nB.mul(0.8));
    return dir.mul(sway).mul(this.nodes.strength);
  }

  /**
   * GLSL snippet declaring the wind uniforms and a `vec2 windOffset(vec2)`
   * helper. Drop this near the top of any vertex shader that consumes wind.
   * Two octaves of texture-sampled noise give a low sway + faster gust.
   */
  static get windOffsetGLSL() {
    return /* glsl */ `
      uniform float uWindTime;
      uniform vec2  uWindDir;
      uniform float uWindStrength;
      uniform sampler2D uWindNoise;

      vec2 windOffset(vec2 worldXZ) {
        vec2 dir = uWindDir;
        // Low-frequency sway — large patches drifting along wind direction.
        vec2 uvA = worldXZ * 0.03 + dir * uWindTime * 0.04;
        float nA = texture2D(uWindNoise, uvA).r - 0.5;
        // Higher-frequency gust — faster ripple, smaller amplitude.
        vec2 uvB = worldXZ * 0.11 + dir * uWindTime * 0.22;
        float nB = texture2D(uWindNoise, uvB).r - 0.5;
        float sway = nA * 2.0 + nB * 0.8;
        return dir * sway * uWindStrength;
      }
    `;
  }

  /** Advances wind time. Call once per frame from the app tick. */
  update(delta) {
    this.uniforms.uWindTime.value += delta;
    // Mirror live values into the TSL nodes (one wind across GLSL + TSL).
    this.nodes.time.value = this.uniforms.uWindTime.value;
    const d = this.uniforms.uWindDir.value;
    this.nodes.dir.value.set(d.x, d.y);
    this.nodes.strength.value = this.uniforms.uWindStrength.value;
  }

  /**
   * Build a small smoothed value-noise texture. We start from per-texel
   * random values and 3x3 box-blur a few times so the result has gradients
   * suitable for bilinear sampling — not white-noise speckle.
   */
  #createNoiseTexture(size) {
    let src = new Float32Array(size * size);
    for (let i = 0; i < src.length; i++) src[i] = Math.random();
    let dst = new Float32Array(size * size);

    for (let pass = 0; pass < 3; pass++) {
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          let sum = 0;
          for (let dy = -1; dy <= 1; dy++) {
            const yi = (y + dy + size) % size;
            for (let dx = -1; dx <= 1; dx++) {
              const xi = (x + dx + size) % size;
              sum += src[yi * size + xi];
            }
          }
          dst[y * size + x] = sum / 9;
        }
      }
      [src, dst] = [dst, src];
    }

    const data = new Uint8Array(size * size * 4);
    for (let i = 0; i < src.length; i++) {
      const v = Math.max(0, Math.min(255, Math.round(src[i] * 255)));
      data[i * 4 + 0] = v;
      data[i * 4 + 1] = v;
      data[i * 4 + 2] = v;
      data[i * 4 + 3] = 255;
    }
    const tex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.magFilter = THREE.LinearFilter;
    tex.minFilter = THREE.LinearFilter;
    tex.needsUpdate = true;
    return tex;
  }
}
