import * as THREE from 'three';

/**
 * Stylized pond. Improvements over the first pass:
 *   - Two-layer wave shader for richer surface motion.
 *   - Fake fresnel (view-angle dependent edge highlight).
 *   - Foam ring at the perimeter where the surface meets the grass.
 *   - Lily pads placed on top (real GLB models).
 *   - Player-proximity ripple ring + screen color tint when stood on.
 *
 * The pond is intentionally non-colliding so the player can wade through it.
 */

const vert = /* glsl */ `
  uniform float uTime;
  varying vec2 vUv;
  varying float vWave;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  void main() {
    vUv = uv;
    vec3 pos = position;

    // Two layered waves running at different frequencies.
    float w1 = sin(pos.x * 0.55 + uTime * 1.3) * 0.10;
    float w2 = sin((pos.x + pos.y) * 0.38 + uTime * 0.6) * 0.07;
    float w3 = cos(pos.y * 0.7  + uTime * 1.7) * 0.05;
    float wave = w1 + w2 + w3;
    pos.z += wave;
    vWave = wave;

    // Compute a perturbed normal so the fresnel below has something to bite.
    vec3 normal = normalize(vec3(
      cos(pos.x * 0.55 + uTime * 1.3) * 0.45,
      cos((pos.x + pos.y) * 0.38 + uTime * 0.6) * 0.3,
      1.0
    ));
    vNormal = normalize(mat3(modelMatrix) * normal);

    vec4 worldPos = modelMatrix * vec4(pos, 1.0);
    vViewDir = normalize(cameraPosition - worldPos.xyz);

    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

const frag = /* glsl */ `
  uniform float uTime;
  uniform vec3 uShallow;
  uniform vec3 uDeep;
  uniform vec3 uFoam;
  uniform vec3 uSunDir;
  varying vec2 vUv;
  varying float vWave;
  varying vec3 vNormal;
  varying vec3 vViewDir;

  void main() {
    float d = distance(vUv, vec2(0.5));

    // Smooth alpha-edge so the water blends into the grass.
    float edge = smoothstep(0.5, 0.42, d);
    if (edge <= 0.001) discard;

    // Foam ring at the rim — bright thin band right before the edge.
    float foamRing = smoothstep(0.42, 0.45, d) * (1.0 - smoothstep(0.47, 0.5, d));
    // Animate foam slightly so it looks like lapping ripples.
    foamRing *= 0.5 + 0.5 * sin(vUv.x * 40.0 + vUv.y * 40.0 + uTime * 2.0);

    // Base water color — deeper in the middle, shallower at the edges.
    vec3 water = mix(uDeep, uShallow, smoothstep(0.4, 0.0, d));
    // Add wave-driven shading: peaks brighter, troughs darker.
    water = mix(water * 0.85, water * 1.15, smoothstep(-0.1, 0.1, vWave));

    // Fake fresnel — edges of view reflect more (lighter, sky-tinted).
    float fres = pow(1.0 - max(dot(vNormal, vViewDir), 0.0), 2.5);
    vec3 sky = vec3(0.95, 0.7, 0.55); // sunset
    water = mix(water, sky, fres * 0.55);

    // Specular highlight toward sun direction.
    vec3 H = normalize(uSunDir + vViewDir);
    float spec = pow(max(dot(vNormal, H), 0.0), 64.0);
    water += vec3(1.0, 0.85, 0.6) * spec * 0.8;

    // Mix in the foam ring.
    water = mix(water, uFoam, foamRing * 0.9);

    gl_FragColor = vec4(water, edge);
  }
`;

const rippleVert = /* glsl */ `
  uniform float uTime;
  uniform float uStart;
  void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;
const rippleFrag = /* glsl */ `
  uniform float uTime;
  uniform float uStart;
  void main() {
    float age = (uTime - uStart) / 1.5;
    if (age >= 1.0 || age < 0.0) discard;
    float alpha = (1.0 - age) * 0.55;
    gl_FragColor = vec4(0.85, 0.95, 1.0, alpha);
  }
`;

export class Water {
  constructor(scene, { position = new THREE.Vector3(-12, 0.05, 18), radius = 5.5, loader = null } = {}) {
    this.scene = scene;
    this.position = position.clone();
    this.radius = radius;
    this.loader = loader;

    // Higher-density mesh so the wave displacement looks smooth.
    const geom = new THREE.CircleGeometry(radius, 96);
    geom.rotateX(-Math.PI / 2);

    this.material = new THREE.ShaderMaterial({
      vertexShader: vert,
      fragmentShader: frag,
      transparent: true,
      depthWrite: false,
      uniforms: {
        uTime: { value: 0 },
        uShallow: { value: new THREE.Color('#5fc4e8') },
        uDeep: { value: new THREE.Color('#0e3a5c') },
        uFoam: { value: new THREE.Color('#f2f7ff') },
        uSunDir: { value: new THREE.Vector3(0.6, 0.45, 0.5).normalize() },
      },
    });

    this.mesh = new THREE.Mesh(geom, this.material);
    this.mesh.position.copy(position);
    this.mesh.receiveShadow = true;
    this.mesh.name = 'water';
    scene.add(this.mesh);

    this.lilyGroup = new THREE.Group();
    this.lilyGroup.position.copy(position);
    scene.add(this.lilyGroup);

    this.ripples = [];
    this._rippleTimer = 0;

    if (loader) this.#loadLilies();
  }

  async #loadLilies() {
    await this.#buildPondEcosystem();
  }

  /**
   * Pond ecosystem — rocks ringing the edge, reeds + short plants on the
   * shore, lily pads + frog on the surface, a partially-submerged log, and
   * a wooden dock for visual interest.
   */
  async #buildPondEcosystem() {
    const safeLoad = (url) =>
      this.loader.loadGLTF(url).then((g) => g).catch(() => null);

    const [
      lilyLarge, lilySmall,
      rockA, rockB, rockC,
      reed, shortPlant,
      shoreGrass,
      mushroomTan,
      log,
      dock,
      frog,
    ] = await Promise.all([
      safeLoad('/models/nature/lily-large.glb'),
      safeLoad('/models/nature/lily-small.glb'),
      safeLoad('/models/nature/rock-largea.glb'),
      safeLoad('/models/nature/rock-largeb.glb'),
      safeLoad('/models/nature/rock-largec.glb'),
      safeLoad('/models/nature/plant-flattall.glb'),
      safeLoad('/models/nature/plant-flatshort.glb'),
      safeLoad('/models/nature/grass-leafslarge.glb'),
      safeLoad('/models/nature/mushroom-tan.glb'),
      safeLoad('/models/nature/log.glb'),
      safeLoad('/models/extras/dock-long.glb'),
      safeLoad('/models/wildlife/frog.glb'),
    ]);

    /**
     * For static GLBs, Box3.setFromObject is fine, but rigged/skinned models
     * (like Frog.glb) return a tiny bind-pose box that wrecks the auto-fit
     * math. Computing the union of each mesh's geometry.boundingBox in
     * world space gives a reliable measurement either way.
     */
    const measureSize = (obj) => {
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3();
      obj.traverse((c) => {
        if (c.isMesh && c.geometry) {
          if (!c.geometry.boundingBox) c.geometry.computeBoundingBox();
          const meshBox = c.geometry.boundingBox.clone();
          meshBox.applyMatrix4(c.matrixWorld);
          box.union(meshBox);
        }
      });
      if (box.isEmpty()) return new THREE.Vector3(1, 1, 1);
      return box.getSize(new THREE.Vector3());
    };

    // Place a model with bounding-box auto-fit so a model's native scale
    // can't dwarf the scene. `targetMax` is the longest world-space dim we
    // want the placed model to occupy.
    const place = (src, dx, dy, dz, targetMax, yaw, opts = {}) => {
      if (!src) return null;
      const obj = src.scene.clone(true);
      const size = measureSize(obj);
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      obj.scale.setScalar(targetMax / maxDim);
      obj.position.set(dx, dy, dz);
      obj.rotation.y = yaw;
      obj.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = opts.castShadow ?? false;
          c.receiveShadow = true;
        }
      });
      this.lilyGroup.add(obj);
      return obj;
    };

    // ── Rocks around the edge ────────────────────────────────────────────
    const rockVariants = [rockA, rockB, rockC].filter(Boolean);
    if (rockVariants.length) {
      for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2 + 0.18;
        const r = this.radius * (0.88 + Math.random() * 0.12);
        const variant = rockVariants[i % rockVariants.length];
        place(
          variant,
          Math.cos(angle) * r,
          -0.05 + Math.random() * 0.08,
          Math.sin(angle) * r,
          1.2 + Math.random() * 0.5,   // 1.2–1.7m rocks
          Math.random() * Math.PI * 2,
          { castShadow: true },
        );
      }
    }

    // ── Reed clusters around the perimeter ───────────────────────────────
    if (reed) {
      const reedAngles = [0.3, 1.1, 2.4, 3.5, 4.7, 5.6];
      for (const a of reedAngles) {
        for (let j = 0; j < 3; j++) {
          const jitterA = a + (j - 1) * 0.08;
          const jitterR = this.radius * (0.93 + Math.random() * 0.05);
          place(
            reed,
            Math.cos(jitterA) * jitterR + (Math.random() - 0.5) * 0.2,
            0.05,
            Math.sin(jitterA) * jitterR + (Math.random() - 0.5) * 0.2,
            0.9 + Math.random() * 0.3,  // 0.9–1.2m reeds
            Math.random() * Math.PI * 2,
          );
        }
      }
    }

    // ── Short plants between the rocks ───────────────────────────────────
    if (shortPlant) {
      for (let i = 0; i < 10; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = this.radius * (0.85 + Math.random() * 0.1);
        place(
          shortPlant,
          Math.cos(angle) * r,
          0.05,
          Math.sin(angle) * r,
          0.45 + Math.random() * 0.2,   // 0.45–0.65m
          Math.random() * Math.PI * 2,
        );
      }
    }

    // ── Dense shore grass tucked right at the waterline ──────────────────
    if (shoreGrass) {
      for (let i = 0; i < 14; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = this.radius * (0.92 + Math.random() * 0.06);
        place(
          shoreGrass,
          Math.cos(angle) * r,
          0.04,
          Math.sin(angle) * r,
          0.55 + Math.random() * 0.25,
          Math.random() * Math.PI * 2,
        );
      }
    }

    // ── Mushrooms near the wet rocks ─────────────────────────────────────
    if (mushroomTan) {
      for (let i = 0; i < 3; i++) {
        const angle = Math.random() * Math.PI * 2;
        const r = this.radius * (0.97 + Math.random() * 0.06);
        place(
          mushroomTan,
          Math.cos(angle) * r,
          0.05,
          Math.sin(angle) * r,
          0.4 + Math.random() * 0.15,
          Math.random() * Math.PI * 2,
        );
      }
    }

    // ── A fallen log dipping into the water ──────────────────────────────
    if (log) {
      const logA = 1.9;
      place(log, Math.cos(logA) * (this.radius - 0.6), 0.0, Math.sin(logA) * (this.radius - 0.6), 2.0, logA + Math.PI / 2, { castShadow: true });
    }

    // ── Lily pads floating on the water (5 of them) ─────────────────────
    const lilyPlacements = [
      { src: lilyLarge, dx: -1.8, dz:  1.2, targetMax: 0.95, yaw: 0.7 },
      { src: lilyLarge, dx:  2.1, dz: -0.6, targetMax: 0.85, yaw: 2.1 },
      { src: lilySmall, dx:  1.0, dz:  2.4, targetMax: 0.7,  yaw: 0.0 },
      { src: lilySmall, dx: -2.6, dz: -1.6, targetMax: 0.75, yaw: 1.4 },
      { src: lilySmall, dx:  0.4, dz: -2.8, targetMax: 0.65, yaw: 3.2 },
    ];
    this.lilyMeshes = [];
    for (const p of lilyPlacements) {
      const lily = place(p.src, p.dx, 0.05, p.dz, p.targetMax, p.yaw);
      if (lily) {
        lily.userData.basePos = { x: p.dx, z: p.dz, phase: Math.random() * Math.PI * 2 };
        this.lilyMeshes.push(lily);
      }
    }

    // ── Frog on the largest lily pad ─────────────────────────────────────
    // The frog is skinned/rigged; cloning it loses the skeleton link and the
    // auto-fit reads a tiny bind-pose box that scales it up massively. Use
    // the source scene directly (one frog only) and a hand-picked scale.
    if (frog && this.lilyMeshes.length) {
      const host = this.lilyMeshes[0];
      const f = frog.scene;
      f.scale.setScalar(0.18);   // hand-tuned; Quaternius frog needs this
      f.position.set(host.userData.basePos.x, 0.18, host.userData.basePos.z);
      f.rotation.y = host.rotation.y;
      f.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = true;
          c.receiveShadow = true;
          c.frustumCulled = false; // skinned bounds are unreliable
        }
      });
      this.lilyGroup.add(f);
      this.frog = f;
    }

    // ── Wooden dock projecting into the water from the shore ─────────────
    if (dock) {
      const dockAngle = -1.0;
      const dockDist = this.radius - 0.4;
      place(
        dock,
        Math.cos(dockAngle) * dockDist,
        -0.05,
        Math.sin(dockAngle) * dockDist,
        2.8,                         // 2.8m long footbridge-ish
        dockAngle + Math.PI,
        { castShadow: true },
      );
    }
  }

  /** Spawn a single ripple ring at world position (xz). */
  spawnRipple(x, z, elapsed) {
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(0.05, 0.08, 32),
      new THREE.MeshBasicMaterial({
        color: 0xdaf1ff,
        transparent: true,
        opacity: 0.5,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(x, this.position.y + 0.06, z);
    ring.userData.start = elapsed;
    this.scene.add(ring);
    this.ripples.push(ring);
  }

  /** Returns true if (x, z) is inside the pond. */
  contains(x, z) {
    const dx = x - this.position.x;
    const dz = z - this.position.z;
    return dx * dx + dz * dz < (this.radius - 0.2) * (this.radius - 0.2);
  }

  update(elapsed, delta = 0, playerPos = null) {
    this.material.uniforms.uTime.value = elapsed;

    // Bob lily pads with the waves.
    if (this.lilyMeshes) {
      for (const lily of this.lilyMeshes) {
        const b = lily.userData.basePos;
        lily.position.y = 0.05 + Math.sin(elapsed * 1.5 + b.phase) * 0.04;
        lily.rotation.z = Math.sin(elapsed * 0.9 + b.phase) * 0.04;
      }
    }

    // Spawn a ripple under the player every ~0.35s while they're in the pond.
    if (playerPos && this.contains(playerPos.x, playerPos.z)) {
      this._rippleTimer += delta;
      if (this._rippleTimer >= 0.35) {
        this._rippleTimer = 0;
        this.spawnRipple(playerPos.x, playerPos.z, elapsed);
      }
    } else {
      this._rippleTimer = 0;
    }

    // Animate + cull ripples.
    for (let i = this.ripples.length - 1; i >= 0; i--) {
      const ring = this.ripples[i];
      const age = elapsed - ring.userData.start;
      const life = 1.5;
      if (age >= life) {
        this.scene.remove(ring);
        ring.geometry.dispose();
        ring.material.dispose();
        this.ripples.splice(i, 1);
        continue;
      }
      const t = age / life;
      ring.scale.setScalar(1 + t * 18);
      ring.material.opacity = (1 - t) * 0.5;
    }
  }
}
