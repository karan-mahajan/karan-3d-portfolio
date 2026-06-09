import {
  Fn,
  abs,
  attribute,
  clamp,
  color,
  cos,
  float,
  length,
  max,
  mix,
  mod,
  positionGeometry,
  sin,
  smoothstep,
  step,
  texture,
  uniform,
  varying,
  vec2,
  vec3,
} from "three/tsl";
import * as THREE from "three/webgpu";
import { MeshLambertNodeMaterial } from "three/webgpu";
import { snowGrowAt, SNOW_ALBEDO } from "./SnowState.js";

/**
 * Runtime grass field — karan's authored curved-blade grass ("myGrass") ported
 * to a TSL instanced field for the WebGPU backend.
 *
 * Unlike Bruno's flat camera-billboarded triangle, each blade is the authored
 * Blender arch (`Plane.012`), decimated to a 5-vertex stem (base → elbow → tip)
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

// 5-vert curved blade — the authored Plane.012 arch decimated from 9 verts to
// its base, elbow (old seg2, the point the dropped rings deviate from most), and
// tip. Keeps the forward arch + taper; halves the per-vertex positionNode cost
// (wind + player-bend + mask + height + 3 rotations all run per vertex), the
// dominant grass expense. Blender uses Z-up / +Y-forward; remapped to three's
// Y-up: three(x, y, z) = blender(x_width, z_up, y_fwd). Stored [width, fwd, up].
const BLADE_HEIGHT_MAX = 0.45;
// Vertical scale on the authored blade — 0.6 = 40% shorter (bottom-to-top).
// Scales the arch (up + forward) uniformly so the curve shape and base width
// are unchanged; gives a shorter, calmer lawn and less per-blade fill-rate.
// blade_height (the colour-ramp attribute) stays on the ORIGINAL profile so the
// tip/base colours don't shift when the geometry is scaled.
const BLADE_HEIGHT_SCALE = 0.6;
const BLENDER_VERTS = [
  [-0.03, 0.0, 0.0],
  [0.03, 0.0, 0.0], // base
  [-0.02, 0.065, 0.31],
  [0.02, 0.065, 0.31], // elbow (old seg 2)
  [0.0, 0.17, 0.55], // tip
];
const BLADE_FACES = [0, 1, 3, 0, 3, 2, 2, 3, 4];

// Random rotation envelope per blade (radians). Small lean + full spin.
const TILT_X = 0.35;
const TILT_Y = 0.35;
// Continuous per-blade size multiplier (× the mask), authored range.
const SIZE_MIN_FACTOR = 0.35;
const SIZE_MAX_FACTOR = 1.5;
const DRY_FRACTION = 0.1;

// Mask G → blade coverage. The mask is sparse (G tops out ~0.64, lots of low
// values), so a naive `G × k` scale leaves the partial-mask halos as stubble
// while the olive ground shows through. Instead: cull only where G is
// essentially zero (paths / water / bare plazas), and remap the surviving range
// [PRESENCE..FULL] → height [MIN_VISIBLE..1] so any grassy land grows a
// near-full blade. Raise MIN_VISIBLE / lower FULL_AT for even denser cover.
const GRASS_CULL = 0.03; // G ≤ this → no blade at all
// View cull: a blade whose direction-from-camera dots BELOW this against the
// camera forward is clearly behind the view and gets lifted out. -0.35 ≈ >110°
// off-axis, so it only drops blades well outside the frustum (no edge pop).
const GRASS_VIEW_CULL = -0.35;
const GRASS_PRESENCE = 0.03; // G where blades start growing
const GRASS_FULL_AT = 0.42; // G where blades reach full height
const GRASS_MIN_VISIBLE = 0.55; // blade height floor wherever any grass exists

// Player interaction. This is shader-side "soft physics": cheap enough for the
// full instanced field, but still reads like grass yielding around the avatar.
const WALK_BEND_RADIUS = 0.625;
const RUN_RIPPLE_RADIUS = 0.725;
const WALK_BEND_STRENGTH = 0.36;
const RUN_RIPPLE_STRENGTH = 0.17;
const RUN_RIPPLE_SPEED = 1.8; // quarter preview speed; keeps the wake very subtle

// Blade colour ramp (sRGB hex; three converts → linear, matching Blender).
const PALETTE_GREEN = [
  [0.0, "#4F6429"],
  [0.3, "#617707"],
  [0.55, "#80890C"],
  [0.75, "#90A110"],
  [0.9, "#A8AD36"],
  [1.0, "#B8B868"],
];
const PALETTE_DRY = [
  [0.0, "#4F6429"],
  [0.3, "#617707"],
  [0.55, "#80890C"],
  [0.75, "#6B4A30"],
  [0.9, "#8A6A55"],
  [1.0, "#9B6B75"],
];
// Day grass tint reference — TimeOfDay's day grassColor. setColor() normalises
// against this so day reads neutral (palette intact) and night darkens/cools.
const DAY_GRASS_REF = "#5aa033";

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
    this._lastMoveDir = new THREE.Vector2(0, 1);

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
    const tex = new THREE.DataTexture(
      data,
      verts,
      verts,
      THREE.RedFormat,
      THREE.HalfFloatType,
    );
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
      verts[i * 3] = bx; // width   → x  (unchanged thickness)
      verts[i * 3 + 1] = bz * BLADE_HEIGHT_SCALE; // up      → y  (40% shorter)
      verts[i * 3 + 2] = by * BLADE_HEIGHT_SCALE; // forward → z  (keep arch shape)
      bladeHeight[i] = bz / BLADE_HEIGHT_MAX; // colour ramp uses original profile
    }
    base.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
    base.setAttribute(
      "blade_height",
      new THREE.Float32BufferAttribute(bladeHeight, 1),
    );
    base.setIndex(BLADE_FACES);

    const geom = new THREE.InstancedBufferGeometry();
    geom.index = base.index;
    geom.attributes.position = base.attributes.position;
    geom.attributes.blade_height = base.attributes.blade_height;
    geom.instanceCount = this.count;
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    // Per-instance attributes (built once; CPU never touches them again).
    const offset = new Float32Array(this.count * 2); // pre-wrap grid XZ
    const yaw = new Float32Array(this.count);
    const tilt = new Float32Array(this.count * 2); // lean X, Z
    const sizeRand = new Float32Array(this.count); // [SIZE_MIN, SIZE_MAX]
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
        sizeRand[i] =
          SIZE_MIN_FACTOR + Math.random() * (SIZE_MAX_FACTOR - SIZE_MIN_FACTOR);
        drySeed[i] = Math.random();
      }
    }
    // Spatially shuffle the instances (Fisher–Yates). The grid above is built
    // row-major, so any prefix [0,k) would be one contiguous strip. Shuffling
    // makes every prefix a UNIFORM random sample of the field — that's what lets
    // the adaptive perf-shed thin grass just by lowering instanceCount (a
    // draw-count parameter, no rebuild/recompile) and have it sparsen evenly
    // instead of carving a hole off one edge. Done once at build; CPU never
    // touches these buffers again. (The full field at instanceCount === count
    // is unchanged — only the drop ORDER differs.)
    for (let i = this.count - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      [offset[i * 2], offset[j * 2]] = [offset[j * 2], offset[i * 2]];
      [offset[i * 2 + 1], offset[j * 2 + 1]] = [offset[j * 2 + 1], offset[i * 2 + 1]];
      [yaw[i], yaw[j]] = [yaw[j], yaw[i]];
      [tilt[i * 2], tilt[j * 2]] = [tilt[j * 2], tilt[i * 2]];
      [tilt[i * 2 + 1], tilt[j * 2 + 1]] = [tilt[j * 2 + 1], tilt[i * 2 + 1]];
      [sizeRand[i], sizeRand[j]] = [sizeRand[j], sizeRand[i]];
      [drySeed[i], drySeed[j]] = [drySeed[j], drySeed[i]];
    }

    geom.setAttribute("aOffset", new THREE.InstancedBufferAttribute(offset, 2));
    geom.setAttribute("aYaw", new THREE.InstancedBufferAttribute(yaw, 1));
    geom.setAttribute("aTilt", new THREE.InstancedBufferAttribute(tilt, 2));
    geom.setAttribute("aSize", new THREE.InstancedBufferAttribute(sizeRand, 1));
    geom.setAttribute("aDry", new THREE.InstancedBufferAttribute(drySeed, 1));

    this.geometry = geom;
  }

  // ── Material ────────────────────────────────────────────────────────────────
  #setMaterial() {
    this.center = uniform(vec2(0, 0));
    this.sizeUniform = uniform(this.size);
    this.uTerrainMin = uniform(vec2(this.terrainMin.x, this.terrainMin.y));
    this.uTerrainSpan = uniform(vec2(this.terrainSpan.x, this.terrainSpan.y));
    this.tint = uniform(vec3(1, 1, 1));
    this.uPlayerPos = uniform(vec2(0, 0));
    this.uPlayerDir = uniform(vec2(0, 1));
    this.uPlayerSpeed = uniform(0);
    this.uPlayerRunning = uniform(0);
    // Camera XZ forward + position for the view cull (see GRASS_VIEW_CULL).
    this.uCameraDir = uniform(vec2(0, 1));
    this.uCameraPos = uniform(vec2(0, 0));

    const invSpan = 1 / (this.gridBounds * 2);

    const vBladeH = varying(float(0), "vBladeH");
    const vDry = varying(float(0), "vDry");
    const vSnow = varying(float(0), "vSnow"); // patchy snow coverage at this blade

    // Rotation helpers — build node graphs (pivot at the blade base / origin).
    const rotX = (p, a) => {
      const c = cos(a),
        s = sin(a);
      return vec3(p.x, p.y.mul(c).sub(p.z.mul(s)), p.y.mul(s).add(p.z.mul(c)));
    };
    const rotZ = (p, a) => {
      const c = cos(a),
        s = sin(a);
      return vec3(p.x.mul(c).sub(p.y.mul(s)), p.x.mul(s).add(p.y.mul(c)), p.z);
    };
    const rotY = (p, a) => {
      const c = cos(a),
        s = sin(a);
      return vec3(p.x.mul(c).add(p.z.mul(s)), p.y, p.z.mul(c).sub(p.x.mul(s)));
    };

    const mat = new MeshLambertNodeMaterial({ side: THREE.DoubleSide });

    mat.positionNode = Fn(() => {
      const local = positionGeometry; // blade vertex (m)
      const hb = attribute("blade_height"); // 0 base → 1 tip
      const off = attribute("aOffset");
      const yaw = attribute("aYaw");
      const tilt = attribute("aTilt");
      const sizeR = attribute("aSize");
      const dry = attribute("aDry");

      // Wrap the blade into the player-centred window.
      const half = this.sizeUniform.mul(0.5);
      const loop = off.sub(this.center).toVar();
      loop.x.assign(mod(loop.x.add(half), this.sizeUniform).sub(half));
      loop.y.assign(mod(loop.y.add(half), this.sizeUniform).sub(half));
      const worldXZ = loop.add(this.center);

      // Mask → density/size fade + hard cut over water/paths.
      // Blender Y → runtime -Z: negate Z so the mask isn't sampled Z-mirrored
      // (matches the terrain ground material + the slabs sampling). worldXZ.y
      // is the world Z component.
      const maskUv = vec2(worldXZ.x, worldXZ.y.negate()).mul(invSpan).add(0.5);
      const maskG = this.mask ? texture(this.mask, maskUv).g : float(0.5);
      // Remap G[PRESENCE..FULL] → height[MIN_VISIBLE..1] so partial-mask land
      // fills with near-full blades, not stubble (see consts above). True-zero
      // land is culled below, so this only fattens up actual grass.
      const grassFactor = clamp(
        maskG.sub(GRASS_PRESENCE).div(GRASS_FULL_AT - GRASS_PRESENCE),
        0,
        1,
      )
        .mul(1 - GRASS_MIN_VISIBLE)
        .add(GRASS_MIN_VISIBLE);
      // Snow buries grass patch by patch (grass collects EARLY, bias +0.2):
      // shrink blades where snow has settled so they sink under the drift
      // instead of poking through, and carry the factor to the fragment.
      const grassSnow = snowGrowAt(worldXZ, 0.2).toVar();
      vSnow.assign(grassSnow);
      const size = sizeR.mul(grassFactor).mul(grassSnow.mul(-0.6).add(1));

      // Blade local → scaled → leaned → spun (all rooted at the base).
      let p = local.mul(size);
      p = rotX(p, tilt.x);
      p = rotZ(p, tilt.y);
      p = rotY(p, yaw);

      // Ground Y from the baked height texture.
      const hUv = worldXZ.sub(this.uTerrainMin).div(this.uTerrainSpan);
      const baseY = this.heightTex ? texture(this.heightTex, hUv).r : float(0);

      const world = vec3(
        worldXZ.x.add(p.x),
        baseY.add(p.y),
        worldXZ.y.add(p.z),
      ).toVar();

      // Wind — bend more toward the tip (blade_height weighted).
      const wind = this.wind.offsetNode(worldXZ).mul(hb).mul(0.6);
      world.x.addAssign(wind.x);
      world.z.addAssign(wind.y);

      // Player interaction. Walking uses a direct bend-away bubble. Running
      // swaps to a tighter, slower leg wake so it feels like a local disturbance
      // instead of a fast field-wide wave.
      const deltaToBlade = worldXZ.sub(this.uPlayerPos).toVar();
      const playerDist = length(deltaToBlade).toVar();
      const safeDist = max(playerDist, 0.001);
      const away = deltaToBlade.div(safeDist);
      const moveGate = clamp(this.uPlayerSpeed.div(1.8), 0, 1);
      const running = clamp(this.uPlayerRunning, 0, 1);
      const walking = running.oneMinus();
      const tip = hb.mul(hb);

      const walkBend = smoothstep(WALK_BEND_RADIUS, 0.08, playerDist)
        .mul(WALK_BEND_STRENGTH)
        .mul(moveGate)
        .mul(walking);
      const runEnv = smoothstep(RUN_RIPPLE_RADIUS, 0.12, playerDist)
        .mul(running)
        .mul(moveGate);
      const runWave = sin(
        playerDist.mul(9.0).sub(this.wind.nodes.time.mul(RUN_RIPPLE_SPEED)),
      );
      const runRipple = runWave.mul(runEnv).mul(RUN_RIPPLE_STRENGTH);
      const runDir = away.add(this.uPlayerDir.mul(0.35)).toVar();
      const push = away.mul(walkBend).add(runDir.mul(runRipple)).mul(tip);
      world.x.addAssign(push.x);
      world.z.addAssign(push.y);
      world.y.subAssign(
        tip.mul(walkBend.mul(0.055).add(abs(runRipple).mul(0.035))),
      );

      // Cull blades only where the mask is essentially zero (paths / water /
      // bare plazas) by lifting them out of view; anything with even faint grass
      // now keeps a full blade.
      world.y.addAssign(step(maskG, GRASS_CULL).mul(100.0));

      // View cull — the window wraps 360° around the player but only the
      // forward wedge is on-screen, so lift blades clearly BEHIND the camera
      // out of view. Roughly halves rendered blades with no visible change.
      const toCam = worldXZ.sub(this.uCameraPos).toVar();
      const camDist = max(length(toCam), 0.001);
      const viewDot = toCam.div(camDist).dot(this.uCameraDir);
      world.y.addAssign(step(viewDot, GRASS_VIEW_CULL).mul(100.0));

      vBladeH.assign(hb);
      vDry.assign(dry);
      return world;
    })();

    mat.normalNode = vec3(0, 1, 0);

    // Colour ramp lookup — piecewise-linear over the palette stops.
    const ramp = (t, stops) => {
      let c = color(stops[0][1]);
      for (let i = 1; i < stops.length; i++) {
        const f = clamp(
          t.sub(stops[i - 1][0]).div(stops[i][0] - stops[i - 1][0]),
          0,
          1,
        );
        c = mix(c, color(stops[i][1]), f);
      }
      return c;
    };
    const green = ramp(vBladeH, PALETTE_GREEN);
    const dryCol = ramp(vBladeH, PALETTE_DRY);
    const isDry = step(vDry, DRY_FRACTION); // 1 when this blade is dry
    const bladeCol = mix(green, dryCol, isDry).mul(this.tint);
    // Frost the remaining blade tops white where snow has settled (patchy).
    mat.colorNode = mix(bladeCol, SNOW_ALBEDO, vSnow.mul(0.85));

    this.material = mat;
  }

  #setMesh() {
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    this.mesh.name = "grass-field";
    this.mesh.frustumCulled = false;
    this.mesh.receiveShadow = true;
    this.mesh.castShadow = false;
    this.scene.add(this.mesh);
  }

  // ── Public API (matches the surface TimeOfDay / App expect) ─────────────────

  /** Recentre the grid on the player each frame. */
  setPlayerPos(pos, state = {}) {
    if (!pos) return;
    this.center.value.set(pos.x, pos.z);
    this.uPlayerPos.value.set(pos.x, pos.z);

    const vx = state.velocity?.x ?? 0;
    const vz = state.velocity?.z ?? 0;
    const speed = state.speed ?? Math.hypot(vx, vz);
    if (speed > 0.05) {
      this._lastMoveDir.set(vx, vz).normalize();
    }
    this.uPlayerDir.value.copy(this._lastMoveDir);
    this.uPlayerSpeed.value = speed;
    this.uPlayerRunning.value = state.running ? 1 : 0;

    // Camera XZ forward + position drive the view cull. Normalised in the XZ
    // plane (camera pitch is irrelevant to a horizontal behind/in-front test).
    if (state.camDir) {
      this.uCameraDir.value.set(state.camDir.x, state.camDir.z).normalize();
    }
    if (state.camPos) {
      this.uCameraPos.value.set(state.camPos.x, state.camPos.z);
    }
  }

  /**
   * Thin the rendered blade count to a fraction of the full field (1 = all,
   * 0.35 = ~a third). Cheap + reversible: it only lowers `geometry.instanceCount`
   * — a draw-count parameter, NOT a geometry rebuild or material/pipeline
   * recompile (which would invalidate WebGPU bind groups → black screen). The
   * instance buffer was spatially shuffled at build time, so the dropped blades
   * are a uniform sample and the field sparsens evenly. Used by the adaptive
   * perf-shed so weak hardware keeps a thinner grass field instead of a bare
   * terrain (we never hide it outright).
   */
  setDensityFactor(f) {
    if (!this.geometry) return;
    const k = Math.max(0, Math.min(this.count, Math.round(this.count * f)));
    this.geometry.instanceCount = k;
  }

  /** Day/night tint (TimeOfDay.applyInstant) — normalised against the day ref. */
  setColor(hex) {
    this.baseColor.set(hex);
    this.syncColor();
  }

  /** Push the live tint (baseColor / dayRef) into the GPU uniform. */
  syncColor() {
    const r = THREE.MathUtils.clamp(
      this.baseColor.r / Math.max(this._dayRef.r, 1e-3),
      0,
      1.5,
    );
    const g = THREE.MathUtils.clamp(
      this.baseColor.g / Math.max(this._dayRef.g, 1e-3),
      0,
      1.5,
    );
    const b = THREE.MathUtils.clamp(
      this.baseColor.b / Math.max(this._dayRef.b, 1e-3),
      0,
      1.5,
    );
    this.tint.value.set(r, g, b);
  }

  dispose() {
    this.scene.remove(this.mesh);
    this.geometry?.dispose();
    this.material?.dispose();
    this.heightTex?.dispose();
  }
}
