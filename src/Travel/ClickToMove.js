import * as THREE from 'three/webgpu';
import gsap from 'gsap';
import { SECTIONS } from '../Portfolio/WorldMap.js';

export class ClickToMove {
  constructor({ player, playerCamera, controller, navmask, scene, terrain, audio, sections = SECTIONS }) {
    this.player = player;
    this.playerCamera = playerCamera;
    this.controller = controller;
    this.navmask = navmask;
    this.scene = scene;
    this.terrain = terrain;
    this.audio = audio;
    this.sections = sections;
    this.target = null;
    this.path = [];
    this.waypointIndex = 0;
    this.flag = this.#buildFlag();
    this.routeGroup = new THREE.Group();
    this.routeGroup.name = 'click-to-move-route';
    this.scene.add(this.flag);
    this.scene.add(this.routeGroup);
  }

  requestMove(worldX, worldZ) {
    if (!this.navmask.isWalkable(worldX, worldZ)) return false;
    const start = this.player.position;
    const path = this.navmask.findPath(start.x, start.z, worldX, worldZ);
    if (!path || path.length < 2) return false;
    const y = this.terrain?.heightAt?.(worldX, worldZ) ?? 0;
    this.target = { x: worldX, z: worldZ };
    this.path = path;
    this.waypointIndex = 1;
    this.flag.position.set(worldX, y, worldZ);
    this.flag.visible = true;
    this.#drawRoute(path);
    const first = path[1];
    if (first) {
      const angle = Math.atan2(first.x - start.x, first.z - start.z);
      this.playerCamera?.snapTo?.(start, angle);
    }
    gsap.fromTo(this.flag.scale, { x: 0.01, y: 0.01, z: 0.01 }, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.22,
      ease: 'back.out(2)',
    });
    this.audio?.playFlagDrop?.();
    return true;
  }

  update(_deltaTime) {
    if (!this.target) return;
    if (this.controller?.virtualInputCancelledThisFrame || this.controller?.hasManualMovementInput) {
      this.#finish();
      return;
    }
    const pos = this.player.position;
    const waypoint = this.path[this.waypointIndex] ?? this.target;
    const dx = waypoint.x - pos.x;
    const dz = waypoint.z - pos.z;
    const dist = Math.hypot(dx, dz);
    if (dist <= 0.8 && this.waypointIndex < this.path.length - 1) {
      this.waypointIndex += 1;
      return;
    }
    if (dist <= 0.8) {
      this.#finish();
      return;
    }
    const angle = Math.atan2(dx, dz);
    this.controller?.setVirtualInput?.({ forward: 1, strafe: 0, worldAngle: angle });
  }

  #finish() {
    const finalFacing = this.#finalFacing();
    this.target = null;
    this.path = [];
    this.waypointIndex = 0;
    this.controller?.clearVirtualInput?.();
    if (finalFacing !== null) {
      this.player._targetYaw = finalFacing;
      this.player._currentYaw = finalFacing;
      this.player.group.rotation.y = finalFacing;
      this.playerCamera?.snapTo?.(this.player.position, finalFacing);
    }
    this.#clearRoute();
    gsap.to(this.flag.scale, {
      x: 0.01,
      y: 0.01,
      z: 0.01,
      duration: 0.16,
      ease: 'power2.in',
      onComplete: () => {
        this.flag.visible = false;
      },
    });
  }

  #drawRoute(path) {
    this.#clearRoute();
    const points = path.map((p) => new THREE.Vector3(
      p.x,
      (this.terrain?.heightAt?.(p.x, p.z) ?? 0) + 0.045,
      p.z,
    ));
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(points),
      new THREE.LineBasicMaterial({
        color: 0xd4a017,
        transparent: true,
        opacity: 0.9,
        depthWrite: false,
      }),
    );
    line.renderOrder = 8;
    this.routeGroup.add(line);

    const dotGeom = new THREE.RingGeometry(0.12, 0.2, 18);
    const dotMat = new THREE.MeshBasicMaterial({
      color: 0xf4e8d0,
      transparent: true,
      opacity: 0.88,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    for (let i = 1; i < points.length; i++) {
      const dot = new THREE.Mesh(dotGeom, dotMat);
      dot.position.copy(points[i]);
      dot.rotation.x = -Math.PI / 2;
      dot.renderOrder = 9;
      this.routeGroup.add(dot);
    }
    for (const child of this.routeGroup.children) {
      if (child.isMesh) {
        gsap.fromTo(child.scale, { x: 0.2, y: 0.2, z: 0.2 }, {
          x: 1,
          y: 1,
          z: 1,
          duration: 0.22,
          ease: 'power2.out',
        });
      }
    }
  }

  #clearRoute() {
    for (const child of [...this.routeGroup.children]) {
      this.routeGroup.remove(child);
      child.geometry?.dispose?.();
      if (Array.isArray(child.material)) child.material.forEach((m) => m.dispose?.());
      else child.material?.dispose?.();
    }
  }

  #finalFacing() {
    if (!this.target) return null;
    let best = null;
    let bestD = 10;
    for (const section of this.sections) {
      const [sx, , sz] = section.position;
      const d = Math.hypot(this.target.x - sx, this.target.z - sz);
      if (d < bestD) {
        bestD = d;
        best = section;
      }
    }
    if (!best) return null;
    const [sx, , sz] = best.position;
    return Math.atan2(sx - this.player.position.x, sz - this.player.position.z);
  }

  #buildFlag() {
    const group = new THREE.Group();
    group.name = 'click-to-move-flag';
    group.visible = false;
    const pole = new THREE.Mesh(
      new THREE.CylinderGeometry(0.018, 0.024, 0.42, 8),
      new THREE.MeshStandardMaterial({ color: '#5c4a32', roughness: 0.85 }),
    );
    pole.position.y = 0.21;
    const pennant = new THREE.Mesh(
      new THREE.ConeGeometry(0.11, 0.22, 3),
      new THREE.MeshStandardMaterial({ color: '#f4e8d0', roughness: 0.9 }),
    );
    pennant.position.set(0.08, 0.36, 0);
    pennant.rotation.z = -Math.PI / 2;
    pennant.rotation.y = Math.PI / 6;
    group.add(pole, pennant);
    return group;
  }
}
