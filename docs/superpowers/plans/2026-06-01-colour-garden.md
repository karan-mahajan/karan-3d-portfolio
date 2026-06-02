# Colour Garden Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A pure-entertainment paint-throw toy — walk to a Blender-authored garden inside the world, pick a colour pot, charge + aim + throw a paint orb, and watch a grey sculpture bloom to that colour in slow-motion.

**Architecture:** The garden is authored as a real **v3 build section** (`14-fx-colour-garden.py`, FX family, like the lava pool) — placed in-world via `misc_common.find_spot`, built by the existing `15-section-run-all.py`, finalized by `15-finalize.py`. The export (`16-export-glb.py`) writes it as **its own GLB** (`static/world/colourGarden/colourGarden.glb`) under a new `manifest.interactive` key that `GlbV3World` does NOT iterate — so it's never folded into the shared-material prop-merge, which is what keeps statues individually paintable. The runtime module `ColourGarden.js` loads that GLB directly and owns everything interactive: per-statue materials, static colliders, nearest-pot colour picking, a charge/aim/throw state machine, a computed ballistic-arc projectile with aim-assist, and the paint payoff (colour-lerp + emissive flash + particle burst + brief global slow-mo + camera shake + splat sound). Painted state persists in localStorage.

**Tech Stack:** Three.js `three/webgpu`, Rapier3D, Howler, Blender 4.x `bpy` (misc_common helpers). No new dependencies.

**Build order:** Phase 1 Blender section → Phase 2 runtime (on a stand-in clip) → Phase 3 real animations. **All work lands in ONE final commit** (per `feedback_no_intermediate_commits`); stage only Colour Garden files, never the in-progress snow work.

**Source spec:** `docs/superpowers/specs/2026-06-01-colour-garden-paint-throw-design.md`

**Memories honoured:** never-invent-assets (all geometry Blender-authored), kept out of the shared-material merge + colour-only/no-displacement, Blender Python Console over Alt+P, animations-must-blend-smoothly, no name-prefixed JS variables, props on `height_at` with bbox colliders, single final commit.

---

## File Structure

| File | New/Mod | Responsibility |
|------|---------|----------------|
| `tools/blender/scripts/v3/karan/14-fx-colour-garden.py` | New | v3 FX section: authors garden in-world (cauldron + 6 pots + 6 grey sculptures), placed via find_spot. Built by the existing run-alls. |
| `tools/blender/scripts/v3/karan/16-export-glb.py` | Mod (done) | `_export_colour_garden()` → `static/world/colourGarden/colourGarden.glb` under `manifest.interactive`. |
| `static/world/colourGarden/colourGarden.glb` | New (generated) | Export output (committed). |
| `src/Portfolio/ColourGarden.js` | New | Load + place garden, materials, colliders, pot picking, charge/aim/throw, projectile, paint payoff, persistence. |
| `src/Audio/AudioManager.js` | Mod | Register + play a `splat` one-shot reusing `/sounds/splash-light.mp3`. |
| `src/App.js` | Mod | Construct/wire/tick ColourGarden; apply a global `timeScale` multiplier for slow-mo. |
| `src/Player/Character.js` | Mod (Phase 3) | Register `pickup`+`throw` clips; charge-hold pause; hand-attach hook. |
| `src/Player/Player.js` | Mod (Phase 3) | Locked context/charged action helpers. |

---

# PHASE 1 — Blender section (DONE — needs running)

The section script + export edit are already written:
- `tools/blender/scripts/v3/karan/14-fx-colour-garden.py`
- `tools/blender/scripts/v3/karan/16-export-glb.py` (`_export_colour_garden` + `manifest.interactive`)

### Task 1: Build + eyeball + export the garden

- [ ] **Step 1: Full rebuild (USER, in Blender Python Console)**

```
exec(open('/Users/mahajankaran/Documents/Projects/karan-portfolio/tools/blender/scripts/v3/karan/15-section-run-all.py').read())
```
This rebuilds the whole world from zero and includes the new `14-fx-colour-garden.py` automatically (the run-all globs `14-fx-*`), then runs finalize. Expected console line: `[14-fx-colour-garden] built colour garden: N objects at (x,z)`.

- [ ] **Step 2: USER eyeballs placement in the viewport**

Find the garden near the snapped `(-12, 12)` NW clearing: a dark cauldron + glowing paint disc, 6 glowing colour pots in a semicircle, 6 grey sculptures fanned out facing away from spawn. If the spot is wrong, change `ANCHOR` in `14-fx-colour-garden.py` and rerun Step 1. Don't proceed until happy.

- [ ] **Step 3: Export to GLB (headless or console)**

Headless:
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  tools/blender/world-v3-karan.blend \
  --python tools/blender/scripts/v3/karan/16-export-glb.py
```
Expected: a `colourGarden/colourGarden.glb ... obj` line in the size report and a `manifest.interactive` entry.

- [ ] **Step 4: Verify the output**

Run: `ls -la static/world/colourGarden/colourGarden.glb && python3 -c "import json;print(json.load(open('static/world/manifest.json')).get('interactive'))"`
Expected: GLB exists; manifest prints `{'system':'colourGarden','file':'colourGarden/colourGarden.glb','kind':'interactive','objects':...}`.

---

# PHASE 2 — Runtime code (on a stand-in animation)

### Task 2: Splat sound in AudioManager

**Files:** Modify `src/Audio/AudioManager.js`

- [ ] **Step 1: Register the sound** — in the `SOUND_FILES` map (~line 114), add:
```javascript
splat: { src: "/sounds/splash-light.mp3", loop: false, vol: VOL.splashLight },
```

- [ ] **Step 2: Public play method** — mirror the existing `playSplash` one-shot (~line 518):
```javascript
playSplat({ volume = 1.0 } = {}) {
  if (this.muted || this._focusLost) return;
  const h = this.howls.splat;
  if (!h || h.state() !== "loaded") return;
  const id = h.play();
  h.rate(1.15 + Math.random() * 0.2, id);
  h.volume(volume * VOL.splashLight, id);
}
```

- [ ] **Step 3: Verify** — `npm run dev`, no console errors on load.

---

### Task 3: Global slow-motion hook in App.js

**Files:** Modify `src/App.js` (constructor ~257; `#tick` ~1336–1361)

- [ ] **Step 1: State (constructor)**
```javascript
this.timeScale = 1;
this._timeScaleTarget = 1;
this._slowMoLeft = 0;
```

- [ ] **Step 2: Public trigger**
```javascript
triggerSlowMo(scale = 0.32, duration = 1.2) {
  this._timeScaleTarget = scale;
  this._slowMoLeft = duration;
}
```

- [ ] **Step 3: Apply in `#tick`** — right after `const frameDelta = Math.min(this.clock.getDelta(), 0.1);`:
```javascript
if (this._slowMoLeft > 0) {
  this._slowMoLeft -= frameDelta;
  if (this._slowMoLeft <= 0) this._timeScaleTarget = 1;
}
this.timeScale += (this._timeScaleTarget - this.timeScale) * Math.min(1, frameDelta * 6);
const scaledDelta = frameDelta * this.timeScale;
```
Feed `scaledDelta` to the physics accumulator + `player.update` + `world.update` + `colourGarden.update`; keep `playerCamera.update`, UI, and audio on raw `frameDelta`:
```javascript
this._fixedAccumulator = Math.min(this._fixedAccumulator + scaledDelta, fixedDelta * maxSteps);
```

- [ ] **Step 4: Verify** — `npm run dev`; with no trigger, `timeScale` stays 1, game feels identical.

---

### Task 4: ColourGarden — load, place, grey statues, colliders

**Files:** Create `src/Portfolio/ColourGarden.js`

- [ ] **Step 1: Load the exported GLB + register statues/pots**

The GLB carries world-space transforms (authored in Blender + finalize), so add the loaded scene at the origin — no terrain sampling needed.
```javascript
import * as THREE from 'three/webgpu';

const GARDEN_GLB = '/world/colourGarden/colourGarden.glb';  // static/ is the publicDir
const STORAGE_KEY = 'karan-colour-garden-v1';

// pot id -> exact hex (matches POTS in 14-fx-colour-garden.py)
const POT_HEX = {
  gardenPot_crimson: '#d81e38', gardenPot_amber: '#f3730f', gardenPot_gold: '#fad12b',
  gardenPot_emerald: '#33b34d', gardenPot_azure: '#2e8cf2', gardenPot_violet: '#8c4dd9',
};
const GREY_HEX = '#9aa0aa';

export class ColourGarden {
  constructor({ scene, physics, player, playerCamera, controller, audio, app, loader }) {
    this.scene = scene; this.physics = physics; this.player = player;
    this.playerCamera = playerCamera; this.controller = controller;
    this.audio = audio; this.app = app; this.loader = loader;

    this.group = null;
    this.statues = [];   // { id, obj, mat, center:Vec3, body, painted, hue, bloom }
    this.pots = [];      // { id, obj, hue, pos:Vec3 }
    this.cauldron = null; this.cauldronPaint = null; this.activePot = null;
    this._tmp = new THREE.Vector3();
    this._ready = false;
  }

  async load() {
    let gltf;
    try { gltf = await this.loader.loadGLTF(GARDEN_GLB); }
    catch (err) { console.warn('[ColourGarden] GLB load failed:', err); return; }

    this.group = gltf.scene;
    this.scene.add(this.group);
    this.group.updateWorldMatrix(true, true);

    // group statue meshes by id (gardenStatue_<id> or its joined name)
    const byId = new Map();
    this.group.traverse((o) => {
      if (!o.isMesh) return;
      o.castShadow = true; o.receiveShadow = true;
      if (o.name.startsWith('gardenStatue_')) {
        const id = o.name.replace(/^(gardenStatue_[a-z]+).*$/i, '$1');
        if (!byId.has(id)) byId.set(id, []);
        byId.get(id).push(o);
      } else if (o.name.startsWith('gardenPot_')) {
        this.#registerPot(o);
      } else if (o.name === 'gardenCauldron') this.cauldron = o;
      else if (o.name === 'gardenCauldronPaint') this.cauldronPaint = o;
    });
    for (const [id, meshes] of byId) this.#registerStatue(id, meshes);

    this.#restore();
    this._ready = true;
    console.log(`[ColourGarden] ready — ${this.statues.length} statues, ${this.pots.length} pots`);
  }

  #registerStatue(id, meshes) {
    // per-instance materials so painting never touches the shared system.
    for (const m of meshes) m.material = m.material.clone();
    const box = new THREE.Box3();
    for (const m of meshes) box.expandByObject(m);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    let body = null;
    if (this.physics?.ready) {
      body = this.physics.addStaticCuboid(
        center.x, center.y, center.z,
        Math.max(size.x / 2, 0.05), Math.max(size.y / 2, 0.05), Math.max(size.z / 2, 0.05),
      );
    }
    this.statues.push({ id, meshes, center, body, painted: false, hue: null, bloom: null });
  }

  #registerPot(mesh) {
    const pos = new THREE.Vector3(); mesh.getWorldPosition(pos);
    this.pots.push({ id: mesh.name, obj: mesh, hue: POT_HEX[mesh.name] || '#ffffff', pos });
  }

  update(delta, playerPos) { /* Tasks 5–7 */ }
}
```

- [ ] **Step 2: Construct from App.boot() (after player+physics+world ready)**
```javascript
const { ColourGarden } = await import('./Portfolio/ColourGarden.js');
this.colourGarden = new ColourGarden({
  scene: this.scene, physics: this.physics, player: this.player,
  playerCamera: this.playerCamera, controller: this.player.controller,
  audio: this.audio, app: this, loader: this.loader,
});
await this.colourGarden.load();
```
Add `this.colourGarden = null;` in the constructor.

- [ ] **Step 3: Verify** — `npm run dev`, walk to the garden. Sculptures sit on the ground, you collide with them but pass through pots. Console: `[ColourGarden] ready — 6 statues, 6 pots`.

---

### Task 5: Colour-pot picking + cauldron pulse

**Files:** Modify `src/Portfolio/ColourGarden.js`

- [ ] **Step 1: `update` body**
```javascript
update(delta, playerPos) {
  if (!this._ready) return;
  this._t = (this._t || 0) + delta;
  if (this.cauldronPaint?.material?.emissiveIntensity !== undefined)
    this.cauldronPaint.material.emissiveIntensity = 1.0 + Math.sin(this._t * 4) * 0.3;

  let best = null, bestD = 4.0;
  for (const pot of this.pots) {
    const d = playerPos.distanceTo(pot.pos);
    if (pot.obj.material.emissiveIntensity !== undefined) pot.obj.material.emissiveIntensity = 1.8;
    if (d < bestD) { bestD = d; best = pot; }
  }
  this.activePot = best;
  if (best?.obj.material.emissiveIntensity !== undefined) best.obj.material.emissiveIntensity = 3.5;

  this.#updatePrompt(playerPos);
  this.#updateThrow(delta, playerPos);   // Task 6
  this.#updateBlooms(delta);             // Task 7
  this.#updateParticles(delta);          // Task 7
}

#updatePrompt(playerPos) {
  const near = !!this.activePot;
  if (near !== this._promptShown) this._promptShown = near;
  // minimal DOM hint or ActionPrompts integration (see note)
}
```
> **Implementation note (concrete):** inspect `ActionPrompts.add(trigger)` (`src/Portfolio/ActionPrompts.js`) — either register a trigger at the cauldron world pos labelled `Hold F to paint`, tinting toward `this.activePot.hue`, or add a small dedicated DOM hint matching the HUD style.

- [ ] **Step 2: Verify** — nearest pot brightens as you move between pots; the hint shows within ~4m of the cauldron.

---

### Task 6: Charge / aim / throw + projectile + aim-assist

**Files:** Modify `src/Portfolio/ColourGarden.js`

- [ ] **Step 1: Orb + flight state (constructor)**
```javascript
this.state = 'idle'; this.charge = 0; this._keyWasDown = false; this.CHARGE_KEY = 'KeyF';
const Mat = THREE.MeshStandardNodeMaterial || THREE.MeshStandardMaterial;
this.orb = new THREE.Mesh(new THREE.IcosahedronGeometry(0.16, 2),
  new Mat({ color: '#ffffff', emissive: '#ffffff', emissiveIntensity: 1.2 }));
this.orb.visible = false; this.scene.add(this.orb);
this.orbLight = new THREE.PointLight('#ffffff', 0, 5); this.scene.add(this.orbLight);
this.flight = { from: new THREE.Vector3(), to: new THREE.Vector3(), apex: 3, t: 0, dur: 1, statue: null, hue: '#fff' };
```

- [ ] **Step 2: State machine + launch + arc**
```javascript
#updateThrow(delta, playerPos) {
  const keyDown = this.controller?.keys?.has(this.CHARGE_KEY) === true;
  const pressed = keyDown && !this._keyWasDown;
  const released = !keyDown && this._keyWasDown;
  this._keyWasDown = keyDown;

  if (this.state === 'idle' && pressed && this.activePot) {
    this.state = 'charging'; this.charge = 0;
    this.flight.hue = this.activePot.hue;
    this.orb.material.color.set(this.flight.hue);
    if (this.orb.material.emissive) this.orb.material.emissive.set(this.flight.hue);
    this.orbLight.color.set(this.flight.hue); this.orb.visible = true;
    this.player.playContextAction?.('throw');   // Phase 2 stand-in (Task 9 note)
  }

  if (this.state === 'charging') {
    this.charge = Math.min(1, this.charge + delta / 1.0);
    this.orb.position.copy(playerPos); this.orb.position.y += 1.5;
    this.orbLight.position.copy(this.orb.position); this.orbLight.intensity = 1.4;
    if (released) this.#launch(playerPos);
  } else if (this.state === 'flying') {
    this.flight.t = Math.min(1, this.flight.t + delta / this.flight.dur);
    this.#arcPoint(this.flight.t, this.orb.position);
    this.orb.rotation.x += delta * 10; this.orb.rotation.y += delta * 8;
    this.orbLight.position.copy(this.orb.position);
    if (this.flight.t >= 1) this.#impact();   // Task 7
  }
}

#launch(playerPos) {
  const fwd = this.playerCamera.getGroundForward(new THREE.Vector3());
  const d = new THREE.Vector3(); this.playerCamera.camera.getWorldDirection(d);
  const dist = 5 + this.charge * 10;
  const apex = 2.0 + THREE.MathUtils.clamp(d.y * 0.5 + 0.5, 0, 1) * 5.0;
  const from = this._tmp.copy(playerPos); from.y += 1.5;
  const to = playerPos.clone().addScaledVector(fwd, dist); to.y = playerPos.y;

  let best = null, bestAng = 0.22;
  for (const st of this.statues) {
    if (st.painted) continue;
    const v = st.center.clone().sub(playerPos); v.y = 0; v.normalize();
    const ang = fwd.angleTo(v);
    if (ang < bestAng) { bestAng = ang; best = st; }
  }
  if (best) to.copy(best.center);

  this.flight.from.copy(from); this.flight.to.copy(to); this.flight.apex = apex;
  this.flight.statue = best; this.flight.t = 0;
  this.flight.dur = 0.45 + from.distanceTo(to) * 0.04;
  this.state = 'flying';
}

#arcPoint(t, out) {
  out.copy(this.flight.from).lerp(this.flight.to, t);
  out.y = this.flight.from.y + (this.flight.to.y - this.flight.from.y) * t + this.flight.apex * 4 * t * (1 - t);
  return out;
}
```

- [ ] **Step 3: Verify** — hold F by a pot (orb appears in the pot colour, charges), release → parabola; aiming near a statue snaps the landing. (Paint lands in Task 7.)

---

### Task 7: Paint payoff — bloom, particles, slow-mo, shake, sound, persistence

**Files:** Modify `src/Portfolio/ColourGarden.js`

- [ ] **Step 1: Particle pool (constructor)**
```javascript
this._pool = [];
const pgeo = new THREE.IcosahedronGeometry(0.08, 0);
const PMat = THREE.MeshStandardNodeMaterial || THREE.MeshStandardMaterial;
for (let i = 0; i < 60; i++) {
  const m = new THREE.Mesh(pgeo, new PMat({ color: '#fff', emissive: '#fff', emissiveIntensity: 0.5 }));
  m.visible = false; this.scene.add(m);
  this._pool.push({ mesh: m, vel: new THREE.Vector3(), life: 0, max: 1 });
}
```

- [ ] **Step 2: Impact + paint + burst + payoff**
```javascript
#impact() {
  const st = this.flight.statue, hue = this.flight.hue, at = this.orb.position.clone();
  this.orb.visible = false; this.orbLight.intensity = 0; this.state = 'idle';
  this.#burst(at, hue);
  this.audio?.playSplat?.();
  this.playerCamera?.addImpulse?.(0.3);
  if (st && !st.painted) {
    st.painted = true; st.hue = hue; st.bloom = { t: 0 };
    this.app?.triggerSlowMo?.(0.32, 1.2);   // clean hit only
    this.#persist();
  }
}

#paintApply(st, k) {
  const grey = new THREE.Color(GREY_HEX), target = new THREE.Color(st.hue);
  for (const m of st.meshes) {
    m.material.color.copy(grey).lerp(target, k);
    if (m.material.emissive) { m.material.emissive.copy(target); m.material.emissiveIntensity = (1 - k) * 1.6; }
  }
}

#updateBlooms(delta) {
  for (const st of this.statues) {
    if (!st.bloom) continue;
    st.bloom.t = Math.min(1, st.bloom.t + delta / 0.6);
    this.#paintApply(st, st.bloom.t);
    if (st.bloom.t >= 1) st.bloom = null;
  }
}

#burst(pos, hue) {
  let n = 0;
  for (const p of this._pool) {
    if (p.life > 0) continue;
    p.mesh.position.copy(pos);
    const a = Math.random() * Math.PI * 2, up = 0.4 + Math.random() * 0.9, sp = 2 + Math.random() * 4;
    p.vel.set(Math.cos(a) * sp, up * sp, Math.sin(a) * sp);
    p.life = p.max = 0.7 + Math.random() * 0.5;
    p.mesh.material.color.set(hue);
    if (p.mesh.material.emissive) p.mesh.material.emissive.set(hue);
    p.mesh.scale.setScalar(1); p.mesh.visible = true;
    if (++n >= 36) break;
  }
}

#updateParticles(delta) {
  for (const p of this._pool) {
    if (p.life <= 0) continue;
    p.life -= delta; p.vel.y -= 9.8 * delta;
    p.mesh.position.addScaledVector(p.vel, delta);
    if (p.mesh.position.y < 0.05) { p.mesh.position.y = 0.05; p.vel.y *= -0.35; p.vel.x *= 0.6; p.vel.z *= 0.6; }
    p.mesh.scale.setScalar(Math.max(0, p.life / p.max));
    if (p.life <= 0) p.mesh.visible = false;
  }
}
```
> **Note:** particle ground-plane uses `y < 0.05`; if the garden sits well above y=0, pass the garden ground height in instead. Resolve by logging a statue `center.y` once.

- [ ] **Step 3: Persistence**
```javascript
#persist() {
  const data = {};
  for (const st of this.statues) if (st.painted) data[st.id] = st.hue;
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch {}
}
#restore() {
  let data = {};
  try { data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch {}
  for (const st of this.statues) {
    const hue = data[st.id];
    if (!hue) continue;
    st.painted = true; st.hue = hue; this.#paintApply(st, 1);
  }
}
```

- [ ] **Step 4: Verify full loop** — pick a pot, throw at a grey statue: it blooms grey→colour over ~0.6s, a coloured droplet burst sprays + falls, brief slow-mo, small shake, splat sound. Paint several colours. Reload → painted statues stay coloured. Missing a statue → burst+sound but no slow-mo, nothing painted.

---

### Task 8: Final wiring (App.js)

**Files:** Modify `src/App.js`

- [ ] **Step 1: Tick it with the scaled delta** — near `this.world.update(...)`:
```javascript
this.colourGarden?.update(scaledDelta, this.player.position);
```
- [ ] **Step 2: Verify** — full loop works through the real tick; slow-mo slows orb/particles, not camera/HUD.

---

# PHASE 3 — Real animations

### Task 9: Pickup + throw clips, charge-hold, hand-attach

**Files:** Modify `src/Player/Character.js`, `src/Player/Player.js`, `src/Portfolio/ColourGarden.js`

- [ ] **Step 1: USER sources clips** — Mixamo "Picking Up" + "Throwing" → `static/models/character/animations/picking-up.glb`, `.../throwing.glb`.

- [ ] **Step 2: Register deferred clips** — in `Character.js` `DEFERRED_MIXAMO_CLIPS` (~line 46):
```javascript
{ action: 'pickup', url: '/models/character/animations/picking-up.glb' },
{ action: 'throw',  url: '/models/character/animations/throwing.glb' },
```

- [ ] **Step 3: Charge-hold helper (Character.js)**
```javascript
playCharged(name, holdTime, { fade = 0.2, then = 'idle' } = {}) {
  this.play(name, { fade, once: true, then });
  const action = this.actions[name];
  if (action) this._chargeHold = { action, holdTime };
}
releaseHold() { if (this._chargeHold) { this._chargeHold.action.paused = false; this._chargeHold = null; } }
```
In `update(delta)` before `this.mixer.update(delta)`:
```javascript
if (this._chargeHold) {
  const a = this._chargeHold.action;
  if (a.time >= this._chargeHold.holdTime) { a.time = this._chargeHold.holdTime; a.paused = true; }
}
```

- [ ] **Step 4: Hand-attach hook (Character.js)** — after the bone traversal in `load()`:
```javascript
this.rightHand = null;
this.mesh.traverse((c) => { if (c.isBone && /RightHand$/i.test(c.name) && !this.rightHand) this.rightHand = c; });
```
```javascript
attachToHand(obj) { if (this.rightHand) this.rightHand.add(obj); }
detachToScene(obj, scene) {
  if (!obj.parent) return;
  obj.updateWorldMatrix(true, false);
  const p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3();
  obj.matrixWorld.decompose(p, q, s);
  scene.add(obj); obj.position.copy(p); obj.quaternion.copy(q); obj.scale.copy(s);
}
```
> **Resolve at implementation:** if `/RightHand$/` matches nothing, log all bone names once and pick the throwing-arm wrist bone (Avaturn uses bare Mixamo names → `RightHand` expected).

- [ ] **Step 5: Locked context/charged actions (Player.js)** — mirror how push sets/clears `_actionLocked`:
```javascript
playContextAction(name, opts = {}) { this._actionLocked = true; this._state = name; this.character.play(name, { once: true, then: 'idle', ...opts }); }
playChargedAction(name, holdTime) { this._actionLocked = true; this._state = name; this.character.playCharged(name, holdTime, { then: 'idle' }); }
releaseChargedAction() { this.character.releaseHold(); }
```
Ensure `_actionLocked` is cleared when the one-shot finishes (follow the existing push unlock path).

- [ ] **Step 6: Swap the stand-in in ColourGarden** — on charge start: `playContextAction('pickup')` + `character.attachToHand(this.orb)`; when pickup finishes, `playChargedAction('throw', WINDUP_TIME)`; on release: `releaseChargedAction()` + `character.detachToScene(this.orb, this.scene)` + `#launch`. Set `WINDUP_TIME` from `this.actions.throw.getClip().duration` (~40%, tunable).

- [ ] **Step 7: Verify** — reach/pickup → orb in hand → arm winds up + holds while charging → release swings through, orb leaves on the forward swing → flies → eases to idle. One continuous blended sequence, no pose-popping.

---

# Final: single commit

### Task 10: Stage only Colour Garden files, commit once

- [ ] **Step 1: Confirm snow work untouched** — `git status`; do NOT stage `Snow.js`/`SnowState.js`/`WeatherDirector.js`/snow sounds.

- [ ] **Step 2: Stage only the feature files**
```bash
git add tools/blender/scripts/v3/karan/14-fx-colour-garden.py \
        tools/blender/scripts/v3/karan/16-export-glb.py \
        static/world/colourGarden/colourGarden.glb \
        static/world/manifest.json \
        src/Portfolio/ColourGarden.js \
        src/Audio/AudioManager.js \
        src/App.js \
        src/Player/Character.js \
        src/Player/Player.js \
        docs/superpowers/specs/2026-06-01-colour-garden-paint-throw-design.md \
        docs/superpowers/plans/2026-06-01-colour-garden.md
```

- [ ] **Step 3: Verify staged set** — `git status`; confirm NO snow files staged.

- [ ] **Step 4: Commit (no Claude co-author trailer — `feedback_no_claude_coauthor`)**
```bash
git commit -m "feat(garden): colour-throw paint mechanic (v3 garden section + runtime)"
```

---

## Self-Review

**Spec coverage:** §0 build order → Phases 1/2/3. §2 loop → Tasks 5/6/7. §3 world+pots+placement + §3a v3-section → Task 1 (+ done section script & export edit). §4 anim → Task 9. §5 aim/charge/throw → Task 6. §6 payoff → Tasks 3/7. §7 persistence → Task 7.3. §8 material constraint → `manifest.interactive` (out of merge) + Task 4 per-instance clone. §9 files → all. ✓

**Intentional v1 simplifications (told user):** splat decal folded into the particle burst; the TSL grow-from-impact mask is a colour-lerp + emissive flash (reliable, colour-only — honours no-displacement). Both are follow-up polish.

**Placeholder scan:** the "Implementation note"/"Resolve at implementation" items (prompt API, right-hand bone, push unlock, wind-up time, particle ground height) are concrete instructions with the resolution method, not vague TODOs. ✓

**Name consistency:** Blender object names `gardenStatue_<id>` / `gardenPot_<hue>` / `gardenCauldron` / `gardenCauldronPaint` match `POT_HEX` keys + the traverse prefixes in Task 4; load path `/world/colourGarden/colourGarden.glb` matches the export `rel`; `triggerSlowMo`/`timeScale`/`scaledDelta` and the Player/Character helper names are consistent across tasks. ✓
