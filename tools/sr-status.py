#!/usr/bin/env python3
"""sr-status.py — 'git status' for memory.

Shows what's due, what's healthy, what's leeching, and estimated knowledge.
Designed to run at session start or via `mise run sr`.

Usage:
  python tools/sr-status.py              # all topics
  python tools/sr-status.py iceberg      # one topic
  python tools/sr-status.py --list       # list topics with counts
"""

from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import math
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from questions import (
    Card,
    get_all_due_cards,
    get_due_cards,
    list_topics,
    read_cards,
    stats,
    QUESTIONS_DIR,
    REVIEWS_LOG,
)
from sm2 import CardSchedule, days_overdue, is_due


LEECH_THRESHOLD = 4  # lapses before flagging


def retrievability(card: Card, today: date) -> float:
    """Estimate current retrievability using exponential decay.

    R = e^(-t/S) where t = days since last review, S = stability (interval).
    For unreviewed cards, R = 1.0 (just learned).
    """
    sched = card.schedule
    last_reviewed = sched.get("last_reviewed")
    if not last_reviewed:
        return 1.0  # never reviewed = just created = full recall

    interval = sched.get("interval_days", 1)
    stability = max(interval, 1)  # proxy: last successful interval ≈ stability
    t = (today - date.fromisoformat(last_reviewed)).days
    return math.exp(-t / stability)


def count_leeches(cards: list[Card]) -> list[Card]:
    """Find cards that have lapsed LEECH_THRESHOLD+ times."""
    leeches = []
    for card in cards:
        # Count lapses: times repetitions was reset to 0 after being > 0
        # Proxy: low ease + many reviews = leech
        sched = card.schedule
        ease = sched.get("ease_factor", 2.5)
        reps = sched.get("repetitions", 0)
        interval = sched.get("interval_days", 0)
        # Heuristic: ease dropped significantly AND interval is short despite reviews
        if ease <= 1.5 and reps == 0 and interval <= 1 and sched.get("last_reviewed"):
            leeches.append(card)
    return leeches


def count_lapses_from_log(card_id: str) -> int:
    """Count lapses (quality < 3) from review log."""
    if not REVIEWS_LOG.exists():
        return 0
    lapses = 0
    with open(REVIEWS_LOG, encoding="utf-8") as f:
        for line in f:
            if card_id in line and '"quality": ' in line:
                import json
                try:
                    entry = json.loads(line)
                    if entry.get("card_id") == card_id and entry.get("quality", 5) < 3:
                        lapses += 1
                except (json.JSONDecodeError, KeyError):
                    pass
    return lapses


def find_leeches_from_log(cards: list[Card]) -> list[Card]:
    """Find leeches by counting lapses in the review log."""
    if not REVIEWS_LOG.exists():
        return []
    # Build lapse counts from log
    import json
    lapse_counts: dict[str, int] = {}
    with open(REVIEWS_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("quality", 5) < 3:
                    cid = entry.get("card_id", "")
                    lapse_counts[cid] = lapse_counts.get(cid, 0) + 1
            except (json.JSONDecodeError, KeyError):
                pass

    return [c for c in cards if lapse_counts.get(c.id, 0) >= LEECH_THRESHOLD]


def cmd_status(topic: str | None = None, today: date | None = None) -> None:
    """Show SR status."""
    today = today or date.today()

    if topic:
        topics = [topic]
    else:
        topics = list_topics()

    if not topics:
        print("📚 No question banks found.")
        print("   Cards are created when lessons are written (via the teach skill).")
        return

    all_cards: list[Card] = []
    all_due: list[Card] = []
    for t in topics:
        cards = read_cards(t)
        all_cards.extend(cards)
        all_due.extend(get_due_cards(t, today))

    active = [c for c in all_cards if not c.suspended and not c.mastered]
    mastered = [c for c in all_cards if c.mastered]
    suspended = [c for c in all_cards if c.suspended]
    new_cards = [c for c in active if not c.schedule.get("last_reviewed")]

    # Overdue cards
    overdue = []
    for card in all_due:
        d = days_overdue(CardSchedule.from_dict(card.schedule), today)
        if d > 0:
            overdue.append((card, d))
    overdue.sort(key=lambda x: x[1], reverse=True)

    # Estimated knowledge (avg retrievability of active reviewed cards)
    reviewed_active = [c for c in active if c.schedule.get("last_reviewed")]
    if reviewed_active:
        avg_r = sum(retrievability(c, today) for c in reviewed_active) / len(reviewed_active)
    else:
        avg_r = 0.0

    # Leeches
    leeches = find_leeches_from_log(active)

    # Display
    scope = f"Topic: {topic}" if topic else f"Topics: {len(topics)}"
    print(f"📚 Spaced Repetition Status")
    print(f"   {scope}")
    print(f"   Cards: {len(all_cards)} total ({len(active)} active, {len(mastered)} mastered, {len(suspended)} suspended, {len(new_cards)} new)")
    print(f"   Due today: {len(all_due)} cards")

    if overdue:
        max_overdue = overdue[0][1]
        print(f"   Overdue: {len(overdue)} card{'s' if len(overdue) != 1 else ''} (up to {max_overdue} days late)")

    if reviewed_active:
        pct = round(avg_r * 100)
        print(f"   Estimated knowledge: {pct}% (avg retrievability of active cards)")

    if leeches:
        print(f"   ⚠ Leeches: {len(leeches)} card{'s' if len(leeches) != 1 else ''} lapsed {LEECH_THRESHOLD}+ times → consider rewriting")

    # Next action
    print()
    if all_due:
        print(f"   → {len(all_due)} card{'s' if len(all_due) != 1 else ''} waiting for review")
        cmd = "mise run sr:review"
        if topic:
            cmd += f" -- {topic}"
        print(f"     Run: {cmd}")
    else:
        # Find next due date
        next_due = None
        for card in active:
            due_str = card.schedule.get("due_date")
            if due_str:
                d = date.fromisoformat(due_str)
                if d > today and (next_due is None or d < next_due):
                    next_due = d
        if next_due:
            days_until = (next_due - today).days
            print(f"   ✓ Nothing due today. Next review in {days_until} day{'s' if days_until != 1 else ''}.")
        else:
            print("   ✓ Nothing due.")


def cmd_list(today: date | None = None) -> None:
    """List topics with counts."""
    today = today or date.today()
    topics = list_topics()

    if not topics:
        print("No question banks found.")
        return

    print("Available topics:\n")
    total_due = 0
    for t in topics:
        s = stats(t, today)
        due_str = f"  ({s['due']} due)" if s['due'] > 0 else ""
        total_due += s['due']
        print(f"  {t}  [{s['total']} cards]{due_str}")

    print(f"\n  Total due: {total_due}")
    print(f"\nUsage:")
    print(f"  mise run sr:review             (all topics, interleaved)")
    print(f"  mise run sr:review -- <slug>   (one topic)")


def main():
    parser = argparse.ArgumentParser(description="SR status — git status for memory")
    parser.add_argument("topic", nargs="?", default=None,
                        help="Topic slug to filter (default: all topics)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List topics with due/total counts")

    args = parser.parse_args()

    if args.list:
        cmd_list()
    else:
        cmd_status(args.topic)


if __name__ == "__main__":
    main()
