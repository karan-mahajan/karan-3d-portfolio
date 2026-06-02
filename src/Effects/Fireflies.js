import * as THREE from 'three/webgpu';
import { MeshBasicNodeMaterial } from 'three/webgpu';
import {
  Fn, attribute, uniform, varying, vec3, vec4, float,
  positionGeometry, uv, sin, cos, length, smoothstep, mix,
  modelViewMatrix, cameraProjectionMatrix,
} from 'three/tsl';

/**
 * Drifting emissive points. Each firefly has its own seed and orbits a base
 * position with random sinusoidal motion. A soft round disc with a warm-amber
 * tint is painted per fragment; the bloom pass adds the glow halo.
 *
 * B0/WebGPU: WebGPU renders `THREE.Points` as 1-pixel PointList primitives
 * (no point size — verified in WebGPUUtils.getPrimitiveTopology), so the old
 * GLSL `gl_PointSize` sprite cloud can't survive the backend. Re-authored as
 * INSTANCED BILLBOARDED QUADS: one tiny quad per firefly, billboarded in
 * `material.vertexNode` by adding the quad corner offset in VIEW space (a fixed
 * world-size billboard, which naturally gives perspective attenuation). The
 * orbit motion, twinkle and warm-disc shading are TSL node graphs driven by
 * `uTime` + `uIntensity` uniforms; TimeOfDay mutates
 * `material.uniforms.uIntensity.value` exactly as it did with the old GLSL
 * uniform (re-exposed under the legacy `.uniforms` shape, like Sky.js).
 */

const DEFAULT_COUNT = 144;
const SPREAD = 60;          // half-extent of the firefly spawn box
const HEIGHT_BAND = [0.6, 3.0];
const QUAD_WORLD_SIZE = 0.36; // world-space quad extent → soft disc

export class Fireflies {
  constructor(scene, { count = DEFAULT_COUNT } = {}) {
    this.scene = scene;
    this.count = Math.max(0, Math.floor(count));

    // Base quad — corners in [-0.5, 0.5], with uv for the radial disc.
    const baseGeom = new THREE.BufferGeometry();
    const verts = new Float32Array([
      -0.5, -0.5, 0,
       0.5, -0.5, 0,
       0.5,  0.5, 0,
      -0.5,  0.5, 0,
    ]);
    const uvs = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    baseGeom.setAttribute('position', new THREE.BufferAttribute(verts, 3));
    baseGeom.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    this.geometry = new THREE.InstancedBufferGeometry();
    this.geometry.setAttribute('position', baseGeom.attributes.position);
    this.geometry.setAttribute('uv', baseGeom.attributes.uv);
    this.geometry.setIndex(baseGeom.index);
    this.geometry.instanceCount = this.count;

    const bases = new Float32Array(this.count * 3);
    const seeds = new Float32Array(this.count * 3);
    for (let i = 0; i < this.count; i++) {
      const x = (Math.random() - 0.5) * SPREAD;
      const y = HEIGHT_BAND[0] + Math.random() * (HEIGHT_BAND[1] - HEIGHT_BAND[0]);
      const z = (Math.random() - 0.5) * SPREAD;
      bases[i * 3] = x;
      bases[i * 3 + 1] = y;
      bases[i * 3 + 2] = z;
      seeds[i * 3] = Math.random() * Math.PI * 2;       // phase
      seeds[i * 3 + 1] = 0.4 + Math.random() * 0.8;     // speed
      seeds[i * 3 + 2] = 0.3 + Math.random() * 0.8;     // amplitude
    }
    this.geometry.setAttribute('aBase', new THREE.InstancedBufferAttribute(bases, 3));
    this.geometry.setAttribute('aSeed', new THREE.InstancedBufferAttribute(seeds, 3));
    // Player-following volume — never frustum-cull the whole cloud.
    this.geometry.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const uTime = uniform(0);
    // 1.0 = day baseline. TimeOfDay lerps this up at night so the swarm
    // reads as more prominent against the dark sky.
    const uIntensity = uniform(1.0);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    const vTwinkle = varying(float(0), 'vFireflyTwinkle');

    mat.vertexNode = Fn(() => {
      const base = attribute('aBase');
      const seed = attribute('aSeed');
      const phase = seed.x;
      const speed = seed.y;
      const amp = seed.z;

      // Each firefly bobs in its own little orbit so the swarm feels alive.
      const pos = base.toVar();
      pos.x.addAssign(sin(uTime.mul(speed).add(phase)).mul(amp));
      pos.y.addAssign(sin(uTime.mul(speed.mul(1.3)).add(phase.mul(2.0))).mul(amp.mul(0.4)));
      pos.z.addAssign(cos(uTime.mul(speed.mul(0.9)).add(phase.mul(1.5))).mul(amp));

      // Twinkle: fade in/out at slightly different rates per firefly.
      vTwinkle.assign(float(0.55).add(sin(uTime.mul(2.0).add(phase.mul(4.0))).mul(0.45)));

      // Billboard: offset the quad corner in VIEW space so the disc always
      // faces the camera; constant world size gives perspective attenuation.
      const view = modelViewMatrix.mul(vec4(pos, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(QUAD_WORLD_SIZE));
      return cameraProjectionMatrix.mul(view);
    })();

    // Soft round disc, warm core → amber edge, scaled by intensity.
    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    const discColor = mix(vec3(1.0, 0.65, 0.25), vec3(1.0, 0.92, 0.62), core);
    mat.colorNode = discColor.mul(uIntensity);
    mat.opacityNode = core.mul(vTwinkle).mul(uIntensity.clamp(0.0, 1.5));

    this.material = mat;
    // Re-expose the live uniforms under the legacy `.uniforms` shape so
    // TimeOfDay can keep mutating `.value` in place (and gsap can tween it).
    this.material.uniforms = { uTime, uIntensity };

    // Kept named `points` for API parity with the old THREE.Points cloud.
    this.points = new THREE.Mesh(this.geometry, mat);
    this.points.name = 'fireflies';
    this.points.frustumCulled = false;
    scene.add(this.points);
  }

  update(elapsed) {
    this.material.uniforms.uTime.value = elapsed;
    // Skip the entire draw when fully faded — day mode sets uIntensity to 0.
    this.points.visible = this.material.uniforms.uIntensity.value > 0.001;
  }
}
