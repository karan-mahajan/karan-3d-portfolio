import * as THREE from 'three';
import { portfolio } from './PortfolioData.js';

/**
 * Project billboards arranged in a semi-circle facing the spawn point.
 *
 *   posts    — two vertical wooden cylinders
 *   beam     — horizontal cross-beam joining the posts
 *   screen   — emissive 4×2.5 plane painted in the project accent color
 *   label    — canvas-baked plane above the beam with the project name
 *
 * Each post gets a static physics collider so the player can't walk through
 * the supports. The screen plane itself is non-collidable — interaction is
 * driven by proximity (Phase 2), not collision.
 */

// Projects cluster lives EAST (+X) of spawn, far enough that you have to
// walk to discover it. Center of arc is at world (RADIUS, 0, 0); billboards
// are placed on the arc spanning ±ARC_HALF radians around due-east.
const RADIUS = 36;
const ARC_HALF = Math.PI / 6;   // 30° each side → 60° arc total
const POST_HEIGHT = 4;
const POST_RADIUS = 0.12;
const POST_SPACING = 4.5;
const SCREEN_WIDTH = 4;
const SCREEN_HEIGHT = 2.5;
const SCREEN_Y = 2.2;

export const PROJECTS_CENTER = { x: RADIUS, z: 0, radius: RADIUS };

const WOOD_COLOR = '#6b4226';
const WOOD_DARK = '#3d2615';
const LABEL_BG = '#1a1410';

function makeLabelTexture(text, accent = '#ffd28a') {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = LABEL_BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Accent underline
  ctx.fillStyle = accent;
  ctx.fillRect(0, canvas.height - 12, canvas.width, 12);

  ctx.fillStyle = '#f5e6d3';
  ctx.font = 'bold 110px Oswald, "Arial Black", sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, canvas.width / 2, canvas.height / 2 - 6);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

export class Billboards {
  constructor(scene, physics = null, loader = null, terrain = null) {
    this.scene = scene;
    this.physics = physics;
    this.loader = loader;
    // PROJECTS_CENTER is at distance 36 — well past the r≈22 flatten radius,
    // so terrain there is ~0.46m above y=0. Without lifting, post bottoms and
    // their colliders sit ~half a meter under the visual ground.
    this.terrain = terrain;
    this.items = [];   // { project, group, screen, position, accent }
    this.group = new THREE.Group();
    this.group.name = 'billboards';
    // Day = 1.0 baseline. TimeOfDay lerps this up at night so the screens
    // pop against the dark world — multiplies the per-frame pulse range.
    this.emissiveBoost = 1.0;
    this.scene.add(this.group);

    this.#build();
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
  }

  #build() {
    const projects = portfolio.projects;
    const count = projects.length;
    // Arc on the EAST side (+X). theta=0 → due east; positive theta tilts
    // toward +Z (north-east), negative toward -Z (south-east).
    for (let i = 0; i < count; i++) {
      const t = count > 1 ? i / (count - 1) : 0.5;
      const theta = -ARC_HALF + t * ARC_HALF * 2;
      const x = Math.cos(theta) * RADIUS;
      const z = Math.sin(theta) * RADIUS;
      // Face spawn (origin).
      const yaw = Math.atan2(-x, -z);
      this.#buildOne(projects[i], i, x, z, yaw);
    }
  }

  #buildOne(project, index, x, z, yaw) {
    const groundY = this.#groundY(x, z);
    const group = new THREE.Group();
    group.position.set(x, groundY, z);
    group.rotation.y = yaw;
    group.name = `billboard:${project.name}`;

    const woodMat = new THREE.MeshStandardMaterial({
      color: WOOD_COLOR,
      roughness: 0.85,
      metalness: 0,
    });
    const woodDarkMat = new THREE.MeshStandardMaterial({
      color: WOOD_DARK,
      roughness: 0.9,
      metalness: 0,
    });

    // ── Posts ──────────────────────────────────────────────────────────────
    const postGeom = new THREE.CylinderGeometry(POST_RADIUS, POST_RADIUS * 1.2, POST_HEIGHT, 10);
    for (const side of [-1, 1]) {
      const post = new THREE.Mesh(postGeom, woodMat);
      post.position.set(side * (POST_SPACING / 2), POST_HEIGHT / 2, 0);
      post.castShadow = true;
      post.receiveShadow = true;
      group.add(post);

      // Physics: cylinder per post.
      if (this.physics) {
        // Rotate world position through yaw to place collider in world space.
        const lx = side * (POST_SPACING / 2);
        const wx = x + Math.cos(yaw) * lx;
        const wz = z + -Math.sin(yaw) * lx;
        this.physics.addStaticCylinder(wx, groundY, wz, POST_RADIUS * 1.3, POST_HEIGHT);
      }
    }

    // Slab collider covering the screen area so the player can't walk
    // through the billboard between the two posts. Thin in local Z, rotated
    // into world space by the billboard yaw.
    if (this.physics) {
      const slabHx = SCREEN_WIDTH / 2 + 0.15;
      const slabHy = (POST_HEIGHT - 0.4) / 2;
      const slabHz = 0.08;
      // Slab spans local Y in [0.2, POST_HEIGHT - 0.2] → centre = groundY + POST_HEIGHT/2.
      this.physics.addStaticCuboid(
        x, groundY + POST_HEIGHT / 2, z,
        slabHx, slabHy, slabHz,
        yaw,
      );
    }

    // ── Top beam ───────────────────────────────────────────────────────────
    const beam = new THREE.Mesh(
      new THREE.BoxGeometry(POST_SPACING + 0.3, 0.22, 0.22),
      woodDarkMat,
    );
    beam.position.set(0, POST_HEIGHT - 0.1, 0);
    beam.castShadow = true;
    group.add(beam);

    // Frame around the screen (thin wood border).
    const frame = new THREE.Mesh(
      new THREE.BoxGeometry(SCREEN_WIDTH + 0.25, SCREEN_HEIGHT + 0.25, 0.1),
      woodDarkMat,
    );
    frame.position.set(0, SCREEN_Y, -0.06);
    frame.castShadow = true;
    frame.receiveShadow = true;
    group.add(frame);

    // ── Screen ─────────────────────────────────────────────────────────────
    const accent = new THREE.Color(project.color);
    const screenMat = new THREE.MeshStandardMaterial({
      color: accent.clone().multiplyScalar(0.35),
      emissive: accent,
      emissiveIntensity: 0.55,
      roughness: 0.6,
      metalness: 0,
    });
    const screen = new THREE.Mesh(
      new THREE.PlaneGeometry(SCREEN_WIDTH, SCREEN_HEIGHT),
      screenMat,
    );
    screen.position.set(0, SCREEN_Y, 0);
    group.add(screen);

    // If the project has a screenshot, swap the screen material to show it.
    // We bind the texture as BOTH the diffuse map and the emissive map so
    // the screen glows with the image's own pixel colors at night —
    // crucially, emissive color stays white so the accent never tints
    // pixels on top of the image (previous behaviour painted a flat pink
    // wash over the screen and obscured the design).
    if (project.image && this.loader) {
      this.loader.loadTexture(project.image)
        .then((tex) => {
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = 8;
          screenMat.map = tex;
          screenMat.color.set('#ffffff');
          screenMat.emissive.set('#ffffff');
          screenMat.emissiveMap = tex;
          screenMat.needsUpdate = true;
          // Drop this screen's emissive multiplier so the texture isn't
          // blown out at night — the surrounding world light + a mild
          // self-glow is enough to read it.
          const item = this.items.find((it) => it.project === project);
          if (item) item.emissiveMultiplier = 0.28;
        })
        .catch((err) => console.warn('[Billboards] image load failed', project.image, err));
    }

    // ── Label plate above the beam ─────────────────────────────────────────
    const labelTex = makeLabelTexture(project.name, project.color);
    const label = new THREE.Mesh(
      new THREE.PlaneGeometry(POST_SPACING - 0.2, 0.6),
      new THREE.MeshBasicMaterial({ map: labelTex, transparent: false }),
    );
    label.position.set(0, POST_HEIGHT + 0.35, 0);
    group.add(label);

    this.scene.add(group);
    this.items.push({
      project,
      index,
      group,
      screen,
      position: new THREE.Vector3(x, 0, z),
      accent,
      // Per-item emissive scalar. 1.0 = accent-color glow (the empty
      // colored screen looks pulsing at full strength). Image-backed
      // screens drop this so the texture isn't blown-out white at night.
      emissiveMultiplier: 1.0,
    });
  }

  /** Distance test used by Phase 2 (prompt + zoom). */
  closestWithin(playerPos, radius) {
    let best = null;
    let bestDist = radius;
    for (const item of this.items) {
      const dx = item.position.x - playerPos.x;
      const dz = item.position.z - playerPos.z;
      const d = Math.hypot(dx, dz);
      if (d < bestDist) {
        best = item;
        bestDist = d;
      }
    }
    return best;
  }

  /** Subtle screen pulse so they read as "alive". */
  update(elapsed) {
    const boost = this.emissiveBoost;
    for (const item of this.items) {
      const pulse = (0.5 + 0.1 * Math.sin(elapsed * 1.5 + item.index * 0.7))
        * boost
        * item.emissiveMultiplier;
      item.screen.material.emissiveIntensity = pulse;
    }
  }
}
