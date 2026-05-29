"""Run karan's v3 build through section 04 decorations.

Sequence:
  Step 1: section 03 runner builds foundation + ground-grass + surface detail
  Step 2: every karan/04-decorations-*.py adds Karan-specific decoration props

Run on a fresh empty file:
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/04-decorations-run-all.py').read())
"""
import importlib.util
import os
import sys

KARAN_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
SECTION_03_RUNNER = os.path.join(KARAN_DIR, "03-surface-detail-run-all.py")
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"


def _load(path):
    name = os.path.splitext(os.path.basename(path))[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _section_files(prefix):
    return sorted(
        f for f in os.listdir(KARAN_DIR)
        if f.startswith(prefix) and f.endswith(".py") and "run-all" not in f
    )


def main():
    print("[04-decorations] rebuilding through section 03")
    _load(SECTION_03_RUNNER).main()

    files = _section_files("04-decorations-")
    print(f"[04-decorations] karan decorations: {len(files)} files")
    for filename in files:
        print(f"  [karan-decorations] {filename}")
        _load(os.path.join(KARAN_DIR, filename)).run()

    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[04-decorations] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[04-decorations] save failed: {e}\n")
    print("[04-decorations] DONE")


if __name__ == "__main__":
    main()
