import * as THREE from 'three';
import { DUSK } from './Palette.js';

const vert = /* glsl */ `
  varying vec3 vWorldDir;
  void main() {
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vWorldDir = normalize(wp.xyz - cameraPosition);
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const frag = /* glsl */ `
  varying vec3 vWorldDir;
  uniform vec3 uTop;
  uniform vec3 uMid;
  uniform vec3 uHorizon;
  uniform vec3 uGround;

  void main() {
    float h = vWorldDir.y;
    vec3 color;
    if (h > 0.0) {
      // Three-stop gradient: horizon → mid → top. The horizon band is still
      // sharp (the third-person camera pitches ~20° down and only sees a
      // sliver of sky) but uMid lets day-mode read as blue once you look
      // up, and lets night-mode have a deep mid-purple between horizon and
      // a near-black zenith.
      vec3 lower = mix(uHorizon, uMid, smoothstep(0.005, 0.08, h));
      color = mix(lower, uTop, smoothstep(0.1, 0.5, h));
    } else {
      color = mix(uHorizon, uGround, smoothstep(0.0, -0.25, h));
    }

    gl_FragColor = vec4(color, 1.0);
  }
`;

/**
 * Sunset sky: large inverted sphere with a top→horizon→ground gradient.
 * The visible sun disc + halo live in Sun.js — this shader only paints the
 * gradient bands.
 */
export class Sky {
  constructor(scene) {
    // Radius MUST be less than the camera's far plane (300) — otherwise the
    // whole sphere is clipped and the sky renders as black.
    const geom = new THREE.SphereGeometry(250, 32, 16);

    this.material = new THREE.ShaderMaterial({
      vertexShader: vert,
      fragmentShader: frag,
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {
        uTop: { value: new THREE.Color(DUSK.skyTop) },
        // uMid sits between horizon and zenith — TimeOfDay overrides this on
        // construction; the DUSK fallback keeps the old single-mix behaviour
        // if Sky is ever used standalone (interpolation collapses to the
        // original two-stop look when uMid ≈ uTop).
        uMid: { value: new THREE.Color(DUSK.skyTop) },
        uHorizon: { value: new THREE.Color(DUSK.skyHorizon) },
        uGround: { value: new THREE.Color(DUSK.skyGround) },
      },
    });

    this.mesh = new THREE.Mesh(geom, this.material);
    this.mesh.renderOrder = -1;
    scene.add(this.mesh);
  }

  /** Keep the sky centered on the camera so the player can never "reach" the edge. */
  update(cameraPosition) {
    this.mesh.position.copy(cameraPosition);
  }
}
