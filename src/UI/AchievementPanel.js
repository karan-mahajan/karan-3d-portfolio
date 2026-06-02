/**
 * AchievementPanel — full-screen overlay listing every achievement.
 *
 * Opens via the trophy button (built in this module's ctor) or the J key.
 * Closes on the × button, on backdrop click, or on Escape. The list is
 * filterable by category tabs (each showing an x/y badge); within a filter,
 * unlocked items sort to the top, then locked items by closest-to-unlocking
 * so the player can see what to chase next. A summary bar shows total
 * completion %, and a one-shot celebration fires at 100%.
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
    // The 100% celebration fires once, ever — remember across reloads.
    this._celebrated = (() => {
      try { return localStorage.getItem('karan-portfolio:achievements:celebrated') === '1'; }
      catch { return false; }
    })();

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
    btn.setAttribute('title', 'Achievements (J)');
    btn.innerHTML = `
      <span class="trophy-icon">🏆</span>
      <span class="trophy-count" id="trophy-count">0/0</span>
      <span class="trophy-new" id="trophy-new" hidden>NEW</span>
    `;
    document.body.appendChild(btn);
    this._btn = btn;
    this._newBadge = btn.querySelector('#trophy-new');
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
        <div class="achievement-summary">
          <div class="summary-bar"><div class="summary-bar-fill" id="summary-bar-fill"></div></div>
          <div class="summary-pct" id="summary-pct">0%</div>
        </div>
        <div class="achievement-categories">
          <button class="category-tab active" data-category="all">All</button>
          <button class="category-tab" data-category="exploration">Exploration</button>
          <button class="category-tab" data-category="portfolio">Portfolio</button>
          <button class="category-tab" data-category="actions">Actions</button>
          <button class="category-tab" data-category="games">Games</button>
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
    this._summaryFill = panel.querySelector('#summary-bar-fill');
    this._summaryPct = panel.querySelector('#summary-pct');
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
      if (e.code === 'Escape' && this.isOpen()) { this.close(); return; }
      // J toggles the panel — ignore when a modifier is held or focus is in a
      // text field so it never eats real typing.
      if (e.code === 'KeyJ' && !e.repeat && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const el = document.activeElement;
        const typing = el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
        if (!typing) { e.preventDefault(); this.toggle(); }
      }
    });
  }

  // ── Open / close ──────────────────────────────────────────────────────

  isOpen() {
    return this._panel && !this._panel.classList.contains('hidden');
  }

  open() {
    if (!this._panel || this.isOpen()) return;
    // Opening the panel = the user has now seen every pending unlock.
    this.achievements.markAllSeen?.();
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

    // Unlocked first within the active filter; among the locked ones, surface
    // whatever is closest to unlocking so the player can see what to chase.
    const ratio = (x) => (x.target > 0 ? Math.min(1, x.current / x.target) : 0);
    filtered.sort((a, b) => {
      if (a.unlocked !== b.unlocked) return a.unlocked ? -1 : 1;
      if (!a.unlocked) {
        // Secret achievements have no readable progress hint — sink them below
        // the visible "almost there" ones.
        if (a.secret !== b.secret) return a.secret ? 1 : -1;
        return ratio(b) - ratio(a);
      }
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
    const rarity = a.rarity || 'common';
    const item = document.createElement('div');
    item.className = `achievement-item rarity-${rarity} ${a.unlocked ? 'unlocked' : 'locked'}`;
    // A trophy-hall medal: a rarity-ringed medallion crest, a tier tag, the
    // name/desc, and a progress rail — not a flat list row.
    item.innerHTML = `
      <div class="medal">
        <div class="medal-face"><span class="achievement-icon"></span></div>
        ${a.unlocked ? '<div class="achievement-check">✓</div>' : ''}
      </div>
      <div class="rarity-tag"></div>
      <div class="achievement-name"></div>
      <div class="achievement-desc"></div>
      <div class="achievement-progress-row">
        <div class="achievement-bar"><div class="achievement-bar-fill"></div></div>
        <span class="achievement-counter"></span>
      </div>
    `;
    item.querySelector('.achievement-icon').textContent = a.displayIcon;
    item.querySelector('.rarity-tag').textContent = (a.secret && !a.unlocked) ? 'secret' : rarity;
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
    const pct = t > 0 ? Math.round((u / t) * 100) : 0;
    const chip = document.getElementById('trophy-count');
    if (chip) chip.textContent = `${u}/${t}`;
    if (this._counterEl) this._counterEl.textContent = `${u} / ${t}`;
    if (this._summaryFill) this._summaryFill.style.width = `${pct}%`;
    if (this._summaryPct) this._summaryPct.textContent = `${pct}%`;

    this.#updateNewBadge();
    this.#updateCategoryBadges();

    // One-shot 100% celebration.
    if (this.achievements.isAllComplete?.() && !this._celebrated) {
      this._celebrated = true;
      try { localStorage.setItem('karan-portfolio:achievements:celebrated', '1'); } catch { /* non-fatal */ }
      this.#celebrate();
    }

    // Re-render the list if the panel happens to be open during the unlock.
    if (this.isOpen()) this.#renderList();
  }

  /** Show/hide the "NEW" pill on the trophy button + a pulse class when there
   *  are unlocked-but-unseen achievements. */
  #updateNewBadge() {
    if (!this._newBadge) return;
    const unseen = this.achievements.getUnseenCount?.() || 0;
    this._newBadge.hidden = unseen === 0;
    this._btn?.classList.toggle('has-new', unseen > 0);
  }

  /** Stamp each category tab with its x/y completion. */
  #updateCategoryBadges() {
    const stats = this.achievements.getCategoryStats?.() || {};
    const total = { unlocked: this.achievements.getUnlockedCount(), total: this.achievements.getTotalCount() };
    for (const tab of this._tabs) {
      const cat = tab.dataset.category || 'all';
      const s = cat === 'all' ? total : stats[cat];
      let badge = tab.querySelector('.tab-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'tab-badge';
        tab.appendChild(badge);
      }
      badge.textContent = s ? `${s.unlocked}/${s.total}` : '0/0';
      tab.classList.toggle('tab-complete', !!s && s.unlocked >= s.total);
    }
  }

  /** Full-screen confetti + banner when every achievement is unlocked. */
  #celebrate() {
    const el = document.createElement('div');
    el.className = 'achievement-celebration';
    el.setAttribute('role', 'status');
    const colors = ['#ffcf3a', '#b15cff', '#4aa3ff', '#5be37a', '#ff6b9d'];
    let confetti = '';
    for (let i = 0; i < 60; i++) {
      const left = Math.round((i * 137) % 100); // deterministic spread, no RNG
      const delay = (i % 12) * 0.12;
      const dur = 2.4 + (i % 7) * 0.25;
      const c = colors[i % colors.length];
      confetti += `<span class="confetti" style="left:${left}%;background:${c};animation-delay:${delay}s;animation-duration:${dur}s"></span>`;
    }
    el.innerHTML = `
      <div class="celebration-confetti">${confetti}</div>
      <div class="celebration-card">
        <div class="celebration-trophy">🏆</div>
        <div class="celebration-title">100% Complete!</div>
        <div class="celebration-sub">You unlocked every achievement. Legend.</div>
      </div>
    `;
    document.body.appendChild(el);
    this.audio?.playAchievement?.('legendary');
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 600);
    }, 5200);
  }
}
