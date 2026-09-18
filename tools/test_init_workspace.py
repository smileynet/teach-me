"""init_workspace scaffolds the learner profile the teach skill reads (#375).

The teach skill's state convention (#361) reads `.user/learner-profile.md`; the
scaffolder must create it on fresh workspaces AND backfill it on existing ones
(migrating a real legacy mission out of MISSION.md, which the skill no longer
reads) — otherwise a pre-#361 workspace presents as first-contact forever.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from init_workspace import _DEFAULT_MISSION, init_workspace  # noqa: E402


def test_fresh_scaffold_creates_learner_profile(tmp_path):
    ws = tmp_path / "ws"
    result = init_workspace(ws, default=True)

    profile = ws / ".user" / "learner-profile.md"
    assert result["status"] == "created"
    assert profile.is_file()
    text = profile.read_text(encoding="utf-8")
    assert "## Mission" in text
    assert "Not set yet." in text  # placeholder — a fresh workspace IS first-contact
    assert str(profile) in result["created"]


def test_existing_workspace_gets_profile_backfill_with_migrated_mission(tmp_path):
    ws = tmp_path / "legacy"
    (ws / "lessons").mkdir(parents=True)
    original_mission = "# Legacy Mission\n\nPass the AWS SA exam by December.\n"
    (ws / "MISSION.md").write_text(original_mission, encoding="utf-8")
    original_bytes = (ws / "MISSION.md").read_bytes()

    result = init_workspace(ws)

    profile = ws / ".user" / "learner-profile.md"
    assert result["status"] == "exists"
    assert profile.is_file()
    text = profile.read_text(encoding="utf-8")
    assert "Pass the AWS SA exam by December." in text
    assert "(migrated from MISSION.md)" in text
    assert (ws / "MISSION.md").read_bytes() == original_bytes  # untouched, for audit
    assert any("migrated" in w for w in result["warnings"])


def test_backfill_is_idempotent_and_never_overwrites(tmp_path):
    ws = tmp_path / "legacy2"
    (ws / "lessons").mkdir(parents=True)
    (ws / "MISSION.md").write_text("# Real\n\nLearn Godot properly.", encoding="utf-8")
    init_workspace(ws)
    profile = ws / ".user" / "learner-profile.md"
    profile.write_text(
        profile.read_text(encoding="utf-8") + "\nlearner edits must survive\n",
        encoding="utf-8",
    )

    result = init_workspace(ws)

    assert "learner edits must survive" in profile.read_text(encoding="utf-8")
    assert result["created"] == []


def test_template_mission_is_not_migrated(tmp_path):
    ws = tmp_path / "tmpl"
    (ws / "lessons").mkdir(parents=True)
    (ws / "MISSION.md").write_text(_DEFAULT_MISSION, encoding="utf-8")

    init_workspace(ws)

    text = (ws / ".user" / "learner-profile.md").read_text(encoding="utf-8")
    assert "Not set yet." in text
    assert "migrated" not in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
