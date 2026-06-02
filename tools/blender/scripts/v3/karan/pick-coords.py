"""Print the 3D cursor's world coords — use to find an ANCHOR for a section.

Workflow:
  1. In the viewport, Shift+Right-Click on the ground where you want the spot.
     (That moves Blender's 3D cursor there.)
  2. Run this script (Python Console:
       exec(open('.../karan/pick-coords.py').read())
     or paste it in).
  3. Copy the printed ANCHOR tuple into your section script.

Blender is Z-up: the ground plane is X (east/west) and Y (north/south),
which is exactly what `misc_common` ANCHOR=(x, y) expects. Z is the height.
"""
import bpy

c = bpy.context.scene.cursor.location
x, y, z = c.x, c.y, c.z

print("-" * 48)
print(f"  3D cursor world position:")
print(f"    x = {x:.2f}   y = {y:.2f}   z(height) = {z:.2f}")
print(f"  ANCHOR = ({x:.1f}, {y:.1f})")
print("-" * 48)
