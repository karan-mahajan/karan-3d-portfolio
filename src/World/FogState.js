import {
  uniform, fog, rangeFogFactor, positionWorld, cameraPosition, normalize, mix, vec3,
} from "three/tsl";
import * as THREE from "three/webgpu";
import { skyGradientColor } from "./Sky.js";

/**
 * Scene fog as a TSL node (WebGPU `scene.fogNode`) instead of flat `THREE.Fog`.
 *
 * The old linear fog faded every distant fragment to ONE horizon colour, so a
 * tall tree against the upper sky still dissolved into the horizon band — a
 * visible mismatch and the main reason the atmosphere read flatter than Bruno's
 * (where geometry melts seamlessly into the sky). This node instead fades each
 * fragment toward the sky-gradient colour in ITS OWN view direction (the exact
 * band of sky behind it), using the SAME gradient the dome paints
 * ([Sky.skyGradientColor]). Result: distant geometry truly dissolves into the
 * sky, top to bottom.
 *
 * Range (near/far) is driven per-phase by TimeOfDay; the winter whiten is driven
 * by WeatherDirector — both via the shared uniforms below.
 *
 * The colour/factor are exposed as standalone node builders so the faked-light
 * world material ([WorldLight.js]) can apply the SAME fog manually: a custom
 * `outputNode` bypasses the engine's fog pass, so the world props would
 * otherwise pop against the foggy background.
 */

// Distance range (view-space Z). Seeded to the DAY values; TimeOfDay overwrites.
export const fogNear = uniform(50);
export const fogFar = uniform(130);
// Winter whiten: 0 = pure sky fog, up to ~0.7 in a heavy storm. Driven by
// WeatherDirector. The tint matches its old `_winterFog` (#c9dee9).
export const fogWhiten = uniform(0);
export const fogWinterColor = uniform(new THREE.Color(0xc9dee9));

// Live sky band uniforms (sky.material.uniforms), set once via initFog before
// any fogged material is built. Lets fogColorNode() stay argument-free so both
// the scene fog node and the world material can call it.
let _skyUniforms = null;
export function initFog(skyUniforms) {
  _skyUniforms = skyUniforms;
}

/** Fog colour = the sky gradient in this fragment's view direction, lerped
 *  toward the cold winter tint by the storm amount. */
export function fogColorNode() {
  const dir = normalize(positionWorld.sub(cameraPosition));
  const skyColor = skyGradientColor(_skyUniforms, dir.y);
  return mix(skyColor, vec3(fogWinterColor), fogWhiten);
}

/** Fog amount 0..1 from view-space distance (range fog). */
export function fogFactorNode() {
  return rangeFogFactor(fogNear, fogFar);
}

/** The scene fog node (assigned to scene.fogNode). Call initFog() first. */
export function buildSceneFogNode() {
  return fog(fogColorNode(), fogFactorNode());
}
