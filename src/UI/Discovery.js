import { POIS, SECTIONS } from '../Portfolio/WorldMap.js';

const STORAGE_KEY = 'karan-world-discovered-v1';
const DISCOVERY_RADIUS = 8;

export class Discovery {
  constructor({ sections = SECTIONS, pois = POIS } = {}) {
    this.sections = sections;
    this.pois = pois;
    this._callbacks = new Set();
    this._discovered = new Set();
    this.#load();
  }

  update(playerX, playerZ) {
    for (const target of [...this.sections, ...this.pois]) {
      const [x, , z] = target.position;
      if (Math.hypot(playerX - x, playerZ - z) <= DISCOVERY_RADIUS) {
        this.discover(target.id);
      }
    }
  }

  discover(id) {
    if (!id || this._discovered.has(id)) return false;
    this._discovered.add(id);
    this.#save();
    const target = this.#targetById(id);
    for (const cb of this._callbacks) cb(id, target);
    return true;
  }

  isDiscovered(id) {
    return this._discovered.has(id);
  }

  isVisible(target) {
    if (!target) return false;
    if (this.sections.some((s) => s.id === target.id)) return true;
    return this.isDiscovered(target.id);
  }

  onDiscover(callback) {
    this._callbacks.add(callback);
    return () => this._callbacks.delete(callback);
  }

  reset() {
    this._discovered.clear();
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch {}
    for (const cb of this._callbacks) cb(null, null);
  }

  #targetById(id) {
    return [...this.sections, ...this.pois].find((t) => t.id === id) ?? null;
  }

  #load() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      const values = raw ? JSON.parse(raw) : [];
      if (Array.isArray(values)) this._discovered = new Set(values);
    } catch {
      this._discovered = new Set();
    }
  }

  #save() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...this._discovered]));
    } catch {}
  }
}
