#!/usr/bin/env python3
"""promote-private-topic.py — move a private `.user/` topic into the committed tree (#184).

Private topics live under `{workspace}/.user/maps/{domain}.MAP.md` (+ lessons under
`.user/lessons/{domain}/`), gitignored and local-only. Promotion makes one shareable: it
MOVES the private MAP + lessons to the committed location so they can be reviewed and
committed. This is the optional "promote to shared" AC — deliberately a move + report, NOT
an auto-commit (git-safety: commits stay explicit).

The inverse (shared -> private) is never offered: a committed topic must not become
local-only (it may already be a prereq of other shared topics — ADR 0012).

Usage:
    python tools/promote-private-topic.py --workspace WS --domain DOMAIN [--dry-run]
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def promote(workspace: Path, domain: str, dry_run: bool = False) -> dict:
    """Move `{workspace}/.user/{maps,lessons}` content for `domain` to the committed tree.

    Returns a report dict {moved: [...], skipped: [...], errors: [...]}.
    """
    report: dict = {"moved": [], "skipped": [], "errors": []}
    user = workspace / ".user"
    src_map = user / "maps" / f"{domain}.MAP.md"
    if not src_map.exists():
        report["errors"].append(f"no private map at {src_map}")
        return report

    dst_map = workspace / "maps" / f"{domain}.MAP.md"
    if dst_map.exists():
        report["errors"].append(
            f"committed map already exists at {dst_map} — merge manually (won't overwrite)"
        )
        return report

    moves: list[tuple[Path, Path]] = [(src_map, dst_map)]
    src_lessons = user / "lessons" / domain
    if src_lessons.is_dir():
        moves.append((src_lessons, workspace / "lessons" / domain))

    for src, dst in moves:
        if dst.exists():
            report["skipped"].append(f"{dst} exists — left {src} in place")
            continue
        if dry_run:
            report["moved"].append(f"[dry-run] {src} -> {dst}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        report["moved"].append(f"{src} -> {dst}")
    return report


def main(argv: list[str]) -> int:
    args = list(argv)
    if "--workspace" not in args or "--domain" not in args:
        print(__doc__)
        return 2
    workspace = Path(args[args.index("--workspace") + 1])
    domain = args[args.index("--domain") + 1]
    dry_run = "--dry-run" in args

    report = promote(workspace, domain, dry_run)
    for m in report["moved"]:
        print(f"  moved:   {m}")
    for s in report["skipped"]:
        print(f"  skipped: {s}")
    for e in report["errors"]:
        print(f"  ERROR:   {e}", file=sys.stderr)
    if report["errors"]:
        return 1
    if not dry_run and report["moved"]:
        print(f"\nPromoted '{domain}' to the committed tree. Review with `git status`, "
              f"then commit explicitly (not auto-committed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
