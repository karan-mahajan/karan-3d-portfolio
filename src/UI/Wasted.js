/**
 * Lava death card — a warm, fiery full-screen flash (red / orange / yellow /
 * tan) that fits the lava, instead of the grey GTA "WASTED" look. A big
 * gradient word with a flame-glow + flicker, a small subtitle, over a warm
 * dark vignette. Pure DOM + injected CSS so it sits above the gameplay HUD
 * without touching the global stylesheet.
 *
 * `show()` resolves once the card has held, so the caller can respawn the
 * player while the screen is still dark, then it lifts to reveal the world.
 */

const STYLE_ID = 'lava-death-style';
const TOTAL_MS = 2600;          // fade-in + hold (resolve) then auto fade-out
const WORD = 'TOASTED';         // lava-flavoured, not "WASTED"
const SUBTITLE = 'respawning…';

const CSS = `
#lava-death {
  position: fixed; inset: 0; z-index: 9000;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  /* Warm ember vignette — dark red core fading to near-black, no grey. */
  background: radial-gradient(ellipse at center,
    rgba(70,14,2,0.28) 0%, rgba(34,7,1,0.68) 55%, rgba(8,2,0,0.93) 100%);
  /* Push the scene behind it warm + dim rather than desaturated. */
  backdrop-filter: brightness(0.55) saturate(1.5) sepia(0.35) hue-rotate(-12deg) contrast(1.08);
  -webkit-backdrop-filter: brightness(0.55) saturate(1.5) sepia(0.35) hue-rotate(-12deg) contrast(1.08);
  transition: opacity 0.45s ease;
}
#lava-death.show { opacity: 1; }

#lava-death .ld-word {
  font-family: 'Arial Black', 'Helvetica Neue', Impact, sans-serif;
  font-weight: 900;
  font-size: clamp(54px, 12vw, 170px);
  letter-spacing: 0.04em;
  line-height: 1;
  /* Hot vertical gradient: pale-yellow core → amber → orange → deep red. */
  background: linear-gradient(180deg, #fff3c4 0%, #ffd24a 26%, #ff7a18 62%, #d61c06 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; color: transparent;
  filter:
    drop-shadow(0 0 18px rgba(255,120,20,0.75))
    drop-shadow(0 0 44px rgba(255,60,0,0.5))
    drop-shadow(0 5px 10px rgba(50,8,0,0.85));
  transform: scale(1.32); opacity: 0;
  transition: transform 0.7s cubic-bezier(0.16,0.84,0.3,1), opacity 0.55s ease;
}
#lava-death.show .ld-word { transform: scale(1); opacity: 1; animation: ld-flicker 2.2s ease-in-out 0.5s infinite; }

#lava-death .ld-sub {
  margin-top: 0.5em;
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-size: clamp(14px, 2.4vw, 24px);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #f3c889;                              /* warm tan */
  text-shadow: 0 2px 10px rgba(0,0,0,0.7), 0 0 14px rgba(255,120,30,0.35);
  opacity: 0;
  transition: opacity 0.6s ease 0.18s;
}
#lava-death.show .ld-sub { opacity: 1; }

@keyframes ld-flicker {
  0%, 100% { filter: drop-shadow(0 0 18px rgba(255,120,20,0.75)) drop-shadow(0 0 44px rgba(255,60,0,0.5)) drop-shadow(0 5px 10px rgba(50,8,0,0.85)); }
  45%      { filter: drop-shadow(0 0 26px rgba(255,160,40,0.9))  drop-shadow(0 0 60px rgba(255,80,0,0.65)) drop-shadow(0 5px 10px rgba(50,8,0,0.85)); }
  70%      { filter: drop-shadow(0 0 14px rgba(255,100,15,0.65)) drop-shadow(0 0 36px rgba(255,50,0,0.45)) drop-shadow(0 5px 10px rgba(50,8,0,0.85)); }
}
`;

export class Wasted {
  constructor() {
    this._injectCss();
    this.el = document.createElement('div');
    this.el.id = 'lava-death';
    const word = document.createElement('div');
    word.className = 'ld-word';
    word.textContent = WORD;
    const sub = document.createElement('div');
    sub.className = 'ld-sub';
    sub.textContent = SUBTITLE;
    this.el.append(word, sub);
    document.body.appendChild(this.el);
    this._playing = false;
  }

  _injectCss() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  /** Play the card. Resolves at the start of the fade-out so the caller can
   *  respawn while the screen is dark; the overlay finishes fading on its own. */
  show() {
    if (this._playing) return Promise.resolve();
    this._playing = true;
    void this.el.offsetWidth;            // force reflow so the transition runs
    this.el.classList.add('show');

    return new Promise((resolve) => {
      window.setTimeout(() => {
        resolve();
        this.el.classList.remove('show');
        window.setTimeout(() => { this._playing = false; }, 500);
      }, TOTAL_MS);
    });
  }

  dispose() {
    this.el?.remove();
    document.getElementById(STYLE_ID)?.remove();
  }
}
