/**
 * AchievementToast — the cinematic unlock reveal.
 *
 * NOT a corner toast: a single centered, lower-third "moment" that blooms
 * into frame with a shimmer sweep, holds, then dissolves — closer to a
 * console "Achievement Unlocked" sting (Xbox / BOTW) than a web notification.
 * Rarity drives the crest glow, light rays, eyebrow label, AND how long it
 * lingers (a common First-Steps flashes; a legendary lingers).
 *
 * Anti-backlog: only ONE reveal is on screen at a time, but a *burst* (e.g. a
 * fresh start where movement + snow + water all unlock at once) would queue
 * and play for 30s — so you'd be watching a card for something you did ages
 * ago. Two guards prevent that: (1) a brief coalescing window gathers a
 * same-moment burst before the first card plays, and (2) while anything is
 * still queued behind the current card it plays in a fast "rapid" mode (short
 * flash) — the queue drains quickly and only the LAST/lone unlock gets the
 * full cinematic. The slow-mo + camera punch are driven from App's onUnlock.
 */
const COALESCE_MS = 170; // gather a same-moment burst before the first reveal
const RAPID = { in: 260, hold: 620, out: 260, gap: 70 };
const FULL = {
  common:    { in: 420, hold: 1500, out: 460, gap: 130 },
  rare:      { in: 520, hold: 2300, out: 520, gap: 150 },
  epic:      { in: 520, hold: 2900, out: 520, gap: 160 },
  legendary: { in: 560, hold: 3400, out: 560, gap: 180 },
};

export class AchievementToast {
  constructor() {
    this.container = document.getElementById('achievement-reveal-root');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'achievement-reveal-root';
      document.body.appendChild(this.container);
    }
    this._queue = [];
    this._busy = false;
    this._coalescing = false;
  }

  /** Queue a reveal for the given achievement record. */
  show(achievement) {
    if (!achievement) return;
    this._queue.push(achievement);
    // Idle → wait a beat so a synchronous burst all lands before the first
    // card plays (which then sees the backlog and goes rapid).
    if (!this._busy && !this._coalescing) {
      this._coalescing = true;
      setTimeout(() => { this._coalescing = false; this.#pump(); }, COALESCE_MS);
    }
  }

  #pump() {
    if (this._busy) return;
    const a = this._queue.shift();
    if (!a) return;
    this._busy = true;
    const backlog = this._queue.length > 0; // more waiting → drain fast
    this.#play(a, backlog, (gap) => {
      this._busy = false;
      if (this._queue.length) setTimeout(() => this.#pump(), gap);
    });
  }

  #play(achievement, rapid, done) {
    const rarity = achievement.rarity || 'common';
    const t = rapid ? RAPID : (FULL[rarity] || FULL.common);
    const eyebrow = achievement._synthetic
      ? 'MILESTONE'
      : rarity === 'common'
        ? 'ACHIEVEMENT UNLOCKED'
        : `${rarity.toUpperCase()} · UNLOCKED`;

    const el = document.createElement('div');
    el.className = `ach-reveal rarity-${rarity}${rapid ? ' rapid' : ''}`;
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    // Drive the in/out tween speed from the chosen timing (rapid = snappier).
    el.style.transitionDuration = `${t.in}ms`;
    el.innerHTML = `
      <div class="ach-reveal-rays"></div>
      <div class="ach-reveal-crest"><span class="ach-reveal-icon">${achievement.icon}</span></div>
      <div class="ach-reveal-text">
        <div class="ach-reveal-eyebrow"></div>
        <div class="ach-reveal-name"></div>
        <div class="ach-reveal-desc"></div>
      </div>
      <div class="ach-reveal-shimmer"></div>
    `;
    // textContent for the data-driven strings so names can't inject markup.
    el.querySelector('.ach-reveal-eyebrow').textContent = eyebrow;
    el.querySelector('.ach-reveal-name').textContent = achievement.name;
    el.querySelector('.ach-reveal-desc').textContent = achievement.description;
    this.container.appendChild(el);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => el.classList.add('in'));
    });
    setTimeout(() => {
      el.style.transitionDuration = `${t.out}ms`;
      el.classList.remove('in');
      el.classList.add('out');
      setTimeout(() => { el.remove(); done(t.gap); }, t.out);
    }, t.in + t.hold);
  }
}
