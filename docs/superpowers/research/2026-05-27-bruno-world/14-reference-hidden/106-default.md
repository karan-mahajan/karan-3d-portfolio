# 106_default.py — the statue character (rigged Bruno avatar)

**Path:** `folio-2025/scripts/blender_world_steps/steps/106_default.py`
**Lines:** 618
**Adds:** 15 objects (7× EMPTY, 5× MESH, 3× ARMATURE) to collection `default`
**Group:** [14-reference-hidden](../14-reference-hidden.md)

## What it does (code-level)
The most complex character setup in the world. Builds 3 separate rigged figures (baguira/boy/sudo physical-dynamic variants) plus a static statue mesh — all in the `default` collection (which is `statue` zone's main asset).

Structure (in script order):
1. **baguira variant** — `baguiraPhysicalDynamic` (ARMATURE, `Armature.007`) at `(26.09, 18.94, 1.53)` scale 1.156. Paired with `baguiraMesh.001` (MESH `Cube.195`) — vertex-grouped + ARMATURE modifier binding to `baguiraPhysicalDynamic`. Plus 2 collision cuboids (`cuboid.037`, `cuboid.038`).
2. **boy variant** — `boyPhysicalDynamic` (ARMATURE, `Armature.006`) at `(26.93, 17.23, 1.53)` + `boyMesh` (MESH `Cube.194`) with vertex groups + ARMATURE modifier. Plus `cuboid.036`.
3. **statue mesh** — `refStatuePhysicalDynamic` (MESH `Cube.189`) at `(25.96, 18.45, 3.31)` — the visible statue without an armature (a frozen pose of the Bruno avatar). Plus `cuboid.034`, `cuboid.035` (collision boxes around the statue).
4. **sudo variant** — `sudoPhysicalDynamic` (ARMATURE, `Armature.003`) at `(25.39, 17.53, 1.53)` + `cuboid.039`, `cuboid.040`. Then `sudoMesh.003` (MESH `Cube.191`) with vertex groups + ARMATURE modifier.
5. **wings** — `wings` (MESH `Plane.096`) at `(-13.60, 54.98, 1.40)` — separate winged accessory, with a **MIRROR modifier** (mirroring on Y axis like the antenna). Position is FAR (~13,55), not at the statue — likely the wings for the rigged characters at their authored location elsewhere; parented to `sudoPhysicalDynamic` in finalize and translated to statue position.

## Key data
- **Datablocks referenced**:
  - Armatures: `Armature.003` (sudo), `Armature.006` (boy), `Armature.007` (baguira).
  - Meshes: `Cube.122`/`123`/`189`/`191`/`193`/`194`/`195`, `Plane.096` (wings).
- **Materials assigned**: `palette` (via mesh data on all visible meshes).
- **Modifiers added**: 3× ARMATURE (boyMesh→boyPhysicalDynamic, sudoMesh.003→sudoPhysicalDynamic, baguiraMesh.001→baguiraPhysicalDynamic), 1× MIRROR (on wings, Y-axis).
- **Custom properties**: none directly.
- **World positions**: all 3 character bodies cluster near `(26, 18, 1.5)` — the statue plaza. Wings at `(-13.6, +54.98)` (separate, will be parented).
- **Object types breakdown**: 7 EMPTY (`cuboid.034..040` collision/anchor boxes), 5 MESH (`baguiraMesh.001`, `boyMesh`, `refStatuePhysicalDynamic`, `sudoMesh.003`, `wings`), 3 ARMATURE (`baguiraPhysicalDynamic`, `boyPhysicalDynamic`, `sudoPhysicalDynamic`).
- **Parent collection**: `default` → parented under `statue` in finalize. VISIBLE.

## Technique / recipe
- **One statue, multiple variants**: Bruno keeps 3 differently-rigged Bruno avatars (baguira/boy/sudo) AND a static statue mesh in the same collection — likely so the runtime can swap which one is "active" based on game state (early game = boy, after achievement = baguira, hidden = sudo, ambient = statue).
- **Vertex groups + ARMATURE modifier per character**: same pattern as [128_sudo.md](../13-food-misc-fx/128-sudo.md) but with 3 characters in one script.
- **Statue mesh has NO armature** (`refStatuePhysicalDynamic`) — it's a "frozen pose" baked from a rig, so the player sees an immutable statue.
- **Collision cuboids per character** — 7 cuboids total, 1-2 per character, sized to body. Used by the physics system for player-statue interaction (e.g., the FWA award reveal).

## Connections
- **Reads from**: `008_armatures.py` (3 armatures), `005_meshes_*` (8 mesh datablocks).
- **Read by**: `999_finalize.py` (parents all under the `statue` zone empty + sets parenting between meshes and their armatures).
- **Depends on**: 008, 005, 013.
- **Depended on by**: 107 (FWA), 999_finalize.

## Notable code patterns
- **Three identical-anatomy rigged characters** at near-identical world positions — the runtime overlays/swaps them rather than placing them apart.
- The `wings` mesh is at a FAR location `(-13.6, +54.98)` — it's authored in a sandbox area, will be parented to `sudoPhysicalDynamic` via finalize's matrix_parent_inverse so it ends up attached to sudo's body when displayed.
- Mesh-data sharing isn't used here (each character has its own Cube.NNN) — Bruno wants per-character sculpting freedom, NOT mesh sharing.
- **15 objects = 7 EMPTY + 5 MESH + 3 ARMATURE** — matches group index exactly.
- Heavy script (618 lines) but the bulk is inline vertex weights (same pattern as [128_sudo](../13-food-misc-fx/128-sudo.md)).
