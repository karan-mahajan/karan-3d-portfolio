# 083_board.001.py — lab's interactive info board with title/text/images/url/nav arrows

**Path:** `folio-2025/scripts/blender_world_steps/steps/083_board.001.py`
**Lines:** 203
**Adds:** 14 objects (8 MESH, 6 EMPTY) to collection `board.001`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `board.001` collection — the **interactive info board** in the lab (paginated content + clickable navigation). Adds 14 objects:

**Board frame + interactive surfaces:**

| Object | Type | Mesh / Notes |
|---|---|---|
| `panel.002` | MESH | `Cube.175` at (-28.44, 22.37, 3.05). rotZ=0.702 (≈40°). The board's backing panel |
| `text.007` | MESH | `Plane.071` at (-28.41, 22.34, 3.05). rotX=1.571, rotZ=0.698 — vertical text plane (laid against the panel) |
| `refIntersectUrl.001` | MESH | `Plane.072` at (-28.41, 22.35, 3.05). `preventFrustum=True`. Hidden raycast plane for URL-click detection |
| `Cube.178` | MESH | `Cube.179` at (-28.48, 22.43, 3.43). The title block |
| `text.009` | MESH | `Plane.073` at (-28.47, 22.41, 3.43). The title text plane |
| `refImages.001` | MESH | `Cube.171` at (10.82, -15.39, 1.82). The image carousel plane (at staging — runtime relocates) |
| `refArrowNext` | MESH | `Plane.065` at (12.63, -14.09, 2.38). The "next" arrow icon |
| `refArrowPrevious` | MESH | `Plane.068` at (9.20, -16.99, 2.38). The "previous" arrow icon |

**Anchor empties (runtime hooks):**

| Object | Type | Notes |
|---|---|---|
| `refUrl.002` | EMPTY/PLAIN_AXES | (10.85, -15.42, 3.05) — URL spawn anchor (staging) |
| `inner.006` | EMPTY/PLAIN_AXES | (-28.44, 22.37, 3.05) — co-located with panel.002; "inner content area" anchor |
| `refTitle.001` | EMPTY/PLAIN_AXES | (10.83, -15.40, 3.43) — title alignment anchor (staging) |
| `inner.007` | EMPTY/PLAIN_AXES | (-28.48, 22.43, 3.43) — title's inner area anchor |
| `refIntersectNext` | EMPTY/SPHERE | (12.62, -14.01, 2.38) — clickable hit-area for next arrow (sphere collider for raycasts) |
| `refIntersectPrevious` | EMPTY/SPHERE | (9.19, -16.91, 2.38) — clickable hit-area for previous arrow |

## Key data

- **Datablocks referenced:** meshes `Cube.175`, `Cube.179`, `Cube.171` (3 block mesh frames), planes `Plane.071`, `Plane.072`, `Plane.073`, `Plane.065`, `Plane.068` (5 text/image/arrow planes)
- **Materials assigned:** `palette` (per group .md, all uses base palette)
- **Modifiers added:** none
- **Custom properties:** `preventFrustum=True` on `refIntersectUrl.001` — keeps the raycast plane rendered even when off-screen (so URL detection works at any camera angle)
- **World positions of key anchors:**
  - Board panel: (-28.44, 22.37, 3.05) — lab's east wall area
  - Title block: (-28.48, 22.43, 3.43) — directly above the panel (Δz=0.38m)
  - All real board components at z≈3.05-3.43 (lifted above standing height)
  - Staging area for runtime-spawned content: (10-13, -15 to -17, ...) — 39m away from the board
- **Object types breakdown:** 8 MESH, 6 EMPTY
- **Parent collection:** `board.001` (re-parented under `lab/` by finalize)

## Technique / recipe

**Multi-layer interactive UI board:**

1. **Two block frames** (panel.002 + Cube.178) — the board's backing panel and the title plate on top.
2. **Two visible text planes** (text.007 + text.009) — the body text and the title text, both flat planes against the frame.
3. **One hidden interactive plane** (`refIntersectUrl.001`) marked with `preventFrustum=True` and `display_type='WIRE'` — invisible to the camera but used for raycast hit detection when the player clicks the URL.
4. **Two arrow icon meshes** (refArrowNext + refArrowPrevious) for pagination.
5. **Two SPHERE empties** (`refIntersectNext` + `refIntersectPrevious`) as clickable hit-areas next to the arrows — runtime uses these to detect "next" / "previous" clicks.
6. **Multiple `inner` and `ref*` anchors** at staging positions — runtime-spawn anchors for dynamic content (URL strings, title text).

**Bruno's interactive-board pattern: separate visible mesh from raycast collider.**
- Visible arrow mesh (`refArrowNext`) renders the icon
- Hidden SPHERE empty (`refIntersectNext`) is the clickable hit-area
- Runtime tests cursor against the sphere; on hit, advances the carousel

This is a **decoupled mesh-vs-collider design**: the artist controls the visual icon shape, but the click hitbox is a generous sphere (1m radius) that doesn't need pixel-perfect alignment.

**`text.007` and `refIntersectUrl.001` are both at the same exact position** (28.41, 22.34/22.35, 3.05) and orientation — they layer: visible text + invisible click detector. Same trick for `Cube.178` + `text.009` + `inner.007`.

**The naming scheme** (`text.007`, `text.009`, `inner.006`, `inner.007`, `refUrl.002`, `refIntersectUrl.001`) reveals Bruno has many copies across boards in different sections. Suffix `.001`/`.002` denotes which board (this is the LAB's board); `.007`/`.009` distinguish text slots within the board.

**3D-rotation pattern:** text planes use rotX=1.571 (90°) to lay flat against the board's vertical panel, rotZ=0.698 to match the panel's 40° world rotation. This is the **billboard-on-tilted-surface** rotation trick.

## Connections

- **Reads from:** `005_meshes_*.py` (8 meshes), `004_materials.py` (`palette`)
- **Read by:** `999_finalize.py` (parents `board.001/` under `lab/`)
- **Depends on:** `081_lab.py` (parent zone)
- **Depended on by:** runtime carousel/URL system, raycast click-detection

## Notable code patterns

- **`preventFrustum=True`** — keeps the invisible URL-hit plane rendered (i.e., not frustum-culled) so runtime raycasts work even when the player faces away. First appearance in batch 4.
- **`display_type='WIRE'`** on the raycast meshes (`text.007`, `text.009`, `refIntersectUrl.001`) — they're shown as wireframe in Blender (transparent to render), but their geometry is preserved for the raycast collision.
- **SPHERE-typed EMPTYs as click-hitboxes** — Bruno uses `empty_display_type='SPHERE'` with scale=0.366 to create 0.366m-radius spherical click targets. Generous hitbox for forgiving UI.
- **Decoupled visible vs hit mesh** — the visible arrow icon is a plane; the hit area is a separate SPHERE empty. Easier to tune independently.
- **Title above panel** (Δz=0.38m) — Bruno's vertical board layout: title at z=3.43, body at z=3.05. ~38cm spacing.
- **`refIntersect*` naming** for click-detection objects — runtime contract: "if it starts with refIntersect, run it through the raycast pipeline."
- **board.001 vs board (096)** — the lab's board is `.001`, the projects-section's main board is the unsuffixed `board` (which has 38 objects — 19 project slots). Bruno reuses the same UI template but with different content density.
