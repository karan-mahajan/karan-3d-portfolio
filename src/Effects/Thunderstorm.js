import * as THREE from 'three/webgpu';

/**
 * Thunderstorm. Random lightning + thunder while rain is on, plus a manual
 * ⚡ trigger button at bottom-center that works any time.
 *
 * Each strike does five things, in order:
 *   1. spawns a thick TubeGeometry bolt (main + optional branch) in the
 *      direction the camera is currently looking
 *   2. flashes a full-screen CSS overlay white
 *   3. punches the AmbientLight intensity up for ~300ms (whole scene goes
 *      bright)
 *   4. fires AudioManager.playThunder(delay, intensity) where delay scales
 *      with bolt distance (real-world: ~343 m/s, here ~40 u/s)
 *   5. pops one of a pool of fun messages near the top of the screen
 *
 * Cleanup is per-frame: each bolt's age is tracked and the mesh +
 * geometries are disposed once opacity reaches zero. Maximum one bolt
 * group on screen at a time (a strike while one is still visible is
 * dropped — see #strike).
 */

const FIRST_STRIKE_RANGE = [15, 30];    // seconds after rain starts
const SUBSEQUENT_RANGE  = [20, 60];     // seconds between strikes
const BOLT_LIFETIME     = 0.25;         // seconds the bolt is visible
const MESSAGE_HOLD_MS   = 2500;
const MESSAGE_FADE_MS   = 1500;
const MANUAL_COOLDOWN_S = 3.0;

const MESSAGES = [
  "⚡ Zeus liked your portfolio",
  "⚡ Thor approves of this code",
  "⚡ That's the power of Full Stack",
  "⚡ console.log('BOOM')",
  "⚡ git push --force",
  "⚡ npm run thunderstruck",
  "⚡ 404: Umbrella Not Found",
  "⚡ Deploying to production...",
  "⚡ Bug found. Bug destroyed.",
  "⚡ The cloud has spoken",
  "⚡ Lightning-fast load times",
  "⚡ sudo make it rain",
  "⚡ Merge conflict resolved... dramatically",
  "⚡ That commit hit different",
  "⚡ Production is DOWN... just kidding",
  "⚡ rm -rf rain/",
  "⚡ Stack Overflow approves",
  "⚡ The sky just rage-quit",
  "⚡ HTTP 200: Heavens OK",
  "⚡ Pushed straight to main",
  "⚡ kernel panic in the sky",
  "⚡ The cloud is now on-premise",
  "⚡ Hot reload, but vertical",
  "⚡ Ctrl+Z on the storm",
  "⚡ The DNS gods are angry",
  "⚡ Zeus opened a pull request",
  "⚡ Cache invalidated by lightning",
  "⚡ The forecast was a typo",
  "⚡ 100% uptime... for the storm",
  "⚡ Compiling the heavens",
  "⚡ My WiFi is also flickering",
  "⚡ It's not a bug, it's weather",
  "⚡ Rebasing onto the troposphere",
  "⚡ Lightning: works on my machine",
];

export class Thunderstorm {
  /**
   * @param {THREE.Scene} scene
   * @param {THREE.Camera} camera
   * @param {THREE.AmbientLight} ambientLight
   * @param {import('../Audio/AudioManager.js').AudioManager} audio
   */
  constructor(scene, camera, ambientLight, audio) {
    this.scene = scene;
    this.camera = camera;
    this.ambientLight = ambientLight;
    this.audio = audio;

    this.active = false;                // only ticks while rain is on
    this._timer = 0;
    this._strikeCount = 0;
    this._nextStrike = this.#randomDelay();
    this._activeBolts = [];
    this._lastPlayerPos = new THREE.Vector3();
    this._lastMessageIdx = -1;          // ensure no two same messages in a row
    this._lastManualStrike = 0;         // perf.now() / 1000 of last manual click

    // Shared bolt materials, created ONCE and reused across every strike.
    // Previously each strike newed + disposed its own materials; disposing
    // frees the compiled GPU program, so the next strike recompiled cold —
    // a recurring hitch on every lightning. Persisting them means the
    // shader compiles a single time (first strike) and stays warm. Only
    // one bolt-group is ever on screen at once (see #strike), so sharing
    // is safe; opacity is reset per-strike and driven by the fade in update().
    this._boltMat = new THREE.MeshBasicMaterial({
      color: 0xddeeff,
      transparent: true,
      opacity: 1,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
    });
    this._glowMat = new THREE.MeshBasicMaterial({
      color: 0x8888ff,
      transparent: true,
      opacity: 0.4,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
    });

    this.#createFlashOverlay();
    this.#createTriggerButton();
  }

  // ── Public API ──────────────────────────────────────────────────────────
  setActive(active) {
    if (active === this.active) return;
    this.active = active;
    this._timer = 0;
    if (!active) {
      this._strikeCount = 0;
      this._nextStrike = this.#randomDelay();
      this.#disposeAllBolts();
    } else {
      this._nextStrike = this.#randomDelay();
    }
  }

  update(delta, playerPos) {
    if (playerPos) this._lastPlayerPos.copy(playerPos);

    // Per-frame bolt aging + disposal — runs even when inactive so any
    // in-flight manual strikes get cleaned up if the user toggles rain off
    // mid-flash.
    for (let i = this._activeBolts.length - 1; i >= 0; i--) {
      const bolt = this._activeBolts[i];
      bolt._age += delta;
      if (bolt._age >= BOLT_LIFETIME) {
        this.#disposeBolt(bolt);
        this._activeBolts.splice(i, 1);
        continue;
      }
      const t = 1 - bolt._age / BOLT_LIFETIME;
      bolt._boltMat.opacity = t;
      bolt._glowMat.opacity = t * 0.4;
    }

    if (!this.active) return;
    this._timer += delta;
    if (this._timer >= this._nextStrike) {
      this._timer = 0;
      this._strikeCount++;
      this._nextStrike = this.#randomDelay();
      this.#strike(this._lastPlayerPos);
    }
  }

  /** Manual ⚡ button handler. Has a cooldown + cancels any imminent
   *  auto-strike so the user doesn't get a double flash. Works even when
   *  rain is off — the button is always live. */
  manualStrike() {
    const now = performance.now() / 1000;
    if (now - this._lastManualStrike < MANUAL_COOLDOWN_S) {
      if (this._triggerBtn) {
        this._triggerBtn.style.animation = 'lightning-shake 0.3s ease';
        // Clear the animation so a follow-up rejection still reads visually.
        setTimeout(() => {
          if (this._triggerBtn) this._triggerBtn.style.animation = '';
        }, 320);
      }
      return;
    }
    this._lastManualStrike = now;

    // If an auto-strike is due within 3s, defer it so we don't double up.
    if (this.active && this._nextStrike - this._timer < MANUAL_COOLDOWN_S) {
      this._timer = 0;
      this._nextStrike = this.#randomDelay();
    }

    this.#strike(this._lastPlayerPos);
    this.achievements?.onLightning?.();

    if (this._triggerBtn) {
      this._triggerBtn.style.boxShadow = '0 0 30px rgba(200, 200, 255, 0.8)';
      setTimeout(() => {
        if (this._triggerBtn) this._triggerBtn.style.boxShadow = '';
      }, 500);
    }
  }

  // ── Internals ───────────────────────────────────────────────────────────
  #randomDelay() {
    const [a, b] = this._strikeCount === 0 ? FIRST_STRIKE_RANGE : SUBSEQUENT_RANGE;
    return a + Math.random() * (b - a);
  }

  #strike(playerPos) {
    // Hard cap: only one strike-group on screen at a time. A strike now
    // packs 3–4 main bolts (different angles) + optional forking branches
    // into a single group so they all fade + dispose together.
    if (this._activeBolts.length > 0) return;

    // 3–4 main bolts per strike, scattered across the camera-front cone
    // so the storm reads as a cluster. Each bolt picks its own SHAPE
    // params (segments + jitter) from a varied pool so no two bolts look
    // alike — short clean strikes mix with long chaotic forks. Skipping
    // this and using uniform params (the first pass shipped that way)
    // read as "the same bolt drawn 4 times" — user feedback was that
    // each line needs to look distinct.
    const boltCount = 3 + Math.floor(Math.random() * 2); // 3 or 4
    let group = null;
    let primaryStart = null; // hero bolt's start point — drives audio delay
    for (let i = 0; i < boltCount; i++) {
      const { start, end } = this.#getBoltPosition(playerPos);
      if (i === 0) primaryStart = start;
      // Per-bolt shape variation. Three rough archetypes mixed at random:
      //   "calm"     — few segments, low jitter (smooth long arc)
      //   "standard" — mid segments + jitter (classic lightning)
      //   "chaotic"  — many segments, high jitter (frenetic shatter)
      // The thickness param feeds straight into #appendBranchToBolt's
      // tube radius — varying it stops every bolt from being the same
      // weight as the primary.
      const archetype = Math.random();
      let segments, jitter, thickness;
      if (archetype < 0.33) {        // calm
        segments = 7 + Math.floor(Math.random() * 2);   // 7–8
        jitter   = 3 + Math.random() * 2;               // 3–5
        thickness = 0.08;
      } else if (archetype < 0.7) {  // standard
        segments = 10 + Math.floor(Math.random() * 3);  // 10–12
        jitter   = 6 + Math.random() * 3;               // 6–9
        thickness = 0.12;
      } else {                       // chaotic
        segments = 14 + Math.floor(Math.random() * 4);  // 14–17
        jitter   = 10 + Math.random() * 4;              // 10–14
        thickness = 0.1;
      }

      if (i === 0) {
        // First bolt creates the shared group + materials at primary
        // thickness — guaranteed to read as the strike's hero line.
        group = this.#createBolt(start, end, segments, jitter);
      } else {
        this.#appendBranchToBolt(group, start, end, segments, jitter, thickness);
      }
      // 35% chance per bolt of an extra forking branch off its midpoint —
      // gives some lines a real Y-shape silhouette while leaving others
      // as clean strikes, adding more shape variety to the cluster.
      if (Math.random() < 0.35) {
        const branchStart = start.clone().lerp(end, 0.3 + Math.random() * 0.3);
        const branchEnd = branchStart.clone().add(
          new THREE.Vector3(
            (Math.random() - 0.5) * 20,
            -(10 + Math.random() * 15),
            (Math.random() - 0.5) * 20,
          ),
        );
        this.#appendBranchToBolt(group, branchStart, branchEnd, 6, 5, 0.07);
      }
    }
    this.scene.add(group);
    this._activeBolts.push(group);

    this.#flashOverlay();
    this.#flashAmbient();

    // Thunder fires SIMULTANEOUSLY with the visual flash. The original
    // spec called for a realistic distance-based delay (~dist/40 seconds)
    // but user testing kept reporting that the thunder seemed to belong
    // to a different strike — when distant rumble arrived 1-2s late, the
    // bolt was already gone and they thought the audio was broken. Now
    // the crack lands on-frame with the flash. Intensity still scales
    // with distance so far strikes are subtly quieter.
    const dist = primaryStart.distanceTo(playerPos);
    const intensity = Math.max(0.75, 1 - dist / 240);
    this.audio?.playThunder?.(0, intensity);

    this.#showMessage();
  }

  /** Place the bolt in front of the camera so the player always sees it. */
  #getBoltPosition(playerPos) {
    const q = this.camera.quaternion;
    const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(q);
    const right   = new THREE.Vector3(1, 0,  0).applyQuaternion(q);
    const distance = 40 + Math.random() * 40;
    const lateral  = (Math.random() - 0.5) * 60;
    const baseX = playerPos.x + forward.x * distance + right.x * lateral;
    const baseZ = playerPos.z + forward.z * distance + right.z * lateral;
    return {
      start: new THREE.Vector3(
        baseX + (Math.random() - 0.5) * 10,
        55 + Math.random() * 25,
        baseZ + (Math.random() - 0.5) * 10,
      ),
      end: new THREE.Vector3(baseX, Math.random() * 3, baseZ),
    };
  }

  /** Build a single-group bolt = main tube + outer glow tube (additive).
   *  Returns a Group with _age + _boltMat + _glowMat hung off it for the
   *  per-frame fade in update(). */
  #createBolt(start, end, segments, jitter) {
    const points = this.#zigzagPath(start, end, segments, jitter);
    const curve = new THREE.CatmullRomCurve3(points);

    // Shared, persistent materials — reset opacity for a fresh strike; the
    // per-frame fade in update() drives them down from here.
    const boltMat = this._boltMat;
    const glowMat = this._glowMat;
    boltMat.opacity = 1;
    glowMat.opacity = 0.4;

    const boltGeom = new THREE.TubeGeometry(curve, segments * 2, 0.15, 6, false);
    const boltMesh = new THREE.Mesh(boltGeom, boltMat);

    const glowGeom = new THREE.TubeGeometry(curve, segments * 2, 0.35, 6, false);
    const glowMesh = new THREE.Mesh(glowGeom, glowMat);

    const group = new THREE.Group();
    group.add(boltMesh);
    group.add(glowMesh);
    group.frustumCulled = false;
    group._age = 0;
    group._boltMat = boltMat;
    group._glowMat = glowMat;
    // Track the pair separately so a branch's geometries can be added below.
    group._geometries = [boltGeom, glowGeom];
    return group;
  }

  /** Attach a secondary bolt to an existing group. Shares the group's
   *  materials so it joins the fade animation for free. `thickness`
   *  controls the inner-tube radius; the outer glow is 2.2× thicker so
   *  every bolt keeps the same shape silhouette regardless of weight. */
  #appendBranchToBolt(group, start, end, segments, jitter, thickness = 0.1) {
    const points = this.#zigzagPath(start, end, segments, jitter);
    const curve = new THREE.CatmullRomCurve3(points);
    const branchGeom = new THREE.TubeGeometry(curve, segments * 2, thickness, 5, false);
    const glowGeom = new THREE.TubeGeometry(curve, segments * 2, thickness * 2.2, 5, false);
    group.add(new THREE.Mesh(branchGeom, group._boltMat));
    group.add(new THREE.Mesh(glowGeom, group._glowMat));
    group._geometries.push(branchGeom, glowGeom);
  }

  /** Random zigzag path with bigger jitter in the middle of the bolt. */
  #zigzagPath(start, end, segments, jitter) {
    const points = [start.clone()];
    for (let i = 1; i < segments; i++) {
      const t = i / segments;
      const p = start.clone().lerp(end, t);
      const midFactor = Math.sin(t * Math.PI);
      p.x += (Math.random() - 0.5) * jitter * midFactor;
      p.z += (Math.random() - 0.5) * jitter * midFactor;
      points.push(p);
    }
    points.push(end.clone());
    return points;
  }

  #disposeBolt(group) {
    this.scene.remove(group);
    for (const g of group._geometries) g.dispose();
    // Materials are shared + persistent (created once in the constructor) so
    // their compiled programs stay warm between strikes — do NOT dispose them
    // here. They live for the page lifetime, like the system itself.
  }

  #disposeAllBolts() {
    for (const bolt of this._activeBolts) this.#disposeBolt(bolt);
    this._activeBolts.length = 0;
  }

  // ── DOM overlays ────────────────────────────────────────────────────────
  #createFlashOverlay() {
    let flash = document.getElementById('lightning-flash');
    if (!flash) {
      flash = document.createElement('div');
      flash.id = 'lightning-flash';
      flash.style.cssText = `
        position: fixed;
        inset: 0;
        background: white;
        opacity: 0;
        pointer-events: none;
        z-index: 50;
        mix-blend-mode: screen;
        transition: opacity 0.02s ease;
      `;
      document.body.appendChild(flash);
    }
    this._flashEl = flash;
  }

  /** Four-step flash: hot burst, dip, secondary pulse (re-strike feel),
   *  long tail. Each setTimeout overrides the transition so the curve
   *  reads as discrete pulses, not a single 300ms ramp. */
  #flashOverlay() {
    const el = this._flashEl;
    if (!el) return;
    el.style.transition = 'opacity 0.02s';
    el.style.opacity = '0.6';
    setTimeout(() => { el.style.transition = 'opacity 0.04s'; el.style.opacity = '0.2'; }, 60);
    setTimeout(() => { el.style.transition = 'opacity 0.04s'; el.style.opacity = '0.4'; }, 120);
    setTimeout(() => { el.style.transition = 'opacity 0.15s'; el.style.opacity = '0.1'; }, 180);
    setTimeout(() => { el.style.transition = 'opacity 0.3s';  el.style.opacity = '0';   }, 300);
  }

  /** Push ambient intensity up for ~350ms so the whole scene "blinks
   *  bright." Restores to whatever the current TimeOfDay palette left
   *  on the light (day vs. night). */
  #flashAmbient() {
    const light = this.ambientLight;
    if (!light) return;
    const orig = light.intensity;
    light.intensity = Math.max(2.5, orig + 2.0);
    setTimeout(() => { light.intensity = Math.max(1.2, orig + 0.8); }, 60);
    setTimeout(() => { light.intensity = Math.max(1.8, orig + 1.4); }, 120);
    setTimeout(() => { light.intensity = orig; }, 350);
  }

  #showMessage() {
    let el = document.getElementById('lightning-msg');
    if (!el) {
      el = document.createElement('div');
      el.id = 'lightning-msg';
      // Static look (dark translucent pill with blue glow) lives in
      // style.css — see `#lightning-msg`. Responsive font-size + max-width
      // there keeps the message readable instead of nowrap-overflowing on
      // narrow phones. Only opacity is driven inline because we restart
      // the fade on every strike.
      el.style.opacity = '0';
      document.body.appendChild(el);
    }

    // Pick a fresh message — never the same one twice in a row.
    let idx;
    do { idx = Math.floor(Math.random() * MESSAGES.length); }
    while (MESSAGES.length > 1 && idx === this._lastMessageIdx);
    this._lastMessageIdx = idx;
    el.textContent = MESSAGES[idx];

    // Restart any previous fade by snapping to 0 first, then ramping in
    // the next frame.
    el.style.transition = 'opacity 0s';
    el.style.opacity = '0';
    requestAnimationFrame(() => {
      el.style.transition = 'opacity 0.15s ease';
      el.style.opacity = '1';
      // Clear any pending fade-out from a previous strike before scheduling
      // a fresh one (otherwise rapid back-to-back strikes can race).
      if (this._msgFadeTimer) clearTimeout(this._msgFadeTimer);
      this._msgFadeTimer = setTimeout(() => {
        el.style.transition = `opacity ${MESSAGE_FADE_MS}ms ease`;
        el.style.opacity = '0';
      }, MESSAGE_HOLD_MS);
    });
  }

  #createTriggerButton() {
    const btn = document.createElement('button');
    btn.id = 'lightning-trigger';
    btn.type = 'button';
    btn.innerHTML = '⚡';
    btn.setAttribute('aria-label', 'Trigger lightning');
    btn.setAttribute('title', 'Trigger lightning');
    btn.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      color: #eeeeff;
      font-size: 22px;
      line-height: 1;
      cursor: pointer;
      z-index: 40;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
      padding: 0;
    `;
    btn.addEventListener('mouseenter', () => {
      btn.style.boxShadow = '0 0 16px rgba(100, 100, 255, 0.5)';
      btn.style.borderColor = 'rgba(180, 200, 255, 0.45)';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.boxShadow = '';
      btn.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    });
    btn.addEventListener('click', () => this.manualStrike());

    document.body.appendChild(btn);
    this._triggerBtn = btn;
  }
}
