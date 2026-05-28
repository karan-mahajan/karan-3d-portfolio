# 089_bonfire.py — landing-zone bonfire centerpiece with skull, sword, and burn marker

**Path:** `folio-2025/scripts/blender_world_steps/steps/089_bonfire.py`
**Lines:** 110
**Adds:** 5 objects (4 MESH, 1 EMPTY) to collection `bonfire`
**Group:** [10-lighting](../10-lighting.md)

## What it does (code-level)

Creates `bonfire` collection. Adds 5 objects forming the bonfire prop at the landing zone:

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `base.015` | MESH | `post_skull_skull.001` | (56.16, -47.36, 0.31) | **The skull/log pile base.** `rotation_mode='QUATERNION'`, quat=(0.900, -0.164, 0.150, 0.374) — a non-trivial tilted orientation. **Scale 85.97 uniform** — the mesh is authored at 1cm scale and blown up to bonfire size |
| `refBonfireInteractivePoint` | EMPTY/PLAIN_AXES | — | (53.70, -46.30, 1.50) | "Press E to interact" UI hotspot ~2.5m offset from the base, at chest height |
| `refBonfireHashes` | MESH | `Plane.021` | (55.60, -47.34, -0.013) | Flat plane just below ground level — likely the **scorched-earth marker** under the fire |
| `sword` | MESH | `Cube.090` | (56.27, -46.97, 1.20) | A sword embedded in the bonfire. RotX=-0.144, rotY=0.288, rotZ=-0.125 — leaning at an awkward planted angle. `Smooth by Angle.001` modifier (Input_1=0.524 rad ≈30°) |
| `refBonfireBurn.001` | MESH | `Plane.003` | (55.60, -47.34, -0.025) | Second flat plane, **just below `refBonfireHashes`** (Δz=0.012) — likely the **animated burn/embers** layer |

## Key data

- **Datablocks referenced:** meshes `post_skull_skull.001` (the base), `Plane.021` (hashes/scorch marker), `Cube.090` (sword), `Plane.003` (burn/embers); node-group `Smooth by Angle.001`
- **Materials assigned:** via mesh datablock — `emissiveOrangeRadialGradient` (on burn/hashes), `palette` (base, sword), `redGradient` (on the embers layer per group .md)
- **Modifiers added:** 1× `Smooth by Angle.001` (only on `sword`, Input_1=0.524 rad ≈30°)
- **Custom properties:** none on any object in this script
- **World positions of key anchors:**
  - Bonfire base: (56.16, -47.36) — at the landing zone, north-east area
  - Interactive point: (53.70, -46.30, 1.5) — 2.5m offset, on the player-approach side
  - Burn/hashes layered at near-identical (55.60, -47.34) with Δz ≈ 0.013 — two-layer fire effect
- **Object types breakdown:** 4 MESH, 1 EMPTY
- **Parent collection:** `bonfire` (re-parented under `landing/` by finalize)

## Technique / recipe

**Bruno's centerpiece-prop pattern, plus a multi-layer ground effect:**

1. **Base mesh authored at tiny (1cm-ish) scale, scaled up 85.97×** at the object level — keeps the source mesh data compact while letting Bruno place it at the right world size. The `post_skull_skull.001` mesh name hints at a stylized skull/post hybrid (suggesting a charred bonfire core).
2. **Quaternion rotation** — the base is tilted at an irregular angle that's awkward to express in Euler XYZ. Bruno explicitly sets `rotation_mode='QUATERNION'` for this single mesh.
3. **Interactive point as separate EMPTY** — 2.5m away from the prop, at z=1.5 (player chest height). The runtime shows the interaction prompt here.
4. **Two stacked flat planes for fire effect**: `refBonfireHashes` (z=-0.013) and `refBonfireBurn.001` (z=-0.025) — separated by 12mm so they don't z-fight. One is the scorched-earth texture (matches its hash pattern name), the other is the animated ember/burn shader (likely uses `redGradient`).
5. **Sword embedded at an awkward angle** — the only mesh with a smoothing modifier. Tilted on all three axes, planted point-down in the fire. Pure narrative detail (storytelling: someone left their sword in the fire).

**Why only the sword gets smoothing:** The base skull mesh likely was authored with smooth shading baked into the vertex data (it's a complex `post_skull_skull` mesh). The sword is from a simple `Cube.090` cube primitive that benefits from runtime smoothing.

**`refBonfire*` naming convention** — `ref` prefix marks objects the runtime references by exact name. The `Hashes`, `Burn`, `InteractivePoint` suffixes are runtime contracts: the engine knows to look up these specific names for the bonfire's specific behaviors.

## Connections

- **Reads from:** `005_meshes_*.py` (all 4 meshes), `003_node_groups.py` (`Smooth by Angle.001`)
- **Read by:** `999_finalize.py` (parents `bonfire/` under `landing/`)
- **Depends on:** `088_landing.py` (parent zone)
- **Depended on by:** runtime fire-particle / ember-shader system, interaction system

## Notable code patterns

- **`scale = (85.96..., 85.96..., 85.96...)`** uniform — first appearance in batch 4 of a mesh authored at sub-meter scale and uniformly enlarged. Bruno reuses very-small-scale meshes across the world; this is the trick to keep mesh vertex coords small while placing at real-world sizes.
- **`rotation_mode = 'QUATERNION'`** — first appearance in batch 4. The base.015 mesh has a non-canonical tilted orientation that's cleaner as a quat than 3 Euler angles. Bruno's pipeline preserves the quat for this one mesh.
- **Two-layer ground effect** (hashes plane + burn plane, 12mm apart) — Bruno's technique for layered ground decals: separate planes z-stacked so each can carry its own shader (static texture + animated effect). No alpha-blending conflicts because they're slightly apart.
- **`ref` prefix on names that runtime hooks** — `refBonfireInteractivePoint`, `refBonfireHashes`, `refBonfireBurn.001`. The runtime contract is "if it starts with `ref`, the engine reads it by name."
- **No `mass` custom prop** — the bonfire is static (no Rapier dynamic body). Players can interact via the UI hotspot but can't push the fire.
- **Sword planting via 3-axis Euler rotation** — Bruno hand-tweaked the rotation per-axis to get the "stuck in the ground at an angle" look. The values (rotX=-0.144, rotY=0.288, rotZ=-0.125) are not snapped angles — they're hand-placed.
