#!/usr/bin/env python3
"""sr-lifecycle.py — Card lifecycle operations.

Bulk operations for managing the question bank:
  suspend, retire, reset, sync-lessons.

Usage:
  python tools/sr-lifecycle.py suspend CARD_ID       # pause a card
  python tools/sr-lifecycle.py unsuspend CARD_ID     # resume a card
  python tools/sr-lifecycle.py retire [--min-interval 180]  # graduate old cards
  python tools/sr-lifecycle.py reset CARD_ID         # re-enter learning
  python tools/sr-lifecycle.py sync-lessons          # flag stale cards
"""

from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from questions import Card, list_topics, read_cards, QUESTIONS_DIR
from sm2 import CardSchedule, EASE_DEFAULT


def _rewrite_topic(topic: str, cards: list[Card]) -> None:
    """Rewrite a topic's JSONL file with updated cards."""
    path = QUESTIONS_DIR / f"{topic}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(card.to_json() + "\n")


def _find_card(card_id: str) -> tuple[str, int, list[Card]] | None:
    """Find a card across all topics. Returns (topic, index, cards) or None."""
    for t in list_topics():
        cards = read_cards(t)
        for i, card in enumerate(cards):
            if card.id == card_id or card.id.startswith(card_id):
                return (t, i, cards)
    return None


def cmd_suspend(card_id: str) -> None:
    """Suspend a card (remove from review rotation, keep data)."""
    result = _find_card(card_id)
    if not result:
        print(f"Error: card {card_id} not found", file=sys.stderr)
        sys.exit(1)

    topic, idx, cards = result
    if cards[idx].suspended:
        print(f"Card already suspended: {cards[idx].prompt[:50]}…")
        return

    cards[idx].suspended = True
    _rewrite_topic(topic, cards)
    print(f"✓ Suspended: {cards[idx].prompt[:60]}…")
    print(f"  (topic: {topic}, unsuspend with: sr-lifecycle.py unsuspend {card_id[:8]})")


def cmd_unsuspend(card_id: str) -> None:
    """Unsuspend a card (return to review rotation)."""
    result = _find_card(card_id)
    if not result:
        print(f"Error: card {card_id} not found", file=sys.stderr)
        sys.exit(1)

    topic, idx, cards = result
    if not cards[idx].suspended:
        print(f"Card is not suspended: {cards[idx].prompt[:50]}…")
        return

    cards[idx].suspended = False
    _rewrite_topic(topic, cards)
    print(f"✓ Unsuspended: {cards[idx].prompt[:60]}…")


def cmd_reset(card_id: str) -> None:
    """Reset a card to 'new' state (re-enter learning from scratch)."""
    result = _find_card(card_id)
    if not result:
        print(f"Error: card {card_id} not found", file=sys.stderr)
        sys.exit(1)

    topic, idx, cards = result
    cards[idx].schedule = CardSchedule().to_dict()
    cards[idx].mastered = False
    cards[idx].suspended = False
    _rewrite_topic(topic, cards)
    print(f"✓ Reset to new: {cards[idx].prompt[:60]}…")
    print(f"  (will appear in next review session)")


def cmd_retire(min_interval: int = 180) -> None:
    """Retire cards with interval > min_interval days (mark as mastered)."""
    retired_count = 0
    for t in list_topics():
        cards = read_cards(t)
        changed = False
        for card in cards:
            if card.mastered or card.suspended:
                continue
            interval = card.schedule.get("interval_days", 0)
            if interval >= min_interval:
                card.mastered = True
                retired_count += 1
                changed = True
                print(f"  🏆 Retired: {card.prompt[:55]}… (interval: {interval}d)")
        if changed:
            _rewrite_topic(t, cards)

    if retired_count == 0:
        print(f"No cards with interval ≥ {min_interval} days to retire.")
    else:
        print(f"\n✓ Retired {retired_count} card(s) to mastered.")


def cmd_sync_lessons() -> None:
    """Flag cards whose source lesson may have changed.

    Checks if the lesson file referenced by each card still exists.
    Future: could compare modification times or content hashes.
    """
    lessons_dir = Path(__file__).resolve().parent.parent / "lessons"
    flagged = 0

    for t in list_topics():
        cards = read_cards(t)
        for card in cards:
            lesson_id = card.lesson_id
            if not lesson_id or lesson_id == "quiz-session":
                continue

            # Check if lesson file exists
            lesson_file = lessons_dir / f"{lesson_id}.html"
            if not lesson_file.exists():
                # Try with leading zeros
                found = list(lessons_dir.glob(f"*{lesson_id}*"))
                if not found:
                    print(f"  ⚠ [{t}] Card references missing lesson: {lesson_id}")
                    print(f"    prompt: \"{card.prompt[:50]}…\"")
                    flagged += 1

    if flagged == 0:
        print("✓ All cards reference existing lessons.")
    else:
        print(f"\n⚠ {flagged} card(s) reference missing/renamed lessons.")
        print("  Consider updating provenance or suspending stale cards.")


def main():
    parser = argparse.ArgumentParser(description="SR lifecycle — card management operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # suspend
    p_suspend = subparsers.add_parser("suspend", help="Suspend a card")
    p_suspend.add_argument("card_id", help="Card ID (full or prefix)")

    # unsuspend
    p_unsuspend = subparsers.add_parser("unsuspend", help="Unsuspend a card")
    p_unsuspend.add_argument("card_id", help="Card ID (full or prefix)")

    # reset
    p_reset = subparsers.add_parser("reset", help="Reset a card to new")
    p_reset.add_argument("card_id", help="Card ID (full or prefix)")

    # retire
    p_retire = subparsers.add_parser("retire", help="Retire mastered cards")
    p_retire.add_argument("--min-interval", type=int, default=180,
                          help="Minimum interval (days) to qualify for retirement (default: 180)")

    # sync-lessons
    subparsers.add_parser("sync-lessons", help="Flag cards with missing source lessons")

    args = parser.parse_args()

    if args.command == "suspend":
        cmd_suspend(args.card_id)
    elif args.command == "unsuspend":
        cmd_unsuspend(args.card_id)
    elif args.command == "reset":
        cmd_reset(args.card_id)
    elif args.command == "retire":
        cmd_retire(args.min_interval)
    elif args.command == "sync-lessons":
        cmd_sync_lessons()


if __name__ == "__main__":
    main()
