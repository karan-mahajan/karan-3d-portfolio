"""Shrink Bruno's 192m terrain + grass footprint to ~125m for karan.

Bruno authors his world at 192x192m. Karan's walkable zone is ~60m
radius, so 125m diameter gives a comfortable visual buffer past the
playable area without the huge backdrop Bruno needed for racing+bowling.

X/Y scale = 125/192 ≈ 0.651. Z left at 1.0 so the GeometryNodes
displacement amplitude (pond depths, hill heights) is preserved.

Side effect on grass: the scatter group builds its 192m grid in the
object's local space, so scaling the object compresses ~78k blades into
a 125m area — ~2.36x denser. That's intentional; karan wants a denser
field anyway (per Part 3 brainstorm).

Per the keep-everything policy: this only mutates the OBJECT transform.
Mesh datablocks (Plane.134, Plane.012) and the GeometryNodes groups
(Geometry Nodes, Geometry Nodes.001) are untouched.
"""
import bpy

SCALE_XY = 125.0 / 192.0  # ≈ 0.6510


def _set_xy_scale(name, factor):
    ob = bpy.data.objects.get(name)
    if ob is None:
        print(f"  [WARN] object {name!r} not found — skipping scale")
        return
    ob.scale = (factor, factor, 1.0)
    print(f"  {name}: scale → ({factor:.4f}, {factor:.4f}, 1.0)")


def run():
    print("[02-ground-grass-scale] shrink terrain + grass footprint to ~125m")
    _set_xy_scale("terrain", SCALE_XY)
    _set_xy_scale("Plane.003", SCALE_XY)
    print(f"  done (XY scale = {SCALE_XY:.4f}; Z preserved)")


if __name__ == "__main__":
    run()
