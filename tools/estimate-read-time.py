#!/usr/bin/env python3
"""estimate-read-time.py — Compute a lesson's read time from its content.

Lessons declare "~N min read" in their `lesson-meta` div. This tool derives that
number from the actual content instead of a hand-guess, and can update the div in
place. `check-lesson.py` uses `estimate_read_time()` to warn when the declared time
drifts far from the computed one.

FORMULA (calibrated, stdlib-only):

    minutes = ceil(prose_words / 200  +  code_lines * 1.5 / 60)

- 200 WPM — prose reading rate. The widely-used default (ngryman/reading-time,
  close to Medium's 265 and the ~200-250 adult-nonfiction range). Chosen over a
  slower "beginner" rate because empirically it fit our calibration lessons; a
  slower rate over-counted both.
- 1.5 s per code line — code is scanned, not read at prose speed. A per-LINE
  penalty (not per-char or flat-per-block) tracks how much a reader actually works
  through a snippet; 3-line snippets cost little, 90-line reference stories cost
  real time.
- ceil() — round up; a partial minute still costs the reader a minute.

CALIBRATION (the two anchor lessons in ticket #215):
    ink-godot 0001 (1090 prose words, 107 code lines) -> 9 min  (stated ~8, delta +1)
    ink-godot 0002 (1272 prose words, 221 code lines) -> 12 min (stated ~12, delta 0)
Both within the +/-2 min tolerance the ticket requires.

Prose excludes: <script>, <style>, <nav>, <svg>, <head>, and all <pre> code.
Code is measured as non-blank lines inside <pre> blocks.

Usage:
    python tools/estimate-read-time.py LESSON.html [LESSON.html ...]
    python tools/estimate-read-time.py --update LESSON.html   # rewrite lesson-meta
    python tools/estimate-read-time.py --json LESSON.html
"""

from __future__ import annotations

import json
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PROSE_WPM = 200
SECONDS_PER_CODE_LINE = 1.5

# Tags whose text is not prose the reader consumes linearly.
_SKIP_TAGS = {"script", "style", "nav", "svg", "head"}


class _Measurer(HTMLParser):
    """Walk lesson HTML, separating prose words from code-block lines."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._pre_depth = 0
        self.prose_words = 0
        self.code_lines = 0
        self._code_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        if tag == "pre":
            self._pre_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if tag == "pre" and self._pre_depth:
            self._pre_depth -= 1
            if self._pre_depth == 0:
                self._flush_code()

    def handle_data(self, data: str) -> None:
        if self._pre_depth:
            self._code_buf.append(data)
            return
        if self._skip_depth:
            return
        self.prose_words += len(data.split())

    def _flush_code(self) -> None:
        block = "".join(self._code_buf)
        self._code_buf = []
        # Count non-blank lines — blank lines cost the reader nothing.
        self.code_lines += sum(1 for ln in block.splitlines() if ln.strip())


def measure(html: str) -> tuple[int, int]:
    """Return (prose_words, code_lines) for a lesson's HTML."""
    m = _Measurer()
    m.feed(html)
    return m.prose_words, m.code_lines


def estimate_read_time(html: str) -> int:
    """Estimated read time in whole minutes (ceil), from lesson HTML."""
    prose_words, code_lines = measure(html)
    minutes = prose_words / PROSE_WPM + code_lines * SECONDS_PER_CODE_LINE / 60
    return max(1, math.ceil(minutes))


# lesson-meta line looks like:  Lesson 2 · Ink + Godot · ~12 min read<br>
_READ_TIME_RE = re.compile(r"~\s*(\d+)\s*min read")


def declared_read_time(html: str) -> int | None:
    """The '~N min read' value declared in the lesson, or None if absent."""
    m = _READ_TIME_RE.search(html)
    return int(m.group(1)) if m else None


def update_read_time(html: str, minutes: int) -> tuple[str, bool]:
    """Rewrite the declared '~N min read' to `minutes`. Returns (html, changed)."""
    new_html, n = _READ_TIME_RE.subn(f"~{minutes} min read", html)
    return new_html, n > 0


def _report(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    prose_words, code_lines = measure(html)
    est = estimate_read_time(html)
    declared = declared_read_time(html)
    return {
        "lesson": path.name,
        "prose_words": prose_words,
        "code_lines": code_lines,
        "estimated_minutes": est,
        "declared_minutes": declared,
    }


def main(argv: list[str]) -> int:
    args = list(argv)
    if not args or "-h" in args or "--help" in args:
        print(__doc__)
        return 0

    do_update = "--update" in args
    do_json = "--json" in args
    paths = [Path(a) for a in args if not a.startswith("-")]
    if not paths:
        print("Error: no lesson files given", file=sys.stderr)
        return 2

    reports = []
    for path in paths:
        if not path.exists():
            print(f"Error: not found: {path}", file=sys.stderr)
            return 2
        rep = _report(path)
        if do_update:
            html = path.read_text(encoding="utf-8")
            new_html, changed = update_read_time(html, rep["estimated_minutes"])
            if changed and new_html != html:
                path.write_text(new_html, encoding="utf-8")
                rep["updated"] = True
            else:
                rep["updated"] = False
        reports.append(rep)

    if do_json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            decl = f"declared ~{r['declared_minutes']}" if r["declared_minutes"] else "no declared time"
            upd = " (updated)" if r.get("updated") else ""
            print(
                f"{r['lesson']}: est ~{r['estimated_minutes']} min "
                f"({r['prose_words']} words, {r['code_lines']} code lines) — {decl}{upd}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
