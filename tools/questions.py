#!/usr/bin/env python3
"""Shared card definitions and private, replayable learner progress."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterator

from sm2 import CardSchedule, is_due, review


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVENT_SCHEMA = 1
SCHEDULER_VERSION = "sm2-v1"
_STATE_SCHEMA = 1
_EVENT_ACTIONS = {"reviewed", "suspended", "unsuspended", "reset", "retired", "state_snapshot"}
# Same-card writes serialize through BEGIN IMMEDIATE; a writer held out longer than
# the busy timeout retries with backoff before surfacing a retryable EventStoreError.
_BUSY_TIMEOUT_MS = 5_000
_WRITE_ATTEMPTS = 6
_WRITE_RETRY_BACKOFF_S = 0.05


def user_records_dir_for(workspace: Path) -> Path:
    return workspace / ".user" / "learning-records"


def fixture_records_dir_for(workspace: Path) -> Path:
    return workspace / "learning-records"


def questions_dir_for(workspace: Path) -> Path:
    user_questions = user_records_dir_for(workspace) / "questions"
    return user_questions if user_questions.exists() else fixture_records_dir_for(workspace) / "questions"


def reviews_log_for(workspace: Path) -> Path:
    """Legacy pre-event review-log path, retained for migration only."""
    return user_records_dir_for(workspace) / "reviews.jsonl"


_WORKSPACE = _PROJECT_ROOT / "workspace"
_DEFAULT_WS = _WORKSPACE if _WORKSPACE.exists() else _PROJECT_ROOT
QUESTIONS_DIR = questions_dir_for(_DEFAULT_WS)
USER_QUESTIONS_DIR = user_records_dir_for(_DEFAULT_WS) / "questions"
FIXTURE_QUESTIONS_DIR = fixture_records_dir_for(_DEFAULT_WS) / "questions"
REVIEWS_LOG = reviews_log_for(_DEFAULT_WS)
CARD_STATE_PATH = user_records_dir_for(_DEFAULT_WS) / "card-state.json"
EVENT_STORE_PATH = user_records_dir_for(_DEFAULT_WS) / "sr-events.sqlite3"


class EventStoreError(RuntimeError):
    """The local event stream cannot safely produce a projection."""


class LegacyReviewLogError(EventStoreError):
    """Legacy prefix-ID history needs an explicit migration."""


@dataclass
class Card:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    expected_answer: str = ""
    question_type: str = "explain"
    difficulty_tier: str = "understand"
    lesson_id: str = ""
    section_heading: str = ""
    source_section: str = ""
    source_page: int | None = None
    source_quote: str = ""
    derivation: str = ""
    level: str = ""
    generated_by: str = "teach-skill"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    schedule: dict = field(default_factory=lambda: CardSchedule().to_dict())
    tags: list[str] = field(default_factory=list)
    suspended: bool = False
    mastered: bool = False
    prompt_code: dict | None = None
    answer_code: dict | None = None
    options: list[str] | None = None
    correct_index: int | None = None
    explanation: str | None = None
    sources: list[dict] | None = None
    svg_ref: dict | None = None
    occluded_labels: list[str] | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    def definition_json(self) -> str:
        data = asdict(self)
        for key in ("schedule", "suspended", "mastered"):
            data.pop(key)
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> "Card":
        data = json.loads(line)
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})


def user_topic_path(topic_slug: str) -> Path:
    return USER_QUESTIONS_DIR / f"{topic_slug}.jsonl"


def ensure_dirs() -> None:
    USER_QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_cards(path: Path) -> list[Card]:
    if not path.exists():
        return []
    return [Card.from_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _load_legacy_state() -> dict:
    if not CARD_STATE_PATH.exists():
        return {"schema": _STATE_SCHEMA, "cards": {}, "migrated_topics": []}
    try:
        state = json.loads(CARD_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise LegacyReviewLogError(f"Malformed legacy projection at {CARD_STATE_PATH}: {error}") from error
    if not isinstance(state.get("cards"), dict):
        raise LegacyReviewLogError(f"Malformed legacy projection at {CARD_STATE_PATH}: missing cards object")
    state.setdefault("migrated_topics", [])
    return state


def _write_legacy_state(state: dict) -> None:
    ensure_dirs()
    CARD_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _state_for(card: Card) -> dict:
    return {"schedule": card.schedule, "suspended": card.suspended, "mastered": card.mastered}


def _migrate_legacy_private_topic(topic_slug: str) -> None:
    path = user_topic_path(topic_slug)
    if not path.exists():
        return
    state = _load_legacy_state()
    if topic_slug in state["migrated_topics"]:
        return
    fixture_ids = {card.id for card in _read_cards(FIXTURE_QUESTIONS_DIR / f"{topic_slug}.jsonl")}
    remaining = []
    for card in _read_cards(path):
        state["cards"].setdefault(card.id, _state_for(card))
        if card.id not in fixture_ids:
            remaining.append(card)
    if remaining:
        path.write_text("".join(card.definition_json() + "\n" for card in remaining), encoding="utf-8")
    else:
        path.unlink()
    state["migrated_topics"].append(topic_slug)
    _write_legacy_state(state)


def _connect() -> sqlite3.Connection:
    ensure_dirs()
    connection = sqlite3.connect(EVENT_STORE_PATH, timeout=_BUSY_TIMEOUT_MS / 1000)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
    # DDL only: CREATE IF NOT EXISTS on existing tables takes no write lock, so
    # connecting never contends with writers. store_meta seeds happen inside write
    # transactions instead (see record_card_event / rebuild_projection).
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS store_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (
          sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
          occurred_at TEXT NOT NULL, topic TEXT NOT NULL, card_id TEXT NOT NULL,
          action TEXT NOT NULL CHECK (action IN ('reviewed','suspended','unsuspended','reset','retired','state_snapshot')),
          rating INTEGER CHECK (rating IS NULL OR rating BETWEEN 0 AND 5), scheduler_version TEXT NOT NULL,
          effective_date TEXT, previous_event_id TEXT, result_state TEXT NOT NULL, schema_version INTEGER NOT NULL,
          FOREIGN KEY (previous_event_id) REFERENCES events(event_id)
        );
        CREATE TABLE IF NOT EXISTS card_projection (
          card_id TEXT PRIMARY KEY, schedule TEXT NOT NULL, suspended INTEGER NOT NULL, mastered INTEGER NOT NULL,
          last_event_id TEXT NOT NULL, last_sequence INTEGER NOT NULL
        );
        """
    )
    return connection


@contextmanager
def _store_connection() -> Iterator[sqlite3.Connection]:
    """Open the event store with transaction semantics AND a deterministic close (#377).

    `with sqlite3.Connection` alone commits/rolls back but never closes, so connections
    previously lingered until GC/process exit — and `iter_events`, which yields inside
    the block, could strand one (with its read snapshot) when a consumer abandoned the
    generator. The finally-close fixes all exit paths: normal, exception, and
    GeneratorExit.
    """
    connection = _connect()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _meta(connection: sqlite3.Connection, key: str) -> str | None:
    row = connection.execute("SELECT value FROM store_meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def _set_meta(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT INTO store_meta(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _event_from_state(topic: str, card_id: str, action: str, state: dict, previous_event_id: str | None,
                      rating: int | None = None, effective_date: str | None = None,
                      scheduler_version: str = SCHEDULER_VERSION) -> dict:
    if action not in _EVENT_ACTIONS:
        raise ValueError(f"Unsupported event action: {action}")
    if action == "reviewed" and rating is None:
        raise ValueError("A reviewed event requires a rating")
    return {
        "event_id": str(uuid.uuid4()), "occurred_at": _utc_now(), "topic": topic, "card_id": card_id,
        "action": action, "rating": rating, "scheduler_version": scheduler_version,
        "effective_date": effective_date, "previous_event_id": previous_event_id,
        "result_state": state, "schema_version": EVENT_SCHEMA,
    }


def _validate_state(state: dict, event_id: str) -> None:
    if not isinstance(state, dict) or not isinstance(state.get("schedule"), dict):
        raise EventStoreError(f"Event {event_id} has no schedule result")
    try:
        CardSchedule.from_dict(state["schedule"])
    except TypeError as error:
        raise EventStoreError(f"Event {event_id} has an invalid schedule result") from error
    if not isinstance(state.get("suspended"), bool) or not isinstance(state.get("mastered"), bool):
        raise EventStoreError(f"Event {event_id} has invalid lifecycle state")


def _decode_event(row: sqlite3.Row) -> dict:
    try:
        state = json.loads(row["result_state"])
    except json.JSONDecodeError as error:
        raise EventStoreError(f"Event {row['event_id']} has malformed result state") from error
    event = dict(row)
    event["result_state"] = state
    if event["schema_version"] != EVENT_SCHEMA or event["action"] not in _EVENT_ACTIONS:
        raise EventStoreError(f"Unsupported event version or action for {event['event_id']}")
    if event["action"] == "reviewed" and event["rating"] is None:
        raise EventStoreError(f"Review event {event['event_id']} has no rating")
    _validate_state(state, event["event_id"])
    return event


def _apply_event(previous: dict | None, event: dict) -> dict:
    previous = previous or {"schedule": CardSchedule().to_dict(), "suspended": False, "mastered": False}
    result = event["result_state"]
    if event["action"] == "reviewed":
        if event["scheduler_version"] != SCHEDULER_VERSION or not event["effective_date"]:
            raise EventStoreError(f"Review event {event['event_id']} has unsupported scheduler metadata")
        schedule = review(CardSchedule.from_dict(previous["schedule"]), event["rating"], date.fromisoformat(event["effective_date"])).to_dict()
        expected = {"schedule": schedule, "suspended": previous["suspended"],
                    "mastered": previous["mastered"] or schedule["interval_days"] >= 180}
        if result != expected:
            raise EventStoreError(f"Review event {event['event_id']} result does not match {SCHEDULER_VERSION}")
    return result


def _rebuild_projection(connection: sqlite3.Connection) -> None:
    events = [_decode_event(row) for row in connection.execute("SELECT * FROM events ORDER BY sequence")]
    states: dict[str, dict] = {}
    last_events: dict[str, tuple[str, int]] = {}
    connection.execute("DELETE FROM card_projection")
    for event in events:
        previous = last_events.get(event["card_id"])
        if event["previous_event_id"] != (previous[0] if previous else None):
            raise EventStoreError(f"Event {event['event_id']} has a missing or out-of-order predecessor")
        state = _apply_event(states.get(event["card_id"]), event)
        states[event["card_id"]] = state
        last_events[event["card_id"]] = (event["event_id"], event["sequence"])
        connection.execute(
            """INSERT INTO card_projection VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(card_id) DO UPDATE SET schedule = excluded.schedule, suspended = excluded.suspended,
               mastered = excluded.mastered, last_event_id = excluded.last_event_id, last_sequence = excluded.last_sequence""",
            (event["card_id"], json.dumps(state["schedule"], sort_keys=True), state["suspended"],
             state["mastered"], event["event_id"], event["sequence"]),
        )
    _set_meta(connection, "projection_sequence", str(events[-1]["sequence"] if events else 0))


def _ensure_legacy_migrated(connection: sqlite3.Connection) -> None:
    if _meta(connection, "legacy_jsonl_v0"):
        return
    legacy_state = _load_legacy_state()
    legacy_reviews = REVIEWS_LOG.exists() and REVIEWS_LOG.read_text(encoding="utf-8").strip()
    if legacy_reviews and not legacy_state["cards"]:
        raise LegacyReviewLogError(
            "Legacy prefix-ID review history cannot be replayed without card-state.json. Restore it or reset local progress."
        )
    for card_id, state in sorted(legacy_state["cards"].items()):
        event = _event_from_state("legacy", card_id, "state_snapshot", state, None, scheduler_version="legacy-state-v1")
        connection.execute(
            """INSERT INTO events(event_id, occurred_at, topic, card_id, action, rating, scheduler_version,
               effective_date, previous_event_id, result_state, schema_version)
               VALUES (:event_id, :occurred_at, :topic, :card_id, :action, :rating, :scheduler_version,
               :effective_date, :previous_event_id, :result_state, :schema_version)""",
            {**event, "result_state": json.dumps(event["result_state"], sort_keys=True)},
        )
    _set_meta(connection, "legacy_jsonl_v0", "migrated")
    _rebuild_projection(connection)


def _ensure_projection(connection: sqlite3.Connection) -> None:
    _ensure_legacy_migrated(connection)
    max_sequence = connection.execute("SELECT COALESCE(MAX(sequence), 0) AS value FROM events").fetchone()["value"]
    if _meta(connection, "projection_sequence") != str(max_sequence):
        _rebuild_projection(connection)


def rebuild_projection() -> None:
    """Replace the local projection with deterministic replay of canonical events."""
    with _store_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if _meta(connection, "event_schema") is None:
                _set_meta(connection, "event_schema", str(EVENT_SCHEMA))
            _ensure_legacy_migrated(connection)
            _rebuild_projection(connection)
            connection.commit()
        except Exception:
            connection.rollback()
            raise


def _projected_state(connection: sqlite3.Connection, card_id: str) -> tuple[dict, str | None]:
    row = connection.execute("SELECT schedule, suspended, mastered, last_event_id FROM card_projection WHERE card_id = ?", (card_id,)).fetchone()
    if not row:
        return ({"schedule": CardSchedule().to_dict(), "suspended": False, "mastered": False}, None)
    return ({"schedule": json.loads(row["schedule"]), "suspended": bool(row["suspended"]),
             "mastered": bool(row["mastered"])}, row["last_event_id"])


def record_card_event(topic_slug: str, card: Card, action: str, *, rating: int | None = None,
                      effective_date: date | None = None) -> str:
    """Atomically append one event and its derived projection update.

    The write transaction (BEGIN IMMEDIATE) is acquired BEFORE the card's projected
    state is read, so concurrent reviews of one card serialize into an ordered event
    stream instead of deriving from the same predecessor. A `reviewed` result is
    derived from the projected state inside the transaction — the replay contract
    (_apply_event) recomputes exactly this — so a serialized second writer chains on
    the first writer's schedule rather than poisoning the replay. Writers held out
    past the busy timeout retry with backoff and finally raise a retryable
    EventStoreError; raw sqlite3.OperationalError never reaches the caller.
    """
    if action == "reviewed" and effective_date is None:
        raise ValueError("A reviewed event requires an effective_date")
    with _store_connection() as connection:
        for attempt in range(_WRITE_ATTEMPTS):
            try:
                connection.execute("BEGIN IMMEDIATE")
                if _meta(connection, "event_schema") is None:
                    _set_meta(connection, "event_schema", str(EVENT_SCHEMA))
                _ensure_projection(connection)
                state, previous_event_id = _projected_state(connection, card.id)
                if action == "reviewed":
                    schedule = review(CardSchedule.from_dict(state["schedule"]), rating, effective_date).to_dict()
                    result_state = {"schedule": schedule, "suspended": state["suspended"],
                                    "mastered": state["mastered"] or schedule["interval_days"] >= 180}
                else:
                    result_state = _state_for(card)
                event = _event_from_state(topic_slug, card.id, action, result_state, previous_event_id, rating,
                                          effective_date.isoformat() if effective_date else None)
                connection.execute(
                    """INSERT INTO events(event_id, occurred_at, topic, card_id, action, rating, scheduler_version,
                       effective_date, previous_event_id, result_state, schema_version)
                       VALUES (:event_id, :occurred_at, :topic, :card_id, :action, :rating, :scheduler_version,
                       :effective_date, :previous_event_id, :result_state, :schema_version)""",
                    {**event, "result_state": json.dumps(event["result_state"], sort_keys=True)},
                )
                sequence = connection.execute("SELECT sequence FROM events WHERE event_id = ?", (event["event_id"],)).fetchone()["sequence"]
                connection.execute(
                    """INSERT INTO card_projection VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(card_id) DO UPDATE SET schedule = excluded.schedule, suspended = excluded.suspended,
                       mastered = excluded.mastered, last_event_id = excluded.last_event_id, last_sequence = excluded.last_sequence""",
                    (card.id, json.dumps(result_state["schedule"], sort_keys=True), result_state["suspended"],
                     result_state["mastered"], event["event_id"], sequence),
                )
                _set_meta(connection, "projection_sequence", str(sequence))
                connection.commit()
                return event["event_id"]
            except sqlite3.OperationalError as error:
                connection.rollback()
                if "lock" not in str(error).lower() and "busy" not in str(error).lower():
                    raise
                if attempt == _WRITE_ATTEMPTS - 1:
                    raise EventStoreError(
                        f"SR event store stayed locked after {_WRITE_ATTEMPTS} attempts; retry the review"
                    ) from error
                time.sleep(_WRITE_RETRY_BACKOFF_S)
            except Exception:
                connection.rollback()
                raise
    raise EventStoreError("unreachable: write retry loop exhausted without raising")


def iter_events() -> Iterator[dict]:
    with _store_connection() as connection:
        _ensure_projection(connection)
        for row in connection.execute("SELECT * FROM events ORDER BY sequence"):
            yield _decode_event(row)


def append_card(topic_slug: str, card: Card) -> None:
    ensure_dirs()
    with user_topic_path(topic_slug).open("a", encoding="utf-8") as file:
        file.write(card.definition_json() + "\n")


def read_cards(topic_slug: str) -> list[Card]:
    _migrate_legacy_private_topic(topic_slug)
    cards = {card.id: card for card in _read_cards(FIXTURE_QUESTIONS_DIR / f"{topic_slug}.jsonl")}
    cards.update({card.id: card for card in _read_cards(user_topic_path(topic_slug))})
    with _store_connection() as connection:
        _ensure_projection(connection)
        projection = {row["card_id"]: {"schedule": json.loads(row["schedule"]),
                      "suspended": bool(row["suspended"]), "mastered": bool(row["mastered"])}
                      for row in connection.execute("SELECT card_id, schedule, suspended, mastered FROM card_projection")}
    for card in cards.values():
        if state := projection.get(card.id):
            card.schedule, card.suspended, card.mastered = state["schedule"], state["suspended"], state["mastered"]
    return list(cards.values())


def get_due_cards(topic_slug: str, today: date | None = None) -> list[Card]:
    today = today or date.today()
    return [card for card in read_cards(topic_slug) if not card.suspended and not card.mastered
            and is_due(CardSchedule.from_dict(card.schedule), today)]


def get_all_due_cards(today: date | None = None) -> list[Card]:
    today = today or date.today()
    return [card for topic in list_topics() for card in get_due_cards(topic, today)]


def _resolve_card(cards: list[Card], card_id: str) -> Card | None:
    matches = [card for card in cards if card.id == card_id or card.id.startswith(card_id)]
    if len(matches) > 1:
        raise ValueError(f"Card ID prefix {card_id!r} is ambiguous")
    return matches[0] if matches else None


def review_card(topic_slug: str, card_id: str, quality: int, today: date | None = None) -> Card | None:
    today = today or date.today()
    card = _resolve_card(read_cards(topic_slug), card_id)
    if card is None:
        return None
    card.schedule = review(CardSchedule.from_dict(card.schedule), quality, today).to_dict()
    card.mastered = card.mastered or card.schedule["interval_days"] >= 180
    record_card_event(topic_slug, card, "reviewed", rating=quality, effective_date=today)
    return card


def list_topics() -> list[str]:
    return sorted({path.stem for directory in (USER_QUESTIONS_DIR, FIXTURE_QUESTIONS_DIR)
                   if directory.exists() for path in directory.glob("*.jsonl")})


def stats(topic_slug: str, today: date | None = None) -> dict:
    today = today or date.today()
    cards = read_cards(topic_slug)
    due = [card for card in cards if not card.suspended and not card.mastered
           and is_due(CardSchedule.from_dict(card.schedule), today)]
    return {"total": len(cards), "due": len(due), "mastered": sum(card.mastered for card in cards),
            "suspended": sum(card.suspended for card in cards),
            "active": sum(not card.suspended and not card.mastered for card in cards)}
