"""Author karan's grass mask on terrainGrass.G and reveal the grass scatter.

Reference image (`karan/resources/reference/reference.png`) shows tan winding
trails carved through grass on a small island. Reproducing that look needs
three masks working together:

  - terrainWater.R   → water depressions               (authored by base.py)
  - terrainFurnitures.R → tile/path texture overlay     (authored by tiles.py)
  - terrainGrass.G   → grass blade scatter + ground tint (THIS file)

Bruno's `Geometry Nodes.001` reads terrainGrass.G as the per-blade SCALE on
the 192m × 192m point grid that drives `Plane.003`. G=1 → full-height blade,
G=0 → no visible blade. The terrain material's `Mix` chain ALSO tints the
ground green wherever G is high. So one mask drives both the geometry and
the colour.

Authoring rule for this file:
  grass_G = land_mask * (1 - path_mask)

  land_mask: 1 where terrainWater.R is below the shoreline threshold, 0 in
             water. Sharp shoreline fade matches the beach material edge so
             blades stop right at the waterline.
  path_mask: 1 inside a path stamp's core, fading to 0 at the path edge.
             Defined as a polyline network through the island that avoids
             every known water body in base.py.

Side effects:
  - Un-hides `Plane.003` (base.py hides it; this re-shows it now that we
    have an actual mask).
  - Saves the .blend so reopening Blender shows the result.

Per keep-everything policy: mutates terrainGrass pixels in memory + toggles
hide flags on Plane.003. Re-running blank-bruno.py zeros G again; re-running
base.py re-hides Plane.003.
"""
import bpy
import numpy as np

GRASS_IMAGE = "terrainGrass"
WATER_IMAGE = "terrainWater"
GRASS_OBJECT = "Plane.003"
BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"

# Shoreline band on terrainWater.R. Below LAND_START → fully grass; above
# LAND_END → fully water; smooth fade in between matches the beach material
# threshold so blades and waves meet at the same pixel.
LAND_START = 0.05
LAND_END = 0.18

# Path polylines — winding sandy trail network through the island.
#
# Coordinate space: 512×512 EXR pixels. With karan's scaled 125m world,
# 1 px ≈ 0.244 m.
#
# Image-to-screen axis mapping (terrain at rotation 0, Blender top-down view):
#   Image X axis (0→511) → screen TOP→BOTTOM
#   Image Y axis (0→511) → screen LEFT→RIGHT
#
# Designed to avoid every water body authored by base.py:
#   ponds at (~95,130) (~75,100) (~265,210) (~410,365) (~410,460)
#   main river + south-branch, stream inlets along the edges.
#
# Tile mask in 02-ground-grass-tiles.py reads from this same list so the
# tile texture lights up exactly where the grass drops out.
PATH_HALFWIDTH = 9.0   # ≈ 4.4 m wide main tile corridor
DETAIL_PATH_HALFWIDTH = 6.0  # sketched tile strokes stay readable
GRASS_CLEAR_HALFWIDTH = 16.0
DETAIL_GRASS_CLEAR_HALFWIDTH = 11.0
PATH_PEAK = 1.0        # full clearance at path centre
GRASS_STRENGTH = 0.52  # keep meadows lighter so the island is not a solid grass mat

PATH_POLYLINES = [
    # Long curving spine — enters from north (top), meanders down past the
    # central pond and big lagoon, exits south (bottom).
    [(330,  20), (320,  60), (310, 110), (300, 165), (305, 215), (320, 265),
     (320, 315), (310, 365), (305, 415), (300, 470), (305, 510)],

    # East-west connector — left coast into the middle of the island and out
    # past the right coast (slightly south of the centre pond).
    [( 30, 270), ( 80, 260), (145, 255), (205, 248), (255, 252), (305, 258),
     (355, 265), (415, 270), (480, 260)],

    # Central spawn approach — a dry stone arm with a small plaza just south
    # of the river crossing, away from ponds and shore water.
    [(205, 248), (220, 270), (235, 292), (250, 310), (265, 326)],

    # Northern loop branch — splits off the spine, swings up past the upper
    # ponds, rejoins near the centre.
    [(118, 180), (145, 198), (172, 225), (205, 248), (235, 270), (270, 285)],

    # Southern loop branch — splits off the spine, dips toward the big lagoon
    # but stays north of it, then curves back.
    [(330, 275), (355, 295), (382, 315), (410, 305), (432, 278)],

    # Lower-right connector — bridges spine to the bottom-right lobe of the
    # island between the lagoon and the lower-right pond.
    [(320, 315), (350, 345), (390, 372), (425, 405), (445, 440), (440, 468)],

    # Upper-left spur — short trail from the spine toward the lighthouse
    # corner (NW lobe), threading between the two upper ponds.
    [(190, 165), (170, 145), (140, 130), (105, 125)],

    # Bottom-left loop gives the large empty meadow another readable route
    # and connects the lagoon-side trail back into the main spine.
    [(295, 360), (260, 390), (220, 420), (180, 435), (135, 422), (105, 390)],

    # Right-side shoreline walk, kept inland from the water gate so it reads
    # like Bruno's curved secondary path instead of a straight border stripe.
    [(110, 360), (145, 385), (185, 410), (225, 430), (270, 438), (315, 430)],

    # Short upper-right connection around the large pond cluster.
    [(305, 165), (345, 155), (392, 150), (440, 140), (482, 128)],
]

DETAIL_PATH_POLYLINES = [
    # User-sketched upper-left crossings: several loose, hand-drawn strokes.
    [( 78,  38), ( 86,  82), ( 98, 135), (108, 195), (112, 270)],
    [(102,  28), (112,  86), (116, 150), (120, 220), (118, 305)],
    [(150,  38), (137,  75), (112, 112), ( 90, 152), ( 68, 200), ( 58, 245)],
    [(166,  42), (156,  92), (132, 132), (100, 170), ( 66, 210), ( 44, 255)],
    [( 55, 155), ( 75, 130), ( 95, 118), (120, 112), (150, 104), (178,  88)],

    # Short curved marks by the upper-right crossing in the screenshot.
    [(165, 250), (185, 275), (208, 292), (235, 305)],
    [(178, 278), (202, 302), (232, 316), (268, 320)],

    # Lower-left parallel strokes and a small fork into the existing trail.
    [(220,  42), (225,  90), (224, 142), (220, 182)],
    [(235,  35), (238,  82), (238, 135), (235, 178)],
    [(245, 145), (260, 160), (278, 175), (296, 194)],
    [(248, 150), (268, 160), (292, 170), (316, 185)],

    # C-shaped spawn-side curve around the small central pond, close to the
    # user's drawn loop but still clipped by the water gate.
    [(250, 205), (270, 194), (292, 202), (307, 225), (306, 254), (288, 276),
     (262, 278), (242, 264)],

    # Bottom-left long sweep near the lagoon.
    [(335, 155), (352, 182), (372, 212), (390, 242), (405, 280)],
    [(352, 150), (370, 178), (390, 205), (408, 225), (425, 255)],

    # Lower-right cluster: a denser cross/grid of paths like the hand sketch.
    [(290, 355), (318, 380), (350, 410), (390, 428), (440, 438)],
    [(322, 352), (325, 390), (332, 430), (344, 470)],
    [(298, 382), (340, 382), (386, 390), (432, 406), (470, 430)],
    [(318, 430), (355, 420), (392, 405), (432, 384), (472, 350)],
    [(290, 414), (330, 420), (372, 422), (416, 410), (455, 382)],
    [(305, 446), (345, 448), (390, 440), (432, 420), (470, 392)],
    [(285, 394), (330, 398), (378, 402), (430, 404), (482, 406)],
]

OPEN_AREAS = [
    # Spawn plaza: intentionally near the centre but not on the river or pond.
    {"center": (255, 305), "radius": (30, 24), "angle": -0.18, "wobble": 0.13},
    # Small pocket clearings break up the grass carpet and help paths feel
    # like places rather than lines.
    {"center": (118, 182), "radius": (18, 15), "angle": 0.35, "wobble": 0.16},
    {"center": (380, 306), "radius": (22, 15), "angle": 0.08, "wobble": 0.14},
    {"center": (210, 420), "radius": (24, 16), "angle": -0.42, "wobble": 0.12},
    {"center": (356, 410), "radius": (22, 16), "angle": 0.22, "wobble": 0.14},
]

SPARSE_GRASS_AREAS = [
    {"center": (160, 360), "radius": (34, 22), "angle": 0.10, "strength": 0.64},
    {"center": (250, 360), "radius": (30, 24), "angle": -0.36, "strength": 0.60},
    {"center": (365, 250), "radius": (36, 24), "angle": 0.22, "strength": 0.62},
    {"center": (430, 175), "radius": (34, 20), "angle": -0.18, "strength": 0.58},
]


def _build_pixel_grid(w, h):
    ys, xs = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    return xs.astype(np.float32), ys.astype(np.float32)


def _segment_distance(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-6:
        return np.sqrt((px - x0) ** 2 + (py - y0) ** 2)
    t = np.clip(((px - x0) * dx + (py - y0) * dy) / length_sq, 0.0, 1.0)
    cx = x0 + t * dx
    cy = y0 + t * dy
    return np.sqrt((px - cx) ** 2 + (py - cy) ** 2)


def _stamp_polyline(mask, px, py, waypoints, halfwidth, peak):
    """Sqrt-falloff polyline stamp, max-merged into mask."""
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        d = _segment_distance(px, py, x0, y0, x1, y1)
        intensity = np.where(
            d < halfwidth,
            peak * np.sqrt(np.maximum(0.0, 1.0 - d / halfwidth)),
            0.0,
        )
        np.maximum(mask, intensity, out=mask)


def _stamp_solid_polyline(mask, px, py, waypoints, halfwidth, edge_width, peak):
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        d = _segment_distance(px, py, x0, y0, x1, y1)
        core = np.where(d <= halfwidth - edge_width, peak, 0.0)
        edge = np.where(
            (d > halfwidth - edge_width) & (d < halfwidth),
            peak * np.clip((halfwidth - d) / edge_width, 0.0, 1.0),
            0.0,
        )
        np.maximum(mask, np.maximum(core, edge), out=mask)


def _stamp_hard_polyline(mask, px, py, waypoints, halfwidth):
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        d = _segment_distance(px, py, x0, y0, x1, y1)
        intensity = np.where(d < halfwidth, 1.0, 0.0)
        np.maximum(mask, intensity, out=mask)


def _stamp_open_area(mask, px, py, center, radius, angle, wobble):
    cx, cy = center
    rx, ry = radius
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    dx = px - cx
    dy = py - cy
    local_x = dx * cos_a + dy * sin_a
    local_y = -dx * sin_a + dy * cos_a
    theta = np.arctan2(local_y / max(ry, 1e-6), local_x / max(rx, 1e-6))
    edge = 1.0 + wobble * np.sin(theta * 3.0 + 0.7) + wobble * 0.55 * np.cos(theta * 5.0 - 1.2)
    d = np.sqrt((local_x / (rx * edge)) ** 2 + (local_y / (ry * edge)) ** 2)
    intensity = np.clip((1.18 - d) / 0.28, 0.0, 1.0)
    np.maximum(mask, intensity, out=mask)


def _stamp_sparse_grass(mask, px, py, area):
    cx, cy = area["center"]
    rx, ry = area["radius"]
    angle = area["angle"]
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    dx = px - cx
    dy = py - cy
    local_x = dx * cos_a + dy * sin_a
    local_y = -dx * sin_a + dy * cos_a
    d = np.sqrt((local_x / rx) ** 2 + (local_y / ry) ** 2)
    intensity = np.clip((1.0 - d) / 0.35, 0.0, 1.0) * area["strength"]
    np.maximum(mask, intensity, out=mask)


def build_path_mask(w, h):
    path = np.zeros((h, w), dtype=np.float32)
    px, py = _build_pixel_grid(w, h)
    for poly in PATH_POLYLINES:
        _stamp_solid_polyline(path, px, py, poly, PATH_HALFWIDTH, 2.0, PATH_PEAK)
    for poly in DETAIL_PATH_POLYLINES:
        _stamp_solid_polyline(path, px, py, poly, DETAIL_PATH_HALFWIDTH, 1.4, PATH_PEAK)
    for area in OPEN_AREAS:
        _stamp_open_area(path, px, py, area["center"], area["radius"], area["angle"], area["wobble"])
    return np.clip(path, 0.0, 1.0)


def build_grass_clear_mask(w, h):
    clear = np.zeros((h, w), dtype=np.float32)
    px, py = _build_pixel_grid(w, h)
    for poly in PATH_POLYLINES:
        _stamp_hard_polyline(clear, px, py, poly, GRASS_CLEAR_HALFWIDTH)
    for poly in DETAIL_PATH_POLYLINES:
        _stamp_hard_polyline(clear, px, py, poly, DETAIL_GRASS_CLEAR_HALFWIDTH)
    for area in OPEN_AREAS:
        expanded = (area["radius"][0] + 4.0, area["radius"][1] + 4.0)
        _stamp_open_area(clear, px, py, area["center"], expanded, area["angle"], area["wobble"])
    return np.where(clear > 0.02, 1.0, 0.0).astype(np.float32)


def build_sparse_grass_mask(w, h):
    sparse = np.zeros((h, w), dtype=np.float32)
    px, py = _build_pixel_grid(w, h)
    for area in SPARSE_GRASS_AREAS:
        _stamp_sparse_grass(sparse, px, py, area)
    return np.clip(sparse, 0.0, 1.0)


def _author_grass_mask(w, h, water_r):
    land = 1.0 - np.clip((water_r - LAND_START) / (LAND_END - LAND_START), 0.0, 1.0)

    clear = build_grass_clear_mask(w, h)
    sparse = build_sparse_grass_mask(w, h)
    meadow = np.maximum(GRASS_STRENGTH, sparse)

    return land * meadow * (1.0 - clear)


def _show_grass():
    ob = bpy.data.objects.get(GRASS_OBJECT)
    if ob is None:
        print(f"  [WARN] grass object {GRASS_OBJECT!r} not found — cannot un-hide")
        return
    ob.hide_viewport = False
    ob.hide_render = False
    print(f"  {GRASS_OBJECT}: hide flags cleared (grass blades visible)")


def run():
    print("[02-ground-grass-grass] author terrainGrass.G + reveal scatter")
    img_g = bpy.data.images.get(GRASS_IMAGE)
    img_w = bpy.data.images.get(WATER_IMAGE)
    if img_g is None:
        print(f"  [WARN] image {GRASS_IMAGE!r} not found — skipping")
        return
    if img_w is None:
        print(f"  [WARN] image {WATER_IMAGE!r} not found — cannot derive land mask")
        return

    w, h = img_g.size
    if w == 0 or h == 0:
        print(f"  [WARN] {GRASS_IMAGE!r} has zero size — skipping")
        return
    if (img_w.size[0], img_w.size[1]) != (w, h):
        print(f"  [WARN] image sizes differ ({img_w.size} vs {img_g.size}) — using grass size")

    channels_g = img_g.channels
    channels_w = img_w.channels

    water_pixels = np.asarray(img_w.pixels[:], dtype=np.float32).reshape((h, w, channels_w))
    water_r = water_pixels[:, :, 0]

    grass_g = _author_grass_mask(w, h, water_r)

    grass_pixels = np.asarray(img_g.pixels[:], dtype=np.float32).reshape((h, w, channels_g))
    grass_pixels[:, :, 1] = grass_g  # G — drives scatter scale + ground tint
    if channels_g >= 4:
        grass_pixels[:, :, 3] = 1.0

    img_g.pixels.foreach_set(grass_pixels.ravel())
    try:
        img_g.update()
    except Exception:
        pass

    coverage = float((grass_g > 0.5).mean()) * 100.0
    full = float((grass_g > 0.95).mean()) * 100.0
    path_pct = float((grass_g < 0.05).mean()) * 100.0
    print(
        f"  {GRASS_IMAGE}.G authored — grass coverage {coverage:.1f}% "
        f"(full-strength {full:.1f}%, no-grass {path_pct:.1f}% covers water+paths)."
    )

    _show_grass()

    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
