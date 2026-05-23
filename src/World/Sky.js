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
  uniform vec3 uHorizon;
  uniform vec3 uGround;
  uniform vec3 uSunDir;
  uniform vec3 uSunColor;

  void main() {
    float h = vWorldDir.y;
    vec3 color;
    if (h > 0.0) {
      // VERY sharp transition. Our third-person camera pitches ~20° down so
      // top-of-screen is only ~2° above horizon (h ≈ 0.04). Anything softer
      // than this and the sky reads as solid orange.
      color = mix(uHorizon, uTop, smoothstep(0.005, 0.05, h));
    } else {
      color = mix(uHorizon, uGround, smoothstep(0.0, -0.25, h));
    }

    // Sun glow halo around the sun direction
    float sunDot = max(dot(vWorldDir, normalize(uSunDir)), 0.0);
    float halo = pow(sunDot, 16.0) * 0.55 + pow(sunDot, 256.0) * 1.4;
    color += uSunColor * halo;

    gl_FragColor = vec4(color, 1.0);
  }
`;

/**
 * Sunset sky: large inverted sphere with a top→horizon→ground gradient and
 * a sun halo computed from the directional light's position.
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
        uHorizon: { value: new THREE.Color(DUSK.skyHorizon) },
        uGround: { value: new THREE.Color(DUSK.skyGround) },
        uSunDir: { value: new THREE.Vector3(0.6, 0.45, 0.5).normalize() },
        uSunColor: { value: new THREE.Color(DUSK.sunColor) },
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

  /** Lock the sun halo to wherever the directional light is in world space. */
  setSunDirection(worldPos) {
    this.material.uniforms.uSunDir.value.copy(worldPos).normalize();
  }
}
