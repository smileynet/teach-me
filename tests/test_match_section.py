"""Tests for tools/match_section.py — section query matching."""

import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from match_section import match_sections

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


class TestMatchSections:
    def test_chapter_number(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "chapter 3")
        assert len(matches) >= 1
        assert "3" in matches[0]["heading"]

    def test_section_number(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "2.1")
        assert len(matches) >= 1
        assert "2.1" in matches[0]["heading"]

    def test_keyword_match(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "kafka")
        assert len(matches) >= 1
        assert "kafka" in matches[0]["heading"].lower()

    def test_partial_word_match(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "event")
        assert len(matches) >= 1
        assert "event" in matches[0]["heading"].lower()

    def test_no_match_returns_empty(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "quantum physics")
        assert matches == []

    def test_empty_query_returns_empty(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "")
        assert matches == []

    def test_empty_chunks_returns_empty(self):
        matches = match_sections([], "chapter 1")
        assert matches == []

    def test_results_sorted_by_relevance(self):
        chunks = load_fixture("chunks_tutorial.json")
        matches = match_sections(chunks, "chapter 3")
        # Chapter 3 (level 1) should come before 3.1 (level 2)
        if len(matches) >= 2:
            assert matches[0]["level"] <= matches[1]["level"]

    def test_case_insensitive(self):
        chunks = load_fixture("chunks_tutorial.json")
        upper = match_sections(chunks, "KAFKA")
        lower = match_sections(chunks, "kafka")
        assert len(upper) == len(lower)
