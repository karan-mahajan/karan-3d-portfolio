"""Run Bruno's faithful world from zero through section 04 (props/vegetation).

Rebuilds the whole Bruno world in numeric dependency order into its own file:
  Step 1: every bruno/01-foundation-bruno-*.py      (datablocks; no visible objects)
  Step 2: every bruno/02-ground-grass-bruno-*.py    (terrain + grass)
  Step 3: every bruno/03-surface-detail-bruno-*.py  (scenery, rocks, bridges, road, slabs)
  Step 4: every bruno/04-*-bruno-*.py               (section 04 KEEP items)

Section 04 here is scoped to the triaged KEEP set only (the heterogeneous
race/lab/easter/avatar steps were dropped). As 04 sub-sections land they are
picked up automatically by the `04-` prefix:
  - 04-vegetation-bruno-*   trees (028/032/036 stubs + 134/135/136 placements)
  - 04-decorations-bruno-*  bonfire, benches, lanterns, poleLights, pole (later)

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender - Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/04-section-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/04-section-bruno-run-all.py
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
        msg = f"[04-section-bruno] {'ERROR' if required else 'WARN'}: no files matched {prefix!r}\n"
        sys.stderr.write(msg)
        return 0
    print(f"[04-section-bruno] {label}: {len(files)} files")
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
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[04-section-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[04-section-bruno] save failed: {e}\n")
    print(f"[04-section-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
