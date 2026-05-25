import { WORLD_BOUNDS } from '../Portfolio/WorldMap.js';

const DEFAULT_RESOLUTION = 128;

export class Navmask {
  constructor({
    bounds = WORLD_BOUNDS,
    blockers = [],
    resolution = DEFAULT_RESOLUTION,
  } = {}) {
    this.bounds = bounds;
    this.blockers = blockers;
    this.resolution = resolution;
    this.data = new Uint8Array(resolution * resolution);
    this.#bake();
  }

  isWalkable(worldX, worldZ) {
    const value = this.valueAt(worldX, worldZ);
    return value === 1 || value === 2;
  }

  hasClearance(worldX, worldZ, radius = 0.8) {
    if (!this.isWalkable(worldX, worldZ)) return false;
    const samples = Math.max(10, Math.ceil(radius * 12));
    for (let i = 0; i < samples; i++) {
      const a = (i / samples) * Math.PI * 2;
      if (!this.isWalkable(
        worldX + Math.cos(a) * radius,
        worldZ + Math.sin(a) * radius,
      )) return false;
    }
    return true;
  }

  segmentHasClearance(ax, az, bx, bz, radius = 0.5) {
    const dist = Math.hypot(bx - ax, bz - az);
    const steps = Math.max(2, Math.ceil(dist / 0.45));
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      if (!this.hasClearance(
        ax + (bx - ax) * t,
        az + (bz - az) * t,
        radius,
      )) return false;
    }
    return true;
  }

  valueAt(worldX, worldZ) {
    const { minX, maxX, minZ, maxZ } = this.bounds;
    if (worldX < minX || worldX > maxX || worldZ < minZ || worldZ > maxZ) return 0;
    const ix = Math.floor(((worldX - minX) / (maxX - minX)) * this.resolution);
    const iz = Math.floor(((maxZ - worldZ) / (maxZ - minZ)) * this.resolution);
    const x = Math.min(this.resolution - 1, Math.max(0, ix));
    const z = Math.min(this.resolution - 1, Math.max(0, iz));
    return this.data[z * this.resolution + x];
  }

  findPath(startX, startZ, endX, endZ) {
    let start = this.#worldToCell(startX, startZ);
    let end = this.#worldToCell(endX, endZ);
    if (!start || !end) return null;
    if (!this.#cellWalkable(start.x, start.z)) start = this.#nearestWalkableCell(start.x, start.z, 8);
    if (!this.#cellWalkable(end.x, end.z)) end = this.#nearestWalkableCell(end.x, end.z, 8);
    if (!start || !end) return null;

    const n = this.resolution;
    const startKey = start.z * n + start.x;
    const endKey = end.z * n + end.x;
    const open = [startKey];
    const openSet = new Set(open);
    const came = new Int32Array(n * n);
    came.fill(-1);
    const g = new Float32Array(n * n);
    g.fill(Infinity);
    const f = new Float32Array(n * n);
    f.fill(Infinity);
    g[startKey] = 0;
    f[startKey] = this.#heuristic(start.x, start.z, end.x, end.z);

    const dirs = [
      [1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1],
      [1, 1, Math.SQRT2], [1, -1, Math.SQRT2], [-1, 1, Math.SQRT2], [-1, -1, Math.SQRT2],
    ];

    while (open.length) {
      let bestIndex = 0;
      let bestKey = open[0];
      for (let i = 1; i < open.length; i++) {
        if (f[open[i]] < f[bestKey]) {
          bestKey = open[i];
          bestIndex = i;
        }
      }
      open.splice(bestIndex, 1);
      openSet.delete(bestKey);
      if (bestKey === endKey) return this.#simplifyPath(this.#reconstruct(came, bestKey));

      const cx = bestKey % n;
      const cz = Math.floor(bestKey / n);
      for (const [dx, dz, cost] of dirs) {
        const nx = cx + dx;
        const nz = cz + dz;
        if (!this.#cellWalkable(nx, nz)) continue;
        if (dx !== 0 && dz !== 0 && (!this.#cellWalkable(cx + dx, cz) || !this.#cellWalkable(cx, cz + dz))) {
          continue;
        }
        const nk = nz * n + nx;
        const tentative = g[bestKey] + cost;
        if (tentative >= g[nk]) continue;
        came[nk] = bestKey;
        g[nk] = tentative;
        f[nk] = tentative + this.#heuristic(nx, nz, end.x, end.z);
        if (!openSet.has(nk)) {
          openSet.add(nk);
          open.push(nk);
        }
      }
    }
    return null;
  }

  getDebugCanvas() {
    const canvas = document.createElement('canvas');
    canvas.width = this.resolution;
    canvas.height = this.resolution;
    canvas.className = 'map-debug-canvas';
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(this.resolution, this.resolution);
    for (let z = 0; z < this.resolution; z++) {
      for (let x = 0; x < this.resolution; x++) {
        const value = this.data[z * this.resolution + x];
        const i = (z * this.resolution + x) * 4;
        if (value === 0) {
          img.data[i + 0] = 180;
          img.data[i + 1] = 45;
          img.data[i + 2] = 35;
          img.data[i + 3] = 150;
        } else if (value === 2) {
          img.data[i + 0] = 214;
          img.data[i + 1] = 160;
          img.data[i + 2] = 23;
          img.data[i + 3] = 150;
        } else {
          img.data[i + 0] = 90;
          img.data[i + 1] = 145;
          img.data[i + 2] = 70;
          img.data[i + 3] = 135;
        }
      }
    }
    ctx.putImageData(img, 0, 0);
    return canvas;
  }

  #bake() {
    const { minX, maxX, minZ, maxZ, islandRadius = 45, shoreRadius = 33 } = this.bounds;
    for (let iz = 0; iz < this.resolution; iz++) {
      const z = maxZ - ((iz + 0.5) / this.resolution) * (maxZ - minZ);
      for (let ix = 0; ix < this.resolution; ix++) {
        const x = minX + ((ix + 0.5) / this.resolution) * (maxX - minX);
        const r = Math.hypot(x, z);
        let value = 0;
        if (r <= islandRadius) value = r >= shoreRadius ? 2 : 1;
        for (const blocker of this.blockers) {
          if (value === 0) break;
          if (blocker.type !== 'circle') continue;
          const [cx, cz] = blocker.center;
          if ((x - cx) * (x - cx) + (z - cz) * (z - cz) <= blocker.radius * blocker.radius) {
            value = 0;
            break;
          }
        }
        this.data[iz * this.resolution + ix] = value;
      }
    }
  }

  #worldToCell(worldX, worldZ) {
    const { minX, maxX, minZ, maxZ } = this.bounds;
    if (worldX < minX || worldX > maxX || worldZ < minZ || worldZ > maxZ) return null;
    return {
      x: Math.min(this.resolution - 1, Math.max(0, Math.floor(((worldX - minX) / (maxX - minX)) * this.resolution))),
      z: Math.min(this.resolution - 1, Math.max(0, Math.floor(((maxZ - worldZ) / (maxZ - minZ)) * this.resolution))),
    };
  }

  #cellToWorld(x, z) {
    const { minX, maxX, minZ, maxZ } = this.bounds;
    return {
      x: minX + ((x + 0.5) / this.resolution) * (maxX - minX),
      z: maxZ - ((z + 0.5) / this.resolution) * (maxZ - minZ),
    };
  }

  #cellWalkable(x, z) {
    if (x < 0 || x >= this.resolution || z < 0 || z >= this.resolution) return false;
    return this.data[z * this.resolution + x] > 0;
  }

  #nearestWalkableCell(cx, cz, maxRadius = 8) {
    for (let r = 1; r <= maxRadius; r++) {
      for (let dz = -r; dz <= r; dz++) {
        for (let dx = -r; dx <= r; dx++) {
          if (Math.abs(dx) !== r && Math.abs(dz) !== r) continue;
          const x = cx + dx;
          const z = cz + dz;
          if (this.#cellWalkable(x, z)) return { x, z };
        }
      }
    }
    return null;
  }

  #heuristic(ax, az, bx, bz) {
    return Math.hypot(ax - bx, az - bz);
  }

  #reconstruct(came, key) {
    const cells = [];
    let cur = key;
    while (cur !== -1) {
      cells.push(this.#cellToWorld(cur % this.resolution, Math.floor(cur / this.resolution)));
      cur = came[cur];
    }
    cells.reverse();
    return cells;
  }

  #simplifyPath(points) {
    if (points.length <= 2) return points;
    const simplified = [points[0]];
    let anchor = 0;
    while (anchor < points.length - 1) {
      let next = points.length - 1;
      for (; next > anchor + 1; next--) {
        if (this.#lineWalkable(points[anchor], points[next])) break;
      }
      simplified.push(points[next]);
      anchor = next;
    }
    return simplified;
  }

  #lineWalkable(a, b) {
    const dist = Math.hypot(b.x - a.x, b.z - a.z);
    const steps = Math.max(2, Math.ceil(dist / 0.5));
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      if (!this.isWalkable(
        a.x + (b.x - a.x) * t,
        a.z + (b.z - a.z) * t,
      )) return false;
    }
    return true;
  }
}
