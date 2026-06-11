import gsap from "gsap";
import {
  Fn,
  atan,
  attribute,
  cameraProjectionMatrix,
  cos,
  float,
  length,
  mix,
  modelViewMatrix,
  positionGeometry,
  positionWorld,
  sin,
  smoothstep,
  uniform,
  uv,
  varying,
  vec2,
  vec3,
  vec4,
} from "three/tsl";
import * as THREE from "three/webgpu";
import { MeshBasicNodeMaterial } from "three/webgpu";
import { BANNER_TINTS, MUSEUM_CHAPTERS } from "./MuseumData.js";

/**
 * The hidden making-of museum.
 *
 * A lone Doraemon-style magic door in a quiet clearing; opening it teleports
 * the player (TransitionFX iris) into a sealed underground gallery ~45m below
 * — real walkable geometry, never a terrain hole. door.glb is tiny and loads
 * right after boot; museum.glb lazy-fetches when the player comes within 25m
 * (neither is in the boot Loader manifest — Colour Garden precedent).
 *
 * Owns: door placement + beacon, collider harvest from the Blender-authored
 * cuboid_*\/ramp_* proxies, the E-prompt + crossing sequences, the interior
 * state swap (player flags, camera clamp, audio, HUD body-class, App callback
 * for the outdoor world), torch-flicker / rune-pulse TSL materials, the
 * float/orbit prop animations, the per-station accent tints, the paged
 * chapter reading panel (content in MuseumData.js), and the first-entry
 * secret reveal (achievement + hidden map marker, see mapSection()).
 *
 * WebGPU note: all custom shading is TSL node materials (mirrors
 * ResumeBook.js); GLSL onBeforeCompile silently no-ops on this renderer.
 */

// Door placement — across from the east-shore bench (bench_slab01_south at
// (29.6, 14.7), the one flanked by its two pole lights at (31.3, 6.9) and
// (30.3, 24.0)): a lone door on the grass a few metres inland of the bench,
// clear of the lamps, bridge02 and the (24, 20) tree cluster. Front (local
// −Z) faces spawn so a player coming up the shore path sees the door
// face-on. Flip DOOR_YAW by +Math.PI if the walk-test shows the back.
// (v3 nature.addExclusion is a no-op stub — trees are baked in Blender — so
// the spot is chosen clear instead of excluded; #buildDoor warns if the
// navmask disagrees.)
const DOOR_POS = { x: 26.5, z: 9.5 };
const DOOR_YAW = Math.atan2(26.5, 9.5);

const INTERIOR_DROP = 45; // interior group sits this far below the door ground
const LOAD_RADIUS = 25; // lazy-fetch museum.glb inside this range
const DOOR_PROMPT_RADIUS = 3.4;
const EXIT_PROMPT_RADIUS = 2.8;
const STATION_PROMPT_RADIUS = 2.3;
const DOOR_SWING_RAD = -1.92; // leaf rotation.y when open (hinge contract)

const BEACON_HEIGHT = 7;
const MOTE_COUNT = 14;

const CAMERA_MAX_DISTANCE = 4.5; // interior orbit clamp (spec §6)
const CAMERA_MIN_POLAR = Math.PI * 0.3; // keep the orbit below the ceilings

const chapterById = (id) => MUSEUM_CHAPTERS.find((c) => c.id === id);

export class Museum {
  static #LIGHT_INTENSITY = [16, 18, 26, 26];

  /**
   * @param {object} opts
   * @param {THREE.Scene} opts.scene
   * @param {object} opts.terrain        — heightAt(x, z)
   * @param {object} opts.physics       — addStaticRotatedCuboid(...)
   * @param {object} opts.loader        — Utils/Loader (loadGLTF)
   * @param {object} opts.player        — placeAt / interiorMode / controller
   * @param {object} opts.playerCamera  — snapTo + camera-controls handle
   * @param {object} opts.audio
   * @param {object} opts.transitionFx  — iris wipe
   * @param {object} [opts.navmask]    — clearance tests for the exit landing
   * @param {object} [opts.discovery]  — first entry calls discover('museum')
   * @param {object} [opts.achievements] — first entry triggers 'museum_found'
   * @param {Function} [opts.onInteriorChange] — App hides/restores the outdoor world
   * @param {Function} [opts.warmShaders]      — off-thread pipeline warm after loads
   */
  constructor({
    scene,
    terrain,
    physics,
    loader,
    player,
    playerCamera,
    audio,
    transitionFx,
    navmask = null,
    discovery = null,
    achievements = null,
    onInteriorChange = null,
    warmShaders = null,
  }) {
    this.scene = scene;
    this.terrain = terrain;
    this.physics = physics;
    this.loader = loader;
    this.player = player;
    this.playerCamera = playerCamera;
    this.audio = audio;
    this.transitionFx = transitionFx;
    this.navmask = navmask;
    this.discovery = discovery;
    this.achievements = achievements;
    this.onInteriorChange = onInteriorChange;
    this.warmShaders = warmShaders;

    this.groundY = terrain?.heightAt
      ? terrain.heightAt(DOOR_POS.x, DOOR_POS.z)
      : 0;
    this.interiorY = this.groundY - INTERIOR_DROP;

    this.isInside = false;
    this._busy = false; // a crossing sequence is running
    this._doorReady = false;
    this._interiorReady = false;
    this._interiorLoadStarted = false;
    this._panelOpen = false;
    this._armed = null; // { action: 'enter'|'exit'|'station', ... } the E key fires

    this.doorGroup = null;
    this.doorLeaf = null;
    this.interiorGroup = null;
    this.exitLeaf = null;
    this.stations = [];
    this.floatProps = [];
    this._orbit = [];
    this.doorPortal = null;
    this.exitPortal = null;
    // Interior wall/floor boxes kept (invisible) for the camera occlusion
    // raycast — without them the orbit pokes through the gallery walls and
    // the player sees the museum from outside, floating in the void. The
    // outdoor door keeps its own set so the orbit can't sit behind the door
    // panel (door filling the frame, character hidden).
    this._cameraBlockers = [];
    this._doorCameraBlockers = [];
    this._walk = null; // active scripted-walk segment (see #walkTo)
    this._outfitBefore = "default"; // outfit to restore on the way out

    // One clock uniform drives every TSL material here (beacon, flames, runes).
    this.uTime = uniform(0);
    this.uBeaconBoost = uniform(0.6); // night-boosted in update()
    this.uPortalFade = uniform(0); // door-frame portal opacity (one at a time)

    this.#createInteriorLights();
    this.#installDom();
    this.#bindKeys();
  }

  /** Fire-and-forget from App.boot — the door is ~29m from spawn and pops in
   *  a beat after the reveal (football/guestbook precedent). */
  load() {
    return this.loader
      .loadGLTF("/world/museum/door.glb")
      .then((gltf) => {
        this.#buildDoor(gltf);
        this._doorReady = true;
        this.warmShaders?.();
      })
      .catch((err) => console.warn("[Museum] door.glb load failed:", err));
  }

  // ── Exterior door ──────────────────────────────────────────────────────────

  #buildDoor(gltf) {
    const g = gltf.scene;
    g.name = "museumDoor";
    this.doorLeaf = g.getObjectByName("doorLeaf");
    if (!this.doorLeaf) console.warn("[Museum] doorLeaf missing in door.glb");
    g.traverse((o) => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
      }
    });
    // Portal sized from the closed leaf's bbox — measured BEFORE the group
    // transform so the box is in door-local space.
    if (this.doorLeaf) {
      g.updateMatrixWorld(true);
      this.doorPortal = this.#buildPortal(
        new THREE.Box3().setFromObject(this.doorLeaf),
      );
      g.add(this.doorPortal);
    }
    g.position.set(DOOR_POS.x, this.groundY, DOOR_POS.z);
    g.rotation.y = DOOR_YAW;
    this.scene.add(g);
    this.doorGroup = g;
    this.#harvestColliders(g, this._doorCameraBlockers);
    // Active whenever the player is outdoors: the orbit clamps in front of
    // the door panel instead of sitting behind it with the door filling the
    // frame (the post-exit view). Three small boxes — raycast cost is noise.
    if (!this.isInside) {
      this.playerCamera.collisionMeshes = this._doorCameraBlockers;
    }
    this.#buildBeacon(g);
    if (this.groundY < 0.05) {
      console.warn(
        `[Museum] door ground is low (${this.groundY.toFixed(2)}m) — ` +
          "possibly in/near water; nudge DOOR_POS",
      );
    }
    if (this.navmask && !this.navmask.hasClearance?.(DOOR_POS.x, DOOR_POS.z, 1.5)) {
      console.warn(
        "[Museum] door spot overlaps a navmask blocker (rock/tree/lamp) — nudge DOOR_POS",
      );
    }
  }

  /**
   * Convert every cuboid_/ramp_ proxy mesh under `root` into a Rapier collider
   * matching its world transform, then strip the proxy from the scene. The
   * proxies are authored boxes with size baked into the geometry and rotation
   * on the object (ramps), so bbox + world quaternion reproduces them exactly.
   *
   * `keepInto` (an array) keeps the proxies in place instead (invisible) and
   * collects them there as raycast targets for the camera occlusion test
   * — a couple dozen boxes, far cheaper than raycasting the visual meshes.
   */
  #harvestColliders(root, keepInto = null) {
    root.updateMatrixWorld(true);
    const proxies = [];
    root.traverse((o) => {
      if (
        o.isMesh &&
        (o.name.startsWith("cuboid_") || o.name.startsWith("ramp_"))
      ) {
        proxies.push(o);
      }
    });
    const center = new THREE.Vector3();
    const size = new THREE.Vector3();
    const pos = new THREE.Vector3();
    const quat = new THREE.Quaternion();
    const scl = new THREE.Vector3();
    for (const m of proxies) {
      m.geometry.computeBoundingBox();
      m.geometry.boundingBox.getCenter(center);
      m.geometry.boundingBox.getSize(size);
      pos.copy(center);
      m.localToWorld(pos);
      m.getWorldQuaternion(quat);
      m.getWorldScale(scl);
      this.physics.addStaticRotatedCuboid(
        pos.x,
        pos.y,
        pos.z,
        (size.x / 2) * scl.x,
        (size.y / 2) * scl.y,
        (size.z / 2) * scl.z,
        { x: quat.x, y: quat.y, z: quat.z, w: quat.w },
      );
      if (keepInto) {
        m.visible = false;
        // DoubleSide so the occlusion ray hits walls from either face
        // (Mesh.raycast culls by material.side; the proxies' visual side is
        // irrelevant — they never render).
        m.material = this._blockerMat ??= new THREE.MeshBasicMaterial({
          side: THREE.DoubleSide,
        });
        keepInto.push(m);
      } else {
        m.removeFromParent();
        m.geometry.dispose();
      }
    }
    return proxies.length;
  }

  // ── Beacon: light shaft + ground glow + drifting motes (night-boosted) ─────

  #buildBeacon(doorGroup) {
    const group = new THREE.Group();
    group.name = "museumDoorBeacon";

    const shaftMat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });
    const v = uv().y;
    const pulse = float(0.72).add(sin(this.uTime.mul(1.4)).mul(0.14));
    const fade = v.oneMinus().pow(1.7).mul(smoothstep(0.0, 0.05, v));
    shaftMat.colorNode = mix(
      vec3(1.0, 0.78, 0.42),
      vec3(1.0, 0.96, 0.82),
      v.oneMinus(),
    );
    shaftMat.opacityNode = fade.mul(pulse).mul(0.5).mul(this.uBeaconBoost);
    const shaft = new THREE.Mesh(
      new THREE.CylinderGeometry(0.42, 0.13, BEACON_HEIGHT, 22, 1, true),
      shaftMat,
    );
    shaft.position.y = BEACON_HEIGHT / 2 + 2.6; // base hovers above the lintel
    shaft.frustumCulled = false;
    group.add(shaft);

    const glowMat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    });
    const d = length(uv().sub(0.5));
    glowMat.colorNode = vec3(1.0, 0.74, 0.38);
    glowMat.opacityNode = smoothstep(0.5, 0.06, d).mul(0.32).mul(this.uBeaconBoost);
    const disc = new THREE.Mesh(new THREE.CircleGeometry(1.5, 36), glowMat);
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = 0.07;
    disc.frustumCulled = false;
    group.add(disc);

    this.#buildMotes(group);
    doorGroup.add(group);
  }

  /** Small golden mote drift around the door (mini-ResumeBook recipe). */
  #buildMotes(parent) {
    const base = new THREE.BufferGeometry();
    base.setAttribute(
      "position",
      new THREE.BufferAttribute(
        new Float32Array([
          -0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0,
        ]),
        3,
      ),
    );
    base.setAttribute(
      "uv",
      new THREE.BufferAttribute(new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]), 2),
    );
    base.setIndex([0, 1, 2, 0, 2, 3]);
    const geo = new THREE.InstancedBufferGeometry();
    geo.setAttribute("position", base.attributes.position);
    geo.setAttribute("uv", base.attributes.uv);
    geo.setIndex(base.index);
    geo.instanceCount = MOTE_COUNT;
    const bases = new Float32Array(MOTE_COUNT * 3);
    const seeds = new Float32Array(MOTE_COUNT * 3);
    for (let i = 0; i < MOTE_COUNT; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = 0.5 + Math.random() * 0.9;
      bases[i * 3] = Math.cos(a) * r;
      bases[i * 3 + 1] = 0.3 + Math.random() * 2.2;
      bases[i * 3 + 2] = Math.sin(a) * r;
      seeds[i * 3] = Math.random() * Math.PI * 2;
      seeds[i * 3 + 1] = 0.4 + Math.random() * 0.7;
      seeds[i * 3 + 2] = 0.08 + Math.random() * 0.18;
    }
    geo.setAttribute("aBase", new THREE.InstancedBufferAttribute(bases, 3));
    geo.setAttribute("aSeed", new THREE.InstancedBufferAttribute(seeds, 3));
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 1.4, 0), 5);

    const mat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const vTwinkle = varying(float(0), "vMuseumMoteTwinkle");
    const uTime = this.uTime;
    mat.vertexNode = Fn(() => {
      const b = attribute("aBase");
      const s = attribute("aSeed");
      const pos = b.toVar();
      pos.x.addAssign(sin(uTime.mul(s.y).add(s.x)).mul(s.z));
      pos.y.addAssign(
        sin(uTime.mul(s.y.mul(1.4)).add(s.x.mul(2.0))).mul(s.z.mul(2.0)),
      );
      pos.z.addAssign(cos(uTime.mul(s.y.mul(0.8)).add(s.x.mul(1.5))).mul(s.z));
      vTwinkle.assign(
        float(0.5).add(sin(uTime.mul(2.4).add(s.x.mul(4.0))).mul(0.5)),
      );
      const view = modelViewMatrix.mul(vec4(pos, 1.0)).toVar();
      view.xy.addAssign(positionGeometry.xy.mul(0.07));
      return cameraProjectionMatrix.mul(view);
    })();
    const core = smoothstep(0.5, 0.0, length(uv().sub(0.5)));
    mat.colorNode = mix(vec3(1.0, 0.7, 0.3), vec3(1.0, 0.95, 0.7), core);
    mat.opacityNode = core.mul(vTwinkle).mul(this.uBeaconBoost);

    const motes = new THREE.Mesh(geo, mat);
    motes.name = "museumDoor-motes";
    motes.frustumCulled = false;
    parent.add(motes);
  }

  // ── Doorway portal ─────────────────────────────────────────────────────────

  /** A swirling magic plane filling the door frame, so an opening door shows
   *  "somewhere else" instead of the grass behind it. Sized from the closed
   *  leaf's local-space bbox; hidden until a crossing sequence fades it in. */
  #buildPortal(leafBox) {
    const size = leafBox.getSize(new THREE.Vector3());
    const center = leafBox.getCenter(new THREE.Vector3());
    const alongX = size.x >= size.z; // leaf plane orientation in local space
    const geo = new THREE.PlaneGeometry(
      (alongX ? size.x : size.z) * 0.96,
      size.y * 0.96,
    );
    const mesh = new THREE.Mesh(geo, this.#portalMaterial());
    mesh.position.copy(center);
    if (!alongX) mesh.rotation.y = Math.PI / 2;
    mesh.name = "museumPortal";
    mesh.visible = false;
    mesh.renderOrder = 2;
    return mesh;
  }

  #portalMaterial() {
    if (this._portalMat) return this._portalMat;
    const m = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    // Spiral in door-frame UV space, squashed vertically so the vortex fills
    // the tall opening; deep violet core with a golden rim that ties into the
    // beacon. Both door portals share this material + fade uniform — only one
    // is ever visible at a time.
    const p = vec2(uv().x.sub(0.5).mul(2.0), uv().y.sub(0.5).mul(1.15));
    const r = length(p);
    const ang = atan(p.y, p.x);
    const spiral = sin(ang.mul(3.0).add(r.mul(9.0)).sub(this.uTime.mul(2.2)))
      .mul(0.5)
      .add(0.5);
    const sparkle = sin(ang.mul(5.0).sub(r.mul(13.0)).add(this.uTime.mul(1.5)))
      .mul(0.5)
      .add(0.5);
    const core = smoothstep(1.0, 0.12, r);
    m.colorNode = mix(
      vec3(0.05, 0.02, 0.12),
      vec3(0.38, 0.22, 0.95),
      spiral.mul(core),
    )
      .add(vec3(1.0, 0.72, 0.35).mul(sparkle).mul(smoothstep(0.35, 0.95, r)).mul(0.3))
      .mul(1.7);
    m.opacityNode = this.uPortalFade.mul(
      smoothstep(1.1, 0.85, r).mul(0.3).add(0.7),
    );
    this._portalMat = m;
    return m;
  }

  #portalShow(mesh) {
    if (!mesh) return;
    gsap.killTweensOf(this.uPortalFade);
    mesh.visible = true;
    gsap.to(this.uPortalFade, { value: 1, duration: 0.7, ease: "power1.in" });
  }

  #portalHide(mesh) {
    if (!mesh) return;
    gsap.killTweensOf(this.uPortalFade);
    this.uPortalFade.value = 0;
    mesh.visible = false;
  }

  // ── Interior: lazy load + build ────────────────────────────────────────────

  #maybeLoadInterior() {
    if (this._interiorLoadStarted) return;
    this._interiorLoadStarted = true;
    // Warm the museum outfit alongside the gallery so the golden wipe never
    // waits on a download at the threshold.
    this.player.character?.outfits?.prefetch?.("museum");
    this.loader
      .loadGLTF("/world/museum/museum.glb")
      .then((gltf) => {
        this.#buildInterior(gltf);
        this._interiorReady = true;
        this.warmShaders?.();
      })
      .catch((err) => console.warn("[Museum] museum.glb load failed:", err));
  }

  #buildInterior(gltf) {
    const g = gltf.scene;
    g.name = "museumInterior";
    this.exitLeaf = g.getObjectByName("exitDoorLeaf");
    // Portal sized in local space (group still at identity), added after the
    // shadow/material traversals can't touch it.
    if (this.exitLeaf) {
      g.updateMatrixWorld(true);
      this.exitPortal = this.#buildPortal(
        new THREE.Box3().setFromObject(this.exitLeaf),
      );
      g.add(this.exitPortal);
    }
    g.position.set(DOOR_POS.x, this.interiorY, DOOR_POS.z);
    g.rotation.y = DOOR_YAW;
    g.visible = false; // revealed on entry (behind the iris)
    this.scene.add(g);
    this.interiorGroup = g;
    const colliderCount = this.#harvestColliders(g, this._cameraBlockers);

    // The Blender build frames the exit doorway (vestSouthL/R/Header boxes)
    // but the opening itself ships unproxied — seal it at runtime so neither
    // the player nor the camera ray slips through the closed exit door into
    // the void (the "staring at the back of the door" arrival view).
    {
      const sealLocal = new THREE.Vector3(0, 1.26, 2.7);
      const seal = new THREE.Mesh(
        new THREE.BoxGeometry(1.42, 2.52, 0.16),
        (this._blockerMat ??= new THREE.MeshBasicMaterial({
          side: THREE.DoubleSide,
        })),
      );
      seal.name = "museumExitDoorSeal";
      seal.position.copy(sealLocal);
      seal.visible = false;
      g.add(seal);
      this._cameraBlockers.push(seal);
      const wp = g.localToWorld(sealLocal.clone());
      this.physics.addStaticRotatedCuboid(wp.x, wp.y, wp.z, 0.71, 1.26, 0.08, {
        x: g.quaternion.x,
        y: g.quaternion.y,
        z: g.quaternion.z,
        w: g.quaternion.w,
      });
    }

    // Anchors — read live world positions from the exported empties.
    this._spawnEntryWorld = new THREE.Vector3(0, 0, 1.2); // contract fallback
    const spawn = g.getObjectByName("spawn_entry");
    if (spawn) spawn.getWorldPosition(this._spawnEntryWorld);
    else {
      this._spawnEntryWorld.applyMatrix4(g.matrixWorld);
      console.warn("[Museum] spawn_entry missing — using contract fallback");
    }
    const stairsDir = new THREE.Vector3(0, 0, -1).applyQuaternion(g.quaternion);
    this._stairsDir = { x: stairsDir.x, z: stairsDir.z }; // local −Z in world
    this._spawnFacing = Math.atan2(stairsDir.x, stairsDir.z); // face the stairs

    this._exitWorld = new THREE.Vector3();
    (g.getObjectByName("exitDoorRef") ?? g).getWorldPosition(this._exitWorld);

    this._roomLocal =
      g.getObjectByName("roomRef")?.position?.clone() ??
      new THREE.Vector3(15.32, -4.8, -8.8);

    // Stations — empties station_01..08 with userData.chapter.
    this.stations = [];
    g.traverse((o) => {
      const m = /^station_(\d\d)$/.exec(o.name);
      if (!m) return;
      const p = new THREE.Vector3();
      o.getWorldPosition(p);
      this.stations.push({
        chapter: o.userData?.chapter ?? parseInt(m[1], 10),
        pos: p,
      });
    });
    this.stations.sort((a, b) => a.chapter - b.chapter);

    this.#collectAnimProps(g);
    this.#applyGlowMaterials(g);
    this.#applyAccentTints(g);
    this.#positionLights(g);
    console.log(
      `[Museum] interior ready — ${colliderCount} colliders, ` +
        `${this.stations.length} stations`,
    );
  }

  /** floatProp_* bob+spin in place; orbitProp_* circle the island miniature. */
  #collectAnimProps(g) {
    this.floatProps = [];
    const orbiters = [];
    g.traverse((o) => {
      if (o.name.startsWith("floatProp_")) {
        this.floatProps.push({
          obj: o,
          baseY: o.position.y,
          phase: o.position.x * 2.7,
        });
      } else if (o.name.startsWith("orbitProp_")) {
        orbiters.push(o);
      }
    });
    // Exported objects are siblings in the group's local space, so orbit math
    // runs in local coords around the room-centre pivot (the miniature table).
    this._orbit = orbiters.map((o, i) => {
      const dx = o.position.x - this._roomLocal.x;
      const dz = o.position.z - this._roomLocal.z;
      return {
        obj: o,
        r: Math.hypot(dx, dz),
        a0: Math.atan2(dz, dx),
        y: o.position.y,
        speed: 0.45 + i * 0.13,
      };
    });
  }

  /** Swap torchFlame_* and runeGlow_* onto shared TSL materials — per-fragment
   *  world-position hashing gives every flame its own phase with ONE material
   *  and zero per-frame CPU. HDR colour (>1) feeds the bloom pass. */
  #applyGlowMaterials(g) {
    const uTime = this.uTime;
    const flameMat = new MeshBasicNodeMaterial();
    const seed = positionWorld.x.mul(7.13).add(positionWorld.z.mul(5.71));
    const flick = sin(uTime.mul(9.0).add(seed))
      .mul(0.5)
      .add(sin(uTime.mul(13.7).add(seed.mul(1.7))).mul(0.5))
      .mul(0.25)
      .add(1.0); // ≈ 0.5 .. 1.5
    // Flame cones are 0.3 tall, centred — remap local height to 0..1.
    const h = positionGeometry.y.mul(3.0).add(0.5).clamp(0.0, 1.0);
    flameMat.colorNode = mix(vec3(1.0, 0.62, 0.22), vec3(1.0, 0.3, 0.06), h)
      .mul(flick)
      .mul(2.4);

    const runeMat = new MeshBasicNodeMaterial({
      transparent: true,
      depthWrite: false,
    });
    runeMat.colorNode = vec3(0.45, 0.7, 1.0).mul(1.6);
    runeMat.opacityNode = sin(
      uTime.mul(1.3).add(positionWorld.x.mul(0.8)).add(positionWorld.z.mul(1.1)),
    )
      .mul(0.3)
      .add(0.5);

    g.traverse((o) => {
      if (!o.isMesh) return;
      if (o.name.startsWith("torchFlame_")) o.material = flameMat;
      else if (o.name.startsWith("runeGlow_")) o.material = runeMat;
    });
  }

  /** Colour-variety pass: each station's trim (header band + brass cap) takes
   *  its chapter's accent colour, and the four wall banners spread to four
   *  distinct tints — so the room reads as eight themed alcoves instead of a
   *  single brown. Clones are cached per (material, colour) pair; a dozen tiny
   *  materials in the cheapest scene on the site. */
  #applyAccentTints(g) {
    const cache = new Map();
    const tinted = (mat, hex, k) => {
      const key = `${mat.uuid}|${hex}|${k}`;
      let m = cache.get(key);
      if (!m) {
        m = mat.clone();
        m.color.lerp(new THREE.Color(hex), k);
        cache.set(key, m);
      }
      return m;
    };
    g.traverse((o) => {
      if (!o.isMesh) return;
      let m;
      if ((m = /^station(Header|Cap)_(\d\d)$/.exec(o.name))) {
        const accent = chapterById(parseInt(m[2], 10))?.accent;
        if (accent)
          o.material = tinted(o.material, accent, m[1] === "Cap" ? 0.8 : 0.55);
      } else if ((m = /^bannerCloth_(\d\d)$/.exec(o.name))) {
        const tint = BANNER_TINTS[(parseInt(m[1], 10) - 1) % BANNER_TINTS.length];
        if (tint) o.material = tinted(o.material, tint, 1);
      }
    });
  }

  // ── Interior lights ────────────────────────────────────────────────────────

  /** Created at BOOT, intensity 0, parked far below: adding a light later
   *  changes the shader light-count and recompiles every lit material (see the
   *  Lights-rig note in App.boot). Repositioned when the interior arrives. */
  #createInteriorLights() {
    this.lights = [];
    for (let i = 0; i < 4; i++) {
      const l = new THREE.PointLight(0xffb066, 0, 16, 1.8);
      l.position.set(DOOR_POS.x, -1000, DOOR_POS.z);
      this.scene.add(l);
      this.lights.push(l);
    }
  }

  #positionLights(g) {
    // Local (Y-up) spots: vestibule, landing, room W, room E — at torch height.
    const spots = [
      new THREE.Vector3(0, 2.1, 0),
      new THREE.Vector3(0, -0.2, -8.82),
      new THREE.Vector3(10.5, -2.2, -8.8),
      new THREE.Vector3(20.0, -2.2, -8.8),
    ];
    this.lights.forEach((l, i) => {
      const p = spots[Math.min(i, spots.length - 1)].clone();
      g.localToWorld(p);
      l.position.copy(p);
    });
  }

  // ── Portal crossings ───────────────────────────────────────────────────────

  async enter() {
    if (this._busy || this.isInside || !this._interiorReady || !this.doorLeaf)
      return;
    this._busy = true;
    this.#setPrompt(null);
    const c = this.player.controller;
    c.clearVirtualInput?.();
    this.audio?.playInteract?.(); // stand-in until the door-creak asset (Phase D)
    const outfits = this.player.character?.outfits;
    this._outfitBefore = outfits?.target ?? "default";
    this.#portalShow(this.doorPortal);
    await this.#swing(this.doorLeaf, DOOR_SWING_RAD, 0.75);
    // The character walks itself up to the threshold — into the swirl, not
    // teleported off the lawn. (Controller stays unlocked: virtual input only
    // runs while unlocked; a WASD press cancels it and the timeout proceeds.)
    const front = this.#doorFront();
    await this.#walkTo(
      DOOR_POS.x + front.x * 0.55,
      DOOR_POS.z + front.z * 0.55,
      { arrive: 0.35, timeout: 3.2 },
    );
    c.lock?.();
    this.audio?.playTeleportWoosh?.();
    this.audio?.duckAmbient?.(0.25, 400); // hushed until the underground loop (Phase D)
    await this.transitionFx.play(50, 58, async () => {
      this.#setInside(true);
      const p = this._spawnEntryWorld;
      const f = this._stairsDir ?? { x: 0, z: -1 };
      // Arrive just inside the exit door, facing the stairs — the walk-out
      // below makes it read as stepping THROUGH the same door.
      this.player.placeAt(
        p.x - f.x * 0.35,
        p.y + 0.05,
        p.z - f.z * 0.35,
        this._spawnFacing,
      );
      this.playerCamera.snapTo?.(p, this._spawnFacing);
      this.doorLeaf.rotation.y = 0; // shut silently behind the iris
      this.#portalHide(this.doorPortal);
    });
    this.audio?.playTeleportArrive?.();
    // First crossing: the secret is out — rare unlock, and the door joins the
    // map (markers + return teleport land OUTSIDE the door, never down here).
    this.achievements?.trigger?.("museum_found");
    this.discovery?.discover?.("museum");
    c.unlock?.();
    // Golden-wipe into the museum outfit while stepping out of the doorway.
    outfits?.set?.("museum", { duration: 1.6 });
    {
      const p = this._spawnEntryWorld;
      const f = this._stairsDir ?? { x: 0, z: -1 };
      await this.#walkTo(p.x + f.x * 1.1, p.z + f.z * 1.1, {
        arrive: 0.3,
        timeout: 2.0,
      });
    }
    this._busy = false;
  }

  async exit() {
    if (this._busy || !this.isInside) return;
    this._busy = true;
    this.#setPrompt(null);
    const c = this.player.controller;
    c.clearVirtualInput?.();
    this.audio?.playInteract?.();
    this.#portalShow(this.exitPortal);
    if (this.exitLeaf) await this.#swing(this.exitLeaf, DOOR_SWING_RAD, 0.75);
    // Walk into the doorway swirl before the iris fires.
    {
      const p = this._spawnEntryWorld;
      const f = this._stairsDir ?? { x: 0, z: -1 };
      await this.#walkTo(p.x - f.x * 0.35, p.z - f.z * 0.35, {
        arrive: 0.3,
        timeout: 3.2,
      });
    }
    c.lock?.();
    this.audio?.playTeleportWoosh?.();
    const land = this.#exitLanding();
    const front = this.#doorFront();
    // Re-emerge AT the outdoor door and walk out of it toward the clear
    // landing spot. The camera starts close (between character and door) so
    // the door panel can't fill the frame, then relaxes back out.
    const sx = DOOR_POS.x + front.x * 0.9;
    const sz = DOOR_POS.z + front.z * 0.9;
    const sy = (this.terrain?.heightAt?.(sx, sz) ?? this.groundY) + 0.05;
    const facing = Math.atan2(land.x - sx, land.z - sz);
    const cam = this.playerCamera.controls;
    const savedMinDistance = cam.minDistance;
    await this.transitionFx.play(50, 58, async () => {
      this.#setInside(false);
      this.player.placeAt(sx, sy, sz, facing);
      this.playerCamera.snapTo?.({ x: sx, y: sy, z: sz }, facing);
      cam.minDistance = 1.2;
      cam.dollyTo?.(1.4, false);
      if (this.exitLeaf) this.exitLeaf.rotation.y = 0;
      this.#portalHide(this.exitPortal);
    });
    this.audio?.duckAmbient?.(1.0, 600);
    this.audio?.playTeleportArrive?.();
    c.unlock?.();
    // Outfit melts back to whatever the player wore on the way in (App's
    // weather hysteresis takes over again outside).
    this.player.character?.outfits?.set?.(this._outfitBefore ?? "default");
    cam.dollyTo?.(
      Math.min(this._saved?.distance ?? 4, cam.maxDistance),
      true,
    );
    await this.#walkTo(land.x, land.z, { arrive: 0.35, timeout: 2.4 });
    cam.minDistance = savedMinDistance;
    this._busy = false;
  }

  /** Door front direction (local −Z) on the ground plane. */
  #doorFront() {
    return { x: -Math.sin(DOOR_YAW), z: -Math.cos(DOOR_YAW) };
  }

  /**
   * Scripted walk: steer the character to (x, z) via the controller's virtual
   * input (same channel as click-to-move — full walk animation + physics).
   * Resolves on arrival or timeout; a WASD press cancels the virtual input,
   * in which case the timeout still resolves the promise.
   */
  #walkTo(x, z, { arrive = 0.3, timeout = 2.6 } = {}) {
    const c = this.player.controller;
    if (!c?.setVirtualInput) return Promise.resolve();
    return new Promise((resolve) => {
      this._walk = { x, z, arrive, timeout, t: 0, resolve };
    });
  }

  #driveWalk(frameDelta, playerPos) {
    const w = this._walk;
    w.t += frameDelta;
    const dx = w.x - playerPos.x;
    const dz = w.z - playerPos.z;
    const dist = Math.hypot(dx, dz);
    if (dist < w.arrive || w.t > w.timeout) {
      this.player.controller.clearVirtualInput?.();
      this._walk = null;
      w.resolve();
      return;
    }
    this.player.controller.setVirtualInput?.({
      forward: Math.min(1, dist * 2.5), // ease off over the last metre
      strafe: 0,
      worldAngle: Math.atan2(dx, dz),
    });
  }

  /**
   * Pick a clear spot just outside the door for the return crossing — never
   * inside a rock/tree/lamp (navmask blockers) and never on a water-dipped
   * patch. Candidates fan out from the door's front, nearest-first; the
   * straight-ahead spot wins when it's clear.
   */
  #exitLanding() {
    const fx = -Math.sin(DOOR_YAW);
    const fz = -Math.cos(DOOR_YAW);
    const a0 = Math.atan2(fz, fx);
    for (const r of [1.9, 2.8, 3.8]) {
      for (const da of [0, 0.6, -0.6, 1.2, -1.2, 1.9, -1.9, Math.PI]) {
        const a = a0 + da;
        const x = DOOR_POS.x + Math.cos(a) * r;
        const z = DOOR_POS.z + Math.sin(a) * r;
        const h = this.terrain?.heightAt?.(x, z) ?? this.groundY;
        if (h < 0.05) continue; // dips toward water — never land wet
        if (this.navmask && !this.navmask.hasClearance?.(x, z, 1.2)) continue;
        return {
          x,
          z,
          y: h + 0.1,
          facing: Math.atan2(x - DOOR_POS.x, z - DOOR_POS.z), // walk away from the door
        };
      }
    }
    // Worst case (everything blocked): straight out the front anyway.
    const x = DOOR_POS.x + fx * 1.9;
    const z = DOOR_POS.z + fz * 1.9;
    return {
      x,
      z,
      y: (this.terrain?.heightAt?.(x, z) ?? this.groundY) + 0.1,
      facing: Math.atan2(fx, fz),
    };
  }

  /**
   * Map-marker descriptor for App's mapSections. `hidden: true` keeps it off
   * the mini-map/overlay AND out of proximity auto-discovery until the first
   * crossing calls discovery.discover('museum'). The landing reuses the
   * navmask-checked exit-landing search, flipped to face the door — a map
   * teleport always arrives OUTSIDE on the grass, never in the basement.
   */
  mapSection() {
    const land = this.#exitLanding();
    return {
      id: "museum",
      name: "Museum",
      color: "#8a63ff", // the portal-swirl violet
      position: [DOOR_POS.x, 0, DOOR_POS.z],
      landing: {
        x: land.x,
        z: land.z,
        facing: Math.atan2(DOOR_POS.x - land.x, DOOR_POS.z - land.z),
      },
      hidden: true,
    };
  }

  #swing(leaf, target, duration) {
    return new Promise((resolve) => {
      gsap.killTweensOf(leaf.rotation);
      gsap.to(leaf.rotation, {
        y: target,
        duration,
        ease: "power2.out",
        onComplete: resolve,
      });
    });
  }

  // ── Interior state swap ────────────────────────────────────────────────────

  #setInside(active) {
    this.isInside = active;
    document.body.classList.toggle("in-museum", active);
    if (this.interiorGroup) this.interiorGroup.visible = active;
    // The beacon shaft/motes are frustumCulled=false — hide the whole door
    // group while underground so they don't draw into the void.
    if (this.doorGroup) this.doorGroup.visible = !active;
    this.lights.forEach((l, i) => {
      l.intensity = active ? Museum.#LIGHT_INTENSITY[i] : 0;
    });

    const p = this.player;
    const cam = this.playerCamera.controls;
    p.interiorMode = active;
    // Orbit occlusion: gallery wall boxes while inside, the door's own boxes
    // while outside — the camera can neither poke through a gallery wall nor
    // park behind the door panel after the exit walk-out.
    this.playerCamera.collisionMeshes = active
      ? this._cameraBlockers
      : this._doorCameraBlockers;
    if (active) {
      this._saved = {
        respawnFallY: p.respawnFallY,
        maxDistance: cam.maxDistance,
        minPolarAngle: cam.minPolarAngle,
        distance: cam.distance,
        minTargetY: this.playerCamera.minTargetY ?? 0.4,
      };
      p.respawnFallY = this.interiorY - 12;
      p.respawnPoint = {
        x: this._spawnEntryWorld.x,
        y: this._spawnEntryWorld.y + 0.1,
        z: this._spawnEntryWorld.z,
      };
      cam.maxDistance = CAMERA_MAX_DISTANCE;
      cam.minPolarAngle = CAMERA_MIN_POLAR;
      // PlayerCamera.follow() clamps its orbit target to y ≥ minTargetY (the
      // wading guard). Drop the floor to the basement, or the camera stays
      // pinned at the surface 45m above the character — black screen.
      this.playerCamera.minTargetY = this.interiorY - 5;
      this.audio?.setOceanProximity?.(1e9, 45); // shore ambience falls silent
    } else if (this._saved) {
      p.respawnFallY = this._saved.respawnFallY;
      p.respawnPoint = null;
      cam.maxDistance = this._saved.maxDistance;
      cam.minPolarAngle = this._saved.minPolarAngle;
      this.playerCamera.minTargetY = this._saved.minTargetY;
      cam.dollyTo?.(
        Math.min(this._saved.distance, this._saved.maxDistance),
        false,
      );
    }
    this.onInteriorChange?.(active);
  }

  // ── Prompt + placeholder panel ─────────────────────────────────────────────

  #installDom() {
    this.promptEl = document.createElement("div");
    this.promptEl.className = "billboard-prompt hidden";
    this.promptEl.innerHTML = `
      <span class="key">E</span>
      <span class="label"></span>
    `;
    document.body.appendChild(this.promptEl);

    this.panelEl = document.createElement("div");
    this.panelEl.className = "project-panel museum-panel hidden";
    this.panelEl.innerHTML = `
      <button class="panel-close" aria-label="Close">×</button>
      <div class="panel-scroll">
        <div class="panel-accent"></div>
        <h2 class="panel-title"></h2>
        <p class="panel-meta"></p>
        <h3 class="museum-page-heading"></h3>
        <div class="panel-description"></div>
      </div>
      <div class="panel-nav museum-pager">
        <button class="museum-prev" aria-label="Previous page">‹ Prev</button>
        <span class="panel-counter"></span>
        <button class="museum-next" aria-label="Next page">Next ›</button>
      </div>
      <div class="panel-hint">← → PAGES · ESC TO RETURN</div>
    `;
    this.panelEl
      .querySelector(".panel-close")
      .addEventListener("click", () => this.#hidePanel());
    this.panelEl
      .querySelector(".museum-prev")
      .addEventListener("click", () => this.#turnPage(-1));
    this.panelEl
      .querySelector(".museum-next")
      .addEventListener("click", () => this.#turnPage(1));
    document.body.appendChild(this.panelEl);
  }

  #bindKeys() {
    this._onKeyDown = (e) => {
      if (document.body.classList.contains("booting")) return;
      if (e.code === "Escape" && this._panelOpen) {
        e.preventDefault();
        this.#hidePanel();
        return;
      }
      if (this._panelOpen && (e.code === "ArrowLeft" || e.code === "ArrowRight")) {
        e.preventDefault();
        this.#turnPage(e.code === "ArrowRight" ? 1 : -1);
        return;
      }
      if (e.code !== "KeyE" || e.repeat) return;
      if (this._panelOpen) {
        this.#hidePanel();
        return;
      }
      const armed = this._armed;
      if (!armed || this._busy) return;
      if (armed.action === "enter") this.enter();
      else if (armed.action === "exit") this.exit();
      else if (armed.action === "station") this.#showPanel(armed.chapter);
    };
    window.addEventListener("keydown", this._onKeyDown);
  }

  #setPrompt(armed) {
    const same =
      (!armed && !this._armed) ||
      (armed &&
        this._armed &&
        armed.action === this._armed.action &&
        armed.chapter === this._armed.chapter);
    this._armed = armed;
    if (same) return;
    if (!armed) {
      this.promptEl.classList.add("hidden");
      return;
    }
    const label = this.promptEl.querySelector(".label");
    label.innerHTML = armed.name
      ? `${armed.label} <strong class="project-name"></strong>`
      : armed.label;
    if (armed.name)
      label.querySelector(".project-name").textContent = armed.name;
    this.promptEl.classList.remove("hidden");
  }

  #showPanel(chapter) {
    const data = chapterById(chapter);
    if (!data) return;
    this._panelOpen = true;
    this._chapterData = data;
    this._pageIndex = 0;
    this.player.controller.paused = true;
    this.#setPrompt(null);
    this.audio?.playMenuOpen?.();
    this.panelEl.querySelector(".panel-title").textContent = data.title;
    this.panelEl.querySelector(".panel-meta").textContent =
      `Chapter ${data.id} of ${MUSEUM_CHAPTERS.length} — the making of this world`;
    this.panelEl.querySelector(".panel-accent").style.background = data.accent;
    this.#renderPage();
    this.panelEl.classList.remove("hidden");
  }

  #turnPage(dir) {
    const data = this._chapterData;
    if (!this._panelOpen || !data) return;
    const next = this._pageIndex + dir;
    if (next < 0 || next >= data.pages.length) return;
    this._pageIndex = next;
    this.audio?.playInteract?.();
    this.#renderPage();
  }

  #renderPage() {
    const data = this._chapterData;
    const page = data.pages[this._pageIndex];
    this.panelEl.querySelector(".museum-page-heading").textContent =
      page.heading;

    const desc = this.panelEl.querySelector(".panel-description");
    desc.textContent = "";
    const paragraphs = Array.isArray(page.body) ? page.body : [page.body];
    for (const text of paragraphs) {
      const p = document.createElement("p");
      p.textContent = text;
      desc.appendChild(p);
    }

    const last = data.pages.length - 1;
    this.panelEl.querySelector(".museum-prev").disabled = this._pageIndex === 0;
    this.panelEl.querySelector(".museum-next").disabled =
      this._pageIndex === last;
    this.panelEl.querySelector(".panel-counter").textContent =
      `${this._pageIndex + 1} / ${data.pages.length}`;
    this.panelEl.querySelector(".panel-scroll").scrollTop = 0;
  }

  #hidePanel() {
    if (!this._panelOpen) return;
    this._panelOpen = false;
    this.panelEl.classList.add("hidden");
    this.audio?.playMenuClose?.();
    this.player.controller.paused = false;
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────

  update(elapsed, frameDelta, playerPos, nightFactor = 0) {
    this.uTime.value = elapsed;
    this.uBeaconBoost.value = 0.45 + nightFactor * 0.8;

    if (this._walk) this.#driveWalk(frameDelta, playerPos);

    if (!this.isInside) {
      if (!this._doorReady) return;
      const dx = playerPos.x - DOOR_POS.x;
      const dz = playerPos.z - DOOR_POS.z;
      const d2 = dx * dx + dz * dz;
      if (d2 < LOAD_RADIUS * LOAD_RADIUS) this.#maybeLoadInterior();
      if (this._busy || this.player.controller.paused) {
        this.#setPrompt(null);
        return;
      }
      this.#setPrompt(
        d2 < DOOR_PROMPT_RADIUS * DOOR_PROMPT_RADIUS && this._interiorReady
          ? { action: "enter", label: "Open the door" }
          : null,
      );
      return;
    }

    // Inside — drive the crafted props.
    for (const f of this.floatProps) {
      f.obj.position.y = f.baseY + Math.sin(elapsed * 0.9 + f.phase) * 0.07;
      f.obj.rotation.y += frameDelta * 0.5;
    }
    for (const o of this._orbit) {
      const a = o.a0 + elapsed * o.speed;
      o.obj.position.set(
        this._roomLocal.x + Math.cos(a) * o.r,
        o.y + Math.sin(elapsed * 1.7 + o.a0) * 0.04,
        this._roomLocal.z + Math.sin(a) * o.r,
      );
    }

    if (this._panelOpen || this._busy || this.player.controller.paused) {
      this.#setPrompt(null);
      return;
    }
    const dxE = playerPos.x - this._exitWorld.x;
    const dzE = playerPos.z - this._exitWorld.z;
    if (dxE * dxE + dzE * dzE < EXIT_PROMPT_RADIUS * EXIT_PROMPT_RADIUS) {
      this.#setPrompt({ action: "exit", label: "Leave the museum" });
      return;
    }
    let best = null;
    let bestD2 = STATION_PROMPT_RADIUS * STATION_PROMPT_RADIUS;
    for (const s of this.stations) {
      const sx = playerPos.x - s.pos.x;
      const sz = playerPos.z - s.pos.z;
      const d2 = sx * sx + sz * sz;
      if (d2 < bestD2) {
        bestD2 = d2;
        best = s;
      }
    }
    this.#setPrompt(
      best
        ? {
            action: "station",
            chapter: best.chapter,
            label: "Read",
            name: chapterById(best.chapter)?.title ?? `Chapter ${best.chapter}`,
          }
        : null,
    );
  }
}
