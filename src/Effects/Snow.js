import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import {
  Fn, attribute, varying, float, vec3, vec4,
  positionLocal, uv, modelViewMatrix, cameraProjectionMatrix, smoothstep,
  sin, cos, uniform,
} from "three/tsl";
import { snowFall } from "../World/SnowState.js";

/**
 * Falling snow — instanced camera-facing quads inside a box that follows the
 * camera. Each flake is a soft circular sprite (alpha falloff in the fragment
 * node), drifting down with a gentle sway. Intensity is driven entirely by the
 * shared `snowFall` uniform: WeatherDirector ramps it 0→1, which scales both
 * the visible instance count (cheaper when light) and the opacity.
 *
 * No splash/ground layer — accumulation is handled separately by the snow
 * material term on the terrain + props (see SnowState.js). This class is purely
 * the precipitation in the air.
 */

const AREA = 46; // half-extent of the flake volume around the camera
const SPAWN_HEIGHT = 32;
const BASE_FALL = 1.3; // units/sec at flake speed 1 — slow, snow-like

export class Snow {
  constructor(scene, camera, { count = 2000 } = {}) {
    this.scene = scene;
    this.camera = camera;
    this.count = Math.max(200, Math.floor(count));
    this.group = new THREE.Group();
    this.group.name = "snow";
    scene.add(this.group);
    this._time = 0;
    this.#build();
  }

  #build() {
    // Unit quad centred on origin, expanded in view space per-instance.
    const quad = new THREE.BufferGeometry();
    // prettier-ignore
    const verts = new Float32Array([
      -0.5, -0.5, 0,  0.5, -0.5, 0,  0.5, 0.5, 0,
      -0.5, -0.5, 0,  0.5, 0.5, 0,  -0.5, 0.5, 0,
    ]);
    // prettier-ignore
    const uvs = new Float32Array([0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1]);
    quad.setAttribute("position", new THREE.BufferAttribute(verts, 3));
    quad.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));

    const geom = new THREE.InstancedBufferGeometry();
    geom.setAttribute("position", quad.attributes.position);
    geom.setAttribute("uv", quad.attributes.uv);
    geom.setIndex(null);
    geom.instanceCount = this.count;

    this.offsets = new Float32Array(this.count * 3);
    this.speeds = new Float32Array(this.count);
    this.sizes = new Float32Array(this.count);
    this.phases = new Float32Array(this.count);
    for (let i = 0; i < this.count; i++) {
      this.offsets[i * 3] = (Math.random() - 0.5) * AREA * 2;
      this.offsets[i * 3 + 1] = Math.random() * SPAWN_HEIGHT;
      this.offsets[i * 3 + 2] = (Math.random() - 0.5) * AREA * 2;
      this.speeds[i] = 0.7 + Math.random() * 0.9;
      this.sizes[i] = 0.05 + Math.random() * 0.07;
      this.phases[i] = Math.random() * Math.PI * 2;
    }
    geom.setAttribute("aOffset", new THREE.InstancedBufferAttribute(this.offsets, 3));
    geom.setAttribute("aSize", new THREE.InstancedBufferAttribute(this.sizes, 1));
    geom.setAttribute("aSpeed", new THREE.InstancedBufferAttribute(this.speeds, 1));
    geom.setAttribute("aPhase", new THREE.InstancedBufferAttribute(this.phases, 1));

    const mat = new MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
    const vFade = varying(float(0), "vSnowFade");
    // Time-driven on the GPU: the old CPU per-flake fall+sway loop + full
    // aOffset re-upload (2000 instances every frame) is gone. The vertex node
    // derives each flake's live position analytically from its seed
    // (aOffset = spawn x/y/z), aSpeed, aPhase and a single uTime uniform —
    // matching Fireflies' pattern. `aOffset` is now an immutable seed buffer.
    this.uTime = uniform(0);
    const H = float(SPAWN_HEIGHT);
    mat.vertexNode = Fn(() => {
      const seed = attribute("aOffset"); // spawn x/y/z
      const speed = attribute("aSpeed");
      const phase = attribute("aPhase");
      // Fall wraps in [0, H]: y0 sets the start so flakes desync; the modulo
      // recycles to the top exactly as the old `y < 0 → y = SPAWN_HEIGHT` did.
      const fallPhase = H.sub(seed.y);
      const progressed = fallPhase.add(this.uTime.mul(speed).mul(BASE_FALL)).mod(H);
      const y = H.sub(progressed);
      // Gentle bounded lateral wander (no wind) — direct sinusoid replaces the
      // CPU-integrated drift; same look, fully analytic.
      const x = seed.x.add(sin(this.uTime.mul(0.8).add(phase)).mul(0.44));
      const z = seed.z.add(cos(this.uTime.mul(0.6).add(phase)).mul(0.5));
      const center = modelViewMatrix.mul(vec4(vec3(x, y, z), 1.0)).toVar();
      // Billboard: expand the quad in view space so it always faces the camera.
      center.xy.addAssign(positionLocal.xy.mul(attribute("aSize")));
      // Fade distant flakes so the far volume doesn't read as static fog.
      vFade.assign(center.z.negate().div(55.0).oneMinus().clamp(0.0, 1.0));
      return cameraProjectionMatrix.mul(center);
    })();
    mat.colorNode = vec4(0.95, 0.97, 1.0, 1.0);
    // Soft round sprite × distance fade × global snowfall intensity.
    const d = uv().sub(0.5).length();
    mat.opacityNode = smoothstep(0.5, 0.12, d).mul(vFade).mul(snowFall);

    this.mesh = new THREE.Mesh(geom, mat);
    this.mesh.frustumCulled = false;
    this.mesh.renderOrder = 5;
    this.group.add(this.mesh);
  }

  update(delta) {
    const intensity = snowFall.value;
    if (intensity <= 0.001) {
      if (this.mesh.visible) this.mesh.visible = false;
      return;
    }
    this.mesh.visible = true;
    this._time += delta;
    this.uTime.value = this._time;

    // Show fewer flakes when snowfall is light (cheaper), all of them in a storm.
    this.mesh.geometry.instanceCount = Math.max(
      1,
      Math.floor(this.count * Math.min(1, intensity)),
    );

    // Keep the flake volume centred on the camera so it always covers the player.
    this.mesh.position.set(this.camera.position.x, 0, this.camera.position.z);
  }

  dispose() {
    this.mesh?.geometry?.dispose();
    this.mesh?.material?.dispose();
    this.group?.removeFromParent();
  }
}
