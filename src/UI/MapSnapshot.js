import * as THREE from 'three/webgpu';

// Off-screen render size. Must be a multiple of 64 so width*4 bytes is a
// multiple of the 256-byte row alignment WebGPU's copyTextureToBuffer uses —
// otherwise the readback rows would be padded and the blit would skew.
// 768 keeps the overlay crisp while cutting render + readback cost ~45% vs
// 1024; captures only ever run paused (boot / map open) so this is headroom,
// not a per-frame cost.
const SNAP_SIZE = 768;

// A literal top-down camera view is the MIRROR of a "north-up / east-right"
// map (looking straight down, putting east on the right forces north to the
// bottom). Our marker projection (coords.js worldToSvg) is east-right +
// north-up, so we render with the camera's up = world +Z — which puts north
// at the top of the framebuffer (correct) but east on the LEFT — and then
// mirror horizontally on blit to bring east back to the right.
//
// WebGPU's readback (copyTextureToBuffer) is top-origin, so row 0 is already
// the top of the frame; no vertical flip is needed. If a future three.js
// changes that convention and the map comes out upside-down, flip FLIP_Y.
const FLIP_X = true;
const FLIP_Y = false;

/**
 * Renders the real 3D world straight down into an off-screen texture, reads it
 * back, and exposes it as a plain 2D <canvas>. The map UI (mini-map + overlay)
 * draws that canvas as its background and positions DOM/SVG markers on top via
 * the same worldToSvg projection, so the image and the markers line up exactly.
 *
 * The capture frustum matches WORLD_BOUNDS one-to-one, which is what guarantees
 * that line-up: world X∈[minX,maxX] maps to the full canvas width, Z likewise.
 *
 * Captured BEFORE post-processing (raw scene render) so bloom/tilt-shift don't
 * blow out the map, and with scene.fog nulled (a top-down camera sits hundreds
 * of metres above the terrain, well past the fog far plane).
 */
export class MapSnapshot {
  constructor({ renderer, scene, bounds, hideDuringCapture = [] }) {
    this.renderer = renderer;
    this.scene = scene;
    this.bounds = bounds;
    this.hideList = hideDuringCapture;
    this.size = SNAP_SIZE;
    this.ready = false;
    this._capturing = false;
    this._listeners = new Set();

    const { minX, maxX, minZ, maxZ } = bounds;
    const halfX = (maxX - minX) / 2;
    const halfZ = (maxZ - minZ) / 2;
    const cx = (minX + maxX) / 2;
    const cz = (minZ + maxZ) / 2;

    this.camera = new THREE.OrthographicCamera(-halfX, halfX, halfZ, -halfZ, 1, 800);
    this.camera.up.set(0, 0, 1); // world +Z (north) → top of frame
    this.camera.position.set(cx, 400, cz);
    this.camera.lookAt(cx, 0, cz);
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld(true);

    this.renderTarget = new THREE.RenderTarget(this.size, this.size, {
      depthBuffer: true,
      stencilBuffer: false,
    });
    // Encode to sRGB in the target so the readback bytes match what a 2D
    // canvas expects — otherwise the linear values read back dark/desaturated.
    this.renderTarget.texture.colorSpace = THREE.SRGBColorSpace;

    this.canvas = document.createElement('canvas');
    this.canvas.width = this.size;
    this.canvas.height = this.size;
    this.ctx = this.canvas.getContext('2d');

    this._tmp = document.createElement('canvas');
    this._tmp.width = this.size;
    this._tmp.height = this.size;
    this._tmpCtx = this._tmp.getContext('2d');
  }

  /** Register a callback fired whenever a fresh snapshot is painted. Returns an unsubscribe fn. */
  onReady(fn) {
    this._listeners.add(fn);
    if (this.ready) fn();
    return () => this._listeners.delete(fn);
  }

  /**
   * Render the world top-down once and blit it to the public canvas.
   *
   * `hide` toggles the player (and any hideDuringCapture objects). It's safe
   * for boot/open captures — they happen behind the loading screen or the map
   * backdrop — but the periodic in-game refresh passes hide:false to avoid a
   * one-frame on-screen blink (the async render reads visibility synchronously,
   * so the next on-screen frame would otherwise see the hidden player). From
   * 400m up the player is a couple of pixels and always sits under a marker.
   */
  async capture({ hide = true } = {}) {
    if (this._capturing || !this.renderer) return;
    this._capturing = true;
    const scene = this.scene;
    const prevFog = scene.fog;
    // The scene fog is now a TSL node (FogState); nulling scene.fog alone no
    // longer disables it, so clear the node too for the un-fogged top-down map.
    const prevFogNode = scene.fogNode;
    const hidden = [];
    try {
      scene.fog = null;
      scene.fogNode = null;
      if (hide) {
        for (const obj of this.hideList) {
          if (obj && obj.visible) {
            hidden.push(obj);
            obj.visible = false;
          }
        }
      }
      this.renderer.setRenderTarget(this.renderTarget);
      await this.renderer.renderAsync(scene, this.camera);
      this.renderer.setRenderTarget(null);

      const data = await this.renderer.readRenderTargetPixelsAsync(
        this.renderTarget, 0, 0, this.size, this.size,
      );
      this.#blit(data);
      this.ready = true;
      this._listeners.forEach((fn) => fn());
    } catch (err) {
      console.warn('[MapSnapshot] capture failed', err);
    } finally {
      scene.fog = prevFog;
      scene.fogNode = prevFogNode;
      for (const obj of hidden) obj.visible = true;
      this._capturing = false;
    }
  }

  #blit(data) {
    const bytes = this.size * this.size * 4;
    const clamped = new Uint8ClampedArray(data.buffer, data.byteOffset, bytes);
    this._tmpCtx.putImageData(new ImageData(clamped, this.size, this.size), 0, 0);

    const ctx = this.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.size, this.size);
    ctx.setTransform(
      FLIP_X ? -1 : 1, 0,
      0, FLIP_Y ? -1 : 1,
      FLIP_X ? this.size : 0,
      FLIP_Y ? this.size : 0,
    );
    ctx.drawImage(this._tmp, 0, 0);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }

  dispose() {
    this._listeners.clear();
    this.renderTarget?.dispose?.();
  }
}
