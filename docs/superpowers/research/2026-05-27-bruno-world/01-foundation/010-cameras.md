# 010_cameras.py — 2 orthographic cameras (world-wide minimap + close-up scope)

**Path:** `folio-2025/scripts/blender_world_steps/steps/010_cameras.py`
**Lines:** 55
**Adds:** 2 camera datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Creates two camera datablocks via `bpy.data.cameras.new(name)`. Each block sets:

```python
C = bpy.data.cameras.new('<name>')
C.type = 'ORTHO'
C.lens = 50.0
C.lens_unit = 'MILLIMETERS'
C.clip_start = 0.1
C.clip_end = 1000.0
C.sensor_width = 36.0
C.sensor_height = 24.0
C.sensor_fit = 'AUTO'
C.shift_x = 0.0
C.shift_y = 0.0
C.ortho_scale = <varies>
C.name = '<name>'
```

The two cameras only differ in `ortho_scale`:

| Camera | `ortho_scale` (m) | Frame width covered | Use |
|---|---:|---|---|
| `Camera` | **192.0** | 192 m | Top-down render of the whole world for the **stylized minimap PNG** baking. Aligns with `Geometry Nodes.001`'s `Grid` of 192×192 m → same coordinate frame |
| `Camera.001` | **3.8** | 3.8 m | Close-up render — likely a vehicle / first-person scope, or an interaction-detail camera |

## Key data

- **Datablocks referenced**: none.
- **Materials assigned**: n/a.
- **Modifiers added**: n/a.
- **Custom properties**: none on the camera datablock.
- **World positions of key anchors**: n/a — placement happens when an object holds the camera in 020+.
- **Object types breakdown**: 0.
- **Parent collection**: n/a.

## Technique / recipe

The "ortho-camera-for-minimap-baking + ortho-detail-camera" pattern:

- **`type = 'ORTHO'`** for both — perspective is unwanted for either use:
  - The minimap is a 2D parchment-style top-down render; orthographic gives clean top-down projection with no perspective distortion at the corners.
  - The detail/scope camera (`Camera.001`) at 3.8 m frame width might be a HUD scope or weapon/tool preview — ortho prevents lens-style distortion.
- **`ortho_scale = 192`** matches the grass-scatter grid in `Geometry Nodes.001` (192 m wide). That's no coincidence — both cover Bruno's full world bounds with the same coordinate frame.
- **`ortho_scale = 3.8` for the close-up** suggests an indoor or hand-held view; a single prop fits in ~3.8 m.
- **Lens / sensor settings are kept at defaults** (`50mm, 36×24 sensor`) — irrelevant for ORTHO render but Blender requires them set.
- **No focal effects** (no DOF, no aperture set): both cameras are pinhole-perfect orthos.

## Connections

- **Reads from**: nothing.
- **Read by**:
  - `Camera` → minimap rig object (probably named `cameraTerrain` per the group .md). Used by the runtime to render the stylized world map texture (the same texture referenced in `stylizedMap.png` / material `stylizedMap`).
  - `Camera.001` → secondary camera object (vehicle scope / detail / unused).
- **Depends on**: 000_init (wipe of `bpy.data.cameras`).
- **Depended on by**: minimap-rig script and vehicle / detail-camera scripts. The 999_finalize.py is what sets the **active camera** of the scene.

## Notable code patterns

- **Two cameras and only two** for a world of 1,507 objects: confirms that Bruno doesn't use Blender for in-game cameras — the runtime camera is a Three.js camera. These two are tooling cameras only (map baking + detail capture).
- **Try/except on every config write**: even on a 55-line file, the pattern is preserved. Defensive against Blender version drift in camera property defaults.
- **`sensor_fit = 'AUTO'`**: lets Blender pick sensor fit based on render aspect ratio.
- **`shift_x = shift_y = 0`**: no lens shift; the camera looks straight along its local -Z.
- **`clip_end = 1000`**: 1 km far plane — enough to render the entire 192 m world plus generous headroom.
- **Identical sensor + lens for both**: they only differ in `ortho_scale`. So they behave like "framed-area pickers" — the scale is the only meaningful parameter for ortho cameras.
