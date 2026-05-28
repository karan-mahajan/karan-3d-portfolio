"""Author the tile/path overlay on terrainFurnitures.R — only on path zones.

The path polylines live in `02-ground-grass-grass.py` so the tile texture
lights up exactly where the grass mask drops out. We import that module via
importlib (run-all.py loads scripts in alphabetical order so grass.py has
already executed by the time we get here, but the import doesn't require
that — it just reads constants).

Mapping:
   path_d <= 0          (path centre)  → tiles_R = 1.0
   path_d == halfwidth  (path edge)    → tiles_R fades to 0
   path_d  > halfwidth                  → tiles_R = 0

Edge of path also receives an explicit water gate so the tile texture never
bleeds into a pond or river even if a polyline waypoint drifts too close.

Bruno's slabs.png is the tile texture used until the user supplies their
own. Material vector-math scale on the texture is (0.2, 0.2, 0.2) →
bricks repeat every ~5m at world scale.

Per the keep-everything policy: mutates terrainFurnitures.R pixels in
memory. Re-running blank-bruno.py zeros it again. Saves the .blend at end
so iterations persist.
"""
import bpy
import importlib.util
import numpy as np
import os

IMAGE_FURNITURE = "terrainFurnitures"
IMAGE_WATER = "terrainWater"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
MASK_DIR = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/resources/masks"
FURNITURE_MASK_FILE = f"{MASK_DIR}/terrainFurnitures-authored.exr"

# Source of truth for path polylines and width. Hardcoded absolute path so
# the import works both via run-all.py (where __file__ is set) and via
# `exec(open(...).read())` in the Blender Python Console (where it isn't).
GRASS_SCRIPT = (
    "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/"
    "scripts/v3/karan/02-ground-grass-grass.py"
)

# Fade band on the water-R mask. Tile alpha drops to 0 wherever this gate
# says "water" so paths can graze the shoreline without producing tile
# slivers floating in water.
WATER_GATE_START = 0.05
WATER_GATE_END = 0.18


def _load_grass_module():
    """Import the grass authoring script for its PATH_POLYLINES + helpers."""
    spec = importlib.util.spec_from_file_location("_authored_grass", GRASS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _save_mask_image(img, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.filepath_raw = filepath
        img.file_format = "OPEN_EXR"
        img.save()
        print(f"  {img.name}: saved edited pixels -> {filepath}")
    except Exception as e:
        print(f"  [WARN] could not save {img.name!r}: {e}")


def run():
    print("[02-ground-grass-tiles] author tile overlay on path zones only")
    img_f = bpy.data.images.get(IMAGE_FURNITURE)
    img_w = bpy.data.images.get(IMAGE_WATER)
    if img_f is None:
        print(f"  [WARN] image {IMAGE_FURNITURE!r} not found — skipping")
        return
    if img_w is None:
        print(f"  [WARN] image {IMAGE_WATER!r} not found — cannot derive water gate")
        return

    w, h = img_f.size
    if w == 0 or h == 0:
        print(f"  [WARN] image {IMAGE_FURNITURE!r} has zero size — skipping")
        return

    grass = _load_grass_module()
    polylines = grass.PATH_POLYLINES
    detail_polylines = getattr(grass, "DETAIL_PATH_POLYLINES", [])
    open_areas = getattr(grass, "OPEN_AREAS", [])
    if hasattr(grass, "build_path_mask"):
        path = grass.build_path_mask(w, h)
    else:
        halfwidth = grass.PATH_HALFWIDTH
        px, py = grass._build_pixel_grid(w, h)
        path = np.zeros((h, w), dtype=np.float32)
        for poly in polylines:
            grass._stamp_polyline(path, px, py, poly, halfwidth, 1.0)
        path = np.clip(path, 0.0, 1.0)

    channels_w = img_w.channels
    water_pixels = np.asarray(img_w.pixels[:], dtype=np.float32).reshape((h, w, channels_w))
    water_r = water_pixels[:, :, 0]
    land_gate = 1.0 - np.clip(
        (water_r - WATER_GATE_START) / (WATER_GATE_END - WATER_GATE_START),
        0.0, 1.0,
    )

    tile_r = path * land_gate

    channels_f = img_f.channels
    furniture_pixels = np.asarray(img_f.pixels[:], dtype=np.float32).reshape((h, w, channels_f))
    furniture_pixels[:, :, 0] = tile_r
    if channels_f >= 4:
        furniture_pixels[:, :, 3] = 1.0

    img_f.pixels.foreach_set(furniture_pixels.ravel())
    try:
        img_f.update()
    except Exception:
        pass
    _save_mask_image(img_f, FURNITURE_MASK_FILE)

    # terrainGrass.G is owned by 02-ground-grass-grass.py, which authors a
    # SOFT sqrt falloff that already eases blade scale + ground tint to 0
    # at path centres. Re-zeroing G here on a hard tile threshold would
    # clobber that gradient and bring back the harsh grey/green seam.

    coverage = float((tile_r > 0.05).mean()) * 100.0
    full = float((tile_r >= 0.95).mean()) * 100.0
    print(
        f"  {IMAGE_FURNITURE}.R authored — tile coverage {coverage:.1f}% "
        f"(full-strength {full:.1f}%, gated against water). "
        f"{len(polylines)} main paths + {len(detail_polylines)} detail paths "
        f"+ {len(open_areas)} open areas stamped."
    )

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
