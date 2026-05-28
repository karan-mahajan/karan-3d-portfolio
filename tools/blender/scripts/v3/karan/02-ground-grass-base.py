"""Author karan's base terrain shape — depressions only, no water/grass rendering.

Replaces Bruno's `terrainWater.exr` R channel with a hand-coded layout
matching karan's design intent (per Part 5 reference image): a meandering
river through the island center, a south-branch tributary, two small ponds,
and a soft beach perimeter so the island edges slope down into ocean.

The R channel drives terrain vertex Z displacement via the foundation's
`Geometry Nodes` modifier (`R × -1.5m`). Bright = depression, black = flat
ground. So the depression LAYOUT lives entirely in this script's
`MAIN_RIVER`, `SOUTH_BRANCH`, `PONDS` waypoint lists — tune those to
reshape the world.

ALSO clears terrainWater's G and B channels: the terrain material samples
those for teal/navy water-coloring on top of the displaced terrain. We're
in "bare base shape only" mode — no water color rendering, no grass.

ALSO hides Plane.003 (grass scatter object): user sees ONLY the bare
terrain, no grass blades. Reverse later by un-hiding the object.

Per the keep-everything policy: mutates in-memory pixels of the existing
`terrainWater` datablock + sets hide flags on `Plane.003`. Nothing is
deleted. Reload-from-file on the EXR + un-hide on the object restores
Bruno's behavior.
"""
import bpy
import numpy as np

IMAGE_NAME = "terrainWater"
GRASS_OBJECT = "Plane.003"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# Softens the otherwise-perfectly-square island. Distance is in pixels of the
# 512x512 mask (≈0.244m/px at karan's 125m world). 80 px ≈ 19.5m — corners
# read as gently rounded instead of a hard 90° angle.
ISLAND_CORNER_RADIUS = 80

# All coords are EXR pixel space (512x512). With karan's 125m walkable
# world (terrain scaled to 0.651 of Bruno's 192m), 1 pixel ≈ 0.244m.
# Origin (0,0) = bottom-left.

# Main river: enters west, weaves through middle, exits east.
# Endpoints extend ~40 px PAST the image bounds so the channel retains
# full depth at x=0 / x=511 and visually reads as a river mouth flowing
# IN from the surrounding ocean (instead of fizzling into the beach).
# Soft 12-pixel-wide channel ≈ 2.9m wide, ~1.05m deep.
MAIN_RIVER = [
    (-40, 255),  # west: extends into ocean
    (  0, 260),  # crosses west island edge
    ( 80, 290),
    (160, 310),
    (240, 285),  # ~ center of map
    (310, 250),
    (380, 235),
    (450, 245),
    (511, 245),  # crosses east island edge
    (551, 245),  # east: extends into ocean
]

# South tributary branches off main and exits south into ocean.
SOUTH_BRANCH = [
    (310, 250),  # tee off MAIN_RIVER
    (330, 190),
    (340, 120),
    (315,  60),
    (300,   0),  # crosses south island edge
    (290, -40),  # south: extends into ocean
]

# Ponds — mixed shapes for an organic feel.
#
# Image-to-screen axis mapping (terrain at rotation 0, Blender top-down view):
#   Image X axis (0→511) → screen TOP→BOTTOM
#   Image Y axis (0→511) → screen LEFT→RIGHT
# So image pixel (0,0) renders at screen TOP-LEFT; (511,511) at BOTTOM-RIGHT.
# Use that when tuning waypoints from a screenshot.

# Perfectly circular ponds — (cx, cy, radius_px, peak_depth_value)
PONDS_CIRCLES = [
    (110, 145, 22, 0.70),  # UPPER-LEFT — kept circular by request (1 still-water pool)
    ( 75, 100, 18, 0.70),  # NEW small pond above the original (drawn oval)
]

# Organic ponds — each is (list_of_component_circles, peak_depth_value).
# Each component is (cx, cy, radius_px). The union of overlapping circles
# produces an irregular outline that reads as a natural shape instead of
# a perfect disc.
PONDS_BLOBS = [
    # LOWER-LEFT pond — kidney shape (was 24-px circle)
    ([(430, 110, 22),
      (450, 100, 16),
      (415, 125, 14)], 0.65),
    # CENTER pond — small irregular blob (was 26-px circle)
    ([(256, 200, 22),
      (240, 215, 16),
      (272, 188, 17),
      (248, 188, 14)], 0.80),
    # LOWER-RIGHT pond — large organic blob (was 80-px circle)
    ([(410, 365, 62),
      (370, 340, 40),
      (450, 390, 38),
      (395, 415, 32),
      (440, 335, 30)], 1.80),
]

RIVER_HALFWIDTH = 6.0       # pixels — channel half-width
RIVER_PEAK = 0.65           # peak R value at river center
BEACH_INSET = 32            # pixels — how far inland the beach slope reaches
BEACH_PEAK = 1.00           # peak R value at very edge (full ocean)

# Secondary water features (the user-drawn marks):
#   - Small streams crossing parts of the island
#   - Coastal bays/inlets that punch the smooth perimeter inward
# Stamped with the same polyline machinery as MAIN_RIVER, just thinner
# (≈75% of river width) and slightly shallower so they read as smaller
# water features.
STREAM_HALFWIDTH = 4.5
STREAM_PEAK = 0.60

STREAMS = [
    # Upper-right diagonals — 2 parallel streams that flow INTO the big
    # blob pond. Endpoints extend past the pond outline (~410, 365) so
    # the stream visually merges with it instead of stopping short.
    [(180, 510), (250, 470), (320, 425), (380, 390), (410, 365)],
    [(220, 510), (290, 460), (350, 405), (400, 380), (425, 360)],

    # Lower-left squiggle — short curving stream coming IN from the
    # south-west ocean (starts past the image edge so it joins the sea).
    [(540,  80), (511,  90), (485, 110), (465, 140), (450, 165)],

    # Right-edge inlet — bay curving in from the east coast. First
    # waypoint sits past Y=511 so the inlet merges with the ocean.
    [(265, 540), (270, 511), (285, 490), (290, 470)],

    # Bottom-edge arcs ∩∩ — two coastal inlets. Endpoints extend past
    # X=511 on both sides so each inlet visibly enters and exits the
    # sea instead of fizzling at the coastline.
    [(540, 200), (511, 205), (495, 215), (490, 230), (495, 245), (511, 260), (540, 265)],
    [(540, 270), (511, 275), (495, 285), (490, 300), (495, 315), (511, 330), (540, 335)],
]


def _build_pixel_grid(w, h):
    """Return (px, py) coordinate grids in pixel space (h,w) shape."""
    ys, xs = np.meshgrid(np.arange(h, dtype=np.float32),
                         np.arange(w, dtype=np.float32),
                         indexing="ij")
    return xs, ys


def _segment_distance(px, py, x0, y0, x1, y1):
    """Vectorised pixel→line-segment distance."""
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return np.sqrt((px - x0) ** 2 + (py - y0) ** 2)
    t = ((px - x0) * dx + (py - y0) * dy) / length_sq
    t = np.clip(t, 0.0, 1.0)
    cx = x0 + t * dx
    cy = y0 + t * dy
    return np.sqrt((px - cx) ** 2 + (py - cy) ** 2)


def _stamp_polyline(r, px, py, waypoints, halfwidth, peak):
    """Add a soft channel along a polyline, taking max into r in-place."""
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        d = _segment_distance(px, py, x0, y0, x1, y1)
        # Linear falloff from peak at center to 0 at d=halfwidth (smoothed via sqrt)
        intensity = np.where(
            d < halfwidth,
            peak * np.sqrt(np.maximum(0.0, 1.0 - d / halfwidth)),
            0.0,
        )
        np.maximum(r, intensity, out=r)


def _stamp_circle(r, px, py, cx, cy, radius, peak):
    """Add a soft circular depression, taking max into r in-place."""
    d = np.sqrt((px - cx) ** 2 + (py - cy) ** 2)
    intensity = np.where(
        d < radius,
        peak * np.sqrt(np.maximum(0.0, 1.0 - d / radius)),
        0.0,
    )
    np.maximum(r, intensity, out=r)


def _stamp_beach(r, px, py, w, h, inset, peak):
    """Soft beach slope along the ROUNDED-RECTANGLE island border.

    Uses the standard rounded-box signed distance function so the
    perimeter is straight along the four sides but curves inward at
    each corner with radius ISLAND_CORNER_RADIUS. Pixels outside the
    rounded shape (the cut-off corner regions of the image) get full
    peak so they read as open ocean wrapping the island.
    """
    cx = (w - 1) * 0.5
    cy = (h - 1) * 0.5
    hx = (w - 1) * 0.5
    hy = (h - 1) * 0.5
    cr = float(ISLAND_CORNER_RADIUS)
    qx = np.abs(px - cx) - hx + cr
    qy = np.abs(py - cy) - hy + cr
    outside_d = np.sqrt(np.maximum(0.0, qx) ** 2 + np.maximum(0.0, qy) ** 2)
    inside_d = np.minimum(np.maximum(qx, qy), 0.0)
    sdf = outside_d + inside_d - cr
    # sdf >= 0      → outside rounded boundary (full ocean, clipped to 1)
    # sdf == -inset → far edge of beach (dry land begins)
    # sdf <= -inset → fully dry interior (clipped to 0)
    base = np.clip(1.0 + sdf / inset, 0.0, 1.0)
    intensity = peak * base ** 1.5
    np.maximum(r, intensity, out=r)


def _author_water_mask(w, h):
    px, py = _build_pixel_grid(w, h)
    r = np.zeros((h, w), dtype=np.float32)
    _stamp_beach(r, px, py, w, h, BEACH_INSET, BEACH_PEAK)
    _stamp_polyline(r, px, py, MAIN_RIVER, RIVER_HALFWIDTH, RIVER_PEAK)
    _stamp_polyline(r, px, py, SOUTH_BRANCH, RIVER_HALFWIDTH * 0.85, RIVER_PEAK)
    for cx, cy, radius, peak in PONDS_CIRCLES:
        _stamp_circle(r, px, py, cx, cy, radius, peak)
    for components, peak in PONDS_BLOBS:
        for cx, cy, radius in components:
            _stamp_circle(r, px, py, cx, cy, radius, peak)
    for stream in STREAMS:
        _stamp_polyline(r, px, py, stream, STREAM_HALFWIDTH, STREAM_PEAK)
    return r


def _hide_grass():
    ob = bpy.data.objects.get(GRASS_OBJECT)
    if ob is None:
        print(f"  [WARN] grass object {GRASS_OBJECT!r} not found — nothing to hide")
        return
    ob.hide_viewport = True
    ob.hide_render = True
    print(f"  hid {GRASS_OBJECT!r} (viewport + render) — no grass scatter shown")


def run():
    print("[02-ground-grass-base] author karan terrain shape, hide water-color + grass")
    img = bpy.data.images.get(IMAGE_NAME)
    if img is None:
        print(f"  [WARN] image {IMAGE_NAME!r} not found — skipping mask authoring")
        return
    w, h = img.size
    if w == 0 or h == 0:
        print(f"  [WARN] image {IMAGE_NAME!r} has zero size — skipping")
        return
    channels = img.channels
    pixels = np.asarray(img.pixels[:], dtype=np.float32).reshape((h, w, channels))

    new_r = _author_water_mask(w, h)
    pixels[:, :, 0] = new_r
    pixels[:, :, 1] = 0.0  # kill water-color G channel
    pixels[:, :, 2] = 0.0  # kill deep-water-color B channel
    if channels >= 4:
        pixels[:, :, 3] = 1.0  # solid alpha

    img.pixels.foreach_set(pixels.ravel())
    try:
        img.update()
    except Exception:
        pass

    coverage = float((new_r > 0.01).mean()) * 100.0
    deep_coverage = float((new_r > 0.3).mean()) * 100.0
    print(
        f"  {IMAGE_NAME}: R authored — coverage {coverage:.1f}%, "
        f"deep (>0.3) {deep_coverage:.1f}%. G+B zeroed (no water-color rendering)."
    )
    _hide_grass()

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
