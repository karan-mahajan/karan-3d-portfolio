"""Run Bruno's faithful world from zero through section 05 (foliage/flowers/boundaries).

Rebuilds the whole Bruno world in numeric dependency order into its own file:
  Step 1: every bruno/01-foundation-bruno-*.py      (datablocks; no visible objects)
  Step 2: every bruno/02-ground-grass-bruno-*.py    (terrain + grass)
  Step 3: every bruno/03-surface-detail-bruno-*.py  (scenery, rocks, bridges, road, slabs)
  Step 4: every bruno/04-*-bruno-*.py               (section 04 KEEP items: trees, decorations, markers)
  Step 5: every bruno/05-foliage-bruno-*.py         (bushes, flowers, fences, bricks)

Section 05 sub-steps are picked up automatically by the `05-` prefix:
  - 05-foliage-bruno-040-bushes   130 SDF-anchor bush meshes
  - 05-foliage-bruno-041-flowers  108 flat flower-decal patches
  - 05-foliage-bruno-042-fences   16 fence planks + 16 wire colliders
  - 05-foliage-bruno-043-bricks   30 brick blocks

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender - Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/05-section-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/05-section-bruno-run-all.py
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
        msg = f"[05-section-bruno] {'ERROR' if required else 'WARN'}: no files matched {prefix!r}\n"
        sys.stderr.write(msg)
        return 0
    print(f"[05-section-bruno] {label}: {len(files)} files")
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
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[05-section-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[05-section-bruno] save failed: {e}\n")
    print(f"[05-section-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
