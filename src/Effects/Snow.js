import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import {
  Fn, attribute, varying, float, vec4,
  positionLocal, uv, modelViewMatrix, cameraProjectionMatrix, smoothstep,
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

    const mat = new MeshBasicNodeMaterial({ transparent: true, depthWrite: false });
    const vFade = varying(float(0), "vSnowFade");
    mat.vertexNode = Fn(() => {
      const center = modelViewMatrix.mul(vec4(attribute("aOffset"), 1.0)).toVar();
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

    // Show fewer flakes when snowfall is light (cheaper), all of them in a storm.
    this.mesh.geometry.instanceCount = Math.max(
      1,
      Math.floor(this.count * Math.min(1, intensity)),
    );

    const cx = this.camera.position.x;
    const cz = this.camera.position.z;
    this.mesh.position.set(cx, 0, cz);

    const t = this._time;
    const active = this.mesh.geometry.instanceCount;
    for (let i = 0; i < active; i++) {
      const i3 = i * 3;
      this.offsets[i3 + 1] -= this.speeds[i] * BASE_FALL * delta;
      // Lateral sway so flakes wander rather than fall in straight lines.
      const ph = this.phases[i];
      this.offsets[i3] += Math.sin(t * 0.8 + ph) * 0.35 * delta;
      this.offsets[i3 + 2] += Math.cos(t * 0.6 + ph) * 0.3 * delta;
      if (this.offsets[i3 + 1] < 0) {
        this.offsets[i3] = (Math.random() - 0.5) * AREA * 2;
        this.offsets[i3 + 1] = SPAWN_HEIGHT;
        this.offsets[i3 + 2] = (Math.random() - 0.5) * AREA * 2;
      }
    }
    this.mesh.geometry.attributes.aOffset.needsUpdate = true;
  }

  dispose() {
    this.mesh?.geometry?.dispose();
    this.mesh?.material?.dispose();
    this.group?.removeFromParent();
  }
}
