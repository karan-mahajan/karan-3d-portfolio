import * as THREE from 'three';
import gsap from 'gsap';

export const INTERACTABLE_PROP_EXCLUSIONS = [
  { x: 18, z:   0, r: 2.2 }, // stuck crate
  { x:  8, z: -20, r: 1.6 }, // punching bag
  { x:  7, z:  -8, r: 1.2 }, // football
  { x: -28, z: -3, r: 2.2 }, // dance tile
  { x: 14, z: -14, r: 1.4 }, // chalk circle
  { x:  3, z:  44, r: 2.4 }, // disappointed sign + trophy
];

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
  static SOLID_PROP_CLEARANCE = 0.18;

  constructor(scene, loader, physics, actionPrompts, terrain = null) {
    this.scene = scene;
    this.loader = loader;
    this.physics = physics;
    this.prompts = actionPrompts;
    // Terrain is a heightfield (see Terrain.heightAt). Props placed at y=0
    // get buried past r≈22 from spawn where the wave exceeds 0.3m. We sample
    // heightAt(x,z) for every placement so things sit ON the ground rather
    // than IN it. Also used by the football's rolling clamp.
    this.terrain = terrain;

    this.bag = null;          // { mesh, swing(strength) }
    this.football = null;     // { mesh, kick(yaw) }
    this.danceTile = null;    // { mesh }
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
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
    const url = '/models/props/cardboardboxclosed.glb';
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(url);
    } catch (e) {
      console.warn('[Interactables] stuck crate missing:', url);
      return;
    }
    const obj = gltf.scene;
    obj.name = 'interactable:stuck-crate';
    const pos = new THREE.Vector3(18, 0, 0);
    const groundY = this.#groundY(pos.x, pos.z);

    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z) || 1;
    const target = 1.44; // +20% over the original 1.2m target
    const s = target / maxDim;
    obj.scale.setScalar(s);
    obj.position.set(pos.x, groundY, pos.z);
    obj.rotation.y = Math.PI * 0.1; // slightly wonky
    obj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    this.scene.add(obj);

    // Measured (rather than hardcoded 0.72³) so non-cubic crate GLBs collide
    // tight to the visible mesh.
    if (this.physics) {
      obj.updateMatrixWorld(true);
      const scaledBox = new THREE.Box3().setFromObject(obj);
      const scaledSize = scaledBox.getSize(new THREE.Vector3());
      const center = scaledBox.getCenter(new THREE.Vector3());
      const clearance = Interactables.SOLID_PROP_CLEARANCE;
      this.physics.addStaticCuboid(
        center.x, center.y, center.z,
        scaledSize.x / 2 + clearance, scaledSize.y / 2, scaledSize.z / 2 + clearance,
      );
    }

    // Crate is a "push spot" — the P-key push hint will surface when the
    // player is near, with crate-flavored jokes ("shipping ETA: never",
    // "what's inside? more crates", etc.). colliderRadius = max XZ half of
    // the scaled crate so the push-start snap parks the hand on the front
    // face at apex instead of clipping through it.
    obj.updateMatrixWorld(true);
    const finalBox = new THREE.Box3().setFromObject(obj);
    const finalSize = finalBox.getSize(new THREE.Vector3());
    this.prompts.addPushSpot({
      position: pos,
      surfaceRadius: 1.6,
      type: 'crate',
      colliderRadius: Math.max(finalSize.x, finalSize.z) / 2,
    });
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
    const groundY = this.#groundY(pos.x, pos.z);

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
    pivot.position.set(pos.x, groundY + bagTopY, pos.z);
    obj.position.set(0, -bagTopY, 0);
    pivot.add(obj);
    this.scene.add(pivot);

    // Thin cylindrical collider in the bag's center so the player can't
    // walk through it (but can brush past). Disabled while the bag is
    // swinging — see update() — so the painted bag and the collider never
    // disagree about where the bag is.
    let bagBody = null;
    if (this.physics) {
      bagBody = this.physics.addStaticCylinder(pos.x, groundY, pos.z, 0.34, targetH);
    }

    let swingT = 0;
    let swingAmp = 0;
    const swingAxis = new THREE.Vector3(1, 0, 0); // updated per-punch
    const bag = {
      mesh: pivot,
      body: bagBody,
      swing(yaw) {
        // The bag pendulums *in the punch direction*. The rotation axis is
        // the horizontal vector 90° to the right of the punch direction, so
        // positive rotation tilts the bag's bottom toward the punch.
        swingAxis.set(Math.cos(yaw), 0, -Math.sin(yaw)).normalize();
        swingAmp = 0.55;
        swingT = 0;
      },
      update(delta) {
        const settle = () => {
          swingAmp = 0;
          pivot.quaternion.identity();
          if (bagBody && !bagBody.isEnabled()) bagBody.setEnabled(true);
        };
        if (swingAmp < 0.001) {
          settle();
          return;
        }
        if (bagBody && bagBody.isEnabled()) bagBody.setEnabled(false);
        swingT += delta;
        const damp = Math.exp(-swingT * 1.2);
        const phase = Math.sin(swingT * 7) * damp * swingAmp;
        pivot.quaternion.setFromAxisAngle(swingAxis, phase);
        if ((swingT > 1.2 && Math.abs(phase) < 0.015) || damp < 0.12 || swingT > 2.8) settle();
      },
    };
    this.bag = bag;

    // Bag is also a "push spot" for the P-key hint — punch with E, push with P.
    // colliderRadius matches the static-cylinder radius (0.34) so the push
    // snap places the hand on the bag's surface at apex.
    this.prompts.addPushSpot({ position: pos, surfaceRadius: 1.2, type: 'bag', colliderRadius: 0.34 });

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
        // player's current facing yaw. Audio fires on the same frame so the
        // thud lands with the visible impact.
        const yaw = this.prompts.player.group.rotation.y;
        bag.swing(yaw);
        this.prompts.audio?.playPunch();
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

    const spawnX = 7, spawnZ = -8;
    const spawnGround = this.#groundY(spawnX, spawnZ);
    const startPos = new THREE.Vector3(spawnX, spawnGround + radius, spawnZ);
    obj.position.copy(startPos);
    obj.traverse((c) => {
      if (!c.isMesh) return;
      c.castShadow = true;
      c.receiveShadow = true;
      const materials = Array.isArray(c.material) ? c.material : [c.material];
      materials.forEach((material) => {
        if (!material?.isMeshStandardMaterial) return;
        material.emissive = new THREE.Color('#f8f2df');
        material.emissiveMap = material.map || material.emissiveMap;
        material.emissiveIntensity = Math.max(material.emissiveIntensity || 0, material.map ? 0.162 : 0.027);
        material.roughness = Math.min(material.roughness ?? 0.65, 0.55);
        material.needsUpdate = true;
      });
    });
    this.scene.add(obj);

    // Rapier dynamic body — the player's character controller has
    // setApplyImpulsesToDynamicBodies(true), so just walking into the ball
    // nudges it. Kick applies a forward+upward impulse. The old custom
    // rolling physics let the ball pass through every static collider in
    // the world — this swap fixes that family of bugs at once.
    const physics = this.physics;
    const RECOVERY_RADIUS = 50;        // ball further than this → respawn
    const RECOVERY_Y = -1.0;           // or below this (rolled into ocean)
    const KICK_POWER = 6.0;            // forward impulse magnitude (m/s of Δv at density 0.6)
    const KICK_LIFT = 2.2;             // upward impulse so the ball arcs
    const _tmpV3 = new THREE.Vector3();
    const _tmpQ = new THREE.Quaternion();
    let body = null;
    if (physics) {
      body = physics.addDynamicBall(startPos.x, startPos.y, startPos.z, radius);
    }

    const respawn = () => {
      if (!body) return;
      const gy = this.#groundY(spawnX, spawnZ);
      body.setTranslation({ x: spawnX, y: gy + radius, z: spawnZ }, true);
      body.setLinvel({ x: 0, y: 0, z: 0 }, true);
      body.setAngvel({ x: 0, y: 0, z: 0 }, true);
    };

    const football = {
      mesh: obj,
      body,
      kick(yaw) {
        if (!body) return;
        // Mass = density * (4/3 π r³); applyImpulse uses kg·m/s so scale by mass.
        const mass = body.mass();
        body.applyImpulse({
          x: Math.sin(yaw) * KICK_POWER * mass,
          y: KICK_LIFT * mass,
          z: Math.cos(yaw) * KICK_POWER * mass,
        }, true);
        // Match the spin to the kick direction so the ball doesn't look like
        // it slides — a forward kick should produce forward roll.
        body.applyTorqueImpulse({
          x: Math.cos(yaw) * KICK_POWER * mass * 0.15,
          y: 0,
          z: -Math.sin(yaw) * KICK_POWER * mass * 0.15,
        }, true);
      },
      respawn,
      update(_delta) {
        if (!body) return;
        const t = body.translation();
        // Recover if the ball has been kicked into the ocean or way off-island.
        if (t.y < RECOVERY_Y || (t.x * t.x + t.z * t.z) > RECOVERY_RADIUS * RECOVERY_RADIUS) {
          respawn();
          return;
        }
        obj.position.set(t.x, t.y, t.z);
        const r = body.rotation();
        _tmpQ.set(r.x, r.y, r.z, r.w);
        obj.quaternion.copy(_tmpQ);
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
        // Audio fires on the same beat as the physics impulse.
        const yaw = this.prompts.player.group.rotation.y;
        setTimeout(() => {
          football.kick(yaw);
          this.prompts.audio?.playKick();
        }, 350);
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
    disc.position.set(pos.x, this.#groundY(pos.x, pos.z) + 0.02, pos.z);
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

    // Moved from (10, -10) → (14, -14) so the football (start 7, -8; rolls
    // freely) can't drift into the cartwheel zone — both prompts had 1.8m
    // radii at 3.6m separation, so a single kick used to swap the prompt
    // from "Kick" to "Cartwheel".
    const pos = new THREE.Vector3(14, 0, -14);
    const groundY = this.#groundY(pos.x, pos.z);

    if (obj) {
      obj.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(obj);
      const size = box.getSize(new THREE.Vector3());
      const target = 2.88; // +20%
      const s = target / Math.max(size.x, size.z);
      obj.scale.setScalar(s);
      obj.position.set(pos.x, groundY + 0.02, pos.z);
      obj.traverse((c) => { if (c.isMesh) { c.receiveShadow = true; } });
      this.scene.add(obj);
    } else {
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(1.08, 1.26, 48),
        new THREE.MeshStandardMaterial({ color: '#f5e6d3', transparent: true, opacity: 0.6, roughness: 1 }),
      );
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(pos.x, groundY + 0.02, pos.z);
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
    // Dock extends from south shore toward the pond. Lift to terrain so it
    // doesn't bury into the sloped pond bank; keep the 0.05 lift above ground.
    const dockGroundY = this.#groundY(pondCenter.x, pondCenter.z - 7);
    const dockAnchor = new THREE.Vector3(pondCenter.x, dockGroundY + 0.05, pondCenter.z - 7);
    const triggerPos = new THREE.Vector3(pondCenter.x, this.#groundY(pondCenter.x, pondCenter.z - 2) + 0.05, pondCenter.z - 2);

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
    const groundY = this.#groundY(pos.x, pos.z);

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
      signObj.position.set(pos.x, groundY, pos.z);
      // Face -Z (toward spawn at the south) so the player approaching from
      // the experience trail reads the sign's front, not its back.
      signObj.rotation.y = 0;
      signObj.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
      this.scene.add(signObj);

      // Static collider so the player can't walk through the post or panel.
      // Sized to the scaled GLB box; cuboid Y arg is the cuboid's CENTRE.
      if (this.physics) {
        const scaledBox = new THREE.Box3().setFromObject(signObj);
        const scaledSize = scaledBox.getSize(new THREE.Vector3());
        this.physics.addStaticCuboid(
          pos.x, (scaledBox.min.y + scaledBox.max.y) / 2, pos.z,
          Math.max(scaledSize.x / 2, 0.18),
          Math.max(scaledSize.y / 2, 0.1),
          Math.max(scaledSize.z / 2, 0.06),
        );
      }
    }

    const label = this.#bakeSignLabel('This is where the resume ends... for now.');
    label.position.set(pos.x, groundY + 2.5, pos.z);
    label.lookAt(pos.x, groundY + 2.5, 0); // face spawn
    this.scene.add(label);

    // Sad participation trophy next to the sign.
    try {
      const gltf = await this.loader.loadGLTF('/models/props/trophy.glb');
      const trophy = gltf.scene;
      const tbox = new THREE.Box3().setFromObject(trophy);
      const tsize = tbox.getSize(new THREE.Vector3());
      const ts = 0.72 / Math.max(tsize.y, 0.001); // +20%
      trophy.scale.setScalar(ts);
      const tx = pos.x + 1.2;
      const tz = pos.z - 0.3;
      const tgroundY = this.#groundY(tx, tz);
      trophy.position.set(tx, tgroundY, tz);
      trophy.rotation.y = Math.PI;
      trophy.traverse((c) => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
      this.scene.add(trophy);

      // Small cylinder collider so the trophy isn't walk-through.
      if (this.physics) {
        const scaledBox = new THREE.Box3().setFromObject(trophy);
        const scaledSize = scaledBox.getSize(new THREE.Vector3());
        const trophyR = Math.max(scaledSize.x, scaledSize.z) / 2;
        this.physics.addStaticCylinder(tx, tgroundY, tz, trophyR, scaledSize.y);
      }
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
