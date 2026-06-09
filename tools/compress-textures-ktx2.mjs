#!/usr/bin/env node
/**
 * Generate KTX2 siblings for the runtime textures that measured smaller and are
 * actually sampled by Three materials.
 *
 * Requires KTX-Software 4.4.x's `ktx` CLI on PATH, or pass an explicit binary:
 *   KTX_BIN=/path/to/ktx npm run compress:textures
 */
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, statSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const KTX = process.env.KTX_BIN || 'ktx';

const JOBS = [
  {
    kind: 'linear-mask',
    src: 'static/textures/foliage/foliageSDF.png',
    dst: 'static/textures/foliage/foliageSDF.ktx2',
    args: [
      '--format', 'R8_UNORM',
      '--assign-tf', 'linear',
      '--assign-primaries', 'none',
      '--encode', 'basis-lz',
      '--qlevel', '128',
    ],
  },
  {
    kind: 'linear-mask',
    src: 'static/textures/foliage/leaf-mask.png',
    dst: 'static/textures/foliage/leaf-mask.ktx2',
    args: [
      '--format', 'R8_UNORM',
      '--assign-tf', 'linear',
      '--assign-primaries', 'none',
      '--encode', 'basis-lz',
      '--qlevel', '128',
    ],
  },
  {
    kind: 'srgb-decal',
    src: 'static/textures/foliage/footprint-tread.png',
    dst: 'static/textures/foliage/footprint-tread.ktx2',
    args: [
      '--format', 'R8G8B8A8_SRGB',
      '--assign-tf', 'srgb',
      '--generate-mipmap',
      '--encode', 'basis-lz',
      '--qlevel', '128',
    ],
  },
  {
    // Painted path/slab art, sampled (RepeatWrapping) in the terrain ground
    // material — always GPU-resident. KTX2 is ~+40KB on disk but stays
    // block-compressed in VRAM (~1MB) vs the WebP decoding to full RGBA+mips
    // (~8MB at 1254²). `ktx create` can't read WebP → pre-decode via sips.
    kind: 'srgb-color',
    src: 'static/world/tiles.webp',
    dst: 'static/world/tiles.ktx2',
    decodeWebp: true,
    // Source is 1254² (non-POT, not a mult of 4 → fails basis block compression
    // + RepeatWrapping mipmaps want POT). Resize to 1024² on decode.
    resizeTo: 1024,
    args: [
      '--format', 'R8G8B8A8_SRGB',
      '--assign-tf', 'srgb',
      '--generate-mipmap',
      '--encode', 'basis-lz',
      '--qlevel', '128',
    ],
  },
];

const version = spawnSync(KTX, ['--version'], { encoding: 'utf8' });
if (version.status !== 0) {
  console.error('ktx CLI not found. Install Khronos KTX-Software 4.4.x or set KTX_BIN.');
  console.error('\nPlanned KTX2 jobs:');
  for (const job of JOBS) {
    console.error(`  ${job.kind.padEnd(12)} ${job.src} -> ${job.dst}`);
  }
  process.exit(version.status || 1);
}

console.log(version.stdout.trim());

for (const job of JOBS) {
  const src = join(ROOT, job.src);
  const dst = join(ROOT, job.dst);
  if (!existsSync(src)) {
    console.warn(`skip missing ${job.src}`);
    continue;
  }
  mkdirSync(dirname(dst), { recursive: true });

  // ktx create reads PNG/JPEG only — WebP sources are pre-decoded to a temp PNG
  // via macOS `sips` (this is a dev-machine tool, run on the author's Mac).
  let input = src;
  let tmpPng = null;
  if (job.decodeWebp) {
    tmpPng = join(tmpdir(), `ktx-decode-${job.kind}.png`);
    const sipsArgs = ['-s', 'format', 'png'];
    if (job.resizeTo) sipsArgs.push('-z', String(job.resizeTo), String(job.resizeTo));
    sipsArgs.push(src, '--out', tmpPng);
    const dec = spawnSync('sips', sipsArgs, { encoding: 'utf8' });
    if (dec.status !== 0) {
      console.warn(`skip ${job.src}: WebP→PNG decode failed (sips, macOS only)`);
      continue;
    }
    input = tmpPng;
  }

  run(['create', ...job.args, input, dst]);
  run(['validate', '--gltf-basisu', dst]);
  if (tmpPng) rmSync(tmpPng, { force: true });

  const start = statSync(src).size;
  const end = statSync(dst).size;
  const pct = start ? (100 * (1 - end / start)).toFixed(1) : '0.0';
  console.log(`${job.dst}: ${kb(start)} -> ${kb(end)} (${pct}% smaller)`);
}

function run(args) {
  const result = spawnSync(KTX, args, { stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status || 1);
}

function kb(bytes) {
  return `${(bytes / 1024).toFixed(1)} KB`;
}
