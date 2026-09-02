"""Tests for estimate-read-time.py — calibration + helpers.

The module filename has a hyphen, so load it by path (as check-lesson.py does).
"""

import importlib.util
from pathlib import Path

import pytest

_RT_PATH = Path(__file__).resolve().parent.parent / "tools" / "estimate-read-time.py"
_spec = importlib.util.spec_from_file_location("estimate_read_time", _RT_PATH)
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)

_LIB = Path(__file__).resolve().parent.parent / "library"
_CAL_01 = _LIB / "ink-godot" / "lessons" / "0001-ink-flow-and-knots.html"
_CAL_02 = _LIB / "ink-godot" / "lessons" / "0002-ink-choices-and-weave.html"


class TestCalibration:
    """The #215 AC: lesson 01 -> ~8 min, lesson 02 -> ~12 min, each within +/-2."""

    @pytest.mark.skipif(not _CAL_01.exists(), reason="calibration lesson 01 absent")
    def test_lesson_01_about_8_min(self):
        est = rt.estimate_read_time(_CAL_01.read_text(encoding="utf-8"))
        assert abs(est - 8) <= 2, f"lesson 01 estimated {est} min, expected ~8"

    @pytest.mark.skipif(not _CAL_02.exists(), reason="calibration lesson 02 absent")
    def test_lesson_02_about_12_min(self):
        est = rt.estimate_read_time(_CAL_02.read_text(encoding="utf-8"))
        assert abs(est - 12) <= 2, f"lesson 02 estimated {est} min, expected ~12"


class TestFormula:
    def test_prose_only_uses_wpm(self):
        # 400 words at 200 WPM = 2.0 min, no code -> ceil(2.0) = 2
        html = "<p>" + " ".join(["word"] * 400) + "</p>"
        assert rt.estimate_read_time(html) == 2

    def test_code_lines_add_penalty(self):
        # 200 words = 1.0 min prose; 40 non-blank code lines * 1.5s = 60s = 1.0 min
        # total 2.0 -> ceil = 2
        code = "\n".join([f"line {i}" for i in range(40)])
        html = "<p>" + " ".join(["w"] * 200) + f"</p><pre>{code}</pre>"
        assert rt.estimate_read_time(html) == 2

    def test_blank_code_lines_ignored(self):
        # Blank lines inside <pre> cost nothing; only 2 real lines here.
        html = "<p>" + " ".join(["w"] * 200) + "</p><pre>a\n\n\n\nb</pre>"
        # 200/200 = 1.0 min + 2*1.5/60 = 0.05 -> ceil(1.05) = 2
        assert rt.estimate_read_time(html) == 2

    def test_skips_script_and_svg(self):
        html = (
            "<p>" + " ".join(["w"] * 200) + "</p>"
            "<script>" + " ".join(["junk"] * 5000) + "</script>"
            "<svg>" + " ".join(["label"] * 500) + "</svg>"
        )
        # Only the 200 prose words count -> 1 min
        assert rt.estimate_read_time(html) == 1

    def test_minimum_one_minute(self):
        assert rt.estimate_read_time("<p>short</p>") == 1


class TestHelpers:
    def test_declared_read_time_parses(self):
        assert rt.declared_read_time("... · ~12 min read<br>") == 12
        assert rt.declared_read_time("~8 min read") == 8

    def test_declared_read_time_absent(self):
        assert rt.declared_read_time("<p>no meta here</p>") is None

    def test_update_read_time_rewrites(self):
        html = "Lesson 2 · Ink + Godot · ~99 min read<br>"
        new_html, changed = rt.update_read_time(html, 12)
        assert changed
        assert "~12 min read" in new_html
        assert "~99" not in new_html

    def test_update_read_time_noop_when_absent(self):
        html = "<p>no declared time</p>"
        new_html, changed = rt.update_read_time(html, 12)
        assert not changed
        assert new_html == html
