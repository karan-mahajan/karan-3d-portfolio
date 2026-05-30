"""Run Bruno's faithful world from zero through section 13 (food / misc / fx).

Rebuilds the whole Bruno world in numeric dependency order into its own file:
  Step 1: every bruno/01-foundation-bruno-*.py      (datablocks; no visible objects)
  Step 2: every bruno/02-ground-grass-bruno-*.py    (terrain + grass)
  Step 3: every bruno/03-surface-detail-bruno-*.py  (scenery, rocks, bridges, road, slabs)
  Step 4: every bruno/04-*-bruno-*.py               (section 04: trees, decorations, markers)
  Step 5: every bruno/05-foliage-bruno-*.py         (bushes, flowers, fences, bricks)
  Step 6: every bruno/06-buildings-bruno-*.py       (building, altar, cabin, lab, etc.)
  Step 7: every bruno/13-misc-fx-bruno-*.py         (title, airDancers, cookie, fx, props)

Section 13 sub-steps are picked up automatically by the `13-` prefix:
  - 13-misc-fx-bruno-063-airDancers           2 inflatable tube-guys (airDancer shader)
  - 13-misc-fx-bruno-079-cookie               interactive cookie zone (preventAutoAdd)
  - 13-misc-fx-bruno-080-easter-001           easter-hunt event anchors (EXCLUDED)
  - 13-misc-fx-bruno-090-controls             controls signage + gamepad/phone props
  - 13-misc-fx-bruno-092-title-001            knockable welcome-title letters (mass props)
  - 13-misc-fx-bruno-107-FWA                  FWA award badges under statue (EXCLUDED)
  - 13-misc-fx-bruno-110-cups                 drink cups inside timeMachine
  - 13-misc-fx-bruno-111-playstation          PlayStation console prop
  - 13-misc-fx-bruno-121-fwa                  FWA badges from explosive crates (EXCLUDED)
  - 13-misc-fx-bruno-124-antenna-001          sci-fi antenna accent (EXCLUDED)
  - 13-misc-fx-bruno-126-oldSchool            retro accent prop set (EXCLUDED)
  - 13-misc-fx-bruno-128-sudo                 rigged "sudo" dev character (EXCLUDED)
  - 13-misc-fx-bruno-129-easter               easter/egg parent collection stub (EXCLUDED)
  - 13-misc-fx-bruno-130-egg                  easter-egg meshes (EXCLUDED)
  - 13-misc-fx-bruno-138-tornado              tornado-event path anchors (EXCLUDED)
  - 13-misc-fx-bruno-139-whispersForbiddenAreas  forbidden-zone audio anchors (EXCLUDED)

Note: Bruno's 101_pole (the projects signage pole, also part of his
food/misc/fx group) already lives in section 04 as
`04-decorations-bruno-101-pole.py`, so it is NOT re-added here.

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender - Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/13-section-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/13-section-bruno-run-all.py
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
        msg = f"[13-section-bruno] {'ERROR' if required else 'WARN'}: no files matched {prefix!r}\n"
        sys.stderr.write(msg)
        return 0
    print(f"[13-section-bruno] {label}: {len(files)} files")
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
    total += _run_section("section-13",     "13-")
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[13-section-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[13-section-bruno] save failed: {e}\n")
    print(f"[13-section-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
