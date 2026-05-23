import * as THREE from 'three';
import { DUSK } from '../World/Palette.js';

/**
 * Autumn leaves drifting through the air. ~COUNT instanced quads, each
 * carrying its own:
 *   - world position (updated CPU-side each frame: fall + wind drift)
 *   - tumble axis (random unit vec3, baked once)
 *   - tumble angle (accumulated CPU-side: angle += spinSpeed * delta)
 *   - autumn tint (one of four palette colors, baked once)
 *
 * The volume is a VOL_X × VOL_Z box that follows the player — leaves that
 * exit the XZ box mod-wrap to the opposite side (same trick as WindLines);
 * leaves that fall below y=0 respawn at the top with a fresh XZ inside the
 * volume. Drift is `wind.direction * driftCoeff * wind.strength`, so calm
 * wind = mostly-vertical fall, gusty wind = slanted drift — matches grass
 * sway and wind streaks since they all read the same uniforms.
 *
 * Material is a custom ShaderMaterial (not transparent — alphaTest only)
 * with `lights: true` so the same shadowmap binding the grass uses pipes
 * through here. Shadowed leaves get a magenta tint (DUSK.shadowTint),
 * matching the rest of the scene's patchShadowTint convention.
 *
 * Toggle via setEnabled(); persists under 'karan-portfolio:leaves'.
 */

const COUNT = 120;
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

const vert = /* glsl */ `
  #include <common>
  #include <fog_pars_vertex>
  #include <shadowmap_pars_vertex>

  uniform float uSize;

  attribute vec3 aOffset;
  attribute vec3 aSpinAxis;
  attribute float aAngle;
  attribute vec3 aTint;

  varying vec2 vUv;
  varying vec3 vTint;

  // Rodrigues rotation — rotate a vector around a unit axis by an angle.
  mat3 axisAngleMat(vec3 axis, float angle) {
    float c = cos(angle);
    float s = sin(angle);
    float t = 1.0 - c;
    float x = axis.x;
    float y = axis.y;
    float z = axis.z;
    return mat3(
      t*x*x + c,    t*x*y - s*z,  t*x*z + s*y,
      t*x*y + s*z,  t*y*y + c,    t*y*z - s*x,
      t*x*z - s*y,  t*y*z + s*x,  t*z*z + c
    );
  }

  void main() {
    // PlaneGeometry vertices are in [-0.5, 0.5] on x/y, z=0.
    vec3 local = position * uSize;
    vec3 rotated = axisAngleMat(normalize(aSpinAxis), aAngle) * local;
    vec3 wpos = aOffset + rotated;

    vUv = uv;
    vTint = aTint;

    vec4 worldPosition = vec4(wpos, 1.0);
    vec4 mvPosition = viewMatrix * worldPosition;
    gl_Position = projectionMatrix * mvPosition;

    #include <shadowmap_vertex>
    #include <fog_vertex>
  }
`;

const frag = /* glsl */ `
  #include <common>
  #include <fog_pars_fragment>
  #include <shadowmap_pars_fragment>

  uniform sampler2D uLeafMask;
  uniform vec3 uShadowTint;
  uniform float uShadowTintStrength;

  varying vec2 vUv;
  varying vec3 vTint;

  void main() {
    // Single-channel mask. Hard alphaTest (no blending) — leaves stay
    // opaque so they sort cleanly against trees / grass / each other.
    float alpha = texture2D(uLeafMask, vUv).r;
    if (alpha < 0.1) discard;

    vec3 color = vTint;

    // Same shadow-tint pattern as Grass.js / patchShadowTint: shadowed
    // pixels blend toward color*shadowTint instead of just darkening.
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
      vec3 _stintTarget = color * uShadowTint;
      color = mix( color, _stintTarget, _stintAmt * uShadowTintStrength );
    #endif

    gl_FragColor = vec4(color, 1.0);
    #include <fog_fragment>
  }
`;

export class Leaves {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Wind.js').Wind} wind  Read-only; supplies direction + strength.
   */
  constructor(scene, wind) {
    this.scene = scene;
    this.wind = wind;
    this.enabled = localStorage.getItem(STORAGE_KEY) !== '0';

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
    instGeom.instanceCount = COUNT;
    // Bounding sphere set huge so frustum-culling never drops us — leaves
    // live in a player-following volume, so per-frame culling math would be
    // wrong anyway.
    instGeom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    this.offsets    = new Float32Array(COUNT * 3);
    this.spinAxes   = new Float32Array(COUNT * 3);
    this.angles     = new Float32Array(COUNT);
    this.tints      = new Float32Array(COUNT * 3);
    this.falls      = new Float32Array(COUNT);
    this.drifts     = new Float32Array(COUNT);
    this.spinSpeeds = new Float32Array(COUNT);

    for (let i = 0; i < COUNT; i++) {
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

      const tint = PALETTE[(Math.random() * PALETTE.length) | 0];
      this.tints[ix]     = tint.r;
      this.tints[ix + 1] = tint.g;
      this.tints[ix + 2] = tint.b;
    }

    this.offsetAttr = new THREE.InstancedBufferAttribute(this.offsets, 3);
    this.offsetAttr.setUsage(THREE.DynamicDrawUsage);
    this.angleAttr = new THREE.InstancedBufferAttribute(this.angles, 1);
    this.angleAttr.setUsage(THREE.DynamicDrawUsage);

    instGeom.setAttribute('aOffset',   this.offsetAttr);
    instGeom.setAttribute('aSpinAxis', new THREE.InstancedBufferAttribute(this.spinAxes, 3));
    instGeom.setAttribute('aAngle',    this.angleAttr);
    instGeom.setAttribute('aTint',     new THREE.InstancedBufferAttribute(this.tints, 3));

    // Texture: single-channel mask, linear-sampled, no color-space conversion
    // (we sample .r as a raw alpha value, gamma would skew the threshold).
    const tex = new THREE.TextureLoader().load(LEAF_MASK_URL);
    tex.colorSpace = THREE.NoColorSpace;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 4;

    // Deep-merge built-in lights + fog uniforms (per-material clones), then
    // overwrite the wind/own uniforms by reference so the Wind module's
    // updates propagate live.
    const uniforms = THREE.UniformsUtils.merge([
      THREE.UniformsLib.lights,
      THREE.UniformsLib.fog,
      {
        uLeafMask:          { value: tex },
        uSize:              { value: LEAF_SIZE },
        uShadowTint:        { value: new THREE.Color(DUSK.shadowTint) },
        uShadowTintStrength:{ value: 0.6 },
      },
    ]);

    this.material = new THREE.ShaderMaterial({
      vertexShader: vert,
      fragmentShader: frag,
      uniforms,
      side: THREE.DoubleSide,
      transparent: false,
      depthWrite: true,
      fog: true,
      lights: true,
    });

    this.mesh = new THREE.Mesh(instGeom, this.material);
    this.mesh.name = 'leaves';
    this.mesh.frustumCulled = false;
    this.mesh.receiveShadow = true;
    this.scene.add(this.mesh);
  }

  // ── Toggle ───────────────────────────────────────────────────────────────
  setEnabled(value) {
    this.enabled = value;
    this.mesh.visible = value;
    localStorage.setItem(STORAGE_KEY, value ? '1' : '0');
    this.#updateButton();
  }
  toggle() { this.setEnabled(!this.enabled); }

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
   * Fall, drift, spin, wrap. Volume tracks the player so the swirl is
   * always around them — leaves never get "left behind" as you walk.
   *
   * @param {number} delta seconds since last frame
   * @param {THREE.Vector3} playerPos
   */
  update(delta, playerPos) {
    if (!this.enabled) return;

    const dir = this.wind.uniforms.uWindDir.value;
    const strength = this.wind.uniforms.uWindStrength.value;
    const dx = dir.x;
    const dz = dir.y;
    const px = playerPos.x;
    const pz = playerPos.z;

    for (let i = 0; i < COUNT; i++) {
      const ix = i * 3;

      // Fall + horizontal wind drift.
      this.offsets[ix]     += dx * this.drifts[i] * strength * delta;
      this.offsets[ix + 1] -= this.falls[i] * delta;
      this.offsets[ix + 2] += dz * this.drifts[i] * strength * delta;

      // Tumble.
      this.angles[i] += this.spinSpeeds[i] * delta;

      if (this.offsets[ix + 1] < 0) {
        // Hit ground — respawn at the top, anywhere in the player-centered XZ box.
        this.offsets[ix]     = px + (Math.random() - 0.5) * VOL_X;
        this.offsets[ix + 1] = Y_MIN + Math.random() * (Y_MAX - Y_MIN);
        this.offsets[ix + 2] = pz + (Math.random() - 0.5) * VOL_Z;
      } else {
        // XZ wrap — same mod-wrap trick as WindLines so the volume travels
        // with the player without re-randomizing in-flight leaves.
        const rx = this.offsets[ix] - px;
        if (rx >  HALF_X) this.offsets[ix] -= VOL_X;
        else if (rx < -HALF_X) this.offsets[ix] += VOL_X;

        const rz = this.offsets[ix + 2] - pz;
        if (rz >  HALF_Z) this.offsets[ix + 2] -= VOL_Z;
        else if (rz < -HALF_Z) this.offsets[ix + 2] += VOL_Z;
      }
    }

    this.offsetAttr.needsUpdate = true;
    this.angleAttr.needsUpdate = true;
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
