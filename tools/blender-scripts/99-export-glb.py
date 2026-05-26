"""
99: Re-export GLB from any Phase-6+ .blend with Bruno's documented export settings.

Standalone script — load whichever .blend you want to re-export from, then:

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/06-final.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/99-export-glb.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/landing.glb

You can also run it from GUI (Scripting workspace → Run Script) — it will write to
the default `--out` path (`bruno-blend-recreate/landing.glb`).

After this script writes the uncompressed GLB, run Bruno's `compress.js` pipeline
on it manually to get the runtime-shaped compressed form:

  cd /Users/mahajankaran/Documents/Projects/bruno-blend-recreate
  npx @gltf-transform/cli draco landing.glb landing-compressed.glb \\
    --quantize-position 12 --quantize-normal 6 --quantize-texcoord 6

(or the matching `npx gltf-transform draco …` if you have it installed via
@gltf-transform/cli@4). The compression settings match
`reports/bruno-runtime-source.md` → `scripts/compress.js` lines for draco. Bruno's
end-of-pipeline `static/areas/areas.glb` is the Draco-compressed result; ours
should land in similar size (~3 MB compressed for landing-only at ~0.47 MB
uncompressed → after Draco, ~150 KB).

Documented gaps for full Bruno fidelity:
- GAP-B-003 (export preset) — we use the hypothesis from bruno-analysis.md:
  export_apply=True, export_yup=True, export_extras=True, export_animations=False,
  export_lights=False, export_cameras=False. If a future v3 extraction recovers
  Bruno's saved Operator Preset, swap these in.
"""

import bpy
import sys
import traceback
from pathlib import Path

OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
DEFAULT_OUT = OUTPUT_DIR / 'landing.glb'
LOG_PATH = Path('/tmp/blender-phase-99.log')


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
            return Path(rest[i + 1])
    return None


def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out_path = parse_args() or DEFAULT_OUT
    log(f'GLB re-export → {out_path}')

    areas_coll = bpy.data.collections.get('areas')
    if areas_coll is None:
        log('  no `areas` collection — exporting whole scene')
        use_selection = False
    else:
        for o in bpy.data.objects:
            o.select_set(False)

        def select_recursive(coll):
            n = 0
            for o in coll.objects:
                o.select_set(True)
                n += 1
            for sub in coll.children:
                n += select_recursive(sub)
            return n

        n_sel = select_recursive(areas_coll)
        log(f'  selected {n_sel} objects under `areas`')
        use_selection = True

    bpy.ops.export_scene.gltf(
        filepath=str(out_path),
        export_format='GLB',
        use_selection=use_selection,
        export_apply=True,
        export_yup=True,
        export_extras=True,
        export_animations=False,
        export_lights=False,
        export_cameras=False,
    )

    if out_path.exists():
        size = out_path.stat().st_size
        log(f'  wrote {size:,} bytes ({size / 1024 / 1024:.2f} MB)')
        log('')
        log('Next step (manual): run Draco compression to match Bruno\'s runtime shape:')
        log('  cd /Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
        log('  npx @gltf-transform/cli draco landing.glb landing-compressed.glb \\')
        log('    --quantize-position 12 --quantize-normal 6 --quantize-texcoord 6')
    else:
        log('  ERROR: export operator returned but file does not exist')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log(tb)
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
