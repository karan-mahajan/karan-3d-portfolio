import * as THREE from 'three/webgpu';

/**
 * Phase F point-light rig. Places a warm PointLight at every lamp-post anchor
 * (`refPoleLight_*`, ×12) and bonfire anchor (`refBonfire_*`, ×4) baked into
 * references.glb. The extras carry no light params, so colours/intensities are
 * chosen here.
 *
 * Day/night is read straight off TimeOfDay's discrete mode (no TimeOfDay edit):
 * a 0→1 `dayNight` factor lerps each frame toward 1 at night / 0 by day, and
 * every light's live intensity = base × factor. Lamp posts go fully dark in the
 * day (matching the old StreetLights behaviour); bonfires keep a small daytime
 * floor so the fire still reads as lit, and both get a cheap multi-sine flicker.
 *
 * castShadow stays false on every light — only the sun casts shadows (perf).
 */

const LAMP_COLOR = '#ffd9a0';   // warm tungsten
const LAMP_INTENSITY = 9;       // physical PointLight, decays over ~14m
const LAMP_DISTANCE = 15;
const LAMP_DECAY = 1.6;

const FIRE_COLOR = '#ff7a2a';   // hot orange
const FIRE_INTENSITY = 7;
const FIRE_DISTANCE = 11;
const FIRE_DECAY = 1.7;
const FIRE_DAY_FLOOR = 0.22;    // bonfires never fully die in daylight

export class Lights {
  /**
   * @param {THREE.Scene} scene
   * @param {{ all: Array<{name:string, position?:THREE.Vector3, object3d?:THREE.Object3D, extras?:object}> }} refs
   */
  constructor(scene, refs) {
    this.scene = scene;
    this.lamps = [];
    this.fires = [];
    // 0 = day (lamps off), 1 = night (full). Snapped on the first update().
    this._factor = 0;
    this._snapped = false;

    const all = refs?.all ?? [];
    for (const entry of all) {
      const name = entry.name ?? '';
      if (name.startsWith('refPoleLight')) this.#addLamp(entry);
      else if (name.startsWith('refBonfire')) this.#addFire(entry);
    }
  }

  #pos(entry) {
    const p = entry.position ?? entry.object3d?.position ?? entry;
    return [p.x, p.y, p.z];
  }

  #addLamp(entry) {
    const [x, y, z] = this.#pos(entry);
    const light = new THREE.PointLight(LAMP_COLOR, 0, LAMP_DISTANCE, LAMP_DECAY);
    light.position.set(x, y, z);
    light.castShadow = false;
    light.name = `light:${entry.name}`;
    this.scene.add(light);
    // Phase offsets so the dozen lamps don't flicker in unison.
    this.lamps.push({ light, phase: x * 1.7 + z * 0.9 });
  }

  #addFire(entry) {
    const [x, y, z] = this.#pos(entry);
    const light = new THREE.PointLight(FIRE_COLOR, 0, FIRE_DISTANCE, FIRE_DECAY);
    light.position.set(x, y, z);
    light.castShadow = false;
    light.name = `light:${entry.name}`;
    this.scene.add(light);
    this.fires.push({ light, phase: x * 2.3 - z * 1.1 });
  }

  /** Cheap fire flicker — two desynced sines so it reads as a live flame. */
  #flicker(t, phase) {
    return 0.82
      + 0.12 * Math.sin(t * 11 + phase)
      + 0.06 * Math.sin(t * 23 + phase * 1.7);
  }

  /**
   * @param {number} delta - frame seconds
   * @param {'day'|'night'} mode
   * @param {number} elapsed - clock seconds (drives flicker)
   */
  update(delta, mode, elapsed = 0) {
    const target = mode === 'night' ? 1 : 0;
    if (!this._snapped) {
      this._factor = target;
      this._snapped = true;
    } else {
      // ~1s ramp, matching the TimeOfDay colour tween feel.
      this._factor += (target - this._factor) * Math.min(1, delta * 3);
    }

    const f = this._factor;
    for (const { light, phase } of this.lamps) {
      light.intensity = LAMP_INTENSITY * f * this.#flicker(elapsed, phase) * 1.02;
    }
    // Bonfires keep a daytime floor so the flame still glows in sunlight.
    const fireF = FIRE_DAY_FLOOR + (1 - FIRE_DAY_FLOOR) * f;
    for (const { light, phase } of this.fires) {
      light.intensity = FIRE_INTENSITY * fireF * this.#flicker(elapsed, phase);
    }
  }

  dispose() {
    for (const { light } of [...this.lamps, ...this.fires]) {
      this.scene.remove(light);
      light.dispose?.();
    }
    this.lamps = [];
    this.fires = [];
  }
}
