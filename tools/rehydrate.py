#!/usr/bin/env python3
"""rehydrate.py — clone the reference repos listed in REFERENCES.md.

Cross-platform replacement for the old bash `mise run rehydrate` task, which used
bash-isms (`mkdir -p`, `while read`, `awk`, `eval`) that fail under Windows' cmd.exe
(the `mkdir -p .references` erroring on an existing dir was the first casualty).

Contract (unchanged): parse every line in REFERENCES.md that starts with `git clone`,
take the LAST whitespace-separated token as the target dir, skip it if it already
exists, otherwise run the clone. Existing dirs are never touched.

Exit codes: 0 = all present/cloned OK, 1 = one or more clones failed.
"""
from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "REFERENCES.md"
REF_DIR = ROOT / ".references"


def clone_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip().startswith("git clone")]


def target_dir(line: str) -> str:
    # Last token is the destination dir (matches the old `awk '{print $NF}'`).
    return shlex.split(line)[-1]


def main() -> int:
    if not REFERENCES.is_file():
        print(f"rehydrate: REFERENCES.md not found at {REFERENCES}", file=sys.stderr)
        return 1

    REF_DIR.mkdir(parents=True, exist_ok=True)  # idempotent — no error if it exists

    lines = clone_lines(REFERENCES.read_text(encoding="utf-8"))
    if not lines:
        print("rehydrate: no 'git clone' lines in REFERENCES.md — nothing to do")
        return 0

    cloned = skipped = failed = 0
    for line in lines:
        dest = target_dir(line)
        if (ROOT / dest).is_dir():
            print(f"  skip: {dest} (exists)")
            skipped += 1
            continue
        print(f"  clone: {dest}")
        # Run the clone as an argv list (no shell) so it's portable + injection-safe.
        result = subprocess.run(shlex.split(line), cwd=str(ROOT))
        if result.returncode != 0:
            print(f"  FAILED: {dest} (git exit {result.returncode})", file=sys.stderr)
            failed += 1
        else:
            cloned += 1

    print(f"\nrehydrate: {cloned} cloned, {skipped} skipped, {failed} failed "
          f"({len(lines)} repos in manifest)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
