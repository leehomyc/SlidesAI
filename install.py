#!/usr/bin/env python3
"""
SlidesAI installer — runs pip and npm setup in one command.

Usage:
    python3 install.py
"""

import subprocess
import sys
import shutil


def run(description, cmd):
    print(f"\n▶  {description}")
    print(f"   {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n✗  Failed: {description}", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"✓  Done")


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║               SlidesAI — Setup                            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Step 1: Python dependencies
    run(
        "Installing Python dependencies",
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
    )

    # Step 2: Marp CLI via npm
    npm = shutil.which("npm")
    if npm is None:
        print("\n⚠  npm not found — skipping Marp CLI install.")
        print("   To render slides to PDF, install Node.js from https://nodejs.org")
        print("   then run:  npm install -g @marp-team/marp-cli")
    else:
        run(
            "Installing Marp CLI",
            [npm, "install", "-g", "@marp-team/marp-cli"],
        )

    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║               Setup complete!                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\nNext: copy project_secrets.py.example → project_secrets.py")
    print("      and add your API key, then run:")
    print("      python3 build.py <your_file.pdf>")
    print()


if __name__ == "__main__":
    main()
