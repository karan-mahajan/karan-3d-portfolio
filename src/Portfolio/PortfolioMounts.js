import * as THREE from 'three/webgpu';
import { experience } from './ExperienceData.js';
import { skills } from './SkillsData.js';
import { contact } from './ContactData.js';
import { resume } from './ResumeData.js';

/**
 * Replaces Signs.js. Mounts portfolio content (skills artifacts, experience
 * cairns, contact plinth, resume lectern) onto the Blender-authored meshes
 * via refs collected during GlbWorld.load(). Each mount is a canvas-baked
 * world-space panel attached at the appropriate Blender ref or above the
 * matching mesh.
 *
 * Compatibility — preserves the Signs.js public API the rest of the
 * codebase reads:
 *   .experienceItems            — [{ index, position, accent, entry, mesh }]
 *   .skillsPosition             — THREE.Vector3
 *   .contactPosition            — THREE.Vector3
 *   .nearContact(playerPos, r)  — boolean-ish (Signs.js returned bool; we
 *                                 return a payload object or null. Callers
 *                                 use it as truthy, so this is compatible.)
 *   .nearResume(playerPos, r)   — payload or null (NEW)
 *
 * Missing-mesh policy: per CLAUDE.md rule 1, NEVER procedurally fake assets.
 * If a Blender mesh (skills_artifact_*, contact_inscription_plinth,
 * refResumeInteractivePoint) is missing, we log the absence loudly and skip
 * that mount block. The controller decides whether to flag, re-author, or
 * work around.
 */

const ACCENT_PALETTE = ['#ffb074', '#9ec5d6', '#c69a4a', '#a5d6a7', '#e08b8b'];

export class PortfolioMounts {
  static EXP_PROXIMITY = 6;
  static SKILLS_PROXIMITY = 7;
  static CONTACT_PROXIMITY = 5;
  static RESUME_PROXIMITY = 4;

  /**
   * @param {THREE.Scene} scene
   * @param {object} glbRefs — refs map from GlbWorld (see GlbWorld.refs shape)
   * @param {object} sectionPositions — SECTION_POSITIONS accessor (optional;
   *                                     used as a fallback for skills/contact
   *                                     positions if refs are sparse)
   */
  constructor(scene, glbRefs, sectionPositions = null) {
    this.scene = scene;
    this.refs = glbRefs;
    this.section = sectionPositions;
    this.missingMeshes = [];   // surfaced to App on construction

    this.experienceItems = [];
    this.skillsPosition = this.refs.section.skills?.clone() ?? new THREE.Vector3();
    this.contactPosition = this.refs.section.contact?.clone() ?? new THREE.Vector3();
    this.resumePosition = this.refs.interaction.resumeLectern?.clone() ?? null;

    this.#buildExperienceCairns();
    this.#buildSkillsArtifacts();
    this.#buildContactPlinth();
    // Resume moved to the floating ResumeBook (NW quadrant) — the old lectern
    // "Read resume" decal is retired so it isn't a dead marker.
    // this.#buildResumeLectern();

    if (this.missingMeshes.length) {
      console.warn(
        '[PortfolioMounts] missing Blender meshes — skipped mounting:',
        this.missingMeshes,
      );
    }
  }

  // ── Experience: one canvas-baked plank floats above each cairn ───────────
  #buildExperienceCairns() {
    const cairns = (this.refs.lights.cairnLantern ?? []).slice();
    if (cairns.length === 0) {
      this.missingMeshes.push('refCairnLantern_* (none found)');
      return;
    }
    // South→north so first cairn = first experience entry.
    cairns.sort((a, b) => a.position.z - b.position.z);
    for (let i = 0; i < Math.min(experience.length, cairns.length); i++) {
      const entry = experience[i];
      const cairn = cairns[i];
      const accent = ACCENT_PALETTE[i % ACCENT_PALETTE.length];
      const plank = this.#makeExperiencePlank(entry, accent);
      // Float 1.6m above the cairn cap so the player reads the inscription
      // as they approach. Faces the world center so it's readable from the
      // trail-approach side.
      plank.position.copy(cairn.position).add(new THREE.Vector3(0, 1.6, 0));
      plank.lookAt(0, plank.position.y, 0);
      this.scene.add(plank);
      this.experienceItems.push({
        index: i,
        position: cairn.position.clone(),
        accent,
        entry,
        mesh: plank,
      });
    }
  }

  #makeExperiencePlank(entry, accent) {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = accent;
    ctx.fillRect(0, 0, 32, canvas.height);

    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#f5e6d3';
    ctx.font = '700 96px "Fredoka", sans-serif';
    ctx.fillText(entry.company ?? '', 56, 60);

    ctx.fillStyle = accent;
    ctx.font = '600 56px "Nunito", sans-serif';
    ctx.fillText(entry.role ?? '', 56, 180);

    ctx.fillStyle = '#cfc0a8';
    ctx.font = '500 42px "Nunito", sans-serif';
    ctx.fillText(entry.dates ?? entry.period ?? '', 56, 260);
    if (entry.location) ctx.fillText(entry.location, 56, 320);

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const plank = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.2), mat);
    plank.name = `experience-plank-${entry.company ?? 'entry'}`;
    return plank;
  }

  // ── Skills: one decal canvas per artifact mesh in the observatory base ──
  #buildSkillsArtifacts() {
    const artifacts = [];
    this.scene.traverse((o) => {
      if (o.isMesh && /^skills_artifact_/.test(o.name)) artifacts.push(o);
    });
    if (artifacts.length === 0) {
      this.missingMeshes.push('skills_artifact_* (none found in scene)');
      return;
    }
    artifacts.sort((a, b) => a.name.localeCompare(b.name));
    // Skills data shape: [{ category, items }] (also tolerate {categories} or
    // {title}/{name} from older shapes).
    const categories = skills.categories ?? skills;
    for (let i = 0; i < Math.min(categories.length, artifacts.length); i++) {
      const cat = categories[i];
      const artifact = artifacts[i];
      const panel = this.#makeSkillsPanel(cat);
      artifact.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(artifact);
      panel.position.set(
        (box.min.x + box.max.x) / 2,
        box.max.y + 0.8,
        (box.min.z + box.max.z) / 2,
      );
      panel.lookAt(this.skillsPosition);
      this.scene.add(panel);
    }
  }

  #makeSkillsPanel(category) {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 84px "Fredoka", sans-serif';
    const title = category.title ?? category.name ?? category.category ?? '';
    ctx.fillText(title, 40, 40);

    ctx.fillStyle = '#f5e6d3';
    ctx.font = '500 42px "Nunito", sans-serif';
    const items = category.items ?? category.list ?? [];
    items.slice(0, 6).forEach((s, i) => {
      ctx.fillText(`• ${s}`, 40, 160 + i * 56);
    });

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.0), mat);
    panel.name = `skills-panel-${title || 'category'}`;
    return panel;
  }

  // ── Contact: inscription plinth gets a canvas decal facing spawn ─────────
  #buildContactPlinth() {
    const plinth = this.scene.getObjectByName('contact_inscription_plinth');
    if (!plinth) {
      this.missingMeshes.push('contact_inscription_plinth');
      return;
    }
    plinth.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(plinth);
    const panel = this.#makeContactPanel();
    panel.position.set(
      (box.min.x + box.max.x) / 2,
      box.max.y + 0.5,
      (box.min.z + box.max.z) / 2,
    );
    panel.lookAt(0, panel.position.y, 0);  // face spawn
    this.scene.add(panel);
  }

  #makeContactPanel() {
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 96px "Fredoka", sans-serif';
    ctx.fillText('Contact', 40, 40);

    ctx.fillStyle = '#f5e6d3';
    ctx.font = '500 44px "Nunito", sans-serif';
    // Real ContactData has `links: [{ label, value, href }]`. Tolerate older
    // shapes (`lines`, `entries`) too.
    const lines =
      contact.lines
      ?? contact.entries
      ?? (contact.links ?? []).map((l) => `${l.label}: ${l.value}`);
    lines.slice(0, 5).forEach((line, i) => {
      ctx.fillText(line, 40, 180 + i * 60);
    });

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 1.0), mat);
    panel.name = 'contact-panel';
    return panel;
  }

  // ── Resume lectern: open scroll mesh exists in .glb; we attach a glow ────
  #buildResumeLectern() {
    if (!this.refs.interaction.resumeLectern) {
      this.missingMeshes.push('refResumeInteractivePoint');
      return;
    }
    const pos = this.resumePosition;
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#2b1c12';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffb074';
    ctx.font = '700 64px "Fredoka", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Read resume', canvas.width / 2, canvas.height / 2);

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.35), mat);
    panel.name = 'resume-decal';
    panel.position.copy(pos).add(new THREE.Vector3(0, 1.4, 0));
    panel.lookAt(0, panel.position.y, 0);
    this.scene.add(panel);
  }

  // ── Proximity helpers (Interaction.js consumes these) ────────────────────

  /**
   * Returns a payload `{ kind, position, data }` if the player is within
   * `radius` of the contact plinth, else null. Signs.js returned a plain
   * boolean — callers (Interaction.js) use the result as truthy/falsy, so
   * the richer payload is API-compatible.
   */
  nearContact(playerPosition, radius = PortfolioMounts.CONTACT_PROXIMITY) {
    if (!this.contactPosition) return null;
    const dx = playerPosition.x - this.contactPosition.x;
    const dz = playerPosition.z - this.contactPosition.z;
    if (dx * dx + dz * dz <= radius * radius) {
      return { kind: 'contact', position: this.contactPosition, data: contact };
    }
    return null;
  }

  nearResume(playerPosition, radius = PortfolioMounts.RESUME_PROXIMITY) {
    if (!this.resumePosition) return null;
    const dx = playerPosition.x - this.resumePosition.x;
    const dz = playerPosition.z - this.resumePosition.z;
    if (dx * dx + dz * dz <= radius * radius) {
      return { kind: 'resume', position: this.resumePosition, data: resume };
    }
    return null;
  }
}
