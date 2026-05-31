import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { skills } from './SkillsData.js';

const CATEGORY_COLORS = {
  Frontend: '#4a90d9',
  CMS: '#d98aa8',
  'Backend & DB': '#7fd1a8',
  'DevOps & Tools': '#e0a05a',
  Other: '#c4a6e8',
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
const tmpParentQuat = new THREE.Quaternion();
const tmpRootQuat = new THREE.Quaternion();
const tmpLabelPos = new THREE.Vector3();
const tmpToCam = new THREE.Vector3();
const tmpRight = new THREE.Vector3();
const tmpUp = new THREE.Vector3();
const tmpBasis = new THREE.Matrix4();
const tmpWorldQuat = new THREE.Quaternion();
const tmpCamFwd = new THREE.Vector3();
const tmpToLabel = new THREE.Vector3();
const tmpLook = new THREE.Vector3();
const tmpColor = new THREE.Color();

const WORLD_UP = new THREE.Vector3(0, 1, 0);

// Card orbit shares the equator ring's base rate so cards read as carried by
// the structure, not animated independently. Scaled down inside for calm browse.
const CARD_ORBIT_RATE = 0.18;

// Observatory identity, recolored per time of day so the rings always read
// against the sky behind them:
//   NIGHT   — warm brass gold + teal accent (pops against the dark sky).
//   MORNING — bold orange + rose accent (gold/teal vanish against blue sky).
const NIGHT_PRIMARY = '#e6c172'; // gold
const NIGHT_ACCENT = '#6fd6c4'; // teal
const MORNING_PRIMARY = '#ef6a2e'; // bold orange
const MORNING_ACCENT = '#ffd24d'; // golden yellow (sunrise pair, no pink)

// Differential spin rates (rad/s) + direction + per-mode emissive tints for each
// ring/core part, keyed by Blender object name. Speeds/dirs differ = orrery feel.
const STRUCTURE_SPIN = [
  { name: 'skillSphere_orbit_ring_equator', rate: 0.18, dir: 1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_orbit_ring_meridian_a', rate: 0.26, dir: -1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_orbit_ring_meridian_b', rate: 0.22, dir: -1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_orbit_ring_meridian_c', rate: 0.30, dir: 1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_orbit_ring_meridian_d', rate: 0.24, dir: -1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_orbit_lat_north_mid', rate: 0.14, dir: -1, night: NIGHT_ACCENT, day: MORNING_ACCENT },
  { name: 'skillSphere_orbit_lat_south_mid', rate: 0.14, dir: 1, night: NIGHT_ACCENT, day: MORNING_ACCENT },
  { name: 'skillSphere_orbit_lat_north_high', rate: 0.20, dir: 1, night: NIGHT_ACCENT, day: MORNING_ACCENT },
  { name: 'skillSphere_orbit_lat_south_high', rate: 0.20, dir: -1, night: NIGHT_ACCENT, day: MORNING_ACCENT },
  { name: 'skillSphere_orb_shell', rate: 0.05, dir: 1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_energy_column', rate: 0.10, dir: 1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_core_inner', rate: 0.12, dir: 1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
  { name: 'skillSphere_core_halo', rate: 0.03, dir: -1, night: NIGHT_PRIMARY, day: MORNING_PRIMARY },
];

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
    timeOfDay = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.audio = audio;
    this.achievements = achievements;
    this.timeOfDay = timeOfDay;

    const ref = refs?.sections?.skills ?? null;
    this.ref = ref;
    this.ready = !!ref;
    this.active = false;
    this.zooming = false;
    this.interactive = false;
    this.elapsed = 0;
    this._near = false;
    this._todMode = null;
    this._todCardScale = 1;

    this.center = ref?.position?.clone?.() ?? new THREE.Vector3(0, 7, -70);
    const extras = ref?.extras ?? {};
    this.radius = Number(extras.sphereRadius) || 6;
    this.insideScale = 2.15;
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
    this.labelRoot.scale.setScalar(1);
    this.root.add(this.labelRoot);

    this.labels = [];
    this.title = null;
    this.coreVisuals = [];
    if (this.ready) {
      this.#buildLabels();
      this.#buildTitle();
      this.scene.add(this.root);
      this.#collectStructure();
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
    this.#setInsideProjection(true);
    gsap.to(this.labelRoot.scale, {
      x: this.insideScale,
      y: this.insideScale,
      z: this.insideScale,
      duration: 1.1,
      ease: 'power3.inOut',
    });

    const playerPos = this.player?.position ?? this._returnPos;
    tmpDir.set(playerPos.x - this.center.x, 0, playerPos.z - this.center.z);
    if (tmpDir.lengthSq() < 0.001) {
      this.camera.getWorldDirection(tmpDir);
      tmpDir.y = 0;
      tmpDir.multiplyScalar(-1);
    }
    tmpDir.normalize();

    this.#setInsideControlsFromDirection(tmpDir);

    this.#setHint(true);
    this.#popLabels();
    this.camera.position.copy(this.center);
    this.#applyInsideCamera(0);
    this.interactive = true;
    this.zooming = false;
  }

  exit() {
    if (!this.ready || (!this.active && !this.zooming)) return;
    this.active = false;
    this.zooming = true;
    this.interactive = false;
    this.audio?.playMenuClose?.();
    this.#setHint(false);
    this.#restoreInsideControlLimits();
    this.#setInsideProjection(false);
    gsap.to(this.labelRoot.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.85,
      ease: 'power2.inOut',
    });

    this.camera.position.copy(this._returnPos);
    this.camera.lookAt(this._returnLook);
    this.zooming = false;
    this.#setCoreVisible(true);
    if (this.controller) this.controller.paused = false;
    if (this.playerCamera) {
      this.playerCamera.locked = false;
      this.playerCamera.resync();
    }
  }

  update(delta) {
    if (!this.ready) return;
    this.elapsed += delta;
    if (this.timeOfDay?.mode) this.#applyTimeOfDay(this.timeOfDay.mode);
    if (this.active && this.interactive) this.#applyInsideCamera(delta);

    this.#animateStructure(delta);

    const orbitScale = this.active ? 0.9 : 2.0; // cards drift a touch faster than rings outside
    this.labelRoot.rotation.y += delta * CARD_ORBIT_RATE * orbitScale;
    this.labelRoot.rotation.x = Math.sin(this.elapsed * 0.28) * 0.055;

    this.labelRoot.getWorldQuaternion(tmpParentQuat).invert();
    this.camera.getWorldDirection(tmpCamFwd);
    const opacityLift = this.active ? 0.22 : this._near ? 0.12 : 0;
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      this.#faceCamera(label, tmpParentQuat);
      label.getWorldPosition(tmpLabelPos);
      tmpToLabel.copy(tmpLabelPos).sub(this.camera.position).normalize();
      const facing = tmpCamFwd.dot(tmpToLabel); // 1 = dead ahead, -1 = behind
      const depthFactor = THREE.MathUtils.clamp((facing + 0.35) / 1.0, 0.12, 1);
      const mat = label.material;
      const target = (label.userData.baseOpacity + opacityLift) * depthFactor * this._todCardScale;
      mat.opacity += (target - mat.opacity) * Math.min(1, delta * 5);
    }
    if (this.title) {
      this.root.getWorldQuaternion(tmpRootQuat).invert();
      this.#faceCamera(this.title, tmpRootQuat);
      this.title.position.y = this.radius + 1.1 + Math.sin(this.elapsed * 1.3) * 0.08;
    }
  }

  /**
   * Spin each ring/core part about the vertical world axis. `rotateOnWorldAxis`
   * pivots about the object's own origin — this only spins about the sphere
   * centre because each part's origin is authored at the sphere centre in
   * Blender. If a ring ever orbits off-centre, that export invariant broke.
   */
  #animateStructure(delta) {
    if (!this.structure) return;
    const scale = this.active ? 0.45 : 1; // calmer while the player is inside
    for (let i = 0; i < this.structure.length; i++) {
      const part = this.structure[i];
      part.obj.rotateOnWorldAxis(WORLD_UP, delta * part.rate * part.dir * scale);
    }
  }

  /** Orient `mesh` to face the camera upright (no roll, no mirror) from any angle. */
  #faceCamera(mesh, parentInvQuat) {
    mesh.getWorldPosition(tmpLabelPos);
    tmpToCam.copy(this.camera.position).sub(tmpLabelPos);
    if (tmpToCam.lengthSq() < 1e-6) return;
    tmpToCam.normalize();

    tmpRight.crossVectors(WORLD_UP, tmpToCam);
    if (tmpRight.lengthSq() < 1e-4) tmpRight.set(1, 0, 0); // looking straight up/down
    tmpRight.normalize();
    tmpUp.crossVectors(tmpToCam, tmpRight).normalize();

    // Basis columns right(x), up(y), toCam(z): plane faces camera, +Y stays world-up.
    tmpBasis.makeBasis(tmpRight, tmpUp, tmpToCam);
    tmpWorldQuat.setFromRotationMatrix(tmpBasis);
    mesh.quaternion.copy(parentInvQuat).multiply(tmpWorldQuat);
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
    const worldWidth = isLarge ? 2.75 : isMedium ? 2.28 : 1.82;
    const worldHeight = isLarge ? 0.78 : isMedium ? 0.64 : 0.52;

    this.#drawBoard(ctx, canvas, item, isLarge, isMedium);

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;

    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      opacity: 1,
      depthTest: false,
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

  #drawCategoryIcon(ctx, category, cx, cy, r, ink) {
    ctx.save();
    ctx.strokeStyle = ink;
    ctx.fillStyle = ink;
    ctx.lineWidth = 3;
    ctx.beginPath();
    switch (category) {
      case 'Frontend': // orbit/atom — circle + ellipse
        ctx.arc(cx, cy, r * 0.35, 0, Math.PI * 2);
        ctx.moveTo(cx + r, cy);
        ctx.ellipse(cx, cy, r, r * 0.45, 0, 0, Math.PI * 2);
        ctx.stroke();
        break;
      case 'Backend & DB': // stacked database
        ctx.ellipse(cx, cy - r * 0.5, r * 0.8, r * 0.3, 0, 0, Math.PI * 2);
        ctx.moveTo(cx - r * 0.8, cy - r * 0.5);
        ctx.lineTo(cx - r * 0.8, cy + r * 0.5);
        ctx.moveTo(cx + r * 0.8, cy - r * 0.5);
        ctx.lineTo(cx + r * 0.8, cy + r * 0.5);
        ctx.ellipse(cx, cy + r * 0.5, r * 0.8, r * 0.3, 0, 0, Math.PI);
        ctx.stroke();
        break;
      case 'DevOps & Tools': // gear-ish cross + ring
        ctx.arc(cx, cy, r * 0.45, 0, Math.PI * 2);
        ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r);
        ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy);
        ctx.stroke();
        break;
      case 'CMS': // document
        ctx.rect(cx - r * 0.6, cy - r * 0.8, r * 1.2, r * 1.6);
        ctx.moveTo(cx - r * 0.3, cy - r * 0.3); ctx.lineTo(cx + r * 0.3, cy - r * 0.3);
        ctx.moveTo(cx - r * 0.3, cy + r * 0.1); ctx.lineTo(cx + r * 0.3, cy + r * 0.1);
        ctx.stroke();
        break;
      default: // Other — diamond
        ctx.moveTo(cx, cy - r);
        ctx.lineTo(cx + r, cy);
        ctx.lineTo(cx, cy + r);
        ctx.lineTo(cx - r, cy);
        ctx.closePath();
        ctx.stroke();
    }
    ctx.restore();
  }

  #drawBoard(ctx, canvas, item, isLarge, isMedium) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 18 : isMedium ? 13 : 9; // crisper than before
    ctx.fillStyle = 'rgba(20, 17, 11, 0.97)';          // warm charcoal, not cold black
    this.#roundRect(ctx, 28, 28, w - 56, h - 56, 28);
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = 'rgba(255, 246, 224, 0.05)';
    this.#roundRect(ctx, 44, 44, w - 88, h - 88, 22);
    ctx.fill();

    ctx.strokeStyle = item.color;
    ctx.lineWidth = isLarge ? 8 : isMedium ? 6 : 4;
    this.#roundRect(ctx, 34, 34, w - 68, h - 68, 24);
    ctx.stroke();

    // Category chip: icon + word, color + shape + text (accessible triple-encode).
    const chipW = 196;
    const chipH = 40;
    ctx.fillStyle = item.color;
    this.#roundRect(ctx, 54, 48, chipW, chipH, 16);
    ctx.fill();
    const ink = '#0c0f0a';
    this.#drawCategoryIcon(ctx, item.category, 54 + 24, 48 + chipH / 2, 11, ink);
    ctx.fillStyle = ink;
    ctx.font = '900 20px Rajdhani, Inter, Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.#shortCategory(item.category), 54 + 46, 48 + chipH / 2 + 1);

    let fontSize = isLarge ? 78 : isMedium ? 66 : 56;
    ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    while (ctx.measureText(item.label).width > w - 132 && fontSize > 34) {
      fontSize -= 4;
      ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    }
    ctx.lineWidth = isLarge ? 8 : 6;
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.9)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.strokeText(item.label, w / 2, h / 2 + 24);
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 14 : 10;
    ctx.fillStyle = '#f6f1df';
    ctx.fillText(item.label, w / 2, h / 2 + 24);
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
      <span class="skill-sphere-controls">drag to look · scroll to zoom</span>
      <span class="skill-sphere-exit">ESC to return</span>
    `;
    document.body.appendChild(this.hintEl);
  }

  #setHint(show) {
    if (!this.hintEl) return;
    this.hintEl.classList.toggle('hidden', !show);
  }

  #collectStructure() {
    this.structure = [];
    // Emissive baselines consumed by the day/night glow cross-fade (#applyTimeOfDay).
    this.ringMaterials = [];
    for (const spec of STRUCTURE_SPIN) {
      const obj = this.scene.getObjectByName(spec.name);
      if (!obj) continue;
      this.structure.push({ obj, rate: spec.rate, dir: spec.dir });
      obj.traverse((node) => {
        if (!node.isMesh || !node.material) return;
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        for (const mat of mats) {
          // Recolor the green Blender glow to the Observatory identity. Default to
          // the night tint at load; #applyTimeOfDay swaps to the morning tint when
          // the mode is day. Track both tints + the base glow for the cross-fade.
          if (mat.emissive) mat.emissive.set(spec.night);
          if (mat.color) mat.color.set(spec.night);
          this.ringMaterials.push({
            mat,
            base: mat.emissiveIntensity ?? 1,
            night: spec.night,
            day: spec.day,
          });
        }
      });
    }
    // Subset kept visible-but-dimmed inside (they sit at the camera origin).
    const coreNames = ['skillSphere_core_inner', 'skillSphere_core_halo', 'skillSphere_energy_column'];
    this.coreVisuals = coreNames
      .map((n) => this.scene.getObjectByName(n))
      .filter(Boolean);
  }

  #setCoreVisible(visible) {
    // The core/halo/column sit AT the camera origin inside the sphere; even
    // dimmed they bloom and flood the whole view green (and look identical
    // day/night since it's the sphere's own geometry, not the sky). Hide them
    // outright while inside — the orbiting rings (NOT in this list) stay
    // visible and spinning as the living structure around the player.
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
    controls.minPolarAngle = Math.PI * 0.02;
    controls.maxPolarAngle = Math.PI * 0.98;
    controls.minDistance = 0.1;
    controls.maxDistance = 4.0; // pull back toward the shell for parallax + zoom
    controls.azimuthAngle = Math.atan2(direction.x, direction.z);
    controls.polarAngle = Math.PI * 0.5;
    controls.distance = 0.1;
    this._idleClock = 0;
    this._driftAzimuth = controls.azimuthAngle;
    this.#bindDriftListeners(controls);
  }

  // User input resets the idle timer. We listen to camera-controls' own events
  // because programmatic azimuth writes (the drift) do NOT fire them — so the
  // drift can't mistake its own motion for the user, the way a damped-getter
  // diff would.
  #bindDriftListeners(controls) {
    if (this._driftBound) return;
    if (!this._onUserControl) this._onUserControl = () => { this._idleClock = 0; };
    controls.addEventListener('controlstart', this._onUserControl);
    controls.addEventListener('control', this._onUserControl);
    controls.addEventListener('controlend', this._onUserControl);
    this._driftBound = true;
  }

  #unbindDriftListeners() {
    const controls = this.playerCamera?.controls;
    if (!this._driftBound || !controls || !this._onUserControl) return;
    controls.removeEventListener('controlstart', this._onUserControl);
    controls.removeEventListener('control', this._onUserControl);
    controls.removeEventListener('controlend', this._onUserControl);
    this._driftBound = false;
  }

  #restoreInsideControlLimits() {
    this.#unbindDriftListeners();
    const controls = this.playerCamera?.controls;
    const saved = this._savedControlLimits;
    if (!controls || !saved) return;
    controls.minPolarAngle = saved.minPolarAngle;
    controls.maxPolarAngle = saved.maxPolarAngle;
    controls.minDistance = saved.minDistance;
    controls.maxDistance = saved.maxDistance;
    this._savedControlLimits = null;
  }

  #setInsideProjection(enabled) {
    if (!this.camera?.isPerspectiveCamera) return;
    if (enabled) {
      if (this._savedFov == null) this._savedFov = this.camera.fov;
      gsap.to(this.camera, {
        fov: 64,
        duration: 0.85,
        ease: 'power2.out',
        onUpdate: () => this.camera.updateProjectionMatrix(),
      });
    } else if (this._savedFov != null) {
      gsap.to(this.camera, {
        fov: this._savedFov,
        duration: 0.55,
        ease: 'power2.inOut',
        onUpdate: () => this.camera.updateProjectionMatrix(),
        onComplete: () => {
          this.camera.fov = this._savedFov;
          this.camera.updateProjectionMatrix();
          this._savedFov = null;
        },
      });
    }
  }

  #applyInsideCamera(delta) {
    const controls = this.playerCamera?.controls;
    if (controls) controls.update(delta);

    // Idle auto-drift: 2.5s after the last user input, slowly rotate the view so
    // the look-around affordance is obvious. We advance our OWN azimuth target
    // (not the damped getter) so the motion is smooth and never self-cancels.
    if (controls) {
      this._idleClock = (this._idleClock ?? 0) + delta;
      if (this._idleClock > 2.5) {
        this._driftAzimuth = (this._driftAzimuth ?? controls.azimuthAngle) + delta * 0.06;
        controls.azimuthAngle = this._driftAzimuth;
      } else {
        this._driftAzimuth = controls.azimuthAngle; // stay synced until drift resumes
      }
    }

    const azimuth = controls?.azimuthAngle ?? 0;
    const polar = controls?.polarAngle ?? Math.PI * 0.5;
    const distance = controls?.distance ?? 0.1;
    const sinPolar = Math.sin(polar);
    tmpDir.set(sinPolar * Math.sin(azimuth), Math.cos(polar), sinPolar * Math.cos(azimuth));

    // Camera sits offset back from centre along -viewDir, looks at the far shell.
    this.camera.position.copy(this.center).addScaledVector(tmpDir, -distance);
    this.camera.lookAt(tmpLook.copy(this.center).addScaledVector(tmpDir, this.radius));
  }

  /** React to the binary day/night mode (the same `mode` TorchLight reads). */
  #applyTimeOfDay(mode) {
    if (mode === this._todMode) return;
    this._todMode = mode;
    const night = mode === 'night';
    // Night: gold/teal beacon, brighter glow. Morning: bold orange/rose so the
    // rings stay visible against the blue sky. Cross-fade both hue and glow.
    const glowMul = night ? 1.5 : 1.15;
    for (const entry of this.ringMaterials ?? []) {
      const { mat, base, night: nightHex, day: dayHex } = entry;
      gsap.to(mat, { emissiveIntensity: base * glowMul, duration: 1.2, ease: 'power2.inOut' });
      tmpColor.set(night ? nightHex : dayHex);
      const rgb = { r: tmpColor.r, g: tmpColor.g, b: tmpColor.b };
      if (mat.emissive) gsap.to(mat.emissive, { ...rgb, duration: 1.2, ease: 'power2.inOut' });
      if (mat.color) gsap.to(mat.color, { ...rgb, duration: 1.2, ease: 'power2.inOut' });
    }
    gsap.to(this, { _todCardScale: night ? 0.88 : 1, duration: 1.2, ease: 'power2.inOut' });
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
