import * as THREE from 'three';

/**
 * A single roaming PointLight that illuminates the nearest interactive
 * object as the player approaches it. One light, not one-per-object —
 * 13+ stationary PointLights crushed FPS, and a single moving light
 * gives the same "look, this is readable" cue for a tiny fraction of
 * the GPU cost.
 *
 * Targets come from Signs (experience trail, skills board, contact,
 * welcome board) and Billboards (project screens). The light fades in
 * once the player is within ENGAGE_RANGE of any target and rides on top
 * of whichever is closest; it fades out when nothing is in range.
 *
 * Day mode runs the light dimly (just a subtle focus highlight); night
 * mode cranks it up so signage stays readable against the dark world.
 */
const ENGAGE_RANGE = 8;
const LIGHT_LERP = 0.12;
const INTENSITY_LERP = 0.12;

export class ProximityLight {
  constructor(scene) {
    this.scene = scene;
    this.light = new THREE.PointLight(0xffffff, 0, 10, 1.8);
    this.light.castShadow = false;
    this.light.position.set(0, 4, 0);
    scene.add(this.light);

    this.targets = [];
    this._tmpTarget = new THREE.Vector3();
    this._currentDayIntensity = 0.8;
    this._currentNightIntensity = 2.5;
    this._activeMode = 'day';
  }

  /** Populate the target list from the loaded world. Called once after
   *  Signs + Billboards finish loading. */
  collectTargets({ signs, billboards }) {
    this.targets.length = 0;
    if (signs) {
      for (const item of signs.experienceItems || []) {
        this.targets.push({ pos: item.position, yOffset: 2.0, zOffset: 0.4 });
      }
      if (signs.skillsPosition) {
        this.targets.push({ pos: signs.skillsPosition, yOffset: 3.0, zOffset: 1.2 });
      }
      if (signs.contactPosition) {
        this.targets.push({ pos: signs.contactPosition, yOffset: 2.6, zOffset: 1.0 });
      }
      if (signs.compassPosition) {
        this.targets.push({ pos: signs.compassPosition, yOffset: 2.6, zOffset: -0.8 });
      }
    }
    if (billboards) {
      for (const item of billboards.items) {
        this.targets.push({ pos: item.position, yOffset: 2.8, zOffset: 0.6 });
      }
    }
  }

  setMode(mode) {
    this._activeMode = mode;
  }

  tick(playerPos) {
    let closest = null;
    let bestSq = ENGAGE_RANGE * ENGAGE_RANGE;
    for (const t of this.targets) {
      const dx = t.pos.x - playerPos.x;
      const dz = t.pos.z - playerPos.z;
      const dsq = dx * dx + dz * dz;
      if (dsq < bestSq) { bestSq = dsq; closest = t; }
    }

    if (closest) {
      this._tmpTarget.set(
        closest.pos.x,
        closest.pos.y + closest.yOffset,
        closest.pos.z + closest.zOffset,
      );
      this.light.position.lerp(this._tmpTarget, LIGHT_LERP);
      const target = this._activeMode === 'night'
        ? this._currentNightIntensity
        : this._currentDayIntensity;
      this.light.intensity = THREE.MathUtils.lerp(this.light.intensity, target, INTENSITY_LERP);
    } else {
      this.light.intensity = THREE.MathUtils.lerp(this.light.intensity, 0, INTENSITY_LERP);
    }
  }
}
