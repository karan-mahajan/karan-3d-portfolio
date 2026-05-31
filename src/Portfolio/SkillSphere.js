import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { skills } from './SkillsData.js';

const CATEGORY_COLORS = {
  Frontend: '#77d8ff',
  CMS: '#f08cb0',
  'Backend & DB': '#7af0ae',
  'DevOps & Tools': '#bfa2ff',
  Other: '#f6c56f',
};

const PRIORITY = new Map([
  ['Next.js', 4],
  ['React', 4],
  ['TypeScript', 4],
  ['Node.js', 4],
  ['Python', 4],
  ['AWS', 4],
  ['PostgreSQL', 3],
  ['MongoDB', 3],
  ['Django', 3],
  ['WordPress', 3],
  ['REST APIs', 3],
  ['GraphQL', 3],
  ['Git', 3],
  ['JavaScript', 3],
  ['Tailwind', 3],
]);

const tmpDir = new THREE.Vector3();
const tmpSide = new THREE.Vector3();
const tmpCameraQuat = new THREE.Quaternion();
const tmpParentQuat = new THREE.Quaternion();
const tmpRootQuat = new THREE.Quaternion();

/**
 * Runtime layer for the Blender-authored skills sphere.
 *
 * Blender owns the plinth/rings/core. This class adds the readable skill boards
 * and the press-E camera state from `sectionRef_skills` metadata.
 */
export class SkillSphere {
  constructor({
    scene,
    camera,
    player,
    playerCamera,
    controller,
    refs,
    audio = null,
    achievements = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.audio = audio;
    this.achievements = achievements;

    const ref = refs?.sections?.skills ?? null;
    this.ref = ref;
    this.ready = !!ref;
    this.active = false;
    this.zooming = false;
    this.interactive = false;
    this.elapsed = 0;
    this._near = false;

    this.center = ref?.position?.clone?.() ?? new THREE.Vector3(0, 7, -70);
    const extras = ref?.extras ?? {};
    this.radius = Number(extras.sphereRadius) || 6;
    // The pond is part of the interaction area, not just the exact globe
    // center. Keep this generous so the prompt appears from the stepping
    // stones, shore, and shallow water around the installation.
    this.proximity = Math.max(15.5, this.radius + 9.5);
    this.enterOffset = this.#vectorFromExtra(extras.enterCameraOffset, new THREE.Vector3(0, 0, 0.85));

    this.root = new THREE.Group();
    this.root.name = 'runtime-skill-sphere';
    this.root.position.copy(this.center);
    this.root.userData.noTorchRaycast = true;

    this.labelRoot = new THREE.Group();
    this.labelRoot.name = 'runtime-skill-label-orbit';
    this.root.add(this.labelRoot);

    this.labels = [];
    this.title = null;
    this.coreVisuals = [];
    if (this.ready) {
      this.#buildLabels();
      this.#buildTitle();
      this.scene.add(this.root);
      this.#collectCoreVisuals();
      this.#installDom();
    } else {
      console.warn('[SkillSphere] sectionRef_skills missing; runtime labels skipped');
    }
  }

  near(playerPosition) {
    if (!this.ready || this.active || this.zooming || !playerPosition) return false;
    const dx = playerPosition.x - this.center.x;
    const dz = playerPosition.z - this.center.z;
    this._near = dx * dx + dz * dz <= this.proximity * this.proximity;
    return this._near;
  }

  enter() {
    if (!this.ready || this.active || this.zooming) return;
    this.active = true;
    this.zooming = true;
    this.interactive = false;
    this._near = false;
    this.audio?.playMenuOpen?.();
    this.achievements?.onSectionVisited?.('skills');

    if (!this._returnPos) {
      this._returnPos = new THREE.Vector3();
      this._returnLook = new THREE.Vector3();
      this._returnDir = new THREE.Vector3();
    }
    this._returnPos.copy(this.camera.position);
    this.camera.getWorldDirection(this._returnDir);
    this._returnLook.copy(this._returnPos).add(this._returnDir);

    if (this.controller) this.controller.paused = true;
    if (this.playerCamera) this.playerCamera.locked = true;
    this.#setCoreVisible(false);

    const playerPos = this.player?.position ?? this._returnPos;
    tmpDir.set(playerPos.x - this.center.x, 0, playerPos.z - this.center.z);
    if (tmpDir.lengthSq() < 0.001) {
      this.camera.getWorldDirection(tmpDir);
      tmpDir.y = 0;
      tmpDir.multiplyScalar(-1);
    }
    tmpDir.normalize();

    const targetPos = this.center.clone();
    const targetLook = this.center.clone().addScaledVector(tmpDir, this.radius);
    targetLook.y += 0.12;
    this.#setInsideControlsFromDirection(tmpDir);

    const lookProxy = this.camera.position.clone().add(this._returnDir);
    this.#setHint(true);
    this.#popLabels();

    gsap.to(lookProxy, {
      x: targetLook.x,
      y: targetLook.y,
      z: targetLook.z,
      duration: 1.25,
      ease: 'power3.inOut',
    });
    gsap.to(this.camera.position, {
      x: targetPos.x,
      y: targetPos.y,
      z: targetPos.z,
      duration: 1.25,
      ease: 'power3.inOut',
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.camera.position.copy(this.center);
        this.#applyInsideCamera(0);
        this.interactive = true;
        this.zooming = false;
      },
    });
  }

  exit() {
    if (!this.ready || (!this.active && !this.zooming)) return;
    this.active = false;
    this.zooming = true;
    this.interactive = false;
    this.audio?.playMenuClose?.();
    this.#setHint(false);
    this.#restoreInsideControlLimits();

    const currentDir = new THREE.Vector3();
    this.camera.getWorldDirection(currentDir);
    const lookProxy = this.camera.position.clone().add(currentDir);

    gsap.to(lookProxy, {
      x: this._returnLook.x,
      y: this._returnLook.y,
      z: this._returnLook.z,
      duration: 1.0,
      ease: 'power2.inOut',
    });
    gsap.to(this.camera.position, {
      x: this._returnPos.x,
      y: this._returnPos.y,
      z: this._returnPos.z,
      duration: 1.0,
      ease: 'power2.inOut',
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.zooming = false;
        this.#setCoreVisible(true);
        if (this.controller) this.controller.paused = false;
        if (this.playerCamera) {
          this.playerCamera.locked = false;
          this.playerCamera.resync();
        }
      },
    });
  }

  update(delta) {
    if (!this.ready) return;
    this.elapsed += delta;
    if (this.active && this.interactive) this.#applyInsideCamera(delta);
    const speed = this.active ? 0.16 : 0.36;
    this.labelRoot.rotation.y += delta * speed;
    this.labelRoot.rotation.x = Math.sin(this.elapsed * 0.28) * 0.055;

    const opacityLift = this.active ? 0.22 : this._near ? 0.12 : 0;
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      this.camera.getWorldQuaternion(tmpCameraQuat);
      this.labelRoot.getWorldQuaternion(tmpParentQuat).invert();
      label.quaternion.copy(tmpParentQuat.multiply(tmpCameraQuat));
      const mat = label.material;
      const base = label.userData.baseOpacity;
      mat.opacity += ((base + opacityLift) - mat.opacity) * Math.min(1, delta * 5);
    }
    if (this.title) {
      this.camera.getWorldQuaternion(tmpCameraQuat);
      this.root.getWorldQuaternion(tmpRootQuat).invert();
      this.title.quaternion.copy(tmpRootQuat.multiply(tmpCameraQuat));
      this.title.position.y = this.radius + 1.1 + Math.sin(this.elapsed * 1.3) * 0.08;
    }
  }

  #buildLabels() {
    const entries = this.#flattenSkills();
    const golden = Math.PI * (3 - Math.sqrt(5));
    const orbitRadius = this.radius * 0.91;
    const yRadius = this.radius * 0.64;

    for (let i = 0; i < entries.length; i++) {
      const item = entries[i];
      const y = 1 - (i / Math.max(entries.length - 1, 1)) * 2;
      const ring = Math.sqrt(Math.max(0, 1 - y * y));
      const theta = i * golden;
      const label = this.#makeBoard(item);
      label.position.set(
        Math.cos(theta) * ring * orbitRadius,
        y * yRadius,
        Math.sin(theta) * ring * orbitRadius,
      );
      label.userData.homePosition = label.position.clone();
      this.labelRoot.add(label);
      this.labels.push(label);
    }
  }

  #buildTitle() {
    this.title = this.#makeTitleBoard();
    this.title.position.set(0, this.radius + 1.1, 0);
    this.root.add(this.title);
  }

  #flattenSkills() {
    return skills.flatMap((category) => {
      const categoryName = category.category ?? category.title ?? category.name ?? 'Skills';
      const color = CATEGORY_COLORS[categoryName] ?? CATEGORY_COLORS.Other;
      return (category.items ?? []).map((label) => ({
        label,
        category: categoryName,
        color,
        weight: PRIORITY.get(label) ?? this.#categoryWeight(categoryName, label),
      }));
    });
  }

  #categoryWeight(category, label) {
    if (category === 'Frontend' && ['HTML', 'CSS', 'JavaScript'].includes(label)) return 2;
    if (category === 'Backend & DB' && ['Java', 'MySQL'].includes(label)) return 2;
    if (category === 'DevOps & Tools' && ['Jenkins', 'Pantheon', 'Figma'].includes(label)) return 2;
    if (category === 'Other' && ['Stripe', 'WooCommerce', 'WCAG'].includes(label)) return 2;
    return 1;
  }

  #makeBoard(item) {
    const canvas = document.createElement('canvas');
    canvas.width = 768;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');
    const isLarge = item.weight >= 4;
    const isMedium = item.weight === 3;
    const worldWidth = isLarge ? 3.05 : isMedium ? 2.55 : 2.05;
    const worldHeight = isLarge ? 0.86 : isMedium ? 0.72 : 0.58;

    this.#drawBoard(ctx, canvas, item, isLarge, isMedium);

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;

    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: isLarge ? 0.92 : isMedium ? 0.82 : 0.72,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(worldWidth, worldHeight), material);
    mesh.name = `skill-board-${item.label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
    mesh.userData.noTorchRaycast = true;
    mesh.userData.skill = item;
    mesh.userData.baseOpacity = material.opacity;
    mesh.userData.baseScale = mesh.scale.clone();
    return mesh;
  }

  #drawBoard(ctx, canvas, item, isLarge, isMedium) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 28 : isMedium ? 20 : 14;
    ctx.fillStyle = 'rgba(6, 13, 12, 0.78)';
    this.#roundRect(ctx, 28, 28, w - 56, h - 56, 28);
    ctx.fill();
    ctx.restore();

    ctx.strokeStyle = item.color;
    ctx.lineWidth = isLarge ? 8 : isMedium ? 6 : 4;
    this.#roundRect(ctx, 34, 34, w - 68, h - 68, 24);
    ctx.stroke();

    ctx.fillStyle = item.color;
    ctx.globalAlpha = 0.92;
    this.#roundRect(ctx, 54, 50, 138, 34, 16);
    ctx.fill();
    ctx.globalAlpha = 1;

    ctx.fillStyle = '#06100e';
    ctx.font = '900 20px Rajdhani, Inter, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.#shortCategory(item.category), 123, 68);

    let fontSize = isLarge ? 78 : isMedium ? 66 : 56;
    ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    while (ctx.measureText(item.label).width > w - 132 && fontSize > 34) {
      fontSize -= 4;
      ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    }
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 18 : 10;
    ctx.fillStyle = '#f6f1df';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(item.label, w / 2, h / 2 + 20);
    ctx.shadowBlur = 0;
  }

  #makeTitleBoard() {
    const canvas = document.createElement('canvas');
    canvas.width = 768;
    canvas.height = 192;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'rgba(6, 13, 12, 0.68)';
    this.#roundRect(ctx, 68, 36, canvas.width - 136, canvas.height - 72, 26);
    ctx.fill();
    ctx.strokeStyle = '#7af0ae';
    ctx.lineWidth = 5;
    this.#roundRect(ctx, 76, 44, canvas.width - 152, canvas.height - 88, 22);
    ctx.stroke();
    ctx.shadowColor = '#7af0ae';
    ctx.shadowBlur = 22;
    ctx.fillStyle = '#f6f1df';
    ctx.font = '900 72px Oswald, Rajdhani, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('SKILLS', canvas.width / 2, canvas.height / 2 + 2);

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 0.85), material);
    mesh.name = 'skill-sphere-title-board';
    mesh.userData.noTorchRaycast = true;
    return mesh;
  }

  #popLabels() {
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      gsap.killTweensOf(label.scale);
      gsap.fromTo(
        label.scale,
        { x: 0.16, y: 0.16, z: 1 },
        {
          x: 1,
          y: 1,
          z: 1,
          duration: 0.72,
          delay: i * 0.018,
          ease: 'back.out(1.75)',
        },
      );
    }
  }

  #installDom() {
    this.hintEl = document.createElement('div');
    this.hintEl.className = 'skill-sphere-hint hidden';
    this.hintEl.innerHTML = `
      <span class="skill-sphere-kicker">Inside Skills</span>
      <strong>Frontend / CMS / Backend / DevOps</strong>
      <span class="skill-sphere-exit">ESC to return</span>
    `;
    document.body.appendChild(this.hintEl);
  }

  #setHint(show) {
    if (!this.hintEl) return;
    this.hintEl.classList.toggle('hidden', !show);
  }

  #collectCoreVisuals() {
    const names = [
      'skillSphere_core_inner',
      'skillSphere_core_halo',
      'skillSphere_energy_column',
    ];
    for (const name of names) {
      const obj = this.scene.getObjectByName(name);
      if (obj) this.coreVisuals.push(obj);
    }
  }

  #setCoreVisible(visible) {
    for (const obj of this.coreVisuals) obj.visible = visible;
  }

  #setInsideControlsFromDirection(direction) {
    const controls = this.playerCamera?.controls;
    if (!controls) return;
    if (!this._savedControlLimits) {
      this._savedControlLimits = {
        minPolarAngle: controls.minPolarAngle,
        maxPolarAngle: controls.maxPolarAngle,
        minDistance: controls.minDistance,
        maxDistance: controls.maxDistance,
      };
    }
    controls.minPolarAngle = Math.PI * 0.08;
    controls.maxPolarAngle = Math.PI * 0.92;
    controls.minDistance = 0.1;
    controls.maxDistance = 0.1;
    controls.azimuthAngle = Math.atan2(direction.x, direction.z);
    controls.polarAngle = Math.PI * 0.5;
    controls.distance = 0.1;
  }

  #restoreInsideControlLimits() {
    const controls = this.playerCamera?.controls;
    const saved = this._savedControlLimits;
    if (!controls || !saved) return;
    controls.minPolarAngle = saved.minPolarAngle;
    controls.maxPolarAngle = saved.maxPolarAngle;
    controls.minDistance = saved.minDistance;
    controls.maxDistance = saved.maxDistance;
    this._savedControlLimits = null;
  }

  #applyInsideCamera(delta) {
    const controls = this.playerCamera?.controls;
    if (controls) controls.update(delta);
    const azimuth = controls?.azimuthAngle ?? 0;
    const polar = controls?.polarAngle ?? Math.PI * 0.5;
    const sinPolar = Math.sin(polar);
    tmpDir.set(
      sinPolar * Math.sin(azimuth),
      Math.cos(polar),
      sinPolar * Math.cos(azimuth),
    );
    this.camera.position.copy(this.center);
    this.camera.lookAt(this.center.clone().addScaledVector(tmpDir, this.radius));
  }

  #vectorFromExtra(value, fallback) {
    if (Array.isArray(value)) return new THREE.Vector3(value[0] ?? 0, value[1] ?? 0, value[2] ?? 0);
    if (value && typeof value === 'object') {
      return new THREE.Vector3(value.x ?? 0, value.y ?? 0, value.z ?? 0);
    }
    return fallback.clone();
  }

  #shortCategory(category) {
    if (category === 'Backend & DB') return 'BACKEND';
    if (category === 'DevOps & Tools') return 'DEVOPS';
    return String(category || 'SKILL').toUpperCase();
  }

  #roundRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }
}
