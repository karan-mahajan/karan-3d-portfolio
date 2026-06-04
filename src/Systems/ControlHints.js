/**
 * Contextual control hints — gently nudge a new player toward the two controls
 * they're most likely to miss: Shift-to-run and Space-to-jump.
 *
 * Trigger rules:
 *   - RUN:  after ~11s of *walking* without ever running this session.
 *   - JUMP: after ~15s of play without ever jumping this session.
 *
 * Cadence: each hint shows at most ONCE per session, and at most TWICE per
 * visitor ever (persisted counts). The instant the player actually uses the
 * control, a "known" flag is written and that hint never shows again — no
 * point nagging someone who already discovered it.
 *
 * Desktop-only: touch builds already surface visible on-screen run/jump
 * buttons, so the keyboard hints don't apply there.
 */

const LS = {
  runCount: 'karan-portfolio:hint-run-count',
  runKnown: 'karan-portfolio:hint-run-known',
  jumpCount: 'karan-portfolio:hint-jump-count',
  jumpKnown: 'karan-portfolio:hint-jump-known',
};

const RUN_WALK_SECONDS = 11; // cumulative walking before the run nudge
const JUMP_PLAY_SECONDS = 15; // play time before the jump nudge
const MAX_SHOWS = 2; // lifetime shows per hint (across sessions)
const VISIBLE_MS = 5200; // how long a banner stays up
const GAP_MS = 700; // spacing so two queued hints never overlap

export class ControlHints {
  #root;
  #el;
  #disabled;
  #run;
  #jump;
  #queue;
  #showing;
  #activeUntil;
  #nextAllowedAt;

  constructor() {
    this.#disabled =
      typeof document === 'undefined' ||
      document.body.classList.contains('is-mobile');
    this.#queue = [];
    this.#showing = null;
    this.#activeUntil = 0;
    this.#nextAllowedAt = 0;

    // Per-session accumulators reset every load; counts/known persist.
    this.#run = {
      ls: { count: LS.runCount, known: LS.runKnown },
      accum: 0,
      shown: false,
      count: this.#readInt(LS.runCount),
      known: this.#readBool(LS.runKnown),
    };
    this.#jump = {
      ls: { count: LS.jumpCount, known: LS.jumpKnown },
      accum: 0,
      shown: false,
      count: this.#readInt(LS.jumpCount),
      known: this.#readBool(LS.jumpKnown),
    };

    if (!this.#disabled) this.#buildDom();
  }

  #readInt(k) {
    try { return parseInt(localStorage.getItem(k) || '0', 10) || 0; } catch { return 0; }
  }
  #readBool(k) {
    try { return localStorage.getItem(k) === '1'; } catch { return false; }
  }
  #persist(k, v) {
    try { localStorage.setItem(k, String(v)); } catch { /* private mode */ }
  }

  #buildDom() {
    const root = document.createElement('div');
    root.id = 'control-hint-root';
    root.className = 'control-hint-root';
    const el = document.createElement('div');
    el.className = 'control-hint';
    root.appendChild(el);
    document.body.appendChild(root);
    this.#root = root;
    this.#el = el;
  }

  /**
   * @param {number} dt seconds since last frame
   * @param {{moving:boolean, running:boolean, jumped:boolean, paused:boolean}} state
   */
  update(dt, state) {
    if (this.#disabled) return;
    const now = performance.now();

    // The player used the control → remember it, retire the hint for good.
    if (state.running && !this.#run.known) {
      this.#run.known = true;
      this.#persist(LS.runKnown, 1);
    }
    if (state.jumped && !this.#jump.known) {
      this.#jump.known = true;
      this.#persist(LS.jumpKnown, 1);
    }

    if (!state.paused) {
      // RUN — accrue only while actually walking (not already running).
      if (this.#eligible(this.#run) && state.moving && !state.running) {
        this.#run.accum += dt;
        if (this.#run.accum >= RUN_WALK_SECONDS) this.#fire('run');
      }
      // JUMP — accrue plain play time.
      if (this.#eligible(this.#jump)) {
        this.#jump.accum += dt;
        if (this.#jump.accum >= JUMP_PLAY_SECONDS) this.#fire('jump');
      }
    }

    this.#pump(now);
  }

  #eligible(h) {
    return !h.known && !h.shown && h.count < MAX_SHOWS;
  }

  #fire(kind) {
    const h = kind === 'run' ? this.#run : this.#jump;
    if (!this.#eligible(h)) return;
    h.shown = true; // once per session
    h.count += 1;
    this.#persist(h.ls.count, h.count);
    this.#queue.push(kind);
  }

  #pump(now) {
    // Retire an expired banner.
    if (this.#showing && now >= this.#activeUntil) {
      this.#el.classList.remove('is-shown');
      this.#showing = null;
      this.#nextAllowedAt = now + GAP_MS;
    }
    // Promote the next queued hint once the gap has elapsed.
    if (!this.#showing && this.#queue.length && now >= this.#nextAllowedAt) {
      this.#render(this.#queue.shift());
      this.#showing = true;
      this.#activeUntil = now + VISIBLE_MS;
    }
  }

  #render(kind) {
    const { key, text } =
      kind === 'run'
        ? { key: 'Shift', text: 'Hold to run faster' }
        : { key: 'Space', text: 'Tap to jump' };
    this.#el.innerHTML =
      `<span class="control-hint-key">${key}</span>` +
      `<span class="control-hint-text">${text}</span>`;
    void this.#el.offsetWidth; // reflow so the transition plays from hidden
    this.#el.classList.add('is-shown');
  }

  dispose() {
    this.#root?.remove();
    this.#root = null;
  }
}
