import gsap from "gsap";
import * as THREE from "three";
import { contact } from "./ContactData.js";
import { resume } from "./ResumeData.js";

const PROXIMITY = 4.5; // distance from billboard to show prompt
const CONTACT_PROXIMITY = 3.2;
const RESUME_PROXIMITY = 4;
const ZOOM_DURATION = 1.1; // seconds
const ZOOM_STANDOFF = 4.0; // distance from screen during focused view — sized so the full 3m-tall screen fits the 45° vertical FOV with margin
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
    skillSphere = null,
    audio = null,
    actionPrompts = null,
    timeOfDay = null,
    achievements = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.playerCamera = playerCamera;
    this.player = player;
    this.controller = controller;
    this.billboards = billboards;
    this.signs = signs;
    this.skillSphere = skillSphere;
    this.audio = audio;
    this.actionPrompts = actionPrompts;
    this.timeOfDay = timeOfDay;
    this.achievements = achievements;

    this.activeIndex = -1; // -1 = not focused
    this.candidate = null; // billboard the player is currently near
    this.contactCandidate = false;
    this.contactOpen = false;
    this.skillCandidate = false;
    this.resumeCandidate = false;
    this.resumeOpen = false;
    this.zooming = false;

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

    // ── Resume overlay ─────────────────────────────────────────────────────
    // Mirrors the contact-panel structure so existing .contact-panel CSS
    // applies (avoids a CSS round-trip in Phase 2). Renders raw HTML from
    // ResumeData.js — later sessions can swap in a real CV.
    this.resumeEl = document.createElement("div");
    this.resumeEl.className = "contact-panel resume-panel hidden";
    this.resumeEl.innerHTML = `
      <button class="panel-close" aria-label="Close">×</button>
      <div class="contact-accent"></div>
      <div class="resume-body">${resume.html}</div>
      ${resume.downloadUrl
        ? `<div class="panel-actions"><a class="panel-link" href="${resume.downloadUrl}" target="_blank" rel="noopener noreferrer">Download PDF ↗</a></div>`
        : ''}
      <div class="panel-hint">ESC to close</div>
    `;
    document.body.appendChild(this.resumeEl);
    this.resumeEl
      .querySelector(".panel-close")
      .addEventListener("click", () => this.closeResume());
  }

  // ── Input ──────────────────────────────────────────────────────────────────

  #installKeyListeners() {
    this._onKey = (e) => {
      if (this.zooming) return;
      if (e.code === "KeyE") {
        if (this.contactOpen || this.resumeOpen || this.skillOpen) return;
        if (this.activeIndex === -1) {
          // Resume is a smaller proximity than contact, so when both fire
          // (shouldn't happen — different anchors — but be defensive), the
          // resume lectern wins.
          if (this.resumeCandidate) this.openResume();
          else if (this.contactCandidate) this.openContact();
          else if (this.skillCandidate) this.openSkills();
          else if (this.candidate) this.focus(this.candidate.index);
        }
      } else if (e.code === "Escape") {
        if (this.skillOpen) this.closeSkills();
        else if (this.resumeOpen) this.closeResume();
        else if (this.contactOpen) this.closeContact();
        else if (this.activeIndex !== -1) this.exit();
      } else if (this.activeIndex !== -1) {
        if (e.code === "ArrowLeft") this.cycle(-1);
        else if (e.code === "ArrowRight") this.cycle(+1);
      }
    };
    window.addEventListener("keydown", this._onKey);
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────

  tick(playerPosition) {
    if (this.activeIndex !== -1 || this.zooming || this.contactOpen || this.resumeOpen || this.skillOpen) {
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
      this.signs && this.signs.nearContact?.(playerPosition, CONTACT_PROXIMITY);
    const nearResume =
      this.signs && this.signs.nearResume?.(playerPosition, RESUME_PROXIMITY);
    const nearSkills = this.skillSphere?.near?.(playerPosition);
    this.candidate = nearBillboard;
    // Resume has the smallest proximity radius — when both fire, prefer it.
    this.resumeCandidate = !!nearResume && !nearBillboard;
    this.contactCandidate = !!nearContact && !nearBillboard && !nearResume;
    this.skillCandidate = !!nearSkills && !nearBillboard && !nearResume && !nearContact;

    // Defer to ActionPrompts — if it's about to show its own E prompt at the
    // same spot (e.g. Dance tile right next to the Contact mailbox), suppress
    // ours. The action prompt is more specific to the player's current state.
    const ap = this.actionPrompts;
    const apActionActive = ap && (ap.activeZoneLoop || ap.activeHoldLoop);
    if (apActionActive) {
      this.#hidePrompt();
      return;
    }
    const apOwnsPrompt = ap && ap.candidate;
    if (apOwnsPrompt && !this.skillCandidate) {
      this.#hidePrompt();
      return;
    }

    if (nearBillboard) this.#showPrompt(nearBillboard.project.name);
    else if (this.resumeCandidate) this.#showPrompt("Résumé");
    else if (this.contactCandidate) this.#showPrompt("Contact");
    else if (this.skillCandidate) this.#showPrompt("Skills", "Enter");
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

  #showPrompt(name, verb = "View") {
    this.promptEl.classList.remove("hidden");
    const label = this.promptEl.querySelector(".label");
    if (label?.childNodes?.[0]) label.childNodes[0].nodeValue = `${verb} `;
    this.promptEl.querySelector(".project-name").textContent = name;
  }
  #hidePrompt() {
    this.promptEl.classList.add("hidden");
  }

  // ── Focus / exit ───────────────────────────────────────────────────────────

  focus(index) {
    // The single showcase always returns items[0]; the project at that
    // slot is whatever the showcase is currently displaying. `index` is
    // the project index (0..projects.length-1) because the showcase
    // mutates items[0].index to track its current project.
    this.billboards.setFocused?.(true);
    // Make sure the showcase is showing the project we're activating —
    // important if the auto-rotate had advanced past it between the
    // proximity prompt and the keypress.
    if (this.billboards.setIndex && this.billboards.items[0]?.index !== index) {
      this.billboards.setIndex(index);
    }
    const item = this.billboards.items[0];
    if (!item) return;
    this.activeIndex = index;
    this.#hidePrompt();
    this.audio?.playMenuOpen();
    this.achievements?.onProjectViewed?.(item.project?.name);

    this.controller.paused = true;
    this.playerCamera.locked = true;
    // Hide the player so the character mesh doesn't sit between the focus
    // camera and the screen (the camera tweens to `screen + 4m forward`,
    // which is roughly where the player is standing when E is pressed).
    if (this.player?.character?.root) this.player.character.root.visible = false;

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
    // With one screen in the world the camera doesn't move on cycle — we
    // just swap the texture on the showcase and re-populate the panel.
    if (this.zooming) return;
    if (this.billboards.transitioning) return;
    const n = this.billboards.projects?.length ?? this.billboards.items.length;
    if (n <= 1) return;
    const next = (this.activeIndex + direction + n) % n;
    this.activeIndex = next;
    this.audio?.playInteract();
    if (this.billboards.setIndex) this.billboards.setIndex(next);
    const item = this.billboards.items[0];
    if (item) {
      this.#populatePanel(item);
      this.achievements?.onProjectViewed?.(item.project?.name);
    }
  }

  exit() {
    if (this.activeIndex === -1) return;
    this.activeIndex = -1;
    this.panelEl.classList.add("hidden");
    this.audio?.playMenuClose();
    this.billboards.setFocused?.(false);
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
        if (this.player?.character?.root) this.player.character.root.visible = true;
      },
    });
  }

  /**
   * Smooth incoming zoom. Camera position AND look target tween at the
   * same pace so the screen never snaps into the centre of the frame on
   * frame 1. The panel is held back until the position tween is ~80%
   * complete so the UI doesn't pop in before the camera has settled.
   */
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

    // Start the look-proxy where the camera is actually pointing right now
    // so the first frame of the tween reads as a continuation, not a snap.
    const tmpDir = new THREE.Vector3();
    this.camera.getWorldDirection(tmpDir);
    const lookProxy = this.camera.position.clone().add(tmpDir);

    const duration = incoming ? ZOOM_DURATION : ZOOM_DURATION * 0.65;
    const panelEl = this.panelEl;
    let panelShown = false;

    // Lookproxy tween — same duration + ease as the position tween below.
    const lookTween = gsap.to(lookProxy, {
      x: look.x,
      y: look.y,
      z: look.z,
      duration,
      ease: "power2.inOut",
    });

    gsap.to(this.camera.position, {
      x: target.x,
      y: target.y,
      z: target.z,
      duration,
      ease: "power2.inOut",
      onUpdate: () => {
        this.camera.lookAt(lookProxy);
        if (!panelShown && lookTween.progress() > 0.8) {
          panelShown = true;
          panelEl.classList.remove("hidden");
        }
      },
      onComplete: () => {
        this.camera.lookAt(look);
        this.zooming = false;
        if (!panelShown) panelEl.classList.remove("hidden");
      },
    });
  }

  // ── Contact ──────────────────────────────────────────────────────────────

  openContact() {
    if (this.contactOpen) return;
    this.contactOpen = true;
    this.#hidePrompt();
    this.audio?.playMenuOpen();
    this.controller.paused = true;
    this.contactEl.classList.remove("hidden");
    this.achievements?.onSectionVisited?.('contact');
  }

  closeContact() {
    if (!this.contactOpen) return;
    this.contactOpen = false;
    this.audio?.playMenuClose();
    this.controller.paused = false;
    this.contactEl.classList.add("hidden");
  }

  // ── Resume ────────────────────────────────────────────────────────────────

  openResume() {
    if (this.resumeOpen) return;
    this.resumeOpen = true;
    this.#hidePrompt();
    this.audio?.playMenuOpen();
    this.controller.paused = true;
    this.resumeEl.classList.remove("hidden");
    this.achievements?.onSectionVisited?.('resume');
  }

  closeResume() {
    if (!this.resumeOpen) return;
    this.resumeOpen = false;
    this.audio?.playMenuClose();
    this.controller.paused = false;
    this.resumeEl.classList.add("hidden");
  }

  // ── Skills sphere ────────────────────────────────────────────────────────

  get skillOpen() {
    return !!(this.skillSphere?.active || this.skillSphere?.zooming);
  }

  openSkills() {
    if (!this.skillSphere || this.skillOpen) return;
    this.#hidePrompt();
    this.skillSphere.enter();
  }

  closeSkills() {
    this.skillSphere?.exit?.();
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
    const total = this.billboards.projects?.length ?? this.billboards.items.length;
    counter.textContent = `${item.index + 1} / ${total}`;
  }
}
