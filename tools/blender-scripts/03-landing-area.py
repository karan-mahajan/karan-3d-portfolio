"""
Phase 3: Landing area geometry

Input  : 02-materials.blend (Phase 2 output)
Output : 03-landing.blend

What this adds:
- The `areas` collection with `landing` sub-collection (and `title.001`, `controls`,
  `kiosk`, `bonfire` further nested under it) — matching Bruno's outliner structure.
- 23 MESH objects + 1 FONT object (built from depsgraph-evaluated topology, since
  FONT geometry is realized identically): BRUNO letters, kiosk body, controls signs,
  bonfire base, sword, gizmo etc. — full topology + UVs from _FROM_BLEND/<name>.json.
- 30 EMPTY objects: ref-markers (refZoneBounding, refZoneFrustum, the 3 interactive
  points) + collider primitives (cuboid.*, tube.*) parented to their physical hosts.
- All Bruno's userData restored as Blender custom properties (the 10 letter meshes
  each get `mass=0.2`).
- Material assignments by name (palette, redGradient, emissiveOrangeRadialGradient,
  stylizedMap) — the materials already exist from Phase 2.
- Parent relationships preserved (cuboids → physicals, sub-collection nesting).

Important: object transforms are restored via matrix_world from bruno-blend.json so
the result is positionally identical to Bruno's source, even though Blender's internal
matrix_basis values will differ (Bruno uses matrix_parent_inverse to cancel out
parent transforms; we set matrix_world directly and let Blender compute the basis).

How to run (Blender GUI):

  1. Open 02-materials.blend (File → Open).
  2. Switch to the "Scripting" workspace.
  3. New text block → paste this script → Run Script (or Alt+P).
  4. Watch /tmp/blender-phase-3.log for "built object: <name>" lines (54 of them).
  5. In the 3D viewport: zoom in on world coords roughly (47, -38) — that's where
     the landing area lives. You should see the BRUNO letters lined up, a kiosk,
     a controls sign, and a bonfire base near the southern shoreline.
  6. File → Save As → /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/03-landing.blend

How to run (CLI, headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/02-materials.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/03-landing-area.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/03-landing.blend

What you should see after running:

- Outliner: Scene Collection > terrain (unchanged) + areas > landing > {title.001,
  controls, kiosk, bonfire} with the 54 objects nested per Bruno's structure.
- 3D viewport: 10 individual BRUNO/S letter meshes lined up at approximately
  (45, -41, 0.75); a kiosk + controls signage cluster near (54, -30, 1); a bonfire
  base and sword at (56, -47, 0); zone-marker empties as small + axes at the area
  center (49, -38, 3.3) showing the bounding/frustum cylinder radii.
- N-panel → Item → Custom Properties: clicking any of the 10 refLetters* objects
  shows `mass = 0.2`.
- Console: "Built X meshes + Y empties + Z fonts. Z parent links resolved."

What to report back:

- "Worked, viewport shows <whatever>" → I produce Phase 4 (roads + scenery).
- "Worked but viewport shows <different>" → I diagnose.
- "Failed with error <message>" → paste the "=== PHASE 3 FAILED:" line.
"""

import bpy
import bmesh
import json
import os
import sys
import traceback
from pathlib import Path
import mathutils

REPORTS_DIR = Path('/Users/mahajankaran/Documents/Projects/karan-portfolio/reports')
OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
LOG_PATH = Path('/tmp/blender-phase-3.log')

BRUNO_BLEND_JSON = REPORTS_DIR / 'bruno-blend.json'
FB_DIR = REPORTS_DIR / 'bruno-mesh-topology' / '_FROM_BLEND'

TARGET_AREA = 'landing'
PARENT_COLLECTION_NAME = 'areas'  # we add `areas` then `landing` underneath

# Blender-internal custom properties we should not copy
INTERNAL_PROP_KEYS = {'cycles', 'cycles_visibility', '_RNA_UI'}


def log(msg):
    print(msg)
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(str(msg) + '\n')
    except Exception:
        pass


def parse_args():
    if '--' not in sys.argv:
        return None
    rest = sys.argv[sys.argv.index('--') + 1:]
    if '--out' in rest:
        i = rest.index('--out')
        if i + 1 < len(rest):
            return rest[i + 1]
    return None


def assert_blender_version():
    v = bpy.app.version
    if v < (4, 0, 0):
        raise RuntimeError(
            f'Targets Blender 5.x; detected {bpy.app.version_string}.'
        )
    log(f'Blender version: {bpy.app.version_string}')


# ─── Source-data helpers ────────────────────────────────────────────────────

def find_collection_node(tree, name):
    if tree.get('name') == name:
        return tree
    for c in tree.get('children', []):
        r = find_collection_node(c, name)
        if r is not None:
            return r
    return None


def load_blend_data():
    log(f'Reading {BRUNO_BLEND_JSON.name} ({BRUNO_BLEND_JSON.stat().st_size / 1024 / 1024:.1f} MB)')
    with open(BRUNO_BLEND_JSON) as f:
        d = json.load(f)
    objs_by_name = {o['name']: o for o in d['scenes'][0]['objects']}
    ct = d['scenes'][0]['collection_tree']
    landing_tree = find_collection_node(ct, TARGET_AREA)
    if landing_tree is None:
        raise RuntimeError(f'Could not find {TARGET_AREA!r} collection in scene tree')
    return objs_by_name, landing_tree


# ─── Idempotent cleanup ─────────────────────────────────────────────────────

def remove_prior_landing(landing_tree, objs_by_name):
    """Remove any objects/meshes/collections this script previously created."""
    names_to_remove = set(landing_tree.get('all_object_names', []))
    # Remove objects first
    removed_objs = 0
    for name in list(names_to_remove):
        o = bpy.data.objects.get(name)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
            removed_objs += 1
    # Remove collections (landing + sub-collections + parent areas if empty)
    sub_coll_names = [landing_tree['name']]
    for c in landing_tree.get('children', []):
        sub_coll_names.append(c['name'])
    for cname in sub_coll_names:
        coll = bpy.data.collections.get(cname)
        if coll is not None:
            bpy.data.collections.remove(coll)
    # The `areas` collection might exist but be empty now — leave it for re-use
    # Orphaned mesh data
    orphan_meshes = 0
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)
            orphan_meshes += 1
    if removed_objs or orphan_meshes:
        log(f'Cleared prior Phase 3 output: {removed_objs} objects, {orphan_meshes} orphan meshes')


# ─── Mesh building from _FROM_BLEND topology ────────────────────────────────

def build_mesh_from_topology(obj_name):
    """Build a Blender mesh datablock from _FROM_BLEND/<obj_name>.json."""
    src = FB_DIR / f'{obj_name}.json'
    if not src.exists():
        log(f'  WARN: no topology for {obj_name!r}, creating empty mesh')
        return bpy.data.meshes.new(f'{obj_name}_data'), []

    with open(src) as f:
        topo = json.load(f)

    mesh = bpy.data.meshes.new(topo.get('mesh_name') or f'{obj_name}_data')
    mat_slots = topo.get('material_slots', [])

    verts = topo['vertices']
    tri_inds = topo['triangle_indices']
    tri_loop_inds = topo.get('triangle_loop_indices', [])
    uv_layers = topo.get('uv_layers', {})

    if not verts or not tri_inds:
        return mesh, mat_slots

    bm = bmesh.new()
    bm_verts = [bm.verts.new(tuple(v)) for v in verts]
    bm.verts.ensure_lookup_table()

    valid_tri_count = 0
    valid_face_indices = []  # tracks which tri indices made it for UV alignment
    for i, tri in enumerate(tri_inds):
        try:
            bm.faces.new([bm_verts[idx] for idx in tri])
            valid_face_indices.append(i)
            valid_tri_count += 1
        except (ValueError, IndexError):
            pass
    bm.faces.ensure_lookup_table()

    # UVs
    for uv_name, uv_data in uv_layers.items():
        if not uv_data:
            continue
        try:
            uv_layer = bm.loops.layers.uv.new(uv_name)
        except (ValueError, RuntimeError):
            continue
        for face_i, face in enumerate(bm.faces):
            src_tri = valid_face_indices[face_i] if face_i < len(valid_face_indices) else face_i
            if src_tri >= len(tri_loop_inds):
                break
            tlis = tri_loop_inds[src_tri]
            for k, loop in enumerate(face.loops):
                if k >= len(tlis):
                    continue
                loop_idx = tlis[k]
                if 0 <= loop_idx < len(uv_data):
                    u, v = uv_data[loop_idx]
                    loop[uv_layer].uv = (u, v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh, mat_slots


# ─── Object construction ────────────────────────────────────────────────────

def make_object(obj_info):
    """Create a Blender object for one entry in bruno-blend.json's scenes[0].objects."""
    name = obj_info['name']
    obj_type = obj_info['type']

    if obj_type in ('MESH', 'FONT'):
        # FONT TextCurves are evaluated to mesh in the depsgraph dump
        mesh, mat_slots = build_mesh_from_topology(name)
        obj = bpy.data.objects.new(name, mesh)
        # Attach materials by name (created in Phase 2)
        for slot_name in mat_slots:
            mat = bpy.data.materials.get(slot_name)
            mesh.materials.append(mat)  # None if Phase 2 hadn't created it
    elif obj_type == 'EMPTY':
        obj = bpy.data.objects.new(name, None)
        # Choose a display type that makes ref/zone markers obvious in the viewport
        n_lower = name.lower()
        if any(p in n_lower for p in ('zonebounding', 'zonefrustum', 'waterfallzone')):
            obj.empty_display_type = 'CIRCLE'
            obj.empty_display_size = 1.0
        elif 'interactivepoint' in n_lower:
            obj.empty_display_type = 'PLAIN_AXES'
            obj.empty_display_size = 1.0
        elif n_lower.startswith(('cuboid', 'tube', 'ball', 'hull', 'trimesh')):
            obj.empty_display_type = 'CUBE' if n_lower.startswith('cuboid') else 'SPHERE'
            obj.empty_display_size = 0.5
        else:
            obj.empty_display_type = 'PLAIN_AXES'
            obj.empty_display_size = 0.5
    else:
        log(f'  WARN: unsupported obj type {obj_type!r} for {name}; created as empty')
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'

    # Custom properties (Bruno's userData — mass, preventAutoAdd, etc.)
    for k, v in (obj_info.get('custom_properties') or {}).items():
        if k in INTERNAL_PROP_KEYS:
            continue
        try:
            obj[k] = v
        except (TypeError, ValueError):
            pass

    # Visibility flags
    obj.hide_render = obj_info.get('hide_render', False)
    obj.hide_viewport = obj_info.get('hide_viewport', False)

    return obj


def set_object_world_transform(obj, matrix_world_list):
    """Apply Bruno's matrix_world directly."""
    mw = mathutils.Matrix(matrix_world_list)
    obj.matrix_world = mw


# ─── Collection wiring ──────────────────────────────────────────────────────

def get_or_create_collection(name, parent_coll):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    # Make sure it's linked under parent_coll
    if coll.name not in [c.name for c in parent_coll.children]:
        parent_coll.children.link(coll)
    return coll


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log('=' * 60)
    log(f'Phase 3: Landing area geometry ({TARGET_AREA})')
    log('=' * 60)

    assert_blender_version()
    objs_by_name, landing_tree = load_blend_data()

    # Sanity check Phase 2 ran
    if not bpy.data.materials.get('palette'):
        log('WARN: no `palette` material found — did you open 02-materials.blend? '
            'Continuing, but mesh material slots will end up empty.')

    remove_prior_landing(landing_tree, objs_by_name)

    # Build collection hierarchy: Scene > areas > landing > {title.001, controls, kiosk, bonfire}
    scene_coll = bpy.context.scene.collection
    areas_coll = get_or_create_collection(PARENT_COLLECTION_NAME, scene_coll)
    landing_coll = get_or_create_collection(landing_tree['name'], areas_coll)

    sub_colls = {}
    for sub in landing_tree.get('children', []):
        sub_colls[sub['name']] = get_or_create_collection(sub['name'], landing_coll)

    # Track which collection each object's name belongs to
    obj_to_coll = {n: landing_coll for n in landing_tree.get('object_names', [])}
    for sub in landing_tree.get('children', []):
        sc = sub_colls[sub['name']]
        for n in sub.get('object_names', []):
            obj_to_coll[n] = sc

    # Pass 1: Create all objects without parents
    log('')
    log('Pass 1: creating objects')
    created = {}
    mesh_count = 0
    empty_count = 0
    font_count = 0
    for name in landing_tree['all_object_names']:
        obj_info = objs_by_name.get(name)
        if obj_info is None:
            log(f'  WARN: object {name!r} listed in collection but not in objects[]; skipping')
            continue
        obj = make_object(obj_info)

        # Link to its declared collection (default to landing if unknown)
        coll = obj_to_coll.get(name, landing_coll)
        coll.objects.link(obj)
        created[name] = obj

        otype = obj_info['type']
        if otype == 'MESH':
            mesh_count += 1
        elif otype == 'FONT':
            font_count += 1
        elif otype == 'EMPTY':
            empty_count += 1

        log(
            f'  built {otype:5s}: {name:38s} mats={[m.name if m else None for m in obj.data.materials] if obj.type == "MESH" else "-"}'
        )

    # Pass 2: Apply world transforms (no parents yet, so matrix_world == matrix_basis)
    log('')
    log('Pass 2: applying world transforms')
    for name, obj in created.items():
        obj_info = objs_by_name[name]
        set_object_world_transform(obj, obj_info['matrix_world'])
    bpy.context.view_layer.update()

    # Pass 3: Set parents + restore matrix_world (Blender computes matrix_parent_inverse)
    log('')
    log('Pass 3: setting parent hierarchy')
    parent_links = 0
    skipped_parents = 0
    for name, obj in created.items():
        parent_name = objs_by_name[name].get('parent')
        if not parent_name:
            continue
        parent_obj = created.get(parent_name) or bpy.data.objects.get(parent_name)
        if parent_obj is None:
            skipped_parents += 1
            continue
        saved_mw = obj.matrix_world.copy()
        obj.parent = parent_obj
        # Restoring matrix_world tells Blender to compute matrix_parent_inverse so
        # the world position is preserved.
        obj.matrix_world = saved_mw
        parent_links += 1
    bpy.context.view_layer.update()

    # Summary
    log('')
    log('── Summary ────────────────────────────────────────')
    log(f'  Total objects built: {len(created)}  '
        f'(MESH={mesh_count}, EMPTY={empty_count}, FONT={font_count})')
    log(f'  Parent links resolved: {parent_links}'
        + (f', skipped {skipped_parents}' if skipped_parents else ''))
    log(f'  Collections: areas > {landing_tree["name"]} > '
        f'{{{", ".join(sub_colls.keys())}}}')

    # Visual nicety: select the BRUNO letters so they're easy to find in the viewport
    if 'refLettersPhysicalDynamic.015' in created:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        letters_to_select = [
            o for n, o in created.items()
            if n.startswith('refLettersPhysicalDynamic')
        ]
        for o in letters_to_select:
            o.select_set(True)
        if letters_to_select:
            bpy.context.view_layer.objects.active = letters_to_select[0]

    log('')
    log('Phase 3 complete.')
    log(f'>>> Save this file as: {OUTPUT_DIR / "03-landing.blend"} via File → Save As')
    log('>>> In the 3D viewport press Numpad . to frame the selected BRUNO letters '
        '(or just zoom out and pan to roughly (47, -38)).')

    out_path = parse_args()
    if out_path:
        bpy.ops.wm.save_as_mainfile(filepath=out_path)
        log(f'(CLI --out: saved to {out_path})')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log(tb)
        last_line = tb.strip().splitlines()[-1] if tb.strip() else 'unknown'
        log(f'=== PHASE 3 FAILED: {last_line} ===')
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
