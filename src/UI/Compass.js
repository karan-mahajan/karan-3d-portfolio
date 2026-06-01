import * as THREE from 'three/webgpu';

/**
 * Camera-linked compass HUD (top-right, desktop only).
 *
 * Each frame we read the camera's ground-plane forward vector, compute the
 * heading (0 = north / +Z, clockwise positive), and rotate the compass ring
 * so the cardinal facing the camera sits under the fixed pointer at the top.
 *
 * Why getGroundForward() instead of `controls.azimuthAngle`: camera-controls'
 * internal azimuth has a sign + offset convention that's coupled to its
 * own spherical math. Reading the rendered camera direction is the
 * source-of-truth, matches what the player sees, and survives any future
 * change to how we drive the spherical coordinates.
 *
 * Counter-rotation: the cardinal labels are children of the rotating ring,
 * so they'd flip upside-down. Instead of writing 4 inline `transform`s per
 * frame, we set one CSS custom property (`--counter-rotate`) on the ring
 * and each label's own `transform: …rotate(var(--counter-rotate))` keeps
 * the text upright. One style write per frame for rotation + one for
 * counter-rotation — cheap.
 *
 * Hidden via CSS on mobile (`.is-mobile .compass { display: none }`); the
 * update is still issued but is a no-op cost (one DOM lookup once on
 * construction + a tiny vector math + style write).
 */
export class Compass {
  constructor({ playerCamera }) {
    this.playerCamera = playerCamera;
    this.ring = document.getElementById('compass-ring');
    this._fwd = new THREE.Vector3();
    this._cardinalsEl = null;
    this._cardinalsTimer = null;
  }

  /**
   * Flash the four cardinal section names for a few seconds — fired once when
   * the intro cinematic lands, to orient newcomers in-world (replaces the old
   * static welcome-screen compass card). Built lazily on first call.
   */
  revealCardinals(holdMs = 2800) {
    if (!this._cardinalsEl) {
      const el = document.createElement('div');
      el.className = 'compass-cardinals';
      el.setAttribute('aria-hidden', 'true');
      el.innerHTML = `
        <div class="cc-row"><span class="cc-dir">N</span><span class="cc-name">Experience</span></div>
        <div class="cc-row"><span class="cc-dir">E</span><span class="cc-name">Projects</span></div>
        <div class="cc-row"><span class="cc-dir">S</span><span class="cc-name">Skills</span></div>
        <div class="cc-row"><span class="cc-dir">W</span><span class="cc-name">Contact</span></div>`;
      document.body.appendChild(el);
      this._cardinalsEl = el;
    }
    const el = this._cardinalsEl;
    clearTimeout(this._cardinalsTimer);
    // Force reflow so re-triggering restarts the fade transition cleanly.
    el.classList.remove('is-shown');
    void el.offsetWidth;
    el.classList.add('is-shown');
    this._cardinalsTimer = setTimeout(() => el.classList.remove('is-shown'), holdMs);
  }

  update() {
    if (!this.ring || !this.playerCamera) return;
    const fwd = this.playerCamera.getGroundForward(this._fwd);
    // Heading: 0 = looking +Z (north), +π/2 = +X (east), ±π = -Z (south),
    // -π/2 = -X (west). atan2(x, z) matches the compass convention
    // (clockwise from north).
    const heading = Math.atan2(fwd.x, fwd.z);
    // CSS rotate is positive=clockwise. We want the cardinal the camera is
    // looking at to swing to the top, which is the opposite direction.
    const deg = -heading * 180 / Math.PI;
    this.ring.style.transform = `rotate(${deg}deg)`;
    this.ring.style.setProperty('--counter-rotate', `${-deg}deg`);
  }
}
