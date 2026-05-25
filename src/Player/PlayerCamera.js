import CameraControls from "camera-controls";
import * as THREE from "three";

// Tree-shake-safe subset for camera-controls.
const subsetOfTHREE = {
  Vector2: THREE.Vector2,
  Vector3: THREE.Vector3,
  Vector4: THREE.Vector4,
  Quaternion: THREE.Quaternion,
  Matrix4: THREE.Matrix4,
  Spherical: THREE.Spherical,
  Box3: THREE.Box3,
  Sphere: THREE.Sphere,
  Raycaster: THREE.Raycaster,
};
CameraControls.install({ THREE: subsetOfTHREE });

const HEAD_HEIGHT = 1.2;

// Wheel-input sensitivities for the custom trackpad/mouse handler.
// Tuned for a MacBook trackpad; mouse-wheel ticks come in ~100px deltas
// which produces ~0.5 dolly per click — comfortable single-step zoom.
const ROTATE_SENSITIVITY = 0.003;
const PINCH_SENSITIVITY = 0.02;
const WHEEL_SENSITIVITY = 0.005;

const HINT_DISMISS_KEY = 'camera-hint-dismissed-v1';
const HINT_AUTO_HIDE_MS = 6000;
// Idle trackpad contact emits stray wheel events with deltaY=1 — without
// a minimum show time, the hint disappears before the user can read it.
const HINT_MIN_SHOW_MS = 2500;

/**
 * Smooth third-person orbital camera.
 *
 * Camera-controls is great at handling input + smoothing, but its built-in
 * "follow" semantics don't work the way we want — `setTarget` keeps the
 * camera in place (just rotates), and `moveTo` accumulates a focal offset.
 * Both feel wrong for a third-person rig.
 *
 * Instead we let camera-controls handle ONLY input (drag → azimuth/polar,
 * scroll → distance, with its own damping) and read those smoothed values
 * each frame. We compute the camera position ourselves from the player's
 * head + spherical offset — guaranteed to translate with the player.
 */
export class PlayerCamera {
  constructor(camera, canvas) {
    this.camera = camera;
    this.canvas = canvas;
    this.controls = new CameraControls(camera, canvas);

    // We handle wheel events ourselves (trackpad two-finger drag vs pinch
    // vs mouse-wheel zoom needs custom dispatch). Disable the built-in
    // wheel-dolly so we don't double-apply.
    this.controls.mouseButtons.wheel = CameraControls.ACTION.NONE;
    canvas.addEventListener('wheel', this.#onWheel, { passive: false, capture: true });

    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 12;

    this.controls.azimuthRotateSpeed = 0.55;
    this.controls.polarRotateSpeed = 0.35;
    this.controls.minPolarAngle = Math.PI * 0.18;
    this.controls.maxPolarAngle = Math.PI * 0.48;

    this.controls.smoothTime = 0.16;
    this.controls.draggingSmoothTime = 0.1;

    this.controls.truckSpeed = 0;
    this.controls.dollyToCursor = false;

    // Seed initial state. Pinned to the minimum zoom distance and the most
    // horizontal polar angle — but azimuth=0 places the camera in FRONT of
    // the player so we see the character's face, with the welcome board
    // behind the camera (out of frame).
    // distance≈2.5, polar≈85° (nearly flat), azimuth=0 (in front).
    this.controls.setLookAt(0, 1.66, -3.94, 0, HEAD_HEIGHT, 0, false);

    this._target = new THREE.Vector3(0, HEAD_HEIGHT, 0);
    this._tmpOffset = new THREE.Vector3();
    this.locked = false; // when true, update() doesn't move the camera (used by zoom)

    // Dynamic movement-zoom multiplier — applied on top of the user's
    // own controls.distance (preserved). 1.0 = idle, 1.10 = walking,
    // 1.18 = running. THREE.MathUtils.damp gives a frame-rate-independent
    // exponential smoothing with a time-constant of `1/lambda` seconds.
    // Lambda = 3 → ~95% convergence in 1 second, which matches the
    // cinematic "weighted but not slow" feel.
    this._movementZoomFactor = 1.0;
    this._movementZoomTarget = 1.0;

    // Sprint polar tilt — adds a small extra pitch-down when running so
    // the character is framed slightly higher on screen during a sprint.
    // Same 1-second damping as the zoom.
    this._polarTilt = 0;
    this._polarTiltTarget = 0;

    // Mobile devices have a narrower FOV-to-screen ratio and the character
    // fills too much frame at the default distance. Pull the resting view
    // back 25% so the world reads at a glance. matchMedia is evaluated once
    // — orientation flips don't retro-apply, which matches our existing
    // is-mobile body-class lifecycle.
    const coarse = typeof matchMedia === 'function'
      && matchMedia('(pointer: coarse)').matches;
    this._mobileZoom = coarse ? 1.25 : 1.0;

    this.#initTrackpadHint();
  }

  // Wheel events come from three input classes across macOS / Windows / Linux:
  //   • Pinch (all platforms, Chrome / Edge / Safari):   ctrlKey === true
  //   • Two-finger drag on a trackpad:                    deltaMode=0 (pixel), small delta
  //   • Mouse wheel click:                                deltaMode!=0 OR large pixel delta
  //
  // Mouse-wheel detection details:
  //   • Chrome / Edge / Safari on macOS+Windows: mouse wheel emits deltaMode=0
  //     with |deltaY| ≈ 100 (or a multiple of 120 in wheelDeltaY).
  //   • Firefox on Windows: deltaMode=1 (line mode), |deltaY| = 3 per notch.
  //   • Firefox on macOS: deltaMode=0, |deltaY| ≈ 53 (a misclassification we
  //     accept — Firefox-on-Mac mouse-wheel users will get a small rotate
  //     instead of a zoom; rare enough to live with).
  //   • Windows Precision Touchpads emit pixel-mode deltas like macOS but
  //     can spike to ~60–80 during a fast swipe, so the magnitude threshold
  //     is set to 100 (mouse wheels never undershoot that in mainstream
  //     browsers).
  #onWheel = (event) => {
    if (event.ctrlKey) {
      const zoomDelta = -event.deltaY * PINCH_SENSITIVITY;
      this.controls.dolly(zoomDelta, false);
      this.#dismissHint();
      event.preventDefault();
      return;
    }

    const isMouseWheel =
      event.deltaMode !== 0
      || Math.abs(event.deltaY) >= 100
      || Math.abs(event.deltaX) >= 100;

    if (isMouseWheel) {
      // Normalise line/page modes to pixels so WHEEL_SENSITIVITY (tuned for
      // pixel-mode 100/click) gives a consistent dolly across browsers.
      // Line ≈ 33px, page ≈ viewport height (rare; treat as 400 as a cap).
      let pixelDelta = event.deltaY;
      if (event.deltaMode === 1) pixelDelta *= 33;
      else if (event.deltaMode === 2) pixelDelta *= 400;
      const wheelZoom = -pixelDelta * WHEEL_SENSITIVITY;
      this.controls.dolly(wheelZoom, false);
      event.preventDefault();
      return;
    }

    // Trackpad two-finger drag. Require some motion so idle-contact events
    // (deltaX=0, deltaY=0 — Chrome fires these on subtle rests) don't no-op
    // and prematurely dismiss the hint.
    if (event.deltaX !== 0 || event.deltaY !== 0) {
      this.controls.rotate(
        event.deltaX * ROTATE_SENSITIVITY,
        event.deltaY * ROTATE_SENSITIVITY,
        false,
      );
      this.#dismissHint();
    }
    event.preventDefault();
  };

  #initTrackpadHint() {
    if (typeof document === 'undefined' || typeof window === 'undefined') return;
    if ('ontouchstart' in window) return;
    if (sessionStorage.getItem(HINT_DISMISS_KEY)) return;
    const el = document.getElementById('camera-hint');
    if (!el) return;
    this._hintEl = el;
    // Defer until the welcome/loading overlays are gone — the boot can take
    // longer than HINT_AUTO_HIDE_MS, and we don't want the hint to expire
    // before the user can see the world.
    const reveal = () => {
      if (!this._hintEl) return;
      el.classList.remove('hidden');
      requestAnimationFrame(() => el.classList.add('is-shown'));
      this._hintShownAt = performance.now();
      this._hintTimer = setTimeout(() => this.#dismissHint(true), HINT_AUTO_HIDE_MS);
    };
    if (!document.body.classList.contains('booting')) { reveal(); return; }
    const obs = new MutationObserver(() => {
      if (!document.body.classList.contains('booting')) {
        obs.disconnect();
        this._hintBootObs = null;
        reveal();
      }
    });
    obs.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    this._hintBootObs = obs;
  }

  // force=true bypasses the minimum-show grace period (used by the 6s
  // auto-hide timer). User gestures only dismiss after the hint has been
  // readable for HINT_MIN_SHOW_MS.
  #dismissHint(force = false) {
    if (!this._hintEl) return;
    if (!force && this._hintShownAt
      && performance.now() - this._hintShownAt < HINT_MIN_SHOW_MS) return;
    const el = this._hintEl;
    this._hintEl = null;
    clearTimeout(this._hintTimer);
    this._hintTimer = null;
    if (this._hintBootObs) { this._hintBootObs.disconnect(); this._hintBootObs = null; }
    sessionStorage.setItem(HINT_DISMISS_KEY, '1');
    el.classList.remove('is-shown');
    setTimeout(() => el.classList.add('hidden'), 360);
  }

  dispose() {
    if (this.canvas) {
      this.canvas.removeEventListener('wheel', this.#onWheel, { capture: true });
    }
    clearTimeout(this._hintTimer);
    this._hintTimer = null;
    this._hintEl = null;
    if (this._hintBootObs) { this._hintBootObs.disconnect(); this._hintBootObs = null; }
    if (this.controls && typeof this.controls.dispose === 'function') {
      this.controls.dispose();
    }
  }

  /** Tell the camera what the player is doing this frame so we can
   *  smoothly zoom out a bit while moving (and a bit more while running). */
  setMovementState({ moving = false, running = false } = {}) {
    if (running && moving) {
      this._movementZoomTarget = 1.18;
      this._polarTiltTarget = 0.03;
    } else if (moving) {
      this._movementZoomTarget = 1.10;
      this._polarTiltTarget = 0;
    } else {
      this._movementZoomTarget = 1.0;
      this._polarTiltTarget = 0;
    }
  }

  /** Set the orbit pivot to the player's head. Camera position derives from this in update(). */
  follow(position) {
    // Clamp the orbit target above the water surface (WATER_LEVEL_Y=0).
    // Without this, wading drops target.y below sea level and certain
    // azimuths push the camera through the back of the double-sided
    // transparent ocean plane (Effects/Water.js).
    this._target.set(
      position.x,
      Math.max(position.y + HEAD_HEIGHT, 0.4),
      position.z,
    );
  }

  /** Forward vector on the ground plane, from camera azimuth. */
  getGroundForward(out = new THREE.Vector3()) {
    this.camera.getWorldDirection(out);
    out.y = 0;
    if (out.lengthSq() < 1e-6) out.set(0, 0, -1);
    else out.normalize();
    return out;
  }

  /** Right vector on the ground plane. */
  getGroundRight(out = new THREE.Vector3()) {
    this.getGroundForward(out);
    out.cross(new THREE.Vector3(0, 1, 0)).normalize();
    return out;
  }

  /**
   * 1. Let camera-controls process input → updates azimuth/polar/distance.
   * 2. Override camera.position = playerHead + sphericalToCartesian(d, az, polar).
   * 3. Look at playerHead.
   *
   * Camera-controls writes camera.position during step 1 — step 2 overrides it.
   * Internal target/sphericalEnd may drift from what we render, but we never
   * read those, so it doesn't matter.
   */
  update(delta) {
    if (this.locked) return; // GSAP zoom drives camera directly while locked.
    this.controls.update(delta);

    // Cinematic zoom: lambda=3 → ~95% convergence in 1 second, so the
    // zoom-out feels smooth and gradual when starting to walk / sprint
    // and slowly relaxes back when stopping. damp() is frame-rate
    // independent so this looks identical at 60 / 120 / 144 fps.
    this._movementZoomFactor = THREE.MathUtils.damp(
      this._movementZoomFactor, this._movementZoomTarget, 3, delta,
    );
    this._polarTilt = THREE.MathUtils.damp(this._polarTilt, this._polarTiltTarget, 3, delta);

    const distance = this.controls.distance * this._movementZoomFactor * this._mobileZoom;
    const azimuth = this.controls.azimuthAngle;
    // Clamp the tilted polar to the orbit's own min/max so the sprint
    // pitch can't push the camera through the ground or up past zenith.
    const polar = THREE.MathUtils.clamp(
      this.controls.polarAngle + this._polarTilt,
      this.controls.minPolarAngle,
      this.controls.maxPolarAngle,
    );

    const sinPolar = Math.sin(polar);
    this._tmpOffset.set(
      distance * sinPolar * Math.sin(azimuth),
      distance * Math.cos(polar),
      distance * sinPolar * Math.cos(azimuth),
    );

    this.camera.position.copy(this._target).add(this._tmpOffset);
    this.camera.lookAt(this._target);
  }

  /**
   * Temporarily zoom the orbit out by `factor` (1.10 = 10% farther). Called
   * by ActionPrompts when a performance animation starts so the player can
   * see the character do the thing. Re-entrant safe.
   */
  applyActionZoom(factor = 1.1) {
    if (this._actionZoomActive) return;
    this._actionZoomActive = true;
    this._savedActionDistance = this.controls.distance;
    const target = Math.min(this.controls.distance * factor, this.controls.maxDistance);
    this.controls.dollyTo(target, true);
  }

  releaseActionZoom() {
    if (!this._actionZoomActive) return;
    this._actionZoomActive = false;
    if (this._savedActionDistance !== undefined) {
      this.controls.dollyTo(this._savedActionDistance, true);
      this._savedActionDistance = undefined;
    }
  }

  /**
   * Used after a GSAP zoom-out completes — re-derive the spherical state from
   * wherever the camera currently is, so the orbit picks up smoothly.
   */
  resync() {
    const offset = this.camera.position.clone().sub(this._target);
    const distance = offset.length();
    const polar = Math.acos(THREE.MathUtils.clamp(offset.y / distance, -1, 1));
    const azimuth = Math.atan2(offset.x, offset.z);
    this.controls.distance = distance;
    this.controls.azimuthAngle = azimuth;
    this.controls.polarAngle = polar;
  }

  snapTo(position, facing = 0) {
    this.follow(position);
    const distance = THREE.MathUtils.clamp(this.controls.distance || 4, this.controls.minDistance, this.controls.maxDistance);
    const polar = THREE.MathUtils.clamp(
      this.controls.polarAngle || Math.PI * 0.42,
      this.controls.minPolarAngle,
      this.controls.maxPolarAngle,
    );
    const azimuth = facing + Math.PI;
    const sinPolar = Math.sin(polar);
    this._tmpOffset.set(
      distance * sinPolar * Math.sin(azimuth),
      distance * Math.cos(polar),
      distance * sinPolar * Math.cos(azimuth),
    );
    const cameraPos = this._target.clone().add(this._tmpOffset);
    this.controls.setLookAt(
      cameraPos.x, cameraPos.y, cameraPos.z,
      this._target.x, this._target.y, this._target.z,
      false,
    );
    this.controls.distance = distance;
    this.controls.azimuthAngle = azimuth;
    this.controls.polarAngle = polar;
    this.camera.position.copy(cameraPos);
    this.camera.lookAt(this._target);
  }
}
