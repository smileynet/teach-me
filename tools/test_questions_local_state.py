"""SR mutations must never rewrite committed question fixtures."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import questions

_SPEC = importlib.util.spec_from_file_location("sr_lifecycle", Path(__file__).with_name("sr-lifecycle.py"))
assert _SPEC and _SPEC.loader
sr_lifecycle = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sr_lifecycle)


def _configure(monkeypatch, root: Path) -> tuple[Path, Path]:
    fixture = root / "learning-records" / "questions"
    user = root / ".user" / "learning-records" / "questions"
    monkeypatch.setattr(questions, "FIXTURE_QUESTIONS_DIR", fixture)
    monkeypatch.setattr(questions, "USER_QUESTIONS_DIR", user)
    monkeypatch.setattr(questions, "REVIEWS_LOG", user.parent / "reviews.jsonl")
    monkeypatch.setattr(questions, "CARD_STATE_PATH", user.parent / "card-state.json")
    return fixture, user


def test_review_writes_only_fixture_card_state(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    card = questions.Card(id="fixture-card", prompt="Explain the boundary.")
    fixture.mkdir(parents=True)
    source = fixture / "privacy.jsonl"
    source.write_text(card.to_json() + "\n", encoding="utf-8")

    updated = questions.review_card("privacy", "fixture-card", 5, today=date(2026, 9, 17))

    assert updated is not None
    assert source.read_text(encoding="utf-8") == card.to_json() + "\n"
    assert not (user / "privacy.jsonl").exists()
    state = questions.CARD_STATE_PATH.read_text(encoding="utf-8")
    assert '"fixture-card"' in state and "Explain the boundary." not in state
    assert questions.REVIEWS_LOG.is_file()


def test_append_and_lifecycle_rewrite_stay_private(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    fixture.mkdir(parents=True)
    fixture_card = questions.Card(id="fixture-card", prompt="Fixture card")
    source = fixture / "privacy.jsonl"
    source.write_text(fixture_card.to_json() + "\n", encoding="utf-8")

    questions.append_card("new-topic", questions.Card(id="private-card", prompt="Private card"))
    sr_lifecycle._rewrite_topic("privacy", questions.read_cards("privacy"))

    assert source.read_text(encoding="utf-8") == fixture_card.to_json() + "\n"
    assert (user / "new-topic.jsonl").is_file()
    assert not (user / "privacy.jsonl").exists()
    assert '"schedule"' not in (user / "new-topic.jsonl").read_text(encoding="utf-8")
    assert "Fixture card" not in questions.CARD_STATE_PATH.read_text(encoding="utf-8")


def test_legacy_private_card_copy_migrates_without_hiding_fixture(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    fixture.mkdir(parents=True)
    card = questions.Card(id="fixture-card", prompt="Public definition")
    (fixture / "privacy.jsonl").write_text(card.to_json() + "\n", encoding="utf-8")
    user.mkdir(parents=True)
    legacy = questions.Card(id="fixture-card", prompt="Public definition")
    legacy.suspended = True
    (user / "privacy.jsonl").write_text(legacy.to_json() + "\n", encoding="utf-8")

    cards = questions.read_cards("privacy")

    assert [(item.id, item.prompt, item.suspended) for item in cards] == [("fixture-card", "Public definition", True)]
    assert not (user / "privacy.jsonl").exists()
    assert "Public definition" not in questions.CARD_STATE_PATH.read_text(encoding="utf-8")


def test_empty_local_state_keeps_every_public_definition_visible(monkeypatch, tmp_path):
    fixture, user = _configure(monkeypatch, tmp_path)
    fixture.mkdir(parents=True)
    card = questions.Card(id="fixture-card", prompt="Public definition")
    (fixture / "privacy.jsonl").write_text(card.definition_json() + "\n", encoding="utf-8")
    user.parent.mkdir(parents=True)
    questions.CARD_STATE_PATH.write_text('{"schema": 1, "cards": {}, "migrated_topics": []}\n', encoding="utf-8")

    cards = questions.read_cards("privacy")

    assert [(item.id, item.prompt) for item in cards] == [("fixture-card", "Public definition")]


def test_private_progress_leaves_a_clean_git_status(tmp_path):
    project = Path(__file__).parent.parent
    shutil.copy(project / ".gitignore", tmp_path / ".gitignore")
    for args in (
        ["git", "init", "-q"],
        ["git", "add", ".gitignore"],
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-qm", "fixture"],
    ):
        subprocess.run(args, cwd=tmp_path, check=True)

    progress = tmp_path / "library" / "example" / ".user" / "learning-records" / "reviews.jsonl"
    progress.parent.mkdir(parents=True)
    progress.write_text("{}\n", encoding="utf-8")

    result = subprocess.run(["git", "status", "--short"], cwd=tmp_path, capture_output=True, text=True, check=True)
    assert result.stdout == ""
