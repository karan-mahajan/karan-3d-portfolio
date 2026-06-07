import gsap from "gsap";
import * as THREE from "three";
import { resume } from "./ResumeData.js";
import { getProjectField } from "./PortfolioData.js";
import { PORTFOLIO_URL } from "./ExperienceData.js";

const PROXIMITY = 4.5; // distance from billboard to show prompt
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
    projectsHut = null,
    contactBoard = null,
    experience = null,
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
    this.projectsHut = projectsHut;
    this.contactBoard = contactBoard;
    this.experience = experience;
    this.audio = audio;
    this.actionPrompts = actionPrompts;
    this.timeOfDay = timeOfDay;
    this.achievements = achievements;

    this.activeIndex = -1; // -1 = not focused
    this.candidate = null; // billboard the player is currently near
    this.contactCandidate = false;
    this.skillCandidate = false;
    this.projectsCandidate = false;
    this.resumeCandidate = false;
    this.resumeOpen = false;
    this.experienceCandidate = false;
    this.experienceOpen = false;
    this.experienceIndex = -1;
    this._experienceItem = null;
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
      <div class="panel-scroll">
        <div class="panel-accent"></div>
        <h2 class="panel-title"></h2>
        <p class="panel-meta"></p>
        <div class="panel-description"></div>
        <section class="panel-section panel-problem hidden"><h3>The Problem</h3><p></p></section>
        <section class="panel-section panel-solution hidden"><h3>The Solution</h3><p></p></section>
        <section class="panel-section panel-impact hidden"><h3>Impact</h3><p></p></section>
        <ul class="panel-highlights hidden"></ul>
        <div class="panel-tech"></div>
        <div class="panel-actions">
          <a class="panel-link" target="_blank" rel="noopener noreferrer">Open Site ↗</a>
          <a class="panel-github" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
        </div>
        <div class="panel-portfolio-note hidden"></div>
      </div>
      <nav class="panel-nav">
        <button class="panel-prev" aria-label="Previous">← Prev</button>
        <span class="panel-counter"></span>
        <button class="panel-next" aria-label="Next">Next →</button>
      </nav>
      <div class="panel-hint">ESC to return</div>
    `;
    document.body.appendChild(this.panelEl);

    // Panel controls are context-aware: inside the Projects hut they drive the
    // hut (so touch users — who have no arrow keys or ESC — can browse + exit),
    // otherwise they drive the single outdoor showcase.
    this.panelEl
      .querySelector(".panel-close")
      .addEventListener("click", () =>
        this.experienceOpen
          ? this.closeExperience()
          : this.projectsOpen
            ? this.closeProjects()
            : this.exit());
    this.panelEl
      .querySelector(".panel-prev")
      .addEventListener("click", () =>
        this.experienceOpen
          ? this.experienceNav(-1)
          : this.projectsOpen
            ? this.projectsHutNav(-1)
            : this.cycle(-1));
    this.panelEl
      .querySelector(".panel-next")
      .addEventListener("click", () =>
        this.experienceOpen
          ? this.experienceNav(+1)
          : this.projectsOpen
            ? this.projectsHutNav(+1)
            : this.cycle(+1));

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
        if (this.contactOpen || this.resumeOpen || this.skillOpen || this.projectsOpen || this.experienceOpen) return;
        if (this.activeIndex === -1) {
          // Resume is a smaller proximity than contact, so when both fire
          // (shouldn't happen — different anchors — but be defensive), the
          // resume lectern wins.
          if (this.resumeCandidate) this.openResume();
          else if (this.contactCandidate) this.openContact();
          else if (this.skillCandidate) this.openSkills();
          else if (this.projectsCandidate) this.openProjects();
          else if (this.experienceCandidate) this.openExperience(this._experienceItem?.index ?? 0);
          else if (this.candidate) this.focus(this.candidate.index);
        }
      } else if (e.code === "Escape") {
        if (this.skillOpen) this.closeSkills();
        else if (this.projectsOpen) this.closeProjects();
        else if (this.experienceOpen) this.closeExperience();
        else if (this.resumeOpen) this.closeResume();
        else if (this.contactOpen) this.closeContact();
        else if (this.activeIndex !== -1) this.exit();
      } else if (this.experienceOpen) {
        if (e.code === "ArrowLeft" || e.code === "KeyA") this.experienceNav(-1);
        else if (e.code === "ArrowRight" || e.code === "KeyD") this.experienceNav(+1);
      } else if (this.projectsOpen) {
        if (e.code === "ArrowLeft" || e.code === "KeyA") this.projectsHutNav(-1);
        else if (e.code === "ArrowRight" || e.code === "KeyD") this.projectsHutNav(+1);
      } else if (this.activeIndex !== -1) {
        if (e.code === "ArrowLeft") this.cycle(-1);
        else if (e.code === "ArrowRight") this.cycle(+1);
      }
    };
    window.addEventListener("keydown", this._onKey);
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────

  tick(playerPosition) {
    if (this.activeIndex !== -1 || this.zooming || this.contactOpen || this.resumeOpen || this.skillOpen || this.projectsOpen || this.experienceOpen) {
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
    const nearContact = this.contactBoard?.near?.(playerPosition);
    const nearResume =
      this.signs && this.signs.nearResume?.(playerPosition, RESUME_PROXIMITY);
    const nearSkills = this.skillSphere?.near?.(playerPosition);
    const nearProjects = this.projectsHut?.near?.(playerPosition);
    const nearExperience = this.experience?.near?.(playerPosition);
    this.candidate = nearBillboard;
    // Resume has the smallest proximity radius — when both fire, prefer it.
    this.resumeCandidate = !!nearResume && !nearBillboard;
    this.contactCandidate = !!nearContact && !nearBillboard && !nearResume;
    this.skillCandidate = !!nearSkills && !nearBillboard && !nearResume && !nearContact;
    this.projectsCandidate =
      !!nearProjects && !nearBillboard && !nearResume && !nearContact && !nearSkills;
    this._experienceItem = nearExperience || null;
    this.experienceCandidate =
      !!nearExperience && !nearBillboard && !nearResume && !nearContact && !nearSkills && !nearProjects;

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
    else if (this.contactCandidate) this.#showPrompt("Contact", "Enter");
    else if (this.skillCandidate) this.#showPrompt("Skills", "Enter");
    else if (this.projectsCandidate) this.#showPrompt("Projects", "Enter");
    else if (this.experienceCandidate)
      this.#showPrompt(this._experienceItem?.company ?? "Experience");
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
    const total = this.billboards.projects?.length ?? this.billboards.items.length;
    this.panelEl.classList.remove("projects-mode");
    this.#populatePanel(item.project, item.index, total);
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
      this.#populatePanel(item.project, item.index, n);
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

  /** True while the contact-board dolly is animating in/out or held at the board. */
  get contactOpen() {
    return !!(this.contactBoard?.active || this.contactBoard?.zooming);
  }

  openContact() {
    if (!this.contactBoard || this.contactOpen) return;
    this.#hidePrompt();
    this.contactBoard.enter();
  }

  closeContact() {
    this.contactBoard?.exit?.();
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

  // ── Experience (Career Ascent on the bridge) ──────────────────────────────

  /**
   * Open the Career-Ascent detail panel for a station. No camera dolly — the
   * stations float over the water and the player stays on the deck, so this
   * mirrors the Résumé overlay (pause + show the shared panel) rather than the
   * zoom-in focus used for billboards. The panel reuses `.project-panel`; the
   * prev/next/close buttons route here while `experienceOpen` is set.
   */
  openExperience(index) {
    const items = this.experience?.items;
    if (!items?.length || this.experienceOpen) return;
    this.experienceIndex = ((index % items.length) + items.length) % items.length;
    this.experienceOpen = true;
    this.experience.cardSuppressed = true; // hide the ambient auto-card behind the panel
    this.#hidePrompt();
    this.audio?.playMenuOpen?.();
    this.controller.paused = true;
    this.panelEl.classList.remove("projects-mode");
    this.#showExperiencePanel();
    this.panelEl.classList.remove("hidden");
    this.achievements?.onSectionVisited?.("experience");
  }

  closeExperience() {
    if (!this.experienceOpen) return;
    this.experienceOpen = false;
    this.panelEl.classList.add("hidden");
    this.audio?.playMenuClose?.();
    this.controller.paused = false;
    if (this.experience) this.experience.cardSuppressed = false;
  }

  /** Browse to the prev/next company while the panel is open. */
  experienceNav(direction) {
    const n = this.experience?.items?.length ?? 0;
    if (n <= 1) return;
    this.experienceIndex = (this.experienceIndex + direction + n) % n;
    this.audio?.playInteract?.();
    this.#showExperiencePanel();
  }

  /** Populate the shared detail panel from the current experience station. */
  #showExperiencePanel() {
    const st = this.experience?.items?.[this.experienceIndex];
    if (!st) return;
    // Shape an experience entry like a project so #populatePanel formats the
    // meta row (year · role) + the full bullet-point details (as highlights),
    // and hides the empty case-study/tech/link blocks.
    this.#populatePanel(
      {
        name: st.company,
        color: st.accent,
        year: st.year ? String(st.year) : "",
        category: "",
        role: st.role,
        description: "",
        highlights: st.points,
        tech: [],
      },
      this.experienceIndex,
      this.experience.items.length,
    );
    // Footer CTA to the full portfolio (only on experience cards).
    const note = this.panelEl.querySelector(".panel-portfolio-note");
    if (note) {
      note.innerHTML =
        `Want the full story? See every role in detail at ` +
        `<a href="${PORTFOLIO_URL}" target="_blank" rel="noopener noreferrer">karanmahajan.ca ↗</a>`;
      note.classList.remove("hidden");
    }
    this.achievements?.onExperienceSignViewed?.(st.index);
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

  // ── Projects hut ───────────────────────────────────────────────────────────

  get projectsOpen() {
    return !!(this.projectsHut?.active || this.projectsHut?.zooming);
  }

  openProjects() {
    if (!this.projectsHut || this.projectsOpen) return;
    this.#hidePrompt();
    this.projectsHut.enter();
    this.#showProjectsPanel();
  }

  closeProjects() {
    this.projectsHut?.exit?.();
    this.panelEl.classList.add("hidden");
    this.panelEl.classList.remove("projects-mode");
  }

  /** Step the hut board and keep the detail panel in sync. */
  projectsHutNav(direction) {
    if (!this.projectsHut) return;
    if (direction < 0) this.projectsHut.prev();
    else this.projectsHut.next();
    this.#showProjectsPanel();
  }

  /**
   * Populate + reveal the shared detail panel for the hut's current project.
   * `projects-mode` hides the panel's own nav/close/hint — the hut owns
   * navigation (arrow keys) and its centred hint shows the controls.
   */
  #showProjectsPanel() {
    const hut = this.projectsHut;
    const project = hut.projects?.[hut.currentIndex];
    if (!project) return;
    this.panelEl.classList.add("projects-mode");
    this.#populatePanel(project, hut.currentIndex, hut.projects.length);
    this.panelEl.classList.remove("hidden");
  }

  #populatePanel(p, index, total) {
    const panel = this.panelEl;

    panel.querySelector(".panel-title").textContent = p.name;
    panel.querySelector(".panel-accent").style.background = p.color;

    // Meta row: year · category · role — drop empty parts so we never render
    // dangling separators.
    const meta = [
      getProjectField(p, "year", ""),
      getProjectField(p, "category", ""),
      getProjectField(p, "role", ""),
    ].filter(Boolean).join("  ·  ");
    panel.querySelector(".panel-meta").textContent = meta;

    // Description: split blank-line-separated paragraphs into <p> blocks so a
    // long narrative reads as paragraphs rather than one wall of text.
    const descEl = panel.querySelector(".panel-description");
    descEl.innerHTML = "";
    const desc = getProjectField(p, "description", getProjectField(p, "summary"));
    for (const para of String(desc).split(/\n\s*\n/)) {
      const text = para.trim();
      if (!text) continue;
      const el = document.createElement("p");
      el.textContent = text;
      descEl.appendChild(el);
    }

    // Case-study sections — wired now, dormant until the data is populated.
    this.#toggleSection(".panel-problem", getProjectField(p, "problem", ""));
    this.#toggleSection(".panel-solution", getProjectField(p, "solution", ""));
    this.#toggleSection(".panel-impact", getProjectField(p, "impact", ""));

    const highlights = Array.isArray(p.highlights) ? p.highlights : [];
    const hl = panel.querySelector(".panel-highlights");
    hl.innerHTML = "";
    if (highlights.length) {
      for (const h of highlights) {
        const li = document.createElement("li");
        li.textContent = h;
        hl.appendChild(li);
      }
      hl.classList.remove("hidden");
    } else {
      hl.classList.add("hidden");
    }

    const techEl = panel.querySelector(".panel-tech");
    techEl.innerHTML = "";
    for (const t of p.tech || []) {
      const pill = document.createElement("span");
      pill.className = "tech-pill";
      pill.textContent = t;
      techEl.appendChild(pill);
    }

    this.#toggleLink(".panel-link", getProjectField(p, "liveUrl"));
    this.#toggleLink(".panel-github", getProjectField(p, "github"));

    const counter = panel.querySelector(".panel-counter");
    counter.textContent = `${index + 1} / ${total}`;

    // Portfolio note is experience-only — hidden unless #showExperiencePanel
    // re-shows it for this same panel.
    panel.querySelector(".panel-portfolio-note")?.classList.add("hidden");

    // Long descriptions scroll — reset to the top whenever content swaps.
    panel.querySelector(".panel-scroll").scrollTop = 0;
  }

  #toggleSection(selector, text) {
    const el = this.panelEl.querySelector(selector);
    if (text) {
      el.querySelector("p").textContent = text;
      el.classList.remove("hidden");
    } else {
      el.classList.add("hidden");
    }
  }

  #toggleLink(selector, href) {
    const link = this.panelEl.querySelector(selector);
    if (href) {
      link.href = href;
      link.style.display = "";
    } else {
      link.removeAttribute("href");
      link.style.display = "none";
    }
  }
}
