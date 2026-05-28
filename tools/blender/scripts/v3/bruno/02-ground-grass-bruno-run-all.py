"""Run Bruno's faithful 01-foundation + 02-ground-grass in order.

Step 1: every bruno/01-foundation-bruno-*.py (textures, materials, node
        groups, mesh datablocks, collections — populates datablocks but
        spawns no visible scene objects).
Step 2: every bruno/02-ground-grass-bruno-*.py (terrain + grass scatter
        — the first visible objects in the scene).

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender — Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/02-ground-grass-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/02-ground-grass-bruno-run-all.py
"""
import importlib.util
import os
import sys

BRUNO_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-bruno.blend"


def _load(directory, filename):
    path = os.path.join(directory, filename)
    name = os.path.splitext(filename)[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _section_files(prefix):
    return sorted(
        f for f in os.listdir(BRUNO_DIR)
        if f.startswith(prefix) and f.endswith(".py") and "run-all" not in f
    )


def main():
    foundation = _section_files("01-foundation-bruno-")
    ground = _section_files("02-ground-grass-bruno-")
    if not foundation:
        sys.stderr.write(f"[02-ground-grass-bruno] ERROR: no foundation scripts in {BRUNO_DIR}\n")
        return
    if not ground:
        sys.stderr.write(f"[02-ground-grass-bruno] ERROR: no ground-grass scripts in {BRUNO_DIR}\n")
        return
    print(f"[02-ground-grass-bruno] step 1: foundation ({len(foundation)} files)")
    for f in foundation:
        print(f"  [foundation] {f}")
        _load(BRUNO_DIR, f).run()
    print(f"[02-ground-grass-bruno] step 2: ground-grass ({len(ground)} files)")
    for f in ground:
        print(f"  [ground-grass] {f}")
        _load(BRUNO_DIR, f).run()
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[02-ground-grass-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[02-ground-grass-bruno] save failed: {e}\n")
    total = len(foundation) + len(ground)
    print(f"[02-ground-grass-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
