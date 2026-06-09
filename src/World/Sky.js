import * as THREE from 'three/webgpu';
import { MeshBasicNodeMaterial } from 'three/webgpu';
import { Fn, positionWorld, cameraPosition, uniform, mix, smoothstep, normalize, vec4 } from 'three/tsl';
import { DUSK } from './Palette.js';

/**
 * The sky's vertical gradient as a reusable TSL node, given the four band
 * uniforms and a view-direction elevation `h` (dir.y, -1..1). Exported so the
 * scene fog ([FogState.js]) fades distant geometry into the EXACT same gradient
 * band behind it — not a single flat horizon colour — keeping the dissolve
 * seamless. Single source of truth: both the sky dome and the fog call this, so
 * they can never drift apart.
 * @param {{uTop,uMid,uHorizon,uGround}} u live colour-uniform nodes
 * @param {*} h elevation node (view dir .y)
 */
export function skyGradientColor(u, h) {
  // Above horizon: horizon → mid → top three-stop gradient.
  const lower = mix(u.uHorizon, u.uMid, smoothstep(0.005, 0.08, h));
  const above = mix(lower, u.uTop, smoothstep(0.1, 0.5, h));
  // Below horizon: horizon → ground.
  const below = mix(u.uHorizon, u.uGround, smoothstep(0.0, -0.25, h));
  return h.greaterThan(0.0).select(above, below);
}

/**
 * Sunset sky: large inverted sphere with a top→mid→horizon→ground gradient.
 * The visible sun disc + halo live in Sun.js — this material only paints the
 * gradient bands.
 *
 * B0: ported from the GLSL ShaderMaterial to a TSL MeshBasicNodeMaterial so it
 * renders on WebGPU. The four gradient stops are exposed as TSL `uniform` nodes
 * whose `.value` is a live THREE.Color; TimeOfDay mutates those colours in place
 * (`.set()` / gsap tweens on `.r/.g/.b`) exactly as it did with the old GLSL
 * uniforms — re-exposed via `this.material.uniforms.{uTop,uMid,uHorizon,uGround}`
 * so no TimeOfDay change is needed.
 */
export class Sky {
  constructor(scene) {
    // Radius MUST be less than the camera's far plane (300) — otherwise the
    // whole sphere is clipped and the sky renders as black.
    const geom = new THREE.SphereGeometry(250, 32, 16);

    const uTop = uniform(new THREE.Color(DUSK.skyTop));
    // uMid sits between horizon and zenith; TimeOfDay overrides it on
    // construction. The DUSK fallback collapses to the old two-stop look.
    const uMid = uniform(new THREE.Color(DUSK.skyTop));
    const uHorizon = uniform(new THREE.Color(DUSK.skyHorizon));
    const uGround = uniform(new THREE.Color(DUSK.skyGround));

    const colorNode = Fn(() => {
      // View direction from the camera to this fragment's world position.
      const dir = normalize(positionWorld.sub(cameraPosition));
      const color = skyGradientColor({ uTop, uMid, uHorizon, uGround }, dir.y);
      return vec4(color, 1.0);
    })();

    this.material = new MeshBasicNodeMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      fog: false,
    });
    this.material.colorNode = colorNode;
    // Re-expose the live Color uniforms under the legacy `.uniforms` shape so
    // TimeOfDay can keep mutating `.value` in place.
    this.material.uniforms = {
      uTop: uTop,
      uMid: uMid,
      uHorizon: uHorizon,
      uGround: uGround,
    };

    this.mesh = new THREE.Mesh(geom, this.material);
    this.mesh.renderOrder = -1;
    scene.add(this.mesh);
  }

  /** Keep the sky centered on the camera so the player can never "reach" the edge. */
  update(cameraPosition) {
    this.mesh.position.copy(cameraPosition);
  }
}
