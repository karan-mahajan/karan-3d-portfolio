/**
 * AchievementToast — slide-in notification card in the top-right.
 *
 * Stacks vertically; up to a few visible at once. Each toast auto-dismisses
 * after 4 seconds via slide-out and then removes its DOM node. Style + dark
 * glass theming live in style.css (`.achievement-toast`); day/night tint
 * is driven by body[data-tod].
 */
const VISIBLE_MS = 4000;
const EXIT_MS = 500;

export class AchievementToast {
  constructor() {
    this.container = document.getElementById('achievement-toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'achievement-toast-container';
      document.body.appendChild(this.container);
    }
  }

  /** Build + animate a single toast for the given achievement record. */
  show(achievement) {
    if (!achievement) return;
    const toast = document.createElement('div');
    toast.className = 'achievement-toast';
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML = `
      <div class="toast-icon">${achievement.icon}</div>
      <div class="toast-content">
        <div class="toast-label">ACHIEVEMENT UNLOCKED</div>
        <div class="toast-name"></div>
        <div class="toast-desc"></div>
        <div class="toast-progress"><div class="toast-progress-bar"></div></div>
      </div>
      <div class="toast-check">✓</div>
    `;
    // Use textContent for name + desc so external data can't inject HTML.
    toast.querySelector('.toast-name').textContent = achievement.name;
    toast.querySelector('.toast-desc').textContent = achievement.description;
    this.container.appendChild(toast);

    // Force a layout flush then add the visible class so the slide-in
    // transition runs (transform/opacity tween from the .toast-visible rule).
    requestAnimationFrame(() => {
      requestAnimationFrame(() => toast.classList.add('toast-visible'));
    });

    setTimeout(() => {
      toast.classList.add('toast-exit');
      setTimeout(() => toast.remove(), EXIT_MS);
    }, VISIBLE_MS);
  }
}
