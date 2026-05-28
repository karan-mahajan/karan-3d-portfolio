# 013_collections.py — empty 120-collection skeleton + parent/child hierarchy

**Path:** `folio-2025/scripts/blender_world_steps/steps/013_collections.py`
**Lines:** 501
**Adds:** 120 collection datablocks + 98 parent→child links + 21 color tags + 8 hide_render flags + 1 hide_viewport flag — no scene objects
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Three sequential phases:

### Phase 1 — create 120 empty collections (~lines 5-244)

```python
if '<name>' not in bpy.data.collections:
    bpy.data.collections.new('<name>')
```
Repeated 120 times for every collection name in Bruno's world.

### Phase 2 — link parent → child (~lines 245-... ≈98 links)

```python
try: bpy.data.collections['<parent>'].children.link(bpy.data.collections['<child>'])
except Exception: pass
```

This builds the tree. Notable parent→child structures:

- **`areas`** (the section-root container) ← `landing`, `career`, `social`, `projects`, `lab`, `cookie`, `altar`, `toilet`, `bowling`, `circuit`, `behindTheScene`, `achievements`, `timeMachine`, `easter.001`. ← 14 children directly under `areas`. This is Bruno's **list of explorable sections**.
- **`bowling`** ← `pins`, `screen`, `bumpers`, `sign`, `furnitures`, `jukebox`, `pinsPosition`, `alley`. 8 children — every sub-collection of the bowling alley.
- **`circuit`** ← `checkpoints`, `cones`, `barrels`, `startingLights`, `timer`, `road`, `zigzag`, `obstacles`, `jump`, `rails`, `scenery`, `airDancers`, `banners`, `leaderboard`, `podium`, `leaderboardReset`. 16 children — the race-track is the most-childed section.
- **`lab`** ← `mainTable`, `scroller`, `board.001`, `blackBoard.001`, `cauldron`, `sideTable`. 6 children.
- **`achievements`** ← `archive.001`, `building`.
- **`behindTheScene`** ← `lightGenerators`, `scenery.001`.
- **`birchTrees`** ← `archives.002`, `visual.002`, `references` (the "reference / hidden" backup templates Bruno keeps for re-baking tree scatters).
- **`cherryTrees`** ← `archives`, `visual.005`, `references.003`.
- **`explosiveCrates`** ← `fwa`.
- **`easter`** ← `egg`.
- **`archives.003`** ← `sudo` (the sudo character lives under archives).

The 16 "container" collections (per the group .md) — `areas`, `scenery.002`, `oakTrees`/`birchTrees`/`cherryTrees`, `behindTheScene`, `bowling`, `circuit`, `landing`, `lab`, `projects`, `social`, `statue`, `timeMachine`, `toilet`, `vehicle` — match the parent collections that get children linked into them here.

### Phase 3 — visual tags + visibility flags (~lines 440-500)

```python
try: bpy.data.collections['<name>'].color_tag = 'COLOR_NN'   # for outliner color coding
try: bpy.data.collections['<name>'].hide_render = True       # exclude from render
try: bpy.data.collections['<name>'].hide_viewport = True     # hide in viewport
```

**Color-tagged collections (21 total)** — purely visual organization in the Blender Outliner:
- `areas` = `COLOR_06` (pink-ish)
- `benches`, `birchTrees`, `bricks`, `bushes`, `cherryTrees`, `explosiveCrates`, `fences`, `flowers`, `lanterns`, `oakTrees`, `poleLights` = `COLOR_02` (orange) — anything that's a **prop scatter family**
- `grass`, `respawns`, `terrain`, `tornado`, `whispersForbiddenAreas` = `COLOR_04` (green) — **ground / world-system** collections
- `easter`, `scenery.002` = `COLOR_07` (red) — **misc / decoration containers**
- `map` = `COLOR_05` (purple) — minimap
- `vehicle` = `COLOR_01` (red-ish) — the car

**Hide-from-render collections (8 total)** — these are **excluded from the view layer at render time**, but their objects exist in the .blend:
- `archive.001`, `archives.001`, `birchTrees`, `checkpoints`, `cherryTrees`, `flowers`, `podium`, `timer`.

The `birchTrees` / `cherryTrees` exclusion is **highly significant**: the trees Bruno's game DOES render are placed by a Geometry-Nodes scatter (probably in the `references` / `references.002` / `references.003` collections), not by direct objects in the named tree collections. The named `birchTrees` / `cherryTrees` hold **archive / reference / visual** templates the scatter reads but doesn't render directly.

**Hide-from-viewport (1)**: only `archive.001`.

## All 120 collection names (in alphabetical order)

`FWA`, `achievements`, `airDancers`, `alley`, `altar`, `altar.001`, `antenna.001`, `anvil`, `archive.001`, `archives`, `archives.001`, `archives.002`, `archives.003`, `archives.004`, `areas`, `banners`, `barrels`, `basaltRocks`, `behindTheScene`, `behindTheScene.001`, `benches`, `birchTrees`, `birchTrees.001`, `blackBoard.001`, `blackBoard.002`, `board`, `board.001`, `bonfire`, `bowling`, `bricks`, `bridges`, `building`, `bumpers`, `bushes`, `cabin`, `career`, `cauldron`, `checkpoints`, `cherryTrees`, `cherryTrees.001`, `circuit`, `cones`, `controls`, `cookie`, `cups`, `default`, `default.001`, `distinctions`, `easter`, `easter.001`, `egg`, `explosiveCrates`, `fences`, `flowers`, `furnitures`, `fwa`, `grass`, `grinder`, `icons`, `jukebox`, `jump`, `kiosk`, `lab`, `landing`, `lanterns`, `leaderboard`, `leaderboardReset`, `lightGenerators`, `mainTable`, `mainTable.001`, `map`, `oakTrees`, `oakTrees.001`, `obstacles`, `oldSchool`, `oven`, `pins`, `pinsPosition`, `playstation`, `podium`, `pole`, `poleLights`, `projects`, `quench`, `rails`, `references`, `references.002`, `references.003`, `respawns`, `road`, `road.001`, `rocks`, `scenery`, `scenery.001`, `scenery.002`, `screen`, `scroller`, `sideTable`, `sign`, `slabs`, `social`, `startingLights`, `statue`, `stool`, `stool.001`, `sudo`, `terrain`, `timeMachine`, `timer`, `title.001`, `toilet`, `tornado`, `tv`, `vehicle`, `vehicle.001`, `visual.002`, `visual.004`, `visual.005`, `whispersForbiddenAreas`, `zigzag`.

(120 unique names confirmed.)

## Key data

- **Datablocks referenced**: none directly. Phase 2 / 3 references collections by name, but always within `bpy.data.collections`.
- **Materials assigned**: n/a.
- **Modifiers added**: n/a.
- **Custom properties**: none.
- **World positions**: n/a (collections are organizational, not spatial).
- **Object types breakdown**: 0.
- **Parent collection**: each new collection initially has no parent — root level. Phase 2 establishes parents via `children.link`.

## Technique / recipe

The "pre-built collection tree" pattern — collections-first, then objects:

- **All 120 collection names defined upfront** before any per-section script runs. This means when 020-139 scripts create objects, they can do `bpy.data.collections['<name>'].objects.link(ob)` and the target collection always exists.
- **Tree structure mirrors the world layout**: `areas` is the explorable-sections root; each major section (`bowling`, `circuit`, `lab`, etc.) is a child of `areas` and itself contains 6-16 sub-collections per the per-section internal layout.
- **`scene.collection.children.link(<root>)` is NOT in this script** — the per-section scripts (or 999_finalize) attach the top-level collections (`areas`, `terrain`, `grass`, `oakTrees`, etc.) to the scene's master collection.
- **Color tags are organizational only**, no render effect — they color-code the Outliner panel so Bruno can visually sort while authoring.
- **`hide_render = True` is the workhorse for "ghost" collections**: the `birchTrees` / `cherryTrees` / `archive.001` / `archives.001` template-trees and the `checkpoints` / `timer` / `podium` debug props all live in the .blend so Bruno can edit them, but never render in the final game. Equivalent to "marked as hidden" in his runtime export.
- **`hide_viewport = True`** on just `archive.001` keeps it out of the viewport (for performance / clutter reduction).
- **120 collections vs ~15 actual gameplay sections**: most of the 120 are sub-collections holding prop families. E.g., the lab is one section but spawns 6 sub-collections. The hierarchy is ~3 levels deep at most.

## Connections

- **Reads from**: nothing.
- **Read by**:
  - Every 020-139 script: `bpy.data.collections['<name>'].objects.link(ob)` to add the script's objects.
  - 999_finalize: traverses the tree, applies object parenting to root empties, attaches view-layer excludes.
- **Depends on**: 000_init (wipe of `bpy.data.collections`).
- **Depended on by**: every later script.

## Notable code patterns

- **`if 'X' not in bpy.data.collections: bpy.data.collections.new('X')`**: explicit guard rather than `get() or new()` (a stylistic choice — the script uses both patterns inconsistently across files).
- **`try/except` around every link/flag** — defensive against missing collection names (e.g., a renamed collection in a future Blender version would break the lookup; the try/except prevents a single failed link from halting the rest).
- **Case-sensitive collision: `FWA` + `fwa`** — two distinct collections that differ only in case. Outliner displays both. Probably one is the "FWA award" achievement, the other is the explosive-crate brand.
- **`achievements` → `archive.001`, `building`** (only 2 children) — the achievements section is shallow. Most depth is under `bowling` and `circuit`.
- **Wide flat `areas` parent** (14 direct children): suggests the world structure is one root section list, not nested deeply.
- **No physical positions**: this script defines purely the *organizational hierarchy*. Spatial information lives in the objects added later. To know where each section *physically is*, you have to look at the per-section objects' coordinates.
- **The duplicates `.001` suffix everywhere** (e.g., `altar.001`, `behindTheScene.001`, `oakTrees.001`, `birchTrees.001`, `vehicle.001`) — most are **archive / template / variant** collections, not actively rendered. They hold the source assets that Geometry-Nodes scatter instances reference.
