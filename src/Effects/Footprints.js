import * as THREE from 'three/webgpu';
import {
  texture, attribute, uv, vec2, vec3, float, mix, smoothstep, clamp, step,
} from 'three/tsl';

/**
 * Footprints — pooled flat decal quads dropped one-per-step at the player's
 * feet, fading out over LIFETIME seconds.
 *
 * Architecture:
 *   - Single InstancedMesh of POOL_SIZE quads (PlaneGeometry rotated to lie
 *     flat on XZ, +Y normal). The mesh is allocated once; new prints
 *     overwrite the oldest slot via a ring-buffer cursor.
 *   - Material is a MeshBasicNodeMaterial (the project renders with
 *     WebGPURenderer, so material logic must live in TSL nodes — GLSL
 *     onBeforeCompile patching is silently ignored by the WebGPU backend).
 *     Three per-instance attributes drive the look: `aAge` → fade-out,
 *     `aMirror` → horizontal UV flip so one asymmetric sole serves both feet,
 *     and `aSnow` → 0 on bare ground, or a ~0.6–1.4 depth factor that recolours
 *     the print into a pale, cold pressed-in snow dent.
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
// Y lift above the heightfield — just enough to beat z-fighting with the
// ground. Grass is disabled, so the print sits planted on the surface rather
// than hovering. The quad is also tilted to the terrain normal (see onStep).
const PRINT_LIFT = 0.02;
// On snow the GROUND mesh is displaced up ~0.1–0.16 m by terrainSnowDrift
// (shader-only — heightAt still returns bare terrain). A bare-height print
// would be buried + depth-occluded by the raised snow, so snow prints ride
// higher to sit on the snow surface, reading as a pressed-in dent.
const SNOW_PRINT_LIFT = 0.16;
const FOOTPRINT_MAP_URL = '/textures/foliage/footprint-tread.png?v=2';

export class Footprints {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Terrain.js').Terrain} terrain
   */
  constructor(scene, terrain, { loader = null } = {}) {
    this.scene = scene;
    this.terrain = terrain;
    this.loader = loader;
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
    this._snow   = new Float32Array(POOL_SIZE); // 1 = print was laid on snow
    for (let i = 0; i < POOL_SIZE; i++) this._ages[i] = LIFETIME + 1; // dead

    const ageAttr    = new THREE.InstancedBufferAttribute(this._ages, 1).setUsage(THREE.DynamicDrawUsage);
    const mirrorAttr = new THREE.InstancedBufferAttribute(this._mirror, 1).setUsage(THREE.DynamicDrawUsage);
    const snowAttr   = new THREE.InstancedBufferAttribute(this._snow, 1).setUsage(THREE.DynamicDrawUsage);
    geom.setAttribute('aAge', ageAttr);
    geom.setAttribute('aMirror', mirrorAttr);
    geom.setAttribute('aSnow', snowAttr);
    this._ageAttr = ageAttr;
    this._mirrorAttr = mirrorAttr;
    this._snowAttr = snowAttr;

    // TSL node material — the WebGPU backend ignores GLSL onBeforeCompile, so
    // all per-instance logic (fade / mirror / snow recolour) lives in nodes.
    const material = new THREE.MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      // depthTest stays ON so prints behind the player are occluded — with
      // it off, renderOrder=4 paints them over the character regardless of
      // geometry. depthWrite stays off so prints don't shadow other
      // transparents (grass, water foam) sorted behind them.
      depthTest: true,
      side: THREE.DoubleSide,
      // toneMapped off — ACES otherwise brightens the dark brown into a
      // muddy pink which reads as a sticker, not mud.
      toneMapped: false,
    });
    material.alphaTest = 0.04;

    const applyTexture = (map) => {
      const aAge = attribute('aAge', 'float');
      const aMirror = attribute('aMirror', 'float');
      const aSnow = attribute('aSnow', 'float');

      // Mirror the right foot horizontally so one asymmetric sole serves L and R.
      const baseUv = uv();
      const mirroredU = mix(baseUv.x, baseUv.x.oneMinus(), step(0.5, aMirror));
      const texel = texture(map, vec2(mirroredU, baseUv.y));

      // Age fade: full until 70% of life, ramp to 0 by the end (dead slots have
      // age ≥ LIFETIME → fade 0 → discarded by alphaTest).
      const t = clamp(aAge.div(LIFETIME), 0.0, 1.0);
      const fade = smoothstep(0.7, 1.0, t).oneMinus();

      // Snow recolour: the brown mud tread becomes a pale, COLD pressed-in dent
      // so it reads as packed snow (white family), not a brown/black sticker.
      // aSnow > 0 means "on snow"; its magnitude (~0.6–1.4) is a per-print depth
      // so some prints are stronger/darker than others, like a real trail.
      const isSnow = step(0.01, aSnow);
      const depth = clamp(aSnow, 0.0, 1.4);
      const snowTint = vec3(0.66, 0.74, 0.86); // cold light blue-grey snow shadow
      const snowRgb = mix(texel.rgb, snowTint, clamp(depth.mul(0.88), 0.0, 0.96));
      material.colorNode = mix(texel.rgb, snowRgb, isSnow);

      // Alpha: texture cutout × age fade, with snow prints depth-scaled so the
      // shallow ones stay faint.
      const snowAlpha = clamp(float(0.5).add(depth.mul(0.35)), 0.0, 1.0);
      const alphaMul = mix(float(1.0), snowAlpha, isSnow);
      material.opacityNode = texel.a.mul(fade).mul(alphaMul);
      material.needsUpdate = true;
    };

    this._material = material;

    this._mesh = new THREE.InstancedMesh(geom, material, POOL_SIZE);
    this._mesh.frustumCulled = false;
    this._mesh.castShadow = false;
    this._mesh.receiveShadow = false;
    this._mesh.name = 'footprints';
    this._mesh.renderOrder = 4;
    this.scene.add(this._mesh);

    // Tread texture: prefer the block-compressed KTX2 (47KB on disk, stays
    // compressed in VRAM); fetch the 331KB PNG ONLY if KTX2 is unavailable or
    // fails — never both. No print is on screen at boot (pool starts dead), so
    // the async swap-in is invisible.
    const configure = (map) => {
      map.colorSpace = THREE.SRGBColorSpace;
      map.minFilter = THREE.LinearMipmapLinearFilter;
      map.magFilter = THREE.LinearFilter;
      map.anisotropy = 8;
      this._texture = map;
      applyTexture(map);
    };
    const loadPng = () => {
      const tex = new THREE.TextureLoader().load(FOOTPRINT_MAP_URL);
      configure(tex);
    };
    if (this.loader?.loadKTX2) {
      this.loader
        .loadKTX2('/textures/foliage/footprint-tread.ktx2')
        .then(configure)
        .catch(loadPng);
    } else {
      loadPng();
    }
  }

  /**
   * Drop a single footprint at the player's current foot position.
   *
   * @param {THREE.Vector3} playerPos
   * @param {number} facingYaw  player.group.rotation.y in radians
   * @param {boolean} [forceSide]  optional override of the L/R alternator.
   * @param {boolean} [onSnow]  true → render as a compressed-snow dent.
   */
  onStep(playerPos, facingYaw, forceSide = null, onSnow = false) {
    if (forceSide === null) this._stepLeft = !this._stepLeft;
    else this._stepLeft = !!forceSide;
    const leftFoot = this._stepLeft;

    // Forward unit at yaw=0 points +Z; rotate to get fx/fz.
    const fx = Math.sin(facingYaw);
    const fz = Math.cos(facingYaw);
    // Right unit, perpendicular to forward (right of motion).
    const rx = fz;
    const rz = -fx;

    // Small per-step jitter so a trail reads like a real gait — prints land at
    // slightly varied spots/angles/depths instead of a perfect repeating line.
    const jLateral = (Math.random() - 0.5) * 0.06;
    const jBack = (Math.random() - 0.5) * 0.08;
    const lateral = (leftFoot ? -FOOT_LATERAL : FOOT_LATERAL) + jLateral;
    const stepBack = STEP_BACK + jBack;
    const stepX = playerPos.x + rx * lateral - fx * stepBack;
    const stepZ = playerPos.z + rz * lateral - fz * stepBack;
    const printYaw = facingYaw + (Math.random() - 0.5) * 0.22;

    // Grass-only surface guard.
    const r = Math.hypot(stepX, stepZ);
    if (r >= SAND_INNER) return;
    for (let i = 0; i < this.pathCount; i++) {
      const dx = stepX - this.pathPositions[i * 2];
      const dz = stepZ - this.pathPositions[i * 2 + 1];
      if (dx * dx + dz * dz < this.pathRadius * this.pathRadius) return;
    }

    const lift = onSnow ? SNOW_PRINT_LIFT : PRINT_LIFT;
    const stepY = (this.terrain ? this.terrain.heightAt(stepX, stepZ) : 0) + lift;

    const idx = this._cursor;
    this._cursor = (this._cursor + 1) % POOL_SIZE;

    this._ages[idx] = 0;
    this._mirror[idx] = leftFoot ? 0 : 1;
    // 0 = not snow. On snow, store a varied DEPTH factor (~0.6–1.4) so prints
    // read as some-deep, some-shallow dents rather than identical stamps.
    this._snow[idx] = onSnow ? 0.6 + Math.random() * 0.8 : 0;

    // Orient the quad to the terrain so it conforms to slopes instead of
    // floating level. Sample the heightfield around the step to get a surface
    // normal, project the player's facing onto that plane for the long axis,
    // then build an orthonormal basis (local +Y → normal, +Z → forward).
    if (this.terrain) {
      const e = 0.3;
      const hL = this.terrain.heightAt(stepX - e, stepZ);
      const hR = this.terrain.heightAt(stepX + e, stepZ);
      const hD = this.terrain.heightAt(stepX, stepZ - e);
      const hU = this.terrain.heightAt(stepX, stepZ + e);
      _up.set(hL - hR, 2 * e, hD - hU).normalize();
    } else {
      _up.set(0, 1, 0);
    }
    _fwd.set(Math.sin(printYaw), 0, Math.cos(printYaw));
    _right.crossVectors(_up, _fwd).normalize();
    _fwd.crossVectors(_right, _up).normalize(); // re-orthogonalize against the slope
    _matrix.makeBasis(_right, _up, _fwd);
    _matrix.setPosition(stepX, stepY, stepZ);
    this._mesh.setMatrixAt(idx, _matrix);

    this._mesh.instanceMatrix.needsUpdate = true;
    this._ageAttr.needsUpdate = true;
    this._mirrorAttr.needsUpdate = true;
    this._snowAttr.needsUpdate = true;

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
const _up = new THREE.Vector3();
const _fwd = new THREE.Vector3();
const _right = new THREE.Vector3();
