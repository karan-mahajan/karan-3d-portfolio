// src/UI/LoadingScreen.js
import gsap from 'gsap';
import {
  MILESTONES, MILESTONE_LABELS, MILESTONE_FLOOR, MARKERS,
  TRIVIA, FINAL_TRIVIA, phaseToMilestone,
} from './loadingMilestones.js';

/**
 * Owns everything inside #loading-screen: the asymptotic trickle bar, the
 * milestone state machine (driven by App's `phase` events), trivia rotation,
 * and (Phase 2+) the map-marker illumination.
 *
 * The trickle bar exists because the dominant boot cost — opaque GPU shader
 * compilation — emits no progress signal; a byte-accurate bar would freeze.
 * So the bar eases toward an asymptotic ceiling over time (never frozen) while
 * real asset bytes + milestone floors raise it from underneath, snapping to a
 * true 100% only once boot() resolves (complete()).
 */
export class LoadingScreen {
  #els;
  #loadStart = performance.now();
  #assetFloor = 0;       // 0..70 from asset bytes
  #milestoneFloor = 0;   // 0..100 from milestones
  #displayed = 0;
  #booted = false;
  #hintShown = false;
  #raf = 0;
  #dead = false;         // set by fadeOut() to stop the rAF loop + trivia timer
  #reached = new Set();  // milestone keys already hit
  #triviaIdx = 0;
  #triviaTimer = 0;
  #triviaPaused = false;
  #reduced = typeof matchMedia === 'function'
    && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Show the "taking longer than usual" hint only past a comfortable fast-load
  // window, so it appears on genuinely slow boots (cold shader compile) — not on
  // every visit. Carried over from the previous loader's 9s threshold.
  static #HINT_AFTER_MS = 9000;

  constructor() {
    this.#els = {
      screen: document.getElementById('loading-screen'),
      bar: document.getElementById('loading-bar-fill'),
      percent: document.getElementById('loading-percent'),
      trivia: document.getElementById('loading-trivia'),
      hint: document.getElementById('loading-hint'),
      refresh: document.getElementById('loading-refresh'),
      chips: document.getElementById('loading-milestones'),
      markers: document.getElementById('loading-markers'),
    };
    this.#els.refresh?.addEventListener('click', () => window.location.reload());
    this.#buildChips();
    this.#buildMarkers();
    if (!this.#reduced) this.#animateEntrance();
    this.#startTrivia();
    this.#raf = requestAnimationFrame(this.#tick);
  }

  get element() { return this.#els.screen; }

  /** 0..1 asset byte ratio — raises the bar floor only. */
  setProgress(ratio) {
    const r = Math.min(70, Math.max(0, (ratio || 0) * 70));
    this.#assetFloor = Math.max(this.#assetFloor, r);
  }

  /** A boot `phase` label — advance the milestone state machine. */
  setPhase(label) {
    const key = phaseToMilestone(label);
    if (!key || this.#reached.has(key)) return;
    // Monotonic: mark this and all earlier milestones reached.
    const upto = MILESTONES.indexOf(key);
    for (let i = 0; i <= upto; i++) this.#reach(MILESTONES[i]);
  }

  #reach(key) {
    if (this.#reached.has(key)) return;
    this.#reached.add(key);
    // -2 keeps the bar just shy of each milestone's floor so it never visibly
    // "jumps" to a round number; 'final' lands at 98 and waits for complete()
    // to snap the true 100% (we must never show 100% before boot resolves).
    this.#milestoneFloor = Math.max(this.#milestoneFloor, MILESTONE_FLOOR[key] - 2);
    this.#markChip(key, 'done');
    const next = MILESTONES[MILESTONES.indexOf(key) + 1];
    if (next) this.#markChip(next, 'cur');
    this.#igniteMarkersFor(key);
    if (key === 'final') this.#freezeTriviaFinal();
  }

  /** Boot resolved — snap to true 100%, freeze timelines. */
  complete() {
    this.#booted = true;
    this.#els.hint?.setAttribute('hidden', '');
    // Kill the idle parallax so it doesn't fight the subsequent fade-out tween.
    const map = this.#els.screen?.querySelector('.loading-map');
    if (map) gsap.killTweensOf(map);
    for (const k of MILESTONES) this.#reach(k);
  }

  /**
   * GSAP opacity fade-out; resolves when done. Pointer-events off immediately so
   * the fading overlay doesn't eat the first click (audio-arm / onboarding).
   * Reduced-motion → instant. (Phase 4 also adds a subtle map zoom.)
   */
  fadeOut(durationMs = 700) {
    const el = this.#els.screen;
    // Tear down both loops so nothing runs against the hidden overlay — even on
    // a fadeOut() that skips complete() (the #dead guard stops the rAF; the
    // interval clear stops trivia, which #freezeTriviaFinal only stops on the
    // normal 'final' path).
    this.#dead = true;
    cancelAnimationFrame(this.#raf);
    clearInterval(this.#triviaTimer);
    if (!el) return Promise.resolve();
    el.style.pointerEvents = 'none';
    if (this.#reduced) { el.classList.add('hidden'); return Promise.resolve(); }
    return new Promise((resolve) => {
      const map = el.querySelector('.loading-map');
      const tl = gsap.timeline({
        onComplete: () => { el.classList.add('hidden'); resolve(); },
      });
      // Two tweens at position 0: map zooms in (subtly "steps into" the world)
      // while the full overlay fades — compositor-only, no layout during fade.
      if (map) tl.to(map, { scale: 1.12, duration: durationMs / 1000, ease: 'power2.in' }, 0);
      tl.to(el, { opacity: 0, duration: durationMs / 1000, ease: 'power2.inOut' }, 0);
    });
  }

  // ── internals ──────────────────────────────────────────────────────────
  #buildChips() {
    if (!this.#els.chips) return;
    this.#els.chips.innerHTML = MILESTONES
      .map((k, i) => `<span class="loading-chip${i === 0 ? ' cur' : ''}" data-k="${k}">${MILESTONE_LABELS[k]}</span>`)
      .join('');
  }

  #markChip(key, state) {
    const chip = this.#els.chips?.querySelector(`[data-k="${key}"]`);
    if (!chip) return;
    chip.classList.remove('cur');
    if (state === 'done') chip.classList.add('done');
    if (state === 'cur' && !chip.classList.contains('done')) chip.classList.add('cur');
  }

  #animateEntrance() {
    const map = this.#els.screen?.querySelector('.loading-map');
    if (!map) return;
    // Settle-in: map rises + fades on first paint.
    gsap.from(map, { y: 24, opacity: 0, duration: 0.8, ease: 'power3.out' });
    // Slow idle drift — pure transform, compositor-only, killed by complete().
    gsap.to(map, {
      rotationZ: 1.2, y: '-=6', duration: 6, ease: 'sine.inOut',
      yoyo: true, repeat: -1,
    });
  }

  #buildMarkers() {
    if (!this.#els.markers) return;
    this.#els.markers.innerHTML = MARKERS.map((m) => `
      <span class="loading-marker${m.litAt === null ? ' soon' : ''}" data-id="${m.id}"
            style="left:${m.left}%;top:${m.top}%;--mk:${m.tint}">
        ${m.label ? `<i class="loading-marker-label">${m.label}</i>` : ''}
      </span>`).join('');
  }

  #igniteMarkersFor(key) {
    if (!this.#els.markers) return;
    for (const m of MARKERS) {
      if (m.litAt === key) {
        const el = this.#els.markers.querySelector(`[data-id="${m.id}"]`);
        if (!el || el.classList.contains('lit')) continue;
        el.classList.add('lit');
        if (!this.#reduced) {
          gsap.fromTo(el, { scale: 0.4 }, { scale: 1, duration: 0.5, ease: 'back.out(2)' });
        }
      }
    }
  }

  #startTrivia() {
    if (!this.#els.trivia) return;
    this.#els.trivia.textContent = TRIVIA[0];
    const cycle = () => {
      if (this.#triviaPaused) return;
      this.#triviaIdx = (this.#triviaIdx + 1) % TRIVIA.length;
      this.#crossfadeTrivia(TRIVIA[this.#triviaIdx]);
    };
    this.#triviaTimer = setInterval(cycle, 3500);
  }

  #crossfadeTrivia(text) {
    const el = this.#els.trivia;
    if (!el) return;
    if (this.#reduced) { el.textContent = text; return; }
    gsap.to(el, {
      opacity: 0, duration: 0.4, onComplete: () => {
        el.textContent = text;
        gsap.to(el, { opacity: 1, duration: 0.4 });
      },
    });
  }

  #freezeTriviaFinal() {
    this.#triviaPaused = true;
    clearInterval(this.#triviaTimer);
    this.#crossfadeTrivia(FINAL_TRIVIA);
  }

  #tick = () => {
    if (this.#dead) return; // stopped by fadeOut() — don't re-queue
    const elapsed = performance.now() - this.#loadStart;
    let target;
    if (this.#booted) {
      target = 100;
    } else {
      const creep = 93 * (1 - Math.exp(-elapsed / 4000));
      target = Math.max(creep, this.#assetFloor, this.#milestoneFloor);
    }
    this.#displayed += (target - this.#displayed) * (this.#booted ? 0.3 : 0.08);
    if (this.#booted && this.#displayed > 99.5) this.#displayed = 100;
    const pct = Math.min(100, Math.floor(this.#displayed));
    if (this.#els.bar) this.#els.bar.style.width = `${pct}%`;
    if (this.#els.percent) this.#els.percent.textContent = `${pct}%`;

    if (!this.#booted && !this.#hintShown && elapsed > LoadingScreen.#HINT_AFTER_MS) {
      this.#hintShown = true;
      this.#els.hint?.removeAttribute('hidden');
    }
    if (pct >= 100 && this.#booted) return; // done — stop loop
    this.#raf = requestAnimationFrame(this.#tick);
  };
}
