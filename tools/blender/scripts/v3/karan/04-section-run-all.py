"""Run karan's FULL v3 world build — sections 01 through 04, everything.

This is the single master entry point. It rebuilds the whole world from
zero into `world-v3-karan.blend`:

  Step 1: bruno/01-foundation-bruno-*.py     (Bruno foundation — loads all meshes)
  Step 2: karan/01-foundation-*.py            (karan foundation deltas — palette swap)
  Step 3: bruno/02-ground-grass-bruno-*.py    (Bruno terrain + grass)
  Step 4: karan/02-ground-grass-*.py          (karan section-02: terrain shape, water, grass)
  Step 5: karan/03-surface-detail-*.py        (karan section-03: bridges, rocks, slabs)
  Step 6: karan/04-decorations-*.py           (benches, lanterns, bonfire, pole-lights)
  Step 7: karan/04-vegetation-*.py            (oak, cherry, birch trees)

Why no bruno/03-surface-detail-* or bruno/04-* step: karan's sections 03+
fully DIVERGE from Bruno (keep-everything-but-can-diverge policy). The kept
items are authored as independent objects on top of the foundation meshes, so
Bruno's own placement scripts are intentionally skipped — nothing is removed,
those placements are simply never built. The foundation still loads every
Bruno mesh.

The first bruno step (000-init) wipes the open .blend's datablocks, so this is
safe to run on top of a previous build. Best on a fresh file (File > New).

Auto-saves to `tools/blender/world-v3-karan.blend` when done. (Individual
sub-scripts also save as they run; the final save here is authoritative.)

Inside Blender — Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-section-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/karan/04-section-run-all.py
"""
import importlib.util
import os
import sys

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
BRUNO_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"


def _load(directory, filename):
    path = os.path.join(directory, filename)
    name = os.path.splitext(filename)[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _section_files(directory, prefix):
    return sorted(
        f for f in os.listdir(directory)
        if f.startswith(prefix) and f.endswith(".py") and "run-all" not in f
    )


def _run_section(label, directory, prefix):
    files = _section_files(directory, prefix)
    if not files:
        sys.stderr.write(f"[04-section] WARN: no files matched {prefix!r} in {directory}\n")
        return 0
    print(f"[04-section] {label}: {len(files)} files")
    for f in files:
        print(f"  [{label}] {f}")
        _load(directory, f).run()
    return len(files)


def main():
    total = 0
    total += _run_section("bruno-foundation",     BRUNO_DIR, "01-foundation-bruno-")
    total += _run_section("karan-foundation",     KARAN_DIR, "01-foundation-")
    total += _run_section("bruno-ground-grass",   BRUNO_DIR, "02-ground-grass-bruno-")
    total += _run_section("karan-ground-grass",   KARAN_DIR, "02-ground-grass-")
    total += _run_section("karan-surface-detail", KARAN_DIR, "03-surface-detail-")
    total += _run_section("karan-decorations",    KARAN_DIR, "04-decorations-")
    total += _run_section("karan-vegetation",     KARAN_DIR, "04-vegetation-")
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[04-section] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[04-section] save failed: {e}\n")
    print(f"[04-section] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
