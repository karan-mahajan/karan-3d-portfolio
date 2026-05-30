"""Run Bruno's faithful world from zero AND finalize it (the LAST build step).

Supersedes 13-section-bruno-run-all.py (which stopped at section 13). Rebuilds
the whole Bruno world in numeric dependency order, then runs Bruno's verbatim
999_finalize as the FINAL step so the assembled scene is wired together:

  Step 1: every bruno/01-foundation-bruno-*.py      (datablocks; no visible objects)
  Step 2: every bruno/02-ground-grass-bruno-*.py    (terrain + grass)
  Step 3: every bruno/03-surface-detail-bruno-*.py  (scenery, rocks, bridges, road, slabs)
  Step 4: every bruno/04-*-bruno-*.py               (section 04: trees, decorations, markers)
  Step 5: every bruno/05-foliage-bruno-*.py         (bushes, flowers, fences, bricks)
  Step 6: every bruno/06-buildings-bruno-*.py       (building, altar, cabin, lab, etc.)
  Step 7: every bruno/13-misc-fx-bruno-*.py         (title, airDancers, cookie, fx, props)
  Step 8: bruno/15-finalize-bruno-999-finalize.py   (parenting + view-layers + compositor)

Step 8 is `999_finalize.py` copied VERBATIM from Bruno's
folio-2025/scripts/blender_world_steps/steps/. It is idempotent (`if _o is
not None` guards every relationship) and only ADDS/organizes — it never
deletes a datablock. Objects from Bruno sections we did NOT build (race track,
bowling, etc.) simply do not exist, so their parenting/view-layer lines are
skipped. This is faithful Bruno behaviour on a partial Bruno world.

The first foundation step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-bruno.blend` when done.

Inside Blender - Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/15-section-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/15-section-bruno-run-all.py
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
        msg = f"[15-section-bruno] {'ERROR' if required else 'WARN'}: no files matched {prefix!r}\n"
        sys.stderr.write(msg)
        return 0
    print(f"[15-section-bruno] {label}: {len(files)} files")
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
    total += _run_section("finalize",       "15-finalize-bruno-")  # MUST be last
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[15-section-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[15-section-bruno] save failed: {e}\n")
    print(f"[15-section-bruno] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
