"""
Phase 2: Materials + palette texture

Input  : 01-terrain-base.blend (Phase 1 output)
Output : 02-materials.blend

What this adds:
- Loads available raster textures from reports/bruno-texture-pixels/ as Blender Images
  (palette.png, terrain/terrain.png, floor/slabs.png, career/career*.png — 9 textures
  with real pixel data). Missing textures (EXR masks, area label PNGs not extracted)
  become magenta placeholders so they're visible-but-non-fatal — see GAP-B-006, B-007.
- Builds all 35 of Bruno's materials literally from bruno-blend.json's extracted
  `datablocks.materials[*].node_tree` — node-by-node, link-by-link, with correct
  interpolation/extension/projection on TEX_IMAGE nodes, correct RGB default values,
  Emission strength values, MIX blend_type/data_type, MATH/VECT_MATH operations.
- Assigns the `terrain` material to terrain.material_slots[0] so the viewport (in
  Material Preview or Rendered shading) shows Bruno's actual terrain shading.

Why this is full-fidelity (not the placeholder version from the Phase 0 plan):
Phase 0 anticipated GAP-B-001 (per-material node tree not extracted). Direct inspection
of bruno-blend.json showed the full node graph IS extracted — including each socket's
default_value, every link, and image metadata. So Phase 2 wires every material
verbatim. GAP-B-001 is retracted in blender-recreate-gaps.md.

How to run (Blender GUI):

  1. With 01-terrain-base.blend still open (or File → Open → 01-terrain-base.blend):
  2. Switch to the "Scripting" workspace tab.
  3. In the text editor pane: click "New" or open this file, then click "Run Script"
     (or Alt+P with cursor in editor).
  4. Watch your Terminal (or /tmp/blender-phase-2.log) — you should see ~35 lines of
     "built material: <name>" plus image-loading status, then "Phase 2 complete."
  5. In the 3D viewport, switch the shading mode (top-right of viewport, the 4 spheres)
     from "Solid" to "Material Preview" — the terrain should change colour: faint
     yellow-brown ground with darker patches where the (placeholder) mask textures
     would normally carve out grass/furniture zones.
  6. File → Save As → /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/02-materials.blend

How to run (CLI, headless):

  /Applications/Blender.app/Contents/MacOS/Blender --background \\
    /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/01-terrain-base.blend \\
    --python /Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender-scripts/02-materials.py \\
    -- --out /Users/mahajankaran/Documents/Projects/bruno-blend-recreate/02-materials.blend

What you should see in Blender after running:

- Outliner: Scene Collection > terrain > terrain (unchanged from Phase 1).
- Properties panel → Material Properties (red sphere icon) with `terrain` selected:
  the terrain object now has a `terrain` material in slot 0. Click the slot and you'll
  see a 25-node shader graph in the Shading workspace.
- bpy.data.materials shows 35 entries: airDancer, black, blackboardLabels, ...,
  palette, ..., waterfall (full list in bruno-blend-summary.md §6 + content catalog).
- bpy.data.images contains: real pixel data for palette, terrain.png, slabs.png,
  the 6 career text labels, plus magenta placeholders for the ~13 missing textures.
- Viewport in "Material Preview" mode shows colored terrain (palette-sampled).

What to report back:

- "Worked, viewport shows <whatever>" → I produce Phase 3 (landing area geometry).
- "Worked but viewport shows <different>" → I diagnose as a script bug or extraction gap.
- "Failed with error <message>" → paste the "=== PHASE 2 FAILED:" line and I fix.
"""

import base64
import bpy
import json
import os
import sys
import traceback
from pathlib import Path

REPORTS_DIR = Path('/Users/mahajankaran/Documents/Projects/karan-portfolio/reports')
OUTPUT_DIR = Path('/Users/mahajankaran/Documents/Projects/bruno-blend-recreate')
LOG_PATH = Path('/tmp/blender-phase-2.log')

BRUNO_BLEND_JSON = REPORTS_DIR / 'bruno-blend.json'
PIXEL_INDEX_JSON = REPORTS_DIR / 'bruno-texture-pixels' / 'INDEX.json'
PIXEL_DATA_DIR = REPORTS_DIR / 'bruno-texture-pixels'

TERRAIN_OBJ_NAME = 'terrain'
PLACEHOLDER_TAG = 'BRUNO_PLACEHOLDER'  # written to image["BRUNO_PLACEHOLDER"]=True


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
            f'This script targets Blender 5.x (project uses 5.1.2); '
            f'detected {bpy.app.version_string}.'
        )
    log(f'Blender version: {bpy.app.version_string}')


# ─── Texture pixel loading ──────────────────────────────────────────────────

def load_pixel_index():
    """Build name/path lookup tables from bruno-texture-pixels/INDEX.json."""
    if not PIXEL_INDEX_JSON.exists():
        raise FileNotFoundError(f'Missing {PIXEL_INDEX_JSON}')
    with open(PIXEL_INDEX_JSON) as f:
        idx = json.load(f)
    by_rel = {}
    by_basename = {}
    by_stem = {}
    for e in idx['entries']:
        rel = e['rel']
        by_rel[rel] = e
        bn = os.path.basename(rel)
        by_basename.setdefault(bn, e)
        stem, _ = os.path.splitext(bn)
        by_stem.setdefault(stem, e)
    log(f'Pixel index: {len(idx["entries"])} texture entries indexed')
    return {'by_rel': by_rel, 'by_basename': by_basename, 'by_stem': by_stem}


def find_pixel_entry(image_name, filepath_raw, lookup):
    """Try several lookup keys to find the texture pixel JSON for an image reference."""
    candidates = []
    # Try image.name directly (e.g., 'palette.png', 'palette')
    if image_name in lookup['by_rel']:
        candidates.append(lookup['by_rel'][image_name])
    if image_name in lookup['by_basename']:
        candidates.append(lookup['by_basename'][image_name])
    if image_name in lookup['by_stem']:
        candidates.append(lookup['by_stem'][image_name])

    # Try filepath_raw basename ('//palette.png' -> 'palette.png')
    if filepath_raw:
        fp = filepath_raw.lstrip('/').replace('\\', '/')
        bn = os.path.basename(fp)
        if bn in lookup['by_basename']:
            candidates.append(lookup['by_basename'][bn])
        # Try the tail (e.g., 'textures/slabs.png')
        for prefix in ('textures/', '../static/', 'static/'):
            stripped = fp.replace(prefix, '')
            if stripped in lookup['by_rel']:
                candidates.append(lookup['by_rel'][stripped])

    # de-dup, keep order
    seen = set()
    out = []
    for c in candidates:
        k = c['rel']
        if k not in seen:
            seen.add(k)
            out.append(c)
    return out[0] if out else None


def decode_pixels_to_blender(raw_bytes, w, h, channels):
    """Convert top-down RGBA bytes -> bottom-up flat float RGBA list for img.pixels."""
    pixels = [0.0] * (w * h * 4)
    for src_y in range(h):
        dst_y = h - 1 - src_y
        for x in range(w):
            src_off = (src_y * w + x) * channels
            dst_off = (dst_y * w + x) * 4
            pixels[dst_off] = raw_bytes[src_off] / 255.0
            pixels[dst_off + 1] = raw_bytes[src_off + 1] / 255.0 if channels >= 2 else pixels[dst_off]
            pixels[dst_off + 2] = raw_bytes[src_off + 2] / 255.0 if channels >= 3 else pixels[dst_off]
            pixels[dst_off + 3] = raw_bytes[src_off + 3] / 255.0 if channels >= 4 else 1.0
    return pixels


def create_image_from_pixels(blender_name, entry, colorspace):
    """Decode base64 RGBA pixels into a new Blender Image."""
    pj_path = PIXEL_DATA_DIR / entry['pixelJson']
    with open(pj_path) as f:
        pj = json.load(f)
    w = pj['width']
    h = pj['height']
    channels = pj['channels']
    raw = base64.b64decode(pj['pixels'])

    # Remove any existing image with the same Blender name (idempotency)
    existing = bpy.data.images.get(blender_name)
    if existing is not None:
        bpy.data.images.remove(existing)

    img = bpy.data.images.new(blender_name, width=w, height=h, alpha=True)
    img.colorspace_settings.name = colorspace
    pixels = decode_pixels_to_blender(raw, w, h, channels)
    img.pixels.foreach_set(pixels)
    img.update()
    img.pack()
    return img, (w, h, channels)


def create_placeholder_image(blender_name, size, colorspace):
    """Magenta 1×1 (or target-sized) placeholder so missing textures are visible."""
    w, h = size if size and size[0] > 0 and size[1] > 0 else (1, 1)
    # Cap placeholder size so we don't waste memory on missing 512×512 EXRs
    if w * h > 4096:
        w, h = 4, 4

    existing = bpy.data.images.get(blender_name)
    if existing is not None:
        bpy.data.images.remove(existing)

    img = bpy.data.images.new(blender_name, width=w, height=h, alpha=True)
    img.colorspace_settings.name = colorspace
    img[PLACEHOLDER_TAG] = True
    # Magenta to make missing textures obvious in the viewport
    pixels = [1.0, 0.0, 1.0, 1.0] * (w * h)
    img.pixels.foreach_set(pixels)
    img.update()
    img.pack()
    return img


# ─── Material building ──────────────────────────────────────────────────────

# Properties to skip when copying — read-only or context-dependent
SKIP_PROPS = {'show_texture'}


def safe_set(node, attr, value):
    """setattr with try/except — properties differ across Blender versions."""
    try:
        setattr(node, attr, value)
        return True
    except (AttributeError, TypeError, RuntimeError):
        return False


def set_socket_default(socket, value):
    """Assign default_value to a socket of any type."""
    try:
        if isinstance(value, list):
            socket.default_value = value
        else:
            socket.default_value = value
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def build_material(mat_info, image_cache, pixel_lookup, gap_log):
    """Construct one Blender material from its bruno-blend.json record."""
    name = mat_info['name']

    # Idempotency: remove any prior material with the same name
    existing = bpy.data.materials.get(name)
    if existing is not None:
        bpy.data.materials.remove(existing)

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    # Copy top-level material properties (diffuse fallback, metallic, roughness, etc.)
    if 'diffuse_color' in mat_info:
        try:
            mat.diffuse_color = mat_info['diffuse_color']
        except (TypeError, ValueError):
            pass
    for top_attr in ('metallic', 'roughness', 'specular_intensity'):
        if top_attr in mat_info:
            safe_set(mat, top_attr, mat_info[top_attr])

    nt_info = mat_info.get('node_tree')
    if not nt_info:
        log(f'  WARN: material {name!r} has no node_tree dump; left at default')
        return mat

    # Clear the default nodes Blender created so we rebuild from scratch
    mat.node_tree.nodes.clear()
    mat.node_tree.links.clear()

    nodes_map = {}

    # ── Pass 1: create nodes
    for n_info in nt_info.get('nodes', []):
        bl_idname = n_info.get('bl_idname')
        if not bl_idname:
            continue
        try:
            n = mat.node_tree.nodes.new(type=bl_idname)
        except RuntimeError as e:
            log(f'  WARN: {name}: cannot create {bl_idname}: {e}')
            continue

        # Set name (Blender renames on collision; we then overwrite anyway)
        try:
            n.name = n_info['name']
        except (TypeError, RuntimeError):
            pass
        n.label = n_info.get('label', '') or ''
        if 'location' in n_info:
            n.location = n_info['location']
        if 'width' in n_info:
            safe_set(n, 'width', n_info['width'])
        safe_set(n, 'mute', n_info.get('mute', False))
        safe_set(n, 'hide', n_info.get('hide', False))

        # Apply node-type-specific properties BEFORE setting socket defaults,
        # because some properties (e.g., ShaderNodeMix.data_type) reshape the sockets.
        for prop_key, prop_val in n_info.get('properties', {}).items():
            if prop_key in SKIP_PROPS:
                continue
            safe_set(n, prop_key, prop_val)

        # TEX_IMAGE: wire the image
        if bl_idname == 'ShaderNodeTexImage':
            img_info = n_info.get('image')
            if img_info:
                img = get_or_create_image(img_info, image_cache, pixel_lookup, gap_log)
                if img is not None:
                    n.image = img

        # RGB: the output Color has the default_value we want
        if bl_idname == 'ShaderNodeRGB':
            for o in n_info.get('outputs', []):
                if o.get('name') == 'Color' and 'default_value' in o:
                    set_socket_default(n.outputs['Color'], o['default_value'])

        # Inputs: set default_value on non-linked sockets, by INDEX (handles multiple
        # sockets sharing the same display name, e.g., Math has 3 "Value" inputs)
        json_inputs = n_info.get('inputs', [])
        for idx, ji in enumerate(json_inputs):
            if idx >= len(n.inputs):
                break
            if ji.get('is_linked'):
                continue
            if 'default_value' not in ji:
                continue
            set_socket_default(n.inputs[idx], ji['default_value'])

        nodes_map[n_info['name']] = n

    # ── Pass 2: links. Handle duplicate socket-name disambiguation via FIFO counter.
    in_link_n = {}  # (to_node_name, to_socket_name) -> next match index
    out_link_n = {}  # outputs can fan out, so we typically don't increment
    link_errors = 0

    for link in nt_info.get('links', []):
        if link.get('is_muted'):
            continue
        from_name = link['from_node']
        to_name = link['to_node']
        from_sock = link['from_socket']
        to_sock = link['to_socket']

        src_node = nodes_map.get(from_name)
        dst_node = nodes_map.get(to_name)
        if src_node is None or dst_node is None:
            link_errors += 1
            continue

        out_matches = [s for s in src_node.outputs if s.name == from_sock]
        if not out_matches:
            link_errors += 1
            continue
        out_key = (from_name, from_sock)
        out_idx = out_link_n.get(out_key, 0) % len(out_matches)
        src_socket = out_matches[out_idx]

        in_matches = [s for s in dst_node.inputs if s.name == to_sock]
        if not in_matches:
            link_errors += 1
            continue
        in_key = (to_name, to_sock)
        in_idx = in_link_n.get(in_key, 0)
        if in_idx >= len(in_matches):
            # More links than sockets — last-resort wrap
            in_idx = 0
        dst_socket = in_matches[in_idx]
        in_link_n[in_key] = in_idx + 1

        try:
            mat.node_tree.links.new(src_socket, dst_socket)
        except RuntimeError:
            link_errors += 1

    n_nodes = len(nt_info.get('nodes', []))
    n_links = len(nt_info.get('links', []))
    suffix = f' ({link_errors} link errors)' if link_errors else ''
    log(f'  built material: {name:30s} nodes={n_nodes:3d} links={n_links:3d}{suffix}')
    return mat


def get_or_create_image(image_info, image_cache, pixel_lookup, gap_log):
    """Resolve a material's image reference to a Blender Image, loading or stubbing."""
    img_name = image_info.get('name')
    if not img_name:
        return None
    if img_name in image_cache:
        return image_cache[img_name]

    colorspace = image_info.get('colorspace') or 'sRGB'
    target_size = tuple(image_info.get('size') or [1, 1])

    entry = find_pixel_entry(img_name, image_info.get('filepath_raw', ''), pixel_lookup)
    if entry is not None:
        try:
            img, dims = create_image_from_pixels(img_name, entry, colorspace)
            image_cache[img_name] = img
            log(f'    image loaded: {img_name:30s} {dims[0]}x{dims[1]} {dims[2]}ch  ({entry["rel"]})')
            return img
        except Exception as e:
            log(f'    WARN: failed to decode {img_name!r} from {entry["rel"]}: {e}')

    # Placeholder
    img = create_placeholder_image(img_name, target_size, colorspace)
    image_cache[img_name] = img
    gap_log.add(img_name)
    log(f'    image PLACEHOLDER: {img_name:30s} {target_size} colorspace={colorspace}  (no pixel data found)')
    return img


# ─── Terrain material assignment ────────────────────────────────────────────

def apply_terrain_material():
    obj = bpy.data.objects.get(TERRAIN_OBJ_NAME)
    if obj is None or obj.type != 'MESH':
        log(f'  WARN: object {TERRAIN_OBJ_NAME!r} not found — terrain material not assigned. '
            f'Did you open 01-terrain-base.blend before running this?')
        return
    mesh = obj.data
    terrain_mat = bpy.data.materials.get('terrain')
    if terrain_mat is None:
        log('  WARN: terrain material not built — slot left empty')
        return

    if len(mesh.materials) > 0:
        mesh.materials[0] = terrain_mat
    else:
        mesh.materials.append(terrain_mat)
    log(f'  assigned `terrain` material to {TERRAIN_OBJ_NAME}.material_slots[0]')


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log('=' * 60)
    log('Phase 2: Materials + palette texture')
    log('=' * 60)

    assert_blender_version()

    # Pre-check: ensure we're operating on a post-Phase-1 file
    if not bpy.data.objects.get(TERRAIN_OBJ_NAME):
        log(
            f'WARN: no `{TERRAIN_OBJ_NAME}` object found in this scene. '
            f'Phase 2 expects you to open 01-terrain-base.blend first. '
            f'Materials will still be created, but the terrain assignment will be skipped.'
        )

    pixel_lookup = load_pixel_index()

    log(f'Reading {BRUNO_BLEND_JSON.name} ({BRUNO_BLEND_JSON.stat().st_size / 1024 / 1024:.1f} MB)')
    with open(BRUNO_BLEND_JSON) as f:
        blend = json.load(f)
    materials_info = blend['datablocks']['materials']
    log(f'Found {len(materials_info)} materials in source .blend')

    image_cache = {}
    placeholder_names = set()

    log('')
    log('Building materials:')
    for mat_info in materials_info:
        build_material(mat_info, image_cache, pixel_lookup, placeholder_names)

    log('')
    log('Applying terrain material to terrain object:')
    apply_terrain_material()

    # Summary
    n_real = sum(1 for img in bpy.data.images if PLACEHOLDER_TAG not in img.keys())
    n_placeholder = sum(1 for img in bpy.data.images if PLACEHOLDER_TAG in img.keys())
    log('')
    log('── Summary ────────────────────────────────────────')
    log(f'  Materials created: {len(bpy.data.materials)}')
    log(f'  Images loaded with pixel data: {n_real}')
    log(f'  Image placeholders (missing pixel data): {n_placeholder}')
    if placeholder_names:
        log(f'  Placeholder names: {sorted(placeholder_names)}')
        log(f'  (see GAP-B-006, B-007 in reports/blender-recreate-gaps.md)')

    log('')
    log('Phase 2 complete.')
    log(
        f'>>> Save this file as: {OUTPUT_DIR / "02-materials.blend"} '
        f'via File → Save As'
    )
    log(
        '>>> In the 3D viewport, switch shading mode (top-right) from "Solid" to '
        '"Material Preview" to see the terrain rendered with its actual material.'
    )

    out_path = parse_args()
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
        log(f'=== PHASE 2 FAILED: {last_line} ===')
        if '--' not in sys.argv:
            raise
        else:
            sys.exit(1)
