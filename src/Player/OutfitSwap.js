import * as THREE from 'three/webgpu';
import { float, hash, mix, positionWorld, select, uniform } from 'three/tsl';

// Alternate outfits — each a second Avaturn GLB on the same rig, grafted onto
// the live skeleton (bones matched by name). `glow` tints the wipe sweep:
// icy frost for the snow dressing, warm gold for the museum's magic.
const OUTFITS = {
  snow: { url: '/models/character/avatar-snow.glb', glow: '#9fd4ff' },
  museum: { url: '/models/character/avatar-museum.glb', glow: '#ffc966' },
};

// World-space height of the wipe sweep — must clear the head with margin so
// the settled states are fully one outfit.
const WIPE_SPAN = 2.2;
// How far past the feet/head the line parks once a transition settles. The
// uniform is refreshed every frame relative to the feet, so a fixed margin is
// enough even when the player climbs.
const PARK_MARGIN = 10;

/**
 * Outfit system for the avatar: alternate Avaturn GLBs (same rig, different
 * clothes) grafted onto the live skeleton, revealed by a glow-line wipe that
 * sweeps up the body when dressing and back down when undressing — so the
 * change reads as the outfit re-dressing itself, not a model swap.
 *
 * All outfits are driven by the one AnimationMixer/skeleton, so animation
 * state, foot IK and the contact shadow carry across untouched.
 *
 * The base avatar is outfit 'default' and always occupies the ABOVE half of
 * the wipe line; incoming outfits reveal from below as the line rises, and
 * undressing back to default drops the line head→feet (the melt). One shared
 * line/glow uniform pair drives every cutout, so the seam is gapless even
 * when two non-default outfits hand over directly.
 */
export class OutfitSwap {
  constructor(character, loader) {
    this.character = character;
    this.loader = loader;
    this.current = 'default';
    this._target = 'default';
    this._transition = null;
    this._defaultMeshes = [];
    character.mesh.traverse((o) => {
      if (o.isSkinnedMesh) this._defaultMeshes.push(o);
    });

    // Shared wipe state: one line + glow for all outfits; a per-outfit `side`
    // uniform (1 = visible below the line, 0 = above) orients each cutout.
    this._wipeY = uniform(0);
    this._glow = uniform(0);
    this._glowColor = uniform(new THREE.Color(OUTFITS.snow.glow));
    this._tmpV = new THREE.Vector3();

    this._sets = {
      default: {
        meshes: this._defaultMeshes,
        side: uniform(0),
        loaded: Promise.resolve(true),
      },
    };
    for (const name of Object.keys(OUTFITS)) {
      this._sets[name] = { meshes: null, side: uniform(1), loaded: null };
    }

    this.#applyWipeNodes(this._defaultMeshes, this._sets.default.side);
    this.#parkWipe();
  }

  /** The outfit the swap is heading toward (== current when settled). */
  get target() {
    return this._target;
  }

  /** Kick off an outfit GLB download without swapping — call ahead of need. */
  prefetch(name = 'snow') {
    this.#ensureLoaded(name).catch(() => {});
  }

  /**
   * Swap to a named outfit ('default', 'snow', 'museum') with the glow-line
   * transition. Idempotent — repeated calls with the current target are
   * no-ops, so App can call this every tick from the weather state.
   */
  set(name, { duration = 1.6 } = {}) {
    if (name === this._target) return;
    if (name !== 'default' && !OUTFITS[name]) {
      console.warn(`[OutfitSwap] unknown outfit "${name}"`);
      return;
    }
    this._target = name;
    this.#ensureLoaded(name)
      .then((ok) => {
        if (!ok || name !== this._target || name === this.current) return;
        const fromSet = this._sets[this.current];
        const toSet = this._sets[name];
        if (!fromSet?.meshes || !toSet?.meshes) return;
        for (const [key, s] of Object.entries(this._sets)) {
          if (!s.meshes) continue;
          const on = key === this.current || key === name;
          for (const m of s.meshes) m.visible = on;
        }
        // 'default' always takes the ABOVE half; an incoming outfit reveals
        // from below as the line rises, undressing melts the line back down.
        const toBelow = name !== 'default';
        toSet.side.value = toBelow ? 1 : 0;
        fromSet.side.value = toBelow ? 0 : 1;
        this._glowColor.value.set(
          OUTFITS[toBelow ? name : this.current]?.glow ?? OUTFITS.snow.glow,
        );
        this._transition = { from: this.current, to: name, t: 0, duration };
      })
      .catch((err) => console.warn('[OutfitSwap] swap failed:', err));
  }

  update(delta) {
    if (!this._transition) {
      this.#parkWipe();
      return;
    }
    const tr = this._transition;
    tr.t = Math.min(1, tr.t + delta / tr.duration);
    const k = tr.t * tr.t * (3 - 2 * tr.t); // smoothstep ease
    const feetY = this.character.root.getWorldPosition(this._tmpV).y;
    // Dressing: the line RISES feet→head (new clothes climb up the body).
    // Back to default: it FALLS head→feet (the outfit melts away down).
    const rise = tr.to === 'default' ? 1 - k : k;
    this._wipeY.value = feetY - 0.1 + rise * WIPE_SPAN;
    // Sweep glow fades in fast, out fast, full strength mid-sweep.
    this._glow.value = Math.min(1, Math.min(tr.t, 1 - tr.t) * 6);

    if (tr.t >= 1) {
      this.current = tr.to;
      this._transition = null;
      const hide = this._sets[tr.from]?.meshes ?? [];
      for (const m of hide) m.visible = false;
      this._glow.value = 0;
      this.#parkWipe();
    }
  }

  /** Rest position for the wipe line: far from the body on the settled side. */
  #parkWipe() {
    if (!this.character.root.parent) return;
    const feetY = this.character.root.getWorldPosition(this._tmpV).y;
    this._wipeY.value =
      this.current !== 'default' ? feetY + PARK_MARGIN : feetY - PARK_MARGIN;
  }

  async #ensureLoaded(name) {
    if (name === 'default') return true;
    const s = this._sets[name];
    if (!s) return false;
    if (!s.loaded) {
      s.loaded = this.#loadOutfit(name).catch((err) => {
        console.warn(`[OutfitSwap] ${name} outfit failed to load:`, err);
        s.loaded = null;
        return false;
      });
    }
    return s.loaded;
  }

  /**
   * Load an outfit GLB and rebind its skinned meshes onto the avatar's live
   * skeleton (bones matched by name — all outfits share the Avaturn rig), so
   * the clothes follow every animation with zero extra mixer cost.
   */
  async #loadOutfit(name) {
    const gltf = await this.loader.loadGLTF(OUTFITS[name].url);
    const boneByName = new Map();
    this.character.mesh.traverse((o) => {
      if (o.isBone) boneByName.set(o.name, o);
    });

    const incoming = [];
    gltf.scene.traverse((o) => {
      if (o.isSkinnedMesh) incoming.push(o);
    });
    const parent = this._defaultMeshes[0]?.parent;
    if (!incoming.length || !parent) return false;

    for (const mesh of incoming) {
      const bones = mesh.skeleton.bones.map((b) => boneByName.get(b.name));
      if (bones.some((b) => !b)) {
        console.warn(`[OutfitSwap] ${name} outfit rig does not match avatar rig.`);
        return false;
      }
      mesh.bind(new THREE.Skeleton(bones, mesh.skeleton.boneInverses), mesh.bindMatrix);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.visible = false;
      const apply = (m) => {
        if (!m) return;
        if (m.envMapIntensity !== undefined) m.envMapIntensity = 0.6;
        m.side = /hair/i.test(mesh.name) || /hair/i.test(m.name ?? '')
          ? THREE.DoubleSide
          : THREE.FrontSide;
      };
      if (Array.isArray(mesh.material)) mesh.material.forEach(apply);
      else apply(mesh.material);
      parent.add(mesh);
    }

    this._sets[name].meshes = incoming;
    this.#applyWipeNodes(incoming, this._sets[name].side);
    return true;
  }

  /**
   * GLTFLoader produces core materials; custom TSL slots only exist on node
   * materials. Mirror what WebGPURenderer.library.fromMaterial does internally
   * (instantiate the node twin, copy every property) so we can attach nodes.
   */
  #toNodeMaterial(m) {
    if (!m || m.isNodeMaterial) return m;
    const nm = m.isMeshPhysicalMaterial
      ? new THREE.MeshPhysicalNodeMaterial()
      : new THREE.MeshStandardNodeMaterial();
    for (const key in m) nm[key] = m[key];
    return nm;
  }

  /**
   * Cutout + glow-edge nodes for one outfit's materials. `sideU` picks which
   * half of the wipe this outfit occupies at runtime: 1 shows below the
   * line, 0 above it.
   */
  #applyWipeNodes(meshes, sideU) {
    // Crinkly sweep edge instead of a laser-straight cut.
    const edge = hash(positionWorld.xz.mul(47.0)).mul(0.07);
    const d = this._wipeY.add(edge).sub(positionWorld.y); // >0 below the line
    const below = select(d.greaterThan(0.0), float(1.0), float(0.0));
    const visible = mix(below.oneMinus(), below, sideU);
    const band = d.abs().div(0.12).clamp(0.0, 1.0).oneMinus();
    const sweep = this._glowColor.mul(band).mul(this._glow).mul(2.0);
    for (const mesh of meshes) {
      if (Array.isArray(mesh.material)) {
        mesh.material = mesh.material.map((m) => this.#toNodeMaterial(m));
      } else {
        mesh.material = this.#toNodeMaterial(mesh.material);
      }
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const m of mats) {
        if (!m?.isNodeMaterial) continue;
        m.opacityNode = visible;
        m.alphaTest = 0.5; // cutout — keeps the materials opaque (no sorting)
        m.emissiveNode = sweep;
        m.needsUpdate = true;
      }
    }
  }
}
