"""Run karan's FULL v3 world build from zero AND finalize it — the LAST step.

The master entry point (supersedes 14-section-run-all.py, which stopped before
finalize). Rebuilds the whole world from zero into `world-v3-karan.blend`, then
runs 15-finalize as the FINAL step so the assembled scene graph is wired
(section-root parenting + collection/view-layer hygiene) ready for a clean GLB
export later.

  Step  1: bruno/01-foundation-bruno-*.py     (Bruno foundation — loads all meshes)
  Step  2: karan/01-foundation-*.py            (karan foundation deltas — palette swap)
  Step  3: bruno/02-ground-grass-bruno-*.py    (Bruno terrain + grass)
  Step  4: karan/02-ground-grass-*.py          (karan terrain shape, water, grass)
  Step  5: karan/03-surface-detail-*.py        (bridges, rocks, slabs)
  Step  6: karan/04-decorations-*.py           (benches, lanterns, bonfire, pole-lights)
  Step  7: karan/04-markers-*.py               (cardinal section landmarks + structures)
  Step  8: karan/04-vegetation-*.py            (oak, cherry, birch trees)
  Step  9: karan/05-foliage-*.py               (bushes, flowers, fences, bricks)
  Step 10: karan/06-buildings-*.py             (cabin, outhouse, statue)
  Step 11: karan/13-misc-fx-*.py               (title, controls, air dancers, playstation, animals)
  Step 12: karan/14-fx-*.py                    (lava pool behind the Projects hut)
  Step 13: karan/15-finalize.py                (FINALIZE — parenting + view-layers)  <-- LAST

15-finalize is discovery-driven: it inventories whatever the build produced and
wires only what exists, so changes to any earlier section (e.g. the lava) are
picked up automatically with no edits here.

The first bruno step (000-init) wipes the open .blend's datablocks, so this is
safe to run on top of a previous build. Best on a fresh file (File > New).

Auto-saves to `tools/blender/world-v3-karan.blend` AFTER finalize.

Inside Blender — Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/15-section-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/karan/15-section-run-all.py
"""
import importlib.util
import os
import sys

# Always compile section scripts fresh — never load stale .pyc from a prior run
# (a finalize edit must take effect on the very next rebuild).
sys.dont_write_bytecode = True

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
BRUNO_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# karan/05 + 06 + 13 + 14 scripts import their *_common modules; ensure importable.
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)


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
        sys.stderr.write(f"[15-section] WARN: no files matched {prefix!r} in {directory}\n")
        return 0
    print(f"[15-section] {label}: {len(files)} files")
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
    total += _run_section("karan-markers",        KARAN_DIR, "04-markers-")
    total += _run_section("karan-vegetation",     KARAN_DIR, "04-vegetation-")
    total += _run_section("karan-foliage",        KARAN_DIR, "05-foliage-")
    total += _run_section("karan-buildings",      KARAN_DIR, "06-buildings-")
    total += _run_section("karan-misc-fx",        KARAN_DIR, "13-misc-fx-")
    total += _run_section("karan-fx-lava",        KARAN_DIR, "14-fx-")

    # ---- FINALIZE (must be the last build step) ----
    print("[15-section] finalize: 15-finalize.py")
    _load(KARAN_DIR, "15-finalize.py").run()
    total += 1

    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[15-section] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[15-section] save failed: {e}\n")
    print(f"[15-section] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
