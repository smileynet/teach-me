#!/usr/bin/env python3
"""SM-2 spaced repetition scheduler.

Pure functions: takes card state + quality rating, returns updated state.
No side effects, no I/O, no dependencies beyond stdlib.

Quality scale (0-5):
  5 — perfect, instant recall
  4 — correct after brief hesitation
  3 — correct but required significant effort
  2 — wrong, but recognized correct answer
  1 — wrong, vaguely remembered
  0 — complete blackout

References:
  - https://github.com/cnnrhill/sm-2
  - https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta


EASE_FLOOR = 1.3
EASE_DEFAULT = 2.5


@dataclass
class CardSchedule:
    """Mutable scheduling state for one card."""

    interval_days: int = 0
    ease_factor: float = EASE_DEFAULT
    repetitions: int = 0
    due_date: str = ""  # ISO date string, empty = due now
    last_reviewed: str = ""
    last_quality: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CardSchedule":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def review(schedule: CardSchedule, quality: int, today: date | None = None) -> CardSchedule:
    """Apply one review to a card schedule. Returns a new CardSchedule.

    Args:
        schedule: current card state
        quality: 0-5 rating from the learner
        today: override for testing (defaults to date.today())

    Returns:
        New CardSchedule with updated interval, ease, repetitions, and due date.
    """
    if not 0 <= quality <= 5:
        raise ValueError(f"quality must be 0-5, got {quality}")

    today = today or date.today()
    today_str = today.isoformat()

    if quality < 3:
        # Failed — reset to beginning
        new_interval = 1
        new_reps = 0
    else:
        # Passed — advance interval
        if schedule.repetitions == 0:
            new_interval = 1
        elif schedule.repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(schedule.interval_days * schedule.ease_factor)
        new_reps = schedule.repetitions + 1

    # Ease factor adjustment (applied regardless of pass/fail)
    new_ease = schedule.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(EASE_FLOOR, new_ease)

    due = today + timedelta(days=new_interval)

    return CardSchedule(
        interval_days=new_interval,
        ease_factor=round(new_ease, 4),
        repetitions=new_reps,
        due_date=due.isoformat(),
        last_reviewed=today_str,
        last_quality=quality,
    )


def is_due(schedule: CardSchedule, today: date | None = None) -> bool:
    """Check if a card is due for review."""
    if not schedule.due_date:
        return True
    today = today or date.today()
    return date.fromisoformat(schedule.due_date) <= today


def days_overdue(schedule: CardSchedule, today: date | None = None) -> int:
    """How many days past due. Negative = not yet due."""
    if not schedule.due_date:
        return 0
    today = today or date.today()
    return (today - date.fromisoformat(schedule.due_date)).days
