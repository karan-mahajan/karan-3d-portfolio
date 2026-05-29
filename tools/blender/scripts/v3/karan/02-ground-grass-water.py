"""Add water color to karan's depressions by populating terrainWater.B.

Runs AFTER `02-ground-grass-base.py`, which authored R (depression depth)
and zeroed B (no water). This script mirrors R into B so the terrain
material's Map Range chain paints water color where the depressions are.

Bruno's terrain material samples `terrainWater.B` only (R and G are unused
by the material). The B-channel drives two Map Range thresholds:
  - B in [0.10, 0.30]: blends ground → teal  (RGB.002 = 0.10, 0.54, 0.49)
  - B in [0.30, 1.00]: blends teal  → navy   (RGB.003 = 0.01, 0.04, 0.11)
  - B  < 0.10: no water tint
  - B >= 1.00: full navy (ocean)

In Bruno's source EXR, R == G == B identically (verified). So mirroring R
into B is the faithful approach and gives water exactly where depressions
are. The natural sqrt falloff in `base.py`'s river/pond stamps means
shoreline tints fade smoothly to ground color.

Per the keep-everything policy: only mutates in-memory pixels of the
existing `terrainWater` datablock. Re-running `base.py` resets B to 0.

ISOLATION (added 2026-05-29): Bruno's foundation loads `terrainWater` from
`bruno/resources/textures/terrainWater.exr` — his pristine reference, which
karan must NEVER overwrite (doing so once corrupted Bruno's world). After
painting, this script repoints the datablock at karan's OWN copy and PACKS the
painted pixels into `world-v3-karan.blend`, so the karan world is self-contained
and Bruno's reference file stays untouched no matter what is saved.
"""
import bpy
import numpy as np

IMAGE_NAME = "terrainWater"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
KARAN_TERRAINWATER = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/resources/textures/terrainWater.exr"


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
    pixels[:, :, 2] = new_b

    img.pixels.foreach_set(pixels.ravel())
    try:
        img.update()
    except Exception:
        pass

    # --- Isolation: keep karan's painted water on karan's own file + packed ---
    # so Bruno's shared EXR is never written and the karan world is self-contained.
    img.filepath = KARAN_TERRAINWATER
    img.filepath_raw = KARAN_TERRAINWATER
    try:
        img.pack()
        print(f"  packed terrainWater into .blend, repointed -> {KARAN_TERRAINWATER}")
    except Exception as e:
        print(f"  [WARN] pack failed: {e}")

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
