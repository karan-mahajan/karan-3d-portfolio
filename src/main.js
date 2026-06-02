import { injectSpeedInsights } from '@vercel/speed-insights';
import { App } from './App.js';

injectSpeedInsights();

const loadingScreen = document.getElementById('loading-screen');
const loadingBar = document.getElementById('loading-bar-fill');
const loadingPercent = document.getElementById('loading-percent');
const loadingStatus = document.getElementById('loading-status');

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

let lastPct = 0;
// Asset byte-progress only covers GLB/texture streaming — but boot() keeps
// working after that (player + foliage loads, then a multi-second shader
// prewarm/compile). So map asset ratio to 0–90% and reserve the last 10% for
// "boot fully resolved", set explicitly in bootstrap(). This fixes the bar
// sitting at 100% while the world is still compiling.
function setProgress(ratio) {
  const raw = Math.min(90, Math.max(0, Math.round(ratio * 90)));
  // Concurrent loaders fire progress events out of order — a chunky GLB can
  // resolve before smaller earlier ones, so the raw ratio occasionally dips
  // (e.g. 70 → 50 → 70). Clamp upward-only so the number is monotonic.
  const pct = Math.max(lastPct, raw);
  lastPct = pct;
  if (loadingBar) loadingBar.style.width = `${pct}%`;
  if (loadingPercent) loadingPercent.textContent = `${pct}%`;
}

/** Snap the bar to a true 100% — only called once boot() has fully resolved. */
function setProgressComplete() {
  lastPct = 100;
  if (loadingBar) loadingBar.style.width = '100%';
  if (loadingPercent) loadingPercent.textContent = '100%';
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

  // Pre-tick a little so the bar shows life even before the first asset fires.
  setProgress(0.05);

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
  app.achievements?.onJourneyBegin?.();

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

  // Reveal the HUD (compass + button stacks) and start first-visit coachmarks.
  document.body.classList.remove('booting');
  app.tutorial?.start();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
