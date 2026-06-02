import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { ColourGardenHud } from './ColourGardenHud.js';

/**
 * Colour Garden — a pure-entertainment paint-throw mini-game.
 *
 * Discovery: a bobbing down-arrow + ground ring beacon (time-of-day tinted)
 * marks the Blender-authored garden. Walk within range → "Press E". Entering
 * is a deliberate GAME MODE: the camera eases to a raised wide shot of the
 * sculpture field, WASD locks, and a HUD appears (six colour swatches + a
 * charge meter + instructions). You pick a colour (1–6 / click) — it loads as
 * paint in your hand — aim with the mouse (a live dotted trajectory arc +
 * landing reticle show exactly where it lands; aim-assist snaps onto a
 * sculpture), hold F to charge distance, release to throw. The orb flies the
 * shown arc, splats, and the grey sculpture blooms to that colour in slow-mo.
 * Esc exits and restores the normal camera + controls. Painted state persists.
 *
 * Loaded from its OWN GLB (manifest.interactive), deliberately kept out of
 * GlbV3World's shared-material prop-merge so each statue keeps an individual
 * material this class can recolour. Effects are colour-only (no displacement).
 */

const GARDEN_GLB = '/world/colourGarden/colourGarden.glb'; // static/ is publicDir
const STORAGE_KEY = 'karan-colour-garden-v1';
const GREY_HEX = '#9aa0aa';

// Fallback hues by pot name — only used if a pot mesh has no readable colour.
// The live hue is read from the pot's actual material so hand == pot == bloom.
const POT_FALLBACK = {
  gardenPot_crimson: '#d81e38',
  gardenPot_amber: '#f3730f',
  gardenPot_gold: '#fad12b',
  gardenPot_emerald: '#33b34d',
  gardenPot_azure: '#2e8cf2',
  gardenPot_violet: '#8c4dd9',
};
// Stable swatch order (so 1–6 is consistent regardless of GLB traversal order).
const POT_ORDER = [
  'gardenPot_crimson', 'gardenPot_amber', 'gardenPot_gold',
  'gardenPot_emerald', 'gardenPot_azure', 'gardenPot_violet',
];

const HEAD_HEIGHT = 1.2;          // mirrors PlayerCamera; used to restore orbit on exit
const ENTER_RADIUS = 9;           // show "Press E" within this of the field
// The character controller auto-steps onto anything ≤0.4m tall (Physics.js
// enableAutostep). The pots are knee-high, so a pot-sized collider lets the
// player perch on them. Make their collider taller than that so it blocks at
// the side instead of being climbable (base stays on the ground).
const POT_BLOCK_HEIGHT = 0.75;
const SHOULDER_Y = 1.4;           // throw origin height above the throwing spot
const CAM_FIT_K = 2.0;            // wide-shot distance behind the station ≈ field span × this
const CAM_HEIGHT_K = 1.4;         // wide-shot height ≈ field span × this
const CAM_BACK_MIN = 9;           // floors so a small field still frames the whole fan
const CAM_UP_MIN = 7.5;
const CAM_TARGET_LIFT = 0.8;      // raise the look-at a touch off the ground
const STATION_SETBACK = 1.6;      // player stands this far behind the pots (toward the camera)
const ENTER_TWEEN = 0.9;          // camera ease in/out (seconds)

const CHARGE_KEY = 'KeyF';
const CHARGE_TIME = 0.9;          // seconds hold → full charge (a fuller charge throws flatter)
const ARC_APEX_BASE = 1.3;        // arc height floor
const ARC_APEX_PER_M = 0.13;      // arc height growth per metre of throw distance
const MIN_DIST = 4;               // landing distance at zero charge
const MAX_DIST = 20;              // landing distance at full charge
const HIT_RADIUS = 1.7;           // landing must fall within this of a sculpture to hit it (skill tolerance)
const ARC_DOTS = 18;              // trajectory preview resolution
const TRAIL_N = 16;               // flying-orb trail length

const BLOOM_TIME = 0.6;           // grey→colour lerp duration
// Frame fractions into the (sped-up) throw clip — tune after first viewing.
const WINDUP_FRAC = 0.34;         // clip freezes here while F is held (arm cocked)
const RELEASE_FRAC = 0.45;        // orb leaves the hand here → arc launches
const THROW_RATE = 1.9;           // clip is ~5.6s; play faster so release follows the key quickly

const DIGIT_TO_INDEX = {
  Digit1: 0, Digit2: 1, Digit3: 2, Digit4: 3, Digit5: 4, Digit6: 5,
  Numpad1: 0, Numpad2: 1, Numpad3: 2, Numpad4: 3, Numpad5: 4, Numpad6: 5,
};

export class ColourGarden {
  constructor({ scene, physics, player, playerCamera, controller, audio, app, loader, timeOfDay, achievements = null }) {
    this.scene = scene;
    this.physics = physics;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.audio = audio;
    this.app = app;
    this.loader = loader;
    this.timeOfDay = timeOfDay;
    this.achievements = achievements;

    this.group = null;
    this.statues = [];   // { id, meshes, center, body, painted, hue, bloom }
    this.pots = [];      // { id, obj, hue:Color, hex, css }
    this.swatches = [];  // ordered [{ hue:Color, hex, css }]
    this.cauldron = null;
    this.cauldronPaint = null;
    this.groundY = 0.05;

    // out | entering | aiming | charging | releasing | flying | exiting
    this.mode = 'out';
    this._near = false;
    this._selected = 0;
    this._hue = new THREE.Color('#ffffff');
    this.charge = 0;
    this._keyWasDown = false;
    this._t = 0;
    this._ready = false;
    this._mouseNX = 0.5;
    this._mouseNY = 0.5;
    this._mouseX = typeof window !== 'undefined' ? window.innerWidth / 2 : 0;
    this._mouseY = typeof window !== 'undefined' ? window.innerHeight / 2 : 0;
    // Aim needs a mouse and exit needs Esc, so the game is desktop-only for now.
    // On touch the beacon still shows, but the walk-up prompt / entry are gated.
    this._isTouch = typeof matchMedia === 'function' && matchMedia('(pointer: coarse)').matches;

    // Stations (computed once statues are known).
    this.fieldCenter = new THREE.Vector3();
    this.throwSpot = new THREE.Vector3();
    this.baseYaw = 0;
    this._camEye = new THREE.Vector3();
    this._camTarget = new THREE.Vector3();
    this._wideEye = new THREE.Vector3();
    this._wideTarget = new THREE.Vector3();

    this._tmp = new THREE.Vector3();
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    this._hand = new THREE.Vector3();

    // Mouse-cursor aiming: raycast from the wide-shot camera through the cursor
    // onto the sculptures (or the ground plane). The cursor literally points at
    // where the paint lands — no inversion, no cone, reaches every sculpture.
    this._ray = new THREE.Raycaster();
    this._ndc = new THREE.Vector2();
    this._baseDir = new THREE.Vector3(0, 0, 1);
    this._station = new THREE.Vector3();
    this._potsRadius = 1.6;
    this._statueMeshes = [];
    this._meshStatue = new Map();
    this._groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

    this._aim = {
      origin: new THREE.Vector3(),
      landing: new THREE.Vector3(),
      apex: 3,
      statue: null,
    };
    this.flight = {
      from: new THREE.Vector3(),
      to: new THREE.Vector3(),
      apex: 3,
      t: 0,
      dur: 1,
      statue: null,
    };

    this._hueMats = new Map();
    this.#buildOrb();
    this.#buildParticlePool();
    this.#buildArc();
    this.#buildReticle();
    this.#buildTrail();

    this.hud = new ColourGardenHud();
    this.hud.onSelect((i) => this.#selectSwatch(i, true));

    this._onPointerMove = (e) => {
      this._mouseX = e.clientX;
      this._mouseY = e.clientY;
      this._mouseNX = e.clientX / Math.max(1, window.innerWidth);
      this._mouseNY = e.clientY / Math.max(1, window.innerHeight);
    };
    window.addEventListener('pointermove', this._onPointerMove);
    this._onKeyDown = this.#onKeyDown.bind(this);
    window.addEventListener('keydown', this._onKeyDown, { capture: true });
  }

  // ----------------------------------------------------------------- loading
  async load() {
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(GARDEN_GLB);
    } catch (err) {
      console.warn('[ColourGarden] GLB load failed:', err?.message || err);
      return;
    }

    this.group = gltf.scene;
    this.group.name = 'colourGarden';
    this.scene.add(this.group);
    this.group.updateWorldMatrix(true, true);

    const byId = new Map();
    this.group.traverse((o) => {
      if (!o.isMesh) return;
      o.receiveShadow = true;
      o.castShadow = o.name.startsWith('gardenStatue_'); // only statues cast shadow
      if (o.name.startsWith('gardenStatue_')) {
        const id = o.name.replace(/^(gardenStatue_[a-z]+).*$/i, '$1');
        if (!byId.has(id)) byId.set(id, []);
        byId.get(id).push(o);
      } else if (o.name.startsWith('gardenPot_')) {
        this.#registerPot(o);
      } else if (o.name === 'gardenCauldron') {
        this.cauldron = o;
        this.#addColliderFor(o);
      } else if (o.name === 'gardenCauldronPaint') {
        this.cauldronPaint = o;
      }
    });
    for (const [id, meshes] of byId) this.#registerStatue(id, meshes);

    if (this.statues.length) {
      const box = new THREE.Box3();
      for (const m of this.statues[0].meshes) box.expandByObject(m);
      this.groundY = box.min.y + 0.05;
    }

    // Raycast targets + the ground plane the aim ray falls back to.
    for (const st of this.statues) {
      for (const m of st.meshes) { this._statueMeshes.push(m); this._meshStatue.set(m, st); }
    }
    this._groundPlane.set(new THREE.Vector3(0, 1, 0), -(this.groundY - 0.05));

    this.#buildSwatches();
    this.#computeStations();
    this.#buildBeacon();
    this.#restore();
    this._ready = true;
    console.log(
      `[ColourGarden] ready — ${this.statues.length} statues, ${this.pots.length} pots`,
    );
  }

  #registerStatue(id, meshes) {
    for (const m of meshes) m.material = m.material.clone(); // per-instance → paintable
    const box = new THREE.Box3();
    for (const m of meshes) box.expandByObject(m);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    let body = null;
    if (this.physics?.ready) {
      body = this.physics.addStaticCuboid(
        center.x, center.y, center.z,
        Math.max(size.x / 2, 0.05),
        Math.max(size.y / 2, 0.05),
        Math.max(size.z / 2, 0.05),
      );
    }
    this.statues.push({ id, meshes, center, body, painted: false, hue: null, bloom: null });
  }

  #registerPot(mesh) {
    mesh.material = mesh.material.clone();
    // The hue the player SEES on the pot is the source of truth (so the orb +
    // bloom match). Fall back to the authored hex only if the material has no
    // usable colour.
    let hue = mesh.material?.color ? mesh.material.color.clone() : null;
    if (!hue || (hue.r + hue.g + hue.b) < 0.05) hue = new THREE.Color(POT_FALLBACK[mesh.name] || '#ffffff');
    this.#addColliderFor(mesh, POT_BLOCK_HEIGHT);
    this.pots.push({ id: mesh.name, obj: mesh, hue, hex: hue.getHexString(), css: hue.getStyle() });
  }

  // Box collider sized to the visible mesh (CLAUDE.md rule 5) so the player
  // can't walk through it. `minHeight` raises the collider's TOP above the
  // controller's 0.4m autostep (keeping the base on the ground) so small props
  // block at the side instead of being climbable.
  #addColliderFor(mesh, minHeight = 0) {
    if (!this.physics?.ready) return;
    const box = new THREE.Box3().setFromObject(mesh);
    const size = box.getSize(this._tmpA);
    const center = box.getCenter(this._tmpB);
    const height = Math.max(size.y, minHeight);
    const cy = box.min.y + height / 2; // extend upward; keep the base grounded
    this.physics.addStaticCuboid(
      center.x, cy, center.z,
      Math.max(size.x / 2, 0.05), Math.max(height / 2, 0.05), Math.max(size.z / 2, 0.05),
    );
  }

  #buildSwatches() {
    const found = new Map(this.pots.map((p) => [p.id, p]));
    const ordered = POT_ORDER.map((id) => found.get(id)).filter(Boolean);
    // Any pots not in the canonical order get appended so nothing is lost.
    for (const p of this.pots) if (!POT_ORDER.includes(p.id)) ordered.push(p);
    this.swatches = ordered.map((p) => ({ hue: p.hue, hex: p.hex, css: p.css }));
    for (const s of this.swatches) this.#hueMaterial(s.hex);
    this.hud.setSwatches(this.swatches.map((s) => s.css));
    if (this.swatches.length) this.#applySwatch(0);
  }

  #computeStations() {
    // Field centre = average of statue centres (the throw targets).
    const fc = this.fieldCenter.set(0, 0, 0);
    for (const st of this.statues) fc.add(st.center);
    if (this.statues.length) fc.multiplyScalar(1 / this.statues.length);

    // Station = the pots cluster (where the colours live) — the player stands
    // here and the beacon marks it. Fall back to a point pulled back from the
    // field if there are no pots.
    const station = this._station;
    if (this.pots.length) {
      station.set(0, 0, 0);
      for (const p of this.pots) station.add(p.obj.getWorldPosition(this._tmpA));
      station.multiplyScalar(1 / this.pots.length);
    } else {
      const toSpawn = this._tmpA.set(-fc.x, 0, -fc.z);
      if (toSpawn.lengthSq() < 1e-4) toSpawn.set(0, 0, 1);
      station.copy(fc).addScaledVector(toSpawn.normalize(), 5.5);
    }
    station.y = this.#groundAt(station.x, station.z);

    // Radius that encloses the pots (for the beacon ring).
    let pr = 1.2;
    for (const p of this.pots) pr = Math.max(pr, station.distanceTo(p.obj.getWorldPosition(this._tmpA)));
    this._potsRadius = pr + 0.5;

    // Aim base direction: from the station toward the field.
    const baseDir = this._baseDir.copy(fc).sub(station);
    baseDir.y = 0;
    if (baseDir.lengthSq() < 1e-4) baseDir.set(0, 0, 1);
    baseDir.normalize();
    this.baseYaw = Math.atan2(baseDir.x, baseDir.z);

    // Throwing spot: a touch behind the pots so the player isn't inside them.
    this.throwSpot.copy(station).addScaledVector(baseDir, -STATION_SETBACK);
    this.throwSpot.y = this.#groundAt(this.throwSpot.x, this.throwSpot.z);

    // Frame the WHOLE fan: pull back/up proportional to how far the sculptures
    // spread from the field centre, so corner statues stay on-screen and the
    // cursor can reach every one of them.
    let span = 4;
    for (const st of this.statues) span = Math.max(span, st.center.distanceTo(fc));
    span += 3;
    const camBack = Math.max(CAM_BACK_MIN, span * CAM_FIT_K);
    const camUp = Math.max(CAM_UP_MIN, span * CAM_HEIGHT_K);
    this._wideEye.copy(this.throwSpot).addScaledVector(baseDir, -camBack);
    this._wideEye.y = this.throwSpot.y + camUp;
    this._wideTarget.copy(fc);
    this._wideTarget.y += CAM_TARGET_LIFT;
  }

  #groundAt(x, z) {
    const h = this.player?.terrain?.heightAt?.(x, z);
    return Number.isFinite(h) ? h : this.groundY;
  }

  // ------------------------------------------------------------- 3D builders
  #hueMaterial(hex) {
    let mat = this._hueMats.get(hex);
    if (!mat) {
      mat = new THREE.MeshBasicNodeMaterial({ color: `#${hex.replace('#', '')}`, toneMapped: false });
      this._hueMats.set(hex, mat);
    }
    return mat;
  }

  #buildOrb() {
    this.orb = new THREE.Mesh(new THREE.IcosahedronGeometry(0.15, 2), this.#hueMaterial('ffffff'));
    this.orb.visible = false;
    this.orb.castShadow = false;
    this.scene.add(this.orb);
  }

  #buildParticlePool() {
    this._pool = [];
    const geo = new THREE.IcosahedronGeometry(0.06, 0);
    for (let i = 0; i < 60; i++) {
      const mesh = new THREE.Mesh(geo, this.#hueMaterial('ffffff'));
      mesh.visible = false;
      mesh.castShadow = false;
      this.scene.add(mesh);
      this._pool.push({ mesh, vel: new THREE.Vector3(), life: 0, max: 1 });
    }
  }

  // The aim guide (arc + reticle) is gameplay-critical UI, so it draws ON TOP of
  // the world — depthTest off + a high renderOrder — and can't be hidden by
  // weather (snow flakes render at renderOrder 5) or occluded by terrain.
  #buildArc() {
    this._arcDots = [];
    const geo = new THREE.IcosahedronGeometry(0.05, 0);
    this._arcMat = new THREE.MeshBasicNodeMaterial({
      color: '#ffffff', toneMapped: false, transparent: true, opacity: 0.9,
      depthTest: false, depthWrite: false,
    });
    for (let i = 0; i < ARC_DOTS; i++) {
      const m = new THREE.Mesh(geo, this._arcMat);
      m.visible = false;
      m.castShadow = false;
      m.renderOrder = 20;
      this.scene.add(m);
      this._arcDots.push(m);
    }
  }

  #buildReticle() {
    this._reticleMat = new THREE.MeshBasicNodeMaterial({
      color: '#ffffff', toneMapped: false, transparent: true, opacity: 0.95,
      depthTest: false, depthWrite: false,
    });
    this.reticle = new THREE.Mesh(new THREE.RingGeometry(0.42, 0.6, 30), this._reticleMat);
    this.reticle.rotation.x = -Math.PI / 2;
    this.reticle.visible = false;
    this.reticle.renderOrder = 20;
    this.scene.add(this.reticle);
  }

  #buildTrail() {
    this._trail = [];
    const geo = new THREE.IcosahedronGeometry(0.1, 0);
    for (let i = 0; i < TRAIL_N; i++) {
      const m = new THREE.Mesh(geo, this.#hueMaterial('ffffff'));
      m.visible = false;
      m.castShadow = false;
      this.scene.add(m);
      this._trail.push({ mesh: m, life: 0, max: 0.3 });
    }
    this._trailWrite = 0;
  }

  #dropTrail() {
    const t = this._trail[this._trailWrite];
    t.mesh.position.copy(this.orb.position);
    t.mesh.material = this.orb.material;
    t.life = t.max;
    t.mesh.scale.setScalar(0.9);
    t.mesh.visible = true;
    this._trailWrite = (this._trailWrite + 1) % TRAIL_N;
  }

  #updateTrail(delta) {
    for (const t of this._trail) {
      if (t.life <= 0) continue;
      t.life -= delta;
      t.mesh.scale.setScalar(Math.max(0, t.life / t.max) * 0.9);
      if (t.life <= 0) t.mesh.visible = false;
    }
  }

  #buildBeacon() {
    this.beacon = new THREE.Group();
    // Bright, unlit, drawn on top (depthWrite off) so it reads as a clear marker.
    this._beaconMat = new THREE.MeshBasicNodeMaterial({
      color: '#ffe27a', toneMapped: false, transparent: true, opacity: 1.0, depthWrite: false,
    });
    // A proper downward arrow: a stem + a wide head, pointing at the pots.
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.7, 12), this._beaconMat);
    stem.position.y = 0.55;
    const head = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.6, 18), this._beaconMat);
    head.rotation.x = Math.PI; // point down
    head.position.y = 0.0;
    this._beaconArrow = new THREE.Group();
    this._beaconArrow.add(stem, head);
    this._beaconArrow.position.y = 2.2;
    const r = Math.max(1.4, this._potsRadius);
    const ring = new THREE.Mesh(new THREE.RingGeometry(r, r + 0.3, 48), this._beaconMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.06;
    this.beacon.add(this._beaconArrow, ring);
    this.beacon.position.copy(this._station);
    this.beacon.position.y = this.#groundAt(this._station.x, this._station.z);
    this.beacon.renderOrder = 10;
    this.scene.add(this.beacon);
    this._dayTint = new THREE.Color('#ffe27a');
    this._nightTint = new THREE.Color('#9af0ff');
  }

  // ---------------------------------------------------------------- input
  #onKeyDown(e) {
    if (!this._ready || document.body.classList.contains('booting')) return;
    if (this.mode === 'out') {
      // Consume the enter press so ActionPrompts / Interaction (which also
      // listen for KeyE) don't fire a prop gag at the same time.
      if (e.code === 'KeyE' && this._near) {
        e.preventDefault();
        e.stopImmediatePropagation();
        this.#enterGame();
      }
      return;
    }
    // In game mode — own these keys and stop them reaching the global handlers
    // (so M/` etc. can't open the map or debug overlays mid-game).
    if (e.code === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); this.#exitGame(); return; }
    if (e.code === 'KeyM' || e.code === 'Backquote') { e.preventDefault(); e.stopImmediatePropagation(); return; }
    const idx = DIGIT_TO_INDEX[e.code];
    if (idx !== undefined) { e.preventDefault(); e.stopImmediatePropagation(); this.#selectSwatch(idx, true); }
  }

  #selectSwatch(i, scoop = false) {
    if (i < 0 || i >= this.swatches.length) return;
    this.#applySwatch(i);
    if (scoop && this.mode !== 'out') this.audio?.playPaintScoop?.();
  }

  #applySwatch(i) {
    this._selected = i;
    const s = this.swatches[i];
    if (!s) return;
    this._hue.copy(s.hue);
    this.orb.material = this.#hueMaterial(s.hex);
    this._arcMat.color.copy(s.hue);
    this._reticleMat.color.copy(s.hue);
    this.hud.setActive(i);
  }

  get inGameMode() {
    return this.mode !== 'out';
  }

  // ---------------------------------------------------------- enter / exit
  #enterGame() {
    if (this.mode !== 'out') return;
    this.mode = 'entering';
    this.beacon.visible = false;
    this.hud.showPrompt(false);
    this.hud.enter();

    // Station the player at the fixed throwing spot, facing the field.
    this.player.placeAt?.(this.throwSpot.x, this.throwSpot.y, this.throwSpot.z, this.baseYaw);
    this.controller?.lock?.();
    this.playerCamera.locked = true;

    // Ease the camera from where it is to the raised wide shot.
    this._camEye.copy(this.playerCamera.camera.position);
    this._camTarget.copy(this.player.position);
    this._camTarget.y += HEAD_HEIGHT;
    gsap.killTweensOf([this._camEye, this._camTarget]);
    gsap.to(this._camEye, { x: this._wideEye.x, y: this._wideEye.y, z: this._wideEye.z, duration: ENTER_TWEEN, ease: 'power2.inOut' });
    gsap.to(this._camTarget, {
      x: this._wideTarget.x, y: this._wideTarget.y, z: this._wideTarget.z,
      duration: ENTER_TWEEN, ease: 'power2.inOut',
      onComplete: () => { if (this.mode === 'entering') this.mode = 'aiming'; },
    });

    this.charge = 0;
    this.hud.setCharge(0);
    if (this.swatches.length) this.#applySwatch(this._selected);
    this.audio?.playPaintScoop?.();
  }

  #exitGame() {
    if (this.mode === 'out' || this.mode === 'exiting') return;
    this.mode = 'exiting';
    this.audio?.stopPaintCharge?.();
    this.hud.exit();
    this.orb.visible = false;
    this.#hideAim();

    // Ease back to a normal third-person orbit pose, then hand control back.
    const ctrl = this.playerCamera.controls;
    const target = this._tmpA.copy(this.player.position);
    target.y += HEAD_HEIGHT;
    const dist = (ctrl.distance || 4) * (this.playerCamera._mobileZoom || 1);
    const az = ctrl.azimuthAngle;
    const polar = ctrl.polarAngle;
    const sp = Math.sin(polar);
    const eye = this._tmpB.set(
      target.x + dist * sp * Math.sin(az),
      target.y + dist * Math.cos(polar),
      target.z + dist * sp * Math.cos(az),
    );
    gsap.killTweensOf([this._camEye, this._camTarget]);
    gsap.to(this._camEye, { x: eye.x, y: eye.y, z: eye.z, duration: ENTER_TWEEN, ease: 'power2.inOut' });
    gsap.to(this._camTarget, {
      x: target.x, y: target.y, z: target.z, duration: ENTER_TWEEN, ease: 'power2.inOut',
      onComplete: () => {
        this.controller?.unlock?.();
        this.playerCamera.locked = false;
        this.playerCamera.resync?.();
        this.mode = 'out';
      },
    });
  }

  #driveCamera() {
    const cam = this.playerCamera.camera;
    cam.position.copy(this._camEye);
    cam.lookAt(this._camTarget);
    cam.updateMatrixWorld(); // so the aim raycast this frame uses the current pose
  }

  // --------------------------------------------------------------- per-frame
  update(delta, playerPos) {
    if (!this._ready || !playerPos) return;
    this._t += delta;

    if (this.cauldronPaint?.material?.emissiveIntensity !== undefined) {
      this.cauldronPaint.material.emissiveIntensity = 1.0 + Math.sin(this._t * 4) * 0.3;
    }
    this.#updateTrail(delta); // fades whether or not we're mid-throw

    if (this.mode === 'out') {
      this.#updateBeacon(delta, playerPos);
      this.#updateParticles(delta);
      this.#updateBlooms(delta);
      return;
    }

    // In game mode — we own the camera every frame.
    this.#driveCamera();

    if (this.mode === 'entering' || this.mode === 'exiting') {
      this.#updateParticles(delta);
      this.#updateBlooms(delta);
      return;
    }

    // aiming / charging / releasing / flying
    this.player.setFacing?.(this._aimYaw ?? this.baseYaw);
    this.#updateThrow(delta);
    this.#updateBlooms(delta);
    this.#updateParticles(delta);
  }

  #updateBeacon(delta, playerPos) {
    this.beacon.visible = true;
    // Bob straight up/down (no spin) so it reads as an arrow pointing at the spot.
    this._beaconArrow.position.y = 2.2 + Math.sin(this._t * 2.6) * 0.3;
    const pulse = 1 + Math.sin(this._t * 2.6) * 0.06;
    this._beaconArrow.scale.setScalar(pulse);
    const nf = THREE.MathUtils.clamp(this.timeOfDay?.nightFactor ?? 0, 0, 1);
    this._beaconMat.color.copy(this._dayTint).lerp(this._nightTint, nf);

    const d = Math.hypot(playerPos.x - this._station.x, playerPos.z - this._station.z);
    const near = !this._isTouch && d < ENTER_RADIUS;
    if (near !== this._near) {
      this._near = near;
      this.hud.showPrompt(near);
    }
  }

  // --------------------------------------------------- aim + charge + throw
  #updateThrow(delta) {
    const keyDown = this.controller?.keys?.has(CHARGE_KEY) === true;
    const pressed = keyDown && !this._keyWasDown;
    const released = !keyDown && this._keyWasDown;
    this._keyWasDown = keyDown;

    // Keep the orb (paint) loaded in the hand any time we're aiming/charging.
    if (this.mode === 'aiming' || this.mode === 'charging' || this.mode === 'releasing') {
      this.orb.visible = true;
      const hand = this.player.getHandWorldPosition?.(this._hand);
      if (hand) this.orb.position.copy(hand);
      else { this.orb.position.copy(this.throwSpot); this.orb.position.y += SHOULDER_Y; }
    }

    if (this.mode === 'aiming') {
      this.charge = 0;
      this.hud.setCharge(0);
      this.#updateAim();
      this.#showAim(true);
      if (pressed) {
        this.mode = 'charging';
        this._animated = this.player.playChargedAction?.('paintThrow', WINDUP_FRAC, THROW_RATE) === true;
        this.audio?.playPaintCharge?.();
      }
    } else if (this.mode === 'charging') {
      this.charge = Math.min(1, this.charge + delta / CHARGE_TIME);
      this.hud.setCharge(this.charge);
      this.#updateAim();
      this.#showAim(true);
      const s = 1 + this.charge * 0.4 + Math.sin(this._t * 18) * 0.06;
      this.orb.scale.setScalar(s);
      if (released) {
        this.player.releaseChargedAction?.();
        this.audio?.stopPaintCharge?.();
        // Snapshot the aim so the throw can't be re-steered mid-swing.
        this.flight.from.copy(this.orb.position);
        this.flight.to.copy(this._aim.landing);
        this.flight.apex = this._aim.apex;
        this.flight.statue = this._aim.statue;
        this.#showAim(false);
        if (this._animated) this.mode = 'releasing';
        else this.#launch();
      }
    } else if (this.mode === 'releasing') {
      if ((this.player.actionProgress?.('paintThrow') ?? 1) >= RELEASE_FRAC) {
        this.flight.from.copy(this.orb.position); // launch from the swung hand
        this.#launch();
      }
    } else if (this.mode === 'flying') {
      this.flight.t = Math.min(1, this.flight.t + delta / this.flight.dur);
      this.#arcPoint(this.flight.t, this.orb.position);
      this.orb.rotation.x += delta * 10;
      this.orb.rotation.y += delta * 8;
      this.#dropTrail();
      if (this.flight.t >= 1) this.#impact();
    }
  }

  #updateAim() {
    const cam = this.playerCamera.camera;

    // Cursor → NDC from the actual canvas rect (robust to any offset/scale).
    let ndcX = this._mouseNX * 2 - 1;
    let ndcY = -(this._mouseNY * 2 - 1);
    const rect = this.playerCamera.canvas?.getBoundingClientRect?.();
    if (rect && rect.width > 0 && rect.height > 0) {
      ndcX = ((this._mouseX - rect.left) / rect.width) * 2 - 1;
      ndcY = -(((this._mouseY - rect.top) / rect.height) * 2 - 1);
    }

    // DIRECTION is the player's (cursor → ground); DISTANCE is the player's
    // (charge). No homing — under/over-charge and you land short/long. A throw
    // only counts if its landing falls within HIT_RADIUS of a sculpture, so both
    // aim AND force have to be right.
    this._ray.setFromCamera(this._ndc.set(ndcX, ndcY), cam);
    const dir = this._tmpB;
    if (this._ray.ray.intersectPlane(this._groundPlane, this._tmpA)) {
      dir.set(this._tmpA.x - this.throwSpot.x, 0, this._tmpA.z - this.throwSpot.z);
      if (dir.lengthSq() < 1e-4) dir.copy(this._baseDir); else dir.normalize();
    } else {
      dir.copy(this._baseDir); // cursor above the horizon → straight ahead
    }
    this._aimYaw = Math.atan2(dir.x, dir.z);

    const dist = MIN_DIST + this.charge * (MAX_DIST - MIN_DIST);
    const ground = this._tmp.copy(this.throwSpot).addScaledVector(dir, dist);
    ground.y = this.#groundAt(ground.x, ground.z);

    // Does the landing fall on a sculpture? (This is where charge matters.)
    let target = null;
    let bestD = HIT_RADIUS;
    for (const st of this.statues) {
      const d = Math.hypot(st.center.x - ground.x, st.center.z - ground.z);
      if (d < bestD) { bestD = d; target = st; }
    }
    this._aim.statue = target;

    // Arc/reticle end: the sculpture body when the throw would hit one, else
    // the ground landing point. (The landing is NOT moved onto the sculpture —
    // this only reads which one a correct throw connects with.)
    const landing = this._aim.landing;
    if (target) landing.copy(target.center);
    else landing.copy(ground);

    const origin = this._aim.origin.copy(this.throwSpot);
    origin.y += SHOULDER_Y;
    const horiz = Math.hypot(landing.x - origin.x, landing.z - origin.z);
    // A fuller charge throws flatter (lower apex) so it reads as a harder throw.
    this._aim.apex = (ARC_APEX_BASE + horiz * ARC_APEX_PER_M) * (1 - this.charge * 0.35);

    // Dotted arc, tapering toward the landing.
    for (let i = 0; i < this._arcDots.length; i++) {
      const t = i / (this._arcDots.length - 1);
      const p = this._arcDots[i].position;
      p.copy(origin).lerp(landing, t);
      p.y = origin.y + (landing.y - origin.y) * t + this._aim.apex * 4 * t * (1 - t);
      this._arcDots[i].scale.setScalar(0.55 + (1 - t) * 0.7);
    }
    // Reticle: snaps to a sculpture base + brightens when the throw is dialled in
    // (right aim AND charge), else sits at the ground landing point.
    const rp = 1 + Math.sin(this._t * 6) * 0.08;
    if (target) {
      this.reticle.position.set(target.center.x, this.#groundAt(target.center.x, target.center.z) + 0.04, target.center.z);
      this.reticle.scale.setScalar(rp * 1.4);
      this._reticleMat.opacity = 1.0;
    } else {
      this.reticle.position.set(ground.x, ground.y + 0.04, ground.z);
      this.reticle.scale.setScalar(rp);
      this._reticleMat.opacity = 0.7;
    }
  }

  #showAim(visible) {
    for (const d of this._arcDots) d.visible = visible;
    this.reticle.visible = visible;
  }

  #hideAim() {
    this.#showAim(false);
  }

  #launch() {
    this.flight.t = 0;
    this.flight.dur = 0.3 + this.flight.from.distanceTo(this.flight.to) * 0.025;
    this.orb.visible = true;
    this.orb.scale.setScalar(1);
    this.mode = 'flying';
    this.audio?.playPaintThrow?.();
  }

  #arcPoint(t, out) {
    out.copy(this.flight.from).lerp(this.flight.to, t);
    out.y = this.flight.from.y + (this.flight.to.y - this.flight.from.y) * t
      + this.flight.apex * 4 * t * (1 - t);
    return out;
  }

  // ------------------------------------------------------------- payoff
  #impact() {
    const st = this.flight.statue;
    const at = this._tmp.copy(this.orb.position);
    this.orb.visible = false;

    this.#burst(at, this._hue);
    this.audio?.playSplat?.();
    this.playerCamera?.addImpulse?.(0.3);

    const newHue = this._hue.getHexString();
    if (st && st.hue !== newHue) {
      // Paint, OR re-paint with a new colour — bloom from its current colour to
      // the new one (grey for a first paint).
      const from = st.meshes[0]?.material?.color?.clone?.() || new THREE.Color(GREY_HEX);
      st.painted = true;
      st.hue = newHue;
      st.bloom = { t: 0, from };
      this.app?.triggerSlowMo?.(0.32, 1.2); // clean hit only
      this.audio?.playPaintBloom?.();
      this.#persist();
      const allPainted = this.statues.every((s) => s.painted);
      this.achievements?.onStatuePainted?.(allPainted);
    }

    // Reload: back to aiming with the orb re-appearing in the hand next frame.
    this.mode = this.mode === 'flying' ? 'aiming' : this.mode;
  }

  #paintApply(st, k, fromColor) {
    const target = new THREE.Color(`#${st.hue}`);
    for (const m of st.meshes) {
      m.material.color.copy(fromColor).lerp(target, k);
      if (m.material.emissive) {
        m.material.emissive.copy(target);
        m.material.emissiveIntensity = (1 - k) * 1.6;
      }
    }
  }

  #updateBlooms(delta) {
    for (const st of this.statues) {
      if (!st.bloom) continue;
      st.bloom.t = Math.min(1, st.bloom.t + delta / BLOOM_TIME);
      this.#paintApply(st, st.bloom.t, st.bloom.from);
      if (st.bloom.t >= 1) st.bloom = null;
    }
  }

  #burst(pos, hueColor) {
    const mat = this.#hueMaterial(hueColor.getHexString());
    let n = 0;
    for (const p of this._pool) {
      if (p.life > 0) continue;
      p.mesh.position.copy(pos);
      const a = Math.random() * Math.PI * 2;
      const up = 0.3 + Math.random() * 0.6;
      const sp = 1.4 + Math.random() * 2.8; // gentler than before → splatter, not shrapnel
      p.vel.set(Math.cos(a) * sp, up * sp, Math.sin(a) * sp);
      p.life = p.max = 0.6 + Math.random() * 0.5;
      p.mesh.material = mat;
      p.mesh.scale.setScalar(1);
      p.mesh.visible = true;
      if (++n >= 44) break;
    }
  }

  #updateParticles(delta) {
    for (const p of this._pool) {
      if (p.life <= 0) continue;
      p.life -= delta;
      p.vel.y -= 9.8 * delta;
      p.mesh.position.addScaledVector(p.vel, delta);
      if (p.mesh.position.y < this.groundY) {
        p.mesh.position.y = this.groundY;
        p.vel.y *= -0.35;
        p.vel.x *= 0.6;
        p.vel.z *= 0.6;
      }
      p.mesh.scale.setScalar(Math.max(0, p.life / p.max));
      if (p.life <= 0) p.mesh.visible = false;
    }
  }

  // --------------------------------------------------------- persistence
  #persist() {
    const data = {};
    for (const st of this.statues) if (st.painted) data[st.id] = st.hue;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      /* storage unavailable — painted state just won't survive reload */
    }
  }

  #restore() {
    let data = {};
    try {
      data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch {
      data = {};
    }
    for (const st of this.statues) {
      const hue = data[st.id];
      if (!hue) continue;
      st.painted = true;
      st.hue = hue;
      this.#paintApply(st, 1, new THREE.Color(GREY_HEX));
    }
  }

  dispose() {
    window.removeEventListener('pointermove', this._onPointerMove);
    window.removeEventListener('keydown', this._onKeyDown, { capture: true });
    this.hud?.dispose?.();
  }
}
