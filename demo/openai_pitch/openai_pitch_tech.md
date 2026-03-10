---
marp: true
theme: default
size: 16:9
paginate: true
math: katex
style: |
 

  :root {
    --accent:       #2563EB;
    --accent-light: rgba(37, 99, 235, 0.12);
    --accent-sky:   #0EA5E9;
    --accent-indigo:#6366F1;
    --accent-green: #10B981;
    --dark:         #0A0F1E;
    --text-main:    #0F172A;
    --text-soft:    #475569;
    --font-base:    26px;
    --font-head:    56px;
    --bg-header:    rgba(37, 99, 235, 0.07);
    --bg-row-even:  rgba(37, 99, 235, 0.03);
    --border-color: rgba(37, 99, 235, 0.14);
    --radius:       12px;
  }

  section {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 90% 8%, rgba(14, 165, 233, 0.14) 0%, transparent 44%),
      radial-gradient(ellipse at 8% 92%, rgba(99, 102, 241, 0.11) 0%, transparent 44%),
      linear-gradient(150deg, #F8FAFF 0%, #F0F5FF 55%, #EBF2FF 100%);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end {
    flex: 1; min-height: 0;
  }

  /* TYPOGRAPHY */
  h1 {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    font-weight: 700;
    font-size: var(--font-head);
    letter-spacing: -2px;
    color: var(--dark);
    margin: 0 0 22px 0;
    line-height: 1.05;
  }

  h3 {
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 6px;
    margin: 0 0 16px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.42); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(37, 99, 235, 0.14); padding: 1px 6px; border-radius: 4px; color: var(--accent); font-weight: 500; }

  /* LISTS */
  ul { padding: 0; margin: 0; list-style: none !important; }

  li {
    line-height: var(--slide-lh, 1.38);
    margin-bottom: 11px;
    padding-left: 22px;
    position: relative;
    font-size: var(--slide-fs, inherit);
  }

  li::before {
    content: "";
    position: absolute;
    left: 0; top: 0.58em;
    width: 7px; height: 7px;
    border-radius: 2px;
    background: var(--accent);
  }
  li:nth-child(2)::before { background: var(--accent-sky); }
  li:nth-child(3)::before { background: var(--accent-indigo); }
  li:nth-child(4)::before { background: var(--accent-green); }

  /* IMAGES */
  .img-col { display: flex; align-items: center; justify-content: center; width: 100%; overflow: hidden; position: relative; }
  .img-col img { display: block; max-width: calc(100% - 2px); max-height: calc(100% - 2px); width: auto; height: auto; object-fit: contain; padding: 16px; box-sizing: border-box; }

  /* TABLE */
  .table-clean { width: auto; margin: 0 auto; }
  .table-clean th, .table-clean td { text-align: center; }

  /* GRIDS */
  .grid-50-50 { display: grid; grid-template-columns: 1fr 1fr; }
  .grid-40-60 { display: grid; grid-template-columns: 40% 60%; }
  .grid-60-40 { display: grid; grid-template-columns: 60% 40%; }
  .grid-30-70 { display: grid; grid-template-columns: 30% 70%; }
  .grid-35-65 { display: grid; grid-template-columns: 35% 65%; }
  .grid-50-50 table { font-size: 16px; } .grid-35-65 table { font-size: 12px; }
  .grid-40-60 table { font-size: 14px; } .grid-60-40 table { font-size: 16px; }
  .grid-30-70 table { font-size: 11px; }

  .pad-col {
    padding: 44px 50px; display: flex; flex-direction: column;
    justify-content: flex-start; height: 100%; min-width: 0; min-height: 0;
    overflow: hidden; box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  /* CARDS */
  .card-grid { display: grid; gap: 16px; margin-top: 16px; align-content: start; }

  .feature-card {
    background: #FFFFFF;
    padding: 20px 24px;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    box-shadow: 0 2px 12px rgba(37, 99, 235, 0.08), 0 1px 3px rgba(0,0,0,0.04);
    position: relative; overflow: hidden;
  }
  .feature-card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: var(--accent);
    border-radius: 12px 0 0 12px;
  }
  .card-grid .feature-card:nth-child(2)::before { background: var(--accent-sky); }
  .card-grid .feature-card:nth-child(3)::before { background: var(--accent-indigo); }
  .card-grid .feature-card:nth-child(4)::before { background: var(--accent-green); }

  /* DARK SLIDES */
  .bg-dark {
    background:
      radial-gradient(ellipse at 15% 15%, rgba(37, 99, 235, 0.22) 0%, transparent 50%),
      radial-gradient(ellipse at 85% 85%, rgba(14, 165, 233, 0.14) 0%, transparent 50%),
      linear-gradient(145deg, #050D1F 0%, #091328 50%, #0A1830 100%) !important;
    color: #E2EEFF !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #E2EEFF !important; }
  .bg-dark strong { color: #60A5FA !important; }
  .bg-dark h3 { color: rgba(96, 165, 250, 0.80) !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 10% 10%, rgba(255,255,255,0.15) 0%, transparent 45%),
      linear-gradient(135deg, #1D4ED8 0%, #2563EB 40%, #0EA5E9 100%) !important;
    color: #FFFFFF !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFFFFF !important; }
  .bg-accent h3 { color: rgba(255,255,255,0.68) !important; }

  /* TITLE SLIDE */
  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 68px; line-height: 1.02; max-width: 18ch; letter-spacing: -2px; }
  .title-rule { width: 80px !important; height: 4px !important; border-radius: 999px; background: rgba(255,255,255,0.70) !important; }
  .title-authors  { font-size: 24px !important; font-weight: 500; opacity: 0.90; }
  .title-subtitle { font-size: 15px !important; font-weight: 700; letter-spacing: 0.24em; text-transform: uppercase; opacity: 0.68; }

  /* END SLIDE */
  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 84px !important; letter-spacing: -3px; margin-bottom: 20px; }
  .slide-end .end-note {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius); padding: 22px 28px;
    max-width: 900px; margin: 0 auto; text-align: left;
  }

  /* SPLIT TEXT COLUMN */
  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #E0EBFF 0%, #E8F0FF 60%, #EEF3FF 100%);
  }

  /* STEP CARDS */
  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card {
    background: rgba(255, 255, 255, 0.92); border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent); border-radius: 4px 12px 12px 4px;
    padding: 14px 18px; box-shadow: 0 2px 8px rgba(37, 99, 235, 0.08);
  }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  /* HERO PANEL */
  .slide-hero .hero-panel,
  .slide-split .hero-panel {
    background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px; padding: 22px 26px !important;
  }
  .slide-hero.slide-hero-full .hero-panel {
    padding: 26px 34px !important; border-left: 5px solid var(--accent-sky) !important;
    border-radius: 0 14px 14px 0 !important;
    background: rgba(37, 99, 235, 0.12) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.45 !important; font-weight: 500; color: rgba(255,255,255,0.93); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  /* TABLES */
  table {
    width: 100%; max-width: 100%; table-layout: fixed;
    border-collapse: collapse; margin-top: 18px; font-size: 16px;
    background: transparent; border-radius: 12px; overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 16px rgba(37, 99, 235, 0.10);
  }
  th {
    text-align: left; padding: 10px 14px; color: var(--accent); font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.80em;
    background: rgba(37, 99, 235, 0.06); border-bottom: 2px solid rgba(37, 99, 235, 0.18);
    overflow-wrap: anywhere; word-break: break-word;
  }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(37, 99, 235, 0.06); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }

  .slide-results .pad-col:last-child { background: rgba(224, 235, 255, 0.60); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }

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
