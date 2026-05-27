import * as THREE from "three";

// Six different ways to scatter quad centers inside a unit volume. The whole
// point is that the cluster silhouette stops being a circle — each shape
// produces a visibly different blob. Per-instance, a ref deterministically
// picks one of these by hashing its position, so reload is stable.
const SHAPE_SCATTERS = {
  // Original spherical scatter (Bruno's default).
  sphere: () => {
    const radius = 1 - Math.pow(Math.random(), 3);
    const phi = Math.random() * Math.PI;
    const theta = Math.random() * Math.PI * 2;
    const sp = Math.sin(phi);
    return new THREE.Vector3(
      radius * sp * Math.cos(theta),
      radius * sp * Math.sin(theta),
      radius * Math.cos(phi),
    );
  },
  // Vertical pole — taller than wide. Reads like a column of leaves.
  pole: () => {
    const r = 1 - Math.pow(Math.random(), 3);
    const phi = Math.random() * Math.PI;
    const theta = Math.random() * Math.PI * 2;
    return new THREE.Vector3(
      r * 0.5 * Math.sin(phi) * Math.cos(theta),
      r * 1.55 * Math.cos(phi),
      r * 0.5 * Math.sin(phi) * Math.sin(theta),
    );
  },
  // Flat disc — wide and squashed. Reads like an umbrella canopy.
  disc: () => {
    const r = Math.sqrt(1 - Math.pow(Math.random(), 2));
    const theta = Math.random() * Math.PI * 2;
    return new THREE.Vector3(
      r * Math.cos(theta) * 1.4,
      (Math.random() - 0.5) * 0.55,
      r * Math.sin(theta) * 1.4,
    );
  },
  // Lopsided sphere — mass concentrated on one side. Reads like a half-eaten
  // canopy or a tree that grew toward the sun.
  lopsided: () => {
    const radius = 1 - Math.pow(Math.random(), 3);
    const phi = Math.random() * Math.PI;
    const theta = Math.random() * Math.PI * 2;
    const sp = Math.sin(phi);
    return new THREE.Vector3(
      radius * sp * Math.cos(theta) + 0.40,
      radius * sp * Math.sin(theta),
      radius * Math.cos(phi),
    );
  },
  // Cone — wide at bottom, narrow at top. Reads like a conifer.
  cone: () => {
    const t = Math.random();
    const yNorm = 1 - 2 * Math.pow(t, 0.55);  // -1..1, biased toward -1
    const rAtY = Math.max(0.1, (1 - yNorm) * 0.55);
    const theta = Math.random() * Math.PI * 2;
    const r = Math.sqrt(1 - Math.pow(Math.random(), 2)) * rAtY;
    return new THREE.Vector3(
      r * Math.cos(theta),
      yNorm,
      r * Math.sin(theta),
    );
  },
  // Rough/lumpy sphere — sinusoidal warping breaks the smooth silhouette
  // into a potato-like irregular blob.
  rough: () => {
    const radius = 1 - Math.pow(Math.random(), 3);
    const phi = Math.random() * Math.PI;
    const theta = Math.random() * Math.PI * 2;
    const warp = 0.7 + 0.55 * Math.sin(3 * theta) * Math.cos(2 * phi);
    const sp = Math.sin(phi);
    return new THREE.Vector3(
      radius * warp * sp * Math.cos(theta),
      radius * warp * sp * Math.sin(theta),
      radius * warp * Math.cos(phi),
    );
  },
};
const SHAPE_KEYS = Object.keys(SHAPE_SCATTERS);

/**
 * Runtime SDF-quad foliage, port of Bruno Simon's folio-2025 `Foliage.js`
 * from three/webgpu (TSL) down to plain WebGL2 GLSL.
 *
 * Inputs:
 *  - refsByGroup: { leaves: [...], bushes: [...] } from GlbWorld.refs.foliage.
 *    Each ref is { position: Vector3, radius: number, species: string }.
 *    Emitted by `phase-11c-foliage-refs.py` as Blender empties.
 *  - sdfTexture: 128×128 grayscale foliage SDF (Bruno's `foliageSDF.png`).
 *  - wind: shared Wind instance — its uniforms drive the per-quad UV rotation
 *    so canopies shimmer in sync with grass / wind lines.
 *  - sunDirection: live-updated by App tick from TimeOfDay so two-tone
 *    light/shadow flips with day/night.
 *
 * Output:
 *  Per species, one InstancedMesh of an 80-quad sphere geometry, materialed
 *  with a custom ShaderMaterial: SDF alpha test, normal·sun two-color mix,
 *  and Three.js fog. Replaces the chunky baked canopies stripped by
 *  phase-11c — refs are the canopy anchors.
 */
export class Foliage {
  static QUADS_PER_CLOUD = 95;
  static QUAD_SIZE = 0.6; // larger quads → less see-through between clusters
  static ALPHA_THRESHOLD = 0.2; // lower discard → fuller leaf coverage

  // Multi-pair palettes per species. Each tree picks ONE pair deterministically
  // (by hashing its instance name) so the whole canopy of one tree shares a
  // colour — but neighbouring trees can be deep-green / lime / autumn-red /
  // salmon, the way real forests look.
  // Index 0 of each species array is the "default" used as a fallback.
  static PALETTES = {
    pine: [
      { a: "#243a1d", b: "#4a7e34" }, // classic deep green
      { a: "#395428", b: "#7da645" }, // lime spring green
      { a: "#582a1c", b: "#a14628" }, // autumn red
      { a: "#5e4216", b: "#c08a26" }, // autumn yellow-orange
      { a: "#2c4a1c", b: "#5b8a35" }, // mid green
    ],
    birch: [
      { a: "#3e5827", b: "#94b85a" }, // classic pale green
      { a: "#5d7838", b: "#bcd089" }, // pale lime
      { a: "#74332a", b: "#cb6457" }, // autumn pink-red
      { a: "#65532a", b: "#c89e3a" }, // autumn gold
      { a: "#4a652f", b: "#a5c570" }, // bright birch green
    ],
    hero: [
      { a: "#1f3220", b: "#3e6e30" }, // classic
      { a: "#172a18", b: "#345d27" }, // deep
      { a: "#5a2818", b: "#9c3e22" }, // autumn
      { a: "#3a4f24", b: "#6f9b3a" }, // mid green
    ],
    bush: [
      { a: "#2c4a20", b: "#5a8a3a" },
      { a: "#3f5827", b: "#7eaa45" },
      { a: "#5b2618", b: "#a8421f" },
      { a: "#5a4a1a", b: "#b09030" },
    ],
  };

  /** Extract the tree instance key from a ref name so all clusters on the
   * same tree get the same colour. */
  static treeIdFromRef(name) {
    // Matches:
    //   refTreeLeaves_tree_pine_inst_001_07   → tree_pine_inst_001
    //   refTreeLeaves_hero_tree_3_05          → hero_tree_3
    //   refBushLeaves_gc_bush_inst_042_00     → gc_bush_inst_042
    const m = (name || "").match(/^(?:refTreeLeaves|refBushLeaves)_(.+)_\d+$/);
    return m ? m[1] : (name || "");
  }

  /** Stable string hash for deterministic palette picks. */
  static _hashString(s) {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h;
  }

  /**
   * @param {THREE.Scene} scene
   * @param {{leaves: Array, bushes: Array}} refsByGroup
   * @param {THREE.Texture} sdfTexture
   * @param {import('./Wind.js').Wind} wind
   * @param {THREE.Vector3} [sunDirection]
   */
  constructor(scene, refsByGroup, sdfTexture, wind, sunDirection = null) {
    this.scene = scene;
    this.wind = wind;
    this.sunDirection = (sunDirection || new THREE.Vector3(-0.45, 0.86, -0.25))
      .clone()
      .normalize();
    this.meshes = [];
    this.materials = [];

    sdfTexture.wrapS = THREE.RepeatWrapping;
    sdfTexture.wrapT = THREE.RepeatWrapping;
    sdfTexture.minFilter = THREE.LinearFilter;
    sdfTexture.magFilter = THREE.LinearFilter;
    sdfTexture.colorSpace = THREE.NoColorSpace;
    sdfTexture.needsUpdate = true;

    // Group refs by species — one InstancedMesh per species (each has its
    // own color pair, but the quad geometry is shared across all of them).
    const groups = new Map();
    const collect = (arr) => {
      for (const r of arr || []) {
        const key = r.species || "pine";
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(r);
      }
    };
    collect(refsByGroup?.leaves);
    collect(refsByGroup?.bushes);

    if (groups.size === 0) {
      console.warn(
        "[Foliage] no refTreeLeaves_* / refBushLeaves_* refs found — run phase-11c-foliage-refs.py then re-export.",
      );
      return;
    }

    // Pre-build one geometry per shape — 6 distinct quad scatter patterns.
    // All clusters of a given shape share their geometry (instancing wins).
    const geometriesByShape = new Map();
    for (const shape of SHAPE_KEYS) {
      geometriesByShape.set(
        shape,
        this.#buildClusterGeometry(Foliage.QUADS_PER_CLOUD, SHAPE_SCATTERS[shape]),
      );
    }

    // Group refs by (species, shape). Shape is picked deterministically by
    // hashing position so a single ref always gets the same silhouette
    // across reloads.
    const subgroups = new Map(); // key="species:shape" → {species, shape, refs}
    for (const [species, refs] of groups) {
      for (const r of refs) {
        const h = Math.floor(
          Math.abs(r.position.x * 7.3 + r.position.z * 3.1 + r.position.y * 11.7),
        ) % SHAPE_KEYS.length;
        const shape = SHAPE_KEYS[h];
        const key = `${species}:${shape}`;
        if (!subgroups.has(key))
          subgroups.set(key, { species, shape, refs: [] });
        subgroups.get(key).refs.push(r);
      }
    }

    // Tree-id → color pair cache so all clusters on the same tree share a colour.
    const treeColorCache = new Map();
    const _tmpA = new THREE.Color();
    const _tmpB = new THREE.Color();

    for (const { species, shape, refs } of subgroups.values()) {
      const palette = Foliage.PALETTES[species] || Foliage.PALETTES.pine;
      const material = this.#buildMaterial(sdfTexture);
      // Clone the shared shape geometry so per-instance colour attributes
      // attached below only affect THIS InstancedMesh (BufferGeometry
      // attributes are mesh-shared otherwise).
      const geom = geometriesByShape.get(shape).clone();
      const mesh = new THREE.InstancedMesh(geom, material, refs.length);
      mesh.name = `foliage_${species}_${shape}`;
      mesh.frustumCulled = false;
      mesh.castShadow = false;
      mesh.receiveShadow = false;
      mesh.userData.noTorchRaycast = true;

      const colorAArr = new Float32Array(refs.length * 3);
      const colorBArr = new Float32Array(refs.length * 3);

      const m = new THREE.Matrix4();
      const q = new THREE.Quaternion();
      const e = new THREE.Euler();
      const s = new THREE.Vector3();
      for (let i = 0; i < refs.length; i++) {
        const r = refs[i];
        const baseR = Math.max(0.1, r.radius || 1);

        const tiltX = (Math.random() - 0.5) * 0.55;
        const tiltZ = (Math.random() - 0.5) * 0.55;
        const yaw = Math.random() * Math.PI * 2;
        e.set(tiltX, yaw, tiltZ);
        q.setFromEuler(e);

        const sx = baseR * (0.85 + Math.random() * 0.40);
        const sy = baseR * (0.75 + Math.random() * 0.35);
        const sz = baseR * (0.85 + Math.random() * 0.40);
        s.set(sx, sy, sz);

        m.compose(r.position, q, s);
        mesh.setMatrixAt(i, m);

        // Pick a palette pair PER TREE (not per cluster) so a single tree's
        // canopy is colour-coherent. Cached so repeated lookups are cheap.
        const treeId = Foliage.treeIdFromRef(r.name);
        let pair = treeColorCache.get(treeId);
        if (!pair) {
          const idx = Foliage._hashString(treeId) % palette.length;
          pair = palette[idx];
          treeColorCache.set(treeId, pair);
        }
        _tmpA.set(pair.a);
        _tmpB.set(pair.b);
        const off = i * 3;
        colorAArr[off + 0] = _tmpA.r;
        colorAArr[off + 1] = _tmpA.g;
        colorAArr[off + 2] = _tmpA.b;
        colorBArr[off + 0] = _tmpB.r;
        colorBArr[off + 1] = _tmpB.g;
        colorBArr[off + 2] = _tmpB.b;
      }
      geom.setAttribute(
        "instanceColorA",
        new THREE.InstancedBufferAttribute(colorAArr, 3),
      );
      geom.setAttribute(
        "instanceColorB",
        new THREE.InstancedBufferAttribute(colorBArr, 3),
      );
      mesh.instanceMatrix.needsUpdate = true;
      scene.add(mesh);
      this.meshes.push(mesh);
      this.materials.push(material);
    }

    console.log(
      "[Foliage] created",
      this.meshes.length,
      "shape-meshes across",
      groups.size,
      "species —",
      Array.from(subgroups.values())
        .map((g) => `${g.species}/${g.shape}:${g.refs.length}`)
        .join(" "),
    );
  }

  // ── Geometry ──────────────────────────────────────────────────────────────

  /**
   * Build one indexed BufferGeometry of `count` small quads whose centers are
   * scattered by `scatterFn` (one of SHAPE_SCATTERS). Each quad's vertex
   * normals lerp 85% toward the cluster center's radial direction — Bruno's
   * trick that makes the cloud light like a volumetric blob rather than
   * flat sheets, no matter the shape.
   */
  #buildClusterGeometry(count, scatterFn) {
    const half = Foliage.QUAD_SIZE * 0.5;
    const positions = new Float32Array(count * 4 * 3);
    const normals = new Float32Array(count * 4 * 3);
    const uvs = new Float32Array(count * 4 * 2);
    const indices = new Uint16Array(count * 6);

    const localCorners = [
      [-half, -half, 0],
      [half, -half, 0],
      [half, half, 0],
      [-half, half, 0],
    ];
    const localUv = [
      [0, 0],
      [1, 0],
      [1, 1],
      [0, 1],
    ];

    const tmp = new THREE.Vector3();
    const tangent = new THREE.Vector3();
    const bitangent = new THREE.Vector3();
    const axisA = new THREE.Vector3();
    const axisB = new THREE.Vector3();
    const refUp = new THREE.Vector3();

    for (let i = 0; i < count; i++) {
      // Cluster shape is decided by the scatter function passed in — sphere,
      // pole, disc, lopsided, cone, or rough.
      const center = scatterFn();

      const outward =
        center.lengthSq() > 1e-6
          ? center.clone().normalize()
          : new THREE.Vector3(0, 0, 1);

      // Orthonormal basis around outward, plus a random spin.
      refUp.set(
        Math.abs(outward.y) < 0.9 ? 0 : 1,
        Math.abs(outward.y) < 0.9 ? 1 : 0,
        0,
      );
      tangent.crossVectors(outward, refUp).normalize();
      bitangent.crossVectors(outward, tangent).normalize();
      const spin = Math.random() * Math.PI * 2;
      const cs = Math.cos(spin),
        sn = Math.sin(spin);
      axisA.copy(tangent).multiplyScalar(cs).addScaledVector(bitangent, sn);
      axisB.copy(tangent).multiplyScalar(-sn).addScaledVector(bitangent, cs);

      for (let v = 0; v < 4; v++) {
        const lc = localCorners[v];
        tmp
          .copy(center)
          .addScaledVector(axisA, lc[0])
          .addScaledVector(axisB, lc[1]);
        const p3 = (i * 4 + v) * 3;
        positions[p3 + 0] = tmp.x;
        positions[p3 + 1] = tmp.y;
        positions[p3 + 2] = tmp.z;

        // 85% sphere-normal + 15% local-from-centre, normalized.
        const local = tmp.clone().sub(center);
        if (local.lengthSq() > 1e-6) local.normalize();
        else local.copy(outward);
        local.lerp(outward, 0.85).normalize();
        normals[p3 + 0] = local.x;
        normals[p3 + 1] = local.y;
        normals[p3 + 2] = local.z;

        const u2 = (i * 4 + v) * 2;
        uvs[u2 + 0] = localUv[v][0];
        uvs[u2 + 1] = localUv[v][1];
      }

      const base = i * 4;
      const ix = i * 6;
      indices[ix + 0] = base + 0;
      indices[ix + 1] = base + 1;
      indices[ix + 2] = base + 2;
      indices[ix + 3] = base + 0;
      indices[ix + 4] = base + 2;
      indices[ix + 5] = base + 3;
    }

    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.setAttribute("normal", new THREE.BufferAttribute(normals, 3));
    g.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
    g.setIndex(new THREE.BufferAttribute(indices, 1));
    return g;
  }

  // ── Material ──────────────────────────────────────────────────────────────

  #buildMaterial(sdfTexture) {
    const wu = this.wind?.uniforms || {};
    const uniforms = THREE.UniformsUtils.merge([
      THREE.UniformsLib.fog,
      {
        uFoliageSDF: { value: null },
        uSunDir: { value: new THREE.Vector3() },
        uAlphaThreshold: { value: Foliage.ALPHA_THRESHOLD },
        uWindTime: { value: 0 },
        uWindDir: { value: new THREE.Vector2(1, 0) },
        uWindStrength: { value: 0.35 },
        uWindNoise: { value: null },
      },
    ]);
    // After merge clone, set live references so wind / sdf updates flow.
    uniforms.uFoliageSDF.value = sdfTexture;
    uniforms.uSunDir.value = this.sunDirection.clone();
    if (wu.uWindTime) uniforms.uWindTime = wu.uWindTime;
    if (wu.uWindDir) uniforms.uWindDir = wu.uWindDir;
    if (wu.uWindStrength) uniforms.uWindStrength = wu.uWindStrength;
    if (wu.uWindNoise) uniforms.uWindNoise = wu.uWindNoise;

    const vertexShader = /* glsl */ `
      attribute vec3 instanceColorA;
      attribute vec3 instanceColorB;

      varying vec3 vNormalWorld;
      varying vec2 vUv;
      varying vec3 vLocalPos;
      varying vec3 vColorA;
      varying vec3 vColorB;

      #include <fog_pars_vertex>

      void main() {
        vUv = uv;
        vLocalPos = position;
        vColorA = instanceColorA;
        vColorB = instanceColorB;

        mat4 worldMatrix = modelMatrix * instanceMatrix;
        vec4 worldPos = worldMatrix * vec4(position, 1.0);
        vec4 mvPosition = viewMatrix * worldPos;

        mat3 nm = mat3(worldMatrix);
        vNormalWorld = normalize(nm * normal);

        gl_Position = projectionMatrix * mvPosition;

        #include <fog_vertex>
      }
    `;

    const fragmentShader = /* glsl */ `
      uniform sampler2D uFoliageSDF;
      uniform vec3      uSunDir;
      uniform float     uAlphaThreshold;

      uniform float     uWindTime;
      uniform vec2      uWindDir;
      uniform float     uWindStrength;
      uniform sampler2D uWindNoise;

      varying vec3 vNormalWorld;
      varying vec2 vUv;
      varying vec3 vLocalPos;
      varying vec3 vColorA;
      varying vec3 vColorB;

      #include <fog_pars_fragment>

      vec2 windOffset(vec2 worldXZ) {
        vec2 dir = uWindDir;
        vec2 uvA = worldXZ * 0.03 + dir * uWindTime * 0.04;
        float nA = texture2D(uWindNoise, uvA).r - 0.5;
        vec2 uvB = worldXZ * 0.11 + dir * uWindTime * 0.22;
        float nB = texture2D(uWindNoise, uvB).r - 0.5;
        float sway = nA * 2.0 + nB * 0.8;
        return dir * sway * uWindStrength;
      }

      vec2 rotateUv(vec2 inUv, float angle, vec2 center) {
        float s = sin(angle);
        float c = cos(angle);
        vec2 p = inUv - center;
        return vec2(p.x * c - p.y * s, p.x * s + p.y * c) + center;
      }

      void main() {
        float angle = length(windOffset(vLocalPos.xz)) * 2.2;
        vec2 rUv = rotateUv(vUv, angle, vec2(0.5));

        float sdf = texture2D(uFoliageSDF, rUv).r;
        if (sdf < uAlphaThreshold) discard;

        float mixStrength = smoothstep(0.0, 1.0,
          dot(normalize(vNormalWorld), normalize(uSunDir)));
        // Colours are per-instance — each tree picks its own pair from the
        // species palette so the forest reads green/red/yellow/lime.
        vec3 col = mix(vColorA, vColorB, mixStrength);

        gl_FragColor = vec4(col, 1.0);
        #include <fog_fragment>
      }
    `;

    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader,
      fragmentShader,
      side: THREE.DoubleSide,
      transparent: false,
      depthWrite: true,
      fog: true,
    });
    material.userData.isFoliage = true;
    return material;
  }

  // ── Public hooks ─────────────────────────────────────────────────────────

  /** Update the sun direction (call from App tick / TimeOfDay). */
  setSunDirection(dir) {
    if (!dir) return;
    this.sunDirection.copy(dir).normalize();
    for (const m of this.materials) {
      m.uniforms.uSunDir.value.copy(this.sunDirection);
    }
  }

  /** Override per-species palette at runtime (mostly for tuning). */
  setSpeciesPalette(species, colorA, colorB) {
    const palette = Foliage.PALETTES[species];
    if (!palette) return;
    palette.a = colorA;
    palette.b = colorB;
    for (const m of this.materials) {
      // No species marker on the material yet — caller can pass mesh.name
      // and look up via meshes[]. Kept simple for first cut.
    }
  }

  dispose() {
    for (const m of this.meshes) {
      this.scene.remove(m);
      m.geometry?.dispose?.();
      m.material?.dispose?.();
    }
    this.meshes.length = 0;
    this.materials.length = 0;
  }
}
