# 027_slabs.py — 3 cobblestone slab paths (1 with Smooth-by-Angle modifier)

**Path:** `folio-2025/scripts/blender_world_steps/steps/027_slabs.py`
**Lines:** 82
**Adds:** 3 MESH objects in collection `slabs`
**Group:** [03-surface-detail](../03-surface-detail.md)

## What it does (code-level)

3 slab MESH objects:

### Slab 1 — `slabes` (typo: should be "slabs")
- Mesh: `Cube.063` (from [005-meshes-00](../01-foundation/005-meshes-00.md)).
- Location: `(27.69, -16.77, -0.394)` — slightly below ground (terrain compensates).
- Rotation Z: `-0.948` rad (≈ -54°).
- Scale: `(0.813, 0.813, 1.0)` — XY shrunk to 81%, Z unchanged.
- No modifier.

### Slab 2 — `Cube.001`
- Mesh: `Cube.001` (mesh name matches object name).
- Location: `(-1.731, -15.725, 1.000)` — same anchor as the 12 road-segment cubes in [025-road-001](025-road-001.md). Z=+1 lift.
- Rotation: identity.
- Scale: `(1, 1, 1)`.
- **Has `Smooth by Angle.003` modifier**:
  ```python
  m = ob.modifiers.new('Smooth by Angle.003', 'NODES')
  m.use_pin_to_last = True
  m.node_group = bpy.data.node_groups.get('Smooth by Angle.003')
  m['Input_1']  = 0.5236   # angle threshold ≈ 30°
  m['Input_1_use_attribute'] = 0
  m['Socket_1'] = False     # Ignore Sharpness = False
  ```
  The Smooth-by-Angle modifier softens face normals between adjacent faces whose edge angle is ≤ 30°. This rounds the corners of the cobblestones so each tile reads as "weathered" rather than "fresh-cut."

### Slab 3 — `Cube.002`
- Mesh: `Cube.002` (matches object name).
- Location: `(-4.04, 26.57, 0.348)` — well above terrain.
- Rotation Y: `-π` rad (= -180°) → essentially upside-down on Y axis, then visible from above.
- Scale: `(1.89, 1.30, 1.30)` — non-uniformly stretched X-wide.
- No modifier.

## Key data

- **Datablocks referenced**:
  - Meshes: `Cube.001`, `Cube.002`, `Cube.063` (from [005-meshes-00](../01-foundation/005-meshes-00.md)).
  - Node group: `Smooth by Angle.003` (from [003-node-groups](../01-foundation/003-node-groups.md)) — applied to slab 2 only.
- **Materials assigned**: `palette` via each mesh's material slot.
- **Modifiers added**: one `NODES` modifier (`Smooth by Angle.003`) on `Cube.001` only.
- **Custom properties** on `Cube.001` modifier:
  - `Input_1 = 0.5236` (≈ 30° in radians — the Smooth-by-Angle threshold)
  - `Input_1_use_attribute = 0` (use literal value, not per-vert attribute)
  - `Input_1_attribute_name = ''`
  - `Socket_1 = False` (Ignore Sharpness off)
  - `Socket_1_use_attribute = 0`
  - `Socket_1_attribute_name = ''`
- **World positions of key anchors**:
  - `slabes`: `(27.69, -16.77, -0.39)` — south-east of origin
  - `Cube.001`: `(-1.73, -15.73, +1.00)` — south of origin, +1 m above (matches road-segment anchor)
  - `Cube.002`: `(-4.04, 26.57, +0.35)` — north of origin
- **Object types breakdown**: 3 MESH.
- **Parent collection**: `slabs` (child of `scenery.002`, mounted by 022).

## Technique / recipe

The "modifier-on-one-mesh-only" pattern:

- **Each slab is its own MESH object**, not instances of a shared template. The 3 slabs differ in scale, rotation, and mesh data — each is its own bespoke prop.
- **Smooth-by-Angle modifier added ONLY to `Cube.001`**: the other two (`slabes`, `Cube.002`) keep their raw face normals. Bruno selectively applies smoothing where the cobblestone effect benefits from it.
- **Modifier params set via `m['Socket_N']` indexing**: Blender Geometry-Nodes modifiers expose their group inputs as dictionary-style item access on the modifier datablock. `Input_1` is the angle threshold (the second socket of the group; the first being the input Mesh which isn't user-set). `Socket_1` here = the boolean "Ignore Sharpness" input.
- **`use_pin_to_last = True`** for the modifier — keeps it at the end of the modifier stack on the object. Important when multiple modifiers stack (smoothing should be last).
- **The Smooth-by-Angle threshold `0.5236 rad ≈ 30°`** — the default seen in [003-node-groups.md](../01-foundation/003-node-groups.md) for the same group. Bruno doesn't tune the angle per-prop; he uses the group's default everywhere.
- **`slabes` is a typo Bruno kept**: object name is `'slabes'` (sic). The collection is correctly `'slabs'`. Bruno never fixed the misspelling.
- **`Cube.001` at the same anchor as the road segments** (`(-1.73, -15.73, +1.00)`): suggests Cube.001 is a baked output paired with the road bake — possibly a sidewalk slab beside the road, sharing the road's origin.
- **`Cube.002` with `rotation_euler.y = -π`**: a 180° Y-flip — the mesh is mirrored upside-down on Y. Often this is how Bruno re-uses a one-sided mesh on the underside of something.

## Connections

- **Reads from**:
  - 005-meshes-00 (Cube.001, Cube.002, Cube.063)
  - 003-node-groups (`Smooth by Angle.003`)
  - 004-materials (`palette` via mesh slots)
  - 013-collections (`slabs` collection exists)
  - 022_scenery.002.py (parent mounted)
- **Read by**: 999_finalize.
- **Depends on**: 005, 003, 004, 013, 022.
- **Depended on by**: 999_finalize.

## Notable code patterns

- **Geometry-Nodes modifier on a single prop**: `Smooth by Angle.003` is added here for `Cube.001`. Hundreds of other props elsewhere in Bruno's pipeline also use one of the `Smooth by Angle.*` variants — this is the canonical "soften normals" Bruno-step. Apply to any prop where the polygon-edge angles are <30° and you want them shaded smooth.
- **Modifier-key API `m['Input_N']`** vs `m.node_group.interface.items[N].default_value`: Bruno uses the former (item-access on the modifier). This is the Blender 4.x way; it binds the group input to the modifier instance's per-input override.
- **3 slabs total** despite the group .md naming this collection "cobblestone slabs along cardinal paths": Bruno's actual world has 3 slab placements. The cardinal pattern doesn't apply at this layer — that's probably handled by his runtime path system or the terrain mask.
- **Slabs are at very different scales and rotations**: each is a one-off, not a tiled pattern. The visual continuity comes from sharing the `palette` material.
- **`Cube.063` (slabes mesh) is a specifically authored slab mesh**, not a generic cube — likely modeled with cobblestone subdivisions.
