#!/usr/bin/env node
/**
 * Generate KTX2 siblings for the runtime textures that measured smaller and are
 * actually sampled by Three materials.
 *
 * Requires KTX-Software 4.4.x's `ktx` CLI on PATH, or pass an explicit binary:
 *   KTX_BIN=/path/to/ktx npm run compress:textures
 */
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
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
  run([
    'create',
    ...job.args,
    src,
    dst,
  ]);
  run(['validate', '--gltf-basisu', dst]);

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
