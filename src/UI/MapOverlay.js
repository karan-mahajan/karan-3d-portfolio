import gsap from 'gsap';
import { SECTIONS, WORLD_BOUNDS } from '../Portfolio/WorldMap.js';
import { svgToWorld, worldToSvg } from './coords.js';
import { renderIslandMap, svgEl } from './MapMarkers.js';

const SIZE = 800;

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
    snapshot,
    sections = SECTIONS,
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
    this.snapshot = snapshot;
    this.sections = sections;
    this.isOpen = false;

    this.root.className = 'map-overlay-root hidden';
    this.root.innerHTML = `
      <div class="map-overlay-backdrop"></div>
      <div class="map-overlay-panel map-overlay-panel--full" role="dialog" aria-modal="true" aria-label="World map">
        <button class="map-close" type="button" aria-label="Close map">×</button>
        <div class="map-overlay-stage">
          <canvas class="map-overlay-canvas"></canvas>
          <svg class="map-overlay-svg"></svg>
        </div>
        <button class="map-reset" type="button">Reset Discovery</button>
      </div>
    `;
    this.panel = this.root.querySelector('.map-overlay-panel');
    this.stage = this.root.querySelector('.map-overlay-stage');
    this.canvas = this.root.querySelector('.map-overlay-canvas');
    this.svg = this.root.querySelector('.map-overlay-svg');
    if (this.snapshot) {
      this.canvas.width = this.snapshot.size;
      this.canvas.height = this.snapshot.size;
    }
    this.#render();
    this.#wire();
    this.snapshot?.onReady?.(() => this.#paintWorld());
    this.discovery?.onDiscover?.(() => this.#render());
  }

  #paintWorld() {
    if (!this.snapshot?.ready || !this.canvas) return;
    const ctx = this.canvas.getContext('2d');
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.drawImage(this.snapshot.canvas, 0, 0);
  }

  open(fromRect = null) {
    if (this.isOpen || document.body.classList.contains('booting')) return;
    this.isOpen = true;
    this.audio?.playMapOpen?.();
    this.controller && (this.controller.paused = true);
    // Pure blit of the snapshot captured once at boot — opening never renders
    // or reads back the GPU, so it can't hitch.
    this.#paintWorld();
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
      worldImage: !!this.snapshot,
      sections: this.sections,
    });
    // "You are here" beacon — a pulsing halo + a high-contrast cored dot with a
    // heading wedge. The white ring keeps it legible on both the bright day and
    // dark night world renders. aria-hidden: the dialog already announces the map.
    this.playerDot = svgEl('g', { class: 'map-overlay-player', 'aria-hidden': 'true' });
    this.playerDot.appendChild(svgEl('circle', { r: 26, class: 'map-player-pulse' }));
    this.playerDot.appendChild(svgEl('path', { d: 'M 0 -26 L 9 -8 L -9 -8 Z', class: 'map-player-heading' }));
    this.playerDot.appendChild(svgEl('circle', { r: 9, class: 'map-player-core' }));
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
  }

  #wireMarkers() {
    for (const marker of this.svg.querySelectorAll('.map-marker-section')) {
      const section = this.sections.find((s) => s.id === marker.dataset.markerId);
      if (!section) continue;
      marker.addEventListener('click', (e) => {
        e.stopPropagation();
        this.audio?.playMarkerClick?.();
        this.close({ silent: true });
        this.teleport?.toSection?.(section, { x: e.clientX, y: e.clientY });
      });
      marker.addEventListener('mouseenter', () => this.audio?.playMarkerHover?.(section.id));
    }
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
    for (const section of this.sections) {
      // Hidden entries have no marker until discovered — no invisible hitbox.
      if (section.hidden && !this.discovery?.isDiscovered?.(section.id)) continue;
      const [x, , z] = section.position;
      const p = worldToSvg(x, z, SIZE, SIZE, WORLD_BOUNDS);
      if (Math.hypot(svgX - p.x, svgY - p.y) <= 24) return section;
    }
    return null;
  }
}
