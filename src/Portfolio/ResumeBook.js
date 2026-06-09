import gsap from "gsap";
import {
  Fn,
  attribute,
  cameraProjectionMatrix,
  cos,
  float,
  length,
  mix,
  modelViewMatrix,
  positionGeometry,
  sin,
  smoothstep,
  uniform,
  uv,
  varying,
  vec3,
  vec4,
} from "three/tsl";
import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial, MeshStandardNodeMaterial } from "three/webgpu";

/**
 * The floating magical resume book.
 *
 * Phase 1 (this file) is the in-world PROP only: a dark-leather + gold-trim
 * book that hovers in the air, leaks warm light, throws a tall glowing light
 * shaft skyward as a "come here" beacon, drifts a few motes around itself and
 * bobs/spins on idle. The open/close cinematic, two-page reading view and
 * page-flip land in later phases — the front cover is already built on a spine
 * pivot (`#coverPivot`) so Phase 2 can swing it open without re-modelling.
 *
 * WebGPU note: the renderer is WebGPURenderer, so all custom shading is TSL
 * node materials (mirrors Fireflies.js); `onBeforeCompile` GLSL patches no-op
 * on this backend. Lit surfaces use MeshStandardNodeMaterial (plain .color /
 * .emissive props), additive glow uses MeshBasicNodeMaterial with node graphs.
 */

// Book dimensions (metres), lying flat — thickness runs along local +Y, the
// covers are the broad faces, the spine binds the -Z edge.
const W = 0.64; // width  (local X)
const D = 0.82; // page depth/height (local Z)
const CT = 0.045; // cover thickness
const PT = 0.13; // page-block thickness
const TOTAL_THK = PT + 2 * CT;
const COVER_Y = PT / 2 + CT / 2; // ± offset of each cover from centre

const HOVER_HEIGHT = 1.5; // book centre height above the ground
const BOB_AMP = 0.08; // idle vertical bob
const SPIN_SPEED = 0.22; // idle yaw spin (rad/s)

const BEACON_HEIGHT = 6.0; // light-shaft length
const MOTE_COUNT = 28;

const DEFAULT_PROXIMITY = 4.0; // prompt radius (XZ)

export class ResumeBook {
  /**
   * @param {object}   opts
   * @param {THREE.Scene} opts.scene
   * @param {object}   opts.terrain  — exposes heightAt(x, z)
   * @param {object}   opts.physics  — exposes addStaticCylinder(...)
   * @param {number}   opts.x        — world X
   * @param {number}   opts.z        — world Z
   */
  constructor({ scene, terrain, physics, x = -22, z = -20 }) {
    this.scene = scene;
    this.terrain = terrain;
    this.physics = physics;

    const groundY = terrain?.heightAt ? terrain.heightAt(x, z) : 0;
    this.baseX = x;
    this.baseZ = z;
    this.hoverY = groundY + HOVER_HEIGHT;

    this.proximity = DEFAULT_PROXIMITY;

    // Idle ↔ focused animation state.
    this._last = null; // last elapsed (for dt)
    this._yaw = 0; // integrated spin so focus/idle hand off smoothly
    this._bob = 1; // bob amplitude scalar (eased to 0 while focused)
    this._glow = 1; // emissive/light multiplier (bloom on open)
    this._beacon = 1; // beacon opacity multiplier (dimmed while reading)
    this._focused = false;
    this._targetYaw = null; // yaw that faces the reader while focused

    // Root that bobs + spins. Beacon, motes and glow disc ride along so the
    // whole artifact reads as one floating object.
    this.group = new THREE.Group();
    this.group.name = "resumeBook";
    this.group.position.set(x, this.hoverY, z);
    scene.add(this.group);

    this.#buildBook();
    this.#buildBeacon();
    this.#buildGlowDisc();
    this.#buildMotes();
    this.#buildLight();
    this.#addCollider();
  }

  /** World position of the book centre (XZ stable; Y at mean hover height). */
  get position() {
    return new THREE.Vector3(this.baseX, this.hoverY, this.baseZ);
  }

  /** True-ish when the player is within `radius` (XZ) of the book. */
  near(playerPosition, radius = this.proximity) {
    const dx = playerPosition.x - this.baseX;
    const dz = playerPosition.z - this.baseZ;
    if (dx * dx + dz * dz <= radius * radius) {
      return { kind: "resume", position: this.position };
    }
    return null;
  }

  // ── Geometry ──────────────────────────────────────────────────────────────

  #buildBook() {
    const leather = new MeshStandardNodeMaterial({
      color: new THREE.Color(0x4a1c24), // dark burgundy leather
      roughness: 0.55,
      metalness: 0.0,
    });
    const spineMat = new MeshStandardNodeMaterial({
      color: new THREE.Color(0x35141a),
      roughness: 0.6,
      metalness: 0.0,
    });
    const gold = new MeshStandardNodeMaterial({
      color: new THREE.Color(0xd9a441),
      roughness: 0.3,
      metalness: 0.9,
      emissive: new THREE.Color(0x4a3410),
      emissiveIntensity: 0.4,
    });
    // Warm parchment — emissive so the page edges read as "lit from within".
    const parchment = new MeshStandardNodeMaterial({
      color: new THREE.Color(0xe8d8a8),
      roughness: 0.85,
      metalness: 0.0,
      emissive: new THREE.Color(0xc8932f),
      emissiveIntensity: 0.55,
    });
    this.parchment = parchment; // glow target for the open-bloom
    this._parchmentEmissive = 0.55;

    // Page block (centre).
    const pages = new THREE.Mesh(
      new THREE.BoxGeometry(W * 0.92, PT, D * 0.94),
      parchment,
    );
    this.group.add(pages);

    // Back cover (static).
    const back = new THREE.Mesh(new THREE.BoxGeometry(W, CT, D), leather);
    back.position.y = -COVER_Y;
    this.group.add(back);

    // Spine binding along the -Z edge, full thickness.
    const spine = new THREE.Mesh(
      new THREE.BoxGeometry(W, TOTAL_THK, CT),
      spineMat,
    );
    spine.position.set(0, 0, -D / 2 + CT / 2);
    this.group.add(spine);

    // Front cover on a hinge pivot at the spine edge so Phase 2 can rotate
    // `#coverPivot.rotation.x` to swing it open. Closed = rotation 0.
    this.coverPivot = new THREE.Group();
    this.coverPivot.position.set(0, COVER_Y, -D / 2);
    this.group.add(this.coverPivot);

    const front = new THREE.Mesh(new THREE.BoxGeometry(W, CT, D), leather);
    front.position.set(0, 0, D / 2);
    this.coverPivot.add(front);

    // Gold rim peeking around the front cover (slightly larger, thinner).
    const rim = new THREE.Mesh(
      new THREE.BoxGeometry(W + 0.04, CT * 0.6, D + 0.04),
      gold,
    );
    rim.position.set(0, -CT * 0.25, D / 2);
    this.coverPivot.add(rim);

    // Embossed gold emblem on the cover face.
    const emblem = new THREE.Mesh(
      new THREE.CylinderGeometry(0.1, 0.1, CT * 1.2, 24),
      gold,
    );
    emblem.position.set(0, CT * 0.6, D / 2);
    this.coverPivot.add(emblem);
  }

  // ── Beacon: vertical light shaft (the "come here" marker) ──────────────────

  #buildBeacon() {
    const uTime = uniform(0);
    const uBeacon = uniform(1); // dimmed while the book is open for reading
    const geo = new THREE.CylinderGeometry(
      0.5,
      0.16,
      BEACON_HEIGHT,
      28,
      1,
      true,
    );
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });

    const v = uv().y; // 0 at base → 1 at top
    const pulse = float(0.7).add(sin(uTime.mul(1.6)).mul(0.16));
    // Bright near the book, fading out toward the sky; soft cut at the very base.
    const fade = v
      .oneMinus()
      .pow(1.7)
      .mul(smoothstep(0.0, 0.05, v));
    mat.colorNode = mix(
      vec3(1.0, 0.78, 0.42),
      vec3(1.0, 0.96, 0.82),
      v.oneMinus(),
    );
    mat.opacityNode = fade.mul(pulse).mul(0.55).mul(uBeacon);
    mat.uniforms = { uTime, uBeacon };

    const beacon = new THREE.Mesh(geo, mat);
    beacon.position.y = BEACON_HEIGHT / 2 + 0.05; // base sits at the book
    beacon.frustumCulled = false;
    this.beacon = beacon;
    this.group.add(beacon);
  }

  // ── Soft ground glow halo under the book ───────────────────────────────────

  #buildGlowDisc() {
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    });
    const d = length(uv().sub(0.5));
    mat.colorNode = vec3(1.0, 0.74, 0.38);
    mat.opacityNode = smoothstep(0.5, 0.05, d).mul(0.4);

    const disc = new THREE.Mesh(new THREE.CircleGeometry(1.3, 40), mat);
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = -COVER_Y - 0.18;
    disc.frustumCulled = false;
    this.group.add(disc);
  }

  // ── Drifting golden motes around the book (mini-Fireflies) ─────────────────

  #buildMotes() {
    const baseGeom = new THREE.BufferGeometry();
    const verts = new Float32Array([
      -0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0,
    ]);
    const uvs = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    baseGeom.setAttribute("position", new THREE.BufferAttribute(verts, 3));
    baseGeom.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    const geo = new THREE.InstancedBufferGeometry();
    geo.setAttribute("position", baseGeom.attributes.position);
    geo.setAttribute("uv", baseGeom.attributes.uv);
    geo.setIndex(baseGeom.index);
    geo.instanceCount = MOTE_COUNT;

    const bases = new Float32Array(MOTE_COUNT * 3);
    const seeds = new Float32Array(MOTE_COUNT * 3);
    for (let i = 0; i < MOTE_COUNT; i++) {
      // Flattened cloud hugging the book.
      const a = Math.random() * Math.PI * 2;
      const r = 0.25 + Math.random() * 0.6;
      bases[i * 3] = Math.cos(a) * r;
      bases[i * 3 + 1] = -0.1 + Math.random() * 0.7;
      bases[i * 3 + 2] = Math.sin(a) * r;
      seeds[i * 3] = Math.random() * Math.PI * 2; // phase
      seeds[i * 3 + 1] = 0.4 + Math.random() * 0.7; // speed
      seeds[i * 3 + 2] = 0.06 + Math.random() * 0.16; // amplitude
    }
    geo.setAttribute("aBase", new THREE.InstancedBufferAttribute(bases, 3));
    geo.setAttribute("aSeed", new THREE.InstancedBufferAttribute(seeds, 3));
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 4);

    const uTime = uniform(0);
    const quadSize = 0.08;
    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const vTwinkle = varying(float(0), "vMoteTwinkle");

    mat.vertexNode = Fn(() => {
      const base = attribute("aBase");
      const seed = attribute("aSeed");
      const phase = seed.x;
      const speed = seed.y;
      const amp = seed.z;
      const pos = base.toVar();
      pos.x.addAssign(sin(uTime.mul(speed).add(phase)).mul(amp));
      pos.y.addAssign(
        sin(uTime.mul(speed.mul(1.4)).add(phase.mul(2.0))).mul(amp.mul(2.0)),
      );
      pos.z.addAssign(
        cos(uTime.mul(speed.mul(0.8)).add(phase.mul(1.5))).mul(amp),
      );
      vTwinkle.assign(
        float(0.5).add(sin(uTime.mul(2.4).add(phase.mul(4.0))).mul(0.5)),
      );
      const view = modelViewMatrix.mul(vec4(pos, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(quadSize));
      return cameraProjectionMatrix.mul(view);
    })();

    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.7, 0.3), vec3(1.0, 0.95, 0.7), core);
    mat.opacityNode = core.mul(vTwinkle);
    mat.uniforms = { uTime };

    const motes = new THREE.Mesh(geo, mat);
    motes.name = "resumeBook-motes";
    motes.frustumCulled = false;
    this.motes = motes;
    this.group.add(motes);
  }

  // ── Warm point light for the "light leaking from inside" wash ──────────────

  #buildLight() {
    // Intensity is WebGPU/physical-light scale — tune visually in Phase 1.
    const light = new THREE.PointLight(0xffcf8a, 6, 5, 2);
    light.position.set(0, 0.1, 0.1);
    this._lightBase = 6;
    this.light = light;
    this.group.add(light);
  }

  // ── Collider — rotation-invariant cylinder hugging the floating book ───────

  #addCollider() {
    if (!this.physics?.addStaticCylinder) return;
    const radius = Math.max(W, D) / 2 + 0.05;
    const height = TOTAL_THK + 2 * BOB_AMP + 0.1;
    // addStaticCylinder lifts by height/2 internally → pass the bottom Y.
    const bottomY = this.hoverY - height / 2;
    this.physics.addStaticCylinder(
      this.baseX,
      bottomY,
      this.baseZ,
      radius,
      height,
    );
  }

  // ── Focus / cinematic hooks (driven by Interaction) ────────────────────────

  /** Stop spinning and turn the OPENING edge toward the reader so the cover
   *  swings open to face the player (spine ends up on the far side). */
  focusOn(playerPosition) {
    this._focused = true;
    const dx = playerPosition.x - this.baseX;
    const dz = playerPosition.z - this.baseZ;
    // yaw such that the book's local +Z (free/opening edge) points at the player.
    this._targetYaw = Math.atan2(dx, dz);
  }

  /** Resume idle spin/bob. */
  unfocus() {
    this._focused = false;
    this._targetYaw = null;
  }

  /** Camera pose that frames the open book from the reader's side. */
  getFocusPose(playerPosition) {
    const dx = playerPosition.x - this.baseX;
    const dz = playerPosition.z - this.baseZ;
    const len = Math.hypot(dx, dz) || 1;
    const ux = dx / len;
    const uz = dz / len;
    const STANDOFF = 2.4;
    const HEIGHT = 1.1;
    return {
      position: new THREE.Vector3(
        this.baseX + ux * STANDOFF,
        this.hoverY + HEIGHT,
        this.baseZ + uz * STANDOFF,
      ),
      lookAt: new THREE.Vector3(this.baseX, this.hoverY + 0.1, this.baseZ),
    };
  }

  /** Swing the cover open with a warm bloom that flares then settles. */
  playOpen(duration = 0.9) {
    gsap.killTweensOf(this.coverPivot.rotation);
    gsap.to(this.coverPivot.rotation, {
      x: -2.3,
      duration,
      ease: "power3.out",
    });
    gsap.killTweensOf(this);
    gsap
      .timeline()
      .to(this, { _glow: 2.6, duration: 0.35, ease: "power2.out" })
      .to(this, { _glow: 1.6, duration: 0.7, ease: "power2.inOut" });
    gsap.to(this, { _beacon: 0.18, duration: 0.5, ease: "power2.out" });
  }

  /** Reverse: cover shuts, glow dims, beacon returns. */
  playClose(duration = 0.6) {
    gsap.killTweensOf(this.coverPivot.rotation);
    gsap.to(this.coverPivot.rotation, { x: 0, duration, ease: "power2.inOut" });
    gsap.killTweensOf(this);
    gsap.to(this, { _glow: 1, duration, ease: "power2.inOut" });
    gsap.to(this, {
      _beacon: 1,
      duration: duration + 0.2,
      ease: "power2.inOut",
    });
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────

  update(elapsed) {
    const dt = this._last == null ? 0 : Math.min(0.05, elapsed - this._last);
    this._last = elapsed;

    if (this._focused) {
      if (this._targetYaw != null) {
        const d = Math.atan2(
          Math.sin(this._targetYaw - this._yaw),
          Math.cos(this._targetYaw - this._yaw),
        );
        this._yaw += d * Math.min(1, dt * 4);
      }
      this._bob = THREE.MathUtils.damp(this._bob, 0, 4, dt);
    } else {
      this._yaw += SPIN_SPEED * dt;
      this._bob = THREE.MathUtils.damp(this._bob, 1, 3, dt);
    }

    this.group.rotation.y = this._yaw;
    this.group.position.y =
      this.hoverY + Math.sin(elapsed * 0.8) * BOB_AMP * this._bob;

    if (this.beacon) {
      this.beacon.material.uniforms.uTime.value = elapsed;
      this.beacon.material.uniforms.uBeacon.value = this._beacon;
    }
    if (this.motes) this.motes.material.uniforms.uTime.value = elapsed;
    if (this.parchment) {
      this.parchment.emissiveIntensity = this._parchmentEmissive * this._glow;
    }
    if (this.light) {
      this.light.intensity =
        (this._lightBase + Math.sin(elapsed * 3.1) * 0.6) * this._glow;
    }
  }
}
