import * as THREE from 'three';

const TARGET_HEIGHT = 1.7;
const AVATAR_GLB = '/models/character/avatar.glb';

const TORCH_GLB = '/models/props/Torch.glb';
// Bone-local transform for the torch on the hand bone. Starting
// values per user spec; tweak in Character.js when re-tuning the grip.
const TORCH_BONE_SCALE = 0.34;
const TORCH_BONE_OFFSET = { x: -0.03, y: 0.02, z: 0.06 };
const TORCH_BONE_EULER = { x: -Math.PI / 2, y: 0, z: 0 };
const TORCH_HAND_LIGHT_COLOR = 0xff8833;
// Lowered from (1.8, 6) — the PointLight sat inside the shirt and washed
// the torso orange. (1.2, 4) keeps a tight warm glow on the wielding arm
// without bleeding through fabric.
const TORCH_HAND_LIGHT_INTENSITY = 1.2;
const TORCH_HAND_LIGHT_DISTANCE = 4;
const TORCH_HAND_LIGHT_DECAY = 2;
const TORCH_FLAME_COLOR = 0xff8833;
// Torch.glb's Fire mesh tops out around local y=0.88 before scaling.
const TORCH_HAND_LIGHT_LOCAL = { x: 0, y: 0.88, z: 0 };
const TORCH_FLAME_IDLE_EMISSIVE = 0.35;
const TORCH_FLAME_AIM_EMISSIVE = 1.8;
const TORCH_AIM_YAW_LIMIT = 0.85;
const TORCH_AIM_PITCH_LIMIT = 0.55;

const _torchAimEuler = new THREE.Euler(0, 0, 0, 'XYZ');
const _torchAimQuat = new THREE.Quaternion();
const _torchAimHandWorld = new THREE.Vector3();
const _torchAimHandLocal = new THREE.Vector3();
const _torchAimTargetLocal = new THREE.Vector3();
const _torchAimDir = new THREE.Vector3();

// Each entry: a GLB whose first animation clip is extracted and renamed to
// `action`. The mesh inside is discarded — only the AnimationClip is kept.
const AVATURN_CLIPS = [
  { action: 'running',         url: '/models/character/animations/running-avaturn.glb' },
  { action: 'crouchWalk',      url: '/models/character/animations/crouch-walk.glb' },
  { action: 'push',            url: '/models/character/animations/push.glb' },
  { action: 'fightStance',     url: '/models/character/animations/fight-stance.glb' },
  { action: 'supermanPunch',   url: '/models/character/animations/superman-punch.glb' },
  { action: 'kickFootball',    url: '/models/character/animations/kick-football.glb' },
  { action: 'kickLeg',         url: '/models/character/animations/kick-leg.glb' },
  { action: 'dance',           url: '/models/character/animations/dance.glb' },
  { action: 'danceCelebrate',  url: '/models/character/animations/dance-celebrate.glb' },
  { action: 'backflip',        url: '/models/character/animations/backflip.glb' },
  { action: 'cartwheel',       url: '/models/character/animations/cartwheel.glb' },
  { action: 'facepalm',        url: '/models/character/animations/facepalm.glb' },
];

// Mixamo clips still used for actions Avaturn doesn't ship.
const MIXAMO_CLIPS = [
  { action: 'walking',          url: '/models/character/walking.fbx' },
  { action: 'walkingBackwards', url: '/models/character/walking-backwards.fbx' },
  { action: 'jump',             url: '/models/character/jump.fbx' },
  { action: 'standingUp',       url: '/models/character/standing-up.fbx' },
  { action: 'startWalking',     url: '/models/character/start-walking.fbx' },
  { action: 'lookingAround',    url: '/models/character/looking-around.fbx' },
  { action: 'pointing',         url: '/models/character/pointing.fbx' },
  { action: 'waving',           url: '/models/character/waving-gesture.fbx' },
  { action: 'torchIdle',        url: '/models/character/animations/torch-idle.fbx' },
  { action: 'torchAim',         url: '/models/character/animations/torch-aim.fbx' },
  { action: 'torchEquip',       url: '/models/character/animations/torch-equip.fbx' },
];

function stripRootMotion(clip) {
  clip.tracks = clip.tracks.filter((t) => !t.name.endsWith('.position'));
  return clip;
}

const UPPER_BODY_ONLY_ACTIONS = new Set(['torchIdle', 'torchAim', 'torchEquip']);
const TORCH_OVERLAY_WEIGHT = 2.2;

/**
 * Mixamo FBX exports name bones like "mixamorigHips" (or "mixamorig:Hips").
 * Avaturn's rig uses the bare Mixamo convention ("Hips"). Stripping the
 * prefix lets AnimationMixer bind Mixamo tracks onto the Avaturn skeleton.
 */
function retargetMixamoToAvaturn(clip) {
  for (const track of clip.tracks) {
    track.name = track.name.replace(/^mixamorig:?/, '');
  }
  return clip;
}

function keepTorchUpperBodyOnly(clip) {
  clip.tracks = clip.tracks.filter((track) => (
    /^(Spine|Spine1|Spine2|Neck|Head|LeftShoulder|LeftArm|LeftForeArm|LeftHand|RightShoulder|RightArm|RightForeArm|RightHand)/.test(track.name)
  ));
  return clip;
}

/**
 * Avaturn avatar (GLB) + a mix of Avaturn-native and Mixamo-retargeted clips
 * driven by a single AnimationMixer. The avatar's embedded "Animation" clip
 * serves as the idle.
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
    this._torchOverlayAction = null;
    this._torchOverlayName = null;
    this._torchOverlayTimer = null;
    this.rootBone = null;
    this.rootBoneBindPos = new THREE.Vector3();
    this.torchHandBone = null;
    this.leftArmBone = null;
    this.leftForeArmBone = null;
    this.leftHandBone = null;
    this.rightHandBone = null;
    this.torchMesh = null;
    this.torchLight = null;
    this.torchFlameMaterials = [];
    this.torchAimNdc = new THREE.Vector2();
    this.torchAimTarget = new THREE.Vector3();
    this.hasTorchAimTarget = false;
  }

  async load() {
    let gltf;
    try {
      gltf = await this.loader.loadGLTF(AVATAR_GLB);
    } catch (err) {
      console.warn('[Character] failed to load Avaturn GLB:', err);
      return { ok: false, reason: 'glb-load-failed' };
    }

    const avatar = gltf.scene;
    this.skinned = false;
    avatar.traverse((child) => {
      if (child.isSkinnedMesh) {
        this.skinned = true;
        child.castShadow = true;
        child.receiveShadow = true;
        const apply = (m) => {
          if (!m) return;
          if (m.envMapIntensity !== undefined) m.envMapIntensity = 0.6;
          // Force front-side only. Avaturn ships some clothing as DoubleSide
          // (jackets, hair planes); when the third-person camera momentarily
          // clips inside the body — e.g. when wading into a pool and
          // camera-controls slides the camera between player and water — the
          // back faces fill the viewport with a near-solid silhouette colour.
          // FrontSide makes those interior faces invisible.
          m.side = THREE.FrontSide;
        };
        if (Array.isArray(child.material)) child.material.forEach(apply);
        else apply(child.material);
      }
    });

    if (!this.skinned) {
      console.warn('[Character] Avaturn GLB contains no SkinnedMesh.');
      return { ok: false, reason: 'no-skinned-mesh' };
    }

    const box = new THREE.Box3().setFromObject(avatar);
    const size = box.getSize(new THREE.Vector3());
    const scale = TARGET_HEIGHT / Math.max(size.y, 0.001);
    avatar.scale.setScalar(scale);
    const scaledBox = new THREE.Box3().setFromObject(avatar);
    avatar.position.y -= scaledBox.min.y;

    this.mesh = avatar;
    this.root.add(this.mesh);

    let leftHand = null;
    let rightHand = null;
    const boneNames = [];
    this.mesh.traverse((child) => {
      if (!child.isBone) return;
      boneNames.push(child.name);
      if (!this.rootBone && /hips/i.test(child.name)) {
        this.rootBone = child;
        this.rootBoneBindPos.copy(child.position);
      }
      if (!leftHand && /lefthand/i.test(child.name) && !/lefthand(index|middle|ring|pinky|thumb)/i.test(child.name)) {
        leftHand = child;
      }
      if (!this.leftArmBone && /leftarm/i.test(child.name) && !/leftforearm|lefthand/i.test(child.name)) {
        this.leftArmBone = child;
      }
      if (!this.leftForeArmBone && /leftforearm/i.test(child.name)) {
        this.leftForeArmBone = child;
      }
      if (!rightHand && /righthand/i.test(child.name) && !/righthand(index|middle|ring|pinky|thumb)/i.test(child.name)) {
        rightHand = child;
      }
    });
    this.leftHandBone = leftHand;
    this.rightHandBone = rightHand;
    this.torchHandBone = this.leftHandBone ?? this.rightHandBone;
    if (this.torchHandBone) {
      console.log('[Torch] attaching to bone:', this.torchHandBone.name);
    } else {
      console.warn('[Torch] hand bone not found — torch will not be attached. Available bones:');
      for (const n of boneNames) console.warn('  ', n);
    }

    this.mixer = new THREE.AnimationMixer(this.mesh);
    this.mixer.addEventListener('finished', this.#onActionFinished);

    // Idle: the GLB's embedded animation is authored for this exact rig.
    if (gltf.animations?.length) {
      const idleClip = stripRootMotion(gltf.animations[0]);
      idleClip.name = 'idle';
      this.actions.idle = this.mixer.clipAction(idleClip);
    }

    // Avaturn-native clips: each GLB ships its own skeleton + one anim. We
    // discard the mesh and just bind the clip onto our existing mixer (bone
    // names match, no retargeting needed).
    const avaturnResults = await Promise.allSettled(
      AVATURN_CLIPS.map(async ({ action, url }) => {
        const g = await this.loader.loadGLTF(url);
        return { action, clip: g.animations?.[0] };
      }),
    );
    for (const r of avaturnResults) {
      if (r.status !== 'fulfilled' || !r.value.clip) continue;
      const { action, clip } = r.value;
      stripRootMotion(clip);
      clip.name = action;
      this.actions[action] = this.mixer.clipAction(clip);
    }

    // Mixamo clips for actions Avaturn doesn't ship — retarget by stripping
    // the mixamorig prefix from track names.
    const mixamoResults = await Promise.allSettled(
      MIXAMO_CLIPS.map(async ({ action, url }) => {
        const fbx = await this.loader.loadFBX(url);
        return { action, clip: fbx.animations?.[0] };
      }),
    );
    for (const r of mixamoResults) {
      if (r.status !== 'fulfilled' || !r.value.clip) continue;
      const { action, clip } = r.value;
      stripRootMotion(clip);
      retargetMixamoToAvaturn(clip);
      clip.name = action;
      if (UPPER_BODY_ONLY_ACTIONS.has(action)) {
        keepTorchUpperBodyOnly(clip);
      } else {
        this.actions[action] = this.mixer.clipAction(clip);
        continue;
      }
      this.actions[action] = this.mixer.clipAction(clip);
    }

    if (this.torchHandBone) {
      try {
        const torchGltf = await this.loader.loadGLTF(TORCH_GLB);
        const torchScene = torchGltf.scene;
        torchScene.scale.setScalar(TORCH_BONE_SCALE);
        torchScene.position.set(TORCH_BONE_OFFSET.x, TORCH_BONE_OFFSET.y, TORCH_BONE_OFFSET.z);
        torchScene.rotation.set(TORCH_BONE_EULER.x, TORCH_BONE_EULER.y, TORCH_BONE_EULER.z);
        torchScene.traverse((o) => {
          if (o.isMesh) {
            o.castShadow = false;
            o.receiveShadow = false;
            o.userData.noTorchRaycast = true;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            const isFlame = o.name === 'Torch_2' || mats.some((m) => /fire/i.test(m?.name ?? ''));
            if (isFlame) {
              const cloned = mats.map((m) => {
                const c = m.clone();
                c.emissive = c.emissive ?? new THREE.Color(TORCH_FLAME_COLOR);
                c.emissive.set(TORCH_FLAME_COLOR);
                c.emissiveIntensity = 0;
                c.toneMapped = false;
                this.torchFlameMaterials.push(c);
                return c;
              });
              o.material = Array.isArray(o.material) ? cloned : cloned[0];
            }
          }
        });
        this.torchLight = new THREE.PointLight(
          TORCH_HAND_LIGHT_COLOR,
          TORCH_HAND_LIGHT_INTENSITY,
          TORCH_HAND_LIGHT_DISTANCE,
          TORCH_HAND_LIGHT_DECAY,
        );
        this.torchLight.castShadow = false;
        this.torchLight.position.set(
          TORCH_HAND_LIGHT_LOCAL.x,
          TORCH_HAND_LIGHT_LOCAL.y,
          TORCH_HAND_LIGHT_LOCAL.z,
        );
        this.torchLightBaseIntensity = TORCH_HAND_LIGHT_INTENSITY;
        torchScene.add(this.torchLight);
        this.torchMesh = torchScene;
        this.torchMesh.visible = false;
        this.torchLight.visible = false;
        this.torchHandBone.add(this.torchMesh);
      } catch (err) {
        console.warn('[Character] failed to load Torch.glb:', err);
      }
    }

    if (this.actions.standingUp) {
      this.play('standingUp', { fade: 0, once: true, then: 'idle' });
    } else if (this.actions.idle) {
      this.play('idle');
    }

    return {
      ok: true,
      animationCount: Object.keys(this.actions).length,
      availableActions: Object.keys(this.actions),
    };
  }

  /**
   * Show/hide the held torch + its hand-light. When showing, plays the
   * torchEquip one-shot then settles into torchIdle; if torchEquip failed
   * to load, falls straight to torchIdle. No-op if the torch wasn't
   * attached (bone missing or load failed).
   */
  setTorchVisible(visible) {
    if (!this.torchMesh) return;
    const want = !!visible;
    if (this.torchMesh.visible === want) return;
    this.torchMesh.visible = want;
    if (this.torchLight) this.torchLight.visible = false;
    this.setTorchFlameIntensity(want ? TORCH_FLAME_IDLE_EMISSIVE : 0);
    if (!want) {
      this.stopTorchOverlay();
      return;
    }
    // Equip flourish — overlay one-shot. Plays on top of whatever the
    // state machine is currently doing (idle / walking / running) so the
    // arm raises briefly to "ignite" without taking over the rig pose.
    this.playTorchOverlayOnce('torchEquip', 0.2);
  }

  get torchOverlayName() {
    return this._torchOverlayName;
  }

  setTorchFlameIntensity(value) {
    for (const mat of this.torchFlameMaterials) {
      mat.emissiveIntensity = value;
    }
  }

  setTorchAimInput(ndc, target = null) {
    if (!ndc) {
      this.hasTorchAimTarget = false;
      this.torchAimNdc.set(0, 0);
      return;
    }
    this.torchAimNdc.set(
      THREE.MathUtils.clamp(ndc.x, -1, 1),
      THREE.MathUtils.clamp(ndc.y, -1, 1),
    );
    if (target) {
      this.torchAimTarget.copy(target);
      this.hasTorchAimTarget = true;
    }
  }

  get torchFlameAimIntensity() {
    return TORCH_FLAME_AIM_EMISSIVE;
  }

  get torchFlameIdleIntensity() {
    return TORCH_FLAME_IDLE_EMISSIVE;
  }

  playTorchOverlay(name, fade = 0.2) {
    const action = this.actions[name];
    if (!action) return;
    if (this._torchOverlayAction === action) return;
    this.stopTorchOverlay(fade);
    action.setLoop(THREE.LoopRepeat, Infinity);
    action.clampWhenFinished = false;
    action.reset().setEffectiveWeight(TORCH_OVERLAY_WEIGHT).fadeIn(fade).play();
    this._torchOverlayAction = action;
    this._torchOverlayName = name;
  }

  playTorchOverlayOnce(name, fade = 0.2) {
    const action = this.actions[name];
    if (!action) return;
    this.stopTorchOverlay(fade);
    action.setLoop(THREE.LoopOnce, 1);
    action.clampWhenFinished = true;
    action.reset().setEffectiveWeight(TORCH_OVERLAY_WEIGHT).fadeIn(fade).play();
    this._torchOverlayAction = action;
    this._torchOverlayName = name;
    const dur = action.getClip().duration;
    clearTimeout(this._torchOverlayTimer);
    this._torchOverlayTimer = setTimeout(() => {
      if (this._torchOverlayAction === action) this.stopTorchOverlay(0.2);
    }, Math.max(80, dur * 1000 + 80));
  }

  stopTorchOverlay(fade = 0.2) {
    clearTimeout(this._torchOverlayTimer);
    this._torchOverlayTimer = null;
    if (!this._torchOverlayAction) return;
    this._torchOverlayAction.fadeOut(fade);
    this._torchOverlayAction = null;
    this._torchOverlayName = null;
    this.setTorchAimInput(null);
  }

  /**
   * Cross-fade to a new animation.
   * opts.fade: seconds, default 0.25
   * opts.once: if true, plays the clip once and fires opts.then on finish
   * opts.then: state name to transition to after a one-shot finishes
   * opts.interruptible: cosmetic clips can be cancelled by movement input
   */
  play(name, opts = {}) {
    const action = this.actions[name];
    if (!action || this.currentName === name) return;

    const fade = opts.fade ?? 0.25;
    const next = action;

    if (opts.once) {
      next.setLoop(THREE.LoopOnce, 1);
      next.clampWhenFinished = true;
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
    if (this.rootBone) {
      this.rootBone.position.copy(this.rootBoneBindPos);
    }
    this.#applyTorchAimOffset();
  }

  #applyTorchAimOffset() {
    if (this._torchOverlayName !== 'torchAim') return;
    let yaw = this.torchAimNdc.x * TORCH_AIM_YAW_LIMIT;
    let pitch = -this.torchAimNdc.y * TORCH_AIM_PITCH_LIMIT;

    if (this.hasTorchAimTarget && (this.torchLight || this.leftHandBone)) {
      const source = this.torchLight ?? this.leftHandBone;
      source.getWorldPosition(_torchAimHandWorld);
      _torchAimHandLocal.copy(_torchAimHandWorld);
      _torchAimTargetLocal.copy(this.torchAimTarget);
      this.root.worldToLocal(_torchAimHandLocal);
      this.root.worldToLocal(_torchAimTargetLocal);
      _torchAimDir.subVectors(_torchAimTargetLocal, _torchAimHandLocal);
      const flat = Math.max(0.001, Math.hypot(_torchAimDir.x, _torchAimDir.z));
      yaw = THREE.MathUtils.clamp(Math.atan2(_torchAimDir.x, _torchAimDir.z), -TORCH_AIM_YAW_LIMIT, TORCH_AIM_YAW_LIMIT);
      pitch = THREE.MathUtils.clamp(Math.atan2(_torchAimDir.y, flat), -TORCH_AIM_PITCH_LIMIT, TORCH_AIM_PITCH_LIMIT);
    }

    if (this.leftArmBone) {
      _torchAimEuler.set(pitch * 0.75, yaw * 0.85, -yaw * 0.28, 'XYZ');
      _torchAimQuat.setFromEuler(_torchAimEuler);
      this.leftArmBone.quaternion.multiply(_torchAimQuat);
    }
    if (this.leftForeArmBone) {
      _torchAimEuler.set(pitch * 0.45, yaw * 0.4, -yaw * 0.16, 'XYZ');
      _torchAimQuat.setFromEuler(_torchAimEuler);
      this.leftForeArmBone.quaternion.multiply(_torchAimQuat);
    }
    if (this.leftHandBone) {
      _torchAimEuler.set(pitch * 0.25, yaw * 0.25, 0, 'XYZ');
      _torchAimQuat.setFromEuler(_torchAimEuler);
      this.leftHandBone.quaternion.multiply(_torchAimQuat);
    }
  }
}
