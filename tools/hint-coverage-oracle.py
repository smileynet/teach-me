#!/usr/bin/env python3
"""hint-coverage-oracle.py — prove a generated lesson USED its concept hints (#176).

The concept-hints pipeline (concept_hints.py, #286) produces a per-topic hint file:
a ranked set of ANCHOR + HOOK terms the lesson should be built around. This oracle
is the Tier-1, deterministic acceptance gate for "the lesson actually consumed the
hints" — the CommonGen concept-coverage metric adapted to teaching prose:

    coverage = |hint terms found in lesson prose| / |hint terms|

A hint term counts as PRESENT when all of its content words appear in the lesson's
teaching prose (stemmed, order-free) — so "world position" matches "world-space
position", "positions in world coordinates", etc. Chrome (nav, read-time, script/
style blocks) is stripped first so a lesson can't score coverage on boilerplate.

The value is the MISS LIST: hints the lesson failed to teach. A generate-lesson run
that ignores its hints scores low and names exactly which concepts it dropped.

Distinct from `check-topic-completeness --concepts`, which extracts concepts FROM the
lesson and checks them against the glossary (a different question, and one currently
contaminated by chrome — see #176 notes). This oracle goes the other direction:
hints IN → is each taught?

Usage:
    hint-coverage-oracle.py --hints .scratch/concepts/topic.json --lesson path/to/lesson.html
    hint-coverage-oracle.py --hints H.json --lesson L.html --core-threshold 1.0 --json

Exit codes: 0 = coverage gate met, 1 = below gate (hints dropped), 2 = error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.html_prose import html_to_prose  # noqa: E402 — shared chrome-strip (#288)

# Minimal Porter-ish suffix stemmer (stdlib only — no nltk dependency).
_SUFFIXES = ("ational", "tional", "ization", "iveness", "fulness", "ousness",
             "ations", "ings", "ies", "sses", "ness", "ment", "ing", "ers",
             "ed", "es", "s", "ly", "er")


def _stem(word: str) -> str:
    w = word.lower()
    for suf in _SUFFIXES:
        suf = suf.strip()
        if suf and len(w) - len(suf) >= 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def _content_words(term: str) -> list[str]:
    """Split a hint term into stemmed content words (drop <=2-char glue)."""
    cleaned = re.sub(r"[^a-z0-9 ]", " ", term.lower())
    return [_stem(w) for w in cleaned.split() if len(w) > 2]


def _stemmed_haystack(prose: str) -> set[str]:
    return {_stem(w) for w in re.findall(r"[a-z0-9]+", prose) if len(w) > 2}


def term_present(term: str, haystack: set[str]) -> bool:
    words = _content_words(term)
    if not words:
        return False
    return all(w in haystack for w in words)


def evaluate(hints_path: Path, lesson_path: Path, core_threshold: float) -> dict:
    hints = json.loads(hints_path.read_text(encoding="utf-8"))
    concepts = hints.get("concepts", [])
    terms = [c["term"] for c in concepts]
    # ANCHORs are the topic-central hints; treat L1/L2 or explicit anchor flag as "core".
    core_terms = [c["term"] for c in concepts if c.get("relevant_to_target")]
    if not core_terms:  # fall back to the top-half by rank as the core set
        core_terms = terms[: max(1, len(terms) // 2)]

    haystack = _stemmed_haystack(html_to_prose(lesson_path.read_text(encoding="utf-8")))

    found = [t for t in terms if term_present(t, haystack)]
    missing = [t for t in terms if t not in found]
    core_found = [t for t in core_terms if term_present(t, haystack)]
    core_missing = [t for t in core_terms if t not in core_found]

    coverage = len(found) / len(terms) if terms else 0.0
    core_coverage = len(core_found) / len(core_terms) if core_terms else 0.0
    status = "pass" if core_coverage >= core_threshold else "fail"

    return {
        "status": status,
        "topic": hints.get("topic"),
        "lesson": lesson_path.name,
        "coverage": round(coverage, 3),
        "core_coverage": round(core_coverage, 3),
        "core_threshold": core_threshold,
        "total": len(terms),
        "covered": len(found),
        "core_total": len(core_terms),
        "core_covered": len(core_found),
        "missing": missing,
        "core_missing": core_missing,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Prove a lesson used its concept hints (#176)")
    ap.add_argument("--hints", required=True, help="concept-hints JSON (from concept_hints.py)")
    ap.add_argument("--lesson", required=True, help="lesson HTML file")
    ap.add_argument("--core-threshold", type=float, default=1.0,
                    help="required coverage of CORE (anchor) hints (default 1.0)")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    args = ap.parse_args()

    hints_path = Path(args.hints)
    lesson_path = Path(args.lesson)
    if not hints_path.is_file():
        print(f"hint-coverage-oracle ERROR: hints not found: {hints_path}", file=sys.stderr)
        return 2
    if not lesson_path.is_file():
        print(f"hint-coverage-oracle ERROR: lesson not found: {lesson_path}", file=sys.stderr)
        return 2

    r = evaluate(hints_path, lesson_path, args.core_threshold)

    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"  topic:  {r['topic']}")
        print(f"  lesson: {r['lesson']}")
        print(f"  coverage:      {r['coverage']:.0%} ({r['covered']}/{r['total']} hints)")
        print(f"  core coverage: {r['core_coverage']:.0%} ({r['core_covered']}/{r['core_total']} anchors)"
              f"  [gate >= {r['core_threshold']:.0%}]")
        if r["missing"]:
            print(f"  missing: {r['missing']}")
        if r["core_missing"]:
            print(f"  CORE missing (gate-failing): {r['core_missing']}")
        print(f"\nhint-coverage-oracle: {r['status'].upper()}")

    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"hint-coverage-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
