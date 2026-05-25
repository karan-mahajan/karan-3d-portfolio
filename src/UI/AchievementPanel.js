/**
 * AchievementPanel — full-screen overlay listing all 28 achievements.
 *
 * Opens via the trophy button (built in this module's ctor and appended to
 * the bottom-left stack alongside the other UI buttons). Closes on the ×
 * button, on backdrop click, or on Escape. The list is filterable by
 * category tabs; unlocked items sort to the top within whatever filter
 * is active.
 *
 * The whole panel + button DOM is constructed here rather than living in
 * index.html so the achievement system is self-contained and easy to
 * remove if the user ever wants to disable it.
 */
export class AchievementPanel {
  /**
   * @param {object} opts
   * @param {import('../Systems/Achievements.js').Achievements} opts.achievements
   * @param {import('../Audio/AudioManager.js').AudioManager} [opts.audio]
   */
  constructor({ achievements, audio = null }) {
    this.achievements = achievements;
    this.audio = audio;
    this.currentCategory = 'all';

    this.#buildButton();
    this.#buildPanel();
    this.#wireEvents();

    // Subscribe to unlocks so the counter chip on the button stays live.
    this.achievements.onUnlock(() => this.#refreshCounter());
    this.#refreshCounter();
  }

  // ── Trophy button (placed bottom-left, above the existing stack) ─────

  #buildButton() {
    const btn = document.createElement('button');
    btn.id = 'trophy-btn';
    btn.type = 'button';
    btn.className = 'ui-btn trophy-btn';
    btn.setAttribute('aria-label', 'Achievements');
    btn.setAttribute('title', 'Achievements');
    btn.innerHTML = `
      <span class="trophy-icon">🏆</span>
      <span class="trophy-count" id="trophy-count">0/0</span>
    `;
    document.body.appendChild(btn);
    this._btn = btn;
  }

  // ── Panel overlay ─────────────────────────────────────────────────────

  #buildPanel() {
    const panel = document.createElement('div');
    panel.id = 'achievement-panel';
    panel.className = 'achievement-panel hidden';
    // Layout: panel-content itself is the scroll container; the header is
    // pinned with position:sticky so it stays put while categories + list
    // scroll past underneath. The earlier flex-based "header pinned + list
    // scrolls" approach collapsed the scroll wrapper to 0 height because
    // the panel-content sized to content, leaving its flex children no
    // room to grow into.
    panel.innerHTML = `
      <div class="achievement-panel-backdrop"></div>
      <div class="achievement-panel-content" role="dialog" aria-modal="true" aria-labelledby="achievement-panel-title">
        <div class="achievement-panel-header">
          <div class="panel-title" id="achievement-panel-title">
            <span class="panel-trophy">🏆</span>
            <span>Achievements</span>
          </div>
          <div class="panel-counter" id="panel-counter">0 / 0</div>
          <button class="panel-close" id="panel-close" aria-label="Close">✕</button>
        </div>
        <div class="achievement-categories">
          <button class="category-tab active" data-category="all">All</button>
          <button class="category-tab" data-category="exploration">Exploration</button>
          <button class="category-tab" data-category="portfolio">Portfolio</button>
          <button class="category-tab" data-category="actions">Actions</button>
          <button class="category-tab" data-category="world">World</button>
          <button class="category-tab" data-category="time">Time</button>
          <button class="category-tab" data-category="secret">Secret</button>
        </div>
        <div class="achievement-list" id="achievement-list"></div>
      </div>
    `;
    document.body.appendChild(panel);
    this._panel = panel;
    this._listEl = panel.querySelector('#achievement-list');
    this._counterEl = panel.querySelector('#panel-counter');
    this._backdrop = panel.querySelector('.achievement-panel-backdrop');
    this._tabs = Array.from(panel.querySelectorAll('.category-tab'));
  }

  #wireEvents() {
    this._btn.addEventListener('click', () => this.toggle());
    this._panel.querySelector('#panel-close').addEventListener('click', () => this.close());
    this._backdrop.addEventListener('click', () => this.close());
    for (const tab of this._tabs) {
      tab.addEventListener('click', () => {
        for (const t of this._tabs) t.classList.remove('active');
        tab.classList.add('active');
        this.currentCategory = tab.dataset.category || 'all';
        this.#renderList();
      });
    }
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Escape' && this.isOpen()) this.close();
    });
  }

  // ── Open / close ──────────────────────────────────────────────────────

  isOpen() {
    return this._panel && !this._panel.classList.contains('hidden');
  }

  open() {
    if (!this._panel || this.isOpen()) return;
    this.#renderList();
    this.#refreshCounter();
    this._panel.classList.remove('hidden');
    this.audio?.playMenuOpen?.();
  }

  close() {
    if (!this._panel || !this.isOpen()) return;
    this._panel.classList.add('hidden');
    this.audio?.playMenuClose?.();
  }

  toggle() {
    if (this.isOpen()) this.close();
    else this.open();
  }

  // ── Rendering ─────────────────────────────────────────────────────────

  #renderList() {
    if (!this._listEl) return;
    const all = this.achievements.getAll();
    const filtered = this.currentCategory === 'all'
      ? all
      : all.filter((a) => a.category === this.currentCategory);

    // Unlocked first within the active filter, otherwise stable order.
    filtered.sort((a, b) => {
      if (a.unlocked && !b.unlocked) return -1;
      if (!a.unlocked && b.unlocked) return 1;
      return 0;
    });

    const frag = document.createDocumentFragment();
    for (const a of filtered) frag.appendChild(this.#itemNode(a));
    this._listEl.replaceChildren(frag);
  }

  /** Build one .achievement-item row. Uses textContent on the user-visible
   *  strings so achievement names + descriptions can never break the panel
   *  layout with stray HTML in the future. */
  #itemNode(a) {
    const percent = Math.min(100, (a.current / a.target) * 100);
    const item = document.createElement('div');
    item.className = `achievement-item ${a.unlocked ? 'unlocked' : 'locked'}`;
    item.innerHTML = `
      <div class="achievement-icon"></div>
      <div class="achievement-info">
        <div class="achievement-name"></div>
        <div class="achievement-desc"></div>
        <div class="achievement-progress-row">
          <div class="achievement-bar"><div class="achievement-bar-fill"></div></div>
          <span class="achievement-counter"></span>
        </div>
      </div>
      ${a.unlocked ? '<div class="achievement-check">✓</div>' : ''}
    `;
    item.querySelector('.achievement-icon').textContent = a.displayIcon;
    item.querySelector('.achievement-name').textContent = a.displayName;
    item.querySelector('.achievement-desc').textContent = a.displayDescription;
    item.querySelector('.achievement-bar-fill').style.width = `${percent}%`;
    item.querySelector('.achievement-counter').textContent = this.#formatCounter(a);
    return item;
  }

  /** Time-category achievements show "Xm Ys / Tm" so a 300-second target
   *  reads as "5m" instead of "300 / 300". Everything else stays numeric. */
  #formatCounter(a) {
    if (a.category === 'time') {
      const cur = Math.min(a.current, a.target);
      const fmt = (s) => {
        s = Math.max(0, Math.floor(s));
        const m = Math.floor(s / 60);
        const r = s % 60;
        return r === 0 ? `${m}m` : `${m}m ${r}s`;
      };
      return `${fmt(cur)} / ${fmt(a.target)}`;
    }
    return `${Math.min(a.current, a.target)} / ${a.target}`;
  }

  #refreshCounter() {
    const u = this.achievements.getUnlockedCount();
    const t = this.achievements.getTotalCount();
    const chip = document.getElementById('trophy-count');
    if (chip) chip.textContent = `${u}/${t}`;
    if (this._counterEl) this._counterEl.textContent = `${u} / ${t}`;
    // Re-render the list if the panel happens to be open during the unlock.
    if (this.isOpen()) this.#renderList();
  }
}
