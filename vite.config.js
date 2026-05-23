import { defineConfig } from 'vite';

export default defineConfig({
  assetsInclude: ['**/*.glb', '**/*.gltf', '**/*.fbx', '**/*.hdr'],
  publicDir: 'static',
  build: {
    target: 'esnext',
    assetsInlineLimit: 0,
  },
  optimizeDeps: {
    exclude: ['@dimforge/rapier3d', '@dimforge/rapier3d-compat'],
  },
  server: {
    host: true,
    open: false,
  },
});
