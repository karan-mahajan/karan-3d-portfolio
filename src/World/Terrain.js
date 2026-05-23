import * as THREE from 'three';

/**
 * Large walkable ground plane. Grass-green base color so even where tiles
 * don't cover, the world reads as a meadow not a desert. GroundTiles places
 * real Kenney grass models on top.
 */
export class Terrain {
  constructor(scene, { size = 200, segments = 96 } = {}) {
    this.size = size;

    const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
    geometry.rotateX(-Math.PI / 2);
    this.#displaceVertices(geometry);
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: '#4a7c2e',
      roughness: 0.95,
      metalness: 0,
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.receiveShadow = true;
    this.mesh.name = 'terrain';
    scene.add(this.mesh);
  }

  #displaceVertices(geometry) {
    const pos = geometry.attributes.position;
    const center = new THREE.Vector2(0, 0);
    const tmp = new THREE.Vector2();
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      tmp.set(x, z);
      const distance = tmp.distanceTo(center);

      const wave =
        Math.sin(x * 0.08) * 0.25 +
        Math.cos(z * 0.07) * 0.22 +
        Math.sin((x + z) * 0.05) * 0.18;
      const flatten = THREE.MathUtils.smoothstep(distance, 8, 22);
      pos.setY(i, wave * flatten);
    }
    pos.needsUpdate = true;
  }

  heightAt(x, z) {
    const distance = Math.hypot(x, z);
    const wave =
      Math.sin(x * 0.08) * 0.25 +
      Math.cos(z * 0.07) * 0.22 +
      Math.sin((x + z) * 0.05) * 0.18;
    const flatten = THREE.MathUtils.smoothstep(distance, 8, 22);
    return wave * flatten;
  }
}
