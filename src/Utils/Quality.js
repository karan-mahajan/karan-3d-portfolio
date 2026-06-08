const PROFILES = {
  high: {
    name: 'high',
    physicsStep: 1 / 60,
    maxPhysicsSteps: 5,
    grassMultiplier: 1,
    // Full water shader: refraction, caustics, whitecaps, shoreline foam,
    // noise-broken normal. Dropped to false on medium/low (see Water.js).
    waterHighDetail: true,
    // Foliage leaf-card "shell" — a double-sided, alpha-tested SDF overdraw
    // pass on top of every canopy/bush core. Pure fill-rate; dropped on
    // medium/low so weaker GPUs render foliage as just the solid core blob.
    foliageShell: true,
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
    grassMultiplier: 0.62,
    waterHighDetail: false,
    foliageShell: false,
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
    grassMultiplier: 0.35,
    waterHighDetail: false,
    foliageShell: false,
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

export function detectQuality() {
  const params = new URLSearchParams(window.location.search);
  const requested = (params.get('quality') || 'auto').toLowerCase();
  const forced = requested === 'high' || requested === 'medium' || requested === 'low'
    ? requested
    : null;
  const tier = forced || autoTier();
  return {
    ...PROFILES[tier],
    requested: forced || 'auto',
    forced: !!forced,
  };
}
