#!/usr/bin/env python3
"""Review mode: surface due cards for spaced repetition.

Usage:
  python tools/review.py                  # show all due cards
  python tools/review.py --topic SLUG     # show due cards for one topic
  python tools/review.py --stats          # show stats per topic
  python tools/review.py --review ID QUALITY  # record a review

The agent uses this to drive review sessions. It surfaces cards,
the learner explains, and the agent records the quality rating.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from questions import (
    Card,
    get_all_due_cards,
    get_due_cards,
    list_topics,
    review_card,
    stats,
)
from sm2 import days_overdue, CardSchedule


def cmd_due(topic: str | None, today: date | None = None) -> None:
    """Show cards due for review."""
    today = today or date.today()

    if topic:
        cards = get_due_cards(topic, today)
    else:
        cards = get_all_due_cards(today)

    if not cards:
        print("No cards due for review. 🎉")
        return

    # Sort by most overdue first
    cards.sort(key=lambda c: days_overdue(CardSchedule.from_dict(c.schedule), today), reverse=True)

    print(f"📚 {len(cards)} card(s) due for review:\n")
    for i, card in enumerate(cards, 1):
        overdue = days_overdue(CardSchedule.from_dict(card.schedule), today)
        overdue_str = f" ({overdue}d overdue)" if overdue > 0 else ""
        topic_slug = _find_topic(card)
        print(f"  {i}. [{card.question_type}] {card.prompt}")
        print(f"     id: {card.id}  topic: {topic_slug}{overdue_str}")
        print()


def cmd_stats(today: date | None = None) -> None:
    """Show stats for all topics."""
    today = today or date.today()
    topics = list_topics()

    if not topics:
        print("No question banks found.")
        return

    print("Topic                          Total  Due  Active  Mastered")
    print("─" * 62)
    for t in topics:
        s = stats(t, today)
        print(f"  {t:<28} {s['total']:>5}  {s['due']:>3}  {s['active']:>6}  {s['mastered']:>8}")


def cmd_review(card_id: str, quality: int, topic: str | None = None) -> None:
    """Record a review for a card."""
    if not 0 <= quality <= 5:
        print(f"Error: quality must be 0-5, got {quality}", file=sys.stderr)
        sys.exit(1)

    # Find the topic if not specified
    if not topic:
        topic = _find_topic_by_id(card_id)
        if not topic:
            print(f"Error: card {card_id} not found in any topic", file=sys.stderr)
            sys.exit(1)

    result = review_card(topic, card_id, quality)
    if result is None:
        print(f"Error: card {card_id} not found in topic {topic}", file=sys.stderr)
        sys.exit(1)

    sched = result.schedule
    print(f"✓ Reviewed (quality={quality}): next review in {sched['interval_days']}d (due {sched['due_date']})")
    if result.mastered:
        print("  🏆 Card graduated to mastered!")


def _find_topic(card: Card) -> str:
    """Find which topic file contains a card (by lesson_id heuristic)."""
    topics = list_topics()
    # Try to find by iterating (cards don't store their topic slug)
    from questions import read_cards
    for t in topics:
        for c in read_cards(t):
            if c.id == card.id:
                return t
    return "unknown"


def _find_topic_by_id(card_id: str) -> str | None:
    """Find which topic contains a card by ID."""
    from questions import read_cards
    for t in list_topics():
        for c in read_cards(t):
            if c.id == card_id:
                return t
    return None


def main():
    parser = argparse.ArgumentParser(description="Spaced repetition review mode")
    parser.add_argument("--topic", "-t", help="Filter to a specific topic slug")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats per topic")
    parser.add_argument("--review", "-r", nargs=2, metavar=("ID", "QUALITY"),
                        help="Record a review: card ID and quality (0-5)")

    args = parser.parse_args()

    if args.stats:
        cmd_stats()
    elif args.review:
        card_id, quality = args.review
        cmd_review(card_id, int(quality), args.topic)
    else:
        cmd_due(args.topic)


if __name__ == "__main__":
    main()
