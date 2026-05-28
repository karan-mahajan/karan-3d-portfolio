# 094_anvil.py — projects-zone anvil with hammer and blade props

**Path:** `folio-2025/scripts/blender_world_steps/steps/094_anvil.py`
**Lines:** 77
**Adds:** 5 objects (3 MESH, 2 EMPTY) to collection `anvil`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `anvil` collection. Adds the anvil + hammer + blade props for the projects-zone forge:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `Cube.094` | MESH | `Cube.127` | (-22.37, 20.72, 0.263) | The visible anvil base. scale=1.294 uniform. No rotation |
| `refHammer` | MESH | `Cube.129` | (39.88, -10.93, 1.750) | The hammer mesh **at the projects zone's actual position** (rotZ=-0.611 ≈-35°). scale=1.294 |
| `refBlade` | MESH | `Plane.057` | (-22.53, 20.96, 1.468) | The blade plane at staging (rotZ=0.524 ≈30°). scale=1.294 |
| `refAnvilPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (39.47, -11.44, 0.743) | Anvil physics anchor at the projects zone (empty_display_size=2.0 — visible-larger gizmo) |
| `cuboid.054` | EMPTY/CUBE | — | (0.39, 25.83, 0.743) | Anvil collider, rotZ=-1.571 (-90°), scale (1.16, 1.28, 1.44) — at staging |

## Key data

- **Datablocks referenced:** `Cube.127` (anvil), `Cube.129` (hammer), `Plane.057` (blade)
- **Materials assigned:** `palette`
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:**
  - Anvil at (-22.37, 20.72, 0.263) — projects zone staging (this is also where the projects bound is)
  - refHammer at (39.88, -10.93, 1.750) — actual projects-zone placement
  - refBlade at (-22.53, 20.96, 1.468) — co-located with anvil but elevated (Δz=1.2m, on top of the anvil)
  - Anvil physics anchor at (39.47, -11.44, 0.743) — projects zone, near hammer
  - Collider at (0.39, 25.83, 0.743) — separate staging
- **Object types breakdown:** 3 MESH, 2 EMPTY
- **Parent collection:** `anvil` (re-parented under `projects/` by finalize)

## Technique / recipe

**Anvil + hammer + blade as a forging-station trio:**

1. **Anvil base** (`Cube.094` / `Cube.127`) — the chunky visible anvil, no rotation, scale 1.294 (slightly upsized).
2. **Hammer** (`refHammer` / `Cube.129`) — placed at the projects-zone's actual position (39.88, -10.93), suggesting the hammer is **NOT at the anvil** but somewhere else in the zone (probably on the projects table or hanging on a wall). Rotated -35° around Z.
3. **Blade** (`refBlade` / `Plane.057`) — a flat plane mesh (the blade as a 2D billboard) sitting **on top of the anvil** at z=1.468 (anvil at z=0.263 + ~1.2m, which is anvil-top height + the blade's vertical extent).
4. **Anvil physics anchor** (`refAnvilPhysicalDynamic`) — at the projects zone (39.47, -11.44). The anvil is dynamic-physics-active.
5. **One CUBE collider** at staging (0.39, 25.83) sized to the anvil's body.

**Different "staging" patterns for different roles:**
- Anvil mesh at the projects-zone position (-22.37, 20.72) — this is where the visible anvil sits in the world
- Hammer at (39.88, -10.93) — separate position (real placement in zone)
- Blade at (-22.53, 20.96) — co-located with anvil (sits on top)
- Anvil collider at (0.39, 25.83) — yet another staging area

Bruno's pattern: different runtime-systems read different anchors. The visible anvil + the blade are at the anvil position; the hammer is elsewhere; the physics body anchor is at the zone position; the collider is at a separate staging.

**Uniform scale 1.294 across the 3 mesh objects** — Bruno upsized the source meshes uniformly. The anvil + hammer + blade share the same scaling.

**`Plane.057` as blade** — a flat plane representing the blade. Cheap 2D approximation; the texture carries the blade detail.

**Empty display size 2.0** on `refAnvilPhysicalDynamic` (vs the usual 1.0) — Bruno made the anchor extra-visible for the artist (twice the default gizmo size in Blender).

## Connections

- **Reads from:** `005_meshes_*.py` (`Cube.127`, `Cube.129`, `Plane.057`)
- **Read by:** `999_finalize.py` (parents `anvil/` under `projects/`)
- **Depends on:** `093_projects.py` (projects parent)
- **Depended on by:** runtime forging-animation system, physics

## Notable code patterns

- **Anvil + hammer + blade trio** for the forge-tool metaphor — Bruno's projects-as-blacksmithing narrative.
- **3 different "staging" positions** for 3 different roles (visible mesh, hammer, anvil collider) — Bruno's runtime reads from each independently.
- **`refHammer` and `refBlade`** — runtime hooks. The runtime probably animates the hammer striking the blade on the anvil (project-completion animation).
- **`Cube.094` named like other Cube.NNN meshes** — Bruno's exporter doesn't rename meshes. This is the anvil; in 099_mainTable.001 there's also a `Cube.090` (projects table). Global Cube counter.
- **No `mass` custom prop** — anvil is dynamic via the `PhysicalDynamic` suffix but uses runtime's default mass (probably heavy by default).
- **Same scale 1.294 across the trio** — visual consistency between anvil + hammer + blade. Bruno's forge tools share scaling.
- **Empty_display_size=2.0** — Bruno occasionally enlarges the artist-visible gizmo for important anchors.
- **No smoothing modifiers** — all 3 mesh datablocks are pre-smoothed or polygonally angular by design (anvils are blocky).
