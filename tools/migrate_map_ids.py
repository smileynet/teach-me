#!/usr/bin/env python3
"""Backfill immutable ULID `- **id:**` fields into committed MAP.md topic blocks (#257 B).

Surgical, idempotent, formatting-preserving. Reads raw bytes (never newline-translating),
inserts `- **id:** <ULID>` as the FIRST field after each `### slug` header if the block
lacks a valid one, and writes atomically. Re-running is a no-op (empty git diff) — the
data (a present, valid ULID) is the idempotency key. Does NOT parse+reserialize (that
would normalize formatting and break the empty-diff proof) — same raw-text discipline as
map_parser.update_status.

Usage:
    python tools/migrate_map_ids.py                       # dry-run, report only
    python tools/migrate_map_ids.py --apply               # write changes
    python tools/migrate_map_ids.py --apply path/to.MAP.md ...   # specific files
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
import threading
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import ulid  # noqa: E402

_write_lock = threading.Lock()

# Topic header anchor. Group 4 captures THIS line's newline token (\r\n or \n) so the
# inserted id line reuses it — preserving each file's (possibly mixed) EOL.
_HEADER_RE = re.compile(r"^(### )([^\r\n]+?)([ \t]*)(\r?\n)", re.MULTILINE)
# An existing id line anywhere in a block (idempotency / manual-review probe).
_ID_LINE_RE = re.compile(r"^- \*\*id:\*\*[ \t]*(\S+)", re.MULTILINE)


def _block_bounds(text: str, header_end: int) -> str:
    """Block text from header_end to the next '## '/'### ' heading (or EOF)."""
    nxt = re.search(r"^#{2,3} ", text[header_end:], re.MULTILINE)
    return text[header_end : header_end + (nxt.start() if nxt else len(text) - header_end)]


def insert_ids(text: str) -> tuple[str, int, int, list[str]]:
    """Insert `- **id:**` as the first field of every `### slug` block lacking a valid one.

    Returns (new_text, inserted, skipped, manual_review). Pure — no I/O.
    `manual_review` lists slugs whose existing id line is present but not a valid ULID
    (these are left untouched, never duplicated).
    """
    inserted = skipped = 0
    manual_review: list[str] = []

    def _repl(m: re.Match) -> str:
        nonlocal inserted, skipped
        slug = m.group(2).strip()
        block = _block_bounds(text, m.end())
        existing = _ID_LINE_RE.search(block)
        if existing:
            if ulid.is_valid(existing.group(1)):
                skipped += 1
            else:
                manual_review.append(slug)  # present but invalid — do NOT duplicate
                skipped += 1
            return m.group(0)
        inserted += 1
        newline = m.group(4)
        return f"{m.group(0)}- **id:** {ulid.new()}{newline}"

    return _HEADER_RE.sub(_repl, text), inserted, skipped, manual_review


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)  # atomic same-volume rename (NTFS + POSIX)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def migrate_file(path: str | Path, *, dry_run: bool = True) -> dict:
    """Surgical, lock-guarded, atomic id backfill for one MAP.md. Byte-level (EOL-safe)."""
    path = Path(path)
    with _write_lock:
        text = path.read_bytes().decode("utf-8")
        new_text, inserted, skipped, manual = insert_ids(text)
        changed = new_text != text
        if not dry_run and changed:
            _atomic_write_bytes(path, new_text.encode("utf-8"))
        return {
            "path": str(path),
            "inserted": inserted,
            "skipped": skipped,
            "manual_review": manual,
            "changed": changed,
        }


def _default_maps() -> list[Path]:
    return sorted(_PROJECT_ROOT.glob("examples/**/*.MAP.md"))


def migrate_all(paths: list[Path] | None = None, *, dry_run: bool = True) -> int:
    """Migrate the given maps (or all committed example maps). Returns total inserted."""
    paths = paths or _default_maps()
    total_ins = total_skip = 0
    any_manual = False
    for p in paths:
        r = migrate_file(p, dry_run=dry_run)
        total_ins += r["inserted"]
        total_skip += r["skipped"]
        flag = "DRY " if dry_run else ("WROTE" if r["changed"] else "noop ")
        rel = Path(r["path"]).relative_to(_PROJECT_ROOT)
        print(f"[{flag}] {rel}  +{r['inserted']} ids  ({r['skipped']} kept)")
        if r["manual_review"]:
            any_manual = True
            print(f"        MANUAL REVIEW (invalid existing id): {', '.join(r['manual_review'])}")
    tail = "DRY RUN — no files changed." if dry_run else "Files written."
    print(f"--- {total_ins} inserted, {total_skip} kept across {len(paths)} file(s). {tail}")
    if any_manual:
        print("!! Some blocks have an invalid existing id — fix by hand, then re-run.")
    return total_ins


def main() -> None:
    args = sys.argv[1:]
    dry_run = "--apply" not in args
    explicit = [Path(a) for a in args if not a.startswith("--")]
    paths = None
    if explicit:
        paths = [p if p.is_absolute() else _PROJECT_ROOT / p for p in explicit]
    migrate_all(paths, dry_run=dry_run)


if __name__ == "__main__":
    main()
