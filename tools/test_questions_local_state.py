"""Shared card definitions and private SR events stay separate and recoverable."""

from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
import json
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import questions


def _configure(monkeypatch, root: Path) -> tuple[Path, Path]:
    fixture = root / "learning-records" / "questions"
    user = root / ".user" / "learning-records" / "questions"
    monkeypatch.setattr(questions, "FIXTURE_QUESTIONS_DIR", fixture)
    monkeypatch.setattr(questions, "USER_QUESTIONS_DIR", user)
    monkeypatch.setattr(questions, "REVIEWS_LOG", user.parent / "reviews.jsonl")
    monkeypatch.setattr(questions, "CARD_STATE_PATH", user.parent / "card-state.json")
    monkeypatch.setattr(questions, "EVENT_STORE_PATH", user.parent / "sr-events.sqlite3")
    return fixture, user


def _fixture_card(fixture: Path, card_id: str = "fixture-card") -> questions.Card:
    card = questions.Card(id=card_id, prompt="Explain the boundary.")
    fixture.mkdir(parents=True)
    (fixture / "privacy.jsonl").write_text(card.definition_json() + "\n", encoding="utf-8")
    return card


def test_review_writes_canonical_local_event_without_copying_definition(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    card = _fixture_card(fixture)

    updated = questions.review_card("privacy", "fixture-card", 5, today=date(2026, 9, 17))

    assert updated is not None
    assert (fixture / "privacy.jsonl").read_text(encoding="utf-8") == card.definition_json() + "\n"
    assert not (user / "privacy.jsonl").exists()
    events = list(questions.iter_events())
    assert len(events) == 1
    event = events[0]
    assert event["card_id"] == "fixture-card"
    assert event["action"] == "reviewed"
    assert event["rating"] == 5
    assert event["scheduler_version"] == questions.SCHEDULER_VERSION
    assert event["occurred_at"].endswith("Z")
    assert event["result_state"] == {"schedule": updated.schedule, "suspended": False, "mastered": False}
    assert questions.EVENT_STORE_PATH.is_file()


def test_rebuild_replaces_projection_from_event_fixture(monkeypatch, tmp_path):
    fixture, _ = _configure(monkeypatch, tmp_path)
    _fixture_card(fixture)
    expected = questions.review_card("privacy", "fixture-card", 5, today=date(2026, 9, 17))
    expected = questions.review_card("privacy", "fixture-card", 4, today=date(2026, 9, 18))

    with questions._connect() as connection:
        connection.execute("DELETE FROM card_projection")
        connection.execute("UPDATE store_meta SET value = '0' WHERE key = 'projection_sequence'")
    questions.rebuild_projection()

    rebuilt = questions.read_cards("privacy")[0]
    assert rebuilt.schedule == expected.schedule
    assert (rebuilt.suspended, rebuilt.mastered) == (expected.suspended, expected.mastered)


def test_lifecycle_events_replay_reset_and_retirement(monkeypatch, tmp_path):
    fixture, _ = _configure(monkeypatch, tmp_path)
    card = _fixture_card(fixture)
    card.suspended = True
    questions.record_card_event("privacy", card, "suspended")
    card.suspended = False
    questions.record_card_event("privacy", card, "unsuspended")
    card.schedule = questions.Card().schedule
    questions.record_card_event("privacy", card, "reset")
    card.schedule = {**card.schedule, "interval_days": 180}
    card.mastered = True
    questions.record_card_event("privacy", card, "retired")

    questions.rebuild_projection()
    rebuilt = questions.read_cards("privacy")[0]
    assert [event["action"] for event in questions.iter_events()] == ["suspended", "unsuspended", "reset", "retired"]
    assert rebuilt.mastered and not rebuilt.suspended and rebuilt.schedule["interval_days"] == 180


def test_duplicate_and_missing_events_are_rejected_without_projection_change(monkeypatch, tmp_path):
    fixture, _ = _configure(monkeypatch, tmp_path)
    _fixture_card(fixture)
    questions.review_card("privacy", "fixture-card", 5, today=date(2026, 9, 17))
    event = next(questions.iter_events())
    with questions._connect() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO events SELECT sequence + 100, event_id, occurred_at, topic, card_id, action, rating, scheduler_version, effective_date, previous_event_id, result_state, schema_version FROM events"
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """INSERT INTO events(event_id, occurred_at, topic, card_id, action, rating, scheduler_version,
                   effective_date, previous_event_id, result_state, schema_version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("missing-predecessor", event["occurred_at"], "privacy", "fixture-card", "suspended", None,
                 questions.SCHEDULER_VERSION, None, "not-an-event", json.dumps(event["result_state"]), questions.EVENT_SCHEMA),
            )
    assert len(list(questions.iter_events())) == 1
    assert questions.read_cards("privacy")[0].schedule["repetitions"] == 1


def test_interrupted_event_transaction_leaves_no_partial_review(monkeypatch, tmp_path):
    fixture, _ = _configure(monkeypatch, tmp_path)
    _fixture_card(fixture)
    list(questions.iter_events())
    original_set_meta = questions._set_meta

    def fail_after_projection(connection, key, value):
        if key == "projection_sequence":
            raise RuntimeError("simulated interruption")
        original_set_meta(connection, key, value)

    monkeypatch.setattr(questions, "_set_meta", fail_after_projection)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        questions.review_card("privacy", "fixture-card", 5, today=date(2026, 9, 17))
    assert list(questions.iter_events()) == []
    assert questions.read_cards("privacy")[0].schedule == questions.Card().schedule


def test_legacy_state_migrates_to_snapshot_events(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    _fixture_card(fixture)
    user.parent.mkdir(parents=True)
    legacy_state = {"schema": 1, "cards": {"fixture-card": {
        "schedule": {"interval_days": 6, "ease_factor": 2.5, "repetitions": 2, "due_date": "2026-09-23", "last_reviewed": "2026-09-17", "last_quality": 5},
        "suspended": True, "mastered": False,
    }}, "migrated_topics": []}
    questions.CARD_STATE_PATH.write_text(json.dumps(legacy_state), encoding="utf-8")

    card = questions.read_cards("privacy")[0]

    assert card.suspended and card.schedule["interval_days"] == 6
    assert [event["action"] for event in questions.iter_events()] == ["state_snapshot"]
    assert questions.CARD_STATE_PATH.is_file()


def test_legacy_prefix_log_without_state_has_explicit_diagnostic(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    _fixture_card(fixture)
    user.parent.mkdir(parents=True)
    questions.REVIEWS_LOG.write_text('{"card_id":"fixture","quality":5}\n', encoding="utf-8")

    with pytest.raises(questions.LegacyReviewLogError, match="prefix-ID"):
        questions.read_cards("privacy")


def test_private_progress_leaves_a_clean_git_status(tmp_path):
    project = Path(__file__).parent.parent
    shutil.copy(project / ".gitignore", tmp_path / ".gitignore")
    for args in (
        ["git", "init", "-q"],
        ["git", "add", ".gitignore"],
        # -c commit.gpgsign=false: the fixture must commit regardless of the host's
        # global signing config (commit.gpgsign=true + gpg.format=ssh fails headless).
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com",
         "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"],
    ):
        subprocess.run(args, cwd=tmp_path, check=True)
    progress = tmp_path / "library" / "example" / ".user" / "learning-records" / "sr-events.sqlite3"
    progress.parent.mkdir(parents=True)
    progress.write_bytes(b"SQLite format 3\x00")
    result = subprocess.run(["git", "status", "--short"], cwd=tmp_path, capture_output=True, text=True, check=True)
    assert result.stdout == ""
