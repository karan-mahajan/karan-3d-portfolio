"""Swap Bruno's palette.png for ours.

Bruno's `bruno/01-foundation-bruno-002-images.py` creates a datablock
named `palette` pointing at `v3/bruno/resources/palette.png` (his warm
clay/olive 25-color strip). This delta script redirects that datablock
to `v3/karan/resources/palette.png` (our 16-color sunset palette) so
every material in Bruno's foundation that samples
`bpy.data.images['palette']` now reads our colors.

Per the design decision: don't drop any of Bruno's other datablocks.
We just won't reference them. The only substantive customization to
01-foundation right now is this palette swap.
"""
import bpy
import os

KARAN_PALETTE = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/resources/palette.png"


def run():
    print("[01-foundation-palette] swapping palette image")
    if not os.path.exists(KARAN_PALETTE):
        raise FileNotFoundError(f"karan palette.png not found: {KARAN_PALETTE}")
    img = bpy.data.images.get("palette")
    if img is None:
        # Bruno's 002 hasn't run yet — load our palette directly as `palette`.
        img = bpy.data.images.load(KARAN_PALETTE, check_existing=False)
        img.name = "palette"
        print("  no existing `palette` image; created new")
    else:
        img.filepath = KARAN_PALETTE
        try:
            img.reload()
        except Exception as e:
            print("  reload failed:", e)
        print("  rebased existing `palette` filepath + reloaded")
    try: img.source = "FILE"
    except Exception: pass
    try: img.colorspace_settings.name = "sRGB"
    except Exception: pass
    try: img.alpha_mode = "STRAIGHT"
    except Exception: pass
    print(f"  palette now -> {KARAN_PALETTE}")


if __name__ == "__main__":
    run()
