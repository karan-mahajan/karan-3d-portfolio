"""Run karan's full v3 build up to section 03 (foundation + ground-grass + surface-detail).

Sequence:
  Step 1: every bruno/01-foundation-bruno-*.py     (Bruno foundation — loads all meshes)
  Step 2: every karan/01-foundation-*.py            (karan foundation deltas — palette swap)
  Step 3: every bruno/02-ground-grass-bruno-*.py    (Bruno terrain + grass)
  Step 4: every karan/02-ground-grass-*.py          (karan section-02 deltas)
  Step 5: every karan/03-surface-detail-*.py         (karan section-03: bridges, rocks, slabs)

Why no bruno/03-surface-detail-bruno-* step: karan's section-03 fully DIVERGES
from Bruno (per the keep-everything-but-can-diverge policy). The kept items are
authored as independent objects built from the foundation meshes —
  - bridges: bridge01 + bridge02 (curved) from Cube.211
  - rocks:   procedural boulder/shard meshes, transforms locked in shore_stones.json
  - slabs:   slab01/02/03 from Cube.063/Cube.001/Cube.002
Running Bruno's placement scripts (023/024/027) would duplicate these, and
024/051/075 would re-add the road + scenery we dropped. So Bruno's surface
scripts are intentionally skipped — nothing is removed, those object placements
are simply never built. The foundation still loads every Bruno mesh.

The first bruno step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-karan.blend` when done.

Inside Blender — Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/03-surface-detail-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/karan/03-surface-detail-run-all.py
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
        sys.stderr.write(f"[03-surface-detail] WARN: no files matched {prefix!r} in {directory}\n")
        return 0
    print(f"[03-surface-detail] {label}: {len(files)} files")
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
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[03-surface-detail] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[03-surface-detail] save failed: {e}\n")
    print(f"[03-surface-detail] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
