import { PostProcessing } from 'three/webgpu';
import { pass, screenUV, smoothstep, float, vec2, vec4, Fn, uniform, sin, cos, hash } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

/**
 * WebGPU render pipeline (B0): render → tilt-shift → bloom → output.
 *
 * Ported from the legacy WebGL EffectComposer (RenderPass → UnrealBloomPass →
 * tilt-shift ShaderPass → OutputPass).
 *
 * Tilt-shift / fake-DOF: the old GLSL computed a per-pixel
 * strength = smoothstep(0.15, 0.55, abs(uv.y - 0.5)) then averaged 8
 * hash-jittered taps to fake bokeh at the top/bottom of the frame, leaving
 * the centerline crisp (strength 0). Re-authored below as a screen-UV TSL Fn:
 * an 8-point ring sampled around each pixel, ring radius scaled by the same
 * vertical-distance strength, ring angle dithered by a per-pixel hash so the
 * blur reads as bokeh, not banding. At strength 0 the radius collapses to 0 so
 * every tap lands on the same texel → the centerline stays pixel-crisp with no
 * special-case branch.
 *
 * Tilt-shift runs on the SHARP scene texture and bloom is added on top, so the
 * glow highlights stay clean (matches the intent of the old chain).
 */

const TILT_TAPS = 8;

// screen-UV bokeh approximation. `tex` is the scene pass texture node; `amount`
// is a live uniform scalar (0 = off, 1 = full).
const tiltShift = /*#__PURE__*/ Fn(([tex, amount]) => {
  const uvc = screenUV;
  // Keep a WIDE crisp band through the middle — blur only ramps in near the
  // very top/bottom edges. (0.30,0.55) leaves the central ~60% of the frame
  // sharp; the earlier (0.15,0.55) started blurring barely a third of the way
  // out from centre, which smeared the whole upper third of the scene.
  const strength = smoothstep(0.30, 0.55, uvc.y.sub(0.5).abs()).mul(amount);
  // Max blur radius in UV units at the extreme top/bottom edges. 0.0035 (was
  // 0.012) reads as a gentle depth hint, not a smear.
  const radius = strength.mul(0.0035);
  // Per-pixel ring rotation so the taps don't band into a fixed rosette.
  const ang0 = hash(uvc.x.add(uvc.y.mul(0.6180339887))).mul(6.28318530718);

  const acc = tex.sample(uvc).rgb.toVar();
  for (let i = 0; i < TILT_TAPS; i++) {
    const a = ang0.add((i / TILT_TAPS) * Math.PI * 2);
    const off = vec2(cos(a), sin(a)).mul(radius);
    acc.addAssign(tex.sample(uvc.add(off)).rgb);
  }
  return vec4(acc.div(float(TILT_TAPS + 1)), 1.0);
});

export class PostFX {
  #tiltShiftAmount = 1.0;
  #tiltUniform = null;

  constructor(renderer, scene, camera, sizes, quality = {}) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.enabled = quality.enabled !== false;
    if (!this.enabled) return;

    this.postProcessing = new PostProcessing(renderer);
    // PostProcessing.outputColorTransform stays at its default (true): the
    // pipeline applies ACESFilmic tonemapping + sRGB on the final outputNode,
    // matching the old OutputPass at the tail of the WebGL composer. (Do NOT
    // also use a RenderOutputNode or tonemapping is applied twice.)

    const scenePass = pass(scene, camera);
    const scenePassColor = scenePass.getTextureNode('output');

    this.#tiltShiftAmount = quality.tiltShiftAmount ?? 1.0;
    this.#tiltUniform = uniform(this.#tiltShiftAmount);

    // Subtle bloom — only truly bright pixels (sun, fireflies, emissive
    // screens) bloom. Lower strength + higher threshold keeps the sun a clean
    // glowing disc instead of a blown-out blob. Same values as the legacy
    // UnrealBloomPass. Bloom reads the SHARP scene so highlights stay clean.
    const bloomPass = bloom(
      scenePassColor,
      quality.bloomStrength ?? 0.30,
      quality.bloomRadius ?? 0.55,
      quality.bloomThreshold ?? 0.92,
    );

    this.postProcessing.outputNode = tiltShift(scenePassColor, this.#tiltUniform).add(bloomPass);
  }

  /** Live-tune tilt-shift intensity (default 1.0). */
  set tiltShiftAmount(value) {
    this.#tiltShiftAmount = value;
    if (this.#tiltUniform) this.#tiltUniform.value = value;
  }

  get tiltShiftAmount() {
    return this.#tiltShiftAmount;
  }

  resize(width, height, pixelRatio) {
    if (!this.enabled) return;
    // PostProcessing tracks the renderer's own size; the renderer's setSize
    // (driven by App's resize handler) is the source of truth, so this is a
    // no-op. Kept for API stability with the WebGL composer.
  }

  render(delta) {
    // renderer.init() already ran in App.boot(), so the sync render() path is
    // safe (renderAsync() is deprecated in r184's RenderPipeline). render()
    // still schedules WebGPU command submission internally.
    if (!this.enabled) {
      this.renderer.render(this.scene, this.camera);
      return;
    }
    this.postProcessing.render();
  }
}
