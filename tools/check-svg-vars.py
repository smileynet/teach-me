#!/usr/bin/env python3
"""Check that inline SVGs use CSS custom properties instead of hardcoded hex colors.

Scans HTML files for SVG elements with hardcoded fill/stroke hex values.
Reports violations with line numbers.

Usage:
    python tools/check-svg-vars.py library/oidc-rust/lessons/0001-oidc-auth-flows.html
    python tools/check-svg-vars.py --workspace library/oidc-rust
    python tools/check-svg-vars.py --workspace library/oidc-rust --fix  # future: auto-migrate
"""

import argparse
import re
import sys
from pathlib import Path

# Windows consoles default to cp1252; force UTF-8 so ✓/✗/⚠/— glyphs don't crash.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Hex colors that are acceptable (not in SVG context, or intentionally static)
# Currently none — all SVG colors should use variables.
# Add entries here if a specific hex is deliberately static (e.g., a brand logo).

HEX_PATTERN = re.compile(r'(?:fill|stroke)="(#[0-9a-fA-F]{6})"')


def check_file(path: Path) -> list[dict]:
    """Check one HTML file for hardcoded hex in SVGs."""
    content = path.read_text(encoding="utf-8")
    violations = []

    # Find SVG blocks
    in_svg = False
    svg_start = 0
    for i, line in enumerate(content.splitlines(), 1):
        if "<svg" in line.lower():
            in_svg = True
            svg_start = i
        if "</svg>" in line.lower():
            in_svg = False

        if in_svg:
            for match in HEX_PATTERN.finditer(line):
                hex_val = match.group(1)
                violations.append({
                    "file": str(path),
                    "line": i,
                    "hex": hex_val,
                    "context": line.strip()[:80],
                })

    return violations


def main():
    parser = argparse.ArgumentParser(description="Check SVGs for hardcoded hex colors")
    parser.add_argument("files", nargs="*", help="HTML files to check")
    parser.add_argument("--workspace", help="Check all lesson files in a workspace")
    args = parser.parse_args()

    files = []
    if args.workspace:
        ws = Path(args.workspace)
        if not ws.is_absolute():
            ws = Path.cwd() / ws
        # Check lesson files only (map pages use Graphviz SVG which can't use CSS vars)
        for f in sorted(ws.glob("lessons/*.html")):
            if not f.stem.endswith("-map"):
                files.append(f)
    if args.files:
        files.extend(Path(f) for f in args.files)

    if not files:
        print("No files to check. Provide file paths or --workspace.")
        sys.exit(1)

    total_violations = 0
    for f in files:
        if not f.exists():
            print(f"  ⚠ {f}: file not found (skipped)", file=sys.stderr)
            continue
        violations = check_file(f)
        if violations:
            total_violations += len(violations)
            for v in violations:
                print(f"  {f.name}:{v['line']} — {v['hex']} in: {v['context']}")

    if total_violations == 0:
        print(f"✓ {len(files)} files checked, no hardcoded hex in SVGs")
    else:
        print(f"\n✗ {total_violations} violation(s) in {len(files)} files")
        sys.exit(1)


if __name__ == "__main__":
    main()
