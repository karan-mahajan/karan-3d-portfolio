# 057_pins.py — 1 pin template mesh + 10 pin-spawn empties + collider primitives

**Path:** `folio-2025/scripts/blender_world_steps/steps/057_pins.py`
**Lines:** 231
**Adds:** 14 objects (1 MESH, 13 EMPTY) to collection `pins`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `pins` collection. Adds 1 pin mesh template + 10 pin instance empties + 2 collider primitives + 1 anchor:

**Pin mesh template** (1 object):
- `refPinPhysicalDynamic` MESH(`Cube.180`) at (-6.88, -67.98, 0.00) — `preventAutoAdd=True` custom prop. The mesh is at the bowling zone's general area but with `preventAutoAdd` the runtime SKIPS adding it to the scene at startup. Pins are runtime-spawned per game.

**Collider primitives** (2 EMPTY):
- `tube.005` CUBE at (~0, 0, 0.81) scale (0.975, 0.975, 1.59) — narrow tall pin body collider
- `tube.004` CUBE at (~0, 0, 2.26) scale (0.599, 0.599, 1.33) — even narrower top portion (pin head)

These are at LOCAL origin (~0, 0), making them the LOCAL collider shape relative to a spawned pin.

**Pin instance empties** (10 EMPTY/PLAIN_AXES, `empty_display_size=0.707`):
| Empty | Local Location |
|---|---|
| `pin0` | (-49.87, -26.33, 0) |
| `pin1` | (-51.02, -27.05, 0) |
| `pin2` | (-51.02, -25.61, 0) |
| `pin3` | (-52.16, -27.77, 0) |
| `pin4` | (-52.16, -26.33, 0) |
| `pin5` | (-52.16, -24.88, 0) |
| `pin6` | (-53.33, -28.49, 0) |
| `pin7` | (-53.33, -27.05, 0) |
| `pin8` | (-53.33, -25.61, 0) |
| `pin9` | (-53.33, -24.16, 0) |

Plus `refPinPositions` PLAIN_AXES at (~0, 0, 0) — the anchor that runtime translates to align all pins to the lane.

## Key data

- **Datablocks referenced:** mesh `Cube.180` (pin template)
- **Materials assigned:** via mesh datablock — `palette`
- **Modifiers added:** none
- **Custom properties:** `preventAutoAdd=True` on the pin mesh template — instructs the runtime "don't auto-spawn this object; the bowling-game logic will spawn it on demand"
- **World positions of key anchors:**
  - Pin template at (-6.88, -67.98) — bowling zone, but invisible due to preventAutoAdd
  - 10 pin-position anchors in a clustered area far away (around -52, -26) — these are TEMPLATE positions; `refPinPositions` will translate them
  - Local collider tubes near origin
- **Object types breakdown:** 1 MESH, 13 EMPTY
- **Parent collection:** `pins` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Runtime-spawned pin system:**
1. **`preventAutoAdd=True` on the template** stops the .blend from auto-spawning the pin mesh into the scene at startup
2. **10 named pin instance empties** (`pin0` through `pin9`) define the **local pin layout** — classic 4-3-2-1 triangle. Coordinates show pins at x ≈ -49.87 to -53.33, y ≈ -28.49 to -24.16 — a roughly 3.5m × 4m triangular cluster
3. **`refPinPositions` PLAIN_AXES at origin** is the runtime alignment anchor — the runtime probably translates this empty to the bowling lane's pin deck, dragging all 10 pin instances with it
4. **2 collider tubes at local origin** define the pin's **collision shape** (a 2-tube compound: lower wide body + upper narrow head — matches a bowling pin's silhouette)

This is the cleanest example so far of Bruno's **template + spawn-anchor + collider compound** pattern:
- 1 mesh template (preventAutoAdd)
- N named anchor empties for spawn positions
- Collider primitives defining the spawn collider shape

The runtime, on "new bowling game" event, clones the template at each pin anchor with the compound collider attached.

**The 10 pin layout** has the classic bowling triangle:
- Row 1 (1 pin): pin0
- Row 2 (2 pins): pin1, pin2
- Row 3 (3 pins): pin3, pin4, pin5
- Row 4 (4 pins): pin6, pin7, pin8, pin9

X-spacing ≈ 1.15m between rows, y-spacing ≈ 1.44m within rows. Real bowling pins are 12-inch (0.305m) apart center-to-center, so Bruno's scale ≈ 4× real (matching the giant car scale of the game).

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.180`)
- **Read by:** `999_finalize.py` (parents `pins/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime bowling game logic (reads `pin0`-`pin9` + `refPinPositions` + spawn template)

## Notable code patterns

- **`preventAutoAdd=True`** — first appearance of this custom prop in batch 3. Bruno's pattern: any prop that's runtime-spawned (not statically placed) gets this flag.
- **`pin0`-`pin9` simple-integer suffix naming** — easy for the runtime to iterate. Bruno avoided `pin.001`-`pin.010` because Blender adds `.NNN` suffixes for duplicates and this would confuse the lookup.
- **Compound collider via two stacked tubes** (tube.004 and tube.005) — pin shape approximated by two cylinders. Same compound-collider pattern seen on cones (067), but pins use tubes (cylinder) instead of cuboids (box). Naming maps to runtime shape class.
- **`refPinPositions` anchor at origin** — Bruno's universal "runtime alignment empty" pattern. The runtime translates this and all children move.
- **Pin instance empties not at the bowling zone but at (-52, -26)** — far west of the bowling alley (bowling zone is near (2, -68)). This odd location suggests the empties are stored in a "pin staging area" until runtime alignment.
