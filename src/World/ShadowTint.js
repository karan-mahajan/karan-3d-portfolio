import { uniform, Fn, vec3, mix } from "three/tsl";
import * as THREE from "three/webgpu";

/**
 * Shared coloured-shadow state. The proper WebGPU replacement for the dead
 * GLSL `patchShadowTint` (see [Palette.js] — `onBeforeCompile` no-ops on node
 * materials).
 *
 * `NodeMaterial.receivedShadowNode` lets us intercept the per-light shadow
 * factor (0 = fully shadowed → 1 = fully lit) before it scales the light's
 * radiance. By default the sun's contribution is multiplied by that scalar, so
 * shadowed fragments fall to ambient/hemi only and read near-black with a hard
 * brightness cliff at the terminator. Instead we LIFT THE FLOOR to a tinted
 * colour: in shadow the sun term becomes `lightColor * (shadowTint * strength)`
 * rather than 0, so the shadow→light transition is a soft HUE shift, not a
 * darkness cliff. That hue gradient is what reads as Bruno-Simon "smooth"
 * shading — but here the real PBR lighting (ambient, hemi, IBL, spec) is kept
 * on top, so it stays grounded/realistic instead of fully faked.
 *
 * One writer (TimeOfDay) drives `shadowTintColor` per phase: cool periwinkle by
 * day (sky-fill blue, physically plausible), magenta-rose at dusk/dawn, deep
 * indigo at night. Every shadow-receiving surface (props, ground) shares these
 * two uniforms so the whole world's shadows shift mood in one place.
 */

// Seeded to the authored dusk shadow tint; TimeOfDay overwrites per phase.
export const shadowTintColor = uniform(new THREE.Color("#7a2da8"));
// 0 = vanilla black shadows; 1 = shadow floor is the full tint colour. 0.38 is
// the tasteful default — clearly coloured + softer, still reads as shadow.
export const shadowTintStrength = uniform(0.38);

/**
 * Build the `receivedShadowNode` Fn to assign to a node material. Returns a
 * fresh node each call (a material owns its own node graph). `shadow` is the
 * incoming shadow factor; the returned value replaces it and is multiplied into
 * the light colour downstream (AnalyticLightNode: `colorNode.mul(shadowNode)`).
 */
export function receivedShadowTintNode() {
  return Fn(([shadow]) => {
    // Floor the shadow at a dim tint instead of 0. strength 0 → floor 0 →
    // identical to vanilla shadows (safe no-op).
    const floorColor = shadowTintColor.mul(shadowTintStrength);
    return mix(floorColor, vec3(1.0), shadow);
  });
}
