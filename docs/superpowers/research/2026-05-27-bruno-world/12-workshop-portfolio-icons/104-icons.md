# 104_icons.py — 9 social platform icons (PhysicalDynamic) + array-reference + collider compounds

**Path:** `folio-2025/scripts/blender_world_steps/steps/104_icons.py`
**Lines:** 555
**Adds:** 23 objects (10 MESH, 13 EMPTY) to collection `icons`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `icons` collection — the **9 social platform icons** that the player can knock around in the social zone. Each is a PhysicalDynamic mesh with a matching cuboid/tube collider.

**9 social icons + 1 fan (10 MESH):**

| Object | Type | Mesh | Location | Notes |
|---|---|---|---|---|
| `twitchPhysicalDynamic` | MESH | `Plane.063` | (24.21, 25.81, 1.465) | Twitch icon (plane) |
| `mailPhysicalDynamic` | MESH | `Cube.074` | (27.68, 25.18, 1.059) | Mail icon (cube) |
| `gitHubPhysicalDynamic` | MESH | `qsdqsdqsd` | (21.05, 24.23, 1.514) | **GitHub icon** with `Auto Smooth` modifier (Socket_2=1.396 rad ≈80°). Mesh name `qsdqsdqsd` is gibberish |
| `linkedInPhysicalDynamic` | MESH | `Curve` | (18.85, 21.50, 1.535) | LinkedIn icon (mesh from a CURVE conversion). `Smooth by Angle.002` |
| `youtubePhysicalDynamic` | MESH | (per script) | (further out) | YouTube icon. Smoothed (Input_1=0.811 rad ≈46.5°) |
| `discordPhysicalDynamic` | MESH | (per script) | (further out) | Discord icon |
| `blueskyPhysicalDynamic.001` | MESH | `Plane.090` | (33.05, 21.35, 1.640) | Bluesky icon (vertical plane, rotX=1.571) |
| `xPhysicalDynamic` | MESH | `Plane.083` | (33.82, 18.11, 1.382) | X (Twitter) icon |
| `onlyfansPhysicalDynamic` | MESH | `Circle.007` | (39.57, 33.21, 1.373) | **OnlyFans icon** (joke?) with `Smooth by Angle.003`. At the FAR EDGE of the social zone (x=39.57) |
| `refFan` | MESH | `Cylinder.023` | (per script) | `preventAutoAdd=True` — runtime-spawned, not auto-loaded |

**Anchor EMPTYs (13):**

| Object | Notes |
|---|---|
| `refCenter` | PLAIN_AXES at (25.95, 18.09, 1.544) — **center anchor for the social zone** |
| `socialArrayReference` | PLAIN_AXES at (25.95, 18.09, 0.0), rotZ=0.449 (≈26°) — **array reference for fan-out arrangement** (referenced by other scripts' ARRAY modifiers) |
| `refOnlyFans` | PLAIN_AXES — OnlyFans icon's runtime hook |
| `cuboid.025/.026/.027/.028/.029/.030/.031/.032/.033` | 9 EMPTY/CUBE colliders, one per social icon mesh |
| `tube` | EMPTY/CUBE (cylinder-shaped collider) for one of the round icons |

## Key data

- **Datablocks referenced:** `Plane.063` (twitch), `Cube.074` (mail), `qsdqsdqsd` (github — gibberish name), `Curve` (linkedIn), `Plane.090` (bluesky), `Plane.083` (x), `Circle.007` (onlyfans), `Cylinder.023` (fan); node-groups `Auto Smooth`, `Smooth by Angle.002`, `Smooth by Angle.003`
- **Materials assigned:** `palette` (per group .md, all icons use palette)
- **Modifiers added:** multiple `Smooth by Angle.*` + `Auto Smooth` (6 NODES modifiers total per group .md)
- **Custom properties:** `preventAutoAdd=True` on `refFan` — runtime-spawned only when needed
- **World positions of key anchors:**
  - 9 social icons clustered in (18.85 to 33.82, 18.11 to 25.81) — a 15m × 8m social-zone area
  - OnlyFans at (39.57, 33.21) — outlier, far from the cluster
  - refCenter at (25.95, 18.09) — central anchor
  - socialArrayReference at the same XY (25.95, 18.09) — used as ARRAY pivot
- **Object types breakdown:** 10 MESH, 13 EMPTY
- **Parent collection:** `icons` (re-parented under `social/` by finalize)

## Technique / recipe

**9 social platform icons as pushable physics-dynamic props:**

1. **9 unique mesh datablocks** — one per platform (no shared template). Each platform's icon mesh has its own logo baked in.
2. **All 9 are `PhysicalDynamic`** — players can knock them around. Each has a `cuboid.NNN` collider sized to the icon shape.
3. **`refFan` with `preventAutoAdd=True`** — the runtime SPAWNS a fan separately (probably for the OnlyFans joke — the runtime spawns a literal fan blowing dollar bills or similar).
4. **`refCenter`** at the social-zone center — anchor for runtime systems (camera focus, particle origin).
5. **`socialArrayReference`** at the same XY as refCenter but at z=0 with rotZ=0.449 — this is a **rotation pivot for ARRAY-modifier instancing**. Other scripts (probably elsewhere in the social zone) use this as the offset reference for a fan-out array of social icons.
6. **9 cuboid + 1 tube colliders** — one per icon, sized to its silhouette. The `tube` collider name signals cylindrical-shape for one of the round icons (probably bluesky or onlyfans).
7. **3 different smoothing-node variants** in one script — `Auto Smooth` (on GitHub), `Smooth by Angle.002` (on LinkedIn), `Smooth by Angle.003` (on OnlyFans). Bruno picks per-icon.

**Gibberish mesh name `qsdqsdqsd`** — same pattern as `sdfsdf`/`qosdjqosjd` in 090 controls. Bruno's pipeline doesn't enforce mesh-name validation. GitHub mesh was authored as a quick test and never renamed.

**`Auto Smooth` modifier** (different from `Smooth by Angle`) — uses a `Socket_2` instead of `Input_1` (different node-group schema). Likely a Blender 4.x variant of the smooth-by-angle pattern.

**`LinkedIn` icon from `Curve` mesh** — first appearance in batch 4 of a curve-converted mesh. The LinkedIn logo was modeled as a Bezier curve in Blender, then converted to mesh data for use.

**OnlyFans icon at outlier position** (39.57, 33.21) far from the other 8 icons — possibly a hidden easter-egg placement: the OnlyFans icon isn't with the official social icons, it's stuck off in a corner.

**`socialArrayReference`** at z=0 with rotation — this empty is the **offset_object** for an ARRAY modifier elsewhere. The same pattern as `chainPulleyArrayReference` in 086 scroller. Bruno uses these named empties as **rotational pivots for array-replication**.

## Connections

- **Reads from:** `005_meshes_*.py` (10 meshes), `003_node_groups.py` (Auto Smooth + Smooth by Angle variants)
- **Read by:** `999_finalize.py` (parents `icons/` under `social/`)
- **Depends on:** `103_social.py` (social zone root), `005_meshes_*.py`
- **Depended on by:** runtime ARRAY modifier instancing (`socialArrayReference` referenced by other scripts), runtime fan-spawn system, physics

## Notable code patterns

- **9 unique mesh datablocks per icon** — no template-share. Each platform's logo is its own mesh.
- **`PhysicalDynamic` on all 9 icons** — they're pushable. Bruno's whimsy: kick the social icons around.
- **Gibberish mesh names survive to production** — `qsdqsdqsd` (GitHub icon). Pipeline doesn't validate.
- **`Curve` mesh datablock** — LinkedIn icon comes from a curve-converted mesh.
- **`socialArrayReference` empty** with rotation — used as offset pivot for ARRAY modifiers elsewhere. Pattern identical to `chainPulleyArrayReference` (086).
- **`preventAutoAdd=True`** on refFan — runtime-spawn-only pattern, same as `pin0`-`pin9` template (057).
- **Mix of smoothing variants** in one script — Bruno picks per-icon (Auto Smooth, Smooth.002, Smooth.003). No consistency.
- **Outlier icon (OnlyFans) placed far from the cluster** — possibly intentional easter-egg or just an old experiment Bruno didn't remove.
- **9 social icons = Twitch, Mail, GitHub, LinkedIn, YouTube, Discord, Bluesky, X, OnlyFans** — Bruno's actual social presence. Realistic per-platform branding.
- **3 different empty hook types** — refCenter (focus anchor), socialArrayReference (array pivot), refOnlyFans (per-icon hook). Multi-role anchor pattern.
- **555 lines, 23 objects** — second-largest script in batch 4 after 096_board.py (541 lines, 38 objects) by line count.
