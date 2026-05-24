import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

/**
 * Cheap tilt-shift / fake-DOF pass.
 *
 * Computes a per-pixel strength based on vertical distance from the screen
 * centerline, then averages 20 hash-jittered taps. The randomness reads as
 * noisy bokeh — not depth-correct, but cinematic enough for a stylized scene.
 * Middle of the frame stays at strength 0 → fully crisp.
 */
const TiltShiftShader = {
  uniforms: {
    tDiffuse: { value: null },
    uTiltShiftAmount: { value: 1.0 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uTiltShiftAmount;
    varying vec2 vUv;

    float hash11(vec2 p) {
      return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
    }

    vec2 hash2(vec2 p, float seed) {
      return vec2(
        hash11(p + vec2(seed, 0.0)),
        hash11(p + vec2(0.0, seed + 17.0))
      );
    }

    void main() {
      vec4 originalSample = texture2D(tDiffuse, vUv);
      float strength = smoothstep(0.15, 0.55, abs(vUv.y - 0.5));

      if (strength <= 0.0) {
        gl_FragColor = originalSample;
        return;
      }

      float blurRadius = strength * uTiltShiftAmount * 0.003;
      vec4 acc = vec4(0.0);
      // Cut from 20 → 8 samples after the Quaternius overhaul: the perf
      // pass measured tilt-shift as the most expensive screen-space cost
      // in the composer. 8 hash-jittered taps still read as bokeh blur
      // rather than banded steps at the frame edges.
      const int SAMPLES = 8;
      for (int i = 0; i < SAMPLES; i++) {
        vec2 offset = (hash2(vUv, float(i)) - 0.5) * 2.0 * blurRadius;
        acc += texture2D(tDiffuse, vUv + offset);
      }
      vec4 blurredSample = acc / float(SAMPLES);
      gl_FragColor = mix(originalSample, blurredSample, strength);
    }
  `,
};

/**
 * Render pipeline: render → bloom (subtle) → tilt-shift (top/bottom blur)
 * → output (tonemap + colorspace).
 */
export class PostFX {
  #tiltShift;

  constructor(renderer, scene, camera, sizes) {
    this.composer = new EffectComposer(renderer);
    this.composer.setPixelRatio(sizes.pixelRatio);
    this.composer.setSize(sizes.width, sizes.height);

    this.composer.addPass(new RenderPass(scene, camera));

    // Subtle bloom — only truly bright pixels (sun, fireflies, emissive
    // screens) bloom. Lower strength + higher threshold keeps the sun a
    // clean glowing disc instead of a blown-out blob. Resolution dropped
    // 0.5× → 0.25× of canvas size after the Quaternius overhaul (quarters
    // the per-pixel work again — bloom is the second-most-expensive pass).
    const bloom = new UnrealBloomPass(
      new THREE.Vector2(sizes.width * 0.25, sizes.height * 0.25),
      0.30,   // strength
      0.55,   // radius
      0.92,   // threshold
    );
    this.bloom = bloom;
    this.composer.addPass(bloom);

    // Cheap tilt-shift after bloom so the bloomed sun also softens at frame
    // edges instead of staying razor-sharp against a blurred sky.
    const tiltShift = new ShaderPass(TiltShiftShader);
    this.#tiltShift = tiltShift;
    this.composer.addPass(tiltShift);

    // OutputPass handles tonemapping + colorspace conversion correctly when
    // composer is downstream of the WebGLRenderer's sRGB output.
    this.composer.addPass(new OutputPass());
  }

  /** Live-tune tilt-shift intensity (default 1.0). */
  set tiltShiftAmount(value) {
    this.#tiltShift.uniforms.uTiltShiftAmount.value = value;
  }

  get tiltShiftAmount() {
    return this.#tiltShift.uniforms.uTiltShiftAmount.value;
  }

  resize(width, height, pixelRatio) {
    this.composer.setPixelRatio(pixelRatio);
    this.composer.setSize(width, height);
    this.bloom.setSize(width * 0.25, height * 0.25);
  }

  render(delta) {
    this.composer.render(delta);
  }
}
