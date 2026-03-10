---
marp: true
theme: default
size: 16:9
paginate: true
math: katex
style: |
 

  :root {
    --accent: #6C5CE7;
    --accent-warm: #FD79A8;
    --accent-gold: #FDCB6E;
    --accent-teal: #00CEC9;
    --dark: #0B0E11;
    --text-main: #1A1D23;
    --text-soft: #4A5568;
    --surface: #FFFFFF;
    --surface-warm: #FFF8F3;
    --surface-cool: #F0F4FF;
    --font-base: 24px;
    --font-head: 56px;
    --bg-header: rgba(108, 92, 231, 0.06);
    --bg-row-even: rgba(108, 92, 231, 0.025);
    --bg-card: rgba(255, 255, 255, 0.92);
    --bg-secondary: #F7F8FC;
    --border-color: rgba(108, 92, 231, 0.12);
    --radius: 20px;
  }

  section {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 88% 12%, rgba(108, 92, 231, 0.18) 0%, transparent 48%),
      radial-gradient(ellipse at 12% 88%, rgba(0, 206, 201, 0.14) 0%, transparent 48%),
      linear-gradient(135deg, #F0F4FF 0%, #ECF1FC 50%, #E8F0FC 100%);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }

  section > * {
    position: relative;
    z-index: 1;
  }

  /* Slide content sections must fill the full slide height so grid-template-rows % values resolve */
  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end {
    flex: 1;
    min-height: 0;
  }

  /* TYPOGRAPHY — Large & Expressive */
  h1 {
    font-family: Georgia, 'Palatino Linotype', 'Book Antiqua', serif;
    font-weight: 600;
    font-size: var(--font-head);
    letter-spacing: -2px;
    color: var(--dark);
    margin: 0 0 22px 0;
    line-height: 1.04;
  }

  h3 {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 14px 0;
  }

  p {
    margin-bottom: 14px;
    line-height: var(--slide-lh, 1.40);
    color: var(--text-main);
    font-size: var(--slide-fs, inherit);
  }

  strong {
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -0.02em;
  }

  em, i {
    color: var(--text-soft);
    font-style: italic;
  }

  mark {
    background: rgba(253, 203, 110, 0.35);
    padding: 1px 5px;
    border-radius: 4px;
    font-weight: 500;
    color: inherit;
  }

  /* LISTS — Spacious & Readable */
  ul {
    padding: 0;
    margin: 0;
    list-style: none !important;
  }

  li {
    line-height: var(--slide-lh, 1.35);
    margin-bottom: 11px;
    padding-left: 24px;
    position: relative;
    font-size: var(--slide-fs, inherit);
    letter-spacing: -0.01em;
  }

  /* Vibrant circle bullets with subtle glow rings */
  li::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0.57em;
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: var(--accent);
    box-shadow: 0 0 0 2.5px rgba(108, 92, 231, 0.18);
  }

  /* Alternating bullet colors with matching glow */
  li:nth-child(2)::before {
    background: var(--accent-teal);
    box-shadow: 0 0 0 2.5px rgba(0, 206, 201, 0.18);
  }
  li:nth-child(3)::before {
    background: var(--accent-gold);
    box-shadow: 0 0 0 2.5px rgba(253, 203, 110, 0.30);
  }
  li:nth-child(4)::before {
    background: var(--accent-warm);
    box-shadow: 0 0 0 2.5px rgba(253, 121, 168, 0.20);
  }

  li strong, li b {
    letter-spacing: -0.02em;
  }

  li em, li i {
    color: var(--text-soft);
    font-style: italic;
  }

  /* IMAGES */
  .img-col {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    overflow: hidden;
    position: relative;
  }

  .img-col > div {
    max-width: 100%;
    max-height: 100%;
    overflow: hidden;
    box-sizing: border-box;
  }

  .img-col img {
    display: block;
    max-width: calc(100% - 2px);
    max-height: calc(100% - 2px);
    width: auto;
    height: auto;
    object-fit: contain;
    padding: 14px;
    box-sizing: border-box;
  }

  /* TABLE: centered auto-width layout */
  .table-clean { width: auto; margin: 0 auto; }
  .table-clean th, .table-clean td { text-align: center; }

  /* LAYOUT GRIDS */
  .grid-50-50 { display: grid; grid-template-columns: 1fr 1fr; }
  .grid-40-60 { display: grid; grid-template-columns: 40% 60%; }
  .grid-60-40 { display: grid; grid-template-columns: 60% 40%; }
  .grid-30-70 { display: grid; grid-template-columns: 30% 70%; }
  .grid-35-65 { display: grid; grid-template-columns: 35% 65%; }

  .grid-50-50 table { font-size: 16px; }
  .grid-35-65 table { font-size: 12px; }
  .grid-40-60 table { font-size: 14px; }
  .grid-60-40 table { font-size: 16px; }
  .grid-30-70 table { font-size: 11px; }

  .pad-col {
    padding: 46px 48px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
    box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child { margin-bottom: auto; }

  /* CARDS */
  .card-grid {
    display: grid;
    gap: 20px;
    margin-top: 18px;
    height: auto;
    align-content: start;
  }

  .feature-card {
    background: #FFFFFF;
    padding: 20px 22px;
    border: 1px solid rgba(108, 92, 231, 0.10);
    border-radius: var(--radius);
    box-shadow: none;
    overflow: hidden;
    position: relative;
    transition: none;
  }

  /* Accent top-bar on cards — rotating colors */
  .feature-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 4px;
    background: var(--accent);
    border-radius: 20px 20px 0 0;
  }

  .card-grid .feature-card:nth-child(2)::before {
    background: var(--accent-teal);
  }
  .card-grid .feature-card:nth-child(3)::before {
    background: var(--accent-gold);
  }
  .card-grid .feature-card:nth-child(4)::before {
    background: var(--accent-warm);
  }

  .card-grid .feature-card:nth-child(2n) {
    transform: none;
  }

  .card-grid .feature-card:nth-child(3n) {
    background: rgba(240, 244, 255, 0.88);
  }

  /* DARK BACKGROUND — Rich gradient */
  .bg-dark {
    background:
      radial-gradient(ellipse at 20% 0%, rgba(108, 92, 231, 0.15), transparent 50%),
      radial-gradient(ellipse at 80% 100%, rgba(253, 121, 168, 0.10), transparent 45%),
      linear-gradient(160deg, #0B0E11 0%, #141820 45%, #1A1F2E 100%) !important;
    color: #F0F2F8 !important;
  }

  .bg-dark h1,
  .bg-dark p,
  .bg-dark li {
    color: #F0F2F8 !important;
  }

  .bg-dark strong {
    color: var(--accent-gold) !important;
  }

  .bg-dark li::before {
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.35);
  }

  .bg-accent {
    background:
      linear-gradient(135deg, #6C5CE7 0%, #A29BFE 40%, #FD79A8 100%) !important;
    color: #FFFFFF !important;
  }

  .bg-accent h1,
  .bg-accent p,
  .bg-accent li {
    color: #FFFFFF !important;
  }

  /* TITLE SLIDE overrides */
  .slide-title::after {
    content: "";
    position: absolute;
    right: -80px;
    bottom: -80px;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
  }

  .slide-title::before {
    content: "";
    position: absolute;
    left: -60px;
    top: -60px;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    z-index: 0;
  }

  .slide-title .title-shell {
    gap: 14px;
    justify-content: center;
  }

  .slide-title h1 {
    font-size: 72px;
    line-height: 1.0;
    max-width: 16ch;
    letter-spacing: -2.5px;
    text-shadow: 0 2px 30px rgba(0, 0, 0, 0.15);
  }

  .title-rule {
    width: 120px !important;
    height: 6px !important;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.7) !important;
    box-shadow: 0 8px 24px rgba(255, 255, 255, 0.15);
  }

  .title-authors {
    font-size: 26px !important;
    font-weight: 500;
    letter-spacing: 0.02em;
    opacity: 0.92;
  }

  .title-subtitle {
    font-size: 18px !important;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.75;
  }

  /* END SLIDE */
  .slide-end .pad-col {
    justify-content: center;
    align-items: center;
    text-align: center;
  }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }

  .slide-end h1 {
    font-size: 88px !important;
    max-width: none;
    letter-spacing: -3px;
    margin-bottom: 20px;
  }

  .slide-end .end-note {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: var(--radius);
    padding: 24px 28px;
    box-shadow: none;
    max-width: 900px;
    margin: 0 auto;
    text-align: left;
  }

  /* HERO overrides */
  .slide-hero .hero-copy {
    justify-content: center;
  }

  .slide-hero.slide-hero-full h1 {
    margin-bottom: 22px;
  }

  .slide-hero.slide-hero-full .hero-panel {
    padding: 28px 36px !important;
    border-left: 5px solid var(--accent) !important;
    border-radius: 0 18px 18px 0 !important;
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.15) 0%, rgba(108, 92, 231, 0.04) 100%) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li {
    font-size: 24px !important;
    line-height: 1.45 !important;
    font-weight: 500;
    color: rgba(255,255,255,0.93);
  }
  .slide-hero.slide-hero-full .hero-panel li::before {
    display: none;
  }

  .slide-hero .hero-panel,
  .slide-split .hero-panel {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 22px 26px !important;
    box-shadow: none;
  }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #E4ECFA 0%, #E9EFF9 60%, #EDF2FB 100%);
  }

  /* METHOD / STEPS */
  .slide-method .step-stack {
    display: grid;
    gap: 10px;
  }

  .slide-method .step-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent);
    border-radius: 4px 16px 16px 4px;
    padding: 14px 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }

  .slide-method.bg-dark .step-card,
  .slide-hero.bg-dark .hero-panel,
  .slide-split.bg-dark .hero-panel {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.10);
    box-shadow: none;
  }

  .slide-results .pad-col:last-child {
    background: rgba(247, 248, 252, 0.85);
    border-left: 1px solid var(--border-color);
  }

  /* TABLES — Clean & Elegant */
  table {
    width: 100%;
    max-width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    margin-top: 18px;
    font-size: 16px;
    background: transparent;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: none;
    border: 1px solid var(--border-color);
  }

  th {
    text-align: left;
    padding: 10px 12px;
    color: var(--accent);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.82em;
    background: rgba(108, 92, 231, 0.04);
    border-bottom: 2px solid rgba(108, 92, 231, 0.15);
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  td {
    padding: 9px 12px;
    border-bottom: 1px solid rgba(108, 92, 231, 0.06);
    color: var(--text-main);
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  tr:nth-child(even) {
    background: rgba(108, 92, 231, 0.018);
  }

  tr:last-child td {
    border-bottom: none;
  }

  .dense .pad-col {
    padding: 36px 40px;
  }

  .dense h1 {
    margin-bottom: 14px;
  }

  .dense .feature-card,
  .dense .step-card,
  .dense .hero-panel {
    padding: 14px 16px !important;
    border-radius: 14px;
  }

  .dense li {
    margin-bottom: 8px;
    padding-left: 20px;
  }

  .dense li::before {
    width: 8px;
    height: 8px;
  }

  .dense table {
    font-size: 15px;
  }

  .x-dense .pad-col {
    padding: 30px 34px;
  }

  .x-dense h1 {
    margin-bottom: 10px;
  }

  .x-dense .feature-card,
  .x-dense .step-card,
  .x-dense .hero-panel {
    padding: 12px 14px !important;
    border-radius: 12px;
  }

  .x-dense li {
    margin-bottom: 6px;
    padding-left: 18px;
    line-height: 1.22;
  }

  .x-dense li::before {
    width: 7px;
    height: 7px;
    box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.15);
  }

  .x-dense table {
    font-size: 14px;
  }

  /* KATEX */
  .katex {
    font-size: inherit !important;
    color: inherit !important;
  }
  .katex-display {
    font-size: inherit !important;
    margin: 0 !important;
  }

  /* Dynamic grid classes for split layouts */
  .split-gap { width: 100%; gap: 12px; box-sizing: border-box; }
  .split-gap > * { min-width: 0; min-height: 0; }
  .grid-34-66 { display: grid; grid-template-columns: 34% 66%; height: 100%; }
  .grid-35-65 { display: grid; grid-template-columns: 35% 65%; height: 100%; }
  .grid-36-64 { display: grid; grid-template-columns: 36% 64%; height: 100%; }
  .grid-37-63 { display: grid; grid-template-columns: 37% 63%; height: 100%; }
  .grid-38-62 { display: grid; grid-template-columns: 38% 62%; height: 100%; }
  .grid-39-61 { display: grid; grid-template-columns: 39% 61%; height: 100%; }
  .grid-40-60 { display: grid; grid-template-columns: 40% 60%; height: 100%; }
  .grid-41-59 { display: grid; grid-template-columns: 41% 59%; height: 100%; }
  .grid-42-58 { display: grid; grid-template-columns: 42% 58%; height: 100%; }
  .grid-43-57 { display: grid; grid-template-columns: 43% 57%; height: 100%; }
  .grid-44-56 { display: grid; grid-template-columns: 44% 56%; height: 100%; }
  .grid-45-55 { display: grid; grid-template-columns: 45% 55%; height: 100%; }
  .grid-46-54 { display: grid; grid-template-columns: 46% 54%; height: 100%; }
  .grid-47-53 { display: grid; grid-template-columns: 47% 53%; height: 100%; }
  .grid-48-52 { display: grid; grid-template-columns: 48% 52%; height: 100%; }
  .grid-49-51 { display: grid; grid-template-columns: 49% 51%; height: 100%; }
  .grid-50-50 { display: grid; grid-template-columns: 50% 50%; height: 100%; }
  .grid-51-49 { display: grid; grid-template-columns: 51% 49%; height: 100%; }
  .grid-52-48 { display: grid; grid-template-columns: 52% 48%; height: 100%; }
  .grid-53-47 { display: grid; grid-template-columns: 53% 47%; height: 100%; }
  .grid-54-46 { display: grid; grid-template-columns: 54% 46%; height: 100%; }
  .grid-55-45 { display: grid; grid-template-columns: 55% 45%; height: 100%; }
  .grid-56-44 { display: grid; grid-template-columns: 56% 44%; height: 100%; }
  .grid-57-43 { display: grid; grid-template-columns: 57% 43%; height: 100%; }
  .grid-58-42 { display: grid; grid-template-columns: 58% 42%; height: 100%; }
  .grid-59-41 { display: grid; grid-template-columns: 59% 41%; height: 100%; }
  .grid-60-40 { display: grid; grid-template-columns: 60% 40%; height: 100%; }
  .grid-61-39 { display: grid; grid-template-columns: 61% 39%; height: 100%; }
  .grid-62-38 { display: grid; grid-template-columns: 62% 38%; height: 100%; }
  .grid-63-37 { display: grid; grid-template-columns: 63% 37%; height: 100%; }
  .grid-64-36 { display: grid; grid-template-columns: 64% 36%; height: 100%; }
  .grid-65-35 { display: grid; grid-template-columns: 65% 35%; height: 100%; }
  .grid-66-34 { display: grid; grid-template-columns: 66% 34%; height: 100%; }
  .grid-67-33 { display: grid; grid-template-columns: 67% 33%; height: 100%; }
  .grid-68-32 { display: grid; grid-template-columns: 68% 32%; height: 100%; }
  .grid-69-31 { display: grid; grid-template-columns: 69% 31%; height: 100%; }
  .grid-70-30 { display: grid; grid-template-columns: 70% 30%; height: 100%; }
  .grid-71-29 { display: grid; grid-template-columns: 71% 29%; height: 100%; }
  .grid-72-28 { display: grid; grid-template-columns: 72% 28%; height: 100%; }
  .grid-73-27 { display: grid; grid-template-columns: 73% 27%; height: 100%; }
  .grid-74-26 { display: grid; grid-template-columns: 74% 26%; height: 100%; }
  .grid-75-25 { display: grid; grid-template-columns: 75% 25%; height: 100%; }
  .grid-76-24 { display: grid; grid-template-columns: 76% 24%; height: 100%; }
  .grid-77-23 { display: grid; grid-template-columns: 77% 23%; height: 100%; }
  .grid-78-22 { display: grid; grid-template-columns: 78% 22%; height: 100%; }
  .grid-rows-24-76 { display: grid; grid-template-rows: 24% 76%; height: 100%; }
  .grid-rows-25-75 { display: grid; grid-template-rows: 25% 75%; height: 100%; }
  .grid-rows-26-74 { display: grid; grid-template-rows: 26% 74%; height: 100%; }
  .grid-rows-27-73 { display: grid; grid-template-rows: 27% 73%; height: 100%; }
  .grid-rows-28-72 { display: grid; grid-template-rows: 28% 72%; height: 100%; }
  .grid-rows-29-71 { display: grid; grid-template-rows: 29% 71%; height: 100%; }
  .grid-rows-30-70 { display: grid; grid-template-rows: 30% 70%; height: 100%; }
  .grid-rows-31-69 { display: grid; grid-template-rows: 31% 69%; height: 100%; }
  .grid-rows-32-68 { display: grid; grid-template-rows: 32% 68%; height: 100%; }
  .grid-rows-33-67 { display: grid; grid-template-rows: 33% 67%; height: 100%; }
  .grid-rows-34-66 { display: grid; grid-template-rows: 34% 66%; height: 100%; }
  .grid-rows-35-65 { display: grid; grid-template-rows: 35% 65%; height: 100%; }
  .grid-rows-36-64 { display: grid; grid-template-rows: 36% 64%; height: 100%; }
  .grid-rows-37-63 { display: grid; grid-template-rows: 37% 63%; height: 100%; }
  .grid-rows-38-62 { display: grid; grid-template-rows: 38% 62%; height: 100%; }
  .grid-rows-39-61 { display: grid; grid-template-rows: 39% 61%; height: 100%; }
  .grid-rows-40-60 { display: grid; grid-template-rows: 40% 60%; height: 100%; }
  .grid-rows-41-59 { display: grid; grid-template-rows: 41% 59%; height: 100%; }
  .grid-rows-42-58 { display: grid; grid-template-rows: 42% 58%; height: 100%; }
  .grid-rows-43-57 { display: grid; grid-template-rows: 43% 57%; height: 100%; }
  .grid-rows-44-56 { display: grid; grid-template-rows: 44% 56%; height: 100%; }
  .grid-rows-45-55 { display: grid; grid-template-rows: 45% 55%; height: 100%; }
  .grid-rows-46-54 { display: grid; grid-template-rows: 46% 54%; height: 100%; }
  .grid-rows-47-53 { display: grid; grid-template-rows: 47% 53%; height: 100%; }
  .grid-rows-48-52 { display: grid; grid-template-rows: 48% 52%; height: 100%; }
  .grid-rows-49-51 { display: grid; grid-template-rows: 49% 51%; height: 100%; }
  .grid-rows-50-50 { display: grid; grid-template-rows: 50% 50%; height: 100%; }
  .grid-rows-51-49 { display: grid; grid-template-rows: 51% 49%; height: 100%; }
  .grid-rows-52-48 { display: grid; grid-template-rows: 52% 48%; height: 100%; }
  .grid-rows-53-47 { display: grid; grid-template-rows: 53% 47%; height: 100%; }
  .grid-rows-54-46 { display: grid; grid-template-rows: 54% 46%; height: 100%; }
  .grid-rows-55-45 { display: grid; grid-template-rows: 55% 45%; height: 100%; }
  .grid-rows-56-44 { display: grid; grid-template-rows: 56% 44%; height: 100%; }
  .grid-rows-57-43 { display: grid; grid-template-rows: 57% 43%; height: 100%; }
  .grid-rows-58-42 { display: grid; grid-template-rows: 58% 42%; height: 100%; }
  .grid-rows-59-41 { display: grid; grid-template-rows: 59% 41%; height: 100%; }
  .grid-rows-60-40 { display: grid; grid-template-rows: 60% 40%; height: 100%; }
  .grid-rows-61-39 { display: grid; grid-template-rows: 61% 39%; height: 100%; }
  .grid-rows-62-38 { display: grid; grid-template-rows: 62% 38%; height: 100%; }
  .grid-rows-63-37 { display: grid; grid-template-rows: 63% 37%; height: 100%; }
  .grid-rows-64-36 { display: grid; grid-template-rows: 64% 36%; height: 100%; }
  .grid-rows-65-35 { display: grid; grid-template-rows: 65% 35%; height: 100%; }
  .grid-rows-66-34 { display: grid; grid-template-rows: 66% 34%; height: 100%; }
  .grid-rows-67-33 { display: grid; grid-template-rows: 67% 33%; height: 100%; }
  .grid-rows-68-32 { display: grid; grid-template-rows: 68% 32%; height: 100%; }
  .grid-rows-auto-1fr { display: grid; grid-template-rows: auto 1fr; height: 100%; }
---

<div class="slide-title bg-accent">
<div class="pad-col title-shell" style="text-align: center; align-items: center;">
  <h1 style="color: white; margin-bottom: 20px;">Building Artificial Intelligence for Humanity</h1>
  <div class="title-rule" style="width: 100px; height: 6px; background: white; margin: 30px 0;"></div>
  <p class='title-authors' style='font-size: 28px; opacity: 0.9; color: white;'>OpenAI</p>
  <p class='title-subtitle' style='font-size: 28px; opacity: 0.9; color: white;'>An Overview of Mission, Technology, and Impact</p>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 40px; margin-bottom: 20px;">Mission: Ensure AGI Benefits All of Humanity</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- Develop artificial general intelligence (AGI) to perform most economically valuable tasks better than humans.
- Ensure powerful AI is developed responsibly, deployed safely, and widely distributed.
- Make the advantages of advanced AI accessible to everyone.

</div>
</div>
</div>

---


<div class="slide-columns x-dense">

<div class="pad-col">
<h1 style="font-size: 36px; margin-bottom: 16px;">The Global Challenge: A Gap Between Information and Intelligence</h1>
<div class="card-grid" style="grid-template-columns: 1fr 1fr; grid-template-rows: auto auto;; gap:16px; align-content:start; margin-top:16px;">

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Limited Expertise</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

The internet expanded information access but didn't solve the problem of interpretation and reasoning.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Organizational Barriers</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Businesses struggle to analyze vast data, automate complex workflows, and scale knowledge.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Information Overload</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Extracting useful insights from the ever-growing volume of digital information is increasingly difficult.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Rigid Software</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Traditional tools solve narrow tasks but lack the ability to reason, adapt, and interact naturally with humans.

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 44px; margin-bottom: 20px;">Our Approach: General-Purpose AI Systems</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- Instead of narrow tools, we build foundation models applicable to countless domains.
- These models are scaled using massive datasets and compute resources.
- We enable powerful capabilities in reasoning, language understanding, and problem-solving through simple interfaces.

</div>
</div>
</div>

---


<div class="slide-method x-dense">

<div class="pad-col">
<h1 style="font-size: 44px; margin-bottom: 20px;">The OpenAI Platform Strategy</h1>
<div class="step-stack" style="grid-template-columns:1fr 1fr; gap:12px; align-content:start; margin-top:16px;">

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 1</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Frontier Foundation Models</span>
<div style="margin-top: 8px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Develop the core intelligence layer for language, images, audio, and other modalities.

</div>
</div>

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 2</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Developer Tools & APIs</span>
<div style="margin-top: 8px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Enable organizations to integrate advanced AI into their products and workflows.

</div>
</div>

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 3</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">User-Facing Products</span>
<div style="margin-top: 8px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Make AI accessible to individuals through natural, conversational interfaces.

</div>
</div>

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 4</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Alignment & Safety Research</span>
<div style="margin-top: 8px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Ensure that increasingly capable AI systems behave reliably and remain beneficial to humanity.

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-columns x-dense">

<div class="pad-col">
<h1 style="font-size: 44px; margin-bottom: 20px;">Core Technology Stack</h1>
<div class="card-grid" style="grid-template-columns: 1fr 1fr; grid-template-rows: auto auto;; gap:16px; align-content:start; margin-top:16px;">

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Large Language Models</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

The backbone of our system, trained to understand and generate text for complex tasks.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Multimodal Models</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Extend capabilities beyond text to process and generate images, audio, and video.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Reinforcement Learning</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Refines model behavior to align with human preferences, making them more helpful and safe.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Large-Scale Infrastructure</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Massive computational resources and specialized techniques to train frontier models efficiently.

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 40px; margin-bottom: 20px;">The Ecosystem Effect: A Foundation for Innovation</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- Our API platform allows developers to build their own AI-powered solutions.
- This approach enables our technology to scale rapidly across all industries.
- The ecosystem significantly expands the reach and impact of our core research.

</div>
</div>
</div>

---


<div class="slide-columns x-dense">

<div class="pad-col">
<h1 style="font-size: 44px; margin-bottom: 20px;">Applications Powered by the Ecosystem</h1>
<div class="card-grid" style="grid-template-columns: 1fr 1fr; grid-template-rows: auto auto;; gap:16px; align-content:start; margin-top:16px;">

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Enterprise Automation</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Powering customer support, document analysis, and software development assistants.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Creative Content</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Tools for generating novel text, images, and other creative media.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Personalized Education</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

AI tutors that adapt to individual learning styles and needs.

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Scientific Research</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

Accelerating discovery by analyzing complex medical and scientific data.

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 44px; margin-bottom: 20px;">A Trillion-Dollar Market Opportunity</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- The global AI market is projected to exceed $1 trillion in the coming decade.
- AI is becoming a foundational layer of the digital economy, similar to cloud computing.
- OpenAI operates at the intersection of research, infrastructure, enterprise, and consumer markets.

</div>
</div>
</div>

---


<div class="slide-split slide-split-full bg-dark x-dense">

<div class="pad-col" style="text-align:center; align-items:center;">
<h1 style="font-size: 40px; margin-bottom: 20px;">Societal Impact: Benefits and Responsibilities</h1>
<div class="hero-panel" style="background:rgba(255,255,255,0.1); padding:40px; border-radius:10px; text-align:left; margin-top:14px; width:100%; max-width:900px; --slide-fs:20px; --slide-lh:1.22; font-size:20px; line-height:1.22;" markdown="1">

- <strong>Democratizing Expertise:</strong> Making specialized knowledge in education and healthcare accessible to all.
- <strong>Productivity Gains:</strong> Automating routine tasks and enabling faster innovation cycles across industries.
- <strong>Managing Risks:</strong> Addressing potential misuse, economic disruption, and alignment challenges through responsible development.

</div>
</div>
</div>

---


<div class="slide-method x-dense">

<div class="pad-col">
<h1 style="font-size: 44px; margin-bottom: 20px;">Our Commitment to Safety and Alignment</h1>
<div class="step-stack" style="gap:12px; align-content:start; margin-top:16px;">

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 1</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Alignment Research</span>
<div style="margin-left: 48px; margin-top: 6px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Ensuring AI systems behave according to human intentions and values, using techniques like RLHF.

</div>
</div>

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 2</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Misuse Prevention</span>
<div style="margin-left: 48px; margin-top: 6px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Developing robust policies and monitoring systems to detect and prevent harmful use of our technology.

</div>
</div>

<div class="step-card" style="margin-bottom: 14px;">
<span style="font-size:14px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step 3</span>
<span style="font-size:19px; font-weight:700; line-height:1.15;">Industry Collaboration</span>
<div style="margin-left: 48px; margin-top: 6px; --slide-fs:16px; --slide-lh:1.16; font-size:16px; line-height:1.16; opacity:0.9;" markdown="1">

Working with policymakers, academics, and partners to establish standards for responsible AI deployment.

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 44px; margin-bottom: 20px;">Long-Term Vision: The Path to AGI</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- Our vision is the development of Artificial General Intelligence—systems that can perform most intellectual tasks humans can.
- AGI could help solve global challenges like climate change and disease.
- Achieving this requires careful planning, responsible governance, and broad collaboration to ensure shared benefits.

</div>
</div>
</div>

---


<div class="slide-end bg-dark">

<div class="pad-col">
<h1>Thank You</h1>

<div class="end-note" style="font-size: 27.0px; opacity: 0.8;" markdown="1">

<p>OpenAI's mission is to build advanced technology and ensure the future of artificial intelligence is aligned with the interests of humanity.</p>

</div>

</div>
</div>
