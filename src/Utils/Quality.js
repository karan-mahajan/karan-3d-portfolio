const PROFILES = {
  high: {
    name: 'high',
    physicsStep: 1 / 60,
    maxPhysicsSteps: 5,
    grassMultiplier: 1,
    // Full water shader: refraction, caustics, whitecaps, shoreline foam,
    // noise-broken normal. Dropped to false on medium/low (see Water.js).
    waterHighDetail: true,
    // Leaf cards per canopy/bush blob (the double-sided alpha-tested SDF
    // shell). Pure fill-rate, so weaker tiers get FEWER cards — never zero:
    // a bald core blob reads as a broken tree on every machine.
    foliageShellCards: 150,
    // Two-bone foot IK that plants the feet on the terrain. Cheap (one solve
    // per leg) but skipped on the low tier to spare weak CPUs the per-frame
    // matrix refreshes.
    footIK: true,
    rainCount: 1200,
    rainSplashBudget: 8,
    leafCount: 120,
    maxSettledLeaves: 80,
    windLineCount: 350,
    fireflyCount: 144,
    // Adaptive DPR floor: under sustained frame budget pressure, the
    // adaptive controller in App.js may scale the renderer's pixelRatio
    // down to (base * dprFloor) to recover frametime. On a healthy GPU
    // this never engages; on a weak one it prevents stutter.
    dprFloor: 0.85,
    // Render-resolution ceiling (Sizes caps devicePixelRatio to this). 2.0 =
    // full Retina sharpness on capable machines, matching Bruno. The adaptive
    // DPR controller scales BELOW this (down to dprFloor×) under load.
    dprCap: 2.0,
    // Boot-reveal shader-warm budget. `frames` = how many live frames to let
    // render behind the loader (compiles the scene/post-FX pass); `capMs` =
    // hard ceiling on the whole hold. Strong tier holds longest for a fully
    // hitch-free reveal. See App.boot().
    prewarm: { frames: 5, capMs: 4000 },
    postfx: {
      enabled: true,
      bloomStrength: 0.30,
      bloomRadius: 0.55,
      bloomThreshold: 0.92,
      tiltShiftAmount: 1.0,
    },
  },
  medium: {
    name: 'medium',
    physicsStep: 1 / 60,
    maxPhysicsSteps: 4,
    grassMultiplier: 0.7,
    waterHighDetail: false,
    foliageShellCards: 90,
    footIK: true,
    rainCount: 700,
    rainSplashBudget: 5,
    leafCount: 75,
    maxSettledLeaves: 50,
    windLineCount: 210,
    fireflyCount: 96,
    dprFloor: 0.7,
    dprCap: 1.5, // sharper than 1.0, lighter than full Retina (2.25× px vs 4×)
    prewarm: { frames: 5, capMs: 3000 },
    postfx: {
      enabled: true,
      bloomStrength: 0.18,
      bloomRadius: 0.45,
      bloomThreshold: 0.94,
      tiltShiftAmount: 0.45,
    },
  },
  low: {
    name: 'low',
    physicsStep: 1 / 60,
    maxPhysicsSteps: 3,
    grassMultiplier: 0.5,
    waterHighDetail: false,
    foliageShellCards: 54,
    footIK: false,
    rainCount: 360,
    rainSplashBudget: 2,
    leafCount: 36,
    maxSettledLeaves: 24,
    windLineCount: 90,
    fireflyCount: 48,
    dprFloor: 0.55,
    dprCap: 1.0, // weak machines stay at 1.0 — resolution is the cheapest lever
    prewarm: { frames: 3, capMs: 2000 },
    postfx: {
      enabled: false,
      bloomStrength: 0,
      bloomRadius: 0,
      bloomThreshold: 1,
      tiltShiftAmount: 0,
    },
  },
};

function isMobileLike() {
  const touch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  return touch && window.innerWidth < 768;
}

function autoTier() {
  const memory = navigator.deviceMemory ?? null;
  const cores = navigator.hardwareConcurrency ?? null;
  if (isMobileLike() || (memory !== null && memory <= 4) || (cores !== null && cores <= 4)) {
    return 'low';
  }
  if (!isMobileLike() && memory !== null && cores !== null && memory >= 8 && cores >= 8) {
    return 'high';
  }
  return 'medium';
}

const QUALITY_STORAGE_KEY = 'karan-portfolio:quality';
const TIER_RANK = { low: 0, medium: 1, high: 2 };
const TIERS = ['low', 'medium', 'high'];

function lowerOf(a, b) {
  return TIER_RANK[a] <= TIER_RANK[b] ? a : b;
}

/**
 * One-shot WebGL probe: creates a throwaway context, reads the unmasked
 * renderer string, releases the context. Shared by the demote-side cap and
 * the promote-side hint below so only one probe context is ever created.
 */
function probeGpu() {
  let gl = null;
  try {
    const canvas = document.createElement('canvas');
    gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  } catch {
    gl = null;
  }
  if (!gl) return { hasWebgl: false, renderer: '' };

  let renderer = '';
  try {
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    renderer = String(
      (ext && gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) ||
        gl.getParameter(gl.RENDERER) ||
        '',
    ).toLowerCase();
  } catch {
    renderer = '';
  }
  // Release the probe context immediately so it doesn't linger as a live GL
  // context alongside the real WebGPU one.
  try {
    gl.getExtension('WEBGL_lose_context')?.loseContext();
  } catch {
    /* no-op */
  }
  return { hasWebgl: true, renderer };
}

/**
 * Demote-only GPU heuristic. Returns the HIGHEST tier this GPU should be
 * trusted with ('low' | 'medium'), or null when the GPU is unknown or discrete
 * (no cap — defer to the spec tier). We never UPGRADE off this: a capable-spec
 * machine (8+ cores, 8+ GB) sitting on a weak integrated GPU is the exact
 * mis-tier this guards against — the reported Windows-laptop-on-`high` lag was
 * a strong CPU/RAM box with a fill-bound integrated GPU. Detection is kept
 * conservative because a false "integrated" match only costs a slightly
 * lighter scene, never a black screen, so erring toward demotion is safe.
 * (Bruno rejected GPU scoring for *picking* a tier; using it only to *cap* one
 * sidesteps his accuracy concern — the failure mode is benign in this
 * direction.)
 */
function gpuTierCap(probe) {
  if (!probe.hasWebgl) return 'low'; // no WebGL at all → weakest hardware/software path
  const renderer = probe.renderer;
  if (!renderer) return null; // info withheld (Firefox/privacy) → defer to spec

  // Pure-software rasterizers — always the floor.
  if (/swiftshader|llvmpipe|software|microsoft basic|\bwarp\b|softpipe/.test(renderer)) {
    return 'low';
  }
  // Intel integrated graphics.
  if (/intel/.test(renderer)) {
    if (/\barc\b/.test(renderer)) return null; // discrete Arc — trust the spec tier
    if (/iris/.test(renderer)) return 'medium'; // Iris / Iris Xe — middling
    if (/uhd|hd graphics|\bgraphics\b/.test(renderer)) return 'low'; // UHD/HD/generic
  }
  // AMD integrated APUs (Vega 3–11, plain "Radeon(TM) Graphics") — note a
  // discrete "Radeon RX 6800" or APU "Radeon 780M Graphics" won't match these
  // contiguous patterns, so strong parts correctly escape the cap.
  if (/vega [0-9]|radeon\(tm\) graphics|radeon graphics/.test(renderer)) {
    return 'low';
  }
  return null; // discrete NVIDIA/AMD, Apple M-series, anything else → no cap
}

/**
 * Promote-side GPU hint, used ONLY when navigator.deviceMemory is unavailable
 * (Safari, Firefox) — those browsers can otherwise never spec into 'high'.
 * Deliberately narrow: desktop Apple Silicon (Chrome/Edge ANGLE says
 * "apple m1/m2/…", Safari masks to "apple gpu") and unmistakable discrete
 * parts. The no-touch gate excludes iPads, which also report "Apple GPU".
 */
function gpuTierHint(probe) {
  const r = probe.renderer;
  if (!r) return null;
  const touch = (navigator.maxTouchPoints ?? 0) > 0 || 'ontouchstart' in window;
  if (!touch && /apple (m\d|gpu)/.test(r)) return 'high';
  if (/geforce rtx|radeon rx [4-9]\d{2}0/.test(r)) return 'high';
  return null;
}

/** Tier the heuristics (spec ∩ GPU cap, + promote hint when memory is unknown)
 *  would pick, ignoring any saved override. */
export function autoQualityTier() {
  const probe = probeGpu();
  const cap = gpuTierCap(probe);
  const spec = autoTier();
  let tier = cap ? lowerOf(spec, cap) : spec;
  // deviceMemory is Chrome/Edge-only — Safari/Firefox on an M-series Mac (or a
  // discrete-GPU desktop) land on 'medium' forever because the 'high' spec
  // branch requires a memory reading. Uplift exactly that case: memory
  // unknown, strong core count, an uncapped GPU we positively recognise.
  if (
    tier === 'medium' &&
    !cap &&
    navigator.deviceMemory == null &&
    (navigator.hardwareConcurrency ?? 0) >= 8 &&
    gpuTierHint(probe) === 'high' &&
    !isMobileLike()
  ) {
    tier = 'high';
  }
  return tier;
}

function readSavedTier() {
  try {
    const s = localStorage.getItem(QUALITY_STORAGE_KEY);
    return TIERS.includes(s) ? s : null;
  } catch {
    return null;
  }
}

export function detectQuality() {
  const params = new URLSearchParams(window.location.search);
  const requested = (params.get('quality') || '').toLowerCase();
  const urlForced = TIERS.includes(requested) ? requested : null;

  // Precedence: ?quality= URL param (dev/repro) > saved user choice > auto.
  const saved = urlForced ? null : readSavedTier();
  const auto = autoQualityTier();
  const tier = urlForced || saved || auto;

  return {
    ...PROFILES[tier],
    requested: urlForced || (saved ? 'saved' : 'auto'),
    forced: !!urlForced,
    auto, // what auto-detection alone would choose (drives the toggle's "Auto" state)
    usingSaved: !urlForced && !!saved,
  };
}

/**
 * Persist the user's manual quality choice (or clear it back to Auto). The
 * post-FX chain, water shader and material bind groups are all baked at
 * construction, and toggling post-FX/toneMapping live black-screens the
 * consolidated materials (see App #applyPerfShed), so the ONLY safe way to
 * apply a new tier is a full reload — detectQuality() reads this on next boot.
 * Caller is responsible for the reload.
 */
export function setQualityPreference(tier) {
  try {
    if (tier === 'auto' || tier == null) {
      localStorage.removeItem(QUALITY_STORAGE_KEY);
    } else if (TIERS.includes(tier)) {
      localStorage.setItem(QUALITY_STORAGE_KEY, tier);
    }
  } catch {
    /* storage blocked (private mode) — choice just won't persist */
  }
}
