import * as THREE from 'three';

/**
 * Footprints — pooled flat decal quads dropped one-per-step at the player's
 * feet, fading out over LIFETIME seconds.
 *
 * Architecture:
 *   - Single InstancedMesh of POOL_SIZE quads (PlaneGeometry rotated to lie
 *     flat on XZ, +Y normal). The mesh is allocated once; new prints
 *     overwrite the oldest slot via a ring-buffer cursor.
 *   - Material is a MeshBasicMaterial (not a raw ShaderMaterial) with the
 *     transparent muddy tread PNG as `map` + `alphaTest`. MeshBasicMaterial handles
 *     InstancedMesh setup (USE_INSTANCING, uv attribute injection) natively
 *     — a raw ShaderMaterial requires manual declarations and was the
 *     reason prints weren't rendering on first attempt.
 *   - Per-instance fade is injected via onBeforeCompile: a new
 *     `aAge` instanced attribute drives an opacity multiplier in the
 *     fragment shader; another `aMirror` flips UVs horizontally so a
 *     single asymmetric sole asset works for both feet.
 *
 * Cadence is driven externally: App wires AudioManager.onStep to onStep()
 * so audio + visual cadence stay aligned regardless of mute state.
 *
 * Surface guard: prints are suppressed over water, over the shore band
 * (r ≥ SAND_INNER) and on path tiles, so they only appear on grass.
 */

const POOL_SIZE = 40;
const LIFETIME = 10.0;
// Sole dims tuned to read as a sneaker tread from third-person camera height.
const SOLE_LENGTH = 0.58;
const SOLE_WIDTH = 0.27;
const FOOT_LATERAL = 0.13;  // half-distance between L and R prints
const STEP_BACK = 0.18;     // keep heel prints visible from follow camera
const SAND_INNER = 38;      // anything past this is shore/water — skip
// Y lift above the heightfield. Set well above the tallest grass tuft
// (~0.2–0.3 m at the default scale) so prints aren't covered by grass.
const PRINT_LIFT = 0.08;
const FOOTPRINT_MAP_URL = '/textures/foliage/footprint-tread.png?v=2';

export class Footprints {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Terrain.js').Terrain} terrain
   */
  constructor(scene, terrain) {
    this.scene = scene;
    this.terrain = terrain;
    this.pathPositions = new Float32Array(0);
    this.pathCount = 0;
    this.pathRadius = 1.4;

    this._cursor = 0;
    this._stepLeft = false;

    this.#build();
  }

  setPaths({ pathPositions, pathCount, pathRadius = 1.4 }) {
    this.pathPositions = pathPositions;
    this.pathCount = pathCount;
    this.pathRadius = pathRadius;
  }

  #build() {
    const geom = new THREE.PlaneGeometry(SOLE_WIDTH, SOLE_LENGTH);
    // Lay flat — long axis (Z after rotate) aligns with player forward.
    geom.rotateX(-Math.PI / 2);

    this._ages   = new Float32Array(POOL_SIZE);
    this._mirror = new Float32Array(POOL_SIZE);
    for (let i = 0; i < POOL_SIZE; i++) this._ages[i] = LIFETIME + 1; // dead

    const ageAttr    = new THREE.InstancedBufferAttribute(this._ages, 1).setUsage(THREE.DynamicDrawUsage);
    const mirrorAttr = new THREE.InstancedBufferAttribute(this._mirror, 1).setUsage(THREE.DynamicDrawUsage);
    geom.setAttribute('aAge', ageAttr);
    geom.setAttribute('aMirror', mirrorAttr);
    this._ageAttr = ageAttr;
    this._mirrorAttr = mirrorAttr;

    const tex = new THREE.TextureLoader().load(FOOTPRINT_MAP_URL);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearMipmapLinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 8;
    this._texture = tex;

    // The PNG carries both the muddy color and transparency, so the print
    // reads like disturbed soil instead of a tinted white mask/sticker.
    const material = new THREE.MeshBasicMaterial({
      color: new THREE.Color(0xffffff),
      map: tex,
      transparent: true,
      opacity: 1.0,
      depthWrite: false,
      // depthTest stays ON so prints behind the player are occluded — with
      // it off, renderOrder=4 paints them over the character regardless of
      // geometry. depthWrite stays off so prints don't shadow other
      // transparents (grass, water foam) sorted behind them.
      depthTest: true,
      side: THREE.DoubleSide,
      alphaTest: 0.04,
      // toneMapped off — ACES otherwise brightens the dark brown into a
      // muddy pink under day lighting which reads as a sticker, not mud.
      toneMapped: false,
    });
    this._material = material;

    // Patch the standard pipeline to add:
    //   - per-instance fade via aAge → alpha multiplier
    //   - per-instance UV mirror via aMirror (flip x)
    // We chain onBeforeCompile so any future material chunk modifications
    // (e.g. shadow tinting) can also stack on top.
    material.onBeforeCompile = (shader) => {
      shader.uniforms.uLifetime = { value: LIFETIME };
      shader.vertexShader = shader.vertexShader
        .replace(
          '#include <common>',
          `#include <common>
           attribute float aAge;
           attribute float aMirror;
           uniform float uLifetime;
           varying float vFade;`,
        )
        .replace(
          '#include <uv_vertex>',
          `#include <uv_vertex>
           // Mirror the right foot horizontally so a single asymmetric
           // sole asset renders both L and R correctly.
           #ifdef USE_MAP
             if (aMirror > 0.5) vMapUv.x = 1.0 - vMapUv.x;
           #endif
           float t = clamp(aAge / uLifetime, 0.0, 1.0);
           float fadeOut = 1.0 - smoothstep(0.7, 1.0, t);
           vFade = (aAge >= uLifetime) ? 0.0 : fadeOut;`,
        );
      shader.fragmentShader = shader.fragmentShader
        .replace(
          '#include <common>',
          `#include <common>
           varying float vFade;`,
        )
        .replace(
          '#include <alphatest_fragment>',
          `diffuseColor.a *= vFade;
           #include <alphatest_fragment>`,
        );
    };
    material.customProgramCacheKey = () => 'footprints-map-fade-v5';

    this._mesh = new THREE.InstancedMesh(geom, material, POOL_SIZE);
    this._mesh.frustumCulled = false;
    this._mesh.castShadow = false;
    this._mesh.receiveShadow = false;
    this._mesh.name = 'footprints';
    this._mesh.renderOrder = 4;
    this.scene.add(this._mesh);
  }

  /**
   * Drop a single footprint at the player's current foot position.
   *
   * @param {THREE.Vector3} playerPos
   * @param {number} facingYaw  player.group.rotation.y in radians
   * @param {boolean} [forceSide]  optional override of the L/R alternator.
   */
  onStep(playerPos, facingYaw, forceSide = null) {
    if (forceSide === null) this._stepLeft = !this._stepLeft;
    else this._stepLeft = !!forceSide;
    const leftFoot = this._stepLeft;

    // Forward unit at yaw=0 points +Z; rotate to get fx/fz.
    const fx = Math.sin(facingYaw);
    const fz = Math.cos(facingYaw);
    // Right unit, perpendicular to forward (right of motion).
    const rx = fz;
    const rz = -fx;

    const lateral = leftFoot ? -FOOT_LATERAL : FOOT_LATERAL;
    const stepX = playerPos.x + rx * lateral - fx * STEP_BACK;
    const stepZ = playerPos.z + rz * lateral - fz * STEP_BACK;

    // Grass-only surface guard.
    const r = Math.hypot(stepX, stepZ);
    if (r >= SAND_INNER) return;
    for (let i = 0; i < this.pathCount; i++) {
      const dx = stepX - this.pathPositions[i * 2];
      const dz = stepZ - this.pathPositions[i * 2 + 1];
      if (dx * dx + dz * dz < this.pathRadius * this.pathRadius) return;
    }

    const stepY = (this.terrain ? this.terrain.heightAt(stepX, stepZ) : 0) + PRINT_LIFT;

    const idx = this._cursor;
    this._cursor = (this._cursor + 1) % POOL_SIZE;

    this._ages[idx] = 0;
    this._mirror[idx] = leftFoot ? 0 : 1;

    _matrix.makeRotationY(facingYaw);
    _matrix.setPosition(stepX, stepY, stepZ);
    this._mesh.setMatrixAt(idx, _matrix);

    this._mesh.instanceMatrix.needsUpdate = true;
    this._ageAttr.needsUpdate = true;
    this._mirrorAttr.needsUpdate = true;

    // Achievement count only fires for prints that actually landed (after
    // the surface guard above), so the counter matches what the player can
    // see on the ground.
    this.achievements?.onFootprint?.();
  }

  /** Age every live instance once per frame. */
  update(delta) {
    let any = false;
    for (let i = 0; i < POOL_SIZE; i++) {
      if (this._ages[i] >= LIFETIME) continue;
      this._ages[i] += delta;
      any = true;
    }
    if (any) this._ageAttr.needsUpdate = true;
  }

}

const _matrix = new THREE.Matrix4();
