import * as THREE from 'three';

/**
 * Drifting emissive points. Each firefly has its own seed and orbits a base
 * position with random sinusoidal motion. The fragment shader paints a soft
 * round disc with a warm-amber tint; the bloom pass adds the glow halo.
 */

// 144 — dialed down 20% from the earlier 180 bump. User felt the swarm
// was too dense at night; still ~20% above the original 120 so there's
// some extra breadcrumb effect between street lamps.
const COUNT = 144;
const SPREAD = 60;          // half-extent of the firefly spawn box
const HEIGHT_BAND = [0.6, 3.0];

const vert = /* glsl */ `
  uniform float uTime;
  attribute vec3 aSeed;     // x: phase, y: speed, z: amplitude
  attribute vec3 aBase;
  varying float vAlpha;

  void main() {
    float phase = aSeed.x;
    float speed = aSeed.y;
    float amp   = aSeed.z;

    // Each firefly bobs in its own little orbit so the swarm feels alive.
    vec3 pos = aBase;
    pos.x += sin(uTime * speed + phase) * amp;
    pos.y += sin(uTime * speed * 1.3 + phase * 2.0) * amp * 0.4;
    pos.z += cos(uTime * speed * 0.9 + phase * 1.5) * amp;

    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * mv;

    // Size shrinks with distance — perspective scaled point size.
    gl_PointSize = 18.0 * (1.0 / max(0.1, -mv.z * 0.05));

    // Twinkle: fade in/out at slightly different rates per firefly.
    vAlpha = 0.55 + 0.45 * sin(uTime * 2.0 + phase * 4.0);
  }
`;

const frag = /* glsl */ `
  uniform float uIntensity;
  varying float vAlpha;

  void main() {
    // Distance from the center of the point sprite.
    vec2 c = gl_PointCoord - vec2(0.5);
    float d = length(c);
    if (d > 0.5) discard;

    // Soft core → bright center, transparent edge.
    float core = smoothstep(0.5, 0.0, d);
    vec3 color = mix(vec3(1.0, 0.65, 0.25), vec3(1.0, 0.92, 0.62), core);
    // uIntensity scales the brightness (driven by day/night cycle).
    gl_FragColor = vec4(color * uIntensity, core * vAlpha * clamp(uIntensity, 0.0, 1.5));
  }
`;

export class Fireflies {
  constructor(scene) {
    this.scene = scene;
    this.geometry = new THREE.BufferGeometry();

    const positions = new Float32Array(COUNT * 3);
    const seeds = new Float32Array(COUNT * 3);
    const bases = new Float32Array(COUNT * 3);

    for (let i = 0; i < COUNT; i++) {
      const x = (Math.random() - 0.5) * SPREAD;
      const y = HEIGHT_BAND[0] + Math.random() * (HEIGHT_BAND[1] - HEIGHT_BAND[0]);
      const z = (Math.random() - 0.5) * SPREAD;
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
      bases[i * 3] = x;
      bases[i * 3 + 1] = y;
      bases[i * 3 + 2] = z;
      seeds[i * 3] = Math.random() * Math.PI * 2;
      seeds[i * 3 + 1] = 0.4 + Math.random() * 0.8;
      seeds[i * 3 + 2] = 0.3 + Math.random() * 0.8;
    }

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('aBase', new THREE.BufferAttribute(bases, 3));
    this.geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 3));

    this.material = new THREE.ShaderMaterial({
      vertexShader: vert,
      fragmentShader: frag,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      uniforms: {
        uTime: { value: 0 },
        // 1.0 = day baseline. TimeOfDay lerps this up at night so the swarm
        // reads as more prominent against the dark sky.
        uIntensity: { value: 1.0 },
      },
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.name = 'fireflies';
    this.points.frustumCulled = false;
    scene.add(this.points);
  }

  update(elapsed) {
    this.material.uniforms.uTime.value = elapsed;
    // Skip the entire draw (vertex + fragment shader) when fully faded —
    // day mode sets uIntensity to 0 so 144 point-sprite invocations per
    // frame are saved. Matches the same pattern stars + moon use.
    this.points.visible = this.material.uniforms.uIntensity.value > 0.001;
  }
}
