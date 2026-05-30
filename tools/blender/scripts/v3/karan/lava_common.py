"""Single source of truth for the lava-pool basin geometry.

The lava pool is carved into the terrain the SAME way the water ponds are — by
stamping the `terrainWater.R` height mask at terrain-build time (section 02), so
the Geometry-Nodes terrain genuinely sinks (R x -1.5 m) exactly like water.
Live pixel edits at section-14 time do NOT re-trigger GN, so the DIP must be
authored here, in the build.

Used by:
  - 02-ground-grass-base.py  : carves R (the dip) via `basin_intensity`
  - 02-ground-grass-water.py : zeroes B inside the basin (no teal water tint)
  - 02-ground-grass-grass.py : zeroes G inside the basin (no grass blades)
  - 14-fx-lava.py            : reads CENTER/RADIUS to drop the lava surface +
                               crust stones into the pre-carved dip

Named WITHOUT a section prefix so no run-all glob ever tries to `.run()` it.
"""
import numpy as np

# World (Blender X, Y) centre of the pool — the 3D-cursor spot in the open
# meadow behind the Projects hut. THE one knob for where the pool lives.
CENTER = (34.18, -46.05)
RADIUS_M = 3.0               # pool radius in metres (~6 m across)
PEAK_R = 0.42                # R stamp peak -> ~0.63 m terrain dip (shallower than ponds' ~1 m)

TERRAIN_WORLD_SIZE = 125.0   # terrainWater 512 px spans the 125 m terrain UV


def _fields(w, h):
    """Return (dist_px, wobble_radius_px) arrays of shape (h, w) for the basin,
    in terrain EXR pixel space. Image rows map to world Y/Z; columns map to
    world X. This is the same orientation the terrain UVs use in Blender."""
    ys, xs = np.meshgrid(np.arange(h, dtype=np.float32),
                         np.arange(w, dtype=np.float32), indexing="ij")
    row_c = (CENTER[1] / TERRAIN_WORLD_SIZE + 0.5) * (h - 1)
    col_c = (CENTER[0] / TERRAIN_WORLD_SIZE + 0.5) * (w - 1)
    radius_px = RADIUS_M * (w / TERRAIN_WORLD_SIZE)
    dr = ys - row_c
    dc = xs - col_c
    dist = np.sqrt(dr * dr + dc * dc)
    ang = np.arctan2(dr, dc)
    # Lopsided, non-circular rim (matches the organic karan ponds).
    wob = radius_px * (1.0 + 0.16 * np.sin(3.0 * ang + 0.7)
                       + 0.09 * np.sin(5.0 * ang - 1.1))
    return dist, wob


def basin_intensity(w, h):
    """(h, w) R-displacement intensity for the basin — smoothstep falloff, full
    depth at centre to 0 at the rim. `np.maximum` this into terrainWater.R."""
    dist, wob = _fields(w, h)
    t = np.clip(dist / wob, 0.0, 1.0)
    falloff = 1.0 - (t * t * (3.0 - 2.0 * t))
    return (PEAK_R * falloff).astype(np.float32)


def basin_inside(w, h):
    """(h, w) boolean mask of the basin footprint — zero terrainWater.B here so
    the terrain shader paints no teal/navy water inside the lava pool."""
    dist, wob = _fields(w, h)
    return dist < (wob + 1.0)
