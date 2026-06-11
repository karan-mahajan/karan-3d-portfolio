import gsap from 'gsap';
import { SECTIONS, WORLD_BOUNDS } from '../Portfolio/WorldMap.js';
import { worldToSvg } from './coords.js';

// Canvas backing resolution (CSS-scaled down to the 140px shell). 256 keeps
// the rotated world crop crisp without a devicePixelRatio dance.
const SIZE = 256;
// Metres from the player to the rim of the circle. Sections farther than this
// pin to the rim as a direction arrow until you walk closer.
const VIEW_RADIUS_M = 40;
const OCEAN_FILL = '#7a99a3';

export class MiniMap {
  constructor({
    root = document.getElementById('minimap-root'),
    player,
    discovery,
    snapshot,
    sections = SECTIONS,
    audio,
    onExpand,
  }) {
    this.root = root;
    this.player = player;
    this.discovery = discovery;
    this.snapshot = snapshot;
    this.sections = sections;
    this.audio = audio;
    this.onExpand = onExpand;
    this.trail = [];
    this._reducedMotion = typeof matchMedia === 'function'
      && matchMedia('(prefers-reduced-motion: reduce)').matches;

    this.root.className = 'minimap-root';
    this.root.innerHTML = `
      <button class="minimap-shell" type="button" aria-label="Open map">
        <canvas class="minimap-canvas" width="${SIZE}" height="${SIZE}"></canvas>
        <div class="minimap-ring" aria-hidden="true"></div>
      </button>
    `;
    this.shell = this.root.querySelector('.minimap-shell');
    this.canvas = this.root.querySelector('.minimap-canvas');
    this.ctx = this.canvas.getContext('2d');

    this.#wireBootFade();
    this.shell.addEventListener('click', () => {
      if (document.body.classList.contains('booting')) return;
      this.audio?.playMapOpen?.();
      this.onExpand?.(this.shell.getBoundingClientRect());
    });
    this.snapshot?.onReady?.(() => this.#draw());
  }

  update() {
    if (!this.player) return;
    const p = this.player.position;
    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(last.x - p.x, last.z - p.z) > 0.6) {
      this.trail.push({ x: p.x, z: p.z });
      if (this.trail.length > 24) this.trail.shift();
    }
    this.#draw();
  }

  getRect() {
    return this.shell.getBoundingClientRect();
  }

  #draw() {
    const ctx = this.ctx;
    const c = SIZE / 2;
    const yaw = this.player?.group?.rotation?.y ?? 0;
    const px = this.player?.position?.x ?? 0;
    const pz = this.player?.position?.z ?? 0;
    const mppm = c / VIEW_RADIUS_M; // mini-map pixels per metre

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, SIZE, SIZE);
    ctx.fillStyle = OCEAN_FILL;
    ctx.fillRect(0, 0, SIZE, SIZE);

    // World crop: rotate the whole snapshot so the player's heading points up,
    // centred on the player. cos/sin built from yaw; the map spins opposite the
    // player so the fixed centre arrow always reads "forward".
    if (this.snapshot?.ready) {
      const snapSize = this.snapshot.size;
      const ppmSnap = snapSize / (WORLD_BOUNDS.maxX - WORLD_BOUNDS.minX);
      const drawScale = mppm / ppmSnap;
      const pSnap = worldToSvg(px, pz, snapSize, snapSize, WORLD_BOUNDS);
      ctx.save();
      ctx.translate(c, c);
      ctx.rotate(-yaw);
      ctx.scale(drawScale, drawScale);
      ctx.translate(-pSnap.x, -pSnap.y);
      ctx.drawImage(this.snapshot.canvas, 0, 0);
      ctx.restore();
    }

    this.#drawTrail(c, mppm, yaw, px, pz);
    this.#drawSections(c, mppm, yaw, px, pz);
    this.#drawPlayerMarker(c);
  }

  // Rotate a world delta (relative to the player) into mini-map screen space.
  // North-up screen offset is (dx, -dz); then rotate by -yaw to match the crop.
  #project(dx, dz, mppm, yaw) {
    const ux = dx * mppm;
    const uy = -dz * mppm;
    const cos = Math.cos(-yaw);
    const sin = Math.sin(-yaw);
    return { x: ux * cos - uy * sin, y: ux * sin + uy * cos };
  }

  #drawTrail(c, mppm, yaw, px, pz) {
    const ctx = this.ctx;
    const rim = c - 8;
    ctx.fillStyle = 'rgba(255, 107, 53, 0.5)';
    this.trail.forEach((pt, i) => {
      const o = this.#project(pt.x - px, pt.z - pz, mppm, yaw);
      if (Math.hypot(o.x, o.y) > rim) return;
      const age = i / Math.max(1, this.trail.length - 1);
      ctx.globalAlpha = 0.1 + age * 0.4;
      ctx.beginPath();
      ctx.arc(c + o.x, c + o.y, 1.4 + age * 1.1, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }

  #drawSections(c, mppm, yaw, px, pz) {
    const ctx = this.ctx;
    const rim = c - 12;
    for (const section of this.sections) {
      const discovered = this.discovery?.isDiscovered?.(section.id) ?? false;
      // Hidden entries (the museum door) stay off the map until discovered.
      if (section.hidden && !discovered) continue;
      const [sx, , sz] = section.position;
      let o = this.#project(sx - px, sz - pz, mppm, yaw);
      const dist = Math.hypot(o.x, o.y);
      const atRim = dist > rim;
      if (atRim && dist > 0) {
        o = { x: (o.x / dist) * rim, y: (o.y / dist) * rim };
      }
      ctx.beginPath();
      ctx.arc(c + o.x, c + o.y, atRim ? 3.4 : 5, 0, Math.PI * 2);
      ctx.fillStyle = discovered ? section.color : '#9a9082';
      ctx.fill();
      ctx.lineWidth = 1.4;
      ctx.strokeStyle = 'rgba(40, 30, 18, 0.85)';
      ctx.stroke();
    }
  }

  // Heading-up "you are here" beacon. A pulsing halo (motion-gated), a white
  // ring for contrast on both day and night crops, a coloured core, and a small
  // forward notch. The mini-map rotates under it, so "up" is always forward.
  #drawPlayerMarker(c) {
    const ctx = this.ctx;
    ctx.save();
    ctx.translate(c, c);

    if (!this._reducedMotion) {
      const t = (performance.now() % 1600) / 1600; // 0..1
      const pulseR = 9 + t * 12;
      ctx.beginPath();
      ctx.arc(0, 0, pulseR, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255, 107, 53, ${0.5 * (1 - t)})`;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Forward notch (points up = heading).
    ctx.beginPath();
    ctx.moveTo(0, -13);
    ctx.lineTo(5, -5);
    ctx.lineTo(-5, -5);
    ctx.closePath();
    ctx.fillStyle = '#ff6b35';
    ctx.fill();

    // Cored dot with a white halo ring.
    ctx.beginPath();
    ctx.arc(0, 0, 6.5, 0, Math.PI * 2);
    ctx.fillStyle = '#ff6b35';
    ctx.fill();
    ctx.lineWidth = 2.4;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, 2.4, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    ctx.restore();
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
}
