import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { portfolio } from './PortfolioData.js';

// All anchors are expressed in root_projectsHut LOCAL space (the marker that
// survives the areas spatial-merge), measured from the authored geometry in
// areas.glb. Applying them through the marker's live world matrix keeps the
// interaction correct even if the hut is ever repositioned.
//   SCREEN_LOCAL    — centre of projectHut_screen_panel (the project board)
//   SCREEN_NORMAL   — the panel's facing axis (points out the door / toward the
//                     approaching player); the camera views the board from here
//   DOOR_LOCAL      — arch centre, the camera fly-through waypoint
//   BODY_*          — solid collider box covering the hut walls (door side at
//                     the front face so the porch stays walkable)
const SCREEN_LOCAL = new THREE.Vector3(0.0637, -0.4727, 0.5496);
const SCREEN_NORMAL_LOCAL = new THREE.Vector3(0.0698, 0, -0.9976);
const DOOR_LOCAL = new THREE.Vector3(0.1615, -0.8927, -0.8483);

// Per-mesh solid colliders for the hut + its entrance, baked from areas.glb
// geometry in root_projectsHut LOCAL space: [cx, cy, cz, hx, hy, hz] (centre +
// half-extents). Covers walls, corner posts, all buttress tiers, arch jambs,
// foundation edges, recess sides/back, steps, porch, and the flagstone path —
// the doorway is left OPEN (gap between the two front-wall halves). Applied
// through the marker's live world matrix so they track the hut if it moves.
// (root is unrotated + unit-scale; AABBs are tight.)
const HUT_COLLIDERS = [
  [1.388, -0.893, -0.763, 0.202, 0.71, 0.255],
  [-1.065, -0.893, -0.934, 0.202, 0.71, 0.255],
  [-4.121, -0.543, 4.013, 0.427, 0.25, 0.427],
  [-4.426, -1.693, 4.278, 0.725, 0.4, 0.725],
  [-4.273, -1.043, 4.145, 0.565, 0.31, 0.565],
  [-3.761, -0.543, -1.123, 0.427, 0.25, 0.427],
  [-4.027, -1.693, -1.428, 0.725, 0.4, 0.725],
  [-3.894, -1.043, -1.275, 0.565, 0.31, 0.565],
  [3.725, -0.543, 4.561, 0.427, 0.25, 0.427],
  [3.991, -1.693, 4.867, 0.725, 0.4, 0.725],
  [3.858, -1.043, 4.714, 0.565, 0.31, 0.565],
  [4.084, -0.543, -0.574, 0.427, 0.25, 0.427],
  [4.39, -1.693, -0.839, 0.725, 0.4, 0.725],
  [4.237, -1.043, -0.707, 0.565, 0.31, 0.565],
  [0.351, -2.033, -3.559, 0.982, 0.06, 0.849],
  [1.215, -2.033, -4.645, 0.796, 0.06, 0.73],
  [-0.213, -2.033, -5.748, 0.87, 0.06, 0.771],
  [1.08, -2.033, -6.805, 0.73, 0.06, 0.796],
  [0.1, -2.033, -8.163, 0.903, 0.06, 0.737],
  [1.035, -2.033, -9.245, 0.758, 0.06, 0.692],
  [4.775, -1.853, 2.055, 0.422, 0.15, 3.394],
  [-4.811, -1.853, 1.384, 0.422, 0.15, 3.394],
  [2.725, -0.313, -0.612, 1.38, 1.5, 0.253],
  [-2.41, -0.313, -0.971, 1.38, 1.5, 0.253],
  [3.891, -0.313, 1.993, 0.336, 1.5, 2.579],
  [-4.155, -0.393, 1.43, 0.125, 1.2, 0.165],
  [4.119, -0.393, 2.009, 0.125, 1.2, 0.165],
  [0.191, -1.653, -1.276, 1.889, 0.1, 0.629],
  [-4.163, -0.353, 4.01, 0.198, 1.6, 0.198],
  [-3.804, -0.353, -1.126, 0.198, 1.6, 0.198],
  [3.768, -0.353, 4.564, 0.198, 1.6, 0.198],
  [4.127, -0.353, -0.571, 0.198, 1.6, 0.198],
  [0.052, -0.433, 0.721, 1.292, 1.16, 0.204],
  [1.39, -0.743, 0.026, 0.174, 1.15, 0.864],
  [-1.177, -0.743, -0.154, 0.174, 1.15, 0.864],
  [-3.927, -0.313, 1.446, 0.336, 1.5, 2.579],
  [-3.984, -1.673, 1.442, 0.368, 0.1, 2.623],
  [3.948, -1.673, 1.997, 0.368, 0.1, 2.623],
  [0.299, -1.953, -2.817, 1.822, 0.14, 0.681],
  [0.239, -1.793, -1.961, 1.533, 0.14, 0.604],
  // Floor pads — without these the player drops through the open door onto
  // terrain (~0.5 m below the stone floor) and sinks in. recess_floor is the
  // raised inner floor at the screen (top ≈0.58); foundation_stone_slab is the
  // platform base under the whole hut (top ≈0.22).
  [0.107, -1.573, -0.064, 1.429, 0.06, 0.952],
  [-0.018, -1.973, 1.719, 4.873, 0.1, 3.705],
];

const tmpVec = new THREE.Vector3();
const tmpVec2 = new THREE.Vector3();
const tmpQuat = new THREE.Quaternion();
const tmpScale = new THREE.Vector3();
const tmpEuler = new THREE.Euler();

/**
 * Runtime "enter the projects hut" interaction.
 *
 * Blender owns the hut shell (root_projectsHut) + an open stone archway — there
 * is no door leaf to swing, so entering is a cinematic camera dolly THROUGH the
 * arch onto the interior project board, then a smooth return on Escape. The
 * player stays put outside; only the camera travels.
 *
 * The board reuses ProjectShowcase's canvas layout (screenshot + name + counter
 * + tech pills + arrows), painted onto our own plane mounted just in front of
 * the authored projectHut_screen_panel (which is spatially merged at load and
 * can't be repainted by name).
 *
 * Also installs the hut's solid collider — areas ships no hut proxy in
 * colliders.glb, so without this the player walks straight through the walls.
 *
 * Lifecycle mirrors SkillSphere: near() → enter() → prev()/next() → exit().
 */
export class ProjectsHut {
  static DOOR_PROXIMITY = 5.5;  // m — prompt shows from the porch/steps
  static ENTER_DURATION = 1.4;  // s — dolly in through the arch
  static EXIT_DURATION = 1.1;   // s — dolly back to the player
  static STANDOFF = 1.35;       // m — camera distance from the board, inside
  static SCREEN_WIDTH = 1.5;    // m — sized to fit the recessed alcove
  static SCREEN_HEIGHT = 0.9;   // m — 5:3 to match the screenshot framing
  static FADE_DURATION = 0.18;  // s — cross-fade between projects

  constructor({
    scene,
    camera,
    player,
    playerCamera,
    controller,
    refs,
    physics = null,
    postfx = null,
    audio = null,
    achievements = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.physics = physics;
    this.postfx = postfx;
    this.audio = audio;
    this.achievements = achievements;

    this.projects = portfolio.projects;
    this.currentIndex = 0;

    this.hutRoot = refs?.markers?.projectsHut ?? null;
    this.ready = !!this.hutRoot;
    this.active = false;
    this.zooming = false;
    this.transitioning = false;
    this._near = false;

    if (!this.ready) {
      console.warn('[ProjectsHut] markers.projectsHut missing; hut interaction skipped');
      return;
    }

    // Resolve every anchor through the marker's live world matrix.
    this.hutRoot.updateWorldMatrix(true, false);
    const m = this.hutRoot.matrixWorld;
    this.hutRoot.getWorldQuaternion(tmpQuat);

    this.boardPos = SCREEN_LOCAL.clone().applyMatrix4(m);
    this.boardNormal = SCREEN_NORMAL_LOCAL.clone().applyQuaternion(tmpQuat).normalize();
    this.doorPoint = DOOR_LOCAL.clone().applyMatrix4(m);
    this.doorPoint.y = this.boardPos.y; // fly-through at board eye height

    this.camStandoff = this.boardPos
      .clone()
      .addScaledVector(this.boardNormal, ProjectsHut.STANDOFF);
    this.camStandoff.y = this.boardPos.y;

    this.#buildScreen();
    this.#installCollider();
    this.#installDom();
    this.#applyIndex(0, /* immediate */ true);
    this.#kickOffImagePreload();
  }

  // ── Proximity ──────────────────────────────────────────────────────────────

  near(playerPosition) {
    if (!this.ready || this.active || this.zooming || !playerPosition) return false;
    const dx = playerPosition.x - this.doorPoint.x;
    const dz = playerPosition.z - this.doorPoint.z;
    this._near =
      dx * dx + dz * dz <= ProjectsHut.DOOR_PROXIMITY * ProjectsHut.DOOR_PROXIMITY;
    return this._near;
  }

  // ── Enter / exit ─────────────────────────────────────────────────────────

  enter() {
    if (!this.ready || this.active || this.zooming) return;
    this.active = true;
    this.zooming = true;
    this._near = false;
    this.audio?.playMenuOpen?.();
    this.achievements?.onSectionVisited?.('projects');
    this.achievements?.onProjectViewed?.(this.projects[this.currentIndex]?.name);

    if (this.controller) this.controller.paused = true;
    if (this.playerCamera) this.playerCamera.locked = true;
    if (this.player?.character?.root) this.player.character.root.visible = false;
    this.#suppressPostFX(true);

    if (!this._returnPos) {
      this._returnPos = new THREE.Vector3();
      this._returnLook = new THREE.Vector3();
    }
    this._returnPos.copy(this.camera.position);
    this.camera.getWorldDirection(tmpVec);
    this._returnLook.copy(this._returnPos).add(tmpVec);

    this.#showHint(true);
    this.#dolly(this._returnPos, this._returnLook, this.camStandoff, this.boardPos, {
      duration: ProjectsHut.ENTER_DURATION,
      onComplete: () => { this.zooming = false; },
    });
  }

  exit() {
    if (!this.ready || (!this.active && !this.zooming)) return;
    this.active = false;
    this.zooming = true;
    this.audio?.playMenuClose?.();
    this.#showHint(false);

    const fromPos = this.camera.position.clone();
    this.camera.getWorldDirection(tmpVec);
    const fromLook = fromPos.clone().add(tmpVec);

    this.#dolly(fromPos, fromLook, this._returnPos, this._returnLook, {
      duration: ProjectsHut.EXIT_DURATION,
      onComplete: () => {
        this.zooming = false;
        this.#suppressPostFX(false);
        if (this.controller) this.controller.paused = false;
        if (this.playerCamera) {
          this.playerCamera.locked = false;
          this.playerCamera.resync();
        }
        if (this.player?.character?.root) this.player.character.root.visible = true;
      },
    });
  }

  /** Cut bloom + tilt-shift while inside so the board reads clean, restore on exit. */
  #suppressPostFX(inside) {
    if (!this.postfx) return;
    if (inside) {
      if (this._savedBloom == null) this._savedBloom = this.postfx.bloomStrength ?? 0.3;
      if (this._savedTilt == null) this._savedTilt = this.postfx.tiltShiftAmount ?? 1.0;
      this.postfx.bloomStrength = 0.02;
      this.postfx.tiltShiftAmount = 0;
    } else {
      if (this._savedBloom != null) this.postfx.bloomStrength = this._savedBloom;
      if (this._savedTilt != null) this.postfx.tiltShiftAmount = this._savedTilt;
      this._savedBloom = null;
      this._savedTilt = null;
    }
  }

  /**
   * Fly the camera straight between two poses, easing position and look-target
   * in lockstep so the move reads as a smooth push-in with no backward swing.
   * (A curved 3-point path overshoots on its end tangents — hence the straight
   * line; the camera clipping through a wall mid-move is invisible.)
   */
  #dolly(fromPos, fromLook, toPos, toLook, { duration, onComplete }) {
    const lookProxy = fromLook.clone();
    gsap.killTweensOf(this.camera.position);
    gsap.killTweensOf(lookProxy);
    gsap.to(lookProxy, {
      x: toLook.x, y: toLook.y, z: toLook.z,
      duration, ease: 'power2.inOut',
    });
    gsap.to(this.camera.position, {
      x: toPos.x, y: toPos.y, z: toPos.z,
      duration,
      ease: 'power2.inOut',
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.camera.position.copy(toPos);
        this.camera.lookAt(toLook);
        onComplete?.();
      },
    });
  }

  // ── Project navigation ─────────────────────────────────────────────────────

  next() {
    if (!this.ready || this.transitioning) return;
    this.#applyIndex((this.currentIndex + 1) % this.projects.length);
  }

  prev() {
    if (!this.ready || this.transitioning) return;
    const n = this.projects.length;
    this.#applyIndex((this.currentIndex - 1 + n) % n);
  }

  update() {
    // Static board + gsap-driven camera — nothing per-frame. Kept for tick parity.
  }

  // ── Collider ───────────────────────────────────────────────────────────────

  #installCollider() {
    if (!this.physics?.addStaticCuboid) return;
    this.hutRoot.matrixWorld.decompose(tmpVec, tmpQuat, tmpScale);
    const yaw = tmpEuler.setFromQuaternion(tmpQuat, 'YXZ').y;
    const m = this.hutRoot.matrixWorld;
    for (const [cx, cy, cz, hx, hy, hz] of HUT_COLLIDERS) {
      tmpVec2.set(cx, cy, cz).applyMatrix4(m);
      this.physics.addStaticCuboid(
        tmpVec2.x, tmpVec2.y, tmpVec2.z,
        hx * tmpScale.x, hy * tmpScale.y, hz * tmpScale.z,
        yaw,
      );
    }
  }

  // ── Screen (canvas board) ────────────────────────────────────────────────

  #buildScreen() {
    this.canvasScale = 2;
    this.logicalW = 1024;
    this.logicalH = 614;
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.logicalW * this.canvasScale;
    this.canvas.height = this.logicalH * this.canvasScale;
    this.ctx = this.canvas.getContext('2d');

    const tex = new THREE.CanvasTexture(this.canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 16;
    this.texture = tex;

    this.screenMat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: false,
      depthWrite: true,
      opacity: 1,
    });

    // Dark backdrop behind the board: occludes the bright interior glows /
    // windows so the project images read with contrast instead of washing out.
    // Unlit + matte so PostFX bloom doesn't grab it.
    this.backdrop = new THREE.Mesh(
      new THREE.PlaneGeometry(ProjectsHut.SCREEN_WIDTH + 1.7, ProjectsHut.SCREEN_HEIGHT + 1.1),
      new THREE.MeshBasicMaterial({ color: 0x07090a }),
    );
    this.backdrop.name = 'projects-hut-backdrop';
    this.backdrop.position.copy(this.boardPos);
    this.backdrop.lookAt(tmpVec.copy(this.backdrop.position).add(this.boardNormal));
    this.scene.add(this.backdrop);

    this.screen = new THREE.Mesh(
      new THREE.PlaneGeometry(ProjectsHut.SCREEN_WIDTH, ProjectsHut.SCREEN_HEIGHT),
      this.screenMat,
    );
    this.screen.name = 'projects-hut-board';
    // Sit just in front of the backdrop (toward the camera) to avoid z-fight.
    this.screen.position.copy(this.boardPos).addScaledVector(this.boardNormal, 0.05);
    // PlaneGeometry's front face is +Z — aim it along the board normal (out the door).
    this.screen.lookAt(tmpVec.copy(this.screen.position).add(this.boardNormal));
    this.scene.add(this.screen);
  }

  #applyIndex(index, immediate = false) {
    this.currentIndex = index;
    if (immediate) {
      this.#renderCanvas(index);
      this.screenMat.opacity = 1;
      this.screenMat.transparent = false;
      return;
    }
    this.transitioning = true;
    this.screenMat.transparent = true;
    gsap.to(this.screenMat, {
      opacity: 0.2,
      duration: ProjectsHut.FADE_DURATION,
      ease: 'power2.out',
      onComplete: () => {
        this.#renderCanvas(index);
        gsap.to(this.screenMat, {
          opacity: 1,
          duration: ProjectsHut.FADE_DURATION,
          ease: 'power2.out',
          onComplete: () => {
            this.screenMat.transparent = false;
            this.transitioning = false;
          },
        });
      },
    });
  }

  #kickOffImagePreload() {
    for (const project of this.projects) {
      if (!project.image || project._loadedImage) continue;
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        project._loadedImage = img;
        if (this.projects[this.currentIndex] === project) this.#renderCanvas(this.currentIndex);
      };
      img.onerror = () => { /* silent — falls back to accent block */ };
      img.src = project.image;
    }
  }

  /** Paint the board for a project — same layout as ProjectShowcase. */
  #renderCanvas(index) {
    const project = this.projects[index];
    const ctx = this.ctx;
    const w = this.logicalW;
    const h = this.logicalH;
    const imageH = Math.floor(h * 0.74);

    ctx.setTransform(this.canvasScale, 0, 0, this.canvasScale, 0, 0);

    ctx.fillStyle = '#1a1a2a';
    ctx.fillRect(0, 0, w, h);

    const img = project._loadedImage;
    if (img && img.naturalWidth > 0) {
      const areaAR = w / imageH;
      const srcAR = img.naturalWidth / img.naturalHeight;
      let dx, dy, dw, dh;
      if (srcAR >= areaAR) {
        dw = w; dh = w / srcAR; dx = 0; dy = (imageH - dh) / 2;
      } else {
        dh = imageH; dw = imageH * srcAR; dx = (w - dw) / 2; dy = 0;
      }
      ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, dx, dy, dw, dh);
    } else {
      ctx.fillStyle = project.color || '#2a3a5a';
      ctx.fillRect(0, 0, w, imageH);
    }

    // Dim the screenshot — many project pages are near-white and blow out the
    // view from inside the dark hut. Knock brightness down so it reads calmly.
    ctx.fillStyle = 'rgba(8, 10, 16, 0.40)';
    ctx.fillRect(0, 0, w, imageH);

    const fadeH = 40;
    const grad = ctx.createLinearGradient(0, imageH - fadeH, 0, imageH);
    grad.addColorStop(0, 'rgba(26, 26, 42, 0)');
    grad.addColorStop(1, 'rgba(26, 26, 42, 1)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, imageH - fadeH, w, fadeH);

    ctx.fillStyle = project.color || '#ffd28a';
    ctx.fillRect(40, imageH + 14, 64, 6);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 44px Oswald, "Arial Black", sans-serif';
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillText(project.name, 40, imageH + 28);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '24px Oswald, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${index + 1} / ${this.projects.length}`, w - 40, imageH + 40);
    ctx.textAlign = 'left';

    const tags = project.tech || [];
    ctx.font = `600 22px Rajdhani, sans-serif`;
    let tagX = 40;
    const tagY = imageH + 92;
    const tagH = 38;
    const padX = 14;
    const padY = 8;
    for (const tech of tags) {
      const textW = ctx.measureText(tech).width;
      const pillW = textW + padX * 2;
      if (tagX + pillW > w - 40) break;
      ctx.fillStyle = 'rgba(170, 238, 68, 0.22)';
      this.#drawRoundedRect(ctx, tagX, tagY, pillW, tagH, 9);
      ctx.fill();
      ctx.fillStyle = '#bbf055';
      ctx.fillText(tech, tagX + padX, tagY + padY + 1);
      tagX += pillW + 10;
    }

    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.font = 'bold 40px sans-serif';
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    ctx.fillText('◀', 12, imageH / 2);
    ctx.textAlign = 'right';
    ctx.fillText('▶', w - 12, imageH / 2);

    ctx.textBaseline = 'alphabetic';
    ctx.textAlign = 'left';

    this.texture.needsUpdate = true;
  }

  #drawRoundedRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    if (typeof ctx.roundRect === 'function') {
      ctx.roundRect(x, y, w, h, r);
      return;
    }
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  // ── DOM hint ────────────────────────────────────────────────────────────

  #installDom() {
    this.hintEl = document.createElement('div');
    this.hintEl.className = 'skill-sphere-hint hidden';
    this.hintEl.innerHTML = `
      <span class="skill-sphere-kicker">Inside Projects</span>
      <strong>Browse the work</strong>
      <span class="skill-sphere-controls">← / → to change project</span>
      <span class="skill-sphere-exit">ESC to return</span>
    `;
    document.body.appendChild(this.hintEl);
  }

  #showHint(show) {
    if (!this.hintEl) return;
    this.hintEl.classList.toggle('hidden', !show);
  }
}
