import {
  LAMPS,
  SECTIONS,
  TREE_CLUSTERS,
  WORLD_BOUNDS,
} from '../Portfolio/WorldMap.js';
import { worldToSvg } from './coords.js';

export const SVG_NS = 'http://www.w3.org/2000/svg';

export function svgEl(name, attrs = {}) {
  const el = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== undefined && value !== null) el.setAttribute(key, String(value));
  }
  return el;
}

export function starPath(cx, cy, outer = 8, inner = 3.8, points = 5) {
  const parts = [];
  for (let i = 0; i < points * 2; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / points;
    const r = i % 2 === 0 ? outer : inner;
    const x = cx + Math.cos(a) * r;
    const y = cy + Math.sin(a) * r;
    parts.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return `${parts.join(' ')} Z`;
}

export function renderIslandMap(svg, {
  width,
  height,
  bounds = WORLD_BOUNDS,
  showLabels = false,
  discovery = null,
  worldImage = false,
  sections = SECTIONS,
} = {}) {
  svg.replaceChildren();
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('role', 'img');

  // When a real top-down render of the world sits behind the SVG, the
  // procedural parchment base (ocean/shore/land/grain/coastline + the faked
  // tree & lamp dots) is redundant — draw only the section markers on top.
  if (worldImage) {
    svg.appendChild(renderSections(width, height, bounds, { showLabels, discovery, sections }));
    return;
  }

  const defs = svgEl('defs');
  defs.appendChild(svgEl('filter', {
    id: 'map-paper-grain',
    x: '-10%',
    y: '-10%',
    width: '120%',
    height: '120%',
  }));
  const filter = defs.firstChild;
  filter.appendChild(svgEl('feTurbulence', {
    type: 'fractalNoise',
    baseFrequency: '0.9',
    numOctaves: '2',
    seed: '8',
    result: 'noise',
  }));
  filter.appendChild(svgEl('feColorMatrix', {
    in: 'noise',
    type: 'matrix',
    values: '0 0 0 0 0.36 0 0 0 0 0.29 0 0 0 0 0.20 0 0 0 0.16 0',
  }));
  svg.appendChild(defs);

  const center = worldToSvg(0, 0, width, height, bounds);
  const scale = width / (bounds.maxX - bounds.minX);
  const islandR = bounds.islandRadius * scale;
  const shoreR = bounds.shoreRadius * scale;

  const ocean = svgEl('circle', {
    cx: center.x,
    cy: center.y,
    r: Math.min(width, height) * 0.49,
    class: 'map-ocean',
  });
  svg.appendChild(ocean);

  const shore = svgEl('circle', {
    cx: center.x,
    cy: center.y,
    r: islandR,
    class: 'map-shore',
  });
  svg.appendChild(shore);

  const land = svgEl('circle', {
    cx: center.x,
    cy: center.y,
    r: shoreR,
    class: 'map-land',
  });
  svg.appendChild(land);

  const grain = svgEl('circle', {
    cx: center.x,
    cy: center.y,
    r: islandR,
    class: 'map-grain',
  });
  svg.appendChild(grain);

  const rings = svgEl('g', { class: 'map-ink-rings' });
  rings.appendChild(svgEl('circle', { cx: center.x, cy: center.y, r: islandR, class: 'map-coastline' }));
  rings.appendChild(svgEl('circle', { cx: center.x, cy: center.y, r: shoreR, class: 'map-shoreline' }));
  svg.appendChild(rings);

  svg.appendChild(renderTreeClusters(width, height, bounds));
  svg.appendChild(renderLamps(width, height, bounds));
  svg.appendChild(renderSections(width, height, bounds, { showLabels, discovery, sections }));
}

export function renderTreeClusters(width, height, bounds = WORLD_BOUNDS) {
  const group = svgEl('g', { class: 'map-trees' });
  for (const cluster of TREE_CLUSTERS) {
    const [cx, cz] = cluster.center;
    const count = Math.max(10, Math.round(cluster.radius * cluster.density * 4));
    for (let i = 0; i < count; i++) {
      const n = seeded(i + cx * 17 + cz * 31);
      const a = n() * Math.PI * 2;
      const r = Math.sqrt(n()) * cluster.radius;
      const p = worldToSvg(cx + Math.cos(a) * r, cz + Math.sin(a) * r, width, height, bounds);
      group.appendChild(svgEl('circle', {
        cx: p.x,
        cy: p.y,
        r: 1.2 + n() * 1.1,
      }));
    }
  }
  return group;
}

export function renderLamps(width, height, bounds = WORLD_BOUNDS) {
  const group = svgEl('g', { class: 'map-lamps' });
  for (const [x, z] of LAMPS) {
    const p = worldToSvg(x, z, width, height, bounds);
    group.appendChild(svgEl('circle', { cx: p.x, cy: p.y, r: 2.2 }));
  }
  return group;
}

export function renderSections(width, height, bounds = WORLD_BOUNDS, { showLabels = false, discovery = null, sections = SECTIONS } = {}) {
  const group = svgEl('g', { class: 'map-sections' });
  for (const section of sections) {
    const [x, , z] = section.position;
    const p = worldToSvg(x, z, width, height, bounds);
    const discovered = discovery?.isDiscovered(section.id) ?? false;
    const marker = svgEl('g', {
      class: `map-marker map-marker-section ${discovered ? 'is-discovered' : 'is-undiscovered'}`,
      'data-marker-id': section.id,
      'data-marker-kind': 'section',
      transform: `translate(${p.x} ${p.y})`,
      'pointer-events': 'all',
      tabindex: '0',
      role: 'button',
      'aria-label': section.name,
    });
    marker.style.setProperty('--marker-color', section.color);
    marker.appendChild(svgEl('path', {
      d: starPath(0, 0, 9, 4.2),
      class: 'map-star',
    }));
    marker.appendChild(svgEl('circle', {
      cx: 0,
      cy: 0,
      r: 13,
      fill: '#000000',
      opacity: '0.001',
      class: 'map-marker-hit',
    }));
    if (showLabels) {
      const label = svgEl('text', {
        x: 0,
        y: -16,
        class: 'map-section-label',
        'text-anchor': 'middle',
      });
      label.textContent = section.name;
      marker.appendChild(label);
    }
    group.appendChild(marker);
  }
  return group;
}

function seeded(seed) {
  let s = Math.floor(Math.abs(seed) * 1000) >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
