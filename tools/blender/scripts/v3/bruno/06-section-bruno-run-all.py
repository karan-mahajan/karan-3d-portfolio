"""Run Bruno's faithful world from zero through section 06 (buildings & structures).

Rebuilds the whole Bruno world in numeric dependency order into its own file:
  Step 1: every bruno/01-foundation-bruno-*.py      (datablocks; no visible objects)
  Step 2: every bruno/02-ground-grass-bruno-*.py    (terrain + grass)
  Step 3: every bruno/03-surface-detail-bruno-*.py  (scenery, rocks, bridges, road, slabs)
  Step 4: every bruno/04-*-bruno-*.py               (section 04: trees, decorations, markers)
  Step 5: every bruno/05-foliage-bruno-*.py         (bushes, flowers, fences, bricks)
  Step 6: every bruno/06-buildings-bruno-*.py       (building, altar, cabin, lab, etc.)

Section 06 sub-steps are picked up automatically by the `06-` prefix:
  - 06-buildings-bruno-047-building         main building (waterfall feature)
  - 06-buildings-bruno-048-altar            ritual altar zone + collision shapes
  - 06-buildings-bruno-049-behindTheScene   backstage zone scaffold (empties)
  - 06-buildings-bruno-081-lab              lab room scaffold (carpet, fire, walls)
  - 06-buildings-bruno-091-kiosk            kiosk interaction point
  - 06-buildings-bruno-105-statue           statue collection stub (0 objects)
  - 06-buildings-bruno-108-timeMachine      time-machine prop + zone anchors
  - 06-buildings-bruno-114-toilet           toilet zone + fallen rock
  - 06-buildings-bruno-115-cabin            cabin + hidden metaball moss
  - 06-buildings-bruno-132-altar-001        EXCLUDED minimap altar stand-in
  - 06-buildings-bruno-133-behindTheScene-001  EXCLUDED minimap stand-in

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender - Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/06-section-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/06-section-bruno-run-all.py
"""
import importlib.util
import os
import sys

BRUNO_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-bruno.blend"


def _load(filename):
    path = os.path.join(BRUNO_DIR, filename)
    name = os.path.splitext(filename)[0].replace("-", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _section_files(prefix):
    return sorted(
        f for f in os.listdir(BRUNO_DIR)
        if f.startswith(prefix) and f.endswith(".py") and "run-all" not in f
    )


def _run_section(label, prefix, required=True):
    files = _section_files(prefix)
    if not files:
        msg = f"[06-section-bruno] {'ERROR' if required else 'WARN'}: no files matched {prefix!r}\n"
        sys.stderr.write(msg)
        return 0
    print(f"[06-section-bruno] {label}: {len(files)} files")
    for f in files:
        print(f"  [{label}] {f}")
        _load(f).run()
    return len(files)


def main():
    total = 0
    total += _run_section("foundation",     "01-foundation-bruno-")
    total += _run_section("ground-grass",   "02-ground-grass-bruno-")
    total += _run_section("surface-detail", "03-surface-detail-bruno-")
    total += _run_section("section-04",     "04-")
    total += _run_section("section-05",     "05-")
    total += _run_section("section-06",     "06-")
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[06-section-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[06-section-bruno] save failed: {e}\n")
    print(f"[06-section-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
