# 059_screen.py — bowling score screen: panel + label + collider + crosses/discs overlays

**Path:** `folio-2025/scripts/blender_world_steps/steps/059_screen.py`
**Lines:** 224
**Adds:** 8 objects (6 MESH, 2 EMPTY) to collection `screen`
**Group:** [09-bowling](../09-bowling.md)

## What it does (code-level)

Creates `screen` collection. Adds 8 objects forming the score screen mounted above the bowling alley:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refScreenPhysicalKinematicPositionBased` | EMPTY/PLAIN_AXES | — | (13.30, -62.81, 0.00) | Runtime physics anchor |
| `Cube.177` | MESH | `Cube.199` | (-36.53, -28.65, -0.35) | Smooth by Angle.003 (Input_1=π/4 ≈45°) — screen frame |
| `cuboid.092` | EMPTY/CUBE | — | (-34.34, -32.31, 2.12) | Collider, scale (5.21, 0.54, 3.67) — thin screen-shaped |
| `refCrosses` | MESH | `Plane.121` | (-33.38, -28.34, 2.02) | Strike-X overlay |
| `refDiscs` | MESH | `Circle.010` | (-33.38, -28.34, 2.02) | Score-disc overlay (same XY as crosses) |
| `Cube.180` | MESH | `Cube.159` | (-36.53, -28.65, -0.35) | Smooth by Angle.003 — screen back/frame |
| `Cube.182` | MESH | `Cube.185` | (-36.53, -28.65, -0.35) | Smooth by Angle.003 — third frame layer |
| `refLabelStrike` | MESH | `Plane.112` | (-34.32, -32.55, 2.61) | Rotated π/2 around X (the strike-animation label) |

3 of the meshes (`Cube.177`, `Cube.180`, `Cube.182`) have the `Smooth by Angle.003` modifier with Input_1=π/4 rad (45°) — sharp edges for the screen frame.

Note Cube.180 here uses mesh `Cube.159` (a screen frame mesh), distinct from the bowling-pin template `Cube.180` mesh in `057_pins.py`. Naming collision: Bruno reuses `Cube.180` as an OBJECT name in two different scripts, but the underlying mesh DATABLOCKS differ.

## Key data

- **Datablocks referenced:** meshes `Cube.199`, `Plane.121`, `Circle.010`, `Cube.159`, `Cube.185`, `Plane.112`, node-group `Smooth by Angle.003`
- **Materials assigned:** via mesh datablocks — `bowlingLabelStrike`, `emissivePurpleRadialGradient`, `palette` (per group .md)
- **Modifiers added:** 3× `Smooth by Angle.003` (NODES, Input_1=π/4 ≈45°) on the frame meshes
- **Custom properties:** none in this script
- **World positions of key anchors:**
  - Screen anchor at (13.30, -62.81) — bowling zone
  - Most visible meshes at (-36.53, -28.65) and (-33.38, -28.34) — far west "screen depot" location
  - Label strike at (-34.32, -32.55, 2.61) rotated for vertical display
- **Object types breakdown:** 6 MESH, 2 EMPTY
- **Parent collection:** `screen` (re-parented under `bowling/` by finalize)

## Technique / recipe

**Screen assembly with overlay layers:**
1. **3-layer frame** (`Cube.177`, `Cube.180`, `Cube.182`) — three Smooth-by-Angle meshes at the SAME location (-36.53, -28.65, -0.35). Together they form the screen's physical frame/border in 3 pieces (front face, back face, side trim)
2. **Crosses + Discs overlays** (`refCrosses` and `refDiscs`) at the same location (-33.38, -28.34, 2.02) — these are the score symbols (X for strike, / for spare, dots for partial). The runtime swaps which mesh is visible based on current score state
3. **Label strike** (`refLabelStrike`) at (-34.32, -32.55, 2.61) rotated π/2 around X (laid flat or vertical) — the "STRIKE!" animation flash
4. **Anchor + collider** for runtime physics binding

**Mesh objects far off-stage** (-36.53, -28.65) — the screen pieces are NOT at the bowling zone XY but at the "screen depot" area. The runtime probably reads `refScreenPhysicalKinematicPositionBased` anchor (at the bowling zone) and translates the off-stage meshes there.

**`bowlingLabelStrike` material** on `refLabelStrike` — Bruno authored a custom strike-animation texture/shader for this specific label. Polish detail.

**Smooth-by-Angle 45°** on the frame meshes — sharper edges than the universal 55° default. Gives the screen a more rectangular/industrial look.

## Connections

- **Reads from:** `005_meshes_*.py` (many: Cube.199, Plane.121, Circle.010, Cube.159, Cube.185, Plane.112), `003_node_groups.py` (`Smooth by Angle.003`)
- **Read by:** `999_finalize.py` (parents `screen/` under `bowling/`)
- **Depends on:** `052_bowling.py`
- **Depended on by:** runtime score-display logic

## Notable code patterns

- **Same-XY overlay technique**: `refCrosses` and `refDiscs` are at IDENTICAL world coords (-33.38, -28.34, 2.02) — the runtime toggles their visibility to swap the displayed symbol. Standard texture-swap-via-mesh-swap.
- **3 frame meshes at SAME LOCATION** (-36.53, -28.65, -0.35) — Bruno layered three frame parts for the screen, each a separate mesh, all at the same origin. Each carries its own smooth-by-angle.
- **`refLabelStrike` rotated π/2 around X** — Z-Y swap. Makes the label face upward/forward instead of sideways.
- **`KinematicPositionBased` anchor + far-away mesh** — fits the pattern where the visible mesh is parked off-stage and parented to the in-zone anchor at runtime.
- **No `preventFrustum`** — interesting, since the score display is gameplay-critical. Maybe Bruno trusts the bowling zone's frustum to keep the screen rendered while the player is in the alley.
