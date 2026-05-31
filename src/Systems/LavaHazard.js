import * as THREE from 'three/webgpu';

/**
 * Lava hazard. While the player stands in the molten pool for SINK_DELAY
 * seconds they start to sink; once fully submerged the GTA-style "WASTED" card
 * plays and the player respawns at base.
 *
 * The sink is procedural — the player is frozen (input ignored, normal motion
 * suspended) and the character group is lowered into the lava while its meshes
 * glow hot. No animation clip is required.
 *
 * Fed once per frame from the App tick AFTER `player.update`, so the manual
 * group-Y lowering during the sink isn't immediately overwritten by physics.
 */

const SINK_DELAY = 2.0;     // seconds in the lava before sinking begins
const SINK_TIME = 1.5;      // seconds to fully submerge
const SINK_DEPTH = 1.7;     // metres the character drops while sinking
const FORGIVE_RATE = 1.6;   // how fast the dwell timer bleeds off after stepping out

export class LavaHazard {
  /**
   * @param {{ player: import('../Player/Player.js').Player,
   *           lava: import('../World/Lava.js').Lava,
   *           wasted: import('../UI/Wasted.js').Wasted }} deps
   */
  constructor({ player, lava, wasted }) {
    this.player = player;
    this.lava = lava;
    this.wasted = wasted;

    this.state = 'idle';   // 'idle' | 'sinking' | 'dead'
    this.dwell = 0;        // seconds stood in the lava
    this.sinkT = 0;
    this.sinkStartY = 0;

    // Cache of character materials we tint, with their original emissive.
    this._tinted = null;
  }

  update(delta) {
    if (!this.lava?.center || !this.player) return;
    const pos = this.player.position;

    if (this.state === 'idle') {
      if (this.lava.containsPoint(pos.x, pos.z)) {
        this.dwell += delta;
        if (this.dwell >= SINK_DELAY) this.#beginSink();
      } else {
        this.dwell = Math.max(0, this.dwell - delta * FORGIVE_RATE);
      }
    } else if (this.state === 'sinking') {
      this.sinkT += delta;
      const k = Math.min(1, this.sinkT / SINK_TIME);
      const eased = k * k;                       // accelerate as they go under
      this.player.group.position.y = this.sinkStartY - eased * SINK_DEPTH;
      this.#tint(k);
      if (k >= 1) this.#wasted();
    }
  }

  #beginSink() {
    this.state = 'sinking';
    this.sinkT = 0;
    this.sinkStartY = this.player.group.position.y;
    this.player.freeze?.();
    this.player.character?.setLocomotion?.(false, false);
    this.#captureMaterials();
  }

  async #wasted() {
    if (this.state === 'dead') return;
    this.state = 'dead';
    await this.wasted.show();      // resolves while the screen is still dark
    this.#tint(0);
    this.player.respawn?.();
    this.player.unfreeze?.();
    this.dwell = 0;
    this.sinkT = 0;
    this.state = 'idle';
  }

  // ── Character "burning" tint ────────────────────────────────────────────────
  #captureMaterials() {
    if (this._tinted) return;
    const root = this.player.character?.root;
    if (!root) { this._tinted = []; return; }
    const list = [];
    root.traverse((o) => {
      const mat = o.isMesh && o.material;
      if (mat && 'emissive' in mat && mat.emissive?.isColor) {
        list.push({ mat, base: mat.emissive.clone() });
      }
    });
    this._tinted = list;
  }

  /** k: 0 = original, 1 = fully glowing hot. */
  #tint(k) {
    if (!this._tinted) return;
    const hot = new THREE.Color(1.0, 0.28, 0.04);
    for (const { mat, base } of this._tinted) {
      mat.emissive.copy(base).lerp(hot, k);
      if ('emissiveIntensity' in mat) mat.emissiveIntensity = 1 + k * 2.5;
      mat.needsUpdate = true;
    }
  }
}
