import * as THREE from 'three';
import gsap from 'gsap';
import { portfolio } from './PortfolioData.js';

/**
 * Project showcase station — one large screen east of spawn that cycles
 * through every project. Replaces the old per-project billboard fan.
 *
 * Structure:
 *   posts    — two vertical wooden cylinders flanking the screen
 *   beam     — horizontal cross-beam joining the posts
 *   frame    — dark wood border around the screen
 *   screen   — 5×3 plane painted with a per-project canvas (image +
 *              name + summary + tech tags + counter + arrows)
 *
 * Compatibility:
 *   `items` is an array with EXACTLY one entry — the currently displayed
 *   project. Other systems (TimeOfDay, StreetLights, ActionPrompts,
 *   Achievements) iterate `items` and only care about position + project
 *   + screen + accent, which all stay valid through index changes.
 *
 *   `emissiveBoost` is still read by TimeOfDay; we treat it as a global
 *   night-pop multiplier on screen brightness via material emissive
 *   intensity (the canvas is bound as both `map` and `emissiveMap` so the
 *   screen glows with its own pixel colors at night, same as the old
 *   per-project screens).
 */

// Showcase sits east of spawn at the same spot the old billboard arc was
// centered around. The arc previously fanned ±30° at radius 36; one screen
// at PROJECTS_CENTER puts the showcase right in the middle of that fan.
const STATION_X = 36;
const STATION_Z = 0;

const POST_HEIGHT = 4.6;
const POST_RADIUS = 0.14;
const POST_SPACING = 5.5;
const SCREEN_WIDTH = 5;
const SCREEN_HEIGHT = 3;
const SCREEN_Y = 2.6;
const FRAME_THICKNESS = 0.12;

const AUTO_ROTATE_SECONDS = 5;
const NEAR_PAUSE_RADIUS = 8;     // auto-rotate pauses when player is within this
const FADE_DURATION = 0.18;      // screen fade-out / fade-in during content swap

const WOOD_COLOR = '#6b4226';
const WOOD_DARK = '#3d2615';

export const PROJECTS_CENTER = { x: STATION_X, z: STATION_Z, radius: STATION_X };

export class Billboards {
  constructor(scene, physics = null, loader = null, terrain = null) {
    this.scene = scene;
    this.physics = physics;
    this.loader = loader;
    this.terrain = terrain;

    this.projects = portfolio.projects;
    this.currentIndex = 0;
    this.transitioning = false;
    this.focused = false;          // Interaction.js writes this so we pause auto-rotate
    this._autoTimer = 0;
    this._playerNearby = false;
    // Day=1.0 baseline. TimeOfDay lerps this up at night for the night-pop.
    this.emissiveBoost = 1.0;

    this.group = new THREE.Group();
    this.group.name = 'project-showcase';
    this.scene.add(this.group);

    // items[] is single-entry for compatibility with other systems. The
    // referenced project + index get mutated in #applyIndex when the
    // showcase rotates, so any code holding the item reference still sees
    // the current project's name / accent / etc.
    this.items = [];

    this.#buildStation();
    this.#applyIndex(0, /*immediate*/ true);
    this.#kickOffImagePreload();
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
  }

  // ── Build ────────────────────────────────────────────────────────────────

  #buildStation() {
    const x = STATION_X;
    const z = STATION_Z;
    const groundY = this.#groundY(x, z);
    // Face the spawn point (origin). World forward (front side of the
    // billboard) = (sin yaw, cos yaw) — for (x=36, z=0) yaw=-π/2 puts the
    // front face pointing west (-X) toward the player.
    const yaw = Math.atan2(-x, -z);

    this.group.position.set(x, groundY, z);
    this.group.rotation.y = yaw;
    this.yaw = yaw;
    this.groundY = groundY;

    const woodMat = new THREE.MeshStandardMaterial({
      color: WOOD_COLOR, roughness: 0.85, metalness: 0,
    });
    const woodDarkMat = new THREE.MeshStandardMaterial({
      color: WOOD_DARK, roughness: 0.9, metalness: 0,
    });

    // ── Posts ──────────────────────────────────────────────────────────────
    const postGeom = new THREE.CylinderGeometry(POST_RADIUS, POST_RADIUS * 1.2, POST_HEIGHT, 12);
    for (const side of [-1, 1]) {
      const post = new THREE.Mesh(postGeom, woodMat);
      post.position.set(side * (POST_SPACING / 2), POST_HEIGHT / 2, 0);
      post.castShadow = true;
      post.receiveShadow = true;
      this.group.add(post);

      if (this.physics) {
        // Rotate the local post offset into world space so the cylinder
        // collider lands under the visible post regardless of yaw.
        const lx = side * (POST_SPACING / 2);
        const wx = x + Math.cos(yaw) * lx;
        const wz = z + -Math.sin(yaw) * lx;
        this.physics.addStaticCylinder(wx, groundY, wz, POST_RADIUS * 1.3, POST_HEIGHT);
      }
    }

    // Slab collider through the middle so the player can't walk through the
    // screen. Same approach as the old multi-billboard slab.
    if (this.physics) {
      const slabHx = SCREEN_WIDTH / 2 + 0.2;
      const slabHy = (POST_HEIGHT - 0.4) / 2;
      const slabHz = 0.08;
      this.physics.addStaticCuboid(
        x, groundY + POST_HEIGHT / 2, z,
        slabHx, slabHy, slabHz,
        yaw,
      );
    }

    // ── Top beam ───────────────────────────────────────────────────────────
    const beam = new THREE.Mesh(
      new THREE.BoxGeometry(POST_SPACING + 0.3, 0.26, 0.26),
      woodDarkMat,
    );
    beam.position.set(0, POST_HEIGHT - 0.12, 0);
    beam.castShadow = true;
    this.group.add(beam);

    // ── Frame around the screen ────────────────────────────────────────────
    const frame = new THREE.Mesh(
      new THREE.BoxGeometry(SCREEN_WIDTH + FRAME_THICKNESS * 2, SCREEN_HEIGHT + FRAME_THICKNESS * 2, 0.1),
      woodDarkMat,
    );
    frame.position.set(0, SCREEN_Y, -0.06);
    frame.castShadow = true;
    frame.receiveShadow = true;
    this.group.add(frame);

    // ── Canvas-backed screen ───────────────────────────────────────────────
    // Layout is authored in 1024×614 logical pixels (≈ 5:3 to match the
    // plane); the canvas is allocated at 2× so text + image stay crisp
    // when the player zooms in to ~3 m from the 5×3 m screen. ctx.scale()
    // makes every draw call use the logical grid regardless of the
    // physical resolution.
    this.canvasScale = 2;
    this.logicalW = 1024;
    this.logicalH = 614;
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.logicalW * this.canvasScale;
    this.canvas.height = this.logicalH * this.canvasScale;
    this.ctx = this.canvas.getContext('2d');

    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.colorSpace = THREE.SRGBColorSpace;
    this.texture.minFilter = THREE.LinearFilter;
    this.texture.magFilter = THREE.LinearFilter;
    this.texture.anisotropy = 16;

    // White diffuse + emissive map so the screen glows with the canvas's own
    // pixel colors at night without an accent tint over the image.
    this.screenMat = new THREE.MeshStandardMaterial({
      map: this.texture,
      emissive: new THREE.Color('#ffffff'),
      emissiveMap: this.texture,
      emissiveIntensity: 0.4,
      roughness: 0.6,
      metalness: 0,
      transparent: true,    // for the cross-fade tween (opacity 1→0.2→1)
      opacity: 1,
    });

    this.screen = new THREE.Mesh(
      new THREE.PlaneGeometry(SCREEN_WIDTH, SCREEN_HEIGHT),
      this.screenMat,
    );
    this.screen.position.set(0, SCREEN_Y, 0);
    this.group.add(this.screen);

    // Single-entry items[] for compatibility — fields are mutated in-place
    // by #applyIndex when the showcase rotates.
    this.items.push({
      project: this.projects[0],
      index: 0,
      group: this.group,
      screen: this.screen,
      position: new THREE.Vector3(x, 0, z),
      accent: new THREE.Color(this.projects[0].color || '#ffffff'),
      emissiveMultiplier: 0.4,
    });
  }

  // ── Image preload ────────────────────────────────────────────────────────

  /**
   * Kick off image loading for every project. Each image is cached on the
   * project object as `_loadedImage`. As soon as the current project's
   * image is ready, the screen re-renders. Failures are silent — the fallback
   * is the accent color background.
   */
  #kickOffImagePreload() {
    for (const project of this.projects) {
      if (!project.image) continue;
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        project._loadedImage = img;
        // If this is the one currently on screen, re-render now.
        if (this.projects[this.currentIndex] === project) {
          this.#renderCanvas(this.currentIndex);
        }
      };
      img.onerror = () => {
        // Swallow — render will fall back to the accent color block.
      };
      img.src = project.image;
    }
  }

  // ── Navigation ───────────────────────────────────────────────────────────

  /** Advance to the next project with a quick cross-fade. */
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

  /** Jump directly to a specific index (e.g. from the panel's dot nav). */
  setIndex(index) {
    if (this.transitioning) return;
    if (index === this.currentIndex) return;
    const n = this.projects.length;
    this.#applyIndex(((index % n) + n) % n);
  }

  /** Interaction.js calls this when the proximity prompt opens / closes. */
  setFocused(focused) {
    this.focused = !!focused;
    if (this.focused) {
      this._autoTimer = 0;
      // If an auto-rotate fade was in flight, snap it to a clean fully-
      // opaque state so the incoming camera zoom doesn't land on a screen
      // mid-cross-fade.
      if (this.transitioning) {
        gsap.killTweensOf(this.screenMat);
        this.screenMat.opacity = 1;
        this.transitioning = false;
        this.#renderCanvas(this.currentIndex);
      }
    }
  }

  /**
   * Per-frame proximity + auto-rotate driver. Called from World.update.
   * When the player is outside NEAR_PAUSE_RADIUS *and* nobody is in the
   * focused view, advance every AUTO_ROTATE_SECONDS.
   */
  update(elapsed, playerPos = null, delta = 0) {
    // Screen pulse — same vibe as the old code but applied to a single mesh.
    const item = this.items[0];
    if (item) {
      const pulse = (0.5 + 0.1 * Math.sin(elapsed * 1.2))
        * this.emissiveBoost
        * item.emissiveMultiplier;
      item.screen.material.emissiveIntensity = pulse;
    }

    if (!playerPos) return;
    const dx = playerPos.x - STATION_X;
    const dz = playerPos.z - STATION_Z;
    this._playerNearby = (dx * dx + dz * dz) < (NEAR_PAUSE_RADIUS * NEAR_PAUSE_RADIUS);

    if (this.focused || this._playerNearby || this.transitioning) {
      this._autoTimer = 0;
      return;
    }
    this._autoTimer += delta;
    if (this._autoTimer >= AUTO_ROTATE_SECONDS) {
      this._autoTimer = 0;
      this.next();
    }
  }

  // ── Internals ────────────────────────────────────────────────────────────

  #applyIndex(index, immediate = false) {
    this.currentIndex = index;
    const project = this.projects[index];

    // Mutate items[0] so other systems (TimeOfDay, ActionPrompts, etc.)
    // pick up the new project / accent on their next read.
    const item = this.items[0];
    if (item) {
      item.project = project;
      item.index = index;
      item.accent = new THREE.Color(project.color || '#ffffff');
    }

    if (immediate) {
      this.#renderCanvas(index);
      this.screenMat.opacity = 1;
      return;
    }

    // Brief cross-fade — fade the screen out, swap the canvas, fade back in.
    this.transitioning = true;
    gsap.to(this.screenMat, {
      opacity: 0.2,
      duration: FADE_DURATION,
      ease: 'power2.out',
      onComplete: () => {
        this.#renderCanvas(index);
        gsap.to(this.screenMat, {
          opacity: 1,
          duration: FADE_DURATION,
          ease: 'power2.out',
          onComplete: () => { this.transitioning = false; },
        });
      },
    });
  }

  /** Paint the canvas texture for the given project index. Layout is
   *  authored on a 1024×614 logical grid; setTransform applies the high-
   *  DPI scale so text + image stay crisp at close-up zoom. */
  #renderCanvas(index) {
    const project = this.projects[index];
    const ctx = this.ctx;
    const w = this.logicalW;
    const h = this.logicalH;
    // Image takes most of the canvas now; info strip is just a thin band
    // at the bottom with the project name + tech pills + counter. Full
    // description / link live on the side panel when focused.
    const imageH = Math.floor(h * 0.74);

    ctx.setTransform(this.canvasScale, 0, 0, this.canvasScale, 0, 0);

    // Dark canvas background — also serves as the letterbox fill for
    // screenshots whose aspect ratio doesn't match the image area.
    ctx.fillStyle = '#1a1a2a';
    ctx.fillRect(0, 0, w, h);

    // Screenshot — `contain` fit so the WHOLE image is always visible,
    // even when it's taller or wider than the image region. Empty bars
    // around the image fall back to the canvas bg fill above.
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
      // No image — show the accent color as a solid panel so the screen
      // still reads as a "project" at a glance.
      ctx.fillStyle = project.color || '#2a3a5a';
      ctx.fillRect(0, 0, w, imageH);
    }

    // Thin gradient fade so the image edge meets the info strip cleanly.
    const fadeH = 40;
    const grad = ctx.createLinearGradient(0, imageH - fadeH, 0, imageH);
    grad.addColorStop(0, 'rgba(26, 26, 42, 0)');
    grad.addColorStop(1, 'rgba(26, 26, 42, 1)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, imageH - fadeH, w, fadeH);

    // Accent bar above the title
    ctx.fillStyle = project.color || '#ffd28a';
    ctx.fillRect(40, imageH + 14, 64, 6);

    // Project name + counter on the same baseline
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

    // Tech tag pills — bumped to 22px logical so they read cleanly at
    // the steepest viewing angle (player standing in front, looking up
    // at the screen).
    const tags = project.tech || [];
    const tagFontSize = 22;
    ctx.font = `600 ${tagFontSize}px Rajdhani, sans-serif`;
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

    // Prev / Next arrow hints — anchored to the image vertical midpoint.
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.font = 'bold 40px sans-serif';
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'left';
    ctx.fillText('◀', 12, imageH / 2);
    ctx.textAlign = 'right';
    ctx.fillText('▶', w - 12, imageH / 2);

    // Reset for next call.
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
    // Manual fallback for browsers without CanvasRenderingContext2D.roundRect.
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


  // ── Proximity API (used by Interaction.js) ───────────────────────────────

  /** Closest item within `radius` of the player's XZ. Always returns the
   *  single showcase item (or null) — keeps signature parity with the old
   *  multi-billboard implementation. */
  closestWithin(playerPos, radius) {
    const item = this.items[0];
    if (!item) return null;
    const dx = item.position.x - playerPos.x;
    const dz = item.position.z - playerPos.z;
    const d = Math.hypot(dx, dz);
    return d < radius ? item : null;
  }
}
