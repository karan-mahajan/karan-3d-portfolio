import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import {
  Fn, attribute, uniform, varying, vec3, vec4, float,
  positionGeometry, uv, sin, cos, length, smoothstep, mix, step, max,
  modelViewMatrix, cameraProjectionMatrix,
} from "three/tsl";

/**
 * "Like lights" — the visual home of the global like count. A soft cluster of
 * warm lights hangs high in the sky over the island; how many are lit IS the
 * like count (capped for perf), so the sky literally glows brighter the more
 * the place is loved. Liking releases a spark that rises from the player up into
 * the cluster and joins it.
 *
 * Deliberately NOT the ambient ground Fireflies (that's a separate night-only
 * system) — this is a sky constellation tied to a number, and reads as its own
 * thing rather than a copy of anyone else's pinned-light idea.
 *
 * WebGPU: billboarded instanced quads with TSL node materials (mirrors
 * Fireflies.js / ResumeBook motes); the bloom pass adds the halo.
 */

const MAX_SWARM = 200; // visible cap — the count keeps rising in the DB regardless
const RISE_SLOTS = 32; // ring buffer of in-flight "released" sparks
const RISE_DUR = 2.6; // seconds for a released spark to reach the cluster

// Cluster volume, high in the sky over the island centre.
const CLUSTER = { y: 36, rxz: 30, ry: 9 };
const SWARM_QUAD = 1.7; // world-size of each sky light
const RISE_QUAD = 0.55; // world-size of a rising spark

export class LikeLights {
  constructor(scene) {
    this.scene = scene;
    this._elapsed = 0;
    this._visible = 0;
    this._risePtr = 0;

    this.#buildSwarm();
    this.#buildRiseSparks();
  }

  // ── The sky cluster (count = number of lit quads) ───────────────────────────
  #buildSwarm() {
    const geo = this.#quadGeometry(MAX_SWARM);
    const bases = new Float32Array(MAX_SWARM * 3);
    const seeds = new Float32Array(MAX_SWARM * 3);
    for (let i = 0; i < MAX_SWARM; i++) {
      // Distribute through a flattened ellipsoid so the cluster reads as a soft
      // drift, not a hard ball. Earlier slots sit nearer the centre so the first
      // few likes form a tight core that spreads as the count grows.
      const a = Math.random() * Math.PI * 2;
      const r = Math.pow(Math.random(), 0.6) * CLUSTER.rxz;
      bases[i * 3] = Math.cos(a) * r;
      bases[i * 3 + 1] = CLUSTER.y + (Math.random() - 0.5) * 2 * CLUSTER.ry;
      bases[i * 3 + 2] = Math.sin(a) * r;
      seeds[i * 3] = Math.random() * Math.PI * 2;
      seeds[i * 3 + 1] = 0.18 + Math.random() * 0.4; // slow drift speed
      seeds[i * 3 + 2] = 0.6 + Math.random() * 1.4; // drift amplitude
    }
    geo.setAttribute("aBase", new THREE.InstancedBufferAttribute(bases, 3));
    geo.setAttribute("aSeed", new THREE.InstancedBufferAttribute(seeds, 3));
    geo.instanceCount = 0; // nothing lit until the like count loads
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, CLUSTER.y, 0), 1e6);

    const uTime = uniform(0);
    const uIntensity = uniform(0.9);
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const vTwinkle = varying(float(0), "vSwarmTwinkle");
    mat.vertexNode = Fn(() => {
      const base = attribute("aBase");
      const seed = attribute("aSeed");
      const phase = seed.x;
      const speed = seed.y;
      const amp = seed.z;
      const pos = base.toVar();
      pos.x.addAssign(sin(uTime.mul(speed).add(phase)).mul(amp));
      pos.y.addAssign(sin(uTime.mul(speed.mul(1.3)).add(phase.mul(2.0))).mul(amp.mul(0.4)));
      pos.z.addAssign(cos(uTime.mul(speed.mul(0.9)).add(phase.mul(1.5))).mul(amp));
      vTwinkle.assign(float(0.6).add(sin(uTime.mul(1.4).add(phase.mul(3.0))).mul(0.4)));
      const view = modelViewMatrix.mul(vec4(pos, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(SWARM_QUAD));
      return cameraProjectionMatrix.mul(view);
    })();
    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.66, 0.3), vec3(1.0, 0.94, 0.7), core).mul(uIntensity);
    mat.opacityNode = core.mul(vTwinkle).mul(uIntensity.clamp(0.0, 1.6));
    mat.uniforms = { uTime, uIntensity };

    this.swarm = new THREE.Mesh(geo, mat);
    this.swarm.name = "likeLights-swarm";
    this.swarm.frustumCulled = false;
    this.scene.add(this.swarm);
  }

  // ── Released sparks (player → cluster) ──────────────────────────────────────
  #buildRiseSparks() {
    const geo = this.#quadGeometry(RISE_SLOTS);
    this._riseStart = new Float32Array(RISE_SLOTS * 3);
    this._riseTarget = new Float32Array(RISE_SLOTS * 3);
    this._riseT0 = new Float32Array(RISE_SLOTS).fill(-1e3); // long-dead by default
    geo.setAttribute("aStart", (this._aStart = new THREE.InstancedBufferAttribute(this._riseStart, 3)));
    geo.setAttribute("aTarget", (this._aTarget = new THREE.InstancedBufferAttribute(this._riseTarget, 3)));
    geo.setAttribute("aT0", (this._aT0 = new THREE.InstancedBufferAttribute(this._riseT0, 1)));
    geo.instanceCount = RISE_SLOTS;
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, CLUSTER.y / 2, 0), 1e6);

    const uTime = uniform(0);
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const vGlow = varying(float(0), "vRiseGlow");
    mat.vertexNode = Fn(() => {
      const start = attribute("aStart");
      const target = attribute("aTarget");
      const t0 = attribute("aT0");
      const age = uTime.sub(t0);
      const tt = age.div(RISE_DUR).clamp(0.0, 1.0);
      // Ease-out so the spark leaps off the hand then settles into the cluster.
      const ease = float(1.0).sub(float(1.0).sub(tt).mul(float(1.0).sub(tt)));
      const pos = mix(start, target, ease).toVar();
      // Gentle sideways wander as it climbs.
      pos.x.addAssign(sin(age.mul(3.0).add(t0)).mul(0.6).mul(tt));
      // Alive only between t0 and t0+RISE_DUR.
      const alive = step(0.0, age).mul(step(age, float(RISE_DUR)));
      // Bright on release, fading as it arrives.
      vGlow.assign(alive.mul(float(1.3).sub(tt)).max(0.0));
      const view = modelViewMatrix.mul(vec4(pos, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(RISE_QUAD).mul(alive));
      return cameraProjectionMatrix.mul(view);
    })();
    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.7, 0.32), vec3(1.0, 0.97, 0.78), core).mul(max(vGlow, float(0.0)));
    mat.opacityNode = core.mul(max(vGlow, float(0.0)));
    mat.uniforms = { uTime };

    this.rise = new THREE.Mesh(geo, mat);
    this.rise.name = "likeLights-rise";
    this.rise.frustumCulled = false;
    this.scene.add(this.rise);
  }

  #quadGeometry(count) {
    const base = new THREE.BufferGeometry();
    base.setAttribute("position", new THREE.BufferAttribute(new Float32Array([
      -0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0,
    ]), 3));
    base.setAttribute("uv", new THREE.BufferAttribute(new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]), 2));
    base.setIndex([0, 1, 2, 0, 2, 3]);
    const geo = new THREE.InstancedBufferGeometry();
    geo.setAttribute("position", base.attributes.position);
    geo.setAttribute("uv", base.attributes.uv);
    geo.setIndex(base.index);
    geo.instanceCount = count;
    return geo;
  }

  // ── Public API ───────────────────────────────────────────────────────────────

  /** Light `n` of the sky cluster (the global like count). */
  setCount(n) {
    this._visible = Math.max(0, Math.min(MAX_SWARM, Math.floor(n || 0)));
    if (this.swarm) this.swarm.geometry.instanceCount = this._visible;
  }

  /** Release a spark from `worldPos` that rises into the cluster. */
  release(worldPos) {
    const slot = this._risePtr % RISE_SLOTS;
    this._risePtr++;
    const s = slot * 3;
    this._riseStart[s] = worldPos.x;
    this._riseStart[s + 1] = worldPos.y + 1.2; // from about head height
    this._riseStart[s + 2] = worldPos.z;
    // Aim at a random spot inside the cluster.
    const a = Math.random() * Math.PI * 2;
    const r = Math.pow(Math.random(), 0.6) * CLUSTER.rxz;
    this._riseTarget[s] = Math.cos(a) * r;
    this._riseTarget[s + 1] = CLUSTER.y + (Math.random() - 0.5) * 2 * CLUSTER.ry;
    this._riseTarget[s + 2] = Math.sin(a) * r;
    this._riseT0[slot] = this._elapsed;
    this._aStart.needsUpdate = true;
    this._aTarget.needsUpdate = true;
    this._aT0.needsUpdate = true;
  }

  /** nightFactor 0..1 — the cluster reads brighter against a dark sky. */
  setNightFactor(n) {
    if (this.swarm) {
      this.swarm.material.uniforms.uIntensity.value = 0.6 + (n || 0) * 0.8;
    }
  }

  update(elapsed) {
    this._elapsed = elapsed;
    if (this.swarm) this.swarm.material.uniforms.uTime.value = elapsed;
    if (this.rise) this.rise.material.uniforms.uTime.value = elapsed;
  }
}
