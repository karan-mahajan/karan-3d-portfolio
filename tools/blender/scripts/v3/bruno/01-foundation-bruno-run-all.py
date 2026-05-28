"""Run every 01-foundation-bruno-*.py step in order.

These are copies of Bruno's folio-2025 foundation scripts (000_init through
013_collections), renamed with the `01-foundation-bruno-NNN-*` prefix so
they sort into the same execution order Bruno uses.

The first script (000-init) wipes the open .blend's datablocks. Run on a
fresh empty file (File > New > General) or save the current file first.
None of these scripts call save_as_mainfile() — datablocks live in memory
until you save.

Inside Blender:
    Text Editor > Open this file > Alt+P (Run Script)

Or in the Python Console (more reliable than Alt+P):
    exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno/01-foundation-bruno-run-all.py').read())

Headless:
    blender --background --factory-startup \
        --python tools/blender/scripts/v3/bruno/01-foundation-bruno-run-all.py
"""
import os
import sys
import importlib.util

PREFIX = "01-foundation-bruno-"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-bruno.blend"


def _here():
    """Resolve the v3/ directory under several invocation contexts.

    - Headless (`blender --python this_file.py`): __file__ is set.
    - Text Editor (Alt+P): __file__ is sometimes unset depending on Blender
      version + how the text was loaded. Fall back to the active Text
      block's filepath, then to a hardcoded absolute path as a last resort.
    """
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import bpy
        for area in bpy.context.screen.areas:
            if area.type == "TEXT_EDITOR" and area.spaces.active.text and area.spaces.active.text.filepath:
                fp = area.spaces.active.text.filepath
                if PREFIX in os.path.basename(fp):
                    return os.path.dirname(os.path.abspath(bpy.path.abspath(fp)))
    except Exception:
        pass
    return "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/bruno"


def _load(path):
    name = os.path.splitext(os.path.basename(path))[0].replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    here = _here()
    files = sorted(
        f for f in os.listdir(here)
        if f.startswith(PREFIX) and f.endswith(".py") and "run-all" not in f
    )
    print(f"[01-foundation-bruno] resolved dir: {here}")
    print(f"[01-foundation-bruno] found {len(files)} step files")
    if not files:
        sys.stderr.write(
            f"[01-foundation-bruno] ERROR: no step files matched in {here}. "
            "Check the directory and the PREFIX.\n"
        )
        return
    for f in files:
        print(f"[01-foundation-bruno] {f}")
        _load(os.path.join(here, f)).run()
    try:
        import bpy
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"[01-foundation-bruno] saved -> {BLEND_PATH}")
    except Exception as e:
        sys.stderr.write(f"[01-foundation-bruno] save failed: {e}\n")
    print(f"[01-foundation-bruno] DONE ({len(files)} steps)")


if __name__ == "__main__":
    main()
