"""Tests for tools/classify_document.py — document type classification."""

import json
from pathlib import Path

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from classify_document import (
    classify_document,
    signal_heading_progression,
    signal_length_variance,
    signal_forward_references,
    signal_code_density_distribution,
    signal_prerequisite_language,
    signal_first_paragraph_style,
    _find_split_point,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


# --- Integration tests: full classification ---


class TestClassifyDocument:
    def test_tutorial_document(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = classify_document(chunks)
        assert result["type"] == "tutorial"
        assert result["score"] < 0.35
        assert result["confidence"] > 0.5
        assert result["split_point"] is None

    def test_reference_document(self):
        chunks = load_fixture("chunks_reference.json")
        result = classify_document(chunks)
        assert result["type"] == "reference"
        assert result["score"] > 0.65
        assert result["confidence"] > 0.5

    def test_mixed_document(self):
        chunks = load_fixture("chunks_mixed.json")
        result = classify_document(chunks)
        assert result["type"] == "mixed"
        assert result["split_point"] is not None
        # Split should be at the "API Reference" heading (index 5)
        assert result["split_point"] == 5

    def test_ambiguous_document_low_confidence(self):
        chunks = load_fixture("chunks_ambiguous.json")
        result = classify_document(chunks)
        # Short config doc — classifies as reference but with lower confidence
        assert result["type"] == "reference"
        assert result["confidence"] < 0.6

    def test_empty_chunks(self):
        result = classify_document([])
        assert result["type"] == "mixed"
        assert result["confidence"] == 0.0
        assert result["score"] == 0.5

    def test_result_structure(self):
        chunks = load_fixture("chunks_tutorial.json")
        result = classify_document(chunks)
        assert "type" in result
        assert "confidence" in result
        assert "score" in result
        assert "signals" in result
        assert "split_point" in result
        assert result["type"] in ("tutorial", "reference", "mixed")
        assert 0.0 <= result["confidence"] <= 1.0
        assert 0.0 <= result["score"] <= 1.0
        assert len(result["signals"]) == 6


# --- Unit tests: individual signal functions ---


class TestHeadingProgression:
    def test_numbered_chapters_scores_tutorial(self):
        chunks = [
            {"heading": "Chapter 1: Intro", "level": 1},
            {"heading": "Chapter 2: Basics", "level": 1},
            {"heading": "Chapter 3: Advanced", "level": 1},
            {"heading": "Chapter 4: Mastery", "level": 1},
        ]
        score = signal_heading_progression(chunks)
        assert score < 0.3

    def test_alphabetical_headings_scores_reference(self):
        chunks = [
            {"heading": "accept()", "level": 2},
            {"heading": "bind()", "level": 2},
            {"heading": "close()", "level": 2},
            {"heading": "connect()", "level": 2},
            {"heading": "listen()", "level": 2},
        ]
        score = signal_heading_progression(chunks)
        assert score > 0.6

    def test_few_chunks_returns_neutral(self):
        chunks = [{"heading": "A", "level": 1}, {"heading": "B", "level": 1}]
        score = signal_heading_progression(chunks)
        assert score == 0.5


class TestLengthVariance:
    def test_uniform_lengths_scores_reference(self):
        chunks = [{"word_count": 100}, {"word_count": 105}, {"word_count": 98}, {"word_count": 102}]
        score = signal_length_variance(chunks)
        assert score > 0.7

    def test_varied_lengths_scores_tutorial(self):
        chunks = [
            {"word_count": 200},
            {"word_count": 800},
            {"word_count": 1500},
            {"word_count": 450},
            {"word_count": 2000},
        ]
        score = signal_length_variance(chunks)
        assert score < 0.3

    def test_few_chunks_returns_neutral(self):
        chunks = [{"word_count": 100}, {"word_count": 200}]
        score = signal_length_variance(chunks)
        assert score == 0.5


class TestForwardReferences:
    def test_many_references_scores_tutorial(self):
        chunks = [
            {"content": "As we saw in Chapter 1, the basics matter."},
            {"content": "Recall from the previous section that X is true."},
            {"content": "As we'll see in Chapter 5, this becomes important."},
        ]
        score = signal_forward_references(chunks)
        assert score < 0.2

    def test_no_references_scores_reference(self):
        chunks = [
            {"content": "Returns a new socket object."},
            {"content": "Bind the socket to address."},
            {"content": "Mark the socket closed."},
        ]
        score = signal_forward_references(chunks)
        assert score == 1.0

    def test_empty_content(self):
        chunks = [{"content": ""}, {"content": ""}]
        score = signal_forward_references(chunks)
        assert score == 1.0


class TestCodeDensityDistribution:
    def test_increasing_density_scores_tutorial(self):
        chunks = [
            {"has_code": False},
            {"has_code": False},
            {"has_code": False},
            {"has_code": True},
            {"has_code": True},
            {"has_code": True},
            {"has_code": True},
            {"has_code": True},
        ]
        score = signal_code_density_distribution(chunks)
        assert score < 0.3

    def test_uniform_high_density_scores_reference(self):
        chunks = [{"has_code": True}] * 8
        score = signal_code_density_distribution(chunks)
        assert score > 0.6

    def test_few_chunks_returns_neutral(self):
        chunks = [{"has_code": True}, {"has_code": False}, {"has_code": True}]
        score = signal_code_density_distribution(chunks)
        assert score == 0.5


class TestPrerequisiteLanguage:
    def test_prereq_in_early_sections_scores_tutorial(self):
        chunks = [
            {"content": "Before we dive into streaming, let's understand the basics."},
            {"content": "The main concept here is event sourcing."},
            {"content": "As covered in the previous chapter, events are immutable."},
        ]
        score = signal_prerequisite_language(chunks)
        assert score < 0.3

    def test_no_prereq_language_scores_reference(self):
        chunks = [
            {"content": "Returns the remote address to which the socket is connected."},
            {"content": "Bind the socket to the given address."},
            {"content": "Close the socket and free resources."},
        ]
        score = signal_prerequisite_language(chunks)
        assert score > 0.6


class TestFirstParagraphStyle:
    def test_motivational_opening_scores_tutorial(self):
        chunks = [{"content": "In this chapter, we'll build a mental model for stream processing. By the end, you'll understand why batch isn't enough."}]
        score = signal_first_paragraph_style(chunks)
        assert score < 0.3

    def test_definitional_opening_scores_reference(self):
        chunks = [{"content": "The socket module provides access to the BSD socket interface. It is available on all modern Unix systems."}]
        score = signal_first_paragraph_style(chunks)
        assert score > 0.6

    def test_empty_document_returns_neutral(self):
        score = signal_first_paragraph_style([])
        assert score == 0.5


# --- Split point detection ---


class TestFindSplitPoint:
    def test_detects_tutorial_to_reference_transition(self):
        chunks = load_fixture("chunks_mixed.json")
        split = _find_split_point(chunks)
        assert split is not None
        # Should split at "API Reference" (index 5)
        assert split == 5

    def test_no_split_in_uniform_document(self):
        chunks = load_fixture("chunks_reference.json")
        split = _find_split_point(chunks)
        # Uniform short entries — no dramatic length drop
        assert split is None

    def test_no_split_in_short_document(self):
        chunks = load_fixture("chunks_ambiguous.json")
        split = _find_split_point(chunks)
        # Too short (5 chunks, need at least 6)
        assert split is None
