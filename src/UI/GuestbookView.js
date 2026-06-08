/**
 * Guestbook UI — two modes that pair with the in-world camera tour:
 *
 *  • READING: a small caption card (bottom of screen) showing ONE note while the
 *    camera is parked in front of its hanging tag on the tree. ←/→ move to the
 *    next/previous note (the GuestbookTree flies the camera there + calls
 *    showReading again). A "Leave a note" button switches to compose.
 *  • COMPOSE: a centred card with the name + message form (dims the world).
 *
 * The view owns DOM + the post request; navigation/camera is delegated to the
 * GuestbookTree via callbacks. Typing never leaks into the game (keydown in the
 * fields stops propagation; Escape closes, ⌘/Ctrl-Enter posts).
 */
const TEXT_MAX = 140;
const NAME_MAX = 24;

export class GuestbookView {
  constructor({ social, audio = null, onPrev, onNext, onSign, onBack, onClose, onPosted }) {
    this.social = social;
    this.audio = audio;
    this.onPrev = onPrev;
    this.onNext = onNext;
    this.onSign = onSign;
    this.onBack = onBack;
    this.onClose = onClose;
    this.onPosted = onPosted;
    this.#build();
  }

  #build() {
    this.root = document.createElement("div");
    this.root.className = "guestbook-view hidden";
    this.root.innerHTML = `
      <!-- Reading caption (camera parked at the note) -->
      <div class="guestbook-card guestbook-read">
        <button class="guestbook-close" data-close aria-label="Close">×</button>
        <div class="guestbook-note">
          <p class="guestbook-msg"></p>
          <div class="guestbook-meta"><span class="guestbook-by"></span><span class="guestbook-time"></span></div>
        </div>
        <div class="guestbook-readnav">
          <button class="guestbook-prev" aria-label="Previous note">←</button>
          <span class="guestbook-counter"></span>
          <button class="guestbook-next" aria-label="Next note">→</button>
        </div>
        <button class="guestbook-signbtn" type="button">Leave a note ✦</button>
        <div class="guestbook-hint">← → browse · ESC to step back</div>
      </div>

      <!-- Compose card -->
      <div class="guestbook-card guestbook-compose-card hidden">
        <button class="guestbook-close" data-close aria-label="Close">×</button>
        <h2 class="guestbook-title">Leave a note</h2>
        <p class="guestbook-sub">Enjoyed the visit? Leave a note for the next traveller.</p>
        <form class="guestbook-compose">
          <input class="guestbook-name" maxlength="${NAME_MAX}" placeholder="Your name (optional)" autocomplete="off" />
          <textarea class="guestbook-text" maxlength="${TEXT_MAX}" rows="2" placeholder="Leave a note…"></textarea>
          <div class="guestbook-row">
            <span class="guestbook-count">0/${TEXT_MAX}</span>
            <span class="guestbook-feedback" role="status"></span>
            <button class="guestbook-submit" type="submit">Leave it on the tree ✦</button>
          </div>
        </form>
        <button class="guestbook-back hidden" type="button">← Back to the notes</button>
        <div class="guestbook-hint">ESC to step back</div>
      </div>
    `;
    document.body.appendChild(this.root);

    this.readCard = this.root.querySelector(".guestbook-read");
    this.composeCard = this.root.querySelector(".guestbook-compose-card");
    this.msgEl = this.root.querySelector(".guestbook-msg");
    this.byEl = this.root.querySelector(".guestbook-by");
    this.timeEl = this.root.querySelector(".guestbook-time");
    this.counterEl = this.root.querySelector(".guestbook-counter");
    this.formEl = this.root.querySelector(".guestbook-compose");
    this.nameEl = this.root.querySelector(".guestbook-name");
    this.textEl = this.root.querySelector(".guestbook-text");
    this.countEl = this.root.querySelector(".guestbook-count");
    this.feedbackEl = this.root.querySelector(".guestbook-feedback");
    this.submitEl = this.root.querySelector(".guestbook-submit");
    this.backEl = this.root.querySelector(".guestbook-back");

    this.root.querySelectorAll("[data-close]").forEach((b) =>
      b.addEventListener("click", () => this.onClose?.()),
    );
    this.root.querySelector(".guestbook-prev").addEventListener("click", () => this.onPrev?.());
    this.root.querySelector(".guestbook-next").addEventListener("click", () => this.onNext?.());
    this.root.querySelector(".guestbook-signbtn").addEventListener("click", () => this.onSign?.());
    this.backEl.addEventListener("click", () => this.onBack?.());
    this.formEl.addEventListener("submit", (e) => {
      e.preventDefault();
      this.#submit();
    });
    this.textEl.addEventListener("input", () => this.#updateCount());

    const guard = (e) => {
      if (e.code === "Escape") { e.preventDefault(); this.onClose?.(); return; }
      if ((e.metaKey || e.ctrlKey) && e.code === "Enter") { e.preventDefault(); this.#submit(); return; }
      e.stopPropagation();
    };
    this.nameEl.addEventListener("keydown", guard);
    this.textEl.addEventListener("keydown", guard);
  }

  // ── Reading mode ────────────────────────────────────────────────────────────
  showReading(note, index, total) {
    this.root.classList.remove("hidden", "composing");
    this.composeCard.classList.add("hidden");
    this.readCard.classList.remove("hidden");
    this.msgEl.textContent = note?.text ?? "";
    this.byEl.textContent = note?.name ? `— ${note.name}` : "";
    this.timeEl.textContent = this.#relTime(note?.ts);
    this.counterEl.textContent = total > 1 ? `${index + 1} / ${total}` : "";
    const multi = total > 1;
    this.readCard.querySelector(".guestbook-prev").style.visibility = multi ? "" : "hidden";
    this.readCard.querySelector(".guestbook-next").style.visibility = multi ? "" : "hidden";
  }

  // ── Compose mode ────────────────────────────────────────────────────────────
  showCompose({ hasNotes = false } = {}) {
    this.root.classList.remove("hidden");
    this.root.classList.add("composing");
    this.readCard.classList.add("hidden");
    this.composeCard.classList.remove("hidden");
    this.backEl.classList.toggle("hidden", !hasNotes);
    this.#updateCount();
    this.#feedback("", "");
    requestAnimationFrame(() => this.textEl?.focus());
  }

  hide() {
    this.root.classList.add("hidden");
    this.root.classList.remove("composing");
    if (document.activeElement && this.root.contains(document.activeElement)) {
      document.activeElement.blur();
    }
  }

  // ── Posting ───────────────────────────────────────────────────────────────
  async #submit() {
    const text = this.textEl.value.trim();
    if (!text) {
      this.#feedback("Write a little something first.", "warn");
      return;
    }
    this.submitEl.disabled = true;
    this.#feedback("Leaving it…", "");
    const res = await this.social.sendWhisper(text, this.nameEl.value.trim());
    this.submitEl.disabled = false;
    if (res.ok) {
      this.audio?.playInteract?.();
      this.textEl.value = "";
      this.#updateCount();
      this.#feedback("Your note is on the tree ✦", "ok");
      this.backEl.classList.remove("hidden"); // there's at least one note now
      this.onPosted?.(res.whisper);
      return;
    }
    const msg =
      res.error === "blocked" || res.status === 422
        ? "Let's keep it kind — try different words."
        : res.error === "rate_limited" || res.status === 429
          ? "One note at a time — give it a moment."
          : res.error === "empty" || res.status === 400
            ? "Write a little something first."
            : "Couldn't reach the tree. Try again.";
    this.#feedback(msg, "warn");
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  #updateCount() {
    this.countEl.textContent = `${this.textEl.value.length}/${TEXT_MAX}`;
  }

  #feedback(text, kind) {
    this.feedbackEl.textContent = text;
    this.feedbackEl.dataset.kind = kind || "";
  }

  #relTime(ts) {
    if (!ts) return "";
    const s = Math.max(0, (Date.now() - ts) / 1000);
    if (s < 60) return "just now";
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    const d = Math.floor(h / 24);
    return d < 30 ? `${d}d ago` : "a while ago";
  }
}
