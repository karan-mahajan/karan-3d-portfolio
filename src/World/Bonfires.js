import gsap from "gsap";
import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import {
  Fn,
  attribute,
  cameraProjectionMatrix,
  cos,
  float,
  fract,
  length,
  mix,
  modelViewMatrix,
  positionGeometry,
  smoothstep,
  sin,
  uniform,
  uv,
  varying,
  vec2,
  vec3,
  vec4,
} from "three/tsl";

const FLAMES_PER_FIRE = 4;
const EMBERS_PER_FIRE = 14;
const SMOKE_PER_FIRE = 6;
const ASH_PER_FIRE = 8;
const NEAR_RADIUS = 5.5;

/**
 * Runtime polish for Karan's Blender-authored bonfires.
 *
 * The actual bowl, orange side stones, wood blocks, ember bed, and flame
 * pyramids come from `static/world/bonfires/bonfires.glb`. This class only
 * enhances those objects: material glow, soft light spill, smoke, ash, embers,
 * and proximity/day-night response.
 */
export class Bonfires {
  constructor(scene, refs, wind) {
    this.scene = scene;
    this.refs = refs;
    this.wind = wind;
    this.root = new THREE.Group();
    this.root.name = "bonfire-runtime-fx";
    this.scene.add(this.root);

    this.fires = [];
    this.glows = [];
    this.glowMaterials = [];
    this.flameLicks = [];
    this.flameTextures = [];
    this.emissiveMats = new Set();
    this.uTime = uniform(0);
    this.uNear = uniform(0);
    this.uNight = uniform(0);

    this._nearState = { value: 0 };
    this._nearTo = gsap.quickTo(this._nearState, "value", {
      duration: 0.5,
      ease: "power2.out",
    });
  }

  load() {
    const refs = (this.refs?.all ?? []).filter((entry) =>
      (entry.name ?? "").startsWith("refBonfire_"),
    );

    refs.forEach((ref, index) => {
      const objectName = ref.name.replace("refBonfire_", "bonfire_");
      const object = this.scene.getObjectByName(objectName);
      const fire = this.#registerFire(ref, object, index);
      this.fires.push(fire);
    });

    if (!this.fires.length) return this;

    this.#buildFlameLicks();
    this.#buildFlames();
    this.#buildEmbers();
    this.#buildSmoke();
    this.#buildAsh();
    return this;
  }

  #registerFire(ref, object, index) {
    const refPos = ref.position ?? ref.object3d?.position ?? { x: 0, y: 0, z: 0 };
    const ground = new THREE.Vector3(refPos.x, refPos.y - 0.58, refPos.z);

    if (object) {
      object.getWorldPosition(ground);
      object.traverse((child) => {
        if (!child.isMesh) return;
        child.castShadow = true;
        child.receiveShadow = true;
        child.frustumCulled = false;
        this.#styleMaterial(child.material);
      });
    }

    const seed = this.#hash(ref.name);
    const glow = this.#buildLightSpill(ground, index);
    return {
      name: ref.name,
      object,
      x: refPos.x,
      y: ground.y,
      z: refPos.z,
      flameY: Math.max(refPos.y, ground.y + 0.56),
      seed,
      glow,
    };
  }

  #styleMaterial(material) {
    const materials = Array.isArray(material) ? material : [material];
    for (const mat of materials) {
      if (!mat) continue;
      mat.needsUpdate = true;
      if (/bonfire_black_metal/i.test(mat.name)) {
        mat.roughness = 0.78;
        mat.metalness = 0.2;
      }
      if (/bonfire_bench_dark_brown/i.test(mat.name)) {
        mat.roughness = 0.9;
      }
      if (!/bonfire_(ember|flame)/i.test(mat.name)) continue;
      if (/outer/i.test(mat.name)) {
        mat.color?.set?.("#ff7a08");
      } else if (/inner/i.test(mat.name)) {
        mat.color?.set?.("#ffe36a");
      } else if (/ember/i.test(mat.name)) {
        mat.color?.set?.("#ff3a05");
      }
      if (mat.emissive) {
        mat.emissive.copy(mat.color ?? new THREE.Color("#ff8a2a"));
        mat.emissiveIntensity = /inner/i.test(mat.name) ? 1.45 : 1.1;
      }
      mat.toneMapped = true;
      this.emissiveMats.add(mat);
    }
  }

  #buildLightSpill(ground, index) {
    const mat = new THREE.MeshBasicMaterial({
      color: "#ffb15a",
      transparent: true,
      opacity: 0.055,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    const mesh = new THREE.Mesh(new THREE.CircleGeometry(2.45, 48), mat);
    mesh.name = `bonfire:warm-spill:${index}`;
    mesh.position.set(ground.x, ground.y + 0.035, ground.z);
    mesh.rotation.x = -Math.PI / 2;
    mesh.renderOrder = 2;
    this.root.add(mesh);
    const glow = { mesh, mat, seed: index * 1.7 };
    this.glows.push(glow);
    this.glowMaterials.push(mat);
    return glow;
  }

  #buildFlameLicks() {
    const variants = [
      this.#makeFlameTexture(["rgba(255, 28, 0, 0.0)", "#d91c04", "#ff6a08", "#ffe36a", "#fff8cd"], 0),
      this.#makeFlameTexture(["rgba(255, 40, 0, 0.0)", "#b91504", "#ff5005", "#ffb21c", "#fff0a0"], 1),
      this.#makeFlameTexture(["rgba(255, 90, 0, 0.0)", "#ff3b05", "#ff8a0c", "#ffd84a", "#ffffff"], 2),
      this.#makeFlameTexture(["rgba(255, 20, 0, 0.0)", "#8f1004", "#f13a04", "#ff9f17", "#fff3b8"], 3),
    ];
    this.flameTextures.push(...variants);

    for (const fire of this.fires) {
      const holder = new THREE.Group();
      holder.name = `bonfire:flame-licks:${fire.name}`;
      holder.position.set(fire.x, fire.flameY - 0.2, fire.z);
      this.root.add(holder);

      for (let i = 0; i < 8; i++) {
        const tall = i % 5 === 0;
        const wide = i % 4 === 0;
        const width = (wide ? 0.68 : 0.46) * (0.82 + Math.random() * 0.24);
        const height = (tall ? 1.55 : 1.08) * (0.82 + Math.random() * 0.28);
        const geometry = new THREE.PlaneGeometry(width, height, 1, 1);
        const texture = variants[i % variants.length];
        const material = new THREE.MeshBasicMaterial({
          map: texture,
          transparent: true,
          opacity: 0.62,
          depthWrite: false,
          blending: THREE.AdditiveBlending,
          side: THREE.DoubleSide,
          toneMapped: false,
        });
        const mesh = new THREE.Mesh(geometry, material);
        const angle = (i / 8) * Math.PI * 2 + fire.seed * 6.28;
        const ring = i < 3 ? 0.04 : i < 6 ? 0.16 : 0.25;
        mesh.position.set(Math.cos(angle) * ring, height * 0.48, Math.sin(angle) * ring);
        mesh.rotation.set(
          (Math.random() - 0.5) * 0.16,
          angle + Math.PI * 0.5,
          (Math.random() - 0.5) * 0.2,
        );
        mesh.renderOrder = 7;
        holder.add(mesh);
        this.flameLicks.push({
          mesh,
          geometry,
          material,
          baseY: mesh.position.y,
          baseScale: 0.82 + Math.random() * 0.42,
          phase: fire.seed * 20 + i * 0.73,
          speed: 3.8 + Math.random() * 3.2,
          opacity: 0.38 + Math.random() * 0.18,
        });
      }
    }
  }

  #makeFlameTexture(colors, variant) {
    const canvas = document.createElement("canvas");
    canvas.width = 96;
    canvas.height = 192;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
    gradient.addColorStop(0.0, "rgba(255, 35, 0, 0)");
    gradient.addColorStop(0.13, colors[1]);
    gradient.addColorStop(0.42, colors[2]);
    gradient.addColorStop(0.72, colors[3]);
    gradient.addColorStop(1.0, colors[4]);

    ctx.save();
    ctx.translate(canvas.width * 0.5, canvas.height * 0.94);
    ctx.beginPath();
    const lean = (variant - 1.5) * 10;
    ctx.moveTo(-26, 4);
    ctx.bezierCurveTo(-36, -41, -17 + lean * 0.5, -72, -9, -108);
    ctx.bezierCurveTo(-5 + lean * 0.5, -131, 3 - lean * 0.5, -157, 2 + lean * 0.5, -179);
    ctx.bezierCurveTo(18 + lean * 0.5, -146, 38, -114, 22, -77);
    ctx.bezierCurveTo(36, -54, 33, -24, 26, 4);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.shadowColor = "rgba(255, 95, 0, 0.72)";
    ctx.shadowBlur = 14;
    ctx.fill();

    const inner = ctx.createLinearGradient(0, 0, 0, -canvas.height);
    inner.addColorStop(0.0, "rgba(255, 210, 40, 0)");
    inner.addColorStop(0.45, "rgba(255, 232, 90, 0.74)");
    inner.addColorStop(1.0, "rgba(255, 255, 235, 0.92)");
    ctx.beginPath();
    ctx.moveTo(-10, 0);
    ctx.bezierCurveTo(-16, -43, -4 - lean * 0.5, -71, -2, -113);
    ctx.bezierCurveTo(11 + lean * 0.5, -83, 16, -48, 12, 0);
    ctx.closePath();
    ctx.fillStyle = inner;
    ctx.shadowBlur = 5;
    ctx.fill();
    ctx.restore();

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    texture.generateMipmaps = false;
    texture.needsUpdate = true;
    return texture;
  }

  #buildFlames() {
    const count = this.fires.length * FLAMES_PER_FIRE;
    const { geom, base, seed } = this.#particleGeometry(count);
    let i = 0;
    for (const fire of this.fires) {
      for (let j = 0; j < FLAMES_PER_FIRE; j++, i++) {
        const a = (j / FLAMES_PER_FIRE) * Math.PI * 2 + fire.seed * 6.28;
        const r = j === 0 ? 0 : 0.08 + 0.08 * (j % 2);
        base[i * 3] = fire.x + Math.cos(a) * r;
        base[i * 3 + 1] = fire.flameY + 0.1 + (j % 3) * 0.025;
        base[i * 3 + 2] = fire.z + Math.sin(a) * r;
        seed[i * 4] = fire.seed + j * 0.173;
        seed[i * 4 + 1] = 0.34 + (j % 3) * 0.06;
        seed[i * 4 + 2] = 0.72 + (j % 4) * 0.1;
        seed[i * 4 + 3] = j % 2 ? -1 : 1;
      }
    }
    this.#finishParticleGeometry(geom, base, seed);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      fog: false,
    });
    const vHeat = varying(float(0), "vBonfireHeat");

    mat.vertexNode = Fn(() => {
      const basePos = attribute("aBase");
      const data = attribute("aSeed");
      const phase = this.uTime.mul(data.x.mul(2.4).add(4.4));
      const flicker = sin(phase).mul(0.12).add(sin(phase.mul(2.1)).mul(0.05));
      const width = data.y.mul(float(1.08).add(this.uNear.mul(0.22)));
      const height = data.z.mul(float(1.08).add(this.uNight.mul(0.22))).add(flicker.mul(0.36));
      vHeat.assign(float(0.86).add(flicker).add(this.uNear.mul(0.16)));

      const sway = vec2(sin(phase).mul(0.052), cos(phase.mul(0.74)).mul(0.035));
      const world = vec3(
        basePos.x.add(sway.x.mul(data.w)),
        basePos.y.add(flicker.mul(0.13)),
        basePos.z.add(sway.y),
      );
      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(vec2(width, height)));
      return cameraProjectionMatrix.mul(view);
    })();

    const local = uv().sub(vec2(0.5, 0.3));
    const core = smoothstep(0.32, 0.0, length(local.mul(vec2(0.72, 1.5))));
    const body = smoothstep(0.54, 0.02, length(local.mul(vec2(1.05, 1.2))));
    const bottom = smoothstep(0.02, 0.18, uv().y);
    const top = smoothstep(1.0, 0.54, uv().y);
    const orange = mix(vec3(0.95, 0.06, 0.0), vec3(1.0, 0.52, 0.04), uv().y);
    mat.colorNode = mix(orange, vec3(1.0, 0.92, 0.42), core)
      .mul(vHeat)
      .mul(float(0.82).add(this.uNight.mul(0.42)));
    mat.opacityNode = body.mul(bottom).mul(top).mul(float(0.58).add(core.mul(0.28)));

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = "bonfire:flame-aura";
    mesh.frustumCulled = false;
    mesh.renderOrder = 8;
    this.root.add(mesh);
    this.flames = { mesh, geom, mat };
  }

  #buildEmbers() {
    const count = this.fires.length * EMBERS_PER_FIRE;
    const { geom, base, seed } = this.#particleGeometry(count);
    let i = 0;
    for (const fire of this.fires) {
      for (let j = 0; j < EMBERS_PER_FIRE; j++, i++) {
        const a = Math.random() * Math.PI * 2;
        const r = Math.sqrt(Math.random()) * 0.34;
        base[i * 3] = fire.x + Math.cos(a) * r;
        base[i * 3 + 1] = fire.flameY + 0.15;
        base[i * 3 + 2] = fire.z + Math.sin(a) * r;
        seed[i * 4] = Math.random();
        seed[i * 4 + 1] = 1.0 + Math.random() * 1.2;
        seed[i * 4 + 2] = 0.035 + Math.random() * 0.045;
        seed[i * 4 + 3] = fire.seed * 6.28 + j;
      }
    }
    this.#finishParticleGeometry(geom, base, seed);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    });
    const vFade = varying(float(0), "vBonfireEmberFade");

    mat.vertexNode = Fn(() => {
      const basePos = attribute("aBase");
      const data = attribute("aSeed");
      const life = float(2.2).div(data.y);
      const phase = fract(this.uTime.div(life).add(data.x));
      const fade = phase.oneMinus().mul(smoothstep(0.0, 0.12, phase));
      vFade.assign(fade);

      const wind = this.wind.offsetNode(basePos.xz).mul(phase).mul(0.55);
      const curl = vec2(sin(phase.mul(10.0).add(data.w)), cos(phase.mul(7.4).add(data.w))).mul(0.16);
      const world = vec3(
        basePos.x.add(wind.x).add(curl.x),
        basePos.y.add(phase.mul(float(1.85).add(this.uNear.mul(0.5)))),
        basePos.z.add(wind.y).add(curl.y),
      );
      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(data.z.mul(float(0.85).add(this.uNear.mul(0.5)))));
      return cameraProjectionMatrix.mul(view);
    })();

    const disc = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.34, 0.03), vec3(1.0, 0.88, 0.42), vFade)
      .mul(float(0.86).add(this.uNight.mul(0.75)));
    mat.opacityNode = disc.mul(vFade).mul(float(0.42).add(this.uNear.mul(0.32)));

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = "bonfire:embers";
    mesh.frustumCulled = false;
    mesh.renderOrder = 9;
    this.root.add(mesh);
    this.embers = { mesh, geom, mat };
  }

  #buildSmoke() {
    const count = this.fires.length * SMOKE_PER_FIRE;
    const { geom, base, seed } = this.#particleGeometry(count);
    let i = 0;
    for (const fire of this.fires) {
      for (let j = 0; j < SMOKE_PER_FIRE; j++, i++) {
        const a = Math.random() * Math.PI * 2;
        const r = Math.sqrt(Math.random()) * 0.2;
        base[i * 3] = fire.x + Math.cos(a) * r;
        base[i * 3 + 1] = fire.flameY + 0.45;
        base[i * 3 + 2] = fire.z + Math.sin(a) * r;
        seed[i * 4] = Math.random();
        seed[i * 4 + 1] = 0.65 + Math.random() * 0.6;
        seed[i * 4 + 2] = 0.46 + Math.random() * 0.32;
        seed[i * 4 + 3] = fire.seed * 8.0 + j;
      }
    }
    this.#finishParticleGeometry(geom, base, seed);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.NormalBlending,
      fog: true,
    });
    const vFade = varying(float(0), "vBonfireSmokeFade");

    mat.vertexNode = Fn(() => {
      const basePos = attribute("aBase");
      const data = attribute("aSeed");
      const phase = fract(this.uTime.mul(0.17).mul(data.y).add(data.x));
      const fade = smoothstep(0.0, 0.12, phase).mul(phase.oneMinus());
      vFade.assign(fade);

      const wind = this.wind.offsetNode(basePos.xz).mul(phase).mul(1.6);
      const curl = vec2(sin(phase.mul(7.0).add(data.w)), cos(phase.mul(5.8).add(data.w))).mul(0.34);
      const world = vec3(
        basePos.x.add(wind.x).add(curl.x),
        basePos.y.add(phase.mul(2.75)),
        basePos.z.add(wind.y).add(curl.y),
      );
      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(data.z.mul(float(0.7).add(phase.mul(1.25)))));
      return cameraProjectionMatrix.mul(view);
    })();

    const puff = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(0.18, 0.16, 0.14), vec3(0.52, 0.49, 0.43), this.uNight);
    mat.opacityNode = puff
      .mul(vFade)
      .mul(float(0.085).add(this.uNear.mul(0.055)))
      .mul(float(1.0).sub(this.uNight.mul(0.22)));

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = "bonfire:smoke";
    mesh.frustumCulled = false;
    mesh.renderOrder = 5;
    this.root.add(mesh);
    this.smoke = { mesh, geom, mat };
  }

  #buildAsh() {
    const count = this.fires.length * ASH_PER_FIRE;
    const { geom, base, seed } = this.#particleGeometry(count);
    let i = 0;
    for (const fire of this.fires) {
      for (let j = 0; j < ASH_PER_FIRE; j++, i++) {
        const a = Math.random() * Math.PI * 2;
        const r = 0.3 + Math.random() * 0.68;
        base[i * 3] = fire.x + Math.cos(a) * r;
        base[i * 3 + 1] = fire.flameY - 0.08;
        base[i * 3 + 2] = fire.z + Math.sin(a) * r;
        seed[i * 4] = Math.random();
        seed[i * 4 + 1] = 0.42 + Math.random() * 0.62;
        seed[i * 4 + 2] = 0.02 + Math.random() * 0.024;
        seed[i * 4 + 3] = fire.seed * 9.0 + j;
      }
    }
    this.#finishParticleGeometry(geom, base, seed);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.NormalBlending,
      fog: true,
    });
    const vFade = varying(float(0), "vBonfireAshFade");

    mat.vertexNode = Fn(() => {
      const basePos = attribute("aBase");
      const data = attribute("aSeed");
      const phase = fract(this.uTime.mul(0.105).mul(data.y).add(data.x));
      const fade = smoothstep(0.0, 0.08, phase).mul(phase.oneMinus());
      vFade.assign(fade);

      const wind = this.wind.offsetNode(basePos.xz).mul(phase).mul(1.0);
      const swirl = vec2(sin(phase.mul(12.0).add(data.w)), cos(phase.mul(8.0).add(data.w))).mul(0.28);
      const world = vec3(
        basePos.x.add(wind.x).add(swirl.x),
        basePos.y.add(sin(phase.mul(6.28).add(data.w)).mul(0.22)).add(phase.mul(0.9)),
        basePos.z.add(wind.y).add(swirl.y),
      );
      const view = modelViewMatrix.mul(vec4(world, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(data.z));
      return cameraProjectionMatrix.mul(view);
    })();

    const speck = smoothstep(0.46, 0.0, length(uv().sub(0.5)));
    mat.colorNode = vec3(0.64, 0.59, 0.51);
    mat.opacityNode = speck.mul(vFade).mul(float(0.18).add(this.uNear.mul(0.1)));

    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = "bonfire:ash";
    mesh.frustumCulled = false;
    mesh.renderOrder = 6;
    this.root.add(mesh);
    this.ash = { mesh, geom, mat };
  }

  #particleGeometry(count) {
    const baseGeom = new THREE.BufferGeometry();
    const quad = new Float32Array([
      -0.5, -0.5, 0,
      0.5, -0.5, 0,
      0.5, 0.5, 0,
      -0.5, 0.5, 0,
    ]);
    const quadUv = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
    baseGeom.setAttribute("position", new THREE.BufferAttribute(quad, 3));
    baseGeom.setAttribute("uv", new THREE.BufferAttribute(quadUv, 2));
    baseGeom.setIndex([0, 1, 2, 0, 2, 3]);

    const geom = new THREE.InstancedBufferGeometry();
    geom.setAttribute("position", baseGeom.attributes.position);
    geom.setAttribute("uv", baseGeom.attributes.uv);
    geom.setIndex(baseGeom.index);
    geom.instanceCount = count;
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    return {
      geom,
      base: new Float32Array(count * 3),
      seed: new Float32Array(count * 4),
    };
  }

  #finishParticleGeometry(geom, base, seed) {
    geom.setAttribute("aBase", new THREE.InstancedBufferAttribute(base, 3));
    geom.setAttribute("aSeed", new THREE.InstancedBufferAttribute(seed, 4));
  }

  #hash(value) {
    let h = 2166136261;
    for (let i = 0; i < value.length; i++) {
      h ^= value.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return ((h >>> 0) % 10000) / 10000;
  }

  update(elapsed, delta, playerPosition, mode = "day") {
    if (!this.fires.length) return;

    this.uTime.value = elapsed;
    const nightTarget = mode === "night" ? 1 : 0;
    this.uNight.value +=
      (nightTarget - this.uNight.value) * Math.min(1, delta * 2.8);

    let near = 0;
    if (playerPosition) {
      for (const fire of this.fires) {
        const dx = playerPosition.x - fire.x;
        const dz = playerPosition.z - fire.z;
        const d = Math.sqrt(dx * dx + dz * dz);
        near = Math.max(near, 1 - Math.min(1, d / NEAR_RADIUS));
      }
    }
    this._nearTo(near);
    this.uNear.value = this._nearState.value;

    const flicker =
      0.9 +
      Math.sin(elapsed * 9.2) * 0.08 +
      Math.sin(elapsed * 17.1) * 0.035;
    for (const mat of this.emissiveMats) {
      if (!mat.emissive) continue;
      const inner = /inner/i.test(mat.name) ? 1.25 : 1.0;
      mat.emissiveIntensity =
        inner * (0.95 + this.uNight.value * 1.05 + this.uNear.value * 0.32) * flicker;
    }

    for (const lick of this.flameLicks) {
      const wave =
        0.78 +
        Math.sin(elapsed * lick.speed + lick.phase) * 0.18 +
        Math.sin(elapsed * (lick.speed * 1.83) + lick.phase * 0.7) * 0.08;
      const heat = 1 + this.uNear.value * 0.18 + this.uNight.value * 0.12;
      const y = lick.baseScale * wave * heat;
      const xz = lick.baseScale * (1.08 - wave * 0.16);
      lick.mesh.scale.set(xz, y, xz);
      lick.mesh.position.y =
        lick.baseY + Math.sin(elapsed * lick.speed + lick.phase) * 0.055;
      lick.mesh.rotation.y += delta * (0.28 + (lick.phase % 1.2));
      lick.material.opacity =
        lick.opacity *
        (0.58 + this.uNight.value * 0.22 + this.uNear.value * 0.08) *
        (0.86 + Math.sin(elapsed * lick.speed * 1.4 + lick.phase) * 0.14);
    }

    for (const glow of this.glows) {
      const localFlicker =
        0.86 +
        Math.sin(elapsed * 8.0 + glow.seed) * 0.08 +
        Math.sin(elapsed * 14.0 + glow.seed * 1.7) * 0.035;
      glow.mat.opacity =
        (0.045 + this.uNight.value * 0.12 + this.uNear.value * 0.055) *
        localFlicker;
      glow.mesh.scale.setScalar(1 + this.uNight.value * 0.08 + this.uNear.value * 0.12);
    }
  }

  dispose() {
    gsap.killTweensOf(this._nearState);
    for (const part of [this.flames, this.embers, this.smoke, this.ash]) {
      if (!part) continue;
      this.root.remove(part.mesh);
      part.geom?.dispose();
      part.mat?.dispose();
    }
    for (const lick of this.flameLicks) {
      lick.mesh.geometry?.dispose();
      lick.material?.dispose();
    }
    for (const texture of this.flameTextures) texture.dispose();
    for (const glow of this.glows) {
      glow.mesh.geometry?.dispose();
      glow.mat?.dispose();
    }
    this.scene.remove(this.root);
  }
}
