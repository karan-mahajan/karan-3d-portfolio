export const WORLD_BOUNDS = Object.freeze({
  minX: -55,
  maxX: 55,
  minZ: -55,
  maxZ: 55,
  islandRadius: 45,
  shoreRadius: 33,
});

export const SPAWN_POSITION = Object.freeze([0, 0, 0]);

export const SECTIONS = Object.freeze([
  {
    id: 'projects',
    name: 'Projects',
    blurb: 'A rotating showcase of selected web and product work.',
    position: [36, 0, 0],
    color: '#e86f3a',
    landingOffset: [-7, 0, -5],
    facing: Math.PI / 2,
  },
  {
    id: 'experience',
    name: 'Experience',
    blurb: 'A northbound trail through roles, teams, and shipped work.',
    position: [3, 0, 42],
    color: '#4b8fbd',
    landingOffset: [5, 0, -8],
    facing: 0,
  },
  {
    id: 'skills',
    name: 'Skills',
    blurb: 'The toolkit board: frontend, backend, CMS, and platform skills.',
    position: [0, 0, -32],
    color: '#6f9f36',
    landingOffset: [5, 0, 8],
    facing: Math.PI,
  },
  {
    id: 'contact',
    name: 'Contact',
    blurb: 'A west-side mailbox for links, socials, and direct contact.',
    position: [-28, 0, 0],
    color: '#bf7d2f',
    landingOffset: [8, 0, -5],
    facing: -Math.PI / 2,
  },
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
