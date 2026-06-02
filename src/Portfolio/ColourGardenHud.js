/**
 * DOM overlay for the Colour Garden game mode: the walk-up prompt, the colour
 * swatch bar (1–6 / click), a charge meter, and the on-screen instructions.
 *
 * Pure DOM — the 3D side (ColourGarden.js) owns state and calls these setters.
 * Styling lives in src/style.css (.cg-* classes).
 */
export class ColourGardenHud {
  constructor() {
    this._onSelect = null;

    // Walk-up prompt (shown when near the garden, not yet playing).
    this.prompt = document.createElement('div');
    this.prompt.className = 'cg-prompt hidden';
    this.prompt.innerHTML = '<span class="cg-key">E</span><span class="cg-prompt-label">Play Colour Garden</span>';

    // Full game overlay.
    this.game = document.createElement('div');
    this.game.className = 'cg-game';

    const title = document.createElement('div');
    title.className = 'cg-title';
    title.textContent = 'Colour Garden';

    const help = document.createElement('div');
    help.className = 'cg-help';
    help.innerHTML =
      'Move mouse to <b>aim</b> · hold <span class="cg-key sm">F</span> to <b>charge</b>, release to <b>throw</b>'
      + ' · <span class="cg-key sm">1</span>–<span class="cg-key sm">6</span> pick colour'
      + ' · <span class="cg-key sm">Esc</span> exit';

    this.charge = document.createElement('div');
    this.charge.className = 'cg-charge';
    this.chargeFill = document.createElement('div');
    this.chargeFill.className = 'cg-charge-fill';
    this.charge.appendChild(this.chargeFill);

    this.swatches = document.createElement('div');
    this.swatches.className = 'cg-swatches';

    this.game.append(title, help, this.charge, this.swatches);
    document.body.append(this.prompt, this.game);

    this._swatchEls = [];
  }

  /** cssColors: array of CSS colour strings (already sRGB) → builds 1..N swatches. */
  setSwatches(cssColors) {
    this.swatches.innerHTML = '';
    this._swatchEls = cssColors.map((css, i) => {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = 'cg-swatch';
      el.style.setProperty('--c', css);
      el.innerHTML = `<span class="cg-swatch-num">${i + 1}</span>`;
      el.addEventListener('click', () => this._onSelect && this._onSelect(i));
      this.swatches.appendChild(el);
      return el;
    });
  }

  onSelect(cb) {
    this._onSelect = cb;
  }

  setActive(index) {
    this._swatchEls.forEach((el, i) => el.classList.toggle('is-active', i === index));
  }

  showPrompt(visible) {
    this.prompt.classList.toggle('hidden', !visible);
  }

  enter() {
    this.showPrompt(false);
    this.game.classList.add('is-active');
  }

  exit() {
    this.game.classList.remove('is-active');
  }

  /** charge 0..1 → fill width. */
  setCharge(t) {
    this.chargeFill.style.width = `${Math.round(Math.max(0, Math.min(1, t)) * 100)}%`;
  }

  dispose() {
    this.prompt.remove();
    this.game.remove();
  }
}
