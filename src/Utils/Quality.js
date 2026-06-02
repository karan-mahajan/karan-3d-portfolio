const PROFILES = {
  high: {
    name: 'high',
    physicsStep: 1 / 60,
    maxPhysicsSteps: 5,
    grassMultiplier: 1,
    // Full water shader: refraction, caustics, whitecaps, shoreline foam,
    // noise-broken normal. Dropped to false on medium/low (see Water.js).
    waterHighDetail: true,
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
    rainCount: 700,
    rainSplashBudget: 5,
    leafCount: 75,
    maxSettledLeaves: 50,
    windLineCount: 210,
    fireflyCount: 96,
    dprFloor: 0.7,
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
    rainCount: 360,
    rainSplashBudget: 2,
    leafCount: 36,
    maxSettledLeaves: 24,
    windLineCount: 90,
    fireflyCount: 48,
    dprFloor: 0.55,
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
