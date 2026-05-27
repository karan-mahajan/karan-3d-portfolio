"""
Pull mountains + lighthouse close to the new shore and SNAP the ocean plane
to an absolute size that just covers the terrain. Runs after resize-world.py.

# Why this exists

After resize-world.py shrank the island to r≈60m walkable (terrain ±96.85m),
the backdrop elements (mountains at y≈180+, lighthouse at x=-130, ocean
plane potentially extended) look disproportionately far from the compact
island. Top-orthographic shows a small island floating in a vast sea.

This script tightens everything to a predictable absolute scale:

  - Mountains: location XY scaled by MOUNTAIN_LOC_SCALE (default 0.7).
    Proportional pull — bands stay layered relative to each other.
  - Lighthouse: translated so its EAST edge sits LIGHTHOUSE_OFFSHORE_M past
    the new shore (default 10m past x=-96.85, so east edge at x=-106.85).
  - Ocean plane: SNAPPED to ±OCEAN_TARGET_HALF_EXTENT (default ±105m).
    Each vertex is reassigned by sign — this is idempotent and works no
    matter what the ocean was before (200×200 original or 500×500 extended).

# How to run

Dry-run (default — prints the plan, does NOT mutate):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/tighten-backdrop.py

Apply (mutates + saves; writes a .pre-tighten-*.bak alongside):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/tighten-backdrop.py -- --apply
"""

import sys
import time

import bpy


# ----------------------------------------------------------------------------
# Config — tune these and re-run if the dry-run doesn't match the look you want
# ----------------------------------------------------------------------------


# Mountain location-XY scale. 0.7 pulls them in ~30% — bands keep their
# layered offset relative to each other. Try 0.6 for more aggressive pull,
# 0.8 for gentler.
MOUNTAIN_LOC_SCALE = 0.7


# Distance from the new shore edge to the lighthouse islet's EAST edge.
LIGHTHOUSE_OFFSHORE_M = 10.0


# Post-resize terrain west corner X. Reference for lighthouse + ocean
# coverage check. (Terrain is centred symmetric around 0, ±96.85.)
NEW_SHORE_EDGE_X = -96.85


# Distance from islet_rock object origin to its east bbox edge.
LIGHTHOUSE_ISLET_EAST_OFFSET = 4.0


# Ocean plane absolute half-extent. ±105 covers the terrain (±96.85) with
# a thin 8m margin past shore — feels like a real coastal sea rather than
# an endless ocean.
OCEAN_TARGET_HALF_EXTENT = 105.0


# ----------------------------------------------------------------------------
# Object lists
# ----------------------------------------------------------------------------


MOUNTAIN_OBJS = [
    "mountain_band_far_snow",
    "mountain_band_mid_peaks",
    "mountain_band_front_ridge",
    "mountain_band_foothills_east",
]


# Lighthouse cluster — all translated by the same delta to preserve their
# relative geometry. The beam empty must move with the lighthouse so its
# parented lighthouse_beam stays attached.
LIGHTHOUSE_OBJS = [
    "islet_rock",
    "lighthouse_body",
    "lighthouse_cupola",
    "lighthouse_lamp_emissive",
    "refLighthouseBeamPivot",
]

LIGHTHOUSE_REFERENCE_OBJ = "islet_rock"

OCEAN_OBJ_NAME = "ocean_plane"
SCENE_STAMP_KEY = "backdrop_tighten_applied"


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def _cli_apply():
    if "--" not in sys.argv:
        return False
    return "--apply" in sys.argv[sys.argv.index("--") + 1:]


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main():
    APPLY = _cli_apply()
    print("=" * 72)
    print(
        f"tighten-backdrop.py  mountain_scale={MOUNTAIN_LOC_SCALE}  "
        f"lighthouse_offshore={LIGHTHOUSE_OFFSHORE_M}m  "
        f"ocean_target=±{OCEAN_TARGET_HALF_EXTENT}m  "
        f"mode={'APPLY' if APPLY else 'DRY-RUN'}"
    )
    print("=" * 72)

    scene = bpy.context.scene
    prior = scene.get(SCENE_STAMP_KEY)
    if prior is not None and APPLY:
        print(f"\nABORT: scene already has {SCENE_STAMP_KEY}={prior}. Restore .bak to re-run.")
        raise SystemExit(1)
    if prior is not None:
        print(f"\n[note] scene has {SCENE_STAMP_KEY}={prior} (prior tighten detected).\n")

    # === MOUNTAINS ===
    print(f"\n=== Mountains (location-XY scale by {MOUNTAIN_LOC_SCALE}) ===")
    mountain_changes = []
    for name in MOUNTAIN_OBJS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            print(f"  MISSING: {name}")
            continue
        before = (obj.location.x, obj.location.y, obj.location.z)
        after = (
            obj.location.x * MOUNTAIN_LOC_SCALE,
            obj.location.y * MOUNTAIN_LOC_SCALE,
            obj.location.z,
        )
        mountain_changes.append((obj, before, after))
        print(f"  {name}: ({before[0]:7.2f}, {before[1]:7.2f}) → ({after[0]:7.2f}, {after[1]:7.2f})")

    # === LIGHTHOUSE ===
    print(f"\n=== Lighthouse (uniform translation) ===")
    ref_obj = bpy.data.objects.get(LIGHTHOUSE_REFERENCE_OBJ)
    if ref_obj is None:
        print(f"  ERROR: reference object {LIGHTHOUSE_REFERENCE_OBJ!r} not found")
        raise SystemExit(1)
    target_islet_x = NEW_SHORE_EDGE_X - LIGHTHOUSE_OFFSHORE_M - LIGHTHOUSE_ISLET_EAST_OFFSET
    delta_x = target_islet_x - ref_obj.location.x
    delta_y = ref_obj.location.y * MOUNTAIN_LOC_SCALE - ref_obj.location.y
    target_east_edge = NEW_SHORE_EDGE_X - LIGHTHOUSE_OFFSHORE_M
    print(f"  reference {LIGHTHOUSE_REFERENCE_OBJ} at ({ref_obj.location.x:.2f}, {ref_obj.location.y:.2f})")
    print(f"  target islet east edge: x = {target_east_edge:.2f}  "
          f"(= shore {NEW_SHORE_EDGE_X:.2f} - {LIGHTHOUSE_OFFSHORE_M:.0f}m offshore)")
    print(f"  delta to apply: ({delta_x:+.2f}, {delta_y:+.2f})")

    lighthouse_changes = []
    for name in LIGHTHOUSE_OBJS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            print(f"  MISSING: {name}")
            continue
        before = (obj.location.x, obj.location.y, obj.location.z)
        after = (obj.location.x + delta_x, obj.location.y + delta_y, obj.location.z)
        lighthouse_changes.append((obj, before, after))
        print(f"  {name}: ({before[0]:7.2f}, {before[1]:7.2f}) → ({after[0]:7.2f}, {after[1]:7.2f})")

    # === OCEAN (snap to absolute target) ===
    print(f"\n=== Ocean (snap vertices to ±{OCEAN_TARGET_HALF_EXTENT}m) ===")
    ocean = bpy.data.objects.get(OCEAN_OBJ_NAME)
    if ocean is None:
        print(f"  ERROR: {OCEAN_OBJ_NAME} not found")
        raise SystemExit(1)
    verts = ocean.data.vertices
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]
    print(f"  before: XY [{min(xs):.2f}, {min(ys):.2f}] - [{max(xs):.2f}, {max(ys):.2f}]  "
          f"({len(verts)} verts)")
    # Compute new vertex positions: snap by sign to ±target. Works for the
    # 4-vertex plane regardless of starting size (could be ±100, ±250, etc).
    new_ocean_verts = []
    for v in verts:
        nx = OCEAN_TARGET_HALF_EXTENT if v.co.x >= 0 else -OCEAN_TARGET_HALF_EXTENT
        ny = OCEAN_TARGET_HALF_EXTENT if v.co.y >= 0 else -OCEAN_TARGET_HALF_EXTENT
        new_ocean_verts.append((nx, ny, v.co.z))
    new_xs = [v[0] for v in new_ocean_verts]
    new_ys = [v[1] for v in new_ocean_verts]
    print(f"  after:  XY [{min(new_xs):.2f}, {min(new_ys):.2f}] - "
          f"[{max(new_xs):.2f}, {max(new_ys):.2f}]")

    # === COVERAGE CHECK ===
    terrain_half_extent = abs(NEW_SHORE_EDGE_X)
    margin = OCEAN_TARGET_HALF_EXTENT - terrain_half_extent
    print(f"\n=== Terrain coverage check ===")
    print(f"  terrain ±{terrain_half_extent:.2f}m, ocean ±{OCEAN_TARGET_HALF_EXTENT:.2f}m")
    if margin >= 0:
        print(f"  OK: ocean covers terrain with {margin:.2f}m margin past shore.")
    else:
        print(f"  ⚠️  WARNING: ocean is smaller than terrain by {-margin:.2f}m.")
        print(f"     Seabed past ocean edge will be visible as bare geometry.")

    # === BACKDROP FRAMING CHECK ===
    print(f"\n=== Backdrop framing check ===")
    print(f"  Where the closest backdrop edges land relative to ocean edge ±{OCEAN_TARGET_HALF_EXTENT:.2f}:")
    for obj, _, after in mountain_changes:
        n = obj.name
        print(f"    {n}: new origin ({after[0]:.2f}, {after[1]:.2f})")
    for obj, _, after in lighthouse_changes:
        if obj.name == LIGHTHOUSE_REFERENCE_OBJ:
            new_east_edge = after[0] + LIGHTHOUSE_ISLET_EAST_OFFSET
            print(f"    lighthouse islet east edge: x = {new_east_edge:.2f}  "
                  f"(should be ~{NEW_SHORE_EDGE_X - LIGHTHOUSE_OFFSHORE_M:.2f})")
            break

    if not APPLY:
        print("\n" + "=" * 72)
        print("DRY-RUN complete. No changes were saved.")
        print("To apply: rerun with `-- --apply` appended.")
        print("To tune: edit MOUNTAIN_LOC_SCALE / LIGHTHOUSE_OFFSHORE_M / OCEAN_TARGET_HALF_EXTENT in the script.")
        print("=" * 72)
        return

    # === APPLY ===
    print("\n" + "=" * 72)
    print("APPLYING")
    print("=" * 72)

    blend_path = bpy.data.filepath
    if not blend_path:
        print("ERROR: blend file has no path")
        raise SystemExit(1)

    timestamp = time.strftime("%Y-%m-%d-%H%M%S")
    bak_path = f"{blend_path}.pre-tighten-{timestamp}.bak"
    print(f"[backup] copying to {bak_path}")
    bpy.ops.wm.save_as_mainfile(filepath=bak_path, copy=True)

    for obj, _, after in mountain_changes:
        obj.location.x = after[0]
        obj.location.y = after[1]
    print(f"[mountains] moved {len(mountain_changes)} objects")

    for obj, _, after in lighthouse_changes:
        obj.location.x = after[0]
        obj.location.y = after[1]
    print(f"[lighthouse] moved {len(lighthouse_changes)} objects")

    for v, new_pos in zip(verts, new_ocean_verts):
        v.co.x = new_pos[0]
        v.co.y = new_pos[1]
    ocean.data.update()
    print(f"[ocean] snapped {len(verts)} vertices to ±{OCEAN_TARGET_HALF_EXTENT}m")

    scene[SCENE_STAMP_KEY] = (
        f"mountain_scale={MOUNTAIN_LOC_SCALE},"
        f"lighthouse_offshore_m={LIGHTHOUSE_OFFSHORE_M},"
        f"ocean_target_half_extent={OCEAN_TARGET_HALF_EXTENT}"
    )

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[save] wrote {blend_path}")

    print("\n" + "=" * 72)
    print("DONE. Next: re-export world.glb via `./tools/blender/run-phase.sh 13`")
    print("=" * 72)


if __name__ == "__main__":
    main()
