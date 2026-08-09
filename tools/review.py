#!/usr/bin/env python3
"""Review mode: surface due cards for spaced repetition.

Usage:
  python tools/review.py                  # show all due cards
  python tools/review.py iceberg-on-aws   # show due cards for one topic
  python tools/review.py --list           # list topics with counts
  python tools/review.py --stats          # show stats per topic
  python tools/review.py --review ID QUALITY  # record a review

The agent uses this to drive review sessions. It surfaces cards,
the learner explains, and the agent records the quality rating.

Rendering: uses Rich library for markdown, code blocks, and panels
when available; falls back to plain text if Rich isn't installed.
"""

from __future__ import annotations

import argparse
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
    read_cards,
    review_card,
    stats,
)
from sm2 import days_overdue, CardSchedule

# Rich rendering (graceful fallback)
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def _console():
    """Get a Rich Console (or None if unavailable)."""
    if RICH_AVAILABLE:
        return Console()
    return None


def _render_card(card: Card, index: int, topic_slug: str, overdue: int) -> None:
    """Render a single card — Rich if available, plain text fallback."""
    console = _console()

    if console and RICH_AVAILABLE:
        # Rich rendering with markdown support
        overdue_str = f"  [dim]({overdue}d overdue)[/dim]" if overdue > 0 else ""
        subtitle = f"[dim]{card.id[:8]}… · {topic_slug} · {card.question_type}[/dim]{overdue_str}"

        console.print(Panel(
            Markdown(card.prompt),
            title=f"[bold]{index}[/bold]",
            subtitle=subtitle,
            border_style="blue",
            padding=(0, 1),
        ))
    else:
        # Plain text fallback
        overdue_str = f" ({overdue}d overdue)" if overdue > 0 else ""
        print(f"  {index}. [{card.question_type}] {card.prompt}")
        print(f"     id: {card.id}  topic: {topic_slug}{overdue_str}")
        print()


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
        topic_slug = _find_topic(card)
        _render_card(card, i, topic_slug, overdue)


def cmd_stats(topic: str | None = None, today: date | None = None) -> None:
    """Show stats for all topics or a single topic."""
    today = today or date.today()
    topics = [topic] if topic else list_topics()

    if not topics:
        print("No question banks found.")
        return

    console = _console()
    if console and RICH_AVAILABLE:
        table = Table(title="SR Stats")
        table.add_column("Topic", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Due", justify="right", style="yellow")
        table.add_column("Active", justify="right")
        table.add_column("Mastered", justify="right", style="green")
        for t in topics:
            s = stats(t, today)
            table.add_row(t, str(s['total']), str(s['due']), str(s['active']), str(s['mastered']))
        console.print(table)
    else:
        print("Topic                          Total  Due  Active  Mastered")
        print("─" * 62)
        for t in topics:
            s = stats(t, today)
            print(f"  {t:<28} {s['total']:>5}  {s['due']:>3}  {s['active']:>6}  {s['mastered']:>8}")


def cmd_list_topics(today: date | None = None) -> None:
    """List topics with due/total counts."""
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
    console = _console()
    if console and RICH_AVAILABLE:
        console.print(f"[green]✓[/green] Reviewed (quality={quality}): next review in [bold]{sched['interval_days']}d[/bold] (due {sched['due_date']})")
        if result.mastered:
            console.print("  [gold1]🏆 Card graduated to mastered![/gold1]")
    else:
        print(f"✓ Reviewed (quality={quality}): next review in {sched['interval_days']}d (due {sched['due_date']})")
        if result.mastered:
            print("  🏆 Card graduated to mastered!")


def _find_topic(card: Card) -> str:
    """Find which topic file contains a card."""
    for t in list_topics():
        for c in read_cards(t):
            if c.id == card.id:
                return t
    return "unknown"


def _find_topic_by_id(card_id: str) -> str | None:
    """Find which topic contains a card by ID."""
    for t in list_topics():
        for c in read_cards(t):
            if c.id == card_id or c.id.startswith(card_id):
                return t
    return None


def main():
    parser = argparse.ArgumentParser(description="Spaced repetition review mode")
    parser.add_argument("topic", nargs="?", default=None,
                        help="Topic slug to filter (default: all topics)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List topics with due/total counts")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats per topic")
    parser.add_argument("--review", "-r", nargs=2, metavar=("ID", "QUALITY"),
                        help="Record a review: card ID and quality (0-5)")

    args = parser.parse_args()

    if args.list:
        cmd_list_topics()
    elif args.stats:
        cmd_stats(args.topic)
    elif args.review:
        card_id, quality = args.review
        cmd_review(card_id, int(quality), args.topic)
    else:
        cmd_due(args.topic)


if __name__ == "__main__":
    main()
