import gsap from "gsap";
import * as THREE from "three";

/**
 * Day / night cycle driver. Owns:
 *   - day + night palettes (colors, intensities, sun position, etc.)
 *   - the night-only visuals: starfield, moon disc + halo
 *   - the character-following lights: a soft fill (always on) and a magical
 *     overhead spotlight that turns on at night
 *   - lanterns next to each sign / billboard so text stays readable at night
 *
 * Every value that differs between modes is lerped via GSAP over `duration`
 * seconds — colors via Color.r/g/b, positions via Vector3.x/y/z, scalars
 * directly. The current mode auto-detects from the user's local clock; the
 * toggle button (wired in App.js) flips between modes.
 */

const TRANSITION_SECONDS = 2.0;
const STAR_COUNT = 280;
const STAR_DOME_RADIUS = 230;

export const DAY_PALETTE = Object.freeze({
  sunColor: "#ffeedd",
  sunIntensity: 1.3,
  // Position chosen so the visible Sun.js disc falls inside the default
  // third-person camera frame (player at spawn, camera at -Z facing +Z,
  // FOV 45° vertical / ~67° horizontal). Direction (15, 9, 35) gives:
  //   horizontal ≈ 23° right of camera (within ±33° half-FOV)
  //   elevation  ≈ 13° above horizon  (within +15° upper-frame edge)
  // Shadow direction is fine at this elevation; cast length is moderate.
  sunOffset: new THREE.Vector3(15, 9, 35),
  rimColor: "#ff8855",
  rimIntensity: 0.35,
  ambientColor: "#ccbbaa",
  ambientIntensity: 0.5,
  hemiSky: "#88bbee",
  hemiGround: "#886644",
  hemiIntensity: 0.35,
  skyTop: "#4488cc",
  skyMid: "#88bbee",
  // Horizon === fog colour so the ocean fades seamlessly into the sky band
  // — no visible ring where the water plane ends. Tuned cool-steel-blue to
  // bridge the deep-ocean tint (#1a4a6a) into the upper sky.
  skyHorizon: "#88aabb",
  skyGround: "#4a3528",
  fogColor: "#88aabb",
  // Pulled tighter than the old 65→165 so the ocean plane (extending 150 m
  // from the island centre) fully dissolves into fog before its edge.
  fogNear: 50,
  fogFar: 130,
  grassColor: "#5aa033",
  grassShadowStrength: 0.75,
  fireflyIntensity: 0.55,
  starsOpacity: 0,
  moonOpacity: 0,
  // Subtle 0.6 fill from above in day mode so the character's face has a
  // neutral top-light counter to the warm sun — keeps the skin from
  // reading yellow. Night cranks it up to 9 for an obvious stage-light
  // pool on the ground around the character. The numbers look high
  // because three.js's physical lighting model + linear decay over 10u
  // dilutes the light a lot — spec's "2" wasn't visible.
  spotlightIntensity: 0.6,
  fillColor: "#ffffff",
  // Day face fill — counters the warm directional sun on the face so
  // the skin doesn't read yellow. 1.5 was OK but with the camera-side
  // anchored fill now actually pointing at the face, 1.8 is what reads
  // best across both modes.
  fillIntensity: 1.8,
  sunMeshOpacity: 1,
  billboardEmissiveBoost: 1.0,
  lanternIntensity: 0,
  // Physical lamp lights — subtle in daylight (just a hint of warmth)
  // and a glowing bulb that the bloom pass picks up.
  lampIntensity: 0.3,
  lampBulbBrightness: 0.6,
  // Warm daylight tint on the water — sky-fresh reads as a brighter blue
  // because the Water2 shader multiplies the reflected colour by this tint.
  waterColor: "#4a90c4",
});

export const NIGHT_PALETTE = Object.freeze({
  sunColor: "#6688bb",
  sunIntensity: 0.3,
  sunOffset: new THREE.Vector3(-30, 25, -20),
  rimColor: "#3a4d80",
  rimIntensity: 0.0,
  ambientColor: "#0a1525",
  ambientIntensity: 0.18,
  hemiSky: "#112244",
  hemiGround: "#0a0a15",
  hemiIntensity: 0.12,
  // Lifted from near-black so the night sky still reads as a sky band
  // rather than the void around the canvas. Bands kept in deep blue family
  // so stars + moon still stand out brightly against them. Horizon === fog
  // so the night ocean dissolves into the sky band at the horizon ring.
  skyTop: "#0c1228",
  skyMid: "#15203f",
  skyHorizon: "#0a1520",
  skyGround: "#0a0a18",
  fogColor: "#0a1520",
  fogNear: 30,
  fogFar: 95,
  grassColor: "#1f3a2a",
  grassShadowStrength: 0.25,
  fireflyIntensity: 1.6,
  starsOpacity: 1,
  moonOpacity: 1,
  spotlightIntensity: 9.0,
  // Cool-neutral fill that DOMINATES the near-black night ambient so
  // the character's face stays clearly readable. 0.45 was an anaemic
  // top-up; 2.5 with decay=1.4 over the 1.5u face distance gives ≈ 1.5
  // effective intensity at the face — enough to actually see skin
  // detail against the dark world.
  fillColor: "#ccd6ec",
  fillIntensity: 2.5,
  sunMeshOpacity: 0,
  billboardEmissiveBoost: 2.2,
  lanternIntensity: 0.55,
  // Night lamps are the primary light source for sign text.
  lampIntensity: 1.2,
  lampBulbBrightness: 1.8,
  // Cooler, deeper night water — moon + lanterns + stars reflect against
  // a darker blue-grey base so the night scene reads as cold water.
  waterColor: "#2a4a64",
});

/**
 * Returns 'day' between 6:00 and 18:59, 'night' otherwise.
 */
export function detectAutoMode() {
  const hour = new Date().getHours();
  return hour >= 21 || hour < 6 ? "night" : "day";
}

export class TimeOfDay {
  /**
   * @param {object} opts
   * @param {THREE.Scene} opts.scene
   * @param {THREE.Fog}   opts.fog
   * @param {THREE.DirectionalLight} opts.sun
   * @param {THREE.DirectionalLight} opts.rim
   * @param {THREE.AmbientLight}     opts.ambient
   * @param {THREE.HemisphereLight}  opts.hemi
   * @param {import('./Sky.js').Sky} opts.sky
   * @param {import('./Sun.js').Sun} opts.sunMesh
   * @param {import('./Grass.js').Grass} opts.grass
   * @param {import('../Effects/Fireflies.js').Fireflies} opts.fireflies
   * @param {import('../Portfolio/Billboards.js').Billboards} opts.billboards
   * @param {import('../Portfolio/Signs.js').Signs}           opts.signs
   * @param {THREE.Object3D} opts.playerGroup - the visual player root (rotates with character)
   */
  constructor({
    scene,
    fog,
    sun,
    rim,
    ambient,
    hemi,
    sky,
    sunMesh,
    grass,
    fireflies,
    water = null,
    billboards = null,
    signs = null,
    playerGroup,
  }) {
    this.scene = scene;
    this.fog = fog;
    this.sun = sun;
    this.rim = rim;
    this.ambient = ambient;
    this.hemi = hemi;
    this.sky = sky;
    this.sunMesh = sunMesh;
    this.grass = grass;
    this.fireflies = fireflies;
    this.water = water;
    this.billboards = billboards;
    this.signs = signs;
    this.playerGroup = playerGroup;

    this.mode = detectAutoMode();

    this.#buildCharacterLights();
    this.#buildStars();
    this.#buildMoon();
    // Sign lanterns are wired lazily — if Signs / Billboards aren't ready
    // yet (they load async), call attachLanterns() once they exist.
    if (signs || billboards) this.attachLanterns();

    // Apply the initial mode instantly so the world is rendered correctly
    // on the very first frame.
    this.#applyInstant(this.mode);
  }

  // ── Public API ────────────────────────────────────────────────────────────
  setMode(mode, duration = TRANSITION_SECONDS) {
    if (mode !== "day" && mode !== "night") return;
    if (mode === this.mode) return;
    this.mode = mode;
    this.dispatchEvent?.("change", mode);
    this.#transition(mode, duration);
  }

  toggle(duration = TRANSITION_SECONDS) {
    this.setMode(this.mode === "day" ? "night" : "day", duration);
  }

  /** Hard-reset every uniform / light / lantern to match the current mode.
   *  Called by App.js after async loads (Signs / Billboards) so freshly
   *  created scene objects pick up the correct intensities without a
   *  visible transition. */
  reapply() {
    this.#applyInstant(this.mode);
  }

  /** No-op kept for backwards compatibility with App.js. Static Lamps
   *  (see Lamps.js) cover the role the old per-sign lanterns used to —
   *  one PointLight per spot, intensity driven by the day/night mode. */
  attachLanterns() {
    this.lanterns = [];
    this._lanternsAttached = true;
  }

  /**
   * Update per-frame state — spotlight + fill light tracking the player,
   * stars + moon following the camera.
   */
  tick(playerPos, camera, elapsed) {
    if (this.fillLight && playerGroupExists(this.playerGroup) && camera) {
      // Position the fill BETWEEN the camera and the player so it always
      // lights whichever side of the character the camera is seeing.
      // Anchoring to the player's own facing direction was wrong: the
      // Avaturn model's face is on the side opposite to the player's
      // "forward" yaw, so the previous offset put the fill behind the
      // head and the face read as completely dark at night.
      const cx = camera.position.x - playerPos.x;
      const cz = camera.position.z - playerPos.z;
      const cl = Math.max(0.001, Math.hypot(cx, cz));
      this.fillLight.position.set(
        playerPos.x + (cx / cl) * 1.5,
        playerPos.y + 1.7,
        playerPos.z + (cz / cl) * 1.5,
      );
    }
    if (this.spotLight && playerGroupExists(this.playerGroup)) {
      this.spotLight.position.set(playerPos.x, playerPos.y + 10, playerPos.z);
      this.spotTarget.position.set(playerPos.x, playerPos.y, playerPos.z);
      this.spotTarget.updateMatrixWorld();
      // Visible shaft: cone (height=9) is centered at origin, so position
      // its center at player.y + 4.5 so apex sits ≈ y+9 and base ≈ y+0.
      if (this.spotShaft) {
        this.spotShaft.position.set(
          playerPos.x,
          playerPos.y + 4.5,
          playerPos.z,
        );
        // Opacity tracks live spotlight intensity so the shaft fades
        // in / out with the day-night transition automatically. Lower
        // peak (0.35) than before so the cone reads as a hint, not a
        // floodlight.
        const peak = NIGHT_PALETTE.spotlightIntensity;
        this.spotShaftMat.uniforms.uOpacity.value =
          (Math.max(
            0,
            this.spotLight.intensity - DAY_PALETTE.spotlightIntensity,
          ) /
            Math.max(0.001, peak - DAY_PALETTE.spotlightIntensity)) *
          0.35;
        this.spotShaft.visible =
          this.spotShaftMat.uniforms.uOpacity.value > 0.005;
      }
    }
    if (this.starGroup && camera) {
      this.starGroup.position.copy(camera.position);
      this.starMaterial.uniforms.uTime.value = elapsed;
      // Visibility tracks live uniform so a partially-faded starfield
      // mid-transition still renders, but a fully-faded one is skipped.
      this.starGroup.visible =
        this.starMaterial.uniforms.uOpacity.value > 0.001;
    }
    if (this.moonGroup && camera) {
      this.#updateMoonPosition(camera);
      this.moonGroup.visible = this.moonDisc.material.opacity > 0.001;
    }
  }

  // ── Build helpers ─────────────────────────────────────────────────────────
  #buildCharacterLights() {
    // Face fill — placed in front of the character (rotates with him)
    // so it actually lights the face rather than sitting on a fixed
    // world axis offset. Decay=1.4 keeps it tight to the head; intensity
    // is high because three.js's physical lighting model dilutes
    // PointLight contribution fast over the head-height distance.
    this.fillLight = new THREE.PointLight(0xffffff, 1.5, 6, 1.4);
    this.fillLight.castShadow = false;
    this.scene.add(this.fillLight);

    // Magical overhead spotlight — day=subtle fill, night=bright cone.
    // castShadow stays FALSE: shadows from a second light kill FPS, and the
    // sun already shadows the character correctly from above.
    this.spotLight = new THREE.SpotLight(
      0xddeeff,
      0, // intensity (set by mode)
      20, // distance
      Math.PI / 5, // 36° cone (half-angle)
      0.6, // penumbra (soft edges)
      1, // linear decay (decay=2 dilutes too aggressively at this distance)
    );
    this.spotLight.castShadow = false;
    this.spotTarget = new THREE.Object3D();
    this.scene.add(this.spotTarget);
    this.spotLight.target = this.spotTarget;
    this.scene.add(this.spotLight);

    // Visible light shaft — three.js SpotLight only lights surfaces it
    // hits, the volumetric cone is invisible without a custom mesh. This
    // additive-blended open cone gives the "stage spotlight" look: bright
    // at the apex, fading toward the ground.
    // Radius 1.2 at the ground = tightly framed around the character; the
    // 2.5 base was too wide and read as a stadium floodlight.
    const shaftGeom = new THREE.ConeGeometry(1.2, 9, 24, 1, true);
    this.spotShaftMat = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
      fog: false,
      uniforms: {
        uColor: { value: new THREE.Color("#ccddff") },
        uOpacity: { value: 0 },
      },
      vertexShader: /* glsl */ `
        varying float vUp;     // 0 at base, 1 at apex
        varying float vEdge;   // 0 at the central axis, 1 at the silhouette
        void main() {
          // Cone is 9 tall, centered at origin → y in [-4.5, 4.5].
          vUp = (position.y + 4.5) / 9.0;
          vEdge = length(position.xz) / max(1.2 * (1.0 - vUp), 0.001);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform vec3 uColor;
        uniform float uOpacity;
        varying float vUp;
        varying float vEdge;
        void main() {
          // Apex hot core, base feathered out. Edge softer than center.
          float fall = pow(vUp, 1.6) * (1.0 - vEdge * 0.4);
          gl_FragColor = vec4(uColor, fall * uOpacity);
        }
      `,
    });
    this.spotShaft = new THREE.Mesh(shaftGeom, this.spotShaftMat);
    this.spotShaft.frustumCulled = false;
    this.spotShaft.renderOrder = 5;
    this.scene.add(this.spotShaft);
  }

  #buildStars() {
    const positions = new Float32Array(STAR_COUNT * 3);
    const sizes = new Float32Array(STAR_COUNT);
    const phases = new Float32Array(STAR_COUNT);
    for (let i = 0; i < STAR_COUNT; i++) {
      // Sample in the upper hemisphere only so we don't waste points below
      // the horizon (player can never look past −15° down anyway).
      const u = Math.random();
      const v = Math.random() * 0.7 + 0.15;
      const theta = u * Math.PI * 2;
      const phi = Math.acos(v); // v in [0.15, 0.85] → phi in [~0.55, ~1.42]
      const r = STAR_DOME_RADIUS;
      positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.cos(phi);
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
      sizes[i] = 0.5 + Math.random() * 1.5;
      phases[i] = Math.random() * Math.PI * 2;
    }
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geom.setAttribute("aSize", new THREE.BufferAttribute(sizes, 1));
    geom.setAttribute("aPhase", new THREE.BufferAttribute(phases, 1));

    this.starMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      uniforms: {
        uTime: { value: 0 },
        uOpacity: { value: 0 },
      },
      vertexShader: /* glsl */ `
        uniform float uTime;
        attribute float aSize;
        attribute float aPhase;
        varying float vTwinkle;
        void main() {
          vec4 mv = modelViewMatrix * vec4(position, 1.0);
          gl_Position = projectionMatrix * mv;
          gl_PointSize = aSize * 3.5;
          vTwinkle = 0.3 + 0.7 * (0.5 + 0.5 * sin(uTime * 1.6 + aPhase * 5.0));
        }
      `,
      fragmentShader: /* glsl */ `
        uniform float uOpacity;
        varying float vTwinkle;
        void main() {
          vec2 c = gl_PointCoord - vec2(0.5);
          float d = length(c);
          if (d > 0.5) discard;
          float core = smoothstep(0.5, 0.0, d);
          gl_FragColor = vec4(vec3(1.0), core * vTwinkle * uOpacity);
        }
      `,
    });

    this.starGroup = new THREE.Group();
    const points = new THREE.Points(geom, this.starMaterial);
    points.frustumCulled = false;
    this.starGroup.add(points);
    this.starGroup.renderOrder = -1; // draw with the sky
    this.scene.add(this.starGroup);
  }

  #buildMoon() {
    this.moonGroup = new THREE.Group();
    this.moonGroup.renderOrder = -1;

    // HDR-boost the disc colour so UnrealBloomPass picks it up (threshold
    // is 0.92 in linear space; 2.4× boost on #ddeeff puts it cleanly past
    // that). Same trick Sun.js uses on the day-side disc.
    const moonColor = new THREE.Color("#ddeeff").multiplyScalar(2.4);
    const moonMat = new THREE.MeshBasicMaterial({
      color: moonColor,
      transparent: true,
      opacity: 0,
      depthWrite: false,
      fog: false,
      toneMapped: false,
    });
    this.moonDisc = new THREE.Mesh(
      new THREE.SphereGeometry(5.0, 24, 18),
      moonMat,
    );
    this.moonDisc.frustumCulled = false;
    this.moonDisc.renderOrder = 10;
    this.moonGroup.add(this.moonDisc);

    // Soft glow corona — billboarded plane with a procedural radial
    // gradient, additive blended so the falloff feathers into the sky
    // instead of reading as a solid disc behind the moon (which is how
    // the old BackSide sphere halo looked).
    const coronaTex = this.#buildCoronaTexture();
    const coronaMat = new THREE.MeshBasicMaterial({
      map: coronaTex,
      color: new THREE.Color("#aac6ff"),
      transparent: true,
      opacity: 0,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
      toneMapped: false,
      side: THREE.DoubleSide,
    });
    this.moonHalo = new THREE.Mesh(new THREE.PlaneGeometry(26, 26), coronaMat);
    this.moonHalo.frustumCulled = false;
    this.moonHalo.renderOrder = 9;
    this.moonGroup.add(this.moonHalo);

    // Fixed direction relative to the camera — moon visible at default
    // tilt: mostly ahead (+Z), a little right (+X), slightly up (+Y).
    this._moonDir = new THREE.Vector3(0.4, 0.15, 0.9).normalize();
    this._moonDist = 150;

    this.scene.add(this.moonGroup);
  }

  /** Procedural 256² halo: hot core fading to fully transparent at the
   *  edge with a pow(1-d, 3.0) curve. Identical technique to Sun.js. */
  #buildCoronaTexture() {
    const size = 256;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    const img = ctx.createImageData(size, size);
    const half = size / 2;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const dx = (x - half) / half;
        const dy = (y - half) / half;
        const d = Math.min(Math.sqrt(dx * dx + dy * dy), 1);
        const a = Math.pow(1 - d, 3.0);
        const i = (y * size + x) * 4;
        img.data[i] = 255;
        img.data[i + 1] = 255;
        img.data[i + 2] = 255;
        img.data[i + 3] = Math.round(a * 255);
      }
    }
    ctx.putImageData(img, 0, 0);
    const tex = new THREE.CanvasTexture(canvas);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    tex.generateMipmaps = false;
    return tex;
  }

  #updateMoonPosition(camera) {
    // Fixed direction relative to the camera so the moon stays in the
    // same part of the sky regardless of player position or sun
    // direction. The previous sun-anchored scheme drifted off-screen as
    // the night-sun moved during the transition tween.
    this.moonGroup.position
      .copy(camera.position)
      .addScaledVector(this._moonDir, this._moonDist);
    // Halo plane billboards toward the camera so the additive corona
    // is always seen face-on (instead of edge-on, which made it vanish).
    this.moonHalo.quaternion.copy(camera.quaternion);
  }

  // ── State application ─────────────────────────────────────────────────────
  #applyInstant(mode) {
    const p = mode === "night" ? NIGHT_PALETTE : DAY_PALETTE;
    // Hard-set every animatable field with no tween. Used on construction so
    // the first rendered frame matches the auto-detected mode.
    this.sun.color.set(p.sunColor);
    this.sun.intensity = p.sunIntensity;
    this.rim.color.set(p.rimColor);
    this.rim.intensity = p.rimIntensity;
    this.ambient.color.set(p.ambientColor);
    this.ambient.intensity = p.ambientIntensity;
    this.hemi.color.set(p.hemiSky);
    this.hemi.groundColor.set(p.hemiGround);
    this.hemi.intensity = p.hemiIntensity;

    this.sky.material.uniforms.uTop.value.set(p.skyTop);
    this.sky.material.uniforms.uMid.value.set(p.skyMid);
    this.sky.material.uniforms.uHorizon.value.set(p.skyHorizon);
    this.sky.material.uniforms.uGround.value.set(p.skyGround);

    this.fog.color.set(p.fogColor);
    this.fog.near = p.fogNear;
    this.fog.far = p.fogFar;

    if (this.grass) {
      this.grass.setColor(p.grassColor);
    }
    if (this.fireflies) {
      this.fireflies.material.uniforms.uIntensity.value = p.fireflyIntensity;
    }
    this.sunMesh?.setOpacity?.(p.sunMeshOpacity);

    this.fillLight.color.set(p.fillColor);
    this.fillLight.intensity = p.fillIntensity;
    this.spotLight.intensity = p.spotlightIntensity;

    this.moonDisc.material.opacity = p.moonOpacity;
    // Halo is additive — a higher peak (0.7) gives a real soft bloom-glow
    // instead of the dull 0.08-opacity backside sphere we had before.
    this.moonHalo.material.opacity = p.moonOpacity * 0.7;
    this.moonGroup.visible = p.moonOpacity > 0.001;

    this.starMaterial.uniforms.uOpacity.value = p.starsOpacity;
    this.starGroup.visible = p.starsOpacity > 0.001;

    if (this.billboards)
      this.billboards.emissiveBoost = p.billboardEmissiveBoost;
    if (this.lanterns)
      for (const l of this.lanterns) l.intensity = p.lanternIntensity;
    // Ocean tints (shallow / deep / foam / sun position) ride day-night
    // together — see Water.applyTimeOfDay for the colour palettes.
    if (this.water) this.water.applyTimeOfDay(mode);
    if (this.lamps) {
      this.lamps.apply({
        intensity: p.lampIntensity,
        bulbColor: 0xffe9b0,
        bulbBrightness: p.lampBulbBrightness,
      });
    }

    // Sun offset (for App.js to track in #tick).
    this.sunOffset = p.sunOffset.clone();
  }

  #transition(mode, duration) {
    const p = mode === "night" ? NIGHT_PALETTE : DAY_PALETTE;
    const ease = "sine.inOut";

    // Make sure stars/moon are added to the render queue at the start of any
    // fade-in (they're hidden when opacity is ~0).
    this.starGroup.visible = true;
    this.moonGroup.visible = true;

    const tweens = [];
    const colorTo = (color, hex) =>
      tweens.push(
        gsap.to(color, {
          r: tmp.set(hex).r,
          g: tmp.g,
          b: tmp.b,
          duration,
          ease,
        }),
      );
    const tmp = new THREE.Color();

    // Lights
    colorTo(this.sun.color, p.sunColor);
    tweens.push(
      gsap.to(this.sun, { intensity: p.sunIntensity, duration, ease }),
    );
    colorTo(this.rim.color, p.rimColor);
    tweens.push(
      gsap.to(this.rim, { intensity: p.rimIntensity, duration, ease }),
    );
    colorTo(this.ambient.color, p.ambientColor);
    tweens.push(
      gsap.to(this.ambient, { intensity: p.ambientIntensity, duration, ease }),
    );
    colorTo(this.hemi.color, p.hemiSky);
    colorTo(this.hemi.groundColor, p.hemiGround);
    tweens.push(
      gsap.to(this.hemi, { intensity: p.hemiIntensity, duration, ease }),
    );

    // Sun follow offset (per-frame writer in App.js reads sunOffset).
    tweens.push(
      gsap.to(this.sunOffset, {
        x: p.sunOffset.x,
        y: p.sunOffset.y,
        z: p.sunOffset.z,
        duration,
        ease,
      }),
    );

    // Sky
    colorTo(this.sky.material.uniforms.uTop.value, p.skyTop);
    colorTo(this.sky.material.uniforms.uMid.value, p.skyMid);
    colorTo(this.sky.material.uniforms.uHorizon.value, p.skyHorizon);
    colorTo(this.sky.material.uniforms.uGround.value, p.skyGround);

    // Fog
    colorTo(this.fog.color, p.fogColor);
    tweens.push(
      gsap.to(this.fog, { near: p.fogNear, far: p.fogFar, duration, ease }),
    );

    // Grass — tween the shared baseColor and propagate to all per-layer
    // materials each onUpdate. GLB grass uses patchShadowTint at a fixed
    // strength so the old uShadowTintStrength tween is dropped.
    if (this.grass) {
      const gTarget = new THREE.Color(p.grassColor);
      tweens.push(
        gsap.to(this.grass.baseColor, {
          r: gTarget.r,
          g: gTarget.g,
          b: gTarget.b,
          duration,
          ease,
          onUpdate: () => this.grass.syncColor(),
        }),
      );
    }

    // Fireflies
    if (this.fireflies) {
      tweens.push(
        gsap.to(this.fireflies.material.uniforms.uIntensity, {
          value: p.fireflyIntensity,
          duration,
          ease,
        }),
      );
    }

    // Sun mesh (visible disc + corona)
    if (this.sunMesh?.tweenOpacity) {
      this.sunMesh.tweenOpacity(p.sunMeshOpacity, duration, ease);
    }

    // Character lights
    colorTo(this.fillLight.color, p.fillColor);
    tweens.push(
      gsap.to(this.fillLight, { intensity: p.fillIntensity, duration, ease }),
    );
    tweens.push(
      gsap.to(this.spotLight, {
        intensity: p.spotlightIntensity,
        duration,
        ease,
      }),
    );

    // Moon (disc + halo opacity lerped together)
    tweens.push(
      gsap.to(this.moonDisc.material, {
        opacity: p.moonOpacity,
        duration,
        ease,
      }),
    );
    tweens.push(
      gsap.to(this.moonHalo.material, {
        opacity: p.moonOpacity * 0.7,
        duration,
        ease,
      }),
    );

    // Stars
    tweens.push(
      gsap.to(this.starMaterial.uniforms.uOpacity, {
        value: p.starsOpacity,
        duration,
        ease,
      }),
    );

    // Billboards (read the scalar each pulse in Billboards.update)
    if (this.billboards) {
      tweens.push(
        gsap.to(this.billboards, {
          emissiveBoost: p.billboardEmissiveBoost,
          duration,
          ease,
        }),
      );
    }

    // Lanterns
    if (this.lanterns) {
      for (const l of this.lanterns) {
        tweens.push(
          gsap.to(l, { intensity: p.lanternIntensity, duration, ease }),
        );
      }
    }

    // Ocean tint — tweens shallow + deep + foam + sun position together.
    if (this.water)
      this.water.applyTimeOfDay(mode, { tween: true, duration, ease });

    // Physical lamps — tween each PointLight's intensity, and animate
    // the shared bulb material color (toward target hex × brightness).
    if (this.lamps && this.lamps.items.length) {
      for (const item of this.lamps.items) {
        tweens.push(
          gsap.to(item.light, { intensity: p.lampIntensity, duration, ease }),
        );
      }
      const tmp = new THREE.Color(0xffe9b0).multiplyScalar(
        p.lampBulbBrightness,
      );
      tweens.push(
        gsap.to(this.lamps.bulbMaterial.color, {
          r: tmp.r,
          g: tmp.g,
          b: tmp.b,
          duration,
          ease,
        }),
      );
    }

    // Note: we deliberately do NOT schedule a delayed visibility hide
    // here — a previous tween's delayedCall firing mid-way through the
    // NEXT (opposite) transition would hide the moon / stars while they
    // should still be ramping up. Visibility is now derived from the
    // live opacity each frame inside tick().

    this._activeTweens = tweens;
  }
}

function playerGroupExists(g) {
  return !!g;
}
