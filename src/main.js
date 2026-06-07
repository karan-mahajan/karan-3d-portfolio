import { injectSpeedInsights } from '@vercel/speed-insights';
import { App } from './App.js';

injectSpeedInsights();

const loadingScreen = document.getElementById('loading-screen');
const loadingBar = document.getElementById('loading-bar-fill');
const loadingPercent = document.getElementById('loading-percent');
const loadingStatus = document.getElementById('loading-status');
const loadingHint = document.getElementById('loading-hint');
const loadingRefresh = document.getElementById('loading-refresh');

loadingRefresh?.addEventListener('click', () => window.location.reload());

const statuses = [
  'Growing the forest…',
  'Placing the billboards…',
  'Warming up the lights…',
  'Waking the character…',
  'Almost there…',
];

let statusIndex = 0;
const statusInterval = setInterval(() => {
  statusIndex = (statusIndex + 1) % statuses.length;
  if (loadingStatus) loadingStatus.textContent = statuses[statusIndex];
}, 900);

// ── Smooth "trickle" loading bar ───────────────────────────────────────────
// The honest problem: the dominant boot cost is opaque GPU shader/pipeline
// compilation, which emits NO progress signal — so a byte-accurate bar sits
// frozen (the old "stuck at 5%"). Instead the bar always eases toward an
// asymptotic ceiling over time (it never looks frozen), while real asset
// byte-progress raises a floor underneath it; it only snaps to a true 100% once
// boot() actually resolves. If a single attempt runs long, a "taking longer
// than usual / refresh" hint fades in (the renderer also auto-reloads at 12s).
const loadStart = performance.now();
let assetFloor = 0; // 0..70, from real asset byte-progress
let displayed = 0; // % currently shown
let booted = false;
let hintShown = false;
const HINT_AFTER_MS = 9000;

function tickBar() {
  const elapsedMs = performance.now() - loadStart;
  let target;
  if (booted) {
    target = 100;
  } else {
    // Asymptotic creep toward (but never past) 93%: ~37% @2s, ~63% @5s,
    // ~86% @10s. Real asset progress can push the floor higher than the creep.
    const creep = 93 * (1 - Math.exp(-elapsedMs / 4000));
    target = Math.max(creep, assetFloor);
  }
  displayed += (target - displayed) * (booted ? 0.3 : 0.08);
  if (booted && displayed > 99.5) displayed = 100;
  const pct = Math.min(100, Math.floor(displayed));
  if (loadingBar) loadingBar.style.width = `${pct}%`;
  if (loadingPercent) loadingPercent.textContent = `${pct}%`;

  if (!booted && !hintShown && elapsedMs > HINT_AFTER_MS) {
    hintShown = true;
    loadingHint?.removeAttribute('hidden');
  }

  if (pct >= 100 && booted) return; // finished — stop the rAF loop
  requestAnimationFrame(tickBar);
}
requestAnimationFrame(tickBar);

/** Feed real asset byte-progress (0..1) — raises the bar's floor only. */
function setProgress(ratio) {
  assetFloor = Math.max(assetFloor, Math.min(70, Math.max(0, ratio * 70)));
}

/** Mark boot fully resolved — the trickle then eases to a true 100%. */
function setProgressComplete() {
  booted = true;
  loadingHint?.setAttribute('hidden', '');
}

// ── Calm onboarding ─────────────────────────────────────────────────────────
// A fresh (incognito) visit used to fire the WASD/Look/Zoom coachmark card AND
// the "journey begins" achievement toast the instant the cinematic handed off —
// several popups stacking over the world's very first impression. Instead, hold
// them both back until the visitor ENGAGES (first move / look / scroll / tap) OR
// a short grace window passes — whichever comes first. So an idle newcomer gets
// a calm few seconds to take the world in before any gentle nudge appears, and
// someone who immediately starts exploring triggers it on their own terms (the
// tutorial then shows with the gestures they've already done pre-checked).
const ONBOARDING_GRACE_MS = 7000;

function startOnboardingWhenReady(app) {
  let started = false;
  const ENGAGE_EVENTS = ['keydown', 'pointerdown', 'wheel', 'touchstart'];

  function begin() {
    if (started) return;
    started = true;
    clearTimeout(graceTimer);
    ENGAGE_EVENTS.forEach((t) => window.removeEventListener(t, begin));
    app.achievements?.onJourneyBegin?.();
    app.tutorial?.start();
  }

  const graceTimer = setTimeout(begin, ONBOARDING_GRACE_MS);
  ENGAGE_EVENTS.forEach((t) =>
    window.addEventListener(t, begin, { passive: true }),
  );
}

async function bootstrap() {
  const app = new App();
  window.__app = app;

  // Browsers block audio until a real user gesture (click / key / tap). There's
  // no button anymore, so we arm the unlock from the very first frame: ANY
  // interaction during the (multi-second) loading phase unlocks audio, so by
  // the time the character lands the impact hit can actually be heard. If the
  // visitor never interacts before landing, that first hit is silent — a
  // browser rule no code can bypass. Registered early to maximise the window.
  const startAudioOnce = () => {
    app.audio?.start();
    window.removeEventListener('pointerdown', startAudioOnce);
    window.removeEventListener('keydown', startAudioOnce);
    window.removeEventListener('touchstart', startAudioOnce);
  };
  window.addEventListener('pointerdown', startAudioOnce, { once: true });
  window.addEventListener('keydown', startAudioOnce, { once: true });
  window.addEventListener('touchstart', startAudioOnce, { once: true });

  app.addEventListener('progress', (e) => {
    setProgress(e.detail.ratio);
  });

  let result;
  try {
    result = await app.boot();
  } catch (err) {
    console.error('Boot failed', err);
    if (loadingStatus) loadingStatus.textContent = 'Failed to load — check console';
    return;
  }

  clearInterval(statusInterval);

  if (result?.character && !result.character.ok) {
    if (loadingStatus) {
      loadingStatus.innerHTML =
        'Character mesh missing. Showing placeholder.<br>' +
        '<span style="opacity:0.7;font-size:0.7rem;">' +
        'Re-download any Mixamo FBX with "Skin" enabled.</span>';
    }
  } else if (loadingStatus) {
    loadingStatus.textContent = 'Ready';
  }

  // boot() is fully resolved here (assets + player + shader prewarm) — NOW the
  // world is genuinely ready, so the bar earns its 100%.
  setProgressComplete();
  // NOTE: onJourneyBegin() + the first-visit tutorial are deliberately NOT
  // fired here — they're deferred to startOnboardingWhenReady() below so they
  // don't pop the instant the world reveals (see that helper).

  // Keep input paused until the cinematic hands off (IntroCinematic.play also
  // freezes the player; pausing here covers the brief pre-fall beat too).
  if (app.player?.controller) app.player.controller.paused = true;

  // (Audio unlock was armed at the very top of bootstrap so a click during
  // loading enables the landing-impact sound.)

  // Let the true 100% register for a beat, then drop the loader and fall.
  await new Promise((r) => setTimeout(r, 420));
  loadingScreen?.classList.add('hidden');

  // The cinematic always plays through to the landing — clicks during the fall
  // only unlock audio (armed at the top), they do NOT skip it.
  try {
    await (app.intro?.play?.() ?? Promise.resolve());
  } catch (err) {
    console.warn('Intro cinematic failed; handing off directly.', err);
    if (app.player?.controller) app.player.controller.paused = false;
  }

  // Reveal the HUD (compass + button stacks). The first-visit coachmarks + the
  // "journey begins" toast are held back (see startOnboardingWhenReady) so the
  // reveal isn't buried under popups the moment control hands off.
  document.body.classList.remove('booting');
  startOnboardingWhenReady(app);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
