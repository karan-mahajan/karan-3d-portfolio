import * as THREE from 'three/webgpu';
import { FootIK, SNOW_RISE } from './FootIK.js';
import { OutfitSwap } from './OutfitSwap.js';

const TARGET_HEIGHT = 1.7;
const AVATAR_GLB = '/models/character/avatar.glb';

// Clips for which foot IK runs — grounded idle/locomotion only. One-shots and
// aerial/special clips (jump, backflip, cartwheel, dance, sit, lava death…)
// play untouched so IK never yanks an airborne foot down to the ground.
const IK_GROUNDED_POSES = new Set([
  'idle', 'breathingIdle', 'walking', 'walkingBackwards', 'running', 'crouchWalk',
]);
// Foot-above-ground distance (m) over which IK fades to 0, so walking off a
// ledge (still in the 'walking' clip) releases the planting smoothly.
const IK_AIR_FADE = 0.35;

// Each entry: a GLB whose first animation clip is extracted and renamed to
// `action`. The mesh inside is discarded — only the AnimationClip is kept.
const AVATURN_CLIPS = [
  // Core locomotion set (2026-06-09 batch) — Mixamo exports whose tracks
  // already use bare Avaturn bone names, so they bind without retargeting.
  // The avatar GLB itself is a clean T-pose; 'idle' comes from this list.
  // breathingIdle is NOT the base idle — Player plays it for a few seconds
  // as a catch-breath when the player stops from a run, then settles to idle.
  { action: 'idle',            url: '/models/character/animations/idle.glb' },
  { action: 'breathingIdle',   url: '/models/character/animations/breathing-idle.glb' },
  { action: 'walking',         url: '/models/character/animations/walking.glb' },
  { action: 'running',         url: '/models/character/animations/running.glb' },
  // Two in-place jump arcs — Player picks by ground speed at takeoff.
  { action: 'jumpStanding',    url: '/models/character/animations/jump-standing.glb' },
  { action: 'jumpMoving',      url: '/models/character/animations/jump-moving.glb' },
  { action: 'crouchWalk',      url: '/models/character/animations/crouch-walk.glb' },
];

// Emote / interaction / mini-game clips — fired only by explicit input, never at
// spawn. Deferred off the reveal-blocking load (~1.6 MB total): warmed in the
// background shortly after spawn (preloadDeferredAnimations), with a lazy
// load-on-first-use fallback in play(). Avaturn format → bind directly, no
// retarget.
const DEFERRED_AVATURN_CLIPS = [
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
  // Colour Garden: one continuous reach→grab→wind-up→throw→recover take. Driven
  // as a charge-hold one-shot (paused at the wind-up frame while charging).
  { action: 'paintThrow',      url: '/models/character/animations/paint-throw.glb' },
];

// Mixamo clips still used for actions Avaturn doesn't ship. The source FBX
// files have been round-tripped through Three.js's FBXLoader → GLTFExporter
// pipeline (see .verify/scripts/extract-fbx-as-glb.mjs) into mesh-stripped
// animation-only GLBs, ~125-300 KB each vs the original ~27 MB each. Bone
// orientations are preserved because the same FBXLoader that reads them in
// the app is the one that produced the GLBs.
const MIXAMO_CLIPS = [
  { action: 'walkingBackwards', url: '/models/character/walking-backwards.glb' },
  // Intro cinematic: looping mid-air descent + one-shot superhero landing.
  // Root motion is stripped (like all clips) so IntroCinematic drives the
  // actual fall height; the landing plays in-place at the spawn point.
  { action: 'falling',          url: '/models/character/animations/falling.glb' },
  // Root motion stripped like every other clip (in-place). The landing's
  // ground penetration is handled instead by a per-frame ground-clamp in
  // IntroCinematic, which lifts the body so the lowest foot/hand bone never
  // sinks below the surface — robust regardless of the clip's authored contact.
  { action: 'hardLanding',      url: '/models/character/animations/hard-landing.glb' },
  // Deep-water locomotion — Player swaps to these while swim mode is active
  // (see Player.#updateAnimationState). Vertical float is physics-driven, so
  // root motion is stripped like the rest.
  { action: 'swimming',         url: '/models/character/animations/swimming.glb' },
  { action: 'treadingWater',    url: '/models/character/animations/treading-water.glb' },
  // Edge-grab exit: prone approach strokes → vertical reach → two-handed
  // hold on the bank lip (the clip has NO climb-up — Player boosts the body
  // procedurally after the hold). See Player.#maybeStartEdgeGrab.
  { action: 'swimmingToEdge',   url: '/models/character/animations/swimming-to-edge.glb' },
];

const DEFERRED_MIXAMO_CLIPS = [
  { action: 'lookingAround', url: '/models/character/looking-around.glb' },
  { action: 'pointing',      url: '/models/character/pointing.glb' },
  { action: 'waving',        url: '/models/character/waving-gesture.glb' },
];
// Combined deferred registry used by both the background warm and the lazy
// load-on-play path. `retarget: true` → mixamo clip needs retargetMixamoToAvaturn;
// avaturn clips bind directly.
const DEFERRED_BY_ACTION = new Map([
  ...DEFERRED_AVATURN_CLIPS.map((c) => [c.action, { ...c, retarget: false }]),
  ...DEFERRED_MIXAMO_CLIPS.map((c) => [c.action, { ...c, retarget: true }]),
]);

function stripRootMotion(clip) {
  clip.tracks = clip.tracks.filter((t) => !t.name.endsWith('.position'));
  return clip;
}

/**
 * Some Mixamo FBX→GLB conversions are authored in Z-up armature space: the
 * clip carries a constant -90° X rotation track on the "Armature" node and
 * the hips tracks live in that rotated frame. Our avatar rig is Y-up with an
 * identity Armature, and update() pins the hips to the Y-up bind position —
 * under a rotated Armature that pin puts the hips at ground level (body sinks
 * waist-deep, foot IK folds the legs trying to compensate). Bake the armature
 * rotation into the hips tracks and drop the Armature tracks so every clip
 * plays in the avatar's Y-up space. Clips without an Armature rotation track
 * pass through untouched.
 */
function normalizeClipUpAxis(clip) {
  const armRot = clip.tracks.find((t) => t.name === 'Armature.quaternion');
  if (!armRot) return clip;
  const q = new THREE.Quaternion().fromArray(armRot.values, 0).normalize();
  const tmpQ = new THREE.Quaternion();
  const tmpV = new THREE.Vector3();
  for (const track of clip.tracks) {
    if (track.name === 'Hips.quaternion') {
      for (let i = 0; i < track.values.length; i += 4) {
        tmpQ.fromArray(track.values, i).premultiply(q).toArray(track.values, i);
      }
    } else if (track.name === 'Hips.position') {
      for (let i = 0; i < track.values.length; i += 3) {
        tmpV.fromArray(track.values, i).applyQuaternion(q).toArray(track.values, i);
      }
    }
  }
  clip.tracks = clip.tracks.filter((t) => !t.name.startsWith('Armature.'));
  return clip;
}

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

/**
 * Correct each rotation track for the difference between the CLIP skeleton's
 * rest pose and the avatar's. Clip GLBs carry their own armature, and its
 * joint rest orientations differ from the Avaturn rig by a few degrees
 * (spine/neck/shoulders) — raw track copy stacks those errors down the chain
 * into a puffed-out chest, tilted head and twisted arms. Rebase each key as
 * q' = restTarget * restSource⁻¹ * q so the motion is replayed relative to
 * OUR bind pose. Identical rests → identity correction (skipped).
 */
function rebaseClipToBind(clip, sourceRoot, targetRoot) {
  if (!sourceRoot || !targetRoot) return clip;
  const srcRest = new Map();
  sourceRoot.traverse((o) => srcRest.set(o.name.replace(/^mixamorig:?/, ''), o.quaternion));
  const dstRest = new Map();
  targetRoot.traverse((o) => {
    if (o.isBone) dstRest.set(o.name, o.quaternion);
  });
  const corr = new THREE.Quaternion();
  const tmp = new THREE.Quaternion();
  for (const track of clip.tracks) {
    if (!track.name.endsWith('.quaternion')) continue;
    const bone = track.name.slice(0, -'.quaternion'.length);
    // Hips lives under the (possibly Z-up) Armature frame handled by
    // normalizeClipUpAxis; its residual rest delta is <0.5°, so leave it.
    if (bone === 'Hips' || bone === 'Armature') continue;
    const qs = srcRest.get(bone);
    const qt = dstRest.get(bone);
    if (!qs || !qt) continue;
    corr.copy(qt).multiply(tmp.copy(qs).invert());
    if (Math.abs(2 * Math.acos(Math.min(1, Math.abs(corr.w)))) < 0.003) continue;
    for (let i = 0; i < track.values.length; i += 4) {
      tmp.fromArray(track.values, i).premultiply(corr).toArray(track.values, i);
    }
  }
  return clip;
}

/**
 * Avaturn avatar (GLB, clean T-pose) + a mix of bare-named and
 * Mixamo-retargeted clips driven by a single AnimationMixer. The idle is the
 * breathing-idle clip from AVATURN_CLIPS, not an embedded animation.
 */
export class Character {
  constructor(loader, quality = {}) {
    this.loader = loader;
    // Foot IK is one cheap per-leg solve; gated off on the low tier (and any
    // profile that sets footIK:false) via this flag.
    this._footIKEnabled = quality.footIK !== false;
    this.footIK = null;
    this.root = new THREE.Group();
    this.root.name = 'character-root';

    this.mesh = null;
    this.skinned = false;
    this.mixer = null;
    this.actions = {};
    this.currentName = null;
    this.currentAction = null;
    this._oneShot = null;
    // Charge-hold: a one-shot frozen at a wind-up frame until releaseHold().
    this._chargeHold = null;
    // Right wrist bone — resolved in load(); the Colour Garden orb tracks it.
    this.rightHand = null;
    this._deferredClipPromises = new Map();
    this.rootBone = null;
    this.rootBoneBindPos = new THREE.Vector3();
    // Foot/toe/hand bones — used by IntroCinematic's landing ground-clamp to
    // find the lowest contact point of the current pose.
    this.groundBones = [];
    this._tmpV = new THREE.Vector3();
    // How the hips (rootBone) are clamped each frame:
    //   'full' — pin x/y/z to bind (in-place; default for locomotion/idle)
    //   'xz'   — pin x/z only, let the clip's vertical root motion through
    //            (used for the landing crouch so the body actually drops).
    this._rootPin = 'full';
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
          // Hair is thin alpha cards — FrontSide makes it vanish whenever the
          // camera sees its back faces (low camera angles, swimming). Keep it
          // DoubleSide; only solid body/clothing gets the FrontSide treatment.
          if (/hair/i.test(child.name) || /hair/i.test(m.name ?? '')) {
            m.side = THREE.DoubleSide;
            return;
          }
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

    this.mesh.traverse((child) => {
      if (!child.isBone) return;
      if (!this.rootBone && /hips/i.test(child.name)) {
        this.rootBone = child;
        this.rootBoneBindPos.copy(child.position);
      }
      if (/(foot|toebase|hand)/i.test(child.name)) this.groundBones.push(child);
      // Right wrist (not the finger bones) — the Colour Garden orb tracks this
      // bone's world position so it reads as held + thrown from the hand.
      if (!this.rightHand && /righthand$/i.test(child.name)) this.rightHand = child;
    });

    // Two-bone foot IK over the same skeleton (no-op if its leg chain or the
    // quality flag is missing). Built here so it shares the loaded bones.
    if (this._footIKEnabled) this.footIK = new FootIK(this.mesh);

    // Weather outfit (winter clothes during snow) — second GLB grafted onto
    // this same skeleton, revealed by a frost-line wipe. App drives it from
    // the WeatherDirector's coverage.
    this.outfits = new OutfitSwap(this, this.loader);

    this.mixer = new THREE.AnimationMixer(this.mesh);
    this.mixer.addEventListener('finished', this.#onActionFinished);

    // Avaturn-native clips: each GLB ships its own skeleton + one anim. We
    // discard the mesh and just bind the clip onto our existing mixer (bone
    // names match, no retargeting needed).
    const avaturnResults = await Promise.allSettled(
      AVATURN_CLIPS.map(async ({ action, url }) => {
        const g = await this.loader.loadGLTF(url);
        return { action, clip: g.animations?.[0], rig: g.scene };
      }),
    );
    for (const r of avaturnResults) {
      if (r.status !== 'fulfilled' || !r.value.clip) continue;
      const { action, clip, rig } = r.value;
      rebaseClipToBind(clip, rig, this.mesh);
      normalizeClipUpAxis(clip);
      stripRootMotion(clip);
      clip.name = action;
      this.actions[action] = this.mixer.clipAction(clip);
    }

    // Mixamo clips for actions Avaturn doesn't ship — retarget by stripping
    // the mixamorig prefix from track names.
    const mixamoResults = await Promise.allSettled(
      MIXAMO_CLIPS.map(async ({ action, url, keepRoot }) => {
        const g = await this.loader.loadGLTF(url);
        return { action, clip: g.animations?.[0], keepRoot, rig: g.scene };
      }),
    );
    for (const r of mixamoResults) {
      if (r.status !== 'fulfilled' || !r.value.clip) continue;
      const { action, clip, keepRoot, rig } = r.value;
      retargetMixamoToAvaturn(clip);
      rebaseClipToBind(clip, rig, this.mesh);
      normalizeClipUpAxis(clip);
      // keepRoot clips (e.g. the landing) preserve their hips translation so the
      // crouch reads correctly; everything else is flattened to in-place.
      if (!keepRoot) stripRootMotion(clip);
      clip.name = action;
      this.actions[action] = this.mixer.clipAction(clip);
    }

    // Fallback idle: if the breathing-idle clip failed to load but the GLB
    // ships an embedded animation (the old Avaturn export did), use that.
    if (!this.actions.idle && gltf.animations?.length) {
      const idleClip = stripRootMotion(gltf.animations[0]);
      idleClip.name = 'idle';
      this.actions.idle = this.mixer.clipAction(idleClip);
    }

    if (this.actions.idle) {
      this.play('idle', { fade: 0 });
    }

    return {
      ok: true,
      animationCount: Object.keys(this.actions).length,
      availableActions: Object.keys(this.actions),
      deferredActions: [...DEFERRED_BY_ACTION.keys()],
    };
  }

  preloadDeferredAnimations() {
    for (const name of DEFERRED_BY_ACTION.keys()) {
      this.#loadDeferredAction(name).catch((err) => {
        console.warn(`[Character] deferred animation "${name}" failed:`, err);
      });
    }
  }

  /**
   * Force a single deferred clip to load NOW (idempotent — returns the shared
   * load promise; true once bound, false if unknown / no clip). For opt-in
   * features that need a charged clip ready before the player can trigger it
   * (e.g. Colour Garden's paintThrow, which has no lazy fallback in playCharged).
   */
  ensureAction(name) {
    return this.#loadDeferredAction(name);
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
    if (!action) {
      if (DEFERRED_BY_ACTION.has(name)) {
        this.#loadDeferredAction(name)
          .then((loaded) => {
            if (loaded) this.play(name, opts);
          })
          .catch((err) => console.warn(`[Character] deferred animation "${name}" failed:`, err));
      }
      return;
    }
    if (this.currentName === name) return;

    const fade = opts.fade ?? 0.25;
    const next = action;

    // Any new play() supersedes a pending charge-hold (playCharged re-sets it
    // immediately after calling play, so this only clears stale holds).
    this._chargeHold = null;

    if (opts.once) {
      next.setLoop(THREE.LoopOnce, 1);
      next.clampWhenFinished = true;
      this._oneShot = {
        name,
        action: next,
        then: opts.then ?? 'idle',
        interruptible: opts.interruptible === true,
      };
    } else {
      next.setLoop(THREE.LoopRepeat, Infinity);
      next.clampWhenFinished = false;
      this._oneShot = null;
    }

    if (this.currentAction && this.currentAction !== next) {
      this.currentAction.fadeOut(fade);
    }
    // .reset() doesn't clear timeScale (only weight + paused + loop). Player
    // sets timeScale on walking/running each frame to match ground speed,
    // so we must reset it here or a stale value would carry into the next
    // play (e.g. waving played at 0.3× because the player stopped mid-walk).
    next.reset().fadeIn(fade).play();
    next.timeScale = 1;
    // Optional playhead offset — jumps skip their authored anticipation crouch
    // because the physics impulse has already left the ground by the time the
    // clip starts.
    if (opts.startAt) next.time = opts.startAt;

    this.currentName = name;
    this.currentAction = next;
  }

  async #loadDeferredAction(name) {
    if (this.actions[name]) return true;
    const cfg = DEFERRED_BY_ACTION.get(name);
    if (!cfg) return false;
    if (!this._deferredClipPromises.has(name)) {
      this._deferredClipPromises.set(name, (async () => {
        const g = await this.loader.loadGLTF(cfg.url);
        const clip = g.animations?.[0];
        if (!clip) return false;
        if (cfg.retarget) retargetMixamoToAvaturn(clip);
        rebaseClipToBind(clip, g.scene, this.mesh);
        normalizeClipUpAxis(clip);
        stripRootMotion(clip);
        clip.name = name;
        this.actions[name] = this.mixer.clipAction(clip);
        return true;
      })());
    }
    return this._deferredClipPromises.get(name);
  }

  #onActionFinished = (event) => {
    if (!this._oneShot) return;
    const finishedClip = event.action.getClip();
    if (finishedClip.name !== this._oneShot.name) return;
    this.#finishOneShot();
  };

  /**
   * Play a one-shot clip but FREEZE it at `holdTime` (seconds into the clip)
   * until releaseHold() resumes it — for charge-and-release motions where the
   * body cocks at a wind-up frame, holds, then completes the swing on release.
   * Chains to opts.then (default 'idle') once the clip finishes after release.
   * @returns {boolean} false if the clip isn't loaded.
   */
  playCharged(name, holdTime, opts = {}) {
    if (!this.actions[name]) return false;
    this.play(name, { once: true, then: opts.then ?? 'idle', fade: opts.fade ?? 0.2 });
    this._chargeHold = { action: this.actions[name], holdTime };
    return true;
  }

  /** Resume a clip frozen by playCharged so the rest of the motion plays out. */
  releaseHold() {
    if (!this._chargeHold) return;
    this._chargeHold.action.paused = false;
    this._chargeHold = null;
  }

  /** World position of the right wrist bone (or null if unavailable). */
  getHandWorldPosition(out) {
    if (!this.rightHand) return null;
    return this.rightHand.getWorldPosition(out);
  }

  /** Normalised 0..1 playhead of a loaded action (0 if missing). */
  actionProgress(name) {
    const a = this.actions[name];
    if (!a) return 0;
    const dur = a.getClip()?.duration ?? 0;
    return dur > 0 ? a.time / dur : 0;
  }

  #finishOneShot() {
    if (!this._oneShot) return;
    const next = this._oneShot.then;
    this._oneShot = null;
    this._chargeHold = null;
    // Restore the default full-pin as any keepRoot one-shot (the landing)
    // resolves, so the follow-up clip (idle) sits at the right hip height.
    this._rootPin = 'full';
    if (next) this.play(next);
  }

  /**
   * Lowest foot/toe/hand bone height for the current pose, expressed relative
   * to the player group's origin (this.root's parent). Negative means a contact
   * point is below the feet plane (would sink through ground). IntroCinematic
   * lifts the group by -this so the landing crouch never penetrates the floor.
   * @returns {number}
   */
  lowestContactLocalY() {
    if (!this.groundBones.length || !this.root.parent) return 0;
    const groupY = this.root.parent.position.y;
    let lowest = Infinity;
    for (const bone of this.groundBones) {
      const y = bone.getWorldPosition(this._tmpV).y;
      if (y < lowest) lowest = y;
    }
    return lowest === Infinity ? 0 : lowest - groupY;
  }

  /**
   * Plant the feet on the terrain for the current frame's pose. Call AFTER
   * update() (so the mixer + root pin have set the animated pose) and BEFORE
   * anything reads the solved feet (the contact shadow, the renderer). No-op
   * unless IK is enabled, the leg chain resolved, and the current clip is a
   * grounded idle/locomotion pose.
   * @param {{ heightAt:(x:number,z:number)=>number }} terrain
   * @param {number} [snowCoverage] 0..1
   */
  solveFootIK(terrain, snowCoverage = 0) {
    if (!this.footIK?.valid || !terrain) return;
    // Stand ON the snow blanket: the IK raises the ankle targets by the snow
    // surface rise, so the body must ride up by the same amount or the hips
    // stay at bare-ground level and the knees fold. Applied before the pose
    // gates so it persists through one-shots/jumps too (coverage itself ramps
    // over ~30s, so no extra smoothing is needed).
    this.root.position.y = snowCoverage * SNOW_RISE;
    if (this._oneShot || !IK_GROUNDED_POSES.has(this.currentName)) return;

    const parent = this.root.parent;
    if (!parent) return;
    // Fade IK out as the body lifts off the ground (e.g. stepping off a ledge
    // mid-walk) so the planting releases instead of stretching the legs down.
    // The snow rise counts as ground here, not as an air gap.
    const groundY = terrain.heightAt(parent.position.x, parent.position.z)
      + snowCoverage * SNOW_RISE;
    const footY = parent.position.y + this.lowestContactLocalY();
    const airGap = Math.max(0, footY - groundY);
    const t = Math.min(1, airGap / IK_AIR_FADE);
    const weight = 1 - t * t * (3 - 2 * t); // smoothstep, inverted
    if (weight <= 0.001) return;

    this.footIK.solve(terrain, snowCoverage, weight);
  }

  update(delta) {
    if (!this.mixer) return;
    this.mixer.update(delta);
    this.outfits?.update(delta);
    // Charge-hold: once the playhead reaches the wind-up frame, pin it there
    // and pause until releaseHold(). Re-pinning each frame is idempotent.
    if (this._chargeHold) {
      const { action, holdTime } = this._chargeHold;
      if (action.time >= holdTime) {
        action.time = holdTime;
        action.paused = true;
      }
    }
    if (this._oneShot?.action) {
      const action = this._oneShot.action;
      const duration = action.getClip()?.duration ?? 0;
      if (duration > 0 && action.time >= duration - 0.03) {
        this.#finishOneShot();
      }
    }
    if (this.rootBone) {
      if (this._rootPin === 'xz') {
        // Keep the clip's vertical root motion (crouch depth); cancel drift.
        this.rootBone.position.x = this.rootBoneBindPos.x;
        this.rootBone.position.z = this.rootBoneBindPos.z;
      } else {
        this.rootBone.position.copy(this.rootBoneBindPos);
      }
    }
  }
}
