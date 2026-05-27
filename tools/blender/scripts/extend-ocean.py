"""
One-shot ocean-plane XY extension.

After the world was shrunk by resize-world.py (factor 0.745), the ocean plane
(held fixed at 200×200m, vertices ±100m) ended up barely larger than the new
terrain footprint (±96.85m) and the gap between ocean edge and the mountain
backdrop (y≈180+) became visible as empty Blender grid.

This script vertex-XY scales `ocean_plane` by OCEAN_SCALE so the water plane
reaches past the mountains. Z (height = -1.5) is preserved. Idempotent via a
scene stamp.

# How to run

Dry-run (default — prints the plan, does NOT mutate the blend):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/extend-ocean.py

Apply (mutates + saves; writes a .pre-ocean-*.bak alongside):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/extend-ocean.py -- --apply
"""

import sys
import time

import bpy


# 2.5× → 200×200m becomes 500×500m (vertices ±100 → ±250). Comfortably past
# the northernmost mountain band at y≈192 and the easternmost foothills at
# x≈124. Adjust here if a different size is wanted later.
OCEAN_SCALE = 2.5

OCEAN_OBJ_NAME = "ocean_plane"
SCENE_STAMP_KEY = "ocean_extend_applied"


def _argv_after_double_dash():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return []


APPLY = "--apply" in _argv_after_double_dash()


def main():
    print("=" * 72)
    print(f"extend-ocean.py  OCEAN_SCALE={OCEAN_SCALE}  mode={'APPLY' if APPLY else 'DRY-RUN'}")
    print("=" * 72)

    scene = bpy.context.scene
    prior = scene.get(SCENE_STAMP_KEY)
    if prior is not None and APPLY:
        print(f"\nABORT: scene already has {SCENE_STAMP_KEY}={prior}.")
        print("Ocean extension was applied previously. Restore the .bak file to re-run.")
        raise SystemExit(1)
    if prior is not None:
        print(f"\n[note] scene already has {SCENE_STAMP_KEY}={prior} (prior extension detected).\n")

    obj = bpy.data.objects.get(OCEAN_OBJ_NAME)
    if obj is None:
        print(f"ERROR: object {OCEAN_OBJ_NAME!r} not found.")
        raise SystemExit(1)
    if obj.type != "MESH":
        print(f"ERROR: {OCEAN_OBJ_NAME} is {obj.type}, expected MESH.")
        raise SystemExit(1)

    verts = obj.data.vertices
    if len(verts) == 0:
        print(f"ERROR: {OCEAN_OBJ_NAME} has no vertices.")
        raise SystemExit(1)

    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    zs = [v.co.z for v in verts]
    print(f"\n[ocean] {OCEAN_OBJ_NAME}: {len(verts)} verts")
    print(f"  before XY: [{min(xs):.2f}, {min(ys):.2f}] - [{max(xs):.2f}, {max(ys):.2f}]")
    print(
        f"  after  XY: [{min(xs)*OCEAN_SCALE:.2f}, {min(ys)*OCEAN_SCALE:.2f}] - "
        f"[{max(xs)*OCEAN_SCALE:.2f}, {max(ys)*OCEAN_SCALE:.2f}]"
    )
    print(f"  Z (preserved): {min(zs):.2f} - {max(zs):.2f}")

    # Sanity-check the gap closes
    print("\n[sanity] backdrop reference points")
    backdrop_objs = [
        "mountain_band_far_snow",
        "mountain_band_mid_peaks",
        "mountain_band_front_ridge",
        "mountain_band_foothills_east",
    ]
    for n in backdrop_objs:
        bo = bpy.data.objects.get(n)
        if bo is None:
            continue
        bb = [bo.matrix_world @ v.co for v in bo.data.vertices]
        bx = [v.x for v in bb]; by = [v.y for v in bb]
        print(f"  {n}: x [{min(bx):.1f}, {max(bx):.1f}]  y [{min(by):.1f}, {max(by):.1f}]")
    print(f"  new ocean half-extent: {max(xs) * OCEAN_SCALE:.1f}m (covers if > mountain max abs coord)")

    if not APPLY:
        print("\n" + "=" * 72)
        print("DRY-RUN complete. No changes were saved.")
        print("To apply: rerun with `-- --apply` appended.")
        print("=" * 72)
        return

    # ---- APPLY ----
    print("\n" + "=" * 72)
    print("APPLYING (mutating blend)")
    print("=" * 72)

    blend_path = bpy.data.filepath
    if not blend_path:
        print("ERROR: blend file has no path. Aborting.")
        raise SystemExit(1)

    timestamp = time.strftime("%Y-%m-%d-%H%M%S")
    bak_path = f"{blend_path}.pre-ocean-{timestamp}.bak"
    print(f"[backup] copying current state to {bak_path}")
    bpy.ops.wm.save_as_mainfile(filepath=bak_path, copy=True)

    for v in verts:
        v.co.x *= OCEAN_SCALE
        v.co.y *= OCEAN_SCALE
    obj.data.update()
    print(f"[ocean] scaled {len(verts)} vertices XY by {OCEAN_SCALE}")

    scene[SCENE_STAMP_KEY] = OCEAN_SCALE
    print(f"[stamp] scene['{SCENE_STAMP_KEY}'] = {OCEAN_SCALE}")

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[save] wrote {blend_path}")

    print("\n" + "=" * 72)
    print("DONE. Next: re-export world.glb via `./tools/blender/run-phase.sh 13`")
    print("      (phase-13 EXPECTED_SECTION_XY also still needs updating to ±52.15 per the prior resize step.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
