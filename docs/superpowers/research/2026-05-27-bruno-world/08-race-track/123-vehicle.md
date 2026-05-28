# 123_vehicle.py — empty parent collection for vehicle template variants

**Path:** `folio-2025/scripts/blender_world_steps/steps/123_vehicle.py`
**Lines:** 12
**Adds:** 0 objects to collection `vehicle` (collection-creation only)
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Identical pattern to `044_areas.py`: creates `vehicle` collection and links it to `scene.collection` if not already linked. Zero objects.

```python
coll = bpy.data.collections.get('vehicle')
if coll is None: coll = bpy.data.collections.new('vehicle')
if coll.name not in {c.name for c in bpy.context.scene.collection.children}:
    try: bpy.context.scene.collection.children.link(coll)
    except Exception: pass
```

## Key data

- **Datablocks referenced:** none
- **Materials assigned:** none
- **Modifiers added:** none
- **Custom properties:** none
- **World positions:** none
- **Object types breakdown:** 0 objects
- **Parent collection:** Linked directly to scene root

## Technique / recipe

**Empty parent for vehicle variants.** Like `044_areas.py` reserved the umbrella slot for gameplay zones, `123_vehicle.py` reserves the umbrella slot for vehicle templates. The 3 child collections that will be parented here by finalize (per the group .md): `antenna.001`, `oldSchool`, `default.001` — three car variants.

`137_vehicle.001.py` adds 41 objects to the `vehicle.001` collection (the template vehicle); finalize parents `vehicle.001` under `vehicle/`. Similarly for `antenna.001` and `oldSchool.001`.

## Connections

- **Reads from:** nothing
- **Read by:** `999_finalize.py` (parents `antenna.001`, `oldSchool`, `default.001` under `vehicle/`)
- **Depends on:** nothing (independent)
- **Depended on by:** `137_vehicle.001.py` (whose collection `vehicle.001` gets re-parented under `vehicle/`), and similar antenna/oldSchool scripts elsewhere

## Notable code patterns

- **Self-link pattern** (links to `scene.collection`) — like `044_areas.py` and `120_explosiveCrates.py`. These "umbrella" or "self-managing" collections handle their own scene-root binding.
- **3 vehicle variants** (antenna, oldSchool, default) — Bruno wanted the player to pick (or unlock) different car designs. Each is an instance template; the runtime spawns one based on the user's selection.
- **Smallest script with `scene.collection.children.link()` call** — Bruno uses this script as a stable hierarchy slot for vehicle child collections.
