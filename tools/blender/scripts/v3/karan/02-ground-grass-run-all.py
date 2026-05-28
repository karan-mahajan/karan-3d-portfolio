"""Run karan's full v3 build up to section 02 (foundation + ground-grass).

Sequence:
  Step 1: every bruno/01-foundation-bruno-*.py     (Bruno foundation)
  Step 2: every karan/01-foundation-*.py            (karan foundation deltas — palette swap)
  Step 3: every bruno/02-ground-grass-bruno-*.py    (Bruno terrain + grass)
  Step 4: every karan/02-ground-grass-*.py          (karan section-02 deltas)

The first bruno step (000-init) wipes the open .blend's datablocks.
Run on a fresh empty file (File > New > General).

Auto-saves to `tools/blender/world-v3-karan.blend` when done.

Inside Blender — Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/02-ground-grass-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/karan/02-ground-grass-run-all.py
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
        sys.stderr.write(f"[02-ground-grass] WARN: no files matched {prefix!r} in {directory}\n")
        return 0
    print(f"[02-ground-grass] {label}: {len(files)} files")
    for f in files:
        print(f"  [{label}] {f}")
        _load(directory, f).run()
    return len(files)


def main():
    total = 0
    total += _run_section("bruno-foundation",   BRUNO_DIR, "01-foundation-bruno-")
    total += _run_section("karan-foundation",   KARAN_DIR, "01-foundation-")
    total += _run_section("bruno-ground-grass", BRUNO_DIR, "02-ground-grass-bruno-")
    total += _run_section("karan-ground-grass", KARAN_DIR, "02-ground-grass-")
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[02-ground-grass] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[02-ground-grass] save failed: {e}\n")
    print(f"[02-ground-grass] DONE ({total} steps total)")


if __name__ == "__main__":
    main()
