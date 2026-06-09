import * as THREE from 'three/webgpu';
import { float, hash, positionWorld, select, uniform, vec3 } from 'three/tsl';

const SNOW_OUTFIT_GLB = '/models/character/avatar-snow.glb';
// World-space height of the wipe sweep — must clear the head with margin so
// the settled states are fully one outfit.
const WIPE_SPAN = 2.2;
// How far past the feet/head the line parks once a transition settles. The
// uniform is refreshed every frame relative to the feet, so a fixed margin is
// enough even when the player climbs.
const PARK_MARGIN = 10;
const FROST_COLOR = new THREE.Color('#9fd4ff');

/**
 * Weather outfit for the avatar: a second Avaturn GLB (same rig, winter
 * clothes) grafted onto the live skeleton, revealed by a frost-line wipe that
 * sweeps up the body when snow sets in and back down when it melts — so the
 * change reads as the outfit re-dressing itself, not a model swap.
 *
 * Both outfits are driven by the one AnimationMixer/skeleton, so animation
 * state, foot IK and the contact shadow carry across untouched.
 */
export class OutfitSwap {
  constructor(character, loader) {
    this.character = character;
    this.loader = loader;
    this.current = 'default';
    this._target = 'default';
    this._transition = null;
    this._loadPromise = null;
    this._snowMeshes = null;
    this._defaultMeshes = [];
    character.mesh.traverse((o) => {
      if (o.isSkinnedMesh) this._defaultMeshes.push(o);
    });

    // Shared wipe state. Snow clothes show BELOW the line, default clothes
    // ABOVE it — one uniform drives both cutouts, so the seam is gapless.
    this._wipeY = uniform(0);
    this._glow = uniform(0);
    this._tmpV = new THREE.Vector3();
    this.#applyWipeNodes(this._defaultMeshes, 'above');
    this.#parkWipe();
  }

  /** Kick off the snow GLB download without swapping — call at storm onset. */
  prefetch() {
    this.#ensureLoaded().catch(() => {});
  }

  /**
   * Swap to 'snow' or 'default' with the frost-line transition. Idempotent —
   * repeated calls with the current target are no-ops, so App can call this
   * every tick from the weather state.
   */
  set(name, { duration = 1.6 } = {}) {
    if (name === this._target) return;
    this._target = name;
    this.#ensureLoaded()
      .then((ok) => {
        if (!ok || name !== this._target || name === this.current) return;
        for (const m of this._defaultMeshes) m.visible = true;
        for (const m of this._snowMeshes) m.visible = true;
        this._transition = { to: name, t: 0, duration };
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
    // To snow: the line RISES feet→head (winter clothes climb up the body).
    // Back to default: it FALLS head→feet (the snow outfit melts away down).
    const rise = tr.to === 'snow' ? k : 1 - k;
    this._wipeY.value = feetY - 0.1 + rise * WIPE_SPAN;
    // Frost shimmer fades in fast, out fast, full strength mid-sweep.
    this._glow.value = Math.min(1, Math.min(tr.t, 1 - tr.t) * 6);

    if (tr.t >= 1) {
      this.current = tr.to;
      this._transition = null;
      const hide = tr.to === 'snow' ? this._defaultMeshes : this._snowMeshes;
      for (const m of hide) m.visible = false;
      this._glow.value = 0;
      this.#parkWipe();
    }
  }

  /** Rest position for the wipe line: far from the body on the settled side. */
  #parkWipe() {
    if (!this.character.root.parent) return;
    const feetY = this.character.root.getWorldPosition(this._tmpV).y;
    this._wipeY.value = this.current === 'snow' ? feetY + PARK_MARGIN : feetY - PARK_MARGIN;
  }

  async #ensureLoaded() {
    if (!this._loadPromise) {
      this._loadPromise = this.#loadSnowOutfit().catch((err) => {
        console.warn('[OutfitSwap] snow outfit failed to load:', err);
        this._loadPromise = null;
        return false;
      });
    }
    return this._loadPromise;
  }

  /**
   * Load the snow GLB and rebind its skinned meshes onto the avatar's live
   * skeleton (bones matched by name — both models share the Avaturn rig), so
   * the winter clothes follow every animation with zero extra mixer cost.
   */
  async #loadSnowOutfit() {
    const gltf = await this.loader.loadGLTF(SNOW_OUTFIT_GLB);
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
        console.warn('[OutfitSwap] snow outfit rig does not match avatar rig.');
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

    this._snowMeshes = incoming;
    this.#applyWipeNodes(incoming, 'below');
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
   * Cutout + frost-edge nodes for one outfit's materials. `side` picks which
   * half of the wipe this outfit occupies: snow clothes live 'below' the
   * line, the default outfit 'above' it.
   */
  #applyWipeNodes(meshes, side) {
    // Crinkly frost edge instead of a laser-straight cut.
    const edge = hash(positionWorld.xz.mul(47.0)).mul(0.07);
    const d = this._wipeY.add(edge).sub(positionWorld.y); // >0 below the line
    const belowLine = d.greaterThan(0.0);
    const visibleHere = side === 'below' ? belowLine : belowLine.not();
    const band = d.abs().div(0.12).clamp(0.0, 1.0).oneMinus();
    const frost = vec3(FROST_COLOR.r, FROST_COLOR.g, FROST_COLOR.b)
      .mul(band)
      .mul(this._glow)
      .mul(2.0);
    for (const mesh of meshes) {
      if (Array.isArray(mesh.material)) {
        mesh.material = mesh.material.map((m) => this.#toNodeMaterial(m));
      } else {
        mesh.material = this.#toNodeMaterial(mesh.material);
      }
      const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const m of mats) {
        if (!m?.isNodeMaterial) continue;
        m.opacityNode = select(visibleHere, float(1.0), float(0.0));
        m.alphaTest = 0.5; // cutout — keeps the materials opaque (no sorting)
        m.emissiveNode = frost;
        m.needsUpdate = true;
      }
    }
  }
}
