#!/usr/bin/env python3
"""One-click pipeline: input file → extracted content → presentation markdown → PDF.

Usage examples:
    # From a PDF (extracts content first, then builds slides, then renders PDF)
    python3 build.py paper.pdf

    # From a text or markdown file (skips extraction, builds slides directly)
    python3 build.py notes.txt --theme midnight

    # Generate an academic poster (HTML) instead of a slide deck
    python3 build.py paper.pdf --poster
    python3 build.py paper.pdf --poster --theme crimson

    # With options
    python3 build.py paper.pdf --theme midnight --num_slides 20 --verbosity detailed
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent

# File extensions treated as "already extracted" text (skip PDF extraction)
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".text", ".rst"}
PDF_EXTENSIONS = {".pdf"}


def run_step(
    step_num: int,
    total_steps: int,
    description: str,
    cmd: list[str],
    *,
    log_prefix: str,
    cwd: str | None = None,
    expected_outputs: list[Path] | None = None,
) -> None:
    """Run a subprocess step, stream logs live, and abort on failure."""
    separator = "─" * 72
    print(f"\n{separator}", flush=True)
    print(f"  ▶  Step {step_num}/{total_steps} — {description}", flush=True)
    print(separator, flush=True)
    print(f"  Working dir: {cwd or os.getcwd()}", flush=True)
    print(f"  Command:     {shlex.join(cmd)}", flush=True)
    if expected_outputs:
        print("  Expected:", flush=True)
        for output_path in expected_outputs:
            print(f"    - {output_path}", flush=True)
    print(f"  Streaming logs with prefix [{log_prefix}] ...\n", flush=True)

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    start = time.monotonic()
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        if line:
            print(f"[{log_prefix}] {line}", flush=True)
        else:
            print(f"[{log_prefix}]", flush=True)

    result = process.wait()
    elapsed = time.monotonic() - start
    if result != 0:
        print(
            f"\n  ✗  Step {step_num}/{total_steps} failed with exit code {result} after {elapsed:.1f}s",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(result)

    print(f"\n  ✓  Step {step_num}/{total_steps} finished in {elapsed:.1f}s", flush=True)
    if expected_outputs:
        for output_path in expected_outputs:
            if output_path.exists():
                print(f"     Output ready: {output_path}", flush=True)
    print(flush=True)


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
        default="premium",
        choices=["designer", "editorial", "midnight", "blush", "tech", "premium", "terra", "slate", "crimson"],
        help="Presentation theme (default: premium).",
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
        help="Model name (e.g. gpt-5.2, claude-sonnet-4-6, gemini-3-pro-preview). Defaults to the provider's recommended model.",
    )
    slide_group.add_argument(
        "--use_cached",
        action="store_true",
        help="Skip the LLM call and reuse the cached response from a previous run. Useful for re-styling with a different theme.",
    )

    # --- Poster option ---
    parser.add_argument(
        "--poster",
        action="store_true",
        help="Generate a single-page HTML academic poster instead of a slide deck.",
    )

    # --- Render options ---
    render_group = parser.add_argument_group("PDF render options (slides only)")
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

    mode_label = "poster (HTML)" if args.poster else (
        "PDF extraction → slides → render" if is_pdf else "Text → slides → render"
    )
    # Poster: extract + build (2 steps). Slides: extract + build + [render] (2–3 steps).
    if args.poster:
        total_steps = (1 if is_pdf else 0) + 1
    else:
        total_steps = (1 if is_pdf else 0) + 1 + (0 if args.skip_pdf else 1)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║               SlidesAI — One-Click Build                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  Input:      {input_path}")
    print(f"  Output dir: {output_dir}")
    print(f"  Mode:       {mode_label}")
    print(f"  Theme:      {args.theme}")
    print(f"  Provider:   {args.provider or 'from project_secrets.py'}")
    print(f"  Model:      {args.model or 'provider default'}")
    if not args.poster:
        print(f"  Verbosity:  {args.verbosity}")
    print(f"  Use cache:  {'yes' if args.use_cached else 'no'}")
    if is_pdf:
        print(f"  Page range: {args.page_range or 'all pages'}")
        print(f"  OCR:        {'disabled' if args.disable_ocr else 'enabled'}")
    if not args.poster:
        print(f"  Skip PDF:   {'yes' if args.skip_pdf else 'no'}")

    # ── STEP 1: Extract (PDF only) ──────────────────────────────────
    current_step = 1
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

        run_step(
            current_step,
            total_steps,
            "Extracting content from PDF",
            extract_cmd,
            log_prefix="extract",
            expected_outputs=[
                output_dir / "extracted_content.md",
                output_dir / "assets_map.json",
            ],
        )
        build_input = output_dir / "extracted_content.md"
        current_step += 1
    else:
        print("\n  ⏭  Skipping extraction (input is already text)")
        build_input = input_path
        print(f"     Using input directly: {build_input}")

    if args.poster:
        # ── STEP 2 (poster): Build HTML poster ──────────────────────
        poster_output = output_dir / f"{input_path.stem}_poster.html"
        build_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "build_slides.py"),
            "--input_file", str(build_input),
            "--output_file", str(poster_output),
            "--theme", args.theme,
            "--poster",
        ]
        if args.provider:
            build_cmd.extend(["--provider", args.provider])
        if args.model:
            build_cmd.extend(["--model", args.model])
        if args.use_cached:
            build_cmd.append("--use_cached")

        run_step(
            current_step,
            total_steps,
            "Generating academic poster (HTML)",
            build_cmd,
            log_prefix="build_poster",
            expected_outputs=[poster_output],
        )

        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║                     Build Complete!                       ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"  🪧  Poster HTML : {poster_output}")
        print()

    else:
        # ── STEP 2 (slides): Build presentation markdown ────────────
        slides_output = output_dir / f"{input_path.stem}_slides.md"
        build_cmd = [
            sys.executable,
            str(SCRIPT_DIR / "build_slides.py"),
            "--input_file", str(build_input),
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

        run_step(
            current_step,
            total_steps,
            "Generating presentation markdown",
            build_cmd,
            log_prefix="build_slides",
            expected_outputs=[
                slides_output,
                output_dir / "llm_response_raw.txt",
            ],
        )
        current_step += 1

        # ── STEP 3 (slides): Render to PDF ──────────────────────────
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

            run_step(
                current_step,
                total_steps,
                "Rendering slides to PDF",
                render_cmd,
                log_prefix="render_marp_pdf",
                expected_outputs=[pdf_output],
            )

        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║                     Build Complete!                       ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"  📝  Slides markdown : {slides_output}")
        if not args.skip_pdf:
            print(f"  📄  Slides PDF      : {slides_output.with_suffix('.pdf')}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
