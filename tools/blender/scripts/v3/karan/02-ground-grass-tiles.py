"""Author tile/brick mask on terrainFurnitures.R — tiles cover the entire
walkable island except water.

The mask is derived from the existing terrainWater.R (authored by
02-ground-grass-base.py): tiles fill everywhere R is low, fade out where
R rises, and stay out of any water depression.

Mapping (inverse-water with a soft shoreline ramp):
   water_R <= FADE_START  →  tiles_R = 1.0   (full tile pattern)
   water_R == midpoint    →  tiles_R = 0.5   (shoreline transition)
   water_R >= FADE_END    →  tiles_R = 0.0   (no tiles — water shows)

The result:
  - rivers + south tributary  → no tiles (covered by water)
  - all 4 ponds               → no tiles
  - ocean ring (4 borders)    → no tiles
  - everywhere else on island → full tile pattern

Bruno's slabs.png is the tile texture used until the user supplies their
own. Material's vector-math scale on the texture is (0.2, 0.2, 0.2) →
bricks repeat every ~5m at world scale.

Bruno's material puts the tile overlay LAST in the shader chain
(Mix.004), so wherever we paint R high here, it overrides grass and
water. The water-fade threshold below leaves a small dry shoreline band
to keep the transitions readable.

Per the keep-everything policy: only mutates terrainFurnitures.R pixels
in memory. Re-running blank-bruno.py zeros it again. Saves the .blend
at end so iterations persist.
"""
import bpy
import numpy as np

IMAGE_FURNITURE = "terrainFurnitures"
IMAGE_WATER = "terrainWater"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# Shoreline fade band in water_R units.
# water_R below FADE_START → full tiles; above FADE_END → no tiles.
# A 0.10 wide band ≈ a few pixels of soft transition along each shoreline.
FADE_START = 0.05
FADE_END = 0.15


def run():
    print("[02-ground-grass-tiles] author tile mask on terrainFurnitures.R (everywhere except water)")
    img_f = bpy.data.images.get(IMAGE_FURNITURE)
    img_w = bpy.data.images.get(IMAGE_WATER)
    if img_f is None:
        print(f"  [WARN] image {IMAGE_FURNITURE!r} not found — skipping")
        return
    if img_w is None:
        print(f"  [WARN] image {IMAGE_WATER!r} not found — cannot derive tile mask")
        return

    w, h = img_f.size
    if w == 0 or h == 0:
        print(f"  [WARN] image {IMAGE_FURNITURE!r} has zero size — skipping")
        return
    if (img_w.size[0], img_w.size[1]) != (w, h):
        print(f"  [WARN] image sizes differ ({img_w.size} vs {img_f.size}) — using furnitures size")

    channels_f = img_f.channels
    channels_w = img_w.channels

    water_pixels = np.asarray(img_w.pixels[:], dtype=np.float32).reshape((h, w, channels_w))
    water_r = water_pixels[:, :, 0]

    # Smooth inverse: 1 where water is absent, 0 where water is present
    t = np.clip((water_r - FADE_START) / (FADE_END - FADE_START), 0.0, 1.0)
    new_r = 1.0 - t

    furniture_pixels = np.asarray(img_f.pixels[:], dtype=np.float32).reshape((h, w, channels_f))
    furniture_pixels[:, :, 0] = new_r
    if channels_f >= 4:
        furniture_pixels[:, :, 3] = 1.0

    img_f.pixels.foreach_set(furniture_pixels.ravel())
    try:
        img_f.update()
    except Exception:
        pass

    coverage = float((new_r > 0.05).mean()) * 100.0
    full = float((new_r >= 0.95).mean()) * 100.0
    print(
        f"  {IMAGE_FURNITURE}.R authored — tile coverage {coverage:.1f}% "
        f"(full-strength {full:.1f}%, rest is the shoreline fade band)."
    )

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
