# 006_metaballs.py — 2 metaball datablocks with ~46 BALL elements

**Path:** `folio-2025/scripts/blender_world_steps/steps/006_metaballs.py`
**Lines:** 577
**Adds:** 2 metaball datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Creates two metaball datablocks via `bpy.data.metaballs.new(name)`. For each:

```python
mb = bpy.data.metaballs.new('Mball.NNN')
mb.resolution = 0.36
mb.render_resolution = 0.20
mb.threshold = 0.60
mb.update_method = 'UPDATE_ALWAYS'
# repeated N times:
el = mb.elements.new(type='BALL')
el.co = (x, y, z); el.radius = R; el.stiffness = S
el.rotation = (w, x, y, z)   # quaternion (1, 0, 0, 0) default
el.size_x = 1.0; el.size_y = 1.0; el.size_z = 1.0
el.use_negative = False
mb.name = 'Mball.NNN'         # redundant re-set at end of block
```

Two metaballs, ~46 BALL elements total:

### `Mball.004` (first block, ~lines 5-110)
- Resolution 0.36 (viewport) / 0.20 (render) — fine enough to read as round blobs.
- Threshold 0.60 — standard "where iso-surface lives."
- Update method `UPDATE_ALWAYS` — re-tessellates the implicit surface every frame (heavy, but Bruno doesn't optimize this away).
- Multiple BALL elements with positions roughly in ±2 m around origin, radius `0.833`, stiffness varying between `0.91` and `2.0`.
- One element sits at `Z = -3.20` — much lower than the cluster, suggesting a hanging blob (icicle?).
- Some elements have radius `0.66` (slightly smaller) — mixed-size cluster.

### `Mball.005` (second block, ~line 111-end)
- Same resolution / threshold / update_method.
- Positions shifted further out (origin near `(2.2, 1.8, 0)`) — a second blob group at a different anchor.
- Mix of stiffness values, mostly `2.0` (default) with some at `1.24`.
- Uses identical radius scheme (mostly `0.833`, some `0.656`).

## Key data

- **Datablocks referenced**: none (pure data creation).
- **Materials assigned**: none here (metaballs get material when used by an object in 020+).
- **Modifiers added**: none.
- **Custom properties**: none on the metaball datablock.
- **World positions of key anchors**:
  - `Mball.004` element coords are around the origin (X ±1, Y ±2, Z 0 to -3).
  - `Mball.005` element coords are offset (X 1-2, Y 1-2, Z -0.5 to 0.5).
- **Object types breakdown**: 0 (no scene objects).
- **Parent collection**: n/a — metaball datablocks live in `bpy.data.metaballs`, scene placement happens later.

## Technique / recipe

The "implicit surface for organic blobs" pattern:

- **Metaballs over geometry for amorphous shapes**: rather than modeling a moss patch / mud blob / cluster prop with explicit vertices, Bruno authors a small set of weighted BALL positions and lets Blender compute the iso-surface every frame. Cheaper to author, harder to control precisely.
- **Resolution 0.36 / 0.20**: viewport / render tess resolution. The two values let Blender be coarse in interactive viewport and fine for the final render.
- **`threshold = 0.6` is the standard "skin level"**: lowering it grows the surface outward; raising it shrinks. Bruno keeps both metaballs at the same threshold.
- **`UPDATE_ALWAYS`**: Blender re-meshes the metaball every frame. Important if balls were animated; expensive if they're static. Bruno doesn't optimize this — fine for a Blender-side authoring step that runs once at build time.
- **Mostly identical radius (`0.833`) with a few smaller (`0.656`)**: variation comes from per-ball stiffness more than radius. Smaller-stiffness balls blend in more softly with neighbors.
- **Stiffness `0.91`, `1.24`, `1.35`, `2.0`**: each ball contributes to the iso-field by `stiffness × distance^-2` (roughly). Lower stiffness = the ball "fades" sooner from its neighbors. Bruno uses non-uniform stiffness so the blob has some hotspots and some soft-edges.
- **Quaternion rotation (1, 0, 0, 0)**: default identity for BALL elements (rotation doesn't matter for spheres, only ellipsoids — Bruno could vary `size_x/y/z` to get ellipsoids if needed; here all are 1.0).

## Connections

- **Reads from**: nothing (pure data).
- **Read by**: per-section scripts in 020+ that create scene objects of `type='META'` and assign `ob.data = bpy.data.metaballs.get('Mball.NNN')`. The two scripts most likely to read these are the cabin-moss / mud-pile / organic-blob props (probable matches in the food-misc-fx group 13).
- **Depends on**: 000_init (wipe).
- **Depended on by**: per-section scripts referencing these metaballs.

## Notable code patterns

- **Idempotency missing**: unlike most other foundation scripts, this one doesn't check `if 'Mball.004' not in bpy.data.metaballs` before creating. Running the script twice would create `Mball.004.001` / `Mball.005.001`. Possibly an oversight, or the 000_init wipe is relied upon.
- **Redundant `mb.name = 'Mball.NNN'` at end of block**: the metaball is already named correctly at creation; setting again is a no-op. Likely a serialization artifact (the dumper writes `.name = ...` at the end of every datablock by default).
- **All elements are BALL type**: no CUBE, ELLIPSOID, CAPSULE, or PLANE metaball elements are used. Bruno only needs round blobs, so he sticks with one type.
- **No texture / displacement on the metaballs**: they're pure implicit surfaces. The visual character (mossy, mud-like, etc.) comes from the material applied to the metaball *object* at placement time, not from the datablock here.
- **Group-index stale-name correction**: the group `01-foundation.md` lists "`azeazeaze`" and "`metaMoss`" as the metaball names. The actual names in the script are **`Mball.004`** and **`Mball.005`** (Blender's auto-suffix from `004` and `005`). The `aze...` and `metaMoss` names likely refer to *objects* (in 020+ scripts) that hold these metaballs, not the datablocks themselves.
