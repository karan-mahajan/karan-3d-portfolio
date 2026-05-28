"""Author karan's base terrain shape — depressions only, no water/grass rendering.

Replaces Bruno's `terrainWater.exr` R channel with a hand-coded layout
matching karan's design intent: a meandering river through the island center,
thin water fingers, organic ponds, and a Bruno-like uneven coast with bays.

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

# Image-to-screen axis mapping (terrain at rotation 0, Blender top-down view):
#   Image X axis (0→511) → screen TOP→BOTTOM
#   Image Y axis (0→511) → screen LEFT→RIGHT
# So image pixel (0,0) renders at screen TOP-LEFT; (511,511) at BOTTOM-RIGHT.
# Use that when tuning waypoints from a screenshot.

ORGANIC_PONDS = [
    # Top-left user mark: a non-circular lopsided pool with a small inward bite.
    ([
        (66, 100), (76, 78), (100, 60), (131, 58), (154, 71),
        (170, 98), (166, 126), (145, 151), (113, 161), (82, 151),
        (60, 130),
    ], 14.0, 0.78),
    # Small lower-left curl pool.
    ([
        (430, 92), (450, 84), (468, 93), (475, 115), (462, 135),
        (438, 142), (416, 130), (409, 108),
    ], 12.0, 0.68),
    # Center small pond, more leaf-shaped than circular.
    ([
        (250, 198), (267, 184), (286, 190), (297, 210), (287, 230),
        (263, 238), (242, 228), (235, 211),
    ], 10.0, 0.82),
    # Large lower-right lagoon: one coherent irregular shape, not merged discs.
    ([
        (352, 338), (372, 311), (404, 305), (430, 320), (456, 318),
        (484, 340), (492, 376), (474, 412), (439, 428), (404, 421),
        (372, 434), (342, 414), (330, 379),
    ], 24.0, 1.0),
    # Lower-right small puddle cluster converted into a single organic splash.
    ([
        (390, 438), (405, 424), (427, 428), (444, 446), (439, 468),
        (416, 481), (392, 471), (381, 452),
    ], 12.0, 0.74),
]

RIVER_HALFWIDTH = 7.0       # pixels — channel half-width
RIVER_PEAK = 0.65           # peak R value at river center
BEACH_INSET = 34            # pixels — how far inland the beach slope reaches
BEACH_PEAK = 1.00           # peak R value at very edge (full ocean)

# Secondary water features (the user-drawn marks):
#   - Small streams crossing parts of the island
#   - Coastal bays/inlets that punch the smooth perimeter inward
# Stamped with the same polyline machinery as MAIN_RIVER, just thinner
# (≈75% of river width) and slightly shallower so they read as smaller
# water features.
STREAM_HALFWIDTH = 5.0
STREAM_PEAK = 0.60

STREAMS = [
    # Upper-right diagonals — 2 parallel streams that flow INTO the big
    # blob pond. Endpoints extend past the pond outline (~410, 365) so
    # the stream visually merges with it instead of stopping short.
    [(176, 535), (228, 493), (280, 455), (333, 411), (372, 384), (400, 364)],
    [(216, 535), (273, 491), (324, 443), (374, 398), (421, 362)],

    # Lower-left squiggle — short curving stream coming IN from the
    # south-west ocean (starts past the image edge so it joins the sea).
    [(540,  72), (512,  83), (487, 105), (463, 137), (441, 171)],

    # Right-edge inlet — bay curving in from the east coast. First
    # waypoint sits past Y=511 so the inlet merges with the ocean.
    [(252, 540), (259, 512), (277, 490), (294, 468)],

    # Bottom-edge arcs ∩∩ — two coastal inlets. Endpoints extend past
    # X=511 on both sides so each inlet visibly enters and exits the
    # sea instead of fizzling at the coastline.
    [(540, 196), (512, 202), (492, 216), (483, 236), (491, 255), (512, 268), (540, 272)],
    [(540, 280), (512, 286), (493, 301), (487, 321), (498, 340), (522, 350), (548, 352)],
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


def _point_in_polygon(px, py, points):
    """Vectorised even-odd fill test for closed water loops."""
    inside = np.zeros(px.shape, dtype=bool)
    xj, yj = points[-1]
    for xi, yi in points:
        crosses = ((yi > py) != (yj > py)) & (
            px < (xj - xi) * (py - yi) / ((yj - yi) + 1e-6) + xi
        )
        inside ^= crosses
        xj, yj = xi, yi
    return inside


def _distance_to_polyline(px, py, points, closed=False):
    """Distance to a point loop/polyline."""
    d = np.full(px.shape, np.inf, dtype=np.float32)
    pairs = list(zip(points, points[1:]))
    if closed:
        pairs.append((points[-1], points[0]))
    for (x0, y0), (x1, y1) in pairs:
        d = np.minimum(d, _segment_distance(px, py, x0, y0, x1, y1))
    return d


def _stamp_blob(r, px, py, points, feather, peak):
    """Add a filled organic water body with a soft beach-to-depth ramp."""
    inside = _point_in_polygon(px, py, points)
    edge_d = _distance_to_polyline(px, py, points, closed=True)
    t = np.clip(edge_d / feather, 0.0, 1.0)
    smooth = t * t * (3.0 - 2.0 * t)
    intensity = np.where(inside, peak * smooth, 0.0)
    np.maximum(r, intensity, out=r)


def _stamp_beach(r, px, py, w, h, inset, peak):
    """Soft beach slope along an uneven hand-authored island silhouette."""
    yy = py / max(h - 1, 1)
    xx = px / max(w - 1, 1)

    def g(v, center, width, amp):
        return amp * np.exp(-((v - center) / width) ** 2)

    left = (
        17.0
        + 5.0 * np.sin(yy * np.pi * 5.0 + 0.5)
        + g(yy, 0.13, 0.05, 12.0)
        + g(yy, 0.47, 0.10, 8.0)
        - g(yy, 0.78, 0.06, 10.0)
    )
    right = (
        (w - 1) - 18.0
        - 6.0 * np.sin(yy * np.pi * 4.5 + 1.1)
        - g(yy, 0.25, 0.07, 26.0)
        - g(yy, 0.55, 0.10, 12.0)
        + g(yy, 0.74, 0.05, 9.0)
    )
    top = (
        18.0
        + 5.0 * np.sin(xx * np.pi * 4.0 + 2.0)
        + g(xx, 0.17, 0.06, 10.0)
        + g(xx, 0.48, 0.04, 20.0)
        - g(xx, 0.78, 0.08, 8.0)
    )
    bottom = (
        (h - 1) - 18.0
        - 5.0 * np.sin(xx * np.pi * 5.0 + 0.6)
        - g(xx, 0.18, 0.08, 22.0)
        - g(xx, 0.46, 0.06, 18.0)
        + g(xx, 0.68, 0.07, 8.0)
    )

    inside_d = np.minimum.reduce([px - left, right - px, py - top, bottom - py])
    base = np.clip(1.0 - inside_d / inset, 0.0, 1.0)
    intensity = peak * base ** 1.5
    np.maximum(r, intensity, out=r)


def _author_water_mask(w, h):
    px, py = _build_pixel_grid(w, h)
    r = np.zeros((h, w), dtype=np.float32)
    _stamp_beach(r, px, py, w, h, BEACH_INSET, BEACH_PEAK)
    _stamp_polyline(r, px, py, MAIN_RIVER, RIVER_HALFWIDTH, RIVER_PEAK)
    _stamp_polyline(r, px, py, SOUTH_BRANCH, RIVER_HALFWIDTH * 0.85, RIVER_PEAK)
    for points, feather, peak in ORGANIC_PONDS:
        _stamp_blob(r, px, py, points, feather, peak)
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
