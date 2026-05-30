import * as THREE from 'three/webgpu';

/**
 * Light rain. Two layers:
 *   - Drops: thin vertical line segments raining down inside a box that
 *     follows the camera (recycled when they hit the ground).
 *   - Splashes: expanding rings on the ground for a fraction of drops that
 *     are within view, giving the impression of impact.
 *
 * Toggle on/off via setEnabled(). The toggle button is provided externally.
 */

const DEFAULT_RAIN_COUNT = 1200;
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
  constructor(scene, camera, { count = DEFAULT_RAIN_COUNT, splashBudget = 8 } = {}) {
    this.scene = scene;
    this.camera = camera;
    this.count = Math.max(80, Math.floor(count));
    this.splashBudget = Math.max(0, Math.floor(splashBudget));
    this.enabled = localStorage.getItem(STORAGE_KEY) !== '1';
    this.group = new THREE.Group();
    this.group.name = 'rain';
    scene.add(this.group);

    // Pond surface — set externally via setPond() so rain over water
    // spawns a wider, lighter ripple instead of a hard ground splash.
    this.pond = null;

    this.#buildDrops();
    this.splashPool = [];
    this.activeSplashes = [];
    this.upwardPool = [];
    this.activeUpward = [];
    this.#buildSplashPool();
    this.#buildUpwardPool();

    this.group.visible = this.enabled;
    this.#installButton();
  }

  /** Register the water pond so rain landing on its surface spawns a
   *  ripple instead of a ground splash. */
  setPond(position, radius) {
    this.pond = { position: position.clone(), radius };
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
    instGeom.instanceCount = this.count;

    this.offsets = new Float32Array(this.count * 3);
    this.speeds = new Float32Array(this.count);
    for (let i = 0; i < this.count; i++) {
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
  // Each ring has two parameter sets baked in via userData:
  //   - 'ground' — small, fast (lifetime 0.3s), color #c8e0f0
  //   - 'water' — wider, slower (lifetime 0.8s), color #96c8f0
  // The first index is queried each spawn so we always reuse from the
  // pool (never new/dispose at runtime).
  #buildSplashPool() {
    const geom = new THREE.RingGeometry(0.04, 0.08, 12);
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

  /** Tiny upward droplets for splashes close to the camera. Each entry
   *  is a Group containing 3 small spheres that get re-parented on spawn
   *  and animated via userData. Pre-built once at boot. */
  #buildUpwardPool() {
    const geom = new THREE.SphereGeometry(0.025, 4, 3);
    for (let i = 0; i < 30; i++) {
      const group = new THREE.Group();
      const mat = new THREE.MeshBasicMaterial({
        color: 0xc8e0f0,
        transparent: true,
        opacity: 0,
        depthWrite: false,
      });
      for (let j = 0; j < 3; j++) {
        const s = new THREE.Mesh(geom, mat);
        group.add(s);
      }
      group.visible = false;
      group.userData.mat = mat;
      group.userData.velocities = [
        new THREE.Vector3(),
        new THREE.Vector3(),
        new THREE.Vector3(),
      ];
      this.scene.add(group);
      this.upwardPool.push(group);
    }
  }

  #spawnSplash(x, z) {
    const dx = x - this.camera.position.x;
    const dz = z - this.camera.position.z;
    const dCam = Math.hypot(dx, dz);
    // Far splashes are invisible anyway through fog — skip entirely.
    if (dCam > 25) return;

    const onPond = this.pond
      && Math.hypot(x - this.pond.position.x, z - this.pond.position.z) < this.pond.radius;

    const ring = this.splashPool.find((r) => !r.visible);
    if (!ring) return;
    ring.visible = true;
    if (onPond) {
      ring.position.set(x, this.pond.position.y + 0.02, z);
      ring.material.color.setHex(0x96c8f0);
      ring.material.opacity = 0.6;
      ring.userData.kind = 'water';
      ring.userData.maxScale = dCam < 10 ? 13 : 7;
      ring.userData.life = 0;
      ring.userData.lifetime = 0.8;
    } else {
      ring.position.set(x, 0.05, z);
      ring.material.color.setHex(0xc8e0f0);
      ring.material.opacity = 0.5;
      ring.userData.kind = 'ground';
      // Closer splashes draw a bigger ring so they read at full size.
      ring.userData.maxScale = dCam < 10 ? 6 : 3;
      ring.userData.life = 0;
      ring.userData.lifetime = 0.3;
    }
    ring.scale.setScalar(1);
    this.activeSplashes.push(ring);

    // Spawn upward droplets only for the closest splashes (perf budget).
    if (!onPond && dCam < 10) this.#spawnUpwardParticles(x, z);
  }

  #spawnUpwardParticles(x, z) {
    const group = this.upwardPool.find((g) => !g.visible);
    if (!group) return;
    group.visible = true;
    group.position.set(x, 0.02, z);
    group.userData.life = 0;
    group.userData.mat.opacity = 0.85;
    for (let i = 0; i < 3; i++) {
      const child = group.children[i];
      child.position.set(0, 0, 0);
      const ang = Math.random() * Math.PI * 2;
      const speed = 0.6 + Math.random() * 0.6;
      group.userData.velocities[i].set(
        Math.cos(ang) * speed,
        2.4 + Math.random() * 1.4,
        Math.sin(ang) * speed,
      );
    }
    this.activeUpward.push(group);
  }

  // ── Toggle ───────────────────────────────────────────────────────────────
  setEnabled(value) {
    this.enabled = value;
    this.group.visible = value;
    localStorage.setItem(STORAGE_KEY, value ? '0' : '1');
    this.#updateButton();
  }
  toggle() {
    this.audio?.playToggle();
    this.setEnabled(!this.enabled);
  }

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
    let splashBudget = this.splashBudget; // quality tier scales the splash cost.
    for (let i = 0; i < this.count; i++) {
      this.offsets[i * 3 + 1] -= this.speeds[i] * delta;
      if (this.offsets[i * 3 + 1] < 0) {
        // World x/z of the drop = base offset + camera position.
        const wx = this.offsets[i * 3] + cx;
        const wz = this.offsets[i * 3 + 2] + cz;
        if (splashBudget > 0 && Math.random() < 0.06) {
          this.#spawnSplash(wx, wz);
          splashBudget--;
        }
        this.offsets[i * 3]     = (Math.random() - 0.5) * AREA * 2;
        this.offsets[i * 3 + 1] = SPAWN_HEIGHT;
        this.offsets[i * 3 + 2] = (Math.random() - 0.5) * AREA * 2;
      }
    }
    this.drops.geometry.attributes.aOffset.needsUpdate = true;

    // Animate splash rings. Each ring carries its own maxScale +
    // lifetime in userData (set when spawned), so ground vs pond rings
    // can grow at different rates / sizes from the same pool.
    for (let i = this.activeSplashes.length - 1; i >= 0; i--) {
      const ring = this.activeSplashes[i];
      ring.userData.life += delta;
      const t = ring.userData.life / ring.userData.lifetime;
      if (t >= 1) {
        ring.visible = false;
        this.activeSplashes.splice(i, 1);
        continue;
      }
      const startOpacity = ring.userData.kind === 'water' ? 0.6 : 0.5;
      ring.scale.setScalar(1 + t * ring.userData.maxScale);
      ring.material.opacity = (1 - t) * startOpacity;
    }

    // Animate upward droplets — gravity-affected, fade out fast.
    for (let i = this.activeUpward.length - 1; i >= 0; i--) {
      const group = this.activeUpward[i];
      group.userData.life += delta;
      if (group.userData.life >= 0.22) {
        group.visible = false;
        this.activeUpward.splice(i, 1);
        continue;
      }
      for (let j = 0; j < 3; j++) {
        const child = group.children[j];
        const v = group.userData.velocities[j];
        child.position.x += v.x * delta;
        child.position.y += v.y * delta;
        child.position.z += v.z * delta;
        v.y -= 9.8 * delta; // gravity
      }
      group.userData.mat.opacity = 0.85 * (1 - group.userData.life / 0.22);
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
