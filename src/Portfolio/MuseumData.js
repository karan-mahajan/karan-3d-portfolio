/**
 * Content for the making-of museum (spec §7). Eight chapters, one per
 * station_01..08 in museum.glb — the station's userData.chapter indexes into
 * this list by `id`.
 *
 * Voice: Karan, first person, talking to the visitor who found the secret.
 *
 * `accent` drives both the DOM panel accent bar AND the 3D station trim tint
 * (header band + brass cap) so a chapter's color follows you from the room
 * into the reading panel.
 *
 * `body` is one paragraph as a string, or an array of paragraph strings.
 */
export const MUSEUM_CHAPTERS = [
  {
    id: 1,
    title: "A world written in Python",
    blurb: "Every hill, pond and path on this island came out of a script.",
    accent: "#e8842c",
    pages: [
      {
        heading: "No island was sculpted by hand",
        body: [
          "The world above you was not modeled with a mouse. It is the output of a stack of Python scripts that drive Blender headlessly — fifteen numbered sections that build terrain, carve ponds and a river, lay stones, raise bridges and plant every tree.",
          "Why? Because a hand-sculpted world is frozen. A scripted world is a program you can rerun, tweak and diff.",
        ],
      },
      {
        heading: "Rebuild from zero, every time",
        body:
          "Each section runner wipes the file and rebuilds everything from the foundation up to its own phase. There are no manual fixes hiding in the .blend — if it isn't in a script, it doesn't exist. Change one waypoint in section 02 and the whole island regenerates around it, identical every run.",
      },
      {
        heading: "Masks paint the ground",
        body:
          "Where grass grows, where dirt paths wander, where the beach fades in — none of that is geometry. It's images: grayscale masks exported from the build, sampled at runtime to scatter a hundred thousand grass blades and blend path textures. Editing the ground means editing pixels.",
      },
      {
        heading: "From .blend to browser",
        body:
          "The build exports GLB files that get Draco-compressed before shipping — the geometry you're standing in went from megabytes to a few hundred kilobytes. One npm script re-crunches everything after every Blender export.",
      },
      {
        heading: "Including this room",
        body:
          "This museum is no exception. The staircase you walked down, the torches, the banners, the little island miniature on the table behind you — all authored by another set of Python scripts, about 28,000 triangles in total. The world's making-of museum was made the same way the world was.",
      },
    ],
  },
  {
    id: 2,
    title: "Standing on giants' shoulders",
    blurb: "This world exists because Bruno Simon showed what a portfolio could be.",
    accent: "#2fa08f",
    pages: [
      {
        heading: "Credit, up front",
        body: [
          "If you've seen bruno-simon.com, you already know the giant. Bruno Simon's drivable 3D portfolio — and the seventeen devlogs he published while rebuilding it in 2025 — are the reason this island exists.",
          "This chapter is the public thank-you. None of what follows pretends otherwise.",
        ],
      },
      {
        heading: "Seventeen devlogs, studied like a textbook",
        body:
          "Before a single tree was planted here, every one of Bruno's devlogs was transcribed and cross-referenced against his shipped source code. The result was a knowledge base: how he keeps a whole world to a few hundred draw calls, how his grass never ends, why his weather runs on one shared clock.",
      },
      {
        heading: "What was borrowed",
        body:
          "The ideas that crossed over: a camera-following window of grass instead of an infinite field, instancing discipline for everything repeated, GPU-side particles, draw-call frugality as a design value — and the conviction that a portfolio can be a place, not a page.",
      },
      {
        heading: "What was built differently",
        body:
          "You walk here instead of driving. The grass blade is my own curved nine-vertex design with an olive palette. The renderer is WebGPU with TSL node materials throughout. The world is authored by Python instead of by hand. The palette, the weather moods, the mini-games, the character — those are mine. Study the master, then make it yours.",
      },
    ],
  },
  {
    id: 3,
    title: "WebGPU & TSL",
    blurb: "The whole world renders on the browser's newest graphics API.",
    accent: "#8a63ff",
    pages: [
      {
        heading: "A renderer from the future",
        body:
          "This site runs on WebGPURenderer — Three.js's next-generation backend — with automatic WebGL2 fallback for browsers that aren't there yet. Every custom effect is built in TSL, Three's node-based shading language, which compiles to WGSL or GLSL depending on what your machine speaks.",
      },
      {
        heading: "The day the old tricks died",
        body: [
          "Classic Three.js shader hacking meant patching GLSL with onBeforeCompile. On WebGPU those patches don't error — they silently do nothing.",
          "The footprints you leave in snow were invisible for days because of exactly this: the effect was 'working' in code and absent on screen, until it was rebuilt as TSL nodes. Rule learned the hard way: on this renderer, everything is a node graph or it doesn't exist.",
        ],
      },
      {
        heading: "Water without mirrors",
        body:
          "The ocean refracts the world without a single extra render pass. No reflection targets, no refraction cameras — the surface reads the live frame through viewportSharedTexture and bends it in the shader. The most expensive-looking effect in the world is nearly free.",
      },
      {
        heading: "Particles the CPU never touches",
        body:
          "Snow, rain, wind lines and fireflies are GPU instances driven entirely by time uniforms. The CPU uploads nothing per frame — each snowflake computes its own fall, drift and respawn in the vertex shader, forever.",
      },
      {
        heading: "Wipes, swirls and frost",
        body:
          "The frost line that dresses the character for snow, the golden wipe that dressed you for this museum, the violet swirl inside the magic door, the flicker on these torches — all small TSL node graphs sharing one clock. Even this room is a shader gallery.",
      },
    ],
  },
  {
    id: 4,
    title: "The performance war",
    blurb: "The scariest bug was a number that was never real.",
    accent: "#d8503f",
    pages: [
      {
        heading: "The 75,000 draw-call myth",
        body: [
          "For a while this project believed it was issuing 75,000 draw calls a frame — a catastrophic number that spawned a whole optimization battle plan.",
          "It was a misread. That counter was the renderer's lifetime total, not per-frame. The real number: about 414 draws, 1.18 million triangles, with the CPU finishing its work in under a millisecond. Lesson one of performance work: make sure the number you're fighting actually exists.",
        ],
      },
      {
        heading: "The real enemy: pixels",
        body:
          "Properly measured, the bottleneck is GPU fill — the cost of shading every pixel of grass, water and fog, especially on high-DPI screens. So the war was fought there: 157 materials consolidated into a couple of shared ones, static props merged into spatial chunks, the post-processing chain fused into a single node graph.",
      },
      {
        heading: "Quality that heals itself",
        body:
          "The site watches its own frame rate and walks up or down a ladder of quality tiers — thinning leaves, shrinking resolution, swapping image-based lighting for a simple hemisphere — then climbs back when headroom returns. A MacBook at night and a gaming PC at noon both get the best version of the world they can hold at speed.",
      },
      {
        heading: "The asset diet",
        body:
          "Around 25 MB was cut from the initial payload: avatar textures crushed to WebP (4.9 MB → 2.2 MB), world geometry Draco-compressed, ground textures in GPU-native KTX2. This museum follows suit — it costs the initial load zero bytes, fetching itself only when you wander near the door.",
      },
      {
        heading: "An honest loading screen",
        body:
          "The loading screen draws the real island map and fills it with the real boot milestones — no fake progress bar easing to 90%. Physics, world, character and shaders load in parallel, and what you see is what's actually happening.",
      },
    ],
  },
  {
    id: 5,
    title: "Bringing the character to life",
    blurb: "The hardest pixels on the island are the ones shaped like me.",
    accent: "#de6f9e",
    pages: [
      {
        heading: "An avatar with my face",
        body:
          "The character is an Avaturn scan of me, animated with Mixamo motion clips retargeted onto its skeleton — fifty-two bones that have to agree with every clip about which way is up.",
      },
      {
        heading: "The sinking body",
        body: [
          "They often don't agree. Animation clips arrived authored Z-up while the avatar lives Y-up, and with rest poses that differed just enough to twist arms and puff the chest.",
          "Untreated, the body literally sank through the floor mid-idle. Every clip now gets rebased to the avatar's bind pose and normalized to the right up-axis at load — skip either step and the character breaks in ways you feel before you can explain.",
        ],
      },
      {
        heading: "Walking at the speed of the clip",
        body:
          "Animations have a natural pace — this walk cycle covers ground at 1.65 m/s, the run at 4.43. Drive the character faster than the clip and the legs scramble; slower and they skate. The movement speeds are tuned to the measured paces, not the other way around.",
      },
      {
        heading: "Feet on the ground",
        body:
          "What finally killed the 'pasted on the screen' feeling: a soft procedural contact shadow under the body, and two-bone foot IK that bends each leg so the feet actually plant on slopes and stairs — including the ones you just walked down.",
      },
      {
        heading: "A wardrobe of magic",
        body:
          "The snow outfit and the museum robes you're wearing right now are separate models grafted onto the one live skeleton, bones matched by name. A shader wipe sweeps the change up the body — frost-blue for snow, gold for this room — so getting dressed reads as magic instead of a model swap.",
      },
    ],
  },
  {
    id: 6,
    title: "A hundred little systems",
    blurb: "A world feels alive in the parts you almost don't notice.",
    accent: "#e3b53f",
    pages: [
      {
        heading: "42 reasons to keep exploring",
        body:
          "There are 42 achievements hidden in this world, from common to legendary, each landing with its own cinematic reveal. Finding this museum is one of the rare ones. The trophy panel (press J) tracks your completion — some visitors have found everything.",
      },
      {
        heading: "Weather with moods",
        body:
          "Rain rolls in with thunder, snow accumulates in patches and freezes the pond, and the character quietly puts on a warmer outfit when the storm settles in. All of it shares one clock, so the wind in the grass, the falling leaves and the drifting snow always agree about the weather.",
      },
      {
        heading: "Games hiding in the grass",
        body:
          "The Colour Garden lets you charge and throw paint at giant pots. The shore has a distance-guessing game with exacting standards. Pushing things you shouldn't push earns you commentary. None of it advances your career — that's the point.",
      },
      {
        heading: "A living map",
        body:
          "The parchment minimap unfolds into a full map where discovered places become teleport markers — each jump an iris-wipe with a landing spot chosen by a navigation grid so you never materialize inside a rock. Click bare ground and the character simply walks there.",
      },
      {
        heading: "Other visitors were here",
        body:
          "The social layer speaks in light: liking the site releases a firefly into a permanent sky swarm, notes left on the wishing tree sway in the wind for everyone, and faint lights on the horizon count the people who walked here before you.",
      },
    ],
  },
  {
    id: 7,
    title: "Built with AI",
    blurb: "An honest note about how this was actually made.",
    accent: "#57b7dc",
    pages: [
      {
        heading: "The confession",
        body:
          "Most of the code in this world was written in collaboration with Claude, Anthropic's AI. Not generated and pasted — built across hundreds of working sessions, in a loop that looks a lot like working with a very fast, very literal engineer who never gets tired and occasionally puts a door in your face.",
      },
      {
        heading: "The loop",
        body: [
          "Every feature follows the same rhythm: brainstorm the idea together, lock a written spec, plan the build, implement, and then I walk the world and report what's wrong — 'the camera shows the door, not me.'",
          "Nothing ships until I've walked it. Each feature lands as one commit, after that walk.",
        ],
      },
      {
        heading: "Memory between sessions",
        body:
          "The AI keeps persistent notes between sessions — what was decided, what failed and why, which rules I've set ('never invent an asset', 'I verify everything manually'). A session can pick up a half-built museum exactly where the last one left off. The notes about building this room were read to build this page.",
      },
      {
        heading: "Who did what",
        body:
          "The AI wrote code, chased shader bugs and did the math. I made every call that matters: how the world should feel, what got rejected (plenty did), what's worth building at all, and whether it's done. AI multiplied the hands; the taste, the direction and the stubbornness are human.",
      },
      {
        heading: "Why say it out loud",
        body:
          "Because this is how software is being made now, and pretending otherwise would be a strange thing to do in a museum dedicated to honesty about process. The interesting question was never whether AI wrote the code — it's whether the world is worth walking through. You're standing in the answer.",
      },
    ],
  },
  {
    id: 8,
    title: "Behind the curtain",
    blurb: "About this museum, the secrets still out there, and a thank-you.",
    accent: "#57b96a",
    pages: [
      {
        heading: "You found the secret",
        body:
          "No map marker pointed at that door. You noticed a light-shaft in a quiet clearing, or followed the fireflies at night, and you opened it. That curiosity is exactly what this room was built for — welcome to the basement.",
      },
      {
        heading: "A museum 45 meters down",
        body:
          "There's no hole in the lawn. The door is a portal: crossing it teleports you into this sealed gallery hanging 45 meters under the grass, connected to the surface by nothing but an iris-wipe and a bit of fiction. The Doraemon anywhere-door was the design brief, almost literally.",
      },
      {
        heading: "The camera wars",
        body:
          "Getting you down here cleanly took three rounds of playtesting. The camera escaped through a doorway that had no collision and filmed the museum from the void. It hid behind the door panel so all you saw was wood. It once spun a slow full circle after every teleport because of a 6.28-radian disagreement. Each fix is invisible now — which is the whole job.",
      },
      {
        heading: "More secrets out there",
        body:
          "This isn't the only thing hidden upstairs. Push things that look pushable. Try a backflip. Read the sky during a thunderstorm. Visit the lava pool behind the hill — once. The map only shows what you've already found.",
      },
      {
        heading: "Thank you",
        body: [
          "To Bruno Simon for the inspiration and the open devlogs. To Three.js, Rapier, Blender, Avaturn and Mixamo for the shoulders this stands on. To the CC0 sound and asset communities.",
          "And to you, for walking far enough off the path to find a door that shouldn't exist. The exit is up the stairs — the island is waiting.",
        ],
      },
    ],
  },
];

// Four banner cloths along the gallery walls (bannerCloth_01..04) — richer
// spread than the exported violet/teal pair, sampled from the chapter accents.
export const BANNER_TINTS = ["#6a4a9e", "#2c6e63", "#9e3f3a", "#9e7a2c"];
