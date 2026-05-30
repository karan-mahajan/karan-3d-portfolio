"""Add water color to karan's depressions by populating terrainWater.B.

Runs AFTER `02-ground-grass-base.py`, which authored R (depression depth)
and zeroed B (no water). This script mirrors R into B so the terrain
material's Map Range chain paints water color where the depressions are.

Bruno's terrain material samples `terrainWater.B` only (R and G are unused
by the material). The B-channel drives two Map Range thresholds:
  - B in [0.10, 0.30]: blends ground → shallow water color
  - B in [0.30, 1.00]: blends shallow color → deep water color
  - B  < 0.10: no water tint
  - B >= 1.00: full deep water color

In Bruno's source EXR, R == G == B identically (verified). So mirroring R
into B is the faithful approach and gives water exactly where depressions
are. The natural sqrt falloff in `base.py`'s river/pond stamps means
shoreline tints fade smoothly to ground color.

Per the keep-everything policy: only mutates in-memory pixels of the
existing `terrainWater` datablock. Re-running `base.py` resets B to 0.

ISOLATION (added 2026-05-29): Bruno's foundation loads `terrainWater` from
`bruno/resources/textures/terrainWater.exr` — his pristine reference, which
karan must NEVER overwrite (doing so once corrupted Bruno's world). After
painting, this script replaces that external image with a generated packed
datablock, so the authored pixels live inside `world-v3-karan.blend` without an
EXR save/load round-trip changing the mask orientation.
"""
import importlib
import os
import sys

import bpy
import numpy as np

KARAN_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() \
    else "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan"
if KARAN_DIR not in sys.path:
    sys.path.append(KARAN_DIR)

import lava_common  # the lava basin must NOT get the teal/navy water tint
importlib.reload(lava_common)

IMAGE_NAME = "terrainWater"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"


def _replace_with_packed_image(img, pixels):
    """Store authored pixels in a generated packed image and remap all users.

    Blender's EXR file save/pack path reloads this mask with the row/column
    orientation transposed. A generated packed image avoids that external
    texture round-trip while keeping Bruno's source EXR untouched.
    """
    old_name = img.name
    w, h = img.size
    channels = img.channels
    packed = bpy.data.images.new(
        f"{old_name}.packedAuthored",
        width=w,
        height=h,
        alpha=channels >= 4,
        float_buffer=True,
    )
    try:
        packed.colorspace_settings.name = img.colorspace_settings.name
    except Exception:
        pass
    packed.pixels.foreach_set(pixels.ravel())
    try:
        packed.update()
    except Exception:
        pass
    packed.pack()

    img.user_remap(packed)
    img.name = f"{old_name}.externalSource"
    packed.name = old_name
    return packed


def run():
    print("[02-ground-grass-water] mirror R → B on terrainWater (paint water in depressions)")
    img = bpy.data.images.get(IMAGE_NAME)
    if img is None:
        print(f"  [WARN] image {IMAGE_NAME!r} not found — skipping")
        return
    w, h = img.size
    if w == 0 or h == 0:
        print(f"  [WARN] image {IMAGE_NAME!r} has zero size — skipping")
        return
    channels = img.channels
    pixels = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, channels))

    r = pixels[:, :, 0]
    new_b = np.clip(r, 0.0, 1.0)
    # The lava basin is carved into R (it's a depression) but must NOT read as
    # water — zero B there so the terrain shader paints no teal/navy tint; the
    # molten lava surface (14-fx-lava.py) covers the bare bed instead.
    new_b[lava_common.basin_inside(w, h)] = 0.0
    pixels[:, :, 2] = new_b

    img = _replace_with_packed_image(img, pixels)
    print("  packed authored terrainWater pixels into generated .blend image")

    shallow = float(((new_b >= 0.10) & (new_b < 0.30)).mean()) * 100.0
    deep = float((new_b >= 0.30).mean()) * 100.0
    print(
        f"  {IMAGE_NAME}.B authored — shallow (teal forming) {shallow:.1f}%, "
        f"deep (navy forming) {deep:.1f}%."
    )

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
