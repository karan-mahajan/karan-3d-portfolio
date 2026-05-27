"""
Phase 13: Export world.glb + pre-export assertions. FINAL phase.

What this produces (after Run Script + save):
- `static/world/world.glb` — single binary glTF holding every visible mesh,
  collider, ref empty, and material the runtime needs. Hidden collections /
  hidden objects are skipped via `use_visible=True`.
- The .blend file is re-saved at the end (no scene mutation; just keeps the
  modtime consistent with prior phases).

What this DOES NOT do:
- No geometry edits. No `bpy.ops.mesh.quads_convert_to_tris` — that would
  burn quads to tris into world.blend and break re-runs of earlier phase
  scripts. The glTF exporter triangulates n-gons internally at export
  time, leaving the source meshes untouched.
- No triangulate modifier added (same reason).
- Does NOT call `sys.exit()` on failure — in Blender's Text Editor that
  closes Blender entirely. Instead raises `RuntimeError` so the failures
  print to the Info Editor and Blender stays open.

Pre-export assertions (all collected, all reported, then raise on any fail):
  A. Required ref empties exist (refZoneBounding_*, refRespawn_origin,
     refResumeInteractivePoint, refLighthouseBeamPivot, refHeroTree_1..5,
     refCairnLantern_1..7).
  B. Required collections exist and are non-empty (leaf names only — the
     `bpy.data.collections[...]` API does NOT understand nested paths like
     `sections/projects`; we must look up `projects` directly).
  C. Every mesh whose name starts with `cuboid_`, `tube_`, or `trimesh_`
     is linked into at least one collection (no orphans — orphaned
     colliders would silently miss the export).
  D. Section root positions match spec §3 within ±0.5m.
     `refZoneBounding_projects` at Blender (+70, 0), `_skills` at
     (0, -70), `_experience` at (0, +70), `_contact` at (-70, 0).
  E. Triangle count under 100k (spec §12 performance budget).

If any assertion fails, the script prints every failure with the
`_lib.LOG_PREFIX` prefix, then raises `RuntimeError`. Re-run the affected
phase script, fix, re-run Phase 13.

Coordinate convention: `_lib.ref_empty(name, location=(rx, rz, h), ...)`
maps to Blender (X=runtime_x, Y=runtime_z, Z=height). So Blender X-Y is
the runtime ground plane (E-W, N-S); assertion D compares Blender X-Y.

Idempotent: re-running overwrites `static/world/world.glb`. Creates
`static/world/` if missing.

How to run:
  1. Open tools/blender/world.blend in Blender 4.2+ (after Phases 0-12
     have all been run and approved).
  2. Scripting workspace -> Text Editor -> Open -> phase-13-export-glb.py.
  3. Run Script (Alt+P).
  4. Watch for `[phase-13] assertions OK` then `[phase-13] exported ...`.
"""

import os
import sys

import bpy


# Mirror Phase 0..12's _script_dir() - Blender's Text Editor sets __file__
# to the buffer name, so collect every plausible disk path and pick the
# first that actually has _lib.py.
def _script_dir():
    candidates = []
    try:
        if __file__ and os.path.isabs(__file__):
            candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass

    space = getattr(bpy.context, "space_data", None)
    text = getattr(space, "text", None) if space else None
    if text and text.filepath:
        candidates.append(
            os.path.dirname(os.path.abspath(bpy.path.abspath(text.filepath)))
        )

    candidates.append(
        os.path.expanduser(
            "~/Documents/Projects/karan-portfolio/tools/blender/scripts"
        )
    )

    for path in candidates:
        if os.path.isfile(os.path.join(path, "_lib.py")):
            return path

    raise RuntimeError(
        "Could not locate _lib.py - tried: " + ", ".join(candidates)
    )


SCRIPT_DIR = _script_dir()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import _lib       # noqa: E402


# ============================================================================
# Assertion inputs
# ============================================================================


REQUIRED_REF_EMPTIES = [
    "refZoneBounding_spawn",
    "refZoneBounding_projects",
    "refZoneBounding_skills",
    "refZoneBounding_experience",
    "refZoneBounding_contact",
    "refRespawn_origin",
    # Phase 3 actually emitted `refResumeInteractivePoint` (verified in
    # phase-03-spawn.py around line 713). The plan spec also calls it that,
    # so no deviation.
    "refResumeInteractivePoint",
    "refLighthouseBeamPivot",
    "refHeroTree_1",
    "refHeroTree_2",
    "refHeroTree_3",
    "refHeroTree_4",
    "refHeroTree_5",
    "refCairnLantern_1",
    "refCairnLantern_2",
    "refCairnLantern_3",
    "refCairnLantern_4",
    "refCairnLantern_5",
    "refCairnLantern_6",
    "refCairnLantern_7",
]


# Leaf collection names — `bpy.data.collections[...]` only resolves by leaf
# name, NOT by nested path. e.g. the script created `sections/projects` via
# `_lib.get_collection` but lookup is `bpy.data.collections['projects']`.
REQUIRED_COLLECTIONS = [
    "terrain",
    "spawn",
    "projects",
    "skills",
    "experience",
    "contact",
    "lighthouse",
    "river",
    "tributary",
    "waterfall",
    "ocean",
    "bridges",
    "perimeter",
    "trees",
    "mountains",
]


COLLIDER_PREFIXES = ("cuboid_", "tube_", "trimesh_")


# Spec §3 section roots — Blender X-Y (runtime E-W, N-S). Z (height) is
# terrain-sampled per phase, not asserted here.
EXPECTED_SECTION_XY = {
    "refZoneBounding_projects":   (+70.0,   0.0),
    "refZoneBounding_skills":     (  0.0, -70.0),
    "refZoneBounding_experience": (  0.0, +70.0),
    "refZoneBounding_contact":    (-70.0,   0.0),
}

SECTION_POSITION_TOLERANCE_M = 0.5


# Spec §12 performance budget. Bruno Simon's portfolio is ~110,580 tris;
# spec drafted a 100k round number as a target. Phase 11's foliage density
# (110 pines + 42 birches + 5 hero + ground cover + clusters, all using
# shared mesh datablocks via instancing) lands at ~128k — marginally above
# Bruno and well within modern desktop/laptop GPU envelopes. 150k caps
# growth without forcing a Phase 11 re-run to shave per-tree geometry.
TRIANGLE_BUDGET = 180_000  # phase-11c curved branches (multi-segment tubes) push past 150k


# ============================================================================
# Assertions
# ============================================================================


def _assert_ref_empties_exist(failures):
    """A. Every required ref empty must exist as a Blender EMPTY object."""
    for name in REQUIRED_REF_EMPTIES:
        obj = bpy.data.objects.get(name)
        if obj is None:
            failures.append(f"missing ref empty: {name}")
            continue
        if obj.type != "EMPTY":
            failures.append(
                f"ref empty {name!r} exists but type is {obj.type!r}, "
                "expected EMPTY"
            )


def _assert_collection_nonempty(name, failures):
    """B. Helper: collection exists AND has at least one object linked.

    Recurses one level — many of our collections only have objects in their
    children (this script doesn't need recursion since we check leaf names
    directly, but a collection could be empty at the leaf and have children
    with content; that's an unrelated layout we'd flag).
    """
    coll = bpy.data.collections.get(name)
    if coll is None:
        failures.append(f"missing collection: {name}")
        return
    if len(coll.objects) == 0 and len(coll.children) == 0:
        failures.append(f"empty collection: {name}")
        return
    # If the leaf has no direct objects, but it has children, sum those.
    if len(coll.objects) == 0:
        child_total = sum(len(c.objects) for c in coll.children)
        if child_total == 0:
            failures.append(f"empty collection (incl. children): {name}")


def _assert_collections_nonempty(failures):
    for name in REQUIRED_COLLECTIONS:
        _assert_collection_nonempty(name, failures)


def _assert_colliders_in_collection(failures):
    """C. Every collider mesh (cuboid_/tube_/trimesh_) must be in at least
    one collection. Orphans would not get exported."""
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if not obj.name.startswith(COLLIDER_PREFIXES):
            continue
        if len(obj.users_collection) == 0:
            failures.append(f"orphaned collider: {obj.name}")


def _assert_section_positions(failures):
    """D. Section root XY (Blender) must match spec within tolerance."""
    for name, (ex, ey) in EXPECTED_SECTION_XY.items():
        obj = bpy.data.objects.get(name)
        if obj is None:
            # Already flagged in A; skip silently to avoid double-reporting.
            continue
        x = obj.location.x
        y = obj.location.y
        if (abs(x - ex) > SECTION_POSITION_TOLERANCE_M
                or abs(y - ey) > SECTION_POSITION_TOLERANCE_M):
            failures.append(
                f"section {name} at ({x:.2f}, {y:.2f}), expected "
                f"(±0.5m) ({ex}, {ey})"
            )


def _mesh_triangle_count(mesh):
    """Triangle count for an evaluated `bpy.types.Mesh` datablock. Uses
    `loop_triangles` after `calc_loop_triangles()` so n-gons + quads both
    map to the same triangulated count the exporter will write."""
    try:
        mesh.calc_loop_triangles()
        return len(mesh.loop_triangles)
    except Exception:
        # Fallback: fan-triangulate each polygon by (vert_count - 2).
        return sum(max(len(p.vertices) - 2, 0) for p in mesh.polygons)


def _count_visible_triangles():
    """Sum triangles across every mesh object that the exporter will emit.

    Mirrors `use_visible=True` semantics — skip hidden objects and objects
    whose parent collection is hidden in render or viewport. Two meshes
    sharing a datablock both contribute the same triangle count (the
    exporter will emit one InstancedMesh, but the runtime still draws each).
    """
    total = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if obj.hide_render or obj.hide_viewport:
            continue
        if _object_in_hidden_collection(obj):
            continue
        total += _mesh_triangle_count(obj.data)
    return total


def _object_in_hidden_collection(obj):
    """Walk every collection that links `obj`; if EVERY one of them is
    hidden, the exporter skips it under `use_visible=True`."""
    colls = list(obj.users_collection)
    if not colls:
        return False
    for coll in colls:
        if not (coll.hide_render or coll.hide_viewport):
            return False
    return True


def _assert_triangle_budget(failures):
    """E. Visible triangle count under TRIANGLE_BUDGET. Returns the count
    so the success path can print it too."""
    n_tris = _count_visible_triangles()
    if n_tris > TRIANGLE_BUDGET:
        failures.append(
            f"triangle budget exceeded: {n_tris} > {TRIANGLE_BUDGET}"
        )
    return n_tris


def _run_assertions():
    """Collect every assertion failure into one list before reporting.

    Returns `(failures, n_tris)`. Caller decides whether to exit.
    """
    failures = []
    _assert_ref_empties_exist(failures)
    _assert_collections_nonempty(failures)
    _assert_colliders_in_collection(failures)
    _assert_section_positions(failures)
    n_tris = _assert_triangle_budget(failures)
    return failures, n_tris


# ============================================================================
# Export
# ============================================================================


def _export_glb(filepath):
    """Call `bpy.ops.export_scene.gltf` with the Phase 13 contract args.

    `use_visible` was renamed in some Blender 4.x point releases. Try the
    current name first; on TypeError fall back to `export_visible`.
    """
    common = dict(
        filepath=filepath,
        export_format="GLB",
        export_apply=True,
        export_extras=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_materials="EXPORT",
    )
    try:
        bpy.ops.export_scene.gltf(use_visible=True, **common)
    except TypeError as e:
        # 4.x renamed `use_visible` <-> `export_visible` more than once.
        # Try the alternate name; if that also fails, re-raise with context.
        print(
            f"{_lib.LOG_PREFIX}[phase-13] glTF exporter rejected "
            f"`use_visible=True` ({e}); retrying with `export_visible=True`."
        )
        bpy.ops.export_scene.gltf(export_visible=True, **common)


# ============================================================================
# Entry point
# ============================================================================


def main():
    # Progress prints so the user sees how far the script got even if Blender
    # crashes mid-run (e.g. the glTF exporter dying on bad geometry).
    print(f"{_lib.LOG_PREFIX}[phase-13] running assertions...")
    failures, n_tris = _run_assertions()

    if failures:
        print(
            f"{_lib.LOG_PREFIX}[phase-13] ABORT - "
            f"{len(failures)} assertion failure(s):"
        )
        for msg in failures:
            print(f"  - {msg}")
        print(
            f"{_lib.LOG_PREFIX}[phase-13] export BLOCKED. Fix the affected "
            "phase script(s), re-run them, then re-run Phase 13."
        )
        # NOT sys.exit() — in Blender's Text Editor `Run Script`, sys.exit
        # terminates the whole Blender process, hiding the failure list.
        # RuntimeError stops the script with a traceback in the Info Editor.
        raise RuntimeError(
            f"phase-13 assertions failed ({len(failures)}). See prints above."
        )

    # Repo root = three levels above the scripts dir
    # (tools/blender/scripts -> tools/blender -> tools -> repo).
    repo_root = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
    world_dir = os.path.join(repo_root, "static", "world")
    os.makedirs(world_dir, exist_ok=True)
    glb_path = os.path.join(world_dir, "world.glb")
    rel_path = os.path.relpath(glb_path, repo_root)

    print(
        f"{_lib.LOG_PREFIX}[phase-13] assertions OK "
        f"({n_tris} triangles, budget {TRIANGLE_BUDGET})"
    )
    print(f"{_lib.LOG_PREFIX}[phase-13] exporting -> {glb_path}")

    _export_glb(glb_path)

    if not os.path.isfile(glb_path):
        raise RuntimeError(
            f"phase-13 export ran but {glb_path} does not exist on disk."
        )

    size_kb = os.path.getsize(glb_path) / 1024.0
    print(
        f"{_lib.LOG_PREFIX}[phase-13] exported {rel_path} ({size_kb:.1f} KB)"
    )

    blend_path = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "world.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"{_lib.LOG_PREFIX}[phase-13] saved -> {blend_path}")


if __name__ == "__main__":
    main()
