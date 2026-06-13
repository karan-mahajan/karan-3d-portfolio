import * as THREE from "three/webgpu";
import { float, texture as textureNode, vec2 } from "three/tsl";

/**
 * SnowTrail — a world-fixed "pressed snow" map. One R8 texture covers the
 * walkable island (±TRAIL_HALF m); the player stamps soft dents into it as
 * they move through settled snow, and a slow amortized sweep lets fresh
 * snowfall fill the dents back in.
 *
 * Why a CPU DataTexture and not an RT/compute pass: stamps are tiny, rare
 * (a few per second), and single-channel — a partial-row CPU sweep + one
 * texture upload is far cheaper than adding a render pass, and keeps the
 * whole system out of the frame graph on tiers that disable it.
 *
 * The terrain is the only consumer with vertex displacement (1.5 m vertex
 * pitch → the trail reads there as a broad swale); the sharp footprint-scale
 * read comes from FRAGMENT darkening in the terrain material plus the
 * existing footprint decals on top.
 *
 * Module-level singleton: initSnowTrail() is called from the App constructor
 * BEFORE the world loads, so GlbV3World's terrain material can bake the
 * sampler in via snowTrailNode() without holding an instance.
 */

export const TRAIL_HALF = 64; // m — world region covered: [-64, +64] on X/Z

let _tex = null;
let _data = null;
let _res = 0;

/** Create the trail texture (res 0 → system disabled; sampler returns 0). */
export function initSnowTrail(res) {
  _res = res | 0;
  if (_res <= 0) return;
  _data = new Uint8Array(_res * _res); // zero-filled: no dents
  _tex = new THREE.DataTexture(
    _data,
    _res,
    _res,
    THREE.RedFormat,
    THREE.UnsignedByteType,
  );
  _tex.minFilter = THREE.LinearFilter;
  _tex.magFilter = THREE.LinearFilter;
  _tex.wrapS = THREE.ClampToEdgeWrapping;
  _tex.wrapT = THREE.ClampToEdgeWrapping;
  _tex.needsUpdate = true;
}

/**
 * TSL: pressed-snow amount (0..1) at a world-XZ node. Safe to call before
 * init and on disabled tiers — returns a constant 0 node.
 */
export function snowTrailNode(xz) {
  if (!_tex) return float(0);
  const uv = xz.mul(1 / (TRAIL_HALF * 2)).add(0.5);
  return textureNode(_tex, vec2(uv.x, uv.y)).r;
}

/**
 * CPU: pressed-snow amount (0..1) at a world XZ — the same data the shader
 * samples, for gameplay-side reads (drift domes crushing under the player's
 * trail). 0 when the trail system is disabled.
 */
export function snowTrailValueAt(x, z) {
  if (!_data) return 0;
  const px = Math.round((x / (TRAIL_HALF * 2) + 0.5) * _res);
  const py = Math.round((z / (TRAIL_HALF * 2) + 0.5) * _res);
  if (px < 0 || py < 0 || px >= _res || py >= _res) return 0;
  return _data[py * _res + px] / 255;
}

const STAMP_RADIUS = 0.34; // m — soft dent per footstep
const DRAG_SPACING = 0.45; // m moved between continuous drag stamps
const REFILL_SECONDS = 75; // full dent → gone (while it keeps snowing)
const SWEEP_ROWS = 8; // rows decayed per update() call (amortized full sweep)

export class SnowTrail {
  constructor() {
    this._sweepRow = 0;
    this._sweepDirty = false;
    this._lastX = null;
    this._lastZ = null;
    // Per-sweep decrement: a full sweep visits every row each (res/SWEEP_ROWS)
    // frames; scale so a full-strength dent refills in REFILL_SECONDS @60fps.
    this._decay =
      _res > 0
        ? Math.max(1, Math.round(255 / ((REFILL_SECONDS * 60 * SWEEP_ROWS) / _res)))
        : 0;
  }

  get enabled() {
    return !!_tex;
  }

  /** Stamp one footstep dent (called from the audio-aligned step callback). */
  stampStep(x, z) {
    this.#stamp(x, z, STAMP_RADIUS, 235);
  }

  /**
   * Per-frame: continuous drag dent while the player moves through snow
   * (covers run strides between step stamps), plus the amortized refill sweep.
   */
  update(playerPos, moving, coverage) {
    if (!_tex) return;
    if (moving && coverage > 0.35 && playerPos) {
      if (this._lastX === null) {
        this._lastX = playerPos.x;
        this._lastZ = playerPos.z;
      }
      const dx = playerPos.x - this._lastX;
      const dz = playerPos.z - this._lastZ;
      if (dx * dx + dz * dz >= DRAG_SPACING * DRAG_SPACING) {
        this.#stamp(playerPos.x, playerPos.z, STAMP_RADIUS * 0.8, 200);
        this._lastX = playerPos.x;
        this._lastZ = playerPos.z;
      }
    } else {
      this._lastX = this._lastZ = null;
    }
    this.#sweep();
  }

  #stamp(x, z, radius, strength) {
    if (!_tex) return;
    const scale = _res / (TRAIL_HALF * 2);
    const cx = (x / (TRAIL_HALF * 2) + 0.5) * _res;
    const cy = (z / (TRAIL_HALF * 2) + 0.5) * _res;
    const rPx = Math.max(1, radius * scale);
    const x0 = Math.max(0, Math.floor(cx - rPx));
    const x1 = Math.min(_res - 1, Math.ceil(cx + rPx));
    const y0 = Math.max(0, Math.floor(cy - rPx));
    const y1 = Math.min(_res - 1, Math.ceil(cy + rPx));
    if (x1 < x0 || y1 < y0) return; // off the covered region
    for (let py = y0; py <= y1; py++) {
      for (let px = x0; px <= x1; px++) {
        const dx = (px + 0.5 - cx) / rPx;
        const dy = (py + 0.5 - cy) / rPx;
        const d2 = dx * dx + dy * dy;
        if (d2 >= 1) continue;
        const fall = 1 - d2; // soft quadratic falloff
        const i = py * _res + px;
        const v = strength * fall;
        if (v > _data[i]) _data[i] = v;
      }
    }
    _tex.needsUpdate = true;
  }

  #sweep() {
    if (!_tex || this._decay === 0) return;
    let changed = false;
    for (let n = 0; n < SWEEP_ROWS; n++) {
      const row = this._sweepRow;
      this._sweepRow = (this._sweepRow + 1) % _res;
      const base = row * _res;
      for (let px = 0; px < _res; px++) {
        const i = base + px;
        if (_data[i] === 0) continue;
        _data[i] = _data[i] > this._decay ? _data[i] - this._decay : 0;
        changed = true;
      }
    }
    if (changed) this._sweepDirty = true;
    // One upload per full sweep pass at most (needsUpdate is already set by
    // stamps; this catches pure-decay frames).
    if (this._sweepDirty && this._sweepRow === 0) {
      _tex.needsUpdate = true;
      this._sweepDirty = false;
    }
  }
}
