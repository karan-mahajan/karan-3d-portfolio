import * as THREE from 'three';

/**
 * Footstep dust puffs on land — small THREE.Points pool, ring-buffer writes,
 * vertex-shader alpha fade. Mirrors the Water splash system but spawned by
 * the App tick on player footsteps and tinted to the terrain band at the
 * player's feet (grass green inland, sand tan near the shore).
 *
 * Step cadence here is independent of AudioManager's, but uses the same
 * walk/run intervals so visual puffs land in sync with footstep sounds.
 *
 * Disabled over water (Water owns its own splash system) and when the
 * player is airborne — only contact-with-ground spawns a puff.
 */

const DUST_MAX = 90;
const SPAWN_INTERVAL_WALK = 0.42;
const SPAWN_INTERVAL_RUN  = 0.28;
const PER_BURST_WALK = 2;
const PER_BURST_RUN  = 3;
const LIFE = 0.55;
const GRAVITY = -3.2;

// Sand band — players past r ≈ 38 are on the beach; lerp tints in this ring
// so dust gradually shifts from grass to sand instead of popping.
const SAND_INNER = 38;
const SAND_OUTER = 45;

const GRASS_TINT = new THREE.Color('#9e8a4a'); // dry-grass / dust
const SAND_TINT  = new THREE.Color('#d9c184'); // light sand

export class Dust {
  /**
   * @param {THREE.Scene} scene
   * @param {import('../World/Terrain.js').Terrain} terrain
   * @param {import('../Effects/Water.js').Water|null} [water]  Used to skip
   *   spawning when the player is over open water (Water owns its splashes).
   */
  constructor(scene, terrain, water = null) {
    this.scene = scene;
    this.terrain = terrain;
    this.water = water;
    this._spawnTimer = 0;
    this.#buildSystem();
  }

  setWater(water) { this.water = water; }

  #buildSystem() {
    const positions = new Float32Array(DUST_MAX * 3);
    const ages = new Float32Array(DUST_MAX);
    const lifes = new Float32Array(DUST_MAX);
    const tints = new Float32Array(DUST_MAX * 3);
    for (let i = 0; i < DUST_MAX; i++) {
      ages[i] = LIFE + 1; // dead
      lifes[i] = LIFE;
    }
    this._state = {
      positions, ages, lifes, tints,
      velocities: new Float32Array(DUST_MAX * 3),
      cursor: 0,
    };

    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('aAge', new THREE.BufferAttribute(ages, 1));
    geom.setAttribute('aLife', new THREE.BufferAttribute(lifes, 1));
    geom.setAttribute('aTint', new THREE.BufferAttribute(tints, 3));
    geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

    const mat = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      // Normal blending — dust should darken/dirty the scene, not glow like
      // the water splashes do under additive blending.
      blending: THREE.NormalBlending,
      uniforms: { uPxScale: { value: 70 } },
      vertexShader: /* glsl */ `
        attribute float aAge;
        attribute float aLife;
        attribute vec3 aTint;
        uniform float uPxScale;
        varying float vAlpha;
        varying vec3 vTint;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mv;
          float t = clamp(aAge / aLife, 0.0, 1.0);
          // Quick fade-in then long fade-out — gives a "puff that settles" feel.
          float fadeIn = smoothstep(0.0, 0.12, t);
          float fadeOut = pow(1.0 - t, 1.6);
          vAlpha = (aAge >= aLife) ? 0.0 : fadeIn * fadeOut;
          // Grow slightly as the puff ages (dust disperses).
          float grow = mix(1.0, 1.7, t);
          gl_PointSize = uPxScale * grow / max(0.5, -mv.z);
          vTint = aTint;
        }
      `,
      fragmentShader: /* glsl */ `
        varying float vAlpha;
        varying vec3 vTint;
        void main() {
          vec2 c = gl_PointCoord - vec2(0.5);
          float d = length(c);
          if (d > 0.5) discard;
          float soft = smoothstep(0.5, 0.05, d);
          gl_FragColor = vec4(vTint, soft * vAlpha * 0.55);
        }
      `,
    });

    this._points = new THREE.Points(geom, mat);
    this._points.frustumCulled = false;
    this._points.name = 'footstep-dust';
    this._points.renderOrder = 5;
    this.scene.add(this._points);
  }

  /**
   * Pick the dust tint for the player's current footing — grass inland,
   * sand on the shore band, lerped in between so it doesn't pop.
   */
  #tintAt(x, z, out) {
    const r = Math.hypot(x, z);
    const t = THREE.MathUtils.clamp((r - SAND_INNER) / (SAND_OUTER - SAND_INNER), 0, 1);
    out.copy(GRASS_TINT).lerp(SAND_TINT, t);
    return out;
  }

  #spawnBurst(playerPos, count) {
    const s = this._state;
    const tint = this.#tintAt(playerPos.x, playerPos.z, _tmpColor);
    const groundY = this.terrain ? this.terrain.heightAt(playerPos.x, playerPos.z) : 0;
    for (let i = 0; i < count; i++) {
      const idx = s.cursor;
      s.cursor = (s.cursor + 1) % DUST_MAX;
      // Tight scatter around the feet — dust is a small ground-hugging effect.
      s.positions[idx * 3 + 0] = playerPos.x + (Math.random() - 0.5) * 0.35;
      s.positions[idx * 3 + 1] = groundY + 0.03;
      s.positions[idx * 3 + 2] = playerPos.z + (Math.random() - 0.5) * 0.35;
      const angle = Math.random() * Math.PI * 2;
      const horiz = 0.25 + Math.random() * 0.7;
      s.velocities[idx * 3 + 0] = Math.cos(angle) * horiz;
      s.velocities[idx * 3 + 1] = 0.35 + Math.random() * 0.55; // gentle rise
      s.velocities[idx * 3 + 2] = Math.sin(angle) * horiz;
      s.tints[idx * 3 + 0] = tint.r;
      s.tints[idx * 3 + 1] = tint.g;
      s.tints[idx * 3 + 2] = tint.b;
      s.ages[idx] = 0;
    }
    const g = this._points.geometry;
    g.attributes.position.needsUpdate = true;
    g.attributes.aAge.needsUpdate = true;
    g.attributes.aTint.needsUpdate = true;
  }

  /**
   * @param {number} delta seconds since last frame
   * @param {THREE.Vector3} playerPos
   * @param {{moving:boolean, speed:number}|null} sample
   * @param {boolean} grounded
   */
  update(delta, playerPos, sample, grounded) {
    // Skip while the player is over water — splash system handles that.
    const overWater = this.water ? this.water.playerOverWater(playerPos.x, playerPos.z) : false;
    if (sample && sample.moving && grounded && !overWater) {
      const running = (sample.speed ?? 0) > 5;
      const interval = running ? SPAWN_INTERVAL_RUN : SPAWN_INTERVAL_WALK;
      this._spawnTimer += delta;
      if (this._spawnTimer >= interval) {
        this._spawnTimer -= interval;
        this.#spawnBurst(playerPos, running ? PER_BURST_RUN : PER_BURST_WALK);
      }
    } else {
      this._spawnTimer = 0;
    }
    this.#advance(delta);
  }

  #advance(delta) {
    const s = this._state;
    let anyAlive = false;
    const dragHor = Math.exp(-3.0 * delta);
    const dragVer = Math.exp(-2.5 * delta);
    for (let i = 0; i < DUST_MAX; i++) {
      if (s.ages[i] >= s.lifes[i]) continue;
      anyAlive = true;
      s.ages[i] += delta;
      s.velocities[i * 3 + 1] += GRAVITY * delta;
      s.velocities[i * 3 + 0] *= dragHor;
      s.velocities[i * 3 + 1] *= dragVer;
      s.velocities[i * 3 + 2] *= dragHor;
      s.positions[i * 3 + 0] += s.velocities[i * 3 + 0] * delta;
      s.positions[i * 3 + 1] += s.velocities[i * 3 + 1] * delta;
      s.positions[i * 3 + 2] += s.velocities[i * 3 + 2] * delta;
    }
    if (anyAlive) {
      const g = this._points.geometry;
      g.attributes.position.needsUpdate = true;
      g.attributes.aAge.needsUpdate = true;
    }
  }
}

const _tmpColor = new THREE.Color();
