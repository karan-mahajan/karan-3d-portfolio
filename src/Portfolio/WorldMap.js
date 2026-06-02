export const WORLD_BOUNDS = Object.freeze({
  minX: -55,
  maxX: 55,
  minZ: -55,
  maxZ: 55,
  islandRadius: 45,
  shoreRadius: 33,
});

export const SPAWN_POSITION = Object.freeze([0, 0, 0]);

// Metadata only (id / name / colour). The real world positions + landing spots
// are resolved at runtime from the live interaction features (the hut, the
// skill sphere, the contact board) in App.#buildMapSections — these `position`
// values are just a fallback if a feature fails to resolve. Experience is not
// part of the v3 world.
export const SECTIONS = Object.freeze([
  { id: 'projects', name: 'Projects', position: [33, 0, -32], color: '#e86f3a' },
  { id: 'skills', name: 'Skills', position: [-34, 0, -36], color: '#6f9f36' },
  { id: 'contact', name: 'Contact', position: [-13, 0, 36], color: '#bf7d2f' },
]);

export const POIS = Object.freeze([]);

export const BLOCKERS = Object.freeze([]);

export const WATER_FEATURES = Object.freeze([]);

export const TREE_CLUSTERS = Object.freeze([
  { center: [-28, 18], radius: 11, density: 0.8 },
  { center: [24, 20], radius: 10, density: 0.7 },
  { center: [-24, -20], radius: 9, density: 0.75 },
  { center: [22, -22], radius: 10, density: 0.7 },
  { center: [3, 34], radius: 8, density: 0.55 },
]);

export const LAMPS = Object.freeze([
  [8, 0],
  [-8, 0],
  [0, 8],
  [0, -8],
  [18, 0],
  [-18, 0],
  [0, 18],
  [0, -18],
  [12, 12],
  [-12, 12],
  [12, -12],
  [-12, -12],
  [25, 0],
  [-25, 0],
  [0, 25],
  [0, -25],
  [15, 8],
  [-10, -15],
]);
