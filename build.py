#!/usr/bin/env python3
"""One-click pipeline: input file → extracted content → presentation markdown → PDF.

Usage examples:
    # From a PDF (extracts content first, then builds slides, then renders PDF)
    python3 build.py paper.pdf

    # From a text/markdown file (skips extraction, builds slides directly)
    python3 build.py notes.txt
    python3 build.py lecture.md

    # With options
    python3 build.py paper.pdf --theme midnight --num_slides 20 --verbosity detailed
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent

# File extensions treated as "already extracted" text (skip PDF extraction)
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".text", ".rst"}
PDF_EXTENSIONS = {".pdf"}


def run_step(description: str, cmd: list[str], cwd: str | None = None) -> None:
    """Run a subprocess step, printing a banner and aborting on failure."""
    separator = "─" * 60
    print(f"\n{separator}")
    print(f"  ▶  {description}")
    print(separator)
    print(f"  Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n  ✗  Step failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"  ✓  {description} — done")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="One-click pipeline: PDF/text → presentation markdown → PDF slides.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "input_file",
        help="Path to the input file. Use a .pdf for full extraction, or .txt/.md to skip extraction.",
    )
    parser.add_argument(
        "-o", "--output_dir",
        default=None,
        help="Output directory for all generated files. Defaults to a folder named after the input file.",
    )

    # --- Extraction options (PDF only) ---
    extract_group = parser.add_argument_group("PDF extraction options (only used when input is a PDF)")
    extract_group.add_argument("--page_range", default=None, help="Pages to extract (e.g. 0-5, 10, 12-14).")
    extract_group.add_argument("--disable_ocr", action="store_true", help="Disable OCR, use embedded text only.")

    # --- Slide builder options ---
    slide_group = parser.add_argument_group("Slide generation options")
    slide_group.add_argument("--num_slides", type=int, default=None, help="Target number of slides.")
    slide_group.add_argument(
        "--theme",
        default="designer",
        choices=["designer", "editorial", "midnight", "blush", "tech", "premium", "terra", "slate", "crimson"],
        help="Presentation theme (default: designer).",
    )
    slide_group.add_argument(
        "--verbosity",
        default="normal",
        choices=["concise", "normal", "detailed"],
        help="How much text per slide (default: normal).",
    )
    slide_group.add_argument(
        "--provider",
        default=None,
        choices=["google", "openrouter", "openai", "anthropic"],
        help="LLM provider (overrides LLM_PROVIDER in project_secrets.py).",
    )
    slide_group.add_argument(
        "--model",
        default=None,
        help="Model name (e.g. gpt-4o, claude-sonnet-4-6, gemini-2.5-pro). Defaults to the provider's recommended model.",
    )
    slide_group.add_argument(
        "--use_cached",
        action="store_true",
        help="Skip the LLM call and reuse the cached response from a previous run. Useful for re-styling with a different theme.",
    )

    # --- Render options ---
    render_group = parser.add_argument_group("PDF render options")
    render_group.add_argument("--skip_pdf", action="store_true", help="Skip the final Marp-to-PDF render step.")
    render_group.add_argument("--marp_binary", default="marp", help="Path to the Marp CLI binary.")

    return parser.parse_args()


def resolve_output_dir(input_path: Path, output_dir: str | None) -> Path:
    """Determine the output directory, creating it if needed."""
    if output_dir:
        out = Path(output_dir).expanduser().resolve()
    else:
        out = input_path.parent / input_path.stem
    out.mkdir(parents=True, exist_ok=True)
    return out


def main() -> int:
    args = parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    ext = input_path.suffix.lower()
    is_pdf = ext in PDF_EXTENSIONS
    is_text = ext in TEXT_EXTENSIONS

    if not is_pdf and not is_text:
        print(f"Warning: unrecognized extension '{ext}', treating as text input.", file=sys.stderr)
        is_text = True

    output_dir = resolve_output_dir(input_path, args.output_dir)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║               SlidesAI — One-Click Build                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  Input:      {input_path}")
    print(f"  Output dir: {output_dir}")
    print(f"  Mode:       {'PDF extraction → slides → render' if is_pdf else 'Text → slides → render'}")
    print(f"  Theme:      {args.theme}")
    print(f"  Provider:   {args.provider or 'from project_secrets.py'}")

    # ── STEP 1: Extract (PDF only) ──────────────────────────────────
    if is_pdf:
        extract_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "extract_with_marker.py"),
            "--pdf_path", str(input_path),
            "--output_dir", str(output_dir),
        ]
        if args.page_range:
            extract_cmd.extend(["--page_range", args.page_range])
        if args.disable_ocr:
            extract_cmd.append("--disable_ocr")

        run_step("Step 1/3 — Extracting content from PDF", extract_cmd)
        slides_input = output_dir / "extracted_content.md"
    else:
        print("\n  ⏭  Skipping extraction (input is already text)")
        slides_input = input_path

    # ── STEP 2: Build presentation markdown ─────────────────────────
    slides_output = output_dir / f"{input_path.stem}_slides.md"
    build_cmd = [
        sys.executable,
        str(SCRIPT_DIR / "build_slides.py"),
        "--input_file", str(slides_input),
        "--output_file", str(slides_output),
        "--theme", args.theme,
        "--verbosity", args.verbosity,
    ]
    if args.num_slides:
        build_cmd.extend(["--num_slides", str(args.num_slides)])
    if args.provider:
        build_cmd.extend(["--provider", args.provider])
    if args.model:
        build_cmd.extend(["--model", args.model])
    if args.use_cached:
        build_cmd.append("--use_cached")

    step_label = "Step 2/3" if is_pdf else "Step 1/2"
    run_step(f"{step_label} — Generating presentation with AI", build_cmd)

    # ── STEP 3: Render to PDF ───────────────────────────────────────
    if args.skip_pdf:
        print("\n  ⏭  Skipping PDF render (--skip_pdf)")
    else:
        pdf_output = slides_output.with_suffix(".pdf")
        render_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "render_marp_pdf.py"),
            str(slides_output),
            "--output", str(pdf_output),
        ]
        if args.marp_binary != "marp":
            render_cmd.extend(["--marp-binary", args.marp_binary])

        step_label = "Step 3/3" if is_pdf else "Step 2/2"
        run_step(f"{step_label} — Rendering slides to PDF", render_cmd)

    # ── Summary ─────────────────────────────────────────────────────
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║                     Build Complete! 🎉                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  📝  Slides markdown : {slides_output}")
    if not args.skip_pdf:
        print(f"  📄  Slides PDF      : {slides_output.with_suffix('.pdf')}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
