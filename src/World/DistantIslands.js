import * as THREE from 'three';
import gsap from 'gsap';

/**
 * Decorative islands on the ocean horizon. Procedural geometry (deformed
 * icosahedrons + half-sphere vegetation caps), no colliders, no interaction.
 * Sits between 70–140u from origin so the existing fog (day 50→130, night
 * 30→95) does the atmospheric fade automatically — closer islands read as
 * hazy silhouettes, further ones dissolve into the horizon band.
 */

// Size profiles only — distance + angle are randomised per session in
// #pickLayout() so every visit produces a different horizon (required for
// the distance-guess mini-game to feel fresh). Order is mountain → tiny
// rock; the layout picker preserves it so the first two always anchor the
// view as mountainous silhouettes.
const SIZE_PROFILES = [
  // Two mountainous "look at me" peaks.
  { scale: 2.8, heightScale: 2.1 },
  { scale: 3.0, heightScale: 2.0 },
  // Three mediums with vegetation caps.
  { scale: 1.9, heightScale: 1.3 },
  { scale: 1.7, heightScale: 1.1 },
  { scale: 1.5, heightScale: 1.2 },
  // Two small islands.
  { scale: 0.9, heightScale: 1.2 },
  { scale: 0.85, heightScale: 1.3 },
  // Three tiny rock outcrops — no vegetation cap.
  { scale: 0.48, heightScale: 1.4 },
  { scale: 0.45, heightScale: 1.6 },
  { scale: 0.42, heightScale: 1.5 },
];

// Distance range: must be past the island shore (~r=45) and inside the
// outer ocean radius (~r=150). Quantised to multiples of 5 so the
// distance-guess game has guess-friendly target numbers.
const DIST_MIN = 55;
const DIST_MAX = 145;
const DIST_STEP = 5;

const DAY_COLORS = Object.freeze({
  rock: new THREE.Color(0x4a4a3a),
  vegetation: new THREE.Color(0x2a5a2a),
});

// Night colors are deliberately LIGHTER than the night sky horizon
// (#0a1520) so the silhouettes read as moonlit mountains instead of
// blending into the sky band. Earlier dark-grey (#1a1a2a) was almost the
// same luminance as the fog and the islands disappeared.
const NIGHT_COLORS = Object.freeze({
  rock: new THREE.Color(0x4a5870),
  vegetation: new THREE.Color(0x2a3a3a),
});

export class DistantIslands {
  #scene;
  #materials = {};
  #nightOnly = [];
  #activeTweens = null;

  constructor(scene) {
    this.#scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'distant-islands';
    this.group.userData.noTorchRaycast = true;

    // Each entry: { id, position: Vector3, distance, scale, heightScale, mesh }
    // Distance is the exact horizontal distance from origin, quantised to a
    // multiple of DIST_STEP — the mini-game compares the player's slider
    // guess against this value directly.
    this.islands = [];

    this.#build();
    scene.add(this.group);
  }

  /** Public lookup — returns all island descriptors for the mini-game. */
  getIslands() {
    return this.islands;
  }

  #build() {
    this.#materials.rock = new THREE.MeshLambertMaterial({
      color: DAY_COLORS.rock.clone(),
      fog: true,
    });
    this.#materials.vegetation = new THREE.MeshLambertMaterial({
      color: DAY_COLORS.vegetation.clone(),
      fog: true,
    });

    const layout = this.#pickLayout();
    for (let i = 0; i < layout.length; i++) {
      const entry = layout[i];
      const islandGroup = this.#createIsland(entry);
      this.group.add(islandGroup);
      this.islands.push({
        id: `island-${i}`,
        position: islandGroup.position.clone(),
        distance: entry.distance,
        scale: entry.scale,
        heightScale: entry.heightScale,
        mesh: islandGroup,
      });
    }
  }

  /**
   * Per-session randomisation. Each profile draws from a size-appropriate
   * distance range so taller islands can't spawn right on top of the
   * shoreline (their peaks would project above the viewport and the
   * mini-game's arrow indicator would clip off-screen).
   *
   * Ranges are calibrated against the 45° vertical FOV at the default
   * camera tilt — a mountain (scale ≈ 3, heightScale ≈ 2, peak ≈ 23m
   * above water) needs to be ≥ ~70m from the player to keep its summit
   * inside the upper half of the frame, so origin distance ≥ 110m once
   * the player is standing at the r=40 shore.
   */
  #pickLayout() {
    const used = new Set();
    const layout = [];
    const n = SIZE_PROFILES.length;
    const sector = (Math.PI * 2) / n;
    const angleOffset = Math.random() * Math.PI * 2;

    for (let i = 0; i < n; i++) {
      const profile = SIZE_PROFILES[i];
      const [minD, maxD] = this.#rangeFor(profile);
      const choices = [];
      for (let d = minD; d <= maxD; d += DIST_STEP) {
        if (!used.has(d)) choices.push(d);
      }
      // Fallback: nothing left in the preferred band → take any unused
      // distance. Keeps the count guaranteed at 10 even on a worst-case
      // collision chain.
      if (!choices.length) {
        for (let d = DIST_MIN; d <= DIST_MAX; d += DIST_STEP) {
          if (!used.has(d)) choices.push(d);
        }
      }
      const distance = choices[Math.floor(Math.random() * choices.length)];
      used.add(distance);

      const angle = angleOffset + sector * i + (Math.random() - 0.5) * sector * 0.6;
      layout.push({
        ...profile,
        x: Math.cos(angle) * distance,
        z: Math.sin(angle) * distance,
        distance,
        rotation: Math.random() * Math.PI * 2,
      });
    }
    return layout;
  }

  #rangeFor(profile) {
    // Tier by silhouette height (scale * heightScale ≈ visible peak).
    const peak = profile.scale * profile.heightScale;
    if (peak >= 4)   return [110, DIST_MAX];   // mountains: stay far
    if (peak >= 2)   return [80,  DIST_MAX];   // mediums
    if (peak >= 1)   return [65,  130];        // small islands
    return [DIST_MIN, 110];                    // tiny rock outcrops
  }

  #createIsland({ x, z, scale, heightScale, rotation }) {
    const g = new THREE.Group();

    // Deformed icosahedron — organic rock silhouette, ~150 tris at detail 2.
    const baseGeo = new THREE.IcosahedronGeometry(4 * scale, 2);
    const positions = baseGeo.attributes.position;
    for (let i = 0; i < positions.count; i++) {
      const px = positions.getX(i);
      const py = positions.getY(i);
      const pz = positions.getZ(i);
      // Squash the underwater half so the visible shape sits like a dome
      // on the water rather than a full floating sphere.
      let newY = py * heightScale;
      if (newY < 0) newY *= 0.3;
      newY += Math.sin(px * 2.3) * Math.cos(pz * 1.7) * 0.5 * scale;
      positions.setY(i, newY);
      positions.setX(i, px + Math.sin(py * 3) * 0.3 * scale);
      positions.setZ(i, pz + Math.cos(py * 2.5) * 0.3 * scale);
    }
    baseGeo.computeVertexNormals();
    const rockMesh = new THREE.Mesh(baseGeo, this.#materials.rock);
    g.add(rockMesh);

    // Skip the green cap on tiny rock outcrops.
    if (scale > 0.5) {
      const vegGeo = new THREE.SphereGeometry(3 * scale, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2);
      const vegPos = vegGeo.attributes.position;
      for (let i = 0; i < vegPos.count; i++) {
        const vx = vegPos.getX(i);
        const vy = vegPos.getY(i);
        const vz = vegPos.getZ(i);
        const bump = Math.sin(vx * 3) * Math.cos(vz * 3) * 0.3 * scale;
        vegPos.setY(i, vy * 0.6 * heightScale + bump);
      }
      vegGeo.computeVertexNormals();
      const vegMesh = new THREE.Mesh(vegGeo, this.#materials.vegetation);
      vegMesh.position.y = 1.5 * scale * heightScale;
      g.add(vegMesh);
    }

    // Tiny warm dot on the two mountainous islands only — reads as a
    // distant lighthouse / campfire through the night fog. Threshold tied
    // to the mountain peaks (scale ≈ 2.8+); two anchors the eye, more felt
    // busy.
    if (scale > 2.5) {
      const lightDot = new THREE.Mesh(
        new THREE.SphereGeometry(0.45, 6, 6),
        new THREE.MeshBasicMaterial({
          color: 0xffbb55,
          fog: true,
          toneMapped: false,
        }),
      );
      lightDot.position.y = 4 * scale * heightScale;
      lightDot.visible = false;
      lightDot.userData.nightOnly = true;
      this.#nightOnly.push(lightDot);
      g.add(lightDot);
    }

    g.position.set(x, -0.5, z);
    g.rotation.y = rotation;
    g.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = false;
        child.receiveShadow = false;
      }
    });
    return g;
  }

  /**
   * @param {'day'|'night'} mode
   * @param {number} duration  Seconds. 0 snaps; >0 tweens via gsap to match
   *   the rest of TimeOfDay's day/night palette transitions.
   */
  setMode(mode, duration = 0) {
    const target = mode === 'night' ? NIGHT_COLORS : DAY_COLORS;
    const visible = mode === 'night';
    for (const dot of this.#nightOnly) dot.visible = visible;

    if (this.#activeTweens) {
      for (const t of this.#activeTweens) t.kill?.();
      this.#activeTweens = null;
    }

    if (duration <= 0) {
      this.#materials.rock.color.copy(target.rock);
      this.#materials.vegetation.color.copy(target.vegetation);
      return;
    }

    const ease = 'sine.inOut';
    this.#activeTweens = [
      gsap.to(this.#materials.rock.color, {
        r: target.rock.r, g: target.rock.g, b: target.rock.b,
        duration, ease,
      }),
      gsap.to(this.#materials.vegetation.color, {
        r: target.vegetation.r, g: target.vegetation.g, b: target.vegetation.b,
        duration, ease,
      }),
    ];
  }
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}
