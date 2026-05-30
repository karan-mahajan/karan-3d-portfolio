import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import {
  Fn, attribute, uniform, varying, positionGeometry,
  vec2, vec3, float, color, texture, step, mod, clamp, mix, sin, cos,
} from 'three/tsl';

/**
 * Runtime grass field — karan's authored curved-blade grass ("myGrass") ported
 * to a TSL instanced field for the WebGPU backend.
 *
 * Unlike Bruno's flat camera-billboarded triangle, each blade is the real
 * 9-vertex arched blade authored in Blender (`Plane.012`): a 4-segment stem
 * that tapers from a 0.030 m base to a single tip and curves forward, with a
 * per-vertex `blade_height` [0,1] driving a 6-stop colour ramp (dark olive base
 * → soft dry-yellow tip), plus a ~10% "dry" variant whose upper stops go brown.
 * Blades get a random yaw + small ±20° lean (rooted at the base) and a
 * continuous size multiplier — exactly the GN scatter the blend bakes, but
 * instanced at runtime instead of the 3.15 M static mesh.
 *
 * Runtime feasibility (Bruno's technique, kept): a fixed N×N instance grid is
 * generated once and, each frame, modulo-wrapped into a window centred on the
 * player inside the vertex node — the same ~N² blades always surround the
 * player (one draw call, culling off). Density/size fade and water/path
 * cut-outs come from the terrain grass mask (G channel, ±gridBounds grid,
 * `uv = worldXZ/(2*bounds)+0.5`); blade base Y is sampled from a height texture
 * baked off the terrain heightfield so blades sit on the real ground; the tip
 * bends with the shared Wind module (one wind across the scene).
 */

// 9-vert curved blade authored on Plane.012. Blender uses Z-up / +Y-forward;
// remapped here to three's Y-up: three(x, y, z) = blender(x_width, z_up, y_fwd).
const BLADE_HEIGHT_MAX = 0.55;
const BLENDER_VERTS = [
  [-0.030, 0.000, 0.000], [0.030, 0.000, 0.000],   // base
  [-0.026, 0.025, 0.165], [0.026, 0.025, 0.165],   // seg 1
  [-0.020, 0.065, 0.310], [0.020, 0.065, 0.310],   // seg 2
  [-0.013, 0.120, 0.450], [0.013, 0.120, 0.450],   // seg 3
  [0.000, 0.170, 0.550],                           // tip
];
const BLADE_FACES = [0, 1, 3, 0, 3, 2, 2, 3, 5, 2, 5, 4, 4, 5, 7, 4, 7, 6, 6, 7, 8];

// Random rotation envelope per blade (radians). Small lean + full spin.
const TILT_X = 0.35;
const TILT_Y = 0.35;
// Continuous per-blade size multiplier (× the mask), authored range.
const SIZE_MIN_FACTOR = 0.35;
const SIZE_MAX_FACTOR = 1.50;
const DRY_FRACTION = 0.10;

// Blade colour ramp (sRGB hex; three converts → linear, matching Blender).
const PALETTE_GREEN = [
  [0.00, '#4F6429'], [0.30, '#617707'], [0.55, '#80890C'],
  [0.75, '#90A110'], [0.90, '#A8AD36'], [1.00, '#B8B868'],
];
const PALETTE_DRY = [
  [0.00, '#4F6429'], [0.30, '#617707'], [0.55, '#80890C'],
  [0.75, '#6B4A30'], [0.90, '#8A6A55'], [1.00, '#9B6B75'],
];
// Day grass tint reference — TimeOfDay's day grassColor. setColor() normalises
// against this so day reads neutral (palette intact) and night darkens/cools.
const DAY_GRASS_REF = '#5aa033';

export class Grass {
  /**
   * @param {THREE.Scene} scene
   * @param {{heights:Float32Array, segments:number, size:number, bboxMin:THREE.Vector3}} terrain
   * @param {import('./Wind.js').Wind} wind
   * @param {THREE.Texture|null} mask  terrainGrass.exr (G = density). May be null.
   * @param {object} [opts]
   * @param {number} [opts.radius]       visible half-extent around the player (m)
   * @param {number} [opts.subdivisions] blades per axis (N → N² blades)
   * @param {number} [opts.gridBounds]   mask grid half-extent (manifest grassGrid.bounds)
   */
  constructor(scene, terrain, wind, mask, opts = {}) {
    this.scene = scene;
    this.terrain = terrain;
    this.wind = wind;
    this.mask = mask;

    this.radius = opts.radius ?? 38;
    this.subdivisions = Math.max(16, Math.floor(opts.subdivisions ?? 820));
    this.gridBounds = opts.gridBounds ?? 96;
    this.size = this.radius * 2;
    this.count = this.subdivisions * this.subdivisions;
    this.fragmentSize = this.size / this.subdivisions;

    this.baseColor = new THREE.Color(DAY_GRASS_REF);
    this._dayRef = new THREE.Color(DAY_GRASS_REF);

    this.#buildHeightTexture();
    this.#setGeometry();
    this.#setMaterial();
    this.#setMesh();
  }

  // ── Terrain height grounding (half-float so it's linearly filterable) ───────
  #buildHeightTexture() {
    const t = this.terrain;
    const verts = (t?.segments ?? 0) + 1;
    if (!t?.heights || verts < 2) {
      this.heightTex = null;
      this.terrainMin = new THREE.Vector2(-62.5, -62.5);
      this.terrainSpan = new THREE.Vector2(125, 125);
      return;
    }
    const src = t.heights; // src[u*verts + w]  (u = X index, w = Z index)
    const data = new Uint16Array(verts * verts);
    for (let u = 0; u < verts; u++) {
      for (let w = 0; w < verts; w++) {
        data[w * verts + u] = THREE.DataUtils.toHalfFloat(src[u * verts + w]);
      }
    }
    const tex = new THREE.DataTexture(data, verts, verts, THREE.RedFormat, THREE.HalfFloatType);
    tex.wrapS = THREE.ClampToEdgeWrapping;
    tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.generateMipmaps = false;
    tex.needsUpdate = true;
    this.heightTex = tex;
    this.terrainMin = new THREE.Vector2(t.bboxMin.x, t.bboxMin.z);
    this.terrainSpan = new THREE.Vector2(t.size, t.size);
  }

  // ── Geometry: one curved blade, N² instances ───────────────────────────────
  #setGeometry() {
    const base = new THREE.BufferGeometry();
    const verts = new Float32Array(BLENDER_VERTS.length * 3);
    const bladeHeight = new Float32Array(BLENDER_VERTS.length);
    for (let i = 0; i < BLENDER_VERTS.length; i++) {
      const [bx, by, bz] = BLENDER_VERTS[i];
      verts[i * 3] = bx;          // width   → x
      verts[i * 3 + 1] = bz;      // up       → y
      verts[i * 3 + 2] = by;      // forward  → z
      bladeHeight[i] = bz / BLADE_HEIGHT_MAX;
    }
    base.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
    base.setAttribute('blade_height', new THREE.Float32BufferAttribute(bladeHeight, 1));
    base.setIndex(BLADE_FACES);

    const geom = new THREE.InstancedBufferGeometry();
    geom.index = base.index;
    geom.attributes.position = base.attributes.position;
    geom.attributes.blade_height = base.attributes.blade_height;
    geom.instanceCount = this.count;
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    // Per-instance attributes (built once; CPU never touches them again).
    const offset = new Float32Array(this.count * 2);   // pre-wrap grid XZ
    const yaw = new Float32Array(this.count);
    const tilt = new Float32Array(this.count * 2);      // lean X, Z
    const sizeRand = new Float32Array(this.count);      // [SIZE_MIN, SIZE_MAX]
    const drySeed = new Float32Array(this.count);

    const sub = this.subdivisions;
    for (let iX = 0; iX < sub; iX++) {
      const fx = (iX / sub - 0.5) * this.size + this.fragmentSize * 0.5;
      for (let iZ = 0; iZ < sub; iZ++) {
        const fz = (iZ / sub - 0.5) * this.size + this.fragmentSize * 0.5;
        const i = iX * sub + iZ;
        offset[i * 2] = fx + (Math.random() - 0.5) * this.fragmentSize;
        offset[i * 2 + 1] = fz + (Math.random() - 0.5) * this.fragmentSize;
        yaw[i] = Math.random() * Math.PI * 2;
        tilt[i * 2] = (Math.random() * 2 - 1) * TILT_X;
        tilt[i * 2 + 1] = (Math.random() * 2 - 1) * TILT_Y;
        sizeRand[i] = SIZE_MIN_FACTOR + Math.random() * (SIZE_MAX_FACTOR - SIZE_MIN_FACTOR);
        drySeed[i] = Math.random();
      }
    }
    geom.setAttribute('aOffset', new THREE.InstancedBufferAttribute(offset, 2));
    geom.setAttribute('aYaw', new THREE.InstancedBufferAttribute(yaw, 1));
    geom.setAttribute('aTilt', new THREE.InstancedBufferAttribute(tilt, 2));
    geom.setAttribute('aSize', new THREE.InstancedBufferAttribute(sizeRand, 1));
    geom.setAttribute('aDry', new THREE.InstancedBufferAttribute(drySeed, 1));

    this.geometry = geom;
  }

  // ── Material ────────────────────────────────────────────────────────────────
  #setMaterial() {
    this.center = uniform(vec2(0, 0));
    this.sizeUniform = uniform(this.size);
    this.uTerrainMin = uniform(vec2(this.terrainMin.x, this.terrainMin.y));
    this.uTerrainSpan = uniform(vec2(this.terrainSpan.x, this.terrainSpan.y));
    this.tint = uniform(vec3(1, 1, 1));

    const invSpan = 1 / (this.gridBounds * 2);

    const vBladeH = varying(float(0), 'vBladeH');
    const vDry = varying(float(0), 'vDry');

    // Rotation helpers — build node graphs (pivot at the blade base / origin).
    const rotX = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x, p.y.mul(c).sub(p.z.mul(s)), p.y.mul(s).add(p.z.mul(c))); };
    const rotZ = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).sub(p.y.mul(s)), p.x.mul(s).add(p.y.mul(c)), p.z); };
    const rotY = (p, a) => { const c = cos(a), s = sin(a); return vec3(p.x.mul(c).add(p.z.mul(s)), p.y, p.z.mul(c).sub(p.x.mul(s))); };

    const mat = new MeshLambertNodeMaterial({ side: THREE.DoubleSide });

    mat.positionNode = Fn(() => {
      const local = positionGeometry;                 // blade vertex (m)
      const hb = attribute('blade_height');           // 0 base → 1 tip
      const off = attribute('aOffset');
      const yaw = attribute('aYaw');
      const tilt = attribute('aTilt');
      const sizeR = attribute('aSize');
      const dry = attribute('aDry');

      // Wrap the blade into the player-centred window.
      const half = this.sizeUniform.mul(0.5);
      const loop = off.sub(this.center).toVar();
      loop.x.assign(mod(loop.x.add(half), this.sizeUniform).sub(half));
      loop.y.assign(mod(loop.y.add(half), this.sizeUniform).sub(half));
      const worldXZ = loop.add(this.center);

      // Mask → density/size fade + hard cut over water/paths.
      const maskG = this.mask
        ? texture(this.mask, worldXZ.mul(invSpan).add(0.5)).g
        : float(0.5);
      const grassFactor = clamp(maskG.mul(1.8), 0, 1);
      const size = sizeR.mul(grassFactor);

      // Blade local → scaled → leaned → spun (all rooted at the base).
      let p = local.mul(size);
      p = rotX(p, tilt.x);
      p = rotZ(p, tilt.y);
      p = rotY(p, yaw);

      // Ground Y from the baked height texture.
      const hUv = worldXZ.sub(this.uTerrainMin).div(this.uTerrainSpan);
      const baseY = this.heightTex ? texture(this.heightTex, hUv).r : float(0);

      const world = vec3(worldXZ.x.add(p.x), baseY.add(p.y), worldXZ.y.add(p.z)).toVar();

      // Wind — bend more toward the tip (blade_height weighted).
      const wind = this.wind.offsetNode(worldXZ).mul(hb).mul(0.6);
      world.x.addAssign(wind.x);
      world.z.addAssign(wind.y);

      // Hide blades with ~no grass by lifting them out of view.
      world.y.addAssign(step(maskG, 0.06).mul(100.0));

      vBladeH.assign(hb);
      vDry.assign(dry);
      return world;
    })();

    mat.normalNode = vec3(0, 1, 0);

    // Colour ramp lookup — piecewise-linear over the palette stops.
    const ramp = (t, stops) => {
      let c = color(stops[0][1]);
      for (let i = 1; i < stops.length; i++) {
        const f = clamp(t.sub(stops[i - 1][0]).div(stops[i][0] - stops[i - 1][0]), 0, 1);
        c = mix(c, color(stops[i][1]), f);
      }
      return c;
    };
    const green = ramp(vBladeH, PALETTE_GREEN);
    const dryCol = ramp(vBladeH, PALETTE_DRY);
    const isDry = step(vDry, DRY_FRACTION);          // 1 when this blade is dry
    mat.colorNode = mix(green, dryCol, isDry).mul(this.tint);

    this.material = mat;
  }

  #setMesh() {
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    this.mesh.name = 'grass-field';
    this.mesh.frustumCulled = false;
    this.mesh.receiveShadow = true;
    this.mesh.castShadow = false;
    this.mesh.userData.noTorchRaycast = true;
    this.scene.add(this.mesh);
  }

  // ── Public API (matches the surface TimeOfDay / App expect) ─────────────────

  /** Recentre the grid on the player each frame. */
  setPlayerPos(pos) {
    if (!pos) return;
    this.center.value.set(pos.x, pos.z);
  }

  /** Day/night tint (TimeOfDay.applyInstant) — normalised against the day ref. */
  setColor(hex) {
    this.baseColor.set(hex);
    this.syncColor();
  }

  /** Push the live tint (baseColor / dayRef) into the GPU uniform. */
  syncColor() {
    const r = THREE.MathUtils.clamp(this.baseColor.r / Math.max(this._dayRef.r, 1e-3), 0, 1.5);
    const g = THREE.MathUtils.clamp(this.baseColor.g / Math.max(this._dayRef.g, 1e-3), 0, 1.5);
    const b = THREE.MathUtils.clamp(this.baseColor.b / Math.max(this._dayRef.b, 1e-3), 0, 1.5);
    this.tint.value.set(r, g, b);
  }

  dispose() {
    this.scene.remove(this.mesh);
    this.geometry?.dispose();
    this.material?.dispose();
    this.heightTex?.dispose();
  }
}
