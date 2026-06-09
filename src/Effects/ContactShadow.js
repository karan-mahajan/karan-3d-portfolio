import * as THREE from 'three/webgpu';
import { uv, vec2, vec3, smoothstep, uniform } from 'three/tsl';

/**
 * ContactShadow — a single soft radial blob drawn flat on the terrain directly
 * under the player. It's the primary "feet are on the ground" cue: the scene's
 * only real shadow is one soft 512² sun map, which is too weak/spread to read
 * as contact, and the character's fill/spot lights don't cast at all. This
 * tight ambient-occlusion pool fills that gap cheaply (one draw call, no asset).
 *
 * Procedural, no texture: a TSL MeshBasicNodeMaterial whose opacity is a radial
 * falloff (the WebGPU backend ignores GLSL onBeforeCompile, so the look lives in
 * nodes — same constraint as Footprints.js).
 *
 * Each frame the blob is positioned on the heightfield under the player, tilted
 * to the terrain normal so it conforms to slopes/steps, lifted onto the snow
 * surface when snow is accumulating, and faded/spread as the feet leave the
 * ground (jump / backflip / cartwheel) so it never drags a pool through the air.
 *
 * Phase 2 (foot IK) would upgrade this to two per-foot blobs tracking the
 * groundBones — see the loading-screen-redesign sibling plan note.
 */

// Visible blob diameter ≈ 2 × this when grounded. Tuned to sit just under the
// stance width and read from third-person camera height.
const BASE_RADIUS = 0.45;
// Foot-above-ground distance (m) at which the blob has fully faded — a shadow
// vanishes as its caster climbs out of contact range.
const AIR_FADE = 1.2;
// Peak opacity — a contact pool, not a hard drop shadow. Kept low so it reads
// as occlusion under the feet and complements (not fights) the real sun shadow.
const PEAK_OPACITY = 0.4;
// Y lift above the sampled surface, just enough to beat z-fighting (mirrors
// Footprints' PRINT_LIFT).
const SURFACE_LIFT = 0.02;
// On snow the GROUND mesh is displaced up ~0.16 m by terrainSnowDrift (shader
// only — heightAt returns bare terrain), so a bare-height blob would sink under
// the snow. Ride up by coverage × this to sit on the snow surface.
const SNOW_LIFT = 0.16;

const _up = new THREE.Vector3();
const _fwd = new THREE.Vector3();
const _right = new THREE.Vector3();
const _basis = new THREE.Matrix4();

export class ContactShadow {
  /**
   * @param {THREE.Scene} scene
   * @param {object} [opts]
   * @param {object} [opts.quality]  detectQuality() result; pass `contactShadow:false` to disable.
   */
  constructor(scene, { quality = {} } = {}) {
    this.scene = scene;
    // Cheap enough to keep on every tier — it's the main grounding cue, so it
    // matters most on weak/mobile HW. Honour an explicit opt-out only.
    this.enabled = quality.contactShadow !== false;
    if (!this.enabled) return;

    this._strength = uniform(0.0);
    this.#build();
  }

  #build() {
    const geom = new THREE.PlaneGeometry(1, 1);
    geom.rotateX(-Math.PI / 2); // lie flat on XZ, +Y normal

    const material = new THREE.MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false, // don't occlude grass/water transparents behind it
      depthTest: true, // terrain in front still hides it on steep ground
      side: THREE.DoubleSide,
      toneMapped: false, // keep the dark pool dark — ACES would lift it grey
    });

    // Radial falloff: opaque at centre, 0 by the inscribed-circle edge (d=0.5).
    const d = uv().sub(vec2(0.5)).length();
    const falloff = smoothstep(0.5, 0.0, d);
    material.colorNode = vec3(0.0);
    material.opacityNode = falloff.mul(this._strength);

    this._mesh = new THREE.Mesh(geom, material);
    this._mesh.frustumCulled = false;
    this._mesh.castShadow = false;
    this._mesh.receiveShadow = false;
    this._mesh.renderOrder = 2; // under footprints (renderOrder 4)
    this._mesh.name = 'contact-shadow';
    this._mesh.visible = false; // shown once the first update places it
    this.scene.add(this._mesh);
  }

  /**
   * Position + fade the blob under the player. Call once per frame AFTER the
   * visual update (interpolated group.position + mixer-synced bones), so the
   * lowest-foot read is valid for this frame.
   *
   * @param {import('../Player/Player.js').Player} player
   * @param {{ heightAt:(x:number,z:number)=>number }} terrain
   * @param {{ coverage?:number }} [weather]
   */
  update(player, terrain, weather = null) {
    if (!this.enabled || !this._mesh || !terrain) return;

    const pos = player.position;
    const x = pos.x;
    const z = pos.z;
    const groundY = terrain.heightAt(x, z);

    // World Y of the lowest foot bone (groupY + the bone's offset from origin).
    // Comparing it to the bare ground gives the airborne gap directly: ~0 when
    // planted, large on a jump — which both fades and spreads the pool.
    const contactLocalY = player.character?.lowestContactLocalY?.() ?? 0;
    const footY = pos.y + contactLocalY;
    const airGap = Math.max(0, footY - groundY);

    // Fade out as the feet climb away from the ground.
    const fade = 1 - smoothstepScalar(0, AIR_FADE, airGap);
    this._strength.value = PEAK_OPACITY * fade;

    if (fade <= 0.001) {
      this._mesh.visible = false;
      return;
    }
    this._mesh.visible = true;

    // Sit on the snow surface (not buried) when snow is accumulating; matches
    // the terrainSnowDrift(0.16) the ground shader applies in GlbV3World.
    const snowLift = (weather?.coverage ?? 0) * SNOW_LIFT;
    const y = groundY + SURFACE_LIFT + snowLift;

    // Spread a touch as the caster lifts, like a softening shadow.
    const radius = BASE_RADIUS * (1 + airGap * 0.25);

    // Tilt to the terrain normal so the pool conforms to slopes/steps instead
    // of hovering flat (same 4-point finite-difference normal as Footprints).
    const e = 0.3;
    const hL = terrain.heightAt(x - e, z);
    const hR = terrain.heightAt(x + e, z);
    const hD = terrain.heightAt(x, z - e);
    const hU = terrain.heightAt(x, z + e);
    _up.set(hL - hR, 2 * e, hD - hU).normalize();
    // Any horizontal reference for the long axis — the blob is radial, so the
    // exact yaw doesn't matter; just build an orthonormal frame on the slope.
    _fwd.set(0, 0, 1);
    _right.crossVectors(_up, _fwd).normalize();
    _fwd.crossVectors(_right, _up).normalize();
    _basis.makeBasis(_right, _up, _fwd);

    // Let Three compose the matrix from these (matrixAutoUpdate stays on, so
    // matrixWorld refreshes correctly each frame).
    this._mesh.position.set(x, y, z);
    this._mesh.quaternion.setFromRotationMatrix(_basis);
    this._mesh.scale.setScalar(radius * 2);
  }

  dispose() {
    if (!this._mesh) return;
    this.scene.remove(this._mesh);
    this._mesh.geometry.dispose();
    this._mesh.material.dispose();
    this._mesh = null;
  }
}

// CPU-side smoothstep for the strength fade (the GPU smoothstep node only runs
// inside the shader; this drives the JS-side uniform + visibility cull).
function smoothstepScalar(edge0, edge1, v) {
  const t = Math.min(1, Math.max(0, (v - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}
