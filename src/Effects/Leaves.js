import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import {
  Fn, attribute, uniform, vec3, float,
  positionGeometry, uv, sin, cos, cross, dot, normalize, texture,
} from 'three/tsl';

/**
 * Autumn leaves drifting through the air, landing on the terrain, and
 * eventually recycling back to the top when the pool fills.
 *
 * Each leaf has two phases:
 *   - Falling: world position updated CPU-side each frame (fall + wind drift),
 *     tumble angle accumulated, XZ mod-wrapped around the player so the
 *     swirl follows them. Drift = wind.dir * driftCoeff * wind.strength.
 *   - Settled: leaf has hit terrain (terrain.heightAt > water level). It
 *     freezes in WORLD coords, lies flat with a baked yaw, and shrinks/
 *     recycles only once the pool of settled leaves exceeds MAX_SETTLED
 *     (oldest-first) so the air never empties out.
 *
 * B0/WebGPU: ported from the raw-GLSL ShaderMaterial (which deep-merged
 * UniformsLib.lights + fog — neither exported by `three/webgpu`) to a
 * MeshLambertNodeMaterial. Lighting, fog and shadow reception now come from the
 * node-material pipeline for free; the per-leaf transform (tumble in flight /
 * lay-flat when settled) lives in `material.positionNode`, and the leaf-mask
 * cutout is an `alphaTest` on the mask's red channel. The old magenta
 * shadow-tint (a grass-matching stylistic flourish) is dropped — there is no
 * grass in v3 yet and the lit leaves read cleaner. The CPU simulation is
 * unchanged. Toggle via setEnabled(); persists under 'karan-portfolio:leaves'.
 */

const DEFAULT_COUNT = 120;
const DEFAULT_MAX_SETTLED = 80;
const VOL_X = 60;
const VOL_Z = 60;
const HALF_X = VOL_X * 0.5;
const HALF_Z = VOL_Z * 0.5;
const Y_MIN = 6.0;
const Y_MAX = 14.0;
const LEAF_SIZE = 0.15;
const FALL_MIN = 0.4;
const FALL_MAX = 1.0;
const DRIFT_MIN = 0.6;
const DRIFT_MAX = 1.4;
const SPIN_MIN = 0.3;
const SPIN_MAX = 1.2;
// Recycle fade: when an over-pool settled leaf is chosen for recycling we
// shrink it to 0 over FADE_DURATION before respawning at the top.
const FADE_DURATION = 0.5;
// Lift settled leaves clear of the heightfield. 0.02 was barely above the
// painted terrain — flat, edge-on and often lost in the grass base, so leaves
// looked like they vanished the instant they landed. A larger lift keeps the
// resting quad readable from the third-person camera without floating.
const SETTLE_LIFT = 0.06;
// Settled leaves lie flat (near edge-on from a low camera) so they read much
// smaller than a tumbling one. Scale the resting quad up so it stays visible.
const SETTLE_SCALE = 1.6;
// Only settle when the heightfield is above this — under it we're over the
// shore slope / ocean and the leaf should respawn instead of resting on water.
const SETTLE_MIN_GROUND_Y = 0.0;
// Water surface (matches Water.js WATER_LEVEL_Y). Over-water falling leaves
// respawn here instead of falling to the ocean floor.
const WATER_LEVEL_Y = 0.0;
const STORAGE_KEY = 'karan-portfolio:leaves';
const LEAF_MASK_URL = '/textures/foliage/leaf-mask.png';

// Autumn palette — orange / red-orange / yellow-amber / brown. Distinct from
// the white wind streaks and amber firefly points so the scene reads as
// three separate atmospheric layers, not one mush.
const PALETTE = [
  new THREE.Color('#d97a2b'),
  new THREE.Color('#c44a18'),
  new THREE.Color('#e8a93d'),
  new THREE.Color('#8b5a2b'),
];

export class Leaves {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Wind.js').Wind} wind        Read-only; supplies direction + strength.
   * @param {import('../World/Terrain.js').Terrain} [terrain]  Heightfield sampler — leaves land on this.
   */
  constructor(scene, wind, terrain = null, { count = DEFAULT_COUNT, maxSettled = DEFAULT_MAX_SETTLED } = {}) {
    this.scene = scene;
    this.wind = wind;
    this.terrain = terrain;
    this.count = Math.max(8, Math.floor(count));
    this.maxSettled = Math.max(0, Math.floor(maxSettled));
    this.enabled = localStorage.getItem(STORAGE_KEY) !== '0';
    // Runtime gate, separate from the persisted `enabled` toggle. App holds
    // leaves off the spawn frame and suppresses them while it's snowing — both
    // without overwriting the visitor's saved leaves-on/off preference.
    this._active = true;

    this.#buildMesh();
    this.mesh.visible = this.enabled;
    this.#installButton();
  }

  // ── Geometry + material ──────────────────────────────────────────────────
  #buildMesh() {
    const base = new THREE.PlaneGeometry(1, 1);
    const instGeom = new THREE.InstancedBufferGeometry();
    instGeom.setAttribute('position', base.attributes.position);
    instGeom.setAttribute('uv', base.attributes.uv);
    instGeom.setIndex(base.index);
    instGeom.instanceCount = this.count;
    // Bounding sphere set huge so frustum-culling never drops us — leaves
    // live in a player-following volume, so per-frame culling math would be
    // wrong anyway.
    instGeom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    this.offsets     = new Float32Array(this.count * 3);
    this.spinAxes    = new Float32Array(this.count * 3);
    this.angles      = new Float32Array(this.count);
    this.tints       = new Float32Array(this.count * 3);
    this.falls       = new Float32Array(this.count);
    this.drifts      = new Float32Array(this.count);
    this.spinSpeeds  = new Float32Array(this.count);
    // Per-leaf settled state. settled[i] = 1 means frozen on the ground.
    this.settled     = new Float32Array(this.count);
    this.settledYaw  = new Float32Array(this.count);
    this.scales      = new Float32Array(this.count);
    this.landedAt    = new Float32Array(this.count); // elapsed-time when settled
    this.fadeTimer   = new Float32Array(this.count); // >0 while recycling-shrink
    this._settledCount = 0;
    this._elapsed = 0;

    for (let i = 0; i < this.count; i++) {
      const ix = i * 3;
      // Initial volume centered on origin — player spawns at (0,0,0) so
      // first frame already shows leaves around them.
      this.offsets[ix]     = (Math.random() - 0.5) * VOL_X;
      this.offsets[ix + 1] = Y_MIN + Math.random() * (Y_MAX - Y_MIN);
      this.offsets[ix + 2] = (Math.random() - 0.5) * VOL_Z;

      // Random unit axis — uniform on the sphere via the standard
      // (cos θ, φ) parametrization.
      const u = Math.random() * 2 - 1;
      const phi = Math.random() * Math.PI * 2;
      const r = Math.sqrt(1 - u * u);
      this.spinAxes[ix]     = Math.cos(phi) * r;
      this.spinAxes[ix + 1] = u;
      this.spinAxes[ix + 2] = Math.sin(phi) * r;

      this.angles[i]     = Math.random() * Math.PI * 2;
      this.falls[i]      = FALL_MIN + Math.random() * (FALL_MAX - FALL_MIN);
      this.drifts[i]     = DRIFT_MIN + Math.random() * (DRIFT_MAX - DRIFT_MIN);
      this.spinSpeeds[i] = SPIN_MIN + Math.random() * (SPIN_MAX - SPIN_MIN);
      this.scales[i]     = 1.0;

      const tint = PALETTE[(Math.random() * PALETTE.length) | 0];
      this.tints[ix]     = tint.r;
      this.tints[ix + 1] = tint.g;
      this.tints[ix + 2] = tint.b;
    }

    // WebGPU caps a pipeline at 8 vertex buffers. position + uv + 7 instanced
    // attrs = 9 overflowed it ("Vertex buffer count (9) exceeds the maximum").
    // Pack the seven instanced attrs into THREE vec4 buffers + one scalar →
    // 2 (geometry) + 4 (instanced) = 6 vertex buffers. The packed arrays are
    // (re)filled from the per-leaf sim arrays by #packBuffers() each frame.
    this.aOffsetScale = new Float32Array(this.count * 4); // offset.xyz, scale
    this.aSpinAngle   = new Float32Array(this.count * 4); // spinAxis.xyz, angle
    this.aTintSettled = new Float32Array(this.count * 4); // tint.xyz, settled

    this.offsetScaleAttr = new THREE.InstancedBufferAttribute(this.aOffsetScale, 4);
    this.offsetScaleAttr.setUsage(THREE.DynamicDrawUsage);
    this.spinAngleAttr   = new THREE.InstancedBufferAttribute(this.aSpinAngle, 4);
    this.spinAngleAttr.setUsage(THREE.DynamicDrawUsage);
    this.tintSettledAttr = new THREE.InstancedBufferAttribute(this.aTintSettled, 4);
    this.tintSettledAttr.setUsage(THREE.DynamicDrawUsage);
    // settledYaw stays a standalone scalar buffer (written in #settleLeaf).
    this.settledYawAttr  = new THREE.InstancedBufferAttribute(this.settledYaw, 1);
    this.settledYawAttr.setUsage(THREE.DynamicDrawUsage);

    instGeom.setAttribute('aOffsetScale', this.offsetScaleAttr);
    instGeom.setAttribute('aSpinAngle',   this.spinAngleAttr);
    instGeom.setAttribute('aTintSettled', this.tintSettledAttr);
    instGeom.setAttribute('aSettledYaw',  this.settledYawAttr);

    // Texture: single-channel mask, linear-sampled, no color-space conversion
    // (we sample .r as a raw alpha value, gamma would skew the threshold).
    const tex = new THREE.TextureLoader().load(LEAF_MASK_URL);
    tex.colorSpace = THREE.NoColorSpace;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 4;

    const uSize = uniform(LEAF_SIZE);

    this.material = new MeshLambertNodeMaterial({
      side: THREE.DoubleSide,
      transparent: false,
    });
    // Hard cutout from the leaf mask's red channel (alphaTest, not blending,
    // so leaves sort cleanly against trees / each other).
    this.material.alphaTest = 0.1;
    this.material.opacityNode = texture(tex, uv()).r;
    this.material.colorNode = attribute('aTintSettled').xyz;
    // Flat top-facing normal — gives a gentle, consistent sun/ambient response
    // across all leaves regardless of their tumble (matches Bruno's RainLines
    // `normalNode: vec3(0,1,0)` choice for billboard-ish geometry).
    this.material.normalNode = vec3(0.0, 1.0, 0.0);

    // Per-leaf transform: tumble (Rodrigues axis-angle) while falling, or
    // lay-flat with a baked yaw once settled. Mesh sits at the origin with
    // identity transform, so the returned world position passes through cleanly.
    this.material.positionNode = Fn(() => {
      const offsetScale = attribute('aOffsetScale'); // .xyz offset, .w scale
      const spinAngle = attribute('aSpinAngle');     // .xyz axis,   .w angle
      const settled = attribute('aTintSettled').w;
      const local = positionGeometry.mul(uSize).mul(offsetScale.w).toVar();

      // Tumbling (Rodrigues): local*c + cross(axis,local)*s + axis*dot(axis,local)*(1-c)
      const axis = normalize(spinAngle.xyz);
      const angle = spinAngle.w;
      const c = cos(angle);
      const s = sin(angle);
      const t = float(1.0).sub(c);
      const rotTumble = local.mul(c)
        .add(cross(axis, local).mul(s))
        .add(axis.mul(dot(axis, local).mul(t)));

      // Settled: lay flat (swap Y/Z so the +Z plane-normal points +Y) then
      // yaw around world-Y by aSettledYaw.
      const r1 = vec3(local.x, local.z, local.y.negate());
      const yaw = attribute('aSettledYaw');
      const cy = cos(yaw);
      const sy = sin(yaw);
      const rotSettled = vec3(
        cy.mul(r1.x).add(sy.mul(r1.z)),
        r1.y,
        sy.negate().mul(r1.x).add(cy.mul(r1.z)),
      );

      const rotated = settled.greaterThan(0.5).select(rotSettled, rotTumble);
      return offsetScale.xyz.add(rotated);
    })();

    this.mesh = new THREE.Mesh(instGeom, this.material);
    this.mesh.name = 'leaves';
    this.mesh.frustumCulled = false;
    this.mesh.receiveShadow = true;
    this.scene.add(this.mesh);

    // Seed the packed GPU buffers so the first rendered frame is correct even
    // before update() runs (e.g. leaves disabled on boot).
    this.#packBuffers();
  }

  /** Pack the per-leaf sim arrays into the 3 vec4 instanced buffers (+ the
   *  standalone settledYaw scalar) and flag them for upload. count is small
   *  (~120) so the per-frame repack is negligible. */
  #packBuffers() {
    for (let i = 0; i < this.count; i++) {
      const i3 = i * 3;
      const i4 = i * 4;
      this.aOffsetScale[i4]     = this.offsets[i3];
      this.aOffsetScale[i4 + 1] = this.offsets[i3 + 1];
      this.aOffsetScale[i4 + 2] = this.offsets[i3 + 2];
      this.aOffsetScale[i4 + 3] = this.scales[i];
      this.aSpinAngle[i4]       = this.spinAxes[i3];
      this.aSpinAngle[i4 + 1]   = this.spinAxes[i3 + 1];
      this.aSpinAngle[i4 + 2]   = this.spinAxes[i3 + 2];
      this.aSpinAngle[i4 + 3]   = this.angles[i];
      this.aTintSettled[i4]     = this.tints[i3];
      this.aTintSettled[i4 + 1] = this.tints[i3 + 1];
      this.aTintSettled[i4 + 2] = this.tints[i3 + 2];
      this.aTintSettled[i4 + 3] = this.settled[i];
    }
    this.offsetScaleAttr.needsUpdate = true;
    this.spinAngleAttr.needsUpdate = true;
    this.tintSettledAttr.needsUpdate = true;
    this.settledYawAttr.needsUpdate = true; // settledYaw written in-place by #settleLeaf
  }

  // ── Toggle ───────────────────────────────────────────────────────────────
  setEnabled(value) {
    this.enabled = value;
    this.mesh.visible = value && this._active;
    localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
    this.#updateButton();
  }
  toggle() { this.setEnabled(!this.enabled); }

  /** Runtime suppression that does NOT touch the persisted preference. App
   *  drives this each frame: false during the spawn hold and while it snows. */
  setActive(value) {
    if (this._active === value) return;
    this._active = value;
    this.mesh.visible = this.enabled && value;
  }

  #installButton() {
    const btn = document.createElement('button');
    btn.className = 'leaves-toggle';
    btn.setAttribute('aria-label', 'Toggle leaves');
    btn.innerHTML = this.enabled ? leafOn : leafOff;
    btn.addEventListener('click', () => this.toggle());
    document.body.appendChild(btn);
    this._btn = btn;
  }
  #updateButton() {
    if (this._btn) this._btn.innerHTML = this.enabled ? leafOn : leafOff;
  }

  // ── Per-frame ────────────────────────────────────────────────────────────
  /**
   * Fall, drift, spin, wrap, settle, recycle. The falling volume tracks the
   * player; settled leaves stay frozen in world coords. Once more than
   * MAX_SETTLED leaves are on the ground, the oldest one fades out and
   * respawns at the top so the air never empties.
   *
   * @param {number} delta seconds since last frame
   * @param {THREE.Vector3} playerPos
   */
  update(delta, playerPos) {
    if (!this.enabled || !this._active) return;

    this._elapsed += delta;
    const dir = this.wind.uniforms.uWindDir.value;
    const strength = this.wind.uniforms.uWindStrength.value;
    const dx = dir.x;
    const dz = dir.y;
    const px = playerPos.x;
    const pz = playerPos.z;

    for (let i = 0; i < this.count; i++) {
      const ix = i * 3;

      // Recycling-shrink branch: a settled leaf chosen for replacement
      // shrinks to 0 over FADE_DURATION, then respawns at top.
      if (this.fadeTimer[i] > 0) {
        this.fadeTimer[i] -= delta;
        this.scales[i] = Math.max(0, this.fadeTimer[i] / FADE_DURATION);
        if (this.fadeTimer[i] <= 0) {
          this.#respawnLeaf(i, px, pz);
        }
        continue;
      }

      if (this.settled[i] > 0.5) {
        // Frozen — no fall, no drift, no spin, no wrap. We leave the
        // settled leaf at its world position so it stays where it landed
        // even as the player walks past.
        continue;
      }

      // Fall + horizontal wind drift.
      this.offsets[ix]     += dx * this.drifts[i] * strength * delta;
      this.offsets[ix + 1] -= this.falls[i] * delta;
      this.offsets[ix + 2] += dz * this.drifts[i] * strength * delta;

      // Tumble.
      this.angles[i] += this.spinSpeeds[i] * delta;

      // Sample terrain at the leaf's current XZ. On land we settle when the
      // leaf reaches the heightfield; over water we respawn the moment the
      // leaf reaches the water surface so it doesn't keep falling toward
      // the ocean floor at y=-2 (which would leave it visible mid-air over
      // open ocean for tens of seconds).
      const groundY = this.terrain ? this.terrain.heightAt(this.offsets[ix], this.offsets[ix + 2]) : 0;
      const overWater = groundY <= SETTLE_MIN_GROUND_Y;
      if (overWater) {
        if (this.offsets[ix + 1] <= WATER_LEVEL_Y) {
          this.#respawnLeaf(i, px, pz);
          continue;
        }
      } else if (this.offsets[ix + 1] <= groundY + SETTLE_LIFT) {
        this.#settleLeaf(i, groundY);
        continue;
      }

      // XZ wrap — same mod-wrap trick as WindLines so the falling volume
      // travels with the player without re-randomizing in-flight leaves.
      const rx = this.offsets[ix] - px;
      if (rx >  HALF_X) this.offsets[ix] -= VOL_X;
      else if (rx < -HALF_X) this.offsets[ix] += VOL_X;

      const rz = this.offsets[ix + 2] - pz;
      if (rz >  HALF_Z) this.offsets[ix + 2] -= VOL_Z;
      else if (rz < -HALF_Z) this.offsets[ix + 2] += VOL_Z;
    }

    // Recycle policy: while too many leaves sit on the ground, mark the
    // oldest non-fading one to fade out. We mark one per frame so a single
    // huge backlog drains over multiple frames instead of popping all at once.
    if (this._settledCount > this.maxSettled) {
      let oldestIdx = -1;
      let oldestTime = Infinity;
      for (let i = 0; i < this.count; i++) {
        if (this.settled[i] > 0.5 && this.fadeTimer[i] <= 0 && this.landedAt[i] < oldestTime) {
          oldestTime = this.landedAt[i];
          oldestIdx = i;
        }
      }
      if (oldestIdx >= 0) {
        this.fadeTimer[oldestIdx] = FADE_DURATION;
      }
    }

    this.#packBuffers();
  }

  #settleLeaf(i, groundY) {
    const ix = i * 3;
    this.offsets[ix + 1] = groundY + SETTLE_LIFT;
    this.settled[i] = 1;
    this.settledYaw[i] = Math.random() * Math.PI * 2;
    this.landedAt[i] = this._elapsed;
    this.scales[i] = SETTLE_SCALE;
    this._settledCount++;
  }

  #respawnLeaf(i, px, pz) {
    const ix = i * 3;
    this.offsets[ix]     = px + (Math.random() - 0.5) * VOL_X;
    this.offsets[ix + 1] = Y_MIN + Math.random() * (Y_MAX - Y_MIN);
    this.offsets[ix + 2] = pz + (Math.random() - 0.5) * VOL_Z;
    if (this.settled[i] > 0.5) this._settledCount--;
    this.settled[i] = 0;
    this.fadeTimer[i] = 0;
    this.scales[i] = 1.0;
    // Fresh tumble so recycled leaves don't all share a stale angle.
    this.angles[i] = Math.random() * Math.PI * 2;
  }
}

const leafOn = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 11-9 1 0 2 0 3 .3-.3 8-5 13.5-12 15.4Z"/>
  <path d="M2 22c2-4 4-7 9-10"/>
</svg>`;
const leafOff = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.45">
  <path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 11-9 1 0 2 0 3 .3-.3 8-5 13.5-12 15.4Z"/>
  <line x1="4" y1="4" x2="22" y2="22"/>
</svg>`;
