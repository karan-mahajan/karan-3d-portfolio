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
  // Break the snow line so accumulation is LUMPY, not flat paint — but the
  // AMOUNT of break-up varies across the world via a large-scale zone noise, so
  // some areas are nearly solid snow and others are patchy/bare. Uniform-
  // amplitude noise reads as a tiled texture; this varying amplitude reads as
  // real, place-by-place accumulation.
  const zone = mx_noise_float(positionWorld.mul(0.07)).mul(0.5).add(0.5);
  const lumps = mx_noise_float(positionWorld.mul(1.7)).mul(0.5).add(0.5);
  const lo = mix(float(0.85), float(0.4), zone); // smooth zones barely break; rough zones break hard
  const broken = clamp(grow.mul(mix(lo, float(1.25), lumps)), 0, 1);
  return clamp(facing.mul(broken).mul(scale), 0, 1);
}

/**
 * Geometric snow shell — pushes upward-facing vertices OUT along their own
 * normal so settled snow has real THICKNESS (puffy caps that round over edges),
 * not just a colour swap. Lumpy depth so the layer is uneven, and exactly zero
 * when there's no snow. Add the returned vec3 to a material's positionNode.
 *
 * WARNING: only safe on a mesh with correct, independent vertex normals (e.g.
 * the single terrain mesh). Do NOT use on the consolidated shared world
 * material — displacing that merged/instanced geometry breaks its shading
 * normals and renders every prop unlit/black. Prop thickness needs a dedicated
 * snow-cap mesh or a normal-recompute pass instead.
 * @param {number} [maxMeters] peak snow depth on a flat-up face
 */
export function snowShell(maxMeters = 0.09) {
  const mask = snowMask({ low: 0.05, high: 0.55 });
  const lumps = mx_noise_float(positionWorld.mul(2.3)).mul(0.5).add(0.5);
  const depth = mask.mul(mix(float(0.45), float(1.0), lumps)).mul(maxMeters);
  return normalLocal.mul(depth);
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
export function terrainSnowDrift(maxMeters = 0.2) {
  const slope = clamp(normalLocal.y.sub(0.3).mul(2.5), 0, 1);
  const grow = snowGrowAt(positionLocal.xz, 0.1);
  // Base shape = large smooth drifts (low frequency) — most of the snow is a
  // gentle rolling surface, not a cellular bump field.
  const dunes = mx_noise_float(positionLocal.xz.mul(0.13)).mul(0.5).add(0.5);
  // Bumpiness is GATED by a very-large-scale zone: some regions are smooth,
  // others get fine lumps. This is what kills the "same pattern everywhere"
  // tiled look — roughness itself varies place to place.
  const zone = mx_noise_float(positionLocal.xz.mul(0.06)).mul(0.5).add(0.5);
  const lumps = mx_noise_float(positionLocal.xz.mul(0.8)).mul(0.5).add(0.5);
  const height = clamp(dunes.mul(0.7).add(lumps.mul(zone).mul(0.3)), 0, 1);
  return vec3(0, slope.mul(grow).mul(height).mul(maxMeters), 0);
}
