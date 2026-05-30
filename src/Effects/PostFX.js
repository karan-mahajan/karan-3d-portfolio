import { PostProcessing } from 'three/webgpu';
import { pass, output } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

/**
 * WebGPU render pipeline (B0): render → bloom (subtle) → output.
 *
 * Ported from the legacy WebGL EffectComposer (RenderPass → UnrealBloomPass →
 * tilt-shift ShaderPass → OutputPass). The tilt-shift / fake-DOF pass is not
 * yet ported to TSL — bloom-only for now.
 *
 * TODO(B0): port TiltShiftShader to TSL. The old GLSL computed a per-pixel
 * strength = smoothstep(0.15, 0.55, abs(vUv.y - 0.5)) then averaged 8
 * hash-jittered taps to fake bokeh at the top/bottom of the frame, leaving
 * the centerline crisp (strength 0). Re-author as a screen-UV TSL Fn that
 * samples the scene pass with jittered offsets.
 */
export class PostFX {
  #bloomPass;
  #tiltShiftAmount = 0;

  constructor(renderer, scene, camera, sizes, quality = {}) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.enabled = quality.enabled !== false;
    if (!this.enabled) return;

    this.postProcessing = new PostProcessing(renderer);
    // The node graph (via `output`) owns tonemapping + colorspace conversion,
    // matching the old OutputPass at the tail of the WebGL composer; turn off
    // the renderer's implicit output transform so it isn't applied twice.
    this.postProcessing.outputColorTransform = false;

    const scenePass = pass(scene, camera);
    const scenePassColor = scenePass.getTextureNode('output');

    // Subtle bloom — only truly bright pixels (sun, fireflies, emissive
    // screens) bloom. Lower strength + higher threshold keeps the sun a clean
    // glowing disc instead of a blown-out blob. Same values as the legacy
    // UnrealBloomPass.
    const bloomPass = bloom(
      scenePassColor,
      quality.bloomStrength ?? 0.30,
      quality.bloomRadius ?? 0.55,
      quality.bloomThreshold ?? 0.92,
    );
    this.#bloomPass = bloomPass;
    this.#tiltShiftAmount = quality.tiltShiftAmount ?? 1.0;

    this.postProcessing.outputNode = output(scenePassColor.add(bloomPass));
  }

  /** Live-tune tilt-shift intensity (default 1.0). No-op until the TSL port. */
  set tiltShiftAmount(value) {
    this.#tiltShiftAmount = value;
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
    if (!this.enabled) {
      this.renderer.renderAsync(this.scene, this.camera);
      return;
    }
    this.postProcessing.renderAsync();
  }
}
