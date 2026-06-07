import * as THREE from 'three/webgpu';
import { experience as EXPERIENCE_DATA } from './ExperienceData.js';

/**
 * Career Ascent — runtime layer for the Experience section (the 5 company
 * stations flanking the NE bridge, built in Blender section-07). The platforms,
 * pillars, glow rims and light-bridges ship baked in experience.glb; this class
 * adds the *readable* layer + interaction hooks the GLB can't carry:
 *
 *   - a floating canvas holo (company / role / dates) in front of each station's
 *     blank glow panel, facing the deck,
 *   - distance-driven reveal (the holo materialises as the player walks up),
 *   - near() / items[] so Interaction shows the walk-up E prompt + detail panel
 *     and App feeds achievement proximity + the map marker / teleport.
 *
 * Data comes from the `experienceRef_*` empties (deck anchors carrying company/
 * dates/year/side/index in node.extras). Role + summary come from
 * ExperienceData.js matched by company — the split exporter overwrites each
 * ref's `role` prop with its "ref" role-tag, so the extras role is unusable.
 *
 * No new external assets (canvas-baked text only) — CLAUDE.md rule 1 satisfied.
 */

const REF_PREFIX = 'experienceRef_';
const holoNameFor = (key) => `experience_${key}_holo`;

const E_PROMPT_RADIUS = 3.6; // deck distance that shows the "View Experience" prompt
const REVEAL_START = 12; // holo begins fading in at this XZ distance
const REVEAL_FULL = 6; // …and is fully opaque within this distance
const HOLO_WIDTH = 1.85; // matches the Blender holo panel (07 knobs.holo_width)
const HOLO_HEIGHT = 1.12; // …and holo_height

// Warm-magical accents (oldest → newest), echoing the gilded slab + amber glow.
const ACCENTS = ['#d98a2b', '#e0a23a', '#e8b54a', '#f0c45c', '#f7d774'];

// Auto-card (ambient HUD): pops in when the player is within this XZ distance of
// a station's deck anchor; switches cards with a slide-out/slide-in handoff.
const CARD_ACTIVATE_RADIUS = 6.5;
const CARD_HIDE_SECONDS = 0.26; // ≈ the slide-out transition before swapping content

export class Experience {
  /** @param {{ scene: THREE.Scene, refs: object, audio?: object|null }} deps */
  constructor({ scene, refs, audio = null }) {
    this.scene = scene;
    this.audio = audio;
    this.items = [];
    this.center = null; // THREE.Vector3 — map-marker anchor (avg deck anchor)
    this.landing = null; // { x, z, facing } — teleport landing on the deck
    this.structureMats = []; // baked glow materials → night-only emissive

    // Auto-card state. Interaction sets `cardSuppressed` while the focused
    // E-panel is open so the two don't stack.
    this.cardSuppressed = false;
    this.card = null;
    this._cardEls = null;
    this._cardKey = null;
    this._cardState = 'hidden'; // 'hidden' | 'shown' | 'hiding'
    this._cardT = 0;

    this.#build(refs);
    if (this.items.length) {
      this.#collectStructureMaterials();
      this.#installCard();
    }
  }

  /**
   * Make the baked station materials opaque (no see-through glow panels) and
   * remember their authored emissive so update() can drive the glow by
   * nightFactor — the amber glow then only lights up at night, like the title
   * letters / street lamps, instead of shining all day.
   */
  #collectStructureMaterials() {
    const group = this.scene.getObjectByName('system:experience');
    if (!group) return;
    const seen = new Set();
    group.traverse((mesh) => {
      if (!mesh.isMesh) return;
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const mat of mats) {
        if (!mat || seen.has(mat.uuid)) continue;
        seen.add(mat.uuid);
        mat.transparent = false;
        mat.opacity = 1;
        mat.depthWrite = true;
        const base = mat.emissiveIntensity ?? 0;
        const e = mat.emissive;
        if (base > 0 && e && (e.r > 0 || e.g > 0 || e.b > 0)) {
          this.structureMats.push({ mat, base });
          mat.emissiveIntensity = 0; // start unlit (day); update() ramps it at night
        }
        mat.needsUpdate = true;
      }
    });
  }

  #build(refs) {
    const byName = refs?.byName;
    if (!byName) return;
    const dataByCompany = new Map(EXPERIENCE_DATA.map((e) => [e.company, e]));

    const stations = [];
    for (const [name, entry] of byName) {
      if (!name.startsWith(REF_PREFIX)) continue;
      const key = name.slice(REF_PREFIX.length);
      const x = entry.extras || {};
      const data = dataByCompany.get(x.company) || {};
      stations.push({
        key,
        index: x.index ?? stations.length,
        company: x.company ?? data.company ?? key,
        role: data.role ?? '', // exporter clobbers ref.role → ExperienceData is source
        dates: x.dates ?? data.dates ?? '',
        year: x.year ?? '',
        summary: data.summary ?? '',
        points: data.points ?? [], // CMS bullet details for the focused E-panel
        side: x.side ?? 'L',
        position: entry.position.clone(), // deck anchor (the E target the player walks to)
        accent: ACCENTS[(x.index ?? 0) % ACCENTS.length],
      });
    }
    if (!stations.length) return;
    stations.sort((a, b) => a.index - b.index);
    this.items = stations;

    const center = new THREE.Vector3();
    for (const st of stations) {
      this.#buildHolo(st);
      center.add(st.position);
    }
    this.center = center.multiplyScalar(1 / stations.length).clone();

    // Teleport landing = the oldest station's deck anchor (always on the walked
    // deck), facing along the deck toward the next station.
    const first = stations[0];
    const next = stations[1] ?? first;
    this.landing = {
      x: first.position.x,
      z: first.position.z,
      facing: Math.atan2(
        next.position.x - first.position.x,
        next.position.z - first.position.z,
      ),
    };
  }

  #buildHolo(st) {
    const holo = this.scene.getObjectByName(holoNameFor(st.key));
    const holoPos = new THREE.Vector3();
    if (holo) holo.getWorldPosition(holoPos);
    else {
      holoPos.copy(st.position);
      holoPos.y += 1.0; // mesh missing — float above the deck anchor as a fallback
    }

    // Face the holo from the platform back toward the deck (where the player
    // walks), so the text reads head-on as they cross the bridge.
    const toDeck = new THREE.Vector3(
      st.position.x - holoPos.x,
      0,
      st.position.z - holoPos.z,
    );
    if (toDeck.lengthSq() < 1e-4) toDeck.set(0, 0, 1);
    toDeck.normalize();

    const tex = this.#renderHoloTexture(st);
    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      opacity: 0,
      depthWrite: false,
    });
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(HOLO_WIDTH, HOLO_HEIGHT),
      mat,
    );
    mesh.name = `experience_holoText_${st.key}`;
    mesh.renderOrder = 6;
    mesh.position.copy(holoPos).addScaledVector(toDeck, 0.06);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), toDeck);
    mesh.visible = false;
    this.scene.add(mesh);

    st.holoMesh = mesh;
    st.holoMat = mat;
    st._revealT = 0;
  }

  /** Bake the company / role / dates card onto a transparent canvas texture. */
  #renderHoloTexture(st) {
    const scale = 2;
    const W = 660;
    const H = 400;
    const canvas = document.createElement('canvas');
    canvas.width = W * scale;
    canvas.height = H * scale;
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);

    // Soft translucent backdrop so the text reads against a bright sunset sky.
    const pad = 14;
    const r = 26;
    ctx.beginPath();
    ctx.moveTo(pad + r, pad);
    ctx.arcTo(W - pad, pad, W - pad, H - pad, r);
    ctx.arcTo(W - pad, H - pad, pad, H - pad, r);
    ctx.arcTo(pad, H - pad, pad, pad, r);
    ctx.arcTo(pad, pad, W - pad, pad, r);
    ctx.closePath();
    const bg = ctx.createLinearGradient(0, pad, 0, H - pad);
    bg.addColorStop(0, 'rgba(38, 24, 10, 0.50)');
    bg.addColorStop(1, 'rgba(24, 14, 6, 0.62)');
    ctx.fillStyle = bg;
    ctx.fill();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = this.#rgba(st.accent, 0.85);
    ctx.stroke();

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Company — the headline.
    ctx.shadowColor = this.#rgba(st.accent, 0.9);
    ctx.shadowBlur = 22;
    ctx.fillStyle = '#fff4dc';
    ctx.font = '700 52px "Inter", system-ui, sans-serif';
    this.#fitText(ctx, st.company, W - 2 * (pad + 16), 52, 700);
    ctx.fillText(st.company, W / 2, 132);

    // Accent rule under the title.
    ctx.shadowBlur = 0;
    ctx.strokeStyle = this.#rgba(st.accent, 0.95);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(W / 2 - 120, 176);
    ctx.lineTo(W / 2 + 120, 176);
    ctx.stroke();

    // Role.
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 6;
    ctx.fillStyle = '#f3dcaf';
    ctx.font = '600 30px "Inter", system-ui, sans-serif';
    ctx.fillText(st.role || '', W / 2, 232);

    // Dates · year.
    ctx.fillStyle = '#d9bd8a';
    ctx.font = '500 25px "Inter", system-ui, sans-serif';
    ctx.fillText(st.dates || '', W / 2, 286);

    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.anisotropy = 8;
    tex.needsUpdate = true;
    return tex;
  }

  /** Shrink the font until `text` fits `maxWidth` (keeps long names on one line). */
  #fitText(ctx, text, maxWidth, basePx, weight) {
    let px = basePx;
    while (px > 22) {
      ctx.font = `${weight} ${px}px "Inter", system-ui, sans-serif`;
      if (ctx.measureText(text).width <= maxWidth) break;
      px -= 2;
    }
  }

  #rgba(hex, a) {
    const c = new THREE.Color(hex);
    return `rgba(${Math.round(c.r * 255)}, ${Math.round(c.g * 255)}, ${Math.round(c.b * 255)}, ${a})`;
  }

  // ── Auto-card (ambient HUD) ───────────────────────────────────────────────

  #installCard() {
    const el = document.createElement('div');
    el.className = 'experience-card is-left';
    el.innerHTML = `
      <div class="exp-card-accent"></div>
      <h3 class="exp-card-company"></h3>
      <p class="exp-card-role"></p>
      <p class="exp-card-dates"></p>
      <p class="exp-card-summary"></p>
      <div class="exp-card-hint"><span class="key">E</span> details</div>`;
    document.body.appendChild(el);
    this.card = el;
    this._cardEls = {
      company: el.querySelector('.exp-card-company'),
      role: el.querySelector('.exp-card-role'),
      dates: el.querySelector('.exp-card-dates'),
      summary: el.querySelector('.exp-card-summary'),
    };
  }

  #populateCard(st) {
    const e = this._cardEls;
    if (!e) return;
    e.company.textContent = st.company;
    e.role.textContent = [st.year ? String(st.year) : '', st.role]
      .filter(Boolean)
      .join('  ·  ');
    e.dates.textContent = st.dates || '';
    e.summary.textContent = st.summary || '';
    this.card.style.setProperty('--exp-accent', st.accent);
    // Slide in from the side the station physically sits on.
    const right = st.side === 'R';
    this.card.classList.toggle('is-right', right);
    this.card.classList.toggle('is-left', !right);
  }

  #setCard(st) {
    this.#populateCard(st);
    this.card.classList.add('is-shown');
  }

  #hideCard() {
    this.card?.classList.remove('is-shown');
  }

  /** Drive the auto-card: pop in the nearest station, hand off on change. */
  #updateCard(dt, playerPos) {
    if (!this.card) return;
    let active = null;
    let bestD = CARD_ACTIVATE_RADIUS;
    for (const st of this.items) {
      const d = Math.hypot(
        playerPos.x - st.position.x,
        playerPos.z - st.position.z,
      );
      if (d < bestD) {
        bestD = d;
        active = st;
      }
    }
    const desiredKey = this.cardSuppressed || !active ? null : active.key;

    if (this._cardState === 'shown') {
      if (desiredKey !== this._cardKey) {
        this.#hideCard();
        this._cardState = 'hiding';
        this._cardT = 0;
      }
    } else if (this._cardState === 'hiding') {
      this._cardT += dt;
      if (this._cardT >= CARD_HIDE_SECONDS) {
        this._cardState = 'hidden';
        this._cardKey = null;
      }
    } else if (desiredKey) {
      this.#setCard(active);
      this._cardKey = desiredKey;
      this._cardState = 'shown';
    }
  }

  /** Closest station within the E-prompt radius (or null). XZ distance only. */
  near(playerPos) {
    let best = null;
    let bestD = E_PROMPT_RADIUS;
    for (const st of this.items) {
      const d = Math.hypot(
        playerPos.x - st.position.x,
        playerPos.z - st.position.z,
      );
      if (d < bestD) {
        bestD = d;
        best = st;
      }
    }
    return best;
  }

  /** Per-frame holo reveal + night-only glow. */
  update(delta = 0, playerPos = null, nightFactor = 0) {
    if (!this.items.length) return;

    // Night-only glow on the baked station materials (runs even when paused).
    if (this.structureMats.length) {
      const nf = Math.min(1, Math.max(0, nightFactor));
      for (const s of this.structureMats) s.mat.emissiveIntensity = s.base * nf;
    }

    if (!playerPos) return;
    const dt = Math.min(Math.max(delta || 1 / 60, 0), 1 / 30);
    const k = 1 - Math.exp(-dt * 6);
    for (const st of this.items) {
      if (!st.holoMat) continue;
      const d = Math.hypot(
        playerPos.x - st.position.x,
        playerPos.z - st.position.z,
      );
      const target = Math.min(
        1,
        Math.max(0, (REVEAL_START - d) / (REVEAL_START - REVEAL_FULL)),
      );
      st._revealT += (target - st._revealT) * k;
      st.holoMat.opacity = st._revealT;
      st.holoMesh.visible = st._revealT > 0.01;
    }

    this.#updateCard(dt, playerPos);
  }
}
