import gsap from 'gsap';
import { POIS, SECTIONS, WORLD_BOUNDS } from '../Portfolio/WorldMap.js';
import { svgToWorld, worldToSvg } from './coords.js';
import { renderIslandMap, svgEl } from './MapMarkers.js';

const SIZE = 800;
const SECTION_THUMBS = {
  projects: new URL('../../static/map-thumbs/projects.webp', import.meta.url).href,
  experience: new URL('../../static/map-thumbs/experience.webp', import.meta.url).href,
  skills: new URL('../../static/map-thumbs/skills.webp', import.meta.url).href,
  contact: new URL('../../static/map-thumbs/contact.webp', import.meta.url).href,
};
const DEFAULT_THUMB = SECTION_THUMBS.projects;

export class MapOverlay {
  constructor({
    root = document.getElementById('map-overlay-root'),
    player,
    controller,
    discovery,
    teleport,
    clickToMove,
    navmask,
    audio,
    miniMap,
  }) {
    this.root = root;
    this.player = player;
    this.controller = controller;
    this.discovery = discovery;
    this.teleport = teleport;
    this.clickToMove = clickToMove;
    this.navmask = navmask;
    this.audio = audio;
    this.miniMap = miniMap;
    this.isOpen = false;

    this.root.className = 'map-overlay-root hidden';
    this.root.innerHTML = `
      <div class="map-overlay-backdrop"></div>
      <div class="map-overlay-panel" role="dialog" aria-modal="true" aria-label="World map">
        <button class="map-close" type="button" aria-label="Close map">×</button>
        <svg class="map-overlay-svg"></svg>
        <aside class="map-preview">
          <div class="map-preview-eyebrow">Explorer map</div>
          <h2>Choose a destination</h2>
          <img alt="" src="${DEFAULT_THUMB}" />
          <p>Hover a marker for a section preview. Click open land to drop a flag and walk there.</p>
        </aside>
        <button class="map-reset" type="button">Reset Discovery</button>
      </div>
    `;
    this.panel = this.root.querySelector('.map-overlay-panel');
    this.svg = this.root.querySelector('.map-overlay-svg');
    this.preview = this.root.querySelector('.map-preview');
    this.#render();
    this.#wire();
    this.discovery?.onDiscover?.(() => this.#render());
  }

  open(fromRect = null) {
    if (this.isOpen || document.body.classList.contains('booting')) return;
    this.isOpen = true;
    this.audio?.playMapOpen?.();
    this.controller && (this.controller.paused = true);
    this.root.classList.remove('hidden');
    const target = this.panel.getBoundingClientRect();
    const from = fromRect ?? this.miniMap?.getRect?.() ?? target;
    gsap.fromTo(this.panel, {
      x: from.left + from.width / 2 - (target.left + target.width / 2),
      y: from.top + from.height / 2 - (target.top + target.height / 2),
      scaleX: from.width / target.width,
      scaleY: from.height / target.height,
      borderRadius: '999px',
      opacity: 0.35,
    }, {
      x: 0,
      y: 0,
      scaleX: 1,
      scaleY: 1,
      borderRadius: '18px',
      opacity: 1,
      duration: 0.38,
      ease: 'power2.out',
    });
  }

  close({ silent = false } = {}) {
    if (!this.isOpen && this.root.classList.contains('hidden')) return;
    this.isOpen = false;
    if (!silent) this.audio?.playMapClose?.();
    this.controller && (this.controller.paused = false);
    gsap.to(this.panel, {
      scale: 0.96,
      opacity: 0,
      duration: 0.2,
      ease: 'power2.in',
      onComplete: () => {
        this.root.classList.add('hidden');
        gsap.set(this.panel, { clearProps: 'all' });
      },
    });
  }

  toggle() {
    if (this.isOpen) this.close();
    else this.open(this.miniMap?.getRect?.());
  }

  #render() {
    renderIslandMap(this.svg, {
      width: SIZE,
      height: SIZE,
      bounds: WORLD_BOUNDS,
      showLabels: true,
      discovery: this.discovery,
    });
    this.playerDot = svgEl('g', { class: 'map-overlay-player' });
    this.playerDot.appendChild(svgEl('path', { d: 'M 0 -10 L 7 8 L 0 4 L -7 8 Z' }));
    this.svg.appendChild(this.playerDot);
    this.#wireMarkers();
  }

  update() {
    if (!this.isOpen || !this.playerDot || !this.player) return;
    const p = worldToSvg(this.player.position.x, this.player.position.z, SIZE, SIZE, WORLD_BOUNDS);
    const yaw = this.player.group.rotation.y * 180 / Math.PI;
    this.playerDot.setAttribute('transform', `translate(${p.x} ${p.y}) rotate(${yaw})`);
  }

  #wire() {
    this.root.querySelector('.map-close')?.addEventListener('click', () => this.close());
    this.root.querySelector('.map-overlay-backdrop')?.addEventListener('click', () => this.close());
    this.root.querySelector('.map-reset')?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.discovery?.reset?.();
      this.#render();
    });

    this.svg.addEventListener('click', (e) => {
      const { x, y } = this.#eventToSvg(e);
      const section = this.#sectionAt(x, y);
      if (section) {
        this.audio?.playMarkerClick?.();
        this.close({ silent: true });
        this.teleport?.toSection?.(section, { x: e.clientX, y: e.clientY });
        return;
      }
      const world = svgToWorld(x, y, SIZE, SIZE, WORLD_BOUNDS);
      if (this.navmask.isWalkable(world.x, world.z)) {
        if (this.clickToMove.requestMove(world.x, world.z)) {
          this.isOpen = true;
          this.close({ silent: true });
        } else {
          this.audio?.playNope?.();
          this.#showNope(x, y);
        }
      } else {
        this.audio?.playNope?.();
        this.#showNope(x, y);
      }
    });
    this.svg.addEventListener('mousemove', (e) => {
      const { x, y } = this.#eventToSvg(e);
      const section = this.#sectionAt(x, y);
      if (!section || section.id === this._hoverSectionId) return;
      this._hoverSectionId = section.id;
      this.audio?.playMarkerHover?.(section.id);
      this.#showPreview(section);
    });
  }

  #wireMarkers() {
    for (const marker of this.svg.querySelectorAll('.map-marker-section')) {
      const section = SECTIONS.find((s) => s.id === marker.dataset.markerId);
      if (!section) continue;
      marker.addEventListener('click', (e) => {
        e.stopPropagation();
        this.audio?.playMarkerClick?.();
        this.close({ silent: true });
        this.teleport?.toSection?.(section, { x: e.clientX, y: e.clientY });
      });
      marker.addEventListener('mouseenter', () => {
        this.audio?.playMarkerHover?.(section.id);
        this.#showPreview(section);
      });
      marker.addEventListener('focus', () => this.#showPreview(section));
    }
  }

  #showPreview(section) {
    const discovered = this.discovery?.isDiscovered?.(section.id);
    const img = SECTION_THUMBS[section.id] ?? DEFAULT_THUMB;
    this.preview.innerHTML = `
      <div class="map-preview-eyebrow">${discovered ? 'Discovered' : 'Marked route'}</div>
      <h2>${section.name}</h2>
      <img alt="" src="${img}" />
      <p>${discovered ? section.blurb : 'Visible from the start, but the color wakes up when you visit.'}</p>
    `;
  }

  #showNope(x, y) {
    const mark = svgEl('g', { class: 'map-nope', transform: `translate(${x} ${y})` });
    mark.appendChild(svgEl('line', { x1: -9, y1: -9, x2: 9, y2: 9 }));
    mark.appendChild(svgEl('line', { x1: 9, y1: -9, x2: -9, y2: 9 }));
    this.svg.appendChild(mark);
    gsap.to(mark, {
      opacity: 0,
      scale: 1.4,
      duration: 0.6,
      ease: 'power2.out',
      transformOrigin: 'center',
      onComplete: () => mark.remove(),
    });
  }

  #eventToSvg(e) {
    const rect = this.svg.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * SIZE,
      y: ((e.clientY - rect.top) / rect.height) * SIZE,
    };
  }

  #sectionAt(svgX, svgY) {
    for (const section of SECTIONS) {
      const [x, , z] = section.position;
      const p = worldToSvg(x, z, SIZE, SIZE, WORLD_BOUNDS);
      if (Math.hypot(svgX - p.x, svgY - p.y) <= 24) return section;
    }
    return null;
  }
}
