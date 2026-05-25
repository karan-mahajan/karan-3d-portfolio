import gsap from 'gsap';

export class TransitionFX {
  constructor(root = document.getElementById('transition-root')) {
    this.root = root ?? document.body.appendChild(document.createElement('div'));
    this.root.id = this.root.id || 'transition-root';
    this.root.classList.add('transition-root');
    this.root.innerHTML = '<div class="iris-panel" aria-hidden="true"></div>';
    this.panel = this.root.querySelector('.iris-panel');
    this.root.classList.add('is-idle');
  }

  async play(centerXPct = 50, centerYPct = 50, midActionAsync = null) {
    this.root.classList.remove('is-idle');
    const at = `${centerXPct.toFixed(2)}% ${centerYPct.toFixed(2)}%`;
    gsap.set(this.panel, {
      clipPath: `circle(0% at ${at})`,
      webkitClipPath: `circle(0% at ${at})`,
    });
    await tweenTo(this.panel, {
      clipPath: `circle(150% at ${at})`,
      webkitClipPath: `circle(150% at ${at})`,
      duration: 0.4,
      ease: 'power2.in',
    });
    if (midActionAsync) await midActionAsync();
    await new Promise((resolve) => setTimeout(resolve, 100));
    await tweenTo(this.panel, {
      clipPath: `circle(0% at ${at})`,
      webkitClipPath: `circle(0% at ${at})`,
      duration: 0.5,
      ease: 'power2.out',
    });
    this.root.classList.add('is-idle');
  }
}

function tweenTo(target, vars) {
  return new Promise((resolve) => {
    gsap.to(target, { ...vars, onComplete: resolve });
  });
}
