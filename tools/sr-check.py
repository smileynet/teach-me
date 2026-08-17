#!/usr/bin/env python3
"""sr-check.py — Validate question bank quality.

Checks prompts against known-good patterns, detects leeches, flags issues.
Designed as a quality gate after writing lessons.

Usage:
  python tools/sr-check.py              # check all topics
  python tools/sr-check.py iceberg      # check one topic
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from questions import Card, list_topics, read_cards, REVIEWS_LOG


LEECH_THRESHOLD = 4

# Quality checks
WEAK_PREFIXES = [
    "what is",
    "what are",
    "name the",
    "list the",
    "which of",
    "define ",
    "how many",
]

GOOD_PREFIXES = [
    "explain",
    "compare",
    "why does",
    "why do",
    "what happens if",
    "what would happen",
    "predict",
    "your team",
    "your customer",
    "your colleague",
    "how would you",
    "how is",
    "when would",
    "what problem",
    "what breaks",
]


def check_card(card: Card, lapse_counts: dict[str, int]) -> list[str]:
    """Check a single card for quality issues. Returns list of warnings."""
    warnings = []
    prompt_lower = card.prompt.lower().strip()

    # Check for weak question patterns (recall/recognition)
    for prefix in WEAK_PREFIXES:
        if prompt_lower.startswith(prefix):
            warnings.append(f"prompt starts with '{prefix}' — prefer 'Explain why' format")
            break

    # Check answer length (atomicity)
    if len(card.expected_answer) > 300:
        warnings.append(f"expected_answer is {len(card.expected_answer)} chars — may not be atomic (split into multiple cards?)")

    # Check for numbered criteria format (required)
    answer_lower = card.expected_answer.lower()
    has_numbered = "(1)" in card.expected_answer and "(2)" in card.expected_answer
    has_criteria = any(marker in answer_lower for marker in [
        "should mention", "key idea", "check:", "bonus:", "e.g.", "core:"
    ])

    if not has_numbered and len(card.expected_answer) > 30:
        warnings.append("criteria missing numbered points — use 'Should mention: (1)... (2)...' format")

    if len(card.expected_answer) > 80 and not has_criteria and not has_numbered and "\n" not in card.expected_answer:
        warnings.append("expected_answer looks like prose, not criteria — use 'Should mention: (1)...' format")

    # Check prompt length (too short = vague)
    if len(card.prompt) < 20:
        warnings.append("prompt is very short — may be too vague to answer meaningfully")

    # Check for missing provenance
    if not card.lesson_id:
        warnings.append("no lesson_id — card has no provenance trail")

    # Check for missing tags
    if not card.tags:
        warnings.append("no tags — harder to filter and track coverage")

    # Check cognitive load level tagging (ADR 0007)
    level_tags = [t for t in card.tags if t.startswith("L1-") or t.startswith("L2-") or t.startswith("L3-")]
    if card.tags and not level_tags:
        warnings.append("no L1/L2/L3 level tag — add L1-core, L2-practice, or L3-nuance")

    # Leech detection
    lapses = lapse_counts.get(card.id, 0)
    if lapses >= LEECH_THRESHOLD:
        warnings.append(f"lapsed {lapses} times — flagged as leech (rewrite or suspend)")

    return warnings


def load_lapse_counts() -> dict[str, int]:
    """Load lapse counts from review log."""
    counts: dict[str, int] = {}
    if not REVIEWS_LOG.exists():
        return counts
    with open(REVIEWS_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("quality", 5) < 3:
                    cid = entry.get("card_id", "")
                    counts[cid] = counts.get(cid, 0) + 1
            except (json.JSONDecodeError, KeyError):
                pass
    return counts


def cmd_check(topic: str | None = None) -> None:
    """Run quality checks on question bank."""
    if topic:
        topics = [topic]
    else:
        topics = list_topics()

    if not topics:
        print("No question banks found.")
        return

    lapse_counts = load_lapse_counts()
    total_cards = 0
    total_pass = 0
    total_warn = 0
    total_leeches = 0
    all_issues: list[tuple[str, Card, list[str]]] = []

    for t in topics:
        cards = read_cards(t)
        total_cards += len(cards)

        for card in cards:
            warnings = check_card(card, lapse_counts)
            if warnings:
                total_warn += 1
                all_issues.append((t, card, warnings))
                if any("leech" in w for w in warnings):
                    total_leeches += 1
            else:
                total_pass += 1

    # Display results
    if len(topics) == 1:
        print(f"Checking {topics[0]} ({total_cards} cards)...\n")
    else:
        print(f"Checking {len(topics)} topics ({total_cards} cards)...\n")

    for t, card, warnings in all_issues:
        for w in warnings:
            if "leech" in w:
                icon = "🔴"
            else:
                icon = "⚠"
            print(f"  {icon} [{t}] {card.id[:8]}… {w}")
            print(f"     prompt: \"{card.prompt[:60]}...\"")

    # Pass cards
    if total_pass > 0:
        print(f"\n  ✓ {total_pass}/{total_cards} cards pass quality checks")

    # Summary
    if total_warn > 0:
        print(f"\nSuggestions:")
        if total_leeches > 0:
            print(f"  • {total_leeches} leech(es): rewrite the prompt or suspend the card")
        weak_count = sum(1 for _, _, ws in all_issues if any("prefer" in w for w in ws))
        if weak_count > 0:
            print(f"  • {weak_count} weak prompt(s): reframe as 'Explain to a colleague why...'")
        long_count = sum(1 for _, _, ws in all_issues if any("atomic" in w for w in ws))
        if long_count > 0:
            print(f"  • {long_count} non-atomic answer(s): consider splitting into multiple cards")
        criteria_count = sum(1 for _, _, ws in all_issues if any("numbered points" in w for w in ws))
        if criteria_count > 0:
            print(f"  • {criteria_count} card(s) missing numbered criteria: add (1)... (2)... format")
    else:
        print("\n  ✅ All cards pass quality checks!")

    # Exit code
    sys.exit(1 if total_leeches > 0 else 0)


def main():
    parser = argparse.ArgumentParser(description="SR check — validate question quality")
    parser.add_argument("topic", nargs="?", default=None,
                        help="Topic slug to check (default: all topics)")

    args = parser.parse_args()
    cmd_check(args.topic)


if __name__ == "__main__":
    main()
