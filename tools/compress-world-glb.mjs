#!/usr/bin/env node
/**
 * Draco-compress the VISUAL world GLBs in place (Bruno-style load-time win).
 *
 * Driven by static/world/manifest.json so it stays in sync with the export
 * pipeline. Compresses every monolithic system GLB + every instanced *visual*
 * GLB, and deliberately SKIPS:
 *   - terrain.glb (heightfield:true) — its vertex Y is baked into the physics
 *     heightfield + spawn-Y grounding; lossy position quantization would shift
 *     the ground a few mm–cm and sink/float the player.
 *   - colliders.glb — its bboxes/trimeshes become Rapier collider shapes; a
 *     shifted vertex = a mis-sized invisible wall.
 *   - references / *References GLBs — empties only (no mesh geometry), so Draco
 *     is a no-op; their node transforms (exact placements) are untouched anyway.
 *
 * Safe to re-run: a GLB already carrying KHR_draco_mesh_compression is skipped,
 * so re-exporting from Blender (uncompressed) then running this re-compresses,
 * and a second run is a no-op. Default quantization (position 14-bit ≈ 0.76 cm
 * over the 125 m terrain) keeps the silhouettes intact.
 *
 *   node tools/compress-world-glb.mjs        # or: npm run compress:world
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, renameSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const WORLD = join(ROOT, 'static', 'world');
const CLI = join(ROOT, 'node_modules', '.bin', 'gltf-transform');

const manifest = JSON.parse(readFileSync(join(WORLD, 'manifest.json'), 'utf8'));

// Visual GLBs only: every monolithic system except the heightfield terrain,
// plus each instanced system's visual mesh. (colliders/references are addressed
// via separate manifest keys and are never in these lists.)
const targets = [
  ...(manifest.monolithic ?? []).filter((e) => !e.heightfield).map((e) => e.file),
  ...(manifest.instanced ?? []).map((e) => e.visual).filter(Boolean),
];

/** True if the GLB's JSON chunk already declares Draco compression. */
function isAlreadyDraco(absPath) {
  const buf = readFileSync(absPath);
  // glTF binary: 12-byte header, then the first chunk is JSON.
  const jsonLen = buf.readUInt32LE(12);
  const json = JSON.parse(buf.slice(20, 20 + jsonLen).toString('utf8'));
  return (json.extensionsUsed ?? []).includes('KHR_draco_mesh_compression');
}

const kb = (n) => `${(n / 1024).toFixed(1)} KB`;
let before = 0;
let after = 0;
let skipped = 0;

for (const rel of targets) {
  const abs = join(WORLD, rel);
  const startBytes = statSync(abs).size;
  before += startBytes;

  if (isAlreadyDraco(abs)) {
    after += startBytes;
    skipped++;
    console.log(`skip  ${rel}  (already Draco, ${kb(startBytes)})`);
    continue;
  }

  // Encode to a sibling temp, then atomically replace — gltf-transform will not
  // read and write the same path safely. The temp MUST end in `.glb` so the CLI
  // writes a self-contained binary GLB (embedded buffer + textures); any other
  // extension makes it externalise the geometry to a `.bin` + textures to PNG.
  const tmp = `${abs.slice(0, -'.glb'.length)}.tmp.glb`;
  execFileSync(CLI, ['draco', abs, tmp], { stdio: ['ignore', 'ignore', 'inherit'] });
  renameSync(tmp, abs);

  const endBytes = statSync(abs).size;
  after += endBytes;
  const pct = (100 * (1 - endBytes / startBytes)).toFixed(0);
  console.log(`draco ${rel}  ${kb(startBytes)} → ${kb(endBytes)}  (-${pct}%)`);
}

const pct = before ? (100 * (1 - after / before)).toFixed(1) : '0';
console.log(
  `\n${targets.length} visual GLBs (${skipped} already compressed)\n`
  + `total ${kb(before)} → ${kb(after)}  (-${pct}%)`,
);
