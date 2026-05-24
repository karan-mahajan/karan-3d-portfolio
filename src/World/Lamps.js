import * as THREE from 'three';

/**
 * Physical lamps placed next to every readable sign / billboard. Each
 * lamp = one cloned Lantern.glb mesh + one PointLight at the bulb. The
 * lights are static (no per-frame work) and capped at MAX_LAMPS so the
 * scene's total active light count stays under control.
 *
 * Behaviour by mode (TimeOfDay drives the intensity lerp):
 *   day   → PointLight intensity 0.3, bulb emissive dim
 *   night → PointLight intensity 1.2, bulb emissive bright + bloom halo
 *
 * Performance:
 *   - Single GLB load; .scene.clone(true) per instance reuses the geometry
 *   - All PointLights are castShadow=false
 *   - The bulb material is shared across instances so the emissive lerp
 *     done in TimeOfDay touches one material, not N materials
 */
// 10 lamp PointLights dropped the user's FPS from 144 → 100. The spec
// allowed up to 10 but five well-placed lamps (welcome, two billboards,
// skills, contact) cover the most-read text and keep the light count
// closer to the original FPS-tuned baseline.
const MAX_LAMPS = 5;
const LAMP_HEIGHT = 2.4;
const TARGET_LAMP_HEIGHT = 1.7;
const POINT_LIGHT_DISTANCE = 9;
const POINT_LIGHT_DECAY = 1.5;
const LIGHT_COLOR = 0xffd58a;

export class Lamps {
  constructor(scene, loader) {
    this.scene = scene;
    this.loader = loader;
    this.items = [];           // { group, light, bulbMat }
    this.bulbMaterial = null;   // shared across all lamp clones
    this.proto = null;          // GLB scene cached for cloning
  }

  /** Load the lantern GLB once, then place lamps at the planned spots.
   *  Falls back to a procedural pole+bulb lamp if the GLB load fails. */
  async load({ signs, billboards }) {
    let lanternRoot = null;
    try {
      const gltf = await this.loader.loadGLTF('/models/props/Lantern.glb');
      lanternRoot = gltf.scene;
    } catch (err) {
      console.warn('[Lamps] Lantern.glb failed, falling back to procedural', err);
    }

    this.bulbMaterial = new THREE.MeshBasicMaterial({
      color: 0xffe9b0,
      toneMapped: false,
      transparent: false,
    });

    const spots = this.#planSpots({ signs, billboards });
    for (const spot of spots.slice(0, MAX_LAMPS)) {
      this.#placeLamp(lanternRoot, spot);
    }

    return this.items.length;
  }

  /**
   * Choose at most MAX_LAMPS positions, prioritising areas the player
   * needs to read at night: welcome board, billboards, then signs.
   */
  #planSpots({ signs, billboards }) {
    const spots = [];

    // 1. Welcome board (at spawn — most-seen object in the world)
    if (signs?.compassPosition) {
      const p = signs.compassPosition;
      spots.push({ x: p.x + 2.4, z: p.z - 0.6, label: 'welcome' });
    }
    // 2. Skills board
    if (signs?.skillsPosition) {
      const p = signs.skillsPosition;
      spots.push({ x: p.x + 2.4, z: p.z + 2.2, label: 'skills' });
    }
    // 3. Contact mailbox
    if (signs?.contactPosition) {
      const p = signs.contactPosition;
      spots.push({ x: p.x + 2.2, z: p.z + 1.5, label: 'contact' });
    }
    // 4-5. Two billboards (first and last) cover the project arc.
    if (billboards?.items?.length) {
      const idxs = billboards.items.length >= 4
        ? [0, billboards.items.length - 1]
        : [0];
      for (const i of idxs) {
        const item = billboards.items[i];
        const inset = 1.8;
        const dirX = -item.position.x / Math.max(0.001, Math.hypot(item.position.x, item.position.z));
        const dirZ = -item.position.z / Math.max(0.001, Math.hypot(item.position.x, item.position.z));
        spots.push({
          x: item.position.x + dirX * inset,
          z: item.position.z + dirZ * inset,
          label: `billboard-${i}`,
        });
      }
    }
    return spots;
  }

  #placeLamp(lanternRoot, spot) {
    const group = new THREE.Group();
    group.position.set(spot.x, 0, spot.z);
    group.name = `lamp:${spot.label}`;

    let bulbY = 2.0;

    if (lanternRoot) {
      // Clone the lantern model + auto-fit so the largest dimension is
      // TARGET_LAMP_HEIGHT regardless of the GLB's native scale.
      const clone = lanternRoot.clone(true);
      clone.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(clone);
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      const s = TARGET_LAMP_HEIGHT / maxDim;
      clone.scale.setScalar(s);
      clone.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = false;
          child.receiveShadow = true;
        }
      });
      group.add(clone);
      bulbY = TARGET_LAMP_HEIGHT * 0.7;
    } else {
      // Procedural fallback — simple pole + housing + bulb.
      const pole = new THREE.Mesh(
        new THREE.CylinderGeometry(0.05, 0.06, 2.5, 8),
        new THREE.MeshStandardMaterial({ color: 0x3a3a3a, roughness: 0.7 }),
      );
      pole.position.y = 1.25;
      pole.castShadow = false;
      pole.receiveShadow = true;
      group.add(pole);

      const housing = new THREE.Mesh(
        new THREE.CylinderGeometry(0.15, 0.2, 0.3, 8),
        new THREE.MeshStandardMaterial({ color: 0x2a2a2a, roughness: 0.5 }),
      );
      housing.position.y = 2.5;
      housing.castShadow = false;
      group.add(housing);
      bulbY = 2.35;
    }

    // Glowing bulb — shared material across all lamps so day/night
    // emissive switches touch one material instead of N.
    const bulb = new THREE.Mesh(
      new THREE.SphereGeometry(0.13, 12, 10),
      this.bulbMaterial,
    );
    bulb.position.y = bulbY;
    group.add(bulb);

    const light = new THREE.PointLight(LIGHT_COLOR, 0, POINT_LIGHT_DISTANCE, POINT_LIGHT_DECAY);
    light.position.y = bulbY;
    light.castShadow = false;
    group.add(light);

    this.scene.add(group);
    this.items.push({ group, light, bulb });
  }

  /** Hard-set lamp intensities + bulb emissive. Called by TimeOfDay
   *  on construction and instant re-applies. */
  apply({ intensity, bulbColor, bulbBrightness }) {
    for (const item of this.items) {
      item.light.intensity = intensity;
    }
    if (this.bulbMaterial) {
      this.bulbMaterial.color.set(bulbColor);
      // MeshBasicMaterial doesn't have intensity per se — emulate by
      // multiplying the color by the brightness factor (toneMapped:false).
      this.bulbMaterial.color.multiplyScalar(bulbBrightness);
    }
  }
}
