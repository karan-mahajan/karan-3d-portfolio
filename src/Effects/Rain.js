import * as THREE from 'three';

/**
 * Light rain. Two layers:
 *   - Drops: thin vertical line segments raining down inside a box that
 *     follows the camera (recycled when they hit the ground).
 *   - Splashes: expanding rings on the ground for a fraction of drops that
 *     are within view, giving the impression of impact.
 *
 * Toggle on/off via setEnabled(). The toggle button is provided externally.
 */

const RAIN_COUNT = 1200;
const AREA = 70;            // half-extent of the rain volume
const FALL_SPEED = 18;      // units per second
const SPAWN_HEIGHT = 28;
const STORAGE_KEY = 'karan-portfolio:rain-off';

const dropVert = /* glsl */ `
  attribute vec3 aOffset;   // current world position
  attribute float aSpeed;
  uniform float uTime;
  varying float vAlpha;

  void main() {
    vec3 pos = position + aOffset;
    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mv;
    // Fade by distance so drops in the far horizon don't clutter.
    vAlpha = clamp(1.0 - (-mv.z) / 65.0, 0.0, 1.0);
  }
`;
const dropFrag = /* glsl */ `
  varying float vAlpha;
  void main() {
    gl_FragColor = vec4(0.78, 0.85, 0.95, 0.35 * vAlpha);
  }
`;

export class Rain {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    this.enabled = localStorage.getItem(STORAGE_KEY) !== '1';
    this.group = new THREE.Group();
    this.group.name = 'rain';
    scene.add(this.group);

    this.#buildDrops();
    this.splashPool = [];
    this.activeSplashes = [];
    this.#buildSplashPool();

    this.group.visible = this.enabled;
    this.#installButton();
  }

  // ── Drops ────────────────────────────────────────────────────────────────
  #buildDrops() {
    // Each "drop" is a thin vertical line segment.
    const baseGeom = new THREE.BufferGeometry();
    const verts = new Float32Array([0, 0, 0, 0, -0.35, 0]);
    baseGeom.setAttribute('position', new THREE.BufferAttribute(verts, 3));

    const instGeom = new THREE.InstancedBufferGeometry();
    instGeom.setAttribute('position', baseGeom.attributes.position);
    instGeom.setIndex(null);
    instGeom.instanceCount = RAIN_COUNT;

    this.offsets = new Float32Array(RAIN_COUNT * 3);
    this.speeds = new Float32Array(RAIN_COUNT);
    for (let i = 0; i < RAIN_COUNT; i++) {
      this.offsets[i * 3]     = (Math.random() - 0.5) * AREA * 2;
      this.offsets[i * 3 + 1] = Math.random() * SPAWN_HEIGHT;
      this.offsets[i * 3 + 2] = (Math.random() - 0.5) * AREA * 2;
      this.speeds[i] = FALL_SPEED * (0.85 + Math.random() * 0.35);
    }
    instGeom.setAttribute('aOffset', new THREE.InstancedBufferAttribute(this.offsets, 3));
    instGeom.setAttribute('aSpeed',  new THREE.InstancedBufferAttribute(this.speeds, 1));

    const mat = new THREE.ShaderMaterial({
      vertexShader: dropVert,
      fragmentShader: dropFrag,
      transparent: true,
      depthWrite: false,
      uniforms: { uTime: { value: 0 } },
    });

    this.drops = new THREE.LineSegments(instGeom, mat);
    this.drops.frustumCulled = false;
    this.group.add(this.drops);
  }

  // ── Splash ring pool ─────────────────────────────────────────────────────
  #buildSplashPool() {
    const geom = new THREE.RingGeometry(0.04, 0.08, 16);
    for (let i = 0; i < 60; i++) {
      const mesh = new THREE.Mesh(
        geom,
        new THREE.MeshBasicMaterial({
          color: 0xc8e0f0,
          transparent: true,
          opacity: 0,
          depthWrite: false,
          side: THREE.DoubleSide,
        }),
      );
      mesh.rotation.x = -Math.PI / 2;
      mesh.visible = false;
      this.scene.add(mesh);
      this.splashPool.push(mesh);
    }
  }

  #spawnSplash(x, z) {
    const ring = this.splashPool.find((r) => !r.visible);
    if (!ring) return;
    ring.visible = true;
    ring.position.set(x, 0.05, z);
    ring.scale.setScalar(1);
    ring.material.opacity = 0.5;
    ring.userData.life = 0;
    this.activeSplashes.push(ring);
  }

  // ── Toggle ───────────────────────────────────────────────────────────────
  setEnabled(value) {
    this.enabled = value;
    this.group.visible = value;
    localStorage.setItem(STORAGE_KEY, value ? '0' : '1');
    this.#updateButton();
  }
  toggle() { this.setEnabled(!this.enabled); }

  #installButton() {
    const btn = document.createElement('button');
    btn.className = 'rain-toggle';
    btn.setAttribute('aria-label', 'Toggle rain');
    btn.innerHTML = this.enabled ? rainOn : rainOff;
    btn.addEventListener('click', () => this.toggle());
    document.body.appendChild(btn);
    this._btn = btn;
  }
  #updateButton() {
    if (this._btn) this._btn.innerHTML = this.enabled ? rainOn : rainOff;
  }

  // ── Per-frame ────────────────────────────────────────────────────────────
  update(delta) {
    if (!this.enabled) return;

    // Center the rain volume on the camera so it always covers the player.
    const cx = this.camera.position.x;
    const cz = this.camera.position.z;
    this.drops.position.set(cx, 0, cz);

    // Advance each drop. When a drop falls below y=0, recycle it to the top.
    let splashBudget = 4; // cap splashes per frame
    for (let i = 0; i < RAIN_COUNT; i++) {
      this.offsets[i * 3 + 1] -= this.speeds[i] * delta;
      if (this.offsets[i * 3 + 1] < 0) {
        // World x/z of the drop = base offset + camera position.
        const wx = this.offsets[i * 3] + cx;
        const wz = this.offsets[i * 3 + 2] + cz;
        if (splashBudget > 0 && Math.random() < 0.04) {
          this.#spawnSplash(wx, wz);
          splashBudget--;
        }
        this.offsets[i * 3]     = (Math.random() - 0.5) * AREA * 2;
        this.offsets[i * 3 + 1] = SPAWN_HEIGHT;
        this.offsets[i * 3 + 2] = (Math.random() - 0.5) * AREA * 2;
      }
    }
    this.drops.geometry.attributes.aOffset.needsUpdate = true;

    // Animate splash rings.
    for (let i = this.activeSplashes.length - 1; i >= 0; i--) {
      const ring = this.activeSplashes[i];
      ring.userData.life += delta;
      const t = ring.userData.life / 0.45;
      if (t >= 1) {
        ring.visible = false;
        this.activeSplashes.splice(i, 1);
        continue;
      }
      ring.scale.setScalar(1 + t * 4);
      ring.material.opacity = (1 - t) * 0.5;
    }
  }
}

const rainOn = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M16 13v8M8 13v8M12 15v8M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/>
</svg>`;
const rainOff = `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.45">
  <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/>
  <line x1="6" y1="6" x2="22" y2="22"/>
</svg>`;
