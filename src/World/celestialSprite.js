import * as THREE from 'three/webgpu';

/**
 * Procedural radial sprite for the sun / moon. ONE continuous profile —
 * a near-solid hot core with a SOFT (anti-aliased) edge that blends straight
 * into a long glow skirt — so the body reads as a single glowing orb, not a
 * hard disc with a separate ring around it. RGB warms toward the edge so the
 * skirt picks up a sunset/moonlight tint.
 *
 * Used additively so the core blooms to white-hot (sun) or a pale disc (moon)
 * without a visible silhouette edge.
 *
 * @param {object} opts
 * @param {number} [opts.size=256]        texture resolution
 * @param {number} [opts.coreRadius=0.3]  fraction of the radius that stays solid
 * @param {number} [opts.feather=0.12]    soft-edge width (in radius fraction)
 * @param {number} [opts.glowPow=3.0]     skirt falloff exponent (higher = tighter)
 * @param {number} [opts.glowStrength=0.7] skirt brightness
 * @param {number[]} [opts.coreColor=[1,1,1]]   centre RGB (0..1)
 * @param {number[]} [opts.edgeColor=[1,0.8,0.55]] skirt RGB (0..1)
 * @returns {THREE.CanvasTexture}
 */
export function makeCelestialSprite({
  size = 256,
  coreRadius = 0.3,
  feather = 0.12,
  glowPow = 3.0,
  glowStrength = 0.7,
  coreColor = [1, 1, 1],
  edgeColor = [1, 0.8, 0.55],
} = {}) {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  const half = size / 2;
  const smooth = (e0, e1, x) => {
    const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
    return t * t * (3 - 2 * t);
  };
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (x - half) / half;
      const dy = (y - half) / half;
      const d = Math.min(Math.sqrt(dx * dx + dy * dy), 1);
      // Solid core (alpha ~1) up to coreRadius, soft edge over `feather`, then
      // a smooth glow skirt all the way out — added, not stacked, so there is
      // no hard transition between disc and halo.
      const core = 1 - smooth(coreRadius, coreRadius + feather, d);
      const glow = Math.pow(Math.max(0, 1 - d), glowPow) * glowStrength;
      const a = Math.min(1, core + glow);
      // Warm/tint toward the edge.
      const r = coreColor[0] + (edgeColor[0] - coreColor[0]) * d;
      const g = coreColor[1] + (edgeColor[1] - coreColor[1]) * d;
      const b = coreColor[2] + (edgeColor[2] - coreColor[2]) * d;
      const i = (y * size + x) * 4;
      img.data[i] = Math.round(r * 255);
      img.data[i + 1] = Math.round(g * 255);
      img.data[i + 2] = Math.round(b * 255);
      img.data[i + 3] = Math.round(a * 255);
    }
  }
  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  tex.generateMipmaps = false;
  tex.needsUpdate = true;
  return tex;
}

/** Named moon phases → terminator angle (radians). 0 = full (lit toward
 *  viewer), π = new (invisible). We never use `new` so the moon is always
 *  at least a thin crescent. Positive vs negative angle = waxing vs waning
 *  (lit limb on the right vs left). */
export const MOON_PHASES = {
  full: 0.0,
  waxingGibbous: Math.PI * 0.3,
  firstQuarter: Math.PI * 0.5,
  waxingCrescent: Math.PI * 0.72,
  waningGibbous: -Math.PI * 0.3,
  lastQuarter: -Math.PI * 0.5,
  waningCrescent: -Math.PI * 0.72,
};

// Phases used for the random nightly moon. Exact quarters are omitted on
// purpose — a quarter's terminator is a straight line, which reads as a flat
// "semicircle" rather than a moon; crescents + gibbous + full all have a nicely
// curved terminator (or a full round disc).
const RANDOM_PHASE_KEYS = [
  "full",
  "waxingGibbous",
  "waxingCrescent",
  "waningGibbous",
  "waningCrescent",
];

/** Pick a random (curved) moon phase angle — any night can show any phase. */
export function randomMoonPhaseAngle() {
  // Math.random is unavailable in workflow scripts but fine in the app runtime.
  const k = RANDOM_PHASE_KEYS[Math.floor(Math.random() * RANDOM_PHASE_KEYS.length)];
  return MOON_PHASES[k];
}

/**
 * Procedural moon sprite with a real phase (crescent → quarter → gibbous →
 * full). The disc is shaded as a lit sphere: a terminator sweeps across it per
 * `phaseAngle`, the lit limb glows pale and the dark limb falls to ~0 alpha so,
 * additively over the night sky, you only see the illuminated crescent/half/
 * full shape — exactly like the real moon. A soft edge + faint halo keep it
 * from reading as a hard-cut circle.
 *
 * @param {object} opts
 * @param {number} [opts.phaseAngle=0] terminator angle; 0 = full, ±π/2 = quarter
 * @param {number} [opts.size=256]
 * @param {number} [opts.diskRadius=0.6] disc size as a fraction of the sprite
 * @param {number} [opts.edgeFeather=0.05] soft disc edge width
 * @param {number} [opts.haloStrength=0.22] faint surrounding glow
 * @param {number[]} [opts.litColor=[0.92,0.95,1.0]] illuminated pale colour
 * @returns {THREE.CanvasTexture}
 */
export function makeMoonSprite({
  phaseAngle = 0,
  size = 256,
  diskRadius = 0.6,
  edgeFeather = 0.05,
  haloStrength = 0.22,
  litColor = [0.92, 0.95, 1.0],
} = {}) {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  const half = size / 2;
  const smooth = (e0, e1, x) => {
    const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
    return t * t * (3 - 2 * t);
  };
  // Light direction in sphere space: x = sin(angle) (limb), z = cos(angle)
  // (toward viewer). A small +y tilt keeps the terminator from looking too
  // mechanical.
  const lx = Math.sin(phaseAngle);
  const ly = 0.12;
  const lz = Math.cos(phaseAngle);
  const llen = Math.hypot(lx, ly, lz);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const dx = (x - half) / half;
      const dy = (y - half) / half;
      const d = Math.min(Math.sqrt(dx * dx + dy * dy), 1);
      // Disc coordinates normalised so the sphere fills `diskRadius`.
      const nx = dx / diskRadius;
      const ny = dy / diskRadius;
      const r2 = nx * nx + ny * ny;
      let diskAlpha = 0;
      if (r2 <= 1) {
        const nz = Math.sqrt(1 - r2);
        // Illumination = surface normal · light.
        const illum = (nx * lx + ny * ly + nz * lz) / llen;
        const lit = smooth(-0.04, 0.1, illum); // soft terminator
        const edge = 1 - smooth(diskRadius - edgeFeather, diskRadius, d * 1.0);
        diskAlpha = lit * edge;
      }
      const halo = Math.pow(Math.max(0, 1 - d), 3.2) * haloStrength;
      const a = Math.min(1, diskAlpha + halo * 0.6);
      const i = (y * size + x) * 4;
      img.data[i] = Math.round(litColor[0] * 255);
      img.data[i + 1] = Math.round(litColor[1] * 255);
      img.data[i + 2] = Math.round(litColor[2] * 255);
      img.data[i + 3] = Math.round(a * 255);
    }
  }
  ctx.putImageData(img, 0, 0);
  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  tex.generateMipmaps = false;
  tex.needsUpdate = true;
  return tex;
}
