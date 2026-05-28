# 084_cauldron.py — lab cauldron with glowing liquid sphere + 3-layer mesh stack

**Path:** `folio-2025/scripts/blender_world_steps/steps/084_cauldron.py`
**Lines:** 151
**Adds:** 5 objects (3 MESH, 2 EMPTY) to collection `cauldron`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `cauldron` collection. Adds a 5-object cauldron — body, liquid, heat, plus a ball anchor and physics anchor:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `ball` | EMPTY/SPHERE | — | (-27.95, 19.97, 0.749) | scale=1.490 — visualizes the ball's bounding sphere |
| `refLiquid` | MESH | `Sphere.009` | (-44.30, 15.10, 0.679) | scale=0.749. `Smooth by Angle.002` (Input_1=0.524 rad ≈30°) — the visible liquid sphere |
| `cauldronPhysicalDynamic` | EMPTY/PLAIN_AXES | — | (11.14, -17.30, 0.650) | Physics-dynamic anchor at staging |
| `body.001` | MESH | `Sphere.010` | (-44.30, 15.10, 0.679) | scale=0.749 — co-located with `refLiquid`. The visible cauldron body (sphere shell) |
| `refHeat.001` | MESH | `Sphere.012` | (-44.30, 15.10, 0.679) | scale=0.749, `display_type='WIRE'`. `Smooth by Angle.002` (Input_1=0.524 rad). Hidden heat-effect mesh |

**All 3 mesh objects** (`refLiquid`, `body.001`, `refHeat.001`) at **identical staging position** (-44.30, 15.10, 0.679) with **identical scale 0.749** — they stack on top of each other.

## Key data

- **Datablocks referenced:** `Sphere.009` (liquid), `Sphere.010` (cauldron body), `Sphere.012` (heat); node-group `Smooth by Angle.002`
- **Materials assigned:** `emissiveOrangeRadialGradient` (the liquid), `palette` (body)
- **Modifiers added:** 2× `Smooth by Angle.002` (NODES, Input_1=0.524 rad ≈30°) — on `refLiquid` and `refHeat.001`. The body (`body.001`) is unsmoothed
- **Custom properties:** none
- **World positions of key anchors:**
  - All 3 meshes at staging (-44.30, 15.10, 0.679)
  - Ball SPHERE empty at (-27.95, 19.97, 0.749) — different position, at lab's actual placement
  - Physics anchor at staging (11.14, -17.30, 0.650)
- **Object types breakdown:** 3 MESH, 2 EMPTY
- **Parent collection:** `cauldron` (re-parented under `lab/` by finalize)

## Technique / recipe

**3-mesh sphere stack — body + liquid + heat:**

1. **Cauldron body** (`body.001` / `Sphere.010`) — the visible shell of the cauldron (a hemispherical mesh).
2. **Liquid sphere** (`refLiquid` / `Sphere.009`) — emissive orange, glows from inside the cauldron.
3. **Heat-effect sphere** (`refHeat.001` / `Sphere.012`) — invisible (WIRE display), runtime probably uses it as a particle emitter region or shader-only effect zone.
4. **All 3 stacked at staging coords + same scale** — runtime applies the lab's transform via the `ball` anchor (SPHERE-typed EMPTY at the actual lab placement).
5. **PhysicalDynamic anchor** at yet another staging coord — runtime spawns a dynamic rigid body somewhere else (the cauldron probably isn't pushable; this anchor might be for a heat-affected item).

**`ball` empty as SPHERE** (`empty_display_type='SPHERE'`, scale=1.490) — its 1.49m radius circle in Blender represents the cauldron's bounding volume.

**`refHeat.001`** with WIRE display — the heat sphere is invisible in render but runtime can hook to it. Could be:
- A trigger zone (player walking through the heat zone activates an effect)
- A particle emitter region (smoke/steam spawns from this region)
- A shader-only zone (the heat distortion shader operates within this sphere)

**Same-position stack** of 3 spheres — common pattern for layered emissive effects. Bruno layers the body shell + the inner liquid emissive + the heat marker, all at the same position with the same scale. The runtime renders them in z-order or as separate shader layers.

**Naming variations**: `refLiquid` (unsuffixed), `body.001` (suffixed because there's a body elsewhere — likely the lighthouse 048 or building), `refHeat.001` (also suffixed because of multiple heat-marked props).

## Connections

- **Reads from:** `005_meshes_*.py` (3 sphere meshes), `003_node_groups.py` (`Smooth by Angle.002`)
- **Read by:** `999_finalize.py` (parents `cauldron/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime particle/heat-shader system, physics system

## Notable code patterns

- **3-sphere stack at identical staging** (-44.30, 15.10, 0.679, scale 0.749) — body + liquid + heat. Cleanest example in batch 4 of layered emissive geometry.
- **SPHERE EMPTY for anchor** (`ball`) — display type matches the cauldron's silhouette so the artist sees the bounding region.
- **WIRE display** on `refHeat.001` — keeps it invisible in render. Same trick as raycast meshes in 083 and 096.
- **Two of three meshes get smoothing modifier** — the body skips smoothing (presumably pre-smoothed in mesh data), liquid + heat get the .002 variant. Bruno's per-mesh selective smoothing.
- **Lab cauldron, not projects cauldron** — Bruno has two "forge tool" cauldrons: this one in the lab (alchemy theme) AND the projects-zone cauldron concept (per group .md). Different placements, different narratives.
- **`refHeat.NNN` naming** suggests heat-marker objects exist on other forge tools too (oven 100, etc.). Runtime contract for "where the heat is."
- **Tiny script** (151 lines) for a visually-rich prop — 3 mesh layers + 2 anchors. Bruno's efficient use of stacked geometry for layered shader effects.
