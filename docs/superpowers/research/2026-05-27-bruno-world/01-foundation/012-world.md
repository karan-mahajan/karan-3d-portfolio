# 012_world.py — world (environment) shader: flat blue background

**Path:** `folio-2025/scripts/blender_world_steps/steps/012_world.py`
**Lines:** 33
**Adds:** 1 world datablock + assigns it to the scene
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

```python
w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()

# Build a 2-node graph:
# World Output @ (300, 300)
# Background  @ (10, 300)
#   inputs[0] = color (0.347, 0.257, 1.0, 1.0)  # vivid blue
#   inputs[1] = 0.0  # strength
#   inputs[2] = 0.0  # something else (alpha?)
# Background.outputs[0] -> World Output.inputs[0]

bpy.context.scene.world = w   # assign the world to the active scene
```

Two-node shader tree: `Background → World Output`. The background is set to a vivid blue `(0.347, 0.257, 1.0)` with strength `0.0`.

## Key data

- **Datablocks referenced**: none — pure creation.
- **Materials assigned**: n/a.
- **Modifiers added**: n/a.
- **Custom properties**: none.
- **World positions**: n/a.
- **Object types breakdown**: 0.
- **Parent collection**: n/a (worlds are scene-level).

## Technique / recipe

The "minimal world shader, almost off" pattern:

- **Strength = 0**: the background contributes **zero light** to the scene. The color value is set but multiplied by 0, so visually the world is black during render.
- **Why authored at all?** A Blender scene must have a `world` datablock attached (`bpy.context.scene.world = w`) for some baking and the compositor to work. Bruno provides the minimum — a named world with a known shader graph — so the scene is well-formed, but contributes no ambient light.
- **The blue color is a "developer-friendly default"**: if Bruno ever cranks strength up to 1, the world goes blue (looks like sky). With strength 0, it's a dormant fallback.
- **No HDRi environment, no sky texture, no procedural sky**: Bruno's runtime sky is **rendered in Three.js** (gradient / shader-based). Blender's world shader doesn't need to match — it's just a placeholder.

## Connections

- **Reads from**: nothing.
- **Read by**: the scene (via `scene.world` assignment). Compositor and any baking operations also read it.
- **Depends on**: 000_init (wipe of `bpy.data.worlds`).
- **Depended on by**: any baking script (e.g., the minimap render rig).

## Notable code patterns

- **`bpy.context.scene.world = w`** at the end — without this, the datablock is orphaned. Worlds are scene-attached, not just stored.
- **Idempotent `get() or new()`**: standard pattern.
- **2-node graph is the minimum** for a working world shader: Background + Output.
- **`strength = 0.0` is the meaningful setting**: it deactivates the world without removing it. The color is informational.
- **Inputs[2] of Background**: in Blender 4.x's Background node, input 2 is unused; Bruno sets it to 0.0 defensively (some versions add a "Weight" input that's not always present).
- **Same `try/except` defensiveness** as everywhere else, even for a 2-node graph.
