"""Swap Bruno's slabs.png for ours.

Bruno's `bruno/01-foundation-bruno-002-images.py` creates a datablock
named `slabs.png` pointing at `folio-2025/resources/textures/slabs.png`.
The terrain material's `Image Texture.004` node samples that datablock,
so swapping the file under it changes the tile/brick pattern everywhere
without touching the material.

Mirrors the same pattern as `01-foundation-palette.py`.
"""
import bpy
import os

TILE_IMAGE = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/resources/tiles.png"
DATABLOCK_NAME = "slabs.png"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"


def run():
    print("[02-ground-grass-tile-image] swap slabs.png datablock to karan tile image")
    if not os.path.exists(TILE_IMAGE):
        print(f"  [WARN] karan tile image not found at {TILE_IMAGE}")
        print(f"         drop your tile PNG there and re-run. Skipping for now.")
        return

    img = bpy.data.images.get(DATABLOCK_NAME)
    if img is None:
        img = bpy.data.images.load(TILE_IMAGE, check_existing=False)
        img.name = DATABLOCK_NAME
        print(f"  no existing {DATABLOCK_NAME!r} datablock; created new")
    else:
        img.filepath = TILE_IMAGE
        try:
            img.reload()
        except Exception as e:
            print("  reload failed:", e)
        print(f"  rebased existing {DATABLOCK_NAME!r} filepath + reloaded")
    try: img.source = "FILE"
    except Exception: pass
    try: img.colorspace_settings.name = "sRGB"
    except Exception: pass
    try: img.alpha_mode = "STRAIGHT"
    except Exception: pass
    print(f"  {DATABLOCK_NAME} now -> {TILE_IMAGE}")

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
