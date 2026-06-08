/**
 * The like affordance + visitor readout. Deliberately NOT a dead "Like" button:
 * it shows the LIVE global count (social proof — people join a number far more
 * readily than they press a blank button), and liking releases a spark into the
 * sky cluster (LikeLights) with a satisfying burst + chime. One like per
 * visitor; once liked it settles into a glowing "thanks" state.
 *
 * A single, engagement-timed nudge (never on a loop) gently pulses the pill once
 * the visitor is invested — never a repeating pop-up.
 */
import { Confetti } from "./Confetti.js";

const NUDGE_KEY = "karan-portfolio:like-nudged";
const NUDGE_DELAY_MS = 60000; // earliest the nudge may appear after start()

export class SocialHud {
  constructor({ social, likeLights, player, audio = null, controller = null }) {
    this.social = social;
    this.likeLights = likeLights;
    this.player = player;
    this.audio = audio;
    this.controller = controller;

    this._nudged = sessionStorage.getItem(NUDGE_KEY) === "1";
    this._engaged = false;
    this._nudgeTimer = null;
    this.confetti = new Confetti();

    this.#buildDom();
    this.#installKeys();

    // React to every backend state change (initial load, like, etc.).
    this._unsub = this.social.onChange(() => this.#render());
    this.#render();
  }

  // ── DOM ───────────────────────────────────────────────────────────────────
  #buildDom() {
    this.root = document.createElement("div");
    this.root.className = "social-like hidden";
    this.root.innerHTML = `
      <button class="social-like-btn" type="button" aria-label="Send a light">
        <span class="social-like-spark" aria-hidden="true">✦</span>
        <span class="social-like-count">0</span>
      </button>
      <div class="social-like-sub"></div>
      <div class="social-like-nudge hidden">Loving it? Send a light ✦</div>
    `;
    document.body.appendChild(this.root);

    this.btn = this.root.querySelector(".social-like-btn");
    this.countEl = this.root.querySelector(".social-like-count");
    this.subEl = this.root.querySelector(".social-like-sub");
    this.nudgeEl = this.root.querySelector(".social-like-nudge");

    this.btn.addEventListener("click", () => this.#tryLike());
  }

  #installKeys() {
    this._onKey = (e) => {
      if (e.code !== "KeyL") return;
      // Never while typing (whisper compose) or while a modal owns the controls.
      const el = document.activeElement;
      if (el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT")) return;
      if (this.controller?.paused) return;
      this.#tryLike();
    };
    window.addEventListener("keydown", this._onKey);
  }

  // ── Behaviour ───────────────────────────────────────────────────────────────
  async #tryLike() {
    if (this.social.liked || !this.social.configured) return;
    const did = await this.social.like();
    if (!did) return;
    // Release a spark from the player up into the sky cluster + a HUD burst +
    // a confetti shower so the like clearly *does* something on screen.
    const p = this.player?.position;
    if (p && this.likeLights) this.likeLights.release(p);
    this.confetti.burst();
    this.audio?.playInteract?.();
    this.btn.classList.remove("burst");
    // Force reflow so the animation restarts even on rapid re-trigger.
    void this.btn.offsetWidth;
    this.btn.classList.add("burst");
    this.#hideNudge();
  }

  /** Begin the engagement clock (call once after onboarding hands off). */
  start() {
    if (this._nudged) return;
    this._nudgeTimer = setTimeout(() => this.#maybeNudge(), NUDGE_DELAY_MS);
  }

  /** Signal that the visitor is engaged (e.g. visited a section) — may nudge sooner. */
  bumpEngagement() {
    this._engaged = true;
    this.#maybeNudge();
  }

  #maybeNudge() {
    if (this._nudged || this.social.liked || !this.social.configured) return;
    // Only nudge once genuinely engaged: either the timer elapsed or a section
    // was visited. (start()'s timer sets neither flag, so it nudges on time.)
    this._nudged = true;
    sessionStorage.setItem(NUDGE_KEY, "1");
    this.root.classList.add("pulse");
    this.nudgeEl.classList.remove("hidden");
    clearTimeout(this._hideNudgeTimer);
    this._hideNudgeTimer = setTimeout(() => this.#hideNudge(), 6500);
  }

  #hideNudge() {
    this.root.classList.remove("pulse");
    this.nudgeEl?.classList.add("hidden");
  }

  // ── Render ────────────────────────────────────────────────────────────────
  #render() {
    // Stay hidden until we actually have data + a configured backend, so a
    // broken/missing DB never shows a lonely "0".
    if (!this.social.ready || !this.social.configured) {
      this.root.classList.add("hidden");
      return;
    }
    this.root.classList.remove("hidden");
    this.countEl.textContent = this.social.likes.toLocaleString();
    this.root.classList.toggle("liked", this.social.liked);
    this.btn.disabled = this.social.liked;
    this.btn.setAttribute(
      "aria-label",
      this.social.liked ? "You sent a light" : "Send a light",
    );

    const v = this.social.visitors;
    this.subEl.textContent = v > 0
      ? `${v.toLocaleString()} ${v === 1 ? "explorer" : "explorers"}`
      : "";
  }

  destroy() {
    window.removeEventListener("keydown", this._onKey);
    clearTimeout(this._nudgeTimer);
    clearTimeout(this._hideNudgeTimer);
    this._unsub?.();
    this.root?.remove();
  }
}
