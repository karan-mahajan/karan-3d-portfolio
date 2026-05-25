/**
 * First-visit coachmarks (checklist style).
 *
 * Shows a small floating card listing the three gestures a new player needs
 * to learn:
 *   1. Move      — WASD on desktop, virtual joystick on mobile
 *   2. Look      — mouse drag on desktop, right-side swipe on mobile
 *   3. Zoom      — scroll wheel on desktop, pinch on mobile
 *
 * Detection runs in parallel: any pending gesture may complete in any order,
 * which matches how players actually explore (they'll often zoom or drag
 * before they walk). When a gesture is detected, that row collapses out of
 * the list; the card itself stays until every row is gone. After the last
 * row completes the card fades out and a localStorage flag is written so
 * the tutorial is skipped on subsequent visits.
 *
 * Detection is input-agnostic for look/zoom: we sample camera
 * azimuth/distance and compare to the value captured at start, which covers
 * mouse, touch, pinch, AND any future input mode through the same code
 * path. Move is the one exception — position isn't a reliable signal
 * because the player can deliberately stand still, so we read the
 * controller's key set + mobile-intent flag instead.
 *
 * Reset for QA: `window.__resetTutorial()` clears the flag.
 */

const STORAGE_KEY = 'karan-portfolio:tutorial-completed';

// Total accumulated drag distance (canvas pixels) before we consider the
// player to have intentionally turned the camera. ~30px is a small but
// deliberate swipe — well above any accidental click jitter.
const DRAG_PIXELS_NEEDED = 30;

export class Tutorial {
  #controller;
  #root;
  #listEl;
  #steps;
  #pending;
  #rowEls;
  #raf;
  #disposed;
  #isMobile;
  #finishing;
  #dragAccum;
  #dragLast;
  #dragging;
  #lookFired;
  #zoomFired;
  #onPointerDown;
  #onPointerMove;
  #onPointerUp;
  #onWheel;
  #onTouchStart;
  #onTouchMove;
  #onTouchEnd;

  constructor({ controller }) {
    this.#controller = controller;
    this.#disposed = false;
    this.#dragAccum = 0;
    this.#dragLast = null;
    this.#dragging = false;
    this.#lookFired = false;
    this.#zoomFired = false;

    if (typeof window !== 'undefined') {
      window.__resetTutorial = () => {
        try { localStorage.removeItem(STORAGE_KEY); } catch {}
        return 'Tutorial reset. Reload the page to see it again.';
      };
    }
  }

  start() {
    if (this.#raf || this.#disposed) return;
    if (this.#hasCompleted()) return;

    this.#isMobile = document.body.classList.contains('is-mobile');
    this.#buildSteps();
    this.#pending = new Set(this.#steps.map((s) => s.key));
    this.#rowEls = new Map();
    this.#buildDom();
    this.#attachInputListeners();

    this.#raf = requestAnimationFrame(this.#tick);
  }

  dispose() {
    this.#disposed = true;
    if (this.#raf) cancelAnimationFrame(this.#raf);
    this.#raf = null;
    this.#detachInputListeners();
    this.#root?.remove();
    this.#root = null;
  }

  // ── Steps ────────────────────────────────────────────────────────────────

  #buildSteps() {
    if (this.#isMobile) {
      this.#steps = [
        {
          key: 'move',
          title: 'Move',
          hint: 'Drag the left side',
          gesture: () => this.#joystickGesture(),
          detect: () => this.#detectMobileMove(),
        },
        {
          key: 'look',
          title: 'Look',
          hint: 'Swipe the right side',
          gesture: () => this.#swipeGesture(),
          detect: () => this.#detectLook(),
        },
        {
          key: 'zoom',
          title: 'Zoom',
          hint: 'Pinch two fingers',
          gesture: () => this.#pinchGesture(),
          detect: () => this.#detectZoom(),
        },
      ];
    } else {
      this.#steps = [
        {
          key: 'move',
          title: 'Move',
          hint: 'W A S D',
          gesture: () => this.#wasdGesture(),
          detect: () => this.#detectDesktopMove(),
        },
        {
          key: 'look',
          title: 'Look',
          hint: 'Click + drag',
          gesture: () => this.#mouseDragGesture(),
          detect: () => this.#detectLook(),
        },
        {
          key: 'zoom',
          title: 'Zoom',
          hint: 'Scroll wheel',
          gesture: () => this.#scrollGesture(),
          detect: () => this.#detectZoom(),
        },
      ];
    }
  }

  // ── DOM ──────────────────────────────────────────────────────────────────

  #buildDom() {
    const root = document.createElement('div');
    root.id = 'tutorial-card';
    root.className = 'tutorial-card';
    root.innerHTML = `
      <div class="tutorial-head">
        <span class="tutorial-eyebrow">How to play</span>
        <button class="tutorial-skip" type="button" aria-label="Skip tutorial">Skip</button>
      </div>
      <ul class="tutorial-list" data-list></ul>
    `;
    document.body.appendChild(root);

    this.#root = root;
    this.#listEl = root.querySelector('[data-list]');

    for (const step of this.#steps) {
      const li = document.createElement('li');
      li.className = 'tutorial-row';
      li.dataset.key = step.key;
      const gesture = document.createElement('div');
      gesture.className = 'tutorial-gesture';
      gesture.appendChild(step.gesture());
      const body = document.createElement('div');
      body.className = 'tutorial-body';
      body.innerHTML = `
        <div class="tutorial-title"></div>
        <div class="tutorial-hint"></div>
      `;
      body.querySelector('.tutorial-title').textContent = step.title;
      body.querySelector('.tutorial-hint').textContent = step.hint;
      li.appendChild(gesture);
      li.appendChild(body);
      this.#listEl.appendChild(li);
      this.#rowEls.set(step.key, li);
    }

    // Skip hides the card for this visit but does NOT persist completion —
    // the tutorial reappears on reload until the user actually performs all
    // three gestures. (#finish is only called when #pending empties.)
    root.querySelector('.tutorial-skip')?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.#dismissTemp();
    });

    // Mount animation handled in CSS via .is-mounted class on next frame.
    requestAnimationFrame(() => root.classList.add('is-mounted'));
  }

  // ── Detection ────────────────────────────────────────────────────────────
  // Each gesture is detected from the raw input event that performs it, NOT
  // from the camera state. This is more reliable: walking into a billboard
  // can move `controls.distance` enough to false-trigger a distance-based
  // zoom check, and a focused panel that adjusts the camera can falsely
  // trigger a look check. Input events are unambiguous.

  #detectDesktopMove() {
    const keys = this.#controller?.keys;
    if (!keys) return false;
    return keys.has('KeyW') || keys.has('KeyA') || keys.has('KeyS') || keys.has('KeyD')
      || keys.has('ArrowUp') || keys.has('ArrowDown')
      || keys.has('ArrowLeft') || keys.has('ArrowRight');
  }

  #detectMobileMove() {
    return !!this.#controller?.mobileIntent?.active;
  }

  #detectLook() { return this.#lookFired; }
  #detectZoom() { return this.#zoomFired; }

  #attachInputListeners() {
    const canvas = document.getElementById('canvas');

    // ── Desktop: drag (look) + wheel (zoom) ─────────────────────────────
    this.#onPointerDown = (e) => {
      if (e.button !== 0) return;
      // Only count drags that start on the canvas — the tutorial card's
      // own pointer events shouldn't qualify, and neither should drags
      // that start inside any UI panel.
      const target = e.target;
      if (target && target.id !== 'canvas') return;
      this.#dragging = true;
      this.#dragLast = { x: e.clientX, y: e.clientY };
      this.#dragAccum = 0;
    };
    this.#onPointerMove = (e) => {
      if (!this.#dragging || !this.#dragLast) return;
      this.#dragAccum += Math.hypot(
        e.clientX - this.#dragLast.x,
        e.clientY - this.#dragLast.y,
      );
      this.#dragLast = { x: e.clientX, y: e.clientY };
      if (this.#dragAccum > DRAG_PIXELS_NEEDED) this.#lookFired = true;
    };
    this.#onPointerUp = () => {
      this.#dragging = false;
      this.#dragLast = null;
    };
    this.#onWheel = (e) => {
      if (Math.abs(e.deltaY) > 0) this.#zoomFired = true;
    };

    // ── Mobile: single-touch swipe (look) + two-finger pinch (zoom) ─────
    this.#onTouchStart = (e) => {
      if (e.touches.length >= 2) this.#zoomFired = true;
      if (e.touches.length === 1) {
        const t = e.touches[0];
        // Joystick zone covers roughly the left 45%. Look gesture is the
        // OPPOSITE side; ignore touches that begin in the joystick band.
        if (t.clientX < window.innerWidth * 0.5) return;
        this.#dragging = true;
        this.#dragLast = { x: t.clientX, y: t.clientY };
        this.#dragAccum = 0;
      }
    };
    this.#onTouchMove = (e) => {
      if (e.touches.length >= 2) {
        this.#zoomFired = true;
        return;
      }
      if (!this.#dragging || !this.#dragLast || e.touches.length !== 1) return;
      const t = e.touches[0];
      this.#dragAccum += Math.hypot(
        t.clientX - this.#dragLast.x,
        t.clientY - this.#dragLast.y,
      );
      this.#dragLast = { x: t.clientX, y: t.clientY };
      if (this.#dragAccum > DRAG_PIXELS_NEEDED) this.#lookFired = true;
    };
    this.#onTouchEnd = () => {
      this.#dragging = false;
      this.#dragLast = null;
    };

    const canvasTarget = canvas || window;
    canvasTarget.addEventListener('pointerdown', this.#onPointerDown);
    window.addEventListener('pointermove', this.#onPointerMove);
    window.addEventListener('pointerup', this.#onPointerUp);
    canvasTarget.addEventListener('wheel', this.#onWheel, { passive: true });
    canvasTarget.addEventListener('touchstart', this.#onTouchStart, { passive: true });
    window.addEventListener('touchmove', this.#onTouchMove, { passive: true });
    window.addEventListener('touchend', this.#onTouchEnd);
    window.addEventListener('touchcancel', this.#onTouchEnd);
  }

  #detachInputListeners() {
    const canvas = document.getElementById('canvas');
    const canvasTarget = canvas || window;
    if (this.#onPointerDown) canvasTarget.removeEventListener('pointerdown', this.#onPointerDown);
    if (this.#onPointerMove) window.removeEventListener('pointermove', this.#onPointerMove);
    if (this.#onPointerUp) window.removeEventListener('pointerup', this.#onPointerUp);
    if (this.#onWheel) canvasTarget.removeEventListener('wheel', this.#onWheel);
    if (this.#onTouchStart) canvasTarget.removeEventListener('touchstart', this.#onTouchStart);
    if (this.#onTouchMove) window.removeEventListener('touchmove', this.#onTouchMove);
    if (this.#onTouchEnd) {
      window.removeEventListener('touchend', this.#onTouchEnd);
      window.removeEventListener('touchcancel', this.#onTouchEnd);
    }
  }

  // ── Loop ─────────────────────────────────────────────────────────────────
  // Arrow-function field: private methods can't be rebound (they're not
  // writable), so we declare the rAF callback as a bound field directly.

  #tick = () => {
    if (this.#disposed) return;
    this.#raf = requestAnimationFrame(this.#tick);
    if (this.#finishing) return;
    for (const step of this.#steps) {
      if (!this.#pending.has(step.key)) continue;
      if (step.detect()) this.#completeStep(step.key);
    }
  };

  #completeStep(key) {
    if (!this.#pending.has(key)) return;
    this.#pending.delete(key);
    const row = this.#rowEls.get(key);
    if (row) {
      row.classList.add('is-done');
      // Collapse + fade, then remove. The 360 ms matches the CSS transition
      // on .tutorial-row.is-done — keep the two in sync if you tune one.
      setTimeout(() => {
        if (this.#disposed) return;
        row.remove();
        this.#rowEls.delete(key);
        if (this.#pending.size === 0) this.#finish();
      }, 360);
    } else if (this.#pending.size === 0) {
      this.#finish();
    }
  }

  #finish() {
    if (this.#finishing) return;
    this.#finishing = true;
    try { localStorage.setItem(STORAGE_KEY, '1'); } catch {}
    if (!this.#root) { this.dispose(); return; }
    this.#root.classList.add('is-leaving');
    setTimeout(() => this.dispose(), 400);
  }

  /** Skip — dismiss the card for this visit without writing the completion
   *  flag, so it reappears on the next reload. */
  #dismissTemp() {
    if (this.#finishing) return;
    this.#finishing = true;
    if (!this.#root) { this.dispose(); return; }
    this.#root.classList.add('is-leaving');
    setTimeout(() => this.dispose(), 400);
  }

  #hasCompleted() {
    try { return localStorage.getItem(STORAGE_KEY) === '1'; } catch { return false; }
  }

  // ── Gesture visuals ──────────────────────────────────────────────────────
  // All visuals are pure DOM/CSS so they animate without touching the GPU
  // budget the scene cares about.

  #wasdGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-wasd';
    wrap.innerHTML = `
      <div class="g-wasd-row"><span class="key" data-k="W">W</span></div>
      <div class="g-wasd-row">
        <span class="key" data-k="A">A</span>
        <span class="key" data-k="S">S</span>
        <span class="key" data-k="D">D</span>
      </div>
    `;
    return wrap;
  }

  #joystickGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-joystick';
    wrap.innerHTML = `
      <div class="g-joystick-ring">
        <div class="g-joystick-thumb"></div>
      </div>
    `;
    return wrap;
  }

  #mouseDragGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-mouse-drag';
    wrap.innerHTML = `
      <svg viewBox="0 0 80 60" width="80" height="60" aria-hidden="true">
        <rect x="30" y="6" width="20" height="34" rx="10" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="40" y1="6" x2="40" y2="20" stroke="currentColor" stroke-width="2"/>
      </svg>
      <div class="g-mouse-arrow"></div>
    `;
    return wrap;
  }

  #swipeGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-swipe';
    wrap.innerHTML = `
      <div class="g-swipe-trail"></div>
      <div class="g-swipe-finger"></div>
    `;
    return wrap;
  }

  #scrollGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-scroll';
    wrap.innerHTML = `
      <svg viewBox="0 0 80 60" width="80" height="60" aria-hidden="true">
        <rect x="30" y="6" width="20" height="34" rx="10" fill="none" stroke="currentColor" stroke-width="2"/>
        <line x1="40" y1="14" x2="40" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <div class="g-scroll-up">▲</div>
      <div class="g-scroll-down">▼</div>
    `;
    return wrap;
  }

  #pinchGesture() {
    const wrap = document.createElement('div');
    wrap.className = 'g-pinch';
    wrap.innerHTML = `
      <div class="g-pinch-finger g-pinch-a"></div>
      <div class="g-pinch-finger g-pinch-b"></div>
    `;
    return wrap;
  }
}
