#!/usr/bin/env python3
"""sr-analytics.py — Minimal viable SR analytics.

Three metrics that drive behavior:
1. Estimated knowledge (avg retrievability)
2. What's decaying (priority review list)
3. Load forecast (reviews/day for next 7 days)

Usage:
  python tools/sr-analytics.py              # all topics
  python tools/sr-analytics.py iceberg      # one topic
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
import math
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from questions import Card, list_topics, read_cards, REVIEWS_LOG
from sm2 import CardSchedule


def retrievability(card: Card, today: date) -> float:
    """Estimate current retrievability: R = e^(-t/S)."""
    sched = card.schedule
    last_reviewed = sched.get("last_reviewed")
    if not last_reviewed:
        return 1.0

    interval = max(sched.get("interval_days", 1), 1)
    t = (today - date.fromisoformat(last_reviewed)).days
    return math.exp(-t / interval)


def true_retention(today: date, lookback_days: int = 14) -> float | None:
    """Calculate true retention from review log (pass rate in recent reviews)."""
    if not REVIEWS_LOG.exists():
        return None

    cutoff = today - timedelta(days=lookback_days)
    passes = 0
    total = 0

    with open(REVIEWS_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                review_date = date.fromisoformat(entry.get("date", ""))
                if review_date >= cutoff:
                    total += 1
                    if entry.get("quality", 0) >= 3:
                        passes += 1
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

    if total == 0:
        return None
    return passes / total


def load_forecast(cards: list[Card], today: date, days_ahead: int = 7) -> list[int]:
    """Forecast reviews per day for the next N days."""
    forecast = [0] * days_ahead
    for card in cards:
        if card.suspended or card.mastered:
            continue
        due_str = card.schedule.get("due_date")
        if not due_str:
            forecast[0] += 1  # no due date = due now
            continue
        due = date.fromisoformat(due_str)
        delta = (due - today).days
        if delta < 0:
            forecast[0] += 1  # overdue
        elif delta < days_ahead:
            forecast[delta] += 1

    return forecast


def cmd_analytics(topic: str | None = None, today: date | None = None) -> None:
    """Show analytics."""
    today = today or date.today()

    if topic:
        topics = [topic]
    else:
        topics = list_topics()

    if not topics:
        print("No question banks found.")
        return

    # Gather all active cards
    all_cards: list[Card] = []
    for t in topics:
        all_cards.extend(read_cards(t))

    active = [c for c in all_cards if not c.suspended and not c.mastered]
    reviewed = [c for c in active if c.schedule.get("last_reviewed")]

    if not active:
        print("No active cards to analyze.")
        return

    # 1. Estimated knowledge
    if reviewed:
        retrievabilities = [(c, retrievability(c, today)) for c in reviewed]
        avg_r = sum(r for _, r in retrievabilities) / len(retrievabilities)
    else:
        retrievabilities = []
        avg_r = 0.0

    # 2. True retention
    ret = true_retention(today)

    # 3. Categorize by retrievability
    strong = [(c, r) for c, r in retrievabilities if r > 0.9]
    decaying = [(c, r) for c, r in retrievabilities if 0.5 <= r <= 0.9]
    weak = [(c, r) for c, r in retrievabilities if r < 0.5]

    # 4. Load forecast
    forecast = load_forecast(active, today)

    # 5. Activity from review log
    review_count_week = 0
    streak = 0
    if REVIEWS_LOG.exists():
        recent_dates: set[date] = set()
        with open(REVIEWS_LOG, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    d = date.fromisoformat(entry.get("date", ""))
                    if (today - d).days <= 7:
                        review_count_week += 1
                    recent_dates.add(d)
                except (json.JSONDecodeError, KeyError, ValueError):
                    pass

        # Calculate streak
        check = today
        while check in recent_dates:
            streak += 1
            check -= timedelta(days=1)

    # Display
    scope = topic if topic else f"{len(topics)} topics"
    print(f"📊 Knowledge State ({scope})\n")
    print(f"   Estimated knowledge: {round(avg_r * 100)}% (retrievability-weighted)")
    if ret is not None:
        print(f"   True retention: {round(ret * 100)}% (of reviews in last 14 days)")
    print()

    print(f"   🟢 Strong (R > 0.9): {len(strong)} concepts")
    print(f"   🟡 Decaying (R 0.5–0.9): {len(decaying)} concepts")
    print(f"   🔴 Weak (R < 0.5): {len(weak)} concepts")

    # What's decaying (sorted by urgency)
    if decaying or weak:
        print(f"\n   What's decaying:")
        urgent = sorted(decaying + weak, key=lambda x: x[1])
        for card, r in urgent[:5]:
            due_str = card.schedule.get("due_date", "?")
            print(f"     • {card.prompt[:55]}… (R={r:.0%}, due {due_str})")

    # Activity
    print(f"\n   Activity: {review_count_week} reviews this week (streak: {streak} day{'s' if streak != 1 else ''})")

    # Load forecast
    avg_load = sum(forecast) / len(forecast)
    print(f"   Load forecast: ~{avg_load:.0f} reviews/day for next 7 days")
    if max(forecast) > avg_load * 2:
        peak_day = forecast.index(max(forecast))
        peak_date = today + timedelta(days=peak_day)
        print(f"   ⚠ Peak: {max(forecast)} reviews on {peak_date.isoformat()}")


def main():
    parser = argparse.ArgumentParser(description="SR analytics — knowledge state")
    parser.add_argument("topic", nargs="?", default=None,
                        help="Topic slug (default: all topics)")

    args = parser.parse_args()
    cmd_analytics(args.topic)


if __name__ == "__main__":
    main()
