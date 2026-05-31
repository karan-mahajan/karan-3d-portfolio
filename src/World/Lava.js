import * as THREE from 'three/webgpu';
import { MeshStandardNodeMaterial, MeshBasicNodeMaterial } from 'three/webgpu';
import {
  Fn, uniform, varying, vec2, vec3, vec4, float, attribute, uv,
  positionGeometry, positionWorld, modelViewMatrix, cameraProjectionMatrix,
  sin, cos, length, smoothstep, fract, mix, max,
} from 'three/tsl';

/**
 * Phase F lava pool — animates the Blender-authored `lavaSurface_pool` /
 * `lavaSurface_core` meshes (named in lavaRef_pool.extras) and spawns rising
 * ember billboards above the pool.
 *
 * The two surface meshes load with their baked node materials; here they're
 * replaced with emissive MeshStandardNodeMaterials whose glow scrolls along the
 * authored flow direction and pulses, so the lava reads as molten + flowing and
 * the bloom pass picks up the bright emissive. Embers are GPU-looping instanced
 * billboards (no per-frame CPU) drifting in the shared Wind — same billboard
 * technique as the stars/fireflies.
 *
 * Everything is driven by a single `uTime` uniform advanced each frame (the
 * proven pattern across Grass/Water/TimeOfDay — avoids relying on a TSL clock
 * node).
 */

const EMBER_LIFE = 2.6;     // seconds per ember rise loop
const EMBER_RISE = 3.4;     // how high an ember climbs (m)
const EMBER_SIZE = 0.13;    // billboard world size

export class Lava {
  /**
   * @param {THREE.Scene} scene
   * @param {import('./Wind.js').Wind} wind
   * @param {{ byName: Map<string, any> }} refs
   */
  constructor(scene, wind, refs) {
    this.scene = scene;
    this.wind = wind;
    this.uTime = uniform(0);
    this.embers = null;

    const ref = refs?.byName?.get('lavaRef_pool');
    if (!ref) return;
    const ex = ref.extras ?? ref.object3d?.userData ?? {};
    const p = ref.position ?? ref.object3d?.position ?? { x: 0, y: 0, z: 0 };

    const surfaceName = ex.surfaceObject ?? 'lavaSurface_pool';
    const coreName = ex.coreObject ?? 'lavaSurface_core';
    const glow = ex.glowStrength ?? 2.6;
    const pulse = ex.pulseSpeed ?? 0.6;
    const flow = ex.flowDir ?? [1, 0];
    const radius = ex.radius ?? 3;
    const emberRate = ex.emberRate ?? 12;

    // Pool surface — deeper red, broad slow glow.
    this.#styleSurface(surfaceName, {
      cool: new THREE.Color(0.55, 0.02, 0.01),
      hot: new THREE.Color(1.0, 0.18, 0.03),
      glow,
      pulse,
      flow,
      freq: 0.55,
    });
    // Core — brighter, faster pulse so the centre churns.
    this.#styleSurface(coreName, {
      cool: new THREE.Color(0.9, 0.12, 0.02),
      hot: new THREE.Color(1.0, 0.45, 0.08),
      glow: glow * 1.3,
      pulse: pulse * 1.8,
      flow,
      freq: 0.9,
    });

    // Embers anchored at the pool surface world position.
    const baseY = (this.scene.getObjectByName(surfaceName)
      ? this.#worldY(surfaceName, p.y)
      : p.y) + 0.1;
    this.#buildEmbers(p.x, baseY, p.z, radius, Math.max(8, Math.round(emberRate * EMBER_LIFE)));
  }

  #worldY(name, fallback) {
    const o = this.scene.getObjectByName(name);
    if (!o) return fallback;
    const v = new THREE.Vector3();
    o.getWorldPosition(v);
    return v.y;
  }

  // ── Animated emissive surface (replaces the baked GLB material) ─────────────
  #styleSurface(name, opts) {
    const mesh = this.scene.getObjectByName(name);
    if (!mesh || !mesh.isMesh) return;

    const cool = uniform(vec3(opts.cool.r, opts.cool.g, opts.cool.b));
    const hot = uniform(vec3(opts.hot.r, opts.hot.g, opts.hot.b));
    const uGlow = float(opts.glow);
    const uPulse = float(opts.pulse);
    const uFreq = float(opts.freq);
    const fdir = vec2(opts.flow[0], opts.flow[1]);
    const t = this.uTime;

    // Scrolling heat field over world XZ along the flow direction → molten look.
    const heatNode = Fn(() => {
      const flow = fdir.mul(t.mul(0.18));
      const p = positionWorld.xz.mul(uFreq).add(flow);
      const n = sin(p.x.add(t.mul(0.7))).mul(sin(p.y.sub(t.mul(0.5))));
      const ripple = sin(length(positionWorld.xz).mul(2.0).sub(t.mul(1.3)));
      return n.mul(0.5).add(0.5).mul(0.8).add(ripple.mul(0.1)).add(0.1);
    });

    const mat = new MeshStandardNodeMaterial({ metalness: 0, roughness: 0.55 });
    const heat = heatNode();
    const baseCol = mix(cool, hot, heat);
    mat.colorNode = baseCol.mul(0.35);  // darker albedo; emissive carries the glow
    const pulseAmt = sin(t.mul(uPulse)).mul(0.18).add(0.9);
    mat.emissiveNode = baseCol.mul(uGlow).mul(pulseAmt);

    mesh.material = mat;
    mesh.castShadow = false;
    mesh.receiveShadow = false;
  }

  // ── GPU ember billboards (looping rise, wind drift, additive) ───────────────
  #buildEmbers(cx, cy, cz, radius, count) {
    const seeds = new Float32Array(count);
    const angles = new Float32Array(count);
    const radii = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      seeds[i] = i / count;                       // even phase spread
      angles[i] = Math.random() * Math.PI * 2;
      radii[i] = Math.sqrt(Math.random()) * radius * 0.85;
    }

    const baseGeom = new THREE.BufferGeometry();
    const quad = new Float32Array([-0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0]);
    const quadUv = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    baseGeom.setAttribute('position', new THREE.BufferAttribute(quad, 3));
    baseGeom.setAttribute('uv', new THREE.BufferAttribute(quadUv, 2));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    const geom = new THREE.InstancedBufferGeometry();
    geom.setAttribute('position', baseGeom.attributes.position);
    geom.setAttribute('uv', baseGeom.attributes.uv);
    geom.setIndex(baseGeom.index);
    geom.instanceCount = count;
    geom.setAttribute('aSeed', new THREE.InstancedBufferAttribute(seeds, 1));
    geom.setAttribute('aAngle', new THREE.InstancedBufferAttribute(angles, 1));
    geom.setAttribute('aRadius', new THREE.InstancedBufferAttribute(radii, 1));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(cx, cy, cz), 1e6);

    const t = this.uTime;
    const wind = this.wind;
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    });

    // varying: per-instance fade carried vertex → fragment.
    const vFade = varying(float(0), 'vEmberFade');
    mat.vertexNode = Fn(() => {
      const seed = attribute('aSeed');
      const ang = attribute('aAngle');
      const rad = attribute('aRadius');
      const phase = fract(t.div(EMBER_LIFE).add(seed));          // 0..1 loop
      const fade = phase.oneMinus().mul(smoothstep(0, 0.12, phase));
      vFade.assign(fade);

      const bx = float(cx).add(cos(ang).mul(rad));
      const bz = float(cz).add(sin(ang).mul(rad));
      const drift = wind.offsetNode(vec2(bx, bz)).mul(0.6).mul(phase);
      const world = vec3(bx.add(drift.x), float(cy).add(phase.mul(EMBER_RISE)), bz.add(drift.y));

      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      const size = float(EMBER_SIZE).mul(fade.mul(0.6).add(0.4));
      view.xy.addAssign(positionGeometry.xy.mul(size));
      return cameraProjectionMatrix.mul(view);
    })();

    const disc = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    // Hot core cooling to deep orange as it climbs (reuse the fade as a proxy).
    mat.colorNode = mix(vec3(1.0, 0.35, 0.05), vec3(1.0, 0.8, 0.3), vFade);
    mat.opacityNode = disc.mul(vFade);

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = 'lava:embers';
    mesh.frustumCulled = false;
    mesh.renderOrder = 6;
    this.scene.add(mesh);
    this.embers = { mesh, geom, mat };
  }

  update(elapsed) {
    this.uTime.value = elapsed;
  }

  dispose() {
    if (this.embers) {
      this.scene.remove(this.embers.mesh);
      this.embers.geom?.dispose();
      this.embers.mat?.dispose();
      this.embers = null;
    }
  }
}
