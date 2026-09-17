#!/usr/bin/env python3
"""Question bank: JSONL storage for spaced repetition cards.

Storage convention (#255 — per-user store is private):
  learning-records/questions/<topic-slug>.jsonl         — committed card definitions
  .user/learning-records/questions/<topic-slug>.jsonl   — private card definitions
  .user/learning-records/card-state.json                — local schedule/lifecycle state
  .user/learning-records/reviews.jsonl                  — append-only review log

Resolve via questions_dir_for(workspace) / reviews_log_for(workspace): read a local topic
when present and otherwise fall back to the committed fixture. Effective cards join immutable
definitions with local state by card ID; mutations write only local state.
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


def user_records_dir_for(workspace: Path) -> Path:
    """Private, writable SR root for a workspace."""
    return workspace / ".user" / "learning-records"


def fixture_records_dir_for(workspace: Path) -> Path:
    """Optional committed, read-only SR fixture root for a workspace."""
    return workspace / "learning-records"


def questions_dir_for(workspace: Path) -> Path:
    """Preferred question directory for read-only directory consumers."""
    user_questions = user_records_dir_for(workspace) / "questions"
    return user_questions if user_questions.exists() else fixture_records_dir_for(workspace) / "questions"


def reviews_log_for(workspace: Path) -> Path:
    """Private `reviews.jsonl` path for a workspace."""
    return user_records_dir_for(workspace) / "reviews.jsonl"


# Module-level defaults: use workspace/ if it exists, else project root.
_WORKSPACE = _PROJECT_ROOT / "workspace"
_DEFAULT_WS = _WORKSPACE if _WORKSPACE.exists() else _PROJECT_ROOT
QUESTIONS_DIR = questions_dir_for(_DEFAULT_WS)
USER_QUESTIONS_DIR = user_records_dir_for(_DEFAULT_WS) / "questions"
FIXTURE_QUESTIONS_DIR = fixture_records_dir_for(_DEFAULT_WS) / "questions"
REVIEWS_LOG = reviews_log_for(_DEFAULT_WS)
CARD_STATE_PATH = user_records_dir_for(_DEFAULT_WS) / "card-state.json"
_STATE_SCHEMA = 1


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
    source_section: str = ""    # Heading of source chunk this card was derived from
    source_page: int | None = None  # Page number / chunk index from source document
    source_quote: str = ""      # Exact passage that teaches the answer (plain text)
    derivation: str = ""        # "direct" | "inference" | "synthesis"
    level: str = ""             # "L1" | "L2" | "L3"
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

    def definition_json(self) -> str:
        """Serialize shareable content without learner-specific state."""
        data = asdict(self)
        for key in ("schedule", "suspended", "mastered"):
            data.pop(key)
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> "Card":
        d = json.loads(line)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def user_topic_path(topic_slug: str) -> Path:
    """Private writable path for a topic's cards."""
    return USER_QUESTIONS_DIR / f"{topic_slug}.jsonl"


def ensure_dirs() -> None:
    """Create only the private SR storage directories."""
    USER_QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_LOG.parent.mkdir(parents=True, exist_ok=True)


def _read_cards(path: Path) -> list[Card]:
    if not path.exists():
        return []
    return [Card.from_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_state() -> dict:
    if not CARD_STATE_PATH.exists():
        return {"schema": _STATE_SCHEMA, "cards": {}, "migrated_topics": []}
    try:
        state = json.loads(CARD_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema": _STATE_SCHEMA, "cards": {}, "migrated_topics": []}
    if not isinstance(state.get("cards"), dict):
        return {"schema": _STATE_SCHEMA, "cards": {}, "migrated_topics": []}
    state.setdefault("migrated_topics", [])
    return state


def _write_state(state: dict) -> None:
    ensure_dirs()
    CARD_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _state_for(card: Card) -> dict:
    return {"schedule": card.schedule, "suspended": card.suspended, "mastered": card.mastered}


def save_card_states(cards: list[Card]) -> None:
    """Persist only mutable learner state, keyed by canonical card ID."""
    state = _load_state()
    state["cards"].update({card.id: _state_for(card) for card in cards})
    _write_state(state)


def _migrate_legacy_private_topic(topic_slug: str) -> None:
    """Split old full-card private copies into definitions plus state without data loss."""
    path = user_topic_path(topic_slug)
    if not path.exists():
        return
    state = _load_state()
    if topic_slug in state["migrated_topics"]:
        return
    fixture_ids = {card.id for card in _read_cards(FIXTURE_QUESTIONS_DIR / f"{topic_slug}.jsonl")}
    private_cards = _read_cards(path)
    remaining = []
    for card in private_cards:
        state["cards"].setdefault(card.id, _state_for(card))
        if card.id not in fixture_ids:
            remaining.append(card)
    if remaining:
        path.write_text("".join(card.definition_json() + "\n" for card in remaining), encoding="utf-8")
    else:
        path.unlink()
    state["migrated_topics"].append(topic_slug)
    _write_state(state)


def append_card(topic_slug: str, card: Card) -> None:
    """Append a private card definition; its learner state starts absent."""
    ensure_dirs()
    path = user_topic_path(topic_slug)
    with open(path, "a", encoding="utf-8") as f:
        f.write(card.definition_json() + "\n")


def read_cards(topic_slug: str) -> list[Card]:
    """Join public/private definitions with local learner state by card ID."""
    _migrate_legacy_private_topic(topic_slug)
    cards = {card.id: card for card in _read_cards(FIXTURE_QUESTIONS_DIR / f"{topic_slug}.jsonl")}
    cards.update({card.id: card for card in _read_cards(user_topic_path(topic_slug))})
    state = _load_state()["cards"]
    for card in cards.values():
        if local := state.get(card.id):
            card.schedule = local.get("schedule", card.schedule)
            card.suspended = local.get("suspended", card.suspended)
            card.mastered = local.get("mastered", card.mastered)
    return list(cards.values())


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
    for topic_slug in list_topics():
        due.extend(get_due_cards(topic_slug, today))
    return due


def review_card(topic_slug: str, card_id: str, quality: int, today: date | None = None) -> Card | None:
    """Review a card: update its schedule in-place and log the review.

    Rewrites the topic file with the updated card. Returns the updated card or None if not found.
    """
    today = today or date.today()
    cards = read_cards(topic_slug)
    if not cards:
        return None
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

    save_card_states([updated_card])

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
    return sorted({p.stem for directory in (USER_QUESTIONS_DIR, FIXTURE_QUESTIONS_DIR)
                   if directory.exists() for p in directory.glob("*.jsonl")})


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
