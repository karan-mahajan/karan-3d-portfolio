import * as THREE from 'three';

const TARGET_HEIGHT = 1.7;

const ANIMATION_FILES = {
  idle: '/models/character/idle.fbx',
  walking: '/models/character/walking.fbx',
  walkingBackwards: '/models/character/walking-backwards.fbx',
  running: '/models/character/running.fbx',
  jump: '/models/character/jump.fbx',
  standingUp: '/models/character/standing-up.fbx',
  startWalking: '/models/character/start-walking.fbx',
  catwalk: '/models/character/catwalk-idle-to-walk-forward.fbx',
  lookingAround: '/models/character/looking-around.fbx',
  pointing: '/models/character/pointing.fbx',
  waving: '/models/character/waving-gesture.fbx',
};

/**
 * Mixamo clips often arrive with root-motion translation baked into the Hips
 * bone position track. Our movement system handles position itself, so we
 * strip the .position tracks to keep the character "in place" — the legs and
 * arms still animate, but the bone hierarchy no longer translates and the
 * character won't snap back to the origin every loop.
 */
function stripRootMotion(clip) {
  clip.tracks = clip.tracks.filter((t) => !t.name.endsWith('.position'));
  return clip;
}

/**
 * Mixamo character: skinned mesh + AnimationMixer + state machine.
 *
 * Loads idle.fbx as the base (it contains the skin), then loads the
 * other animations and pulls just their AnimationClip onto the same
 * skeleton so we get a single mesh + N animations.
 */
export class Character {
  constructor(loader) {
    this.loader = loader;
    this.root = new THREE.Group();
    this.root.name = 'character-root';

    this.mesh = null;
    this.skinned = false;
    this.mixer = null;
    this.actions = {};
    this.currentName = null;
    this.currentAction = null;
    this._oneShot = null;
    this.rootBone = null;
    this.rootBoneBindPos = new THREE.Vector3();
  }

  async load() {
    const idleFbx = await this.loader.loadFBX(ANIMATION_FILES.idle);

    // Detect whether this FBX actually contains a skinned mesh.
    this.skinned = false;
    idleFbx.traverse((child) => {
      if (child.isSkinnedMesh) {
        this.skinned = true;
        child.castShadow = true;
        child.receiveShadow = true;
        // Mixamo materials often arrive as MeshPhongMaterial with no map —
        // soften them so they read well under warm light.
        const apply = (m) => {
          if (!m) return;
          m.envMapIntensity = 0.6;
          if (m.shininess !== undefined) m.shininess = 8;
        };
        if (Array.isArray(child.material)) child.material.forEach(apply);
        else apply(child.material);
      }
    });

    if (!this.skinned) {
      console.warn(
        '[Character] idle.fbx has no SkinnedMesh — Mixamo download was likely "Without Skin". ' +
          'Re-download any animation with the "Skin" checkbox ticked.',
      );
      return { ok: false };
    }

    // Scale + ground-align the character to ~1.7m, feet at y=0.
    const box = new THREE.Box3().setFromObject(idleFbx);
    const size = box.getSize(new THREE.Vector3());
    const scale = TARGET_HEIGHT / Math.max(size.y, 0.001);
    idleFbx.scale.setScalar(scale);
    const scaledBox = new THREE.Box3().setFromObject(idleFbx);
    idleFbx.position.y -= scaledBox.min.y;

    // Mixamo characters arrive facing +Z, which matches our movement system —
    // no extra rotation needed. Player.group provides yaw.

    this.mesh = idleFbx;
    this.root.add(this.mesh);

    // Locate the root bone (Hips) so we can clamp its position each frame —
    // even with position tracks stripped, the bind pose can drift if multiple
    // mixers blend simultaneously, producing a noticeable lean / float.
    this.mesh.traverse((child) => {
      if (this.rootBone || !child.isBone) return;
      if (/hips/i.test(child.name)) {
        this.rootBone = child;
        this.rootBoneBindPos.copy(child.position);
      }
    });

    this.mixer = new THREE.AnimationMixer(this.mesh);
    this.mixer.addEventListener('finished', this.#onActionFinished);

    // Idle clip is in the same FBX.
    if (idleFbx.animations.length > 0) {
      const clip = stripRootMotion(idleFbx.animations[0]);
      clip.name = 'idle';
      this.actions.idle = this.mixer.clipAction(clip);
    }

    // Load remaining animations in parallel and extract their first clip.
    const others = Object.entries(ANIMATION_FILES).filter(([k]) => k !== 'idle');
    const loaded = await Promise.allSettled(
      others.map(async ([name, url]) => {
        const fbx = await this.loader.loadFBX(url);
        return { name, clip: fbx.animations[0] };
      }),
    );

    for (const r of loaded) {
      if (r.status !== 'fulfilled' || !r.value.clip) continue;
      const { name, clip } = r.value;
      stripRootMotion(clip);
      clip.name = name;
      this.actions[name] = this.mixer.clipAction(clip);
    }

    // Spawn-in: play "standing up" once, then settle to idle.
    if (this.actions.standingUp) {
      this.play('standingUp', { fade: 0, once: true, then: 'idle' });
    } else {
      this.play('idle');
    }

    return { ok: true, animationCount: Object.keys(this.actions).length };
  }

  /**
   * Cross-fade to a new animation.
   * opts.fade: seconds, default 0.25
   * opts.once: if true, plays the clip once and fires opts.then on finish
   * opts.then: state name to transition to after a one-shot finishes
   */
  play(name, opts = {}) {
    const action = this.actions[name];
    if (!action || this.currentName === name) return;

    const fade = opts.fade ?? 0.25;
    const next = action;

    if (opts.once) {
      next.setLoop(THREE.LoopOnce, 1);
      next.clampWhenFinished = true;
      // `interruptible` lets the Player state machine cancel cosmetic
      // one-shots (lookAround, point, wave) when input arrives. Critical
      // ones (standingUp spawn) leave it undefined → treated as non-interruptible.
      this._oneShot = { name, then: opts.then ?? 'idle', interruptible: opts.interruptible === true };
    } else {
      next.setLoop(THREE.LoopRepeat, Infinity);
      next.clampWhenFinished = false;
      this._oneShot = null;
    }

    if (this.currentAction && this.currentAction !== next) {
      this.currentAction.fadeOut(fade);
    }
    next.reset().fadeIn(fade).play();

    this.currentName = name;
    this.currentAction = next;
  }

  #onActionFinished = (event) => {
    if (!this._oneShot) return;
    const finishedClip = event.action.getClip();
    if (finishedClip.name !== this._oneShot.name) return;
    const next = this._oneShot.then;
    this._oneShot = null;
    if (next) this.play(next);
  };

  update(delta) {
    if (!this.mixer) return;
    this.mixer.update(delta);
    // Snap the root bone back to its bind position every frame. Cancels any
    // drift the animation might introduce, keeping the character upright
    // and on its feet.
    if (this.rootBone) {
      this.rootBone.position.copy(this.rootBoneBindPos);
    }
  }
}
