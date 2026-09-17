"""Concurrent SR event writes serialize into ordered, replayable streams (#365)."""

from __future__ import annotations

import multiprocessing
import sqlite3
import sys
import threading
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import questions


def _configure(monkeypatch, root: Path) -> Path:
    fixture = root / "learning-records" / "questions"
    user = root / ".user" / "learning-records" / "questions"
    monkeypatch.setattr(questions, "FIXTURE_QUESTIONS_DIR", fixture)
    monkeypatch.setattr(questions, "USER_QUESTIONS_DIR", user)
    monkeypatch.setattr(questions, "REVIEWS_LOG", user.parent / "reviews.jsonl")
    monkeypatch.setattr(questions, "CARD_STATE_PATH", user.parent / "card-state.json")
    monkeypatch.setattr(questions, "EVENT_STORE_PATH", user.parent / "sr-events.sqlite3")
    return fixture


def _child_writer(root_str: str, card_id: str, reviews: int) -> None:
    root = Path(root_str)
    user = root / ".user" / "learning-records" / "questions"
    questions.FIXTURE_QUESTIONS_DIR = root / "learning-records" / "questions"
    questions.USER_QUESTIONS_DIR = user
    questions.REVIEWS_LOG = user.parent / "reviews.jsonl"
    questions.CARD_STATE_PATH = user.parent / "card-state.json"
    questions.EVENT_STORE_PATH = user.parent / "sr-events.sqlite3"
    card = questions.Card(id=card_id, prompt="p")
    for _ in range(reviews):
        questions.record_card_event("contention", card, "reviewed", rating=4, effective_date=date(2026, 9, 17))


def _card_events(card_id: str) -> list[dict]:
    return [event for event in questions.iter_events() if event["card_id"] == card_id]


def test_same_card_thread_contention_serializes_into_one_chain(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    card = questions.Card(id="shared-card", prompt="p")
    today = date(2026, 9, 17)
    workers, errors = [], []
    barrier = threading.Barrier(8)

    def worker() -> None:
        try:
            barrier.wait()
            questions.record_card_event("contention", card, "reviewed", rating=4, effective_date=today)
        except Exception as error:  # noqa: BLE001 - surfaced by the assert below
            errors.append(error)

    for _ in range(8):
        thread = threading.Thread(target=worker)
        thread.start()
        workers.append(thread)
    for thread in workers:
        thread.join(timeout=60)
    assert errors == []

    events = _card_events("shared-card")
    assert len(events) == 8
    previous = None
    for event in events:
        assert event["previous_event_id"] == previous, "two writers derived from one predecessor"
        previous = event["event_id"]
    with sqlite3.connect(questions.EVENT_STORE_PATH) as connection:
        row = connection.execute(
            "SELECT last_event_id FROM card_projection WHERE card_id = 'shared-card'"
        ).fetchone()
    assert row[0] == previous
    questions.rebuild_projection()
    assert len(_card_events("shared-card")) == 8


def test_different_card_thread_contention_preserves_every_event(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    today = date(2026, 9, 17)
    cards = [questions.Card(id=f"card-{index}", prompt="p") for index in range(6)]
    workers, errors = [], []
    barrier = threading.Barrier(6)

    def worker(card: questions.Card) -> None:
        try:
            barrier.wait()
            for _ in range(2):
                questions.record_card_event("contention", card, "reviewed", rating=3, effective_date=today)
        except Exception as error:  # noqa: BLE001 - surfaced by the assert below
            errors.append(error)

    for card in cards:
        thread = threading.Thread(target=worker, args=(card,))
        thread.start()
        workers.append(thread)
    for thread in workers:
        thread.join(timeout=60)
    assert errors == []
    for card in cards:
        events = _card_events(card.id)
        assert len(events) == 2
        assert events[1]["previous_event_id"] == events[0]["event_id"]


def test_cross_process_writers_serialize_and_preserve_events(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    context = multiprocessing.get_context("spawn")
    processes = [
        context.Process(target=_child_writer, args=(str(tmp_path), "shared-card", 3)),
        context.Process(target=_child_writer, args=(str(tmp_path), "shared-card", 3)),
        context.Process(target=_child_writer, args=(str(tmp_path), "solo-card", 2)),
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=120)
    assert all(process.exitcode == 0 for process in processes), \
        f"child exit codes: {[p.exitcode for p in processes]}"

    shared = _card_events("shared-card")
    solo = _card_events("solo-card")
    assert len(shared) == 6
    assert len(solo) == 2
    previous = None
    for event in shared:
        assert event["previous_event_id"] == previous
        previous = event["event_id"]
    questions.rebuild_projection()
    assert len(_card_events("shared-card")) == 6 and len(_card_events("solo-card")) == 2


def test_prolonged_external_lock_yields_retryable_error_not_raw_sqlite(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    card = questions.Card(id="locked-card", prompt="p")
    today = date(2026, 9, 17)
    questions.record_card_event("contention", card, "reviewed", rating=3, effective_date=today)

    monkeypatch.setattr(questions, "_BUSY_TIMEOUT_MS", 50)
    monkeypatch.setattr(questions, "_WRITE_ATTEMPTS", 2)
    monkeypatch.setattr(questions, "_WRITE_RETRY_BACKOFF_S", 0.01)
    lock = sqlite3.connect(questions.EVENT_STORE_PATH, timeout=0.05)
    lock.execute("BEGIN IMMEDIATE")
    lock.execute("INSERT OR IGNORE INTO store_meta(key, value) VALUES ('lock-probe', '1')")
    try:
        with pytest.raises(questions.EventStoreError) as excinfo:
            questions.record_card_event("contention", card, "reviewed", rating=4, effective_date=today)
        assert "retry" in str(excinfo.value).lower()
    finally:
        lock.rollback()
        lock.close()

    questions.record_card_event("contention", card, "reviewed", rating=4, effective_date=today)
    assert len(_card_events("locked-card")) == 2
