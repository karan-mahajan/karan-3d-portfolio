# 096_board.py — projects-zone main info board with paginated images + 5-page slot system

**Path:** `folio-2025/scripts/blender_world_steps/steps/096_board.py`
**Lines:** 541
**Adds:** 38 objects (19 MESH, 19 EMPTY) to collection `board`
**Group:** [11-furniture-displays-boards](../11-furniture-displays-boards.md)

## What it does (code-level)

Creates `board` collection — the **projects-section's main interactive board** with title, body, image carousel, multi-page pagination, next/previous arrows, and URL link. Much larger and more complex than `board.001` (083):

**Visible board layout (at the projects-zone position):**

| Object | Type | Mesh | Notes |
|---|---|---|---|
| `panel` | MESH | `Cube.098` at (-28.44, 22.37, 3.05) — main backing panel, rotZ=0.702 (≈40°) |
| `Cube.077` | MESH | `Cube.107` at (-28.36, 22.29, 2.24) — secondary body frame |
| `Cube.080` | MESH | (deduced) — title block |
| `cube.023` | MESH | `Cube.081` at (-30.89, 20.54, 2.34) — additional frame block |
| `text.003` | MESH | `Plane.043` at (-26.19, 24.38, 2.99) — body text plane #1 (`display_type='WIRE'`) |
| `text.004` | MESH | `Plane.044` at (-30.83, 20.48, 2.99) — body text plane #2 |
| `text.005` | MESH | (per script) — title text |
| `text.006` | MESH | `Plane.045` at (-28.41, 22.34, 3.05) — body text plane #3 |
| `plane` | MESH | `Plane.046` at (-28.36, 22.33, 0.584) — bottom plane |
| `plane.001` | MESH | (similar) — pagination plane page 2 |
| `plane.002` | MESH | (similar) — pagination plane page 3 |
| `plane.003` | MESH | (similar) — pagination plane page 4 |
| `plane.004` | MESH | (similar) — pagination plane page 5 |
| `refArrowNextProject` | MESH | `Plane.030` at (-26.19, 24.40, 2.34) — visible next-arrow for projects pagination |
| `refArrowPreviousProject` | MESH | `Plane.031` at (-30.86, 20.47, 2.34) — visible previous-arrow |
| `refArrowNextImage` | MESH | (similar) — visible next-image arrow |
| `refArrowPreviousImage` | MESH | (similar) — visible previous-image arrow |
| `refImages` | MESH | `Cube.043` at (33.38, -9.75, 1.82) — image plane at STAGING (`display_type='WIRE'`) |
| `refIntersectUrl` | MESH | (per script) — invisible URL raycast plane |

**Anchors / hit-areas (19 EMPTY):**

| Object | Type | Notes |
|---|---|---|
| `refPagination` | PLAIN_AXES | (33.48, -9.83, 0.584) — pagination position |
| `inner` | PLAIN_AXES | (-28.36, 22.33, 0.584) — inner-content anchor co-located with `plane` |
| `refPrevious` | PLAIN_AXES | (31.74, -10.92, 3.47) — previous-project alignment anchor |
| `refNext` | PLAIN_AXES | (34.81, -8.34, 3.45) — next-project alignment anchor |
| `inner.001/.002/.003/.004` | PLAIN_AXES | Various inner-content anchors per page |
| `refTitle` | PLAIN_AXES | Title anchor |
| `refUrl` | PLAIN_AXES | URL spawn anchor |
| `refIntersectPagination` | (hit area) | Pagination click target |
| `refIntersectPagination.001/.002/.003/.004` | (hit areas) | One per page slot (5 total click targets) |
| `refIntersectNextProject` | EMPTY | Next-project click |
| `refIntersectPreviousProject` | EMPTY | Previous-project click |
| `refIntersectNextImage` | EMPTY | Next-image click |
| `refIntersectPreviousImage` | EMPTY | Previous-image click |

## Key data

- **Datablocks referenced:** ~13 distinct meshes (Cube.043, .081, .098, .107, and 9 Plane.* meshes for text/arrows)
- **Materials assigned:** `palette` (per group .md, all objects)
- **Modifiers added:** none
- **Custom properties:** likely `preventFrustum=True` on the invisible raycast meshes (same pattern as 083)
- **World positions of key anchors:**
  - Main board cluster at (-28-31, 20-24, 2.24-3.05) — projects zone
  - Image staging area at (10-35, -8 to -16, ...) — runtime relocates
- **Object types breakdown:** 19 MESH, 19 EMPTY
- **Parent collection:** `board` (re-parented under `projects/` by finalize)

## Technique / recipe

**The biggest interactive UI in the world — 38 objects supporting 5-page pagination + image carousel + URL.**

1. **Multi-frame backing panel system:**
   - `panel` (main backing)
   - `Cube.077` (body frame at z=2.24)
   - `Cube.080` (title frame above)
   - `cube.023` (extra frame block at z=2.34)
2. **Multi-page pagination system** with **5 page slot planes** (`plane`, `plane.001`, `plane.002`, `plane.003`, `plane.004`) — each at slightly different z or position, with matching `refIntersectPagination.*` hit-areas. The 5 planes represent 5 pages of the carousel.
3. **Dual-arrow navigation:**
   - **Project arrows** (`refArrowNextProject` + `refArrowPreviousProject`) — flip between projects in the gallery
   - **Image arrows** (`refArrowNextImage` + `refArrowPreviousImage`) — flip between images within a project
   - Plus matching SPHERE hit areas (`refIntersectNext/PreviousProject`, `refIntersectNext/PreviousImage`)
4. **Multiple text slots** (`text.003`, `.004`, `.005`, `.006`) — 4 text planes for different content regions (title, description, project name, URL).
5. **`refImages`** at far staging (33.38, -9.75) — the image carousel at runtime-controlled offset. Bruno hides it by placing it 60m away from the board.

**Compare to 083 (`board.001`)**: 14 objects vs 38 here. The lab's info board (083) shows ONE page of static text+URL. This projects board (096) shows **5 pages × N projects × M images per project** — Bruno's richest UI.

**`inner`, `inner.001` … `inner.004`** — 5 inner-content anchors, one per page. The runtime swaps which `inner` is the active layout target as pagination changes.

**Decoupled visible mesh vs hit area** — same pattern as 083 but at scale:
- 5× `plane.NNN` + 5× `refIntersectPagination.NNN` = 10 objects for the 5 pagination slots
- 4× arrow MESHes + 4× refIntersect* EMPTYs = 8 objects for navigation
- Each arrow has a SPHERE hit-area sized for forgiving cursor detection

## Connections

- **Reads from:** `005_meshes_*.py` (~13 meshes), `004_materials.py` (`palette`)
- **Read by:** `999_finalize.py` (parents `board/` under `projects/`)
- **Depends on:** `093_projects.py` (parent zone)
- **Depended on by:** runtime carousel system, raycast click detection, URL system, image-loader

## Notable code patterns

- **Largest non-foundation script in batch 4** (541 lines, 38 objects) — Bruno's most content-rich UI is in the projects section.
- **5-page pagination via 5 stacked plane meshes** + 5 matching click hit-areas — a fully baked 5-page UI structure where runtime just toggles visibility.
- **Dual carousel system** (projects × images) — outer pagination is project selection, inner pagination is image-within-project. Each has its own next/previous arrows and hit areas.
- **`refIntersectPagination.NNN`** integer suffixes — runtime iterates them by index, similar to `pin0`…`pin9` (057_pins).
- **38 objects in one script** — heavier than even the bowling pins script (057, 14 objects). The board is the densest single prop in batch 4.
- **No modifiers anywhere** — all geometry is pre-built; no runtime smoothing. The board's polygonal-flat aesthetic is intentional.
- **`refPrevious`, `refNext`, `refTitle`, `refUrl`, `refImages`** — all at the same staging region (~33, -10, varying z). Runtime relocates them to the actual board position.
- **`inner` (unsuffixed) + 4 suffixed `inner.*`** — Bruno reuses inner-content slots across pages. Unsuffixed is the "default" slot; .001-.004 are pages 2-5.
- **`board.001` (083, in lab) is the simpler sibling** of this script. Same pattern, smaller. Bruno uses the same template at different scales of content.
