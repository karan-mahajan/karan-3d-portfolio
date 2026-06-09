// src/UI/loadingMilestones.js
// Pure data + mapping for the loading screen. No DOM, no Three — node-testable.

/** The 4 user-facing milestones, in order. `key` matches a chip + marker set. */
export const MILESTONES = Object.freeze(['world', 'character', 'lighting', 'final']);

/** Human chip labels. */
export const MILESTONE_LABELS = Object.freeze({
  world: 'World',
  character: 'Character',
  lighting: 'Lighting',
  final: 'Final',
});

/** Bar floor (%) each milestone guarantees, so chips + bar never disagree. */
export const MILESTONE_FLOOR = Object.freeze({
  world: 25, character: 50, lighting: 78, final: 100,
});

/**
 * Map a raw boot `phase` label → milestone key (or null to ignore).
 * Labels come from App.boot()'s phase() calls; matched by substring so minor
 * wording changes don't silently break the mapping.
 */
export function phaseToMilestone(label) {
  if (typeof label !== 'string') return null;
  const l = label.toLowerCase();
  // 'planting' before 'world' — "Planting the world…" must map to character, not world
  if (l.includes('planting') || l.includes('character')) return 'character';
  if (l.includes('engine') || l.includes('world') || l.includes('island')
      || l.includes('optimizing graphics')) return 'world';
  if (l.includes('lights')) return 'lighting';
  if (l.includes('almost ready') || l.includes('preparing graphics')) return 'final';
  return null;
}

/**
 * Which markers ignite when a milestone is reached (cumulative).
 * left/top are % of the map image, captured 2026-06-09 from the RUNTIME-resolved
 * app.mapSections (the live hut / skill sphere / contact board / experience
 * positions) — NOT the WorldMap.SECTIONS fallbacks, whose Z signs are mirrored.
 * Same world→pixel transform the in-game map uses (coords.js worldToSvg over the
 * ±55 MapSnapshot bounds, +Z→top). Re-capture if the world layout changes.
 */
export const MARKERS = Object.freeze([
  { id: 'spawn',      label: '',          left: 50.0, top: 50.0, tint: '#ffe6c2', litAt: 'world' },
  { id: 'projects',   label: 'PROJECTS',  left: 79.9, top: 23.4, tint: '#e86f3a', litAt: 'character' },
  { id: 'skills',     label: 'SKILLS',    left: 19.0, top: 17.5, tint: '#6f9f36', litAt: 'lighting' },
  { id: 'contact',    label: 'CONTACT',   left: 37.8, top: 82.6, tint: '#bf7d2f', litAt: 'lighting' },
  { id: 'experience', label: 'EXPERIENCE', left: 86.5, top: 74.6, tint: '#a87fd6', litAt: 'final' }, // violet, lights last
]);

/** Trivia pool — cross-fades during load. */
export const TRIVIA = Object.freeze([
  'This whole place is one walkable island.',
  'Projects are hidden around the island.',
  'The résumé is a book you can flip through.',
  'Try jumping near the water.',
  'Press M for the map once you’re in.',
  'Built with Three.js + WebGPU.',
  'Day turns to night while you explore.',
  'Follow the paths — or wander off them.',
]);

/** Shown on the final state while the world reveals. */
export const FINAL_TRIVIA = 'Stepping into the world…';
