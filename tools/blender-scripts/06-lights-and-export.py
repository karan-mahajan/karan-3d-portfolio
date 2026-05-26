"""
Phase 6: Lights + cameras + world + GLB export

Input  : 05-foliage.blend (Phase 5 output)
Output : 06-final.blend  +  landing.glb (exported, comparable to Bruno's areas.glb)

What this adds:
- 2 Blender AREA lights — Bruno's `day` (warm) and `night` (cool) reference lights
  both at (17.53, -38.46, 105.82). They're not used at runtime, only as Blender-side
  visual reference while modelling — runtime uses a single THREE.DirectionalLight.
- 2 ORTHO Cameras — `cameraTerrain` and `cameraVehicle` (lens=50mm, sensor 36×24,
  clip 0.1–1000). Per bruno-blend-summary.md §8, these are reference cameras used to
  bake the terrain heightmap preview; runtime uses its own PerspectiveCamera(25°).
- World node tree: ShaderNodeBackground with the actual dark background color from
  bruno-blend.json. Wires Background → Output as Bruno has it.
- A new `lighting-ref` collection that hosts the lights + cameras (matches Bruno's
  grouping; the runtime ignores them via `export_lights=False`/`export_cameras=False`).

After the .blend is fully populated, exports the `areas` collection to GLB:
- `bruno-blend-recreate/landing.glb` — uncompressed master (comparable to Bruno's
  `static/areas/areas.glb`)
- Settings derived from `bruno-analysis.md` hints + bruno-blend-summary.md §11:
  `export_format='GLB'`, `use_active_collection=True`, `export_apply=True`,
  `export_yup=True`, `export_extras=True`, `export_animations=False`,
  `export_lights=False`, `export_cameras=False`
- GAP-B-003 in `blender-recreate-gaps.md` tracks export-preset uncertainty.

How to run (Blender GUI):

  1. Open 05-foliage.blend.
  2. Scripting workspace → paste this script → Run Script.
  3. Watch /tmp/blender-phase-6.log — you should see "built LIGHT", "built CAMERA",
     "world configured", and finally "GLB export complete: <bytes>".
  4. After it finishes, /Users/.../bruno-blend-recreate/landing.glb exists on disk.
     You can verify with `ls -lh bruno-blend-recreate/landing.glb` in Terminal.
  5. File → Save As → /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/06-final.blend

How to run (CLI, headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/05-foliage.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/06-lights-and-export.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/06-final.blend

What you should see after running:

- Outliner: a new `lighting-ref` collection with 4 entries (2 lights + 2 cameras).
- N-panel → Item with one of the lights selected: location (17.53, -38.46, 105.82),
  rotation ~(-0.67, 0, -4.38).
- World node tree (Shading workspace → World tab): 2 nodes, 1 link.
- File `bruno-blend-recreate/landing.glb` on disk — compare its size to Bruno's
  `static/areas/areas.glb` (≈3.1 MB uncompressed) for a rough sanity check.

What to report back:

- "Worked, exported landing.glb is <bytes>" → I produce the closing turn
  (comparison probe + final summary).
- "Worked but viewport shows <different>" → I diagnose.
- "Failed with error <message>" → paste the "=== PHASE 6 FAILED:" line.
"""

import bpy
import json
import os
import sys
import traceback
from pathlib import Path
import mathutils

REPORTS_DIR = Path('/Users/mahajankaran/Documents/Projects/karan-portfolio/reports')
OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
LOG_PATH = Path('/tmp/blender-phase-6.log')

BRUNO_BLEND_JSON = REPORTS_DIR / 'bruno-blend.json'

LIGHTING_COLL_NAME = 'lighting-ref'
GLB_OUTPUT_NAME = 'landing.glb'

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


def load_blend_data():
    log(f'Reading {BRUNO_BLEND_JSON.name}')
    with open(BRUNO_BLEND_JSON) as f:
        d = json.load(f)
    return d


def get_or_create_collection(name, parent_coll):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
    if coll.name not in [c.name for c in parent_coll.children]:
        parent_coll.children.link(coll)
    return coll


def safe_set(obj, attr, value):
    try:
        setattr(obj, attr, value)
        return True
    except (AttributeError, TypeError, RuntimeError):
        return False


# ─── Lights ─────────────────────────────────────────────────────────────────

def build_light_datablock(L_info):
    name = L_info['name']
    existing = bpy.data.lights.get(name)
    if existing is not None:
        bpy.data.lights.remove(existing)

    light = bpy.data.lights.new(name=name, type=L_info.get('type', 'POINT'))

    if 'color' in L_info:
        light.color = L_info['color'][:3]
    if 'energy' in L_info:
        light.energy = L_info['energy']
    if light.type == 'AREA':
        if 'shape' in L_info:
            safe_set(light, 'shape', L_info['shape'])
        if 'size' in L_info:
            safe_set(light, 'size', L_info['size'])
        if 'size_y' in L_info:
            safe_set(light, 'size_y', L_info['size_y'])
    return light


def build_light_object(obj_info, target_coll):
    name = obj_info['name']
    existing = bpy.data.objects.get(name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)

    light_data_name = obj_info['data']['name']
    light_data = bpy.data.lights.get(light_data_name)
    if light_data is None:
        log(f'  WARN: light data {light_data_name!r} missing for {name}')
        return None

    obj = bpy.data.objects.new(name, light_data)
    target_coll.objects.link(obj)
    obj.matrix_world = mathutils.Matrix(obj_info['matrix_world'])
    log(f'  built LIGHT  : {name:18s} data={light_data_name} '
        f'color={[round(c, 3) for c in light_data.color]} energy={light_data.energy}')
    return obj


# ─── Cameras ────────────────────────────────────────────────────────────────

def build_camera_datablock(C_info):
    name = C_info['name']
    existing = bpy.data.cameras.get(name)
    if existing is not None:
        bpy.data.cameras.remove(existing)
    cam = bpy.data.cameras.new(name=name)
    if 'type' in C_info:
        safe_set(cam, 'type', C_info['type'])
    for k in ('lens', 'sensor_width', 'sensor_height', 'clip_start', 'clip_end',
              'shift_x', 'shift_y', 'sensor_fit', 'ortho_scale'):
        if k in C_info:
            safe_set(cam, k, C_info[k])
    # DOF
    if C_info.get('dof_use'):
        cam.dof.use_dof = True
        if 'dof_focus_distance' in C_info:
            cam.dof.focus_distance = C_info['dof_focus_distance']
        if 'dof_aperture_fstop' in C_info:
            cam.dof.aperture_fstop = C_info['dof_aperture_fstop']
    return cam


def build_camera_object(obj_info, target_coll):
    name = obj_info['name']
    existing = bpy.data.objects.get(name)
    if existing is not None:
        bpy.data.objects.remove(existing, do_unlink=True)
    cam_data_name = obj_info['data']['name']
    cam_data = bpy.data.cameras.get(cam_data_name)
    if cam_data is None:
        log(f'  WARN: camera data {cam_data_name!r} missing for {name}')
        return None
    obj = bpy.data.objects.new(name, cam_data)
    target_coll.objects.link(obj)
    obj.matrix_world = mathutils.Matrix(obj_info['matrix_world'])
    log(f'  built CAMERA : {name:18s} data={cam_data_name} type={cam_data.type} lens={cam_data.lens}')
    return obj


# ─── World ──────────────────────────────────────────────────────────────────

def build_world(W_info):
    """Wire the Scene's active world to match Bruno's. Uses the active world if present."""
    name = W_info['name']
    world = bpy.data.worlds.get(name)
    if world is None:
        world = bpy.data.worlds.new(name=name)
    bpy.context.scene.world = world

    if 'color' in W_info:
        try:
            world.color = W_info['color'][:3]
        except (TypeError, ValueError):
            pass

    world.use_nodes = W_info.get('use_nodes', True)
    if not world.use_nodes:
        return world

    nt_info = W_info.get('node_tree', {})
    nodes = nt_info.get('nodes', [])
    links = nt_info.get('links', [])

    world.node_tree.nodes.clear()
    world.node_tree.links.clear()

    nodes_map = {}
    for n_info in nodes:
        bl_idname = n_info.get('bl_idname')
        if not bl_idname:
            continue
        try:
            n = world.node_tree.nodes.new(type=bl_idname)
        except RuntimeError as e:
            log(f'  WARN: world node {bl_idname}: {e}')
            continue
        try:
            n.name = n_info['name']
        except (TypeError, RuntimeError):
            pass
        n.location = n_info.get('location', [0, 0])

        # Apply properties
        for pk, pv in n_info.get('properties', {}).items():
            if pk == 'show_texture':
                continue
            safe_set(n, pk, pv)

        # Set input default_values by index for non-linked sockets
        for i, ji in enumerate(n_info.get('inputs', [])):
            if i >= len(n.inputs):
                break
            if ji.get('is_linked'):
                continue
            if 'default_value' in ji:
                try:
                    n.inputs[i].default_value = ji['default_value']
                except (TypeError, ValueError):
                    pass

        nodes_map[n_info['name']] = n

    # Links (world has simple topology, no socket-name collisions expected)
    for l in links:
        if l.get('is_muted'):
            continue
        src = nodes_map.get(l['from_node'])
        dst = nodes_map.get(l['to_node'])
        if not src or not dst:
            continue
        out_matches = [s for s in src.outputs if s.name == l['from_socket']]
        in_matches = [s for s in dst.inputs if s.name == l['to_socket']]
        if not out_matches or not in_matches:
            continue
        try:
            world.node_tree.links.new(out_matches[0], in_matches[0])
        except RuntimeError as e:
            log(f'  WARN: world link {l}: {e}')

    log(f'  world configured: {len(nodes_map)} nodes, {len(world.node_tree.links)} links')
    return world


# ─── Idempotent cleanup ─────────────────────────────────────────────────────

def remove_prior_phase6():
    """Remove lighting-ref collection and any prior lights/cameras the script makes."""
    coll = bpy.data.collections.get(LIGHTING_COLL_NAME)
    if coll is not None:
        # Remove objects in the collection
        for o in list(coll.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(coll)
    # Also delete prior light/camera data with our names if they exist
    for nm in ('night', 'day', 'cameraTerrain', 'cameraVehicle'):
        o = bpy.data.objects.get(nm)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
    for nm in ('Area', 'Area.001'):
        L = bpy.data.lights.get(nm)
        if L is not None and L.users == 0:
            bpy.data.lights.remove(L)
    for nm in ('Camera', 'Camera.001'):
        C = bpy.data.cameras.get(nm)
        if C is not None and C.users == 0:
            bpy.data.cameras.remove(C)


# ─── GLB export ─────────────────────────────────────────────────────────────

def export_landing_glb():
    """Export the `areas` collection (which contains landing) to a .glb file."""
    out_path = OUTPUT_DIR / GLB_OUTPUT_NAME
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Strategy: select the `areas` collection's objects, then export with use_selection.
    # `use_active_collection` is finicky across Blender versions; use_selection is robust.
    areas_coll = bpy.data.collections.get('areas')
    if areas_coll is None:
        log('  WARN: no `areas` collection — exporting whole scene instead')
        return _do_export(out_path, use_selection=False)

    # Deselect all
    for o in bpy.data.objects:
        o.select_set(False)

    # Select all objects in areas (recursively)
    def select_recursive(coll):
        n = 0
        for o in coll.objects:
            o.select_set(True)
            n += 1
        for sub in coll.children:
            n += select_recursive(sub)
        return n

    n_selected = select_recursive(areas_coll)
    log(f'  selected {n_selected} objects from `areas` collection for GLB export')

    return _do_export(out_path, use_selection=True)


def _do_export(out_path, use_selection):
    log(f'  exporting to {out_path}')
    try:
        bpy.ops.export_scene.gltf(
            filepath=str(out_path),
            export_format='GLB',
            use_selection=use_selection,
            export_apply=True,         # bake modifiers (Smooth-by-Angle in our case)
            export_yup=True,           # gltf standard
            export_extras=True,        # round-trip custom_properties like mass
            export_animations=False,   # Bruno has 0 Blender actions; all anims are runtime
            export_lights=False,       # Bruno's runtime uses its own lighting
            export_cameras=False,      # Bruno's runtime uses its own cameras
        )
        if out_path.exists():
            size = out_path.stat().st_size
            log(f'  GLB export complete: {size:,} bytes ({size / 1024 / 1024:.2f} MB)')
            return size
        log('  WARN: export call returned but file does not exist on disk')
        return 0
    except Exception as e:
        log(f'  ERROR: export failed: {e}')
        raise


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    log('=' * 60)
    log('Phase 6: Lights + cameras + world + GLB export')
    log('=' * 60)

    assert_blender_version()
    d = load_blend_data()
    objs_by_name = {o['name']: o for o in d['scenes'][0]['objects']}

    if not bpy.data.materials.get('palette'):
        log('WARN: no `palette` material — open 05-foliage.blend or later. Continuing.')

    remove_prior_phase6()

    # Lights ─ build data + objects, link into lighting-ref collection
    log('')
    log('Building light data + objects:')
    for L_info in d['datablocks']['lights']:
        build_light_datablock(L_info)
    scene_coll = bpy.context.scene.collection
    lighting_coll = get_or_create_collection(LIGHTING_COLL_NAME, scene_coll)
    for o_info in d['scenes'][0]['objects']:
        if o_info['type'] != 'LIGHT':
            continue
        build_light_object(o_info, lighting_coll)

    # Cameras
    log('')
    log('Building camera data + objects:')
    for C_info in d['datablocks']['cameras']:
        build_camera_datablock(C_info)
    for o_info in d['scenes'][0]['objects']:
        if o_info['type'] != 'CAMERA':
            continue
        build_camera_object(o_info, lighting_coll)

    # World
    log('')
    log('Building world:')
    if d['datablocks']['worlds']:
        build_world(d['datablocks']['worlds'][0])

    bpy.context.view_layer.update()

    # GLB export
    log('')
    log('Exporting landing area to GLB:')
    glb_bytes = export_landing_glb()

    log('')
    log('── Summary ────────────────────────────────────────')
    log(f'  Lights: {len([o for o in bpy.data.objects if o.type == "LIGHT"])}')
    log(f'  Cameras: {len([o for o in bpy.data.objects if o.type == "CAMERA"])}')
    log(f'  Active world: {bpy.context.scene.world.name if bpy.context.scene.world else "<none>"}')
    log(f'  GLB output: {OUTPUT_DIR / GLB_OUTPUT_NAME}  ({glb_bytes:,} bytes)')

    log('')
    log('Phase 6 complete.')
    log(f'>>> Save this file as: {OUTPUT_DIR / "06-final.blend"} via File → Save As')
    log(f'>>> GLB already saved to {OUTPUT_DIR / GLB_OUTPUT_NAME}')
    log('>>> Compare GLB to Bruno\'s `static/areas/areas.glb` (~3.1 MB) — sizes should be '
        'roughly similar (ours has all landing geometry + materials, no compression yet).')

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
        log(f'=== PHASE 6 FAILED: {last_line} ===')
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
