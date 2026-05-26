import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

/**
 * Asset loading manager. Wraps Three's GLTF loader in Promises,
 * tracks a single global progress (0–1) for the loading screen.
 */
export class Loader extends EventTarget {
  constructor() {
    super();
    this.manager = new THREE.LoadingManager();
    this.manager.onProgress = (_url, loaded, total) => {
      this.dispatchEvent(
        new CustomEvent('progress', { detail: { loaded, total, ratio: loaded / Math.max(total, 1) } }),
      );
    };
    this.manager.onLoad = () => {
      this.dispatchEvent(new CustomEvent('load'));
    };
    this.manager.onError = (url) => {
      this.dispatchEvent(new CustomEvent('error', { detail: { url } }));
    };

    this.gltf = new GLTFLoader(this.manager);
    this.fbx = new FBXLoader(this.manager);
    this.texture = new THREE.TextureLoader(this.manager);
  }

  loadGLTF(url) {
    return new Promise((resolve, reject) => {
      this.gltf.load(url, resolve, undefined, reject);
    });
  }

  loadTexture(url) {
    return new Promise((resolve, reject) => {
      this.texture.load(url, resolve, undefined, reject);
    });
  }

  loadFBX(url) {
    return new Promise((resolve, reject) => {
      this.fbx.load(url, resolve, undefined, reject);
    });
  }
}
