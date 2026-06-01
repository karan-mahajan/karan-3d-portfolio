import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { contact } from './ContactData.js';

const tmpVec = new THREE.Vector3();
const WORLD_UP = new THREE.Vector3(0, 1, 0);
const SPAWN = new THREE.Vector3(0, 0, 0);

// Baked-in board text meshes (authored in 04-markers-section-z-contact-board.py).
// We paint our own readable canvas on the face, so these are hidden at boot to
// avoid z-fighting / double text peeking through the panel edges.
const BAKED_TEXT_RE = /^contactBoard_text_/;

/**
 * Runtime "walk up to the contact board" interaction.
 *
 * Blender owns the board shell (root_contactBoard): a tall framed sign with a
 * beacon on top, the `contact_inscription_plinth` face, and a mailbox. The face
 * shipped blank-looking because the only runtime content was a tiny 2×1 m decal
 * floating above it. This class instead paints a face-sized canvas flush on the
 * plinth (name + role + tagline + press-E hint) and, on enter, dollies the
 * camera up to the board while the canvas cross-fades to the full contact
 * details (email / GitHub / LinkedIn). ESC dollies back.
 *
 * It also lights the top — a glowing fixture plus a warm PointLight that lifts
 * at night via timeOfDay.nightFactor — so the board reads after dark.
 *
 * Lifecycle mirrors ProjectsHut: near() → enter() → exit().
 */
export class ContactBoard {
  static PROXIMITY = 12;        // m — prompt shows well before the board (~1.8×)
  static ENTER_DURATION = 1.4;  // s — dolly in to the board
  static EXIT_DURATION = 1.1;   // s — dolly back to the player
  static FADE_DURATION = 0.22;  // s — cross-fade summary ↔ details
  static FACE_FILL = 0.9;       // canvas width as a fraction of the face width
  static FACE_FILL_H = 0.86;    // canvas height as a fraction of the face height
  static BEACON_LIGHT_DAY = 0.0;
  static BEACON_LIGHT_NIGHT = 6.0;

  constructor({
    scene,
    camera,
    player,
    playerCamera,
    controller,
    audio = null,
    achievements = null,
    timeOfDay = null,
    postfx = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.audio = audio;
    this.achievements = achievements;
    this.timeOfDay = timeOfDay;
    this.postfx = postfx;

    this.active = false;
    this.zooming = false;
    this._near = false;
    this._detail = false;
    this._hotspots = [];
    this._hovering = false;

    this.faceMesh = scene.getObjectByName('contact_inscription_plinth');
    this.ready = !!this.faceMesh;

    if (!this.ready) {
      console.warn('[ContactBoard] contact_inscription_plinth missing; contact interaction skipped');
      return;
    }

    this.#hideBakedText();
    this.#measureFace();
    this.#buildPanel();
    this.#buildBeaconLight();
    this.#installDom();
    this.#installPointer();
    this.#render(/* detail */ false);
  }

  // ── Setup ──────────────────────────────────────────────────────────────────

  #hideBakedText() {
    this.scene.traverse((o) => {
      if (o.isMesh && BAKED_TEXT_RE.test(o.name || '')) o.visible = false;
    });
    // Drop the legacy tiny floating decal PortfolioMounts mounts above the
    // plinth — this class now owns the contact content, painted on the face.
    const legacy = this.scene.getObjectByName('contact-panel');
    if (legacy) {
      legacy.parent?.remove(legacy);
      legacy.geometry?.dispose?.();
      legacy.material?.map?.dispose?.();
      legacy.material?.dispose?.();
    }
  }

  /**
   * Derive the face centre, outward normal, and width/height purely from the
   * authored geometry — so the panel tracks the board even if it's moved or
   * rescaled, and we never hardcode the Blender transform.
   */
  #measureFace() {
    this.faceMesh.updateWorldMatrix(true, false);
    const box = new THREE.Box3().setFromObject(this.faceMesh);
    this.faceCenter = box.getCenter(new THREE.Vector3());

    const geo = this.faceMesh.geometry;
    if (!geo.boundingBox) geo.computeBoundingBox();
    const localSize = geo.boundingBox.getSize(new THREE.Vector3());
    const scale = this.faceMesh.getWorldScale(new THREE.Vector3());
    const worldQuat = this.faceMesh.getWorldQuaternion(new THREE.Quaternion());

    // Per local axis: its world-space length and how vertical it points.
    const axes = [
      { vec: new THREE.Vector3(1, 0, 0), len: localSize.x * scale.x },
      { vec: new THREE.Vector3(0, 1, 0), len: localSize.y * scale.y },
      { vec: new THREE.Vector3(0, 0, 1), len: localSize.z * scale.z },
    ];
    for (const a of axes) a.up = Math.abs(a.vec.clone().applyQuaternion(worldQuat).y);

    // Thinnest axis = the facing normal; most-vertical axis = height; the
    // remaining axis = width.
    const thin = axes.reduce((m, a) => (a.len < m.len ? a : m), axes[0]);
    const vert = axes.reduce((m, a) => (a.up > m.up ? a : m), axes[0]);
    const width = axes.find((a) => a !== thin && a !== vert) ?? thin;

    const normal = thin.vec.clone().applyQuaternion(worldQuat);
    normal.y = 0;
    normal.normalize();
    // Point it toward spawn (where the player approaches from).
    tmpVec.subVectors(SPAWN, this.faceCenter).setY(0);
    if (normal.dot(tmpVec) < 0) normal.negate();
    this.faceNormal = normal;

    this.faceWidth = width.len;
    this.faceHeight = vert.len;
    this.faceThickness = thin.len;

    // Camera standoff: far enough that the full panel height fits the FOV.
    const fov = THREE.MathUtils.degToRad((this.camera.fov ?? 50) * 0.5);
    const fit = (this.faceHeight * ContactBoard.FACE_FILL_H * 0.5) / Math.tan(fov);
    this.camStandoff = this.faceCenter
      .clone()
      .addScaledVector(this.faceNormal, fit * 1.18);
    this.camStandoff.y = this.faceCenter.y;
  }

  #buildPanel() {
    const panelW = this.faceWidth * ContactBoard.FACE_FILL;
    const panelH = this.faceHeight * ContactBoard.FACE_FILL_H;

    this.logicalW = 1024;
    this.logicalH = Math.round(this.logicalW * (panelH / panelW));
    const dpr = 2;
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.logicalW * dpr;
    this.canvas.height = this.logicalH * dpr;
    this.ctx = this.canvas.getContext('2d');
    this.dpr = dpr;

    const tex = new THREE.CanvasTexture(this.canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 16;
    this.texture = tex;

    this.panelMat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      depthWrite: true,
      opacity: 1,
    });
    this.panel = new THREE.Mesh(new THREE.PlaneGeometry(panelW, panelH), this.panelMat);
    this.panel.name = 'contact-board-panel';
    // Sit just proud of the board's front surface (the inset frame is a touch
    // thicker than the plinth, so clear the full half-thickness + a hair).
    const standoff = this.faceThickness * 0.5 + 0.12;
    this.panel.position.copy(this.faceCenter).addScaledVector(this.faceNormal, standoff);
    this.panel.lookAt(tmpVec.copy(this.panel.position).add(this.faceNormal));
    this.scene.add(this.panel);
  }

  /**
   * The authored beacon cap (`contactBoard_top_beacon`) is consolidated into a
   * flat merged chunk at load, so it can't be recoloured by name. We add our own
   * glow fixture + a warm PointLight just above the board face — that reads as
   * "a light on top" and, more importantly, lights the face so it stays readable
   * after dark. Position is derived from the face geometry (no Blender numbers).
   */
  #buildBeaconLight() {
    this.beaconPos = this.faceCenter
      .clone()
      .addScaledVector(WORLD_UP, this.faceHeight * 0.5 + 0.85);

    this.beaconGlow = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 20, 12),
      new THREE.MeshBasicMaterial({ color: 0xffcaa0, transparent: true, opacity: 0.95 }),
    );
    this.beaconGlow.name = 'contact-board-beacon';
    this.beaconGlow.position.copy(this.beaconPos);
    this.scene.add(this.beaconGlow);

    this.beaconLight = new THREE.PointLight(0xffb074, ContactBoard.BEACON_LIGHT_DAY, 24, 2);
    this.beaconLight.position.copy(this.beaconPos);
    this.beaconLight.castShadow = false;
    this.scene.add(this.beaconLight);
  }

  // ── Proximity ──────────────────────────────────────────────────────────────

  near(playerPosition) {
    if (!this.ready || this.active || this.zooming || !playerPosition) return false;
    const dx = playerPosition.x - this.faceCenter.x;
    const dz = playerPosition.z - this.faceCenter.z;
    this._near = dx * dx + dz * dz <= ContactBoard.PROXIMITY * ContactBoard.PROXIMITY;
    return this._near;
  }

  // ── Enter / exit ─────────────────────────────────────────────────────────

  enter() {
    if (!this.ready || this.active || this.zooming) return;
    this.active = true;
    this.zooming = true;
    this._near = false;
    this.audio?.playMenuOpen?.();
    this.achievements?.onSectionVisited?.('contact');

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

    this.#crossfadeTo(/* detail */ true);
    this.#showHint(true);
    this.#dolly(this._returnPos, this._returnLook, this.camStandoff, this.faceCenter, {
      duration: ContactBoard.ENTER_DURATION,
      onComplete: () => { this.zooming = false; },
    });
  }

  exit() {
    if (!this.ready || (!this.active && !this.zooming)) return;
    this.active = false;
    this.zooming = true;
    this.audio?.playMenuClose?.();
    this.#showHint(false);
    this.#crossfadeTo(/* detail */ false);
    if (this._hovering) { this._hovering = false; this.#setCursor(false); }

    const fromPos = this.camera.position.clone();
    this.camera.getWorldDirection(tmpVec);
    const fromLook = fromPos.clone().add(tmpVec);

    this.#dolly(fromPos, fromLook, this._returnPos, this._returnLook, {
      duration: ContactBoard.EXIT_DURATION,
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

  /** Tilt-shift blurs the far board edges from up close — cut it while inside. */
  #suppressPostFX(inside) {
    if (!this.postfx) return;
    if (inside) {
      if (this._savedTilt == null) this._savedTilt = this.postfx.tiltShiftAmount ?? 1.0;
      this.postfx.tiltShiftAmount = 0;
    } else if (this._savedTilt != null) {
      this.postfx.tiltShiftAmount = this._savedTilt;
      this._savedTilt = null;
    }
  }

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

  // ── Per-frame ──────────────────────────────────────────────────────────────

  update(elapsed = 0) {
    if (!this.ready || !this.beaconLight) return;
    const night = this.timeOfDay?.nightFactor ?? 0;
    const base = THREE.MathUtils.lerp(
      ContactBoard.BEACON_LIGHT_DAY,
      ContactBoard.BEACON_LIGHT_NIGHT,
      night,
    );
    // Gentle breathing so the beacon reads as a live light, not a decal.
    const pulse = 1 + Math.sin(elapsed * 2.1) * 0.08;
    this.beaconLight.intensity = base * pulse;
    if (this.beaconGlow) this.beaconGlow.scale.setScalar(pulse);
  }

  // ── Canvas ──────────────────────────────────────────────────────────────────

  #crossfadeTo(detail) {
    if (this._detail === detail) return;
    gsap.killTweensOf(this.panelMat);
    gsap.to(this.panelMat, {
      opacity: 0.15,
      duration: ContactBoard.FADE_DURATION,
      ease: 'power2.out',
      onComplete: () => {
        this.#render(detail);
        gsap.to(this.panelMat, {
          opacity: 1,
          duration: ContactBoard.FADE_DURATION,
          ease: 'power2.out',
        });
      },
    });
  }

  #render(detail) {
    this._detail = detail;
    this._hotspots = [];
    const ctx = this.ctx;
    const w = this.logicalW;
    const h = this.logicalH;
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    // Warm dark backing + left accent bar, matching the in-world board palette.
    ctx.fillStyle = '#211610';
    ctx.fillRect(0, 0, w, h);
    const vign = ctx.createRadialGradient(w / 2, h / 2, h * 0.2, w / 2, h / 2, h * 0.9);
    vign.addColorStop(0, 'rgba(255, 176, 116, 0.05)');
    vign.addColorStop(1, 'rgba(0, 0, 0, 0.28)');
    ctx.fillStyle = vign;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#ff9a4a';
    ctx.fillRect(0, 0, 14, h);

    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';

    if (!detail) {
      // Summary — readable from a distance.
      ctx.fillStyle = '#f6e9d6';
      ctx.font = '800 96px Oswald, "Arial Black", sans-serif';
      ctx.fillText(contact.name, 64, h * 0.34);

      ctx.fillStyle = '#ff9a4a';
      ctx.font = '600 50px Rajdhani, sans-serif';
      ctx.fillText((contact.title || '').toUpperCase(), 66, h * 0.46);

      ctx.fillStyle = '#cdbb9f';
      ctx.font = '400 38px Rajdhani, sans-serif';
      this.#wrap(ctx, contact.blurb || '', 66, h * 0.58, w - 130, 50);

      // Press-E pill, bottom-left.
      this.#pill(ctx, 64, h - 96, 'E', 'PRESS  E  TO  GET  IN  TOUCH');
    } else {
      // Detail — full contact links, read from up close + clickable (see
      // #linkAt). No ESC pill here: it collided with the last link; the
      // bottom-right hint card carries the "ESC to step back" cue instead.
      ctx.fillStyle = '#cdbb9f';
      ctx.font = '600 36px Rajdhani, sans-serif';
      ctx.fillText(`${contact.name.toUpperCase()} · ${(contact.title || '').toUpperCase()}`, 64, h * 0.13);

      ctx.fillStyle = '#f6e9d6';
      ctx.font = '800 72px Oswald, "Arial Black", sans-serif';
      ctx.fillText('GET IN TOUCH', 62, h * 0.27);

      const links = contact.links || [];
      const maxW = w - 64 - 36;
      const top = h * 0.40;
      const rowGap = (h * 0.52) / Math.max(links.length, 1);
      this._hotspots = [];
      links.forEach((link, i) => {
        const y = top + i * rowGap;
        ctx.fillStyle = '#ff9a4a';
        ctx.font = '700 32px Rajdhani, sans-serif';
        ctx.fillText((link.label || '').toUpperCase(), 66, y);
        ctx.fillStyle = '#f6e9d6';
        ctx.font = this.#fitFont(ctx, link.value || '', 44, '500', 'Rajdhani, sans-serif', maxW);
        ctx.fillText(link.value || '', 66, y + 50);
        // Clickable band spanning label + value, generous for easy targeting.
        this._hotspots.push({
          x0: 48, x1: w - 28, y0: y - 34, y1: y + 64, href: link.href,
        });
      });
    }

    this.texture.needsUpdate = true;
  }

  /** Largest size ≤ base (px) at which `text` fits `maxW`; returns a font string. */
  #fitFont(ctx, text, base, weight, family, maxW) {
    let size = base;
    for (; size > 22; size -= 2) {
      ctx.font = `${weight} ${size}px ${family}`;
      if (ctx.measureText(text).width <= maxW) break;
    }
    return `${weight} ${size}px ${family}`;
  }

  #pill(ctx, x, y, key, label) {
    const keyW = 64;
    ctx.fillStyle = 'rgba(255, 154, 74, 0.16)';
    this.#roundRect(ctx, x, y, keyW, 56, 10);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 154, 74, 0.6)';
    ctx.lineWidth = 2;
    this.#roundRect(ctx, x, y, keyW, 56, 10);
    ctx.stroke();
    ctx.fillStyle = '#ffc89a';
    ctx.font = '800 34px Oswald, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(key, x + keyW / 2, y + 40);
    ctx.textAlign = 'left';
    ctx.fillStyle = '#cdbb9f';
    ctx.font = '700 30px Rajdhani, sans-serif';
    ctx.fillText(label, x + keyW + 22, y + 38);
  }

  #wrap(ctx, text, x, y, maxW, lineH) {
    const words = String(text).split(/\s+/);
    let line = '';
    let cy = y;
    for (const word of words) {
      const test = line ? `${line} ${word}` : word;
      if (ctx.measureText(test).width > maxW && line) {
        ctx.fillText(line, x, cy);
        line = word;
        cy += lineH;
      } else {
        line = test;
      }
    }
    if (line) ctx.fillText(line, x, cy);
  }

  #roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    if (typeof ctx.roundRect === 'function') { ctx.roundRect(x, y, w, h, r); return; }
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  // ── DOM hint ────────────────────────────────────────────────────────────

  #installDom() {
    this.hintEl = document.createElement('div');
    this.hintEl.className = 'skill-sphere-hint hidden';
    this.hintEl.innerHTML = `
      <span class="skill-sphere-kicker">Contact</span>
      <strong>Get in touch</strong>
      <span class="skill-sphere-exit">ESC to step back</span>
    `;
    document.body.appendChild(this.hintEl);
  }

  #showHint(show) {
    if (!this.hintEl) return;
    this.hintEl.classList.toggle('hidden', !show);
  }

  // ── Clickable links (raycast onto the board panel) ───────────────────────

  /**
   * The detail links live on a canvas painted onto a 3D plane, so they can't be
   * real anchors. We instead raycast the pointer onto the panel, map the hit UV
   * to canvas pixels, and test it against the per-link hotspot rects recorded in
   * #render — opening the matching URL in a new tab. Only live once the dolly has
   * settled (active && !zooming) and only over the detail view (hotspots empty
   * otherwise).
   */
  #installPointer() {
    this._raycaster = new THREE.Raycaster();
    this._ndc = new THREE.Vector2();

    this._onClick = (e) => {
      const hit = this.#linkAt(e.clientX, e.clientY);
      if (!hit) return;
      window.open(hit.href, '_blank', 'noopener,noreferrer');
      this.audio?.playInteract?.();
    };
    this._onMove = (e) => {
      const over = !!this.#linkAt(e.clientX, e.clientY);
      if (over !== this._hovering) {
        this._hovering = over;
        this.#setCursor(over);
      }
    };
    window.addEventListener('pointermove', this._onMove);
    window.addEventListener('click', this._onClick);
  }

  #linkAt(clientX, clientY) {
    if (!this.active || this.zooming || !this.panel || !this._hotspots.length) return null;
    this._ndc.set(
      (clientX / window.innerWidth) * 2 - 1,
      -(clientY / window.innerHeight) * 2 + 1,
    );
    this._raycaster.setFromCamera(this._ndc, this.camera);
    const hits = this._raycaster.intersectObject(this.panel, false);
    const uv = hits[0]?.uv;
    if (!uv) return null;
    const cx = uv.x * this.logicalW;
    const cy = (1 - uv.y) * this.logicalH;
    for (const hs of this._hotspots) {
      if (cx >= hs.x0 && cx <= hs.x1 && cy >= hs.y0 && cy <= hs.y1) return hs;
    }
    return null;
  }

  #setCursor(on) {
    document.body.style.cursor = on ? 'pointer' : '';
  }
}
