import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

/**
 * Render pipeline with a soft UnrealBloom pass — makes the emissive billboard
 * screens, fireflies, and the mailbox flag glow against the sunset.
 */
export class PostFX {
  constructor(renderer, scene, camera, sizes) {
    this.composer = new EffectComposer(renderer);
    this.composer.setPixelRatio(sizes.pixelRatio);
    this.composer.setSize(sizes.width, sizes.height);

    this.composer.addPass(new RenderPass(scene, camera));

    // Subtle bloom — strong enough to glow the screens, weak enough to keep
    // the grass + character looking grounded.
    const bloom = new UnrealBloomPass(
      new THREE.Vector2(sizes.width, sizes.height),
      0.55,   // strength
      0.55,   // radius
      0.85,   // threshold (only the brightest pixels bloom)
    );
    this.bloom = bloom;
    this.composer.addPass(bloom);

    // OutputPass handles tonemapping + colorspace conversion correctly when
    // composer is downstream of the WebGLRenderer's sRGB output.
    this.composer.addPass(new OutputPass());
  }

  resize(width, height, pixelRatio) {
    this.composer.setPixelRatio(pixelRatio);
    this.composer.setSize(width, height);
    this.bloom.setSize(width, height);
  }

  render(delta) {
    this.composer.render(delta);
  }
}
