"""
Phase 5: World-wide foliage + ground props

Input  : 04-roads-scenery.blend (Phase 4 output)
Output : 05-foliage.blend

What this adds — 506 objects across 11 collections:
- bushes (130 Icospheres, varied scales — bushy ground decoration)
- flowers (108 identical 3 m clumps)
- bricks (30 uniform 1.12 × 1.50 × 0.75 m blocks)
- oakTrees > {archives.001, visual.004, references.002} — 7 visual mesh variants +
  24 reference curves (Bruno scatters tree instances along these curves via
  Geometry Nodes — see GAP-B-002)
- birchTrees > {archives.002, visual.002, references} — 7 visual variants + 26
  reference MESH markers (birches don't use curves; they're directly placed)
- cherryTrees > {archives, visual.005, references.003} — 7 visual variants +
  20 reference curves (curve-based like oak)
- lanterns (17 unique positions × 3 sub-objects = 51 objects: 34 mesh + 17 empty)
- poleLights (26 unique × 3 = 39)
- benches (7 visual variants × 21 markers)
- fences (32 panels)
- grass (1 tile reference)

Because Bruno applies Geometry Nodes modifiers at GLB export time, the
oak/cherry tree CURVE references will appear in the viewport as visible Bezier
outlines, NOT as the scattered trees you'd see at runtime. This is GAP-B-002.
Birch references are MESH so they ARE the visible placements — birches will
look correct after this phase.

How to run (Blender GUI):

  1. Open 04-roads-scenery.blend.
  2. Scripting workspace → paste this script → Run Script (or Alt+P).
  3. WARNING — this phase processes 506 objects. Estimated runtime: ~3 minutes.
     Blender will appear unresponsive during the bmesh builds. That's normal.
     Watch /tmp/blender-phase-5.log for progress; it logs every ~50 objects.
  4. When complete, the 3D viewport shows the landscape populated with bushes,
     flowers, trees (birches in clusters; oak/cherry as curve outlines per
     GAP-B-002), lanterns + pole lights at intervals, benches in rows.
  5. File → Save As → /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/05-foliage.blend

How to run (CLI, headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/04-roads-scenery.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/05-foliage.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/05-foliage.blend

What you should see after running:

- Outliner: 11 new top-level collections (bushes, flowers, bricks, oakTrees,
  birchTrees, cherryTrees, lanterns, poleLights, benches, fences, grass)
- 3D viewport: a populated world. Birches in stands, bushes carpet the ground,
  flowers scattered, brick piles at choke points, lanterns marking lit areas.
- Outliner Blender Data view → Objects: total count now around 620 (previous
  phases ~110 + this phase 506).

What to report back:

- "Worked, viewport shows <whatever>" → I produce Phase 6 (lights + export).
- "Worked but viewport shows <different>" → I diagnose.
- "Failed with error <message>" → paste the "=== PHASE 5 FAILED:" line.
- "Way too slow — Blender hung" → I can split into 5a/5b sub-phases.
"""

import bpy
import bmesh
import json
import os
import sys
import time
import traceback
from pathlib import Path
import mathutils

REPORTS_DIR = Path('/Users/mahajankaran/Documents/Projects/karan-portfolio/reports')
OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
LOG_PATH = Path('/tmp/blender-phase-5.log')

BRUNO_BLEND_JSON = REPORTS_DIR / 'bruno-blend.json'
BRUNO_CURVES_JSON = REPORTS_DIR / 'bruno-curves.json'
FB_DIR = REPORTS_DIR / 'bruno-mesh-topology' / '_FROM_BLEND'

TARGET_COLLECTIONS = [
    'bushes', 'flowers', 'bricks',
    'oakTrees', 'birchTrees', 'cherryTrees',
    'lanterns', 'poleLights', 'benches', 'fences',
    'grass',
]

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


# ─── Mesh + Curve builders (shared from Phase 4) ────────────────────────────

def build_mesh_from_topology(obj_name):
    src = FB_DIR / f'{obj_name}.json'
    if not src.exists():
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


def build_curve_from_dump(obj_name, curve_dump):
    name = curve_dump.get('curve_name') or f'{obj_name}_data'
    cd = bpy.data.curves.new(name=name, type='CURVE')
    cd.dimensions = curve_dump.get('dimensions', '3D')
    if 'resolution_u' in curve_dump:
        cd.resolution_u = curve_dump['resolution_u']
    if 'render_resolution_u' in curve_dump:
        cd.render_resolution_u = curve_dump['render_resolution_u']
    if 'fill_mode' in curve_dump:
        try:
            cd.fill_mode = curve_dump['fill_mode']
        except (TypeError, ValueError):
            pass
    if 'extrude' in curve_dump:
        cd.extrude = curve_dump['extrude']
    if 'bevel_depth' in curve_dump:
        cd.bevel_depth = curve_dump['bevel_depth']
    if 'bevel_resolution' in curve_dump:
        cd.bevel_resolution = curve_dump['bevel_resolution']
    for flag in ('use_radius', 'use_stretch', 'use_deform_bounds'):
        if flag in curve_dump:
            try:
                setattr(cd, flag, curve_dump[flag])
            except (AttributeError, TypeError):
                pass
    for sd in curve_dump.get('splines', []):
        spl_type = sd.get('type', 'BEZIER')
        try:
            spline = cd.splines.new(spl_type)
        except RuntimeError:
            continue
        if spl_type == 'BEZIER':
            bps = sd.get('bezier_points', [])
            if len(bps) > 1:
                spline.bezier_points.add(len(bps) - 1)
            for i, bp_data in enumerate(bps):
                bp = spline.bezier_points[i]
                if 'co' in bp_data: bp.co = bp_data['co']
                if 'handle_left' in bp_data: bp.handle_left = bp_data['handle_left']
                if 'handle_right' in bp_data: bp.handle_right = bp_data['handle_right']
                try:
                    if 'handle_left_type' in bp_data: bp.handle_left_type = bp_data['handle_left_type']
                    if 'handle_right_type' in bp_data: bp.handle_right_type = bp_data['handle_right_type']
                except (TypeError, ValueError):
                    pass
                if bp_data.get('radius') is not None: bp.radius = bp_data['radius']
                if bp_data.get('tilt') is not None: bp.tilt = bp_data['tilt']
        else:
            pts = sd.get('points', [])
            if len(pts) > 1:
                spline.points.add(len(pts) - 1)
            for i, p_data in enumerate(pts):
                p = spline.points[i]
                if 'co' in p_data: p.co = p_data['co']
                if p_data.get('radius') is not None: p.radius = p_data['radius']
                if p_data.get('tilt') is not None: p.tilt = p_data['tilt']
        spline.use_cyclic_u = sd.get('cyclic_u', False)
        if 'resolution_u' in sd: spline.resolution_u = sd['resolution_u']
    return cd


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
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = 0.5
    else:
        log(f'  WARN: unsupported type {obj_type!r} for {name}; created as empty')
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


def walk_collection_obj_map(node, default_coll, mapping, coll_lookup, scene_coll):
    """Populate mapping[obj_name] = host_collection, recursively walking sub-colls."""
    cn = node['name']
    host = coll_lookup.get(cn) or default_coll
    for n in node.get('object_names', []):
        mapping[n] = host
    for child in node.get('children', []):
        sub_coll = get_or_create_collection(child['name'], host)
        coll_lookup[child['name']] = sub_coll
        walk_collection_obj_map(child, sub_coll, mapping, coll_lookup, scene_coll)


# ─── Idempotent cleanup ─────────────────────────────────────────────────────

def remove_prior(target_nodes):
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

    orphan_meshes = sum(1 for m in list(bpy.data.meshes) if m.users == 0)
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)
    orphan_curves = sum(1 for c in list(bpy.data.curves) if c.users == 0)
    for c in list(bpy.data.curves):
        if c.users == 0:
            bpy.data.curves.remove(c)

    if removed_objs or removed_colls:
        log(f'Cleared prior Phase 5: {removed_objs} objects, {removed_colls} collections, '
            f'{orphan_meshes} orphan meshes, {orphan_curves} orphan curves')


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time.monotonic()
    log('=' * 60)
    log('Phase 5: World-wide foliage + ground props')
    log('=' * 60)

    assert_blender_version()
    objs_by_name, ct = load_blend_data()
    curves_dump = load_curves_data()

    if not bpy.data.materials.get('palette'):
        log('WARN: no `palette` material — open 04-roads-scenery.blend or later. Continuing.')

    target_nodes = []
    for t in TARGET_COLLECTIONS:
        n = find_collection_node(ct, t)
        if n is None:
            log(f'WARN: collection {t!r} not found in scene tree')
            continue
        target_nodes.append(n)

    if not target_nodes:
        raise RuntimeError('No target collections found')

    remove_prior(target_nodes)

    scene_coll = bpy.context.scene.collection
    coll_lookup = {}  # name -> bpy collection
    obj_to_coll = {}  # obj_name -> bpy collection
    for tn in target_nodes:
        root_coll = get_or_create_collection(tn['name'], scene_coll)
        coll_lookup[tn['name']] = root_coll
        walk_collection_obj_map(tn, root_coll, obj_to_coll, coll_lookup, scene_coll)

    all_target_names = []
    for tn in target_nodes:
        all_target_names.extend(tn.get('all_object_names', []))

    log('')
    log(f'Pass 1: creating {len(all_target_names)} objects (this is the slow part)')
    created = {}
    type_counts = {'MESH': 0, 'EMPTY': 0, 'CURVE': 0, 'FONT': 0}
    progress_interval = max(50, len(all_target_names) // 20)
    t_pass1 = time.monotonic()
    for i, name in enumerate(all_target_names):
        obj_info = objs_by_name.get(name)
        if obj_info is None:
            continue
        obj = make_object(obj_info, curves_dump)
        coll = obj_to_coll.get(name, scene_coll)
        coll.objects.link(obj)
        created[name] = obj
        type_counts[obj_info['type']] = type_counts.get(obj_info['type'], 0) + 1
        if (i + 1) % progress_interval == 0:
            elapsed = time.monotonic() - t_pass1
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (len(all_target_names) - i - 1) / rate if rate > 0 else 0
            log(f'  [{i + 1}/{len(all_target_names)}] built — {rate:.1f} obj/s, ETA {eta:.0f}s')

    log(f'  Pass 1 done in {time.monotonic() - t_pass1:.1f}s. Counts: {type_counts}')

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

    elapsed = time.monotonic() - t0
    log('')
    log('── Summary ────────────────────────────────────────')
    log(f'  Total objects built: {len(created)}  {type_counts}')
    log(f'  Parent links: {parent_links}'
        + (f', skipped {skipped_parents}' if skipped_parents else ''))
    log(f'  Collections: {[tn["name"] for tn in target_nodes]}')
    log(f'  Total wall-clock: {elapsed:.1f}s')

    log('')
    log('Phase 5 complete.')
    log(f'>>> Save this file as: {OUTPUT_DIR / "05-foliage.blend"} via File → Save As')
    log('>>> NOTE: oak + cherry tree references are CURVE objects that Bruno used '
        'with Geometry Nodes to scatter trees. Without GN, you see just the curve '
        'outlines — that is GAP-B-002. Birches use MESH references so they look correct.')

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
        log(f'=== PHASE 5 FAILED: {last_line} ===')
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
