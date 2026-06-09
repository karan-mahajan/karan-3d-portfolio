import {
  PostProcessing,
  SRGBColorSpace,
  NeutralToneMapping,
  AgXToneMapping,
  ACESFilmicToneMapping,
} from 'three/webgpu';
import { pass, screenUV, smoothstep, float, vec2, vec3, vec4, Fn, uniform, sin, cos, hash, dot, mix, clamp, length, workingToColorSpace } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

/**
 * WebGPU render pipeline (B0): render → tilt-shift → bloom → tone-map → output.
 *
 * Ported from the legacy WebGL EffectComposer (RenderPass → UnrealBloomPass →
 * tilt-shift ShaderPass → OutputPass).
 *
 * Tone mapping is applied EXPLICITLY in the output node (outputColorTransform
 * is turned OFF) so the operator is switchable at runtime and so a future
 * color-grade can slot in AFTER tone mapping but BEFORE the sRGB encode. The
 * renderer is set to NoToneMapping in App.js so nothing double-applies; the
 * exposure still comes from renderer.toneMappingExposure (the .toneMapping()
 * node reads it). Default operator is Neutral (Khronos PBR Neutral) — it
 * reproduces the authored palette ~1:1 with no hue shift, unlike ACES which
 * desaturates and skews warm hues toward yellow.
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

// Tone-mapping operators the `T` debug key cycles through, in order. Neutral is
// the default (index 0). Labels are logged so the user knows which is active.
export const TONE_MAPPING_MODES = [
  { mode: NeutralToneMapping, label: 'Neutral (PBR Neutral)' },
  { mode: AgXToneMapping, label: 'AgX' },
  { mode: ACESFilmicToneMapping, label: 'ACESFilmic' },
];

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

// Rec.709 luma weights for the saturation + split-tone steps.
const LUMA = vec3(0.2126, 0.7152, 0.0722);
// Split-tone chroma directions (tiny additive offsets). Highlights drift warm
// (toward the authored sun #ffd58a: more red, less blue); shadows drift cool-
// purple (toward the authored shadowTint #7a2da8: less green, more blue). This
// is the chromatic-shadow "pop" — applied here because patchShadowTint is dead
// on WebGPU node materials.
const SPLIT_HI = vec3(0.18, 0.02, -0.22);
const SPLIT_SH = vec3(0.02, -0.10, 0.16);

/**
 * Subtle, hue-preserving palette grade applied AFTER tone mapping + sRGB encode
 * so pivots are perceptual (mid-gray ≈ 0.5). Kept gentle on purpose — the goal
 * is to make the authored palette read with more depth/cohesion, NOT to recolor
 * it. `c` is the sRGB-encoded color; the rest are live uniform scalars.
 */
const colorGrade = /*#__PURE__*/ Fn(([c, contrast, saturation, splitStrength, vignette]) => {
  const col = c.rgb.toVar();
  // Contrast about mid-gray.
  col.assign(col.sub(0.5).mul(contrast).add(0.5));
  // Saturation (luma-preserving — no hue rotation).
  const luma = dot(col, LUMA).toVar();
  col.assign(mix(vec3(luma), col, saturation));
  // Luminance split-tone: warm highlights, cool-purple shadows.
  col.addAssign(SPLIT_HI.mul(luma).mul(splitStrength));
  col.addAssign(SPLIT_SH.mul(luma.oneMinus()).mul(splitStrength));
  // Soft vignette to focus the eye and add depth.
  const d = length(screenUV.sub(0.5));
  const vig = float(1.0).sub(smoothstep(0.45, 0.95, d).mul(vignette));
  col.mulAssign(vig);
  // Scene renders opaque (renderer alpha:false), so alpha is always 1.
  return vec4(clamp(col, 0.0, 1.0), 1.0);
});

export class PostFX {
  #tiltShiftAmount = 1.0;
  #tiltUniform = null;
  #bloomStrength = 0.30;
  // Linear HDR node (tiltShift(scene) + bloom) — the input to tone mapping.
  // Kept so the output node can be rebuilt when the tone-mapping operator
  // changes (the operator is a compile-time constant, so a swap = recompile).
  #hdrNode = null;
  #toneMappingIndex = 0;
  // Subtle palette grade (Step 4). All gentle on purpose — enhance, don't recolor.
  #grade = null;

  constructor(renderer, scene, camera, sizes, quality = {}) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.enabled = quality.enabled !== false;
    if (!this.enabled) {
      // No post chain to apply tone mapping, so the plain renderer.render path
      // must do it. App.js set the renderer to NoToneMapping (it expects PostFX
      // to handle it) — restore an operator here so the fallback isn't raw HDR.
      renderer.toneMapping = NeutralToneMapping;
      return;
    }

    this.postProcessing = new PostProcessing(renderer);
    // We apply tone mapping + sRGB ourselves in #buildOutputNode (see class
    // doc), so disable the engine's auto output transform — otherwise tone
    // mapping would be applied twice.
    this.postProcessing.outputColorTransform = false;

    const scenePass = pass(scene, camera);
    const scenePassColor = scenePass.getTextureNode('output');

    this.#tiltShiftAmount = quality.tiltShiftAmount ?? 1.0;
    this.#tiltUniform = uniform(this.#tiltShiftAmount);

    // Subtle bloom — only truly bright pixels (sun, fireflies, emissive
    // screens) bloom. Lower strength + higher threshold keeps the sun a clean
    // glowing disc instead of a blown-out blob. Same values as the legacy
    // UnrealBloomPass. Bloom reads the SHARP scene so highlights stay clean.
    this.#bloomStrength = quality.bloomStrength ?? 0.30;
    const bloomPass = bloom(
      scenePassColor,
      this.#bloomStrength,
      quality.bloomRadius ?? 0.55,
      quality.bloomThreshold ?? 0.92,
    );
    this.bloomPass = bloomPass;

    // Linear HDR scene (sharp + bloom), still in working/linear space — tone
    // mapping happens in #buildOutputNode.
    this.#hdrNode = tiltShift(scenePassColor, this.#tiltUniform).add(bloomPass);

    // Grade uniforms (live-tunable). Conservative defaults.
    this.#grade = {
      // Pushed from the old near-identity (1.08/1.10/0.06) so the grade is
      // actually visible: more depth + richer colour. Split-tone eased a touch
      // (shadows now get real per-phase colour from ShadowTint.js, so the grade
      // no longer has to fake it — it just warms highlights).
      contrast: uniform(quality.gradeContrast ?? 1.11),
      saturation: uniform(quality.gradeSaturation ?? 1.16),
      splitStrength: uniform(quality.gradeSplitStrength ?? 0.05),
      vignette: uniform(quality.gradeVignette ?? 0.24),
    };

    this.#buildOutputNode();
  }

  /**
   * (Re)assemble the output node: HDR → tone-map (current operator) → sRGB.
   * Called once at construction and again whenever the operator is swapped.
   * The operator is baked into the ToneMappingNode's cache key, so swapping
   * requires a fresh node + needsUpdate (a one-time recompile hitch — fine for
   * the `T` debug toggle).
   */
  #buildOutputNode() {
    const operator = TONE_MAPPING_MODES[this.#toneMappingIndex].mode;
    // .toneMapping(mode) reads renderer.toneMappingExposure internally and
    // returns display-referred LINEAR rgb; workingToColorSpace applies the
    // sRGB transfer for the canvas. The grade runs LAST (perceptual space).
    const toneMapped = this.#hdrNode.toneMapping(operator);
    const encoded = workingToColorSpace(toneMapped, SRGBColorSpace);
    const g = this.#grade;
    this.postProcessing.outputNode = colorGrade(
      encoded,
      g.contrast,
      g.saturation,
      g.splitStrength,
      g.vignette,
    );
    this.postProcessing.needsUpdate = true;
  }

  /** Cycle to the next tone-mapping operator (Neutral → AgX → ACES → …). */
  cycleToneMapping() {
    if (!this.enabled) return TONE_MAPPING_MODES[this.#toneMappingIndex].label;
    this.#toneMappingIndex = (this.#toneMappingIndex + 1) % TONE_MAPPING_MODES.length;
    this.#buildOutputNode();
    return TONE_MAPPING_MODES[this.#toneMappingIndex].label;
  }

  /** Current operator label (e.g. for a HUD readout). */
  get toneMappingLabel() {
    return TONE_MAPPING_MODES[this.#toneMappingIndex].label;
  }

  /**
   * Live-tune bloom strength (default 0.30). Dropped to ~0 while the camera
   * sits inside the projects hut so the bright board doesn't bloom into a haze.
   */
  set bloomStrength(value) {
    this.#bloomStrength = value;
    if (this.bloomPass?.strength) this.bloomPass.strength.value = value;
  }

  get bloomStrength() {
    return this.#bloomStrength;
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
