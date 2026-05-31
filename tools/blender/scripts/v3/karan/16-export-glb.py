"""karan section 16 — SPLIT EXPORT: world-v3-karan.blend -> static/world/*.glb.

First step of the JS/Three.js runtime phase. Runs headless against the finalized
karan world (build sections 01..15 already baked into
`tools/blender/world-v3-karan.blend`) and writes a Bruno-style SPLIT model set:
per-system GLBs + a generated `manifest.json` the runtime loader reads.

NEVER edits the source .blend on disk. Every mutation (neutralizing the grass GN,
tagging roles, building template/reference temp objects) happens in-memory in the
headless session and is discarded on exit. No save_as_mainfile(). Re-runnable;
deterministic for a given .blend.

--------------------------------------------------------------------------- #
WHY SPLIT (Bruno Simon's folio-2025 model)
--------------------------------------------------------------------------- #
Bruno ships one GLB per content system instead of a monolith, so the runtime can
load/instance each independently. Three output kinds:

  MONOLITHIC  — placed-once geometry, added to the scene whole. One GLB per
                system, world transforms baked (the system's root_<collection>
                empty + its meshes are exported together so the finalize scene-
                graph + world poses survive).
                  terrain, structures, areas (3 section markers, NOT experience),
                  scenery (bridges+slabs), statue, lava, miscFx, the three tree-
                  trunk collections, fences, benches, lanterns, poleLights.
                  bonfires is monolithic too: each fire is a custom authored
                  mesh with per-face material slots, not an instanced Kenney
                  campfire prop.

  INSTANCED   — systems whose objects SHARE a mesh datablock (verified: pure
                transforms of a template, no per-object modifiers). Emitted as a
                Bruno-style pair:
                  {sys}Visual.glb      — one template object per shared datablock,
                                         at IDENTITY (raw local geometry; the
                                         reference's world matrix re-applies
                                         placement+scale). Named by datablock so
                                         references map back.
                  {sys}References.glb  — one EMPTY per source object at its world
                                         matrix, custom prop `template`=datablock.
                Systems: rocks (boulderCluster/volcanicShards), bricks (pave/pile/
                kerb — unit meshes scaled per-instance), flowers (8 zone meshes).
                Runtime builds one InstancedMesh per (system, template).
                NOTE: benches/lanterns/poleLights each have UNIQUE per-object
                datablocks (not shared) -> they are MONOLITHIC, not instanced.

  FOLIAGE     — reference empties only; the runtime grows SDF clouds at them
                (Bruno Foliage), no exported visual:
                  bushes      — world matrices of the bushAnchor meshes.
                  treeLeaves  — the refTreeLeaves_* empties (carry `species`).

Plus:
  colliders.glb  — every `colliders` proxy mesh (tube_=cylinder, cuboid_=box,
                   *Footprint_=walkable pad). Runtime builds Rapier shapes from
                   the name prefix + bbox, then hides the meshes.
  references.glb — interaction/light/anim anchor empties: sectionRef_* (the
                   section interaction contract in `extras`), controlsRef,
                   playstationRef, titleRef, lavaRef_pool, refBonfire_*,
                   refPoleLight_*, animalPivot_*, airDancerPivot_*.
  terrainGrass.exr — the authored grass/water mask, copied next to the GLBs for
                   the runtime grass shader (Bruno terrain-mask grass).
  manifest.json  — lists every file + its runtime handler + counts. Data-driven
                   loader (improvement over Bruno's hand-maintained list).

GRASS: `Plane.003`'s grass geometry-nodes evaluates to ~12.8M tris baked. Bruno
never exports it — his live grass is a runtime shader fed by the terrain mask. We
disable the plane's NODES modifier(s) in-memory; the plane is NOT exported (the
runtime grows grass from terrainGrass.exr over the grid bounds instead).

EXPORTER CONTRACT (per GLB):
  export_format="GLB", export_apply=True (bake BEVELs + terrain heightfield so
  terrain.heightAt matches visuals), export_extras=True (carry role/section/
  species/template/interaction custom props -> node.extras), export_yup=True,
  export_cameras=False, export_lights=False, export_animations=False,
  export_draco_mesh_compression_enable=False (ship uncompressed first; gltf-
  transform Draco/KTX2 is a later optional pass).

HOW TO RUN (headless):
    /Applications/Blender.app/Contents/MacOS/Blender --background \
      tools/blender/world-v3-karan.blend \
      --python tools/blender/scripts/v3/karan/16-export-glb.py

Writes static/world/<system>/*.glb + manifest.json and prints a per-file size
report. Exits non-zero (RuntimeError) on a pre-export assertion failure.
"""
import json
import os
import shutil

import bpy
from mathutils import Matrix

LOG = "[16-split-export]"


def _repo_root():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))
        if os.path.isdir(os.path.join(root, "static")):
            return root
    except NameError:
        pass
    return os.path.expanduser("~/Documents/Projects/karan-portfolio")


REPO_ROOT = _repo_root()
OUT_DIR = os.path.join(REPO_ROOT, "static", "world")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")

# files the previous single-GLB exporter / v2 left behind — removed after a clean
# split so the runtime never loads a stale monolith.
STALE_FILES = ["world.glb", "world-v3.glb"]

GRASS_GRID_OBJECT = "Plane.003"
GRASS_GRID_BOUNDS = 96.0          # Plane.003 half-extent (m); grid bounds for runtime grass
COLLIDER_COLLECTION = "colliders"
REFS_COLLECTION = "refs"
SECTION_ROOT_PROP = "section_root"

GRASS_MASK_SRC = os.path.join(
    REPO_ROOT, "tools", "blender", "scripts", "v3", "karan",
    "resources", "masks", "terrainGrass-authored.exr")
GRASS_MASK_DST_NAME = "terrainGrass.exr"

RUNAWAY_TRI_THRESHOLD = 500_000

# --- system spec ------------------------------------------------------------ #
# MONOLITHIC: (system, output_subdir/file, [collection names])  the collection's
# root empty + meshes export together (hierarchy + world pose preserved).
MONOLITHIC = [
    ("terrain",     "terrain/terrain.glb",          ["terrain"]),
    ("structures",  "structures/structures.glb",    ["structures"]),
    ("scenery",     "scenery/scenery.glb",          ["bridges", "slabs"]),
    ("statue",      "statue/statue.glb",            ["statue"]),
    ("lava",        "lava/lava.glb",                ["lavaPool"]),
    ("miscFx",      "miscFx/miscFx.glb",            ["miscFx"]),
    ("birchTrees",  "vegetation/birchTrees.glb",    ["birchTrees"]),
    ("cherryTrees", "vegetation/cherryTrees.glb",   ["cherryTrees"]),
    ("oakTrees",    "vegetation/oakTrees.glb",      ["oakTrees"]),
    ("fences",      "fences/fences.glb",            ["fences"]),
    ("benches",     "benches/benches.glb",          ["benches"]),
    ("lanterns",    "lanterns/lanterns.glb",        ["lanterns"]),
    ("poleLights",  "poleLights/poleLights.glb",    ["pole_lights"]),
    ("bonfires",    "bonfires/bonfires.glb",        ["bonfire"]),
]

# AREAS is special: the 3 section-marker subcollections only (NOT the inert
# experience marker/label that sit at the sectionMarkers top level).
AREAS_SUBCOLLECTIONS = ["projectsHut", "skillsSphere", "contactBoard"]

# INSTANCED: (system, subdir, collection)  -> {sys}Visual.glb + {sys}References.glb
INSTANCED = [
    ("rocks",   "rocks",   "basaltRocks"),
    ("bricks",  "bricks",  "bricks"),
    ("flowers", "flowers", "flowers"),
]

# FOLIAGE references-only (empties): from mesh-collection transforms, or from
# existing ref empties matched by prefix.
FOLIAGE_FROM_MESHES = [("bushes", "bushes/bushesReferences.glb", "bushes")]
FOLIAGE_FROM_REFS = [("treeLeaves", "treeLeaves/treeLeavesReferences.glb",
                      "refTreeLeaves_")]

# references.glb: ref empties matched by these prefixes (sectionRef_* etc.).
REFERENCE_PREFIXES = (
    "sectionRef_", "controlsRef", "playstationRef", "titleRef", "lavaRef_",
    "refBonfire_", "refPoleLight_", "animalPivot_", "airDancerPivot_",
)


# --------------------------------------------------------------------------- #
# scene helpers
# --------------------------------------------------------------------------- #
def _coll(name):
    return bpy.data.collections.get(name)


def _coll_objects(name, types=None):
    c = _coll(name)
    if c is None:
        return []
    out = []

    def walk(cc):
        for o in cc.objects:
            if types is None or o.type in types:
                out.append(o)
        for ch in cc.children:
            walk(ch)

    walk(c)
    return out


def _deselect_all():
    for o in bpy.context.selected_objects:
        o.select_set(False)


def _select(objs):
    _deselect_all()
    vl = bpy.context.view_layer
    active = None
    for o in objs:
        o.hide_set(False)
        o.hide_viewport = False
        o.hide_render = False
        o.select_set(True)
        active = o
    vl.objects.active = active


EXPORT_FLAGS = dict(
    export_format="GLB",
    export_apply=True,
    export_extras=True,
    export_yup=True,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_materials="EXPORT",
    export_draco_mesh_compression_enable=False,
)


def _export_selection(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True,
                                  **EXPORT_FLAGS)
    except TypeError as e:
        print(f"{LOG} exporter rejected use_selection ({e}); retrying use_visible")
        bpy.ops.export_scene.gltf(filepath=filepath, use_visible=True,
                                  **EXPORT_FLAGS)
    if not os.path.isfile(filepath):
        raise RuntimeError(f"{LOG} export ran but {filepath} missing")
    return os.path.getsize(filepath)


def _evaluated_tris(obj, dg):
    if obj.type not in ("MESH", "FONT", "CURVE", "SURFACE"):
        return 0
    try:
        ev = obj.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        ev.to_mesh_clear()
        return n
    except Exception:
        return 0


# --------------------------------------------------------------------------- #
# prep: neutralize grass GN + tag colliders so they survive/are identifiable
# --------------------------------------------------------------------------- #
def _neutralize_grass():
    plane = bpy.data.objects.get(GRASS_GRID_OBJECT)
    if plane is None:
        print(f"{LOG} WARNING: '{GRASS_GRID_OBJECT}' not found — no grass GN to "
              "neutralize.")
        return
    disabled = 0
    for m in plane.modifiers:
        if m.type == "NODES":
            m.show_viewport = False
            m.show_render = False
            disabled += 1
    print(f"{LOG} neutralized {disabled} grass NODES modifier(s) on "
          f"'{GRASS_GRID_OBJECT}' (not exported; runtime grows grass from mask)")


# --------------------------------------------------------------------------- #
# temp-object bookkeeping (templates + reference empties) — cleaned each system
# --------------------------------------------------------------------------- #
_TEMP = []


def _new_empty(name, world_matrix, props=None):
    e = bpy.data.objects.new(name, None)          # None data -> EMPTY
    bpy.context.scene.collection.objects.link(e)
    e.parent = None
    e.matrix_basis = world_matrix.copy()          # no parent => basis == world
    e.empty_display_size = 0.2
    if props:
        for k, v in props.items():
            e[k] = v
    _TEMP.append(e)
    return e


def _template_from(member, name):
    """Duplicate a group member, share its mesh data, drop transform to identity.
    Keeps object-level material slots (rocks link materials at OBJECT level)."""
    t = member.copy()                              # object copy; shares .data
    bpy.context.scene.collection.objects.link(t)
    t.parent = None
    t.matrix_basis = Matrix.Identity(4)
    t.name = name
    t.hide_set(False)
    t.hide_viewport = False
    t.hide_render = False
    _TEMP.append(t)
    return t


def _purge_temp():
    global _TEMP
    for o in _TEMP:
        try:
            bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass
    _TEMP = []


# --------------------------------------------------------------------------- #
# exporters per kind
# --------------------------------------------------------------------------- #
def _export_monolithic(system, rel, coll_names, report):
    objs = []
    for cn in coll_names:
        c = _coll(cn)
        if c is None:
            print(f"{LOG} WARNING: monolithic '{system}': collection "
                  f"'{cn}' missing")
            continue
        objs.extend(_coll_objects(cn))             # includes root empty + meshes
    if not objs:
        print(f"{LOG} WARNING: monolithic '{system}' selected 0 objects — skip")
        return None
    _select(objs)
    size = _export_selection(os.path.join(OUT_DIR, rel))
    report.append((rel, size, len(objs)))
    return {"system": system, "file": rel, "kind": "monolithic",
            "objects": len(objs),
            **({"heightfield": True} if system == "terrain" else {})}


def _export_areas(report):
    objs = []
    for cn in AREAS_SUBCOLLECTIONS:
        objs.extend(_coll_objects(cn))
    if not objs:
        print(f"{LOG} WARNING: areas selected 0 objects — skip")
        return None
    _select(objs)
    rel = "areas/areas.glb"
    size = _export_selection(os.path.join(OUT_DIR, rel))
    report.append((rel, size, len(objs)))
    return {"system": "areas", "file": rel, "kind": "monolithic",
            "objects": len(objs), "markers": AREAS_SUBCOLLECTIONS}


def _export_instanced(system, subdir, coll_name, report):
    members = _coll_objects(coll_name, types={"MESH"})
    if not members:
        print(f"{LOG} WARNING: instanced '{system}': 0 meshes — skip")
        return None
    # group by mesh datablock
    groups = {}
    for o in members:
        groups.setdefault(o.data.name, []).append(o)

    # Visual: one identity template object per datablock
    _purge_temp()
    templates = [_template_from(grp[0], db) for db, grp in groups.items()]
    _select(templates)
    vis_rel = f"{subdir}/{system}Visual.glb"
    vis_size = _export_selection(os.path.join(OUT_DIR, vis_rel))
    _purge_temp()

    # References: one empty per member, tagged with its template datablock
    empties = []
    for db, grp in groups.items():
        for o in grp:
            props = {"template": db}
            for k in o.keys():
                if k != "_RNA_UI":
                    props.setdefault(k, o[k])
            empties.append(_new_empty(f"ref_{o.name}", o.matrix_world, props))
    _select(empties)
    ref_rel = f"{subdir}/{system}References.glb"
    ref_size = _export_selection(os.path.join(OUT_DIR, ref_rel))
    _purge_temp()

    report.append((vis_rel, vis_size, len(templates)))
    report.append((ref_rel, ref_size, len(members)))
    return {"system": system, "kind": "instanced",
            "visual": vis_rel, "references": ref_rel,
            "templates": sorted(groups.keys()), "count": len(members)}


def _export_foliage_from_meshes(system, rel, coll_name, report):
    members = _coll_objects(coll_name, types={"MESH"})
    if not members:
        print(f"{LOG} WARNING: foliage '{system}': 0 meshes — skip")
        return None
    _purge_temp()
    empties = [_new_empty(f"ref_{o.name}", o.matrix_world) for o in members]
    _select(empties)
    size = _export_selection(os.path.join(OUT_DIR, rel))
    _purge_temp()
    report.append((rel, size, len(members)))
    return {"system": system, "kind": "foliage", "references": rel,
            "count": len(members)}


def _export_foliage_from_refs(system, rel, prefix, report):
    src = [o for o in _coll_objects(REFS_COLLECTION) if o.name.startswith(prefix)]
    if not src:
        print(f"{LOG} WARNING: foliage '{system}': no refs '{prefix}*' — skip")
        return None
    _select(src)
    size = _export_selection(os.path.join(OUT_DIR, rel))
    report.append((rel, size, len(src)))
    species = sorted({o.get("species") for o in src if o.get("species")})
    return {"system": system, "kind": "foliage", "references": rel,
            "count": len(src), "bySpecies": species or None}


def _export_colliders(report):
    objs = _coll_objects(COLLIDER_COLLECTION, types={"MESH"})
    for o in objs:
        o["role"] = "collider"
    if not objs:
        print(f"{LOG} WARNING: no colliders — skip")
        return None
    _select(objs)
    rel = "colliders/colliders.glb"
    size = _export_selection(os.path.join(OUT_DIR, rel))
    report.append((rel, size, len(objs)))
    return {"file": rel, "count": len(objs)}


def _export_references(report):
    src = [o for o in _coll_objects(REFS_COLLECTION)
           if any(o.name.startswith(p) for p in REFERENCE_PREFIXES)]
    if not src:
        print(f"{LOG} WARNING: no reference anchors matched — skip")
        return None
    for o in src:
        o["role"] = "ref"
    _select(src)
    rel = "references.glb"
    size = _export_selection(os.path.join(OUT_DIR, rel))
    report.append((rel, size, len(src)))
    return {"file": rel, "count": len(src)}


# --------------------------------------------------------------------------- #
# pre-export assertions
# --------------------------------------------------------------------------- #
def _assert_ready():
    failures = []
    if not _coll_objects(COLLIDER_COLLECTION):
        failures.append("'colliders' collection empty/missing")
    if not _coll_objects(REFS_COLLECTION):
        failures.append("'refs' collection empty/missing")
    for nm in ("sectionRef_projects", "sectionRef_skills", "sectionRef_contact"):
        if bpy.data.objects.get(nm) is None:
            failures.append(f"missing section ref: {nm}")
    terrain = bpy.data.objects.get("terrain")
    if terrain is None:
        failures.append("missing 'terrain'")
    else:
        live = [m for m in terrain.modifiers
                if m.type == "NODES" and m.show_render]
        if not live:
            failures.append("'terrain' has no live NODES (heightfield would be flat)")
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.name == GRASS_GRID_OBJECT:
            continue
        if not o.visible_get():
            continue
        n = _evaluated_tris(o, dg)
        if n > RUNAWAY_TRI_THRESHOLD:
            failures.append(f"runaway geometry {o.name} -> {n} tris")
    return failures


def _copy_grass_mask():
    if not os.path.isfile(GRASS_MASK_SRC):
        print(f"{LOG} WARNING: grass mask not found at {GRASS_MASK_SRC}")
        return None
    dst = os.path.join(OUT_DIR, GRASS_MASK_DST_NAME)
    shutil.copyfile(GRASS_MASK_SRC, dst)
    print(f"{LOG} copied grass mask -> {os.path.relpath(dst, REPO_ROOT)}")
    return GRASS_MASK_DST_NAME


# --------------------------------------------------------------------------- #
def main():
    print("#" * 70)
    print(f"# {LOG} split-export {bpy.data.filepath or '<unsaved>'}")
    print(f"#   -> {OUT_DIR}")
    print("#" * 70)

    _neutralize_grass()

    failures = _assert_ready()
    if failures:
        print(f"{LOG} ABORT — {len(failures)} pre-export failure(s):")
        for f in failures:
            print(f"    - {f}")
        raise RuntimeError(f"{LOG} pre-export assertions failed ({len(failures)})")

    os.makedirs(OUT_DIR, exist_ok=True)
    report = []
    manifest = {"monolithic": [], "instanced": [], "foliage": []}

    print(f"{LOG} --- monolithic ---")
    for system, rel, colls in MONOLITHIC:
        entry = _export_monolithic(system, rel, colls, report)
        if entry:
            manifest["monolithic"].append(entry)
    areas = _export_areas(report)
    if areas:
        manifest["monolithic"].append(areas)

    print(f"{LOG} --- instanced (Visual + References) ---")
    for system, subdir, coll_name in INSTANCED:
        entry = _export_instanced(system, subdir, coll_name, report)
        if entry:
            manifest["instanced"].append(entry)

    print(f"{LOG} --- foliage references ---")
    for system, rel, coll_name in FOLIAGE_FROM_MESHES:
        entry = _export_foliage_from_meshes(system, rel, coll_name, report)
        if entry:
            manifest["foliage"].append(entry)
    for system, rel, prefix in FOLIAGE_FROM_REFS:
        entry = _export_foliage_from_refs(system, rel, prefix, report)
        if entry:
            manifest["foliage"].append(entry)

    print(f"{LOG} --- colliders + references + mask ---")
    colliders = _export_colliders(report)
    if colliders:
        manifest["colliders"] = colliders
    refs = _export_references(report)
    if refs:
        manifest["references"] = refs
    mask = _copy_grass_mask()
    if mask:
        manifest["grassMask"] = mask
    manifest["grassGrid"] = {"bounds": GRASS_GRID_BOUNDS,
                             "gridObject": GRASS_GRID_OBJECT}

    with open(MANIFEST, "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"{LOG} wrote manifest.json")

    # remove stale monolith(s)
    for nm in STALE_FILES:
        p = os.path.join(OUT_DIR, nm)
        if os.path.isfile(p):
            os.remove(p)
            print(f"{LOG} removed stale {nm}")

    total = sum(s for _, s, _ in report)
    print(f"\n{LOG} ===== {len(report)} GLB files, "
          f"{total / (1024 * 1024):.2f} MB total =====")
    for rel, size, n in sorted(report):
        print(f"    {rel:42} {size/1024:8.1f} KB   {n:4} obj")
    print(f"{LOG} done")


if __name__ == "__main__":
    main()
