"""Deterministic connection close for the SR event store (#377).

`with sqlite3.Connection` commits/rolls back but never closes. `_store_connection`
adds the finally-close; these tests pin that every entry point releases its
connection on success, on exception, and when a consumer abandons `iter_events`
mid-iteration.
"""

from __future__ import annotations

import gc
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import questions


class _TrackedConnection(sqlite3.Connection):
    opened = 0
    closed = 0

    def close(self):
        type(self).closed += 1
        super().close()


@pytest.fixture
def tracked_store(monkeypatch, tmp_path):
    user = tmp_path / ".user" / "learning-records" / "questions"
    monkeypatch.setattr(questions, "FIXTURE_QUESTIONS_DIR", tmp_path / "learning-records" / "questions")
    monkeypatch.setattr(questions, "USER_QUESTIONS_DIR", user)
    monkeypatch.setattr(questions, "REVIEWS_LOG", user.parent / "reviews.jsonl")
    monkeypatch.setattr(questions, "CARD_STATE_PATH", user.parent / "card-state.json")
    monkeypatch.setattr(questions, "EVENT_STORE_PATH", user.parent / "sr-events.sqlite3")

    _TrackedConnection.opened = 0
    _TrackedConnection.closed = 0
    real_connect = sqlite3.connect

    def connect(*args, **kwargs):
        kwargs["factory"] = _TrackedConnection
        _TrackedConnection.opened += 1
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(questions.sqlite3, "connect", connect)
    return user


def _seed_card(fixture_dir: Path, card_id: str = "conn-card") -> questions.Card:
    card = questions.Card(id=card_id, prompt="Explain the boundary.")
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "lifecycle.jsonl").write_text(card.definition_json() + "\n", encoding="utf-8")
    return card


def test_success_paths_close_every_connection(tracked_store, monkeypatch):
    fixture_dir = questions.FIXTURE_QUESTIONS_DIR
    _seed_card(fixture_dir)

    questions.review_card("lifecycle", "conn-card", 4, today=date(2026, 9, 18))
    questions.review_card("lifecycle", "conn-card", 5, today=date(2026, 9, 19))
    questions.read_cards("lifecycle")
    events = list(questions.iter_events())
    questions.rebuild_projection()

    assert len(events) == 2
    assert _TrackedConnection.opened >= 4
    assert _TrackedConnection.closed == _TrackedConnection.opened


def test_abandoned_iter_events_still_closes(tracked_store):
    fixture_dir = questions.FIXTURE_QUESTIONS_DIR
    card = _seed_card(fixture_dir)
    questions.review_card("lifecycle", card.id, 4, today=date(2026, 9, 18))
    questions.review_card("lifecycle", card.id, 5, today=date(2026, 9, 19))
    assert _TrackedConnection.closed == _TrackedConnection.opened

    generator = questions.iter_events()
    next(generator)  # consume one event, then abandon mid-iteration
    del generator
    gc.collect()

    assert _TrackedConnection.closed == _TrackedConnection.opened


def test_exception_path_closes_connection(tracked_store, monkeypatch):
    fixture_dir = questions.FIXTURE_QUESTIONS_DIR
    card = _seed_card(fixture_dir)
    questions.review_card("lifecycle", card.id, 4, today=date(2026, 9, 18))

    def _explode(previous, event):
        raise questions.EventStoreError("injected replay failure")

    monkeypatch.setattr(questions, "_apply_event", _explode)
    with pytest.raises(questions.EventStoreError):
        questions.rebuild_projection()

    assert _TrackedConnection.closed == _TrackedConnection.opened


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
