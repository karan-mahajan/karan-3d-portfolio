# 009_lights.py — 2 area lights (blue + warm, both for the minimap rig)

**Path:** `folio-2025/scripts/blender_world_steps/steps/009_lights.py`
**Lines:** 46
**Adds:** 2 light datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Creates two AREA lights via `bpy.data.lights.new(name, type='AREA')`. Each block sets identical core params:

```python
L = bpy.data.lights.new('<name>', type='AREA')
L.energy = 350000.0
L.color = (r, g, b)
L.shadow_soft_size = 0.0
L.use_shadow = True
L.use_custom_distance = False
L.cutoff_distance = 40.0
L.diffuse_factor = 1.0
L.specular_factor = 1.0
L.volume_factor = 1.0
L.size = 1.0; L.size_y = 1.0
L.shape = 'SQUARE'
L.name = '<name>'
```

The two lights only differ in color:

| Light | Color (R, G, B) | Interpretation |
|---|---|---|
| `Area` | `(0.103, 0.263, 1.0)` | Strong blue (cool moonlight / night palette) |
| `Area.001` | `(1.0, 0.911, 0.805)` | Warm white (sunlight / day palette) |

## Key data

- **Datablocks referenced**: none.
- **Materials assigned**: n/a.
- **Modifiers added**: n/a.
- **Custom properties**: none on the light datablock.
- **World positions of key anchors**: n/a — lights have no position until an object holds them in 020+.
- **Object types breakdown**: 0.
- **Parent collection**: n/a.

## Technique / recipe

The "extreme-energy area light for ortho minimap baking" pattern:

- **Energy = 350,000 W** is huge — far beyond any normal scene light. This is consistent with the **minimap baking rig** Bruno uses to render the stylized map texture: an orthographic top-down camera + a single bright area light gives crisp shadows for the parchment-style minimap.
- **SQUARE area, size 1×1 m**: a small square light, but the energy is so high it dominates the lit scene.
- **`cutoff_distance = 40.0` with `use_custom_distance = False`**: cutoff is set but not enabled — Bruno authored the number but kept it off.
- **`shadow_soft_size = 0.0`**: hard shadows, fitting for a stylized map look.
- **Two color variants — blue + warm**: one for the day-time minimap, one for the night-time minimap. The runtime probably has both maps pre-rendered and switches between them based on time-of-day.

## Connections

- **Reads from**: nothing.
- **Read by**: scripts that create the minimap-baking rig (look for an object of `type='LIGHT'` whose `data = bpy.data.lights.get('Area')` in the minimap setup, probably the same script that creates `Camera`/`Camera.001`). The lights live in an excluded collection at render time so they don't leak into the main world render.
- **Depends on**: 000_init (wipe of `bpy.data.lights`).
- **Depended on by**: minimap rig script (group .md placed cameras in `cameraTerrain`; the lights are likely in the same collection).

## Notable code patterns

- **All emissive in-world lighting is via materials, not lights**: Bruno's world has lanterns, lamps, glowing signs everywhere — but only 2 Blender lights total. Confirms the group .md claim that "in-world lighting is all emissive materials, not Blender lights."
- **Redundant terminal `L.name = '<name>'`**: same pattern as metaballs / materials — auto-export tool always writes the name at the end of a block.
- **No SUN, POINT, SPOT, or HEMI lights**: only AREA. Makes sense for the stylized look (no harsh point shadows from a sun, no realistic falloff cones).
- **Identical `energy = 350000.0` for both**: the only thing different between day and night is **color**. The intensity is the same — Bruno tunes the look via white-balance / color, not via brightness.
- **`size = 1.0; size_y = 1.0; shape = 'SQUARE'`**: a 1m² square. Tiny relative to the world (192 m ortho frame). The result is a near-point area light with a tiny soft falloff.
