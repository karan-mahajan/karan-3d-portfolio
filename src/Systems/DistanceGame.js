import * as THREE from 'three';
import gsap from 'gsap';

/**
 * Distance-guess mini-game. Triggers when the player is standing still at
 * the shore (r > SHORE_RADIUS) looking out toward an unsolved island.
 *
 * Flow:
 *   1. Detect — shore zone + facing outward + island within camera cone
 *      + standing still + not already guessed.
 *   2. Show slider panel; player drags 10-200m and locks in.
 *   3. Animate a 3D additive line from the player to the island with a
 *      slight upward arc + a glowing tracer sphere.
 *   4. Pin a distance label to the arc midpoint via DOM projection.
 *   5. Show result message + accuracy. Within 10m unlocks Eagle Eye;
 *      exact match unlocks Cartographer.
 *   6. Fade and dispose the line 5s after the result.
 *
 * The trigger has hysteresis on top of standing-still detection so the
 * panel doesn't fight a player who's panning the camera while idle.
 */

const SHORE_RADIUS = 38;
const FACING_OUTWARD_DOT = 0.3;
const CAMERA_CONE_RAD = 0.26;           // ≈ 15° half-angle
const SLIDER_MIN = 10;
const SLIDER_MAX = 200;
const LINE_DURATION = 1.6;              // line grow time (slightly longer for drama)
const LINE_HOLD = 4.5;                  // line/label visible after growth
const LINE_FADE = 1.0;                  // fade-out time
const TRIGGER_COOLDOWN = 0.4;           // brief cooldown after skip / close
const STILL_HYSTERESIS = 0.3;           // standing-still time before first show
const NO_TARGET_GRACE = 0.6;            // panel auto-hides after this long with no target in cone
const LINE_ARC_COEFF = 0.11;            // taller arc — gives the line more visible "projection"
const TRACER_RADIUS = 0.6;              // bright core tracer
const TRACER_GLOW_RADIUS = 1.6;         // additive halo around tracer for comet-head look

// Accuracy bands. Cartographer fires on EXACT; Eagle Eye fires on EAGLE_EYE
// or better. Anything past EAGLE_EYE is treated as "wrong" — the panel keeps
// the slider open so the player can guess again without re-acquiring the
// island.
const ACCURACY = {
  EXACT: 0,
  CLOSE: 5,
  EAGLE_EYE: 10,
};

// Random tagline shown under the math hint on a wrong guess. Kept playful
// so the "do some arithmetic" ask doesn't read as a textbook prompt. Each
// tagline must imply the player should apply the expression to their last
// guess to find the answer — but in a teasing voice.
const WRONG_TAGLINES = [
  "Let's see if your math is as bad as your guess.",
  "Quick — what does that come out to?",
  "Time to dust off that grade-school math.",
  "Apply this. Get the answer. Beat the island.",
  "Hope your math is sharper than your eyesight.",
  "Brain go brrr.",
  "Use your fingers if you have to.",
  "Pop quiz. No calculators.",
  "Mental math. You got this. Probably.",
  "Crunch the numbers. The island waits.",
  "If algebra had a beach, this would be it.",
  "Maths. The final frontier.",
  "Show your work — or don't, I won't tell.",
  "Two plus two is four. This is harder.",
  "The island heard your guess. It laughed.",
];

export class DistanceGame {
  #scene;
  #camera;
  #playerCamera;
  #islands;
  #achievements;
  #audio;

  // DOM refs
  #root;
  #panel;
  #slider;
  #guessValue;
  #submitBtn;
  #skipBtn;
  #muteBtn;
  #resultEl;
  #distanceLabel;
  #arrow;

  // State
  #active = false;                      // panel visible / awaiting input
  #lineActive = false;                  // 3D line + tracer in the scene
  #stillTimer = 0;
  #cooldown = 0;
  #noTargetTimer = 0;                   // accumulates while panel is open but no island in cone
  #targetIsland = null;
  #guessedIds = new Set();              // correctly-guessed islands this session
  #skippedIds = new Set();              // explicitly-skipped islands this session
  #disabled = false;                    // session-only flag flipped by "Don't show again"
  #showingCorrectResult = false;        // line is animating; suppress live re-targeting
  #isNight = false;

  // 3D line state
  #line = null;
  #lineGeometry = null;
  #lineMaterial = null;
  #linePositions = null;
  #lineMaxSegments = 100;
  #tracer = null;
  #tracerMaterial = null;
  #animElapsed = 0;
  #animPhase = 'idle';                  // 'growing' | 'holding' | 'fading' | 'idle'
  #lineStart = new THREE.Vector3();
  #lineEnd = new THREE.Vector3();
  #lineArcLift = 0;
  #lineFadeTimer = 0;
  #lineShowLabel = false;               // whether to reveal the distance label (correct guess only)

  // Auto-zoom state: when an arrow would project above the viewport we
  // pull the third-person camera back so the player can see the whole
  // peak. #cameraZoomSaved is the user's previous distance (null when not
  // auto-zoomed); #lastAutoZoomApplied is the value we last wrote so we
  // can detect whether the user manually adjusted the wheel mid-zoom.
  #cameraZoomSaved = null;
  #lastAutoZoomApplied = null;

  constructor({ scene, camera, playerCamera, islands, achievements, audio }) {
    this.#scene = scene;
    this.#camera = camera;
    this.#playerCamera = playerCamera;
    this.#islands = islands;
    this.#achievements = achievements;
    this.#audio = audio;

    this.#root = document.getElementById('distance-game');
    this.#panel = document.getElementById('dg-panel');
    this.#slider = document.getElementById('dg-slider');
    this.#guessValue = document.getElementById('dg-guess-value');
    this.#submitBtn = document.getElementById('dg-submit');
    this.#skipBtn = document.getElementById('dg-skip');
    this.#muteBtn = document.getElementById('dg-mute');
    this.#resultEl = document.getElementById('dg-result');
    this.#distanceLabel = document.getElementById('dg-distance-label');
    this.#arrow = document.getElementById('dg-target-arrow');

    if (!this.#root || !this.#slider || !this.#submitBtn) {
      console.warn('[DistanceGame] missing DOM nodes; mini-game disabled.');
      return;
    }

    this.#wireUI();
  }

  // ── Public API ────────────────────────────────────────────────────────────
  /** Current target island id, or null when no panel is open. */
  getActiveTargetId() {
    return this.#active ? (this.#targetIsland?.id ?? null) : null;
  }

  /** Session-only mute state. True when the player picked "Don't show again". */
  isDisabled() {
    return this.#disabled;
  }

  update(delta, playerPos, { moving = false, isNight = false, inWater = false } = {}) {
    if (!this.#root) return;
    if (this.#disabled) return;
    this.#isNight = isNight;

    if (this.#cooldown > 0) this.#cooldown = Math.max(0, this.#cooldown - delta);

    if (this.#lineActive) this.#tickLine(delta);

    if (inWater) {
      this.#stillTimer = 0;
      this.#hideArrow();
      if (this.#active) this.#close({ cooldown: TRIGGER_COOLDOWN, silent: true });
      return;
    }

    const distFromCenter = Math.hypot(playerPos.x, playerPos.z);
    const inShore = distFromCenter > SHORE_RADIUS;

    // Walking or stepping inland auto-dismisses the panel — the player has
    // moved on, the question shouldn't follow them. Lock state is left
    // intact (#guessedIds, #disabled) so re-engaging at the shore still
    // honours what they've solved or muted.
    if (!inShore || moving) {
      this.#stillTimer = 0;
      this.#hideArrow();
      if (this.#active) this.#close({ cooldown: TRIGGER_COOLDOWN, silent: true });
      return;
    }

    // The correct-result animation locks the target — the line + label are
    // about a specific island and shouldn't repoint mid-flight.
    if (this.#showingCorrectResult) {
      this.#updateArrow();
      return;
    }

    if (!this.#cameraFacingOutward(playerPos)) {
      this.#noTargetTimer += delta;
      this.#hideArrow();
      if (this.#active && this.#noTargetTimer > NO_TARGET_GRACE) {
        this.#close({ cooldown: TRIGGER_COOLDOWN, silent: true });
      }
      this.#stillTimer = 0;
      return;
    }

    const target = this.#findLookedAtIsland(playerPos);
    // Both solved and skipped islands are "off the table" for the rest of
    // the session — neither retriggers the panel.
    if (!target || this.#guessedIds.has(target.id) || this.#skippedIds.has(target.id)) {
      this.#noTargetTimer += delta;
      this.#hideArrow();
      if (this.#active && this.#noTargetTimer > NO_TARGET_GRACE) {
        this.#close({ cooldown: TRIGGER_COOLDOWN, silent: true });
      }
      return;
    }

    // We have a valid target in the camera cone.
    this.#noTargetTimer = 0;
    if (!this.#active) {
      this.#stillTimer += delta;
      if (this.#stillTimer < STILL_HYSTERESIS) return;
      if (this.#cooldown > 0) return;
      this.#open(target);
    } else if (this.#targetIsland !== target) {
      // Live target swap — the player panned to a different island while
      // the slider was open. Switch instantly so the next Lock In grades
      // against the new island. Clear any prior wrong-guess result so the
      // panel reads as a fresh question.
      this.#targetIsland = target;
      this.#clearWrongResult();
    }
    this.#updateArrow();
  }

  // ── Trigger detection ─────────────────────────────────────────────────────
  #cameraFacingOutward(playerPos) {
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(this.#camera.quaternion);
    forward.y = 0;
    if (forward.lengthSq() < 1e-6) return false;
    forward.normalize();
    const outward = new THREE.Vector3(playerPos.x, 0, playerPos.z);
    if (outward.lengthSq() < 1e-6) return false;
    outward.normalize();
    return forward.dot(outward) > FACING_OUTWARD_DOT;
  }

  #findLookedAtIsland(playerPos) {
    const list = this.#islands?.getIslands?.() ?? [];
    if (!list.length) return null;
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(this.#camera.quaternion);
    forward.y = 0;
    if (forward.lengthSq() < 1e-6) return null;
    forward.normalize();

    let best = null;
    let bestAngle = Infinity;
    const toIsland = new THREE.Vector3();
    for (const island of list) {
      toIsland.set(
        island.position.x - playerPos.x,
        0,
        island.position.z - playerPos.z,
      );
      if (toIsland.lengthSq() < 1e-6) continue;
      toIsland.normalize();
      const dot = THREE.MathUtils.clamp(forward.dot(toIsland), -1, 1);
      const angle = Math.acos(dot);
      if (angle < CAMERA_CONE_RAD && angle < bestAngle) {
        bestAngle = angle;
        best = island;
      }
    }
    return best;
  }

  // ── UI ────────────────────────────────────────────────────────────────────
  #wireUI() {
    this.#slider.addEventListener('input', () => {
      this.#guessValue.textContent = `${this.#slider.value}m`;
    });
    this.#submitBtn.addEventListener('click', () => this.#onSubmit());
    this.#skipBtn.addEventListener('click', () => this.#onSkip());
    this.#muteBtn?.addEventListener('click', () => this.#onMute());
    this.#slider.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.#onSubmit();
      }
    });
  }

  #open(island) {
    this.#active = true;
    this.#targetIsland = island;
    this.#resultEl.classList.add('hidden');
    this.#resultEl.innerHTML = '';
    this.#panel.classList.remove('hidden');
    const seed = Math.round((SLIDER_MIN + SLIDER_MAX) / 2 / 5) * 5;
    this.#slider.value = String(seed);
    this.#guessValue.textContent = `${seed}m`;
    this.#submitBtn.disabled = false;
    this.#noTargetTimer = 0;
    this.#root.classList.remove('hidden');
    this.#audio?.playMenuOpen?.();
  }

  /** Close everything UI-related. `silent` skips the close chime — used by
   *  the auto-dismiss path so panning away doesn't squawk every time. */
  #close({ cooldown = TRIGGER_COOLDOWN, silent = false } = {}) {
    this.#active = false;
    this.#showingCorrectResult = false;
    this.#targetIsland = null;
    this.#root.classList.add('hidden');
    this.#resultEl.classList.add('hidden');
    this.#resultEl.innerHTML = '';
    this.#cooldown = cooldown;
    this.#stillTimer = 0;
    this.#noTargetTimer = 0;
    this.#hideArrow();
    this.#restoreCameraZoom();
    if (!silent) this.#audio?.playMenuClose?.();
  }

  #onSkip() {
    if (!this.#active) return;
    // Persist a "I don't want to guess this one" marker for the session.
    // The trigger guard above treats #skippedIds same as #guessedIds so
    // the panel won't pop again for the same island after the player
    // pans back to it — only a page reload re-arms.
    if (this.#targetIsland) this.#skippedIds.add(this.#targetIsland.id);
    this.#close();
  }

  #onMute() {
    this.#disabled = true;
    this.#close({ silent: true });
    this.#disposeLine();
  }

  #onSubmit() {
    if (!this.#active || !this.#targetIsland) return;
    const guess = Number(this.#slider.value);
    const actual = this.#targetIsland.distance;
    const diff = Math.abs(guess - actual);
    const exactMatch = diff <= ACCURACY.EXACT;
    const close = diff <= ACCURACY.CLOSE;
    const eagle = diff <= ACCURACY.EAGLE_EYE;

    this.#audio?.playClick?.();

    if (eagle) {
      // Correct (within 10m). Unlock both achievements as applicable and
      // mark the island solved so the panel won't ask about it again.
      if (exactMatch) this.#achievements?.trigger?.('distance_master');
      this.#achievements?.trigger?.('distance_guesser');
      this.#guessedIds.add(this.#targetIsland.id);
      this.#submitBtn.disabled = true;
      // Shoot line first (it disposes any previous animation), then set
      // the flag — disposeLine reads/manages its own state but the live
      // re-target gate has to remain true for the duration of the new
      // animation.
      this.#shootLine(this.#targetIsland, { exactMatch, close, eagle, showLabel: true });
      this.#showingCorrectResult = true;
      this.#renderCorrectResult({ guess, actual, diff, exactMatch, close });
    } else {
      // Wrong. Shoot the line so the player still sees where the island
      // is — but DON'T pin a label with the actual distance and don't
      // reveal the number in the result text. Keeps "try again" honest.
      this.#shootLine(this.#targetIsland, { exactMatch: false, close: false, eagle: false, showLabel: false });
      this.#renderWrongResult(diff);
    }
  }

  /**
   * Correct-guess card — shows the actual distance, the 3D line, and a
   * "Try Another Island" button. Locks the target until the player
   * dismisses.
   */
  #renderCorrectResult({ guess, actual, diff, exactMatch, close }) {
    let emoji, color, message;
    if (exactMatch) { emoji = '🎯'; color = '#aaee44'; message = 'Bullseye! Exact distance.'; }
    else if (close) { emoji = '🔥'; color = '#aaee44'; message = `So close — off by ${diff}m`; }
    else            { emoji = '🦅'; color = '#ffcc33'; message = `Eagle eye! Off by ${diff}m`; }

    this.#resultEl.innerHTML = `
      <div class="dg-result-emoji">${emoji}</div>
      <div class="dg-result-message" style="color: ${color}">${escapeHTML(message)}</div>
      <div class="dg-result-actual">Actual: ${Math.round(actual)}m · Your guess: ${guess}m</div>
      <button class="dg-try-another" id="dg-try-another" type="button">Try Another Island</button>
    `;
    this.#resultEl.classList.remove('hidden');
    document.getElementById('dg-try-another')?.addEventListener('click', () => {
      this.#audio?.playClick?.();
      this.#showingCorrectResult = false;
      this.#close();
    }, { once: true });
  }

  /**
   * Wrong-guess nudge — slider stays interactive. The hint is a small
   * arithmetic expression on the player's guess that yields the actual
   * distance (e.g. "60 + 25", "120 ÷ 2"). All operands are integers
   * because both guess and actual snap to multiples of 5. The shoot-line
   * still draws toward the island so the player has a visual cue, but
   * the floating distance label is suppressed (see #onSubmit).
   */
  #renderWrongResult(diff) {
    const guess = Number(this.#slider.value);
    const actual = this.#targetIsland.distance;
    const expr = this.#makeMathHint(guess, actual);
    const tagline = WRONG_TAGLINES[Math.floor(Math.random() * WRONG_TAGLINES.length)];
    this.#resultEl.innerHTML = `
      <div class="dg-result-emoji">🤔</div>
      <div class="dg-result-message" style="color: #ffcc33">${escapeHTML(expr)}</div>
      <div class="dg-result-hint">${escapeHTML(tagline)}</div>
    `;
    this.#resultEl.classList.remove('hidden');
    this.#submitBtn.disabled = false;
  }

  /**
   * Build a guess-relative math expression whose evaluation equals the
   * actual distance. Picks randomly among the operations available for
   * the current pair so successive wrong guesses don't always show the
   * same kind of hint.
   *
   * Available ops:
   *   guess + N     when actual > guess  (N = diff)
   *   guess − N     when actual < guess  (N = -diff)
   *   guess × N     when actual is an exact integer multiple of guess
   *   guess ÷ N     when guess is an exact integer multiple of actual
   *
   * Integer-only by construction since both distances are multiples of 5.
   */
  #makeMathHint(guess, actual) {
    const diff = actual - guess;
    const ops = [];
    if (diff > 0) ops.push(`${guess} + ${diff}`);
    else if (diff < 0) ops.push(`${guess} − ${-diff}`);
    else ops.push(`${guess}`);
    if (guess > 0 && actual > guess && actual % guess === 0) {
      ops.push(`${guess} × ${actual / guess}`);
    }
    if (actual > 0 && guess > actual && guess % actual === 0) {
      ops.push(`${guess} ÷ ${guess / actual}`);
    }
    return ops[Math.floor(Math.random() * ops.length)];
  }

  /** Live-target swap clears any wrong-guess hint left over from the
   *  previous island so the panel reads fresh for the new one. */
  #clearWrongResult() {
    if (this.#showingCorrectResult) return;
    if (this.#resultEl.classList.contains('hidden')) return;
    this.#resultEl.classList.add('hidden');
    this.#resultEl.innerHTML = '';
    this.#submitBtn.disabled = false;
  }

  /** Project the targeted island's peak into screen space and pin the
   *  bouncing arrow above it. Hides the arrow when the projection is
   *  behind the camera or off-screen. Also nudges the camera back when
   *  the peak would clip above the viewport. */
  #updateArrow() {
    if (!this.#arrow || !this.#targetIsland) return this.#hideArrow();
    if (this.#showingCorrectResult) return this.#hideArrow();

    const peakLift = 4 * this.#targetIsland.scale * this.#targetIsland.heightScale + 2;
    const world = new THREE.Vector3(
      this.#targetIsland.position.x,
      peakLift,
      this.#targetIsland.position.z,
    );
    const v = world.clone().project(this.#camera);
    if (v.z > 1 || v.z < -1) return this.#hideArrow();
    const x = (v.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-v.y * 0.5 + 0.5) * window.innerHeight;

    // Auto-zoom defense — if the projected peak is too close to the top
    // of the viewport, pull the third-person camera back a step so the
    // mountain fits in frame. Threshold is ~80px because the bouncing
    // arrow itself is ~44px tall + needs breathing room.
    const TOP_MARGIN = 80;
    if (y < TOP_MARGIN) this.#applyAutoZoom();
    else this.#maybeReleaseAutoZoom();

    // Clamp so a slightly off-screen island still gets an arrow at the
    // edge (avoids visually losing the indicator).
    const cx = Math.max(20, Math.min(window.innerWidth - 20, x));
    const cy = Math.max(40, Math.min(window.innerHeight - 40, y));
    this.#arrow.style.left = `${cx}px`;
    this.#arrow.style.top = `${cy}px`;
    this.#arrow.classList.remove('hidden');
  }

  #hideArrow() {
    this.#arrow?.classList.add('hidden');
  }

  /** Pull the third-person camera out enough to keep the targeted peak
   *  in frame. Snapshots the user's previous distance so #close can
   *  restore it. Re-entrant: subsequent calls just bump toward the cap. */
  #applyAutoZoom() {
    const ctrl = this.#playerCamera?.controls;
    if (!ctrl) return;
    const max = ctrl.maxDistance ?? 12;
    if (this.#cameraZoomSaved == null) {
      this.#cameraZoomSaved = ctrl.distance;
    }
    // Bump to the cap — at the third-person rig's maxDistance the FOV
    // covers the tallest mountain at 110m comfortably.
    const target = max;
    if (Math.abs(ctrl.distance - target) > 0.05) {
      ctrl.distance = target;
      this.#lastAutoZoomApplied = target;
    }
  }

  /** Only let auto-zoom go if the user hasn't manually touched the wheel
   *  while it was active — if they did (distance now differs from our
   *  last write), respect their value and abandon the snapshot. */
  #maybeReleaseAutoZoom() {
    if (this.#cameraZoomSaved == null) return;
    const ctrl = this.#playerCamera?.controls;
    if (!ctrl) return;
    if (this.#lastAutoZoomApplied != null
        && Math.abs(ctrl.distance - this.#lastAutoZoomApplied) > 0.5) {
      // User scrolled mid-zoom — keep their new value, drop the snapshot.
      this.#cameraZoomSaved = null;
      this.#lastAutoZoomApplied = null;
      return;
    }
    ctrl.distance = this.#cameraZoomSaved;
    this.#cameraZoomSaved = null;
    this.#lastAutoZoomApplied = null;
  }

  /** Always release on panel close. Same user-override guard as above. */
  #restoreCameraZoom() {
    this.#maybeReleaseAutoZoom();
  }

  // ── 3D animated line + tracer ─────────────────────────────────────────────
  #shootLine(island, { exactMatch, close, eagle, showLabel = true }) {
    this.#disposeLine();
    this.#lineShowLabel = !!showLabel;

    const playerHere = this.#playerCamera?._target ?? null;
    const start = new THREE.Vector3(
      playerHere?.x ?? this.#camera.position.x,
      (playerHere?.y ?? this.#camera.position.y) - 0.4,
      playerHere?.z ?? this.#camera.position.z,
    );
    const end = new THREE.Vector3(island.position.x, 1.5, island.position.z);

    const totalLength = start.distanceTo(end);
    this.#lineStart.copy(start);
    this.#lineEnd.copy(end);
    this.#lineArcLift = totalLength * LINE_ARC_COEFF;

    const color = this.#pickLineColor({ exactMatch, close, eagle });

    this.#linePositions = new Float32Array(this.#lineMaxSegments * 3);
    this.#lineGeometry = new THREE.BufferGeometry();
    this.#lineGeometry.setAttribute('position', new THREE.BufferAttribute(this.#linePositions, 3));
    this.#lineGeometry.setDrawRange(0, 2);
    this.#lineMaterial = new THREE.LineBasicMaterial({
      color,
      transparent: true,
      opacity: 1.0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false,
    });
    this.#line = new THREE.Line(this.#lineGeometry, this.#lineMaterial);
    this.#line.frustumCulled = false;
    this.#line.userData.noTorchRaycast = true;
    this.#scene.add(this.#line);

    // Tracer = bright core sphere + larger additive halo. The halo gives
    // the head a real "comet" feel even at long distances where the line
    // itself is just one pixel wide. Both fade together in #startFade.
    this.#tracerMaterial = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 1.0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false,
      toneMapped: false,
    });
    this.#tracer = new THREE.Mesh(
      new THREE.SphereGeometry(TRACER_RADIUS, 12, 12),
      this.#tracerMaterial,
    );
    this.#tracer.frustumCulled = false;
    this.#tracer.position.copy(start);
    this.#tracer.userData.noTorchRaycast = true;
    this.#scene.add(this.#tracer);

    // Outer glow halo — same colour, much larger, additive, low opacity.
    // Held as a child of the tracer so it tracks automatically.
    const haloMat = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 0.35,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false,
      toneMapped: false,
    });
    const halo = new THREE.Mesh(
      new THREE.SphereGeometry(TRACER_GLOW_RADIUS, 14, 14),
      haloMat,
    );
    halo.frustumCulled = false;
    halo.userData.noTorchRaycast = true;
    halo.userData.dgHalo = true; // tagged so #startFade can fade it
    this.#tracer.add(halo);

    this.#lineActive = true;
    this.#animPhase = 'growing';
    this.#animElapsed = 0;
    this.#lineFadeTimer = 0;

    this.#distanceLabel.textContent = `${Math.round(island.distance)}m`;
    this.#distanceLabel.classList.add('hidden');
  }

  #pickLineColor({ exactMatch, close, eagle }) {
    if (this.#isNight) {
      if (exactMatch) return new THREE.Color(0x88bbff);
      if (close)      return new THREE.Color(0xaaccff);
      if (eagle)      return new THREE.Color(0xffdd66);
      return new THREE.Color(0xff88aa);
    }
    if (exactMatch) return new THREE.Color(0xaaee44);
    if (close)      return new THREE.Color(0xddff66);
    if (eagle)      return new THREE.Color(0xffcc33);
    return new THREE.Color(0xff8844);
  }

  #tickLine(delta) {
    if (this.#animPhase === 'growing') {
      this.#animElapsed += delta;
      const t = Math.min(this.#animElapsed / LINE_DURATION, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      this.#writeLineArc(eased);
      this.#positionTracer(eased);

      if (t >= 1) {
        this.#animPhase = 'holding';
        this.#lineFadeTimer = 0;
        if (this.#lineShowLabel) this.#distanceLabel.classList.remove('hidden');
      }
    } else if (this.#animPhase === 'holding') {
      this.#lineFadeTimer += delta;
      if (this.#lineShowLabel) this.#updateDistanceLabel();
      this.#positionTracer(1);
      // Wrong-guess lines linger a bit shorter so they don't outstay
      // the "try again" prompt; correct lines stay for the full hold.
      const hold = this.#lineShowLabel ? LINE_HOLD : 2.0;
      if (this.#lineFadeTimer >= hold) this.#startFade();
    } else if (this.#animPhase === 'fading') {
      if (this.#lineShowLabel) this.#updateDistanceLabel();
    }
  }

  #writeLineArc(progress) {
    const segments = Math.max(1, Math.floor(progress * (this.#lineMaxSegments - 1)) + 1);
    for (let i = 0; i <= segments; i++) {
      const segT = i / (this.#lineMaxSegments - 1);
      const t = Math.min(segT, progress);
      const px = THREE.MathUtils.lerp(this.#lineStart.x, this.#lineEnd.x, t);
      const py = THREE.MathUtils.lerp(this.#lineStart.y, this.#lineEnd.y, t)
        + Math.sin(t * Math.PI) * this.#lineArcLift;
      const pz = THREE.MathUtils.lerp(this.#lineStart.z, this.#lineEnd.z, t);
      const idx = i * 3;
      this.#linePositions[idx]     = px;
      this.#linePositions[idx + 1] = py;
      this.#linePositions[idx + 2] = pz;
    }
    this.#lineGeometry.attributes.position.needsUpdate = true;
    this.#lineGeometry.setDrawRange(0, segments + 1);
  }

  #positionTracer(progress) {
    const t = progress;
    const px = THREE.MathUtils.lerp(this.#lineStart.x, this.#lineEnd.x, t);
    const py = THREE.MathUtils.lerp(this.#lineStart.y, this.#lineEnd.y, t)
      + Math.sin(t * Math.PI) * this.#lineArcLift;
    const pz = THREE.MathUtils.lerp(this.#lineStart.z, this.#lineEnd.z, t);
    this.#tracer.position.set(px, py, pz);
  }

  #updateDistanceLabel() {
    if (!this.#distanceLabel) return;
    // Pin to the world-space midpoint above the arc apex.
    const midX = (this.#lineStart.x + this.#lineEnd.x) / 2;
    const midZ = (this.#lineStart.z + this.#lineEnd.z) / 2;
    const midY = (this.#lineStart.y + this.#lineEnd.y) / 2 + this.#lineArcLift + 1.0;
    const v = new THREE.Vector3(midX, midY, midZ).project(this.#camera);
    if (v.z > 1 || v.z < -1) {
      this.#distanceLabel.style.opacity = '0';
      return;
    }
    const x = (v.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-v.y * 0.5 + 0.5) * window.innerHeight;
    this.#distanceLabel.style.left = `${x}px`;
    this.#distanceLabel.style.top = `${y}px`;
    this.#distanceLabel.style.opacity = '1';
  }

  #startFade() {
    this.#animPhase = 'fading';
    if (this.#lineMaterial) {
      gsap.to(this.#lineMaterial, { opacity: 0, duration: LINE_FADE });
    }
    // Fade the halo child (if present) alongside the core tracer so the
    // glow disappears with the rest instead of lingering.
    if (this.#tracer) {
      for (const child of this.#tracer.children) {
        if (child.userData?.dgHalo && child.material) {
          gsap.to(child.material, { opacity: 0, duration: LINE_FADE });
        }
      }
    }
    if (this.#tracerMaterial) {
      gsap.to(this.#tracerMaterial, {
        opacity: 0,
        duration: LINE_FADE,
        onComplete: () => this.#disposeLine(),
      });
    } else {
      this.#disposeLine();
    }
    gsap.to(this.#distanceLabel, {
      opacity: 0,
      duration: LINE_FADE,
      onComplete: () => this.#distanceLabel.classList.add('hidden'),
    });
  }

  #disposeLine() {
    if (this.#line) {
      this.#scene.remove(this.#line);
      this.#lineGeometry?.dispose();
      this.#lineMaterial?.dispose();
    }
    if (this.#tracer) {
      // Walk children first so the halo's geometry + material get released.
      for (const child of this.#tracer.children.slice()) {
        child.geometry?.dispose?.();
        child.material?.dispose?.();
        this.#tracer.remove(child);
      }
      this.#scene.remove(this.#tracer);
      this.#tracer.geometry.dispose();
      this.#tracerMaterial?.dispose();
    }
    this.#line = null;
    this.#lineGeometry = null;
    this.#lineMaterial = null;
    this.#linePositions = null;
    this.#tracer = null;
    this.#tracerMaterial = null;
    this.#lineActive = false;
    this.#animPhase = 'idle';
    this.#distanceLabel.classList.add('hidden');
    this.#distanceLabel.style.opacity = '';
    // NOTE: do NOT clear #showingCorrectResult here — disposeLine runs at
    // the *start* of every shootLine (to clean any prior animation) and
    // clearing the flag would let the live-target gate close the panel
    // mid-animation. The flag is owned by #renderCorrectResult /
    // dismissal paths (#close, mute).
  }
}

function escapeHTML(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[c]);
}
