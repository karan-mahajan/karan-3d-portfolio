"""
Phase 4: Roads + scenery (world-wide static dressing)

Input  : 03-landing.blend (Phase 3 output)
Output : 04-roads-scenery.blend

What this adds:
- `scenery.002` collection with 5 sub-collections (`bridges`, `rocks`, `basaltRocks`,
  `slabs`, `road.001`) — 39 objects total (32 MESH + 6 EMPTY + 1 CURVE)
  including the 12 road tile cubes covering the playable area
- The master `curveRoad` Bezier curve (27 control points, extrude=5.0 → 10 m road
  ribbon visible in viewport) — wired from `bruno-curves.json` since CURVE objects
  aren't in `_FROM_BLEND/`
- `refRoad` mesh — the visible road surface that the runtime uses
- `respawns` collection with 17 EMPTY markers (respawnLanding, respawnBonfire, …,
  respawnCircuit) — `Game.js` uses these to teleport the vehicle
- All transforms via matrix_world directly from `bruno-blend.json`, parents
  preserved via the same restore-after-parent trick as Phase 3.

Generalised: object construction now handles MESH + EMPTY + FONT + CURVE in one
helper, so Phase 5 (foliage) can reuse it for the 47 `treeBody.*` curves.

How to run (Blender GUI):

  1. Open 03-landing.blend (File → Open).
  2. Switch to the "Scripting" workspace.
  3. New text block → paste this script → Run Script.
  4. Watch /tmp/blender-phase-4.log for ~56 "built object" lines plus the
     "built CURVE: curveRoad" entry with its 27 bezier points.
  5. In the 3D viewport, you should now see:
       - A grey ribbon snaking across the world (the curveRoad with its 5 m
         extrude making it ~10 m wide)
       - Square road-tile chunks (Cube.049 .. Cube.079, mostly grey palette)
       - Bridges + scattered rocks + slabs around the landing area
       - 17 small empty markers at respawn points (mostly z = 0.5 m)
  6. File → Save As → /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/04-roads-scenery.blend

How to run (CLI, headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/03-landing.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/04-roads-and-scenery.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/04-roads-scenery.blend

What you should see after running:

- Outliner: Scene Collection > terrain + areas/landing/* (Phase 3) + NEW:
  scenery.002 > {bridges, rocks, basaltRocks, slabs, road.001} + respawns
- 3D viewport: the road ribbon spans most of the world's 170 m extent; flat
  road tiles overlap with the terrain near z=0; rocks and bridges sit on the
  ground; respawn empties are small axes markers at known coords.
- Total: roughly 110 objects in the file (Phase 1 terrain + Phase 3's 54 +
  this Phase's 56).

What to report back:

- "Worked, viewport shows <whatever>" → I produce Phase 5 (foliage).
- "Worked but viewport shows <different>" → I diagnose.
- "Failed with error <message>" → paste the "=== PHASE 4 FAILED:" line.
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
LOG_PATH = Path('/tmp/blender-phase-4.log')

BRUNO_BLEND_JSON = REPORTS_DIR / 'bruno-blend.json'
BRUNO_CURVES_JSON = REPORTS_DIR / 'bruno-curves.json'
FB_DIR = REPORTS_DIR / 'bruno-mesh-topology' / '_FROM_BLEND'

TARGET_COLLECTIONS = ['scenery.002', 'respawns']

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
        raise RuntimeError(f'Targets Blender 5.x; detected {bpy.app.version_string}.')
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
    log(f'Reading {BRUNO_BLEND_JSON.name}')
    with open(BRUNO_BLEND_JSON) as f:
        d = json.load(f)
    objs_by_name = {o['name']: o for o in d['scenes'][0]['objects']}
    ct = d['scenes'][0]['collection_tree']
    return objs_by_name, ct


def load_curves_data():
    log(f'Reading {BRUNO_CURVES_JSON.name}')
    with open(BRUNO_CURVES_JSON) as f:
        return json.load(f)


# ─── Mesh building ──────────────────────────────────────────────────────────

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

    verts = topo.get('vertices') or []
    tri_inds = topo.get('triangle_indices') or []
    tri_loop_inds = topo.get('triangle_loop_indices', [])
    uv_layers = topo.get('uv_layers', {})

    if not verts or not tri_inds:
        return mesh, mat_slots

    bm = bmesh.new()
    bm_verts = [bm.verts.new(tuple(v)) for v in verts]
    bm.verts.ensure_lookup_table()

    valid_face_indices = []
    for i, tri in enumerate(tri_inds):
        try:
            bm.faces.new([bm_verts[idx] for idx in tri])
            valid_face_indices.append(i)
        except (ValueError, IndexError):
            pass
    bm.faces.ensure_lookup_table()

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
                    loop[uv_layer].uv = uv_data[loop_idx]

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh, mat_slots


# ─── Curve building ─────────────────────────────────────────────────────────

def build_curve_from_dump(obj_name, curve_dump):
    """Build a Blender Curve datablock from one entry in bruno-curves.json."""
    name = curve_dump.get('curve_name') or f'{obj_name}_data'
    curve_data = bpy.data.curves.new(name=name, type='CURVE')

    curve_data.dimensions = curve_dump.get('dimensions', '3D')
    if 'resolution_u' in curve_dump:
        curve_data.resolution_u = curve_dump['resolution_u']
    if 'render_resolution_u' in curve_dump:
        curve_data.render_resolution_u = curve_dump['render_resolution_u']
    if 'fill_mode' in curve_dump:
        try:
            curve_data.fill_mode = curve_dump['fill_mode']
        except (TypeError, ValueError):
            pass
    if 'extrude' in curve_dump:
        curve_data.extrude = curve_dump['extrude']
    if 'bevel_depth' in curve_dump:
        curve_data.bevel_depth = curve_dump['bevel_depth']
    if 'bevel_resolution' in curve_dump:
        curve_data.bevel_resolution = curve_dump['bevel_resolution']
    for flag in ('use_radius', 'use_stretch', 'use_deform_bounds'):
        if flag in curve_dump:
            try:
                setattr(curve_data, flag, curve_dump[flag])
            except (AttributeError, TypeError):
                pass

    for spline_data in curve_dump.get('splines', []):
        spl_type = spline_data.get('type', 'BEZIER')
        try:
            spline = curve_data.splines.new(spl_type)
        except RuntimeError as e:
            log(f'  WARN: cannot create {spl_type} spline on {obj_name}: {e}')
            continue

        if spl_type == 'BEZIER':
            bps = spline_data.get('bezier_points', [])
            # splines.new('BEZIER') already creates 1 bezier point, so add N-1
            if len(bps) > 1:
                spline.bezier_points.add(len(bps) - 1)
            for i, bp_data in enumerate(bps):
                bp = spline.bezier_points[i]
                if 'co' in bp_data:
                    bp.co = bp_data['co']
                if 'handle_left' in bp_data:
                    bp.handle_left = bp_data['handle_left']
                if 'handle_right' in bp_data:
                    bp.handle_right = bp_data['handle_right']
                if 'handle_left_type' in bp_data:
                    try:
                        bp.handle_left_type = bp_data['handle_left_type']
                    except (TypeError, ValueError):
                        pass
                if 'handle_right_type' in bp_data:
                    try:
                        bp.handle_right_type = bp_data['handle_right_type']
                    except (TypeError, ValueError):
                        pass
                if 'radius' in bp_data and bp_data['radius'] is not None:
                    bp.radius = bp_data['radius']
                if 'tilt' in bp_data and bp_data['tilt'] is not None:
                    bp.tilt = bp_data['tilt']
                if bp_data.get('weight') is not None:
                    bp.weight_softbody = bp_data['weight']
        else:
            # NURBS / POLY — populate spline.points
            pts = spline_data.get('points', [])
            if len(pts) > 1:
                spline.points.add(len(pts) - 1)
            for i, p_data in enumerate(pts):
                p = spline.points[i]
                if 'co' in p_data:
                    p.co = p_data['co']
                if 'radius' in p_data and p_data['radius'] is not None:
                    p.radius = p_data['radius']
                if 'tilt' in p_data and p_data['tilt'] is not None:
                    p.tilt = p_data['tilt']

        spline.use_cyclic_u = spline_data.get('cyclic_u', False)
        if 'resolution_u' in spline_data:
            spline.resolution_u = spline_data['resolution_u']
        if 'order_u' in spline_data and spl_type in ('NURBS', 'POLY'):
            try:
                spline.order_u = spline_data['order_u']
            except (TypeError, ValueError):
                pass
        if 'use_endpoint_u' in spline_data and spl_type in ('NURBS', 'POLY'):
            try:
                spline.use_endpoint_u = spline_data['use_endpoint_u']
            except AttributeError:
                pass

    return curve_data


# ─── Object construction ────────────────────────────────────────────────────

def make_object(obj_info, curves_dump):
    name = obj_info['name']
    obj_type = obj_info['type']

    if obj_type in ('MESH', 'FONT'):
        mesh, mat_slots = build_mesh_from_topology(name)
        obj = bpy.data.objects.new(name, mesh)
        for slot_name in mat_slots:
            mat = bpy.data.materials.get(slot_name)
            mesh.materials.append(mat)
    elif obj_type == 'CURVE':
        cdump = curves_dump.get(name)
        if cdump is None:
            log(f'  WARN: no curve dump for {name!r}, creating empty curve')
            cd = bpy.data.curves.new(name=f'{name}_data', type='CURVE')
        else:
            cd = build_curve_from_dump(name, cdump)
        obj = bpy.data.objects.new(name, cd)
    elif obj_type == 'EMPTY':
        obj = bpy.data.objects.new(name, None)
        n_lower = name.lower()
        if 'respawn' in n_lower:
            obj.empty_display_type = 'PLAIN_AXES'
            obj.empty_display_size = 1.0
        elif any(p in n_lower for p in ('zonebounding', 'zonefrustum', 'waterfallzone')):
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

    for k, v in (obj_info.get('custom_properties') or {}).items():
        if k in INTERNAL_PROP_KEYS:
            continue
        try:
            obj[k] = v
        except (TypeError, ValueError):
            pass

    obj.hide_render = obj_info.get('hide_render', False)
    obj.hide_viewport = obj_info.get('hide_viewport', False)

    return obj


def set_object_world_transform(obj, matrix_world_list):
    obj.matrix_world = mathutils.Matrix(matrix_world_list)


# ─── Collection wiring ──────────────────────────────────────────────────────

def get_or_create_collection(name, parent_coll):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    if coll.name not in [c.name for c in parent_coll.children]:
        parent_coll.children.link(coll)
    return coll


def collect_target_objects(ct, target_names):
    """Returns a list of (collection_node, [object_names]) tuples for each target."""
    out = []
    for tn in target_names:
        node = find_collection_node(ct, tn)
        if node is None:
            log(f'WARN: collection {tn!r} not found in scene tree')
            continue
        out.append(node)
    return out


def walk_for_object_collection_map(node, current_coll, mapping):
    """Recursively populate mapping[obj_name] = collection_name for all descendants."""
    for n in node.get('object_names', []):
        mapping[n] = current_coll
    for child in node.get('children', []):
        walk_for_object_collection_map(child, child['name'], mapping)


# ─── Idempotent cleanup ─────────────────────────────────────────────────────

def remove_prior_phase4(target_nodes):
    """Remove any objects/collections this script previously created."""
    all_names = set()
    coll_names_to_remove = set()

    def gather(node):
        coll_names_to_remove.add(node['name'])
        for n in node.get('object_names', []):
            all_names.add(n)
        for c in node.get('children', []):
            gather(c)

    for node in target_nodes:
        gather(node)

    removed_objs = 0
    for n in list(all_names):
        o = bpy.data.objects.get(n)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
            removed_objs += 1

    removed_colls = 0
    for cn in list(coll_names_to_remove):
        c = bpy.data.collections.get(cn)
        if c is not None:
            bpy.data.collections.remove(c)
            removed_colls += 1

    # Orphan datablocks
    orphan_meshes = 0
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)
            orphan_meshes += 1
    orphan_curves = 0
    for c in list(bpy.data.curves):
        if c.users == 0:
            bpy.data.curves.remove(c)
            orphan_curves += 1

    if removed_objs or removed_colls:
        log(f'Cleared prior Phase 4 output: {removed_objs} objects, {removed_colls} collections, '
            f'{orphan_meshes} orphan meshes, {orphan_curves} orphan curves')


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log('=' * 60)
    log('Phase 4: Roads + scenery + respawns')
    log('=' * 60)

    assert_blender_version()
    objs_by_name, ct = load_blend_data()
    curves_dump = load_curves_data()

    if not bpy.data.materials.get('palette'):
        log('WARN: no `palette` material in this scene — open 03-landing.blend (or later). '
            'Continuing, but mesh material slots will end up null.')

    target_nodes = collect_target_objects(ct, TARGET_COLLECTIONS)
    if not target_nodes:
        raise RuntimeError(f'None of {TARGET_COLLECTIONS} found in scene tree')

    remove_prior_phase4(target_nodes)

    scene_coll = bpy.context.scene.collection
    obj_to_coll = {}
    for tn in target_nodes:
        root_coll = get_or_create_collection(tn['name'], scene_coll)
        # Sub-collections of this target
        sub_colls = {}
        for child in tn.get('children', []):
            sub_colls[child['name']] = get_or_create_collection(child['name'], root_coll)
        # Map every object inside to its actual host collection
        for n in tn.get('object_names', []):
            obj_to_coll[n] = root_coll
        for child in tn.get('children', []):
            sc = sub_colls[child['name']]
            walk_into = [(child, sc)]
            while walk_into:
                node, host = walk_into.pop()
                for n in node.get('object_names', []):
                    obj_to_coll[n] = host
                for inner in node.get('children', []):
                    inner_coll = get_or_create_collection(inner['name'], host)
                    walk_into.append((inner, inner_coll))

    # Gather all object names from all target nodes
    all_target_names = []
    for tn in target_nodes:
        all_target_names.extend(tn.get('all_object_names', []))

    log('')
    log(f'Pass 1: creating {len(all_target_names)} objects')
    created = {}
    type_counts = {'MESH': 0, 'EMPTY': 0, 'CURVE': 0, 'FONT': 0}
    for name in all_target_names:
        obj_info = objs_by_name.get(name)
        if obj_info is None:
            log(f'  WARN: {name!r} listed but missing from objects[]')
            continue
        obj = make_object(obj_info, curves_dump)
        coll = obj_to_coll.get(name)
        if coll is None:
            log(f'  WARN: no collection mapped for {name!r}; linking to Scene root')
            coll = scene_coll
        coll.objects.link(obj)
        created[name] = obj
        type_counts[obj_info['type']] = type_counts.get(obj_info['type'], 0) + 1

        if obj_info['type'] == 'MESH':
            mats = [m.name if m else None for m in obj.data.materials]
            log(f'  built MESH : {name:38s} mats={mats}')
        elif obj_info['type'] == 'CURVE':
            n_pts = sum(len(s.bezier_points) + len(s.points) for s in obj.data.splines)
            log(f'  built CURVE: {name:38s} pts={n_pts} extrude={obj.data.extrude}')
        elif obj_info['type'] == 'FONT':
            log(f'  built FONT : {name}')
        else:
            log(f'  built {obj_info["type"]:5s}: {name}')

    log('')
    log('Pass 2: applying world transforms')
    for name, obj in created.items():
        set_object_world_transform(obj, objs_by_name[name]['matrix_world'])
    bpy.context.view_layer.update()

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
        obj.matrix_world = saved_mw
        parent_links += 1
    bpy.context.view_layer.update()

    log('')
    log('── Summary ────────────────────────────────────────')
    log(f'  Total objects built: {len(created)}  {type_counts}')
    log(f'  Parent links resolved: {parent_links}'
        + (f', skipped {skipped_parents}' if skipped_parents else ''))
    log(f'  Collections: {[tn["name"] for tn in target_nodes]}')

    log('')
    log('Phase 4 complete.')
    log(f'>>> Save this file as: {OUTPUT_DIR / "04-roads-scenery.blend"} via File → Save As')

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
        log(f'=== PHASE 4 FAILED: {last_line} ===')
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
