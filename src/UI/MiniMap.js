import gsap from 'gsap';
import { POIS, SECTIONS, WORLD_BOUNDS } from '../Portfolio/WorldMap.js';
import { worldToSvg } from './coords.js';
import { renderIslandMap, svgEl } from './MapMarkers.js';

const SIZE = 220;

export class MiniMap {
  constructor({
    root = document.getElementById('minimap-root'),
    player,
    playerCamera,
    discovery,
    teleport,
    audio,
    onExpand,
  }) {
    this.root = root;
    this.player = player;
    this.playerCamera = playerCamera;
    this.discovery = discovery;
    this.teleport = teleport;
    this.audio = audio;
    this.onExpand = onExpand;
    this.trail = [];

    this.root.className = 'minimap-root';
    this.root.innerHTML = `
      <button class="minimap-shell" type="button" aria-label="Open map">
        <svg class="minimap-svg"></svg>
        <div class="map-tooltip hidden"></div>
      </button>
    `;
    this.shell = this.root.querySelector('.minimap-shell');
    this.svg = this.root.querySelector('.minimap-svg');
    this.tooltip = this.root.querySelector('.map-tooltip');

    this.#render();
    this.#wireBootFade();
    this.discovery?.onDiscover?.((id) => this.#handleDiscover(id));
    this.shell.addEventListener('click', (e) => {
      if (e.target.closest('.map-marker')) return;
      const section = this.#sectionAtEvent(e);
      if (section) {
        this.audio?.playMarkerClick?.();
        this.teleport?.toSection?.(section, { x: e.clientX, y: e.clientY });
        return;
      }
      if (document.body.classList.contains('booting')) return;
      this.onExpand?.(this.shell.getBoundingClientRect());
    });
    this.svg.addEventListener('mousemove', (e) => {
      const section = this.#sectionAtEvent(e);
      if (!section) {
        this.#hideTooltip();
        this._hoverSectionId = null;
        return;
      }
      if (section.id !== this._hoverSectionId) {
        this._hoverSectionId = section.id;
        this.audio?.playMarkerHover?.(section.id);
      }
      this.#showTooltip(section, e);
    });
    this.svg.addEventListener('mouseleave', () => this.#hideTooltip());
  }

  update() {
    if (!this.player) return;
    const p = this.player.position;
    const svgP = worldToSvg(p.x, p.z, SIZE, SIZE, WORLD_BOUNDS);
    this.arrow?.setAttribute(
      'transform',
      `translate(${svgP.x.toFixed(2)} ${svgP.y.toFixed(2)}) rotate(${this.#playerAngleDeg().toFixed(2)})`,
    );

    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(last.x - p.x, last.z - p.z) > 0.35) {
      this.trail.push({ x: p.x, z: p.z });
      if (this.trail.length > 30) this.trail.shift();
      this.#renderTrail();
    }
  }

  getRect() {
    return this.shell.getBoundingClientRect();
  }

  #render() {
    renderIslandMap(this.svg, {
      width: SIZE,
      height: SIZE,
      bounds: WORLD_BOUNDS,
      discovery: this.discovery,
    });

    this.trailGroup = svgEl('g', { class: 'map-breadcrumbs' });
    this.svg.appendChild(this.trailGroup);

    this.arrow = svgEl('g', { class: 'map-player-arrow' });
    this.arrow.appendChild(svgEl('path', { d: 'M 0 -9 L 6 7 L 0 4 L -6 7 Z' }));
    this.svg.appendChild(this.arrow);
    this.#wireMarkers();
  }

  #renderTrail() {
    if (!this.trailGroup) return;
    this.trailGroup.replaceChildren();
    this.trail.forEach((point, i) => {
      const p = worldToSvg(point.x, point.z, SIZE, SIZE, WORLD_BOUNDS);
      const age = i / Math.max(1, this.trail.length - 1);
      this.trailGroup.appendChild(svgEl('circle', {
        cx: p.x,
        cy: p.y,
        r: 1.2 + age * 0.7,
        opacity: 0.08 + age * 0.36,
      }));
    });
  }

  #wireMarkers() {
    for (const marker of this.svg.querySelectorAll('.map-marker-section')) {
      const section = SECTIONS.find((s) => s.id === marker.dataset.markerId);
      if (!section) continue;
      marker.addEventListener('click', (e) => {
        e.stopPropagation();
        this.audio?.playMarkerClick?.();
        this.teleport?.toSection?.(section, { x: e.clientX, y: e.clientY });
      });
      marker.addEventListener('mouseenter', (e) => {
        this.audio?.playMarkerHover?.(section.id);
        this.#showTooltip(section, e);
      });
      marker.addEventListener('mousemove', (e) => this.#positionTooltip(e));
      marker.addEventListener('mouseleave', () => this.#hideTooltip());
      marker.addEventListener('keydown', (e) => {
        if (e.code !== 'Enter' && e.code !== 'Space') return;
        e.preventDefault();
        this.teleport?.toSection?.(section, this.#markerScreenCenter(marker));
      });
    }
  }

  #showTooltip(target, e) {
    const discovered = this.discovery?.isDiscovered?.(target.id);
    this.tooltip.innerHTML = `
      <strong>${target.name}</strong>
      ${discovered ? `<span>${target.blurb}</span>` : '<span>Undiscovered</span>'}
    `;
    this.tooltip.classList.remove('hidden');
    this.#positionTooltip(e);
  }

  #positionTooltip(e) {
    const rect = this.root.getBoundingClientRect();
    this.tooltip.style.left = `${e.clientX - rect.left - 8}px`;
    this.tooltip.style.top = `${e.clientY - rect.top - 36}px`;
  }

  #hideTooltip() {
    this.tooltip.classList.add('hidden');
  }

  #handleDiscover(id) {
    if (id === null || SECTIONS.some((s) => s.id === id) || POIS.some((p) => p.id === id)) {
      this.#render();
      const marker = this.svg.querySelector(`[data-marker-id="${id}"]`);
      const star = marker?.querySelector('.map-star');
      if (star) {
        gsap.fromTo(star, { scale: 0.4, opacity: 0, rotation: -25 }, {
          scale: 1,
          opacity: 1,
          rotation: 0,
          duration: 0.45,
          ease: 'back.out(2)',
          transformOrigin: 'center',
        });
      }
    }
  }

  #wireBootFade() {
    gsap.set(this.root, { autoAlpha: 0, y: -8 });
    const check = () => {
      if (!document.body.classList.contains('booting')) {
        gsap.to(this.root, { autoAlpha: 1, y: 0, duration: 0.45, ease: 'power2.out' });
        return;
      }
      requestAnimationFrame(check);
    };
    check();
  }

  #playerAngleDeg() {
    const yaw = this.player?.group?.rotation?.y ?? 0;
    return (yaw * 180) / Math.PI;
  }

  #markerScreenCenter(marker) {
    const rect = marker.getBoundingClientRect();
    return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
  }

  #sectionAtEvent(e) {
    const rect = this.svg.getBoundingClientRect();
    const sx = ((e.clientX - rect.left) / rect.width) * SIZE;
    const sy = ((e.clientY - rect.top) / rect.height) * SIZE;
    for (const section of SECTIONS) {
      const [x, , z] = section.position;
      const p = worldToSvg(x, z, SIZE, SIZE, WORLD_BOUNDS);
      if (Math.hypot(sx - p.x, sy - p.y) <= 15) return section;
    }
    return null;
  }
}
