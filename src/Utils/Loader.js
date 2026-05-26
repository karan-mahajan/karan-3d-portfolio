import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';

/**
 * Asset loading manager. Wraps Three's GLTF loader in Promises,
 * tracks a single global progress (0–1) for the loading screen.
 *
 * Decoders are registered up-front so any GLB encountered downstream can
 * use Draco geometry compression, Meshopt buffer compression, or KTX2
 * texture transcoding without per-call setup. KTX2 needs the WebGLRenderer
 * to detect supported texture formats — call attachRenderer() once the
 * renderer exists (see App.js #initRenderer).
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
    this.draco = new DRACOLoader(this.manager).setDecoderPath('/draco/');
    this.gltf.setDRACOLoader(this.draco);
    this.gltf.setMeshoptDecoder(MeshoptDecoder);
    this.ktx2 = null; // set by attachRenderer()

    this.fbx = new FBXLoader(this.manager);
    this.texture = new THREE.TextureLoader(this.manager);
  }

  attachRenderer(renderer) {
    this.ktx2 = new KTX2Loader(this.manager)
      .setTranscoderPath('/basis/')
      .detectSupport(renderer);
    this.gltf.setKTX2Loader(this.ktx2);
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
