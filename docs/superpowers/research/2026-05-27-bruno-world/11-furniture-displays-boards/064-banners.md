# 064_banners.py — 2 race-track branded banner meshes

**Path:** `folio-2025/scripts/blender_world_steps/steps/064_banners.py`
**Lines:** 33
**Adds:** 2 objects (2 MESH) to collection `banners`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `banners` collection. Adds 2 flat plane meshes:

| Object | Type | Mesh | Location | Scale | Notes |
|---|---|---|---|---|---|
| `refBanners` | MESH | `Plane.129` | (-19.35, -0.04, 1.525) | 1.152 uniform | Banner #1 at z=1.525m (head-height) |
| `refBanners.001` | MESH | `Plane.133` | (-19.21, -11.63, 1.525) | 1.152 uniform | Banner #2, ~11.6m south of #1 |

Both banners at x≈-19.3 (west of the race track), aligned vertically (same z=1.525m), no rotation. Spaced ~11.6m apart along the y-axis.

## Key data

- **Datablocks referenced:** meshes `Plane.129` (banner #1), `Plane.133` (banner #2). Different mesh data per banner — they likely have different baked textures
- **Materials assigned:** via mesh datablock — `circuitBrand` (per group .md, branded race-track banner material)
- **Modifiers added:** none
- **Custom properties:** none
- **World positions of key anchors:** see table above. Both at x ≈ -19.3, y ∈ {-0.04, -11.63}, z = 1.525
- **Object types breakdown:** 2 MESH
- **Parent collection:** `banners` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Two-flag pattern for race-track signage:**
1. Two flat plane meshes, each with its own mesh datablock (no shared mesh — they need different bake textures since they show different banner content)
2. Both scaled uniformly to 1.152 — slight oversize from the source plane's authored dimensions
3. Vertically positioned at z=1.525m (a bit above head-height) — readable from ground but not blocking view
4. Spaced 11.6m apart along the south-of-track edge (x=-19.3) — flanking the race start/finish

**Single material `circuitBrand`** for both banners — Bruno's tech-stack branding (likely "WebGL", "WebGPU", "Three.js" branded textures on the planes). The mesh data carries the UVs that select different texture regions per banner.

**Pure visual props:** no colliders, no physics, no interactive anchors. The banners are visual decoration for the race track — players can walk through them.

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.129`, `Plane.133`)
- **Read by:** `999_finalize.py` (parents `banners/` under `circuit/`)
- **Depends on:** `062_circuit.py` (the race-track parent zone)
- **Depended on by:** none

## Notable code patterns

- **`ref` prefix on names** (`refBanners`, `refBanners.001`) — Bruno's runtime-referenced object naming convention.
- **Shortest script in batch 4** — 33 lines, 2 objects. The simplest possible recipe: link two flat planes.
- **No modifiers, no colliders, no custom props** — banners are pure flat-mesh decoration. Bruno's minimum-viable prop pattern.
- **Both meshes scaled identically** (1.152) — Bruno applied a uniform scale-up at the object level. The mesh source was authored slightly undersized.
- **Banner-spacing 11.6m** — matches typical large-format outdoor banner spacing at a race track. Both readable from the same player vantage point.
