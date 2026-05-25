import * as THREE from 'three';

/**
 * Night-only torch beam that lights whatever the mouse points at.
 *
 *   SpotLight  — anchored to the torch flame, aimed at the
 *                first surface the mouse-NDC ray hits. Off in day.
 *   PointLight — a soft warm "pool" placed just above the hit surface.
 *
 * Performance: the per-tick intersect is restricted to scene.children
 * filtered by `userData.noTorchRaycast` — heavy effects (grass tufts,
 * leaves, fireflies, wind lines, rain, water, sky, character) are all
 * flagged in App.js so they don't enter the recursive raycast. Distance
 * is capped via raycaster.far = 22. Each intersection is then re-checked
 * up its parent chain in case a flagged subtree was missed.
 *
 * On touch-only devices the mouse mechanic is silently disabled (the torch
 * still shows in the player's hand and flickers). During billboard /
 * contact modal focus the beam is suppressed so it doesn't bleed across
 * the focused-view camera.
 */

const SPOT_AIM_INTENSITY = 4.6;
const POOL_AIM_INTENSITY = 1.9;
const INTENSITY_LERP = 0.12;
// The camera ray needs to reach a little past the player, but the final hit
// is still gated by torch-to-hit distance so faraway cursor targets do not
// light up from across the island.
const RAYCAST_FAR = 12;
const MAX_TORCH_HIT_DISTANCE = 6.75;
const POOL_NORMAL_OFFSET = 0.05;
const HAND_LIGHT_FLICKER_AMOUNT = 0.3;

const _handPos = new THREE.Vector3();
const _aimPoint = new THREE.Vector3();
const _poolPoint = new THREE.Vector3();

export class TorchLight {
  #scene;
  #camera;
  #character;
  #timeOfDay;
  #terrain;
  #canvas;

  #raycaster;
  #ndc;
  #hasPointer;
  #pointerInside;
  #onMove;

  #spotLight;
  #spotTarget;
  #helper;
  #poolLight;
  #decal;

  #targetsBuf;
  #suppressed;

  constructor({ scene, camera, character, timeOfDay, terrain, debug = false }) {
    this.#scene = scene;
    this.#camera = camera;
    this.#character = character;
    this.#timeOfDay = timeOfDay;
    this.#terrain = terrain;
    this.#canvas = document.getElementById('canvas');

    this.#raycaster = new THREE.Raycaster();
    this.#raycaster.far = RAYCAST_FAR;
    this.#ndc = new THREE.Vector2();
    this.#hasPointer = typeof window !== 'undefined'
      && typeof window.matchMedia === 'function'
      && window.matchMedia('(pointer: fine)').matches;
    this.#pointerInside = this.#hasPointer;
    this.#targetsBuf = [];
    this.#suppressed = false;

    this.#spotLight = new THREE.SpotLight(0xffc870, 0, 18, Math.PI / 5, 0.55, 1.5);
    this.#spotLight.castShadow = false;
    this.#spotTarget = new THREE.Object3D();
    this.#spotLight.target = this.#spotTarget;
    this.#scene.add(this.#spotLight);
    this.#scene.add(this.#spotTarget);

    // Pool is a tight surface pool of warm yellow at the hit point. Range
    // 3.5m so it falls off well before MAX_TORCH_HIT_DISTANCE (6.75m) and
    // never bleeds beyond what the cursor is actually pointing at.
    this.#poolLight = new THREE.PointLight(0xffb060, 0, 3.5, 2);
    this.#poolLight.castShadow = false;
    this.#scene.add(this.#poolLight);

    const decalGeom = new THREE.CircleGeometry(0.01, 8);
    const decalMat = new THREE.MeshBasicMaterial({
      color: 0xffaa66,
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false,
      toneMapped: false,
    });
    this.#decal = new THREE.Mesh(decalGeom, decalMat);
    this.#decal.renderOrder = 6;
    this.#decal.frustumCulled = false;
    this.#decal.visible = false;
    this.#decal.userData.noTorchRaycast = true;
    this.#scene.add(this.#decal);

    if (debug) {
      this.#helper = new THREE.SpotLightHelper(this.#spotLight);
      this.#helper.userData.noTorchRaycast = true;
      this.#scene.add(this.#helper);
    }

    if (this.#hasPointer && this.#canvas) {
      this.#onMove = (e) => {
        const rect = this.#canvas.getBoundingClientRect();
        if (!rect.width || !rect.height) return;
        this.#ndc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.#ndc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        this.#pointerInside = true;
      };
      this.#canvas.addEventListener('mousemove', this.#onMove);
      this.#canvas.addEventListener('mouseleave', () => { this.#pointerInside = false; });
    }
  }

  /** Tells the beam to back off while a modal/focused view is open. */
  setSuppressed(value) {
    this.#suppressed = !!value;
  }

  /** Returns true when the torch is showing AND we're currently in the
   *  torchAim loop — used by App.js / Interaction.js for state checks. */
  get isAiming() {
    return this.#character?.torchOverlayName === 'torchAim';
  }

  /**
   * @param {THREE.Vector3} playerPos
   * @param {THREE.Camera}  camera
   */
  tick(playerPos, camera) {
    const torchVisible = this.#character?.torchMesh?.visible === true;
    const isNight = this.#timeOfDay?.mode === 'night';
    const aimActive = torchVisible && isNight && this.isAiming && !this.#suppressed;

    if (this.#character?.torchLight) {
      this.#character.torchLight.visible = aimActive;
      this.#character.torchLight.intensity = this.#character.torchLightBaseIntensity
        + (Math.random() - 0.5) * HAND_LIGHT_FLICKER_AMOUNT;
    }
    this.#character?.setTorchFlameIntensity?.(
      torchVisible
        ? (aimActive ? this.#character.torchFlameAimIntensity : this.#character.torchFlameIdleIntensity)
        : 0,
    );

    // Beam is now strictly an aim-mode effect — the prior "dim glow at
    // night by default" read as a cursor-attached light following the
    // user around the world even when they weren't pointing anything.
    if (!aimActive || !this.#hasPointer || !this.#pointerInside) {
      this.#character?.setTorchAimTarget?.(null);
      this.#fadeOff();
      return;
    }

    if (!this.#character?.torchHandBone) {
      this.#character?.setTorchAimTarget?.(null);
      this.#fadeOff();
      return;
    }

    if (this.#character.torchLight) this.#character.torchLight.getWorldPosition(_handPos);
    else this.#character.torchHandBone.getWorldPosition(_handPos);

    this.#raycaster.setFromCamera(this.#ndc, camera);
    this.#targetsBuf.length = 0;
    for (const child of this.#scene.children) {
      if (child === this.#spotLight) continue;
      if (child === this.#spotTarget) continue;
      if (child === this.#poolLight) continue;
      if (child === this.#decal) continue;
      if (child === this.#helper) continue;
      if (child.visible === false) continue;
      if (child.userData?.noTorchRaycast) continue;
      this.#targetsBuf.push(child);
    }
    const intersections = this.#raycaster.intersectObjects(this.#targetsBuf, true);

    let hit = null;
    for (const inter of intersections) {
      if (this.#shouldSkip(inter.object)) continue;
      hit = inter;
      break;
    }

    let closeHit = null;
    if (hit && hit.point.distanceTo(_handPos) <= MAX_TORCH_HIT_DISTANCE) {
      closeHit = hit;
    }
    _aimPoint
      .copy(this.#raycaster.ray.direction)
      .multiplyScalar(MAX_TORCH_HIT_DISTANCE)
      .add(_handPos);
    this.#spotLight.position.copy(_handPos);
    const aimWorldPoint = closeHit?.point ?? _aimPoint;
    this.#spotTarget.position.copy(aimWorldPoint);
    this.#spotTarget.updateMatrixWorld();
    // Drive the upper-arm IK aim. Always push a target while the cursor
    // is on-canvas in aim mode — when there is no close hit, _aimPoint
    // is a synthetic point at MAX_TORCH_HIT_DISTANCE along the camera
    // ray, so the arm still tracks the cursor instead of resetting.
    this.#character?.setTorchAimTarget?.(aimWorldPoint);

    this.#poolLight.position.copy(this.#poolPointFor(closeHit?.point ?? _aimPoint));
    this.#poolLight.intensity = THREE.MathUtils.lerp(this.#poolLight.intensity, POOL_AIM_INTENSITY, INTENSITY_LERP);

    this.#spotLight.intensity = THREE.MathUtils.lerp(this.#spotLight.intensity, SPOT_AIM_INTENSITY, INTENSITY_LERP);
    this.#decal.visible = false;
    this.#decal.material.opacity = 0;

    this.#helper?.update();
  }

  #fadeOff() {
    this.#spotLight.intensity = THREE.MathUtils.lerp(this.#spotLight.intensity, 0, INTENSITY_LERP);
    this.#poolLight.intensity = THREE.MathUtils.lerp(this.#poolLight.intensity, 0, INTENSITY_LERP);
    if (this.#spotLight.intensity < 0.01) this.#spotLight.intensity = 0;
    if (this.#poolLight.intensity < 0.01) this.#poolLight.intensity = 0;
    const fade = THREE.MathUtils.lerp(this.#decal.material.opacity, 0, INTENSITY_LERP);
    this.#decal.material.opacity = fade < 0.01 ? 0 : fade;
    if (this.#decal.material.opacity === 0) this.#decal.visible = false;
    this.#helper?.update();
  }

  #shouldSkip(object) {
    let o = object;
    while (o) {
      if (o.visible === false) return true;
      if (o.userData?.noTorchRaycast) return true;
      // Name-based fallback so anything from the avatar GLB hierarchy
      // (clothing, hair, "Avatar_Body" meshes, etc.) is rejected even if
      // the userData flag wasn't propagated to it.
      if (o.name && /(avatar|character)/i.test(o.name)) return true;
      o = o.parent;
    }
    return false;
  }

  #poolPointFor(point) {
    _poolPoint.copy(point);
    if (this.#terrain?.heightAt) {
      _poolPoint.y = this.#terrain.heightAt(point.x, point.z) + POOL_NORMAL_OFFSET;
    } else {
      _poolPoint.y += POOL_NORMAL_OFFSET;
    }
    return _poolPoint;
  }

  destroy() {
    if (this.#onMove && this.#canvas) {
      this.#canvas.removeEventListener('mousemove', this.#onMove);
    }
    this.#scene.remove(this.#spotLight);
    this.#scene.remove(this.#spotTarget);
    this.#scene.remove(this.#poolLight);
    this.#scene.remove(this.#decal);
    if (this.#helper) this.#scene.remove(this.#helper);
    this.#decal.geometry?.dispose?.();
    this.#decal.material?.dispose?.();
  }
}
