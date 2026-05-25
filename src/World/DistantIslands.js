import * as THREE from 'three';
import gsap from 'gsap';

/**
 * Decorative islands on the ocean horizon. Procedural geometry (deformed
 * icosahedrons + half-sphere vegetation caps), no colliders, no interaction.
 * Sits between 70–140u from origin so the existing fog (day 50→130, night
 * 30→95) does the atmospheric fade automatically — closer islands read as
 * hazy silhouettes, further ones dissolve into the horizon band.
 */

// Deliberate size mix so the horizon doesn't read as a ring of identical
// blobs: two big mountain peaks, a handful of mediums, a couple small, and
// a couple tiny rock outcrops. Spread unevenly around the compass. Scales
// bumped a step compared to the first pass so the silhouettes actually
// punch through the night fog instead of dissolving into the sky band.
const ISLANDS = [
  // Two mountainous "look at me" silhouettes — heightScale 2+ gives them
  // a tall pointed peak instead of a dome; reads clearly as a mountain.
  { x: 95,   z: -65,  scale: 2.8, heightScale: 2.1, rotation: 1.2 },
  { x: -108, z: 55,   scale: 3.0, heightScale: 2.0, rotation: 2.5 },
  // Medium islands — vegetation caps visible, distinct shapes.
  { x: 115,  z: 35,   scale: 1.7, heightScale: 1.3, rotation: 0   },
  { x: -75,  z: -115, scale: 1.9, heightScale: 1.1, rotation: 0.8 },
  { x: -125, z: -45,  scale: 1.5, heightScale: 1.2, rotation: 1.7 },
  // Small islands — green cap but lower, more grounded reading.
  { x: 45,   z: 125,  scale: 0.9, heightScale: 1.2, rotation: 3.1 },
  { x: -60,  z: 130,  scale: 0.85, heightScale: 1.3, rotation: 2.0 },
  // Tiny rock outcrops — no vegetation cap, just poking out of the water.
  { x: 135,  z: -20,  scale: 0.45, heightScale: 1.6, rotation: 0.5 },
  { x: 70,   z: -135, scale: 0.42, heightScale: 1.5, rotation: 2.8 },
  { x: -45,  z: 100,  scale: 0.48, heightScale: 1.4, rotation: 1.0 },
];

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

    this.#build();
    scene.add(this.group);
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

    for (const island of ISLANDS) {
      this.group.add(this.#createIsland(island));
    }
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
