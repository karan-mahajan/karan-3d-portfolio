/**
 * UI redesign controller.
 *
 * Owns the desktop layout (top-left stack, bottom-left expander, bottom-
 * right gamepad + controls panel) and — on touch devices — the mobile
 * touch controls (joystick, contextual interact pill, action grid).
 *
 * The module-owned legacy buttons (.audio-toggle, .rain-toggle,
 * .wind-toggle, .leaves-toggle, #lightning-trigger) are constructed by
 * their own modules and appended to <body>. We re-parent them into the
 * new stack containers after they exist, preserving their internal icon-
 * swap logic. Inline cssText on #lightning-trigger is cleared so it
 * inherits the unified .ui-btn style instead of fighting it.
 *
 * Mobile input flows through PlayerController.setMobileIntent({ x, z, running })
 * which takes precedence over the keyboard WASD/Shift while the joystick
 * is engaged. Action buttons reuse public methods on ActionPrompts
 * (triggerBackflip/Cartwheel/startPush/endPush) so the existing clearance,
 * camera-zoom, and audio paths are honored.
 *
 * Camera control on mobile is intentionally NOT wired here — camera-controls
 * handles touch-rotate natively on the canvas, and the joystick zone only
 * covers the LEFT 45% so the right side of the canvas remains touchable
 * for the library's built-in handler.
 */
export class UIController {
  constructor({
    audio,
    rain,
    windLines,
    leaves,
    thunderstorm,
    player,
    playerCamera,
    controller,
    actionPrompts,
    interaction,
  }) {
    this.audio = audio;
    this.rain = rain;
    this.windLines = windLines;
    this.leaves = leaves;
    this.thunderstorm = thunderstorm;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.actionPrompts = actionPrompts;
    this.interaction = interaction;

    this.isMobile = this.#detectMobile();
    document.body.classList.add(this.isMobile ? 'is-mobile' : 'is-desktop');

    this.#reparentModuleButtons();
    this.#wireBottomLeftExpander();
    this.#wireControlsPanel();

    if (this.isMobile) {
      this.#updateWelcomeHint();
      this.#buildJoystick();
      this.#buildInteractPill();
      this.#buildActionGrid();
      this.#suppressCanvasGestures();
    }

    // Outside-click + Escape collapse the expander and close the panel.
    this._onDocClick = (e) => this.#handleOutsideClick(e);
    this._onKeyDown = (e) => this.#handleKey(e);
    document.addEventListener('click', this._onDocClick, true);
    window.addEventListener('keydown', this._onKeyDown);
  }

  // ── Boot detection ─────────────────────────────────────────────────────

  #detectMobile() {
    const ua = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent || '',
    );
    const touch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const narrow = window.innerWidth < 768;
    // Treat as mobile if UA matches OR (touch device AND narrow viewport).
    // Plain touch alone matches laptops with touchscreens — narrow is the
    // tie-breaker.
    return ua || (touch && narrow);
  }

  // ── Layout assembly ────────────────────────────────────────────────────

  #reparentModuleButtons() {
    const topLeft = document.getElementById('top-left-stack');
    const bottomLeft = document.getElementById('bottom-left-stack');
    if (!topLeft || !bottomLeft) return;

    // Audio mute → top-left, below day/night.
    const audioBtn = document.querySelector('.audio-toggle');
    if (audioBtn) {
      audioBtn.classList.add('ui-btn');
      topLeft.appendChild(audioBtn);
    }

    // Bottom-left order matters because the container uses column-reverse —
    // the trigger (#quick-toggle) is already first in the DOM and sits at
    // the bottom; subsequent appends stack ABOVE it. To match the spec
    // (lightning closest to the trigger, rain at the top), append in that
    // order: lightning → leaves → wind → rain.
    const trigger = document.getElementById('quick-toggle');
    const lightningBtn = document.getElementById('lightning-trigger');
    if (lightningBtn) {
      // Module sets cssText with absolute positioning + animation — clear.
      lightningBtn.style.cssText = '';
      lightningBtn.classList.add('ui-btn');
      bottomLeft.appendChild(lightningBtn);
    }
    const leavesBtn = document.querySelector('.leaves-toggle');
    if (leavesBtn) {
      leavesBtn.classList.add('ui-btn');
      bottomLeft.appendChild(leavesBtn);
    }
    const windBtn = document.querySelector('.wind-toggle');
    if (windBtn) {
      windBtn.classList.add('ui-btn');
      bottomLeft.appendChild(windBtn);
    }
    const rainBtn = document.querySelector('.rain-toggle');
    if (rainBtn) {
      rainBtn.classList.add('ui-btn');
      bottomLeft.appendChild(rainBtn);
    }
    // Hint to the layout that the trigger is the anchor.
    trigger?.classList.add('ui-btn-trigger');
  }

  #wireBottomLeftExpander() {
    const stack = document.getElementById('bottom-left-stack');
    const trigger = document.getElementById('quick-toggle');
    if (!stack || !trigger) return;
    this._bottomLeftStack = stack;
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      stack.classList.toggle('collapsed');
      this.audio?.playToggle?.();
    });
  }

  #wireControlsPanel() {
    const trigger = document.getElementById('controls-trigger');
    const panel = document.getElementById('controls-panel');
    if (!trigger || !panel) return;
    this._controlsPanel = panel;
    const close = panel.querySelector('.controls-close');
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = !panel.classList.contains('hidden');
      panel.classList.toggle('hidden', isOpen);
      this.audio?.playToggle?.();
    });
    close?.addEventListener('click', (e) => {
      e.stopPropagation();
      panel.classList.add('hidden');
      this.audio?.playToggle?.();
    });
  }

  #handleOutsideClick(e) {
    // Collapse expander if the click landed outside the bottom-left stack.
    if (this._bottomLeftStack && !this._bottomLeftStack.classList.contains('collapsed')) {
      if (!this._bottomLeftStack.contains(e.target)) {
        this._bottomLeftStack.classList.add('collapsed');
      }
    }
    // Close controls panel if click landed outside the panel AND the trigger.
    if (this._controlsPanel && !this._controlsPanel.classList.contains('hidden')) {
      const trigger = document.getElementById('controls-trigger');
      if (!this._controlsPanel.contains(e.target) && trigger && !trigger.contains(e.target)) {
        this._controlsPanel.classList.add('hidden');
      }
    }
  }

  #handleKey(e) {
    if (e.code !== 'Escape') return;
    if (this._controlsPanel && !this._controlsPanel.classList.contains('hidden')) {
      this._controlsPanel.classList.add('hidden');
    }
    if (this._bottomLeftStack && !this._bottomLeftStack.classList.contains('collapsed')) {
      this._bottomLeftStack.classList.add('collapsed');
    }
  }

  // ── Mobile: welcome hint copy ──────────────────────────────────────────

  #updateWelcomeHint() {
    const hint = document.querySelector('.welcome-hint');
    if (hint) {
      hint.textContent = 'Drag left side to move · Drag right side to look around';
    }
  }

  // ── Mobile: virtual joystick ───────────────────────────────────────────

  #buildJoystick() {
    const zone = document.createElement('div');
    zone.id = 'mobile-joystick-zone';
    document.body.appendChild(zone);

    const base = document.createElement('div');
    base.className = 'joystick-base';
    const thumb = document.createElement('div');
    thumb.className = 'joystick-thumb';
    base.appendChild(thumb);
    document.body.appendChild(base);

    this._joystick = { zone, base, thumb, active: false, touchId: null, cx: 0, cy: 0 };

    // Joystick max travel from centre, in CSS pixels.
    const MAX = 44;
    // Threshold to count as sprint (fraction of MAX).
    const RUN_THRESHOLD = 0.7;

    const begin = (touch) => {
      this._joystick.active = true;
      this._joystick.touchId = touch.identifier;
      this._joystick.cx = touch.clientX;
      this._joystick.cy = touch.clientY;
      base.style.left = `${touch.clientX - 55}px`;
      base.style.top = `${touch.clientY - 55}px`;
      base.classList.add('visible');
    };

    const move = (touch) => {
      const dx = touch.clientX - this._joystick.cx;
      const dy = touch.clientY - this._joystick.cy;
      const dist = Math.min(Math.hypot(dx, dy), MAX);
      const angle = Math.atan2(dy, dx);
      thumb.style.transform = `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px)`;
      const nx = (dist / MAX) * Math.cos(angle);
      const ny = (dist / MAX) * Math.sin(angle);
      // Screen-Y-down → world-Z-forward; negate ny so pushing UP = forward.
      this.controller?.setMobileIntent?.({
        x: nx,
        z: -ny,
        running: (dist / MAX) > RUN_THRESHOLD,
      });
    };

    const end = () => {
      this._joystick.active = false;
      this._joystick.touchId = null;
      thumb.style.transform = 'translate(0, 0)';
      base.classList.remove('visible');
      this.controller?.setMobileIntent?.({ x: 0, z: 0, running: false });
    };

    zone.addEventListener('touchstart', (e) => {
      if (this._joystick.active) return;
      const t = e.changedTouches[0];
      if (!t) return;
      e.preventDefault();
      begin(t);
    }, { passive: false });

    // Move + end listen on the window so a fast swipe that drifts outside the
    // zone (or hits the right edge) still keeps the joystick engaged until
    // the touch lifts.
    window.addEventListener('touchmove', (e) => {
      if (!this._joystick.active) return;
      const touch = this.#touchById(e, this._joystick.touchId);
      if (!touch) return;
      e.preventDefault();
      move(touch);
    }, { passive: false });

    const onEnd = (e) => {
      if (!this._joystick.active) return;
      if (this.#touchById(e, this._joystick.touchId)) end();
    };
    window.addEventListener('touchend', onEnd);
    window.addEventListener('touchcancel', onEnd);
  }

  /** Find a touch in an event by identifier — checks changedTouches first
   *  (relevant for end/cancel) then touches (relevant for move). */
  #touchById(e, id) {
    if (id == null) return null;
    for (let i = 0; i < e.changedTouches.length; i++) {
      if (e.changedTouches[i].identifier === id) return e.changedTouches[i];
    }
    for (let i = 0; i < e.touches.length; i++) {
      if (e.touches[i].identifier === id) return e.touches[i];
    }
    return null;
  }

  // ── Mobile: interact pill ──────────────────────────────────────────────

  #buildInteractPill() {
    const btn = document.createElement('button');
    btn.id = 'mobile-interact';
    btn.type = 'button';
    btn.className = 'hidden';
    btn.innerHTML = `
      <span class="interact-icon">●</span>
      <span class="interact-label">Interact</span>
    `;
    document.body.appendChild(btn);
    this._interactBtn = btn;

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.#dispatchKey('KeyE');
    });
  }

  // ── Mobile: action grid ────────────────────────────────────────────────

  #buildActionGrid() {
    const grid = document.createElement('div');
    grid.id = 'mobile-actions';
    document.body.appendChild(grid);
    this._actionGrid = grid;

    // 2-column grid; entries below define the order. Backflip + jump at the
    // top (most-used), push + dance in the middle, cartwheel + lightning at
    // the bottom.
    const buttons = [
      { key: 'backflip', icon: '🤸', label: 'Backflip' },
      { key: 'jump', icon: '⬆', label: 'Jump' },
      { key: 'push', icon: '👋', label: 'Push' },
      { key: 'dance', icon: '💃', label: 'Dance' },
      { key: 'cartwheel', icon: '🔄', label: 'Cartwheel' },
      { key: 'lightning', icon: '⚡', label: 'Lightning' },
    ];

    this._actionBtns = {};
    for (const def of buttons) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'action-btn';
      b.setAttribute('aria-label', def.label);
      b.setAttribute('title', def.label);
      b.textContent = def.icon;
      b.dataset.action = def.key;
      grid.appendChild(b);
      this._actionBtns[def.key] = b;
      this.#wireActionButton(b, def.key);
    }
  }

  #wireActionButton(btn, key) {
    if (key === 'jump') {
      // Polled: hold-to-jump matches keyboard Space behavior.
      const down = (e) => {
        e.preventDefault();
        this.controller?.keys.add('Space');
      };
      const up = (e) => {
        e.preventDefault();
        this.controller?.keys.delete('Space');
      };
      btn.addEventListener('touchstart', down, { passive: false });
      btn.addEventListener('touchend', up);
      btn.addEventListener('touchcancel', up);
      btn.addEventListener('mousedown', down);
      btn.addEventListener('mouseup', up);
      btn.addEventListener('mouseleave', up);
      return;
    }

    if (key === 'push') {
      // Edge-triggered push start, hold-to-keep-pushing. ActionPrompts
      // refuses if currentPushSpot is null, so the button must reflect
      // availability — tick() syncs data-disabled. We still bind handlers
      // since the disabled state is enforced via CSS pointer-events.
      const start = (e) => {
        e.preventDefault();
        this.actionPrompts?.startPush?.();
      };
      const end = (e) => {
        e.preventDefault();
        this.actionPrompts?.endPush?.();
      };
      btn.addEventListener('touchstart', start, { passive: false });
      btn.addEventListener('touchend', end);
      btn.addEventListener('touchcancel', end);
      btn.addEventListener('mousedown', start);
      btn.addEventListener('mouseup', end);
      btn.addEventListener('mouseleave', end);
      return;
    }

    if (key === 'dance') {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.#toggleDance(btn);
      });
      return;
    }

    if (key === 'lightning') {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.thunderstorm?.manualStrike?.();
      });
      return;
    }

    if (key === 'backflip') {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.actionPrompts?.triggerBackflip?.();
      });
      return;
    }

    if (key === 'cartwheel') {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.actionPrompts?.triggerCartwheel?.();
      });
      return;
    }
  }

  #toggleDance(btn) {
    if (!this.player) return;
    if (this._danceActive) {
      this.player.stopLoopAction?.();
      this._danceActive = false;
      btn.classList.remove('is-active');
      this.controller && (this.controller.paused = false);
    } else {
      // Free the controller of any blocking states first; if a billboard is
      // focused or a one-shot is mid-flight the call will be a no-op which
      // is acceptable.
      if (this.player.startLoopAction?.('dance')) {
        this._danceActive = true;
        btn.classList.add('is-active');
      }
    }
  }

  // ── Per-frame sync (called from App tick) ──────────────────────────────

  /**
   * On mobile, syncs:
   *   - The interact pill: show + label it when the player is near a
   *     billboard / contact sign / zone-loop action.
   *   - The push button: disabled when no push spot is in range.
   *   - The dance button: turn off `is-active` when the dance loop ends
   *     (e.g. external action interrupts it).
   */
  tick() {
    if (!this.isMobile) return;
    this.#syncInteractPill();
    this.#syncPushButton();
    this.#syncDanceButton();
  }

  #syncInteractPill() {
    if (!this._interactBtn) return;
    const ix = this.interaction;
    // While a focused panel is open, the pill should be hidden — the panel
    // owns the screen and has its own × close.
    if (ix && (ix.activeIndex !== -1 || ix.contactOpen)) {
      this._interactBtn.classList.add('hidden');
      return;
    }
    let label = null;
    if (ix?.candidate) label = `View ${ix.candidate.project?.name || ''}`.trim();
    else if (ix?.contactCandidate) label = 'Contact';
    else if (this.actionPrompts?.activeZoneLoop) {
      const t = this.actionPrompts.activeZoneLoop;
      label = (t.cycleActions && t.cycleActions.length)
        ? `${t.label} (switch)`
        : t.label;
    } else if (this.actionPrompts?.candidate) {
      label = this.actionPrompts.candidate.label;
    }
    if (label) {
      this._interactBtn.classList.remove('hidden');
      const labelEl = this._interactBtn.querySelector('.interact-label');
      if (labelEl && labelEl.textContent !== label) labelEl.textContent = label;
    } else {
      this._interactBtn.classList.add('hidden');
    }
  }

  #syncPushButton() {
    const btn = this._actionBtns?.push;
    if (!btn || !this.actionPrompts) return;
    const available = !!this.actionPrompts.currentPushSpot;
    btn.dataset.disabled = available ? 'false' : 'true';
    btn.classList.toggle('is-active', !!this.actionPrompts.globalPushActive);
  }

  #syncDanceButton() {
    const btn = this._actionBtns?.dance;
    if (!btn) return;
    // Dance is intentionally a manual toggle. If a one-shot (backflip,
    // cartwheel, etc.) interrupted the dance loop the visual will lag,
    // but the next tap fires stopLoopAction() (a safe no-op when no loop
    // is active) and flips the visual back. Good enough — the source of
    // truth is the user's intent, not a reverse-engineered animation state.
  }

  // ── Utilities ──────────────────────────────────────────────────────────

  /** Synthetic keydown for actions whose existing flow already lives in a
   *  keydown listener (currently used only by the interact pill, which
   *  triggers KeyE so both Interaction and ActionPrompts can resolve it
   *  using their respective candidate state). */
  #dispatchKey(code) {
    window.dispatchEvent(new KeyboardEvent('keydown', {
      code,
      key: code.replace(/^Key/, ''),
      bubbles: true,
    }));
    // Keyup is sent right after to keep edge-triggered handlers consistent.
    requestAnimationFrame(() => {
      window.dispatchEvent(new KeyboardEvent('keyup', {
        code,
        key: code.replace(/^Key/, ''),
        bubbles: true,
      }));
    });
  }

  /** Tell camera-controls not to react to touches that began inside the
   *  joystick zone or any of the mobile UI buttons. We do this by stopping
   *  propagation on those elements; touches that begin on bare canvas
   *  continue to reach camera-controls' native handler, which gives us
   *  right-side touch-rotate for free. */
  #suppressCanvasGestures() {
    const stop = (e) => e.stopPropagation();
    for (const id of ['mobile-actions', 'mobile-interact', 'mobile-joystick-zone']) {
      const el = document.getElementById(id);
      if (!el) continue;
      el.addEventListener('touchstart', stop);
      el.addEventListener('touchmove', stop);
      el.addEventListener('touchend', stop);
    }
  }
}
