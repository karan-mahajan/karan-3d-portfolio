import * as THREE from 'three';
import gsap from 'gsap';

/**
 * Street lamps placed around the island. Two GLB models alternate for
 * variety — angular (modern, along main paths) and curved (classic, near
 * portfolio sections). Each lamp = a cloned GLB mesh + a thin Rapier
 * cylinder collider on the pole. PointLights are NOT per-lamp — a small
 * pool of 5 lights follows the closest 5 lamps each frame.
 *
 * Performance notes:
 *  - GLBs are loaded once and `.scene.clone(true)` per position so geometry
 *    is shared across instances.
 *  - The bulb glow comes from swapping just the sub-mesh whose source
 *    material is named "Light" (both Quaternius models follow this
 *    convention) with a shared emissive MeshBasicMaterial. The pole +
 *    head meshes keep their original materials so modern and classic
 *    stay visually distinct — and the bloom area stays tiny.
 *  - Only MAX_ACTIVE_LIGHTS PointLights ever exist in the scene. Adding
 *    18 lights inflates THREE's lighting uniforms and re-compiles every
 *    material shader for the new light count; a fixed pool keeps that
 *    cost bounded regardless of how many lamps are placed.
 *  - castShadow is OFF on lamp meshes. Adding 18 tall objects to the
 *    sun's 512² shadow cascade dropped the user from 144 → 30 fps.
 *    Receiving shadows from other casters still works.
 */

const TARGET_LAMP_HEIGHT = 3.6;
const MAX_ACTIVE_LIGHTS = 5;
const POLE_COLLIDER_RADIUS = 0.15;
const LIGHT_COLOR = 0xffe8c0;
const LIGHT_DISTANCE = 12;
const LIGHT_DECAY = 1.5;
// Base bulb tint. Day = colour × 0 (black, unlit). Night = colour × brightness
// (bloom picks up anything past 1.0 in linear space when toneMapped=false).
const BULB_BASE_HEX = 0xfff0c8;
const NIGHT_BULB_BRIGHTNESS = 2.0;
const NIGHT_LIGHT_INTENSITY = 1.5;

// Spread around the island. Mix of `modern` (angular) along main paths and
// `classic` (curved) near portfolio sections and shore perimeter.
const LAMP_POSITIONS = [
  // Inner ring along the cardinal paths — modern
  { x:   8, z:   0, type: 'modern'  },
  { x:  -8, z:   0, type: 'modern'  },
  { x:   0, z:   8, type: 'modern'  },
  { x:   0, z:  -8, type: 'modern'  },
  // Outer ring along the cardinal paths — modern
  { x:  18, z:   0, type: 'modern'  },
  { x: -18, z:   0, type: 'modern'  },
  { x:   0, z:  18, type: 'modern'  },
  { x:   0, z: -18, type: 'modern'  },
  // Diagonals near portfolio sections — classic
  { x:  12, z:  12, type: 'classic' },
  { x: -12, z:  12, type: 'classic' },
  { x:  12, z: -12, type: 'classic' },
  { x: -12, z: -12, type: 'classic' },
  // Perimeter — classic
  { x:  25, z:   0, type: 'classic' },
  { x: -25, z:   0, type: 'classic' },
  { x:   0, z:  25, type: 'classic' },
  { x:   0, z: -25, type: 'classic' },
  // Extras
  { x:  15, z:   8, type: 'modern'  },
  { x: -10, z: -15, type: 'classic' },
];

export class StreetLights {
  constructor(scene, loader, terrain, physics = null) {
    this.scene = scene;
    this.loader = loader;
    this.terrain = terrain;
    this.physics = physics;
    /** @type {Array<{ group: THREE.Group, bulbWorldPos: THREE.Vector3, position: THREE.Vector3, type: string }>} */
    this.lamps = [];
    /** Shared bulb material per type — MeshBasicMaterial with toneMapped:false
     *  so multiplying color past 1.0 reaches the bloom threshold. Day mode
     *  multiplies by 0 (black bulb); night by NIGHT_BULB_BRIGHTNESS. */
    this.bulbMaterials = { modern: null, classic: null };
    /** Cached bulb sub-mesh references per type so update() can hide them
     *  entirely while their shared material is fully unlit (day) — skips
     *  the per-bulb draw call even though the mesh is trivially cheap. */
    this.bulbMeshes = { modern: [], classic: [] };
    /** @type {THREE.PointLight[]} Fixed pool, reused frame-to-frame. */
    this._lightPool = [];
    this.mode = 'day';
    this._currentLightIntensity = 0;
    this._activeTweens = [];
  }

  async load() {
    // Filename with a space needs URL-encoding for fetch().
    const modernUrl  = '/models/props/Streetlight.glb';
    const classicUrl = '/models/props/Street%20Light.glb';

    const [modernGltf, classicGltf] = await Promise.all([
      this.loader.loadGLTF(modernUrl).catch((err) => {
        console.warn('[StreetLights] modern model load failed:', err);
        return null;
      }),
      this.loader.loadGLTF(classicUrl).catch((err) => {
        console.warn('[StreetLights] classic model load failed:', err);
        return null;
      }),
    ]);

    const protos = {
      modern: modernGltf?.scene ?? null,
      classic: classicGltf?.scene ?? null,
    };
    for (const key of ['modern', 'classic']) {
      this.bulbMaterials[key] = new THREE.MeshBasicMaterial({
        color: 0x000000,           // starts unlit (day default)
        toneMapped: false,
        fog: true,
      });
    }

    // Build the fixed PointLight pool once. Five lights total, regardless
    // of lamp count — see class comment for the rationale.
    for (let i = 0; i < MAX_ACTIVE_LIGHTS; i++) {
      const light = new THREE.PointLight(LIGHT_COLOR, 0, LIGHT_DISTANCE, LIGHT_DECAY);
      light.castShadow = false;
      light.visible = false; // promoted to visible only when active (see update())
      light.name = `streetlight-pool-${i}`;
      this.scene.add(light);
      this._lightPool.push(light);
    }

    for (const spot of LAMP_POSITIONS) {
      const proto = protos[spot.type] ?? protos.modern ?? protos.classic;
      if (!proto) continue;
      this.#placeLamp(proto, spot, this.bulbMaterials[spot.type]);
    }

    return this.lamps.length;
  }

  #placeLamp(proto, spot, bulbMat) {
    const groundY = this.terrain ? this.terrain.heightAt(spot.x, spot.z) : 0;

    const clone = proto.clone(true);
    clone.updateMatrixWorld(true);
    // Auto-fit to TARGET_LAMP_HEIGHT regardless of native GLB scale.
    const measureBox = new THREE.Box3().setFromObject(clone);
    const measureSize = measureBox.getSize(new THREE.Vector3());
    const maxDim = Math.max(measureSize.x, measureSize.y, measureSize.z) || 1;
    const scale = TARGET_LAMP_HEIGHT / maxDim;
    clone.scale.setScalar(scale);
    clone.updateMatrixWorld(true);

    // Lift clone so its bottom sits on the terrain — GLB origins aren't
    // always at the model's base.
    const fitBox = new THREE.Box3().setFromObject(clone);
    const liftY = groundY - fitBox.min.y;

    const group = new THREE.Group();
    group.position.set(spot.x, liftY, spot.z);
    group.name = `streetlight:${spot.type}:${spot.x},${spot.z}`;
    group.add(clone);

    // Swap only the sub-mesh whose source material is named "Light" — the
    // bulb/LED on both Quaternius models. Pole + head keep their original
    // materials so modern and classic stay visually distinct.
    let bulbCenter = new THREE.Vector3(spot.x, liftY + TARGET_LAMP_HEIGHT - 0.2, spot.z);
    clone.traverse((child) => {
      if (!child.isMesh) return;
      // Shadow-pass cost on tall thin geometry tanked FPS (144 → 30 with
      // 18 lamps × N submeshes). Receiving still works for the broader
      // landscape shadow falling across the pole.
      child.castShadow = false;
      child.receiveShadow = true;
      if (child.material?.name === 'Light') {
        child.material = bulbMat;
        // Start hidden — update() flips this on once the shared bulb
        // material brightens past the night threshold.
        child.visible = false;
        this.bulbMeshes[spot.type].push(child);
        // Recompute world bbox after material swap — needed so the
        // PointLight pool can be placed at the actual bulb position.
        const b = new THREE.Box3().setFromObject(child);
        if (b.isEmpty() === false) bulbCenter = b.getCenter(new THREE.Vector3());
      }
    });

    // Recompute final scaled bounds for collider sizing.
    const finalBox = new THREE.Box3().setFromObject(group);
    const finalSize = finalBox.getSize(new THREE.Vector3());
    const poleHeight = Math.max(0.5, finalSize.y);

    this.scene.add(group);

    if (this.physics?.addStaticCylinder) {
      this.physics.addStaticCylinder(
        spot.x,
        groundY,
        spot.z,
        POLE_COLLIDER_RADIUS,
        poleHeight,
      );
    }

    this.lamps.push({
      group,
      bulbWorldPos: bulbCenter,
      position: new THREE.Vector3(spot.x, groundY, spot.z),
      type: spot.type,
    });
  }

  /** Per-frame: pick the MAX_ACTIVE_LIGHTS closest lamps and reuse the
   *  PointLight pool to illuminate them. Cheap O(N) sort over ~18 lamps.
   *  Pool lights AND bulb meshes have `.visible` toggled in lockstep with
   *  their effective brightness so day-mode skips both (a) the per-pixel
   *  point-light loop slot and (b) the per-bulb draw call. First toggle in
   *  each direction may compile a new shader program (point-light count
   *  changes 1↔6); subsequent toggles re-use the cached programs. */
  update(playerPos) {
    // Bulb sub-mesh visibility tracks the SHARED bulb material's color
    // brightness — both modern + classic materials lerp together so we
    // can check once per type. Threshold is well below the tween's
    // mid-fade values so the flip happens at the very start/end of the
    // transition where the mesh is essentially black anyway.
    for (const type of ['modern', 'classic']) {
      const mat = this.bulbMaterials[type];
      const meshes = this.bulbMeshes[type];
      if (!mat || !meshes.length) continue;
      const brightness = mat.color.r + mat.color.g + mat.color.b;
      const shouldShow = brightness > 0.001;
      for (const bulb of meshes) {
        if (bulb.visible !== shouldShow) bulb.visible = shouldShow;
      }
    }

    if (!this._lightPool.length || !this.lamps.length) return;

    const intensity = this._currentLightIntensity;
    if (intensity <= 0.001) {
      // Day (or mid-fade to day) — pull every pool light out of the
      // lighting array so the shader skips the loop entirely.
      for (const l of this._lightPool) {
        l.intensity = 0;
        if (l.visible) l.visible = false;
      }
      return;
    }

    const dists = [];
    for (let i = 0; i < this.lamps.length; i++) {
      const p = this.lamps[i].position;
      const dx = p.x - playerPos.x;
      const dz = p.z - playerPos.z;
      dists.push({ i, d2: dx * dx + dz * dz });
    }
    dists.sort((a, b) => a.d2 - b.d2);

    for (let k = 0; k < this._lightPool.length; k++) {
      const light = this._lightPool[k];
      if (k < dists.length) {
        const lamp = this.lamps[dists[k].i];
        light.position.copy(lamp.bulbWorldPos);
        light.intensity = intensity;
        if (!light.visible) light.visible = true;
      } else {
        light.intensity = 0;
        if (light.visible) light.visible = false;
      }
    }
  }

  /** Called by TimeOfDay on day↔night flip. duration=0 snaps instantly.
   *  Bulb emissive lerps via the shared MeshBasicMaterial.color tween
   *  (toneMapped:false so we can push past 1.0 for bloom). */
  setMode(mode, duration = 2) {
    this.mode = mode;
    for (const t of this._activeTweens) t.kill();
    this._activeTweens = [];

    const targetLightIntensity = mode === 'night' ? NIGHT_LIGHT_INTENSITY : 0;
    const bulbBrightness = mode === 'night' ? NIGHT_BULB_BRIGHTNESS : 0;
    const targetColor = new THREE.Color(BULB_BASE_HEX).multiplyScalar(bulbBrightness);

    if (duration <= 0) {
      this._currentLightIntensity = targetLightIntensity;
      for (const key of ['modern', 'classic']) {
        const mat = this.bulbMaterials[key];
        if (mat) mat.color.copy(targetColor);
      }
      return;
    }

    const ease = 'sine.inOut';
    this._activeTweens.push(
      gsap.to(this, { _currentLightIntensity: targetLightIntensity, duration, ease }),
    );
    for (const key of ['modern', 'classic']) {
      const mat = this.bulbMaterials[key];
      if (!mat) continue;
      this._activeTweens.push(
        gsap.to(mat.color, {
          r: targetColor.r, g: targetColor.g, b: targetColor.b,
          duration, ease,
        }),
      );
    }
  }
}
