import * as THREE from 'three/webgpu';

/**
 * IntroCinematic — the first-arrival sequence. The character drops ~30 m out
 * of the sky into the real world, lands in a superhero power-landing, and the
 * ground breaks (GroundBreak) with dust + cracks + screen shake. Camera does a
 * sweeping world-reveal that settles into the normal third-person resting view,
 * then control hands off to the player.
 *
 * It runs as a pre-gameplay layer that drives the existing rig without fighting
 * physics:
 *   - Player.freeze() suspends input + motion but keeps the character animation
 *     and camera-follow ticking, so we just drive group.position.y for the fall.
 *   - PlayerCamera.locked stops the orbit cam; we write camera.position/lookAt
 *     directly each frame, then re-seed the orbit spherical state on handoff so
 *     gameplay resumes with zero snap.
 *
 * update(delta) is called from App's tick while `active`. play() resolves its
 * promise (and fires onComplete) when control hands off; skip() short-circuits
 * to standing-at-spawn on any click/keypress.
 */

const FALL_HEIGHT = 30;     // metres above the landing point
const DESCENT_DUR = 2.6;    // seconds of falling
const SETTLE_DUR = 2.1;     // camera ease-to-rest; long enough for the ~2.0s
                            // landing clip to fully resolve before handoff
const HEAD = 1.2;           // matches PlayerCamera HEAD_HEIGHT (follow offset)
const REST_DIST = 4.2;      // resting orbit distance (≈ the ctor seed)
const REST_POLAR = Math.PI * 0.42;
// Camera azimuth at handoff. Math.PI = straight behind the player (looking
// north), but that frames the bridge post dead-centre on the spawn pad. Pull
// ~20% toward the player's right (smaller angle → camera swings east) so the
// post clears and the view opens toward the statue ahead. Flip to 1.2 to swing
// the other way; nudge the 0.8 to taste.
const REST_AZ = Math.PI * 0.8;

const easeInQuad = (t) => t * t;
const easeInOut = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);

export class IntroCinematic {
  /**
   * @param {object} deps
   * @param {import('../Player/Player.js').Player} deps.player
   * @param {import('../Player/PlayerCamera.js').PlayerCamera} deps.playerCamera
   * @param {import('../World/Terrain.js').Terrain} deps.terrain
   * @param {import('../Effects/GroundBreak.js').GroundBreak} deps.groundBreak
   * @param {object} [deps.audio]
   * @param {() => void} [deps.onLanded]  fired at impact (compass reveal, etc.)
   */
  constructor({ player, playerCamera, terrain, groundBreak, audio, onLanded }) {
    this.player = player;
    this.playerCamera = playerCamera;
    this.camera = playerCamera.camera;
    this.terrain = terrain;
    this.groundBreak = groundBreak;
    this.audio = audio;
    this.onLanded = onLanded;

    this.active = false;
    this._phase = 'idle'; // idle | descent | settle | done
    this._t = 0;
    this._impactDone = false;
    this._onComplete = null;

    this._startCamPos = new THREE.Vector3();
    this._endCamPos = new THREE.Vector3();
    this._lookAt = new THREE.Vector3();
    this._tmp = new THREE.Vector3();
  }

  /** @returns {boolean} whether the cinematic will actually animate (vs instant). */
  static prefersReducedMotion() {
    return typeof matchMedia === 'function'
      && matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * Start the sequence. Resolves (and calls onComplete) when control hands off.
   * Falls back to an instant stand-at-spawn when reduced-motion is requested or
   * the character mesh failed to load.
   * @param {{ onComplete?: () => void }} [opts]
   * @returns {Promise<void>}
   */
  play({ onComplete } = {}) {
    this._onComplete = onComplete ?? null;

    const groundY = this.terrain ? this.terrain.heightAt(0, 0) : 0;
    this._groundY = groundY;

    if (IntroCinematic.prefersReducedMotion() || !this.player.character) {
      this.#instantLand(groundY);
      this.#finish();
      return Promise.resolve();
    }

    // Freeze the player: input + motion off, animation + camera-follow stay on.
    this.player.freeze();
    this.playerCamera.locked = true;

    // Place the character high above spawn, facing north, falling.
    const g = this.player.group;
    g.position.set(0, groundY + FALL_HEIGHT, 0);
    g.rotation.set(0, 0, 0);
    this.player._currentYaw = 0;
    this.player._targetYaw = 0;
    this.player._tiltX = 0;
    this.player._tiltZ = 0;
    this.player.character.play('falling', { fade: 0.1 });

    // Camera keyframes. Start high and to the side (wide world-reveal); end at
    // the normal resting third-person offset behind the player.
    const mobileZoom = this.playerCamera._mobileZoom ?? 1;
    this._startCamPos.set(11, groundY + FALL_HEIGHT + 6, -19);
    this.#sphericalOffset(REST_DIST * mobileZoom, REST_AZ, REST_POLAR, this._tmp);
    this._endCamPos.set(0, groundY + HEAD, 0).add(this._tmp);

    this._t = 0;
    this._impactDone = false;
    this._phase = 'descent';
    this.active = true;

    return new Promise((resolve) => { this._resolve = resolve; });
  }

  /** Per-frame, called from App's tick while active. */
  update(delta) {
    if (!this.active) return;
    this._t += delta;
    const g = this.player.group;

    if (this._phase === 'descent') {
      const p = Math.min(1, this._t / DESCENT_DUR);
      g.position.y = (this._groundY + FALL_HEIGHT)
        + (-FALL_HEIGHT) * easeInQuad(p);
      if (p >= 1) this.#impact();
    } else if (this._phase === 'settle') {
      // Ground-clamp: lift the body so the lowest foot/hand bone of the landing
      // crouch never sinks below the surface. Damped so it eases as the pose
      // rises back to standing (lift → 0 → resting exactly at groundY).
      const localLow = this.player.character.lowestContactLocalY?.() ?? 0;
      const targetY = this._groundY + Math.max(0, -localLow);
      g.position.y += (targetY - g.position.y) * Math.min(1, delta * 18);
    }

    // Camera sweep spans the whole sequence (descent + settle).
    const total = DESCENT_DUR + SETTLE_DUR;
    const camP = easeInOut(Math.min(1, this._t / total));
    this.camera.position.lerpVectors(this._startCamPos, this._endCamPos, camP);
    this._lookAt.set(g.position.x, g.position.y + 1.3, g.position.z);
    this.camera.lookAt(this._lookAt);
    this.playerCamera.applyShake(delta);

    if (this._t >= total) this.#handoff();
  }

  #impact() {
    if (this._impactDone) return;
    this._impactDone = true;
    this._phase = 'settle';

    const g = this.player.group;
    g.position.y = this._groundY;

    // Superhero landing → recover to idle (Character chains the one-shot). A
    // slightly longer crossfade softens the falling→landing pose change. The
    // ground-clamp in update() keeps the crouch from sinking through the floor.
    this.player.character.play('hardLanding', { once: true, then: 'idle', fade: 0.16 });

    this.groundBreak?.burst(
      { x: 0, y: this._groundY, z: 0 },
      { radius: 3.0, debrisCount: 18 },
    );
    this.playerCamera.addImpulse(0.5);
    this.audio?.playLandingImpact?.();
    this.onLanded?.();
  }

  #handoff() {
    // Land exactly at spawn — clear any clamp lift / drift so the physics body
    // and the visual group agree and control resumes from dead-center.
    const g = this.player.group;
    g.position.set(0, this._groundY, 0);
    g.rotation.set(0, 0, 0);
    this.player._tiltX = 0;
    this.player._tiltZ = 0;
    this.player.body?.teleport?.(0, this._groundY, 0);

    // Re-seed the orbit spherical state to exactly where we left the camera so
    // the first unlocked frame places it at _endCamPos (no snap), then release.
    const c = this.playerCamera.controls;
    c.distance = REST_DIST;
    c.azimuthAngle = REST_AZ;
    c.polarAngle = REST_POLAR;
    this.playerCamera.locked = false;
    if (this.player.character) this.player.character._rootPin = 'full';
    this.player.unfreeze();
    this.#finish();
  }

  /** Skip to standing-at-spawn on user input. Idempotent. */
  skip() {
    if (!this.active) return; // never started or already handed off
    const groundY = this._groundY ?? (this.terrain ? this.terrain.heightAt(0, 0) : 0);
    this.#instantLand(groundY);
    // Reveal the orientation labels too (skippers are usually first-timers).
    if (!this._impactDone) this.onLanded?.();
    this.#finish();
  }

  #instantLand(groundY) {
    const g = this.player.group;
    g.position.set(0, groundY, 0);
    g.rotation.set(0, 0, 0);
    this.player._currentYaw = 0;
    this.player._targetYaw = 0;
    if (this.player.character) this.player.character._rootPin = 'full';
    this.player.character?.play?.('idle', { fade: 0.1 });

    const c = this.playerCamera.controls;
    c.distance = REST_DIST;
    c.azimuthAngle = REST_AZ;
    c.polarAngle = REST_POLAR;
    this.playerCamera.locked = false;
    if (this.player._frozen) this.player.unfreeze();
    // Reduced-motion path never froze, so the pause main.js set still stands —
    // clear it explicitly so the player can move.
    if (this.player.controller) this.player.controller.paused = false;
  }

  #finish() {
    if (this._phase === 'done') return;
    this._phase = 'done';
    this.active = false;
    this._onComplete?.();
    this._resolve?.();
    this._resolve = null;
  }

  #sphericalOffset(dist, az, polar, out) {
    const sp = Math.sin(polar);
    out.set(dist * sp * Math.sin(az), dist * Math.cos(polar), dist * sp * Math.cos(az));
    return out;
  }
}
