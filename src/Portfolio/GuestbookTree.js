import gsap from "gsap";
import * as THREE from "three/webgpu";
import { MeshStandardNodeMaterial, MeshBasicNodeMaterial } from "three/webgpu";
import {
  uniform, uv, float, vec3, sin, length, smoothstep, mix,
} from "three/tsl";
import { Foliage } from "../World/Foliage.js";
import { GuestbookView } from "../UI/GuestbookView.js";
import { Confetti } from "../UI/Confetti.js";

/**
 * The Guestbook Tree — a landmark where visitors leave a friendly note that
 * others walk up and read. Framed as a guestbook, not a mystical ritual, so
 * people actually feel invited to sign it:
 * notes hang as warm glowing tags swaying in the wind, collected at ONE
 * discoverable spot. Walk up → press E → read others' notes + leave your own.
 *
 * Self-contained: owns its proximity prompt, key handling, camera dolly and the
 * reading/compose overlay (GuestbookView). It does NOT touch the shared
 * Interaction system — near the tree the player isn't near any billboard/board,
 * so the global E handler is a no-op and only this one acts.
 *
 * Asset: reuses an existing low-poly tree GLB (no new asset), re-tinted +
 * scaled to read as a special landmark; tags + beacon are procedural (TSL),
 * mirroring ResumeBook.js. WebGPU → all custom shading is TSL node materials.
 */

const TREE_GLB = "/models/nature/tree-oak.glb";
const TREE_HEIGHT = 6.5; // target height (m) — bigger than scattered trees
const BEACON_HEIGHT = 7.5;
const PROXIMITY = 5.0; // prompt radius (XZ)
const STANDOFF = 5.0; // camera distance for the compose / overview pose
const READ_STANDOFF = 2.2; // camera distance from a single note's tag while reading
const MAX_TAGS = 28; // hanging tags (decorative; count tracks whisper volume)
const ZOOM_DURATION = 1.1;

// Golden canopy — two-tone (shaded → lit), distinct from the world's green oaks.
const GOLD_SHADE = "#b07d18";
const GOLD_LIT = "#ffd86a";
// Leaf-blob anchor sampling over the stripped green canopy (mirrors GlbV3World).
const ANCHOR_SPACING = 0.95; // m between blobs (denser → this is a feature tree)
const ANCHOR_SCALE = 0.62; // blob scale = spacing × this × jitter
const ANCHOR_JITTER = 0.2; // ±deterministic size variation

export class GuestbookTree {
  constructor({
    scene, camera, playerCamera, player, controller,
    terrain, physics, audio = null, social, loader,
    wind = null, timeOfDay = null,
    x = -2, z = 18,
  }) {
    this.scene = scene;
    this.camera = camera;
    this.playerCamera = playerCamera;
    this.player = player;
    this.controller = controller;
    this.terrain = terrain;
    this.physics = physics;
    this.audio = audio;
    this.social = social;
    this.loader = loader;
    this.wind = wind;
    this.timeOfDay = timeOfDay;

    this.baseX = x;
    this.baseZ = z;
    this.groundY = terrain?.heightAt ? terrain.heightAt(x, z) : 0;

    this.open = false;
    this.zooming = false;
    this._glow = 1;
    this._beacon = 1;
    this._tagPivots = [];
    this._returnPos = null;

    this.group = new THREE.Group();
    this.group.name = "guestbookTree";
    this.group.position.set(x, this.groundY, z);
    scene.add(this.group);

    this.#buildBeacon();
    this.#buildGlowDisc();
    this.#buildLight();

    this.view = new GuestbookView({
      social: this.social,
      audio: this.audio,
      onPrev: () => this.#nav(-1),
      onNext: () => this.#nav(1),
      onSign: () => this.#openCompose(),
      onBack: () => this.#backToReading(),
      onClose: () => this.close(),
      onPosted: () => this.#onPosted(),
    });
    this.confetti = new Confetti();
    this._mode = "reading"; // 'reading' | 'compose'
    this._index = 0;
    this._tour = []; // [{ worldPos: Vector3, note }] — visible tags bound to notes

    this.#buildPrompt();
    this.#installKeys();

    // Re-bind the hanging tags to notes whenever the data changes (load, post).
    this.social?.onChange?.(() => this.#bindNotes());
  }

  /**
   * Load + place the tree GLB, strip its flat low-poly green canopy and grow a
   * golden SDF leaf cloud in its place (same Foliage system the world's trees
   * use), then hang the note tags. Fire-and-forget.
   */
  async load() {
    let gltf, sdf;
    try {
      [gltf, sdf] = await Promise.all([
        this.loader.loadGLTF(TREE_GLB),
        this.#loadFoliageSDF(),
      ]);
    } catch (err) {
      console.warn("[GuestbookTree] tree GLB missing — beacon only:", err);
      return this;
    }
    const tree = gltf.scene;
    tree.updateMatrixWorld(true);
    const rawBox = new THREE.Box3().setFromObject(tree);
    const rawH = rawBox.getSize(new THREE.Vector3()).y || 1;
    tree.scale.setScalar(TREE_HEIGHT / rawH);
    tree.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(tree);
    tree.position.y -= box.min.y; // seat the trunk base on the ground
    this.tree = tree;
    this.group.add(tree);
    this.group.updateMatrixWorld(true);

    const full = new THREE.Box3().setFromObject(tree);
    this._height = full.max.y - full.min.y;

    // Split meshes: leaves (material "leafsGreen") vs trunk (material "woodBark").
    const canopyMeshes = [];
    tree.traverse((c) => {
      if (!c.isMesh) return;
      const name = (c.material?.name || "").toLowerCase();
      if (name.includes("leaf")) {
        canopyMeshes.push(c);
      } else {
        // Trunk — warm bark tint so it sits in the dusk palette.
        c.castShadow = true;
        c.receiveShadow = true;
        const mats = Array.isArray(c.material) ? c.material : [c.material];
        mats.forEach((m) => {
          if (m?.color) m.color.lerp(new THREE.Color(0x6a4a2a), 0.15);
          if (m) m.needsUpdate = true;
        });
      }
    });

    // Canopy region (world) for tags + foliage extent, then grow golden leaves.
    const canopyBox = new THREE.Box3();
    for (const m of canopyMeshes) canopyBox.expandByObject(m);
    const anchors = this.#sampleCanopyAnchors(canopyMeshes);
    for (const m of canopyMeshes) {
      m.removeFromParent();
      m.geometry?.dispose();
    }

    if (sdf && anchors.length && this.wind) {
      this.foliage = new Foliage(
        this.scene,
        this.wind,
        sdf,
        [{ key: "guestbookTree", refs: anchors, colorA: GOLD_SHADE, colorB: GOLD_LIT }],
        { shellCards: 150 },
      );
      this.foliage.setSunDirection(this.timeOfDay?.sunOffset);
    }

    this.#addCollider();
    // Tag region in LOCAL space (group is translated only, no rotation/scale).
    const cSize = canopyBox.getSize(new THREE.Vector3());
    const localCenterY = (canopyBox.min.y + canopyBox.max.y) / 2 - this.group.position.y;
    const canopyR = Math.max(cSize.x, cSize.z) * 0.42 || 1.5;
    this.#buildTags(localCenterY, canopyR, cSize.y * 0.5 || 1.5);
    return this;
  }

  #loadFoliageSDF() {
    return this.loader
      .loadTexture("/textures/foliage/foliageSDF.png", {
        ktx2Url: "/textures/foliage/foliageSDF.ktx2",
      })
      .then((tex) => {
        tex.minFilter = THREE.NearestFilter;
        tex.magFilter = THREE.NearestFilter;
        tex.generateMipmaps = false;
        tex.wrapS = THREE.ClampToEdgeWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;
        tex.colorSpace = THREE.NoColorSpace;
        tex.needsUpdate = true;
        return tex;
      })
      .catch(() => null);
  }

  /** Poisson-thin the canopy verts into world-space leaf-blob anchors (mirrors
   *  GlbV3World.#extractTreeFoliage so the look matches the world's oaks). */
  #sampleCanopyAnchors(meshes) {
    const spacing2 = ANCHOR_SPACING * ANCHOR_SPACING;
    const v = new THREE.Vector3();
    const accepted = [];
    for (const mesh of meshes) {
      const pos = mesh.geometry?.attributes?.position;
      if (!pos) continue;
      mesh.updateWorldMatrix(true, false);
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i).applyMatrix4(mesh.matrixWorld);
        let ok = true;
        for (const a of accepted) {
          if (a.distanceToSquared(v) < spacing2) { ok = false; break; }
        }
        if (ok) accepted.push(v.clone());
      }
    }
    return accepted.map((p) => {
      const key = (Math.round(p.x * 13.1) ^ Math.round(p.y * 3.3) ^ Math.round(p.z * 7.7)) >>> 0;
      const h = (Math.imul(key | 1, 2654435761) >>> 0) / 4294967296;
      const jitter = 1 + (h - 0.5) * 2 * ANCHOR_JITTER;
      return { position: p, scale: ANCHOR_SPACING * ANCHOR_SCALE * jitter };
    });
  }

  // ── World position helpers ─────────────────────────────────────────────────
  get position() {
    return new THREE.Vector3(this.baseX, this.groundY + 1.5, this.baseZ);
  }

  near(playerPosition, radius = PROXIMITY) {
    const dx = playerPosition.x - this.baseX;
    const dz = playerPosition.z - this.baseZ;
    return dx * dx + dz * dz <= radius * radius;
  }

  // ── Trunk collider (thin — walk under the canopy, not through the trunk) ────
  #addCollider() {
    if (!this.physics?.addStaticCylinder) return;
    this.physics.addStaticCylinder(
      this.baseX, this.groundY, this.baseZ, 0.55, this._height || TREE_HEIGHT,
    );
  }

  // ── Hanging tags (warm glowing notes; count tracks whisper volume) ─────────
  // centerY/canopyR/vSpan are LOCAL to this.group (only translated, no scale).
  #buildTags(centerY, canopyR, vSpan) {
    const tagMat = new MeshStandardNodeMaterial({
      color: new THREE.Color(0xf3e2b0),
      roughness: 0.7,
      metalness: 0.0,
      emissive: new THREE.Color(0xffcf7a),
      emissiveIntensity: 0.85,
      side: THREE.DoubleSide,
      transparent: true,
    });
    this._tagMat = tagMat;
    const tagGeo = new THREE.PlaneGeometry(0.16, 0.22);

    for (let i = 0; i < MAX_TAGS; i++) {
      const a = (i / MAX_TAGS) * Math.PI * 2 + Math.random() * 0.4;
      const r = canopyR * (0.55 + Math.random() * 0.5);
      const y = centerY + (Math.random() - 0.5) * vSpan;
      // Pivot at the branch anchor; the tag hangs ~0.3m below and sways.
      const pivot = new THREE.Group();
      pivot.position.set(Math.cos(a) * r, y, Math.sin(a) * r);
      const tag = new THREE.Mesh(tagGeo, tagMat);
      tag.position.y = -0.28;
      pivot.add(tag);
      pivot.userData.phase = Math.random() * Math.PI * 2;
      pivot.userData.amp = 0.12 + Math.random() * 0.12;
      pivot.visible = false; // revealed by #bindNotes
      this.group.add(pivot);
      this._tagPivots.push(pivot);
    }
    this.#bindNotes();
  }

  /**
   * Bind the hanging tags to real notes and build the camera-tour list. Tag i
   * (for i < note count) represents notes[i] and is tourable; a friendly minimum
   * of tags stays visible so the canopy never looks bare. Tag world positions
   * feed #focusNote so the camera can fly to each note.
   */
  #bindNotes() {
    if (!this._tagPivots.length) return;
    const notes = this.social?.whispers ?? [];
    const noteCount = Math.min(notes.length, MAX_TAGS);
    const shown = Math.max(6, noteCount); // keep the tree looking full
    this._tour = [];
    this._tagPivots.forEach((p, i) => {
      p.visible = i < Math.min(MAX_TAGS, shown);
      if (i < noteCount) {
        p.userData.note = notes[i];
        this._tour.push({
          note: notes[i],
          worldPos: new THREE.Vector3(
            this.group.position.x + p.position.x,
            this.group.position.y + p.position.y - 0.28,
            this.group.position.z + p.position.z,
          ),
        });
      } else {
        p.userData.note = null;
      }
    });
    if (this._index >= this._tour.length) this._index = 0;
  }

  // ── Beacon / glow / light (mirrors ResumeBook) ─────────────────────────────
  #buildBeacon() {
    const uTime = uniform(0);
    const uBeacon = uniform(1);
    const geo = new THREE.CylinderGeometry(0.6, 0.18, BEACON_HEIGHT, 28, 1, true);
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false,
      side: THREE.DoubleSide, blending: THREE.AdditiveBlending,
    });
    const v = uv().y;
    const pulse = float(0.7).add(sin(uTime.mul(1.5)).mul(0.16));
    const fade = v.oneMinus().pow(1.7).mul(smoothstep(0.0, 0.05, v));
    mat.colorNode = mix(vec3(1.0, 0.78, 0.42), vec3(1.0, 0.95, 0.8), v.oneMinus());
    mat.opacityNode = fade.mul(pulse).mul(0.45).mul(uBeacon);
    mat.uniforms = { uTime, uBeacon };
    const beacon = new THREE.Mesh(geo, mat);
    beacon.position.y = BEACON_HEIGHT / 2 + 0.05;
    beacon.frustumCulled = false;
    this.beacon = beacon;
    this.group.add(beacon);
  }

  #buildGlowDisc() {
    const mat = new MeshBasicNodeMaterial({
      transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    });
    const d = length(uv().sub(0.5));
    mat.colorNode = vec3(1.0, 0.74, 0.4);
    mat.opacityNode = smoothstep(0.5, 0.05, d).mul(0.34);
    const disc = new THREE.Mesh(new THREE.CircleGeometry(2.0, 40), mat);
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = 0.04;
    disc.frustumCulled = false;
    this.group.add(disc);
  }

  #buildLight() {
    const light = new THREE.PointLight(0xffcf8a, 5, 8, 2);
    light.position.set(0, 2.4, 0);
    this._lightBase = 5;
    this.light = light;
    this.group.add(light);
  }

  // ── Proximity prompt (reuses the shared billboard-prompt styling) ──────────
  #buildPrompt() {
    this.promptEl = document.createElement("div");
    this.promptEl.className = "billboard-prompt hidden";
    this.promptEl.innerHTML = `
      <span class="key">E</span>
      <span class="label">Open <strong class="project-name">the guestbook</strong></span>
    `;
    document.body.appendChild(this.promptEl);
  }

  #installKeys() {
    this._onKey = (e) => {
      if (e.code === "KeyE") {
        const el = document.activeElement;
        if (el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT")) return;
        if (this.open || this.zooming) return;
        if (this._near && !this.controller?.paused) this.enter();
      } else if (!this.open) {
        return;
      } else if (e.code === "Escape" && !this.zooming) {
        this.close();
      } else if (this._mode === "reading" && !this.zooming) {
        // Tour the notes with arrows or A/D (movement is paused, so safe).
        if (e.code === "ArrowLeft" || e.code === "KeyA") this.#nav(-1);
        else if (e.code === "ArrowRight" || e.code === "KeyD") this.#nav(1);
      }
    };
    window.addEventListener("keydown", this._onKey);
  }

  // ── Open / close + camera tour ─────────────────────────────────────────────
  enter() {
    if (this.open || this.zooming) return;
    this.open = true;
    this.#hidePrompt();
    this.audio?.playMenuOpen?.();
    this.controller.paused = true;
    this.playerCamera.locked = true;
    if (this.player?.character?.root) this.player.character.root.visible = false;
    gsap.to(this, { _glow: 1.8, duration: 0.5, ease: "power2.out" });
    gsap.to(this, { _beacon: 0.25, duration: 0.5, ease: "power2.out" });

    // Stash the camera pose to return to on close.
    if (!this._returnPos) {
      this._returnPos = new THREE.Vector3();
      this._returnLook = new THREE.Vector3();
    }
    this._returnPos.copy(this.camera.position);
    const dir = new THREE.Vector3();
    this.camera.getWorldDirection(dir);
    this._returnLook.copy(this._returnPos).add(dir);

    this.#bindNotes();
    if (this._tour.length) {
      this._index = 0;
      this.#focusNote(0);
    } else {
      // No notes yet — go straight to composing the first one.
      this.#openCompose();
    }
  }

  /** Fly the camera to note `i`'s hanging tag and show its caption. */
  #focusNote(i) {
    this._mode = "reading";
    this._index = ((i % this._tour.length) + this._tour.length) % this._tour.length;
    const entry = this._tour[this._index];
    const tag = entry.worldPos;
    // Stand just outside the canopy, on the line from the trunk through the tag,
    // looking back at the tag.
    const dx = tag.x - this.baseX;
    const dz = tag.z - this.baseZ;
    let len = Math.hypot(dx, dz);
    let ux = len > 0.05 ? dx / len : 0;
    let uz = len > 0.05 ? dz / len : -1; // fallback: face from the spawn side
    const camPos = new THREE.Vector3(
      tag.x + ux * READ_STANDOFF,
      tag.y + 0.25,
      tag.z + uz * READ_STANDOFF,
    );
    this.#dolly(camPos, tag, () =>
      this.view.showReading(entry.note, this._index, this._tour.length),
    );
  }

  #nav(dir) {
    if (this._mode !== "reading" || this._tour.length <= 1 || this.zooming) return;
    this.audio?.playInteract?.();
    this.#focusNote(this._index + dir);
  }

  /** Switch to the compose card with a pulled-back view of the whole tree. */
  #openCompose() {
    this._mode = "compose";
    const playerPos = this.player?.group?.position ?? this.player?.position;
    const { position, lookAt } = this.#focusPose(playerPos);
    this.#dolly(position, lookAt, () =>
      this.view.showCompose({ hasNotes: this._tour.length > 0 }),
    );
  }

  #backToReading() {
    if (this._tour.length) this.#focusNote(this._index);
    else this.close();
  }

  /** A note was just posted — celebrate, rebind tags, and fly to it. */
  #onPosted() {
    this.confetti.burst({ count: 60 });
    this.#bindNotes();
    // The new note is newest → index 0. Fly there after a beat so the success
    // line is read first.
    setTimeout(() => {
      if (this.open) this.#focusNote(0);
    }, 900);
  }

  /** Shared camera tween (position + look) with a zoom guard. */
  #dolly(position, lookAt, onComplete) {
    this.zooming = true;
    gsap.killTweensOf(this.camera.position);
    const dir = new THREE.Vector3();
    this.camera.getWorldDirection(dir);
    const lookProxy = this.camera.position.clone().add(dir);
    gsap.killTweensOf(lookProxy);
    gsap.to(lookProxy, {
      x: lookAt.x, y: lookAt.y, z: lookAt.z,
      duration: ZOOM_DURATION, ease: "power2.inOut",
    });
    gsap.to(this.camera.position, {
      x: position.x, y: position.y, z: position.z,
      duration: ZOOM_DURATION, ease: "power2.inOut",
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.camera.lookAt(lookAt);
        this.zooming = false;
        onComplete?.();
      },
    });
  }

  close() {
    if (!this.open || this.zooming) return;
    this.open = false;
    this.zooming = true;
    this.audio?.playMenuClose?.();
    this.view.hide();
    gsap.to(this, { _glow: 1, duration: 0.6, ease: "power2.inOut" });
    gsap.to(this, { _beacon: 1, duration: 0.8, ease: "power2.inOut" });

    const tmp = new THREE.Vector3();
    this.camera.getWorldDirection(tmp);
    const lookProxy = this.camera.position.clone().add(tmp);
    gsap.to(lookProxy, {
      x: this._returnLook.x, y: this._returnLook.y, z: this._returnLook.z,
      duration: ZOOM_DURATION, ease: "power2.inOut",
    });
    gsap.to(this.camera.position, {
      x: this._returnPos.x, y: this._returnPos.y, z: this._returnPos.z,
      duration: ZOOM_DURATION, ease: "power2.inOut",
      onUpdate: () => this.camera.lookAt(lookProxy),
      onComplete: () => {
        this.zooming = false;
        this.controller.paused = false;
        this.playerCamera.locked = false;
        this.playerCamera.resync?.();
        if (this.player?.character?.root) this.player.character.root.visible = true;
      },
    });
  }

  #focusPose(playerPos) {
    const dx = (playerPos?.x ?? 0) - this.baseX;
    const dz = (playerPos?.z ?? 0) - this.baseZ;
    const len = Math.hypot(dx, dz) || 1;
    const ux = dx / len;
    const uz = dz / len;
    const midY = this.groundY + (this._height ?? TREE_HEIGHT) * 0.5;
    return {
      position: new THREE.Vector3(
        this.baseX + ux * STANDOFF, this.groundY + 2.6, this.baseZ + uz * STANDOFF,
      ),
      lookAt: new THREE.Vector3(this.baseX, midY, this.baseZ),
    };
  }

  #showPrompt() {
    this.promptEl.classList.remove("hidden");
  }
  #hidePrompt() {
    this.promptEl.classList.add("hidden");
  }

  // ── Per-frame ──────────────────────────────────────────────────────────────
  update(elapsed, _dt, playerPosition) {
    if (this.foliage) {
      this.foliage.setSunDirection(this.timeOfDay?.sunOffset);
      if (playerPosition) this.foliage.setPlayerPos(playerPosition);
    }
    if (this.beacon) {
      this.beacon.material.uniforms.uTime.value = elapsed;
      this.beacon.material.uniforms.uBeacon.value = this._beacon;
    }
    if (this.light) {
      this.light.intensity =
        (this._lightBase + Math.sin(elapsed * 2.6) * 0.5) * this._glow;
    }
    if (this._tagMat) this._tagMat.emissiveIntensity = 0.85 * this._glow;
    // Tags sway like leaves in the wind.
    for (const p of this._tagPivots) {
      if (!p.visible) continue;
      p.rotation.z = Math.sin(elapsed * 1.3 + p.userData.phase) * p.userData.amp;
      p.rotation.x = Math.cos(elapsed * 1.0 + p.userData.phase) * p.userData.amp * 0.5;
    }

    // Proximity prompt — only while free-roaming (no modal up).
    const near = playerPosition ? this.near(playerPosition) : false;
    this._near = near;
    if (near && !this.open && !this.zooming && !this.controller?.paused) {
      this.#showPrompt();
    } else {
      this.#hidePrompt();
    }
  }
}
