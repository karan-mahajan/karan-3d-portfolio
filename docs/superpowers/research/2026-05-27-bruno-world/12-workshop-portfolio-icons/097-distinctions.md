# 097_distinctions.py — distinctions display table with 3 award badges + 1 medal

**Path:** `folio-2025/scripts/blender_world_steps/steps/097_distinctions.py`
**Lines:** 109
**Adds:** 8 objects (7 MESH, 1 EMPTY) to collection `distinctions`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `distinctions` collection — the **award badges display** in the projects zone:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `cube.024` | MESH | `Cube.085` | (37.12, -10.31, 0.827) | The display base/pedestal. scale=0.712 |
| `table.002` | MESH | `Cube.068` | (37.05, -9.67, 0.494) | The table under the display. rotZ=-1.396 (-80°). Sits at z=0.494 (table-top height) |
| `refel.003` | MESH | `Plane.036` | (37.07, -10.36, 0.866) | A frame/label plane on the display. rotX=1.571 (vertical orientation) |
| `refDistinctions` | EMPTY/PLAIN_AXES | — | (36.97, -9.69, 0.983) | Runtime anchor for the distinctions display |
| `awwwards` | MESH | `Plane.050` | (36.24, -9.60, 0.986) | **Awwwards badge** (Plane.050). `rotation_mode='QUATERNION'`, quat=(0.087, ..., -0.996) — tilted at ~10° |
| `fwa` | MESH | `Plane.054` | (37.18, -10.13, 0.986) | **FWA badge** (Plane.054). QUATERNION rotation (mirrored quat from awwwards) — tilted opposite direction |
| `cssda` | MESH | `Plane.053` | (37.75, -9.38, 0.986) | **CSSDA badge** (Plane.053). QUATERNION rotation similar to awwwards |
| `medal` | MESH | `Circle.004` | (37.94, -10.24, 0.848) | **Medal disc**. Euler rotation rotX=-0.086, rotY=0.015, rotZ=0.348 (≈20°) |

## Key data

- **Datablocks referenced:** `Cube.085`, `Cube.068`, `Plane.036`, `Plane.050` (awwwards), `Plane.054` (fwa), `Plane.053` (cssda), `Circle.004` (medal)
- **Materials assigned:** `palette`, `projectsLabels` (per group .md, branded material for the award labels)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Display base at (37.12, -10.31, 0.827) — projects zone
  - 3 awards spread out across (~36.24 to 37.75, -10.31 to -9.38, all at z=0.986) — small 1.5m-wide strip on top of the display
  - Medal at (37.94, -10.24, 0.848) — slightly to the right of the badges, lower z (sits IN FRONT of/lower than the standing badges)
- **Object types breakdown:** 7 MESH, 1 EMPTY
- **Parent collection:** `distinctions` (re-parented under `projects/` by finalize)

## Technique / recipe

**Award display:**

1. **Table base** (`table.002` / `Cube.068`) at z=0.494 — the underlying table.
2. **Display block** (`cube.024` / `Cube.085`) at z=0.827 — the pedestal on top of the table where the awards stand.
3. **3 award badge planes** (`awwwards`, `fwa`, `cssda`) at z=0.986 (sitting upright on the pedestal):
   - **Awwwards** at (36.24, -9.60) — leftmost
   - **FWA** at (37.18, -10.13) — center
   - **CSSDA** at (37.75, -9.38) — rightmost
4. **Medal disc** (`Circle.004`) at z=0.848 — slightly lower, in front of the badges (probably laid flat on the pedestal in front of the standing awards).
5. **Frame plane** (`refel.003`) — labels/text on the display.
6. **`refDistinctions` anchor** — runtime hook for the whole display.

**Quaternion rotations on the 3 badge planes** — Bruno used QUATERNION rotation_mode for `awwwards`, `fwa`, and `cssda`, with quat values that produce slight (~10°) tilts. The 3 badges aren't perfectly upright — each leans at a slightly different angle. Quat makes the small-angle tilt math cleaner than Euler.

**FWA's quat is mirrored** from awwwards/cssda — FWA leans the opposite way. Visual variation.

**Medal uses Euler XYZ rotation** (`rotation_mode='XYZ'`) with all three angles non-zero — Bruno chose Euler for the medal (more intuitive for laid-flat tilts) and quat for the standing badges.

**3 awards on display = Bruno's actual awards** (Awwwards, FWA, CSSDA) — the iconic web-design awards. They live in his projects zone as bragging-rights display.

**`projectsLabels` material** (per group .md) — branded material applied to the badges. Each badge mesh data carries different UVs to show the right award logo.

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.085/.068`, `Plane.036/.050/.053/.054`, `Circle.004`), `004_materials.py` (`projectsLabels`)
- **Read by:** `999_finalize.py` (parents `distinctions/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent)
- **Depended on by:** runtime UI / hover interactions

## Notable code patterns

- **Quaternion rotations on subtle-tilt props** — Bruno uses QUATERNION mode when the tilt is small + multi-axial (cleaner math than Euler for small angles).
- **`Plane.050/.053/.054` — different mesh datablocks for the 3 badges** — they share the `Plane` topology but carry different UV/material data per badge. Each badge has its own visible logo.
- **Award badge naming = literal brand names** — `awwwards`, `fwa`, `cssda`. Bruno uses unambiguous names for clarity.
- **No `Physical*` suffixes on awards** — they're decoration, NOT pushable. Players can't knock the awards over.
- **Layered z-positioning:** table at 0.494, pedestal at 0.827, badges at 0.986, medal at 0.848 — each prop at its own height. Bruno carefully stacks the display vertically.
- **Tight cluster** (~1.5m × 1m × 0.5m) — all 8 objects in a small volume. The distinctions display is a tabletop scene.
- **No physics dynamic** — the only EMPTY is the runtime anchor, not a physics anchor. This is a pure visual display.
