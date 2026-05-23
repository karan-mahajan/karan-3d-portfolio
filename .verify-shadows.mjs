import { chromium } from 'playwright';
import { mkdirSync } from 'fs';

const URL = process.env.URL || 'http://localhost:5174/';
const OUTDIR = '.verify-shots';
mkdirSync(OUTDIR, { recursive: true });

const errors = [];
const warnings = [];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const page = await ctx.newPage();
page.on('console', (msg) => {
  const t = msg.type();
  const text = msg.text();
  if (t === 'error') errors.push(text);
  else if (t === 'warning') warnings.push(text);
});
page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));

await page.goto(URL, { waitUntil: 'networkidle' });

// Wait for welcome screen and click the start button.
await page.waitForSelector('#welcome-start:not(.hidden), #welcome-start', { timeout: 15000 });
await page.waitForTimeout(800);
await page.click('#welcome-start');
await page.waitForTimeout(3500);

// Walk forward (north toward Experience), strafe east to find tree shadows
await page.keyboard.down('w');
await page.waitForTimeout(1500);
await page.keyboard.up('w');
await page.waitForTimeout(1000);

await page.screenshot({ path: `${OUTDIR}/shadow-tint-default.png`, fullPage: false });

// Strafe east toward dense tree ring
await page.keyboard.down('d');
await page.waitForTimeout(2000);
await page.keyboard.up('d');
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUTDIR}/shadow-tint-east.png`, fullPage: false });

// Tip camera down so shadows under trees fill more of the frame
await page.mouse.move(640, 360);
await page.mouse.down();
await page.mouse.move(640, 600, { steps: 12 });
await page.mouse.up();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUTDIR}/shadow-tint-down.png`, fullPage: false });

// Walk far enough into the tree ring to frame a trunk with sun on one side
// and shadow on the other (looking for any pink stripe on trunk).
await page.keyboard.down('w');
await page.waitForTimeout(2500);
await page.keyboard.up('w');
await page.waitForTimeout(800);
await page.mouse.move(640, 360);
await page.mouse.down();
await page.mouse.move(640, 240, { steps: 10 }); // tilt up to eye level
await page.mouse.up();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUTDIR}/shadow-tint-trunk.png`, fullPage: false });

// Pan to find a trunk centered in frame
await page.mouse.move(640, 360);
await page.mouse.down();
await page.mouse.move(900, 360, { steps: 15 });
await page.mouse.up();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUTDIR}/shadow-tint-trunk-pan.png`, fullPage: false });

await browser.close();

console.log(JSON.stringify({
  errors,
  warnings: warnings.filter((w) => !/DevTools/i.test(w)),
  screenshots: [`${OUTDIR}/shadow-tint-default.png`, `${OUTDIR}/shadow-tint-rotated.png`],
}, null, 2));
