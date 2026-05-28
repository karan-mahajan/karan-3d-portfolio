# 073_rails.py — bezier-curve-driven rails extruded via Geometry Nodes

**Path:** `folio-2025/scripts/blender_world_steps/steps/073_rails.py`
**Lines:** 195
**Adds:** 8 objects (5 MESH, 3 CURVE) to collection `rails`
**Group:** [08-race-track](../08-race-track.md)

## What it does (code-level)

Creates `rails` collection. Adds 8 mostly-hidden objects that constitute Bruno's curve-driven railing system. ALL 8 objects are `hide_viewport=True` and/or `hide_render=True` — these are the BAKING SOURCES; the visible rail geometry must be generated at runtime by the runtime instancing system.

| Object | Type | Datablock | Location | Hidden | GN modifier |
|---|---|---|---|---|---|
| `archiveRailMesh` | MESH | `BézierCircle.003` | (-66.80, 0.59, 0.01) | viewport+render+select | — |
| `archiveRailsCurve` | CURVE | `bumpersRefrenceMesh.001` | (-66.80, 0.59, 0.00) | viewport+render+select | — |
| `archiveRailsTaperCurve` | CURVE | `BézierCurve` | (-64.38, 41.05, 0.01) | viewport+render+select | — |
| `archiveRailCurve` | CURVE | `bumpersRefrenceMesh.002` | (-66.80, 0.59, -0.37) | viewport+render+select | **`Geometry Nodes.002`** |
| `archivePoleInstance` | MESH | `Plane.084` | (-64.38, 41.05, 0.01) | viewport+render+select | — |
| `archivePoles` | MESH | `Mesh` | (-66.80, 0.59, -0.37) | viewport+render+select | **`Geometry Nodes.002`** |
| `refRailsPhysicalFixed` | MESH | `bumpersRefrenceMesh.006` | (-27.71, -36.68, 0.0) | render only | — |
| `trimesh` | MESH | `BézierCircle.005` | (-66.80, 0.59, 0.01) | render only, `display_type='WIRE'` | — |

Two objects carry a `Geometry Nodes.002` modifier — the **rails-along-curve** generator. Both have it as a non-pinned NODES modifier with no exposed input sockets in this script (the modifier internally reads the path curve and an instance mesh).

## Key data

- **Datablocks referenced:**
  - Curves: `bumpersRefrenceMesh.001`, `BézierCurve`, `bumpersRefrenceMesh.002`
  - Meshes: `BézierCircle.003` (cross-section profile?), `Plane.084` (pole instance template), `Mesh` (a generic mesh datablock — likely empty geometry that the GN replaces), `bumpersRefrenceMesh.006` (baked rail collider), `BézierCircle.005` (cross-section)
  - Node groups: `Geometry Nodes.002` (the rails-along-curve generator)
- **Materials assigned:** via mesh datablocks — `gray` and `palette` (per group .md)
- **Modifiers added:** 2× `Geometry Nodes` (NODES, node_group=`Geometry Nodes.002`, no Input sockets exposed in this script)
- **Custom properties:** none
- **World positions of key anchors:**
  - Main curve cluster at (-66.80, 0.59) — west side of the race track
  - Taper/pole template at (-64.38, 41.05)
  - Baked collider `refRailsPhysicalFixed` at (-27.71, -36.68) — far southeast
- **Object types breakdown:** 5 MESH, 3 CURVE — no EMPTY
- **Parent collection:** `rails` (re-parented under `circuit/` by finalize)

## Technique / recipe

**Curve-driven instancing pattern** using Geometry Nodes:

1. A **bezier curve** (`archiveRailCurve` driven by curve datablock `bumpersRefrenceMesh.002`) traces the path the rails should follow
2. The `Geometry Nodes.002` modifier reads the curve and a **cross-section** (probably `BézierCircle.003` or `BézierCircle.005`) to extrude a tube along the curve
3. A **taper curve** (`archiveRailsTaperCurve` with `BézierCurve` datablock) modulates the tube's radius along its length — useful for tapering rails toward endpoints
4. The **pole instance** (`archivePoleInstance` mesh `Plane.084`) is the support pole geometry that the GN scatters along the curve at intervals (the rail uprights)
5. `archivePoles` (with `Mesh` datablock + GN modifier) is the OBJECT that runs the GN and produces the actual scattered poles
6. `refRailsPhysicalFixed` is the baked collider mesh for the rails (runtime physics)
7. `trimesh` is a wire-display debug helper showing the cross-section circle

**EVERYTHING is hidden** — the rails Bruno actually shows in the world live somewhere else (probably baked and instanced via the runtime TSL system), OR they're rendered through the runtime's geometry-nodes pipeline directly. The .blend just holds the templates.

**`archive` prefix** = "template/source data, not direct render content." Same prefix shows up in 060_sign (`signReference`), 070_leaderboardReset (`archiveReset`), and many others — Bruno's universal naming for "hidden baking sources."

## Connections

- **Reads from:** `007_curves.py` (`bumpersRefrenceMesh.001`, `.002`, `.006`, `BézierCurve`), `005_meshes_*.py` (`BézierCircle.003`, `Plane.084`, `Mesh`, `BézierCircle.005`), `003_node_groups.py` (`Geometry Nodes.002`)
- **Read by:** `999_finalize.py` (parents `rails/` under `circuit/`)
- **Depends on:** `062_circuit.py`, `Geometry Nodes.002` definition (the rails-generator GN must exist in 003)
- **Depended on by:** runtime (likely bakes/instances these at startup)

## Notable code patterns

- **Heavy use of `hide_viewport`/`hide_render`/`hide_select`** — Bruno's pattern for "this data exists but should never be touched by the user in the .blend, and shouldn't render directly." This pattern shows up across the world for runtime-template assets.
- **`display_type='WIRE'`** on `trimesh` — wireframe-only display so the cross-section circle is visible in viewport as a guide but doesn't render solid.
- **Curve datablocks named `bumpersRefrenceMesh.NNN`** (note the misspelling "Refrence" — without a second 'e') — Bruno's typo persists through the asset names; would be a refactor risk to fix later.
- **No exposed Input sockets** on the GN modifier — all parameters baked into the node group itself. Runtime cannot tweak rail count/spacing without editing the GN.
