/**
 * Single source of truth for SECTION_POSITIONS. Phase 1 wires this from
 * GlbWorld.refs.section. Downstream consumers (WorldMap, MiniMap, MapMarkers,
 * Discovery) import from here instead of Signs.js.
 *
 * Module is populated after GlbWorld.load() resolves; consumers that read it
 * before then see the spec-fallback (±70 cardinal), so they don't crash if
 * they construct before world load completes. World.loadAssets() calls
 * setSectionPositions(...) once GlbWorld is ready.
 */

const FALLBACK = {
  spawn:      { x: 0,   z: 0    },
  projects:   { x: 70,  z: 0    },
  experience: { x: 0,   z: 70   },
  skills:     { x: 0,   z: -70  },
  contact:    { x: -70, z: 0    },
};

let _positions = { ...FALLBACK };
let _experiencePath = [];

export function setSectionPositions(refs) {
  for (const key of Object.keys(FALLBACK)) {
    const ref = refs.section?.[key];
    if (ref) _positions[key] = { x: ref.x, z: ref.z };
  }
  // experiencePath = sorted cairn lantern positions (south→north).
  const cairns = (refs.lights?.cairnLantern ?? []).slice();
  cairns.sort((a, b) => a.position.z - b.position.z);
  _experiencePath = cairns.map((c) => ({ x: c.position.x, z: c.position.z }));
}

export const SECTION_POSITIONS = {
  get spawn()          { return _positions.spawn; },
  get projects()       { return _positions.projects; },
  get experience()     { return _positions.experience; },
  get skills()         { return _positions.skills; },
  get contact()        { return _positions.contact; },
  get experiencePath() { return _experiencePath; },
};
