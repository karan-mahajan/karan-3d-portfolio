import {
  uniform, float, vec3, vec4, mix, smoothstep, clamp,
  positionWorld, positionLocal, normalWorld, normalLocal, mx_noise_float,
} from "three/tsl";

/**
 * Shared snow weather state. Two global uniform nodes are referenced by every
 * snow-aware material (shared world props, terrain, grass, foliage canopies)
 * and by the falling-snow effect, so one writer — WeatherDirector — drives the
 * whole world from a single value.
 *
 *   snowCoverage — 0..1, how far the storm has progressed.
 *   snowFall     — 0..1, intensity of the falling flakes.
 *
 * Accumulation is PROGRESSIVE and PATCHY, not a uniform global fade: a
 * large-scale world-noise "patch field" assigns each spot a threshold, and a
 * spot only whitens once snowCoverage climbs past its threshold. So as a storm
 * ramps up, snow creeps in patch by patch — like real settling — instead of the
 * entire ground flashing white at once. A per-surface `bias` shifts when a
 * surface starts collecting (grass early, paths/slabs late). The shape-hugging
 * look comes from a normal-based facing term: only upward fragments collect, so
 * snow follows the real silhouette of a rock, canopy, statue, ball.
 */

export const snowCoverage = uniform(0);
export const snowFall = uniform(0);

// Two cold whites — snow albedo varies by noise so the blanket reads as shaded
// drifts, not a flat paint fill. Slightly blue so the world's warm sunset light
// brings it to neutral white instead of cream/brown.
export const SNOW_ALBEDO = vec3(0.9, 0.95, 1.0);
const SNOW_DIM = vec3(0.7, 0.78, 0.9);

/**
 * Large-scale patch field in 0..1 over world XZ. Two octaves so patch edges are
 * organic rather than perfect blobs. Sampled by XZ only so ground, grass and
 * props in the same area cross the snow threshold together.
 */
function patchField(xz) {
  const a = mx_noise_float(xz.mul(0.045)).mul(0.5).add(0.5);
  const b = mx_noise_float(xz.mul(0.13)).mul(0.5).add(0.5);
  return clamp(a.mul(0.65).add(b.mul(0.35)), 0, 1);
}

/**
 * Progressive coverage at a world-XZ position: 0 until snowCoverage (+bias)
 * climbs past this spot's patch threshold, then ramps to 1 with a soft edge.
 * @param {*} xz vec2 world XZ node
 * @param {number} [bias] surface preference (+ = collects earlier)
 * @param {number} [edge] softness of the growing snow line
 */
export function snowGrowAt(xz, bias = 0, edge = 0.16) {
  const patch = patchField(xz);
  const cov = clamp(snowCoverage.add(bias), 0, 1);
  return smoothstep(patch.sub(edge), patch.add(edge * 0.5), cov);
}

/**
 * Normal-based, progressive accumulation mask for a lit surface. Upward faces
 * collect; the patch field gates WHEN they whiten.
 * @param {object} [o]
 * @param {number} [o.low]   normal.y where snow starts
 * @param {number} [o.high]  normal.y for full snow (near-flat tops)
 * @param {number} [o.bias]  surface preference (+ earlier, - later)
 * @param {number} [o.scale] extra multiplier
 */
export function snowMask({ low = 0.1, high = 0.5, bias = 0, scale = 1 } = {}) {
  const facing = smoothstep(low, high, normalWorld.y);
  const grow = snowGrowAt(positionWorld.xz, bias);
  return clamp(facing.mul(grow).mul(scale), 0, 1);
}

/** Noise-varied snow albedo so the white isn't flat. */
function snowAlbedo() {
  const n = mx_noise_float(positionWorld.mul(0.7)).mul(0.5).add(0.5);
  return mix(SNOW_DIM, SNOW_ALBEDO, n);
}

/** Blend a base rgb node toward (shaded) snow by `mask`. */
export function snowColor(baseRgb, mask) {
  return mix(baseRgb, snowAlbedo(), mask);
}

/** Preserve a vec4 colour's alpha while snowing the rgb (shared-material path). */
export function snowColor4(baseRgba, mask) {
  return vec4(mix(baseRgba.xyz, snowAlbedo(), mask), baseRgba.w);
}

/** Snow reads matte — push roughness up where it accumulates. */
export function snowRoughness(baseRough, mask) {
  return mix(baseRough, float(0.92), mask);
}

/**
 * Sparse bright glints + a faint cool self-lift. The world is lit by a warm
 * sunset sun + #ffb084 fog, which drags plain white snow toward cream/brown;
 * this cool emissive contribution keeps snow reading as cold, sparkling snow.
 * Returned as an emissive vec3 to ADD onto a material's emissive output,
 * gated by the snow mask.
 */
function snowSparkle() {
  // High-frequency noise raised to a high power → small, sparse bright specks.
  const glintField = mx_noise_float(positionWorld.mul(11.0)).mul(0.5).add(0.5);
  const glint = glintField.pow(26).mul(1.4);
  const coolLift = vec3(0.05, 0.07, 0.11); // faint cold ambient so snow stays white
  return coolLift.add(glint);
}

/** Emissive snow contribution (sparkle + cool lift) gated by the snow mask. */
export function snowEmissive(mask) {
  return snowSparkle().mul(mask);
}

/**
 * Vertical drift offset for the (single-mesh) terrain — gives the snow blanket
 * real depth + gentle dunes instead of a flat repaint. Tied to the same patch
 * field so the surface only rises where snow has actually settled. Returns a
 * vec3 to add to positionLocal.
 */
export function terrainSnowDrift(maxMeters = 0.12) {
  const slope = clamp(normalLocal.y.sub(0.3).mul(2.5), 0, 1);
  const grow = snowGrowAt(positionLocal.xz, 0.1);
  const n = mx_noise_float(positionLocal.xz.mul(0.35)).mul(0.5).add(0.5);
  return vec3(0, slope.mul(grow).mul(n).mul(maxMeters), 0);
}
