#!/usr/bin/env python3
"""Question bank: JSONL storage for spaced repetition cards.

Storage convention:
  learning-records/questions/<topic-slug>.jsonl  — one card per line
  learning-records/reviews.jsonl                 — append-only review log

Each line in a topic file is a complete card record (JSON object).
Reviews are logged separately for future FSRS training.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterator

from sm2 import CardSchedule, review, is_due, EASE_DEFAULT


# Resolve relative to project root (parent of tools/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = _PROJECT_ROOT / "learning-records" / "questions"
REVIEWS_LOG = _PROJECT_ROOT / "learning-records" / "reviews.jsonl"


@dataclass
class Card:
    """A single spaced repetition card."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Content
    prompt: str = ""
    expected_answer: str = ""
    question_type: str = "explain"  # explain|compare|apply|predict
    difficulty_tier: str = "understand"  # recall|understand|apply|analyze
    # Provenance
    lesson_id: str = ""
    section_heading: str = ""
    generated_by: str = "teach-skill"  # teach-skill|quiz-skill|manual
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    # Schedule (SM-2 state)
    schedule: dict = field(default_factory=lambda: CardSchedule().to_dict())
    # Metadata
    tags: list[str] = field(default_factory=list)
    suspended: bool = False
    mastered: bool = False  # graduated after interval > 180 days
    # Rich content (optional)
    prompt_code: dict | None = None   # {"language": "python", "content": "..."}
    answer_code: dict | None = None   # {"language": "sql", "content": "..."}
    # Quick-check (multiple-choice) fields
    options: list[str] | None = None      # 4 answer choices
    correct_index: int | None = None      # 0-based index into options
    explanation: str | None = None        # shown after answering
    # Source links (shown after answering, for "go deeper")
    sources: list[dict] | None = None     # [{"url": "...", "label": "...", "section": "...", "anchor_type": "heading|text-fragment|prose"}]
    # Diagram card fields
    svg_ref: dict | None = None           # {"lesson_file": "...", "svg_index": 0, "description": "..."}
    occluded_labels: list[str] | None = None  # text content of <text> elements to mask

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> "Card":
        d = json.loads(line)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def topic_path(topic_slug: str) -> Path:
    """Path to the JSONL file for a given topic."""
    return QUESTIONS_DIR / f"{topic_slug}.jsonl"


def ensure_dirs() -> None:
    """Create storage directories if missing."""
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_LOG.parent.mkdir(parents=True, exist_ok=True)


def append_card(topic_slug: str, card: Card) -> None:
    """Append a card to the topic's JSONL file."""
    ensure_dirs()
    path = topic_path(topic_slug)
    with open(path, "a", encoding="utf-8") as f:
        f.write(card.to_json() + "\n")


def read_cards(topic_slug: str) -> list[Card]:
    """Read all cards for a topic."""
    path = topic_path(topic_slug)
    if not path.exists():
        return []
    cards = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cards.append(Card.from_json(line))
    return cards


def get_due_cards(topic_slug: str, today: date | None = None) -> list[Card]:
    """Get all cards due for review in a topic."""
    today = today or date.today()
    return [
        c for c in read_cards(topic_slug)
        if not c.suspended and not c.mastered and is_due(CardSchedule.from_dict(c.schedule), today)
    ]


def get_all_due_cards(today: date | None = None) -> list[Card]:
    """Get all due cards across all topics."""
    today = today or date.today()
    due = []
    if not QUESTIONS_DIR.exists():
        return due
    for path in QUESTIONS_DIR.glob("*.jsonl"):
        topic_slug = path.stem
        due.extend(get_due_cards(topic_slug, today))
    return due


def review_card(topic_slug: str, card_id: str, quality: int, today: date | None = None) -> Card | None:
    """Review a card: update its schedule in-place and log the review.

    Rewrites the topic file with the updated card. Returns the updated card or None if not found.
    """
    today = today or date.today()
    path = topic_path(topic_slug)
    if not path.exists():
        return None

    cards = read_cards(topic_slug)
    updated_card = None

    for i, card in enumerate(cards):
        if card.id == card_id or card.id.startswith(card_id):
            old_schedule = CardSchedule.from_dict(card.schedule)
            new_schedule = review(old_schedule, quality, today)

            # Graduate cards with interval > 180 days
            if new_schedule.interval_days > 180:
                card.mastered = True

            card.schedule = new_schedule.to_dict()
            updated_card = card
            cards[i] = card
            break

    if updated_card is None:
        return None

    # Rewrite topic file
    with open(path, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(card.to_json() + "\n")

    # Append to review log
    log_entry = {
        "card_id": card_id,
        "topic": topic_slug,
        "quality": quality,
        "date": today.isoformat(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "new_interval": updated_card.schedule["interval_days"],
        "new_ease": updated_card.schedule["ease_factor"],
    }
    with open(REVIEWS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return updated_card


def list_topics() -> list[str]:
    """List all topic slugs with question files."""
    if not QUESTIONS_DIR.exists():
        return []
    return sorted(p.stem for p in QUESTIONS_DIR.glob("*.jsonl"))


def stats(topic_slug: str, today: date | None = None) -> dict:
    """Summary stats for a topic's question bank."""
    today = today or date.today()
    cards = read_cards(topic_slug)
    due = [c for c in cards if not c.suspended and not c.mastered and is_due(CardSchedule.from_dict(c.schedule), today)]
    return {
        "total": len(cards),
        "due": len(due),
        "mastered": sum(1 for c in cards if c.mastered),
        "suspended": sum(1 for c in cards if c.suspended),
        "active": sum(1 for c in cards if not c.suspended and not c.mastered),
    }
