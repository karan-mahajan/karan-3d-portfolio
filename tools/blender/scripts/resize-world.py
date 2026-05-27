"""
One-shot XY scale of the v2 Blender world.

Shrinks the walkable island from r≈80.6m → r≈60m (factor 0.745) while
preserving terrain heights, ocean plane, mountain backdrop, and lighthouse
islet. NOT part of the phase-NN build pipeline — this is a post-authoring
transform applied to the finished blend.

# How to run

Dry-run (default — prints the plan, does NOT mutate the blend):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/resize-world.py

Apply (mutates + saves; writes a .pre-resize-*.bak alongside):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    tools/blender/world.blend \\
    --python tools/blender/scripts/resize-world.py -- --apply

Re-export GLB afterward (NOTE: phase-13 section assertions will fail until
their expected XY values are updated to the post-resize coords — see the
post-run notes printed at the end):

  ./tools/blender/run-phase.sh 13

# What it does

Two mechanisms, picked per object:

  - Vertex-XY scale: for meshes whose origin is (0,0,0) and whose vertex
    positions encode world coordinates (terrain heightfield, river surface,
    trail perimeter, etc). Mesh.vertices[i].co.x *= s, .co.y *= s. Z untouched
    so hills + heightfield depths are preserved.

  - Location-XY scale: for placed instances and empties (trees, bridges,
    benches, refs, section roots). obj.location.x *= s, .y *= s. Z untouched.

# What it does NOT touch

  - `mountains`, `lighthouse`, `ocean` collections (held fixed — these are
    horizon/offshore elements that read worse if shrunk).
  - `refLighthouseBeamPivot` (in `refs` but anchored to the lighthouse).
  - Source meshes parked above z = +100 (tree-prototype library).
  - Object scale on instance-meshes (trees, props keep their visual size).
  - Z axis on any mesh or location.

# Idempotency

Stamps `scene['world_resize_applied'] = SCALE` on --apply. Re-running with
--apply detects this and aborts (refuses to scale twice). The stamp also
serves as a marker that downstream scripts (e.g. phase-13) can read.
"""

import os
import sys
import time

import bpy


# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------


# Target factor. 60.0 / 80.6 ≈ 0.745. Anchors on the perimeter trail half-
# extent (the canonical walkable edge). Section endpoints, refs, props all
# follow this factor uniformly.
SCALE = 0.745


# Leaf collection names whose member objects should have `obj.location`
# scaled XY. Children of these collections that are also meshes with
# origin == (0,0,0) get vertex-scaled instead (see VERTEX_SCALE_MESHES).
LOCATION_SCALE_COLLECTIONS = {
    "spawn",
    # sections/
    "projects", "experience", "skills", "contact",
    "bridges",
    # trail/
    "perimeter", "detour_nw", "detour_summit", "detour_se",
    "viewpoints",
    # props/
    "benches", "signs", "boulder_clusters",
    # foliage/
    "trees", "hero_trees", "ground_cover",
    # water/
    "river", "tributary", "waterfall",
    "refs",
}


# Meshes whose origin is (0,0,0) and whose vertices encode world XY directly.
# These need vertex-XY scale instead of location scale (location is already
# zero, so multiplying does nothing). All other meshes in scale collections
# get location-scaled.
VERTEX_SCALE_MESHES = {
    "terrain_mesh",
    "trimesh_terrain",
    "river_surface",
    "tributary_surface",
    "waterfall_plane",
    "trail_perimeter",
    "trail_detour_nw",
    "trail_detour_summit",
    "trail_detour_se",
}


# Collections held entirely fixed (not scaled in any way).
HOLD_FIXED_COLLECTIONS = {"mountains", "lighthouse", "ocean"}


# Refs anchored to hold-fixed geometry. Even though they live in the `refs`
# collection (which is in LOCATION_SCALE_COLLECTIONS), these specific empties
# must stay put or their dependent meshes (lighthouse_beam etc) will drift.
REFS_PINNED_TO_FIXED = {
    "refLighthouseBeamPivot",
}


# Source/library meshes parked at high Z (hidden datablocks used as
# instance prototypes). Never touched. Threshold is generous — actual sources
# sit at z=+200 per inspection.
SOURCE_PARK_Z_MIN = 100.0


# Stamp key on bpy.context.scene to detect prior resizes.
SCENE_STAMP_KEY = "world_resize_applied"


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def _argv_after_double_dash():
    """Blender passes everything after `--` to the script. Anything before
    `--` is consumed by Blender itself (e.g. the .blend path)."""
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return []


_CLI = _argv_after_double_dash()
APPLY = "--apply" in _CLI


# ----------------------------------------------------------------------------
# Collection walk
# ----------------------------------------------------------------------------


def _collect_objects_in(collection_names):
    """Return a flat set of objects belonging to any of the named (leaf)
    collections. `bpy.data.collections[name]` returns the leaf — we then
    walk `coll.objects` only (not recursing into children; the scale lists
    enumerate leaves directly)."""
    out = set()
    for cname in collection_names:
        coll = bpy.data.collections.get(cname)
        if coll is None:
            continue
        for obj in coll.objects:
            out.add(obj)
    return out


def _resolve_fixed_objects():
    """Set of objects belonging to any HOLD_FIXED collection (incl. their
    descendants if any are parented). These are never scaled."""
    fixed = _collect_objects_in(HOLD_FIXED_COLLECTIONS)
    # Walk parent chain — if a parent is fixed, children inherit (so the
    # parented lighthouse_beam is also fixed via its parent ref).
    for obj in bpy.data.objects:
        p = obj.parent
        while p is not None:
            if p in fixed or p.name in REFS_PINNED_TO_FIXED:
                fixed.add(obj)
                break
            p = p.parent
    return fixed


# ----------------------------------------------------------------------------
# Actions
# ----------------------------------------------------------------------------


def _plan_vertex_scale(mesh_obj):
    """Return (n_verts, bbox_before) without mutating."""
    if mesh_obj.type != "MESH":
        return None
    verts = mesh_obj.data.vertices
    if len(verts) == 0:
        return (0, None)
    xs = [v.co.x for v in verts]
    ys = [v.co.y for v in verts]
    return (len(verts), (min(xs), min(ys), max(xs), max(ys)))


def _apply_vertex_scale(mesh_obj, s):
    """In-place XY vertex scale (preserves Z)."""
    for v in mesh_obj.data.vertices:
        v.co.x *= s
        v.co.y *= s
    mesh_obj.data.update()


def _plan_location_scale(obj):
    """Return (before, after) location tuples without mutating."""
    before = (obj.location.x, obj.location.y, obj.location.z)
    after = (obj.location.x * SCALE, obj.location.y * SCALE, obj.location.z)
    return (before, after)


def _apply_location_scale(obj, s):
    obj.location.x *= s
    obj.location.y *= s


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main():
    print("=" * 72)
    print(f"resize-world.py  SCALE={SCALE}  mode={'APPLY' if APPLY else 'DRY-RUN'}")
    print("=" * 72)

    # Refuse to scale twice.
    scene = bpy.context.scene
    prior = scene.get(SCENE_STAMP_KEY)
    if prior is not None and APPLY:
        print(f"\nABORT: scene already has {SCENE_STAMP_KEY}={prior}.")
        print("Resize was applied previously. To re-resize, restore the .bak file first.")
        raise SystemExit(1)
    if prior is not None:
        print(f"\n[note] scene already has {SCENE_STAMP_KEY}={prior} (prior resize detected).\n")

    # Resolve which objects are off-limits.
    fixed_objs = _resolve_fixed_objects()
    print(f"\n[fixed] {len(fixed_objs)} objects held fixed via collection or parent inheritance")

    # Vertex-scale plan
    vs_plan = []
    for name in sorted(VERTEX_SCALE_MESHES):
        obj = bpy.data.objects.get(name)
        if obj is None:
            print(f"  [vertex] MISSING: {name}")
            continue
        if obj in fixed_objs:
            print(f"  [vertex] SKIP (fixed): {name}")
            continue
        info = _plan_vertex_scale(obj)
        if info is None:
            continue
        n_verts, bbox = info
        vs_plan.append((obj, n_verts, bbox))

    # Location-scale plan
    ls_plan = []
    scale_candidates = _collect_objects_in(LOCATION_SCALE_COLLECTIONS)
    for obj in scale_candidates:
        if obj in fixed_objs:
            continue
        if obj.name in REFS_PINNED_TO_FIXED:
            continue
        # Skip source/library meshes parked high.
        if obj.location.z > SOURCE_PARK_Z_MIN:
            continue
        # Skip vertex-scaled meshes (they'd double-process otherwise).
        if obj.name in VERTEX_SCALE_MESHES:
            continue
        before, after = _plan_location_scale(obj)
        # Skip no-ops (loc XY already 0).
        if abs(before[0]) < 1e-6 and abs(before[1]) < 1e-6:
            continue
        ls_plan.append((obj, before, after))

    # Print plan
    print(f"\n=== Vertex-scale ({len(vs_plan)} meshes) ===")
    for obj, n_verts, bbox in vs_plan:
        bx0, by0, bx1, by1 = bbox
        nx0, ny0, nx1, ny1 = bx0 * SCALE, by0 * SCALE, bx1 * SCALE, by1 * SCALE
        print(
            f"  {obj.name}  verts={n_verts}  "
            f"XY [{bx0:7.2f},{by0:7.2f}]-[{bx1:7.2f},{by1:7.2f}] → "
            f"[{nx0:7.2f},{ny0:7.2f}]-[{nx1:7.2f},{ny1:7.2f}]"
        )

    # Group location-scale by source collection for readability
    by_coll = {}
    for obj, before, after in ls_plan:
        coll_name = obj.users_collection[0].name if obj.users_collection else "(none)"
        by_coll.setdefault(coll_name, []).append((obj, before, after))

    print(f"\n=== Location-scale ({len(ls_plan)} objects across {len(by_coll)} collections) ===")
    for coll_name in sorted(by_coll):
        items = by_coll[coll_name]
        print(f"  [{coll_name}] {len(items)} objs")
        for obj, before, after in items[:3]:
            print(
                f"    {obj.name}  "
                f"({before[0]:7.2f},{before[1]:7.2f},{before[2]:6.2f}) → "
                f"({after[0]:7.2f},{after[1]:7.2f},{after[2]:6.2f})"
            )
        if len(items) > 3:
            print(f"    … +{len(items) - 3} more")

    # Sample changes that should move:
    print("\n=== Key reference points (where they end up) ===")
    interesting = [
        "refZoneBounding_projects", "refZoneBounding_skills",
        "refZoneBounding_experience", "refZoneBounding_contact",
        "refZoneBounding_spawn", "refRespawn_origin",
        "refHeroTree_1", "refHeroTree_5",
    ]
    for name in interesting:
        obj = bpy.data.objects.get(name)
        if obj is None:
            print(f"  {name}: MISSING")
            continue
        bx, by = obj.location.x, obj.location.y
        nx, ny = bx * SCALE, by * SCALE
        if obj in fixed_objs or obj.name in REFS_PINNED_TO_FIXED:
            print(f"  {name}: ({bx:.2f}, {by:.2f}) [HELD FIXED]")
        else:
            print(f"  {name}: ({bx:.2f}, {by:.2f}) → ({nx:.2f}, {ny:.2f})")

    print("\n=== Held fixed (not scaled) ===")
    fixed_names = sorted({o.name for o in fixed_objs})
    for n in fixed_names[:20]:
        print(f"  {n}")
    if len(fixed_names) > 20:
        print(f"  … +{len(fixed_names) - 20} more")

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

    # Backup first.
    blend_path = bpy.data.filepath
    if not blend_path:
        print("ERROR: blend file has no path (was it opened from --background?). Aborting.")
        raise SystemExit(1)
    timestamp = time.strftime("%Y-%m-%d-%H%M%S")
    bak_path = f"{blend_path}.pre-resize-{timestamp}.bak"
    print(f"[backup] copying current state to {bak_path}")
    # Save as a copy (does not change the active filepath).
    bpy.ops.wm.save_as_mainfile(filepath=bak_path, copy=True)

    # Apply vertex scales
    print(f"\n[vertex] scaling {len(vs_plan)} meshes")
    for obj, _, _ in vs_plan:
        _apply_vertex_scale(obj, SCALE)
        print(f"  ✓ {obj.name}")

    # Apply location scales
    print(f"\n[location] scaling {len(ls_plan)} objects")
    for obj, _, _ in ls_plan:
        _apply_location_scale(obj, SCALE)

    # Stamp scene
    scene[SCENE_STAMP_KEY] = SCALE
    print(f"\n[stamp] scene['{SCENE_STAMP_KEY}'] = {SCALE}")

    # Save
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[save] wrote {blend_path}")

    # Post-run notes
    print("\n" + "=" * 72)
    print("DONE. Next steps:")
    print("=" * 72)
    print(
        "1. Open the blend in Blender to eyeball the result.\n"
        "2. Update phase-13 section assertions (EXPECTED_SECTION_XY) to:\n"
        f"      projects   : (+{ 70 * SCALE:.2f},  0.00)\n"
        f"      skills     : ( 0.00, -{70 * SCALE:.2f})\n"
        f"      experience : ( 0.00, +{70 * SCALE:.2f})\n"
        f"      contact    : (-{70 * SCALE:.2f},  0.00)\n"
        "3. Re-export: `./tools/blender/run-phase.sh 13`\n"
        "4. Update CLAUDE.md radius constants (was ~80m walkable; now ~60m)."
    )


if __name__ == "__main__":
    main()
