import * as THREE from 'three';

/**
 * Underwater + jumping marine life: fish, seahorses, sharks, dolphins.
 *
 * All creatures are static GLBs from /models/wildlife/. The module loads
 * each model once and clones it per instance — every clone gets its own
 * cloned material so day/night bioluminescent emissive can be toggled
 * per-fish without affecting the others.
 *
 * Behaviour rules (one place rather than scattered per-type):
 *   - Fish + goldfish + dolphins: circle slowly between an inner/outer
 *     radius, dart away if the player gets within 10 m.
 *   - Seahorses: hover near the shore, bob vertically more than fish,
 *     swim at ~1/5 the speed.
 *   - Sharks: deeper, faster, slow wide turns, do NOT react to player.
 *   - Dolphins: occasionally jump in a parabolic arc, splash on re-entry.
 *
 * Public API:
 *   - load()                           — fire-and-forget; rejects only on
 *                                        unexpected internal errors.
 *   - update(delta, elapsed, playerPos) — per-frame swim + jump tick.
 *   - setMode('day' | 'night')          — bioluminescence on a few fish at
 *                                        night, splash colour shift, etc.
 *   - setWater(water)                   — hand the Water reference in so
 *                                        dolphin re-entry can call
 *                                        water.spawnSplash().
 */

// All distances in metres, all speeds in m/s.
const VISIBLE_RANGE_MAX = 82; // beyond this from the camera, hide creatures
const SHORE_REVEAL_RADIUS = 38; // keep spawn clean; reveal once the player approaches water
const PLAYER_STARTLE_RANGE = 10;
const JUMP_INTERVAL_RANGE = [3, 3.4]; // seconds between visible dolphin/shark breaches
const ISLAND_RADIUS = 45;             // matches Water.ISLAND_RADIUS
const BIOLUMINESCENT_COUNT = 4;        // 3-4 glowing fish at night

const FISH_COLORS = [
  0xff7766, 0x66ccff, 0xffd966, 0x88ff99, 0xff7fbf, 0xc88aff,
];

/**
 * Per-species template. count is the number of instances cloned from the
 * one loaded GLB. depth is the resting y; speed is base m/s; radius is
 * [innerRing, outerRing] from world origin.
 */
const CREATURE_SPECS = [
  // ── Fish (10 total) ────────────────────────────────────────────────────
  { id: 'fish-1',   kind: 'fish',     url: '/models/wildlife/fish-1.glb',   count: 20, depth: -1.05, speed: 1.2, radius: [47, 68], targetMax: 0.75, bobAmp: 0.10 },
  { id: 'fish-2',   kind: 'fish',     url: '/models/wildlife/fish-2.glb',   count: 18, depth: -1.15, speed: 1.2, radius: [48, 72], targetMax: 0.75, bobAmp: 0.10 },
  { id: 'goldfish', kind: 'fish',     url: '/models/wildlife/goldfish.glb', count: 14, depth: -0.95, speed: 1.0, radius: [46, 60], targetMax: 0.62, bobAmp: 0.08 },
  // ── Seahorses (3 total) ────────────────────────────────────────────────
  { id: 'seahorse', kind: 'seahorse', url: '/models/wildlife/seahorse.glb', count: 5, depth: -0.85, speed: 0.16, radius: [46, 54], targetMax: 0.52, bobAmp: 0.12 },
  // ── Sharks (2 total) ───────────────────────────────────────────────────
  { id: 'shark-1',  kind: 'shark',    url: '/models/wildlife/shark-1.glb',  count: 1, depth: -1.8, speed: 1.7, radius: [72, 105], targetMax: 2.4, bobAmp: 0.08 },
  { id: 'shark-2',  kind: 'shark',    url: '/models/wildlife/shark-2.glb',  count: 1, depth: -1.8, speed: 1.7, radius: [74, 110], targetMax: 2.6, bobAmp: 0.08 },
  // ── Dolphins (2 total) ─────────────────────────────────────────────────
  { id: 'dolphin-1', kind: 'dolphin', url: '/models/wildlife/dolphin-1.glb', count: 3, depth: -1.15, speed: 1.6, radius: [56, 82], targetMax: 1.5, bobAmp: 0.10 },
  { id: 'dolphin-2', kind: 'dolphin', url: '/models/wildlife/dolphin-2.glb', count: 1, depth: -1.15, speed: 1.6, radius: [58, 86], targetMax: 1.5, bobAmp: 0.10 },
];

/** Authoritative world-space bbox-size for a freshly cloned scene. Uses
 *  Three.js's setFromObject so it picks up child-mesh transforms that a
 *  per-mesh boundingBox + applyMatrix4 walk can miss (e.g. SkinnedMesh
 *  rest-pose extents, baked-in group scales). */
function worldBoxSize(obj, out = new THREE.Vector3()) {
  obj.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(obj);
  if (box.isEmpty()) return out.set(1, 1, 1);
  return box.getSize(out);
}

export class MarineLife {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../Utils/Loader.js').Loader} loader
   */
  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;
    /** @type {Array} */
    this.creatures = [];
    /** @type {Array} */
    this._activeJumps = [];
    this._jumpTimer = 0;
    this._nextJump = JUMP_INTERVAL_RANGE[0]
      + Math.random() * (JUMP_INTERVAL_RANGE[1] - JUMP_INTERVAL_RANGE[0]);
    this.mode = 'day';
    this.water = null;
    this.audio = null;
    this.camera = null;
    this._tmp = new THREE.Vector3();
    this._revealed = false;
  }

  setWater(water) { this.water = water; }
  setAudio(audio) { this.audio = audio; }
  setCamera(camera) { this.camera = camera; }

  /** Bioluminescent emissive on the first BIOLUMINESCENT_COUNT fish at night. */
  setMode(mode) {
    this.mode = mode;
    let glowed = 0;
    for (const c of this.creatures) {
      if (c.kind !== 'fish') continue;
      const wantGlow = mode === 'night' && glowed < BIOLUMINESCENT_COUNT;
      if (wantGlow) glowed++;
      for (const mat of c.materials) {
        if (!mat.emissive) continue;
        if (wantGlow) {
          mat.emissive.setHex(0x0066ff);
          mat.emissiveIntensity = 0.6;
        } else {
          mat.emissive.setHex(0x000000);
          mat.emissiveIntensity = 0;
        }
        mat.needsUpdate = true;
      }
    }
  }

  /** Load every model and place its instances. Safe to fail per-model —
   *  one missing GLB only skips its own creatures. */
  async load() {
    if (!this.loader) return;
    const results = await Promise.all(
      CREATURE_SPECS.map((spec) =>
        this.loader.loadGLTF(spec.url)
          .then((gltf) => ({ spec, gltf }))
          .catch((err) => {
            console.warn(`[MarineLife] failed to load ${spec.url}`, err);
            return null;
          }),
      ),
    );
    for (const r of results) {
      if (!r) continue;
      this.#placeSpecies(r.spec, r.gltf);
    }
    // Re-apply mode in case setMode() was called before load resolved.
    this.setMode(this.mode);
  }

  #placeSpecies(spec, gltf) {
    for (let i = 0; i < spec.count; i++) {
      const root = gltf.scene.clone(true);
      // Clone every material so emissive / opacity per-instance doesn't
      // bleed across siblings. Capture them all for setMode().
      const materials = [];
      root.traverse((c) => {
        if (c.isMesh && c.material) {
          c.material = c.material.clone();
          // Slight translucency so the water-plane fresnel doesn't crush them.
          c.material.transparent = true;
          c.material.opacity = 0.92;
          c.material.depthWrite = true;
          // Tint fish a random color for variety (sharks/dolphins keep their
          // native model colors so the model's identity reads).
          if (spec.kind === 'fish' && c.material.color) {
            c.material.color.setHex(FISH_COLORS[(i + spec.id.length) % FISH_COLORS.length]);
          }
          c.castShadow = false;
          c.receiveShadow = false;
          materials.push(c.material);
        }
      });

      // Scale to consistent target-max-dimension so a 50cm fish model and a
      // 30m shark model both end up at the size we want. setFromObject
      // (inside worldBoxSize) is authoritative — a previous per-mesh
      // bbox walk under-counted fish-1 / fish-2 and they rendered at 10m.
      const size = worldBoxSize(root);
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      const variant = 0.85 + Math.random() * 0.3;
      let scale = (spec.targetMax * variant) / maxDim;
      root.scale.setScalar(scale);

      // Safety: re-measure after scaling and correct if a model's pivot
      // structure threw the first estimate off. Final tolerance is loose
      // (within ±50% of targetMax) so we only fire on egregious misses.
      const postSize = worldBoxSize(root);
      const postMax = Math.max(postSize.x, postSize.y, postSize.z);
      const wanted = spec.targetMax * variant;
      if (postMax > 0 && (postMax > wanted * 1.5 || postMax < wanted * 0.5)) {
        scale *= wanted / postMax;
        root.scale.setScalar(scale);
      }

      // Initial swim position: random angle in this species' band.
      const angle = Math.random() * Math.PI * 2;
      const radius = spec.radius[0] + Math.random() * (spec.radius[1] - spec.radius[0]);
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      // Tangent to the circle around origin gives the initial heading.
      const swimAngle = angle + Math.PI / 2 + (Math.random() - 0.5) * 0.5;
      root.position.set(x, spec.depth, z);
      root.rotation.y = swimAngle;

      // ── Centre the visible mesh on the placement position ─────────────
      // Most of these GLBs put their origin at the nose, the tail, or at
      // some baked-in offset thousands of units from the geometry — without
      // this re-centre step the model draws far from the intended ocean
      // coords (sometimes right back on the island disc). After scaling +
      // positioning, take the world bbox, find its centre, and shift the
      // root so the geometric centre lands exactly where we wanted.
      root.updateMatrixWorld(true);
      const worldBox = new THREE.Box3().setFromObject(root);
      if (!worldBox.isEmpty()) {
        const c = worldBox.getCenter(new THREE.Vector3());
        root.position.x += (x - c.x);
        root.position.y += (spec.depth - c.y);
        root.position.z += (z - c.z);
      }
      // Track the geometric-centre offset so the per-frame bob can move
      // the visible mesh without re-centring drift.
      const baseY = root.position.y;

      this.scene.add(root);
      // Skip the torch raycast: marine props sit far from the player and
      // the spotlight beam should land on the water surface, not on a fish.
      root.userData.noTorchRaycast = true;

      this.creatures.push({
        root,
        materials,
        kind: spec.kind,
        speed: spec.speed * (0.7 + Math.random() * 0.6),
        baseSpeed: spec.speed,
        swimAngle,
        // Sharks turn slowly; fish turn moderately; seahorses barely move.
        turnRate: spec.kind === 'shark'
          ? (Math.random() - 0.5) * 0.06
          : spec.kind === 'seahorse'
            ? (Math.random() - 0.5) * 0.08
            : (Math.random() - 0.5) * 0.30,
        bobPhase: Math.random() * Math.PI * 2,
        bobAmp: spec.bobAmp,
        // baseY is the root y that puts the GEOMETRIC centre at spec.depth;
        // models with offset origins differ from spec.depth here. The bob
        // oscillates around baseY so it never drifts back onto a bad origin.
        baseY,
        depth: spec.depth,
        radius: spec.radius.slice(),
        // Body wiggle phase — code-driven swimming animation since GLBs
        // are static. Seahorses bob more vertically and wiggle less.
        wigglePhase: Math.random() * Math.PI * 2,
        wiggleStrength: spec.kind === 'seahorse' ? 0.03 : 0.10,
        // Breach scheduling — dolphins and an occasional shark can surface.
        eligibleForJump: spec.kind === 'dolphin' || spec.kind === 'shark',
        // Camera-side visibility flag; recomputed each frame.
        visible: true,
      });
    }
  }

  // ── Per-frame ─────────────────────────────────────────────────────────────
  update(delta, elapsed, playerPos) {
    if (!playerPos) return;
    const playerRadius = Math.hypot(playerPos.x, playerPos.z);
    const revealMarineLife = playerRadius > SHORE_REVEAL_RADIUS;
    if (revealMarineLife && !this._revealed) {
      this._revealed = true;
      this.#stageWelcomeSchool(playerPos);
      this._jumpTimer = this._nextJump;
    } else if (!revealMarineLife) {
      this._revealed = false;
      this._activeJumps.length = 0;
      for (const c of this.creatures) {
        if (c.visible) {
          c.root.visible = false;
          c.visible = false;
        }
      }
      return;
    }
    // Camera distance is what actually determines whether the creature is
    // visible — when the player is on the south island looking north, fish
    // 80m to the north are off-camera and can be skipped entirely.
    const camPos = this.camera?.position ?? playerPos;
    for (const c of this.creatures) {
      // Cheap visibility cull — square distance to camera. Far creatures
      // are hidden, but still keep swimming so they do not "wake up" frozen
      // when the player reaches the shore.
      const cdx = c.root.position.x - camPos.x;
      const cdz = c.root.position.z - camPos.z;
      const camDist2 = cdx * cdx + cdz * cdz;
      const wantVisible = revealMarineLife && camDist2 < VISIBLE_RANGE_MAX * VISIBLE_RANGE_MAX;
      if (c.visible !== wantVisible) {
        c.root.visible = wantVisible;
        c.visible = wantVisible;
      }
      if (!wantVisible) continue;
      // Forward swim.
      c.root.position.x += Math.cos(c.swimAngle) * c.speed * delta;
      c.root.position.z += Math.sin(c.swimAngle) * c.speed * delta;
      c.swimAngle += c.turnRate * delta;

      // Bob vertically around the post-centred baseY. baseY is whatever
      // root.position.y had to be set to so the geometric centre lands at
      // spec.depth (some models bake in a large origin offset).
      c.root.position.y = c.baseY + Math.sin(elapsed * 1.5 + c.bobPhase) * c.bobAmp;

      // Body wiggle — rotate slightly around Z so it looks like the fish
      // is undulating. Frequency is faster for small fish, slower for sharks.
      const wiggleFreq = c.kind === 'shark' ? 2.5 : c.kind === 'seahorse' ? 1.5 : 6.0;
      const wiggle = Math.sin(elapsed * wiggleFreq + c.wigglePhase) * c.wiggleStrength;
      // Heading: face the swim direction. The model's local +Z is treated
      // as forward; if a model points the wrong way it'll need a per-spec
      // yaw offset (add as `yawOffset` to CREATURE_SPECS if so).
      c.root.rotation.y = c.swimAngle + Math.PI / 2;
      c.root.rotation.z = wiggle;

      // Constrain to species ring — turn back if drifting in or out of the
      // band. Skip for seahorses (they barely move radially anyway).
      const distFromCenter = Math.hypot(c.root.position.x, c.root.position.z);
      if (distFromCenter < c.radius[0]) c.swimAngle += 0.03;
      else if (distFromCenter > c.radius[1]) c.swimAngle -= 0.03;
      // Hard reject if a fish somehow drifts onto the island disc.
      if (distFromCenter < ISLAND_RADIUS + 2) {
        // Snap heading directly outward.
        c.swimAngle = Math.atan2(c.root.position.z, c.root.position.x);
      }

      // Player-startle — fish/dolphins dart away when the player gets close.
      // Sharks ignore the player (intentional per spec).
      if (c.kind !== 'shark') {
        const dx = c.root.position.x - playerPos.x;
        const dz = c.root.position.z - playerPos.z;
        const d2 = dx * dx + dz * dz;
        if (d2 < PLAYER_STARTLE_RANGE * PLAYER_STARTLE_RANGE) {
          c.speed = c.baseSpeed * 2.5;
          const awayAngle = Math.atan2(dz, dx);
          // Steer toward the away vector — lerp the heading so it's not a snap.
          c.swimAngle += (awayAngle - c.swimAngle) * 0.10;
        } else {
          // Relax speed back to baseline.
          c.speed += (c.baseSpeed - c.speed) * Math.min(1, delta * 0.8);
        }
      }
    }

    // ── Dolphin jumps ──────────────────────────────────────────────────────
    if (!revealMarineLife) return;
    this._jumpTimer += delta;
    if (this._jumpTimer >= this._nextJump) {
      this._jumpTimer = 0;
      this._nextJump = JUMP_INTERVAL_RANGE[0]
        + Math.random() * (JUMP_INTERVAL_RANGE[1] - JUMP_INTERVAL_RANGE[0]);
      this.#triggerDolphinJump(playerPos);
    }
    // Advance active jump animations; drop any that completed.
    if (this._activeJumps.length) {
      this._activeJumps = this._activeJumps.filter((fn) => fn(delta));
    }
  }

  #stageWelcomeSchool(playerPos) {
    const baseAngle = Math.atan2(playerPos.z, playerPos.x);
    const playerRadius = Math.hypot(playerPos.x, playerPos.z);
    const stage = (c, index, total, inner, outer) => {
      const spread = total <= 1 ? 0 : (index / (total - 1) - 0.5);
      const angle = baseAngle + spread * 1.2 + (Math.random() - 0.5) * 0.18;
      const radius = Math.max(ISLAND_RADIUS + inner, playerRadius + inner)
        + Math.random() * Math.max(1, outer - inner);
      c.root.position.x = Math.cos(angle) * radius;
      c.root.position.z = Math.sin(angle) * radius;
      c.root.position.y = c.baseY;
      c.swimAngle = angle + Math.PI / 2 + (Math.random() - 0.5) * 0.6;
      c.root.visible = true;
      c.visible = true;
    };
    const fish = this.creatures.filter((c) => c.kind === 'fish').slice(0, 26);
    fish.forEach((c, i) => stage(c, i, fish.length, 7, 20));
    const seahorses = this.creatures.filter((c) => c.kind === 'seahorse').slice(0, 4);
    seahorses.forEach((c, i) => stage(c, i, seahorses.length, 5, 11));
    const dolphins = this.creatures.filter((c) => c.eligibleForJump).slice(0, 4);
    dolphins.forEach((c, i) => {
      stage(c, i, dolphins.length, 13, 28);
      this.#triggerDolphinJump(playerPos, c);
    });
  }

  #triggerDolphinJump(playerPos, forcedDolphin = null) {
    // Pick a dolphin close enough to be noticed. If both are out of range,
    // move one into the forward ocean arc before launching so the jump is
    // discoverable instead of happening behind the fog.
    const all = this.creatures.filter((c) => c.eligibleForJump);
    const eligible = all.filter((c) => c.visible);
    const pool = eligible.length ? eligible : all;
    if (!pool.length) return;
    const dolphin = forcedDolphin ?? pool[Math.floor(Math.random() * pool.length)];
    if (!eligible.length && playerPos) {
      const angle = Math.atan2(playerPos.z, playerPos.x) + (Math.random() - 0.5) * 0.8;
      const radius = 58 + Math.random() * 10;
      dolphin.root.position.x = Math.cos(angle) * radius;
      dolphin.root.position.z = Math.sin(angle) * radius;
      dolphin.root.position.y = dolphin.baseY;
      dolphin.swimAngle = angle + Math.PI / 2;
      dolphin.root.visible = true;
      dolphin.visible = true;
    }

    const startX = dolphin.root.position.x;
    const startZ = dolphin.root.position.z;
    const startY = dolphin.root.position.y;
    const baseRotZ = dolphin.root.rotation.z;
    const travelAngle = dolphin.swimAngle + Math.PI / 2;
    const travelDist = 4.5 + Math.random() * 1.5;
    const jumpHeight = 3.0 + Math.random() * 1.5;
    const jumpDuration = 1.2;
    let elapsedJump = 0;
    let didReentry = false;

    // While airborne we drive the dolphin's position directly — the regular
    // swim integration in update() also runs, but since position is rewritten
    // every frame here it always wins for the duration.
    const animate = (delta) => {
      elapsedJump += delta;
      const t = Math.min(elapsedJump / jumpDuration, 1);
      const ease = Math.sin(t * Math.PI); // 0 → 1 → 0
      dolphin.root.position.set(
        startX + Math.cos(travelAngle) * travelDist * t,
        Math.max(startY, 0) + jumpHeight * ease,
        startZ + Math.sin(travelAngle) * travelDist * t,
      );
      // Nose-over-tail rotation — Math.cos(t·π) starts at +1, hits 0 at
      // mid-flight, ends at -1.
      dolphin.root.rotation.z = baseRotZ + Math.cos(t * Math.PI) * 0.6;
      dolphin.root.rotation.y = travelAngle + Math.PI / 2;

      // Spawn a single re-entry splash near the end of the arc, once.
      if (!didReentry && t > 0.92) {
        didReentry = true;
        const enterX = dolphin.root.position.x;
        const enterZ = dolphin.root.position.z;
        this._tmp.set(enterX, 0, enterZ);
        if (this.water?.spawnSplash) {
          const distToPlayer = playerPos
            ? Math.hypot(enterX - playerPos.x, enterZ - playerPos.z)
            : 100;
          // Marine splash audio is capped at 25% master per the spec, then
          // falls off linearly with distance up to 40m.
          const volume = Math.max(0, 1 - distToPlayer / 40) * 0.25;
          this.water.spawnSplash(this._tmp, {
            count: 18,
            audio: volume > 0.01,
            volume,
          });
        }
      }
      if (t >= 1) {
        // Restore swim baseY — the next update() tick will take over.
        dolphin.root.position.y = dolphin.baseY;
        dolphin.root.rotation.z = baseRotZ;
        return false;
      }
      return true;
    };
    this._activeJumps.push(animate);
  }
}
