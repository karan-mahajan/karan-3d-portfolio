const CANVAS_FACES = [
  '400 16px Fredoka',
  '500 16px Fredoka',
  '600 16px Fredoka',
  '700 16px Fredoka',
  '400 16px Nunito',
  '600 16px Nunito',
  '700 16px Nunito',
  '800 16px Nunito',
  '900 16px Nunito',
];

/**
 * Resolves once the web fonts used by canvas-baked 3D text are usable, so
 * signs never bake in a fallback face. Capped so a slow font host can't
 * hold up boot.
 */
export function canvasFontsReady(timeoutMs = 2500) {
  const link = document.getElementById('font-css');
  const sheet =
    link && !link.sheet
      ? new Promise((resolve) => {
          link.addEventListener('load', resolve, { once: true });
          link.addEventListener('error', resolve, { once: true });
        })
      : Promise.resolve();
  const loaded = sheet
    .then(() => Promise.all(CANVAS_FACES.map((f) => document.fonts.load(f))))
    .catch(() => {});
  return Promise.race([
    loaded,
    new Promise((resolve) => setTimeout(resolve, timeoutMs)),
  ]);
}
