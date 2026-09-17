"""Learner-dialog skills must keep personal state out of shared curriculum paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_learner_dialog_skills_name_private_state_paths():
    for skill in ("teach", "quiz-me"):
        text = (ROOT / ".kiro" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert ".user/learner-profile.md" in text
        assert ".user/learning-records/" in text


def test_quiz_outcome_instructions_never_target_committed_paths():
    text = (ROOT / ".kiro" / "skills" / "quiz-me" / "SKILL.md").read_text(encoding="utf-8")
    assert "write a learning record" not in text
    assert "note it in `NOTES.md`" not in text
    assert "Never write learner results to `NOTES.md` or committed `learning-records/`" in text


def test_teach_scaffolds_private_profile_with_python_initializer():
    text = (ROOT / ".kiro" / "skills" / "teach" / "SKILL.md").read_text(encoding="utf-8")
    assert "python tools/init_workspace.py --default" in text
    assert "Write the mission to `.user/learner-profile.md`" in text


def test_teach_reference_formats_keep_personal_state_private():
    skill = ROOT / ".kiro" / "skills" / "teach"
    record_format = (skill / "LEARNING-RECORD-FORMAT.md").read_text(encoding="utf-8")
    mission_format = (skill / "MISSION-FORMAT.md").read_text(encoding="utf-8")
    resources_format = (skill / "RESOURCES-FORMAT.md").read_text(encoding="utf-8")
    assert "./.user/learning-records/" in record_format
    assert ".user/learner-profile.md" in mission_format
    assert ".user/learner-profile.md" in resources_format


def test_active_skills_do_not_point_personal_context_at_root_mission():
    jargon = (ROOT / ".kiro" / "skills" / "jargon" / "SKILL.md").read_text(encoding="utf-8")
    assert ".user/learner-profile.md" in jargon
