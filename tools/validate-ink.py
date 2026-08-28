"""
tools/validate-ink.py — Compile and lint all .ink stories in a project.

Usage:
    python tools/validate-ink.py [--dir PATH] [--strict] [--inklecate PATH]

Wraps inklecate to provide:
- Structured error/warning reporting
- Non-zero exit on errors (always) or warnings (--strict)
- Per-file results with line numbers
- Integration with mise run ink:validate
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.ink_compile import DEFAULT_INKLECATE, compile_file, inklecate_available

# Defaults
DEFAULT_INK_DIR = "ink-test-project/stories"


def find_ink_files(directory):
    """Find all .ink files (not .ink.json) in directory."""
    ink_dir = Path(directory)
    if not ink_dir.exists():
        print(f"ERROR: directory not found: {directory}")
        sys.exit(2)
    return sorted(ink_dir.glob("*.ink"))


def compile_ink(ink_file, inklecate_path, count_visits=True):
    """Compile a single .ink file, return (success, issues)."""
    success, issues, _ = compile_file(ink_file, inklecate_path, count_visits=count_visits)
    return success, issues


def main():
    ink_dir = DEFAULT_INK_DIR
    inklecate = DEFAULT_INKLECATE
    strict = False

    # Simple arg parsing
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--dir" and i + 1 < len(args):
            ink_dir = args[i + 1]
            i += 2
        elif args[i] == "--inklecate" and i + 1 < len(args):
            inklecate = args[i + 1]
            i += 2
        elif args[i] == "--strict":
            strict = True
            i += 1
        else:
            print(f"Unknown arg: {args[i]}")
            sys.exit(2)

    # Verify inklecate is resolvable (file path or on PATH via mise)
    if not inklecate_available(inklecate):
        print(f"ERROR: inklecate not found at: {inklecate}")
        print("Set INKLECATE env var or use --inklecate PATH")
        sys.exit(2)

    # Find .ink files
    ink_files = find_ink_files(ink_dir)
    if not ink_files:
        print(f"No .ink files found in {ink_dir}")
        sys.exit(0)

    print(f"Validating {len(ink_files)} ink file(s) in {ink_dir}/")
    print(f"inklecate: {inklecate}")
    print()

    total_errors = 0
    total_warnings = 0
    results = []

    for ink_file in ink_files:
        success, issues = compile_ink(ink_file, inklecate)
        errors = [i for i in issues if i["severity"] == "ERROR"]
        warnings = [i for i in issues if i["severity"] == "WARNING"]

        total_errors += len(errors)
        total_warnings += len(warnings)

        status = "PASS" if not errors else "FAIL"
        if warnings and not errors:
            status = "WARN"

        results.append((ink_file.name, status, issues))

        # Print per-file result
        icon = {"PASS": "ok", "WARN": "!!", "FAIL": "XX"}[status]
        print(f"  [{icon}] {ink_file.name}", end="")
        if errors:
            print(f" ({len(errors)} error(s))")
        elif warnings:
            print(f" ({len(warnings)} warning(s))")
        else:
            print()

        # Print issues
        for issue in issues:
            prefix = "  " if issue["severity"] == "ERROR" else "  "
            line_info = f"line {issue['line']}: " if issue["line"] else ""
            print(f"    {issue['severity']}: {line_info}{issue['message']}")

    # Summary
    print()
    print(f"Results: {len(ink_files)} files, {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        print("FAILED (errors present)")
        sys.exit(1)
    elif total_warnings > 0 and strict:
        print("FAILED (warnings in strict mode)")
        sys.exit(1)
    elif total_warnings > 0:
        print("PASSED (with warnings)")
        sys.exit(0)
    else:
        print("PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
