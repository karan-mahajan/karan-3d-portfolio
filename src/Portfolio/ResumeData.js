/**
 * Structured resume content for the floating-book reading view (ResumeBookView).
 *
 * Content is sourced from the existing data modules so there's one source of
 * truth: experience ← ExperienceData, skills ← SkillsData, projects ←
 * PortfolioData. Bio fields (title/summary/location/education) come from
 * karanmahajan.ca/resume (JSON-LD), 2026-06-07.
 *
 * The view paginates by MEASURING: `overviewLeft`/`overviewRight` are the first
 * spread; every `section` is a title + an array of self-contained `blocks`
 * (one role / project / skill group each, with ALL its detail). The view packs
 * blocks onto fixed-size pages until they fill, so each section flows across as
 * many spreads as it needs and nothing is truncated.
 */
import { experience, PORTFOLIO_URL } from './ExperienceData.js';
import { skills } from './SkillsData.js';
import { portfolio } from './PortfolioData.js';

const NAME = 'Karan Mahajan';
const TITLE = 'Full Stack Developer';
const LOCATION = 'Ontario, Canada';
const SUMMARY =
  'Full-stack web developer based in Ontario, Canada with 5+ years building ' +
  'production applications — from headless CMS architectures to AI-integrated ' +
  'SaaS platforms.';
const CONTACT = {
  email: 'karanmahajan321@gmail.com',
  linkedin: 'https://www.linkedin.com/in/karan-mahajan/',
  website: PORTFOLIO_URL,
  location: LOCATION,
};
const RESUME_URL = `${PORTFOLIO_URL}/resume`;

const education = [
  { school: 'University of Windsor', credential: 'Master of Applied Computing', note: '' },
];

// ── Block builders (each is one self-contained item) ─────────────────────────

const contactRows = () => `
  <div class="rb-contact">
    <a href="mailto:${CONTACT.email}">✉  ${CONTACT.email}</a>
    <a href="${CONTACT.linkedin}" target="_blank" rel="noopener">in  LinkedIn</a>
    <a href="${CONTACT.website}" target="_blank" rel="noopener">↗  ${CONTACT.website.replace(/^https?:\/\//, '')}</a>
    <span class="rb-contact-loc">📍  ${CONTACT.location}</span>
  </div>`;

const overviewLeft = `
  <p class="rb-eyebrow">Resume</p>
  <h1 class="rb-name">${NAME}</h1>
  <p class="rb-title">${TITLE} · ${LOCATION}</p>
  <p class="rb-lead">${SUMMARY}</p>`;

const overviewRight = `
  <h2 class="rb-h2">Get in touch</h2>
  ${contactRows()}
  <a class="rb-download" href="${RESUME_URL}" target="_blank" rel="noopener">↗  View full resume</a>`;

// Experience — EVERY bullet point per role.
const expBlock = (e) => `
  <div class="rb-entry">
    <p class="rb-entry-top">${e.company}</p>
    <p class="rb-entry-meta">${e.role} · ${e.dates}</p>
    <ul class="rb-points">${e.points.map((p) => `<li>${p}</li>`).join('')}</ul>
  </div>`;

// Projects — full summary, no truncation.
const projBlock = (p) => `
  <div class="rb-proj">
    <p class="rb-proj-name">${p.name}</p>
    <p class="rb-proj-cat">${[p.category, p.year, p.role].filter(Boolean).join(' · ')}</p>
    <p class="rb-proj-sum">${p.summary}</p>
  </div>`;

const skillBlock = (c) => `
  <div class="rb-skillcat">
    <p class="rb-skillcat-h">${c.category}</p>
    <div class="rb-chips">${c.items.map((i) => `<span class="rb-chip">${i}</span>`).join('')}</div>
  </div>`;

const eduBlock = (e) => `
  <div class="rb-entry">
    <p class="rb-entry-top">${e.school}</p>
    <p class="rb-entry-meta">${[e.credential, e.note].filter(Boolean).join(' · ')}</p>
  </div>`;

const moreBlock = `
  <div class="rb-entry">
    <p class="rb-lead">See every role and project in full detail, with live links and case studies, on the portfolio.</p>
    <a class="rb-download" href="${RESUME_URL}" target="_blank" rel="noopener">↗  ${CONTACT.website.replace(/^https?:\/\//, '')}/resume</a>
    ${contactRows()}
  </div>`;

const projects = portfolio.projects || [];

export const resume = {
  name: NAME,
  title: TITLE,
  contact: CONTACT,
  downloadUrl: RESUME_URL,
  overviewLeft,
  overviewRight,
  sections: [
    { title: 'Experience', blocks: experience.map(expBlock) },
    { title: 'Selected Projects', blocks: projects.map(projBlock) },
    { title: 'Skills', blocks: skills.map(skillBlock) },
    { title: 'Education', blocks: [...education.map(eduBlock), moreBlock] },
  ],
};
