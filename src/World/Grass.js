import * as THREE from 'three';
import { Wind } from './Wind.js';
import { DUSK } from './Palette.js';

/**
 * Shader-driven blade field.
 *
 * One Mesh, one draw call. ~density camera-billboarded triangle blades —
 * each is a 3-vertex triangle: two base anchors + one tip. The vertex
 * shader wraps each blade's stored position around the camera using
 * `mod(p - cam, tile) - tile/2` so the field reads as infinite while we
 * only ever store a finite tile. The tip is displaced by `Wind.windOffset`;
 * the bases stay anchored to the ground (lifted 1cm to avoid z-fighting).
 *
 * Tuning knobs exposed as constructor options + instance properties
 * (re-read by `#buildGeometry` — change them and re-instantiate to retune):
 *   bladeHeight    — nominal blade height in meters
 *   bladeWidth     — nominal base width in meters
 *   density        — total blade count
 *   patchVariation — low-freq height multiplier amplitude (0 = uniform,
 *                    0.5 = patches range 0.5×–1.5× of nominal)
 *
 * Color: a single grass-green uniform. The fragment shader fakes AO by
 * darkening base vertices (× 0.55) and using full color at the tip. A small
 * per-blade seed adds subtle tone variation.
 */

const FIELD_RADIUS = 40;
const TILE_SIZE = FIELD_RADIUS * 2;

export class Grass {
  /**
   * @param {THREE.Scene} scene
   * @param {Wind} wind
   * @param {object} [opts]
   * @param {string|number} [opts.color]          - grass-green base color.
   * @param {number}        [opts.bladeHeight]    - nominal blade height (m).
   * @param {number}        [opts.bladeWidth]     - nominal base width (m).
   * @param {number}        [opts.density]        - total blade count.
   * @param {number}        [opts.patchVariation] - low-freq sway in height (0..1).
   */
  constructor(scene, wind, {
    color = '#5aa033',
    // Carpet-style meadow: short, dense, soft. Bruno-Simon reference — grass
    // should read as a fuzzy ground texture, not individual spikes.
    bladeHeight = 0.22,
    bladeWidth = 0.05,
    density = 110000,
    patchVariation = 0.35,
  } = {}) {
    this.scene = scene;
    this.wind = wind;
    this.bladeHeight = bladeHeight;
    this.bladeWidth = bladeWidth;
    this.density = density;
    this.patchVariation = patchVariation;

    this.geometry = this.#buildGeometry();

    // UniformsUtils.merge deep-clones so the lights container is per-material;
    // three.js's renderer fills directionalShadowMap / directionalShadowMatrix
    // / directionalLightShadows on it every frame because `lights: true`.
    const uniforms = THREE.UniformsUtils.merge([
      THREE.UniformsLib.lights,
      THREE.UniformsLib.fog,
      {
        uBaseColor: { value: new THREE.Color(color) },
        uShadowTint: { value: new THREE.Color(DUSK.shadowTint) },
        uShadowTintStrength: { value: 0.75 },
        uCamCenter: { value: new THREE.Vector2(0, 0) },
        uTileSize: { value: TILE_SIZE },
        uFieldRadius: { value: FIELD_RADIUS },
        uPatchVariation: { value: this.patchVariation },
        uPlayerPos: { value: new THREE.Vector3(0, 0, 0) },
        uPlayerRadius: { value: 0.75 },
        // Max flatten amount: 1.0 = blade fully pressed flat, 0 = unaffected.
        // No horizontal yank — pure in-place vertical compression. 0.55 keeps
        // the trampled patch subtle (blades shorten, never fully press flat).
        uPlayerPush: { value: 0.55 },
      },
    ]);
    // Wind uniforms spread by reference so Wind.update() propagates here —
    // overwrites the cloned slots from merge with the shared objects.
    Object.assign(uniforms, wind.uniforms);

    this.material = new THREE.ShaderMaterial({
      vertexShader: this.#vertexShader(),
      fragmentShader: this.#fragmentShader(),
      // Billboarded triangles must show from either side of the camera — at
      // grazing angles a single-sided blade can flip-cull and read black.
      side: THREE.DoubleSide,
      // Opaque, explicit depth-write — locks out any "transparent vs opaque"
      // draw-order surprises with neighbouring foliage materials.
      transparent: false,
      depthWrite: true,
      alphaTest: 0,
      fog: true,
      // Required for three.js to inject NUM_DIR_LIGHT_SHADOWS / USE_SHADOWMAP
      // defines and to keep the lights uniforms updated per frame.
      lights: true,
      uniforms,
    });

    this.mesh = new THREE.Mesh(this.geometry, this.material);
    this.mesh.frustumCulled = false;
    // Receive sun shadows so blade tips/bases pick up the same magenta tint
    // the rest of the scene gets from patchShadowTint.
    this.mesh.receiveShadow = true;
    this.mesh.name = 'grass-shader';
    this.mesh.renderOrder = 0;
    scene.add(this.mesh);
  }

  /** Update per-frame uniforms. Call after the player/camera tick. */
  update(camera, playerWorldPos) {
    this.material.uniforms.uCamCenter.value.set(camera.position.x, camera.position.z);
    if (playerWorldPos) {
      this.material.uniforms.uPlayerPos.value.copy(playerWorldPos);
    }
  }

  /**
   * Pack `density` blades into a single BufferGeometry. Layout per blade:
   * 3 verts × { position(3), aBladeCenter(2), aBladeData(3=h,w,seed), aCorner(1) }.
   */
  #buildGeometry() {
    const count = this.density;
    const grid = Math.ceil(Math.sqrt(count));
    const cell = TILE_SIZE / grid;
    const totalVerts = count * 3;

    const positions = new Float32Array(totalVerts * 3);
    const bladeCenters = new Float32Array(totalVerts * 2);
    const bladeData = new Float32Array(totalVerts * 3);
    const bladeTilts = new Float32Array(totalVerts * 2);
    const corners = new Float32Array(totalVerts);

    let bladeIdx = 0;
    outer:
    for (let gy = 0; gy < grid; gy++) {
      for (let gx = 0; gx < grid; gx++) {
        if (bladeIdx >= count) break outer;
        // Wide jitter — ±0.8 of cell width centred on the cell — so blades
        // spill into neighbouring cells and the underlying lattice doesn't
        // read as visible rows in the foreground.
        const jx = (Math.random() - 0.5) * 1.6;
        const jz = (Math.random() - 0.5) * 1.6;
        const cx = (gx + 0.5 + jx) * cell - TILE_SIZE / 2;
        const cz = (gy + 0.5 + jz) * cell - TILE_SIZE / 2;
        // Per-blade ±30% variance around the nominal height/width.
        const h = this.bladeHeight * (0.7 + Math.random() * 0.6);
        const w = this.bladeWidth * (0.7 + Math.random() * 0.6);
        const seed = Math.random();
        // Stable per-blade lean — random ±15° around X and Z axes (encoded
        // as a unit factor in [-1, 1]; shader multiplies by maxTilt).
        const tiltX = (Math.random() - 0.5) * 2.0;
        const tiltZ = (Math.random() - 0.5) * 2.0;

        for (let v = 0; v < 3; v++) {
          const o = bladeIdx * 3 + v;
          // Local position attribute is unused — we build worldspace pos in
          // the vertex shader. Stored as zero to keep the buffer well-formed.
          positions[o * 3 + 0] = 0;
          positions[o * 3 + 1] = 0;
          positions[o * 3 + 2] = 0;
          bladeCenters[o * 2 + 0] = cx;
          bladeCenters[o * 2 + 1] = cz;
          bladeData[o * 3 + 0] = h;
          bladeData[o * 3 + 1] = w;
          bladeData[o * 3 + 2] = seed;
          bladeTilts[o * 2 + 0] = tiltX;
          bladeTilts[o * 2 + 1] = tiltZ;
          corners[o] = v; // 0 = base-left, 1 = base-right, 2 = tip
        }
        bladeIdx++;
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('aBladeCenter', new THREE.BufferAttribute(bladeCenters, 2));
    geometry.setAttribute('aBladeData', new THREE.BufferAttribute(bladeData, 3));
    geometry.setAttribute('aBladeTilt', new THREE.BufferAttribute(bladeTilts, 2));
    geometry.setAttribute('aCorner', new THREE.BufferAttribute(corners, 1));
    // Bounding sphere large enough that three.js never frustum-tests our way
    // out of drawing (we set frustumCulled=false too, belt and braces).
    geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);
    return geometry;
  }

  #vertexShader() {
    return /* glsl */ `
      #include <common>
      #include <fog_pars_vertex>
      #include <shadowmap_pars_vertex>

      attribute vec2 aBladeCenter;
      attribute vec3 aBladeData;
      attribute vec2 aBladeTilt;
      attribute float aCorner;

      uniform vec2  uCamCenter;
      uniform float uTileSize;
      uniform float uFieldRadius;
      uniform float uPatchVariation;
      uniform vec3  uPlayerPos;
      uniform float uPlayerRadius;
      uniform float uPlayerPush;

      varying float vTipBlend;
      varying float vSeed;
      varying float vEdgeFade;

      ${Wind.windOffsetGLSL}

      // Duplicate of Terrain.heightAt so blades sit on the same gentle waves
      // the ground plane displaces to. Kept in sync manually with Terrain.js.
      float terrainHeight(vec2 xz) {
        float dist = length(xz);
        float wave =
          sin(xz.x * 0.08) * 0.25 +
          cos(xz.y * 0.07) * 0.22 +
          sin((xz.x + xz.y) * 0.05) * 0.18;
        float flatten = smoothstep(8.0, 22.0, dist);
        return wave * flatten;
      }

      void main() {
        // Wrap the stored blade XZ around the camera. As the player moves,
        // blades that fall behind reappear ahead — the field is infinite-feeling
        // without paying for more blades.
        vec2 wrap = mod(aBladeCenter - uCamCenter + uTileSize * 0.5, uTileSize)
                  - uTileSize * 0.5 + uCamCenter;

        float bladeH = aBladeData.x;
        float bladeW = aBladeData.y;
        float seed   = aBladeData.z;

        // Low-frequency patch variation. Sample the Wind noise texture at a
        // very low spatial frequency (one cycle ~83m, smoothed by the texture
        // pre-blur + bilinear filter) — that gives Perlin-style continuous
        // patches rather than blocky cell hashes.
        float patchN = texture2D(uWindNoise, wrap * 0.012).r;
        float patchScale = 1.0 + (patchN - 0.5) * 2.0 * uPatchVariation;
        bladeH *= patchScale;

        // Billboard the base in xz: width axis is perpendicular to the
        // camera-to-blade direction so we always see the broad face.
        vec2 toBlade = wrap - uCamCenter;
        float toBladeLen = max(length(toBlade), 0.001);
        vec2 forward = toBlade / toBladeLen;
        vec2 rightXZ = vec2(-forward.y, forward.x);

        // Lift base 1cm above terrain to avoid z-fighting on the ground plane.
        float groundY = terrainHeight(wrap);
        float baseY = groundY + 0.01;

        // Player interaction: blades inside uPlayerRadius get vertically
        // compressed in place — pressed flat, not yanked sideways. A small
        // per-blade jitter offsets each blade's effective distance to the
        // player so the flatten boundary breaks up the perfect circle and
        // doesn't read as a starburst/sunburst pattern.
        float distToPlayer = distance(wrap, uPlayerPos.xz);
        float perBladeJitter = (seed - 0.5) * 0.25;
        float adjustedDist = distToPlayer + perBladeJitter;
        float flattenAmount = 1.0 - smoothstep(
          uPlayerRadius * 0.4,
          uPlayerRadius * 1.1,
          adjustedDist
        );

        vec3 wpos;
        if (aCorner < 0.5) {
          // base-left — anchored, no sway
          wpos = vec3(wrap.x - rightXZ.x * bladeW * 0.5, baseY,
                      wrap.y - rightXZ.y * bladeW * 0.5);
          vTipBlend = 0.0;
        } else if (aCorner < 1.5) {
          // base-right — anchored, no sway
          wpos = vec3(wrap.x + rightXZ.x * bladeW * 0.5, baseY,
                      wrap.y + rightXZ.y * bladeW * 0.5);
          vTipBlend = 0.0;
        } else {
          // tip — apply stable per-blade lean, then add wind sway on top.
          //
          // Lean: rotate around the base by aBladeTilt * 15° on the X and Z
          // axes. Base verts already sit on the ground, so only the tip
          // moves; the triangle gets a fixed lean direction per blade. This
          // breaks the "row of upright pines" silhouette at distance.
          const float maxTilt = 0.2618; // radians (15°)
          float tiltX = aBladeTilt.x * maxTilt;
          float tiltZ = aBladeTilt.y * maxTilt;
          // Rotation around X axis displaces +Z; around Z axis displaces +X.
          // Cos(15°) ≈ 0.966, so height drop is sub-3% — keep it for accuracy.
          float tipX = bladeH * sin(tiltZ);
          float tipZ = bladeH * sin(tiltX);
          float tipY = bladeH * cos(tiltX) * cos(tiltZ);

          // Player press: compress the tip's upward growth in place. No
          // horizontal yank — the blade stays anchored at its base and just
          // gets shorter. uPlayerPush is the max flatten ratio (e.g. 0.85
          // = tip rises only 15% of normal height when fully pressed).
          float heightFactor = 1.0 - flattenAmount * uPlayerPush;
          tipY *= heightFactor;

          // Sway scaled by blade height so taller blades lever more,
          // shorter blades barely move (matches how cantilevered grass behaves).
          vec2 wo = windOffset(wrap) * bladeH * 0.8;
          wpos = vec3(wrap.x + tipX + wo.x,
                      groundY + tipY,
                      wrap.y + tipZ + wo.y);
          vTipBlend = 1.0;
        }

        // Fade out near the field boundary so distant blades don't pop in/out.
        vEdgeFade = 1.0 - smoothstep(uFieldRadius * 0.78, uFieldRadius, toBladeLen);
        vSeed = seed;

        // worldPosition is required by <shadowmap_vertex>. HAS_NORMAL is not
        // defined on this material so the chunk's shadowNormalBias fallback
        // (vec3(0)) is used — acceptable since blades are sub-cm thin and
        // the sun's normalBias on the directional already covers acne.
        vec4 worldPosition = vec4(wpos, 1.0);
        vec4 mvPosition = viewMatrix * worldPosition;
        gl_Position = projectionMatrix * mvPosition;

        #include <shadowmap_vertex>
        #include <fog_vertex>
      }
    `;
  }

  #fragmentShader() {
    return /* glsl */ `
      #include <common>
      #include <fog_pars_fragment>
      #include <shadowmap_pars_fragment>

      uniform vec3 uBaseColor;
      uniform vec3 uShadowTint;
      uniform float uShadowTintStrength;

      varying float vTipBlend;
      varying float vSeed;
      varying float vEdgeFade;

      void main() {
        if (vEdgeFade < 0.02) discard;

        // Fake AO: base verts darker, tip full color.
        float aoMix = mix(0.55, 1.0, vTipBlend);
        vec3 color = uBaseColor * aoMix;
        // Per-blade tone jitter so the field isn't a flat sheet of one color.
        color *= 0.88 + vSeed * 0.22;

        // Real shadow receive — averaged across all directional shadow maps
        // (in practice this scene has exactly one: the sun). Mix toward
        // baseColor*shadowTint so blades inside a tree's shadow turn warm
        // magenta-purple instead of going flat dark.
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
          vec3 _stintTarget = uBaseColor * uShadowTint;
          color = mix( color, _stintTarget, _stintAmt * uShadowTintStrength );
        #endif

        gl_FragColor = vec4(color, 1.0);

        #include <fog_fragment>
      }
    `;
  }
}
