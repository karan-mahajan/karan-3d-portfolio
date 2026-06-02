import * as THREE from 'three/webgpu';

/**
 * GroundBreak — stylized procedural ground-impact FX, fired once when the
 * intro-cinematic character lands (and reusable for any future heavy impact).
 *
 * Four layers, all generated in code (no texture assets):
 *   1. Crack decal — branching radial cracks drawn to a canvas → CanvasTexture
 *      on a flat ground quad. Fades in instantly, lingers, fades out over ~3s.
 *   2. Shockwave  — a thin white ring that scales outward and fades in ~0.5s.
 *   3. Dust       — a soft tan radial puff that expands and fades over ~1.3s.
 *   4. Debris     — a burst of small earth chunks (instanced) thrown out + up,
 *      gravity-pulled, scaled to nothing at end of life (~1s).
 *
 * Each burst() registers an effect bundle; update(delta) advances every live
 * bundle and disposes geometry/materials/textures when it completes. Nothing
 * persists once the last bundle finishes.
 */

const GRAVITY = -22;

export class GroundBreak {
  /** @param {THREE.Scene} scene */
  constructor(scene) {
    this.scene = scene;
    this._bundles = [];
  }

  /**
   * Fire an impact at a world position.
   * @param {THREE.Vector3|{x:number,y:number,z:number}} position  ground point
   * @param {{ radius?: number, debrisCount?: number }} [opts]
   */
  burst(position, opts = {}) {
    const radius = opts.radius ?? 3.0;
    const debrisCount = opts.debrisCount ?? 16;
    const bundle = { parts: [], age: 0, ttl: 3.2 };

    bundle.parts.push(this.#makeCrackDecal(position, radius));
    bundle.parts.push(this.#makeShockwave(position, radius));
    bundle.parts.push(this.#makeDust(position, radius));
    bundle.parts.push(this.#makeDebris(position, radius, debrisCount));

    this._bundles.push(bundle);
  }

  // ── Crack decal ───────────────────────────────────────────────────────────
  #makeCrackDecal(position, radius) {
    const size = 256;
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, size, size);
    const cx = size / 2;
    const cy = size / 2;

    // Branching radial cracks. Pseudo-random but seeded by the loop index so
    // the figure is varied each burst (Math.random is fine in app runtime).
    const spokes = 9 + Math.floor(Math.random() * 4);
    ctx.lineCap = 'round';
    for (let i = 0; i < spokes; i++) {
      const baseAngle = (i / spokes) * Math.PI * 2 + (Math.random() - 0.5) * 0.4;
      this.#drawCrack(ctx, cx, cy, baseAngle, size * 0.46, 4.5, 0);
    }
    // A faint scorched core so the centre doesn't read as empty.
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, size * 0.18);
    grad.addColorStop(0, 'rgba(30,22,16,0.55)');
    grad.addColorStop(1, 'rgba(30,22,16,0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, size * 0.18, 0, Math.PI * 2);
    ctx.fill();

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;

    const geom = new THREE.PlaneGeometry(radius * 2.1, radius * 2.1);
    geom.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      depthTest: true,
      toneMapped: false,
    });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.set(position.x, position.y + 0.03, position.z);
    mesh.rotation.y = Math.random() * Math.PI * 2;
    mesh.renderOrder = 5;
    mesh.frustumCulled = false;
    this.scene.add(mesh);

    return {
      ttl: 3.2,
      update: (age) => {
        // Snap in over 0.08s, hold, fade out over the last 1.4s.
        const fadeIn = Math.min(1, age / 0.08);
        const fadeOut = age > 1.8 ? Math.max(0, 1 - (age - 1.8) / 1.4) : 1;
        mat.opacity = 0.92 * fadeIn * fadeOut;
      },
      dispose: () => {
        this.scene.remove(mesh);
        geom.dispose();
        mat.dispose();
        tex.dispose();
      },
    };
  }

  #drawCrack(ctx, x, y, angle, length, width, depth) {
    // Walk outward in segments, jittering the angle; spawn the odd branch.
    let px = x;
    let py = y;
    const steps = 6;
    const seg = length / steps;
    ctx.strokeStyle = 'rgba(22,16,11,0.9)';
    for (let s = 0; s < steps; s++) {
      const a = angle + (Math.random() - 0.5) * 0.6;
      const nx = px + Math.cos(a) * seg;
      const ny = py + Math.sin(a) * seg;
      ctx.lineWidth = Math.max(0.6, width * (1 - s / steps));
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(nx, ny);
      ctx.stroke();
      // Branch occasionally, but cap recursion depth.
      if (depth < 2 && s > 0 && Math.random() < 0.3) {
        this.#drawCrack(
          ctx, px, py,
          a + (Math.random() < 0.5 ? 1 : -1) * (0.5 + Math.random() * 0.4),
          seg * (steps - s) * 0.8, width * 0.5, depth + 1,
        );
      }
      px = nx;
      py = ny;
    }
  }

  // ── Shockwave ring ─────────────────────────────────────────────────────────
  #makeShockwave(position, radius) {
    const geom = new THREE.RingGeometry(0.85, 1.0, 48);
    geom.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({
      color: 0xfff2dc,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
      blending: THREE.AdditiveBlending,
    });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.set(position.x, position.y + 0.06, position.z);
    mesh.renderOrder = 6;
    mesh.frustumCulled = false;
    this.scene.add(mesh);

    const life = 0.5;
    return {
      ttl: life,
      update: (age) => {
        const t = Math.min(1, age / life);
        const s = 0.3 + t * radius * 2.4;
        mesh.scale.setScalar(s);
        mat.opacity = 0.9 * (1 - t);
      },
      dispose: () => { this.scene.remove(mesh); geom.dispose(); mat.dispose(); },
    };
  }

  // ── Dust puff ──────────────────────────────────────────────────────────────
  #makeDust(position, radius) {
    const size = 128;
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    grad.addColorStop(0, 'rgba(196,176,150,0.55)');
    grad.addColorStop(0.5, 'rgba(176,156,128,0.28)');
    grad.addColorStop(1, 'rgba(176,156,128,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, size, size);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;

    const geom = new THREE.PlaneGeometry(1, 1);
    geom.rotateX(-Math.PI / 2);
    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      toneMapped: false,
    });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.set(position.x, position.y + 0.12, position.z);
    mesh.renderOrder = 5;
    mesh.frustumCulled = false;
    this.scene.add(mesh);

    const life = 1.3;
    return {
      ttl: life,
      update: (age) => {
        const t = Math.min(1, age / life);
        const s = radius * (1.0 + t * 2.2);
        mesh.scale.set(s, 1, s);
        mesh.position.y = position.y + 0.12 + t * 0.6;
        mat.opacity = 0.85 * Math.sin(Math.min(1, t * 1.15) * Math.PI);
      },
      dispose: () => { this.scene.remove(mesh); geom.dispose(); mat.dispose(); tex.dispose(); },
    };
  }

  // ── Debris chunks ──────────────────────────────────────────────────────────
  #makeDebris(position, radius, count) {
    const geom = new THREE.TetrahedronGeometry(0.11);
    const mat = new THREE.MeshStandardMaterial({
      color: 0x5a4632,
      roughness: 0.95,
      metalness: 0,
      flatShading: true,
    });
    const mesh = new THREE.InstancedMesh(geom, mat, count);
    mesh.frustumCulled = false;
    mesh.castShadow = false;
    this.scene.add(mesh);

    // Per-chunk state.
    const chunks = [];
    for (let i = 0; i < count; i++) {
      const ang = (i / count) * Math.PI * 2 + Math.random() * 0.6;
      const speed = 2.5 + Math.random() * 3.5;
      chunks.push({
        pos: new THREE.Vector3(position.x, position.y + 0.1, position.z),
        vel: new THREE.Vector3(
          Math.cos(ang) * speed * (0.4 + Math.random() * 0.6),
          3.5 + Math.random() * 3.5,
          Math.sin(ang) * speed * (0.4 + Math.random() * 0.6),
        ),
        spin: new THREE.Vector3(
          (Math.random() - 0.5) * 8,
          (Math.random() - 0.5) * 8,
          (Math.random() - 0.5) * 8,
        ),
        rot: new THREE.Euler(Math.random() * 6, Math.random() * 6, Math.random() * 6),
        scale: 0.6 + Math.random() * 0.8,
      });
    }

    const life = 1.0;
    const groundY = position.y;
    const m = new THREE.Matrix4();
    const q = new THREE.Quaternion();
    const s = new THREE.Vector3();
    return {
      ttl: life,
      update: (age, delta) => {
        const t = Math.min(1, age / life);
        for (let i = 0; i < count; i++) {
          const c = chunks[i];
          c.vel.y += GRAVITY * delta;
          c.pos.addScaledVector(c.vel, delta);
          if (c.pos.y < groundY + 0.04) {
            c.pos.y = groundY + 0.04;
            c.vel.y *= -0.3;
            c.vel.x *= 0.6;
            c.vel.z *= 0.6;
          }
          c.rot.x += c.spin.x * delta;
          c.rot.y += c.spin.y * delta;
          c.rot.z += c.spin.z * delta;
          q.setFromEuler(c.rot);
          s.setScalar(c.scale * (1 - t)); // shrink to nothing → clean exit
          m.compose(c.pos, q, s);
          mesh.setMatrixAt(i, m);
        }
        mesh.instanceMatrix.needsUpdate = true;
      },
      dispose: () => { this.scene.remove(mesh); geom.dispose(); mat.dispose(); },
    };
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────
  update(delta) {
    if (!this._bundles.length) return;
    for (let b = this._bundles.length - 1; b >= 0; b--) {
      const bundle = this._bundles[b];
      bundle.age += delta;
      let alive = false;
      for (const part of bundle.parts) {
        if (part.done) continue;
        if (bundle.age >= part.ttl) {
          part.dispose();
          part.done = true;
          continue;
        }
        part.update(bundle.age, delta);
        alive = true;
      }
      if (!alive) this._bundles.splice(b, 1);
    }
  }

  dispose() {
    for (const bundle of this._bundles) {
      for (const part of bundle.parts) if (!part.done) part.dispose();
    }
    this._bundles.length = 0;
  }
}
