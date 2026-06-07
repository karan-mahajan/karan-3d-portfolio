// Career history for the "Career Ascent" experience section (the 5 bridge
// stations). Synced from the live CMS at karanmahajan.ca/api/experiences —
// `points` are the per-role bullet details shown in the focused E-panel; the
// one-line `summary` is the ambient walk-up card. Matched by company; the
// University of Windsor entry is the Programming Research Assistant role (the
// CMS also lists the Master's degree, which is not a world station).
export const PORTFOLIO_URL = 'https://karanmahajan.ca';

export const experience = [
  {
    company: 'Skylar Media Group',
    role: 'Full Stack Web Developer',
    dates: 'Feb 2025 – Present',
    summary: 'Scalable CMS-driven and headless architectures across WordPress, Drupal, Next.js, React.',
    points: [
      'Built scalable CMS-driven and headless architectures using WordPress and Drupal, integrating with Next.js via REST and GraphQL to deliver flexible, high-performance web applications',
      'Developed modern frontend applications with React and Next.js (SSR, SSG, ISR), improving performance, SEO, and user experience while supporting scalable SaaS platforms',
      'Customized themes, plugins, and backend systems using CPTs, taxonomies, WP-CLI, and hook-based architecture, streamlining workflows and enhancing content management efficiency',
      'Led complex integrations including Stripe (payments, subscriptions, webhooks) and WooCommerce with ERP systems, managing data pipelines, authentication (JWT/OAuth), and role-based access',
      'Strengthened application performance, security, and accessibility through caching, code splitting, Core Web Vitals optimization, WCAG compliance, and best practices like CSP, CORS, and SEO implementation',
    ],
  },
  {
    company: 'University of Windsor',
    role: 'Programming Research Assistant',
    dates: 'May 2024 – Aug 2024',
    summary: 'Frontend redesign of client platform, dynamic UI components, CMS architecture management.',
    points: [
      'Led the frontend redesign of a client-facing platform, improving usability, navigation, accessibility, and overall user experience while aligning with business requirements',
      'Built dynamic, data-driven UI components and integrated RESTful APIs (Velo by Wix) to enable real-time dashboards, seamless frontend-backend communication, and enhanced user engagement',
      'Managed CMS-driven architectures across Wix and WordPress, handling structured data, customer profiles, dynamic content, and implementing SEO best practices for improved search visibility',
    ],
  },
  {
    company: 'Recro',
    role: 'Software Engineer',
    dates: 'Jul 2022 – Mar 2023',
    summary: 'Reusable React component library with cross-framework support and accessibility standards.',
    points: [
      'Led development of a reusable React component library, integrating with Node.js and MongoDB backends while ensuring WCAG-compliant accessibility standards',
      'Built and published reusable component packages (npm + Stencil.js), enabling cross-framework support (React, Angular, Vue) and reducing integration time across projects',
      'Implemented robust testing and documentation using Jest and Storybook, improving component reliability, usability, and design-developer collaboration',
      'Maintained high-quality frontend architecture using TypeScript, SCSS, BEM, and responsive design, while managing code with Git/Bitbucket and Agile workflows (Jira, Confluence)',
    ],
  },
  {
    company: 'Launch Ventures',
    role: 'Software Craftsperson',
    dates: 'Oct 2021 – Jul 2022',
    summary: 'Responsive PWAs in React/Next.js. Dashboards + Node.js APIs over MongoDB.',
    points: [
      'Developed responsive web applications and PWAs using React, Next.js, HTML, and CSS, improving user engagement and mobile retention through optimized UI/UX',
      'Built dynamic dashboards and custom UI components (BEM, Material UI) to enhance data visualization, scalability, and maintainability',
      'Integrated Node.js APIs with MongoDB backends, ensuring efficient data flow, system reliability, and seamless frontend-backend communication',
      'Deployed and optimized applications using nginx and Vercel, while performing end-to-end testing to ensure performance, stability, and high-quality user experience',
    ],
  },
  {
    company: 'MetricStream',
    role: 'Member of Technical Staff',
    dates: 'Jul 2019 – Oct 2021',
    summary: 'MySQL optimization, JavaScript frontend, Java backend, AWS + Jenkins pipelines.',
    points: [
      'Managed and optimized MySQL databases by writing efficient SQL/PL-SQL queries, procedures, and packages, ensuring data accuracy, performance, and quick resolution of production issues',
      'Developed and enhanced frontend features using JavaScript, HTML, and CSS, including form validations and UI improvements for core product functionality',
      'Contributed to backend development using Java, implementing new features (e.g., multi-attachment forms) and improving system scalability and reliability',
      'Streamlined deployment and testing workflows using AWS and Jenkins CI/CD pipelines, while performing end-to-end testing and handling change requests, bug fixes, and Jira-based production support',
    ],
  },
];
