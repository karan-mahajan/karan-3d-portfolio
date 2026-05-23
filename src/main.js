import { App } from './App.js';

const loadingScreen = document.getElementById('loading-screen');
const loadingBar = document.getElementById('loading-bar-fill');
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

function setProgress(ratio) {
  if (loadingBar) loadingBar.style.width = `${Math.min(100, ratio * 100)}%`;
}

async function bootstrap() {
  const app = new App();
  window.__app = app;

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

  setProgress(1);

  // Pause input while the welcome screen is up so the player can't drift
  // around behind the overlay.
  if (app.player?.controller) app.player.controller.paused = true;

  const welcomeScreen = document.getElementById('welcome-screen');
  const startBtn = document.getElementById('welcome-start');
  const controlsHud = document.getElementById('controls-hud');

  // Once the user has clicked Start (or pressed any movement key) we set
  // this session flag so subsequent reloads in the same tab skip the welcome
  // overlay entirely. Clearing the tab or closing the session resets it.
  const STARTED_KEY = 'karan-portfolio:journey-started';
  const alreadyStarted = sessionStorage.getItem(STARTED_KEY) === '1';

  const START_KEYS = new Set([
    'KeyW', 'KeyA', 'KeyS', 'KeyD',
    'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
    'Space', 'Enter',
  ]);
  let started = false;
  const onStart = () => {
    if (started) return;
    started = true;
    sessionStorage.setItem(STARTED_KEY, '1');
    welcomeScreen?.classList.add('hidden');
    controlsHud?.classList.remove('hidden');
    if (app.player?.controller) app.player.controller.paused = false;
    app.audio?.start();
    window.removeEventListener('keydown', onKeyStart);
  };
  const onKeyStart = (e) => {
    if (START_KEYS.has(e.code)) onStart();
  };

  if (alreadyStarted) {
    // Fast path: no welcome overlay, just hide loading + reveal controls HUD.
    setTimeout(() => {
      loadingScreen?.classList.add('hidden');
      controlsHud?.classList.remove('hidden');
      if (app.player?.controller) app.player.controller.paused = false;
      started = true;
      // Need a user gesture to autoplay; first click anywhere triggers ambient.
      const oneShotAudioStart = () => {
        app.audio?.start();
        window.removeEventListener('click', oneShotAudioStart);
        window.removeEventListener('keydown', oneShotAudioStart);
      };
      window.addEventListener('click', oneShotAudioStart, { once: true });
      window.addEventListener('keydown', oneShotAudioStart, { once: true });
    }, 280);
  } else {
    // First-time-in-this-session path: show the welcome overlay.
    setTimeout(() => {
      loadingScreen?.classList.add('hidden');
      welcomeScreen?.classList.remove('hidden');
    }, 480);
    startBtn?.addEventListener('click', onStart, { once: true });
    window.addEventListener('keydown', onKeyStart);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}
