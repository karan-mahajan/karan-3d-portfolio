import * as THREE from 'three';
import { experience } from './ExperienceData.js';
import { skills } from './SkillsData.js';
import { contact } from './ContactData.js';

/**
 * Wooden signposts for experience / skills / contact zones, plus a central
 * compass at spawn that points visitors toward each cardinal section.
 *
 * Sections (cardinal, ~30–40 units from spawn so each is its own clearing):
 *   North (+Z) — EXPERIENCE: 5 signs along a winding trail
 *   East  (+X) — PROJECTS  (built by Billboards.js, position center exported there)
 *   South (-Z) — SKILLS    : big multi-plank board
 *   West  (-X) — CONTACT   : mailbox + name sign
 *
 * All posts + planks register static colliders with Rapier so the player
 * can't walk through them.
 */

const WOOD_COLOR = '#7a4e2b';
const WOOD_DARK = '#3d2615';
const WOOD_LIGHT = '#a07042';
const PAPER = '#f5e6d3';
const ACCENT = '#ffb074';

// ─── Cardinal positions (used by World for tree exclusions) ─────────────────
export const SECTION_POSITIONS = {
  experiencePath: [
    { x:  4, z: 13 },
    { x: -4, z: 20 },
    { x:  5, z: 28 },
    { x: -5, z: 36 },
    { x:  3, z: 42 },
  ],
  skills:  { x: 0,   z: -32 },
  contact: { x: -28, z: 0 },
  compass: { x: 0,   z: 5 },
};

// ─── Canvas-baked textures ──────────────────────────────────────────────────

/**
 * Auto-shrink a font so the rendered string fits within maxWidth.
 * Returns the px size to use.
 */
function fitFontSize(ctx, text, maxWidth, weight, family, startSize) {
  let size = startSize;
  ctx.font = `${weight} ${size}px ${family}`;
  while (ctx.measureText(text).width > maxWidth && size > 10) {
    size -= 2;
    ctx.font = `${weight} ${size}px ${family}`;
  }
  return size;
}

function bakedPlank(width, height, draw) {
  const px = 256;
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(width * px);
  canvas.height = Math.round(height * px);
  const ctx = canvas.getContext('2d');

  // Wood-grain background gradient with a subtle inner shadow.
  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
  grad.addColorStop(0, '#3a2616');
  grad.addColorStop(0.5, '#2b1c12');
  grad.addColorStop(1, '#3a2616');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  draw(ctx, canvas.width, canvas.height);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

function experienceTexture(entry) {
  return bakedPlank(2.6, 1.2, (ctx, w, h) => {
    // Accent stripe down the left.
    const stripeW = w * 0.03;
    ctx.fillStyle = ACCENT;
    ctx.fillRect(0, 0, stripeW, h);

    const padLeft = stripeW + w * 0.035;
    const usable = w - padLeft - w * 0.04;

    ctx.fillStyle = PAPER;
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';

    const companySize = fitFontSize(ctx, entry.company, usable, '700', '"Oswald", sans-serif', 96);
    ctx.font = `700 ${companySize}px "Oswald", sans-serif`;
    ctx.fillText(entry.company, padLeft, 40);

    ctx.fillStyle = ACCENT;
    const roleSize = fitFontSize(ctx, entry.role, usable, '600', '"Rajdhani", sans-serif', 58);
    ctx.font = `600 ${roleSize}px "Rajdhani", sans-serif`;
    ctx.fillText(entry.role, padLeft, 40 + companySize + 18);

    ctx.fillStyle = 'rgba(245, 230, 211, 0.75)';
    const dateSize = fitFontSize(ctx, entry.dates, usable, '500', '"Rajdhani", sans-serif', 48);
    ctx.font = `500 ${dateSize}px "Rajdhani", sans-serif`;
    ctx.fillText(entry.dates, padLeft, 40 + companySize + roleSize + 36);
  });
}

function skillsTexture() {
  return bakedPlank(5.0, 2.4, (ctx, w, h) => {
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';

    const padX = w * 0.04;

    // Title.
    ctx.fillStyle = ACCENT;
    ctx.font = '700 110px "Oswald", sans-serif';
    ctx.fillText('SKILLS', padX, 36);

    // Two-column layout for the 5 categories.
    const colCount = 2;
    const colW = (w - padX * 2 - 24) / colCount;
    const colStartY = 180;
    const lineH = 50;

    skills.forEach((group, i) => {
      const col = i % colCount;
      const row = Math.floor(i / colCount);
      const x = padX + col * (colW + 24);
      const y = colStartY + row * (lineH * 3.6);

      ctx.fillStyle = PAPER;
      ctx.font = '700 42px "Oswald", sans-serif';
      ctx.fillText(group.category.toUpperCase(), x, y);

      ctx.fillStyle = 'rgba(245, 230, 211, 0.85)';
      const itemsSize = fitFontSize(ctx, group.items.join('  ·  '), colW, '500', '"Rajdhani", sans-serif', 34);
      ctx.font = `500 ${itemsSize}px "Rajdhani", sans-serif`;
      const wrapped = wrapTextLines(ctx, group.items, colW);
      wrapped.forEach((line, k) => {
        ctx.fillText(line, x, y + 48 + k * (itemsSize + 8));
      });
    });
  });
}

function wrapTextLines(ctx, items, maxWidth) {
  const lines = [];
  let current = '';
  for (const item of items) {
    const trial = current ? `${current}  ·  ${item}` : item;
    if (ctx.measureText(trial).width > maxWidth) {
      if (current) lines.push(current);
      current = item;
    } else {
      current = trial;
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 5);
}

function nameSignTexture() {
  return bakedPlank(3.2, 1.5, (ctx, w, h) => {
    ctx.fillStyle = PAPER;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    ctx.fillStyle = ACCENT;
    const titleSize = fitFontSize(ctx, contact.name, w * 0.9, '700', '"Oswald", sans-serif', 96);
    ctx.font = `700 ${titleSize}px "Oswald", sans-serif`;
    ctx.fillText(contact.name, w / 2, h * 0.3);

    ctx.fillStyle = PAPER;
    const subSize = fitFontSize(ctx, contact.title.toUpperCase(), w * 0.85, '600', '"Rajdhani", sans-serif', 48);
    ctx.font = `600 ${subSize}px "Rajdhani", sans-serif`;
    ctx.fillText(contact.title.toUpperCase(), w / 2, h * 0.55);

    ctx.fillStyle = 'rgba(245, 230, 211, 0.7)';
    ctx.font = '500 38px "Rajdhani", sans-serif';
    ctx.fillText('approach the mailbox · press E', w / 2, h * 0.78);
  });
}

/**
 * Welcome board: single wide plank facing the player at spawn. Header at the
 * top, then a compass-rose layout showing N/E/S/W → section name with arrows.
 * From the player's perspective at spawn:
 *   ↑ = +Z (north) = EXPERIENCE
 *   → = +X (east)  = PROJECTS
 *   ↓ = -Z (south) = SKILLS
 *   ← = -X (west)  = CONTACT
 */
function welcomeBoardTexture() {
  return bakedPlank(3.4, 1.9, (ctx, w, h) => {
    ctx.textBaseline = 'middle';

    // Header strip.
    ctx.fillStyle = ACCENT;
    ctx.fillRect(0, 0, w, 8);
    ctx.fillRect(0, h - 8, w, 8);

    ctx.textAlign = 'center';
    ctx.fillStyle = PAPER;
    ctx.font = '700 88px "Oswald", sans-serif';
    ctx.fillText("KARAN'S WORLD", w / 2, 70);

    ctx.fillStyle = ACCENT;
    ctx.font = '600 32px "Rajdhani", sans-serif';
    ctx.fillText('WALK IN ANY DIRECTION TO EXPLORE', w / 2, 122);

    // 2×2 grid of direction cards: north top, south bottom, west left, east right.
    const card = (cx, cy, arrow, label) => {
      // Card background.
      ctx.fillStyle = 'rgba(245, 230, 211, 0.06)';
      ctx.fillRect(cx - 145, cy - 50, 290, 100);

      ctx.fillStyle = ACCENT;
      ctx.font = '700 64px "Oswald", sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(arrow, cx - 135, cy);

      ctx.fillStyle = PAPER;
      ctx.font = '700 40px "Oswald", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(label, cx + 135, cy);
    };

    const cyTop = 220;
    const cyBot = 340;
    const cxL = w / 2 - 165;
    const cxR = w / 2 + 165;

    card(cxL, cyTop, '↑', 'EXPERIENCE');
    card(cxR, cyTop, '→', 'PROJECTS');
    card(cxL, cyBot, '←', 'CONTACT');
    card(cxR, cyBot, '↓', 'SKILLS');
  });
}

// ─── Materials ──────────────────────────────────────────────────────────────

function woodMat(color = WOOD_COLOR) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.9, metalness: 0 });
}

// ─── Sign primitives ────────────────────────────────────────────────────────

function buildPost(parent, height, x = 0, z = 0) {
  const post = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08, 0.1, height, 8),
    woodMat(WOOD_DARK),
  );
  post.position.set(x, height / 2, z);
  post.castShadow = true;
  post.receiveShadow = true;
  parent.add(post);
  return post;
}

function buildPlank(parent, width, height, depth, y, texture, xOffset = 0, zOffset = 0) {
  const mat = texture
    ? new THREE.MeshStandardMaterial({ map: texture, roughness: 0.85, metalness: 0 })
    : woodMat(WOOD_LIGHT);
  const plank = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), mat);
  plank.position.set(xOffset, y, zOffset);
  plank.castShadow = true;
  plank.receiveShadow = true;
  parent.add(plank);
  return plank;
}

// ─── Public class ───────────────────────────────────────────────────────────

export class Signs {
  constructor(scene, physics = null, terrain = null) {
    this.scene = scene;
    this.physics = physics;
    // Sample terrain.heightAt for each sign so the post bottom sits on the
    // grass instead of inside it. Past r≈22 from spawn the terrain wave
    // ranges 0.02–0.65m above y=0; without this lift, signs at +X/+Z far
    // sections looked sunk into the ground.
    this.terrain = terrain;
    this.experienceItems = [];
    this.skillsPosition = null;
    this.contactPosition = null;

    this.#buildCompass();
    this.#buildExperienceTrail();
    this.#buildSkillsBoard();
    this.#buildContactZone();
  }

  #groundY(x, z) {
    return this.terrain ? this.terrain.heightAt(x, z) : 0;
  }

  // ── Welcome board near spawn ──────────────────────────────────────────────
  // A single wide plank facing the player at spawn. Shows all four cardinal
  // directions with correct arrows. Sits a few units forward of spawn so it
  // doesn't impale the player on respawn.
  #buildCompass() {
    const { x, z } = SECTION_POSITIONS.compass;
    const yaw = Math.PI; // face -Z (toward player at spawn)
    const groundY = this.#groundY(x, z);
    const group = new THREE.Group();
    group.position.set(x, groundY, z);
    group.rotation.y = yaw;
    group.name = 'welcome-board';

    const span = 4.0;
    const postHeight = 2.9;
    buildPost(group, postHeight, -span / 2 + 0.25, 0);
    buildPost(group, postHeight, +span / 2 - 0.25, 0);

    // Top cross-beam.
    const beam = new THREE.Mesh(
      new THREE.BoxGeometry(span + 0.2, 0.18, 0.18),
      woodMat(WOOD_DARK),
    );
    beam.position.set(0, postHeight - 0.08, 0);
    beam.castShadow = true;
    group.add(beam);

    // The plank.
    const plankCenterY = postHeight - 1.1;
    const plankH = 1.9;
    buildPlank(group, 3.4, plankH, 0.08, plankCenterY, welcomeBoardTexture());

    this.scene.add(group);
    this.compassGroup = group;
    this.compassPosition = new THREE.Vector3(x, groundY, z);

    if (this.physics) {
      // Posts live at local (±(span/2-0.25), 0, 0). Rotate that local X through
      // yaw to world space — same pattern as Billboards. Hardcoding world X
      // worked only because yaw=π flips both posts symmetrically; any other
      // yaw would mirror the colliders away from the visual posts.
      for (const lx of [-span / 2 + 0.25, +span / 2 - 0.25]) {
        const wx = x + Math.cos(yaw) * lx;
        const wz = z + -Math.sin(yaw) * lx;
        this.physics.addStaticCylinder(wx, groundY, wz, 0.13, postHeight);
      }
      // Plank centre Y = groundY + plankCenterY (addStaticCuboid takes centre).
      this.physics.addStaticCuboid(
        x, groundY + plankCenterY, z,
        1.75, plankH / 2, 0.08, yaw,
      );
    }
  }

  // ── Experience trail to the NORTH (+Z) ────────────────────────────────────
  // Single center pole that stops at the bottom of the plank (no piercing).
  // Each sign has small per-instance variation in cap shape / wood tint so
  // they don't feel like the same prefab repeated five times.
  #buildExperienceTrail() {
    const layout = SECTION_POSITIONS.experiencePath;
    const plankW = 2.6;
    const plankH = 1.2;
    const postHeight = 1.5;                      // post ends right under plank
    const plankCenterY = postHeight + plankH / 2;

    const variations = [
      { post: WOOD_DARK,  cap: 'sphere',   plankTrim: WOOD_LIGHT },
      { post: WOOD_COLOR, cap: 'cube',     plankTrim: WOOD_DARK },
      { post: WOOD_DARK,  cap: 'cone',     plankTrim: WOOD_LIGHT },
      { post: WOOD_LIGHT, cap: 'sphere',   plankTrim: WOOD_DARK },
      { post: WOOD_DARK,  cap: 'cylinder', plankTrim: WOOD_COLOR },
    ];

    experience.forEach((entry, i) => {
      const slot = layout[i];
      if (!slot) return;
      const v = variations[i % variations.length];

      const { x, z } = slot;
      const yaw = Math.atan2(-x, -z); // face origin
      const groundY = this.#groundY(x, z);
      const group = new THREE.Group();
      group.position.set(x, groundY, z);
      group.rotation.y = yaw;
      group.name = `experience:${entry.company}`;

      // Center post — slightly thicker so it reads as supporting the plank.
      const post = new THREE.Mesh(
        new THREE.CylinderGeometry(0.11, 0.13, postHeight, 8),
        woodMat(v.post),
      );
      post.position.set(0, postHeight / 2, 0);
      post.castShadow = true;
      post.receiveShadow = true;
      group.add(post);

      // Plank sits on top of the post.
      buildPlank(group, plankW, plankH, 0.09, plankCenterY, experienceTexture(entry));

      // Small decorative trim/top cap on the plank top edge.
      const trim = new THREE.Mesh(
        new THREE.BoxGeometry(plankW + 0.1, 0.1, 0.13),
        woodMat(v.plankTrim),
      );
      trim.position.set(0, plankCenterY + plankH / 2 + 0.05, 0);
      trim.castShadow = true;
      group.add(trim);

      // Distinct cap atop the trim — varies per sign so each looks unique.
      let cap;
      if (v.cap === 'sphere') {
        cap = new THREE.Mesh(new THREE.SphereGeometry(0.14, 12, 8), woodMat(WOOD_DARK));
      } else if (v.cap === 'cone') {
        cap = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.3, 8), woodMat(WOOD_LIGHT));
      } else if (v.cap === 'cylinder') {
        cap = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.18, 8), woodMat(WOOD_LIGHT));
      } else {
        cap = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.16, 0.26), woodMat(WOOD_DARK));
      }
      cap.position.set(0, plankCenterY + plankH / 2 + 0.2, 0);
      cap.castShadow = true;
      group.add(cap);

      this.scene.add(group);
      this.experienceItems.push({ entry, group, position: new THREE.Vector3(x, groundY, z) });

      if (this.physics) {
        this.physics.addStaticCylinder(x, groundY, z, 0.16, postHeight);
        // Plank centre Y = groundY + plankCenterY (addStaticCuboid takes centre).
        this.physics.addStaticCuboid(
          x, groundY + plankCenterY, z,
          plankW / 2, plankH / 2, 0.09, yaw,
        );
      }
    });
  }

  // ── Skills board to the SOUTH (-Z) ────────────────────────────────────────
  // "Forest information kiosk" style — peaked plank roof + supporting frame.
  // Visually distinct from the welcome board (which has a flat top beam).
  #buildSkillsBoard() {
    const { x, z } = SECTION_POSITIONS.skills;
    const yaw = Math.PI; // face +Z (toward spawn)
    const groundY = this.#groundY(x, z);

    const group = new THREE.Group();
    group.position.set(x, groundY, z);
    group.rotation.y = yaw;
    group.name = 'skills-board';

    const span = 5.0;
    const postHeight = 3.0;
    const plankH = 2.4;
    const plankCenterY = 1.5; // plank center
    // Two thick stone-like posts (darker wood with a chunky base).
    for (const sx of [-span / 2 + 0.3, +span / 2 - 0.3]) {
      const stone = new THREE.Mesh(
        new THREE.CylinderGeometry(0.18, 0.26, postHeight, 10),
        woodMat(WOOD_DARK),
      );
      stone.position.set(sx, postHeight / 2, 0);
      stone.castShadow = true;
      stone.receiveShadow = true;
      group.add(stone);

      // Base ring.
      const base = new THREE.Mesh(
        new THREE.CylinderGeometry(0.32, 0.36, 0.18, 12),
        woodMat(WOOD_LIGHT),
      );
      base.position.set(sx, 0.09, 0);
      base.castShadow = true;
      base.receiveShadow = true;
      group.add(base);
    }

    // Main info plank.
    buildPlank(group, 5.0, plankH, 0.1, plankCenterY, skillsTexture());

    // Peaked roof: two angled planks meeting at the top.
    const roofW = 5.4;
    const roofL = 1.8;
    const roofTilt = Math.PI / 8;
    const roofY = plankCenterY + plankH / 2 + 0.55;

    const leftRoof = new THREE.Mesh(
      new THREE.BoxGeometry(roofW, 0.08, roofL),
      woodMat(WOOD_LIGHT),
    );
    leftRoof.position.set(0, roofY, -Math.cos(roofTilt) * roofL / 2);
    leftRoof.rotation.x = -roofTilt;
    leftRoof.castShadow = true;
    leftRoof.receiveShadow = true;
    group.add(leftRoof);

    const rightRoof = new THREE.Mesh(
      new THREE.BoxGeometry(roofW, 0.08, roofL),
      woodMat(WOOD_LIGHT),
    );
    rightRoof.position.set(0, roofY, Math.cos(roofTilt) * roofL / 2);
    rightRoof.rotation.x = roofTilt;
    rightRoof.castShadow = true;
    rightRoof.receiveShadow = true;
    group.add(rightRoof);

    // Ridge beam along the roof peak.
    const ridge = new THREE.Mesh(
      new THREE.BoxGeometry(roofW + 0.1, 0.14, 0.14),
      woodMat(WOOD_DARK),
    );
    ridge.position.set(0, roofY + 0.15, 0);
    ridge.castShadow = true;
    group.add(ridge);

    this.scene.add(group);
    this.skillsGroup = group;
    this.skillsPosition = new THREE.Vector3(x, groundY, z);

    if (this.physics) {
      // Skills posts: local X = ±(span/2 - 0.3). Same yaw-aware transform as
      // the compass posts so a yaw change wouldn't mirror them.
      for (const lx of [-span / 2 + 0.3, +span / 2 - 0.3]) {
        const wx = x + Math.cos(yaw) * lx;
        const wz = z + -Math.sin(yaw) * lx;
        this.physics.addStaticCylinder(wx, groundY, wz, 0.22, postHeight);
      }
      // Plank centre Y = groundY + plankCenterY (addStaticCuboid takes centre).
      this.physics.addStaticCuboid(
        x, groundY + plankCenterY, z,
        2.6, plankH / 2, 0.1, yaw,
      );
    }
  }

  // ── Contact mailbox to the WEST (-X) ──────────────────────────────────────
  #buildContactZone() {
    const { x, z } = SECTION_POSITIONS.contact;
    const yaw = Math.PI / 2; // face +X (toward spawn)
    const groundY = this.#groundY(x, z);

    const group = new THREE.Group();
    group.position.set(x, groundY, z);
    group.rotation.y = yaw;
    group.name = 'contact-zone';

    // Mailbox post.
    const post = new THREE.Mesh(
      new THREE.CylinderGeometry(0.07, 0.1, 1.2, 8),
      woodMat(WOOD_DARK),
    );
    post.position.set(0, 0.6, 0);
    post.castShadow = true;
    post.receiveShadow = true;
    group.add(post);

    // Mailbox body (warm red).
    const boxBody = new THREE.Mesh(
      new THREE.BoxGeometry(0.7, 0.5, 0.45),
      new THREE.MeshStandardMaterial({ color: '#c25d3b', roughness: 0.7, metalness: 0.1 }),
    );
    boxBody.position.set(0, 1.45, 0);
    boxBody.castShadow = true;
    boxBody.receiveShadow = true;
    group.add(boxBody);

    const lid = new THREE.Mesh(
      new THREE.CylinderGeometry(0.225, 0.225, 0.7, 16, 1, false, 0, Math.PI),
      new THREE.MeshStandardMaterial({ color: '#a04826', roughness: 0.7, metalness: 0.1 }),
    );
    lid.rotation.z = Math.PI / 2;
    lid.position.set(0, 1.7, 0);
    lid.castShadow = true;
    group.add(lid);

    const flagPole = new THREE.Mesh(
      new THREE.CylinderGeometry(0.015, 0.015, 0.4, 6),
      new THREE.MeshStandardMaterial({ color: '#222', roughness: 0.8 }),
    );
    flagPole.position.set(0.4, 1.55, 0);
    flagPole.castShadow = true;
    group.add(flagPole);

    const flag = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 0.12, 0.02),
      new THREE.MeshStandardMaterial({ color: '#ff6b3d', emissive: '#ff3322', emissiveIntensity: 0.25 }),
    );
    flag.position.set(0.5, 1.7, 0);
    flag.castShadow = true;
    group.add(flag);

    // Name plank next to mailbox — single center pole ending at plank bottom.
    const signGroup = new THREE.Group();
    signGroup.position.set(2.0, 0, 0);
    group.add(signGroup);
    const nameW = 3.2;
    const nameH = 1.5;
    const namePostH = 1.6;
    const namePlankY = namePostH + nameH / 2;

    const namePost = new THREE.Mesh(
      new THREE.CylinderGeometry(0.12, 0.14, namePostH, 8),
      woodMat(WOOD_DARK),
    );
    namePost.position.set(0, namePostH / 2, 0);
    namePost.castShadow = true;
    namePost.receiveShadow = true;
    signGroup.add(namePost);

    buildPlank(signGroup, nameW, nameH, 0.09, namePlankY, nameSignTexture());

    // Distinctive curved-top accent so the contact sign doesn't look like a trail marker.
    const arch = new THREE.Mesh(
      new THREE.CylinderGeometry(nameW / 2, nameW / 2, 0.18, 24, 1, false, 0, Math.PI),
      woodMat(WOOD_LIGHT),
    );
    arch.rotation.z = Math.PI / 2;
    arch.rotation.y = Math.PI / 2;
    arch.position.set(0, namePlankY + nameH / 2 + 0.05, 0);
    arch.castShadow = true;
    signGroup.add(arch);

    this.scene.add(group);
    this.contactGroup = group;
    this.contactPosition = new THREE.Vector3(x, groundY, z);

    if (this.physics) {
      // Mailbox post (1.2m) + mailbox body (0.7×0.5×0.45 at y=1.45). One
      // box collider covers both so the player can't walk through the
      // visible mailbox body (post-only collider used to let them).
      this.physics.addStaticCylinder(x, groundY, z, 0.12, 1.2);
      // Body centre matches the visible mesh (boxBody.position.y = 1.45).
      this.physics.addStaticCuboid(x, groundY + 1.45, z, 0.35, 0.25, 0.225, yaw);
      // Name sign at local (2.0, 0, 0) rotated by yaw.
      const nx = x + Math.cos(yaw) * 2.0;
      const nz = z - Math.sin(yaw) * 2.0;
      // Sample terrain at the name-sign spot too — it can be on a different
      // height than the mailbox if the player walks across a hill there.
      const nameGroundY = this.#groundY(nx, nz);
      this.physics.addStaticCylinder(nx, nameGroundY, nz, 0.13, namePostH);
      // Plank centre Y = nameGroundY + namePlankY (addStaticCuboid takes centre).
      this.physics.addStaticCuboid(
        nx, nameGroundY + namePlankY, nz,
        nameW / 2, nameH / 2, 0.08, yaw,
      );
    }
  }

  // ── Proximity helpers ─────────────────────────────────────────────────────
  closestExperience(playerPos, radius = 3.5) {
    let best = null, bestD = radius;
    for (const item of this.experienceItems) {
      const dx = item.position.x - playerPos.x;
      const dz = item.position.z - playerPos.z;
      const d = Math.hypot(dx, dz);
      if (d < bestD) { best = item; bestD = d; }
    }
    return best;
  }

  nearSkills(playerPos, radius = 5) {
    if (!this.skillsPosition) return false;
    const dx = this.skillsPosition.x - playerPos.x;
    const dz = this.skillsPosition.z - playerPos.z;
    return Math.hypot(dx, dz) < radius;
  }

  nearContact(playerPos, radius = 4.5) {
    if (!this.contactPosition) return false;
    const dx = this.contactPosition.x - playerPos.x;
    const dz = this.contactPosition.z - playerPos.z;
    return Math.hypot(dx, dz) < radius;
  }
}
