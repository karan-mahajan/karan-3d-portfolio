# 072_podium.py — race podium with 4 cuboid colliders + confetti spawn anchors

**Path:** `folio-2025/scripts/blender_world_steps/steps/072_podium.py`
**Lines:** 117
**Adds:** 7 objects (1 MESH, 6 EMPTY) to collection `podium`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `podium` collection. Adds 1 visible podium mesh + 4 collider primitives + 2 confetti-spawn anchors:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `refPodiumPhysicalFixed.008` | MESH | `Cube.205` | (-13.66, -14.61, 1.01) | The visible podium mesh. rotZ=-1.047 (-60°). `PhysicalFixed` suffix → static rigid body |
| `cuboid.187` | EMPTY/CUBE | — | (-52.76, 21.84, 0.473) | Collider, rotZ=-1.571 (-90°), scale (3.0, 3.0, 0.909) — the 1st-place step (widest) |
| `cuboid.188` | EMPTY/CUBE | — | (-55.39, 22.22, 0.415) | Collider, rotZ=-1.571, scale (2.25, 2.25, 0.835) — the 2nd-place step (smaller) |
| `cuboid.189` | EMPTY/CUBE | — | (-50.14, 22.22, 0.359) | Collider, rotZ=-1.571, scale (2.25, 2.25, 0.738) — the 3rd-place step (smallest) |
| `cuboid.190` | EMPTY/CUBE | — | (-52.76, 23.46, 2.247) | Collider, rotZ=-1.571, scale (0.36, 7.48, 4.62) — a tall thin back-wall behind the podium (the trophy backdrop?) |
| `refPodiumConfettiA` | EMPTY/PLAIN_AXES | — | (-10.93, -11.63, 0.203) | Confetti spawn anchor A — runtime particle emitter spawn point |
| `refPodiumConfettiB` | EMPTY/PLAIN_AXES | — | (-17.47, -16.04, 0.203) | Confetti spawn anchor B — second confetti emitter |

## Key data

- **Datablocks referenced:** mesh `Cube.205` (the podium silhouette)
- **Materials assigned:** via mesh datablock — `circuitThreejs`, `circuitWebgl`, `circuitWebgpu`, `palette` (per group .md) — the three tech-stack brand mats for the 3 podium steps
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Mesh at (-13.66, -14.61, 1.01) — the visible podium centerpiece position
  - Colliders at (-50.14 to -55.39, 21.84-23.46) — far away from mesh, runtime-bound
  - Confetti A/B at (-10.93, -11.63) and (-17.47, -16.04) — near the visible mesh location, flanking it
- **Object types breakdown:** 1 MESH, 6 EMPTY
- **Parent collection:** `podium` (re-parented under `circuit/` by finalize)

## Technique / recipe

**3-tier podium + decorative back-wall + 2 confetti spawners:**

1. **One visible podium mesh** (`Cube.205`) — pre-modeled with 3 stepped tiers baked in. The mesh carries the multi-material assignment (top step = circuit's main brand, side steps = WebGL/WebGPU/Three.js per the group .md).
2. **3 step colliders** (cuboid.187, .188, .189) at descending scales — sized to match each podium step (1st=widest, 3rd=smallest). All rotated -90° around Z so they align with the podium orientation.
3. **1 back-wall collider** (cuboid.190) — tall and thin (scale 0.36 × 7.48 × 4.62) → blocks players from walking through the back of the podium / trophy display.
4. **2 confetti spawn empties** (refPodiumConfettiA + B) — runtime particle emitters that launch confetti when a race is won. Flanking the visible mesh symmetrically.

**Multi-material on a single mesh:** Bruno's `Cube.205` carries multiple material slots so the same mesh renders with `circuitThreejs` / `circuitWebgl` / `circuitWebgpu` on different parts (one per step). This is how Bruno brands the podium with his tech stack — each step represents a tech (Three.js, WebGL, WebGPU).

**`PhysicalFixed` suffix** — first appearance in batch 4 of the static-rigid-body convention. Unlike `PhysicalDynamic` (rigid bodies that can be pushed), `PhysicalFixed` means the runtime creates a static collider but no movable physics body. The podium doesn't move.

**Colliders at staging position** (-52.76, 21.84) far from the mesh — Bruno stores them at a separate working area. The runtime applies the podium mesh's transform offset.

**Confetti spawn density:** 2 emitters → bilateral confetti coverage when triggered. Both at z=0.203 (low to the ground) — they erupt UPWARD when the event fires.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.205`)
- **Read by:** `999_finalize.py` (parents `podium/` under `circuit/`)
- **Depends on:** `062_circuit.py` (race-track parent), `004_materials.py` (the circuit brand mats)
- **Depended on by:** runtime confetti particle system, race-result UI

## Notable code patterns

- **`refPodium*` and `refPodiumConfetti*`** — the runtime reads these by name to attach systems (e.g., confetti emitters, podium label renderers).
- **3 colliders with descending Z-scale** (0.909, 0.835, 0.738) — heights for the 3 podium steps. Stepped collider matches the stepped visible mesh.
- **`.008` suffix on the podium mesh name** — Blender's auto-suffix indicates Bruno had 8 prior `refPodiumPhysicalFixed.*` objects in earlier iterations; this is the 8th. Suggests heavy iteration on the podium shape.
- **Multi-material mesh** — the podium uses ONE mesh with multiple material slots. Each slot binds to a tech-stack branded material. This is more efficient than 3 separate meshes for 3 steps.
- **No `mass` custom prop** — confirms static (`PhysicalFixed`). The 4 collider primitives also have no mass — they're walk-on (kinematic) colliders.
- **`empty_display_size = 1.0`** on confetti spawners (axes gizmo size) — easy for the Blender artist to spot the emitter locations.
