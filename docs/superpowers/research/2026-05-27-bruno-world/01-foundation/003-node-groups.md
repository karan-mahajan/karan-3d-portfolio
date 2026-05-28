# 003_node_groups.py — build the 9 reusable node trees

**Path:** `folio-2025/scripts/blender_world_steps/steps/003_node_groups.py`
**Lines:** 958
**Adds:** 9 node-group datablocks (8 Geometry, 1 Compositor) — no scene objects
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

For each of 9 named groups, the script:

1. `bpy.data.node_groups.new(name, type)` if not present (idempotent).
2. Grabs the group, `nt.nodes.clear()`, builds a local `nodes_by_name = {}` dict.
3. Declares the group's interface via `nt.interface.new_socket(name, in_out=..., socket_type=...)` and sets each socket's `default_value`.
4. Iterates `nt.nodes.new('<bl_idname>')`, sets `n.name`, `n.location`, per-input `default_value`, then registers in `nodes_by_name`.
5. Connects with `nt.links.new(src.outputs[i], dst.inputs[j])` — each link guarded by try/except.

The 9 groups:

### 1. `Auto Smooth` (GeometryNodeTree)

Sockets: out `Geometry`; in `Geometry`, `Angle` (float, default 0.0).
Nodes: Group I/O × 2, two `Set Shade Smooth` (EDGE then FACE domain), `Edge Angle`, `Is Edge Smooth`, `Is Face Smooth`, `Boolean Math` (AND), `Compare` (LESS_THAN-ish with 0.9-rad epsilon defaults). Conceptually: pick which edges to mark smooth based on edge angle vs user threshold + propagate face-shade-smooth flag.

### 2. `Geometry Nodes` (GeometryNodeTree) — **the terrain displacement group**

Sockets: out `Geometry`; in `Geometry` only.
Pipeline: read `UVMap` named-attribute (FLOAT_VECTOR) → `GeometryNodeImageTexture` sampling **`bpy.data.images.get('terrainWater')`** → `Separate Color` → grab one channel → `Math` MULTIPLY by `-1.5` → `Combine XYZ` (X=0, Y=0, Z=channel*-1.5) → `Set Position` (offset=true).
**Effect:** the terrain plane sampled by its UVMap reads the `terrainWater` EXR's red channel, multiplies by −1.5, and pushes vertices down on Z. That's the river/pond depression. The 020_terrain script binds this group as the terrain's modifier; the terrain's depressions exist only because of this 5-node graph.

### 3. `Geometry Nodes.001` (GeometryNodeTree) — **the grass scatter group**

Sockets: out `Geometry`; in `Geometry` (the grass-blade mesh).
Pipeline:
- `Mesh Grid` 192 × 192 m, 512 × 512 verts → a fine grid covering the whole island.
- `Image Texture` samples `bpy.data.images.get('terrainGrass')` with the grid's UVs.
- `Separate Color` → green channel → `Math` LESS_THAN 0.4 → density mask for `Distribute Points on Faces` (density-min=10, density-max=10, distribution=POISSON-ish via seed param).
- `Transform Geometry` (identity), then `Instance on Points` instancing the input Geometry (the 3-vert grass blade from 021) on those scattered points.
- `Instance on Points` rotation input `(-0.9913, 0, 0)` ≈ −56.8° around X (lays blades roughly upright but tilted).
- `Realize Instances` flattens for export.

**Effect:** ~78k grass-blade instances scattered across the island where `terrainGrass.g < 0.4`. The mask is INVERTED — grass goes where green is low (counter-intuitive; worth flagging).

### 4. `Geometry Nodes.002` (GeometryNodeTree) — **rails-along-curve**

Sockets: out `Geometry`; in `Geometry` (a curve or mesh-to-be-curved).
Pipeline:
- `Mesh to Curve` (selection=true) converts input mesh into a curve.
- `Curve to Points` 233 samples, length=4.0 m.
- `Object Info` reads **`bpy.data.objects.get('archivePoleInstance')`** — a separate object (created later in the build) used as the instance to repeat.
- `Instance on Points` places that object at each curve sample, aligned to curve tangent.
- `Realize Instances`.

**Effect:** along any curve input, plant 233 copies of the `archivePoleInstance` object. This is how Bruno builds repeated fence poles, race-track rails, etc. — a curve drives the placement, the modifier reads one instance object by name. Note: this group fails silently if `archivePoleInstance` doesn't yet exist when the group is created (the `try/except` swallows it). It must be repaired/rebound after the instance object is created.

### 5–8. `Smooth by Angle`, `.001`, `.002`, `.003` (GeometryNodeTree)

All four are **identical 14-node graphs**, byte-for-byte. Each:

- Sockets: out `Mesh`; in `Mesh`, `Angle` (float, default 0.5236 ≈ 30°), `Ignore Sharpness` (bool, default False).
- Three `NodeGroupInput` nodes wired to the three respective inputs of one shared body (Group Input.001 → Compare, Group Input.002 → Boolean Math (AND), Group Input.003 → Boolean Math.002).
- Body: `Edge Angle` → `Compare` (against the input Angle, ≤ comparison) → `Boolean Math.001` (OR with Is-Shade-Smooth-AND-Ignore-Sharpness) → drives `Set Shade Smooth (EDGE)` selection. Then `Set Shade Smooth (FACE)` sets shade-smooth to True on every face.

**Why four copies of the same group?** Blender's "Smooth by Angle" modifier creates these as user-instantiated copies (one per import). Bruno's 040+ scripts add a NODES modifier referencing `Smooth by Angle.003` (or `.001`/`.002`) on different prop classes — the suffix is just which copy was active when the modifier was added during authoring. Functionally interchangeable. The `Smooth by Angle` (no suffix) variant additionally has `use_custom_color = True` purple tint on three Group Input nodes — purely cosmetic for the editor.

### 9. `terrain` (**CompositorNodeTree** — not Geometry!)

Sockets: out `Image` (color), in `Image` (color).
4× `CompositorNodeImage` nodes (Image, Image.001/.002/.003 — the four channel-sourced PNGs/EXRs that compose the final terrain texture; image bindings appear unset in the script, presumably set interactively).
`Combine Color` packs the four channels back into one image. `Set Alpha` (Replace Alpha=1.0). Group output.

**Effect:** a compositor sub-graph that recombines the four terrain mask layers (`terrain.png` R/G/B + `terrainAlpha`/`terrainWater`/`terrainGrass`/`terrainFurnitures`) into a single image for downstream baking. This is the **composite-from-EXRs** half of Bruno's PNG-mask pipeline — gives him one workflow image to tweak then re-export.

## Key data

- **Datablocks referenced**:
  - `bpy.data.images.get('terrainWater')` — by `Geometry Nodes` (terrain)
  - `bpy.data.images.get('terrainGrass')` — by `Geometry Nodes.001` (grass)
  - `bpy.data.objects.get('archivePoleInstance')` — by `Geometry Nodes.002` (forward-reference, undefined at this point)
- **Materials assigned**: n/a (groups, not materials)
- **Modifiers added**: n/a (groups are *bound* by later modifier scripts)
- **Custom properties**: n/a
- **Object types breakdown**: 0
- **Parent collection**: n/a

## Technique / recipe

The "shared node-group library" pattern:

- Treat node groups as **named library assets** the rest of the pipeline references. The whole world's smoothing, terrain displacement, grass scatter, and pole-along-curve logic lives in 9 datablocks.
- **Mask-driven scatter**: instead of authoring grass blade-by-blade, use a fine grid (192 m × 192 m at 512 × 512 verts) as point source, then mask by sampling an EXR — grass goes where the EXR's G channel is below a threshold. The grid resolution decouples scatter density from world size.
- **Terrain depression from EXR R-channel**: the river/pond is not modeled as separate geometry. The terrain is a flat plane; the `Geometry Nodes` group multiplies the EXR's red channel by −1.5 and stuffs that into Z. River = where R is bright in `terrainWater`.
- **Curve → array of instances**: the `Geometry Nodes.002` group is the universal "spawn N copies of object X along curve Y" tool. Bruno uses it for poles, rails, possibly path bricks. The object name (`archivePoleInstance`) is hardcoded INSIDE the group — i.e., one rails-along-curve group instance is one specific repeated object, not parametrized.
- **Identical-body groups for naming variance**: four `Smooth by Angle*` groups exist solely because Blender's modifier creates a per-import copy. Bruno doesn't dedupe them.
- **Compositor groups for image-tooling**: the `terrain` CompositorNodeTree is a packing graph used to repack 4 EXR layers back into one image — a developer tool, not a render-time effect.

## Connections

- **Reads from**:
  - 002_images (`terrainWater`, `terrainGrass`)
  - **Forward-reference to** `archivePoleInstance` object (created later in archive scripts under 029/033/037)
- **Read by**:
  - `020_terrain.py` → `Geometry Nodes` (sets a NODES modifier on Plane.134)
  - `021_grass.py` → `Geometry Nodes.001` (sets a NODES modifier on the 3-vert grass triangle)
  - Race-track scripts (065-078) → `Geometry Nodes.002` (rails-along-curve)
  - Dozens of per-section scripts add modifiers `'NODES'` bound to `Smooth by Angle.001/.002/.003` and `Auto Smooth` on their prop meshes
- **Depends on**: 002_images (terrain EXRs must exist as datablocks)
- **Depended on by**: 020, 021, 040+ (every modifier-using script)

## Notable code patterns

- **Procedural graph emission**: the script reads like dumped data — every `n = nt.nodes.new(...)`, `n.location = (...)`, `n.inputs[N].default_value = ...` line is what you'd get if you serialized a node graph node-by-node. There is no helper. 958 lines for 9 graphs is the cost of that emission scheme.
- **Channel-sampling pattern**: read EXR via UV → `Separate Color` → grab one channel → drive scatter/displacement. Bruno uses this twice (terrain Z and grass density). The EXRs are 16-bit-float per channel; reading R or G is reading data, not color.
- **Forward reference into datablock lookup**: `bpy.data.objects.get('archivePoleInstance')` returns None at script-run time (archive objects don't exist yet) but the try/except silently sets None. Bruno relies on Blender's persistence: the modifier resolves the name once `archivePoleInstance` is created.
- **Group socket creation order matters**: outputs first, then inputs (`new_socket('Geometry', in_out='OUTPUT', ...)` before INPUT). Without that order, Blender's UI shows sockets in odd positions.
- **`use_custom_color = True` cosmetic tints**: the `Smooth by Angle` (no suffix) group has three Group Input nodes tinted purple-pink (0.51, 0.21, 0.30). Pure UI hint that those inputs are "the optional params."
- **`Combine XYZ` for selective-axis offset**: `Math * -1.5 → Combine XYZ.z → Set Position offset` is a cleaner pattern than building a vector node graph for "offset only Z by f(image)." Useful idiom.
- **Mask polarity flip**: grass mask `< 0.4` means grass appears in *dark* regions of `terrainGrass.g`. Easy to invert at the EXR-authoring side; worth noting for any future re-author.
