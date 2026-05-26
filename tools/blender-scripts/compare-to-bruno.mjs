/**
 * compare-to-bruno.mjs
 *
 * Visual comparison probe: renders our recreated GLB exports in a minimal Three.js
 * scene via headless Chromium, and screenshots Bruno's live site at
 * https://bruno-simon.com/. Both screenshots saved to
 * reports/blender-recreate-compare/<YYYY-MM-DD>/ for side-by-side comparison.
 *
 * Run from project root:
 *   NODE_PATH=/tmp/node_modules node tools/blender-scripts/compare-to-bruno.mjs
 *
 * Loads any GLB it finds in /Users/.../bruno-blend-recreate/ (landing.glb is
 * required; terrain.glb, scenery.glb, foliage.glb, props.glb, respawns.glb are
 * optional — see 06-final.blend's optional multi-export script). Any present
 * GLBs are layered into the same Three.js scene, giving a full world render
 * instead of just the landing area.
 *
 * Requirements:
 *   - Playwright installed somewhere reachable. If not in this project, install once:
 *       cd /tmp && npm install --no-save playwright
 *       cd /tmp && npx playwright install chromium
 *     then set NODE_PATH=/tmp/node_modules before running this script.
 *   - landing.glb must exist at bruno-blend-recreate/landing.glb (Phase 6 output).
 *
 * Output:
 *   reports/blender-recreate-compare/<YYYY-MM-DD>/karan-world.png   (or karan-landing.png if only landing.glb is present)
 *   reports/blender-recreate-compare/<YYYY-MM-DD>/bruno-live.png
 *   reports/blender-recreate-compare/<YYYY-MM-DD>/diff-report.md
 */

import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'
import http from 'node:http'

const PROJECT_ROOT = path.resolve(new URL('../..', import.meta.url).pathname)
const GLB_DIR = '/Users/mahajankaran/Documents/Projects/bruno-blend-recreate'
const TODAY = new Date().toISOString().slice(0, 10)
const OUT_DIR = path.join(PROJECT_ROOT, 'reports', 'blender-recreate-compare', TODAY)
const BRUNO_URL = 'https://bruno-simon.com/'

const PORT = 8923

// Order matters: terrain first (so it sits at the back of the depth buffer in case
// of z-fighting), then larger props, then small details, then landing on top.
const CANDIDATE_GLBS = [
  'terrain.glb',
  'scenery.glb',
  'foliage.glb',
  'props.glb',
  'respawns.glb',
  'landing.glb',
]


function discoverGlbs() {
  const found = []
  for (const name of CANDIDATE_GLBS) {
    const full = path.join(GLB_DIR, name)
    if (fs.existsSync(full)) {
      found.push({ name, full, size: fs.statSync(full).size })
    }
  }
  if (found.length === 0) {
    throw new Error(`No GLBs found in ${GLB_DIR}. Run Phase 6 first.`)
  }
  // landing.glb is mandatory for a meaningful comparison
  if (!found.some((g) => g.name === 'landing.glb')) {
    throw new Error(`landing.glb missing. Run Phase 6 first.`)
  }
  console.log('Found GLBs:')
  for (const g of found) {
    console.log(`  ${g.name.padEnd(15)} ${g.size.toLocaleString().padStart(12)} bytes`)
  }
  return found
}

/**
 * Serve a tiny Three.js scene that loads each available GLB. The page exposes
 * `window.__ready` once all loads settle (or `window.__error` if any fail).
 */
function startLocalServer(glbs) {
  const glbList = JSON.stringify(glbs.map((g) => g.name))

  const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>karan-world preview</title>
<style>html,body{margin:0;height:100%;background:#cfd5d8}canvas{display:block}</style>
</head><body>
<script type="importmap">{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}</script>
<script type="module">
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true })
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setSize(1280, 800)
renderer.outputColorSpace = THREE.SRGBColorSpace
document.body.appendChild(renderer.domElement)

const scene = new THREE.Scene()
scene.background = new THREE.Color('#cfd5d8')

const camera = new THREE.PerspectiveCamera(35, 1280 / 800, 0.1, 800)
// Initial guess — overridden by bbox auto-frame once all GLBs load.
camera.position.set(80, 60, 80)
camera.lookAt(0, 0, 0)

scene.add(new THREE.HemisphereLight(0xffffff, 0x404060, 1.2))
const sun = new THREE.DirectionalLight(0xffffff, 2.5)
sun.position.set(100, 120, 80)
scene.add(sun)

const GLBS = ${glbList}
const loader = new GLTFLoader()
const loaded = []

Promise.all(GLBS.map((name) => new Promise((resolve, reject) => {
  loader.load('/glb/' + name, (gltf) => {
    gltf.scene.name = name
    scene.add(gltf.scene)
    loaded.push(name)
    console.log('loaded ' + name)
    resolve()
  }, undefined, (err) => {
    console.error('load error ' + name + ': ' + err.message)
    reject(err)
  })
}))).then(() => {
  // Auto-frame the combined scene
  try {
    const box = new THREE.Box3().setFromObject(scene)
    if (!box.isEmpty()) {
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const dist = Math.max(maxDim * 1.2, 30)
      // Diorama-style top-down-ish angle, looking south
      camera.position.set(center.x + dist * 0.5, center.y + dist * 0.7, center.z + dist * 0.9)
      camera.near = 0.1
      camera.far = dist * 5
      camera.updateProjectionMatrix()
      camera.lookAt(center)
      console.log('framed combined bbox center=' + JSON.stringify(center.toArray().map(v => +v.toFixed(2))) +
        ' size=' + JSON.stringify(size.toArray().map(v => +v.toFixed(2))) +
        ' camera.position=' + JSON.stringify(camera.position.toArray().map(v => +v.toFixed(2))))
    }
  } catch (e) {
    console.warn('bbox framing failed: ' + e.message)
  }
  renderer.render(scene, camera)
  window.__loaded = loaded
  window.__ready = true
}).catch((err) => {
  window.__error = err.message
})

function tick() { renderer.render(scene, camera); requestAnimationFrame(tick) }
tick()
</script></body></html>`

  const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/index.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(html)
      return
    }
    if (req.url.startsWith('/glb/')) {
      const name = req.url.slice('/glb/'.length)
      const safeName = path.basename(name)
      const full = path.join(GLB_DIR, safeName)
      if (!fs.existsSync(full)) {
        res.writeHead(404)
        res.end(`not found: ${safeName}`)
        return
      }
      const data = fs.readFileSync(full)
      res.writeHead(200, { 'content-type': 'model/gltf-binary' })
      res.end(data)
      return
    }
    res.writeHead(404)
    res.end('not found')
  })
  return new Promise((resolve) => server.listen(PORT, () => resolve(server)))
}

async function screenshotOurs(browser, outFile) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  page.on('console', (m) => console.log('  [page]', m.text()))
  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' })
  await page.waitForFunction(() => window.__ready || window.__error, { timeout: 60_000 })
  const err = await page.evaluate(() => window.__error)
  if (err) throw new Error(`Three.js scene errored: ${err}`)
  const loaded = await page.evaluate(() => window.__loaded || [])
  console.log(`  page loaded ${loaded.length} GLBs:`, loaded)
  await page.waitForTimeout(800)
  await page.screenshot({ path: outFile, fullPage: false })
  await ctx.close()
  return loaded
}

async function screenshotBruno(browser, outFile) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } })
  const page = await ctx.newPage()
  try {
    await page.goto(BRUNO_URL, { waitUntil: 'load', timeout: 60_000 })
    await page.waitForTimeout(6_000)
    await page.mouse.click(640, 400)
    await page.waitForTimeout(12_000)
    await page.mouse.click(640, 400)
    await page.waitForTimeout(4_000)
    await page.screenshot({ path: outFile, fullPage: false })
  } catch (e) {
    console.warn(`  WARN: could not screenshot bruno-simon.com (${e.message}). Continuing.`)
    return false
  }
  await ctx.close()
  return true
}

async function writeReport({ outDir, ourPng, brunoPng, loadedGlbs, glbs, brunoOk }) {
  const fileSize = (p) => (fs.existsSync(p) ? fs.statSync(p).size : 0)
  const totalBytes = glbs.reduce((acc, g) => acc + g.size, 0)
  const lines = [
    '# Bruno comparison probe — visual side-by-side',
    '',
    `Run: ${new Date().toISOString()}`,
    '',
    '## What was compared',
    '',
    `- Ours (rendered headless):  \`${path.basename(ourPng)}\`  (${fileSize(ourPng).toLocaleString()} bytes)`,
    `- Bruno's live site:         \`${path.basename(brunoPng)}\`  (${fileSize(brunoPng).toLocaleString()} bytes)` + (brunoOk ? '' : ' — capture failed, see console'),
    '',
    `### GLBs assembled into the Three.js scene (${loadedGlbs.length})`,
    '',
    ...glbs.map((g) =>
      `- \`${g.name}\`  (${g.size.toLocaleString()} bytes)` + (loadedGlbs.includes(g.name) ? '  ✅ loaded' : '  ⚠️ not loaded')
    ),
    '',
    `**Total GLB bytes:** ${totalBytes.toLocaleString()}`,
    '',
    '## How to read these screenshots',
    '',
    'Ours shows the complete reconstructed world from all available GLBs (each one',
    'covers a Bruno-style category: terrain, scenery, foliage, props, landing).',
    'Bruno\'s live shot is taken after clicking through the intro reveal.',
    '',
    'Compare:',
    '- Are the BRUNO letters visible in both?',
    '- Is the bonfire and kiosk roughly in the same relative position?',
    '- Are the palette colors similar (orange-beige dominant)?',
    '- Are there bushes/flowers around the landing area in ours?',
    '',
    'Known visual gaps (per `blender-recreate-gaps.md`):',
    '- GAP-B-002: oak + cherry trees missing in ours (Geometry Nodes not recreated)',
    '- GAP-B-006: terrain looks near-white in ours (EXR mask textures not extracted)',
    '- GAP-B-007: some area label PNGs are magenta placeholders (extraction missed them)',
    '',
    `Open the PNGs in your image viewer. Comparison folder:`,
    `\`${outDir.replace(PROJECT_ROOT + '/', '')}\``,
  ].join('\n')
  const reportPath = path.join(outDir, 'diff-report.md')
  fs.writeFileSync(reportPath, lines + '\n')
  console.log(`Wrote report → ${reportPath}`)
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true })
  const glbs = discoverGlbs()

  const server = await startLocalServer(glbs)
  console.log(`Local Three.js server listening on http://localhost:${PORT}/`)

  const browser = await chromium.launch({ headless: true })
  // Output filename: karan-world.png if multiple GLBs, karan-landing.png if only landing
  const ourPngName = glbs.length > 1 ? 'karan-world.png' : 'karan-landing.png'
  const ourPng = path.join(OUT_DIR, ourPngName)
  const brunoPng = path.join(OUT_DIR, 'bruno-live.png')
  let loadedGlbs = []
  let brunoOk = false
  try {
    console.log(`\nScreenshotting our scene (${glbs.length} GLB${glbs.length > 1 ? 's' : ''}) …`)
    loadedGlbs = await screenshotOurs(browser, ourPng)
    console.log(`  → ${ourPng}`)

    console.log(`\nScreenshotting Bruno's live site …`)
    brunoOk = await screenshotBruno(browser, brunoPng)
    if (!brunoOk) {
      console.log(`  (skipped — see warning above)`)
    } else {
      console.log(`  → ${brunoPng}`)
    }

    await writeReport({ outDir: OUT_DIR, ourPng, brunoPng, loadedGlbs, glbs, brunoOk })
  } finally {
    await browser.close()
    server.close()
  }

  console.log('')
  console.log(`Done. Compare images in:  ${OUT_DIR}`)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
