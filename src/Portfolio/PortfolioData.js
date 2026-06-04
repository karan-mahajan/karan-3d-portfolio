// Project data schema.
//
// Legacy fields (kept for back-compat): `description`, `url`.
// Fields read by the gallery UI:
//   summary       — short tagline (falls back to description)
//   role          — your role on the project; hide the meta part if null
//   year          — project year; shown in the panel meta row
//   category       — project category (Website / Web App / macOS App); meta row
//   description   — full narrative; paragraphs separated by a blank line (\n\n),
//                   rendered as separate <p> blocks in the panel
//   problem/solution/impact — optional case-study sections; hide if null
//   highlights    — array of bullet points; hide if missing or empty
//   links.live    — public site (falls back to url); null hides the button
//   links.github  — repo URL; hide button if null
//   links.caseStudy — write-up URL; hide button if null
//   image         — screenshot path, or null (poster falls back to accent block)
//
// Content + screenshots are synced from the live CMS at
// https://www.karanmahajan.ca/api/projects (see /tmp/fetch-project-shots.mjs
// for the image pipeline). `getProjectField(project, key, fallback)` does the
// fallback so callers don't have to special-case every reader.

export const portfolio = {
  name: "Karan Mahajan",
  title: "Full Stack Developer",
  photo: "/textures/screenshots/karan.webp",
  projects: [
    {
      name: "findabl",
      summary: "findabl is a full-stack SaaS platform I designed and built single-handedly to help businesses improve their visibility across AI-powered search tools like ChatGPT, Gemini, Perplexity, and Microsoft Copilot.",
      description: "findabl is a full-stack SaaS platform I designed and built single-handedly to help businesses improve their visibility across AI-powered search tools like ChatGPT, Gemini, Perplexity, and Microsoft Copilot. I shipped the entire customer-facing product solo in [N weeks] — Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, Supabase, Stripe, and SendGrid — covering the full journey from marketing and authentication through billing, onboarding, and a post-subscription dashboard.\n\nVisitors register with server-side reCAPTCHA v3, choose a Starter or Growth plan, acknowledge a dynamically generated PDF service agreement, and check out through Stripe, with webhooks keeping Supabase in sync and firing automated welcome emails and activity logs. On the technical side I built dual AI-powered business search on GPT-4o-mini and Gemini 2.5 Flash with IP-based rate limiting, promotional flows with auto-applied Stripe coupons matched by email, and marketing pages cached with Next.js's \"use cache\" directive on week-long TTLs and Suspense skeletons for fast loads.",
      role: "Full Stack Web Developer",
      year: 2025,
      category: "Website",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Next.js", "Supabase", "Stripe", "SendGrid", "OpenAI", "Tailwind CSS", "Authentication"],
      links: { live: "https://www.findabl.ai/", github: null, caseStudy: null },
      url: "https://www.findabl.ai/",
      color: "#00e5ff",
      image: "/textures/screenshots/findabl.webp",
    },
    {
      name: "Alectra Utilities",
      summary: "I built and maintained a large-scale, multi-brand enterprise web platform serving two major Ontario utilities — Alectra Utilities and Guelph Hydro — powering their public sites, customer portals, and a shared UI component library consumed by third-party billing and account-management apps.",
      description: "I built and maintained a large-scale, multi-brand enterprise web platform serving two major Ontario utilities — Alectra Utilities and Guelph Hydro — powering their public sites, customer portals, and a shared UI component library consumed by third-party billing and account-management apps. The hardest part was integration: I engineered custom Drupal modules exposing dynamic header/footer and billing endpoints that external JSP applications rendered live, so two separately-built systems looked and behaved like one product.\n\nI stood up full-text search on Apache Solr with advanced filtering and spellcheck, and delivered a responsive, multi-brand front-end on a custom Foundation theme with multi-region layouts, inline alerts, and accessible navigation. The platform runs on Pantheon with enterprise caching and is hardened to utility-sector security standards (CSP, 2FA, and bot/spam protection) for reliability at scale.",
      role: "Full Stack Web Developer",
      year: 2025,
      category: "Website",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Drupal", "PHP", "MySQL", "Pantheon", "Lando", "Terminus", "SCSS", "Drush", "SendGrid", "reCAPTCHA"],
      links: { live: "https://alectrautilities.com/", github: null, caseStudy: null },
      url: "https://alectrautilities.com/",
      color: "#fbbf24",
      image: "/textures/screenshots/alectra.webp",
    },
    {
      name: "AI Writing Assistant",
      summary: "I built a native macOS writing assistant that lives in the system tray and drafts replies in my own voice across Teams, Outlook, JIRA, Confluence, GitHub, and ChatGPT.",
      description: "I built a native macOS writing assistant that lives in the system tray and drafts replies in my own voice across Teams, Outlook, JIRA, Confluence, GitHub, and ChatGPT. The hard problem was reading on-screen context without browser scraping or extensions — I solved it with Swift accessibility helpers calling the macOS Accessibility API directly, then stream replies from the Claude API tuned to a personal style guide and memory file.\n\nThree triggers cover every surface: a selection popover for grammar and rewrites, a proactive compose bubble above multi-line inputs, and a global overlay window. To preserve rich email formatting I write Outlook replies via synthesized CGEventPost keystrokes instead of flattening the content, and the API key never leaves the OS keychain. Built with Electron, Node.js, and Swift.",
      role: "App Developer",
      year: 2026,
      category: "macOS App",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["NodeJS", "Electron", "Swift", "Claude API", "macOS Accessibility API", "AppleScript", "CGEventPost", "Whisper", "Python"],
      links: { live: "", github: "https://github.com/karan-mahajan/Personal-AI-Writing-Assistant", caseStudy: null },
      url: "",
      color: "#6366f1",
      image: null,
    },
    {
      name: "Interstone",
      summary: "I designed and built a custom WordPress theme for Interstone, a premium building-materials company, turning a [N]-product catalogue into a polished, fully responsive browsing experience with no transactional layer.",
      description: "I designed and built a custom WordPress theme for Interstone, a premium building-materials company, turning a [N]-product catalogue into a polished, fully responsive browsing experience with no transactional layer. The interesting constraint was using WooCommerce purely as a catalogue engine — I stripped all cart and checkout UI so users could explore products by category and filter by material, colour, and finish, with live search returning instant results as they type.\n\nThe standout feature is an AI-powered Visual Search page where users upload a photo of their space and get relevant product recommendations back. Under the hood I built a strict SCSS token system on Bootstrap 5 with a Gulp pipeline (compilation, autoprefixing, minification, source maps) and seven reusable Gutenberg blocks on ACF Pro, so the client can compose pages without touching code.",
      role: "Full Stack Web Developer",
      year: 2026,
      category: "Website",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["WordPress", "PHP", "WooCommerce", "ACF", "Gutenberg", "SCSS", "AI"],
      links: { live: "https://interstone.ca", github: null, caseStudy: null },
      url: "https://interstone.ca",
      color: "#39ff14",
      image: "/textures/screenshots/interstone.webp",
    },
    {
      name: "Alectra Corporate Website",
      summary: "I led the Drupal 10 → 11 major-version migration for Alectra Inc.'s corporate website — one of Ontario's largest electricity distributors, serving over 1 million customers — upgrading the platform across a 60+ component, paragraph-based content system with no loss of content or layout.",
      description: "I led the Drupal 10 → 11 major-version migration for Alectra Inc.'s corporate website — one of Ontario's largest electricity distributors, serving over 1 million customers — upgrading the platform across a 60+ component, paragraph-based content system with no loss of content or layout. On top of the migration I owned frontend and custom module development end to end, building three custom Drupal modules covering automated cache management, employee document handling, and security headers, all on a fully custom Foundation for Sites theme. The 60+ reusable components let the client's editors assemble new pages — careers listings, data-sheet sections, CTA layouts — entirely from the CMS without developer involvement.",
      role: "Full Stack Web Developer",
      year: 2025,
      category: "Web App",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Drupal", "PHP", "Twig", "SCSS", "JavaScript", "jQuery", "Gulp", "Lando", "Terminus", "Pantheon"],
      links: { live: "https://www.alectra.com/", github: null, caseStudy: null },
      url: "https://www.alectra.com/",
      color: "#ff6b9d",
      image: "/textures/screenshots/alectra-corporate.webp",
    },
    {
      name: "WEAL Website",
      summary: "Developed and designed a comprehensive website using Wix, enabling efficient sample submission and result management.",
      description: "Developed and designed a comprehensive website using Wix, enabling efficient sample submission and result management. Implemented an admin dashboard for streamlined sample analysis and results uploading, improving overall administrative workflow",
      role: "Programming Research Assistant",
      year: 2024,
      category: "Website",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Wix", "Velo API", "JavaScript", "HTML/CSS"],
      links: { live: "https://www.xsal.ca/", github: null, caseStudy: null },
      url: "https://www.xsal.ca/",
      color: "#a78bfa",
      image: "/textures/screenshots/weal.webp",
    },
    {
      name: "Campus Cart",
      summary: "I built Campus Cart, a university marketplace web app on Django, Python, and PostgreSQL, restricted to verified staff and students so on-campus trading stays inside a trusted community.",
      description: "I built Campus Cart, a university marketplace web app on Django, Python, and PostgreSQL, restricted to verified staff and students so on-campus trading stays inside a trusted community. Users list and browse items across categories with email-authenticated profiles, full-text search, and a map view that surfaces listings by location.",
      role: "Full Stack Developer",
      year: 2024,
      category: "Website",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Django", "Python", "JavaScript", "HTML/CSS", "PostgreSQL"],
      links: { live: "", github: "https://github.com/karan-mahajan/CampusCart", caseStudy: null },
      url: "",
      color: "#ff8c42",
      image: "/textures/screenshots/campus-cart.webp",
    },
    {
      name: "News Article Recommender",
      summary: "Developed a news article recommender system with Python (Pandas) and NLP, featuring a React JS UI and MongoDB storage.",
      description: "Developed a news article recommender system with Python (Pandas) and NLP, featuring a React JS UI and MongoDB storage. Enhanced user engagement through personalized recommendations and Tableau visualizations of user data interactions",
      role: "Full Stack Web Developer",
      year: 2024,
      category: "Web App",
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Python", "NodeJS", "React", "HTML/CSS", "JavaScript", "Tableau"],
      links: { live: "", github: null, caseStudy: null },
      url: "",
      color: "#22d3ee",
      image: "/textures/screenshots/news-recommender.webp",
    },
  ],
};

/**
 * Read a field with graceful fallback to legacy keys. Use this everywhere
 * the gallery UI displays a project so the same fallback rules apply.
 */
export function getProjectField(project, field, fallback = "") {
  if (!project) return fallback;
  if (field === "summary")   return project.summary || project.description || fallback;
  if (field === "liveUrl")   return project.links?.live || project.url || fallback;
  if (field === "github")    return project.links?.github || null;
  if (field === "caseStudy") return project.links?.caseStudy || null;
  const v = project[field];
  return v === undefined || v === null ? fallback : v;
}
