#!/usr/bin/env python3
"""One-time, idempotent migration: strip committed per-user `status` from MAP.md (#258).

Per-user progress is no longer authored into the shared, versioned graph — it lives in
a gitignored overlay (`.user/`, keyed by ULID node id). This removes the
`- **status:** ...` line from every topic block in every committed `*.MAP.md`.

Idempotent: removes the line only when present, so a second run is a no-op (exit 0,
"already clean"). Safe to re-run. Committed `complete`/`in-progress` markers are
per-user state and are intentionally dropped (fresh clone = all not-started; users
re-mark via the overlay).

Usage:
    python tools/migrate_strip_status.py            # strip all examples/**/*.MAP.md
    python tools/migrate_strip_status.py --check     # report only, exit 1 if any remain
    python tools/migrate_strip_status.py PATH ...    # explicit files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A topic status line: leading list marker, bold key, value, to end of line + its newline.
_STATUS_LINE = re.compile(r"^[ \t]*-[ \t]*\*\*status:\*\*[^\n]*\n", re.MULTILINE)


def strip_file(path: Path) -> int:
    """Strip status lines from one MAP.md. Returns the count removed (0 = already clean)."""
    text = path.read_text(encoding="utf-8")
    new_text, n = _STATUS_LINE.subn("", text)
    if n:
        path.write_text(new_text, encoding="utf-8")
    return n


def find_maps() -> list[Path]:
    return sorted(PROJECT_ROOT.glob("examples/**/*.MAP.md"))


def main() -> int:
    args = sys.argv[1:]
    check_only = "--check" in args
    explicit = [Path(a) for a in args if not a.startswith("--")]
    targets = explicit or find_maps()

    total = 0
    touched = 0
    for p in targets:
        if not p.exists():
            print(f"skip (missing): {p}", file=sys.stderr)
            continue
        if check_only:
            n = len(_STATUS_LINE.findall(p.read_text(encoding="utf-8")))
        else:
            n = strip_file(p)
        if n:
            touched += 1
            total += n
            print(f"{'FOUND' if check_only else 'stripped'} {n} status line(s): {p}")

    if check_only:
        if total:
            print(f"\n{total} status line(s) still present in {touched} file(s) — run without --check")
            return 1
        print(f"clean: no committed status lines in {len(targets)} MAP.md file(s)")
        return 0

    if total:
        print(f"\nStripped {total} status line(s) from {touched} file(s).")
    else:
        print(f"Already clean: no status lines in {len(targets)} MAP.md file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
