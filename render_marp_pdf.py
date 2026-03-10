#!/usr/bin/env python3
"""Render a Marp deck to PDF through the real Marp CLI and browser engine.

This wrapper stays as close as practical to VS Code Marp PDF export by
delegating to Marp itself, enabling HTML and local file access by default, and
preferring a local Google Chrome executable on macOS when available.

"Real PDF" here means browser-printed PDF with vector text/layout, not a
screenshot pipeline and not a custom HTML-to-PDF reimplementation in Python.
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


CHROME_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome").expanduser(),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render a Marp markdown deck to PDF using the Marp CLI. "
            "Defaults mirror VS Code Marp export as closely as local tooling "
            "allows: PDF output, HTML rendering, local file access, and "
            "Chrome-backed browser printing when available."
        )
    )
    parser.add_argument("input_md", help="Path to the Marp markdown file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF path. Defaults to the input name with a .pdf suffix.",
    )
    parser.add_argument(
        "--marp-binary",
        default="marp",
        help="Marp CLI binary to invoke. Defaults to 'marp'.",
    )
    parser.add_argument(
        "--browser",
        default="chrome",
        choices=["auto", "chrome", "edge", "firefox"],
        help="Browser engine Marp should use for PDF rendering.",
    )
    parser.add_argument(
        "--browser-path",
        help="Optional explicit browser executable path for Marp.",
    )
    parser.add_argument(
        "--browser-timeout",
        type=int,
        default=120,
        help="Timeout in seconds for each browser operation.",
    )
    parser.add_argument(
        "--pdf-outlines",
        action="store_true",
        help="Include PDF outlines/bookmarks.",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help=(
            "Disable HTML tags in markdown. By default HTML is enabled so "
            "Marp rendering stays close to VS Code preview/export behavior."
        ),
    )
    parser.add_argument(
        "--no-local-files",
        action="store_true",
        help=(
            "Disallow local file access. By default local files are allowed so "
            "local images/fonts/CSS render correctly."
        ),
    )
    return parser.parse_args()


def resolve_paths(input_md: str, output: str | None) -> tuple[Path, Path]:
    input_path = Path(input_md).expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input markdown not found: {input_path}")

    output_path = Path(output).expanduser().resolve() if output else input_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return input_path, output_path


def resolve_marp_binary(binary: str) -> str:
    return shutil.which(binary) or binary


def detect_chrome_path() -> Path | None:
    for candidate in CHROME_CANDIDATES:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def determine_browser_strategy(args: argparse.Namespace) -> tuple[str, str | None, str, bool]:
    if args.browser_path:
        return (
            args.browser,
            str(Path(args.browser_path).expanduser()),
            f"explicit browser path: {Path(args.browser_path).expanduser()}",
            args.browser == "chrome",
        )

    if args.browser == "chrome":
        detected = detect_chrome_path()
        if detected is not None:
            return (
                "chrome",
                str(detected),
                f"auto-detected Chrome path: {detected}",
                True,
            )
        return ("chrome", None, "plain browser selection: chrome", True)

    return (args.browser, None, f"plain browser selection: {args.browser}", False)


def build_command(
    marp_binary: str,
    input_path: Path,
    output_path: Path,
    browser: str,
    browser_path: str | None,
    browser_timeout: int,
    use_html: bool,
    allow_local_files: bool,
    pdf_outlines: bool,
) -> list[str]:
    cmd = [
        marp_binary,
        input_path.name,
        "--pdf",
        "--output",
        str(output_path),
        "--browser",
        browser,
        "--browser-timeout",
        str(browser_timeout),
    ]
    if use_html:
        cmd.append("--html")
    if allow_local_files:
        cmd.append("--allow-local-files")
    if browser_path:
        cmd.extend(["--browser-path", browser_path])
    if pdf_outlines:
        cmd.append("--pdf-outlines")
    return cmd


def print_command(cmd: list[str]) -> None:
    print("Running:", " ".join(shlex.quote(part) for part in cmd))


def run_marp(cmd: list[str], cwd: Path, strategy_description: str) -> int:
    print(f"Browser strategy: {strategy_description}")
    print_command(cmd)
    completed = subprocess.run(cmd, cwd=str(cwd))
    return completed.returncode


def main() -> int:
    args = parse_args()

    try:
        input_path, output_path = resolve_paths(args.input_md, args.output)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    marp_binary = resolve_marp_binary(args.marp_binary)
    use_html = not args.no_html
    allow_local_files = not args.no_local_files
    browser, browser_path, strategy_description, can_retry_auto = determine_browser_strategy(args)

    cmd = build_command(
        marp_binary=marp_binary,
        input_path=input_path,
        output_path=output_path,
        browser=browser,
        browser_path=browser_path,
        browser_timeout=args.browser_timeout,
        use_html=use_html,
        allow_local_files=allow_local_files,
        pdf_outlines=args.pdf_outlines,
    )
    exit_code = run_marp(cmd, input_path.parent, strategy_description)

    if exit_code != 0 and can_retry_auto:
        fallback_cmd = build_command(
            marp_binary=marp_binary,
            input_path=input_path,
            output_path=output_path,
            browser="auto",
            browser_path=None,
            browser_timeout=args.browser_timeout,
            use_html=use_html,
            allow_local_files=allow_local_files,
            pdf_outlines=args.pdf_outlines,
        )
        print("Chrome-based render failed, retrying with fallback browser strategy: auto", file=sys.stderr)
        exit_code = run_marp(fallback_cmd, input_path.parent, "fallback browser strategy: auto")

    if exit_code != 0:
        return exit_code

    print(f"PDF written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
