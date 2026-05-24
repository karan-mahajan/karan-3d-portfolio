import * as THREE from 'three';
import gsap from 'gsap';

/**
 * World-object props that the player can interact with via ActionPrompts.
 * Each helper here loads a Kenney/Sketchfab GLB, places it, registers any
 * physics collider, and pushes a trigger config into the provided
 * ActionPrompts instance.
 *
 * Layout:
 *   Stuck crate    → (18, 0, 0)    push joke on the gravel path to Projects
 *   Punching bag   → (8, 0, -20)   fight-stance + superman-punch combo
 *   Football       → (7, 0, -8)    kick-football one-shot; ball rolls
 *   Dance tile     → (-28, 0, -3)  zone-enter starts dance; E swaps clips
 *   Chalk circle   → (10, 0, -10)  cartwheel one-shot
 *   Dock + trigger → pond (-12, 0, 18) backflip off the end
 *   Disappointed   → (3, 0, 44)    sign + trophy at end of experience trail
 */
export class Interactables {
  constructor(scene, loader, physics, actionPrompts) {
    this.scene = scene;
    this.loader = loader;
    this.physics = physics;
    this.prompts = actionPrompts;

    this.bag = null;          // { mesh, swing(strength) }
    this.football = null;     // { mesh, kick(yaw) }
    this.danceTile = null;    // { mesh }
  }

  async load() {
    // Each helper logs and swallows individual failures so one missing asset
    // doesn't take out the rest.
    await Promise.allSettled([
      this.#buildStuckCrate(),
      this.#buildPunchingBag(),
      this.#buildFootball(),
      this.#buildDanceTile(),
      this.#buildChalkCircle(),
      this.#buildDockBackflipTrigger(),
      this.#buildDisappointedSign(),
    ]);
  }

  update(delta) {
    if (this.football) this.football.update(delta);
    if (this.bag) this.bag.update(delta);
  }

  // ── 1. Stuck crate (push) ────────────────────────────────────────────────

  async #buildStuckCrate() {
    const url = '/models/furniture/cardboardboxclosed.glb';
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(url);
    } catch (e) {
      console.warn('[Interactables] stuck crate missing:', url);
      return;
    }
    const obj = gltf.scene;
    const pos = new THREE.Vector3(18, 0, 0);

    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z) || 1;
    const target = 1.44; // +20% over the original 1.2m target
    const s = target / maxDim;
    obj.scale.setScalar(s);
    obj.position.set(pos.x, 0, pos.z);
    obj.rotation.y = Math.PI * 0.1; // slightly wonky
    obj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    this.scene.add(obj);

    if (this.physics) this.physics.addStaticCuboid(pos.x, 0, pos.z, 0.72, 0.72, 0.72);

    // Crate is a "push spot" — the P-key push hint will surface when the
    // player is near, with crate-flavored jokes ("shipping ETA: never",
    // "what's inside? more crates", etc.).
    this.prompts.addPushSpot({ position: pos, surfaceRadius: 1.6, type: 'crate' });
  }

  // ── 2. Punching bag (fight-stance + superman-punch) ──────────────────────

  async #buildPunchingBag() {
    const url = '/models/extras/punching-bag/scene.gltf';
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(url);
    } catch (e) {
      console.warn('[Interactables] punching bag missing — skipping');
      return;
    }
    const obj = gltf.scene;
    const pos = new THREE.Vector3(8, 0, -20);

    // Scale: +20% over the previous 1.6m target.
    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const targetH = 1.92;
    const s = targetH / Math.max(size.y, 0.001);
    obj.scale.setScalar(s);

    obj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });

    // Wrap in a swing pivot anchored at the bag's TOP (rope attachment point)
    // so it pendulums correctly. Measure the scaled bag, anchor the pivot
    // there, and offset the bag down so its top sits at the pivot origin.
    const scaledBox = new THREE.Box3().setFromObject(obj);
    const bagSize = scaledBox.getSize(new THREE.Vector3());
    const bagTopY = bagSize.y;
    const pivot = new THREE.Group();
    pivot.position.set(pos.x, bagTopY, pos.z);
    obj.position.set(0, -bagTopY, 0);
    pivot.add(obj);
    this.scene.add(pivot);

    let swingT = 0;
    let swingAmp = 0;
    const swingAxis = new THREE.Vector3(1, 0, 0); // updated per-punch
    const bag = {
      mesh: pivot,
      swing(yaw) {
        // The bag pendulums *in the punch direction*. The rotation axis is
        // the horizontal vector 90° to the right of the punch direction, so
        // positive rotation tilts the bag's bottom toward the punch.
        swingAxis.set(Math.cos(yaw), 0, -Math.sin(yaw)).normalize();
        swingAmp = 0.55;
        swingT = 0;
      },
      update(delta) {
        if (swingAmp < 0.001) return;
        swingT += delta;
        const damp = Math.exp(-swingT * 1.2);
        const phase = Math.sin(swingT * 7) * damp * swingAmp;
        pivot.quaternion.setFromAxisAngle(swingAxis, phase);
        if (damp < 0.02) {
          swingAmp = 0;
          pivot.quaternion.identity();
        }
      },
    };
    this.bag = bag;

    if (this.physics) {
      // Thin cylindrical collider in the bag's center so the player can't
      // walk through it (but can brush past).
      this.physics.addStaticCylinder(pos.x, 0, pos.z, 0.34, targetH);
    }

    // Bag is also a "push spot" for the P-key hint — punch with E, push with P.
    this.prompts.addPushSpot({ position: pos, surfaceRadius: 1.2, type: 'bag' });

    this.prompts.add({
      id: 'punching-bag',
      position: pos,
      radius: 3.1,
      label: 'Square up (E)',
      punchLabel: 'Punch! (E)',
      mode: 'combat',
      action: 'supermanPunch',
      stanceAction: 'fightStance',
      onActivate: () => {
        // Swing the bag when the punch fires (not the stance). Use the
        // player's current facing yaw.
        const yaw = this.prompts.player.group.rotation.y;
        bag.swing(yaw);
      },
    });
  }

  // ── 3. Football (kick) ───────────────────────────────────────────────────

  async #buildFootball() {
    const url = '/models/extras/soccer-ball/scene.gltf';
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(url);
    } catch (e) {
      console.warn('[Interactables] football missing — skipping');
      return;
    }
    const obj = gltf.scene;

    // Scale up to ~0.5m diameter — real-world soccer ball (0.22m) reads as a
    // pebble at game scale, this size is closer to a beach ball and is
    // unmistakable from a distance. User explicitly called this out.
    obj.updateMatrixWorld(true);
    const rawBox = new THREE.Box3().setFromObject(obj);
    const rawSize = rawBox.getSize(new THREE.Vector3());
    const targetDiameter = 0.5;
    const rawMax = Math.max(rawSize.x, rawSize.y, rawSize.z) || 0.22;
    obj.scale.setScalar(targetDiameter / rawMax);

    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.x, size.y, size.z) / 2 || 0.25;

    const startPos = new THREE.Vector3(7, radius, -8);
    obj.position.copy(startPos);
    obj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    this.scene.add(obj);

    // Custom rolling physics — no Rapier dynamic body (simpler + lets us
    // reset the ball trivially). Velocity → friction → ground clamp.
    const velocity = new THREE.Vector3();
    let rollAxis = new THREE.Vector3(1, 0, 0);
    let spin = 0;

    const football = {
      mesh: obj,
      kick(yaw) {
        const power = 7; // m/s
        velocity.set(Math.sin(yaw) * power, 0.5, Math.cos(yaw) * power);
        // Rolling axis is perpendicular to travel direction, on the ground.
        rollAxis.set(Math.cos(yaw), 0, -Math.sin(yaw)).normalize();
        spin = power / radius;
      },
      update(delta) {
        if (velocity.lengthSq() < 0.0001) return;
        obj.position.x += velocity.x * delta;
        obj.position.y += velocity.y * delta;
        obj.position.z += velocity.z * delta;
        velocity.y -= 9.8 * delta;
        // Ground bounce + friction.
        if (obj.position.y <= radius) {
          obj.position.y = radius;
          if (velocity.y < 0) velocity.y = -velocity.y * 0.45;
          velocity.x *= 0.86;
          velocity.z *= 0.86;
        }
        // Rolling rotation.
        const speed = Math.hypot(velocity.x, velocity.z);
        spin = speed / radius;
        if (spin > 0.01) {
          obj.rotateOnWorldAxis(rollAxis, spin * delta);
        }
        if (speed < 0.05 && obj.position.y <= radius + 0.01) {
          velocity.set(0, 0, 0);
        }
      },
    };
    this.football = football;

    // Pass `obj.position` (live, mutated each frame as the ball rolls) so the
    // kick prompt follows the ball — otherwise the player can kick from the
    // ball's original spawn point even after the ball has rolled away.
    this.prompts.add({
      id: 'football',
      position: obj.position,
      radius: 1.8,
      label: 'Kick (E)',
      mode: 'oneShot',
      action: 'kickFootball',
      onActivate: () => {
        // Delay the kick slightly so impact lines up with the foot swing.
        const yaw = this.prompts.player.group.rotation.y;
        setTimeout(() => football.kick(yaw), 350);
      },
    });
  }

  // ── 4. Dance tile (zone-enter; E swaps clips) ────────────────────────────

  async #buildDanceTile() {
    // Position the dance tile next to the Contact mailbox, slightly south so
    // it doesn't overlap the existing nameplate.
    const pos = new THREE.Vector3(-28, 0, -3);

    // Just the emissive disc — earlier version stacked a `platform-stone` GLB
    // underneath, but it had no collider, so the character visually sank into
    // the raised stone. Flat ground disc reads cleanly as a dance floor.
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(1.55, 48),
      new THREE.MeshStandardMaterial({
        color: '#ffd28a',
        emissive: '#ffb86b',
        emissiveIntensity: 0.7,
        roughness: 0.5,
        metalness: 0.1,
        transparent: true,
        opacity: 0.9,
      }),
    );
    disc.rotation.x = -Math.PI / 2;
    disc.position.set(pos.x, 0.02, pos.z);
    disc.receiveShadow = true;
    this.scene.add(disc);
    this.danceTile = { mesh: disc };

    this.prompts.add({
      id: 'dance-tile',
      position: pos,
      radius: 1.7,
      label: 'Dance',
      mode: 'zoneLoop',
      action: 'dance',
      cycleActions: ['dance', 'danceCelebrate'],
    });
  }

  // ── 5. Chalk circle (cartwheel) ──────────────────────────────────────────

  async #buildChalkCircle() {
    const url = '/models/nature/path-stonecircle.glb';
    let obj = null;
    try {
      const gltf = await this.loader.loadGLTF(url);
      obj = gltf.scene;
    } catch (e) {
      console.warn('[Interactables] path-stonecircle missing; using bare ring');
    }

    const pos = new THREE.Vector3(10, 0, -10);

    if (obj) {
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const target = 2.88; // +20%
      const s = target / Math.max(size.x, size.z);
      obj.scale.setScalar(s);
      obj.position.set(pos.x, 0.02, pos.z);
      obj.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; } });
      this.scene.add(obj);
    } else {
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(1.08, 1.26, 48),
        new THREE.MeshStandardMaterial({ color: '#f5e6d3', transparent: true, opacity: 0.6, roughness: 1 }),
      );
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(pos.x, 0.02, pos.z);
      this.scene.add(ring);
    }

    this.prompts.add({
      id: 'chalk-circle',
      position: pos,
      radius: 1.8,
      label: 'Cartwheel (E)',
      mode: 'oneShot',
      action: 'cartwheel',
    });
  }

  // ── 6. Dock + backflip trigger ───────────────────────────────────────────

  async #buildDockBackflipTrigger() {
    const url = '/models/extras/dock-long.glb';
    const pondCenter = new THREE.Vector3(-12, 0, 18);
    // Dock extends from south shore toward the pond.
    const dockAnchor = new THREE.Vector3(pondCenter.x, 0.05, pondCenter.z - 7);
    const triggerPos = new THREE.Vector3(pondCenter.x, 0.05, pondCenter.z - 2);

    let dockObj = null;
    try {
      const gltf = await this.loader.loadGLTF(url);
      dockObj = gltf.scene;
    } catch (e) {
      console.warn('[Interactables] dock-long missing; backflip trigger still active');
    }

    if (dockObj) {
      dockObj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(dockObj);
      const size = box.getSize(new THREE.Vector3());
      // Scale to ~6m long, rotate to point along +Z (toward pond).
      const target = 7.2; // +20%
      const s = target / Math.max(size.x, size.z);
      dockObj.scale.setScalar(s);
      if (size.x > size.z) dockObj.rotation.y = Math.PI / 2;
      dockObj.position.set(dockAnchor.x, dockAnchor.y, dockAnchor.z);
      dockObj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
      this.scene.add(dockObj);

      // Solid collider for the deck so the player can't walk THROUGH the
      // dock's edge (previous bug — head clipped over the side). Player
      // auto-step (0.4m) handles stepping UP onto the deck normally; this
      // just stops the side-clip. Sized to the scaled dock.
      if (this.physics) {
        const scaledBox = new THREE.Box3().setFromObject(dockObj);
        const scaledSize = scaledBox.getSize(new THREE.Vector3());
        const cx = (scaledBox.min.x + scaledBox.max.x) / 2;
        const cy = (scaledBox.min.y + scaledBox.max.y) / 2;
        const cz = (scaledBox.min.z + scaledBox.max.z) / 2;
        this.physics.addStaticCuboid(
          cx, cy, cz,
          scaledSize.x / 2,
          Math.max(scaledSize.y / 2, 0.18),
          scaledSize.z / 2,
        );
      }
    }

    this.prompts.add({
      id: 'dock-end',
      position: triggerPos,
      radius: 1.7,
      label: 'Backflip (E)',
      mode: 'oneShot',
      action: 'backflip',
    });
  }

  // ── 7. Disappointed sign (end of experience trail) ───────────────────────

  async #buildDisappointedSign() {
    const url = '/models/nature/sign.glb';
    const pos = new THREE.Vector3(3, 0, 44);

    let signObj = null;
    try {
      const gltf = await this.loader.loadGLTF(url);
      signObj = gltf.scene;
    } catch (e) {
      console.warn('[Interactables] sign.glb missing; using bare post');
    }

    if (signObj) {
      signObj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(signObj);
      const size = box.getSize(new THREE.Vector3());
      const target = 1.92; // +20%
      const s = target / Math.max(size.y, 0.001);
      signObj.scale.setScalar(s);
      signObj.position.set(pos.x, 0, pos.z);
      signObj.rotation.y = Math.PI; // face south, back toward the player coming from spawn
      signObj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
      this.scene.add(signObj);
    }

    const label = this.#bakeSignLabel('This is where the resume ends... for now.');
    label.position.set(pos.x, 2.5, pos.z);
    label.lookAt(pos.x, 2.5, 0); // face spawn
    this.scene.add(label);

    // Sad participation trophy next to the sign.
    try {
      const gltf = await this.loader.loadGLTF('/models/props/trophy.glb');
      const trophy = gltf.scene;
      const tbox = new THREE.Box3().setFromObject(trophy);
      const tsize = tbox.getSize(new THREE.Vector3());
      const ts = 0.72 / Math.max(tsize.y, 0.001); // +20%
      trophy.scale.setScalar(ts);
      trophy.position.set(pos.x + 1.2, 0, pos.z - 0.3);
      trophy.rotation.y = Math.PI;
      trophy.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
      this.scene.add(trophy);
    } catch (e) {
      // Trophy missing is harmless.
    }

    this.prompts.add({
      id: 'disappointed-sign',
      position: pos,
      radius: 2.4,
      label: 'Sigh (E)',
      mode: 'oneShot',
      action: 'facepalm',
    });
  }

  #bakeSignLabel(text) {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#1a1410';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffd28a';
    ctx.fillRect(0, canvas.height - 8, canvas.width, 8);
    ctx.fillStyle = '#f5e6d3';
    ctx.font = 'italic 64px Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2 - 4);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide });
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(3.6, 0.9), mat); // +20%
    return plane;
  }
}
