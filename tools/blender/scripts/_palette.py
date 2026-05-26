"""
Locked 25-color palette for the v2 alpine misty highlands world.

Single source of truth — Phase 1 reads this to bake the 128x4 palette PNG,
later phases read PALETTE_CELL_INDEX + cell_uv() to pick UVs that land in
the correct cell. Hex values mirror spec section 2 exactly; do not adjust
without updating the spec.

Pure Python (no bpy) so it can be imported and unit-checked outside Blender.
"""


PALETTE_COLORS = {
    # Sky & atmosphere (5)
    "sky_high":            "#c6c3bc",
    "sun_rim_warm":        "#d5c4ad",
    "mist_horizon":        "#e0d4c0",
    "overcast_mid":        "#aab2b5",
    "dark_low_fog":        "#7a8079",
    # Rock & mountain (5)
    "rock_mid":            "#5d6770",
    "distant_peak":        "#7e898d",
    "dark_rock_shadow":    "#4a525c",
    "fog_faded_distant":   "#9ea7ab",
    "deep_crevice":        "#2c3540",
    # Snow & ice (3)
    "sunlit_snow":         "#fff5dc",
    "shadowed_snow":       "#d8c8d6",
    "old_snow":            "#c8c8d4",
    # Pine & foliage (4)
    "pine_canopy":         "#3a5536",
    "sunlit_pine":         "#5a7253",
    "deep_shade":          "#283933",
    "meadow_grass":        "#94a978",
    # Water (3)
    "glacial_river":       "#9ec5d6",
    "deeper_water":        "#5d8094",
    "reflective_surface":  "#a8b8c0",
    # Warm accents & earth (5)
    "sun_glow":            "#f4d6b0",
    "lantern_warm":        "#ffc46d",
    "wood_lantern_body":   "#b87850",
    "dirt_path":           "#6e6256",
    "sand_gravel":         "#9a8a72",
}


# Index of each color in the palette PNG. Order matches PALETTE_COLORS
# insertion order (Python 3.7+ preserves dict order). 25 entries total;
# cells 0..24 occupy x = 0..124 in the 128px-wide image, last 3 px unused.
PALETTE_CELL_INDEX = {key: i for i, key in enumerate(PALETTE_COLORS)}


_IMAGE_WIDTH = 128
_IMAGE_HEIGHT = 4
_CELL_WIDTH_PX = 5  # 25 cells x 5 px = 125 px; 3 px slack on the right


def palette_image_size():
    """Return the (width, height) in pixels of the palette PNG."""
    return (_IMAGE_WIDTH, _IMAGE_HEIGHT)


def cell_uv(index):
    """
    Return the (u, v) UV coords of the *center* of cell `index` in the
    palette image. Each cell is 5px wide; center sits at px 2.5 from cell
    start. v is always 0.5 (image is only 4 px tall and one color fills it).
    """
    if index < 0 or index >= len(PALETTE_COLORS):
        raise ValueError(
            f"cell index {index} out of range 0..{len(PALETTE_COLORS) - 1}"
        )
    u = (_CELL_WIDTH_PX * index + _CELL_WIDTH_PX / 2.0) / _IMAGE_WIDTH
    v = 0.5
    return (u, v)


def hex_to_rgb_floats(hex_str):
    """
    Convert "#rrggbb" to (r, g, b) sRGB floats in 0..1. Helper for Phase 1
    when baking the palette PNG. Linear conversion is the caller's problem.
    """
    s = hex_str.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"expected #rrggbb, got {hex_str!r}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return (r, g, b)
