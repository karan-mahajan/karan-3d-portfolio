import * as THREE from 'three';
import { patchShadowTint } from './Palette.js';

/**
 * Large walkable ground plane. The displaced geometry is unchanged from the
 * flat-colour version — physics colliders and the Grass.js shader-field both
 * mirror `heightAt`, so we must not touch the wave or the flat-spawn zone.
 *
 * Material: a `MeshStandardMaterial` extended via `onBeforeCompile` to blend
 * three tileable PBR sets (grass / dirt / stone) at ~5m UV scale. Blend
 * weights are derived from worldspace Y (dirt in dips) and surface slope
 * (stone on the steepest ridges). All three normal maps are sampled and
 * combined, with TBN reconstructed from screen-space derivatives so we don't
 * need a tangent attribute on the geometry.
 *
 * Tuning constants live as `#UV_SCALE`, `#DIRT_*`, `#STONE_*` on the class so
 * a future polish pass can adjust without spelunking the GLSL.
 */
export class Terrain {
  static #UV_SCALE = 5.0;
  // Dirt only fades in for the deepest dips of the sine wave — wave std is
  // ≈0.27, so DIRT_HIGH=-0.25 means roughly the lowest ~18% of terrain area
  // starts to show dirt; full saturation at -0.50 is reached only in the rare
  // deepest pockets. Keeps grass clearly dominant.
  static #DIRT_HIGH = -0.25;
  static #DIRT_LOW = -0.50;
  // Stone gates on surface angle from vertical. STONE_LOW=0.15 corresponds to
  // dot(n, up) = 0.85, i.e. ~32° from vertical; STONE_HIGH=0.30 ≈ 45°. The
  // current sine-wave terrain barely exceeds 4° anywhere, so stone is RARE by
  // design — it's reserved for any future hand-sculpted ridges.
  static #STONE_LOW = 0.15;
  static #STONE_HIGH = 0.30;
  static #TEXTURE_BASE = '/textures/ground';
  // Wet-rim band — terrain darkens within this distance of any water edge,
  // and a thin foam highlight sits right at the shoreline. Must match
  // `#define MAX_WATER` in the fragment shader extension below.
  static #MAX_WATER = 96;
  static #WET_RIM_M = 1.0;
  static #FOAM_BAND_M = 0.18;

  #uniforms;

  constructor(scene, loader, { size = 200, segments = 96 } = {}) {
    this.size = size;
    this.segments = segments;

    const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
    geometry.rotateX(-Math.PI / 2);
    this.#displaceVertices(geometry);
    geometry.computeVertexNormals();

    const material = this.#buildMaterial(loader);
    // Tint shadowed ground toward magenta-purple rather than fading to black.
    // patchShadowTint chains onto our existing onBeforeCompile.
    patchShadowTint(material);

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.receiveShadow = true;
    this.mesh.name = 'terrain';
    scene.add(this.mesh);
  }

  #buildMaterial(loader) {
    const base = Terrain.#TEXTURE_BASE;
    // onError fires per missing file so a single typo'd path doesn't silently
    // weight that texture to zero in the blend (which was hard to distinguish
    // from a low blend weight when first wiring this up).
    const url = (path) => `${base}/${path}`;
    const onErr = (path) => (err) => {
      console.warn(`[Terrain] failed to load texture: ${url(path)}`, err);
    };
    const colorTex = (path) => {
      const t = loader.texture.load(url(path), undefined, undefined, onErr(path));
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = 8;
      return t;
    };
    const normalTex = (path) => {
      const t = loader.texture.load(url(path), undefined, undefined, onErr(path));
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      // Linear sampling — normal maps must not be sRGB-decoded.
      t.anisotropy = 8;
      return t;
    };

    const grassMap   = colorTex('grass/Grass001_1K-PNG_Color.png');
    const dirtMap    = colorTex('dirt/Ground037_1K-PNG_Color.png');
    const stoneMap   = colorTex('stone/Rock026_1K-PNG_Color.png');
    const grassNorm  = normalTex('grass/Grass001_1K-PNG_NormalGL.png');
    const dirtNorm   = normalTex('dirt/Ground037_1K-PNG_NormalGL.png');
    const stoneNorm  = normalTex('stone/Rock026_1K-PNG_NormalGL.png');

    // Water positions packed as (x, z, radius) per entry. setWaterExclusions
    // populates these once at boot; default state (count=0) skips the loop.
    this._waterPositions = new Float32Array(Terrain.#MAX_WATER * 3);

    this.#uniforms = {
      uGrassMap:        { value: grassMap },
      uDirtMap:         { value: dirtMap },
      uStoneMap:        { value: stoneMap },
      uGrassNormal:     { value: grassNorm },
      uDirtNormal:      { value: dirtNorm },
      uStoneNormal:     { value: stoneNorm },
      uTerrainUvScale:  { value: Terrain.#UV_SCALE },
      uDirtHigh:        { value: Terrain.#DIRT_HIGH },
      uDirtLow:         { value: Terrain.#DIRT_LOW },
      uStoneLow:        { value: Terrain.#STONE_LOW },
      uStoneHigh:       { value: Terrain.#STONE_HIGH },
      uWaterPositions:  { value: this._waterPositions },
      uWaterCount:      { value: 0 },
      uWetRim:          { value: Terrain.#WET_RIM_M },
      uFoamBand:        { value: Terrain.#FOAM_BAND_M },
    };

    const material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.95,
      metalness: 0,
    });
    // Assigning a normalMap (any of ours is fine — we override the sampling
    // in onBeforeCompile) forces three to set USE_NORMALMAP, which is what
    // declares `vViewPosition` and the per-channel UV plumbing we rely on
    // inside <normal_fragment_maps>. The texture itself is never read because
    // our chunk replacement samples the three uTexture uniforms instead.
    material.normalMap = grassNorm;

    material.onBeforeCompile = (shader) => {
      Object.assign(shader.uniforms, this.#uniforms);

      shader.vertexShader = shader.vertexShader
        .replace(
          '#include <common>',
          `#include <common>
           varying vec3 vWorldPos;
           varying vec3 vWorldNormalGeom;`
        )
        .replace(
          '#include <beginnormal_vertex>',
          `#include <beginnormal_vertex>
           vWorldNormalGeom = normalize(mat3(modelMatrix) * objectNormal);`
        )
        .replace(
          '#include <begin_vertex>',
          `#include <begin_vertex>
           vWorldPos = (modelMatrix * vec4(transformed, 1.0)).xyz;`
        );

      shader.fragmentShader = shader.fragmentShader
        .replace(
          '#include <common>',
          `#include <common>
           #define MAX_WATER 96
           varying vec3 vWorldPos;
           varying vec3 vWorldNormalGeom;
           uniform sampler2D uGrassMap;
           uniform sampler2D uDirtMap;
           uniform sampler2D uStoneMap;
           uniform sampler2D uGrassNormal;
           uniform sampler2D uDirtNormal;
           uniform sampler2D uStoneNormal;
           uniform float uTerrainUvScale;
           uniform float uDirtHigh;
           uniform float uDirtLow;
           uniform float uStoneLow;
           uniform float uStoneHigh;
           uniform vec3  uWaterPositions[MAX_WATER];
           uniform int   uWaterCount;
           uniform float uWetRim;
           uniform float uFoamBand;`
        )
        .replace(
          '#include <map_fragment>',
          // diffuseColor starts as material.color (white) * opacity. We sample
          // the three diffuse maps at worldspace XZ and layer dirt over grass,
          // then stone over both. Weights stay as locals (_dirtW, _stoneW)
          // because <normal_fragment_maps> below reuses them — both chunks
          // expand at the top level of `void main()` so locals carry over.
          `vec2 _terrainUv = vWorldPos.xz / uTerrainUvScale;
           float _slope = clamp(1.0 - vWorldNormalGeom.y, 0.0, 1.0);
           float _dirtW  = smoothstep(uDirtHigh, uDirtLow, vWorldPos.y);
           float _stoneW = smoothstep(uStoneLow, uStoneHigh, _slope);
           vec3 _gCol = texture2D(uGrassMap, _terrainUv).rgb;
           vec3 _dCol = texture2D(uDirtMap,  _terrainUv).rgb;
           vec3 _sCol = texture2D(uStoneMap, _terrainUv).rgb;
           vec3 _col = mix(_gCol, _dCol, _dirtW);
           _col = mix(_col, _sCol, _stoneW);

           // Wet shoreline: shortest signed distance from this pixel to any
           // water disc edge. Negative inside water (those pixels are hidden
           // by the water mesh anyway), 0 at the rim, positive outside.
           float _minD = 1e6;
           for (int i = 0; i < MAX_WATER; i++) {
             if (i >= uWaterCount) break;
             vec3 wp = uWaterPositions[i];
             float d = distance(vec2(vWorldPos.x, vWorldPos.z), wp.xy) - wp.z;
             _minD = min(_minD, d);
           }
           float _outside = max(_minD, 0.0);
           // Darken within uWetRim of the shoreline (max 45% darker at the
           // edge, easing back to 0 by uWetRim metres out).
           float _wet = 1.0 - smoothstep(0.0, uWetRim, _outside);
           _col *= mix(1.0, 0.55, _wet);
           // Thin foam band at the waterline.
           float _foam = (1.0 - smoothstep(0.0, uFoamBand, _outside));
           _col = mix(_col, vec3(0.92, 0.95, 0.98), _foam * 0.35);

           diffuseColor.rgb *= _col;`
        )
        .replace(
          '#include <normal_fragment_maps>',
          // Blend three tangent-space normals with the same weights, then
          // reconstruct TBN from screen-space derivatives — three's standard
          // no-tangent path, just with our blended mapN instead of a single
          // texture2D(normalMap, vNormalMapUv) sample.
          `vec3 _nG = texture2D(uGrassNormal, _terrainUv).xyz * 2.0 - 1.0;
           vec3 _nD = texture2D(uDirtNormal,  _terrainUv).xyz * 2.0 - 1.0;
           vec3 _nS = texture2D(uStoneNormal, _terrainUv).xyz * 2.0 - 1.0;
           vec3 _mapN = mix(_nG, _nD, _dirtW);
           _mapN = mix(_mapN, _nS, _stoneW);
           _mapN = normalize(_mapN);

           vec3 _q0 = dFdx(-vViewPosition);
           vec3 _q1 = dFdy(-vViewPosition);
           vec2 _st0 = dFdx(_terrainUv);
           vec2 _st1 = dFdy(_terrainUv);
           vec3 _Nrm = normal;
           vec3 _q1perp = cross(_q1, _Nrm);
           vec3 _q0perp = cross(_Nrm, _q0);
           vec3 _T = _q1perp * _st0.x + _q0perp * _st1.x;
           vec3 _B = _q1perp * _st0.y + _q0perp * _st1.y;
           float _det = max(dot(_T, _T), dot(_B, _B));
           float _scale = (_det == 0.0) ? 0.0 : faceDirection * inversesqrt(_det);
           normal = normalize(_T * (_mapN.x * _scale) + _B * (_mapN.y * _scale) + _Nrm * _mapN.z);`
        );
    };

    return material;
  }

  #displaceVertices(geometry) {
    const pos = geometry.attributes.position;
    const center = new THREE.Vector2(0, 0);
    const tmp = new THREE.Vector2();
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      tmp.set(x, z);
      const distance = tmp.distanceTo(center);

      const wave =
        Math.sin(x * 0.08) * 0.25 +
        Math.cos(z * 0.07) * 0.22 +
        Math.sin((x + z) * 0.05) * 0.18;
      const flatten = THREE.MathUtils.smoothstep(distance, 8, 22);
      pos.setY(i, wave * flatten);
    }
    pos.needsUpdate = true;
  }

  /**
   * Register water footprints so the fragment shader can darken the
   * shoreline + paint a foam ring. Same format as Grass.setWaterExclusions:
   * an array of `{x, z, r}` discs. Call once at boot — surfaces don't move.
   *
   * @param {Array<{x:number,z:number,r:number}>} points
   */
  setWaterExclusions(points) {
    const capped = Math.min(points.length, Terrain.#MAX_WATER);
    for (let i = 0; i < capped; i++) {
      this._waterPositions[i * 3 + 0] = points[i].x;
      this._waterPositions[i * 3 + 1] = points[i].z;
      this._waterPositions[i * 3 + 2] = points[i].r;
    }
    this._waterPositions.fill(0, capped * 3);
    this.#uniforms.uWaterCount.value = capped;
  }

  heightAt(x, z) {
    const distance = Math.hypot(x, z);
    const wave =
      Math.sin(x * 0.08) * 0.25 +
      Math.cos(z * 0.07) * 0.22 +
      Math.sin((x + z) * 0.05) * 0.18;
    const flatten = THREE.MathUtils.smoothstep(distance, 8, 22);
    return wave * flatten;
  }
}
