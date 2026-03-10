---
marp: true
theme: default
size: 16:9
paginate: true
math: katex
style: |
 

  :root {
    --accent:       #00D4FF;
    --accent-dim:   rgba(0, 212, 255, 0.15);
    --accent-gold:  #FFD166;
    --accent-gold-dim: rgba(255, 209, 102, 0.15);
    --dark:         #0A1628;
    --surface:      #0D1B2A;
    --text-main:    #E2EBF6;
    --text-soft:    #8BA5C0;
    --font-base:    26px;
    --font-head:    56px;
    --bg-header:    rgba(0, 212, 255, 0.08);
    --bg-row-even:  rgba(255, 255, 255, 0.03);
    --border-color: rgba(0, 212, 255, 0.15);
    --radius:       16px;
  }

  section {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0; font-size: var(--font-base); font-weight: 400;
    background:
      radial-gradient(ellipse at 85% 15%, rgba(0, 212, 255, 0.12) 0%, transparent 45%),
      radial-gradient(ellipse at 15% 85%, rgba(255, 209, 102, 0.10) 0%, transparent 45%),
      linear-gradient(145deg, #0A1628 0%, #0D1B2A 50%, #111F33 100%);
    display: flex; flex-direction: column; overflow: hidden; position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end { flex: 1; min-height: 0; }

  h1 { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; font-weight: 700; font-size: var(--font-head); letter-spacing: -1.5px; color: #F0F7FF; margin: 0 0 22px 0; line-height: 1.06; }
  h3 { font-size: 12px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 5px; margin: 0 0 16px 0; }
  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.42); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(255, 209, 102, 0.25); padding: 1px 5px; border-radius: 3px; color: var(--accent-gold); }

  ul { padding: 0; margin: 0; list-style: none !important; }
  li { line-height: var(--slide-lh, 1.38); margin-bottom: 11px; padding-left: 22px; position: relative; font-size: var(--slide-fs, inherit); color: var(--text-main); }
  li::before { content: ""; position: absolute; left: 0; top: 0.58em; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 6px rgba(0, 212, 255, 0.50); }
  li:nth-child(2)::before { background: var(--accent-gold); box-shadow: 0 0 6px rgba(255,209,102,0.40); }
  li:nth-child(3)::before { background: #A78BFA; box-shadow: 0 0 6px rgba(167,139,250,0.40); }
  li:nth-child(4)::before { background: #34D399; box-shadow: 0 0 6px rgba(52,211,153,0.40); }

  .img-col { display: flex; align-items: center; justify-content: center; width: 100%; overflow: hidden; position: relative; }
  .img-col img { display: block; max-width: calc(100% - 2px); max-height: calc(100% - 2px); width: auto; height: auto; object-fit: contain; padding: 16px; box-sizing: border-box; }

  .table-clean { width: auto; margin: 0 auto; }
  .table-clean th, .table-clean td { text-align: center; }

  .grid-50-50 { display: grid; grid-template-columns: 1fr 1fr; }
  .grid-40-60 { display: grid; grid-template-columns: 40% 60%; }
  .grid-60-40 { display: grid; grid-template-columns: 60% 40%; }
  .grid-30-70 { display: grid; grid-template-columns: 30% 70%; }
  .grid-35-65 { display: grid; grid-template-columns: 35% 65%; }
  .grid-50-50 table { font-size: 16px; } .grid-35-65 table { font-size: 12px; }
  .grid-40-60 table { font-size: 14px; } .grid-60-40 table { font-size: 16px; }
  .grid-30-70 table { font-size: 11px; }

  .pad-col { padding: 44px 50px; display: flex; flex-direction: column; justify-content: flex-start; height: 100%; min-width: 0; min-height: 0; overflow: hidden; box-sizing: border-box; }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  .card-grid { display: grid; gap: 18px; margin-top: 16px; align-content: start; }
  .feature-card { background: rgba(255,255,255,0.04); padding: 20px 24px; border: 1px solid var(--border-color); border-left: 4px solid var(--accent); border-radius: var(--radius); box-shadow: 0 4px 20px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.05); position: relative; overflow: hidden; }
  .card-grid .feature-card:nth-child(2) { border-left-color: var(--accent-gold); }
  .card-grid .feature-card:nth-child(3) { border-left-color: #A78BFA; }
  .card-grid .feature-card:nth-child(4) { border-left-color: #34D399; }

  .bg-dark { background: radial-gradient(ellipse at 20% 15%, rgba(0,212,255,0.10) 0%, transparent 50%), linear-gradient(150deg, #081422 0%, #0A1628 100%) !important; color: var(--text-main) !important; }
  .bg-dark h1 { color: #F0F7FF !important; }
  .bg-dark p, .bg-dark li { color: var(--text-main) !important; }
  .bg-dark strong { color: var(--accent) !important; }

  .bg-accent { background: linear-gradient(135deg, #0A1628 0%, #003B5C 40%, #00D4FF 100%) !important; color: #FFFFFF !important; }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFFFFF !important; }
  .bg-accent strong { color: var(--accent-gold) !important; }
  .bg-accent h3 { color: rgba(255,255,255,0.65) !important; }

  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 68px; line-height: 1.02; max-width: 18ch; letter-spacing: -2px; text-shadow: 0 0 40px rgba(0,212,255,0.30); }
  .title-rule { width: 100px !important; height: 4px !important; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-gold)) !important; box-shadow: 0 0 12px rgba(0,212,255,0.40); }
  .title-authors  { font-size: 24px !important; font-weight: 500; opacity: 0.88; }
  .title-subtitle { font-size: 16px !important; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; opacity: 0.65; }

  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 84px !important; letter-spacing: -3px; margin-bottom: 20px; text-shadow: 0 0 50px rgba(0,212,255,0.25); }
  .slide-end .end-note { background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: var(--radius); padding: 22px 28px; max-width: 900px; margin: 0 auto; text-align: left; }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child { background: linear-gradient(160deg, #0F2035 0%, #122338 60%, #152A40 100%); }

  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card { background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-left: 4px solid var(--accent); border-radius: 4px 14px 14px 4px; padding: 14px 18px; box-shadow: 0 2px 10px rgba(0,0,0,0.30); }

  .slide-hero .hero-panel, .slide-split .hero-panel { background: rgba(255,255,255,0.04); border: 1px solid var(--border-color); border-radius: 16px; padding: 22px 26px !important; }
  .slide-hero.slide-hero-full .hero-panel { padding: 26px 34px !important; border-left: 5px solid var(--accent) !important; border-radius: 0 16px 16px 0 !important; background: rgba(0,212,255,0.07) !important; }
  .slide-hero.slide-hero-full .hero-panel p, .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.45 !important; font-weight: 500; color: rgba(255,255,255,0.93); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  table { width: 100%; max-width: 100%; table-layout: fixed; border-collapse: collapse; margin-top: 18px; font-size: 16px; background: transparent; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 4px 24px rgba(0,0,0,0.40); }
  th { text-align: left; padding: 10px 14px; color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.80em; background: rgba(0,212,255,0.08); border-bottom: 2px solid rgba(0,212,255,0.20); overflow-wrap: anywhere; word-break: break-word; }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(255,255,255,0.05); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }
  .slide-results .pad-col:last-child { background: rgba(255,255,255,0.03); border-left: 1px solid var(--border-color); }

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
  <h1 style="color: white; margin-bottom: 20px;">Attention Is All You Need</h1>
  <div class="title-rule" style="width: 100px; height: 6px; background: white; margin: 30px 0;"></div>
  <p class='title-authors' style='font-size: 28px; opacity: 0.9; color: white;'>Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin</p>
  <p class='title-subtitle' style='font-size: 28px; opacity: 0.9; color: white;'>Google Brain, Google Research, University of Toronto</p>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark x-dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 44px; margin-bottom: 20px;">The Challenge of Sequential Models</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:20px; --slide-lh:1.22; font-size:20px; line-height:1.22;" markdown="1">

- Dominant models like RNNs and LSTMs are inherently sequential, processing data token-by-token.
- This sequential nature ($h_t$ depends on $h_{t-1}$) prevents parallelization within examples.
- Learning long-range dependencies is a key challenge due to long signal paths and vanishing gradients.
- Memory constraints limit batching across examples for long sequences.

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-full bg-dark dense">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="font-size: 44px; margin-bottom: 20px;">A New Architecture: The Transformer</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: 14px; --slide-fs:20px; --slide-lh:1.22; font-size:20px; line-height:1.22;" markdown="1">

- We propose a network architecture based solely on attention mechanisms.
- It dispenses with recurrence and convolutions entirely.
- This design allows for significantly more parallelization, reducing training time.
- Achieves state-of-the-art translation quality while requiring less time to train.

</div>
</div>
</div>

---


<div class="slide-split slide-split-image x-dense">

<div class="grid-52-48 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 8px 34px 30px;">
<h1 style="font-size: 30px; margin-bottom: 18px;">High-Level Architecture</h1>
<div style="--slide-fs:18.0px; --slide-lh:1.30; font-size:18.0px; line-height:1.30;" markdown="1">

- The Transformer follows a standard encoder-decoder structure.
- <b>Encoder:</b> Maps an input sequence of symbols to a sequence of continuous representations.
- <b>Decoder:</b> Generates an output sequence one symbol at a time, consuming previously generated symbols.
- Both components use stacked self-attention and point-wise, fully connected layers.

</div>
</div>
<div class="img-col" style="min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:8px 12px 12px 12px;">
<div style="width:92%; max-width:92%; height:100%; display:flex; align-items:center; justify-content:center; padding:0 5px; box-sizing:border-box; overflow:hidden; margin:0 auto;"><img src="./_page_2_Figure_0.jpeg" /></div>
</div>
</div>
</div>

---


<div class="slide-split slide-split-image dense">

<div class="grid-68-32 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 16px 34px 34px;">
<h1 style="font-size: 38px; margin-bottom: 20px;">The Core Mechanism: Attention</h1>
<div style="--slide-fs:21.2px; --slide-lh:1.33; font-size:21.2px; line-height:1.33;" markdown="1">

- An attention function maps a query and a set of key-value pairs to an output.
- The output is a weighted sum of the values, where weights are computed based on query-key compatibility.
- We use a specific implementation called Scaled Dot-Product Attention.

</div>
</div>
<div class="img-col" style="min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 12px 10px 12px;">
<div style="width:80%; max-width:80%; height:100%; display:flex; align-items:center; justify-content:center; padding:0 8px; box-sizing:border-box; overflow:hidden; margin:0 auto;"><img src="./_page_3_Figure_1.jpeg" /></div>
</div>
</div>
</div>

---


<div class="slide-hero slide-hero-equation bg-dark">

<div class="grid-rows-auto-1fr">
<div class="pad-col hero-copy" style="justify-content: center; align-items: flex-start; padding-bottom: 0;">
  <h1 style="margin-bottom: 20px; font-size: 44px; margin-bottom: 20px;">Scaled Dot-Product Attention</h1>
  <div style="opacity: 0.9; --slide-fs:20px; --slide-lh:1.22; font-size:20px; line-height:1.22;" markdown="1">

- Input consists of queries (Q), keys (K) of dimension $d_k$, and values (V) of dimension $d_v$.
- Dot products of the query with all keys are computed, then scaled by $\frac{1}{\sqrt{d_k}}$.
- Scaling prevents the softmax function from entering regions with small gradients, stabilizing training.
- A softmax is applied to obtain weights on the values.

  </div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: rgba(255,255,255,0.05);">

<div style="width: 100%; display: flex; align-items: center; justify-content: center; margin: auto 0;">
<div style="transform: scale(1.3); transform-origin: center center; width: 100%; text-align: center; margin: 0;" markdown="1">

$$
Attention(Q, K, V) = softmax(\frac{QK^{T}}{\sqrt{d_k}})V
$$

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-split slide-split-image x-dense">

<div class="grid-52-48 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 8px 34px 30px;">
<h1 style="font-size: 30px; margin-bottom: 18px;">Multi-Head Attention</h1>
<div style="--slide-fs:18.0px; --slide-lh:1.30; font-size:18.0px; line-height:1.30;" markdown="1">

- Instead of a single attention function, we use multiple attention 'heads' in parallel.
- Queries, keys, and values are linearly projected $h$ times with different learned projections.
- This allows the model to jointly attend to information from different representation subspaces at different positions.
- Outputs from each head are concatenated and projected to form the final result.

</div>
</div>
<div class="img-col" style="min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:8px 12px 12px 12px;">
<div style="width:92%; max-width:92%; height:100%; display:flex; align-items:center; justify-content:center; padding:0 5px; box-sizing:border-box; overflow:hidden; margin:0 auto;"><img src="./_page_3_Picture_2.jpeg" /></div>
</div>
</div>
</div>

---


<div class="slide-hero slide-hero-equation bg-dark">

<div class="grid-rows-auto-1fr">
<div class="pad-col hero-copy" style="justify-content: center; align-items: flex-start; padding-bottom: 0;">
  <h1 style="margin-bottom: 20px; font-size: 44px; margin-bottom: 20px;">Multi-Head Attention in Detail</h1>
  <div style="opacity: 0.9; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- We use $h=8$ parallel attention heads.
- For each head, we use reduced key, value, and query dimensions: $d_k = d_v = d_{model}/h = 64$.
- The total computational cost is similar to single-head attention with full dimensionality.

  </div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: rgba(255,255,255,0.05);">

<div style="width: 100%; display: flex; align-items: center; justify-content: center; margin: auto 0;">
<div style="transform: scale(1.05); transform-origin: center center; width: 100%; text-align: center; margin: 0;" markdown="1">

$$
\begin{aligned} \text{MultiHead}(Q, K, V) &= \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O \\ \text{where head}_i &= \text{Attention}(QW_i^Q, KW_i^K, VW_i^V) \end{aligned}
$$

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-columns x-dense">

<div class="pad-col">
<h1 style="font-size: 44px; margin-bottom: 20px;">Layer Structure</h1>
<div class="card-grid" style="grid-template-columns: 1fr 1fr;; gap:16px; align-content:start; margin-top:16px;">

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Encoder Layer</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

<ul>
<li>Composed of two sub-layers:</li>
</ul>
<div markdown="1" style="margin: -2px 0 10px 34px; line-height: 1.22;">
i. Multi-Head Self-Attention<br>
ii. Position-wise Feed-Forward Network
</div>
<ul>
<li>Residual connections and Layer Normalization are applied around each sub-layer.</li>
</ul>

</div>
</div>

<div class="feature-card">
<div style="color:var(--accent); font-weight:700; font-size:20px; margin-bottom:5px; line-height:1.18;">Decoder Layer</div>
<div style="--slide-fs:18px; --slide-lh:1.18; font-size:18px; line-height:1.18; opacity:0.82;" markdown="1">

<ul>
<li>Composed of three sub-layers:</li>
</ul>
<div markdown="1" style="margin: -2px 0 10px 34px; line-height: 1.22;">
i. Masked Multi-Head Self-Attention<br>
ii. Encoder-Decoder Attention<br>
iii. Position-wise Feed-Forward Network
</div>
<ul>
<li>Masking in the self-attention layer preserves the auto-regressive property.</li>
</ul>

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-hero slide-hero-equation bg-dark">

<div class="grid-rows-auto-1fr">
<div class="pad-col hero-copy" style="justify-content: center; align-items: flex-start; padding-bottom: 0;">
  <h1 style="margin-bottom: 20px; font-size: 44px; margin-bottom: 20px;">Positional Encoding</h1>
  <div style="opacity: 0.9; --slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;" markdown="1">

- Since the model contains no recurrence or convolution, we must inject information about token position.
- We add 'positional encodings' to the input embeddings at the bottom of the encoder and decoder stacks.
- We use sine and cosine functions of different frequencies.

  </div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: rgba(255,255,255,0.05);">

<div style="width: 100%; display: flex; align-items: center; justify-content: center; margin: auto 0;">
<div style="transform: scale(1.05); transform-origin: center center; width: 100%; text-align: center; margin: 0;" markdown="1">

$$
\begin{aligned} PE_{(pos,2i)} &= \sin(pos/10000^{2i/d_{\rm model}}) \\ PE_{(pos,2i+1)} &= \cos(pos/10000^{2i/d_{\rm model}}) \end{aligned}
$$

</div>
</div>

</div>
</div>
</div>

---


<div class="slide-results x-dense">

<div class="grid-38-62 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 8px 34px 30px;">
<h1 style="font-size: 26px; margin-bottom: 16px;">Why Self-Attention?</h1>
<div style="margin-top: 20px; --slide-fs:16.0px; --slide-lh:1.30; font-size:16.0px; line-height:1.30;" markdown="1">

- Self-attention layers offer advantages in computational complexity, parallelization, and learning long-range dependencies.
- The path length between any two positions is constant ($O(1)$), unlike in recurrent ($O(n)$) or convolutional ($O(\log_k(n))$) layers.

</div>
</div>

<div class="pad-col" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding-right:32px; min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 14px 10px 4px;">
<div style="width:100%; max-width:95%; overflow:auto; display:flex; justify-content:center; align-items:center;">
<table class="table-clean" style="width: auto; max-width: 100%; border-collapse: collapse; font-size: 14px; margin: 10px auto 0 auto; box-sizing: border-box;">
  <thead>
    <tr style="background-color: var(--bg-header); border-bottom: 2px solid var(--accent);">
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Layer Type</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Complexity per Layer</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Sequential Operations</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Maximum Path Length</th>
    </tr>
  </thead>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Self-Attention</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(n<sup>2</sup> &middot; d)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(1)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(1)</p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Recurrent</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(n &middot; d<sup>2</sup>)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(n)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(n)</p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Convolutional</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(k &middot; n &middot; d<sup>2</sup>)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(1)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(log<sub>k</sub>(n))</p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Self-Attention (restricted)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(r &middot; n &middot; d)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(1)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>O(n/r)</p></td>
    </tr>
  </tbody>
</table>
</div>
</div>
</div>
</div>

---


<div class="slide-results x-dense">

<div class="grid-38-62 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 8px 34px 30px;">
<h1 style="font-size: 24px; margin-bottom: 16px;">State-of-the-Art Machine Translation</h1>
<div style="margin-top: 20px; --slide-fs:15.8px; --slide-lh:1.30; font-size:15.8px; line-height:1.30;" markdown="1">

- The Transformer outperforms the best previously reported models on WMT 2014 translation tasks.
- The big model establishes a new SOTA BLEU score of 28.4 on English-to-German.
- This performance is achieved at a fraction of the training cost of competing models.

</div>
</div>

<div class="pad-col" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding-right:32px; min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 14px 10px 4px;">
<div style="width:100%; max-width:95%; overflow:auto; display:flex; justify-content:center; align-items:center;">
<table class="table-clean" style="width: auto; max-width: 100%; border-collapse: collapse; font-size: 14px; margin: 10px auto 0 auto; box-sizing: border-box;">
  <thead>
    <tr style="background-color: var(--bg-header); border-bottom: 2px solid var(--accent);">
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Model</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">BLEU (EN-DE)</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">BLEU (EN-FR)</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Training Cost (FLOPs)</th>
    </tr>
  </thead>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>GNMT + RL [38]</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>24.6</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>39.92</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>2.3 &times; 10<sup>19</sup></p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>ConvS2S [9]</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>25.16</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>40.46</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>9.6 &times; 10<sup>18</sup></p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>GNMT + RL Ensemble [38]</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>26.30</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>41.16</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>1.8 &times; 10<sup>20</sup></p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>Transformer (base)</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>27.3</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>38.1</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>3.3 &times; 10<sup>18</sup></strong></p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>Transformer (big)</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>28.4</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>41.8</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>2.3 &times; 10<sup>19</sup></strong></p></td>
    </tr>
  </tbody>
</table>
</div>
</div>
</div>
</div>

---


<div class="slide-results x-dense">

<div class="grid-56-44 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 12px 34px 30px;">
<h1 style="font-size: 34px; margin-bottom: 18px;">Ablation Studies</h1>
<div style="margin-top: 20px; --slide-fs:18.2px; --slide-lh:1.32; font-size:18.2px; line-height:1.32;" markdown="1">

- We varied components to measure their importance on English-to-German translation.
- (A) 8 attention heads were found to be optimal.
- (D) Dropout is very helpful in avoiding over-fitting.
- (E) Sinusoidal positional encodings perform nearly identically to learned embeddings.

</div>
</div>

<div class="pad-col" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding-right:32px; min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 14px 10px 4px;">
<div style="width:100%; max-width:95%; overflow:auto; display:flex; justify-content:center; align-items:center;">
<table class="table-clean" style="width: auto; max-width: 100%; border-collapse: collapse; font-size: 16px; margin: 10px auto 0 auto; box-sizing: border-box;">
  <thead>
    <tr style="background-color: var(--bg-header); border-bottom: 2px solid var(--accent);">
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Variation</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">PPL (dev)</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">BLEU (dev)</th>
    </tr>
  </thead>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>base (h=8)</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>4.92</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>25.8</strong></p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>(A) h=1</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>5.29</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>24.9</p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>(A) h=16</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>4.91</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>25.8</p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>(D) P<sub>drop</sub>=0.0</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>5.77</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>24.6</p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>(E) Learned Positional Embedding</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>4.92</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>25.7</p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>big</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>4.33</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>26.4</strong></p></td>
    </tr>
  </tbody>
</table>
</div>
</div>
</div>
</div>

---


<div class="slide-results x-dense">

<div class="grid-56-44 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 12px 34px 30px;">
<h1 style="font-size: 32px; margin-bottom: 18px;">Generalizing to Other Tasks: Parsing</h1>
<div style="margin-top: 20px; --slide-fs:18.3px; --slide-lh:1.32; font-size:18.3px; line-height:1.32;" markdown="1">

- To test generalization, we applied the Transformer to English constituency parsing.
- The model performs surprisingly well with minimal task-specific tuning.
- It outperforms the BerkeleyParser even when trained only on the small 40K sentence WSJ dataset.

</div>
</div>

<div class="pad-col" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding-right:32px; min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 14px 10px 4px;">
<div style="width:100%; max-width:95%; overflow:auto; display:flex; justify-content:center; align-items:center;">
<table class="table-clean" style="width: auto; max-width: 100%; border-collapse: collapse; font-size: 16px; margin: 10px auto 0 auto; box-sizing: border-box;">
  <thead>
    <tr style="background-color: var(--bg-header); border-bottom: 2px solid var(--accent);">
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Parser</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">Training Setting</th>
      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">WSJ 23 F1 Score</th>
    </tr>
  </thead>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Recurrent Neural Network Grammar</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>generative</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>93.3</p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Vinyals &amp; Kaiser et al. (2015)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>semi-supervised</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>92.1</p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>Transformer (4 layers)</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>semi-supervised</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>92.7</strong></p></td>
    </tr>
    <tr >
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>Dyer et al. (2016)</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>WSJ only</p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p>91.7</p></td>
    </tr>
    <tr style="background-color: var(--bg-row-even);">
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>Transformer (4 layers)</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>WSJ only</strong></p></td>
      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;"><p><strong>91.3</strong></p></td>
    </tr>
  </tbody>
</table>
</div>
</div>
</div>
</div>

---


<div class="slide-split slide-split-image dense">

<div class="grid-48-52 split-gap" style="height:720px;">
<div class="pad-col" style="min-width:0; min-height:0; overflow:hidden; padding:36px 8px 34px 30px;">
<h1 style="font-size: 26px; margin-bottom: 16px;">Visualizing Attention</h1>
<div style="--slide-fs:18.4px; --slide-lh:1.31; font-size:18.4px; line-height:1.31;" markdown="1">

- Self-attention mechanisms can lead to more interpretable models.
- We can inspect attention distributions to see how the model represents syntactic and semantic structures.
- Different attention heads learn to perform different tasks, such as tracking long-distance dependencies or resolving anaphora.

</div>
</div>
<div class="img-col" style="min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:8px 12px 12px 12px;">
<div style="width:92%; max-width:92%; height:100%; display:flex; align-items:center; justify-content:center; padding:0 5px; box-sizing:border-box; overflow:hidden; margin:0 auto;"><img src="./_page_12_Figure_1.jpeg" /></div>
</div>
</div>
</div>

---


<div class="slide-end bg-dark">

<div class="pad-col">
<h1>Conclusion</h1>

<div class="end-note" style="font-size: 27.0px; opacity: 0.8;" markdown="1">

<ul>
<li>We presented the Transformer, the first sequence transduction model based entirely on attention.</li>
<li>It trains significantly faster and achieves a new state of the art on machine translation tasks.</li>
<li>We are excited about the future of attention-based models and plan to apply them to other tasks and modalities.</li>
</ul>

</div>

</div>
</div>
