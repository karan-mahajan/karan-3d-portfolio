import { defineConfig, loadEnv } from 'vite';

/**
 * Dev-only: serve the Vercel `/api/*` serverless functions under `npm run dev`.
 * Plain Vite doesn't run them (they only exist on Vercel's runtime), so locally
 * the social fetches would 404. This middleware imports the same handlers and
 * runs them in the Vite node process, after loading `.env` files (incl.
 * `.env.local`) into process.env so the Upstash client picks up the keys. In
 * production this plugin is inert — Vercel runs the real functions.
 */
function apiDevServer() {
  const ROUTES = new Set(['state', 'like', 'whisper']);
  return {
    name: 'api-dev-server',
    apply: 'serve',
    configureServer(server) {
      // Load ALL env vars from .env* (no prefix filter) → process.env, so the
      // serverless handlers see KV_REST_API_URL / _TOKEN exactly as on Vercel.
      const env = loadEnv(server.config.mode, process.cwd(), '');
      for (const [k, v] of Object.entries(env)) {
        if (process.env[k] === undefined) process.env[k] = v;
      }

      server.middlewares.use(async (req, res, next) => {
        if (!req.url || !req.url.startsWith('/api/')) return next();
        const url = new URL(req.url, 'http://localhost');
        const name = url.pathname.replace(/^\/api\//, '').replace(/\.js$/, '');
        if (!ROUTES.has(name)) return next();
        try {
          // ssrLoadModule returns Vite's cached module and re-evaluates it when
          // the file changes, so API edits hot-apply without a server restart.
          const handler = (await server.ssrLoadModule(`/api/${name}.js`)).default;
          req.query = Object.fromEntries(url.searchParams);
          await handler(req, res);
        } catch (err) {
          console.error(`[api-dev] /api/${name} failed:`, err);
          if (!res.headersSent) {
            res.statusCode = 500;
            res.setHeader('Content-Type', 'application/json');
          }
          res.end(JSON.stringify({ error: 'dev_handler_error' }));
        }
      });
    },
  };
}

export default defineConfig({
  assetsInclude: ['**/*.glb', '**/*.gltf', '**/*.fbx', '**/*.hdr'],
  publicDir: 'static',
  plugins: [apiDevServer()],
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
