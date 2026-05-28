# 004_materials.py — build the 35 materials that color the world

**Path:** `folio-2025/scripts/blender_world_steps/steps/004_materials.py`
**Lines:** 4297
**Adds:** 35 material datablocks (no scene objects)
**Group:** [01-foundation](../01-foundation.md)

## What it does (code-level)

Single `run()` function with 35 sections separated by `# --- <matname> ---` banners. Each section follows the same boilerplate:

```python
mat = bpy.data.materials.get('<name>') or bpy.data.materials.new('<name>')
mat.use_fake_user = True
mat.use_nodes = True
mat.diffuse_color = (0.8, 0.8, 0.8, 1.0)
mat.metallic = 0.0
mat.roughness = 0.4
try: mat.blend_method = 'HASHED'      # 'BLEND' for projectsLabels
try: mat.alpha_threshold = 0.5
try: mat.use_backface_culling = False
nt = mat.node_tree
nt.nodes.clear()
# 1+ `n = nt.nodes.new(...)` + per-input `.default_value` writes
# then nt.links.new(...) links
```

The materials, grouped by role:

### Universal palette (1)
- **`palette`** — single shared material used by ~80% of meshes. Single `ShaderNodeTexImage` reading `bpy.data.images.get('palette')` (the 128×4 PNG) with `interpolation='Closest'` and `extension='REPEAT'`. Color routed straight into Principled BSDF base color. **The whole world's warm clay/olive look is one tiny PNG sampled per-UV.**

### Solids (5)
- **`black`** — Principled BSDF with base color near 0
- **`darkGray`** — Principled BSDF dark gray base color
- **`gray`** — Principled BSDF mid-gray
- **`green`** — Principled BSDF green
- **`redGradient`** — Principled BSDF; minor color ramp (single solid color despite the "gradient" name)
- **`Dots Stroke`** — special: has a versioning `NodeFrame` labeled "Versioning: Use Nodes was removed", **two Material Outputs** (one targeting `EEVEE`, one `CYCLES`), separate Principled and Diffuse BSDFs. Sets custom prop `mat['yp'] = []`. Probably a freestyle / grease-pencil leftover; the name matches a Blender default linestyle.

### Emissive radial gradients (5)
Each is just `ShaderNodeEmission → Material Output` — no Principled BSDF, no texture:

| Material | Emission color | Strength |
|---|---|---:|
| `emissiveBlueRadialGradient` | (0.0, 0.092, 1.0) | 18.9 |
| `emissiveGreenRadialGradient` | (1.0, 0.194, 0.0) **— actually orange!** | 16.7 |
| `emissiveOrangeRadialGradient` | (1.0, 0.172, 0.0) | 16.7 |
| `emissivePurpleRadialGradient` | (0.476, 0.105, 1.0) | 12.0 |
| `emissiveWhiteRadialGradient` | (1.0, 1.0, 1.0) | 8.0 |

Note the "Green" emission is actually a near-identical orange. The name is misleading — Bruno may have re-purposed an old material slot. Each block also has a leftover `ShaderNodeRGB` node (unconnected purple/blue (0.50, 0.19, 1.0)) which is not wired into the output — debris.

### Branded labels (12)
One per artifact, structure ≈ `ShaderNodeTexImage(<branded.png>) → Principled BSDF.base → Material Output`:
- `blackboardLabels`, `bowlingLabelStrike`, `cookieBanner`, `labCarpet`, `projectsCarpet`, `projectsLabels` (alpha BLEND), `stylizedMap`
- 4 circuit logos: `circuitBrand`, `circuitThreejs`, `circuitWebgl`, `circuitWebgpu`
- 1 air-dancer face: `airDancer` (reads `circuitAirDancerFace.png`)

### Career text materials (6)
- `careerTextFreelancer`, `careerTextHetic`, `careerTextImmersive`, `careerTextIRLTeacher`, `careerTextOnlineTeacher`, `careerTextUzik`
Same template as branded labels, each binds the matching `career*.png` image.

### Vertex/UV-driven gradients (2)
- **`grass`** — `UV Map → Separate XYZ.y → Mix` with two RGB nodes:
  - input[6] = `(0.091, 0.165, 0.057)` — dark olive green (root)
  - input[7] = `(0.416, 0.402, 0.0095)` — yellow-olive (tip)
  The UV.y of the grass blade triangle drives the mix factor → blade base is dark, tip is yellow. This is Bruno's signature yellow-meadow tone.
- **`palette`** — covered above (image-based, but same role).

### Special procedural (2)
- **`mapAltar`** — UV-driven square-mask gradient:
  - `UV Map → Separate XYZ → (X-0.5) → ABS → ×2`, same for Y, then `MAXIMUM(X', Y')` → `Float Curve` → mix two colors.
  - Color: dark brown `(0.027, 0.008, 0)` → multiplied orange `(1.0, 0.054, 0.039) × 22` (giant emission via Vector Math MULTIPLY by 22)
  - Effect: square-edged glowing portal, orange-red border. The UV must run 0–1; the mask is `max(|x-0.5|*2, |y-0.5|*2)` (squared/Chebyshev distance).
- **`mapPortal`** — clone of `mapAltar` with different colors and gain:
  - Dark center `(0.0074, 0.0036, 0.022)`
  - Bright edge `(0.275, 0.643, 1.0) × 10` (blue/cyan glow)
  - Same UV-mask graph (square-edged Chebyshev, **NOT** radial despite the name).

### Animated water (1)
- **`waterfall`** — Principled BSDF only, base color `(0.096, 0.145, 0.508)` (dark blue), no texture. The "animation" comes from the runtime — at Blender level it's just a static blue material.

### Terrain master (1) — the most complex
- **`terrain`** — ~500 lines, used by the island plane (Plane.134, 020_terrain).
  - Reads 4 images: `terrain.png`, `terrainGrass`, `terrainFurnitures`, `terrainWater`. Each via a `ShaderNodeTexImage`.
  - 5 hardcoded RGB colors define the world's tonal palette:
    - `RGB`: `(0.342, 0.429, 0.033)` — olive yellow (grass field)
    - `RGB.001`: `(1.0, 0.397, 0.076)` — orange dirt
    - `RGB.002`: `(0.105, 0.539, 0.485)` — teal water shallow
    - `RGB.003`: `(0.0065, 0.038, 0.114)` — dark navy (deep water)
    - `RGB.004`: `(0.091, 0.165, 0.057)` — dark olive (path/under-grass)
  - Graph topology: 3 `Separate Color` nodes split each EXR into RGB. `Map Range`s (0.1→0.3 and 0.3→1.0 in, 0→1 out, with steepness=4) carve the `terrainWater.b` (deep) channel into shallow/deep regions. `Mix` nodes blend palette colors in sequence: base (`olive`) → blend with `dark olive` (path mask from `terrainGrass.g`) → blend with `teal water` (shallow) → blend with `navy` (deep) → blend with `slab brick` color.
  - Slab overlay: `Geometry → Vector Math (×0.2) → Image Texture(slabs.png)` is sampled via world position (not UV), then a final `Mix.005` between brown `(0.392, 0.184, 0.122)` and bright orange `(1.0, 0.624, 0.258)`. Selected by `Separate Color.003.r` from `terrainFurnitures` → adds painted brick pavement only where that EXR's R channel is high.
  - Principled BSDF receives the final blended color; output is `ALL` target.
  - **Effect:** the entire visible terrain color is sampled per-pixel from this graph reading 3 EXRs + 1 PNG. No vertex colors required.

## Key data

- **Datablocks referenced**:
  - Every image loaded in 002 is bound here as a `ShaderNodeTexImage.image` — `bpy.data.images.get('<name>')`.
  - `palette` (image) → `palette` (material)
  - 4 terrain images → `terrain` (material)
  - One image per branded/career material
- **Materials created**: 35 (list at top)
- **Modifiers**: n/a (materials, not modifiers)
- **Custom properties**: only `mat['yp'] = []` on `Dots Stroke`
- **Object types**: 0 (no scene objects)
- **Parent collection**: n/a

## Technique / recipe

The "thin shader graphs over data-driven textures" pattern:

- **One universal material (`palette`) for all hand-modeled geo**: rather than authoring 30+ tinted variants, every rock/tree/prop has UVs mapped to a 128×4 strip. The mesh's UV.x picks a color column; the mesh's mat slot is just `palette`. Vertex colors / per-vertex UV authoring are the variability.
- **One mega-material (`terrain`) for the ground**: blends 5 base palette colors based on 3 EXR mask channels read in world UV space. Adjustments to ground appearance happen by repainting the EXRs, not by editing the shader.
- **Emissive materials are flat color × strength**: no falloff, no texture. The "radial gradient" effect comes from the **mesh** geometry (gradient is baked into a thin disc that physically holds the gradient), not from the shader. Hence "RadialGradient" in the name + a flat emission shader.
- **Map-portal/altar shapes are math-driven masks**: `max(|u-0.5|*2, |v-0.5|*2)` produces a square-frame mask without any texture. Float Curve shapes the inner falloff.
- **Branded materials are 3-node**: image texture → BSDF base → output. The image carries all complexity.
- **Hardcoded SSS, IOR, sheen, coat defaults**: every Principled BSDF in the file sets all ~30 inputs to identical defaults (SSS color `(1.0, 0.20, 0.10)`, sheen weight 0, coat 0.03 etc.). Almost certainly emitted by a serializer that dumps every input regardless of relevance.

## Connections

- **Reads from**: 002_images (every material binds one or more images by datablock name).
- **Read by**: every per-section script from 020 onward. Assignments via `ob.data.materials.append(bpy.data.materials.get('<name>'))` (the pattern Bruno uses in 023+).
- **Depends on**: 002_images (images must exist), 000_init (materials wiped).
- **Depended on by**: every mesh script (020-139). Without 004, all meshes would render as the Blender default pink.

## Notable code patterns

- **Massive boilerplate from serialization**: 4297 lines for 35 materials means ~120 lines per material on average. Most of that is per-input `.default_value` writes on Principled BSDF (~30 inputs × 4 try/except wrapping lines each = ~120 lines just for one BSDF, dwarfing the actual logic). The script is unmistakably auto-generated from a graph snapshot.
- **Try/except every single line**: even simple assignments like `n.inputs[N].default_value = X` are wrapped. Defensive against Blender version drift (input indices can shift between Blender versions).
- **Hardcoded color values everywhere** (no shared constants): if the project's warm-clay palette needs to drift cooler, you change one value in `palette.png` for global props, but the **terrain** material's 5 RGBs are independent and would each need editing. Same for grass.
- **`Color.001 → Vector Math MULTIPLY (×22)` for emissive overdrive**: instead of cranking emission strength, mapAltar pumps a color through `Vector Math.multiply(22)`, producing values >>1. This trick is used so the color can be Mixed with a darker color via a `MIX` node before going to output (you can't mix-then-emit-with-strength easily).
- **The Map Range "steepness" parameter**: terrain uses `Map Range(0.1→0.3, 0→1, steepness=4)` twice. Steepness >1 sharpens the falloff; the value 4 gives a fairly hard edge between deep/shallow water. Same trick at (0.3→1.0).
- **`Float Curve` for ramp shaping**: mapAltar/mapPortal both pump the distance mask through a `Float Curve` so Bruno could shape the falloff visually in the .blend. The curve points themselves aren't set in the script — only `inputs[0].default_value = 1.0` (the strength multiplier). Curve shape persists across saves but isn't recorded in this script.
- **Misleading material name**: `emissiveGreenRadialGradient` is actually orange. Probably stale name from a refactor.
- **Two outputs for one shader (EEVEE + CYCLES)**: only `Dots Stroke` does this. Other materials target `ALL`. Suggests `Dots Stroke` predates the Bruno-folio-2025 build and was preserved as-is.
- **`mat['yp'] = []` custom prop on `Dots Stroke`**: a leftover from an addon (likely "Ucupaint" / yp). Not used anywhere else.
