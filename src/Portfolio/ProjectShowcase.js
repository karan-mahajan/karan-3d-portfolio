import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { portfolio } from './PortfolioData.js';

/**
 * Single cycling project showcase. Mounts onto refShowcaseMount in the
 * workshop pavilion (Blender Phase 4). Preserves Billboards.js public API
 * so Interaction.js + TimeOfDay.js + ActionPrompts.js work unchanged.
 *
 * Visual: one 5×3m screen mesh painted with a per-project canvas (image +
 * name + summary + tags + arrows + counter). Canvas re-baked when
 * setIndex() rotates content.
 *
 * Public API (matches Billboards.js):
 *   .items[]            — single-entry: { index, position, accent, project,
 *                                          screen, group, emissiveMultiplier }
 *   .projects           — portfolio.projects array
 *   .emissiveBoost      — TimeOfDay lerps this up at night
 *   .focused            — Interaction sets via setFocused()
 *   .transitioning      — true during the cross-fade tween
 *   .update(elapsed, playerPos, delta)
 *   .setIndex(i)
 *   .setFocused(focused)
 *   .closestWithin(playerPos, radius)
 */
export class ProjectShowcase {
  static AUTO_ROTATE_SECONDS = 0; // 0 = auto-rotate disabled; user cycles via Prev/Next in the focused modal
  static NEAR_PAUSE_RADIUS = 8;
  static FADE_DURATION = 0.18;
  static SCREEN_WIDTH = 4;       // narrower than the pavilion's front opening so left/right pillars don't clip it
  static SCREEN_HEIGHT = 2.4;    // 5:3 aspect ratio preserved
  static SCREEN_FORWARD_OFFSET = 1.0; // pushes the screen forward of the back wall + past the pavilion's front pillars (which stick ~0.8m into the room from the wall)
  static SCREEN_VERTICAL_OFFSET = 0;  // raise/lower the screen relative to the mount; mount is already at chest height

  constructor(scene, refs, loader = null, terrain = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;

    this.projects = portfolio.projects;
    this.currentIndex = 0;
    this.transitioning = false;
    this.focused = false;
    this._autoTimer = 0;
    this._playerNearby = false;
    // Day=1.0 baseline. TimeOfDay lerps this up at night for the night-pop.
    this.emissiveBoost = 1.0;

    const mount = refs?.interaction?.showcaseMount;
    if (!mount) {
      // Hard-fail loudly per CLAUDE.md Rule 1 — never invent positions.
      // Phase 1 boot assertion should catch this earlier; this is a safety
      // net so we don't silently render a screen at the origin.
      console.error(
        '[ProjectShowcase] refShowcaseMount missing from glb refs — '
        + 'showcase will NOT render. This usually means world.glb did not '
        + 'include refShowcaseMount.',
      );
      this.items = [];
      this.group = null;
      return;
    }

    this.group = new THREE.Group();
    this.group.name = 'project-showcase';
    this.group.position.copy(mount.position);
    // PlaneGeometry's front normal is +Z, but Blender empties default to a
    // +Y forward — copying the empty's rotation directly aims the screen
    // into the back wall. Compute yaw so the front face points toward
    // world origin (matches old Billboards.js behaviour).
    this.group.rotation.set(
      0,
      Math.atan2(-mount.position.x, -mount.position.z),
      0,
    );
    this.scene.add(this.group);

    this.items = [];
    this.#buildScreen();
    this.#applyIndex(0, /*immediate*/ true);
    // Project screens aren't visible until the player walks up to them, so the
    // art must NOT compete with the world's assets during boot. Preload when
    // the browser is idle (after the critical load), not in the constructor.
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback(() => this.#kickOffImagePreload(), { timeout: 8000 });
    } else {
      setTimeout(() => this.#kickOffImagePreload(), 4000);
    }
  }

  // ── Build ────────────────────────────────────────────────────────────────

  #buildScreen() {
    // Canvas allocated at 2× logical resolution so text + image stay crisp
    // when the player zooms in to ~3 m from the 5×3 m screen. ctx.scale()
    // makes every draw call use the logical grid regardless of physical res.
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

    // MeshBasicMaterial — the showcase screen reads at any time of day
    // independent of scene lighting. transparent flips on during cross-fade
    // tweens and back off when the tween settles.
    this.screenMat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: false,
      depthWrite: true,
      opacity: 1,
    });

    const screen = new THREE.Mesh(
      new THREE.PlaneGeometry(ProjectShowcase.SCREEN_WIDTH, ProjectShowcase.SCREEN_HEIGHT),
      this.screenMat,
    );
    screen.name = 'project-showcase-screen';
    // The mount empty was authored at the back wall — push the screen along
    // its local +Z (its front-face normal, which we've yawed toward origin)
    // so it sits in front of both the back wall and the pillars. Without
    // this the screen z-fights with the wall and gets clipped by pillars
    // co-planar with it.
    screen.position.set(0, ProjectShowcase.SCREEN_VERTICAL_OFFSET, ProjectShowcase.SCREEN_FORWARD_OFFSET);
    this.group.add(screen);
    this.screen = screen;
  }

  // ── Image preload ────────────────────────────────────────────────────────

  /**
   * Kick off image loading for every project. Each image is cached on the
   * project object as `_loadedImage`. As soon as the current project's
   * image is ready, the canvas re-renders. Failures are silent — the
   * fallback is the accent color background.
   */
  #kickOffImagePreload() {
    for (const project of this.projects) {
      if (!project.image) continue;
      if (project._loadedImage) continue; // already preloaded
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        project._loadedImage = img;
        if (this.projects[this.currentIndex] === project) {
          this.#renderCanvas(this.currentIndex);
        }
      };
      img.onerror = () => { /* silent — falls back to accent block */ };
      img.src = project.image;
    }
  }

  // ── Public API ───────────────────────────────────────────────────────────

  /** Jump to a specific index (auto-rotate, dot-nav, or Interaction.cycle). */
  setIndex(index) {
    if (this.transitioning) return;
    const n = this.projects.length;
    const next = ((index % n) + n) % n;
    if (next === this.currentIndex) return;
    this.#applyIndex(next);
  }

  /** Advance to the next project. */
  next() {
    if (this.transitioning) return;
    const n = this.projects.length;
    this.#applyIndex((this.currentIndex + 1) % n);
  }

  /** Step back to the previous project. */
  prev() {
    if (this.transitioning) return;
    const n = this.projects.length;
    this.#applyIndex((this.currentIndex - 1 + n) % n);
  }

  /** Interaction.js calls this when the proximity prompt opens / closes. */
  setFocused(focused) {
    this.focused = !!focused;
    if (this.focused) {
      this._autoTimer = 0;
      if (this.transitioning) {
        gsap.killTweensOf(this.screenMat);
        this.screenMat.opacity = 1;
        this.screenMat.transparent = false;
        this.transitioning = false;
        this.#renderCanvas(this.currentIndex);
      }
    }
  }

  /** Closest item within `radius` of the player's XZ. The single showcase
   *  always returns items[0] (or null) — keeps signature parity with the
   *  old multi-billboard implementation. */
  closestWithin(playerPos, radius) {
    const item = this.items[0];
    if (!item) return null;
    const dx = item.position.x - playerPos.x;
    const dz = item.position.z - playerPos.z;
    const d = Math.hypot(dx, dz);
    return d < radius ? item : null;
  }

  /**
   * Per-frame proximity + auto-rotate driver. Called from World.update.
   * Outside NEAR_PAUSE_RADIUS *and* not focused → advance every
   * AUTO_ROTATE_SECONDS.
   */
  update(elapsed, playerPos = null, delta = 0) {
    if (!this.items[0]) return;
    if (ProjectShowcase.AUTO_ROTATE_SECONDS <= 0) return; // auto-rotate disabled
    if (this.focused) {
      this._autoTimer = 0;
      return;
    }
    if (playerPos) {
      const dx = playerPos.x - this.items[0].position.x;
      const dz = playerPos.z - this.items[0].position.z;
      this._playerNearby = (dx * dx + dz * dz)
        < (ProjectShowcase.NEAR_PAUSE_RADIUS * ProjectShowcase.NEAR_PAUSE_RADIUS);
      if (this._playerNearby || this.transitioning) {
        this._autoTimer = 0;
        return;
      }
    }
    this._autoTimer += delta;
    if (this._autoTimer >= ProjectShowcase.AUTO_ROTATE_SECONDS) {
      this._autoTimer = 0;
      this.next();
    }
  }

  // ── Internals ────────────────────────────────────────────────────────────

  #applyIndex(index, immediate = false) {
    this.currentIndex = index;
    const project = this.projects[index];

    // Single-entry items[] — mutate in place so other systems holding the
    // reference see the new project on their next read. We rebuild the
    // entry the first time through (items is empty), then mutate fields
    // on subsequent calls.
    if (this.items.length === 0) {
      this.items.push({
        index,
        project,
        group: this.group,
        screen: this.screen,
        // Position is the showcase mount XZ — used by Interaction.js,
        // ActionPrompts, Achievements proximity, StreetLights aim, etc.
        position: this.group.position.clone(),
        accent: new THREE.Color(project.color || '#ffffff'),
        emissiveMultiplier: 0.4,
      });
    } else {
      const item = this.items[0];
      item.index = index;
      item.project = project;
      item.accent.set(project.color || '#ffffff');
    }

    if (immediate) {
      this.#renderCanvas(index);
      this.screenMat.opacity = 1;
      this.screenMat.transparent = false;
      return;
    }

    // Brief cross-fade — fade out, swap canvas content, fade back in.
    this.transitioning = true;
    this.screenMat.transparent = true;
    gsap.to(this.screenMat, {
      opacity: 0.2,
      duration: ProjectShowcase.FADE_DURATION,
      ease: 'power2.out',
      onComplete: () => {
        this.#renderCanvas(index);
        gsap.to(this.screenMat, {
          opacity: 1,
          duration: ProjectShowcase.FADE_DURATION,
          ease: 'power2.out',
          onComplete: () => {
            this.screenMat.transparent = false;
            this.transitioning = false;
          },
        });
      },
    });
  }

  /**
   * Paint the canvas texture for the given project index. Layout is
   * authored on a 1024×614 logical grid; setTransform applies the high-DPI
   * scale so text + image stay crisp at close-up zoom.
   */
  #renderCanvas(index) {
    const project = this.projects[index];
    const ctx = this.ctx;
    const w = this.logicalW;
    const h = this.logicalH;
    const imageH = Math.floor(h * 0.74);

    ctx.setTransform(this.canvasScale, 0, 0, this.canvasScale, 0, 0);

    // Dark canvas background — also serves as letterbox fill.
    ctx.fillStyle = '#1a1a2a';
    ctx.fillRect(0, 0, w, h);

    // Screenshot — contain-fit so the whole image is always visible.
    const img = project._loadedImage;
    if (img && img.naturalWidth > 0) {
      const areaAR = w / imageH;
      const srcAR = img.naturalWidth / img.naturalHeight;
      let dx, dy, dw, dh;
      if (srcAR >= areaAR) {
        // image is wider — fit by width, letterbox top/bottom
        dw = w;
        dh = w / srcAR;
        dx = 0;
        dy = (imageH - dh) / 2;
      } else {
        // image is taller — fit by height, pillarbox left/right
        dh = imageH;
        dw = imageH * srcAR;
        dx = (w - dw) / 2;
        dy = 0;
      }
      ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight, dx, dy, dw, dh);
    } else {
      // No image — accent color block so the screen still reads as a project.
      ctx.fillStyle = project.color || '#2a3a5a';
      ctx.fillRect(0, 0, w, imageH);
    }

    // Gradient fade between image and info strip.
    const fadeH = 40;
    const grad = ctx.createLinearGradient(0, imageH - fadeH, 0, imageH);
    grad.addColorStop(0, 'rgba(26, 26, 42, 0)');
    grad.addColorStop(1, 'rgba(26, 26, 42, 1)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, imageH - fadeH, w, fadeH);

    // Accent bar above the title.
    ctx.fillStyle = project.color || '#ffd28a';
    ctx.fillRect(40, imageH + 14, 64, 6);

    // Project name + counter on the same baseline.
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 44px Fredoka, "Arial Black", sans-serif';
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillText(project.name, 40, imageH + 28);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '24px Fredoka, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${index + 1} / ${this.projects.length}`, w - 40, imageH + 40);
    ctx.textAlign = 'left';

    // Year · category meta line under the title.
    const meta = [project.year, project.category].filter(Boolean).join('  ·  ');
    if (meta) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
      ctx.font = '600 18px Nunito, sans-serif';
      ctx.fillText(meta.toUpperCase(), 40, imageH + 78);
    }

    // Tech tag pills.
    const tags = project.tech || [];
    const tagFontSize = 22;
    ctx.font = `600 ${tagFontSize}px Nunito, sans-serif`;
    let tagX = 40;
    const tagY = imageH + 104;
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

    // Prev / Next arrow hints.
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.font = 'bold 40px sans-serif';
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    ctx.fillText('◀', 12, imageH / 2);
    ctx.textAlign = 'right';
    ctx.fillText('▶', w - 12, imageH / 2);

    // Reset for any subsequent draw call.
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
}

// Backwards-compat export — some downstream code may read PROJECTS_CENTER.
// Kept at the legacy XZ so any cached reference still resolves to a sane
// point, but the real position lives on items[0].position (computed from
// refShowcaseMount at load time).
export const PROJECTS_CENTER = { x: 70, z: 0, radius: 70 };
