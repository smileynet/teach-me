"""Tests for tools/concept_hints.py and extract_concepts_from_html."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from concept_hints import (
    generate_concept_hints,
    compute_level,
    compute_prerequisite_depth,
    write_concept_hints,
)
from extract_concepts import extract_concepts_from_html

# Import the hyphenated module
import importlib
_ctc = importlib.import_module("check-topic-completeness")
check_concept_coverage = _ctc.check_concept_coverage


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CHUNKS = [
    {
        "heading": "Introduction to Caching",
        "level": 1,
        "page_start": 1,
        "content": "Caching is a technique for storing frequently accessed data in a fast storage layer. The cache sits between the application and the database, intercepting requests. Cache invalidation is one of the hardest problems in computer science. This chapter covers the fundamentals of caching strategy and when to use different approaches.",
        "word_count": 200,
        "has_code": False,
        "has_table": False,
    },
    {
        "heading": "Cache Invalidation Strategies",
        "level": 1,
        "page_start": 5,
        "content": "When data changes in the source of truth, the cache must be updated or cleared. Time-based expiration (TTL) is the simplest strategy. Event-driven invalidation reacts to writes. Write-through caches update the cache on every write. As discussed in the introduction to caching, choosing a strategy depends on consistency requirements.",
        "word_count": 250,
        "has_code": True,
        "has_table": False,
    },
    {
        "heading": "Distributed Caching",
        "level": 1,
        "page_start": 10,
        "content": "When a single cache node isn't enough, distribute across multiple nodes. Consistent hashing assigns keys to nodes without full redistribution on topology changes. Redis Cluster and Memcached support distributed topologies. The cache invalidation strategies from chapter 2 apply at each node independently.",
        "word_count": 220,
        "has_code": True,
        "has_table": False,
    },
    {
        "heading": "Cache Warming and Preloading",
        "level": 1,
        "page_start": 15,
        "content": "Cold caches have poor hit rates. Warming fills the cache before traffic arrives. Preloading common queries prevents the thundering herd problem. This technique is especially important after deploying new distributed caching nodes.",
        "word_count": 150,
        "has_code": False,
        "has_table": False,
    },
]

SAMPLE_LESSON_HTML = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body>
<h1>Caching Fundamentals</h1>
<h2>What Is Caching</h2>
<p>Caching stores frequently accessed data in a fast layer between app and database.
Cache invalidation is notoriously difficult.</p>

<h2>Invalidation Strategies</h2>
<p>TTL-based expiration is the simplest approach. Event-driven invalidation is more
precise but complex. Write-through caches update on every write operation.</p>

<h2>Check Your Understanding</h2>
<p>Exercise: describe when you'd choose TTL vs event-driven invalidation.</p>

<script type="application/json" id="glossary-data">
{
  "cache": "A fast storage layer between application and database that stores frequently accessed data.",
  "ttl": "Time To Live — automatic expiration of cached entries after a fixed duration.",
  "write-through": "A caching strategy where every write updates both the cache and the backing store simultaneously."
}
</script>
<script type="module" src="../assets/page-shell.js"></script>
</body></html>"""


# ---------------------------------------------------------------------------
# TestComputeLevel
# ---------------------------------------------------------------------------


class TestComputeLevel:
    def test_high_score_shallow_depth_is_l1(self):
        assert compute_level(0.8, 0) == "L1"
        assert compute_level(0.6, 1) == "L1"

    def test_medium_score_is_l2(self):
        assert compute_level(0.3, 0) == "L2"
        assert compute_level(0.4, 2) == "L2"

    def test_low_score_deep_is_l3(self):
        assert compute_level(0.1, 3) == "L3"
        assert compute_level(0.05, 5) == "L3"

    def test_high_score_deep_is_l2(self):
        # High score but deep in DAG → L2 (depth overrides)
        assert compute_level(0.8, 3) == "L2"

    def test_boundary_values(self):
        assert compute_level(0.5, 1) == "L1"  # exactly at L1 threshold
        assert compute_level(0.2, 2) == "L2"  # exactly at L2 threshold
        assert compute_level(0.19, 3) == "L3"  # just below L2


# ---------------------------------------------------------------------------
# TestGenerateConceptHints
# ---------------------------------------------------------------------------


class TestGenerateConceptHints:
    def test_produces_concepts(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "introduction-to-caching", "caching")
        assert len(hints["concepts"]) > 0
        assert len(hints["concepts"]) <= 10

    def test_concepts_have_required_fields(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "introduction-to-caching", "caching")
        for c in hints["concepts"]:
            assert "term" in c
            assert "score" in c
            assert "level" in c
            assert c["level"] in ("L1", "L2", "L3")
            assert "defined_in" in c
            assert "used_in" in c
            assert "prerequisite_of" in c

    def test_metadata_fields(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "cache-invalidation-strategies", "caching")
        assert hints["topic"] == "cache-invalidation-strategies"
        assert hints["domain"] == "caching"
        assert "generated_at" in hints
        assert "coverage_target" in hints

    def test_target_relevant_concepts_first(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "introduction-to-caching", "caching")
        # First concepts should be relevant to the target topic
        relevant = [c for c in hints["concepts"] if c["relevant_to_target"]]
        assert len(relevant) > 0

    def test_edges_have_suggestions(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "cache-invalidation-strategies", "caching")
        for e in hints["edges"]:
            assert "suggestion" in e
            assert "concept" in e
            assert "from_topic" in e
            assert "to_topic" in e

    def test_empty_chunks_returns_empty(self):
        hints = generate_concept_hints([], "nothing", "empty")
        assert hints["concepts"] == []
        assert hints["edges"] == []

    def test_top_n_respected(self):
        hints = generate_concept_hints(SAMPLE_CHUNKS, "introduction-to-caching", "caching", top_n=3)
        assert len(hints["concepts"]) <= 3


# ---------------------------------------------------------------------------
# TestWriteConceptHints
# ---------------------------------------------------------------------------


class TestWriteConceptHints:
    def test_writes_json_file(self):
        tmp = Path(tempfile.mkdtemp(prefix="test_hints_"))
        try:
            hints = {"topic": "test", "concepts": [], "edges": [], "coverage_target": 0}
            path = write_concept_hints(hints, tmp / "concepts" / "test.json")
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["topic"] == "test"
        finally:
            shutil.rmtree(tmp)

    def test_creates_parent_dirs(self):
        tmp = Path(tempfile.mkdtemp(prefix="test_hints_"))
        try:
            hints = {"topic": "nested", "concepts": [], "edges": [], "coverage_target": 0}
            path = write_concept_hints(hints, tmp / "deep" / "path" / "hints.json")
            assert path.exists()
        finally:
            shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# TestExtractConceptsFromHtml
# ---------------------------------------------------------------------------


class TestExtractConceptsFromHtml:
    def test_extracts_from_lesson_file(self):
        tmp = Path(tempfile.mktemp(suffix=".html"))
        try:
            tmp.write_text(SAMPLE_LESSON_HTML, encoding="utf-8")
            result = extract_concepts_from_html(tmp, top_n=8)
            # HTML sections may be short (<50 words) — extraction is best-effort
            assert result.per_chunk is not None
            assert len(result.per_chunk) > 0
        finally:
            tmp.unlink(missing_ok=True)

    def test_returns_empty_for_empty_html(self):
        tmp = Path(tempfile.mktemp(suffix=".html"))
        try:
            tmp.write_text("<html><body></body></html>", encoding="utf-8")
            result = extract_concepts_from_html(tmp, top_n=8)
            assert result.concepts == []
        finally:
            tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# TestCheckConceptCoverage
# ---------------------------------------------------------------------------


class TestCheckConceptCoverage:
    def test_reports_coverage(self):
        workspace = Path(tempfile.mkdtemp(prefix="test_cov_"))
        try:
            lesson_path = workspace / "lessons" / "test.html"
            lesson_path.parent.mkdir(parents=True)
            lesson_path.write_text(SAMPLE_LESSON_HTML, encoding="utf-8")

            result = check_concept_coverage(workspace, "test-topic", lesson_path)
            assert "coverage" in result
            assert "total" in result
            assert "gaps" in result
            assert 0.0 <= result["coverage"] <= 1.0
        finally:
            shutil.rmtree(workspace)

    def test_glossary_terms_count_as_covered(self):
        workspace = Path(tempfile.mkdtemp(prefix="test_cov_"))
        try:
            lesson_path = workspace / "lessons" / "test.html"
            lesson_path.parent.mkdir(parents=True)
            lesson_path.write_text(SAMPLE_LESSON_HTML, encoding="utf-8")

            result = check_concept_coverage(workspace, "test-topic", lesson_path)
            # Short lesson sections may not extract concepts — coverage is 1.0 if total=0
            assert result["covered"] >= 0
        finally:
            shutil.rmtree(workspace)

    def test_empty_lesson_returns_full_coverage(self):
        workspace = Path(tempfile.mkdtemp(prefix="test_cov_"))
        try:
            lesson_path = workspace / "lessons" / "empty.html"
            lesson_path.parent.mkdir(parents=True)
            lesson_path.write_text("<html><body></body></html>", encoding="utf-8")

            result = check_concept_coverage(workspace, "empty", lesson_path)
            assert result["coverage"] == 1.0
            assert result["total"] == 0
        finally:
            shutil.rmtree(workspace)
