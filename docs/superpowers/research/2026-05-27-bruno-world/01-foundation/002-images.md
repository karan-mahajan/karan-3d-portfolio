# 002_images.py — load 25 PNG/EXR textures into `bpy.data.images`

**Path:** `folio-2025/scripts/blender_world_steps/steps/002_images.py`
**Lines:** 480
**Adds:** 25 image datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

The whole script is one `run()` function with 25 nearly-identical 18-line blocks, one per image. Each block:

1. Checks `'<name>' not in bpy.data.images` — idempotency guard so re-running doesn't dup.
2. Hardcodes an absolute path under `/Users/mahajankaran/Documents/Projects/folio-2025/resources/...` (or `/static/terrain/...` for the terrain mask).
3. Tries `bpy.data.images.load(_path, check_existing=False)` and renames the datablock to the canonical name.
4. If the file is missing, falls back to `bpy.data.images.new(name, width=W, height=H)` at a documented size and points `img.filepath` at the missing path so the .blend records what was supposed to be there.
5. If load throws, falls back to a 1×1 placeholder.
6. Sets `img.source = 'FILE'`, then `img.colorspace_settings.name` to `'sRGB'` or `'Non-Color'`, then `img.alpha_mode = 'STRAIGHT'`. Each line wrapped in try/except.

The 25 images (canonical name, dimensions, colorspace, source path):

| # | Datablock name | Size | Colorspace | Source path |
|---:|---|---|---|---|
| 1 | `blackboardLabels.png` | 255×256 | sRGB | `resources/textures/blackboardLabels.png` |
| 2 | `bowlingLabelStrike.png` | 128×32 | Non-Color | `resources/textures/bowlingLabelStrike.png` |
| 3 | `careerFreelancer.png` | 240×60 | sRGB | `resources/textures/career/careerFreelancer.png` |
| 4 | `careerHetic.png` | 316×60 | sRGB | `resources/textures/career/careerHetic.png` |
| 5 | `careerImmersiveGarden.png` | 340×60 | **Non-Color** | `resources/textures/career/careerImmersiveGarden.png` |
| 6 | `careerIRLTeacher.png` | 268×92 | sRGB | `resources/textures/career/careerIRLTeacher.png` |
| 7 | `careerOnlineTeacher.png` | 332×92 | sRGB | `resources/textures/career/careerOnlineTeacher.png` |
| 8 | `careerUzik.png` | 168×60 | **Non-Color** | `resources/textures/career/careerUzik.png` |
| 9 | `circuitAirDancerFace.png` | 128×128 | sRGB | `resources/textures/circuitAirDancerFace.png` |
| 10 | `circuitBrand.png` | 512×128 | sRGB | `resources/textures/circuitBrand.png` |
| 11 | `circuitLogoThreejs.png` | 128×128 | sRGB | `resources/textures/circuitLogoThreejs.png` |
| 12 | `circuitLogoWebgl.png` | 256×128 | sRGB | `resources/textures/circuitLogoWebgl.png` |
| 13 | `circuitLogoWebgpu.png` | 128×128 | sRGB | `resources/textures/circuitLogoWebgpu.png` |
| 14 | `cookieBanner.png` | 314×500 | sRGB | `resources/textures/cookieBanner.png` |
| 15 | `labCarpet.png` | 314×451 | sRGB | `resources/textures/labCarpet.png` |
| 16 | `palette` (no extension!) | 128×4 | sRGB | `resources/palette.png` |
| 17 | `projectsCarpet.png` | 314×451 | sRGB | `resources/textures/projectsCarpet.png` |
| 18 | `projectsLabels.png` | 218×60 | **Non-Color** | `resources/textures/projectsLabels.png` |
| 19 | `slabs.png` | 256×256 | sRGB | `resources/textures/slabs.png` |
| 20 | `stylized-map.png` | 128×128 | sRGB | `resources/textures/stylized-map.png` |
| 21 | `terrain.png` | 512×512 | Non-Color | `static/terrain/terrain.png` |
| 22 | `terrainAlpha` | 1024×1024 | Non-Color | `static/terrain/terrain.png` (**same file as terrain.png**, loaded twice) |
| 23 | `terrainFurnitures` | 512×512 | Non-Color | `resources/textures/terrainFurniture.exr` (note singular "Furniture" in filename, plural "Furnitures" in datablock) |
| 24 | `terrainGrass` | 512×512 | Non-Color | `resources/textures/terrainGrass.exr` |
| 25 | `terrainWater` | 512×512 | Non-Color | `resources/textures/terrainWater.exr` |

## Key data

- **Datablocks referenced**: none — pure loads
- **Materials assigned**: n/a (materials in 004 reference these images by name)
- **Modifiers added**: n/a
- **Custom properties**: n/a
- **Object types breakdown**: 0
- **Parent collection**: n/a (image datablocks)

## Technique / recipe

The "hardcoded resource paths with graceful degradation" pattern:

- **Absolute paths to one developer's home directory** (`/Users/mahajankaran/...`). The scripts are not portable across machines without path rewriting. Bruno publishes them anyway because the .blend ships with the images already embedded — the scripts are documentation of how the .blend was originally built, not a portable installer.
- **Idempotency via `not in bpy.data.images`**: re-running the script after a partial build skips already-loaded images.
- **Three-tier fallback**: real file → blank image at documented size with filepath set → blank 1×1 image. The middle tier is critical: it means downstream shader graphs (in 004) can still bind to the texture node and not error out, even if the source PNG is missing.
- **Per-image colorspace tagging**: `sRGB` for visible color textures, `Non-Color` for masks/data textures (grass density, water depth, normal/AO/displacement, etc.). The PNGs that drive procedural systems (`terrain*`, `slabs`, several `*Label*` masks) are all Non-Color.
- **`alpha_mode = 'STRAIGHT'`** on every image — Bruno treats all textures as straight (premultiplied) alpha. This matches how Three.js textures default, so the Blender preview matches runtime.
- **The `palette` image is the visible-world color reference.** It's 128×4 (a tiny strip) and is sampled by the `palette` material's shader graph to produce the warm clay/olive tints used by ~80% of the meshes. Renaming the datablock to plain `palette` (no extension) is deliberate — the shader graph in 004 references `bpy.data.images['palette']`.

## Connections

- **Reads from**: filesystem only (`resources/textures/*`, `static/terrain/terrain.png`, `resources/textures/*.exr`)
- **Read by** (by datablock name):
  - `palette` → `004_materials.py` (the `palette` material samples it as the master color ramp)
  - `terrain.png` + `terrainAlpha` → `003_node_groups.py` (terrain Geometry Nodes group reads them for displacement + masking)
  - `terrainGrass.exr` → `003_node_groups.py` (grass scatter density)
  - `terrainWater.exr` → terrain shader / water shader
  - `terrainFurnitures.exr` → furniture placement mask (used by 055 furniture script's scatter)
  - `slabs.png` → slabs material (027)
  - `circuitBrand/Webgl/Webgpu/Threejs/AirDancerFace.png` → circuit-branded materials (075, race-track scripts)
  - `career*.png` → career-text materials (one per artifact in the career section)
  - `cookieBanner.png` / `labCarpet.png` / `projectsCarpet.png` / `projectsLabels.png` / `blackboardLabels.png` / `bowlingLabelStrike.png` → branded materials in respective sections
  - `stylized-map.png` → `stylizedMap` material (probably for the in-world parchment minimap prop)
- **Depends on**: 000_init wiping `bpy.data.images`
- **Depended on by**: 003 (node groups), 004 (materials)

## Notable code patterns

- **Same 18-line block repeated 25 times.** No helper function. Generated code, almost certainly machine-emitted from a manifest. Reading the file feels mechanical because it is — the structure is `if not in: try load else fallback; set source; set colorspace; set alpha_mode`, 25 times.
- **Twin-load trick for `terrain.png`**: the same PNG file is loaded into two different datablocks (`terrain.png` at 512×512 fallback, `terrainAlpha` at 1024×1024 fallback). The fallback sizes differ so the two datablocks have different "ghost" identities if the file is missing, but in normal operation they hold the same pixels. Why? Likely so a shader can sample the file twice with different settings (e.g., one read filtered, one read for alpha test) without sharing image-node state. Cross-check this when reading 003 / 004.
- **Inconsistent colorspaces on visually-similar textures**: `careerImmersiveGarden.png` is Non-Color while the other `career*` PNGs are sRGB. Suggests Immersive Garden's PNG is an alpha mask, not a label. Same story for `careerUzik.png` and `projectsLabels.png` / `bowlingLabelStrike.png`. The colorspace flag is the only hint at "this PNG holds data, not color."
- **EXR format for terrain data layers**: `terrainFurnitures`, `terrainGrass`, `terrainWater` are EXR (floating-point) — Bruno wanted >8-bit precision for masks driving scatter density and water depth, since 8-bit quantization would step the scatter visibly.
- **`check_existing=False`**: forces a fresh load even if Blender has the same path cached. Pairs with the `'name not in bpy.data.images'` outer guard to keep the script truly idempotent.

## Correction vs the stale group index

The group-level `01-foundation.md` mentions `terrainData` and `terrainGradient` images — those names **do not exist** in the actual script. The real terrain images are `terrain.png`, `terrainAlpha`, `terrainFurnitures`, `terrainGrass`, `terrainWater` (a 5-image set, the last three being EXRs). The "gradient" the group .md alludes to is actually the `palette` image (128×4 PNG), and the "data" PNG is `terrain.png` itself (with `terrainAlpha` loading the same file as a separate datablock).
