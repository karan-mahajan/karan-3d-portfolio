# 10 — Lighting

**Bruno category:** 💡 Lighting
**Scripts:** 4 (050, 089, 117, 118)
**Total objects:** 107 (12 generators + 5 bonfire + 51 lanterns + 39 pole-lights)
**Status:** VISIBLE

---

## Purpose

All the world's emissive lighting fixtures. **None of these are real Blender lights** (only 2 real lights exist, both for the minimap rig). Bruno's in-world lighting is **mesh-based emissive materials** — every lamp, lantern, fire, and glow is a small mesh with an emissive shader. This is a deliberate stylistic choice: real lights would shadow-cast and complicate the toon palette; emissive meshes give a flat, painterly glow that fits the art direction.

---

## Scripts

| # | File | Objs | Types | Materials | What it adds |
|---:|---|---:|---|---|---|
| 050 | `050_lightGenerators.py` | 12 | 8×EMPTY, 4×MESH | `emissiveOrangeRadialGradient`, `palette` | 4 emissive meshes + 8 anchor empties. 4 NODES modifiers. Custom prop `booleans`. Parented under `behindTheScene` (049). These are likely backstage/effect light emitters |
| 089 | `089_bonfire.py` | 5 | 4×MESH, 1×EMPTY | `emissiveOrangeRadialGradient`, `palette`, `redGradient` | The bonfire at the landing zone — 4 meshes (logs, flames, embers, smoke geometry?) + 1 anchor empty. 1 NODES modifier. The `redGradient` material is likely the ember glow |
| 117 | `117_lanterns.py` | 51 | 34×MESH, 17×EMPTY | `emissiveOrangeRadialGradient`, `palette` | The dominant world lighting — 34 visible lantern meshes + 17 placement empties. 5,780 verts — these are detailed, with the emissive panel + the metal cage + the post |
| 118 | `118_poleLights.py` | 39 | 26×MESH, 13×EMPTY | `emissiveOrangeRadialGradient`, `palette` | 26 pole-mounted lights + 13 anchor empties. 26 NODES modifiers (Smooth by Angle.003). Tall street-lamp style, used along paths |

---

## How Bruno's lighting works

- **Single emissive color across the world:** `emissiveOrangeRadialGradient` (warm amber, ~#ff8800 with falloff). Used by every light fixture. Result: the entire world has tonal consistency at night.
- **No actual light sources.** The mesh's emissive material is the entire effect — no shadows are cast, no surfaces actually brighten near a lantern. Bruno fakes "illumination" via baked vertex colors on nearby props.
- **51 lanterns is a LOT.** They're the dominant fixture type — placed along paths, near buildings, in clusters at gameplay zones. Density gives the night view its character.
- **39 pole-lights** are the secondary fixture — taller, fewer, used as path markers / wayfinding rather than ambient.
- **Bonfire (5 objects) is the singleton centerpiece.** Bigger, more complex (redGradient for embers). Sits at the landing zone — first thing players see.
- **lightGenerators (12) are backstage props** — only inside `behindTheScene`. Probably small studio lights or effect-emitters.

---

## Lighting placement strategy

- **Path lighting** (poleLights): 26 instances along the road/slabs network — wayfinding at night.
- **Ambient cluster lighting** (lanterns): 34 instances clustered around gameplay zones (bowling, race, lab, landing) — atmosphere and zone-anchoring.
- **Focal lighting** (bonfire): 1 centerpiece at landing — gathering point.
- **Effect lighting** (lightGenerators): backstage-only — supports the behindTheScene narrative.

---

## Why this design works for Bruno

- **Emissive-only = no perf cost from real lights.** Modern WebGL with 90+ point lights would tank — but 90+ emissive meshes are just rendering. This is THE technique for stylized real-time game lighting.
- **Single color (orange amber) gives global tonal cohesion.** Even with 90 fixtures, the world doesn't look like a Christmas tree — they all glow the same warm hue.
- **Lanterns are mesh-detailed** (34 meshes for 51 instances → some reuse, ~5,780 verts total) — each lantern has its own cage geometry. This is where Bruno spent geometry budget on lighting.
- **Bonfire uses `redGradient` for ember crackle** — the only non-orange emissive in lighting. Stands out as a focal point.
- **Lighting is NOT parented under specific zones for most fixtures.** Lanterns and poleLights are top-level world props that span the whole island. lightGenerators IS parented (under behindTheScene) because it's zone-specific effect.

---

## Real Blender lights (for reference)

The only 2 actual Blender lights (`Area`, `Area.001`, from script 009) are both used by the **minimap rig** (`131_map.py`). They're hidden in the world and only the minimap camera sees them. The in-world lighting is 100% emissive meshes.

---

## Cross-references

- **Bonfire's home zone (landing):** see [07-major-areas.md](07-major-areas.md), script 088
- **lightGenerators' home (behindTheScene):** see [06-buildings-structures.md](06-buildings-structures.md), script 049
- **Minimap rig (where real lights are used):** see [14-reference-hidden.md](14-reference-hidden.md), script 131

---

## Source pointers

- Step scripts: `folio-2025/scripts/blender_world_steps/steps/050_lightGenerators.py`, `089_bonfire.py`, `117_lanterns.py`, `118_poleLights.py`
- Materials: `emissiveOrangeRadialGradient`, `redGradient`, `palette`
- Real lights: `009_lights.py` (only `Area`, `Area.001` — for minimap)
- Bruno's runtime emissive shader: in `folio-2025/sources/Game/` likely under a `Lights/` or `Emissive/` module
