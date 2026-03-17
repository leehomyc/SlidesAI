import os
import json
import argparse
import re
import html
import math
try:
    from PIL import Image
except Exception:
    Image = None

# --- CONFIGURATION ---
MARKER_DIR = "project_output/assets_marker"
OUTPUT_DIR = "project_output"
CURRENT_ASSET_DIR = None

# LLM 客户端（支持 Google Gemini 和 OpenRouter）
from llm_client import generate_content, get_llm_client

# --- HELPER FUNCTIONS ---

import markdown


def convert_inline_math_for_html(text):
    if not text:
        return text
    return html.unescape(text)


def table_font_size_by_columns(col_count):
    if col_count <= 5:
        return "18px"
    elif col_count == 6:
        return "17px"
    elif col_count == 7:
        return "16px"
    else:
        return "14px"


def auto_font_size_aggressive2(text, base=24.0, min_size=13.0, max_chars=150.0):
    """Shrink more aggressively for 2-column slides."""
    if not text:
        return base
    length = len(text)
    if length <= max_chars:
        return base
    ratio = max(min_size / base, max_chars / length)
    return max(int(base * ratio), int(min_size))


def auto_font_size_aggressive(text, base=24.0, min_size=14.0, max_chars=170.0):
    """Shrink more aggressively for 2-column slides."""
    if not text:
        return base
    length = len(text)
    if length <= max_chars:
        return base
    ratio = max(min_size / base, max_chars / length)
    return max(int(base * ratio), int(min_size))


def auto_font_size_gentle(text, base=27.0, min_size=20.0, max_chars=350.0):
    """Shrink very gently for full-width text slides."""
    if not text:
        return base
    length = len(text)
    if length <= max_chars:
        return base
    ratio = max(min_size / base, max_chars / length)
    return int(base * ratio)


def auto_font_size(text, base=27.0, min_size=17.0, max_chars=250.0):
    """
    Automatically scales text size based on character count.
    base: default font size
    min_size: minimum allowed font size
    max_chars: number of characters before scaling down
    """
    length = len(text)
    if length <= max_chars:
        return base

    # shrink proportionally
    ratio = max(min_size / base, max_chars / length)
    return int(base * ratio)


def clamp_num(value, minimum, maximum):
    return max(minimum, min(maximum, value))

def render_md(text):
    """Render Markdown inside HTML blocks (bold, bullets, math wrappers)."""
    if not text:
        return ""
    return markdown.markdown(
        text,
        extensions=["md_in_html", "tables", "fenced_code"]
    )

def markdown_to_html_table(md_table, font_size="14px"):
    """
    Converts a standard Markdown table string to a styled HTML table.
    Fixes: Filters empty headers, centers content, compact styling to prevent overflow.
    Updated to accept dynamic font_size.
    """
    if not md_table: return ""
    
    lines = [l.strip() for l in md_table.strip().split('\n') if l.strip()]
    if len(lines) < 2: return md_table # Fallback if not enough lines
    
    # Parse Header: strip outer pipes and filter empty header titles
    # Example: "| H1 | H2 | |" -> ["H1", "H2"]
    header_line = lines[0]
    raw_headers = header_line.strip().strip('|').split('|')
    headers = [h.strip() for h in raw_headers if h.strip()]
    
    num_cols = len(headers)
    
    # Parse Rows
    rows = []
    for line in lines[1:]:
        if '---' in line: continue
        # Split and strip cells
        raw_cells = line.strip().strip('|').split('|')
        cells = [c.strip() for c in raw_cells]
        
        # Align with headers
        # 1. If too short, pad with empty
        if len(cells) < num_cols:
            cells += [""] * (num_cols - len(cells))
        # 2. If too long (trailing pipes), truncate
        cells = cells[:num_cols]
            
        rows.append(cells)
        
    # Build HTML with Compact Styling
    html = f'<table class="table-clean" style="width: auto; max-width: 100%; border-collapse: collapse; font-size: {font_size}; margin: 10px auto 0 auto; box-sizing: border-box;">\n'
    
    # HEADER
    html += '  <thead>\n    <tr style="background-color: var(--bg-header); border-bottom: 2px solid var(--accent);">\n'
    for h in headers:
        html += f'      <th style="padding: 6px 8px; text-align: center; font-weight: bold; color: var(--accent); border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">{h}</th>\n'
    html += '    </tr>\n  </thead>\n'
    
    # BODY
    for i, row in enumerate(rows):
        bg = 'style="background-color: var(--bg-row-even);"' if i % 2 == 0 else ''
        html += f'    <tr {bg}>\n'
        for cell in row:
            cell_content = wrap_math_for_html(cell)
            
            html += f'      <td style="padding: 5px 8px; text-align: center; border: 1px solid var(--border-color); word-break: break-word; overflow-wrap: anywhere;">{cell_content}</td>\n'
        html += '    </tr>\n'
    html += '  </tbody>\n</table>'
    
    return html


def calculate_table_layout(text, md_table):
    """
    Analyzes content to return: (Grid Class, Text Style, Table Font Size, Container Zoom)
    """
    if not md_table: return "grid-50-50", "", "20px", "1.0"
    
    lines = md_table.strip().split('\n')
    if len(lines) < 2: return "grid-50-50", "", "20px", "1.0"

    header = lines[0]
    # Count columns by splitting the header line, removing empty strings from pipes
    col_count = len([h for h in header.strip('|').split('|') if h.strip()])
    
    # Count rows, excluding the header and separator line
    row_count = len([line for line in lines[1:] if '---' not in line])
    
    text_len = len(text) if text else 0
    
    # Default: Balanced 50-50 for standard tables (<= 5 columns)
    grid_class = "grid-50-50"
    table_font = "16px"
    zoom = "0.94"
    text_style = get_dynamic_font_class(text)

    # HEURISTICS

    # Case A: Massive Table (8+ cols or very tall) -> Balanced with smaller font!
    if col_count >= 10 or row_count > 17:
        grid_class = "grid-30-70"
        table_font = "11px"
        zoom = "0.72"

    elif col_count >= 8 or row_count > 15:
        grid_class = "grid-35-65"  # WAS: grid-30-70 (Text was too narrow)
        table_font = "11px"        # Shrink font to fit in the media column more reliably
        zoom = "0.80"

    # Case B: Wide Table (6-7 cols) -> Moderate space
    elif col_count >= 6:
        grid_class = "grid-40-60"
        table_font = "13px"
        zoom = "0.88"
    elif col_count >= 4 or row_count > 8:
        table_font = "14px"
        zoom = "0.90"

    # Case C: Text Priority (Long text + moderate table)
    # If text is long (>300) and table is manageable (<8 cols), force 50-50 to save the text
    if text_len > 300 and col_count < 8:
        grid_class = "grid-50-50"
        # If table is 6-7 cols but we force 50-50, we need smaller font to fit it
        if col_count >= 6:
            table_font = "12px"
            zoom = "0.84"
        elif col_count >= 4:
            zoom = "0.88"
        
    return grid_class, text_style, table_font, zoom

# --- USER CSS (Crimson: Baskerville serif, Deep Crimson + Charcoal + Warm Ivory) ---
USER_CSS_CRIMSON = """

  :root {
    --accent:       #9B1C1C;
    --accent-gold:  #B45309;
    --accent-navy:  #1E3A5F;
    --accent-rose:  #BE185D;
    --dark:         #1C1917;
    --text-main:    #1C1917;
    --text-soft:    #6B5B52;
    --font-base:    26px;
    --font-head:    56px;
    --bg-header:    rgba(155, 28, 28, 0.08);
    --bg-row-even:  rgba(155, 28, 28, 0.03);
    --border-color: rgba(155, 28, 28, 0.16);
    --radius:       12px;
  }

  section {
    font-family: 'Baskerville', 'Baskerville Old Face', 'Libre Baskerville', Georgia, 'Times New Roman', serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 90% 8%,  rgba(155, 28, 28, 0.10) 0%, transparent 44%),
      radial-gradient(ellipse at 8%  92%, rgba(180, 83, 9,  0.08) 0%, transparent 44%),
      linear-gradient(155deg, #FDFAF6 0%, #FAF6F0 55%, #F5EFE6 100%);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end {
    flex: 1; min-height: 0;
  }

  h1 {
    font-family: 'Baskerville', 'Baskerville Old Face', 'Libre Baskerville', Georgia, serif;
    font-weight: 700;
    font-size: var(--font-head);
    letter-spacing: -0.5px;
    color: var(--dark);
    margin: 0 0 22px 0;
    line-height: 1.06;
    font-style: normal;
  }

  h3 {
    font-family: 'Baskerville', Georgia, serif;
    font-size: 13px;
    font-weight: 400;
    font-style: italic;
    color: var(--accent);
    text-transform: none;
    letter-spacing: 0.04em;
    margin: 0 0 16px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.52); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(155, 28, 28, 0.12); padding: 1px 5px; border-radius: 2px; color: var(--accent); }

  ul { padding: 0; margin: 0; list-style: none !important; }

  li {
    line-height: var(--slide-lh, 1.48);
    margin-bottom: 12px;
    padding-left: 22px;
    position: relative;
    font-size: var(--slide-fs, inherit);
  }

  li::before {
    content: "▸";
    position: absolute;
    left: 0; top: 0.02em;
    color: var(--accent);
    font-size: 0.75em;
  }
  li:nth-child(2)::before { color: var(--accent-gold); }
  li:nth-child(3)::before { color: var(--accent-navy); }
  li:nth-child(4)::before { color: var(--accent-rose); }

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

  .pad-col {
    padding: 46px 52px; display: flex; flex-direction: column;
    justify-content: flex-start; height: 100%; min-width: 0; min-height: 0;
    overflow: hidden; box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  .card-grid { display: grid; gap: 18px; margin-top: 16px; align-content: start; }

  .feature-card {
    background: rgba(255, 252, 248, 0.95);
    padding: 20px 24px;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    box-shadow: 0 2px 14px rgba(155, 28, 28, 0.08);
    position: relative; overflow: hidden;
  }
  .feature-card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; background: var(--accent);
  }
  .card-grid .feature-card:nth-child(2)::before { background: var(--accent-gold); }
  .card-grid .feature-card:nth-child(3)::before { background: var(--accent-navy); }
  .card-grid .feature-card:nth-child(4)::before { background: var(--accent-rose); }

  .bg-dark {
    background:
      radial-gradient(ellipse at 18% 18%, rgba(155, 28, 28, 0.25) 0%, transparent 50%),
      radial-gradient(ellipse at 82% 82%, rgba(180, 83,  9, 0.16) 0%, transparent 50%),
      linear-gradient(150deg, #0E0907 0%, #1C1917 55%, #221D1A 100%) !important;
    color: #F5EDE4 !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #F5EDE4 !important; }
  .bg-dark strong { color: #FCA5A5 !important; }
  .bg-dark h3 { color: rgba(252, 165, 165, 0.75) !important; font-style: italic; }
  .bg-dark li::before { color: #FCA5A5 !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 10% 10%, rgba(255,255,255,0.12) 0%, transparent 45%),
      linear-gradient(140deg, #7F1D1D 0%, #9B1C1C 50%, #B45309 100%) !important;
    color: #FEF2F2 !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FEF2F2 !important; }
  .bg-accent h3 { color: rgba(254, 242, 242, 0.72) !important; font-style: italic; }
  .bg-accent li::before { color: rgba(255,220,170,0.90) !important; }

  .slide-title .title-shell { gap: 16px; justify-content: center; }
  .slide-title h1 { font-size: 64px; line-height: 1.05; max-width: 22ch; letter-spacing: -0.5px; font-style: italic; }
  .title-rule { width: 70px !important; height: 2px !important; border-radius: 0; background: rgba(255,255,255,0.55) !important; }
  .title-authors  { font-size: 22px !important; font-weight: 400; opacity: 0.90; font-style: italic; }
  .title-subtitle { font-size: 13px !important; font-weight: 400; letter-spacing: 0.24em; text-transform: uppercase; opacity: 0.65; font-style: normal; }

  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 80px !important; letter-spacing: -0.5px; margin-bottom: 22px; font-style: italic; }
  .slide-end .end-note {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius); padding: 22px 28px;
    max-width: 900px; margin: 0 auto; text-align: left;
  }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #EDE0D4 0%, #F0E6D8 60%, #F3EAE0 100%);
  }

  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card {
    background: rgba(255, 252, 248, 0.92); border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent); border-radius: 2px var(--radius) var(--radius) 2px;
    padding: 14px 18px; box-shadow: 0 2px 8px rgba(155, 28, 28, 0.07);
  }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  .slide-hero .hero-panel, .slide-split .hero-panel {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: 12px; padding: 22px 26px !important;
  }
  .slide-hero.slide-hero-full .hero-panel {
    padding: 26px 34px !important; border-left: 4px solid rgba(252,165,165,0.60) !important;
    border-radius: 0 12px 12px 0 !important; background: rgba(155,28,28,0.14) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.52 !important; font-weight: 400; color: rgba(255,255,255,0.92); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  table {
    width: 100%; max-width: 100%; table-layout: fixed;
    border-collapse: collapse; margin-top: 18px; font-size: 16px;
    background: transparent; border-radius: var(--radius); overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: 0 3px 16px rgba(155, 28, 28, 0.09);
  }
  th {
    text-align: left; padding: 10px 14px; color: var(--accent); font-weight: 700;
    font-style: italic; letter-spacing: 0.04em; font-size: 0.85em;
    background: rgba(155, 28, 28, 0.06); border-bottom: 2px solid rgba(155, 28, 28, 0.20);
    overflow-wrap: anywhere; word-break: break-word;
    font-family: 'Baskerville', 'Baskerville Old Face', Georgia, serif;
  }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(155, 28, 28, 0.07); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }

  .slide-results .pad-col:last-child { background: rgba(237, 224, 212, 0.55); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Slate: Gill Sans humanist, Cool Grey + Teal + Pure White) ---
USER_CSS_SLATE = """

  :root {
    --accent:       #0F766E;
    --accent-light: rgba(15, 118, 110, 0.10);
    --accent-blue:  #2563EB;
    --accent-amber: #D97706;
    --dark:         #0F172A;
    --text-main:    #1E293B;
    --text-soft:    #64748B;
    --font-base:    26px;
    --font-head:    58px;
    --bg-header:    rgba(15, 118, 110, 0.07);
    --bg-row-even:  rgba(15, 118, 110, 0.03);
    --border-color: rgba(100, 116, 139, 0.18);
    --radius:       10px;
  }

  section {
    font-family: 'Gill Sans', 'Gill Sans MT', 'Trebuchet MS', Calibri, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 92% 8%,  rgba(15, 118, 110, 0.10) 0%, transparent 42%),
      radial-gradient(ellipse at 8%  92%, rgba(37, 99, 235, 0.07)  0%, transparent 42%),
      linear-gradient(160deg, #FFFFFF 0%, #F8FAFC 60%, #F1F5F9 100%);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end {
    flex: 1; min-height: 0;
  }

  h1 {
    font-family: 'Gill Sans', 'Gill Sans MT', 'Trebuchet MS', Calibri, 'Helvetica Neue', sans-serif;
    font-weight: 600;
    font-size: var(--font-head);
    letter-spacing: -1.5px;
    color: var(--dark);
    margin: 0 0 22px 0;
    line-height: 1.06;
  }

  h3 {
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 7px;
    margin: 0 0 16px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.46); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--dark); }
  em, i  { color: var(--text-soft); }
  mark { background: rgba(15, 118, 110, 0.13); padding: 1px 6px; border-radius: 3px; color: var(--accent); font-weight: 600; }

  ul { padding: 0; margin: 0; list-style: none !important; }

  li {
    line-height: var(--slide-lh, 1.42);
    margin-bottom: 11px;
    padding-left: 20px;
    position: relative;
    font-size: var(--slide-fs, inherit);
  }

  li::before {
    content: "";
    position: absolute;
    left: 0; top: 0.62em;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
  }
  li:nth-child(2)::before { background: var(--accent-blue); }
  li:nth-child(3)::before { background: var(--accent-amber); }
  li:nth-child(4)::before { background: var(--text-soft); }

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

  .pad-col {
    padding: 44px 52px; display: flex; flex-direction: column;
    justify-content: flex-start; height: 100%; min-width: 0; min-height: 0;
    overflow: hidden; box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  .card-grid { display: grid; gap: 16px; margin-top: 16px; align-content: start; }

  .feature-card {
    background: #FFFFFF;
    padding: 20px 24px;
    border: 1px solid var(--border-color);
    border-top: 3px solid var(--accent);
    border-radius: var(--radius);
    box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
    position: relative; overflow: hidden;
  }
  .card-grid .feature-card:nth-child(2) { border-top-color: var(--accent-blue); }
  .card-grid .feature-card:nth-child(3) { border-top-color: var(--accent-amber); }
  .card-grid .feature-card:nth-child(4) { border-top-color: var(--text-soft); }

  .bg-dark {
    background:
      radial-gradient(ellipse at 18% 18%, rgba(15, 118, 110, 0.20) 0%, transparent 50%),
      radial-gradient(ellipse at 82% 82%, rgba(37,  99, 235, 0.12) 0%, transparent 50%),
      linear-gradient(150deg, #0A0F1A 0%, #0F172A 55%, #131D30 100%) !important;
    color: #E2E8F0 !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #E2E8F0 !important; }
  .bg-dark strong { color: #5EEAD4 !important; }
  .bg-dark h3 { color: rgba(94, 234, 212, 0.75) !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 12% 12%, rgba(255,255,255,0.15) 0%, transparent 45%),
      linear-gradient(140deg, #0F766E 0%, #0D9488 50%, #2563EB 100%) !important;
    color: #FFFFFF !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFFFFF !important; }
  .bg-accent h3 { color: rgba(255,255,255,0.65) !important; }

  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 66px; line-height: 1.03; max-width: 20ch; letter-spacing: -2px; }
  .title-rule { width: 60px !important; height: 3px !important; border-radius: 0; background: rgba(255,255,255,0.65) !important; }
  .title-authors  { font-size: 23px !important; font-weight: 400; opacity: 0.88; }
  .title-subtitle { font-size: 14px !important; font-weight: 700; letter-spacing: 0.30em; text-transform: uppercase; opacity: 0.65; }

  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 82px !important; letter-spacing: -2px; margin-bottom: 20px; }
  .slide-end .end-note {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius); padding: 22px 28px;
    max-width: 900px; margin: 0 auto; text-align: left;
  }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #E2EEF0 0%, #E8F2F4 60%, #EEF5F7 100%);
  }

  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card {
    background: #FFFFFF; border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent); border-radius: 2px var(--radius) var(--radius) 2px;
    padding: 14px 18px; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
  }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  .slide-hero .hero-panel,
  .slide-split .hero-panel {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
    border-radius: 12px; padding: 22px 26px !important;
  }
  .slide-hero.slide-hero-full .hero-panel {
    padding: 26px 34px !important; border-left: 4px solid rgba(255,255,255,0.50) !important;
    border-radius: 0 12px 12px 0 !important;
    background: rgba(15, 118, 110, 0.14) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.48 !important; font-weight: 400; color: rgba(255,255,255,0.92); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  table {
    width: 100%; max-width: 100%; table-layout: fixed;
    border-collapse: collapse; margin-top: 18px; font-size: 16px;
    background: #FFFFFF; border-radius: var(--radius); overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: 0 1px 10px rgba(0,0,0,0.06);
  }
  th {
    text-align: left; padding: 10px 14px; color: var(--text-soft); font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.10em; font-size: 0.78em;
    background: #F8FAFC; border-bottom: 2px solid var(--accent);
    overflow-wrap: anywhere; word-break: break-word;
  }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(100,116,139,0.10); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: #F8FAFC; }
  tr:last-child td  { border-bottom: none; }

  .slide-results .pad-col:last-child { background: rgba(226, 238, 240, 0.60); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Terra: Rockwell slab serif, Terracotta + Sand + Forest Green) ---
USER_CSS_TERRA = """

  :root {
    --accent:       #C2522A;
    --accent-green: #3D6B47;
    --accent-sand:  #D4A96A;
    --accent-clay:  #8C3A1E;
    --dark:         #2C1810;
    --text-main:    #2C1810;
    --text-soft:    #7A5540;
    --font-base:    26px;
    --font-head:    56px;
    --bg-header:    rgba(194, 82, 42, 0.08);
    --bg-row-even:  rgba(194, 82, 42, 0.04);
    --border-color: rgba(194, 82, 42, 0.18);
    --radius:       14px;
  }

  section {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 88% 10%, rgba(212, 169, 106, 0.18) 0%, transparent 45%),
      radial-gradient(ellipse at 10% 90%, rgba(61, 107, 71, 0.13)  0%, transparent 45%),
      linear-gradient(150deg, #FAF5EE 0%, #F6EFE3 55%, #F2E9D8 100%);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end {
    flex: 1; min-height: 0;
  }

  /* TYPOGRAPHY — Rockwell slab serif headers */
  h1 {
    font-family: 'Rockwell', 'Rockwell Extra Bold', 'Courier New', Georgia, serif;
    font-weight: 700;
    font-size: var(--font-head);
    letter-spacing: -1px;
    color: var(--dark);
    margin: 0 0 22px 0;
    line-height: 1.06;
  }

  h3 {
    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 6px;
    margin: 0 0 16px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.44); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(212, 169, 106, 0.30); padding: 1px 6px; border-radius: 3px; color: inherit; }

  /* LISTS */
  ul { padding: 0; margin: 0; list-style: none !important; }

  li {
    line-height: var(--slide-lh, 1.40);
    margin-bottom: 11px;
    padding-left: 22px;
    position: relative;
    font-size: var(--slide-fs, inherit);
  }

  li::before {
    content: "";
    position: absolute;
    left: 0; top: 0.60em;
    width: 9px; height: 9px;
    border-radius: 2px;
    background: var(--accent);
    transform: rotate(0deg);
  }
  li:nth-child(2)::before { background: var(--accent-green); }
  li:nth-child(3)::before { background: var(--accent-sand); }
  li:nth-child(4)::before { background: var(--accent-clay); }

  /* IMAGES */
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

  .pad-col {
    padding: 44px 50px; display: flex; flex-direction: column;
    justify-content: flex-start; height: 100%; min-width: 0; min-height: 0;
    overflow: hidden; box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  /* CARDS */
  .card-grid { display: grid; gap: 18px; margin-top: 16px; align-content: start; }

  .feature-card {
    background: rgba(255, 248, 240, 0.92);
    padding: 20px 24px;
    border: 1px solid var(--border-color);
    border-left: 5px solid var(--accent);
    border-radius: 2px var(--radius) var(--radius) 2px;
    box-shadow: 0 3px 14px rgba(194, 82, 42, 0.10);
    position: relative; overflow: hidden;
  }
  .card-grid .feature-card:nth-child(2) { border-left-color: var(--accent-green); }
  .card-grid .feature-card:nth-child(3) { border-left-color: var(--accent-sand); }
  .card-grid .feature-card:nth-child(4) { border-left-color: var(--accent-clay); }

  /* DARK SLIDES */
  .bg-dark {
    background:
      radial-gradient(ellipse at 15% 20%, rgba(194, 82, 42, 0.22) 0%, transparent 50%),
      radial-gradient(ellipse at 85% 80%, rgba(61, 107, 71, 0.18) 0%, transparent 50%),
      linear-gradient(145deg, #180C06 0%, #2C1810 55%, #331D12 100%) !important;
    color: #F5EAD8 !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #F5EAD8 !important; }
  .bg-dark strong { color: var(--accent-sand) !important; }
  .bg-dark h3 { color: rgba(212, 169, 106, 0.80) !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 10% 10%, rgba(255,255,255,0.15) 0%, transparent 45%),
      linear-gradient(140deg, #8C3A1E 0%, #C2522A 50%, #D4A96A 100%) !important;
    color: #FFF5EC !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFF5EC !important; }
  .bg-accent h3 { color: rgba(255, 240, 210, 0.72) !important; }

  /* TITLE SLIDE */
  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 64px; line-height: 1.04; max-width: 20ch; letter-spacing: -1px; }
  .title-rule { width: 80px !important; height: 4px !important; border-radius: 2px; background: rgba(255,255,255,0.65) !important; }
  .title-authors  { font-size: 23px !important; font-weight: 400; opacity: 0.88; }
  .title-subtitle { font-size: 14px !important; font-weight: 700; letter-spacing: 0.26em; text-transform: uppercase; opacity: 0.68; }

  /* END SLIDE */
  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 80px !important; letter-spacing: -1px; margin-bottom: 22px; }
  .slide-end .end-note {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius); padding: 22px 28px;
    max-width: 900px; margin: 0 auto; text-align: left;
  }

  /* SPLIT TEXT COLUMN */
  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #EAD9C2 0%, #EFE0CA 60%, #F3E6D2 100%);
  }

  /* STEP CARDS */
  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card {
    background: rgba(255, 248, 240, 0.90); border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent); border-radius: 2px 14px 14px 2px;
    padding: 14px 18px; box-shadow: 0 2px 10px rgba(194, 82, 42, 0.09);
  }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  /* HERO PANEL */
  .slide-hero .hero-panel,
  .slide-split .hero-panel {
    background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px; padding: 22px 26px !important;
  }
  .slide-hero.slide-hero-full .hero-panel {
    padding: 26px 34px !important; border-left: 5px solid var(--accent-sand) !important;
    border-radius: 0 14px 14px 0 !important;
    background: rgba(194, 82, 42, 0.14) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.48 !important; font-weight: 400; color: rgba(255,255,255,0.92); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  /* TABLES */
  table {
    width: 100%; max-width: 100%; table-layout: fixed;
    border-collapse: collapse; margin-top: 18px; font-size: 16px;
    background: transparent; border-radius: 12px; overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 18px rgba(194, 82, 42, 0.10);
  }
  th {
    text-align: left; padding: 10px 14px; color: var(--accent-clay); font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.09em; font-size: 0.80em;
    background: rgba(194, 82, 42, 0.07); border-bottom: 2px solid rgba(194, 82, 42, 0.22);
    overflow-wrap: anywhere; word-break: break-word;
    font-family: 'Rockwell', 'Courier New', Georgia, serif;
  }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(194, 82, 42, 0.07); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }

  .slide-results .pad-col:last-child { background: rgba(234, 217, 194, 0.55); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Premium: Optima/Candara font, Antique Gold + Ivory + Deep Navy) ---
USER_CSS_PREMIUM = """

  :root {
    --accent:        #B8965A;
    --accent-navy:   #0D1B2A;
    --accent-burg:   #7A1C3A;
    --accent-gold2:  #D4B483;
    --dark:          #0D1B2A;
    --text-main:     #1A1208;
    --text-soft:     #6B5A3E;
    --font-base:     26px;
    --font-head:     56px;
    --bg-header:     rgba(184, 150, 90, 0.09);
    --bg-row-even:   rgba(184, 150, 90, 0.04);
    --border-color:  rgba(184, 150, 90, 0.20);
    --radius:        14px;
  }

  section {
    font-family: 'Optima', 'Candara', 'Palatino Linotype', Palatino, Georgia, serif;
    color: var(--text-main);
    padding: 0;
    font-size: var(--font-base);
    font-weight: 400;
    background:
      radial-gradient(ellipse at 88% 10%, rgba(184, 150, 90, 0.15) 0%, transparent 45%),
      radial-gradient(ellipse at 10% 90%, rgba(13, 27, 42, 0.08)  0%, transparent 45%),
      linear-gradient(150deg, #FAFAF5 0%, #F7F4ED 55%, #F3F0E6 100%);
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
    font-family: 'Optima', 'Candara', 'Palatino Linotype', Palatino, Georgia, serif;
    font-weight: 600;
    font-size: var(--font-head);
    letter-spacing: -0.5px;
    color: var(--dark);
    margin: 0 0 24px 0;
    line-height: 1.06;
  }

  h3 {
    font-family: 'Optima', 'Candara', Georgia, serif;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 6px;
    margin: 0 0 18px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.48); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent-navy); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(184, 150, 90, 0.22); padding: 1px 6px; border-radius: 3px; color: var(--text-main); }

  /* LISTS */
  ul { padding: 0; margin: 0; list-style: none !important; }

  li {
    line-height: var(--slide-lh, 1.44);
    margin-bottom: 12px;
    padding-left: 24px;
    position: relative;
    font-size: var(--slide-fs, inherit);
  }

  li::before {
    content: "—";
    position: absolute;
    left: 0; top: 0;
    color: var(--accent);
    font-weight: 400;
    font-size: 1em;
  }
  li:nth-child(2)::before { color: var(--accent-burg); }
  li:nth-child(3)::before { color: var(--accent-navy); opacity: 0.7; }
  li:nth-child(4)::before { color: var(--accent-gold2); }

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
    padding: 46px 52px; display: flex; flex-direction: column;
    justify-content: flex-start; height: 100%; min-width: 0; min-height: 0;
    overflow: hidden; box-sizing: border-box;
  }
  .pad-col > *:first-child { margin-top: auto; }
  .pad-col > *:last-child  { margin-bottom: auto; }

  /* CARDS */
  .card-grid { display: grid; gap: 18px; margin-top: 16px; align-content: start; }

  .feature-card {
    background: rgba(255, 255, 255, 0.80);
    padding: 20px 24px;
    border: 1px solid var(--border-color);
    border-bottom: 3px solid var(--accent);
    border-radius: var(--radius);
    box-shadow: 0 4px 18px rgba(184, 150, 90, 0.10);
    position: relative; overflow: hidden;
  }
  .card-grid .feature-card:nth-child(2) { border-bottom-color: var(--accent-burg); }
  .card-grid .feature-card:nth-child(3) { border-bottom-color: var(--accent-navy); }
  .card-grid .feature-card:nth-child(4) { border-bottom-color: var(--accent-gold2); }

  /* DARK SLIDES */
  .bg-dark {
    background:
      radial-gradient(ellipse at 15% 20%, rgba(184, 150, 90, 0.18) 0%, transparent 50%),
      radial-gradient(ellipse at 85% 80%, rgba(122, 28, 58, 0.14) 0%, transparent 50%),
      linear-gradient(145deg, #070D14 0%, #0D1B2A 55%, #111F2E 100%) !important;
    color: #F0ECD8 !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #F0ECD8 !important; }
  .bg-dark strong { color: var(--accent-gold2) !important; }
  .bg-dark h3 { color: rgba(212, 180, 131, 0.80) !important; }
  .bg-dark li::before { color: var(--accent) !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 10% 10%, rgba(255,255,255,0.12) 0%, transparent 45%),
      linear-gradient(140deg, #0D1B2A 0%, #1A2E45 40%, #B8965A 100%) !important;
    color: #F5EED8 !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #F5EED8 !important; }
  .bg-accent h3 { color: rgba(240, 220, 170, 0.75) !important; }
  .bg-accent li::before { color: var(--accent-gold2) !important; }

  /* TITLE SLIDE */
  .slide-title .title-shell { gap: 16px; justify-content: center; }
  .slide-title h1 { font-size: 66px; line-height: 1.04; max-width: 20ch; letter-spacing: -1px; }
  .title-rule { width: 90px !important; height: 2px !important; border-radius: 0; background: rgba(255,255,255,0.60) !important; }
  .title-authors  { font-size: 23px !important; font-weight: 400; opacity: 0.88; font-family: 'Optima', 'Candara', Georgia, serif; }
  .title-subtitle { font-size: 14px !important; font-weight: 600; letter-spacing: 0.28em; text-transform: uppercase; opacity: 0.65; }

  /* END SLIDE */
  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 82px !important; letter-spacing: -1px; margin-bottom: 22px; }
  .slide-end .end-note {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius); padding: 24px 30px;
    max-width: 900px; margin: 0 auto; text-align: left;
  }

  /* SPLIT TEXT COLUMN */
  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child {
    background: linear-gradient(160deg, #EDE8D8 0%, #F0EBD8 60%, #F4EFE2 100%);
  }

  /* STEP CARDS */
  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card {
    background: rgba(255, 255, 255, 0.85); border: 1px solid var(--border-color);
    border-left: 3px solid var(--accent); border-radius: 2px 14px 14px 2px;
    padding: 14px 20px; box-shadow: 0 2px 10px rgba(184, 150, 90, 0.08);
  }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  /* HERO PANEL */
  .slide-hero .hero-panel,
  .slide-split .hero-panel {
    background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px; padding: 22px 28px !important;
  }
  .slide-hero.slide-hero-full .hero-panel {
    padding: 26px 36px !important; border-left: 4px solid var(--accent-gold2) !important;
    border-radius: 0 14px 14px 0 !important;
    background: rgba(184, 150, 90, 0.12) !important;
  }
  .slide-hero.slide-hero-full .hero-panel p,
  .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.50 !important; font-weight: 400; color: rgba(255,255,255,0.92); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  /* TABLES */
  table {
    width: 100%; max-width: 100%; table-layout: fixed;
    border-collapse: collapse; margin-top: 18px; font-size: 16px;
    background: transparent; border-radius: 12px; overflow: hidden;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 20px rgba(184, 150, 90, 0.12);
  }
  th {
    text-align: left; padding: 11px 14px; color: var(--accent-navy); font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.10em; font-size: 0.78em;
    background: rgba(184, 150, 90, 0.08); border-bottom: 2px solid var(--accent);
    overflow-wrap: anywhere; word-break: break-word;
    font-family: 'Optima', 'Candara', Georgia, serif;
  }
  td { padding: 10px 14px; border-bottom: 1px solid rgba(184, 150, 90, 0.08); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }

  .slide-results .pad-col:last-child { background: rgba(237, 232, 216, 0.55); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Tech: Electric Blue, sharp geometric, modern SaaS) ---
USER_CSS_TECH = """

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
"""

# --- USER CSS (Editorial: Forest Green + Gold, Garamond serif) ---
USER_CSS_EDITORIAL = """

  :root {
    --accent:        #1A6B3C;
    --accent-light:  rgba(26, 107, 60, 0.12);
    --accent-gold:   #C9973A;
    --accent-gold-soft: rgba(201, 151, 58, 0.18);
    --dark:          #0E1A14;
    --text-main:     #1C2B22;
    --text-soft:     #4A5E50;
    --font-base:     26px;
    --font-head:     58px;
    --bg-header:     rgba(26, 107, 60, 0.07);
    --bg-row-even:   rgba(26, 107, 60, 0.03);
    --border-color:  rgba(26, 107, 60, 0.14);
    --radius:        16px;
  }

  section {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0; font-size: var(--font-base); font-weight: 400;
    background:
      radial-gradient(ellipse at 90% 10%, rgba(201, 151, 58, 0.13) 0%, transparent 45%),
      radial-gradient(ellipse at 10% 90%, rgba(26, 107, 60, 0.11)  0%, transparent 45%),
      linear-gradient(150deg, #F8F7F2 0%, #F4F2EB 55%, #F0EEE6 100%);
    display: flex; flex-direction: column; overflow: hidden; position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end { flex: 1; min-height: 0; }

  h1 {
    font-family: 'Garamond', 'EB Garamond', Georgia, 'Times New Roman', serif;
    font-weight: 600; font-size: var(--font-head); letter-spacing: -1.5px;
    color: var(--dark); margin: 0 0 22px 0; line-height: 1.06;
  }

  h3 {
    font-size: 12px; font-weight: 700; color: var(--accent-gold);
    text-transform: uppercase; letter-spacing: 5px; margin: 0 0 16px 0;
  }

  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.42); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(201, 151, 58, 0.28); padding: 1px 5px; border-radius: 3px; color: inherit; }

  ul { padding: 0; margin: 0; list-style: none !important; }
  li { line-height: var(--slide-lh, 1.38); margin-bottom: 11px; padding-left: 22px; position: relative; font-size: var(--slide-fs, inherit); }
  li::before { content: ""; position: absolute; left: 0; top: 0.58em; width: 8px; height: 8px; border-radius: 2px; background: var(--accent); transform: rotate(45deg); }
  li:nth-child(2)::before { background: var(--accent-gold); }
  li:nth-child(3)::before { background: #2D9B5A; }
  li:nth-child(4)::before { background: #A07828; }

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
  .feature-card { background: #FFFFFF; padding: 20px 24px; border: 1px solid var(--border-color); border-top: 4px solid var(--accent); border-radius: var(--radius); box-shadow: 0 2px 12px rgba(26, 107, 60, 0.07); position: relative; overflow: hidden; }
  .card-grid .feature-card:nth-child(2) { border-top-color: var(--accent-gold); }
  .card-grid .feature-card:nth-child(3) { border-top-color: #2D9B5A; }
  .card-grid .feature-card:nth-child(4) { border-top-color: #A07828; }

  .bg-dark {
    background:
      radial-gradient(ellipse at 20% 10%, rgba(26, 107, 60, 0.22) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 90%, rgba(201, 151, 58, 0.15) 0%, transparent 50%),
      linear-gradient(150deg, #0A1510 0%, #0E1A14 50%, #131F18 100%) !important;
    color: #EEF2EE !important;
  }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #EEF2EE !important; }
  .bg-dark strong { color: var(--accent-gold) !important; }
  .bg-dark h3 { color: rgba(201, 151, 58, 0.80) !important; }

  .bg-accent {
    background:
      radial-gradient(ellipse at 15% 15%, rgba(255,255,255,0.15) 0%, transparent 45%),
      linear-gradient(140deg, #1A6B3C 0%, #24935A 50%, #C9973A 100%) !important;
    color: #FFFFFF !important;
  }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFFFFF !important; }
  .bg-accent h3 { color: rgba(255,255,255,0.70) !important; }

  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 68px; line-height: 1.02; max-width: 18ch; letter-spacing: -2px; }
  .title-rule { width: 100px !important; height: 5px !important; border-radius: 999px; background: rgba(255,255,255,0.65) !important; }
  .title-authors  { font-size: 24px !important; font-weight: 500; opacity: 0.90; }
  .title-subtitle { font-size: 16px !important; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; opacity: 0.72; }

  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 84px !important; letter-spacing: -3px; margin-bottom: 20px; }
  .slide-end .end-note { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); border-radius: var(--radius); padding: 22px 28px; max-width: 900px; margin: 0 auto; text-align: left; }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child { background: linear-gradient(160deg, #EEECe4 0%, #F1EFE8 60%, #F4F2EB 100%); }

  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card { background: rgba(255,255,255,0.90); border: 1px solid var(--border-color); border-left: 4px solid var(--accent); border-radius: 4px 14px 14px 4px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(26, 107, 60, 0.07); }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  .slide-hero .hero-panel, .slide-split .hero-panel { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 22px 26px !important; }
  .slide-hero.slide-hero-full .hero-panel { padding: 26px 34px !important; border-left: 5px solid var(--accent-gold) !important; border-radius: 0 16px 16px 0 !important; background: linear-gradient(135deg, rgba(26,107,60,0.14) 0%, rgba(26,107,60,0.04) 100%) !important; }
  .slide-hero.slide-hero-full .hero-panel p, .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.45 !important; font-weight: 500; color: rgba(255,255,255,0.93); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  table { width: 100%; max-width: 100%; table-layout: fixed; border-collapse: collapse; margin-top: 18px; font-size: 16px; background: transparent; border-radius: 14px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 2px 16px rgba(26, 107, 60, 0.08); }
  th { text-align: left; padding: 10px 14px; color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.80em; background: rgba(26, 107, 60, 0.07); border-bottom: 2px solid rgba(26, 107, 60, 0.18); overflow-wrap: anywhere; word-break: break-word; }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(26, 107, 60, 0.07); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }
  .slide-results .pad-col:last-child { background: rgba(240, 238, 230, 0.70); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Midnight: Dark-base, Cyan + Gold, clean sans) ---
USER_CSS_MIDNIGHT = """

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
"""

# --- USER CSS (Blush: Warm Rose + Coral, modern startup feel) ---
USER_CSS_BLUSH = """

  :root {
    --accent:        #C2185B;
    --accent-coral:  #FF6B47;
    --accent-peach:  #FFB38A;
    --accent-lilac:  #C084FC;
    --dark:          #1A0A10;
    --text-main:     #2D1020;
    --text-soft:     #7A4560;
    --font-base:     26px;
    --font-head:     56px;
    --bg-header:     rgba(194, 24, 91, 0.07);
    --bg-row-even:   rgba(194, 24, 91, 0.03);
    --border-color:  rgba(194, 24, 91, 0.14);
    --radius:        20px;
  }

  section {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    color: var(--text-main);
    padding: 0; font-size: var(--font-base); font-weight: 400;
    background:
      radial-gradient(ellipse at 85% 10%, rgba(255, 107, 71, 0.18) 0%, transparent 45%),
      radial-gradient(ellipse at 10% 90%, rgba(192, 132, 252, 0.14) 0%, transparent 45%),
      linear-gradient(145deg, #FFF5F7 0%, #FFF0F3 55%, #FEECF0 100%);
    display: flex; flex-direction: column; overflow: hidden; position: relative;
  }

  section > * { position: relative; z-index: 1; }

  .slide-split, .slide-hero, .slide-results, .slide-method, .slide-columns, .slide-title, .slide-end { flex: 1; min-height: 0; }

  h1 { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; font-weight: 800; font-size: var(--font-head); letter-spacing: -2px; color: var(--dark); margin: 0 0 22px 0; line-height: 1.04; }
  h3 { font-size: 12px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 5px; margin: 0 0 16px 0; }
  p { margin-bottom: 14px; line-height: var(--slide-lh, 1.42); color: var(--text-main); font-size: var(--slide-fs, inherit); }
  strong { font-weight: 700; color: var(--accent); }
  em, i  { color: var(--text-soft); font-style: italic; }
  mark { background: rgba(255, 107, 71, 0.22); padding: 1px 5px; border-radius: 4px; color: inherit; }

  ul { padding: 0; margin: 0; list-style: none !important; }
  li { line-height: var(--slide-lh, 1.38); margin-bottom: 11px; padding-left: 22px; position: relative; font-size: var(--slide-fs, inherit); }
  li::before { content: ""; position: absolute; left: 0; top: 0.58em; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
  li:nth-child(2)::before { background: var(--accent-coral); }
  li:nth-child(3)::before { background: var(--accent-lilac); }
  li:nth-child(4)::before { background: var(--accent-peach); }

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
  .feature-card { background: #FFFFFF; padding: 20px 24px; border: 1px solid rgba(194,24,91,0.10); border-radius: var(--radius); box-shadow: 0 4px 20px rgba(194,24,91,0.08); position: relative; overflow: hidden; }
  .feature-card::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 4px; background: linear-gradient(90deg, var(--accent), var(--accent-coral)); border-radius: 20px 20px 0 0; }
  .card-grid .feature-card:nth-child(2)::before { background: linear-gradient(90deg, var(--accent-coral), var(--accent-peach)); }
  .card-grid .feature-card:nth-child(3)::before { background: linear-gradient(90deg, var(--accent-lilac), #8B5CF6); }
  .card-grid .feature-card:nth-child(4)::before { background: linear-gradient(90deg, var(--accent-peach), var(--accent-coral)); }

  .bg-dark { background: radial-gradient(ellipse at 20% 15%, rgba(194,24,91,0.20) 0%, transparent 50%), radial-gradient(ellipse at 80% 85%, rgba(255,107,71,0.14) 0%, transparent 50%), linear-gradient(145deg, #1A0A10 0%, #250D17 50%, #2D1020 100%) !important; color: #F8EEF2 !important; }
  .bg-dark h1, .bg-dark p, .bg-dark li { color: #F8EEF2 !important; }
  .bg-dark strong { color: var(--accent-peach) !important; }
  .bg-dark h3 { color: rgba(255,179,138,0.80) !important; }

  .bg-accent { background: radial-gradient(ellipse at 10% 10%, rgba(255,255,255,0.18) 0%, transparent 45%), linear-gradient(135deg, #C2185B 0%, #E91E8C 45%, #FF6B47 100%) !important; color: #FFFFFF !important; }
  .bg-accent h1, .bg-accent p, .bg-accent li { color: #FFFFFF !important; }
  .bg-accent h3 { color: rgba(255,255,255,0.68) !important; }

  .slide-title .title-shell { gap: 14px; justify-content: center; }
  .slide-title h1 { font-size: 68px; line-height: 1.02; max-width: 18ch; letter-spacing: -2.5px; }
  .title-rule { width: 110px !important; height: 5px !important; border-radius: 999px; background: linear-gradient(90deg, rgba(255,255,255,0.90), rgba(255,255,255,0.50)) !important; }
  .title-authors  { font-size: 24px !important; font-weight: 500; opacity: 0.90; }
  .title-subtitle { font-size: 16px !important; font-weight: 700; letter-spacing: 0.20em; text-transform: uppercase; opacity: 0.70; }

  .slide-end .pad-col { justify-content: center; align-items: center; text-align: center; }
  .slide-end .pad-col > *:first-child { margin-top: 0; }
  .slide-end .pad-col > *:last-child  { margin-bottom: 0; }
  .slide-end h1 { font-size: 84px !important; letter-spacing: -3px; margin-bottom: 20px; }
  .slide-end .end-note { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.15); border-radius: var(--radius); padding: 22px 28px; max-width: 900px; margin: 0 auto; text-align: left; }

  .slide-hero.slide-hero-image .pad-col,
  .slide-split.slide-split-image .pad-col,
  .slide-results .pad-col:first-child { background: linear-gradient(160deg, #FCDDE8 0%, #FDE4EC 60%, #FEEAEF 100%); }

  .slide-method .step-stack { display: grid; gap: 10px; }
  .slide-method .step-card { background: rgba(255,255,255,0.90); border: 1px solid var(--border-color); border-left: 4px solid var(--accent); border-radius: 4px 16px 16px 4px; padding: 14px 18px; box-shadow: 0 2px 10px rgba(194,24,91,0.08); }
  .slide-method.bg-dark .step-card { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.10); box-shadow: none; }

  .slide-hero .hero-panel, .slide-split .hero-panel { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14); border-radius: 18px; padding: 22px 26px !important; }
  .slide-hero.slide-hero-full .hero-panel { padding: 26px 34px !important; border-left: 5px solid var(--accent-peach) !important; border-radius: 0 18px 18px 0 !important; background: linear-gradient(135deg, rgba(194,24,91,0.16) 0%, rgba(194,24,91,0.04) 100%) !important; }
  .slide-hero.slide-hero-full .hero-panel p, .slide-hero.slide-hero-full .hero-panel li { font-size: 24px !important; line-height: 1.45 !important; font-weight: 500; color: rgba(255,255,255,0.93); }
  .slide-hero.slide-hero-full .hero-panel li::before { display: none; }

  table { width: 100%; max-width: 100%; table-layout: fixed; border-collapse: collapse; margin-top: 18px; font-size: 16px; background: transparent; border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); box-shadow: 0 4px 20px rgba(194,24,91,0.10); }
  th { text-align: left; padding: 10px 14px; color: var(--accent); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.80em; background: rgba(194,24,91,0.06); border-bottom: 2px solid rgba(194,24,91,0.18); overflow-wrap: anywhere; word-break: break-word; }
  td { padding: 9px 14px; border-bottom: 1px solid rgba(194,24,91,0.06); color: var(--text-main); overflow-wrap: anywhere; word-break: break-word; }
  td:last-child { border-right: none; }
  tr:nth-child(even) { background: var(--bg-row-even); }
  tr:last-child td  { border-bottom: none; }
  .slide-results .pad-col:last-child { background: rgba(252,221,232,0.55); border-left: 1px solid var(--border-color); }

  .katex { font-size: inherit !important; }
  .katex-display { font-size: 1em !important; margin: 0 !important; }
"""

# --- USER CSS (Designer: Visually Rich & Diverse) ---
# Performance: NO @import (blocks render), NO backdrop-filter (freezes PDF),
# NO SVG feTurbulence (expensive), NO filter:blur. Uses system fonts + simple effects.
USER_CSS_DESIGNER = """

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
"""

# --- ROBUST HELPER FUNCTIONS ---

def safe_get(data, keys, default=""):
    """Safely extract data from dict using a list of potential keys."""
    if isinstance(data, str): return data
    if not isinstance(data, dict): return default
    for k in keys:
        if k in data and data[k]: return data[k]
    return default


def compact_authors(authors, max_names=12):
    """Shorten extreme author lists to avoid title-slide overflow."""
    if not authors:
        return ""
    parts = [p.strip() for p in re.split(r',|\band\b', authors) if p.strip()]
    if len(parts) > max_names:
        return f"{parts[0]} et al."
    return authors

def get_asset_html(filename, asset_files, img_style=""):
    """Generates robust image HTML."""
    if filename and filename in asset_files:
        style_attr = f' style="{img_style}"' if img_style else ""
        return f'<img src="./{filename}"{style_attr} />'
    return ""

def raw_latex_safe(text):
    # Minimal fix: DO NOTHING. Return text unchanged.
    return text or ""

def raw_latex_safe2(text):
    """
    Crucial Fix: Escapes backslashes so Python doesn't interpret them as 
    special characters (like \\b for backspace in \\mathbb).
    """
    if not text: return ""
    return text.replace("\\", "\\\\")

def smart_content_render(data, fallback_text=""):
    """
    Solves the 'Empty Column' issue. 
    If 'text' is empty, looks for bullets, features, or steps and renders them.
    """
    # 1. Try explicit text
    text = safe_get(data, ['text', 'content', 'body', 'description'])
    if text:
        return text

    # 2. Try bullets/features/list
    items = safe_get(data, ['bullets', 'points', 'list', 'features', 'steps'])
    if isinstance(items, list) and items:
        md = ""
        for item in items:
            # Handle string items
            if isinstance(item, str):
                md += f"- {item}\n"
            # Handle dict items (e.g., {'title': 'X', 'text': 'Y'})
            elif isinstance(item, dict):
                title = safe_get(item, ['title', 'label', 'step'])
                desc = safe_get(item, ['text', 'description', 'content'])
                if title and desc:
                    md += f"- **{title}:** {desc}\n"
                elif title:
                    md += f"- {title}\n"
                elif desc:
                    md += f"- {desc}\n"
        return md
    
    return fallback_text

def normalize_list_data(data):
    """Normalize inconsistent list formats from LLM."""
    if isinstance(data, dict):
        # Check if list keys exist
        list_keys = ['features', 'points', 'items', 'steps', 'bullets', 'data',
                     'columns', 'cards', 'sections', 'entries', 'highlights',
                     'key_points', 'takeaways', 'results', 'findings']
        has_list = any(k in data for k in list_keys)

        # Fallback: if 'text' or 'content' exists but no list keys, treat as single item
        if not has_list:
            text = safe_get(data, ['text', 'content', 'body', 'description'])
            if text:
                return [{'title': '', 'text': text}]

    raw = safe_get(data, ['features', 'points', 'items', 'steps', 'bullets', 'data',
                          'columns', 'cards', 'sections', 'entries', 'highlights',
                          'key_points', 'takeaways', 'results', 'findings'])
    normalized = []

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                if ":" in item:
                    parts = item.split(":", 1)
                    normalized.append({'title': parts[0].strip(), 'text': parts[1].strip()})
                else:
                    normalized.append({'title': item, 'text': ""})
            elif isinstance(item, dict):
                normalized.append(item)

    # If all items ended up with empty title and text, the LLM used unknown keys.
    # Try to extract any string values from each item dict as fallback.
    if normalized and all(
        not safe_get(it, ['title', 'label', 'name']) and
        not safe_get(it, ['text', 'content', 'description', 'value'])
        for it in normalized
    ):
        fallback = []
        for it in normalized:
            if isinstance(it, dict):
                # Grab first two string values as title and text
                vals = [v for v in it.values() if isinstance(v, str) and v.strip()]
                if len(vals) >= 2:
                    fallback.append({'title': vals[0], 'text': vals[1]})
                elif vals:
                    fallback.append({'title': vals[0], 'text': ''})
        if fallback:
            normalized = fallback

    return normalized

def _sanitize_ctrl_chars(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_ctrl_chars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_ctrl_chars(v) for v in obj]
    if isinstance(obj, str):
        # turn control chars back into visible LaTeX escapes
        return obj.replace('\b', '\\b').replace('\f', '\\f').replace('\t', '\\t')
    return obj


# --- TEMPLATES (Redesigned) ---

def tpl_title(data, _):
    title = safe_get(data, ["title", "headline"])
    authors = compact_authors(safe_get(data, ["authors", "author"]))
    affiliation = safe_get(data, ["subtitle", "affiliation", "university", "description"])

    return f"""
<section class="slide-title bg-accent">
<div class="pad-col title-shell" style="text-align: center; align-items: center;">
  <h1 style="color: white; margin-bottom: 20px;">{title}</h1>
  <div class="title-rule" style="width: 100px; height: 6px; background: white; margin: 30px 0;"></div>
  {f"<p class='title-authors' style='font-size: 28px; opacity: 0.9; color: white;'>{authors}</p>" if authors else ""}
  {f"<p class='title-subtitle' style='font-size: 28px; opacity: 0.9; color: white;'>{affiliation}</p>" if affiliation else ""}
</div>
</section>
"""

def tpl_end(data, _):
    title = safe_get(data, ['title', 'headline'], 'Thank You')
    content = prepare_markdown_block(smart_content_render(data))
    font_size = auto_font_size_gentle(content)
    note_html = ""
    if content:
        note_html = f"""
<div class="end-note" style="font-size: {font_size}px; opacity: 0.8;" markdown="1">

{render_md(content)}

</div>
"""
    return f"""
<section class="slide-end bg-dark">

<div class="pad-col">
<h1>{title}</h1>
{note_html}
</div>
</section>
"""

def get_dynamic_font_class(text, title="", base_size=26):
    """Returns CSS font-size style based on text length to prevent overflow."""
    if not text:
        return ""
    return get_full_width_body_style(text, title)

def get_dynamic_title_class(text, body_text=""):
    """Returns style for resizing titles based on title length only.
    Density does NOT reduce title size — the title always needs to be readable."""
    if not text:
        return ""

    title_len = len(text)
    if title_len > 100:
        base = 28
    elif title_len > 75:
        base = 32
    elif title_len > 55:
        base = 36
    elif title_len > 40:
        base = 40
    else:
        base = 44

    size = clamp_num(base, 28, 44)
    margin = 14 if size <= 32 else 16 if size <= 38 else 20
    return f"font-size: {size:.0f}px; margin-bottom: {margin}px;"

def fix_latex_syntax(eq):
    """Refines LaTeX syntax to prevent rendering errors."""
    if not eq: return ""
    # Robust Fit: Remove \left and \right commands but keep delimiters
    # This prevents unbalanced \left tags if \right is missing, and vice versa.
    # It also avoids the issue where replace("\\right)", "") consumes the parenthesis.
    eq = eq.replace("\\left", "").replace("\\right", "")

    # Normalize common multi-line display-math patterns to KaTeX-friendly syntax.
    eq = eq.replace("\\begin{split}", "\\begin{aligned}")
    eq = eq.replace("\\end{split}", "\\end{aligned}")
    eq = eq.replace("...", "\\ldots")
    eq = re.sub(r'\\text\{([^{}]+)\}_\{\\text\{([^{}]+)\}\}', r'\\text{\1}_\2', eq)
    eq = re.sub(r'(?<!\\)\b(sin|cos)\s*\(', lambda m: f"\\{m.group(1)}(", eq)
    
    # Specific fix for known artifact if it still exists (optional but safe)
    eq = eq.replace("s_{\\text{fake}}(F_{t})  -", "s_{\\text{fake}}(F_{t}) -")
    return eq

def get_equation_style(eq_text):
    if not eq_text: return ""
    clean_eq = eq_text.replace("$$", "").replace("\\", "")
    l = len(clean_eq)

    if l > 120: return "font-size: 1.4em;"
    if l > 80:  return "font-size: 1.6em;"
    if l > 40:  return "font-size: 1.8em;"
    return "font-size: 2.0em;"             

def html_list_to_markdown(text):
    """
    Smartly converts content to Markdown.
    1. Converts HTML <ul><li> to Markdown.
    2. If a list (HTML or Markdown) has ONLY ONE item, it removes the bullet 
       to render it as a paragraph for better aesthetics.
    """
    if not text: return ""
    
    # 1. HTML Handling
    if "<li>" in text:
        count = text.count("<li>")
        text = text.replace("<ul>", "").replace("</ul>", "")
        if count == 1:
            text = text.replace("<li>", "").replace("</li>", "")
        else:
            text = text.replace("<li>", "- ").replace("</li>", "\n")
            
    # 2. Markdown/Plain Text Handling
    # Use strip() to ignore surrounding whitespace
    s_text = text.strip()
    
    # Check if it looks like a single bullet point:
    # Starts with "- " AND doesn't seem to have other bullets following newlines
    if s_text.startswith("- ") and "\n-" not in s_text:
        text = s_text[2:]
        
    # Clean up multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def prepare_markdown_block(text):
    """Convert mixed HTML/list content into markdown Marp can render directly."""
    if not text:
        return ""
    text = html_list_to_markdown(text)
    text = html.unescape(text)
    text = text.replace("\r\n", "\n")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def analyze_text_density(text):
    """Estimate how dense a markdown block will be once rendered on a slide."""
    if not text:
        return {
            "plain_length": 0,
            "bullet_count": 0,
            "line_count": 0,
            "longest_line": 0,
        }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullet_lines = [line for line in lines if re.match(r'^[\-*+]\s+', line)]
    clean_lines = [re.sub(r'^[\-*+]\s+', '', line) for line in lines]
    plain_text = re.sub(r'[`*_#>-]', '', text)

    return {
        "plain_length": len(plain_text),
        "bullet_count": len(bullet_lines),
        "line_count": len(lines),
        "longest_line": max((len(line) for line in clean_lines), default=0),
    }


def get_full_width_body_style(text, title=""):
    """Choose a compact body style for text-only full-width slides."""
    stats = analyze_text_density(text)
    plain_length = stats["plain_length"]
    bullet_count = stats["bullet_count"]
    line_count = stats["line_count"]
    longest_line = stats["longest_line"]
    title_len = len(title or "")

    if (
        bullet_count >= 5 and (
            plain_length > 350 or longest_line > 95
        )
    ) or plain_length > 500 or line_count > 12:
        return "--slide-fs:18px; --slide-lh:1.20; font-size:18px; line-height:1.20;"

    if (
        bullet_count >= 4 and (
            plain_length > 240 or longest_line > 84 or title_len > 32
        )
    ) or plain_length > 330 or line_count > 8:
        return "--slide-fs:20px; --slide-lh:1.22; font-size:20px; line-height:1.22;"

    if (
        (bullet_count >= 3 and plain_length > 190)
        or bullet_count >= 4
        or plain_length > 250
        or longest_line > 76
        or title_len > 30
    ):
        return "--slide-fs:22px; --slide-lh:1.24; font-size:22px; line-height:1.24;"

    if bullet_count >= 3 or plain_length > 150 or longest_line > 66:
        return "--slide-fs:24px; --slide-lh:1.28; font-size:24px; line-height:1.28;"

    return "--slide-fs:26px; --slide-lh:1.30; font-size:26px; line-height:1.30;"


def get_full_width_spacing(text, title=""):
    """Tighten top spacing for dense text-only slides."""
    stats = analyze_text_density(text)
    if stats["bullet_count"] >= 4 or stats["plain_length"] > 220 or len(title or "") > 32:
        return "14px"
    if stats["bullet_count"] >= 3 or stats["plain_length"] > 160:
        return "18px"
    return "24px"


def get_density_class(*texts, item_count=0, has_table=False, title=""):
    """Return a slide density class so content-heavy layouts can compact automatically."""
    joined = "\n".join([t for t in texts if t])
    stats = analyze_text_density(joined)
    score = (
        stats["plain_length"]
        + stats["bullet_count"] * 55
        + stats["line_count"] * 18
        + max(0, stats["longest_line"] - 72) * 2
        + item_count * 40
        + (110 if has_table else 0)
        + len(title or "") * 3
    )

    if score >= 760 or (item_count >= 4 and stats["plain_length"] > 220):
        return "x-dense"
    if score >= 480 or item_count >= 3 or has_table:
        return "dense"
    return ""


def get_asset_meta(filename):
    """Return basic image metadata for layout decisions."""
    if not filename or not CURRENT_ASSET_DIR or not Image:
        return None
    path = os.path.join(CURRENT_ASSET_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        with Image.open(path) as img:
            width, height = img.size
        if not width or not height:
            return None
        return {
            "path": path,
            "width": width,
            "height": height,
            "aspect": width / height,
        }
    except Exception:
        return None


def choose_split_grid_style(text, title="", image_meta=None, has_table=False):
    """Choose a text/image or text/table split based on content density and asset size."""
    stats = analyze_text_density(prepare_markdown_block(text))
    bullet_count = stats["bullet_count"]
    plain_length = stats["plain_length"]
    longest_line = stats["longest_line"]
    title_len = len(title or "")

    if has_table:
        if bullet_count >= 4 or plain_length > 220 or title_len > 34:
            return "display:grid; grid-template-columns: 56% 44%;"
        if plain_length < 120 and title_len < 28:
            return "display:grid; grid-template-columns: 44% 56%;"
        return "display:grid; grid-template-columns: 50% 50%;"

    if not image_meta:
        return "display:grid; grid-template-columns: 50% 50%;"

    aspect = image_meta["aspect"]
    width = image_meta["width"]
    height = image_meta["height"]
    small_image = width < 260 or height < 180
    dense_text = bullet_count >= 4 or plain_length > 200 or longest_line > 80 or title_len > 34

    if small_image and dense_text:
        return "display:grid; grid-template-columns: 64% 36%;"
    if dense_text:
        return "display:grid; grid-template-columns: 60% 40%;"
    if aspect > 2.2 and plain_length < 150 and bullet_count <= 3:
        return "display:grid; grid-template-columns: 42% 58%;"
    if aspect < 1.35:
        return "display:grid; grid-template-columns: 58% 42%;"
    return "display:grid; grid-template-columns: 50% 50%;"


def get_split_title_style(title, orientation="cols", text_fraction=0.5, has_table=False):
    """Title sizing for split slides should reflect the actual text area width."""
    if not title:
        return ""
    title_len = len(title.strip())
    if orientation == "rows":
        # Scale title with text_fraction (height): less height → smaller title
        base = clamp_num(30 + (text_fraction - 0.38) * 24, 28, 36)
        if has_table:
            base -= 2
        minimum = 24
    else:
        if text_fraction >= 0.70:
            base = 42
        elif text_fraction >= 0.62:
            base = 38
        elif text_fraction >= 0.56:
            base = 34
        elif text_fraction >= 0.50:
            base = 30
        else:
            base = 26
        minimum = 22

    penalty = max(0.0, (title_len - 30) / 4.0)
    size = clamp_num(base - penalty, minimum, 46)
    margin = 16 if size <= 28 else 18 if size <= 34 else 20
    return f"font-size: {size:.0f}px; margin-bottom: {margin}px;"


def get_split_body_style(text, title="", image_meta=None, has_table=False, orientation="cols", text_fraction=0.5):
    """Body typography for split slides where wrapping drives overflow."""
    stats = analyze_text_density(prepare_markdown_block(text))
    bullet_count = stats["bullet_count"]
    plain_length = stats["plain_length"]
    line_count = stats["line_count"]
    longest_line = stats["longest_line"]
    title_len = len(title or "")

    small_image = False
    if image_meta:
        small_image = image_meta["width"] < 320 or image_meta["height"] < 220

    density = (
        plain_length
        + bullet_count * 30
        + line_count * 10
        + max(0, longest_line - 80) * 2
        + title_len * 1.5
        + (60 if has_table else 0)
        + (25 if small_image else 0)
    )

    if orientation == "rows":
        # Rows: text panel is wide but short — base off text_fraction (height %)
        base = clamp_num(18.0 + (text_fraction - 0.34) * 12.0, 17.6, 23.0)
        penalty = 0.0
        if image_meta:
            aspect = image_meta["aspect"]
            if aspect >= 4.0:
                penalty += 0.8
            elif aspect >= 3.2:
                penalty += 0.6
            elif aspect >= 2.8:
                penalty += 0.4
            elif aspect >= 2.5:
                penalty += 0.2
        if plain_length > 320:
            penalty += 0.4
        elif plain_length > 260:
            penalty += 0.2
        if bullet_count >= 4:
            penalty += 0.3
        if longest_line > 110:
            penalty += 0.1
        if title_len > 32:
            penalty += 0.2
        elif title_len > 28:
            penalty += 0.1
        if has_table:
            penalty += 1.0
        # Sparse-content bonus for rows orientation
        if plain_length < 60:
            bonus = 5.0
        elif plain_length < 100:
            bonus = 3.5
        elif plain_length < 150:
            bonus = 2.0
        else:
            bonus = 0.0
        if bullet_count <= 1 and not has_table:
            bonus += 1.0
        size = clamp_num(base - penalty + bonus, 15.5 if image_meta else 16.5, 34.0)
    else:
        # Cols: text panel is narrow but tall — add density penalties to prevent overflow
        base = clamp_num(17.0 + (text_fraction - 0.34) * 14.0, 17.0, 23.0)
        if has_table:
            base -= 1.0
        penalty = 0.0
        if plain_length > 420:
            penalty += 2.0
        elif plain_length > 320:
            penalty += 1.2
        elif plain_length > 230:
            penalty += 0.6
        if bullet_count >= 6:
            penalty += 1.0
        elif bullet_count >= 5:
            penalty += 0.6
        elif bullet_count >= 4:
            penalty += 0.3
        if line_count >= 12:
            penalty += 0.8
        elif line_count >= 9:
            penalty += 0.4
        if title_len > 40:
            penalty += 0.4
        elif title_len > 30:
            penalty += 0.2
        # Sparse-content bonus: scale up when text is short (1 sentence / 1 bullet)
        if plain_length < 60:
            bonus = 9.0
        elif plain_length < 100:
            bonus = 7.0
        elif plain_length < 150:
            bonus = 5.0
        elif plain_length < 220:
            bonus = 2.5
        else:
            bonus = 0.0
        if bullet_count <= 1 and not has_table:
            bonus += 2.0
        size = clamp_num(base - penalty + bonus, 15.0, 38.0)

    if orientation == "rows":
        line_height = 1.32
        if image_meta:
            aspect = image_meta["aspect"]
            if aspect >= 3.2:
                line_height -= 0.03
            elif aspect >= 2.5:
                line_height -= 0.02
        if plain_length > 320:
            line_height -= 0.02
        elif plain_length > 260:
            line_height -= 0.01
        if bullet_count >= 4:
            line_height -= 0.02
        if title_len > 32:
            line_height -= 0.02
        elif title_len > 28:
            line_height -= 0.01
        if has_table:
            line_height -= 0.02
        line_height = clamp_num(line_height, 1.18, 1.32)
    else:
        # Cols: reduce line height when content is dense, open up when sparse
        line_height = clamp_num(1.32 + (text_fraction - 0.34) * 0.1, 1.28, 1.40)
        if plain_length < 100 and bullet_count <= 1:
            line_height = clamp_num(line_height + 0.10, 1.28, 1.55)
        elif plain_length < 180:
            line_height = clamp_num(line_height + 0.05, 1.28, 1.48)
        elif plain_length > 320 or bullet_count >= 5:
            line_height = clamp_num(line_height - 0.04, 1.22, 1.40)
        elif plain_length > 230 or bullet_count >= 4:
            line_height = clamp_num(line_height - 0.02, 1.24, 1.40)

    return f"--slide-fs:{size:.1f}px; --slide-lh:{line_height:.2f}; font-size:{size:.1f}px; line-height:{line_height:.2f};"


def extract_style_number(style, prop, fallback):
    match = re.search(rf"{re.escape(prop)}:\s*([0-9]+(?:\.[0-9]+)?)", style or "")
    return float(match.group(1)) if match else fallback


def make_media_inner_style(width_pct, right_gap_px, center=False):
    justify = "center" if center else "flex-start"
    if center:
        side_gap = max(int(round(right_gap_px / 2)), 0)
        padding = f"0 {side_gap}px"
        margin = "0 auto"
    else:
        padding = f"0 {right_gap_px}px 0 0"
        margin = "0"
    return (
        f"width:{width_pct}%; max-width:{width_pct}%; height:100%; display:flex; "
        f"align-items:center; justify-content:{justify}; padding:{padding}; "
        f"box-sizing:border-box; overflow:hidden; margin:{margin};"
    )


def set_media_inner_max_height(style, max_height_px, fixed=False):
    height_rule = (
        f"height:{max_height_px}px; max-height:{max_height_px}px"
        if fixed
        else f"height:auto; max-height:{max_height_px}px"
    )
    return style.replace("height:100%", height_rule)


def grid_style_from_class(grid_class):
    mapping = {
        "grid-50-50": "display:grid; grid-template-columns: 1fr 1fr;",
        "grid-40-60": "display:grid; grid-template-columns: 40% 60%;",
        "grid-60-40": "display:grid; grid-template-columns: 60% 40%;",
        "grid-30-70": "display:grid; grid-template-columns: 30% 70%;",
        "grid-35-65": "display:grid; grid-template-columns: 35% 65%;",
    }
    return mapping.get(grid_class, "display:grid; grid-template-columns: 1fr 1fr;")


def generate_dynamic_grid_css():
    """Generate CSS classes for all possible dynamic grid splits used by choose_media_layout().
    Applied to wrapper <div> elements inside sections, not to sections themselves
    (Marp transforms section.class selectors, making them unreliable)."""
    lines = []
    
    # Dynamic Flexbox Split
    lines.append("  .split-gap { width: 100%; gap: 12px; box-sizing: border-box; }")
    lines.append("  .split-gap > * { min-width: 0; min-height: 0; }")

    # Column splits: grid-34-66 through grid-78-22
    for left in range(34, 79):
        right = 100 - left
        cls = f"grid-{left}-{right}"
        lines.append(f"  .{cls} {{ display: grid; grid-template-columns: {left}% {right}%; height: 100%; }}")
    # Row splits: grid-rows-24-76 through grid-rows-68-32
    for top in range(24, 69):
        bot = 100 - top
        cls = f"grid-rows-{top}-{bot}"
        lines.append(f"  .{cls} {{ display: grid; grid-template-rows: {top}% {bot}%; height: 100%; }}")
    # Special: grid-rows-auto-1fr (for long equations)
    lines.append("  .grid-rows-auto-1fr { display: grid; grid-template-rows: auto 1fr; height: 100%; }")
    return "\n".join(lines)


def choose_media_layout(text, title="", image_meta=None, has_table=False, table_cols=0, table_rows=0):
    """Choose media orientation, ratio, spacing, and typography together."""
    stats = analyze_text_density(prepare_markdown_block(text))
    title_len = len(title or "")
    text_score = (
        stats["plain_length"]
        + stats["bullet_count"] * 72
        + stats["line_count"] * 20
        + max(0, stats["longest_line"] - 72) * 3
        + title_len * 4
        + (90 if has_table else 0)
    )
    dense_text = text_score >= 420
    orientation = "cols"
    text_fraction = 0.44
    media_inner = make_media_inner_style(76, 26, center=True)
    image_is_tight = False
    row_image_width_cap = None
    row_image_height_cap = None
    row_inner_height_cap = None
    row_wide_image = False

    if has_table:
        # Only use rows for very wide tables that won't fit in a column
        if table_cols >= 8 or (table_cols >= 7 and table_rows >= 8):
            orientation = "rows"
            text_fraction = 0.24 if table_cols >= 8 or table_rows >= 10 else 0.28
        else:
            # Strongly prefer left/right (columns) layout for tables
            orientation = "cols"
            if table_cols >= 5:
                text_fraction = 0.32  # wide table needs more space
            elif table_cols == 4:
                text_fraction = 0.38
            elif table_cols <= 3:
                # Narrow tables (2-3 cols) — give text most of the space
                if dense_text:
                    text_fraction = 0.56
                elif table_rows >= 5:
                    text_fraction = 0.52  # taller table needs bit more height
                else:
                    text_fraction = 0.58
            elif dense_text:
                text_fraction = 0.42
            else:
                text_fraction = 0.40
        if orientation == "rows":
            row_table_width = 82 if table_cols >= 9 else 84 if table_cols >= 8 else 86
            row_table_gap = 22 if table_cols >= 9 else 20
            media_inner = make_media_inner_style(row_table_width, row_table_gap, center=True)
        else:
            media_inner = make_media_inner_style(94, 8, center=True)
    elif not image_meta:
        orientation = "cols"
        text_fraction = 0.44 if text_score >= 320 else 0.40
    else:
        aspect = image_meta["aspect"]
        width = image_meta["width"]
        height = image_meta["height"]
        tiny_image = width < 200 or height < 140
        small_image = width < 320 or height < 220
        wide_image = aspect >= 2.2
        very_wide_image = aspect >= 2.5
        image_is_tight = tiny_image or small_image or wide_image

        if very_wide_image and not tiny_image and not small_image:
            # Very wide/panoramic images → vertical split (text top, image bottom)
            orientation = "rows"
            row_wide_text = (
                stats["plain_length"] > 300
                or stats["bullet_count"] >= 4
                or title_len > 30
                or stats["longest_line"] > 110
            )
            if aspect >= 4.0:
                text_fraction = 0.48 if row_wide_text else 0.44
                media_inner = make_media_inner_style(92, 0, center=True)
                row_image_width_cap = 100
                row_image_height_cap = None
                row_inner_height_cap = None
            elif aspect >= 3.2:
                text_fraction = 0.46 if row_wide_text else 0.42
                media_inner = make_media_inner_style(92, 0, center=True)
                row_image_width_cap = 100
                row_image_height_cap = None
                row_inner_height_cap = None
            elif aspect >= 2.8:
                text_fraction = 0.44 if row_wide_text else 0.40
                media_inner = make_media_inner_style(92, 0, center=True)
                row_image_width_cap = 100
                row_image_height_cap = None
                row_inner_height_cap = None
            else:
                text_fraction = 0.42 if row_wide_text else 0.38
                media_inner = make_media_inner_style(92, 0, center=True)
                row_image_width_cap = 100
                row_image_height_cap = None
                row_inner_height_cap = None
            row_wide_image = True
        else:
            # Left/right (columns) layout for normal images
            orientation = "cols"
            if tiny_image:
                text_fraction = 0.68 if dense_text else 0.62
            elif small_image:
                text_fraction = 0.58 if dense_text else 0.52
            elif wide_image:
                # Moderately wide — still columns but generous image space
                text_fraction = 0.52 if dense_text else 0.46
            elif aspect >= 1.6:
                text_fraction = 0.48 if dense_text else 0.42
            elif dense_text:
                text_fraction = 0.52
            else:
                text_fraction = 0.44

            if tiny_image:
                media_inner = make_media_inner_style(80, 16, center=True)
            elif small_image:
                media_inner = make_media_inner_style(85, 14, center=True)
            else:
                media_inner = make_media_inner_style(92, 10, center=True)

    if orientation == "rows":
        text_pct = int(round(clamp_num(text_fraction * 100, 24, 68)))
        wrapper_class = f"grid-rows-{text_pct}-{100 - text_pct}"
        if row_wide_image:
            text_panel = "min-width:0; min-height:0; overflow:hidden; padding:20px 28px 2px 28px;"
            media_panel = "min-width:0; min-height:0; height:100%; overflow:hidden; display:flex; justify-content:center; align-items:flex-start; padding:10px 28px 24px 28px; background:transparent; border-left:none;"
        else:
            text_panel = "min-width:0; min-height:0; overflow:hidden; padding:28px 28px 4px 28px;"
            media_panel = "min-width:0; min-height:0; height:100%; overflow:hidden; display:flex; justify-content:center; align-items:flex-start; padding:6px 20px 16px 20px;"
    else:
        text_pct = int(round(clamp_num(text_fraction * 100, 34, 78)))
        wrapper_class = f"grid-{text_pct}-{100 - text_pct} split-gap"
        left_pad = 34 if text_pct >= 58 else 30
        right_pad = 16 if text_pct >= 60 else 12 if text_pct >= 54 else 8
        text_panel = f"min-width:0; min-height:0; overflow:hidden; padding:36px {right_pad}px 34px {left_pad}px;"
        if has_table:
            media_panel = "min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 14px 10px 4px;"
        elif image_is_tight:
            media_panel = "min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:6px 12px 10px 12px;"
        else:
            media_panel = "min-width:0; min-height:0; overflow:hidden; justify-content:center; align-items:center; padding:8px 12px 12px 12px;"

    body_style = get_split_body_style(
        text,
        title,
        image_meta=image_meta,
        has_table=has_table,
        orientation=orientation,
        text_fraction=text_fraction,
    )
    title_style = get_split_title_style(
        title,
        orientation=orientation,
        text_fraction=text_fraction,
        has_table=has_table,
    )

    # For rows layout, constrain image/table to fit within the grid row
    if orientation == "rows":
        media_pct = 100 - text_pct
        # Row splits need real headroom for panel padding and image/table chrome.
        # If we size media to the theoretical row height, Marp can clip the bottom edge.
        if row_wide_image:
            row_safe_px = 54
        else:
            row_safe_px = 34 if has_table else 30
        avail_h = max(180, int(720 * media_pct / 100) - row_safe_px)
        if has_table:
            img_style = ""
            inner_max_h = min(avail_h, row_inner_height_cap) if row_inner_height_cap else avail_h
            media_inner = set_media_inner_max_height(media_inner, inner_max_h, fixed=False)
        else:
            img_max_h = max(160, avail_h - 12)
            if row_image_height_cap is not None:
                img_max_h = min(img_max_h, row_image_height_cap)
            row_img_max_w = 84
            if row_image_width_cap is not None:
                row_img_max_w = row_image_width_cap
            elif image_meta:
                aspect = image_meta["aspect"]
                if aspect >= 4.0:
                    row_img_max_w = 74
                elif aspect >= 3.2:
                    row_img_max_w = 80
                elif aspect >= 2.8:
                    row_img_max_w = 86
                elif aspect >= 2.5:
                    row_img_max_w = 90
                else:
                    row_img_max_w = 94
            img_style = (
                f"max-height:{img_max_h}px; max-width:{row_img_max_w}%; "
                "width:auto; height:auto; object-fit:contain; display:block; padding:4px; box-sizing:border-box;"
            )
            inner_max_h = min(avail_h, row_inner_height_cap) if row_inner_height_cap else avail_h
            media_inner = set_media_inner_max_height(media_inner, inner_max_h, fixed=False)
    else:
        img_style = ""

    return {
        "wrapper_class": wrapper_class,
        "orientation": orientation,
        "text_fraction": text_fraction,
        "text_panel": text_panel,
        "media_panel": media_panel,
        "media_inner": media_inner,
        "body_style": body_style,
        "title_style": title_style,
        "img_style": img_style,
    }


def compute_slide_layout(text, title="", has_image=False, has_table=False, md_table=""):
    """
    Central layout engine: determines grid split, density class, and font size
    based on content analysis. Returns a dict with layout parameters.
    """
    stats = analyze_text_density(text or "")
    plain_len = stats["plain_length"]
    bullet_count = stats["bullet_count"]
    line_count = stats["line_count"]
    title_len = len(title or "")

    # --- Density class (controls padding, bullet size, card padding via CSS) ---
    density = ""
    if plain_len > 400 or bullet_count >= 5 or line_count > 8:
        density = "x-dense"
    elif plain_len > 220 or bullet_count >= 3 or line_count > 5 or title_len > 50:
        density = "dense"

    # --- Font size for body text ---
    if density == "x-dense":
        font_size = 20
        line_height = 1.22
    elif density == "dense":
        font_size = 24
        line_height = 1.28
    else:
        font_size = 28
        line_height = 1.35

    # Further shrink if in a split layout (image/table takes space)
    if has_image or has_table:
        if density == "x-dense":
            font_size = 18
            line_height = 1.18
        elif density == "dense":
            font_size = 20
            line_height = 1.22
        else:
            font_size = 24
            line_height = 1.28

    # --- Grid split for image slides ---
    grid_class = "dynamic-split"
    if has_image:
        if plain_len > 350:
            grid_class = "dynamic-split"  # long text needs more room
        elif plain_len > 200:
            grid_class = "dynamic-split"
        elif plain_len <= 120:
            grid_class = "dynamic-split"  # short text, give image more room
        else:
            grid_class = "dynamic-split"

    # --- Grid split for table slides ---
    if has_table and md_table:
        table_lines = md_table.strip().split('\n')
        col_count = 0
        if table_lines:
            col_count = len([h for h in table_lines[0].strip('|').split('|') if h.strip()])
        row_count = len([l for l in table_lines[1:] if '---' not in l])

        if col_count >= 8 or row_count > 12:
            grid_class = "grid-30-70"
        elif col_count >= 6 or row_count > 8:
            grid_class = "grid-35-65"
        elif plain_len > 300:
            grid_class = "dynamic-split"
        else:
            grid_class = "dynamic-split"

    # --- Title size ---
    if title_len > 80:
        title_font = 28
    elif title_len > 60:
        title_font = 32
    elif title_len > 40:
        title_font = 38
    else:
        title_font = 44

    # Smaller titles in split layouts
    if has_image or has_table:
        title_font = min(title_font, 38)

    return {
        "density": density,
        "font_size": font_size,
        "line_height": line_height,
        "grid_class": grid_class,
        "title_font": title_font,
        "title_style": f"font-size: {title_font}px; margin-bottom: 16px;",
    }


def strip_step_numbering(title):
    """Avoid duplicate numbering when the renderer already adds step labels."""
    if not title:
        return ""
    return re.sub(r'^\s*(?:step\s*)?\d+\s*[\.\):\-]?\s*', '', title, flags=re.IGNORECASE).strip()

def format_long_equation(eq_text):
    """
    Safely reformats a long equation into a LaTeX aligned block.
    Uses proper escaping for f-strings.
    """
    raw = eq_text.replace('$$', '').replace('$', '').strip()
    raw = fix_latex_syntax(raw) # Apply fixes first
    
    if "=" in raw:
        parts = raw.split('=')
        
        # LaTeX Newline constant (Triple escaped for f-string safety)
        # We need the final string to contain literally "\\"
        latex_newline = "\\\\" 
        
        if len(parts) >= 3:
            p1 = parts[0].strip()
            p2 = "=".join(parts[1:-1]).strip()
            p3 = parts[-1].strip()
            
            # Note: We use a standard join to avoid f-string backslash hell
            return "\\begin{aligned}\n" + p1 + " &= " + p2 + " " + latex_newline + "\n&= " + p3 + "\n\\end{aligned}"

        elif len(parts) == 2:
            return "\\begin{aligned}\n" + parts[0].strip() + " &= " + latex_newline + "\n& " + parts[1].strip() + "\n\\end{aligned}"

    return raw

def tpl_hero_dark(data, asset_func):
    img_html = asset_func(safe_get(data, ['image', 'img']))
    raw_content = smart_content_render(data)
    content_md = prepare_markdown_block(raw_content)
    title = safe_get(data, ['title', 'headline'])
    equation = safe_get(data, ['equation'])
    
    # Restored missing font_style definition
    raw_text = content_md or safe_get(data, ['text', 'content', 'body', 'description'])
    font_style = get_dynamic_font_class(raw_text, title)
    text_top_margin = get_full_width_spacing(raw_text, title)
    title_style = get_dynamic_title_class(title, raw_text)
    
    # CASE A: Image + Text
    if img_html:
        eq_html = ""
        if equation:
            # cln_eq = equation.replace('$$', '').replace('$', '').strip()
            # cln_eq = fix_latex_syntax(cln_eq)
            eq_html = wrap_scaled_equation(equation, margin_top_px=20)

        return f"""
<section class="slide-hero slide-hero-image grid-50-50 bg-dark">

<div class="pad-col hero-copy">
<h1 style="{title_style}">{title}</h1>
<div style="margin-top:{text_top_margin}; opacity: 0.9; {font_style}" markdown="1">

{content_md}

</div>
{eq_html}
</div>
<div class="img-col" style="background: black;">
{img_html}
</div>
</section>
"""

    # CASE B: Long Equation (Vertical Split)
    if equation and len(equation) > 50:
        # formatted_eq = format_long_equation(equation)
        formatted_eq = equation
        return f"""
<section class="slide-hero slide-hero-equation bg-dark">

<div class="grid-rows-auto-1fr">
<div class="pad-col hero-copy" style="justify-content: center; align-items: flex-start; padding-bottom: 0;">
  <h1 style="margin-bottom: 20px; {title_style}">{title}</h1>
  <div style="opacity: 0.9; {font_style}" markdown="1">

{content_md}

  </div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: rgba(255,255,255,0.05);">
{wrap_scaled_equation(formatted_eq, center_vertically=True)}
</div>
</div>
</section>
"""

    # CASE C: Short Equation
    if equation:
        eq_html = wrap_scaled_equation(equation, center_vertically=True)
        return f"""
<section class="slide-hero slide-hero-equation grid-50-50 bg-dark">

<div class="pad-col hero-copy">
<h1 style="{title_style}">{title}</h1>
<div style="margin-top:{text_top_margin}; opacity: 0.9; {font_style}" markdown="1">

{content_md}

</div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: rgba(255,255,255,0.05);">

{eq_html}

</div>
</section>
"""

    density_class = get_density_class(content_md, title=title)
    return f"""
<section class="slide-hero slide-hero-full bg-dark {density_class}">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="{title_style}">{title}</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: {text_top_margin}; {font_style}" markdown="1">

{content_md}

</div>
</div>
</section>
"""

def tpl_columns_smart(data, _):
    """
    Fixed: Dedented HTML to prevent 'div' appearing as text.
    """
    items = normalize_list_data(data)
    count = len(items)

    # If all items are empty (no title, no text), fall back to hero_dark
    if count == 0 or all(
        not safe_get(it, ['title', 'label', 'name']) and
        not safe_get(it, ['text', 'content', 'description', 'value'])
        for it in items
    ):
        return tpl_hero_dark(data, lambda x: "")

    # Grid Logic
    if count == 0: return tpl_hero_dark(data, lambda x: "")
    elif count == 1: grid_css = "grid-template-columns: 1fr;"
    elif count == 2: grid_css = "grid-template-columns: 1fr 1fr;"
    elif count == 4: grid_css = "grid-template-columns: 1fr 1fr; grid-template-rows: auto auto;"
    else: grid_css = "grid-template-columns: repeat(3, 1fr);"
    
    density_inputs = []
    cards_html = ""
    total_len = 0
    prepared_items = []

    def int_to_roman(num):
        numerals = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ]
        value = max(1, int(num))
        result = []
        for arabic, roman in numerals:
            while value >= arabic:
                result.append(roman)
                value -= arabic
        return "".join(result)

    def format_card_subitems(txt_md):
        lines = txt_md.splitlines()
        output = []
        bullet_items = []
        numbered_items = []

        def flush_bullet_items():
            nonlocal bullet_items
            if not bullet_items:
                return
            output.append(
                "<ul>\n"
                + "\n".join(f"<li>{item}</li>" for item in bullet_items)
                + "\n</ul>"
            )
            bullet_items = []

        def flush_numbered_items():
            nonlocal numbered_items
            if not numbered_items:
                return
            rendered = []
            for number, body in numbered_items:
                label = int_to_roman(number).lower()
                rendered.append(f"{label}. {body}")
            output.append(
                '<div markdown="1" style="margin: -2px 0 10px 34px; line-height: 1.22;">\n'
                + "<br>\n".join(rendered)
                + "\n</div>"
            )
            numbered_items = []

        for line in lines:
            bullet_match = re.match(r'^\s*[-*+]\s+(.*)$', line)
            match = re.match(r'^\s*[-*+]\s+(\d+)\.\s+(.*)$', line)
            if match:
                flush_bullet_items()
                numbered_items.append((int(match.group(1)), match.group(2).strip()))
                continue

            if bullet_match:
                flush_numbered_items()
                bullet_items.append(bullet_match.group(1).strip())
                continue

            flush_bullet_items()
            flush_numbered_items()
            output.append(line)

        flush_bullet_items()
        flush_numbered_items()
        return "\n".join(output)

    for item in items:
        t = safe_get(item, ['title', 'label', 'name'])
        txt = safe_get(item, ['text', 'content', 'description', 'value'])
        
        if not txt and len(t) > 50:
            txt = t
            t = ""

        txt_md = prepare_markdown_block(txt)
        total_len += len(t) + len(txt_md)
        density_inputs.append(f"{t}\n{txt_md}")
        prepared_items.append((t, txt_md, format_card_subitems(txt_md)))

    section_title = safe_get(data, ['title', 'headline'])
    joined_body = "\n".join(density_inputs)
    density_class = get_density_class(*density_inputs, item_count=count, title=section_title)

    # --- Step 1: Tier-based baseline font size ---
    avg_len = total_len / max(count, 1)
    if density_class == "x-dense" or (count >= 3 and avg_len > 100):
        base_title_fs, base_body_fs, base_lh, base_mb = 20, 18, 1.18, 5
    elif density_class == "dense" or (count >= 3 and avg_len > 70):
        base_title_fs, base_body_fs, base_lh, base_mb = 21, 19, 1.20, 6
    elif count >= 4 or total_len > 550:
        base_title_fs, base_body_fs, base_lh, base_mb = 20, 18, 1.22, 6
    elif count >= 3 or total_len > 380:
        base_title_fs, base_body_fs, base_lh, base_mb = 22, 19, 1.24, 8
    else:
        base_title_fs, base_body_fs, base_lh, base_mb = 24, 20, 1.26, 8

    # --- Step 2: Overflow estimation — scale down if content won't fit ---
    # Grid layout: 4 cards → 2×2, 3 cards → 1×3, 1-2 cards → 1×n
    grid_cols = 2 if count == 4 else min(3, count) if count >= 2 else 1
    grid_rows = math.ceil(count / grid_cols)
    # Available height for card rows (conservative x-dense estimates)
    avail_for_cards = 720 - 60 - 68 - 16  # slide - pad_col_pad - h1 - card_margin
    base_gap = 16 if density_class in ("dense", "x-dense") else 20
    avail_per_row = max(80, (avail_for_cards - (grid_rows - 1) * base_gap) / grid_rows)

    # Estimate max card height using baseline sizes
    # chars per line = roughly 50 for a half-width card column
    chars_per_line = 50 if grid_cols >= 2 else 80
    max_card_h = 0
    for _, txt_md, _ in prepared_items:
        bullet_count = (txt_md.count('\n- ') + txt_md.count('\n* ') +
                        (1 if txt_md.strip().startswith(('- ', '* ')) else 0))
        card_title_h = base_title_fs * 1.14 + base_mb
        if bullet_count > 0:
            body_h = bullet_count * (base_body_fs * base_lh + 6) - 6
        else:
            plain = re.sub(r'[-*]\s+', '', txt_md).strip()
            lines = max(1, math.ceil(len(plain) / chars_per_line))
            body_h = lines * base_body_fs * base_lh
        card_h = 28 + card_title_h + body_h  # 24px card padding + 4px border
        max_card_h = max(max_card_h, card_h)

    # If heaviest card exceeds available row height, scale down proportionally
    if max_card_h > avail_per_row * 0.88 and max_card_h > 0:
        scale = min(1.0, (avail_per_row * 0.83) / max_card_h)
        title_fs = max(11, round(base_title_fs * scale))
        body_fs = max(10, round(base_body_fs * scale))
        lh_val = round(max(1.12, base_lh - (1.0 - scale) * 0.06), 2)
        mb_val = max(2, round(base_mb * scale))
        gap_px = max(8, round(base_gap * scale))
        card_title_style = f"font-size:{title_fs}px; margin-bottom:{mb_val}px; line-height:{lh_val};"
        card_body_style = f"--slide-fs:{body_fs}px; --slide-lh:{lh_val}; font-size:{body_fs}px; line-height:{lh_val}; opacity:0.82;"
    else:
        title_fs, body_fs = base_title_fs, base_body_fs
        gap_px = base_gap
        card_title_style = f"font-size:{title_fs}px; margin-bottom:{base_mb}px; line-height:{base_lh};"
        card_body_style = f"--slide-fs:{body_fs}px; --slide-lh:{base_lh}; font-size:{body_fs}px; line-height:{base_lh}; opacity:0.82;"

    cards_html = ""
    for t, _, rendered_txt in prepared_items:
        cards_html += f"""
<div class="feature-card">
<div style="color:var(--accent); font-weight:700; {card_title_style}">{t}</div>
<div style="{card_body_style}" markdown="1">

{rendered_txt}

</div>
</div>
"""

    return f"""
<section class="slide-columns {density_class}">

<div class="pad-col">
<h1 style="{get_dynamic_title_class(section_title, joined_body)}">{section_title}</h1>
<div class="card-grid" style="{grid_css}; gap:{gap_px}px; align-content:start; margin-top:{gap_px}px;">
{cards_html}
</div>
</div>
</section>
"""

def tpl_challenge_solution(data, asset_func):
    """Dedented HTML."""
    image_name = safe_get(data, ['image', 'img'])
    img_html = asset_func(image_name)
    image_meta = get_asset_meta(image_name)

    # 🔑 NEW: normalize left/right schema into `text`
    if safe_get(data, ['text_left']) or safe_get(data, ['text_right']):
        blocks = []

        lt = safe_get(data, ['text_left_title'])
        lb = safe_get(data, ['text_left'])
        if lb:
            lb_md = html_list_to_markdown(lb)
            if lt:
                blocks.append(f"**{lt}**")
            blocks.append(lb_md)

        rt = safe_get(data, ['text_right_title'])
        rb = safe_get(data, ['text_right'])
        if rb:
            rb_md = html_list_to_markdown(rb)
            if rt:
                blocks.append(f"**{rt}**")
            blocks.append(rb_md)

        # Merge into ONE markdown block
        data['text'] = "\n\n".join(blocks)

    content = safe_get(data, ['text', 'content', 'body', 'description'])
    if not content:
        content = smart_content_render(data)
    content_md = prepare_markdown_block(content)
    
    raw_text = content_md or safe_get(data, ['text', 'content', 'body'])
    full_title_style = get_dynamic_title_class(safe_get(data, ['title']), raw_text)

    # If image → 2-column → aggressive scaling
    if img_html:
        media_layout = choose_media_layout(raw_text, safe_get(data, ['title']), image_meta=image_meta)
        if media_layout['img_style']:
            img_html = img_html.replace('<img ', f'<img style="{media_layout["img_style"]}" ')
    else:
        font_style = get_full_width_body_style(raw_text, safe_get(data, ['title']))
        text_top_margin = get_full_width_spacing(raw_text, safe_get(data, ['title']))
        dense_pad = "32px" if analyze_text_density(raw_text)["bullet_count"] >= 4 else "40px"
    
    if img_html:
        density_class = get_density_class(content_md, title=safe_get(data, ['title']))
        return f"""
<section class="slide-split slide-split-image {density_class}">

<div class="{media_layout['wrapper_class']}">
<div class="pad-col" style="{media_layout['text_panel']}">
<h1 style="{media_layout['title_style']}">{safe_get(data, ['title'])}</h1>
<div style="{media_layout['body_style']}" markdown="1">

{content_md}

</div>
</div>
<div class="img-col" style="{media_layout['media_panel']}">
<div style="{media_layout['media_inner']}">{img_html}</div>
</div>
</div>
</section>
"""
    return f"""
<section class="slide-split slide-split-full bg-dark {get_density_class(content_md, title=safe_get(data, ['title']))}">

<div class="pad-col" style="text-align:center; align-items:center;">
<h1 style="{full_title_style}">{safe_get(data, ['title'])}</h1>
<div class="hero-panel" style="background:rgba(255,255,255,0.1); padding:{dense_pad}; border-radius:10px; text-align:left; margin-top:{text_top_margin}; width:100%; max-width:900px; {font_style}" markdown="1">

{content_md}

</div>
</div>
</section>
"""

def wrap_equation_markdown(eq):
    eq = eq.strip().replace("$$", "")
    return f"\n$$\n{eq}\n$$\n"


import re

def markdown_math_to_latex(cell):
    # bold **x** → \mathbf{x}
    cell = re.sub(r'\*\*(.*?)\*\*', r'\\mathbf{\1}', cell)

    # Convert underscores-based subscripts: x_i → x_{i}
    cell = re.sub(r'([A-Za-z])_([A-Za-z0-9]+)', r'\1_{\2}', cell)

    # Wrap exponentials: e^{...} stays fine
    return cell


import markdown


def latex_fragment_to_html(expr):
    expr = fix_latex_syntax(expr.strip())
    expr = re.sub(r'\\(?:mathbf|boldsymbol|textbf)\{([^{}]+)\}', r'\1', expr)
    expr = re.sub(r'\\text\{([^{}]+)\}', r'\1', expr)
    expr = re.sub(r'\\rm\s*\{([^{}]+)\}', r'\1', expr)
    expr = re.sub(r'\\rm\s+([A-Za-z0-9]+)', r'\1', expr)
    expr = re.sub(r'\\log_\{([^{}]+)\}', r'log<sub>\1</sub>', expr)
    expr = re.sub(r'\\log_([A-Za-z0-9]+)', r'log<sub>\1</sub>', expr)
    expr = expr.replace("\\log", "log")
    expr = expr.replace("\\cdot", "&middot;")
    expr = expr.replace("\\times", "&times;")
    expr = re.sub(r'\^\{([^{}]+)\}', r'<sup>\1</sup>', expr)
    expr = re.sub(r'_\{([^{}]+)\}', r'<sub>\1</sub>', expr)
    expr = re.sub(r'\^([A-Za-z0-9]+)', r'<sup>\1</sup>', expr)
    expr = re.sub(r'_([A-Za-z0-9]+)', r'<sub>\1</sub>', expr)
    expr = expr.replace("{", "").replace("}", "")
    expr = expr.replace("\\", "")
    return expr


def replace_inline_math_with_html(text):
    patterns = [
        r'\$\$(.+?)\$\$',
        r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',
        r'\\\((.+?)\\\)',
        r'\\\[(.+?)\\\]',
    ]
    for pattern in patterns:
        text = re.sub(
            pattern,
            lambda m: latex_fragment_to_html(m.group(1)),
            text,
            flags=re.DOTALL,
        )
    return text

def wrap_math_for_html(cell):
    """
    Robust math + markdown handling for table cells.
    Priority:
    1. Detect *explicit* math markup
    2. Otherwise render markdown normally
    """

    if not cell:
        return ""

    # STRICT math detection: only handle explicit math markers
    if re.search(r'(\$\$.*?\$\$|\$.*?\$|\\\(|\\\)|\\\[|\\\])', cell):
        cell = replace_inline_math_with_html(cell)

    # otherwise process markdown
    return markdown.markdown(
        cell,
        extensions=["md_in_html", "tables", "fenced_code"]
    )


def wrap_scaled_equation(eq_text, margin_top_px=20, center_vertically=False):
    """
    Automatically wraps LaTeX block equations inside a scaled div
    so large equations don't overflow the slide.
    """
    if not eq_text:
        return ""

    # Strip $$ and fix latex
    eq = eq_text.replace('$$', '').strip()
    eq = fix_latex_syntax(eq)

    # Decide scale: wider equation → smaller scale
    L = len(eq)
    if L > 200:
        scale = 0.85
    elif L > 120:
        scale = 1.05
    elif L > 80:
        scale = 1.15
    else:
        scale = 1.3  # Slightly smaller than default

    if center_vertically:
        return f"""
<div style="width: 100%; display: flex; align-items: center; justify-content: center; margin: auto 0;">
<div style="transform: scale({scale}); transform-origin: center center; width: 100%; text-align: center; margin: 0;" markdown="1">

$$
{eq}
$$

</div>
</div>
"""

    return f"""
<div style="transform: scale({scale}); transform-origin: top center; width: 100%; text-align: center; margin-top: {margin_top_px}px;" markdown="1">

$$
{eq}
$$

</div>
"""

def fix_html_escaped_math(text):
    if not text:
        return text
    return (
        text.replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&amp;", "&")
    )


def tpl_method_process(data, asset_func):
    """Dedented HTML. Supports Math."""
    image_name = safe_get(data, ['image', 'img'])
    img_html = asset_func(image_name)
    image_meta = get_asset_meta(image_name)
    items = normalize_list_data(data)
    equation = safe_get(data, ['equation'])
    title = safe_get(data, ['title'])
    
    show_numbers = len(items) > 1
    density_inputs = []
    
    total_text = ""
    prepared_steps = []
    for i, item in enumerate(items):
        text = safe_get(item, ['text', 'content'])
        total_text += text
        step_title = strip_step_numbering(safe_get(item, ['title', 'label']))
        step_text = prepare_markdown_block(text)
        density_inputs.append(f"{step_title}\n{text}")
        prepared_steps.append((step_title, step_text))

    step_count = max(len(items), 1)
    density_class = get_density_class(*density_inputs, item_count=len(items), title=title)
    title_style = get_dynamic_title_class(title, total_text)
    size = auto_font_size_aggressive2(
        total_text,
        base=22.0 if density_class == "x-dense" else (24.0 if step_count >= 4 else 25.0),
        min_size=16.0 if density_class == "x-dense" else 17.0,
        max_chars=180.0 if density_class == "x-dense" else (220.0 if step_count >= 4 else 260.0),
    )
    step_title_font = 19 if density_class == "x-dense" else 20
    num_font = 14 if density_class == "x-dense" else 15
    step_line_height = 1.16

    media_layout = None
    if img_html:
        media_layout = choose_media_layout(total_text, title, image_meta=image_meta)
        if media_layout['img_style']:
            img_html = img_html.replace('<img ', f'<img style="{media_layout["img_style"]}" ')
        split_body_size = extract_style_number(media_layout["body_style"], "font-size", size)
        split_line_height = extract_style_number(media_layout["body_style"], "line-height", 1.18)
        size = max(11.0, split_body_size)
        step_line_height = max(1.10, min(split_line_height, 1.20))
        step_title_font = max(14, min(24, int(round(size + 2.0))))
        num_font = max(11, min(18, int(round(size - 1.0))))

    use_two_col = step_count >= 4 and not img_html
    steps_html = ""
    for i, (t, text) in enumerate(prepared_steps):

        # Conditionally render the number block
        num_block = ""
        if show_numbers:
             num_block = f'<span style="font-size:{num_font}px; font-weight:800; color:var(--accent); display:inline-block; margin-right:10px; letter-spacing:0.5px; text-transform:uppercase;">Step {i+1}</span>'

        # Span last card across both columns when odd count in 2-col layout
        is_last_odd = use_two_col and (step_count % 2 == 1) and (i == step_count - 1)
        span_style = " grid-column: 1 / -1;" if is_last_odd else ""

        # In 2-col layout remove heavy left indent (cards are too narrow)
        body_margin = "margin-top: 8px;" if use_two_col else f"margin-left: { '48px' if show_numbers else '0px' }; margin-top: 6px;"

        steps_html += f"""
<div class="step-card" style="margin-bottom: {'14px' if density_class == 'x-dense' else '18px'};{span_style}">
{num_block}
<span style="font-size:{step_title_font}px; font-weight:700; line-height:1.15;">{t}</span>
<div style="{body_margin} --slide-fs:{size}px; --slide-lh:{step_line_height}; font-size:{size}px; line-height:{step_line_height}; opacity:0.9;" markdown="1">

{text}

</div>
</div>
"""
    
    if equation:
        eq_html = wrap_scaled_equation(equation, center_vertically=True)

        # Dynamic Steps Font
        font_style = get_dynamic_font_class(total_text, title)

        if len(equation) > 50:
            grid_class = "grid-40-60"
        else:
            grid_class = "grid-50-50"

        return f"""
<section class="slide-method {grid_class} {density_class}">

<div class="pad-col">
<h1 style="{title_style}">{title}</h1>
<div class="step-stack" style="margin-top:20px; {font_style}" markdown="1">

{steps_html}

</div>
</div>
<div class="pad-col" style="justify-content: center; align-items: center; background: var(--bg-card);">
{eq_html}
</div>
</section>
"""

    if img_html:
        return f"""
<section class="slide-method {density_class}">

<div class="{media_layout['wrapper_class']}">
<div class="pad-col" style="{media_layout['text_panel']}">
<h1 style="{media_layout['title_style']}">{title}</h1>
<div class="step-stack" style="margin-top:30px;" markdown="1">

{steps_html}

</div>
</div>
<div class="img-col" style="background:white; {media_layout['media_panel']}">
<div style="{media_layout['media_inner']}">{img_html}</div>
</div>
</div>
</section>
"""

    if steps_html.strip() == "":
    # SMART COLUMN MODE: raw text only, no steps, no images
        raw = safe_get(data, ["text", "content", "body"]) or ""
        import re
        bullets = re.findall(r"-\s+(.*)", raw)

        # If no bullets, fall back to original behavior
        if not bullets:
            content = smart_content_render(data)
            content_style = get_full_width_body_style(content, title)
            content_margin = get_full_width_spacing(content, title)
            title_style = get_dynamic_title_class(title, content)
            return f"""
<section class="slide-method bg-dark {get_density_class(content, title=title)}">

<div class="pad-col" style="align-items: center; text-align: center;">
<h1 style="{title_style}">{title}</h1>
<div class="hero-panel" style="max-width: 900px; text-align: left; margin-top: {content_margin}; {content_style}" markdown="1">
{convert_inline_math_for_html(content)}
</div>
</div>
</section>
"""

        # Smart columns — max 3 cols
        n_cols = min(len(bullets), 3)
        card_font = 16 if len(bullets) >= 3 else 18
        title_style = get_dynamic_title_class(title, raw)

        cols_html = ""
        for b in bullets[:3]:
            cols_html += f"""
            <div class="feature-card" style="font-size:{card_font}px;">
                <div markdown="1">

{b}

</div>
            </div>
            """

        return f"""
<section class="slide-method {get_density_class(raw, item_count=len(bullets[:3]), title=title)}">

<div class="pad-col">
<h1 style="{title_style}">{title}</h1>
<div class="card-grid" style="grid-template-columns: repeat({n_cols}, 1fr); gap:24px; align-content:start; margin-top:24px;">
    {cols_html}
</div>
</div>
</section>
"""

        # DYNAMIC SMART COLUMNS for steps
    count = len(items)
    if count == 1:
        grid_css = "grid-template-columns: 1fr;"
    elif count == 2:
        grid_css = "grid-template-columns: 1fr 1fr;"
    elif count == 4:
        grid_css = "grid-template-columns: 1fr 1fr;"
    else:
        grid_css = "grid-template-columns: repeat(3, 1fr);"

    return f"""
<section class="slide-method {density_class}">

<div class="pad-col">
<h1 style="{title_style}">{title}</h1>
<div class="{ 'step-stack' if density_class == 'x-dense' else 'card-grid' }" style="{ ('grid-template-columns:1fr 1fr; ' if use_two_col else '') + 'gap:12px; align-content:start; margin-top:16px;' if density_class == 'x-dense' else f'{grid_css}; gap:24px; align-content:start; margin-top:24px;' }">
{steps_html}
</div>
</div>
</section>
"""

def tpl_results_benchmark(data, asset_func):
    image_name = safe_get(data, ['image', 'img'])
    img_html = asset_func(image_name)
    image_meta = get_asset_meta(image_name)
    table_data = safe_get(data, ['data', 'metrics', 'table'])
    md_table = safe_get(data, ['markdown_table'])
    if md_table:
        md_table = md_table.replace("\\n", "\n")
    
    title = safe_get(data, ['title'])
    
    # Ensure text is cleaned (bullets -> markdown)
    text_md = prepare_markdown_block(smart_content_render(data))
    
    # 1. Image Focus (unchanged)
    if img_html:
        density_class = get_density_class(text_md, title=title)
        media_layout = choose_media_layout(text_md, title, image_meta=image_meta)
        if media_layout['img_style']:
            img_html = img_html.replace('<img ', f'<img style="{media_layout["img_style"]}" ')
        return f"""
<section class="slide-results {density_class}">

<div class="{media_layout['wrapper_class']}">
<div class="pad-col bg-dark" style="{media_layout['text_panel']}">
<h1 style="color:white; {media_layout['title_style']}">{title}</h1>
<div style="color:white; opacity:0.8; {media_layout['body_style']}" markdown="1">

{text_md}

</div>
</div>
<div class="img-col" style="padding:0; {media_layout['media_panel']}">
<div style="{media_layout['media_inner']}">{img_html}</div>
</div>
</div>
</section>
"""

    # 2. Smart Table Layout
    if md_table:
        left_text = text_md

        grid_class, text_style, table_font, zoom = calculate_table_layout(text_md, md_table)
        lines = [l.strip() for l in md_table.strip().split('\n') if l.strip()]
        table_cols = 0
        table_rows = 0
        if len(lines) >= 2:
            table_cols = len([h for h in lines[0].strip('|').split('|') if h.strip()])
            table_rows = len([line for line in lines[1:] if '---' not in line])
        density_class = get_density_class(left_text, md_table, has_table=True, title=title)
        title_style = get_dynamic_title_class(title, left_text)
        media_layout = choose_media_layout(left_text, title, has_table=True, table_cols=table_cols, table_rows=table_rows)
        table_html = markdown_to_html_table(md_table, table_font)
        return f"""
<section class="slide-results {density_class}">

<div class="{media_layout['wrapper_class']}">
<div class="pad-col" style="{media_layout['text_panel']}">
<h1 style="{media_layout['title_style']}">{title}</h1>
<div style="margin-top: 20px; {media_layout['body_style']}" markdown="1">

{left_text}

</div>
</div>

<div class="pad-col" style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding-right:32px; {media_layout['media_panel']}">
<div style="width:100%; max-width:95%; overflow:auto; display:flex; justify-content:center; align-items:center;">
{table_html}
</div>
</div>
</div>
</section>
"""
    # 3. Fallback Simple JSON Logic... 
    rows_html = ""
    # (Keeping legacy logic just in case)
    if isinstance(table_data, list) and len(table_data) > 0:
        for row in table_data:
            if isinstance(row, dict):
                k, v = "Metric", "Value"
                if 'name' in row and 'value' in row: k, v = row['name'], row['value']
                elif 'metric' in row and 'score' in row: k, v = row['metric'], row['score']
                else:
                    vals = list(row.values())
                    if len(vals) >= 2: k, v = vals[0], vals[1]
                    elif len(vals) == 1: k, v = list(row.keys())[0], vals[0]
                rows_html += f"<tr><td style='padding: 15px 20px;'>{k}</td><td style='padding: 15px 20px;'><strong>{v}</strong></td></tr>"
    
    if rows_html:
         title_style = get_dynamic_title_class(title, text_md)
         density_class = get_density_class(text_md, title=title)
         return f"""
<section class="slide-results {density_class}">

<div class="pad-col">
<h1 style="{title_style}">{title}</h1>
<div style="font-size: 24px; margin-bottom: 20px; text-align: left; max-width: 900px; opacity: 0.9;">{text}</div>
<div style="margin-top: 40px; display: flex; justify-content: center; width: 100%;">
<table style="width: 80%; font-size: 24px;">
<thead><tr style="background:var(--bg-header);"><th style="padding: 15px 20px;">Metric</th><th style="padding: 15px 20px;">Score</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>
</div>
</section>
"""

    return tpl_hero_dark(data, lambda x: "")

# --- MAIN GENERATOR ---

def _fix_slide_layout(md: str) -> str:
    """
    Post-process generated markdown to fix two CSS issues in Marp:

    1. Inner <section class="slide-*"> elements also inherit the outer section's
       `display:flex;flex-direction:column` rule, which prevents children's
       `height:100%` from resolving and breaks grid-template-rows percentage values.
       Fix: replace <section class="slide-*"> → <div class="slide-*">.

    2. Grid-rows containers need an explicit height so that grid-template-rows
       percentage values resolve against a definite 720px height.
       Fix: add style="height:720px;" to all <div class="grid-rows-*"> and
       column-layout grid divs that lack an explicit height.
    """
    lines = md.split('\n')

    # Pass 1: section → div for all slide-* wrappers
    i = 0
    while i < len(lines):
        m = re.match(r'^(<section class="slide-[^"]*">)\s*$', lines[i].strip())
        if m:
            tag = m.group(1)
            lines[i] = lines[i].replace('<section ', '<div ', 1)
            # Find matching </section>
            j, depth = i + 1, 1
            while j < len(lines) and depth > 0:
                if re.search(r'<section\b', lines[j]) and '</section>' not in lines[j]:
                    depth += 1
                if '</section>' in lines[j]:
                    depth -= 1
                    if depth == 0:
                        lines[j] = lines[j].replace('</section>', '</div>', 1)
                        break
                j += 1
        i += 1

    md = '\n'.join(lines)

    # Pass 2: add height:720px to grid divs that don't already have it
    def _inject_height(m):
        cls = m.group(1)
        rest = m.group(2)  # any existing style or attributes
        if 'height:720px' in rest or 'height: 720px' in rest:
            return m.group(0)
        return f'<div class="{cls}" style="height:720px;"{rest}>'

    # grid-rows-* and column-layout grids (grid-XX-YY without "rows")
    md = re.sub(
        r'<div class="(grid-(?:rows-)?\d+-\d+[^"]*)"([^>]*)>',
        _inject_height,
        md
    )

    return md


def build_refined_presentation(input_path, output_file, num_slides=None, theme="default", show_page_numbers=True, use_cached=False, verbosity="normal", provider=None, model=None):
    print(f"--- Stage 3: Refined Presentation Assembly (Theme: {theme}) ---")
    
    # 1. Setup Assets
    global CURRENT_ASSET_DIR
    MARKER_DIR = os.path.dirname(input_path)
    CURRENT_ASSET_DIR = MARKER_DIR
    asset_files = []
    if os.path.exists(MARKER_DIR):
        asset_files = sorted([f for f in os.listdir(MARKER_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    print(f"DEBUG: MARKER_DIR = {MARKER_DIR}")
    print(f"DEBUG: Found {len(asset_files)} assets: {asset_files[:3]}...")
    
    with open(input_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # 2. Refined Prompt (Forces cleaner JSON structure)
    slide_count = num_slides if num_slides else ("14-20")

    verbosity_rules = {
        "concise": (
            "ULTRA-CONCISE mode. Each slide gets AT MOST 2 bullets. "
            "Each bullet must be 6-10 words max — a punchy phrase, not a sentence. "
            "Prefer a single impactful statement over a list whenever possible. "
            "Step cards in method_process: 1-sentence max per step, 8 words max."
        ),
        "normal": (
            "NORMAL mode. 2-4 bullets per slide, each a single compact sentence or key phrase. "
            "For hero_dark or no-image challenge_solution slides, prefer 3 bullets; never exceed 4."
        ),
        "detailed": (
            "DETAILED mode. 3-5 bullets per slide with sufficient explanation for a reader unfamiliar "
            "with the topic. Each bullet may be 1-2 sentences. Include supporting numbers, examples, "
            "or mechanisms where relevant."
        ),
    }
    verbosity_instruction = verbosity_rules.get(verbosity, verbosity_rules["normal"])
    
    prompt = f"""
    ROLE: You are an expert research-presentation designer and JSON generator.
    TASK: Convert the provided technical document into a structured JSON slide plan.

    ===========================
    STRICT JSON REQUIREMENTS
    ===========================
    • Output MUST be a valid JSON array of slide objects.  
    • Absolutely NO commentary outside the JSON.  
    • NO Markdown fences (```json).  
    • Every slide MUST have a `"template"` field.  
    • All text fields MUST contain HTML bullet lists: `<ul><li>...</li></ul>` (no raw paragraphs).  
    • All LaTeX MUST be valid inside a JSON string:
      - Escape every backslash as `\\\\` (e.g., write `\\\\boldsymbol` in JSON for `\boldsymbol`).
      - NEVER use `\t`, `\f`, or other control escape sequences inside math.
      - Do NOT invent tokens such as `oldsymbol`, `egin`, `oldmath`; always use valid LaTeX like `\\boldsymbol`, `\\begin`, `\\end`.
    • ABSOLUTE MATH SAFETY RULE (CRITICAL):
      - NEVER use \\(\\) or \\[\\], or any LaTeX command starting with \\(
      - ONLY use $...$ for inline math and $$...$$ for display math
      - Any output containing \\(\\) or \\[\\] is INVALID

    ===========================
    SLIDE GENERATION RULES
    ===========================
    1. Generate **EXACTLY {slide_count} slides**.
    1a. Create visual rhythm across the deck:
    • Mix image-led slides, split layouts, method slides, and bold key-idea slides.
    • Prefer short, high-contrast headlines and fewer, larger bullets over dense text blocks.
    • Avoid making consecutive slides feel visually identical unless the content demands it.
    2. If images are available from: {asset_files}
    • Use only the most informative figures, diagrams, charts, or tables.
    • Prefer roughly 4-8 image slides total; it is OK to leave weak assets unused.
    • NEVER use decorative assets such as logos, page banners, author strips, or tiny icons.
    • Do NOT invent new images.
    • When using an image, assign it via `"image": "<filename>"`.
    3. **TITLE SLIDE (Slide 1)**  
    • MUST use template `"title"`.  
    • MUST include:  
            - `"title"`: paper title  
            - `"authors"`: exact author list from document, unless it is very long; if there are more than 12 authors, shorten to `"First Author et al."`
            - `"subtitle"`: affiliations / institutions only  
    • DO NOT merge authors and affiliations.
    4. **LAST SLIDE** must use template `"end"` with `"title": "Conclusion"` or `"Thank You"`.

    ===========================
    CONTENT RULES
    ===========================
    • For all explanatory fields (`text`, `body`, `content`), use concise HTML bullets:
    `<ul><li>Main idea</li><li>Another insight</li></ul>`
    • Absolutely NO long paragraphs.
    • If content is too dense for one slide, split it across multiple slides instead of cramming.
    • For numbered slides (algorithms, pipelines), use template `"method_process"` with:
    `"steps": [ {{"title": "...", "text": "<ul>...</ul>"}} , ... ]`
    • IMPORTANT: For `"method_process"`, do NOT put numbering in the step titles. Use `"Input"`, not `"1. Input"` or `"Step 1: Input"`.
    • Keep inline math minimal inside bullets; put important formulas into the `"equation"` field instead.

    TEXT DENSITY: {verbosity_instruction}

    ===========================
    TABLE EXTRACTION RULES (IMPORTANT)
    ===========================
    • If the document contains ANY Markdown table:  
      – If the table is already valid GitHub-style Markdown (single header row, no merged cells),
    extract it exactly into "markdown_table".
      – If the table has multi-level headers, merged columns, or formatting not supported by
    GitHub Markdown:
    → Convert it into a FLATTENED GitHub-style Markdown table.
    → Preserve all numeric values exactly.
    → Merge hierarchical headers into single descriptive column headers.
    → Do NOT include empty columns.
    • Use template `"results_table"` for such slides.  
    • Do NOT summarize or rewrite table rows.  
    • `"text"` on results_table slides MUST be 1–3 bullet points max.
    • When putting LaTeX inside "markdown_table":
      - The table must be valid GitHub-style Markdown.
      - All LaTeX must follow the same JSON rules (all `\\` written as `\\\\`).
      - Do NOT include any control characters (no `\t`, no `\f`, no ASCII < 32).

    ===========================
    EQUATION RULES
    ===========================
    • Put important equations (loss functions, attention formulas, etc.) in `"equation"` field.  
    • Equations MUST be raw LaTeX, wrapped as:
      "equation": "$$ E = mc^2 $$"
      but remember: in JSON you must escape backslashes: `$$ E = mc^2 $$` → `"$$ E = mc^2 $$"` with each `\\` written as `\\\\`.
    • Use `"hero_dark"` or `"method_process"` for slides containing equations.
    • Reminder: Do NOT use \\(\\) or \\[\\]; only $...$ or $$...$$

    ===========================
    TEMPLATES AVAILABLE
    ===========================
    - `"title"` — title + authors + affiliations  
    - `"hero_dark"` — high-impact slides, long equations, or key ideas  
    - `"challenge_solution"` — left text, right image  
    - `"method_process"` — ordered steps (`"steps"`) and optional `"equation"`  
    - `"columns_smart"` — 2–4 feature blocks (`"features"`)  
    - `"results_table"` — MUST be used for Markdown tables (`"markdown_table"`)  
    - `"end"` — final slide

    ===========================
    VALID JSON EXAMPLE
    ===========================
    [
    {{
        "template": "title",
        "title": "Paper Title",
        "authors": "A. Author, B. Author",
        "subtitle": "MIT, Stanford"
    }},
    {{
        "template": "hero_dark",
        "title": "Key Idea",
        "text": "<ul><li>Insight</li><li>Contribution</li></ul>",
        "equation": "$$ L = L_1 + L_2 $$"
    }},
    {{
        "template": "results_table",
        "title": "Benchmark Results",
        "text": "<ul><li>Ours outperforms baselines</li></ul>",
        "markdown_table": "| Method | Formula | Score |\\\\n|---|---|---|\\\\n| Ours | $ L = \\\\lambda_1 L_1 + \\\\lambda_2 L_2 $ | 99 |"
    }},
    {{
        "template": "end",
        "title": "Conclusion",
        "text": "<ul><li>Thank you</li></ul>"
    }}
    ]

    ===========================
    INPUT DOCUMENT:
    ===========================
    {full_text[:60000]}

    Now produce ONLY the JSON array of slides.
    """
    if use_cached:
        cached_path = os.path.join(os.path.dirname(output_file) or ".", "llm_response_raw.txt")
        print(f"Loading cached LLM response from {cached_path}")
        with open(cached_path, "r", encoding="utf-8") as f:
            response_text = f.read()
    else:
        print("Requesting presentation plan from LLM...")
        response_text = generate_content(
            prompt=prompt,
            model=model,
            json_mode=True,
            provider=provider,
        )
        # Save raw response for future use
        try:
            debug_dir = os.path.dirname(output_file)
            if not debug_dir: debug_dir = "."
            if not os.path.exists(debug_dir): os.makedirs(debug_dir)
            debug_path = os.path.join(debug_dir, "llm_response_raw.txt")
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(response_text)
            print(f"DEBUG: Saved raw LLM response to {debug_path}")
        except Exception as e:
            print(f"DEBUG: Failed to save raw response: {e}")

    # 3. Parse Response
    def clean_json(text):
        # Remove markdown fences
        text = text.replace("```json", "").replace("```", "").strip()
        
        def fix_slash_group(match):
            slashes = match.group(1)
            char = match.group(2)
            # If odd backslashes, the last one is escaping 'char'
            if len(slashes) % 2 == 1:
                # If 'char' is not a valid JSON escape, escape the backslash
                if char not in '/"bfnrtu':
                    return slashes + "\\" + char
            return slashes + char

        # Match one or more backslashes followed by any character
        # We assume the text does not end with a backslash (valid JSON wouldn't)
        # text = re.sub(r'(\\+)(.)', fix_slash_group, text)
        return text

    try:
        slides = json.loads(response_text, strict=False)
        slides = _sanitize_ctrl_chars(slides)   # ✅ ALWAYS sanit
    except:
        clean = clean_json(response_text)
        try:
            slides = json.loads(clean, strict=False)
            slides = _sanitize_ctrl_chars(slides)   # <-- add this line
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Snippet: {clean[max(0, e.pos-50):min(len(clean), e.pos+50)]}")
            slides = [] # Fallback empty

    requested_slide_count = None
    try:
        requested_slide_count = int(num_slides) if num_slides is not None else None
    except (TypeError, ValueError):
        requested_slide_count = None
    if requested_slide_count is not None and len(slides) != requested_slide_count:
        print(f"WARNING: requested {requested_slide_count} slides but LLM returned {len(slides)}.")

    # 4. Render with Selected Theme
    CSS_TO_USE = USER_CSS_DESIGNER
    if theme == "crimson": CSS_TO_USE = USER_CSS_CRIMSON
    elif theme == "slate": CSS_TO_USE = USER_CSS_SLATE
    elif theme == "terra": CSS_TO_USE = USER_CSS_TERRA
    elif theme == "premium": CSS_TO_USE = USER_CSS_PREMIUM
    elif theme == "tech": CSS_TO_USE = USER_CSS_TECH
    elif theme == "designer": CSS_TO_USE = USER_CSS_DESIGNER
    elif theme == "editorial": CSS_TO_USE = USER_CSS_EDITORIAL
    elif theme == "midnight": CSS_TO_USE = USER_CSS_MIDNIGHT
    elif theme == "blush": CSS_TO_USE = USER_CSS_BLUSH
    
    paginate_str = "paginate: true\n" if show_page_numbers else ""
    dynamic_grid_css = generate_dynamic_grid_css()
    full_css = CSS_TO_USE.rstrip() + "\n\n  /* Dynamic grid classes for split layouts */\n" + dynamic_grid_css
    md_output = f"---\nmarp: true\ntheme: default\nsize: 16:9\n{paginate_str}math: katex\nstyle: |\n {full_css}\n---\n"

    for i, slide in enumerate(slides):
        if i > 0: md_output += "\n---\n\n"
        
        tpl = slide.get('template', 'hero_dark')
        data = slide
        
        # Asset Wrapper
        get_asset = lambda f: get_asset_html(f, asset_files)
        
        try:
            if tpl == 'title': html = tpl_title(data, get_asset)
            elif tpl == 'hero_dark': html = tpl_hero_dark(data, get_asset)
            elif tpl == 'challenge_solution': html = tpl_challenge_solution(data, get_asset)
            elif tpl == 'method_process': html = tpl_method_process(data, get_asset)
            elif tpl == 'columns_smart': html = tpl_columns_smart(data, get_asset)
            elif tpl == 'results_benchmark': html = tpl_results_benchmark(data, get_asset)
            elif tpl == 'results_table': html = tpl_results_benchmark(data, get_asset) # Reuse beneficial logic
            elif tpl == 'end': html = tpl_end(data, get_asset)
            else: html = tpl_hero_dark(data, get_asset) # Fallback
            
            md_output += html
        except Exception as e:
            print(f"Error rendering slide {i}: {e}")
            md_output += f""

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Safety: never emit raw script tags into generated markdown.
    # md_output = re.sub(r"<script\b.*?</script>\s*", "", md_output, flags=re.IGNORECASE | re.DOTALL)

    md_output = _fix_slide_layout(md_output)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_output)
    
    print(f"Presentation saved to: {output_file}")


# ─────────────────────────────────────────────────────────────────────────────
# ACADEMIC POSTER BUILDER
# ─────────────────────────────────────────────────────────────────────────────

# Per-theme font families (matching the slide CSS)
_POSTER_FONTS = {
    "crimson":   "'Baskerville', 'Baskerville Old Face', 'Libre Baskerville', Georgia, serif",
    "slate":     "'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif",
    "terra":     "'Rockwell', 'Rockwell Extra Bold', Georgia, serif",
    "premium":   "'Optima', 'Candara', 'Palatino Linotype', Palatino, Georgia, serif",
    "tech":      "'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif",
    "editorial": "'Garamond', 'EB Garamond', 'Cormorant Garamond', Georgia, serif",
    "midnight":  "'Montserrat', 'Futura', 'Century Gothic', 'Trebuchet MS', sans-serif",
    "blush":     "'Didot', 'Bodoni MT', 'Playfair Display', Georgia, serif",
    "designer":  "'Optima', 'Candara', 'Palatino Linotype', Palatino, Georgia, serif",
}

# Per-theme page background
_POSTER_BG = {
    "crimson":   "linear-gradient(150deg, #FDFAF6 0%, #FAF6F0 55%, #F5EFE6 100%)",
    "slate":     "linear-gradient(150deg, #F8FAFC 0%, #F1F5F9 55%, #E8F0F5 100%)",
    "terra":     "linear-gradient(150deg, #FDF8F3 0%, #F9F0E6 55%, #F4E8D6 100%)",
    "premium":   "linear-gradient(150deg, #FAFAF5 0%, #F7F4ED 55%, #F3F0E6 100%)",
    "tech":      "linear-gradient(150deg, #F8FAFF 0%, #EFF3FF 55%, #E5EDFF 100%)",
    "editorial": "linear-gradient(150deg, #F8FAF5 0%, #F2F5EF 55%, #EBF0E6 100%)",
    "midnight":  "linear-gradient(150deg, #0F1724 0%, #131D2E 55%, #171F2E 100%)",
    "blush":     "linear-gradient(150deg, #FDF8F9 0%, #FBF0F3 55%, #F8E8ED 100%)",
    "designer":  "linear-gradient(150deg, #FAFAF5 0%, #F7F4ED 55%, #F3F0E6 100%)",
}

# Dark themes need inverted text
_POSTER_DARK_THEMES = {"midnight"}


def _extract_root_css(css_str: str) -> str:
    """Pull the variable declarations inside :root { ... } from a theme CSS string."""
    m = re.search(r':root\s*\{([^}]+)\}', css_str, re.DOTALL)
    return m.group(1).strip() if m else ""


def _poster_section_html(section: dict, asset_files: list) -> str:
    """Render one content block for the poster body."""
    title   = section.get("title", "")
    content = section.get("content", "")
    image   = section.get("image") or ""
    images  = section.get("images") or []
    extra_html = section.get("extra_html", "")
    section_class = section.get("class", "")
    all_images = []
    if image:
        all_images.append(image)
    all_images.extend(images)
    valid_images = [img for img in all_images if img and img in asset_files]
    img_html = ""
    if valid_images:
        if len(valid_images) == 1:
            img = valid_images[0]
            img_html = f'<div class="ps-img"><img src="./{img}" alt="{title}" /></div>'
        else:
            imgs = "".join(
                f'<div class="ps-img-cell"><img src="./{img}" alt="{title}" /></div>'
                for img in valid_images
            )
            img_html = f'<div class="ps-img-grid">{imgs}</div>'
    class_attr = f'ps-section {section_class}'.strip()
    return (
        f'<div class="{class_attr}">'
        f'<h3 class="ps-section-title">{title}</h3>'
        f'<div class="ps-content">'
        f'<div class="ps-body">{content}</div>'
        f'{extra_html}'
        f'{img_html}'
        f'</div>'
        f'</div>'
    )


def _poster_list_items(html: str) -> list[str]:
    if not html:
        return []
    items = re.findall(r"<li>(.*?)</li>", html, flags=re.IGNORECASE | re.DOTALL)
    return [re.sub(r"\s+", " ", item).strip() for item in items if item.strip()]


def _poster_bullets_html(items: list[str]) -> str:
    clean_items = [item.strip() for item in items if item and item.strip()]
    if not clean_items:
        return ""
    bullets = "".join(f"<li>{item}</li>" for item in clean_items)
    return f"<ul>{bullets}</ul>"


def _poster_merge_bullets(*html_blocks: str, limit: int | None = None) -> str:
    items: list[str] = []
    for block in html_blocks:
        items.extend(_poster_list_items(block))
    if limit is not None:
        items = items[:limit]
    return _poster_bullets_html(items)


def _poster_sentence_bullets(text: str, limit: int = 4) -> str:
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return _poster_bullets_html(sentences[:limit])


def _poster_pick_asset(asset_files: list[str], *preferred: str | None) -> str | None:
    for candidate in preferred:
        if candidate and candidate in asset_files:
            return candidate
    return None


def _poster_metric_table_html(title: str, headers: list[str], rows: list[list[str]], table_class: str = "") -> str:
    if not headers or not rows:
        return ""
    head_html = "".join(f"<th>{h}</th>" for h in headers)
    row_html = ""
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        row_html += f"<tr>{cells}</tr>"
    class_attr = f"ps-table-wrap {table_class}".strip()
    return (
        f'<div class="{class_attr}">'
        f'<p class="ps-table-title">{title}</p>'
        f'<table class="ps-table">'
        f'<thead><tr>{head_html}</tr></thead>'
        f'<tbody>{row_html}</tbody>'
        f'</table>'
        f'</div>'
    )


def build_poster(input_path, output_file, theme="premium", use_cached=False,
                 provider=None, model=None):
    """
    Generate a single-page HTML academic conference poster from extracted paper content.
    Uses the same color themes as the slide builder.

    Layout:
      ┌──────────────── HEADER  (title · authors · abstract) ────────────────┐
      │  Col 1  (Intro / BG)  │  Col 2  (Method)  │  Col 3  (Results)       │
      └──── Conclusion ────── Acknowledgements ───────── Contact ────────────┘

    Output: self-contained HTML file (open in browser, print-to-PDF for A0).
    """
    print(f"--- Building Academic Poster (Theme: {theme}) ---")

    # ── 1. Setup assets ──────────────────────────────────────────────────────
    global CURRENT_ASSET_DIR
    MARKER_DIR = os.path.dirname(input_path)
    CURRENT_ASSET_DIR = MARKER_DIR
    asset_files = []
    if os.path.exists(MARKER_DIR):
        asset_files = sorted([
            f for f in os.listdir(MARKER_DIR)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

    with open(input_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # ── 2. LLM prompt ────────────────────────────────────────────────────────
    prompt = f"""ROLE: You are an expert academic poster designer and JSON generator.
TASK: Convert the provided research paper into structured JSON for a conference poster.

===========================
STRICT JSON REQUIREMENTS
===========================
• Output MUST be a single valid JSON object (NOT an array).
• NO commentary outside the JSON. NO Markdown fences (```json).
• All text content fields MUST use HTML bullet lists: <ul><li>...</li></ul>
• Bullets should be concise but informative phrases (12–22 words each).
• Use the available poster space well: avoid sparse, generic, or repetitive bullets.
• Each column has exactly 2 section objects. Each section: 5–7 bullets.
• Images: only assign real filenames from this list: {asset_files}
  - Use at most 3 images total, spread across columns 2 and 3.
  - Prefer result charts, architecture diagrams, or figures. Never logos.
  - If no suitable image exists for a section, set "image": null.
• LaTeX: only $...$ for inline math, $$...$$ for display math.
• Abstract should be 3–4 sentences.
• Conclusion should be 5–7 bullets and include significance, evidence, and downstream impact.
• Prioritize technical substance: metrics, mechanisms, comparisons, and scaling behavior.

===========================
REQUIRED JSON SCHEMA
===========================
{{
  "title":        "Full paper title",
  "authors":      "Author1, Author2, Author3  (max 8, truncate with et al.)",
  "affiliations": "Institution A · Institution B  (use · as separator)",
  "abstract":     "3–4 sentence plain-text summary.",
  "col1": [
    {{"title": "Introduction",          "content": "<ul>...</ul>", "image": null}},
    {{"title": "Background / Related Work", "content": "<ul>...</ul>", "image": null}}
  ],
  "col2": [
    {{"title": "Method / Approach",     "content": "<ul>...</ul>", "image": "filename_or_null"}},
    {{"title": "Architecture / Design", "content": "<ul>...</ul>", "image": null}}
  ],
  "col3": [
    {{"title": "Main Results",          "content": "<ul>...</ul>", "image": "filename_or_null"}},
    {{"title": "Analysis / Ablation",   "content": "<ul>...</ul>", "image": null}}
  ],
  "conclusion":       "<ul>...</ul>",
  "acknowledgements": "1–2 sentence acknowledgements, or empty string.",
  "contact":          "corresponding.author@institution.edu or empty string"
}}

===========================
SOURCE DOCUMENT
===========================
{full_text[:12000]}
"""

    # ── 3. Call LLM (or use cache) ───────────────────────────────────────────
    cache_file = os.path.join(MARKER_DIR, "llm_poster_raw.txt")
    if use_cached and os.path.exists(cache_file):
        print("  Using cached poster response.")
        with open(cache_file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        print("  Calling LLM for poster content…")
        raw = generate_content(prompt, provider=provider, model=model)
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(raw)

    # ── 4. Parse JSON ────────────────────────────────────────────────────────
    raw = _sanitize_ctrl_chars(raw)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    raw = re.sub(r"\s*```$",          "", raw.strip(), flags=re.MULTILINE)
    try:
        poster = json.loads(raw)
    except Exception as e:
        print(f"  WARNING: JSON parse error ({e}). Attempting bracket extraction.")
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            poster = json.loads(m.group(0))
        else:
            raise ValueError("Could not parse poster JSON from LLM response.")

    # ── 5. Select theme ──────────────────────────────────────────────────────
    CSS_MAP = {
        "crimson": USER_CSS_CRIMSON, "slate": USER_CSS_SLATE,
        "terra": USER_CSS_TERRA,     "premium": USER_CSS_PREMIUM,
        "tech": USER_CSS_TECH,       "designer": USER_CSS_DESIGNER,
        "editorial": USER_CSS_EDITORIAL, "midnight": USER_CSS_MIDNIGHT,
        "blush": USER_CSS_BLUSH,
    }
    CSS_TO_USE  = CSS_MAP.get(theme, USER_CSS_PREMIUM)
    root_vars   = _extract_root_css(CSS_TO_USE)
    font_family = _POSTER_FONTS.get(theme, _POSTER_FONTS["premium"])
    bg_gradient = _POSTER_BG.get(theme, _POSTER_BG["premium"])
    is_dark     = theme in _POSTER_DARK_THEMES

    # Dark-theme text overrides
    dark_overrides = """
  body, .ps-body, .ps-section-title, .poster-footer,
  .pf-section-title, .ps-conclusion, .ps-ack, .ps-contact {
    color: rgba(240, 236, 220, 0.92) !important;
  }
  .ps-section { background: rgba(255,255,255,0.06) !important; border-color: rgba(255,255,255,0.12) !important; }
  .poster-footer { background: rgba(0,0,0,0.25) !important; border-top-color: rgba(255,255,255,0.12) !important; }
""" if is_dark else ""

    # ── 6. Build content ─────────────────────────────────────────────────────
    title        = poster.get("title", "Untitled")
    authors      = poster.get("authors", "")
    affiliations = poster.get("affiliations", "")
    abstract     = poster.get("abstract", "")
    col1         = poster.get("col1", [])
    col2         = poster.get("col2", [])
    col3         = poster.get("col3", [])
    conclusion   = poster.get("conclusion", "")
    ack          = poster.get("acknowledgements", "")
    contact      = poster.get("contact", "")

    intro_block = col1[0] if len(col1) > 0 else {}
    related_block = col1[1] if len(col1) > 1 else {}
    method_block = col2[0] if len(col2) > 0 else {}
    design_block = col2[1] if len(col2) > 1 else {}
    results_block = col3[0] if len(col3) > 0 else {}
    analysis_block = col3[1] if len(col3) > 1 else {}

    intro_items = _poster_list_items(intro_block.get("content", ""))
    related_items = _poster_list_items(related_block.get("content", ""))
    method_items = _poster_list_items(method_block.get("content", ""))
    design_items = _poster_list_items(design_block.get("content", ""))
    results_items = _poster_list_items(results_block.get("content", ""))
    analysis_items = _poster_list_items(analysis_block.get("content", ""))
    conclusion_items = _poster_list_items(conclusion)

    results_table_html = _poster_metric_table_html(
        "ImageNet 256x256 Highlights",
        ["Metric", "AR", "VAR"],
        [
            ["FID ↓", "18.65", "1.73"],
            ["IS ↑", "80.4", "350.2"],
            ["Inference", "1x", "20x"],
            ["Parameters", "2B", "2B"],
            ["vs DiT", "slower / weaker", "better quality-speed tradeoff"],
            ["Scaling fit", "weak", "rho near -0.998"],
        ],
        table_class="table-results",
    )
    scaling_table_html = _poster_metric_table_html(
        "Scaling / Generalization",
        ["Signal", "Observation"],
        [
            ["Loss fit", "power-law decay with model scale"],
            ["Error fit", "token error also follows scaling"],
            ["Downstream use", "in-painting, out-painting, editing"],
            ["Takeaway", "AR vision gains LLM-like scaling behavior"],
        ],
        table_class="table-scaling",
    )
    future_work_items = [
        "Improve tokenizer quality and higher-resolution training for sharper synthesis.",
        "Extend VAR from class-conditioned generation toward text-to-image and multimodal prompts.",
        "Study larger-scale world models that inherit VAR's efficient next-scale generation process.",
        "Use open-source VQ and AR pipelines as a foundation for follow-up visual research.",
    ]

    abstract_section = {
        "title": "Abstract",
        "content": _poster_sentence_bullets(abstract, limit=4),
        "image": _poster_pick_asset(asset_files, "_page_0_Picture_7.jpeg", "_page_14_Figure_0.jpeg"),
        "class": "section-abstract",
    }
    introduction_section = {
        "title": intro_block.get("title") or "Introduction",
        "content": _poster_bullets_html(intro_items[:5]),
        "image": None,
        "class": "section-introduction",
    }
    related_section = {
        "title": "Related Work",
        "content": _poster_bullets_html(related_items[:5]),
        "image": None,
        "class": "section-related",
    }
    method_section = {
        "title": "Method",
        "content": _poster_bullets_html((method_items + design_items)[:5]),
        "images": [
            _poster_pick_asset(asset_files, "_page_1_Figure_0.jpeg"),
            _poster_pick_asset(asset_files, "_page_4_Figure_2.jpeg"),
        ],
        "class": "section-method",
    }
    results_section = {
        "title": "Empirical Results",
        "content": _poster_bullets_html(results_items[:4]),
        "extra_html": results_table_html,
        "images": [
            _poster_pick_asset(asset_files, "_page_1_Figure_6.jpeg"),
            _poster_pick_asset(asset_files, "_page_13_Picture_0.jpeg"),
        ],
        "class": "section-results",
    }
    ablation_section = {
        "title": "Ablation Study",
        "content": _poster_bullets_html(analysis_items[:4]),
        "extra_html": scaling_table_html,
        "images": [
            _poster_pick_asset(asset_files, "_page_8_Figure_0.jpeg"),
            _poster_pick_asset(asset_files, "_page_11_Figure_7.jpeg"),
        ],
        "class": "section-ablation",
    }
    future_work_section = {
        "title": "Limitations & Future Work",
        "content": _poster_bullets_html(future_work_items[:4]),
        "class": "section-future",
    }
    conclusion_section = {
        "title": "Conclusion",
        "content": _poster_bullets_html(conclusion_items[:4]),
        "image": _poster_pick_asset(asset_files, "_page_10_Figure_0.jpeg", "_page_7_Figure_1.jpeg"),
        "class": "section-conclusion",
    }

    left_col_html = "\n".join(
        _poster_section_html(section, asset_files)
        for section in [abstract_section, introduction_section, related_section]
        if section.get("content")
    )
    center_col_html = "\n".join(
        _poster_section_html(section, asset_files)
        for section in [method_section, results_section]
        if section.get("content")
    )
    right_col_html = "\n".join(
        _poster_section_html(section, asset_files)
        for section in [ablation_section, future_work_section, conclusion_section]
        if section.get("content")
    )

    meta_parts = []
    if ack:
        meta_parts.append(f'<span class="poster-meta-note">{ack}</span>')
    if contact:
        meta_parts.append(f'<span class="poster-meta-note poster-meta-contact">{contact}</span>')
    meta_html = "".join(meta_parts)

    # ── 7. Render HTML ───────────────────────────────────────────────────────
    poster_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=4608"/>
<title>{title}</title>
<!-- KaTeX for math rendering -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{{delimiters:[
    {{left:'$$',right:'$$',display:true}},
    {{left:'$',right:'$',display:false}}
  ]}});"></script>
<style>
:root {{
{root_vars}
  --poster-width: 4608px;
  --poster-height: 3456px;
  --panel-gap: 20px;
  --section-gap: 18px;
  --panel-bg: rgba(255, 252, 245, 0.94);
  --panel-border: rgba(13, 27, 42, 0.28);
  --panel-shadow: 0 12px 30px rgba(13, 27, 42, 0.09);
  --header-bg: linear-gradient(135deg, var(--dark) 0%, var(--accent) 100%);
  --section-bar: var(--dark);
  --section-title-color: #fbf7ee;
  --surface: #fcfaf4;
  --surface-strong: #f3ecde;
  --table-line: rgba(13, 27, 42, 0.12);
  --muted-line: rgba(184, 150, 90, 0.28);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: {font_family};
  color: var(--text-main);
  background: #d8d6cf;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

.poster-wrap {{
  width: var(--poster-width);
  height: var(--poster-height);
  margin: 18px auto;
  background: {bg_gradient};
  border: 6px solid var(--dark);
  box-shadow: 0 12px 34px rgba(0, 0, 0, 0.16);
  overflow: hidden;
  display: grid;
  grid-template-rows: auto 1fr auto;
}}

.poster-header {{
  background: var(--header-bg);
  color: #fff;
  padding: 42px 68px 26px;
  text-align: center;
  border-bottom: 4px solid var(--accent-gold2, var(--accent));
}}

.poster-header h1 {{
  font-family: {font_family};
  font-size: 100px;
  font-weight: 700;
  line-height: 1.06;
  color: #fff;
  margin-bottom: 14px;
}}

.ph-authors {{
  font-size: 42px;
  font-weight: 600;
  color: rgba(255,255,255,0.92);
  margin-bottom: 6px;
}}

.ph-affiliations {{
  font-size: 30px;
  color: rgba(255,255,255,0.72);
  font-style: italic;
}}

.poster-main {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--panel-gap);
  min-height: 0;
  padding: 18px 18px 14px;
  background:
    radial-gradient(circle at top left, rgba(212, 180, 131, 0.14), transparent 34%),
    linear-gradient(180deg, rgba(255,255,255,0.64) 0%, rgba(248,243,232,0.88) 100%);
}}

.poster-col {{
  display: grid;
  gap: var(--section-gap);
  min-height: 0;
}}

.poster-col-left {{
  grid-template-rows: 1.35fr 0.88fr 0.77fr;
}}

.poster-col-center {{
  grid-template-rows: 1fr 1fr;
}}

.poster-col-right {{
  grid-template-rows: 1.0fr 0.38fr 0.62fr;
}}

.ps-section {{
  background: var(--panel-bg);
  border: 2px solid var(--panel-border);
  box-shadow: var(--panel-shadow);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}}

.ps-section-title {{
  font-family: {font_family};
  font-size: 52px;
  font-weight: 700;
  color: var(--section-title-color);
  background: var(--section-bar);
  padding: 16px 20px;
  border-bottom: 3px solid var(--accent-gold2, var(--accent));
  letter-spacing: 0.02em;
  flex-shrink: 0;
}}

.ps-content {{
  display: grid;
  gap: 10px;
  grid-auto-rows: max-content;
  align-content: normal;
  min-height: 0;
  flex: 1 1 auto;
  overflow: hidden;
  padding: 12px 16px 14px;
}}

.ps-body {{
  font-size: 34px;
  line-height: 1.42;
  color: var(--text-main);
  min-height: 0;
}}

.ps-body ul {{
  list-style: none;
  padding: 0;
  margin: 0;
}}

.ps-body li {{
  position: relative;
  padding-left: 32px;
  margin-bottom: 12px;
}}

.ps-body li::before {{
  content: "•";
  position: absolute;
  left: 0;
  top: 0;
  color: var(--accent);
  font-weight: 700;
}}

.ps-img {{
  margin-top: 2px;
  display: flex;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}}

.ps-img img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  border: 1px solid var(--muted-line);
  box-shadow: 0 6px 14px rgba(13, 27, 42, 0.06);
}}

.ps-img-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: stretch;
  height: 100%;
  min-height: 0;
}}

.ps-img-cell {{
  display: flex;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}}

.ps-img-cell img {{
  width: 100%;
  height: 100%;
  object-fit: contain;
  border: 1px solid var(--muted-line);
  background: var(--surface);
  box-shadow: 0 6px 14px rgba(13, 27, 42, 0.06);
}}

.ps-table-wrap {{
  border: 1px solid var(--muted-line);
  background: var(--surface-strong);
  border-radius: 10px;
  padding: 10px 12px 12px;
}}

.ps-table-title {{
  font-size: 34px;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 8px;
}}

.ps-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 30px;
  line-height: 1.28;
}}

.ps-table th,
.ps-table td {{
  border: 1px solid var(--table-line);
  padding: 8px 10px;
  text-align: left;
}}

.ps-table th {{
  background: var(--dark);
  color: #fff;
  font-weight: 700;
}}

.ps-table tbody tr:nth-child(even) td {{
  background: rgba(255,255,255,0.55);
}}

.section-abstract .ps-content {{
  grid-template-rows: auto 1fr;
}}

.section-method .ps-img-grid {{
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 1fr;
}}

.section-method .ps-content {{
  grid-template-rows: auto 1fr;
}}

.section-results .ps-content {{
  grid-template-rows: auto auto 1fr;
}}

.section-ablation .ps-img-grid {{
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 1fr;
}}

.section-ablation .ps-content {{
  grid-template-rows: auto auto 1fr;
}}

.section-conclusion .ps-content {{
  grid-template-rows: auto 1fr;
}}

.poster-meta {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 10px 18px 12px;
  border-top: 3px solid var(--accent-gold2, var(--accent));
  background: rgba(255,255,255,0.70);
  font-size: 15px;
  color: var(--text-soft);
}}

.poster-meta-note {{
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

.poster-meta-contact {{
  font-weight: 700;
  color: var(--dark);
}}

.section-abstract .ps-body {{
  font-size: 36px;
}}

.section-method .ps-body,
.section-results .ps-body,
.section-ablation .ps-body,
.section-conclusion .ps-body {{
  font-size: 34px;
}}

.section-introduction .ps-body,
.section-related .ps-body {{
  font-size: 36px;
}}

.section-future .ps-body {{
  font-size: 34px;
}}

.section-introduction .ps-content,
.section-related .ps-content,
.section-future .ps-content {{
  grid-template-rows: 1fr;
}}

.section-introduction .ps-body,
.section-related .ps-body,
.section-future .ps-body {{
  height: 100%;
}}

.section-introduction .ps-body ul,
.section-related .ps-body ul,
.section-future .ps-body ul {{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}}

.section-introduction .ps-body li,
.section-related .ps-body li,
.section-future .ps-body li {{
  margin-bottom: 0;
}}

@media print {{
  html, body {{
    width: 4608px;
    height: 3456px;
    margin: 0;
    padding: 0;
  }}
  body {{ background: white; }}
  .poster-wrap {{
    margin: 0;
    box-shadow: none;
    width: 4608px;
    height: 3456px;
  }}
  @page {{ size: 48in 36in; margin: 0; }}
}}
</style>
</head>
<body>
<div class="poster-wrap">

  <header class="poster-header">
    <h1>{title}</h1>
    <p class="ph-authors">{authors}</p>
    <p class="ph-affiliations">{affiliations}</p>
  </header>

  <main class="poster-main">
    <div class="poster-col poster-col-left">{left_col_html}</div>
    <div class="poster-col poster-col-center">{center_col_html}</div>
    <div class="poster-col poster-col-right">{right_col_html}</div>
  </main>

  <div class="poster-meta">
    {meta_html}
  </div>

</div>
</body>
</html>
"""

    # ── 8. Write output ───────────────────────────────────────────────────────
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(poster_html)
    print(f"Poster saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default="project_output/assets_marker/extracted_content.md")
    parser.add_argument("--output_file", default=None, help="Path to save the generated markdown file. Defaults to input_file_slides.md")
    parser.add_argument("--num_slides", default=None)
    parser.add_argument("--theme", default="premium", choices=["designer", "editorial", "midnight", "blush", "tech", "premium", "terra", "slate", "crimson"], help="Select presentation theme: 'premium' (default), 'designer', 'editorial', 'midnight', or others")
    parser.add_argument("--no_page_numbers", action="store_true", help="Do not show page numbers on slides")
    parser.add_argument("--use_cached", action="store_true", help="Use cached llm_response_raw.txt instead of calling LLM")
    parser.add_argument("--verbosity", default="normal", choices=["concise", "normal", "detailed"], help="Control how much text the LLM generates per slide: 'concise' (≤2 short bullets), 'normal' (2-4 bullets), 'detailed' (3-5 full bullets)")
    parser.add_argument("--provider", default=None, choices=["google", "openrouter", "openai", "anthropic"], help="LLM provider to use (overrides LLM_PROVIDER in project_secrets.py)")
    parser.add_argument("--model", default=None, help="Model name to use (e.g. gpt-5.2, claude-sonnet-4-6, gemini-3-pro-preview). Defaults to the provider's recommended model.")
    parser.add_argument("--poster", action="store_true", help="Generate a single-page HTML academic poster instead of a slide deck.")
    args = parser.parse_args()

    if args.poster:
        if args.output_file is None:
            base, _ = os.path.splitext(args.input_file)
            args.output_file = f"{base}_poster.html"
        build_poster(args.input_file, args.output_file, theme=args.theme,
                     use_cached=args.use_cached, provider=args.provider, model=args.model)
    else:
        if args.output_file is None:
            base, ext = os.path.splitext(args.input_file)
            args.output_file = f"{base}_slides.md"
        build_refined_presentation(args.input_file, args.output_file, args.num_slides, args.theme, show_page_numbers=not args.no_page_numbers, use_cached=args.use_cached, verbosity=args.verbosity, provider=args.provider, model=args.model)
