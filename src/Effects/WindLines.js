import * as THREE from 'three/webgpu';

/**
 * Ghibli-style drifting wind streaks. ~350 instanced ribbon quads, each
 * billboarded so its length lies along the world wind direction and its
 * width tilts to face the camera. Head of the ribbon is brightest, tail
 * fades to zero — gives the characteristic "comet-trail" streak look.
 *
 * Ribbons live inside a 60×60×4 box centered on the player. When they
 * leave the box they mod-wrap to the opposite side so the volume always
 * follows the player without re-randomizing positions.
 *
 * Visibility ramps with Wind.uWindStrength via smoothstep(0.05, 0.3) so
 * the streaks are clearly present at the wind module's default strength
 * (~0.35) and only disappear in near-dead calm.
 *
 * Toggle via setEnabled(). Setting persists in localStorage.
 */

const DEFAULT_COUNT = 350;
const VOL_X = 60;            // full extent in x
const VOL_Z = 60;            // full extent in z
const HALF_X = VOL_X * 0.5;
const HALF_Z = VOL_Z * 0.5;
const Y_MIN = 0.3;
const Y_MAX = 4.0;
const RIBBON_LENGTH = 1.2;
const RIBBON_WIDTH = 0.04;
const SPEED_MIN = 0.5;
const SPEED_MAX = 1.5;
const STORAGE_KEY = 'karan-portfolio:wind-lines';

const vert = /* glsl */ `
  uniform vec2 uWindDir;       // shared with Wind module
  uniform float uLength;
  uniform float uWidth;

  attribute vec3 aOffset;      // world-space ribbon center
  varying float vAlpha;

  void main() {
    // position.x is local length_t in [-0.5, 0.5]; position.y is width_t in [-0.5, 0.5].
    float lengthT = position.x;
    float widthT  = position.y;
    float headFrac = lengthT + 0.5;  // 0 at tail, 1 at head

    // Wind axis in world (xz). Already normalized by Wind module.
    vec3 along = vec3(uWindDir.x, 0.0, uWindDir.y);
    vec3 worldCenter = aOffset;

    // Billboard the width axis toward the camera while keeping the length
    // axis locked to the wind direction — gives a thin streak that always
    // catches the light from the third-person view.
    vec3 toCam = cameraPosition - worldCenter;
    vec3 across = normalize(cross(along, toCam));

    vec3 worldPos = worldCenter
                  + along  * (lengthT * uLength)
                  + across * (widthT  * uWidth);

    gl_Position = projectionMatrix * viewMatrix * vec4(worldPos, 1.0);

    // Head bright (0.9) → tail invisible (0.0). Gives the comet-trail look.
    vAlpha = headFrac * 0.9;
  }
`;

const frag = /* glsl */ `
  uniform vec3 uColor;       // HDR (>1.0) so bloom catches the brightest pixels
  uniform float uVisibility;
  varying float vAlpha;

  void main() {
    gl_FragColor = vec4(uColor, vAlpha * uVisibility);
  }
`;

export class WindLines {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Wind.js').Wind} wind  Read-only — shares uniforms.
   */
  constructor(scene, wind, { count = DEFAULT_COUNT } = {}) {
    this.scene = scene;
    this.wind = wind;
    this.count = Math.max(0, Math.floor(count));
    this.enabled = localStorage.getItem(STORAGE_KEY) !== '0';
    this.visibility = 0; // ramps with wind strength

    this.#buildRibbons();
    this.mesh.visible = this.enabled;
    this.#installButton();
  }

  // ── Geometry ─────────────────────────────────────────────────────────────
  #buildRibbons() {
    // Base quad — position.x = length_t, position.y = width_t.
    const baseGeom = new THREE.BufferGeometry();
    const verts = new Float32Array([
      -0.5, -0.5, 0, // tail bottom
       0.5, -0.5, 0, // head bottom
       0.5,  0.5, 0, // head top
      -0.5,  0.5, 0, // tail top
    ]);
    baseGeom.setAttribute('position', new THREE.BufferAttribute(verts, 3));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    const instGeom = new THREE.InstancedBufferGeometry();
    instGeom.setAttribute('position', baseGeom.attributes.position);
    instGeom.setIndex(baseGeom.index);
    instGeom.instanceCount = this.count;

    // Per-ribbon world-space center.
    this.offsets = new Float32Array(this.count * 3);
    this.speeds = new Float32Array(this.count);

    for (let i = 0; i < this.count; i++) {
      this.offsets[i * 3]     = (Math.random() - 0.5) * VOL_X;
      this.offsets[i * 3 + 1] = Y_MIN + Math.random() * (Y_MAX - Y_MIN);
      this.offsets[i * 3 + 2] = (Math.random() - 0.5) * VOL_Z;
      this.speeds[i] = SPEED_MIN + Math.random() * (SPEED_MAX - SPEED_MIN);
    }

    this.offsetAttr = new THREE.InstancedBufferAttribute(this.offsets, 3);
    this.offsetAttr.setUsage(THREE.DynamicDrawUsage);
    instGeom.setAttribute('aOffset', this.offsetAttr);

    const mat = new THREE.ShaderMaterial({
      vertexShader: vert,
      fragmentShader: frag,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        // Share the live wind direction — wind module owns this Vector2.
        uWindDir: this.wind.uniforms.uWindDir,
        uLength: { value: RIBBON_LENGTH },
        uWidth: { value: RIBBON_WIDTH },
        // HDR white — values >1.0 push the streaks above the bloom threshold
        // so they glow against the dusk sky instead of washing out into it.
        uColor: { value: new THREE.Vector3(1.5, 1.5, 1.5) },
        uVisibility: { value: 0 },
      },
    });
    this.material = mat;

    this.mesh = new THREE.Mesh(instGeom, mat);
    this.mesh.name = 'wind-lines';
    this.mesh.frustumCulled = false;
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
    btn.className = 'wind-toggle';
    btn.setAttribute('aria-label', 'Toggle wind lines');
    btn.innerHTML = this.enabled ? windOn : windOff;
    btn.addEventListener('click', () => this.toggle());
    document.body.appendChild(btn);
    this._btn = btn;
  }
  #updateButton() {
    if (this._btn) this._btn.innerHTML = this.enabled ? windOn : windOff;
  }

  // ── Per-frame ────────────────────────────────────────────────────────────
  /**
   * Advance each ribbon along the wind direction, wrap back into the
   * box around the player, and update the visibility uniform from wind
   * strength.
   * @param {number} delta seconds since last frame
   * @param {THREE.Vector3} playerPos
   */
  update(delta, playerPos) {
    // Visibility ramps with wind strength regardless of enabled state — so
    // when re-enabled mid-calm the streaks fade in naturally.
    const strength = this.wind.uniforms.uWindStrength.value;
    // Wind module's default is ~0.35; ramping fully in by 0.3 means
    // streaks are clearly visible in gentle wind without needing a gust.
    const target = THREE.MathUtils.smoothstep(strength, 0.05, 0.3);
    // Cheap one-pole smoothing so the fade doesn't pop when strength jitters.
    this.visibility += (target - this.visibility) * Math.min(1, delta * 4);
    this.material.uniforms.uVisibility.value = this.visibility;

    if (!this.enabled || this.visibility < 0.005) return;

    const dir = this.wind.uniforms.uWindDir.value;
    const dx = dir.x;
    const dz = dir.y;
    const px = playerPos.x;
    const pz = playerPos.z;

    for (let i = 0; i < this.count; i++) {
      const v = this.speeds[i];
      const ix = i * 3;
      this.offsets[ix]     += dx * v * delta;
      this.offsets[ix + 2] += dz * v * delta;

      // Wrap relative to the player so the volume travels with them.
      const rx = this.offsets[ix] - px;
      if (rx >  HALF_X) this.offsets[ix] -= VOL_X;
      else if (rx < -HALF_X) this.offsets[ix] += VOL_X;

      const rz = this.offsets[ix + 2] - pz;
      if (rz >  HALF_Z) this.offsets[ix + 2] -= VOL_Z;
      else if (rz < -HALF_Z) this.offsets[ix + 2] += VOL_Z;
    }
    this.offsetAttr.needsUpdate = true;
  }
}

const windOn = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 8h11a3 3 0 1 0-3-3"/>
  <path d="M3 14h15a3 3 0 1 1-3 3"/>
  <path d="M3 11h9"/>
</svg>`;
const windOff = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.45">
  <path d="M3 8h11a3 3 0 1 0-3-3"/>
  <path d="M3 14h15a3 3 0 1 1-3 3"/>
  <line x1="4" y1="4" x2="22" y2="22"/>
</svg>`;
