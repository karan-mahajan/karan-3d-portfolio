import {
  uniform, Fn, vec3, vec4, float, normalWorld, frontFacing, dot, max, smoothstep, mix, If,
} from "three/tsl";
import * as THREE from "three/webgpu";
import { shadowTintColor } from "./ShadowTint.js";
import { fogColorNode, fogFactorNode } from "./FogState.js";

/**
 * Bruno-Simon-style FAKED lighting for the consolidated static world (props +
 * ground). The PBR path (`MeshStandardNodeMaterial` + the four real lights +
 * IBL) gave correct but HARD shading: the diffuse terminator cut to dark with a
 * crisp `max(N·L, 0)` edge that read harsher than Bruno's painterly world.
 * three r184 exposes no public hook to wrap that terminator inside the physical
 * lighting model, so — by explicit user choice — the shared world material now
 * computes its own light entirely in `outputNode`:
 *
 *   - ONE sun direction + radiance (driven per-phase by TimeOfDay).
 *   - A WRAPPED core/self shadow: `smoothstep(1, -0.3, N·L)` bleeds light ~30%
 *     past the terminator, so nothing snaps to black — the soft low-poly look.
 *   - The real sun shadow map's CAST shadow, caught as a float via
 *     `receivedShadowNode`, combined with the core shadow.
 *   - Shadowed fragments drift toward `base * shadowTint` (a per-phase colour),
 *     never pure black — Bruno's coloured shadows.
 *   - Emissive + the same view-direction fog as the rest of the scene, applied
 *     manually (a custom outputNode bypasses the engine's emissive/fog passes).
 *
 * The material stays LIT (`MeshLambertNodeMaterial`, lights:true) only so the
 * shadow graph runs and `receivedShadowNode` fires; the Lambert result itself is
 * discarded by the outputNode override. No specular/IBL — matte, like Bruno.
 */

// Direction TO the sun (normalised); radiance = sunColor × faked intensity.
// Both driven by TimeOfDay each frame. Seeds keep the first compiled frame sane.
export const sunDir = uniform(new THREE.Vector3(0.35, 0.45, 0.82));
export const sunRadiance = uniform(new THREE.Color(1, 0.97, 0.9));

// Wrap edges for the core shadow. HIGH = fully lit (N·L ≥ 1), LOW = full shadow.
// LOW < 0 wraps light past the geometric terminator → soft, no hard cut.
const CORE_EDGE_HIGH = 1.0;
const CORE_EDGE_LOW = -0.3;
// Scale the coloured shadow ambient so shadows read as shadow, not just a
// recolour at full brightness.
const SHADOW_AMBIENT_SCALE = 0.72;

/**
 * Build the `receivedShadowNode` that catches the sun's cast-shadow factor into
 * a per-material float var (0 = shadowed, 1 = lit) and neutralises the engine's
 * own darkening (returns 1) — the outputNode applies shadow itself.
 */
export function worldShadowCatcher(catchedShadow) {
  return Fn(([shadow]) => {
    catchedShadow.assign(shadow);
    return float(1.0);
  });
}

/**
 * The faked-light `outputNode` (vec4). `baseColor4` is the material's albedo
 * (vec4, rgb + baked alpha); `emissiveRgb` the additive emissive; `catchedShadow`
 * the float var filled by worldShadowCatcher.
 */
export function worldLitOutput(baseColor4, emissiveRgb, catchedShadow) {
  return Fn(() => {
    const base = baseColor4.xyz.toVar();

    // Reorient the normal on backfaces (the shared world material is double-sided).
    const N = normalWorld.toVar();
    If(frontFacing.not(), () => {
      N.mulAssign(-1);
    });

    // Wrapped self/core shadow — soft terminator.
    const ndl = dot(N, sunDir);
    const coreShadow = smoothstep(CORE_EDGE_HIGH, CORE_EDGE_LOW, ndl);
    // Cast shadow from the real sun shadow map.
    const dropShadow = catchedShadow.oneMinus();
    const combined = max(coreShadow, dropShadow).clamp(0, 1);

    // Sunlit vs coloured-ambient shadow, blended by the combined shadow.
    const lit = base.mul(sunRadiance);
    const shadowCol = base.mul(vec3(shadowTintColor)).mul(SHADOW_AMBIENT_SCALE);
    const out = mix(lit, shadowCol, combined).toVar();

    // Emissive glows regardless of shading.
    out.addAssign(emissiveRgb);

    // Same view-direction sky fog as the rest of the scene (applied manually).
    out.assign(mix(out, fogColorNode(), fogFactorNode()));

    return vec4(out, baseColor4.w);
  })();
}
