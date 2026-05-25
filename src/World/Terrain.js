import * as THREE from 'three';
import { patchShadowTint } from './Palette.js';

/**
 * Walkable ground plane, sculpted into an island:
 *   - Inside `ISLAND_RADIUS` (45 m): playable land at y ≈ 0.5, with gentle
 *     painted hills (sin/cos wave) and a flat spawn plateau.
 *   - Between `ISLAND_RADIUS` and `ISLAND_RADIUS + SHORE_WIDTH` (45–57 m):
 *     a sandy shore slope from y ≈ 0.5 down to y ≈ -2.
 *   - Beyond 57 m: clamped at y = -2 — the ocean floor under the water plane.
 *
 * `heightAt(x, z)` mirrors `#displaceVertices`. Physics.addStaticGround() and
 * Grass placement both read it, so the two must stay in lockstep.
 *
 * Material: a `MeshStandardMaterial` extended via `onBeforeCompile` to blend
 * three tileable PBR sets (grass / dirt / stone) at ~5m UV scale plus two
 * cheap colour tints on the dirt sample for "sand" (around the waterline)
 * and "mud" (the submerged ocean floor). Blend weights are derived from
 * worldspace Y; surface slope still gates the stone band for any future
 * hand-sculpted ridges.
 */
export class Terrain {
  static #UV_SCALE = 5.0;

  // Island shape — must match WATER's ISLAND_RADIUS in src/Effects/Water.js.
  // Inside the island the height formula is the same gentle wave-and-spawn-
  // flatten the portfolio was originally built against (signs/billboards
  // placed at y=0 sit on top of the grass). Outside the island radius the
  // land drops away through a shore slope to the ocean floor.
  static #ISLAND_RADIUS = 45;
  static #SHORE_WIDTH = 12;
  static #OCEAN_FLOOR_Y = -2.0;
  // Land floor inside the island. Held a few centimetres above the water
  // plane (y=0) so any wave-dip can't show transparent ocean through itself.
  static #INNER_FLOOR_Y = 0.02;

  // Material bands (worldspace Y):
  //   y > #GRASS_Y_LOW              → grass texture
  //   #SAND_Y_LOW … #GRASS_Y_LOW    → grass→sand blend (visible beach)
  //   #MUD_Y_LOW  … #SAND_Y_LOW     → sand (dirt-tex × sand tint)
  //   y < #MUD_Y_LOW                → mud (dirt-tex × mud tint, ocean floor)
  // Tuned so the full island interior reads as grass and the shore slope
  // (y dropping from 0 to -2 over ~12 m) gives an ~8-m wide visible sand band.
  static #GRASS_Y_LOW = -0.05;
  static #SAND_Y_LOW = -1.50;
  static #MUD_Y_LOW = -1.80;
  static #STONE_LOW = 0.15;
  static #STONE_HIGH = 0.30;
  static #SAND_TINT = [0.77, 0.63, 0.38]; // #c4a060
  static #MUD_TINT = [0.23, 0.19, 0.13];  // #3a3020
  static #TEXTURE_BASE = '/textures/ground';

  #uniforms;

  // Larger than the legacy 200×200 plane so the physics heightfield extends
  // beyond Player.MAX_TRAVEL_RADIUS (120 m) in every direction — players
  // hit the soft horizontal clamp before they could escape the collider.
  constructor(scene, loader, { size = 260, segments = 170 } = {}) {
    this.size = size;
    this.segments = segments;

    const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
    geometry.rotateX(-Math.PI / 2);
    this.#displaceVertices(geometry);
    geometry.computeVertexNormals();

    const material = this.#buildMaterial(loader);
    patchShadowTint(material);

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.receiveShadow = true;
    this.mesh.name = 'terrain';
    scene.add(this.mesh);
  }

  #buildMaterial(loader) {
    const base = Terrain.#TEXTURE_BASE;
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
      t.anisotropy = 8;
      return t;
    };

    const grassMap   = colorTex('grass/Grass001_1K-PNG_Color.jpg');
    const dirtMap    = colorTex('dirt/Ground037_1K-PNG_Color.jpg');
    const stoneMap   = colorTex('stone/Rock026_1K-PNG_Color.jpg');
    const grassNorm  = normalTex('grass/Grass001_1K-PNG_NormalGL.png');
    const dirtNorm   = normalTex('dirt/Ground037_1K-PNG_NormalGL.png');
    const stoneNorm  = normalTex('stone/Rock026_1K-PNG_NormalGL.png');

    this.#uniforms = {
      uGrassMap:       { value: grassMap },
      uDirtMap:        { value: dirtMap },
      uStoneMap:       { value: stoneMap },
      uGrassNormal:    { value: grassNorm },
      uDirtNormal:     { value: dirtNorm },
      uStoneNormal:    { value: stoneNorm },
      uTerrainUvScale: { value: Terrain.#UV_SCALE },
      uGrassYLow:      { value: Terrain.#GRASS_Y_LOW },
      uSandYLow:       { value: Terrain.#SAND_Y_LOW },
      uMudYLow:        { value: Terrain.#MUD_Y_LOW },
      uStoneLow:       { value: Terrain.#STONE_LOW },
      uStoneHigh:      { value: Terrain.#STONE_HIGH },
      uSandTint:       { value: new THREE.Vector3(...Terrain.#SAND_TINT) },
      uMudTint:        { value: new THREE.Vector3(...Terrain.#MUD_TINT) },
    };

    const material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.95,
      metalness: 0,
    });
    // Assigning a normalMap forces three to set USE_NORMALMAP, which is what
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
           varying vec3 vWorldPos;
           varying vec3 vWorldNormalGeom;
           uniform sampler2D uGrassMap;
           uniform sampler2D uDirtMap;
           uniform sampler2D uStoneMap;
           uniform sampler2D uGrassNormal;
           uniform sampler2D uDirtNormal;
           uniform sampler2D uStoneNormal;
           uniform float uTerrainUvScale;
           uniform float uGrassYLow;
           uniform float uSandYLow;
           uniform float uMudYLow;
           uniform float uStoneLow;
           uniform float uStoneHigh;
           uniform vec3  uSandTint;
           uniform vec3  uMudTint;`
        )
        .replace(
          '#include <map_fragment>',
          // Sample three diffuse maps at worldspace XZ. _grassW selects
          // grass-vs-dirt by height; _mudW shifts the dirt tint from sandy
          // (beach band) to muddy (submerged) as Y drops. _stoneW overrides
          // both on steep slopes. Locals are shared with <normal_fragment_maps>.
          `vec2 _terrainUv = vWorldPos.xz / uTerrainUvScale;
           float _slope = clamp(1.0 - vWorldNormalGeom.y, 0.0, 1.0);
           float _grassW = smoothstep(uSandYLow, uGrassYLow, vWorldPos.y);
           float _mudW   = smoothstep(uSandYLow, uMudYLow, vWorldPos.y);
           float _stoneW = smoothstep(uStoneLow, uStoneHigh, _slope);

           vec3 _gCol = texture2D(uGrassMap, _terrainUv).rgb;
           vec3 _dCol = texture2D(uDirtMap,  _terrainUv).rgb;
           vec3 _sCol = texture2D(uStoneMap, _terrainUv).rgb;

           // Beach band uses the dirt texture × sand tint; submerged ground
           // uses the same dirt texture × mud tint. _mudW=0 ⇒ all sand,
           // _mudW=1 ⇒ all mud, with a smooth transition through the band.
           vec3 _belowGrass = mix(_dCol * uSandTint, _dCol * uMudTint, _mudW);
           vec3 _col = mix(_belowGrass, _gCol, _grassW);
           _col = mix(_col, _sCol, _stoneW);

           diffuseColor.rgb *= _col;`
        )
        .replace(
          '#include <normal_fragment_maps>',
          // Blend three tangent-space normals with the same weights, then
          // reconstruct TBN from screen-space derivatives. Dirt normal is
          // used everywhere except where grass dominates.
          `vec3 _nG = texture2D(uGrassNormal, _terrainUv).xyz * 2.0 - 1.0;
           vec3 _nD = texture2D(uDirtNormal,  _terrainUv).xyz * 2.0 - 1.0;
           vec3 _nS = texture2D(uStoneNormal, _terrainUv).xyz * 2.0 - 1.0;
           vec3 _mapN = mix(_nD, _nG, _grassW);
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
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      pos.setY(i, this.#islandHeightAt(x, z));
    }
    pos.needsUpdate = true;
  }

  /**
   * Inside ISLAND_RADIUS we keep the original gentle wave + spawn-flatten
   * the rest of the portfolio expects (signs/billboards/paths anchored at
   * y=0 sit naturally on the grass). Outside the island radius the land
   * drops away through a shore slope to the ocean floor.
   *
   * Used by physics (heightfield), grass placement and prop scatter — must
   * stay in lockstep with #displaceVertices, hence the shared helper.
   */
  #islandHeightAt(x, z) {
    const dist = Math.hypot(x, z);
    const R = Terrain.#ISLAND_RADIUS;
    const W = Terrain.#SHORE_WIDTH;

    if (dist <= R) {
      const wave =
        Math.sin(x * 0.08) * 0.25 +
        Math.cos(z * 0.07) * 0.22 +
        Math.sin((x + z) * 0.05) * 0.18;
      const flatten = THREE.MathUtils.smoothstep(dist, 8, 22);
      // INNER_FLOOR_Y keeps the slightest wave-dip above the water plane so
      // transparent ocean can't bleed through pixels inside the island.
      return Math.max(wave * flatten, Terrain.#INNER_FLOOR_Y);
    }

    const t = Math.min((dist - R) / W, 1.0);
    const h = Terrain.#OCEAN_FLOOR_Y * t;
    return Math.max(h, Terrain.#OCEAN_FLOOR_Y);
  }

  heightAt(x, z) {
    return this.#islandHeightAt(x, z);
  }
}
