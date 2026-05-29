"""Blank Bruno's pre-existing terrain markings that bleed into karan's layout.

Bruno's terrain material composes the ground from several baked masks:
  - terrainGrass.G  → drives Mix + Mix.003 toward dark-green grass color
  - terrainFurniture.R → drives Mix.004 toward slabs/path texture, which
                          OVERRIDES the water mix because it comes later
                          in the shader chain
  - RGB.001 (material node default) = (1.0, 0.40, 0.08) → orange sand,
                          shown wherever terrainGrass.G is 0

Bruno authored those masks for HIS world layout. They don't match karan's
depression layout (rivers + ponds + beach), so when we run, we see:
  - random green patches across the island (from Bruno's terrainGrass)
  - sand-colored ribbons CUTTING through our ponds and rivers (from Bruno's
    terrainFurniture — paths take priority over water in the shader)
  - bright orange base color (from RGB.001 default)

This script blanks all three so karan sees a clean view of:
  - neutral beige terrain
  - teal/navy water exactly in our authored depressions
  - nothing else

Per the keep-everything policy:
  - We MUTATE pixels of terrainGrass + terrainFurniture in memory (datablocks
    kept; reload from disk restores Bruno's masks).
  - We CHANGE the RGB.001 node's default_value in the terrain material
    (node kept; can be set back to (1.0, 0.40, 0.08) any time).
Nothing is removed or unlinked.

Run AFTER `02-ground-grass-base.py` and the Bruno step files; can run before
or after `02-ground-grass-water.py`. Re-running Bruno's step files reloads
the original images and would undo this.
"""
import bpy
import numpy as np

BLEND_PATH = "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/world-v3-karan.blend"
GRASS_IMAGE = "terrainGrass"
# Bruno's 002_images.py renames the source file `terrainFurniture.exr` to
# image datablock `terrainFurnitures` (with an 's') on load. Use the
# datablock name, not the file name.
FURNITURE_IMAGE = "terrainFurnitures"
TERRAIN_MATERIAL = "terrain"

# Color overrides for the terrain material's RGB color nodes. The grass pair
# follows the darker olive-green look from the water-option mockup, while the
# water pair keeps Bruno's depth-falloff behavior with Karan's Option B palette.
#   RGB     = main grass tint (Bruno: dark yellow-green 0.34,0.43,0.03)
#   RGB.001 = base ground   (Bruno: warm sand-orange 1.00,0.40,0.08)
#   RGB.002 = shallow water (Bruno: dark muddy teal  0.10,0.54,0.49)
#   RGB.003 = deep water    (Bruno: near-black navy  0.01,0.04,0.11)
#   RGB.004 = dark grass overlay (Bruno: deep green 0.09,0.16,0.06)
COLOR_OVERRIDES = {
    "RGB": (0.31, 0.39, 0.16, 1.0),       # darker olive main grass
    "RGB.001": (0.50, 0.54, 0.05, 1.0),   # mockup-like olive base
    "RGB.002": (0.28, 0.68, 0.72, 1.0),   # shallow blue-teal edge
    "RGB.003": (0.015, 0.12, 0.25, 1.0),  # deep stylized navy center
    "RGB.004": (0.07, 0.14, 0.06, 1.0),   # deeper grass shadow
}


def _zero_image(name):
    img = bpy.data.images.get(name)
    if img is None:
        print(f"  [WARN] image {name!r} not found — skipping")
        return
    w, h = img.size
    if w == 0 or h == 0:
        print(f"  [WARN] image {name!r} has zero size — skipping")
        return
    channels = img.channels
    flat = np.zeros(w * h * channels, dtype=np.float32)
    if channels >= 4:
        # Keep alpha solid so the texture sampler returns 0,0,0 instead of
        # transparent-and-undefined.
        flat.reshape((h, w, channels))[:, :, 3] = 1.0
    img.pixels.foreach_set(flat)
    try:
        img.update()
    except Exception:
        pass
    print(f"  {name}: pixels zeroed (was painted with Bruno's layout)")


def _override_colors():
    mat = bpy.data.materials.get(TERRAIN_MATERIAL)
    if mat is None or mat.node_tree is None:
        print(f"  [WARN] material {TERRAIN_MATERIAL!r} not found — skipping")
        return
    for node_name, new_value in COLOR_OVERRIDES.items():
        node = mat.node_tree.nodes.get(node_name)
        if node is None:
            print(f"  [WARN] node {node_name!r} not found in {TERRAIN_MATERIAL!r}")
            continue
        old = tuple(node.outputs[0].default_value)
        node.outputs[0].default_value = new_value
        print(
            f"  {TERRAIN_MATERIAL}.{node_name}: "
            f"({old[0]:.2f},{old[1]:.2f},{old[2]:.2f}) → "
            f"({new_value[0]:.2f},{new_value[1]:.2f},{new_value[2]:.2f})"
        )


def run():
    print("[02-ground-grass-blank-bruno] clear Bruno's grass/path/orange so karan layer is clean")
    _zero_image(GRASS_IMAGE)
    _zero_image(FURNITURE_IMAGE)
    _override_colors()
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
