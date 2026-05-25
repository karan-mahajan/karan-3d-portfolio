// Project data schema.
//
// Legacy fields (kept for back-compat): `description`, `url`.
// New optional fields read by the future gallery UI:
//   summary       — short tagline (falls back to description)
//   role          — your role on the project; hide the tab if null
//   problem       — what the project solves; hide the section if null
//   solution      — how it solves it; hide the section if null
//   impact        — quantified outcomes; hide the section if null
//   highlights    — array of bullet points; hide if missing or empty
//   links.live    — public site (falls back to url)
//   links.github  — repo URL; hide button if null
//   links.caseStudy — write-up URL; hide button if null
//
// `getProjectField(project, key, fallback)` does the fallback so callers
// don't have to special-case every reader.

export const portfolio = {
  name: "Karan Mahajan",
  title: "Full Stack Developer",
  photo: "/textures/screenshots/karan.jpg",
  projects: [
    {
      name: "Alectra Utilities",
      summary: "Enterprise Drupal CMS for an Ontario utility. Complex content workflows, scheduled transitions, Pantheon deployments.",
      description: "Enterprise Drupal CMS for an Ontario utility. Complex content workflows, scheduled transitions, Pantheon deployments.",
      role: null,
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Drupal", "PHP", "Pantheon", "Lando"],
      links: { live: "https://alectrautilities.com", github: null, caseStudy: null },
      url: "https://alectrautilities.com",
      color: "#00e5ff",
      image: "/textures/screenshots/alectra.png",
    },
    {
      name: "RPRA Website",
      summary: "Full QA audit + development for Ontario's resource productivity authority. Custom tooling, plugin management, Git deployment pipelines.",
      description: "Full QA audit + development for Ontario's resource productivity authority. Custom tooling, plugin management, Git deployment pipelines.",
      role: null,
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["WordPress", "PHP", "Git", "Pantheon"],
      links: { live: "https://rpra.ca", github: null, caseStudy: null },
      url: "https://rpra.ca",
      color: "#fbbf24",
      image: null,
    },
    {
      name: "Interstone",
      summary: "WooCommerce store with WebP image compression, REST API integrations, Wordfence security across environments.",
      description: "WooCommerce store with WebP image compression, REST API integrations, Wordfence security across environments.",
      role: null,
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["WordPress", "WooCommerce", "REST API", "PHP"],
      links: { live: "", github: null, caseStudy: null },
      url: "",
      color: "#39ff14",
      image: "/textures/screenshots/interstone.png",
    },
    {
      name: "findabl",
      summary: "Next.js app with Apollo GraphQL, dynamic employee profiles, CSP enforcement, SSR optimizations.",
      description: "Next.js app with Apollo GraphQL, dynamic employee profiles, CSP enforcement, SSR optimizations.",
      role: null,
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["Next.js", "React", "GraphQL", "Apollo"],
      links: { live: "", github: null, caseStudy: null },
      url: "",
      color: "#ff6b9d",
      image: "/textures/screenshots/findabl.png",
    },
    {
      name: "Trimark Windows",
      summary: "ExpressionEngine project with isolated landing page system and PHP form handlers using Mailjet/Postmark.",
      description: "ExpressionEngine project with isolated landing page system and PHP form handlers using Mailjet/Postmark.",
      role: null,
      problem: null,
      solution: null,
      impact: null,
      highlights: [],
      tech: ["ExpressionEngine", "PHP", "Mailjet"],
      links: { live: "", github: null, caseStudy: null },
      url: "",
      color: "#a78bfa",
      image: null,
    },
  ],
};

/**
 * Read a field with graceful fallback to legacy keys. Use this everywhere
 * the gallery UI displays a project so the same fallback rules apply.
 *
 *   getProjectField(p, 'summary')   → p.summary || p.description
 *   getProjectField(p, 'liveUrl')   → p.links?.live || p.url
 *   getProjectField(p, 'github')    → p.links?.github || null
 *   getProjectField(p, 'caseStudy') → p.links?.caseStudy || null
 *   getProjectField(p, 'image')     → p.image
 *   getProjectField(p, 'color')     → p.color
 *   getProjectField(p, key)         → p[key] (or fallback)
 */
export function getProjectField(project, field, fallback = '') {
  if (!project) return fallback;
  if (field === 'summary')   return project.summary || project.description || fallback;
  if (field === 'liveUrl')   return project.links?.live || project.url || fallback;
  if (field === 'github')    return project.links?.github || null;
  if (field === 'caseStudy') return project.links?.caseStudy || null;
  const v = project[field];
  return v === undefined || v === null ? fallback : v;
}
