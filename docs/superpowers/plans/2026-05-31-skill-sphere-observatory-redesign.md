# Skills Sphere "Observatory" Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **PROJECT CONVENTIONS THAT OVERRIDE SKILL DEFAULTS:**
> - **No automated test framework / no verify probes.** This is a vanilla
>   Three.js + Rapier app verified by the user in a running dev build
>   (`npm run dev`). Each task ends with a *manual* observation, not an
>   automated assertion. Do NOT write Playwright probes or screenshot loops.
> - **One bundled commit at the very end** (Task 10). Do NOT commit per task.
> - **No Claude co-author trailer** in the commit.
> - Match existing code style: ES modules, `class`, `#private` fields, WHY-only
>   comments, JSDoc on methods. No TypeScript.

**Goal:** Turn the frozen-ringed Skills sphere into a living "Observatory" — differential-spinning rings that carry the skill cards as one mechanism, with day/night-adaptive warm gold+teal styling, a free look-around interior camera, depth-faded and always-upright accessible cards.

**Architecture:** All runtime logic stays in `src/Portfolio/SkillSphere.js` (public surface `near`/`enter`/`exit`/`update` unchanged); styling in `src/style.css`. One new constructor arg (`timeOfDay`) wired from `App.js`. Ring objects are fetched from the loaded GLB scene by name (`scene.getObjectByName`, the pattern `#collectCoreVisuals` already uses) and rotated about the sphere center each frame.

**Tech Stack:** three@0.184 (`three/webgpu` build), gsap@3, camera-controls@3, canvas 2D for card textures.

---

## File structure

| File | Responsibility | Change |
|------|----------------|--------|
| `src/Portfolio/SkillSphere.js` | All sphere runtime behaviour | Modify (most tasks) |
| `src/App.js` | Module wiring | Modify (1 line — Task 1) |
| `src/style.css` | Hint styling | Modify (Task 9) |

No new files. `SkillSphere.js` is already the single home for this feature and
stays focused; we add private helpers rather than splitting.

---

## Task 1: Wire `timeOfDay` into SkillSphere

**Files:**
- Modify: `src/App.js` (the `new SkillSphere({ ... })` call, ~line 474)
- Modify: `src/Portfolio/SkillSphere.js:44-60` (constructor params + assignment)

- [ ] **Step 1: Pass `timeOfDay` from App.js**

In `src/App.js`, find the `this.skillSphere = new SkillSphere({ ... })` block.
`this.timeOfDay` is already constructed earlier (App.js ~line 150). Add one line
to the options object (alongside `audio` / `achievements`):

```js
    this.skillSphere = new SkillSphere({
      scene: this.scene,
      camera: this.camera,
      player: this.player,
      playerCamera: this.playerCamera,
      controller: this.player.controller,
      refs: this.world.glb.refs,
      audio: this.audio,
      achievements: this.achievements,
      timeOfDay: this.timeOfDay,
    });
```

- [ ] **Step 2: Accept and store it in the constructor**

In `src/Portfolio/SkillSphere.js`, extend the destructured params and store it:

```js
  constructor({
    scene,
    camera,
    player,
    playerCamera,
    controller,
    refs,
    audio = null,
    achievements = null,
    timeOfDay = null,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.audio = audio;
    this.achievements = achievements;
    this.timeOfDay = timeOfDay;
```

- [ ] **Step 3: Manual check**

Run `npm run dev`, open the app, walk to the Skills sphere, press E. Behaviour
is unchanged (no visible difference yet). Confirm **no console errors** — this
proves the wiring didn't break construction.

---

## Task 2: Collect the ring/core objects

**Files:**
- Modify: `src/Portfolio/SkillSphere.js:464-474` (replace `#collectCoreVisuals`)
- Modify: `src/Portfolio/SkillSphere.js:94-99` (constructor call site)

- [ ] **Step 1: Add module-level constants near the top (after the `tmp*` declarations, ~line 35)**

```js
const WORLD_UP = new THREE.Vector3(0, 1, 0);

// Differential spin rates (rad/s) and direction for each ring/core part, keyed
// by Blender object name. Different speeds + directions = orrery feel.
const STRUCTURE_SPIN = [
  { name: 'skillSphere_orbit_ring_equator', rate: 0.18, dir: 1 },
  { name: 'skillSphere_orbit_ring_meridian_a', rate: 0.26, dir: -1 },
  { name: 'skillSphere_orbit_ring_meridian_b', rate: 0.22, dir: -1 },
  { name: 'skillSphere_orbit_ring_meridian_c', rate: 0.30, dir: 1 },
  { name: 'skillSphere_orbit_ring_meridian_d', rate: 0.24, dir: -1 },
  { name: 'skillSphere_orbit_lat_north_mid', rate: 0.14, dir: -1 },
  { name: 'skillSphere_orbit_lat_south_mid', rate: 0.14, dir: 1 },
  { name: 'skillSphere_orbit_lat_north_high', rate: 0.20, dir: 1 },
  { name: 'skillSphere_orbit_lat_south_high', rate: 0.20, dir: -1 },
  { name: 'skillSphere_orb_shell', rate: 0.05, dir: 1 },
  { name: 'skillSphere_energy_column', rate: 0.10, dir: 1 },
  { name: 'skillSphere_core_inner', rate: 0.12, dir: 1 },
  { name: 'skillSphere_core_halo', rate: 0.03, dir: -1 },
];
```

- [ ] **Step 2: Replace `#collectCoreVisuals` with `#collectStructure`**

This collects every ring/core part once, captures each material's base
emissive intensity (for day/night later), and keeps the `coreVisuals` subset
(inner/halo/column) only for the dimming behaviour. Rotation pivots about the
object's own origin via `rotateOnWorldAxis`, which preserves each ring's Blender
tilt while spinning it about the sphere center (the object origin sits at center).

```js
  #collectStructure() {
    this.structure = [];
    this.ringMaterials = [];
    for (const spec of STRUCTURE_SPIN) {
      const obj = this.scene.getObjectByName(spec.name);
      if (!obj) continue;
      this.structure.push({ obj, rate: spec.rate, dir: spec.dir });
      obj.traverse((node) => {
        if (!node.isMesh || !node.material) return;
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        for (const mat of mats) {
          if (mat.emissiveIntensity == null) continue;
          this.ringMaterials.push({ mat, base: mat.emissiveIntensity });
        }
      });
    }
    // Subset kept visible-but-dimmed inside (they sit at the camera origin).
    const coreNames = ['skillSphere_core_inner', 'skillSphere_core_halo', 'skillSphere_energy_column'];
    this.coreVisuals = coreNames
      .map((n) => this.scene.getObjectByName(n))
      .filter(Boolean);
  }
```

- [ ] **Step 3: Call it from the constructor**

Replace the existing `this.#collectCoreVisuals();` line (~line 98) with:

```js
      this.#collectStructure();
```

Delete the now-unused `#collectCoreVisuals` method (old lines 464-474).

- [ ] **Step 4: Manual check**

Reload dev. Press E into the sphere — still works, no errors. (Rings don't
animate yet.) In the browser console run `window` checks only if convenient;
otherwise just confirm no errors and the rings are still visible. If any ring
name logged as missing later, names are verified against
`tools/blender/scripts/v3/karan/04-markers-skills-sphere-base.py`.

---

## Task 3: Animate the structure + couple the card orbit

**Files:**
- Modify: `src/Portfolio/SkillSphere.js:231-255` (`update`)
- Add: `#animateStructure` private method
- Modify: `src/Portfolio/SkillSphere.js:133` (remove core-hide-on-enter)
- Modify: `src/Portfolio/SkillSphere.js:476-478` (`#setCoreVisible` → dim instead of hide)

- [ ] **Step 1: Add a shared base-rate constant**

Near the other module constants (top of file), add:

```js
// Card orbit shares the equator ring's base rate so cards read as carried by
// the structure, not animated independently. Scaled down inside for calm browse.
const CARD_ORBIT_RATE = 0.18;
```

- [ ] **Step 2: Add `#animateStructure`**

```js
  #animateStructure(delta) {
    if (!this.structure) return;
    const scale = this.active ? 0.45 : 1; // calmer while the player is inside
    for (let i = 0; i < this.structure.length; i++) {
      const part = this.structure[i];
      part.obj.rotateOnWorldAxis(WORLD_UP, delta * part.rate * part.dir * scale);
    }
  }
```

- [ ] **Step 3: Rewrite `update` to drive the structure and couple the cards**

Replace the body of `update(delta)` (lines 231-255). The card-orbit speed now
derives from `CARD_ORBIT_RATE` (matching the equator) instead of the old
`0.36`/`0.16` literals. Billboarding (label loop) and title handling are touched
again in Task 4/6 — for now keep the existing per-label billboard/opacity code:

```js
  update(delta) {
    if (!this.ready) return;
    this.elapsed += delta;
    if (this.active && this.interactive) this.#applyInsideCamera(delta);

    this.#animateStructure(delta);

    const orbitScale = this.active ? 0.9 : 2.0; // cards drift a touch faster than rings outside
    this.labelRoot.rotation.y += delta * CARD_ORBIT_RATE * orbitScale;
    this.labelRoot.rotation.x = Math.sin(this.elapsed * 0.28) * 0.055;

    const opacityLift = this.active ? 0.22 : this._near ? 0.12 : 0;
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      this.camera.getWorldQuaternion(tmpCameraQuat);
      this.labelRoot.getWorldQuaternion(tmpParentQuat).invert();
      label.quaternion.copy(tmpParentQuat.multiply(tmpCameraQuat));
      const mat = label.material;
      const base = label.userData.baseOpacity;
      mat.opacity += ((base + opacityLift) - mat.opacity) * Math.min(1, delta * 5);
    }
    if (this.title) {
      this.camera.getWorldQuaternion(tmpCameraQuat);
      this.root.getWorldQuaternion(tmpRootQuat).invert();
      this.title.quaternion.copy(tmpRootQuat.multiply(tmpCameraQuat));
      this.title.position.y = this.radius + 1.1 + Math.sin(this.elapsed * 1.3) * 0.08;
    }
  }
```

- [ ] **Step 4: Keep the rings visible inside — change hide to dim**

In `enter()` (line 133) the call `this.#setCoreVisible(false)` currently hides
the core. Change the intent from hide to dim. Replace `#setCoreVisible`
(lines 476-478) with:

```js
  #setCoreVisible(visible) {
    // The core/column sit at the camera origin inside the sphere. Don't hide the
    // moving structure — fade the center pieces so they don't occlude the view.
    const opacity = visible ? 1 : 0.25;
    for (const obj of this.coreVisuals) {
      obj.traverse((node) => {
        if (!node.isMesh || !node.material) return;
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        for (const mat of mats) {
          mat.transparent = true;
          if (mat.userData._baseOpacity == null) mat.userData._baseOpacity = mat.opacity ?? 1;
          gsap.to(mat, { opacity: visible ? mat.userData._baseOpacity : opacity, duration: 0.6 });
        }
      });
    }
  }
```

`enter()` keeps calling `this.#setCoreVisible(false)` (now = fade) and `exit()`
keeps calling `this.#setCoreVisible(true)` (now = restore). No call-site change.

- [ ] **Step 5: Manual check**

Reload dev. From the shore the rings should now **visibly spin at different
speeds** and the cards orbit with them as one mechanism. Press E: inside, the
motion eases to a calm pace and the core/column are dimmed (not gone). ESC
restores. Confirm no errors.

---

## Task 4: Upright, never-inverted billboarding

**Files:**
- Modify: `src/Portfolio/SkillSphere.js` `update` (label loop + title block from Task 3)
- Add: `#faceCamera` private helper

- [ ] **Step 1: Add temps near the other `tmp*` declarations (top of file)**

```js
const tmpLabelPos = new THREE.Vector3();
const tmpToCam = new THREE.Vector3();
const tmpRight = new THREE.Vector3();
const tmpUp = new THREE.Vector3();
const tmpBasis = new THREE.Matrix4();
const tmpWorldQuat = new THREE.Quaternion();
```

- [ ] **Step 2: Add `#faceCamera` — yaw/pitch toward camera, zero roll, world-up locked**

Builds an orthonormal basis whose +Z faces the camera and whose up is world-up
(projected), so text is always horizontal and never mirrored, from any angle.
Degenerate case (card directly above/below camera, `tmpToCam` ~parallel to
world-up) falls back to a fixed right axis. Converts the world quaternion into
the label's local space (it's a child of the spinning `labelRoot`).

```js
  /** Orient `mesh` to face the camera upright (no roll, no mirror) from any angle. */
  #faceCamera(mesh, parentInvQuat) {
    mesh.getWorldPosition(tmpLabelPos);
    tmpToCam.copy(this.camera.position).sub(tmpLabelPos);
    if (tmpToCam.lengthSq() < 1e-6) return;
    tmpToCam.normalize();

    tmpRight.crossVectors(WORLD_UP, tmpToCam);
    if (tmpRight.lengthSq() < 1e-4) tmpRight.set(1, 0, 0); // looking straight up/down
    tmpRight.normalize();
    tmpUp.crossVectors(tmpToCam, tmpRight).normalize();

    // Columns: right (x), up (y), toCam (z) => plane faces camera, +Y stays up.
    tmpBasis.makeBasis(tmpRight, tmpUp, tmpToCam);
    tmpWorldQuat.setFromRotationMatrix(tmpBasis);
    mesh.quaternion.copy(parentInvQuat).multiply(tmpWorldQuat);
  }
```

- [ ] **Step 3: Use it in `update` for labels and title**

Replace the label-billboard line and the title-billboard line from Task 3's
`update` with `#faceCamera` calls. The label loop becomes:

```js
    this.labelRoot.getWorldQuaternion(tmpParentQuat).invert();
    const opacityLift = this.active ? 0.22 : this._near ? 0.12 : 0;
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      this.#faceCamera(label, tmpParentQuat);
      const mat = label.material;
      const base = label.userData.baseOpacity;
      mat.opacity += ((base + opacityLift) - mat.opacity) * Math.min(1, delta * 5);
    }
    if (this.title) {
      this.root.getWorldQuaternion(tmpRootQuat).invert();
      this.#faceCamera(this.title, tmpRootQuat);
      this.title.position.y = this.radius + 1.1 + Math.sin(this.elapsed * 1.3) * 0.08;
    }
```

(The per-label `this.camera.getWorldQuaternion(...)` / `this.labelRoot.getWorldQuaternion(...)`
calls from Task 3 are now removed — `#faceCamera` does the orientation and we
compute `tmpParentQuat` once before the loop.)

- [ ] **Step 4: Manual check**

Reload dev. Watch a card orbit to the **back** of the sphere and one at the
**top/bottom**: text must stay upright and read left-to-right (never mirrored,
never upside-down), both from the shore and from inside. Orbit the inside camera
fully around — every card stays readable.

---

## Task 5: Free the interior camera (dolly, pitch, idle drift)

**Files:**
- Modify: `src/Portfolio/SkillSphere.js:480-498` (`#setInsideControlsFromDirection`)
- Modify: `src/Portfolio/SkillSphere.js:500-509` (`#restoreInsideControlLimits`)
- Modify: `src/Portfolio/SkillSphere.js:536-549` (`#applyInsideCamera`)

- [ ] **Step 1: Widen the control limits on enter**

Replace `#setInsideControlsFromDirection` (lines 480-498). Allow a dolly range
and fuller pitch instead of pinning distance to 0.1:

```js
  #setInsideControlsFromDirection(direction) {
    const controls = this.playerCamera?.controls;
    if (!controls) return;
    if (!this._savedControlLimits) {
      this._savedControlLimits = {
        minPolarAngle: controls.minPolarAngle,
        maxPolarAngle: controls.maxPolarAngle,
        minDistance: controls.minDistance,
        maxDistance: controls.maxDistance,
      };
    }
    controls.minPolarAngle = Math.PI * 0.02;
    controls.maxPolarAngle = Math.PI * 0.98;
    controls.minDistance = 0.1;
    controls.maxDistance = 2.5; // pull back toward the shell for parallax + zoom
    controls.azimuthAngle = Math.atan2(direction.x, direction.z);
    controls.polarAngle = Math.PI * 0.5;
    controls.distance = 0.1;
    this._idleDriftClock = 0;
    this._lastAzimuth = controls.azimuthAngle;
  }
```

- [ ] **Step 2: Restore cleanly on exit**

`#restoreInsideControlLimits` (lines 500-509) already restores the four saved
fields; no signature change needed. Confirm it remains:

```js
  #restoreInsideControlLimits() {
    const controls = this.playerCamera?.controls;
    const saved = this._savedControlLimits;
    if (!controls || !saved) return;
    controls.minPolarAngle = saved.minPolarAngle;
    controls.maxPolarAngle = saved.maxPolarAngle;
    controls.minDistance = saved.minDistance;
    controls.maxDistance = saved.maxDistance;
    this._savedControlLimits = null;
  }
```

- [ ] **Step 3: Rewrite `#applyInsideCamera` — offset orbit + idle auto-drift**

Replace lines 536-549. The camera now sits at `center + sphericalOffset`
(parallax when dollied out; matches today's centered look when `distance` ~0),
and slowly drifts the azimuth when the user isn't interacting:

```js
  #applyInsideCamera(delta) {
    const controls = this.playerCamera?.controls;
    if (controls) controls.update(delta);

    // Idle auto-drift: if azimuth hasn't changed from user input, nudge it.
    if (controls) {
      const az = controls.azimuthAngle;
      const userMoved = Math.abs(az - (this._lastAzimuth ?? az)) > 1e-4;
      if (userMoved) {
        this._idleDriftClock = 0;
      } else {
        this._idleDriftClock = (this._idleDriftClock ?? 0) + delta;
        if (this._idleDriftClock > 2.5) controls.azimuthAngle = az + delta * 0.06;
      }
      this._lastAzimuth = controls.azimuthAngle;
    }

    const azimuth = controls?.azimuthAngle ?? 0;
    const polar = controls?.polarAngle ?? Math.PI * 0.5;
    const distance = controls?.distance ?? 0.1;
    const sinPolar = Math.sin(polar);
    tmpDir.set(sinPolar * Math.sin(azimuth), Math.cos(polar), sinPolar * Math.cos(azimuth));

    // Camera sits offset back from center along -viewDir, looks at the far shell.
    this.camera.position.copy(this.center).addScaledVector(tmpDir, -distance);
    this.camera.lookAt(this.center.clone().addScaledVector(tmpDir, this.radius));
  }
```

- [ ] **Step 4: Manual check**

Reload dev, press E. Inside you can now: **scroll to zoom/pull back** (parallax —
cards gain depth), **look fully up/down**, and if you stop touching it the view
**slowly drifts**. ESC returns to normal third-person (zoom/pitch limits
restored — confirm the outside camera feels exactly as before).

---

## Task 6: Depth-fade the cards

**Files:**
- Modify: `src/Portfolio/SkillSphere.js` `update` label loop (from Task 4)
- Add temps

- [ ] **Step 1: Add temps (top of file, with the other `tmp*`)**

```js
const tmpCamFwd = new THREE.Vector3();
const tmpToLabel = new THREE.Vector3();
```

- [ ] **Step 2: Fold a depth factor into the label opacity lerp**

In `update`, compute camera forward once before the loop, then fade each card by
how far in front of the camera it is (dot of camera-forward vs camera→label).
Front cards bright, side/back cards dim — kills overlap clutter, adds depth.
The label loop (from Task 4) becomes:

```js
    this.labelRoot.getWorldQuaternion(tmpParentQuat).invert();
    this.camera.getWorldDirection(tmpCamFwd);
    const opacityLift = this.active ? 0.22 : this._near ? 0.12 : 0;
    for (let i = 0; i < this.labels.length; i++) {
      const label = this.labels[i];
      this.#faceCamera(label, tmpParentQuat);
      label.getWorldPosition(tmpLabelPos);
      tmpToLabel.copy(tmpLabelPos).sub(this.camera.position).normalize();
      const facing = tmpCamFwd.dot(tmpToLabel);        // 1 = dead ahead, -1 = behind
      const depthFactor = THREE.MathUtils.clamp((facing + 0.35) / 1.0, 0.12, 1);
      const mat = label.material;
      const target = (label.userData.baseOpacity + opacityLift) * depthFactor;
      mat.opacity += (target - mat.opacity) * Math.min(1, delta * 5);
    }
```

- [ ] **Step 3: Manual check**

Reload dev. Inside and outside, cards in front are crisp while side/back cards
fade out — no more far-side cards drawing on top of near ones. Rotating the
view, cards smoothly brighten as they come to the front.

---

## Task 7: Accessible, harmonized cards (icons + retuned palette)

**Files:**
- Modify: `src/Portfolio/SkillSphere.js:5-11` (`CATEGORY_COLORS`)
- Modify: `src/Portfolio/SkillSphere.js:341-390` (`#drawBoard`)
- Add: `#drawCategoryIcon` private helper

- [ ] **Step 1: Retune `CATEGORY_COLORS`**

Replace lines 5-11 with the warm-world-harmonized, colorblind-safer palette:

```js
const CATEGORY_COLORS = {
  Frontend: '#4a90d9',
  CMS: '#d98aa8',
  'Backend & DB': '#7fd1a8',
  'DevOps & Tools': '#e0a05a',
  Other: '#c4a6e8',
};
```

- [ ] **Step 2: Add `#drawCategoryIcon` (simple per-category glyph on the chip)**

Draws a distinct shape per category at a given center, so category is encoded by
shape as well as color/word. `color` is the chip background's foreground ink.

```js
  #drawCategoryIcon(ctx, category, cx, cy, r, ink) {
    ctx.save();
    ctx.strokeStyle = ink;
    ctx.fillStyle = ink;
    ctx.lineWidth = 3;
    ctx.beginPath();
    switch (category) {
      case 'Frontend': // orbit/atom — circle + ellipse
        ctx.arc(cx, cy, r * 0.35, 0, Math.PI * 2);
        ctx.moveTo(cx + r, cy);
        ctx.ellipse(cx, cy, r, r * 0.45, 0, 0, Math.PI * 2);
        ctx.stroke();
        break;
      case 'Backend & DB': // stacked database
        ctx.ellipse(cx, cy - r * 0.5, r * 0.8, r * 0.3, 0, 0, Math.PI * 2);
        ctx.moveTo(cx - r * 0.8, cy - r * 0.5);
        ctx.lineTo(cx - r * 0.8, cy + r * 0.5);
        ctx.moveTo(cx + r * 0.8, cy - r * 0.5);
        ctx.lineTo(cx + r * 0.8, cy + r * 0.5);
        ctx.ellipse(cx, cy + r * 0.5, r * 0.8, r * 0.3, 0, 0, Math.PI);
        ctx.stroke();
        break;
      case 'DevOps & Tools': // gear-ish cross + ring
        ctx.arc(cx, cy, r * 0.45, 0, Math.PI * 2);
        ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r);
        ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy);
        ctx.stroke();
        break;
      case 'CMS': // document
        ctx.rect(cx - r * 0.6, cy - r * 0.8, r * 1.2, r * 1.6);
        ctx.moveTo(cx - r * 0.3, cy - r * 0.3); ctx.lineTo(cx + r * 0.3, cy - r * 0.3);
        ctx.moveTo(cx - r * 0.3, cy + r * 0.1); ctx.lineTo(cx + r * 0.3, cy + r * 0.1);
        ctx.stroke();
        break;
      default: // Other — diamond
        ctx.moveTo(cx, cy - r);
        ctx.lineTo(cx + r, cy);
        ctx.lineTo(cx, cy + r);
        ctx.lineTo(cx - r, cy);
        ctx.closePath();
        ctx.stroke();
    }
    ctx.restore();
  }
```

- [ ] **Step 3: Rewrite `#drawBoard` — warm base, crisper edges, wider chip with icon**

Replace lines 341-390. Changes: warm-charcoal card base (`rgba(20, 17, 11, 0.97)`)
instead of cold near-black; reduced `shadowBlur`; the category chip is widened to
hold an icon + the (shortened) category word.

```js
  #drawBoard(ctx, canvas, item, isLarge, isMedium) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 18 : isMedium ? 13 : 9; // crisper than before
    ctx.fillStyle = 'rgba(20, 17, 11, 0.97)';          // warm charcoal, not cold black
    this.#roundRect(ctx, 28, 28, w - 56, h - 56, 28);
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = 'rgba(255, 246, 224, 0.05)';
    this.#roundRect(ctx, 44, 44, w - 88, h - 88, 22);
    ctx.fill();

    ctx.strokeStyle = item.color;
    ctx.lineWidth = isLarge ? 8 : isMedium ? 6 : 4;
    this.#roundRect(ctx, 34, 34, w - 68, h - 68, 24);
    ctx.stroke();

    // Category chip: icon + word, color + shape + text (accessible triple-encode).
    const chipW = 196;
    const chipH = 40;
    ctx.fillStyle = item.color;
    this.#roundRect(ctx, 54, 48, chipW, chipH, 16);
    ctx.fill();
    const ink = '#0c0f0a';
    this.#drawCategoryIcon(ctx, item.category, 54 + 24, 48 + chipH / 2, 11, ink);
    ctx.fillStyle = ink;
    ctx.font = '900 20px Rajdhani, Inter, Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.#shortCategory(item.category), 54 + 46, 48 + chipH / 2 + 1);

    let fontSize = isLarge ? 78 : isMedium ? 66 : 56;
    ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    while (ctx.measureText(item.label).width > w - 132 && fontSize > 34) {
      fontSize -= 4;
      ctx.font = `900 ${fontSize}px Rajdhani, Inter, Arial, sans-serif`;
    }
    ctx.lineWidth = isLarge ? 8 : 6;
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.9)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.strokeText(item.label, w / 2, h / 2 + 24);
    ctx.shadowColor = item.color;
    ctx.shadowBlur = isLarge ? 14 : 10;
    ctx.fillStyle = '#f6f1df';
    ctx.fillText(item.label, w / 2, h / 2 + 24);
    ctx.shadowBlur = 0;
  }
```

- [ ] **Step 4: Manual check**

Reload dev. Each card now shows a category chip with a **shape icon + word**, on
the retuned palette, with a warm base and crisper edges. Confirm all five
categories render a distinct icon and read clearly.

---

## Task 8: Day/night adaptation

**Files:**
- Modify: `src/Portfolio/SkillSphere.js` `update` (poll mode)
- Add: `#applyTimeOfDay` private method
- Modify: constructor (init `_todMode`)

- [ ] **Step 1: Initialise mode tracking in the constructor**

After `this.timeOfDay = timeOfDay;` (Task 1), add (near the other flags, ~line 68):

```js
    this._todMode = null;
    this._todCardScale = 1; // multiplies card opacity target (day=brighter base)
```

- [ ] **Step 2: Add `#applyTimeOfDay`**

Cross-fades ring glow and a card-opacity scalar on mode flips, mirroring how
`TimeOfDay` tweens `billboards.emissiveBoost`. Day = muted ring glow + fuller
card base; night = stronger ring glow (beacon).

```js
  /** React to the binary day/night mode (the same `mode` TorchLight reads). */
  #applyTimeOfDay(mode) {
    if (mode === this._todMode) return;
    this._todMode = mode;
    const night = mode === 'night';
    const glowMul = night ? 1.35 : 0.55;
    if (this.ringMaterials) {
      for (const { mat, base } of this.ringMaterials) {
        gsap.to(mat, { emissiveIntensity: base * glowMul, duration: 1.2, ease: 'power2.inOut' });
      }
    }
    gsap.to(this, { _todCardScale: night ? 1 : 1.0, duration: 1.2 }); // hook for future per-mode card tuning
  }
```

- [ ] **Step 3: Poll mode in `update`**

Add near the top of `update`, after `this.elapsed += delta;`:

```js
    if (this.timeOfDay?.mode) this.#applyTimeOfDay(this.timeOfDay.mode);
```

- [ ] **Step 4: Manual check**

Reload dev. Toggle time of day (the project's day/night toggle). The ring/core
glow should **cross-fade**: muted in day so it reads against the bright sky,
brighter at night so the installation is a warm beacon. No flicker, no errors.

---

## Task 9: Control hint + gold/teal restyle

**Files:**
- Modify: `src/Portfolio/SkillSphere.js:448-457` (`#installDom`)
- Modify: `src/style.css` (`.skill-sphere-hint` block)

- [ ] **Step 1: Add a controls cue to the hint**

Replace the `innerHTML` in `#installDom` (lines 451-455):

```js
    this.hintEl.innerHTML = `
      <span class="skill-sphere-kicker">Inside Skills</span>
      <strong>Frontend / CMS / Backend / DevOps</strong>
      <span class="skill-sphere-controls">drag to look · scroll to zoom</span>
      <span class="skill-sphere-exit">ESC to return</span>
    `;
```

- [ ] **Step 2: Restyle the hint to the gold+teal identity**

In `src/style.css`, update the `.skill-sphere-hint` accent colors from neon
green to gold+teal and add the new `.skill-sphere-controls` rule. Replace the
green border/shadow/accent values:

```css
.skill-sphere-hint {
  /* …unchanged layout properties… */
  border: 1px solid rgba(230, 193, 114, 0.45);
  background: rgba(18, 16, 11, 0.80);
  box-shadow: 0 18px 52px rgba(0, 0, 0, 0.42), 0 0 30px rgba(230, 193, 114, 0.14);
}

.skill-sphere-kicker,
.skill-sphere-exit {
  color: #e6c172;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.skill-sphere-controls {
  color: #6fd6c4;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
```

Keep the existing layout/position/`.hidden`/`strong` rules; only the listed
properties change.

- [ ] **Step 3: Manual check**

Reload dev, press E. The hint shows the "drag to look · scroll to zoom" line and
the panel/accents are gold+teal (matching the rings). ESC still hides it.

---

## Task 10: Final review + single bundled commit

**Files:** all of the above.

- [ ] **Step 1: Full manual walkthrough**

Run `npm run dev` and verify the full spec checklist in one pass:
1. Rings spin at different speeds — from shore and inside.
2. Cards orbit coupled to the rings (one mechanism).
3. Inside camera: scroll-zoom/dolly, full up/down look, idle drift.
4. Every card upright + readable (back/top/bottom, not mirrored).
5. Far-side cards dim, no overlap clutter.
6. Category chips show icon + word + retuned color.
7. Day vs night glow cross-fades correctly.
8. Hint shows controls + gold/teal styling.
9. Enter/exit transitions smooth; ESC restores third-person exactly.
10. No console errors.

- [ ] **Step 2: Lint-style self-check**

Confirm no leftover references to deleted `#collectCoreVisuals`, the old
`0.36`/`0.16` literals, or the old green hex values in `SkillSphere.js`.

- [ ] **Step 3: Commit everything once (no co-author trailer)**

```bash
git add src/Portfolio/SkillSphere.js src/App.js src/style.css \
        docs/superpowers/specs/2026-05-31-skill-sphere-observatory-redesign.md \
        docs/superpowers/plans/2026-05-31-skill-sphere-observatory-redesign.md
git commit -m "Skills sphere: Observatory redesign — living rings, free interior camera, accessible day/night cards"
```

---

## Self-review notes (author)

- **Spec coverage:** §1 rings→Tasks 2-3; §2 camera→Task 5; §2b upright→Task 4;
  §3 depth fade→Task 6; §4 accessible cards→Task 7; §5 time-of-day→Task 8;
  §6 hint→Task 9. All covered.
- **Type/name consistency:** `#collectStructure`, `this.structure`,
  `this.ringMaterials`, `this.coreVisuals`, `#animateStructure`, `#faceCamera`,
  `#applyTimeOfDay`, `CARD_ORBIT_RATE`, `WORLD_UP`, `_todMode` used consistently
  across tasks. `#setCoreVisible` kept (call sites unchanged).
- **Verification:** manual only, per project convention (no probes).
- **Commit:** single, end-of-plan, no co-author trailer.
