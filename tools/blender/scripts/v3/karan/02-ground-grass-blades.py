"""Replace Bruno's flat-triangle blade with a real arched-blade mesh + dense scatter.

WHY NOT A TEXTURE CARD?
We tried `grass-side.png` as an alpha-mapped card per scatter point and it
looked dense but it cannot be animated per-blade. Each "blade" inside the
photo is a pixel cluster, not geometry — so wind-sway, player collision,
or any vertex-shader animation would have to deform the whole card as one
rigid unit. Bruno's folio-2025 grass animates each blade individually via
its world-space position + time in the runtime shader. For karan to
inherit that capability, every blade must be real geometry.

Three things this script does:

  1. BLADE MESH (`Plane.012`) — 9-VERT CURVED BLADE
     A 4-segment arched stem that curves forward in +Y as it rises in
     +Z. Narrow base (0.030 m), tapers smoothly to a single tip point
     at the top, four-section forward bend for a real curve (not a
     flat triangle pretending to be a blade). Smooth-shaded. Each
     vertex carries a `blade_height` FLOAT attribute in [0, 1] from
     base to tip — the material uses this to look up the colour ramp.

  2. ROTATION JITTER (inside `Geometry Nodes.001`)
     A FunctionNodeRandomValue (FLOAT_VECTOR) is wired into the
     `Rotation` input of `Instance on Points`. Range:
        X: ±20° (forward/back lean)
        Y: ±20° (sideways lean)
        Z: 0 → 360° (random facing)
     Tilt pivots at z=0 (blade base) so blades stay rooted.

  3. SCATTER DENSITY (inside `Geometry Nodes.001` Distribute Points on Faces)
     Bump `Density` from Bruno's 10 → 180 points / local-m² (10% lower
     than the earlier 200 to leave Blender some headroom). The source
     plane is 192×192 m so raw point count is 180 × 192² ≈ 6.64M.
     After the terrainGrass.G mask filter ≈ 3.15M visible blades.

     The Grid node's vertex count is left at Bruno's 512×512 default —
     it controls surface tessellation, NOT blade count, so bumping it
     does nothing for density.

  4. PER-BLADE SIZE VARIATION (inside `Geometry Nodes.001`)
     Continuous random multiplier on top of the terrainGrass.G mask:
        Random Value (0..1) ─→ Map Range (0..1 → SIZE_MIN..SIZE_MAX)
                                          │
                       Separate Color.Green┴─→ Math(×) ─→ Instance.Scale

     Every blade gets a unique multiplier in [SIZE_MIN, SIZE_MAX]
     instead of a binary small/large bucket. Wider visible range,
     more natural distribution. The mask still fades blades at path
     edges and water exactly like before.

  5. BLADE MATERIAL (`Grass Palette`, new datablock)
     Reads the `blade_height` attribute (0=base, 1=tip) and feeds it to
     a ColorRamp built from the user-supplied palette:
        0.00  #235B08  base dark green
        0.30  #5C9E12  lower/middle rich green
        0.55  #9BBE2E  upper/middle yellow-green
        0.75  #B7C943  lime
        0.90  #D6C36A  dry straw
        1.00  #E0D49A  dry yellow-beige tip
     Hex values are sRGB → converted to linear before being written to
     ColorRamp stops so the rendered colour matches the source palette.
     Bruno's `grass` material is left in `bpy.data.materials`
     (keep-everything policy); only the slot assignment on Plane.012
     changes.

  6. PER-INSTANCE DRY-TIP VARIATION
     ~10% of blades render with a second ramp whose top stops are brown
     (#8A6A55 → #9B6B75) instead of the green ramp's straw stops, so
     the field shows occasional older / drying blades.

     Plumbing:
       - In Geometry Nodes: a `Store Named Attribute` (POINT domain,
         FLOAT) writes a per-point random value as `blade_dry_seed`
         BEFORE `Instance on Points`. Each instance inherits its
         parent point's value; after `Realize Instances` every vertex
         of an instance shares the same dry-seed value.
       - In the material: a second ColorRamp is fed the same
         `blade_height` factor as the green one. A Math LESS_THAN(seed,
         0.10) gates a Mix node between the two ramps' outputs —
         factor 0 picks green, factor 1 picks dry.
       - Brown palette keeps the green base (a dry blade is still
         rooted as a living plant); only the tip section transitions
         to brown.

The original `grass` material on `Plane.012` is LEFT ASSIGNED. It already
applies Bruno's Z-gradient (dark green base → bright yellow-green tip),
which is exactly what we want. No texture, no alpha card, no extra image.
The card material `Grass Blade Card` created by an earlier version of
this script is left in `bpy.data.materials` (keep-everything policy);
nothing references it anymore.

Idempotent: rerunning does not pile up nodes — the jitter node is
re-found by name.
"""
import bpy
import math

BLADE_MESH = "Plane.012"
SCATTER_NODE_GROUP = "Geometry Nodes.001"
JITTER_NODE_NAME = "Blade Rotation Jitter"
BLADE_HEIGHT_ATTR = "blade_height"
BLADE_PALETTE_MATERIAL = "Grass Palette"
BLEND_PATH = (
    "/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/"
    "world-v3-karan.blend"
)

# 9-vert curved blade — 4 segments, taper from base width 0.030 to a
# single tip vertex, forward bend grows with height. The Y offsets
# create a real arch rather than a faceted bent stick. All geometry is
# rooted at z=0 so rotation jitter pivots at the ground contact point.
BLADE_HEIGHT_MAX = 0.55  # tip height — used to normalise the height attr
BLADE_VERTS = [
    # base (w=0.030, no forward offset)
    (-0.030, 0.000, 0.000),   # 0
    ( 0.030, 0.000, 0.000),   # 1
    # segment 1 (w=0.026, slight bend)
    (-0.026, 0.025, 0.165),   # 2
    ( 0.026, 0.025, 0.165),   # 3
    # segment 2 (w=0.020, more bend)
    (-0.020, 0.065, 0.310),   # 4
    ( 0.020, 0.065, 0.310),   # 5
    # segment 3 (w=0.013, strong bend, near-tip)
    (-0.013, 0.120, 0.450),   # 6
    ( 0.013, 0.120, 0.450),   # 7
    # tip (w=0, max forward offset)
    ( 0.000, 0.170, 0.550),   # 8
]
BLADE_FACES = [
    (0, 1, 3), (0, 3, 2),  # base quad
    (2, 3, 5), (2, 5, 4),  # segment-1 quad
    (4, 5, 7), (4, 7, 6),  # segment-2 quad
    (6, 7, 8),             # tip triangle
]
# Per-vertex height factor in [0, 1] — drives the colour ramp lookup.
BLADE_HEIGHT_FACTORS = [v[2] / BLADE_HEIGHT_MAX for v in BLADE_VERTS]

# Random rotation per blade. Small X/Y tilt + full Z spin. Applied at the
# blade base (mesh origin = z=0) so the rooted end stays on the ground.
TILT_X = 0.35   # ~20° lean forward/back
TILT_Y = 0.35   # ~20° lean sideways
SPIN_Z = 2.0 * math.pi

# Real density lever — `Distribute Points on Faces → Density` (points
# per local m² of the 192×192 source plane). Bruno's default is 10
# which gives ~370k raw points / ~180k visible after the mask. 180
# → ~6.64M raw / ~3.15M visible (≈425 per world m², ~4.9 cm spacing).
SCATTER_DENSITY = 180

# Per-blade continuous size variation. Each blade picks a random factor
# in [SIZE_MIN_FACTOR, SIZE_MAX_FACTOR]; multiplied with the G mask so
# the mask's spatial fade (paths, water) still applies. Continuous
# distribution gives natural variety vs the binary small/large split.
SIZE_MIN_FACTOR = 0.35
SIZE_MAX_FACTOR = 1.50
SIZE_BUCKET_RANDOM = "Blade Size Random"
SIZE_BUCKET_MAPPER = "Blade Size Mapper"
SIZE_SCALE_MULTIPLIER = "Blade Scale Multiplier"
SIZE_BUCKET_THRESHOLD_LEGACY = "Blade Size Threshold"  # removed if present

# Blade colour palette — sRGB hex stops fed into the ColorRamp on
# `Grass Palette` material. Position 0.0 = blade base, 1.0 = tip.
BLADE_PALETTE = [
    (0.00, "#4F6429"),  # dark olive base
    (0.30, "#617707"),  # lower/middle olive
    (0.55, "#80890C"),  # mockup median grass
    (0.75, "#90A110"),  # highlighted blade face
    (0.90, "#A8AD36"),  # muted sunlit tip
    (1.00, "#B8B868"),  # soft dry yellow-green tip
]
# Dry-tip palette — applied to ~DRY_FRACTION of blades. Base/middle
# stays green so the blade still looks rooted; only the upper section
# transitions to the brown stops the user requested.
BLADE_PALETTE_DRY = [
    (0.00, "#4F6429"),  # dark olive base (same as green ramp)
    (0.30, "#617707"),  # olive middle    (same as green ramp)
    (0.55, "#80890C"),  # mockup grass    (same as green ramp)
    (0.75, "#6B4A30"),  # transition to dry-brown
    (0.90, "#8A6A55"),  # older dry brown
    (1.00, "#9B6B75"),  # mauve-brown tip
]
DRY_FRACTION = 0.10            # P(blade is dry) — used in shader Math node
DRY_SEED_ATTR = "blade_dry_seed"
DRY_RANDOM_NODE = "Blade Dry Seed Random"
DRY_STORE_NODE = "Blade Dry Seed Store"
DRY_RANDOM_SEED = 99           # distinct from rotation (0) + size (42)


def _replace_blade_mesh():
    mesh = bpy.data.meshes.get(BLADE_MESH)
    if mesh is None:
        print(f"  [WARN] mesh {BLADE_MESH!r} not found — skipping mesh swap")
        return
    mesh.clear_geometry()
    mesh.from_pydata(BLADE_VERTS, [], BLADE_FACES)
    mesh.update()
    # Smooth shading so the 4-segment bend reads as a curve, not a faceted fan.
    for poly in mesh.polygons:
        poly.use_smooth = True
    # Per-vertex height factor (0 at base, 1 at tip) — drives the ColorRamp.
    # Remove any prior attribute with the same name (idempotent re-runs).
    existing = mesh.attributes.get(BLADE_HEIGHT_ATTR)
    if existing is not None:
        mesh.attributes.remove(existing)
    attr = mesh.attributes.new(name=BLADE_HEIGHT_ATTR, type="FLOAT", domain="POINT")
    for i, factor in enumerate(BLADE_HEIGHT_FACTORS):
        attr.data[i].value = float(factor)
    print(
        f"  {BLADE_MESH}: reshaped → {len(BLADE_VERTS)}-vert curved blade "
        f"({len(BLADE_FACES)} tris) with per-vert {BLADE_HEIGHT_ATTR!r} attribute"
    )


def _hex_to_linear_rgba(hex_str):
    """Convert an sRGB hex string ('#RRGGBB') to linear-RGB (r,g,b,1.0).

    Blender colour socket defaults are interpreted in linear space, so a
    palette authored in sRGB hex needs gamma decoding before assignment
    or the rendered colour drifts brighter/desaturated.
    """
    h = hex_str.lstrip("#")
    sr, sg, sb = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return (sr ** 2.2, sg ** 2.2, sb ** 2.2, 1.0)


def _populate_color_ramp(ramp_node, palette):
    """Reset and rewrite a ColorRamp node's stops from an (pos, hex) list."""
    cr = ramp_node.color_ramp
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    cr.elements[0].position = palette[0][0]
    cr.elements[0].color = _hex_to_linear_rgba(palette[0][1])
    for pos, hex_str in palette[1:]:
        elem = cr.elements.new(pos)
        elem.color = _hex_to_linear_rgba(hex_str)


def _find_enabled_input(node, socket_name):
    """Return the first ENABLED input on `node` with that display name.

    Blender's Mix / RandomValue / StoreNamedAttribute nodes expose all
    type variants of each input but disable the ones that don't match
    the current data_type. Indexing by integer is fragile (the index of
    the enabled FLOAT/RGBA slot moves between versions).
    """
    for inp in node.inputs:
        if inp.name == socket_name and inp.enabled:
            return inp
    return None


def _build_palette_material():
    """Create or refresh `Grass Palette`.

    Two ColorRamps (green + dry) keyed by `blade_height`; a Mix node
    picks between them using the per-instance `blade_dry_seed` attribute
    (factor = 1 if seed < DRY_FRACTION, else 0).
    """
    mat = bpy.data.materials.get(BLADE_PALETTE_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(BLADE_PALETTE_MATERIAL)
        print(f"  created material {BLADE_PALETTE_MATERIAL!r}")
    else:
        print(f"  refreshing material {BLADE_PALETTE_MATERIAL!r}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (820, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (560, 0)
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.1
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.85

    # Two ColorRamps fed by the same height factor.
    ramp_green = nt.nodes.new("ShaderNodeValToRGB")
    ramp_green.location = (-40, 200)
    ramp_green.label = "Green Ramp"
    _populate_color_ramp(ramp_green, BLADE_PALETTE)

    ramp_dry = nt.nodes.new("ShaderNodeValToRGB")
    ramp_dry.location = (-40, -200)
    ramp_dry.label = "Dry Ramp"
    _populate_color_ramp(ramp_dry, BLADE_PALETTE_DRY)

    # blade_height attribute (per-vertex, from Plane.012) — drives the
    # ramp lookup for BOTH ramps.
    attr_h = nt.nodes.new("ShaderNodeAttribute")
    attr_h.location = (-300, 200)
    attr_h.attribute_name = BLADE_HEIGHT_ATTR
    attr_h.label = "blade_height"

    # blade_dry_seed attribute (per-instance, stored in Geometry Nodes)
    # — every vertex of an instance shares the same seed value.
    attr_dry = nt.nodes.new("ShaderNodeAttribute")
    attr_dry.location = (-300, -400)
    attr_dry.attribute_name = DRY_SEED_ATTR
    attr_dry.label = "blade_dry_seed"

    is_dry = nt.nodes.new("ShaderNodeMath")
    is_dry.operation = "LESS_THAN"
    is_dry.location = (-40, -400)
    is_dry.label = "is_dry"
    is_dry.inputs[1].default_value = DRY_FRACTION

    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    mix.location = (320, 0)
    mix.label = "green <- mix -> dry"

    factor_in = _find_enabled_input(mix, "Factor")
    a_in = _find_enabled_input(mix, "A")
    b_in = _find_enabled_input(mix, "B")
    result_out = next((o for o in mix.outputs if o.name == "Result" and o.enabled), None)

    nt.links.new(attr_h.outputs["Fac"], ramp_green.inputs["Fac"])
    nt.links.new(attr_h.outputs["Fac"], ramp_dry.inputs["Fac"])
    nt.links.new(attr_dry.outputs["Fac"], is_dry.inputs[0])
    nt.links.new(is_dry.outputs["Value"], factor_in)
    nt.links.new(ramp_green.outputs["Color"], a_in)
    nt.links.new(ramp_dry.outputs["Color"], b_in)
    nt.links.new(result_out, bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return mat


def _assign_palette_material():
    mesh = bpy.data.meshes.get(BLADE_MESH)
    if mesh is None:
        return
    mat = _build_palette_material()
    if len(mesh.materials) == 0:
        mesh.materials.append(mat)
    else:
        mesh.materials[0] = mat
    print(f"  {BLADE_MESH}: material slot[0] → {mat.name} (palette ColorRamp)")


def _add_dry_seed_attribute():
    """Splice a per-point random into `blade_dry_seed` before Instance on Points.

    Wires `Store Named Attribute` between whatever currently feeds
    `Instance on Points.Points` and the input socket itself:

      <upstream> ──► Store Named Attribute (POINT, FLOAT, "blade_dry_seed")
                  Random Value (0..1, seed=99) ─┘
                                                 │
                                                 ▼
                                      Instance on Points.Points

    Material's Attribute node reads `blade_dry_seed`; every realized
    vertex of a given instance shares the spawning point's value.
    """
    ng = bpy.data.node_groups.get(SCATTER_NODE_GROUP)
    if ng is None:
        return
    iop = next((n for n in ng.nodes if n.bl_idname == "GeometryNodeInstanceOnPoints"), None)
    if iop is None:
        print("  [WARN] Instance on Points not found — skipping dry seed")
        return
    points_in = iop.inputs.get("Points")
    if points_in is None:
        print("  [WARN] Instance on Points has no 'Points' input — skipping dry seed")
        return

    upstream_link = next(
        (l for l in ng.links if l.to_node == iop and l.to_socket == points_in),
        None,
    )
    if upstream_link is None:
        print("  [WARN] no upstream link feeding Points — skipping dry seed")
        return
    upstream_sock = upstream_link.from_socket  # cache BEFORE we remove the link

    def _get_or_make(name, bl_idname, location):
        node = ng.nodes.get(name)
        if node is None:
            node = ng.nodes.new(bl_idname)
            node.name = name
            node.label = name
            node.location = location
        return node

    base_x = iop.location.x - 520.0
    base_y = iop.location.y + 220.0

    rnd = _get_or_make(DRY_RANDOM_NODE, "FunctionNodeRandomValue", (base_x, base_y))
    rnd.data_type = "FLOAT"
    min_in = _find_enabled_input(rnd, "Min")
    max_in = _find_enabled_input(rnd, "Max")
    seed_in = _find_enabled_input(rnd, "Seed")
    if min_in is not None:
        min_in.default_value = 0.0
    if max_in is not None:
        max_in.default_value = 1.0
    if seed_in is not None:
        seed_in.default_value = DRY_RANDOM_SEED

    store = _get_or_make(DRY_STORE_NODE, "GeometryNodeStoreNamedAttribute", (base_x + 240.0, base_y - 200.0))
    store.data_type = "FLOAT"
    store.domain = "POINT"
    name_in = store.inputs.get("Name")
    if name_in is not None:
        name_in.default_value = DRY_SEED_ATTR

    # Snapshot stale links FIRST, remove SECOND — touching link.to_node
    # on a removed link raises ReferenceError.
    stale = [
        l for l in ng.links
        if (l.to_node == iop and l.to_socket == points_in)
        or l.to_node == store
    ]
    for l in stale:
        ng.links.remove(l)

    value_in = _find_enabled_input(store, "Value")
    geom_in = store.inputs.get("Geometry")
    if value_in is None or geom_in is None:
        print("  [WARN] Store node missing Value/Geometry inputs — skipping dry seed")
        return

    ng.links.new(upstream_sock, geom_in)
    ng.links.new(rnd.outputs["Value"], value_in)
    ng.links.new(store.outputs["Geometry"], points_in)

    print(
        f"  Store Named Attribute: {DRY_SEED_ATTR!r} on POINT domain "
        f"(random 0..1, seed={DRY_RANDOM_SEED}, P(dry)={DRY_FRACTION:.0%})"
    )


def _add_rotation_jitter():
    ng = bpy.data.node_groups.get(SCATTER_NODE_GROUP)
    if ng is None:
        print(f"  [WARN] node group {SCATTER_NODE_GROUP!r} not found — skipping jitter")
        return
    iop = next(
        (n for n in ng.nodes if n.bl_idname == "GeometryNodeInstanceOnPoints"),
        None,
    )
    if iop is None:
        print("  [WARN] Instance on Points node not found — skipping jitter")
        return
    rotation_input = iop.inputs.get("Rotation")
    if rotation_input is None:
        print("  [WARN] Instance on Points has no 'Rotation' input — skipping jitter")
        return

    rnd = ng.nodes.get(JITTER_NODE_NAME)
    if rnd is None:
        rnd = ng.nodes.new("FunctionNodeRandomValue")
        rnd.name = JITTER_NODE_NAME
        rnd.label = JITTER_NODE_NAME
        rnd.data_type = "FLOAT_VECTOR"
        rnd.location = (iop.location.x - 280.0, iop.location.y - 200.0)
        print(f"  {JITTER_NODE_NAME}: added")
    else:
        print(f"  {JITTER_NODE_NAME}: already present — reusing")

    rnd.inputs["Min"].default_value = (-TILT_X, -TILT_Y, 0.0)
    rnd.inputs["Max"].default_value = ( TILT_X,  TILT_Y, SPIN_Z)

    for link in list(ng.links):
        if link.to_node == iop and link.to_socket == rotation_input:
            ng.links.remove(link)
    ng.links.new(rnd.outputs["Value"], rotation_input)
    print(
        f"  Instance on Points: Rotation ← Blade Rotation Jitter "
        f"(tilt ±{math.degrees(TILT_X):.0f}°, spin 0-360°)"
    )


def _add_size_variation():
    """Splice a per-blade CONTINUOUS random size multiplier into the Scale input.

    Existing wiring:
       Separate Color.Green ──► Instance on Points.Scale
    New wiring:
       Separate Color.Green ─┐
                             ├─► Math(MULTIPLY) ─► Instance on Points.Scale
       Random Value (0..1)   │
            └─► Map Range(0..1 → SIZE_MIN..SIZE_MAX) ─┘

    The earlier binary-bucket threshold node (`Blade Size Threshold`) is
    removed if present so we don't leave dead wiring behind.
    """
    ng = bpy.data.node_groups.get(SCATTER_NODE_GROUP)
    if ng is None:
        return
    iop = next((n for n in ng.nodes if n.bl_idname == "GeometryNodeInstanceOnPoints"), None)
    if iop is None:
        print("  [WARN] Instance on Points node not found — skipping size variation")
        return
    scale_in = iop.inputs.get("Scale")
    if scale_in is None:
        print("  [WARN] Instance on Points has no 'Scale' input — skipping size variation")
        return

    def _get_or_make(name, bl_idname, location):
        node = ng.nodes.get(name)
        if node is None:
            node = ng.nodes.new(bl_idname)
            node.name = name
            node.label = name
            node.location = location
        return node

    base_x = iop.location.x - 760.0
    base_y = iop.location.y - 360.0

    rnd = _get_or_make(SIZE_BUCKET_RANDOM, "FunctionNodeRandomValue", (base_x, base_y))
    rnd.data_type = "FLOAT"
    for inp in rnd.inputs:
        if inp.name == "Min" and inp.enabled:
            inp.default_value = 0.0
        elif inp.name == "Max" and inp.enabled:
            inp.default_value = 1.0
        elif inp.name == "Seed" and inp.enabled:
            inp.default_value = 42  # different from rotation jitter (default 0)

    mapper = _get_or_make(SIZE_BUCKET_MAPPER, "ShaderNodeMapRange", (base_x + 220.0, base_y))
    mapper.data_type = "FLOAT"
    mapper.clamp = True
    mapper.inputs["From Min"].default_value = 0.0
    mapper.inputs["From Max"].default_value = 1.0
    mapper.inputs["To Min"].default_value = SIZE_MIN_FACTOR
    mapper.inputs["To Max"].default_value = SIZE_MAX_FACTOR

    mult = _get_or_make(SIZE_SCALE_MULTIPLIER, "ShaderNodeMath", (base_x + 460.0, base_y))
    mult.operation = "MULTIPLY"
    mult.use_clamp = False

    # Remove the legacy threshold node from the binary-bucket version,
    # if it's hanging around in the graph.
    legacy = ng.nodes.get(SIZE_BUCKET_THRESHOLD_LEGACY)
    if legacy is not None:
        ng.nodes.remove(legacy)
        print(f"  removed legacy node {SIZE_BUCKET_THRESHOLD_LEGACY!r}")

    sep_color = next(
        (n for n in ng.nodes if n.bl_idname == "FunctionNodeSeparateColor"),
        None,
    )
    if sep_color is None:
        print("  [WARN] Separate Color node not found — cannot splice size variation")
        return
    green_sock = sep_color.outputs.get("Green")
    if green_sock is None:
        print("  [WARN] Separate Color has no 'Green' output — cannot splice")
        return

    stale = [
        link for link in ng.links
        if (link.to_node == iop and link.to_socket == scale_in)
        or link.to_node == mult
        or link.to_node == mapper
    ]
    for link in stale:
        ng.links.remove(link)

    ng.links.new(rnd.outputs["Value"], mapper.inputs["Value"])
    ng.links.new(green_sock, mult.inputs[0])
    ng.links.new(mapper.outputs["Result"], mult.inputs[1])
    ng.links.new(mult.outputs["Value"], scale_in)

    print(
        f"  Instance on Points: Scale ← (G mask) × random "
        f"[continuous {SIZE_MIN_FACTOR}–{SIZE_MAX_FACTOR}]"
    )


def _boost_scatter_density():
    ng = bpy.data.node_groups.get(SCATTER_NODE_GROUP)
    if ng is None:
        return
    dist = next(
        (n for n in ng.nodes if n.bl_idname == "GeometryNodeDistributePointsOnFaces"),
        None,
    )
    if dist is None:
        print("  [WARN] Distribute Points on Faces node not found — skipping density boost")
        return
    # Single density input drives both random and uniform methods.
    density_sock = dist.inputs.get("Density")
    density_max_sock = dist.inputs.get("Density Max")
    if density_sock is not None:
        density_sock.default_value = float(SCATTER_DENSITY)
    if density_max_sock is not None:
        density_max_sock.default_value = float(SCATTER_DENSITY)
    print(
        f"  Distribute Points on Faces: Density → {SCATTER_DENSITY} pts/local-m² "
        f"(~{int(SCATTER_DENSITY * 192 * 192 / 1000)}k raw scatter points)"
    )


def run():
    print("[02-ground-grass-blades] curved blade + palette ramp + dry-tip variation + continuous size + tilt+spin + dense scatter")
    _replace_blade_mesh()
    _add_dry_seed_attribute()
    _assign_palette_material()
    _add_rotation_jitter()
    _add_size_variation()
    _boost_scatter_density()
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"  saved -> {BLEND_PATH}")
    except Exception as e:
        print(f"  [WARN] save failed: {e}")


if __name__ == "__main__":
    run()
