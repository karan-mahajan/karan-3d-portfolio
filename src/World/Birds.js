import * as THREE from 'three';

/**
 * Birds populate three behaviors:
 *   - flying    : circle overhead at a fixed altitude, wings flap
 *   - perched   : sit on top of a billboard / sign, occasional head bob
 *   - grounded  : idle on the grass near spawn / paths, small hop bob
 *
 * Each bird is a low-poly placeholder (body + wings + tail) — when a real
 * GLB is dropped at `/models/wildlife/bird.glb` the constructor will use it
 * instead, replicating it across all 3 behavior types.
 */

// Per-behavior pools. Every URL listed under a behavior is attempted; any
// that load successfully become candidates and are randomly chosen for each
// instance. Missing files are skipped (no error). Drop any subset.
// Note: animated birds typically ship as gltf+bin pairs; static ones as .glb.
const MODELS = {
  // Flock (bird-fly) disabled — its rig dips the body to the ground
  // regardless of position. Keeping flamingo only for flying.
  fly: [
    '/models/wildlife/bird-fly-2/scene.gltf',
    '/models/wildlife/bird-fly-2.glb',
  ],
  perched: [
    '/models/wildlife/bird-perched.glb',
    '/models/wildlife/bird-perched-2.glb',
  ],
  ground: [
    '/models/wildlife/bird-ground.glb',
    '/models/wildlife/bird-ground-2.glb',
  ],
};

const BODY_COLOR = '#2d2218';
const WING_COLOR = '#1f1810';
const BEAK_COLOR = '#e4a13e';

function makeProceduralBird() {
  const group = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.SphereGeometry(0.13, 12, 8),
    new THREE.MeshStandardMaterial({ color: BODY_COLOR, roughness: 0.85 }),
  );
  body.scale.set(1, 0.85, 1.5);
  body.castShadow = true;
  group.add(body);

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.09, 10, 8),
    new THREE.MeshStandardMaterial({ color: BODY_COLOR, roughness: 0.85 }),
  );
  head.position.set(0, 0.05, 0.18);
  head.castShadow = true;
  group.add(head);

  const beak = new THREE.Mesh(
    new THREE.ConeGeometry(0.03, 0.08, 6),
    new THREE.MeshStandardMaterial({ color: BEAK_COLOR, roughness: 0.6 }),
  );
  beak.rotation.x = Math.PI / 2;
  beak.position.set(0, 0.04, 0.27);
  group.add(beak);

  // Two wings — separate groups so we can flap them independently.
  const wingGeom = new THREE.ConeGeometry(0.08, 0.34, 6);
  const wingMat = new THREE.MeshStandardMaterial({ color: WING_COLOR, roughness: 0.9 });

  const leftWing = new THREE.Group();
  const leftWingMesh = new THREE.Mesh(wingGeom, wingMat);
  leftWingMesh.rotation.z = Math.PI / 2;
  leftWingMesh.position.x = -0.17;
  leftWing.add(leftWingMesh);
  leftWing.position.set(0, 0.02, 0);
  group.add(leftWing);

  const rightWing = new THREE.Group();
  const rightWingMesh = new THREE.Mesh(wingGeom, wingMat);
  rightWingMesh.rotation.z = -Math.PI / 2;
  rightWingMesh.position.x = 0.17;
  rightWing.add(rightWingMesh);
  rightWing.position.set(0, 0.02, 0);
  group.add(rightWing);

  // Tail.
  const tail = new THREE.Mesh(
    new THREE.ConeGeometry(0.06, 0.12, 6),
    wingMat,
  );
  tail.rotation.x = -Math.PI / 2;
  tail.position.set(0, 0.02, -0.2);
  group.add(tail);

  group.userData.leftWing = leftWing;
  group.userData.rightWing = rightWing;
  group.userData.flapAmp = 0.7;
  return group;
}

export class Birds {
  constructor(scene, loader = null) {
    this.scene = scene;
    this.loader = loader;
    this.flyingBirds = [];
    this.perchedBirds = [];
    this.groundedBirds = [];
    /** per-behavior arrays of loaded GLTF templates. Empty array = procedural. */
    this.templates = { fly: [], perched: [], ground: [] };
    this.modelMixers = [];
  }

  async load(billboards = null, signs = null) {
    if (this.loader) {
      for (const [behavior, urls] of Object.entries(MODELS)) {
        for (const url of urls) {
          try {
            const gltf = await this.loader.loadGLTF(url);
            this.templates[behavior].push(gltf);
          } catch (_) { /* skip missing */ }
        }
      }
    }

    // Round-robin counters so every loaded species is guaranteed to appear.
    this._poolIndex = { fly: 0, perched: 0, ground: 0 };

    this.#spawnFlying();
    this.#spawnPerched(billboards, signs);
  }

  /**
   * Compute the real visible bounding box of an object — union of each
   * mesh's geometry.boundingBox in world space. Reliable for skinned meshes
   * where Box3.setFromObject returns the wrong (bind-pose-only) extent.
   */
  #measureBox(obj) {
    obj.updateMatrixWorld(true);
    const box = new THREE.Box3();
    obj.traverse((c) => {
      if (c.isMesh && c.geometry) {
        if (!c.geometry.boundingBox) c.geometry.computeBoundingBox();
        const meshBox = c.geometry.boundingBox.clone();
        meshBox.applyMatrix4(c.matrixWorld);
        box.union(meshBox);
      }
    });
    return box;
  }

  #cloneBird(behavior) {
    const pool = this.templates[behavior];
    if (pool && pool.length > 0) {
      const idx = (this._poolIndex[behavior] ?? 0) % pool.length;
      this._poolIndex[behavior] = idx + 1;
      const template = pool[idx];
      const cloned = template.scene.clone(true);
      cloned.traverse((c) => {
        if (c.isMesh) {
          c.castShadow = true;
          c.receiveShadow = true;
        }
      });

      const wrapper = new THREE.Group();
      wrapper.add(cloned);

      // Upright correction: if Y is smallest dim, the model is lying flat.
      let box = this.#measureBox(cloned);
      let size = box.getSize(new THREE.Vector3());
      if (size.y < size.z * 0.6 && size.y < size.x * 0.6) {
        cloned.rotation.x = -Math.PI / 2;
        box = this.#measureBox(cloned);
        size = box.getSize(new THREE.Vector3());
      }

      // Ground the feet at wrapper-local y=0 (use min from real geometry box).
      cloned.position.y -= box.min.y;
      box = this.#measureBox(cloned);
      size = box.getSize(new THREE.Vector3());

      // Scale-to-fit. Skinned-mesh bind-pose boxes are unreliable, so for
      // animated flying birds we don't trust the measurement — we use a
      // safe fixed scale instead. Perched/ground use the measurement
      // (their models are static).
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      if (behavior === 'fly') {
        // Quaternius/CC0 animated birds typically ship close to 1m at
        // native scale. Trust that; user-tunable below.
        wrapper.scale.setScalar(1.0);
      } else {
        const targetMax = 0.6;
        wrapper.scale.multiplyScalar(targetMax / maxDim);
      }

      if (template.animations?.length) {
        const mixer = new THREE.AnimationMixer(cloned);
        const clip = template.animations.find((a) =>
          new RegExp(behavior === 'fly' ? '(fly|flying)' :
                     behavior === 'perched' ? '(idle|sit|perch)' :
                     '(idle|walk|ground)', 'i').test(a.name)
        ) ?? template.animations[0];
        mixer.clipAction(clip).play();
        this.modelMixers.push(mixer);
      }
      wrapper.userData.fromModel = true;
      // Skinned bounds are unreliable — keep the bird visible from any angle.
      cloned.traverse((c) => { if (c.isMesh) c.frustumCulled = false; });
      return wrapper;
    }
    return makeProceduralBird();
  }

  // Birds circling overhead at varying altitudes & speeds. Slowed + more
  // populated for a calmer "always there" presence.
  #spawnFlying() {
    for (let i = 0; i < 9; i++) {
      const bird = this.#cloneBird('fly');
      if (!this.templates.fly.length) bird.scale.setScalar(1);
      // No shadow casting — at this altitude + sun angle the drop shadow
      // lands right under the bird and looks like a bird on the grass.
      // Setting both on Mesh and SkinnedMesh subclasses.
      bird.traverse((c) => {
        if (c.isMesh || c.isSkinnedMesh) {
          c.castShadow = false;
          c.receiveShadow = false;
        }
      });
      const radius = 14 + Math.random() * 12;     // 14–26
      const altitude = 12 + Math.random() * 6;    // 12–18, safely above heads
      const speed = 0.12 + Math.random() * 0.18;
      const phase = Math.random() * Math.PI * 2;
      bird.userData.flightCircle = { radius, altitude, speed, phase, t: 0 };

      // CRITICAL: place the bird at its first orbit position immediately, so
      // it never renders at world (0,0,0) on the first frame before update().
      const x = Math.cos(phase) * radius;
      const z = Math.sin(phase) * radius;
      bird.position.set(x, altitude, z);
      bird.rotation.y = Math.atan2(-Math.sin(phase), Math.cos(phase)) + Math.PI / 2;

      this.scene.add(bird);
      this.flyingBirds.push(bird);
    }
  }

  // 1 perched bird on top of each billboard + each experience sign.
  #spawnPerched(billboards, signs) {
    const perches = [];
    if (billboards?.items) {
      for (const item of billboards.items) {
        perches.push({ x: item.position.x, y: 4.2, z: item.position.z });
      }
    }
    if (signs?.experienceItems) {
      for (const item of signs.experienceItems) {
        perches.push({ x: item.position.x, y: 2.95, z: item.position.z });
      }
    }
    // Don't put a bird on every single perch — too crowded. Pick ~70%.
    const chosen = perches.filter(() => Math.random() < 0.7);
    for (const p of chosen) {
      const bird = this.#cloneBird('perched');
      if (!this.templates.perched.length) bird.scale.setScalar(0.9);
      bird.position.set(p.x, p.y, p.z);
      bird.rotation.y = Math.random() * Math.PI * 2;
      bird.userData.perched = { baseY: p.y, phase: Math.random() * Math.PI * 2 };
      this.scene.add(bird);
      this.perchedBirds.push(bird);
    }
  }

  // 4 birds on the ground at random clearing positions.
  #spawnGrounded() {
    const spots = [
      { x:  5, z:  7 }, { x: -7, z:  3 },
      { x: -3, z: -6 }, { x:  6, z: -4 },
    ];
    for (const s of spots) {
      const bird = this.#cloneBird('ground');
      if (!this.templates.ground.length) bird.scale.setScalar(0.8);
      bird.position.set(s.x, 0.1, s.z);
      bird.rotation.y = Math.random() * Math.PI * 2;
      bird.userData.grounded = {
        baseY: 0.1,
        phase: Math.random() * Math.PI * 2,
        hopTimer: Math.random() * 3,
      };
      this.scene.add(bird);
      this.groundedBirds.push(bird);
    }
  }

  update(delta, elapsed) {
    // Flying — orbit the world center.
    for (const bird of this.flyingBirds) {
      const c = bird.userData.flightCircle;
      c.t += delta * c.speed;
      const x = Math.cos(c.t + c.phase) * c.radius;
      const z = Math.sin(c.t + c.phase) * c.radius;
      bird.position.set(x, c.altitude + Math.sin(elapsed * 1.5 + c.phase) * 0.4, z);
      // Face direction of motion (tangent to circle).
      bird.rotation.y = Math.atan2(
        -Math.sin(c.t + c.phase),
         Math.cos(c.t + c.phase),
      ) + Math.PI / 2;
      this.#flapWings(bird, elapsed, 9);
    }

    // Perched — gentle bob.
    for (const bird of this.perchedBirds) {
      const p = bird.userData.perched;
      bird.position.y = p.baseY + Math.sin(elapsed * 1.5 + p.phase) * 0.025;
      this.#flapWings(bird, elapsed, 1.2, 0.15);
    }

    // Grounded — occasional hop only. No yaw rotation (was causing the
    // flight-pose models to look like they were slowly spinning on the spot).
    for (const bird of this.groundedBirds) {
      const g = bird.userData.grounded;
      g.hopTimer -= delta;
      if (g.hopTimer <= 0) {
        g.hopStart = elapsed;
        g.hopTimer = 3 + Math.random() * 4;
      }
      const t = elapsed - (g.hopStart ?? 0);
      let hop = 0;
      if (t < 0.4) hop = Math.sin(t / 0.4 * Math.PI) * 0.15;
      bird.position.y = g.baseY + hop;
      this.#flapWings(bird, elapsed, 0.8, 0.1);
    }

    // Drive any embedded animation mixers (real GLB).
    for (const mixer of this.modelMixers) mixer.update(delta);
  }

  #flapWings(bird, elapsed, freq = 9, amp = null) {
    const lw = bird.userData.leftWing;
    const rw = bird.userData.rightWing;
    if (!lw || !rw) return; // real model has its own animation
    const a = amp ?? bird.userData.flapAmp ?? 0.7;
    const z = Math.sin(elapsed * freq) * a;
    lw.rotation.z = z;
    rw.rotation.z = -z;
  }
}
