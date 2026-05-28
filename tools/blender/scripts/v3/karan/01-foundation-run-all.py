"""Run our customized 01-foundation in the open .blend.

Step 1: run every bruno/01-foundation-bruno-*.py file in order
       (Bruno's full 20-script foundation: textures, materials, node
       groups, mesh datablocks, collections, etc.).
Step 2: run every karan/01-foundation-*.py delta in order (currently
       just 01-foundation-palette.py — swaps the palette image).

This is the v3 foundation that later sections build on top of. Per the
"don't drop anything yet" policy, this loads Bruno's full library
(368 meshes, 35 materials, 9 node groups, 120 collections, etc.) and
only overrides the palette image with our sunset 16-color strip.

The first bruno step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General) or save the current
file first. Save the resulting .blend as `world-v3-karan.blend`
(separate from `world-v3-bruno.blend`).

Inside Blender:
    Text Editor > Open this file > Alt+P (Run Script)

Or in the Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/01-foundation-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/karan/01-foundation-run-all.py
"""
import importlib.util
import os
import sys

# Hardcoded absolute paths — single-user project, no portability concern.
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


def main():
    bruno_files = sorted(
        f for f in os.listdir(BRUNO_DIR)
        if f.startswith("01-foundation-bruno-") and f.endswith(".py") and "run-all" not in f
    )
    karan_files = sorted(
        f for f in os.listdir(KARAN_DIR)
        if f.startswith("01-foundation-") and f.endswith(".py") and "run-all" not in f
    )
    if not bruno_files:
        sys.stderr.write(f"[01-foundation] ERROR: no bruno scripts in {BRUNO_DIR}\n")
        return
    print(f"[01-foundation] step 1: bruno foundation ({len(bruno_files)} files)")
    for f in bruno_files:
        print(f"  [bruno] {f}")
        _load(BRUNO_DIR, f).run()
    print(f"[01-foundation] step 2: karan deltas ({len(karan_files)} files)")
    for f in karan_files:
        print(f"  [karan] {f}")
        _load(KARAN_DIR, f).run()
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[01-foundation] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[01-foundation] save failed: {e}\n")
    print(f"[01-foundation] DONE ({len(bruno_files) + len(karan_files)} steps total)")


if __name__ == "__main__":
    main()
