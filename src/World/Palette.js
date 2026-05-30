import * as THREE from 'three/webgpu';

/**
 * Single source of truth for the scene's sky / fog / shadow palette.
 *
 * Sky.js, App.js (fog + lights), Terrain, Grass and Nature all read from the
 * same `DUSK` object so changing the mood is a one-file edit. `fogColor` is
 * intentionally === `skyHorizon` — distant geometry dissolves cleanly into
 * the horizon band rather than fading to an unrelated tint.
 *
 * `shadowTint` is the colour shadowed surfaces drift toward instead of pure
 * black — picked as a desaturated magenta-purple so warm sunlit sides read
 * even warmer by contrast (Bruno-Simon style dusk).
 */
export const DUSK = Object.freeze({
  skyTop:       '#6e95c7',
  skyHorizon:   '#ffb084',
  skyGround:    '#4a3528',
  sunColor:     '#ffd58a',
  shadowTint:   '#7a2da8',
  fogColor:     '#ffb084', // === skyHorizon, see note above
  ambientColor: '#ffb088',
  hemiSky:      '#a8c4ff',
  hemiGround:   '#d4845a',
});

/**
 * Tint a `MeshStandardMaterial` so shadowed fragments mix toward
 * `baseColor * shadowTint` instead of fading to black.
 *
 * Implementation: hooks `onBeforeCompile` and injects a recomputed shadow
 * mask right before `<opaque_fragment>`, then lerps `outgoingLight` toward
 * the tinted base by `(1 - shadowMask) * strength`. We recompute the mask
 * (rather than reusing what `<lights_fragment_begin>` already did per-light)
 * because three doesn't surface the aggregate mask anywhere usable after the
 * lights loop closes.
 *
 * @param {THREE.MeshStandardMaterial} material
 * @param {object}  [palette=DUSK]
 * @param {number}  [strength=0.65] - 0 = no tint, 1 = shadowed pixels are
 *                                    fully replaced by baseColor*shadowTint.
 */
export function patchShadowTint(material, palette = DUSK, strength = 0.65) {
  const tint = new THREE.Color(palette.shadowTint);
  const prevHook = material.onBeforeCompile;
  const prevCacheKey = material.customProgramCacheKey?.bind(material);

  material.onBeforeCompile = (shader, renderer) => {
    if (prevHook) prevHook(shader, renderer);

    shader.uniforms.uShadowTint = { value: tint };
    shader.uniforms.uShadowTintStrength = { value: strength };

    shader.fragmentShader = shader.fragmentShader
      .replace(
        '#include <common>',
        `#include <common>
         uniform vec3 uShadowTint;
         uniform float uShadowTintStrength;`
      )
      .replace(
        '#include <opaque_fragment>',
        `
        #if defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 )
          float _stintSum = 0.0;
          DirectionalLightShadow _stintDls;
          #pragma unroll_loop_start
          for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
            _stintDls = directionalLightShadows[ i ];
            _stintSum += getShadow(
              directionalShadowMap[ i ],
              _stintDls.shadowMapSize,
              _stintDls.shadowIntensity,
              _stintDls.shadowBias,
              _stintDls.shadowRadius,
              vDirectionalShadowCoord[ i ]
            );
          }
          #pragma unroll_loop_end
          float _stintMask = _stintSum / float( NUM_DIR_LIGHT_SHADOWS );
          float _stintAmt = clamp( 1.0 - _stintMask, 0.0, 1.0 );
          vec3 _stintTarget = diffuseColor.rgb * uShadowTint;
          outgoingLight = mix( outgoingLight, _stintTarget, _stintAmt * uShadowTintStrength );
        #endif
        #include <opaque_fragment>
        `,
      );
  };

  // Distinct cache key so three doesn't reuse a previously compiled program
  // that was built without our injection.
  material.customProgramCacheKey = () => `${prevCacheKey ? prevCacheKey() : ''}|shadowTint:${strength}`;
  material.needsUpdate = true;
}
