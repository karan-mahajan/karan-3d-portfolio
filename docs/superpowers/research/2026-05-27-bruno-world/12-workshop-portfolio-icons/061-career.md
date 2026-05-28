# 061_career.py — career timeline with 6 job entries, custom-prop driven per-entry styling

**Path:** `folio-2025/scripts/blender_world_steps/steps/061_career.py`
**Lines:** 493
**Adds:** 32 objects (22 MESH, 10 EMPTY) to collection `career`
**Group:** [12-workshop-portfolio-icons](../12-workshop-portfolio-icons.md)

## What it does (code-level)

Creates `career` collection — Bruno's **career timeline**, structured around **6 `refLine.NNN` anchors** (one per job), each driving an entry's visual via custom properties.

**Per-job structure (template repeated 6 times):**

- `refLine[.NNN]` EMPTY — anchor with **custom props that define the entry**: `hasEnd`, `size`, `color`, `texture`
- `stone[.NNN]` MESH — the stone/plaque at the job position (`Plane.102` mesh, shared)
- `careerText[.NNN]` MESH — the text plane showing the job name/role
- Optional supporting Plane mesh

**6 jobs with their custom props:**

| Anchor | hasEnd | size | color | texture |
|---|:---:|:---:|---|---|
| `refLine` | True | '4' (string) | blue | careerHetic |
| `refLine.001` | True | 2 (int) | orange | careerUzik |
| `refLine.002` | True | 2 | orange | careerImmersiveGarden |
| `refLine.003` | False | 6 | purple | careerOnlineTeacher |
| `refLine.004` | False | 14 | orange | careerFreelancer |
| `refLine.005` | True | 9 | purple | careerIRLTeacher |

**`hasEnd=False`** identifies the 2 still-current jobs (`Online Teacher`, `Freelancer`). `hasEnd=True` for the 4 ended jobs.

**Color distribution:**
- 3× orange (Uzik, Immersive Garden, Freelancer)
- 2× purple (Online Teacher, IRL Teacher)
- 1× blue (Hetic)

**`size` field is the duration in months** (Freelancer 14, IRL Teacher 9, Online Teacher 6, Hetic 4, Uzik 2, Immersive Garden 2). Hetic uses STRING '4' while the others use integer — inconsistency.

**Additional supporting objects:**

| Object | Type | Notes |
|---|---|---|
| `Plane.048` | MESH | `Plane.077` at (23.05, -6.60, 0.040) — timeline backing plane |
| `Plane.049` | MESH | `Plane.078` at (23.05, -6.60, 0.041) — timeline accent plane (Δz=0.001 above .048) |
| `Plane.035` | MESH | `Plane.098` at (27.06, -6.53) — Hetic-specific decoration |
| `Plane.018` | MESH | (per script) — additional timeline element |
| `Plane.022` | MESH | (per script) — additional timeline element |
| `Plane.030` | MESH | Another decoration |
| `refYear` | EMPTY/PLAIN_AXES | The "year" anchor (likely year-tick marker) |
| `digit0`, `digit0.004`, `digit0.005`, `digit0.006` | MESH | 4 digit meshes — likely the year display ('2', '0', '2', '5' or similar 4-digit year) |
| `refZoneBounding.001`, `refZoneFrustum.001` | EMPTY | Career zone bounds + frustum region |
| `career` | EMPTY | Zone root |

## Key data

- **Datablocks referenced:** `Plane.077`, `Plane.078`, `Plane.098`, `Plane.076` (stone), `Plane.102` (stone variant), digit meshes
- **Materials assigned:** `careerTextFreelancer`, `careerTextHetic`, `careerTextIRLTeacher`, `careerTextImmersive`, `careerTextOnlineTeacher`, `careerTextUzik`, `emissiveBlueRadialGradient`, `emissiveOrangeRadialGradient`, `palette` (per group .md)
- **Modifiers added:** none
- **Custom properties:** `hasEnd`, `size`, `color`, `texture` on 6 `refLine.NNN` anchors
- **World positions of key anchors:**
  - Timeline center at (~23, -6.5, 0.04) — central area
  - 6 refLine anchors at varying x positions along the timeline
- **Object types breakdown:** 22 MESH, 10 EMPTY
- **Parent collection:** `career` (re-parented under `areas/` by finalize)

## Technique / recipe

**Custom-prop-driven per-entry visualization:**

1. **6 `refLine.NNN` anchors** define the 6 career entries. Each anchor carries 4 custom props (`hasEnd`, `size`, `color`, `texture`) that the runtime reads to **synthesize the visual for that entry**:
   - `texture` → which `careerText*` material to use (branded per role)
   - `color` → which emissive variant (blue/orange/purple) marks the entry's status
   - `hasEnd` → whether to render a "to-date" cap or leave it open (current job)
   - `size` → likely the duration in months → drives visual length/size of the entry plate
2. **One shared `stone` mesh** (`Plane.102`) — Bruno's template plaque, instanced 6 times (`stone`, `stone.001`, ..., `stone.005`).
3. **6 `careerText.NNN` mesh objects** — each with the same `Plane.076` mesh data but a different material (the careerText* branded mats).
4. **4 digit meshes** for the year display — `digit0`, `digit0.004`, `digit0.005`, `digit0.006` (sparse numbering due to Blender's global counter).
5. **Zone bounding + frustum** for visibility culling around the career area.

**Bruno's data-driven UI pattern:** instead of hand-modeling each entry, he stores the data in custom props on the anchor. The runtime reads the props and applies them. To add a 7th career entry: add a 7th `refLine.NNN` empty with the right props, plus its stone/text meshes. No new visual code needed.

**`color='blue'` is unique to Hetic** (the school/education entry) — distinguishing the educational role from work roles.

**Inconsistent `size` typing** (`'4'` string vs `2/6/14` ints) — Bruno's pipeline doesn't enforce type. Runtime must handle both string and number.

**`hasEnd=True` for 4 jobs, `False` for 2 jobs** — the 2 currently-active jobs (Online Teacher + Freelancer) glow without an end cap; the 4 ended jobs have closed caps. Visual storytelling: "still doing these."

## Connections

- **Reads from:** `005_meshes_*.py` (`Plane.076/.077/.078/.098/.102`, digit meshes), `004_materials.py` (6 careerText* materials + 2 emissive variants), `002_images.py` (career textures)
- **Read by:** `999_finalize.py` (parents `career/` under `areas/`)
- **Depends on:** `044_areas.py` (parent zone)
- **Depended on by:** runtime career-entry renderer, careerText material lookup

## Notable code patterns

- **Data-driven entries via custom props** — most flexible pattern in batch 4. Bruno's career is parametrized; new entries are pure data additions.
- **6 different careerText materials** for 6 different jobs — heavy per-role branding. Each material has its own baked image (careerFreelancer.png, careerHetic.png, etc., loaded by 002_images.py).
- **`hasEnd: bool` + `size: int|str` + `color: enum` + `texture: id` schema** — runtime contract for career entries. Visible only via these 4 props.
- **Inconsistent typing on `size`** (`'4'` vs `2`) — Bruno's pipeline tolerates this. Runtime probably coerces.
- **`digit0` series** for 4-digit year display — single mesh per digit (digit0 + 3 numbered variants). Runtime sets visibility based on the current year.
- **Mix of emissive blues (Hetic) + oranges (3 jobs) + purples (2 jobs)** — three emissive color groups for status differentiation.
- **Career zone at (~23, -6.5)** — central island area, easily visited.
- **`Plane.048` + `Plane.049` stacked at near-identical positions** (Δz=0.001) — two-layer timeline plane: backing + accent strip.
- **Largest portfolio-content script in batch 4** (493 lines) — bigger than even 096_board.py per-object overhead because each entry has 4 custom-prop assignments.
