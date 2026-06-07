import { resume } from '../Portfolio/ResumeData.js';

// page-flip (~tens of KB) is dynamically imported in #initFlip, NOT statically
// here: ~99% of visitors never open the resume book, so keeping it out of the
// initial bundle saves them the download + parse — the chunk is fetched the
// first time the book is opened (and the browser caches it for re-opens).
// Matters most on weak / no-GPU laptops where every KB of boot work counts.

/**
 * The two-page open-book resume reading view (DOM overlay), powered by
 * StPageFlip (`page-flip`) for a real turn.js-style page turn: corner
 * hover-peel, drag-to-fold that follows the pointer, fold shadows and
 * click/swipe — plus Prev/Next buttons and ArrowLeft/Right.
 *
 * Content: ResumeData spreads are flattened into single pages (StPageFlip pairs
 * them into facing spreads) and bracketed by leather hard covers, so opening
 * the cover reveals the first spread. The in-world 3D book + camera cinematic
 * live in ResumeBook.js / Interaction; this owns the reading surface only.
 */
export class ResumeBookView {
  /** @param {() => void} onClose — called when the user dismisses the book. */
  constructor({ onClose = () => {}, audio = null } = {}) {
    this.onClose = onClose;
    this.audio = audio;
    this.open = false;
    this.pageFlip = null;
    // Pages are built per-open in #initFlip once the page size is known, so the
    // measured pagination matches the real layout (no covers; showCover:false
    // → the book opens already on the first two-page spread).
    this.pages = [];

    this.#build();
    this.#installKeys();
  }

  // ── DOM ─────────────────────────────────────────────────────────────────────

  #build() {
    this.root = document.createElement('div');
    this.root.className = 'rb-overlay hidden';
    this.root.innerHTML = `
      <div class="rb-book" role="dialog" aria-label="Resume">
        <button class="rb-close" aria-label="Close">×</button>
        <div class="rb-flip-wrap">
          <div class="rb-stack rb-stack-left"></div>
          <div class="rb-flip"></div>
          <div class="rb-stack rb-stack-right"></div>
        </div>
        <nav class="rb-nav">
          <button class="rb-prev" aria-label="Previous page">←</button>
          <span class="rb-counter"></span>
          <button class="rb-next" aria-label="Next page">→</button>
        </nav>
        <p class="rb-hint">drag a corner · ← / → flip · Esc close</p>
      </div>`;
    document.body.appendChild(this.root);

    this.flipEl = this.root.querySelector('.rb-flip');
    this.stackLeft = this.root.querySelector('.rb-stack-left');
    this.stackRight = this.root.querySelector('.rb-stack-right');
    this.counter = this.root.querySelector('.rb-counter');

    this.root.querySelector('.rb-close').addEventListener('click', () => this.#requestClose());
    this.root.querySelector('.rb-prev').addEventListener('click', () => this.pageFlip?.flipPrev());
    this.root.querySelector('.rb-next').addEventListener('click', () => this.pageFlip?.flipNext());
  }

  #installKeys() {
    this._onKey = (e) => {
      if (!this.open) return;
      if (e.code === 'Escape') { e.stopPropagation(); this.#requestClose(); }
      else if (e.code === 'ArrowRight' || e.code === 'ArrowDown') { e.stopPropagation(); this.pageFlip?.flipNext(); }
      else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') { e.stopPropagation(); this.pageFlip?.flipPrev(); }
    };
    // Capture so the book's keys win over the world controls while open.
    window.addEventListener('keydown', this._onKey, true);
  }

  // ── Open / close ──────────────────────────────────────────────────────────

  show() {
    this.open = true;
    this.root.classList.remove('hidden');
    requestAnimationFrame(() => {
      this.root.classList.add('rb-visible');
      this.#initFlip().catch((err) =>
        console.warn('[ResumeBookView] page-flip failed to load:', err),
      );
    });
  }

  async #initFlip() {
    // Fetch page-flip on first open (code-split chunk). The book DOM is already
    // on screen behind the opening cinematic, so the brief one-time fetch is
    // invisible; re-opens resolve instantly from the module cache.
    const { PageFlip } = await import('page-flip/dist/js/page-flip.module.js');

    const h = Math.min(560, Math.round(window.innerHeight * 0.74));
    const w = Math.round(h * 0.7);

    // Build the page list by measuring content against the real page size.
    this.pages = this.#buildPages(w, h);

    // Build page elements fresh each open (StPageFlip consumes them).
    this.flipEl.innerHTML = this.pages
      .map((html) =>
        `<div class="rb-pf-page" data-density="soft">
           <div class="rb-page-inner">${html}</div>
         </div>`)
      .join('');

    this.pageFlip = new PageFlip(this.flipEl, {
      width: w,
      height: h,
      size: 'fixed',
      showCover: false,   // open on a spread, no closed-cover state
      usePortrait: false, // always two pages, never collapse to one
      mobileScrollSupport: false,
      maxShadowOpacity: 0.5,
      drawShadow: true,
      flippingTime: 800,
      showPageCorners: true,
      useMouseEvents: true,
    });
    this.pageFlip.loadFromHTML(this.flipEl.querySelectorAll('.rb-pf-page'));
    this.pageFlip.on('flip', () => { this.audio?.playInteract?.(); this.#syncChrome(); });
    this.#syncChrome();
  }

  /**
   * Build the flat page list. Overview is the first spread (2 pages); every
   * section's blocks are packed onto fixed `w×h` pages by measuring, so each
   * section flows across as many spreads as it needs without clipping. Pads to
   * an even count so the last spread always shows two sides.
   */
  #buildPages(w, h) {
    const pages = [resume.overviewLeft, resume.overviewRight];
    for (const sec of resume.sections) {
      pages.push(...this.#paginate(sec.title, sec.blocks, w, h));
    }
    if (pages.length % 2) pages.push(''); // blank back page keeps spreads paired
    return pages;
  }

  /** Greedily pack `blocks` onto pages sized like a real page, measuring height. */
  #paginate(title, blocks, w, h) {
    const probe = document.createElement('div');
    probe.className = 'rb-page-inner';
    probe.style.cssText =
      `position:absolute; inset:auto; left:-9999px; top:0; width:${w}px; height:${h}px; visibility:hidden;`;
    document.body.appendChild(probe);
    const fits = (html) => { probe.innerHTML = html; return probe.scrollHeight <= probe.clientHeight; };

    const head = (cont) =>
      `<h2 class="rb-h2${cont ? ' rb-h2-cont' : ''}">${title}${cont ? ' <span class="rb-cont">cont.</span>' : ''}</h2>`;

    const pages = [];
    let cur = head(false);
    let hasBlock = false;
    for (const b of blocks) {
      if (hasBlock && !fits(cur + b)) {
        pages.push(cur);
        cur = head(true) + b;
      } else {
        cur += b;
      }
      hasBlock = true;
    }
    pages.push(cur);
    probe.remove();
    return pages;
  }

  /** Counter + side page-stacks that thin/thicken with reading progress. */
  #syncChrome() {
    if (!this.pageFlip) return;
    const total = this.pageFlip.getPageCount();
    const cur = this.pageFlip.getCurrentPageIndex();
    this.counter.textContent = `${cur + 1} / ${total}`;
    const MAX = 16;
    const frac = total > 1 ? cur / (total - 1) : 0;
    this.stackLeft.style.width = `${Math.max(1, frac * MAX)}px`;
    this.stackRight.style.width = `${Math.max(1, (1 - frac) * MAX)}px`;
  }

  /** User asked to close — let the owner reverse the camera, then hide(). */
  #requestClose() {
    if (!this.open) return;
    this.onClose(); // → Interaction.closeResume() → this.hide()
  }

  /** Hide the DOM only (owner-driven; does NOT re-fire onClose). */
  hide() {
    this.open = false;
    this.root.classList.remove('rb-visible');
    const done = () => {
      this.root.classList.add('hidden');
      try { this.pageFlip?.destroy(); } catch { /* already gone */ }
      this.pageFlip = null;
      this.flipEl.innerHTML = '';
      this.root.removeEventListener('transitionend', done);
    };
    this.root.addEventListener('transitionend', done);
  }

  destroy() {
    window.removeEventListener('keydown', this._onKey, true);
    try { this.pageFlip?.destroy(); } catch { /* noop */ }
    this.root?.remove();
  }
}
