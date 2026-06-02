import * as THREE from 'three/webgpu';
import { MeshLambertNodeMaterial } from 'three/webgpu';
import {
  Fn, uniform, vec3, positionGeometry, attribute,
  length, smoothstep, max, sin, cos, clamp,
} from 'three/tsl';

/**
 * Runtime flower clumps — the authored flower meshes (flowers/flowersVisual.glb:
 * 8 zone templates, each = petal + gold centre + green stem primitives) instanced
 * as wind-swaying, player-parting clumps. Mirrors the Foliage "soft physics"
 * approach (folio-2025-style): each clump is a `Mesh` over an
 * `InstancedBufferGeometry` (NOT InstancedMesh) so the vertex node rebuilds every
 * instance's world position from per-instance attributes (aCenter / aScale / aYaw)
 * and can then layer wind + the player reaction on top.
 *
 * Flowers are walk-through accents (NO Rapier collider — a flower bed must stay
 * crossable), so "physics" here is shader-side: the upper part of each flower
 * sways in the shared Wind and bends AWAY + presses DOWN as the player's body
 * column passes through, instead of the petals clipping through the avatar. The
 * bend is height-weighted (quadratic in local Y) so the base stays planted and
 * the flower nods from the ground like a real stem.
 *
 * Flat per-primitive albedo (the GLB baseColorFactors — petal/centre/stem) is lit
 * by MeshLambertNodeMaterial (scene sun/ambient/hemi + fog) so flowers darken at
 * night through the same rig as everything else, and they cast + receive shadows.
 */

// Whole-flower wind sway (m) at the tip, height-weighted toward the top.
const WIND_SWAY = 0.12;

// Player "soft physics" — the player is a vertical body column (feet→head); a
// flower within REACT_RADIUS of that column bends away from it and presses down.
const BODY_BELOW = 0.3;     // column bottom below the feet anchor (m)
const BODY_ABOVE = 1.9;     // column top above the feet anchor (head, m)
const REACT_RADIUS = 0.85;  // flowers within this of the body column react (m)
const REACT_INNER = 0.1;    // full strength once this close (m)
const PART_STRENGTH = 0.55; // how far the top bends away from the body (m)
const PART_DOWN = 0.22;     // press the parted flower down (m)
const FLUTTER_FREQ = 7.0;   // shimmer speed of a disturbed flower
const FLUTTER_AMP = 0.05;   // shimmer amplitude (m)

export class Flowers {
  /**
   * @param {THREE.Scene} scene
   * @param {import('./Wind.js').Wind} wind
   * @param {Array<{key:string, clumpHeight:number,
   *   primitives:Array<{geometry:THREE.BufferGeometry, color:THREE.Color}>,
   *   placements:Array<{x:number,y:number,z:number,yaw:number,scale:number}>}>} groups
   */
  constructor(scene, wind, groups = []) {
    this.scene = scene;
    this.wind = wind;
    this.meshes = [];

    // Player world position (incl. Y) for the part reaction; parked far below so
    // nothing bends until the first real App.tick update.
    this.uPlayerPos = uniform(vec3(0, -9999, 0));

    for (const group of groups) this.#buildGroup(group);
  }

  // ── World-position vertex node (per primitive — clumpHeight differs) ─────────
  // Rebuilds each instance's vertex in world space from aCenter/aScale/aYaw (the
  // mesh sits at the origin with identity transform, like Grass/Foliage), then
  // layers a height-weighted wind sway + the player part/flutter.
  #positionNode(clumpHeight) {
    const rotY = (p, a) => {
      const c = cos(a); const s = sin(a);
      return vec3(p.x.mul(c).add(p.z.mul(s)), p.y, p.z.mul(c).sub(p.x.mul(s)));
    };
    return Fn(() => {
      const local = positionGeometry;
      const center = attribute('aCenter');   // instance world base position
      const scl = attribute('aScale');       // instance uniform scale
      const yaw = attribute('aYaw');          // instance Y rotation

      // Height weight: 0 at the base → 1 at the top, quadratic so the very base
      // stays rooted and the flower nods from the ground.
      const bend = clamp(local.y.div(clumpHeight), 0, 1).toVar();
      bend.assign(bend.mul(bend));

      let p = local.mul(scl);
      p = rotY(p, yaw);
      const world = center.add(p).toVar();

      // Wind sway — height-weighted so flowers nod from a planted base.
      const sway = this.wind.offsetNode(center.xz).mul(WIND_SWAY).mul(bend);
      world.x.addAssign(sway.x);
      world.z.addAssign(sway.y);

      // Player: bend the upper flower away from the nearest point on the body
      // column + press it down + flutter, so walking through parts the petals.
      const feet = this.uPlayerPos;
      const colY = clamp(world.y, feet.y.sub(BODY_BELOW), feet.y.add(BODY_ABOVE));
      const closest = vec3(feet.x, colY, feet.z);
      const delta = world.sub(closest).toVar();
      const dist = length(delta).toVar();
      const env = smoothstep(REACT_RADIUS, REACT_INNER, dist).mul(bend).toVar();
      const dir = delta.div(max(dist, 0.001));
      const phase = world.x.add(world.z).mul(2.3);
      const flutter = sin(this.wind.nodes.time.mul(FLUTTER_FREQ).add(phase)).mul(FLUTTER_AMP).mul(env);
      world.x.addAssign(dir.x.mul(env.mul(PART_STRENGTH)).add(flutter));
      world.z.addAssign(dir.z.mul(env.mul(PART_STRENGTH)).add(flutter.mul(0.6)));
      world.y.subAssign(env.mul(PART_DOWN));

      return world;
    })();
  }

  // ── One template = its placements × its primitives (petal/centre/stem) ──────
  #buildGroup(group) {
    const placements = group.placements ?? [];
    if (!placements.length || !group.primitives?.length) return;

    const n = placements.length;
    const center = new Float32Array(n * 3);
    const scale = new Float32Array(n);
    const yawArr = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const pl = placements[i];
      center[i * 3] = pl.x;
      center[i * 3 + 1] = pl.y;
      center[i * 3 + 2] = pl.z;
      scale[i] = pl.scale || 1;
      yawArr[i] = pl.yaw || 0;
    }
    // Shared across this template's primitives so they stay glued together.
    const aCenter = new THREE.InstancedBufferAttribute(center, 3);
    const aScale = new THREE.InstancedBufferAttribute(scale, 1);
    const aYaw = new THREE.InstancedBufferAttribute(yawArr, 1);

    const positionNode = this.#positionNode(group.clumpHeight || 1);

    group.primitives.forEach((prim, pi) => {
      const base = prim.geometry;
      const geom = new THREE.InstancedBufferGeometry();
      geom.index = base.index;
      geom.attributes.position = base.attributes.position;
      if (base.attributes.normal) geom.attributes.normal = base.attributes.normal;
      geom.instanceCount = n;
      geom.setAttribute('aCenter', aCenter);
      geom.setAttribute('aScale', aScale);
      geom.setAttribute('aYaw', aYaw);
      // Huge bounding sphere — instances are placed in the vertex node, so the
      // base geometry's bounds don't describe the real extent (skip culling).
      geom.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e6);

      const mat = new MeshLambertNodeMaterial({ side: THREE.DoubleSide });
      mat.color = prim.color.clone();      // flat petal/centre/stem albedo
      mat.positionNode = positionNode;     // shared wind + player bend

      const mesh = new THREE.Mesh(geom, mat);
      mesh.name = `flowers:${group.key}:${pi}`;
      mesh.frustumCulled = false;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      this.scene.add(mesh);
      this.meshes.push({ mesh, geom, mat });
    });
  }

  // ── Public API (mirrors Foliage / Grass so App.tick wiring matches) ─────────

  /** Player world position for the part/flutter interaction (App passes it each frame). */
  setPlayerPos(pos) {
    if (!pos) return;
    this.uPlayerPos.value.set(pos.x, pos.y, pos.z);
  }

  dispose() {
    for (const m of this.meshes) {
      this.scene.remove(m.mesh);
      m.geom?.dispose();
      m.mat?.dispose();
    }
    this.meshes = [];
  }
}
