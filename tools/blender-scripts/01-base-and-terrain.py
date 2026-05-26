"""
Phase 1: Base scene + terrain mesh

Input  : default scene (Phase 1 starts from File → New → General)
Output : 01-terrain-base.blend (you save manually after Run Script)

What this adds:
- Clears the default Cube/Camera/Light (and any prior Phase 1 output, so re-running is safe)
- Configures the scene to match Bruno's .blend: units = meters, render engine = CYCLES,
  fps = 24, resolution = 512×512 (per bruno-blend-summary.md §1)
- Imports the 192×192 m terrain heightfield mesh (16,641 verts / 32,768 tris) into a new
  `terrain` collection at world origin, with UVs preserved so Phase 2 can apply the palette
- Reports terrain dimensions back to console + /tmp/blender-phase-1.log so you can sanity-check

How to run (Blender GUI — easiest path):

  1. First time only: create the workspace directory
       mkdir -p /Users/mahajankaran/Documents/Projects/bruno-blend-recreate

  2. Launch Blender 5.1.2 from Terminal so print() output is visible:
       /Applications/Blender.app/Contents/MacOS/Blender
     (Launching from Finder will hide the console. Terminal also lets you copy errors.)

  3. File → New → General. The viewport shows the default Cube, Camera, Light.
  4. Click the "Scripting" workspace tab at the top of the window.
  5. In the text editor pane (middle), click "New", then paste this entire script.
  6. Click "Run Script" (the play-button icon at the top-right of the editor) — or press Alt+P
     with the cursor inside the editor.
  7. Watch the Terminal you launched Blender from. You should see a series of "===" log
     lines ending in "Phase 1 complete." If you see "PHASE 1 FAILED:" copy that line back.
  8. In the 3D viewport, the default cube should be gone and you should see a large flat
     plane. Scroll-zoom OUT (or press numpad-Home) — the terrain is 192 m wide, much
     bigger than the default view.
  9. File → Save As →
       /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/01-terrain-base.blend

How to run (CLI, headless — alternative):

  mkdir -p /Users/mahajankaran/Documents/Projects/bruno-blend-recreate
  /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/01-base-and-terrain.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/01-terrain-base.blend

  Headless mode auto-saves to the --out path. GUI mode never auto-saves.

What you should see in Blender after running:

- 3D viewport: one large flat-ish plane spanning ~192 m × ~192 m. The middle has gentle
  bumps (the heightfield-displaced terrain — z varies between -1.5 m and 0 m).
- Outliner: Scene Collection > terrain (collection) > terrain (mesh object).
- N-panel → Item tab → Dimensions: roughly X=192, Y=192, Z=1.5.
- Properties panel → Output Properties: render engine "Cycles", FPS 24, Resolution X/Y 512.
- No default Cube / Camera / Light.

What to report back:

- "Worked, viewport shows <whatever you see>" → I produce Phase 2 next.
- "Worked but viewport shows <different thing>" → I diagnose as a script bug or a gap.
- "Failed with error <message>" → paste the error line ("=== PHASE 1 FAILED: ...") and I fix.
"""

import bpy
import bmesh
import json
import os
import sys
import traceback
from pathlib import Path

REPORTS_DIR = Path('/Users/mahajankaran/Documents/Projects/karan-portfolio/reports')
OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
LOG_PATH = Path('/tmp/blender-phase-1.log')

TERRAIN_OBJ_NAME = 'terrain'
TERRAIN_MESH_NAME = 'Plane.134'
TERRAIN_COLL_NAME = 'terrain'


def log(msg):
    print(msg)
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(str(msg) + '\n')
    except Exception:
        pass


def parse_args():
    """Pull --out <path> from sys.argv after the '--' separator. Returns None in GUI mode."""
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
            f'This script targets Blender 5.x (project uses 5.1.2); '
            f'detected {bpy.app.version_string}. Please update Blender.'
        )
    log(f'Blender version: {bpy.app.version_string}')


def clear_prior_outputs():
    """Idempotent reset: remove default starter objects + any prior Phase 1 outputs."""
    removed = []

    # Default Blender starter objects (only if present and unmodified)
    for name in ('Cube', 'Light', 'Camera'):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed.append(f'object:{name}')

    # Outputs from a prior run of this same script
    obj = bpy.data.objects.get(TERRAIN_OBJ_NAME)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
        removed.append(f'object:{TERRAIN_OBJ_NAME}')

    mesh = bpy.data.meshes.get(TERRAIN_MESH_NAME)
    if mesh is not None:
        bpy.data.meshes.remove(mesh)
        removed.append(f'mesh:{TERRAIN_MESH_NAME}')

    coll = bpy.data.collections.get(TERRAIN_COLL_NAME)
    if coll is not None:
        bpy.data.collections.remove(coll)
        removed.append(f'coll:{TERRAIN_COLL_NAME}')

    # Orphaned datablocks left behind by deletes (defensive)
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)

    if removed:
        log(f'Cleared prior data: {", ".join(removed)}')
    else:
        log('Nothing to clear.')


def configure_scene():
    """Match Bruno's .blend top-line settings (bruno-blend-summary.md §1)."""
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.length_unit = 'METERS'
    s.unit_settings.scale_length = 1.0
    s.render.engine = 'CYCLES'
    s.render.fps = 24
    s.render.resolution_x = 512
    s.render.resolution_y = 512
    log(
        f'Scene configured: engine={s.render.engine} fps={s.render.fps} '
        f'res={s.render.resolution_x}x{s.render.resolution_y} '
        f'units={s.unit_settings.length_unit}'
    )


def build_terrain():
    """Construct the terrain mesh from _FROM_BLEND/terrain.json (post-modifier vertices)."""
    src = REPORTS_DIR / 'bruno-mesh-topology' / '_FROM_BLEND' / 'terrain.json'
    if not src.exists():
        raise FileNotFoundError(f'Terrain topology not found at expected path: {src}')

    size_mb = src.stat().st_size / 1024 / 1024
    log(f'Reading terrain topology: {src.name} ({size_mb:.1f} MB)')
    with open(src) as f:
        data = json.load(f)

    verts = data['vertices']
    tri_inds = data['triangle_indices']
    tri_loop_inds = data['triangle_loop_indices']
    uv_data = data.get('uv_layers', {}).get('UVMap')
    transform = data['transform']
    mat_slots = data.get('material_slots', [])
    log(
        f'  topology: {len(verts)} verts, {len(tri_inds)} tris, '
        f'{len(uv_data) if uv_data else 0} UVs, mat_slots={mat_slots}'
    )

    # Build geometry via bmesh — gives us per-loop UV control
    mesh = bpy.data.meshes.new(name=TERRAIN_MESH_NAME)
    bm = bmesh.new()

    bm_verts = [bm.verts.new(tuple(v)) for v in verts]
    bm.verts.ensure_lookup_table()

    skipped = 0
    for tri in tri_inds:
        try:
            bm.faces.new([bm_verts[i] for i in tri])
        except ValueError:
            # Duplicate face — skip silently (terrain shouldn't have any)
            skipped += 1
    bm.faces.ensure_lookup_table()
    if skipped:
        log(f'  WARN: skipped {skipped} duplicate faces during build')

    # UVs — _FROM_BLEND's triangle_loop_indices[i][k] indexes into the original mesh's loop list,
    # and uv_data is keyed by that original loop index. We map each freshly-created face loop
    # to the corresponding original loop's UV.
    if uv_data:
        uv_layer = bm.loops.layers.uv.new('UVMap')
        for face_i, face in enumerate(bm.faces):
            tlis = tri_loop_inds[face_i]
            for k, loop in enumerate(face.loops):
                u, v = uv_data[tlis[k]]
                loop[uv_layer].uv = (u, v)
        log(f'  UVMap layer wired ({len(uv_data)} loop-UVs mapped)')

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Material slot placeholders so Phase 2 can swap them in without renumbering
    for slot_name in mat_slots:
        mesh.materials.append(None)
    if mat_slots:
        log(f'  reserved {len(mat_slots)} material slot(s): {mat_slots}')

    # Create the object, apply Bruno's transform (all-identity for terrain at origin)
    obj = bpy.data.objects.new(TERRAIN_OBJ_NAME, mesh)
    obj.location = tuple(transform['location'])
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = tuple(transform['rotation_euler'])
    obj.scale = tuple(transform['scale'])

    # Link into a fresh `terrain` collection (matches Bruno's outliner)
    coll = bpy.data.collections.new(TERRAIN_COLL_NAME)
    bpy.context.scene.collection.children.link(coll)
    coll.objects.link(obj)

    # Force depsgraph update so .dimensions reflects the new mesh
    bpy.context.view_layer.update()
    dims = obj.dimensions
    log(f'  → terrain object created at location={tuple(obj.location)}')
    log(f'  → dimensions: X={dims.x:.2f} m  Y={dims.y:.2f} m  Z={dims.z:.2f} m')
    log(f'  → expected:   X=192.00 m Y=192.00 m Z=1.50 m  (per bruno-blend-summary.md §1)')

    # Sanity check — flag if dimensions deviate
    if not (190 < dims.x < 195 and 190 < dims.y < 195 and 1.4 < dims.z < 1.6):
        log(
            f'  WARN: dimensions deviate from expected. This may indicate the terrain JSON '
            f'has a different mesh than Bruno\'s, or the post-modifier evaluation changed.'
        )


def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log('=' * 60)
    log('Phase 1: Base scene + terrain')
    log('=' * 60)

    assert_blender_version()
    clear_prior_outputs()
    configure_scene()
    build_terrain()

    out_path = parse_args()
    log('')
    log('Phase 1 complete.')
    log(
        f'>>> Save this file as: {OUTPUT_DIR / "01-terrain-base.blend"} '
        f'via File → Save As'
    )

    if out_path:
        bpy.ops.wm.save_as_mainfile(filepath=out_path)
        log(f'(CLI --out given: saved to {out_path})')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log(tb)
        last_line = tb.strip().splitlines()[-1] if tb.strip() else 'unknown'
        log(f'=== PHASE 1 FAILED: {last_line} ===')
        # In GUI mode, re-raise so Blender's error popup appears too
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
