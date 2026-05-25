import gsap from "gsap";
import * as THREE from "three";
import { contact } from "./ContactData.js";

const PROXIMITY = 4.5; // distance from billboard to show prompt
const CONTACT_PROXIMITY = 3.2;
const ZOOM_DURATION = 1.1; // seconds
const ZOOM_STANDOFF = 3.2; // distance from screen during focused view
const ZOOM_HEIGHT_OFFSET = 0.0; // vertical bias relative to screen center

/**
 * Drives the proximity prompt + focused-view overlay for billboards.
 *
 * Lifecycle:
 *   constructor(deps) — installs key listeners + DOM
 *   tick(playerPosition) — call once per frame, manages prompt visibility
 *   destroy() — removes listeners (not currently used; lifetime == app)
 */
export class Interaction {
  constructor({
    scene,
    camera,
    playerCamera,
    player,
    controller,
    billboards,
    signs = null,
    audio = null,
    actionPrompts = null,
    timeOfDay = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.playerCamera = playerCamera;
    this.player = player;
    this.controller = controller;
    this.billboards = billboards;
    this.signs = signs;
    this.audio = audio;
    this.actionPrompts = actionPrompts;
    this.timeOfDay = timeOfDay;
    this.torchLight = null; // wired post-construction by App.js

    this.activeIndex = -1; // -1 = not focused
    this.candidate = null; // billboard the player is currently near
    this.contactCandidate = false;
    this.contactOpen = false;
    this.zooming = false;
    this.torchAiming = false;
    this._lastTodMode = this.timeOfDay?.mode ?? null;

    this.#installDom();
    this.#installKeyListeners();
  }

  // ── DOM ────────────────────────────────────────────────────────────────────

  #installDom() {
    this.promptEl = document.createElement("div");
    this.promptEl.className = "billboard-prompt hidden";
    this.promptEl.innerHTML = `
      <span class="key">E</span>
      <span class="label">View <strong class="project-name"></strong></span>
    `;
    document.body.appendChild(this.promptEl);

    this.panelEl = document.createElement("div");
    this.panelEl.className = "project-panel hidden";
    this.panelEl.innerHTML = `
      <button class="panel-close" aria-label="Close">×</button>
      <div class="panel-accent"></div>
      <h2 class="panel-title"></h2>
      <p class="panel-description"></p>
      <div class="panel-tech"></div>
      <div class="panel-actions">
        <a class="panel-link" target="_blank" rel="noopener noreferrer">Open Site ↗</a>
      </div>
      <nav class="panel-nav">
        <button class="panel-prev" aria-label="Previous">← Prev</button>
        <span class="panel-counter"></span>
        <button class="panel-next" aria-label="Next">Next →</button>
      </nav>
      <div class="panel-hint">ESC to return</div>
    `;
    document.body.appendChild(this.panelEl);

    this.panelEl
      .querySelector(".panel-close")
      .addEventListener("click", () => this.exit());
    this.panelEl
      .querySelector(".panel-prev")
      .addEventListener("click", () => this.cycle(-1));
    this.panelEl
      .querySelector(".panel-next")
      .addEventListener("click", () => this.cycle(+1));

    // ── Contact overlay ────────────────────────────────────────────────────
    this.contactEl = document.createElement("div");
    this.contactEl.className = "contact-panel hidden";
    const linksHtml = contact.links
      .map(
        (
          l,
        ) => `<a class="contact-link" href="${l.href}" target="_blank" rel="noopener noreferrer">
        <span class="contact-link-label">${l.label}</span>
        <span class="contact-link-value">${l.value}</span>
      </a>`,
      )
      .join("");
    this.contactEl.innerHTML = `
      <button class="panel-close" aria-label="Close">×</button>
      <div class="contact-accent"></div>
      <h2 class="contact-title">${contact.name}</h2>
      <p class="contact-subtitle">${contact.title}</p>
      <p class="contact-blurb">${contact.blurb}</p>
      <div class="contact-links">${linksHtml}</div>
      <div class="panel-hint">ESC to close</div>
    `;
    document.body.appendChild(this.contactEl);
    this.contactEl
      .querySelector(".panel-close")
      .addEventListener("click", () => this.closeContact());

    this.torchHintEl = document.createElement("div");
    this.torchHintEl.className = "billboard-prompt torch-hint hidden";
    this.torchHintEl.innerHTML = `
      <span class="key">F</span>
      <span class="label">Aim torch</span>
    `;
    document.body.appendChild(this.torchHintEl);
  }

  // ── Input ──────────────────────────────────────────────────────────────────

  #installKeyListeners() {
    this._onKey = (e) => {
      if (this.zooming) return;
      if (e.code === "KeyE") {
        if (this.contactOpen) return;
        if (this.activeIndex === -1) {
          if (this.contactCandidate) this.openContact();
          else if (this.candidate) this.focus(this.candidate.index);
        }
      } else if (e.code === "KeyF") {
        if (this.activeIndex !== -1 || this.contactOpen) return;
        const torchOn = this.player?.character?.torchMesh?.visible === true;
        const night = this.timeOfDay?.mode === "night";
        if (!torchOn || !night) return;
        this.toggleTorchAim();
      } else if (e.code === "Escape") {
        if (this.contactOpen) this.closeContact();
        else if (this.activeIndex !== -1) this.exit();
        else if (this.torchAiming) this.exitTorchAim();
      } else if (this.activeIndex !== -1) {
        if (e.code === "ArrowLeft") this.cycle(-1);
        else if (e.code === "ArrowRight") this.cycle(+1);
      }
    };
    window.addEventListener("keydown", this._onKey);
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────

  tick(playerPosition) {
    this.#syncTorchHint();
    // If the world flipped from night → day mid-aim, exit silently so the
    // controller speed multiplier and locked anim don't linger.
    const tod = this.timeOfDay?.mode ?? null;
    if (tod !== this._lastTodMode) {
      this._lastTodMode = tod;
      if (tod !== "night" && this.torchAiming) this.exitTorchAim();
    }
    if (this.activeIndex !== -1 || this.zooming || this.contactOpen) {
      this.#hidePrompt();
      return;
    }
    let nearBillboard = this.billboards.closestWithin(
      playerPosition,
      PROXIMITY,
    );
    // Suppress the prompt when the player is behind the billboard — pure XZ
    // distance fires from either side, which lets the player open a project
    // while staring at the back of the screen.
    if (nearBillboard && !this.#inFrontOf(nearBillboard, playerPosition)) {
      nearBillboard = null;
    }
    const nearContact =
      this.signs && this.signs.nearContact(playerPosition, CONTACT_PROXIMITY);
    this.candidate = nearBillboard;
    this.contactCandidate = !!nearContact && !nearBillboard;

    // Defer to ActionPrompts — if it's about to show its own E prompt at the
    // same spot (e.g. Dance tile right next to the Contact mailbox), suppress
    // ours. The action prompt is more specific to the player's current state.
    const ap = this.actionPrompts;
    const apOwnsPrompt =
      ap && (ap.candidate || ap.activeZoneLoop || ap.activeHoldLoop);
    if (apOwnsPrompt) {
      this.#hidePrompt();
      return;
    }

    if (nearBillboard) this.#showPrompt(nearBillboard.project.name);
    else if (this.contactCandidate) this.#showPrompt("Contact");
    else this.#hidePrompt();
  }

  /**
   * True when the player stands in the billboard's front half-plane. The
   * billboard's local +Z faces the player side, so world-forward = (sin yaw,
   * cos yaw). Dot with (player - billboard) > 0 means front-side.
   */
  #inFrontOf(item, playerPos) {
    const yaw = item.group.rotation.y;
    const fx = Math.sin(yaw);
    const fz = Math.cos(yaw);
    const dx = playerPos.x - item.position.x;
    const dz = playerPos.z - item.position.z;
    return fx * dx + fz * dz > 0;
  }

  #showPrompt(name) {
    this.promptEl.classList.remove("hidden");
    this.promptEl.querySelector(".project-name").textContent = name;
  }
  #hidePrompt() {
    this.promptEl.classList.add("hidden");
  }

  // ── Focus / exit ───────────────────────────────────────────────────────────

  focus(index) {
    const item = this.billboards.items[index];
    if (!item) return;
    if (this.torchAiming) this.exitTorchAim();
    this.activeIndex = index;
    this.#hidePrompt();
    this.audio?.playMenuOpen();

    this.controller.paused = true;
    this.playerCamera.locked = true;

    // Stash the camera's current world transform so we can return to it.
    if (!this._returnPos) {
      this._returnPos = new THREE.Vector3();
      this._returnLook = new THREE.Vector3();
      this._returnDir = new THREE.Vector3();
    }
    this._returnPos.copy(this.camera.position);
    this.camera.getWorldDirection(this._returnDir);
    this._returnLook.copy(this._returnPos).add(this._returnDir);

    this.#animateTo(item, /*incoming*/ true);
    this.#populatePanel(item);
  }

  cycle(direction) {
    const n = this.billboards.items.length;
    const next = (this.activeIndex + direction + n) % n;
    const item = this.billboards.items[next];
    this.activeIndex = next;
    this.audio?.playInteract();
    this.#animateTo(item, /*incoming*/ false);
    this.#populatePanel(item);
  }

  exit() {
    if (this.activeIndex === -1) return;
    this.activeIndex = -1;
    this.panelEl.classList.add("hidden");
    this.audio?.playMenuClose();
    this.zooming = true;

    // Tween position back to the stashed return state and ease the look-target
    // from the current screen back to the original look-target in lockstep.
    const tmp = new THREE.Vector3();
    this.camera.getWorldDirection(tmp);
    const lookProxy = this.camera.position.clone().add(tmp);

    gsap.to(lookProxy, {
      x: this._returnLook.x,
      y: this._returnLook.y,
      z: this._returnLook.z,
      duration: ZOOM_DURATION,
      ease: "power2.inOut",
    });
    gsap.to(this.camera.position, {
      x: this._returnPos.x,
      y: this._returnPos.y,
      z: this._returnPos.z,
      duration: ZOOM_DURATION,
      ease: "power2.inOut",
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.zooming = false;
        this.controller.paused = false;
        this.playerCamera.locked = false;
        this.playerCamera.resync();
      },
    });
  }

  #animateTo(item, incoming) {
    this.zooming = true;

    // World-space center of the screen.
    const screenWorld = new THREE.Vector3();
    item.screen.getWorldPosition(screenWorld);
    // World-space forward of the screen (its +Z in local = forward face).
    const screenFwd = new THREE.Vector3(0, 0, 1).applyQuaternion(
      item.group.getWorldQuaternion(new THREE.Quaternion()),
    );

    const target = screenWorld
      .clone()
      .addScaledVector(screenFwd, ZOOM_STANDOFF);
    target.y += ZOOM_HEIGHT_OFFSET;
    const look = screenWorld.clone();

    gsap.to(this.camera.position, {
      x: target.x,
      y: target.y,
      z: target.z,
      duration: incoming ? ZOOM_DURATION : ZOOM_DURATION * 0.65,
      ease: "power2.inOut",
      onUpdate: () => this.camera.lookAt(look),
      onComplete: () => {
        this.camera.lookAt(look);
        this.zooming = false;
        this.panelEl.classList.remove("hidden");
      },
    });
  }

  // ── Contact ──────────────────────────────────────────────────────────────

  openContact() {
    if (this.contactOpen) return;
    if (this.torchAiming) this.exitTorchAim();
    this.contactOpen = true;
    this.#hidePrompt();
    this.audio?.playMenuOpen();
    this.controller.paused = true;
    this.contactEl.classList.remove("hidden");
  }

  closeContact() {
    if (!this.contactOpen) return;
    this.contactOpen = false;
    this.audio?.playMenuClose();
    this.controller.paused = false;
    this.contactEl.classList.add("hidden");
  }

  #populatePanel(item) {
    const p = item.project;
    this.panelEl.querySelector(".panel-title").textContent = p.name;
    this.panelEl.querySelector(".panel-description").textContent =
      p.description;
    this.panelEl.querySelector(".panel-accent").style.background = p.color;

    const techEl = this.panelEl.querySelector(".panel-tech");
    techEl.innerHTML = "";
    for (const t of p.tech) {
      const pill = document.createElement("span");
      pill.className = "tech-pill";
      pill.textContent = t;
      techEl.appendChild(pill);
    }

    const link = this.panelEl.querySelector(".panel-link");
    if (p.url) {
      link.href = p.url;
      link.style.display = "";
    } else {
      link.removeAttribute("href");
      link.style.display = "none";
    }

    const counter = this.panelEl.querySelector(".panel-counter");
    counter.textContent = `${item.index + 1} / ${this.billboards.items.length}`;
  }

  // ── Torch aim ────────────────────────────────────────────────────────────

  toggleTorchAim() {
    if (this.torchAiming) this.exitTorchAim();
    else this.enterTorchAim();
  }

  enterTorchAim() {
    if (this.torchAiming) return;
    if (!this.player?.character?.actions?.torchAim) return;
    this.torchAiming = true;
    this.controller.actionSpeedMultiplier = 0.5;
    this.player.character.playTorchOverlay("torchAim", 0.35);
    this.audio?.playInteract?.();
  }

  exitTorchAim() {
    if (!this.torchAiming) return;
    this.torchAiming = false;
    this.controller.actionSpeedMultiplier = 1.0;
    this.player?.character?.stopTorchOverlay?.(0.35);
  }

  #syncTorchHint() {
    const torchOn = this.player?.character?.torchMesh?.visible === true;
    const night = this.timeOfDay?.mode === "night";
    const modalOpen =
      this.activeIndex !== -1 || this.contactOpen || this.zooming;
    const show = torchOn && night && !modalOpen;
    if (!this.torchHintEl) return;
    if (show) {
      this.torchHintEl.classList.remove("hidden");
      this.torchHintEl.querySelector(".label").textContent = this.torchAiming
        ? "Lower torch"
        : "Aim torch";
    } else {
      this.torchHintEl.classList.add("hidden");
    }
  }
}
