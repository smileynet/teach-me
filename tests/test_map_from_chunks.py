"""Tests for tools/map_from_chunks.py — MAP.md generation from chunks."""

import json
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from map_from_chunks import generate_map, slugify, is_noise, derive_scope, extract_why
from map_parser import load_map, validate


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


# --- Integration: output parseable by map_parser ---


class TestMapParserCompatibility:
    def _generate_and_parse(self, fixture: str, domain: str = "test", title: str = "Test"):
        chunks = load_fixture(fixture)
        map_md = generate_map(chunks, domain, title)
        assert map_md, "generate_map returned empty string"
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_md)
            return load_map(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_tutorial_parseable(self):
        dm = self._generate_and_parse("chunks_tutorial.json", "streams", "Stream Processing")
        assert dm.domain == "streams"
        assert dm.description == "Stream Processing"
        assert dm.depth == 0
        assert dm.parent is None
        assert len(dm.topics) > 0

    def test_reference_parseable(self):
        dm = self._generate_and_parse("chunks_reference.json", "socket-api", "Socket API")
        assert dm.domain == "socket-api"
        assert len(dm.topics) > 0

    def test_topics_have_required_fields(self):
        dm = self._generate_and_parse("chunks_tutorial.json", "test", "Test")
        for topic in dm.topics:
            assert topic.slug, f"Topic missing slug"
            assert topic.title, f"Topic {topic.slug} missing title"
            assert topic.why, f"Topic {topic.slug} missing why"
            assert topic.scope in ("lightweight", "substantial", "deep")
            assert topic.status == "not-started"

    def test_prereqs_form_linear_chain(self):
        dm = self._generate_and_parse("chunks_tutorial.json", "test", "Test")
        # First topic has no prereqs
        assert dm.topics[0].prereqs == []
        # Each subsequent topic prereqs the previous
        for i in range(1, len(dm.topics)):
            assert dm.topics[i].prereqs == [dm.topics[i - 1].slug]

    def test_frontmatter_has_all_fields(self):
        chunks = load_fixture("chunks_tutorial.json")
        map_md = generate_map(chunks, "test-domain", "Test Title")
        assert "domain: test-domain" in map_md
        assert 'description: "Test Title"' in map_md
        assert "generated:" in map_md
        assert "depth: 0" in map_md
        assert "parent: null" in map_md
        assert "leads_to: []" in map_md

    def test_has_orientation_section(self):
        chunks = load_fixture("chunks_tutorial.json")
        map_md = generate_map(chunks, "test", "Test")
        assert "## Orientation" in map_md

    def test_has_topics_section(self):
        chunks = load_fixture("chunks_tutorial.json")
        map_md = generate_map(chunks, "test", "Test")
        assert "## Topics" in map_md


# --- Noise filtering ---


class TestNoiseFiltering:
    def test_skips_front_matter(self):
        assert is_noise("Table of Contents", 500)
        assert is_noise("Acknowledgments", 300)
        assert is_noise("About the Author", 200)
        assert is_noise("Copyright", 100)

    def test_keeps_real_content(self):
        assert not is_noise("Chapter 1: Introduction", 500)
        assert not is_noise("Getting Started", 200)
        assert not is_noise("Event-Driven Architecture", 800)

    def test_skips_short_chunks(self):
        assert is_noise("Some Heading", 15)

    def test_skips_toc_entries(self):
        assert is_noise("1.2.3.....45", 100)
        assert is_noise("....", 50)

    def test_empty_returns_empty(self):
        map_md = generate_map([], "test", "Test")
        assert map_md == ""


# --- Slugify ---


class TestSlugify:
    def test_strips_chapter_prefix(self):
        assert slugify("Chapter 1: Getting Started") == "getting-started"
        assert slugify("Chapter 12: Advanced Topics") == "advanced-topics"

    def test_strips_section_numbering(self):
        assert slugify("1.1 The Basics") == "the-basics"
        assert slugify("2.2 Producing Messages") == "producing-messages"
        assert slugify("3.1.2 Deep Nested") == "deep-nested"

    def test_strips_part_prefix(self):
        assert slugify("Part 2: Advanced") == "advanced"

    def test_handles_plain_text(self):
        assert slugify("Event-Driven Architecture") == "event-driven-architecture"

    def test_truncates_long_slugs(self):
        long_heading = "A Very Long Chapter Title That Goes On And On And Really Should Be Truncated"
        slug = slugify(long_heading)
        assert len(slug) <= 60


# --- Scope derivation ---


class TestDeriveScope:
    def test_lightweight(self):
        assert derive_scope(200) == "lightweight"
        assert derive_scope(499) == "lightweight"

    def test_substantial(self):
        assert derive_scope(500) == "substantial"
        assert derive_scope(1000) == "substantial"
        assert derive_scope(1500) == "substantial"

    def test_deep(self):
        assert derive_scope(1501) == "deep"
        assert derive_scope(3000) == "deep"


# --- Why extraction ---


class TestExtractWhy:
    def test_extracts_first_sentence(self):
        content = "Streams are unbounded datasets. They have no defined end. This matters for design."
        why = extract_why(content)
        assert why == "Streams are unbounded datasets."

    def test_skips_short_sentences(self):
        content = "Hi. Streams are unbounded, continuously updating datasets that flow forever."
        why = extract_why(content)
        assert "Streams" in why

    def test_truncates_long_sentences(self):
        content = "A " * 200 + "end of sentence."
        why = extract_why(content, max_length=50)
        assert len(why) <= 55  # 50 + "..." + partial word
        assert why.endswith("...")

    def test_fallback_for_empty(self):
        assert extract_why("") == "Core concepts and techniques"
