# World.blend overhaul roadmap

**Date:** 2026-05-27
**Goal:** Improve `tools/blender/world.blend` (and the downstream baked GLB + textures) before any runtime work begins. Study Bruno Simon's folio-2025 *techniques* and apply them to OUR alpine identity and OUR sculpted geometry. The end-state of this roadmap is a richer baked GLB + a freshly authored `static/textures/terrainData.png` data mask — all produced by Blender phase scripts that the user runs and verifies visually inside Blender.
**Parks:** [docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md](../plans/2026-05-27-terraindata-foundation-plan.md) (runtime). Resumes after sub-project F completes.

## Workflow rules

For each sub-project below:

1. **Brainstorm** — clarifying questions one at a time, propose 2-3 approaches, present design in sections, user approves.
2. **Spec** — written to `docs/superpowers/specs/2026-05-27-world-<topic>-design.md` and committed.
3. **Plan** — written to `docs/superpowers/plans/2026-05-27-world-<topic>-plan.md`. For every script: file path, **"How to run"** (open in Blender → Text Editor → `Alt+P`), expected runtime + outputs, **"How to verify in Blender"** (visual checks, refs to inspect, what to compare against). User executes scripts manually; the assistant never runs Blender.
4. **User executes** in Blender. Verifies visually (look at the model, inspect refs, compare renders). Reports back.
5. **Iterate** — if something looks wrong, we adjust the script or back out via `git reset`. Move to next sub-project only after the current one is verified visually.

**No code work** (anything under `src/`, `static/`, `.verify/`) begins until every sub-project A-F is verified and the runtime plan is unparked.

## Textures the user may need to provide

| Sub-project | Textures needed from user | Notes |
|---|---|---|
| A — Palette warm-shift | none | Re-bakes existing `static/textures/palette.png` from updated `_palette.py` hexes. |
| B — Terrain re-color | none | Uses the re-baked palette PNG; terrain UVs already point at palette cells. |
| C — Cobblestone slab refinement | none | Same. |
| D — Mountain backdrop | none | Same. |
| E — Topology / silhouette | none | Pure geometry. |
| F — terrainData.png bake | none | The script **generates** `static/textures/terrainData.png` from world.blend data + ref empties; nothing is fed in. |

**Bruno's textures (`~/Documents/Projects/folio-2025/resources/textures/`):** used as *reference* during script authoring (e.g., to confirm Bruno's PNG channel encoding). NOT shipped in our repo. The parked runtime plan currently references Bruno's `terrainData.png` as a development placeholder — that step is replaced by F's output once F completes.

## Sub-projects

### A — Palette controlled-warmth shift

Aim is already decided (from earlier brainstorm): **keep alpine identity dominant**, warm-shift only the surfaces the player sees most. Mountains, snow, river, pine cells stay cold.

- **Files touched:** `tools/blender/scripts/_palette.py` (3 hex edits — `meadow_grass`, `dirt_path`, `sand_gravel`). Re-run `phase-01-palette-texture.py` to re-bake `static/textures/palette.png`. May re-run `phase-13-export-glb.py` to refresh `static/world/world.glb` if any baked terrain texture is embedded.
- **Visual verify:** open Blender, render or material-preview the terrain. Meadow areas read warmer; mountains/snow/water unchanged.
- **Blocks:** B, C, D.

### B — Terrain re-color

If A's cell-index assignments stay the same, this is **zero code change** — re-baked palette PNG is the only artifact. If cell shifts are needed (e.g., grass cell moves to a new index), edit `phase-02-terrain.py` UV picks accordingly.

- **Files touched:** possibly `phase-02-terrain.py` (UV cell-index picks only). Re-run `phase-13-export-glb.py` to refresh the GLB.
- **Visual verify:** open Blender, inspect the terrain in material preview. The walkable grass band reads warm; transitions to mountain/water look clean.
- **Depends on:** A.

### C — Cobblestone slab refinement

Adjust slab-cell choices + tiling in the existing cobblestone-bearing phase (Phase 2 polish per commit `0302138`). Optionally study Bruno's `slabs.png` + `slabHighColor #ffcf8b` / `slabLowColor #a87762` shading recipe and approximate it via our palette cells.

- **Files touched:** `phase-02-terrain.py` slab block (UV mapping or material slot tweaks). Re-run `phase-13-export-glb.py`.
- **Visual verify:** walk the cobblestone plateau in Blender's viewport. Slabs read as warm-paved path against the new meadow.
- **Depends on:** A.

### D — Mountain backdrop tweaks

Adjust palette choices + band proportions in `phase-12-mountain-bands.py`. Goal: make backdrop read coherently with the new warm-lowlands palette without losing the alpine identity.

- **Files touched:** `phase-12-mountain-bands.py`. Re-run `phase-13-export-glb.py`.
- **Visual verify:** look at the horizon in Blender. Mountain bands read as cold + distant; no awkward palette clashes against warm foreground.
- **Depends on:** A.

### E — Topology / silhouette pass

Re-sculpt `phase-02-terrain.py` (island shape, mountain placement, beach band, valley contours). Biggest scope and riskiest — re-sculpting can break already-placed props from phases 3-11 (showcases, signs, lighthouse, viewpoints). May require `resize-world.py` and `tighten-backdrop.py` reruns.

- **Files touched:** `phase-02-terrain.py` (sculpt parameters). Likely cascading reruns of phases 3-12.
- **Visual verify:** every placed prop sits on terrain correctly (no floating signs, no buried billboards). Camera flyaround confirms silhouette.
- **Independent of palette.**

### F — `terrainData.png` bake (new `phase-14-terrain-data.py`)

New script that paints R/G/B masks and bakes to `static/textures/terrainData.png`:

- **R (slab mask):** rasterize the cardinal walkways from spawn → section refs at ±52.15m + the spawn plaza + each section's inner plaza. White on path, soft Gaussian edge.
- **G (grass mask):** walkable annulus (r ≈ 5 to r ≈ 50) minus R-channel paths. Hand-touch friendly: bake leaves a near-1 across the annulus, fades to 0 toward shore + cardinal sections.
- **B (elevation):** sample the terrain mesh heights into a normalized 0..1 gradient (0 = deepest below sea level, 1 = highest point).

Output: a 256×256 RGB PNG written to `static/textures/terrainData.png`. This is the file the runtime plan's Phase 1 currently expects.

- **Files touched:** new `tools/blender/scripts/phase-14-terrain-data.py`. Writes `static/textures/terrainData.png` directly (no GLB re-bake).
- **Visual verify:** open the output PNG in any image viewer. Eyeball check: paths visible as a "+" shape, grass as a soft ring around them, elevation gradient correlates with the terrain you see in Blender.
- **Depends on:** E (final heights), final walkable layout (drives R + G).

## Sequence

```
            A
            │
   ┌────────┼────────┐                       E (parallel — independent)
   ▼        ▼        ▼                       │
   B        C        D                       │
   └────────┴────────┘                       │
            │                                │
            └────────────┬───────────────────┘
                         ▼
                         F   (after E + final walkable layout)
                         │
                         ▼
   [unpark runtime] docs/superpowers/plans/2026-05-27-terraindata-foundation-plan.md
```

A → (B, C, D in parallel) → wait → E (can start at any point if no palette dependency) → F (after E) → runtime plan resumes.

## What's NOT in this roadmap

- Anything under `src/`, `static/` (except the F-produced PNG), or `.verify/` — those wait until F completes and the runtime plan unparks.
- Authoring our own slab tile texture (Bruno's `slabs.png` equivalent). C tweaks the existing slabs; a custom slab texture is a downstream consideration.
- Bruno's `terrainGrass.exr` / `terrainWater.exr` (HDR data textures). Out of scope; speculative.

## Status

- **Active:** Sub-project A brainstorm begins next.
- **Parked:** Runtime plan (linked above) until F completes.
- **Memory:** No memory entries until at least sub-project A is verified, per the project's "don't auto-update memory until I confirm" rule.
