import { injectSpeedInsights } from '@vercel/speed-insights';
import { App } from './App.js';
import { LoadingScreen } from './UI/LoadingScreen.js';

injectSpeedInsights();

const loadingScreen = new LoadingScreen();

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
    loadingScreen.setProgress(e.detail.ratio);
  });
  app.addEventListener('phase', (e) => {
    loadingScreen.setPhase(e.detail.label);
  });

  let result;
  try {
    result = await app.boot();
  } catch (err) {
    console.error('Boot failed', err);
    return;
  }

  if (result?.character && !result.character.ok) {
    console.warn('Character mesh missing — showing placeholder.');
  }

  // boot() fully resolved — bar earns its true 100% and chips all complete.
  loadingScreen.complete();

  // Keep input paused until the cinematic hands off (IntroCinematic.play also
  // freezes the player; pausing here covers the brief pre-fall beat too).
  if (app.player?.controller) app.player.controller.paused = true;

  // Let the true 100% register for a beat first.
  await new Promise((r) => setTimeout(r, 420));

  // Settle the camera to its resting angle BEHIND the still-opaque loader, THEN
  // fade. intro.play() is an instant land (no descent) that re-seeds the orbit
  // camera (REST distance/azimuth/polar); running it before the fade means the
  // reveal shows the final angle instead of the boot-default orbit snapping into
  // place mid-fade (the visible camera jump).
  try {
    await (app.intro?.play?.() ?? Promise.resolve());
  } catch (err) {
    console.warn('Intro cinematic failed; handing off directly.', err);
    if (app.player?.controller) app.player.controller.paused = false;
  }

  // Now reveal the already-correct world with the GSAP zoom-and-fade.
  await loadingScreen.fadeOut();

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
