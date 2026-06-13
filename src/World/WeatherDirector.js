import { snowCoverage, snowFall, snowWetness } from "./SnowState.js";
import { fogWhiten } from "./FogState.js";

/**
 * Drives the automatic snow cycle. The portfolio has no other weather
 * scheduler (rain is a manual toggle), so this is the sole writer of the shared
 * `snowCoverage` / `snowFall` uniforms.
 *
 * Cycle: clear → onset (snow builds) → storm (heavy, held) → melt → clear …
 * Time-of-day independent — snow can fall at noon or midnight.
 *
 * Fog: lerps a private winter tint over whatever colour TimeOfDay has settled
 * on. The base is re-snapshotted every frame while clear, so day/night changes
 * are picked up automatically and never fought over.
 */

// Default wait before the FIRST storm ≈ one full day→night→dawn revolution
// (TimeOfDay's cycle is ~121s + a ~12s initial settle), so the first flakes land
// as a cinematic beat AFTER the visitor has seen a whole day cycle — not 15s in.
// App.setFirstDelay() shortens this for a returning visitor who never caught snow.
const FIRST_DELAY = 130;
const CLEAR_HOLD = 30; // s of clear weather between storms
const ONSET = 30; // s for snow to creep in patch by patch
const STORM_HOLD = 45; // s of heavy snow
const MELT = 30; // s for snow to melt off

const approach = (a, b, rate, delta) =>
  a + (b - a) * Math.min(1, Math.max(0, rate * delta));

export class WeatherDirector {
  /** @param {{ fog?: object|null }} [o] fog kept for back-compat; unused now. */
  constructor({ fog = null } = {}) {
    this.fog = fog;
    this.enabled = true;
    this._phase = "clear";
    this._t = 0;
    this._wait = FIRST_DELAY;
    this._cov = 0;
    this._fall = 0;
    this._wet = 0;
    // Winter fog tint now lives in FogState (fogWinterColor); WeatherDirector
    // only drives the whiten amount (see #applyFog).
  }

  /** True once snow is visibly falling or laying — for achievements / HUD. */
  get isSnowing() {
    return this._fall > 0.15 || this._cov > 0.15;
  }

  /** True during onset/storm/melt — any non-clear phase. App suppresses rain
   *  (visuals + ambient + thunder) whenever this is true so snow and rain never
   *  share the sky. Wider than isSnowing so the suppression covers the very
   *  start of onset before flakes cross the visibility threshold. */
  get isActive() {
    return this._phase !== "clear";
  }

  /** Override the initial clear-weather wait before the first storm. App calls
   *  this once on boot — only effective while still in the opening clear phase. */
  setFirstDelay(seconds) {
    if (this._phase === "clear" && this._cov < 0.02) {
      this._wait = Math.max(0, seconds);
    }
  }

  /** Current accumulation 0..1 — App reads it to swap footsteps to snow. */
  get coverage() {
    return this._cov;
  }

  setEnabled(value) {
    this.enabled = value;
  }

  #go(phase) {
    this._phase = phase;
    this._t = 0;
  }

  update(delta) {
    if (!this.enabled) {
      this._fall = approach(this._fall, 0, 0.4, delta);
      this._cov = approach(this._cov, 0, 0.1, delta);
      this._wet = approach(this._wet, 0, 0.05, delta);
    } else {
      this._t += delta;
      switch (this._phase) {
        case "clear":
          this._fall = approach(this._fall, 0, 0.4, delta);
          this._cov = approach(this._cov, 0, 0.12, delta);
          this._wet = approach(this._wet, 0, 0.03, delta); // slow ~30s dry-out
          if (this._t >= this._wait) this.#go("onset");
          break;
        case "onset":
          this._fall = approach(this._fall, 1, 0.5, delta);
          this._cov = Math.min(1, this._cov + delta / ONSET);
          this._wet = approach(this._wet, 0, 0.3, delta);
          if (this._t >= ONSET) this.#go("storm");
          break;
        case "storm":
          this._fall = approach(this._fall, 1, 0.6, delta);
          this._cov = Math.min(1, this._cov + delta / ONSET);
          this._wet = approach(this._wet, 0, 0.3, delta);
          if (this._t >= STORM_HOLD) this.#go("melt");
          break;
        case "melt":
          this._fall = approach(this._fall, 0, 0.45, delta);
          this._cov = Math.max(0, this._cov - delta / MELT);
          this._wet = approach(this._wet, 1, 0.35, delta);
          if (this._t >= MELT) {
            this._wait = CLEAR_HOLD;
            this.#go("clear");
          }
          break;
      }
    }
    snowCoverage.value = this._cov;
    snowFall.value = this._fall;
    snowWetness.value = this._wet;
    this.#applyFog();
  }

  #applyFog() {
    // The scene fog is now a view-direction node ([FogState.js]) whose colour is
    // the live sky gradient; winter just lerps that toward the cold tint. One
    // uniform, no per-frame base-colour snapshotting (the gradient is already
    // live), so day/night changes are picked up for free and never fought over.
    fogWhiten.value = this._cov < 0.02 ? 0 : this._cov * 0.7;
  }
}
