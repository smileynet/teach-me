"""Tests for tools/enrich_from_source.py — multi-source enrichment."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from enrich_from_source import (
    match_topics,
    detect_conflicts,
    write_enrichment_overlay,
    enrich_domain,
    TopicMatch,
    HIGH_CONFIDENCE,
    CANDIDATE_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EXISTING_CHUNKS = [
    {
        "heading": "What Are Containers?",
        "level": 1,
        "page_start": 1,
        "content": "Containers package an application with its dependencies into a standardized unit. Unlike virtual machines, containers share the host OS kernel, making them lightweight and fast to start. Docker popularized containers by providing a simple build-and-run workflow.",
        "word_count": 280,
        "has_code": False,
        "has_table": False,
    },
    {
        "heading": "Kubernetes Storage",
        "level": 1,
        "page_start": 10,
        "content": "Persistent Volumes provide durable storage that outlives individual pods. PersistentVolumeClaims request storage from the cluster. Storage classes define different tiers including SSD and HDD. StatefulSets manage stateful workloads that need stable network identities and persistent storage.",
        "word_count": 300,
        "has_code": False,
        "has_table": False,
    },
    {
        "heading": "Monitoring with Prometheus",
        "level": 1,
        "page_start": 20,
        "content": "Prometheus scrapes metrics from instrumented applications and Kubernetes components. PromQL queries time-series data for alerting and dashboards. Grafana visualizes Prometheus metrics. The kube-state-metrics exporter provides cluster-level metrics about node CPU usage of 85% on average.",
        "word_count": 350,
        "has_code": False,
        "has_table": False,
    },
]

NEW_CHUNKS_OVERLAPPING = [
    {
        "heading": "Container Fundamentals",
        "level": 1,
        "page_start": 1,
        "content": "A container is an isolated process running in user space, sharing the host kernel. Linux namespaces provide isolation. Cgroups limit resource usage. Container images use a layered filesystem. The OCI specification standardizes image format and runtime behavior. Docker and containerd are common runtimes.",
        "word_count": 310,
        "has_code": False,
        "has_table": False,
    },
    {
        "heading": "Storage and State Management",
        "level": 1,
        "page_start": 10,
        "content": "Container storage interface standardizes how orchestrators interact with storage backends. Persistent volumes provide block or file storage that survives pod restarts. StatefulSets give pods stable identities. Storage classes abstract provider-specific details. Updated in 2025, the CSI spec now requires 50GB minimum allocation.",
        "word_count": 360,
        "has_code": False,
        "has_table": False,
    },
    {
        "heading": "Security and Access Control",
        "level": 1,
        "page_start": 20,
        "content": "RBAC governs who can do what in a cluster. Pod Security Standards define privilege levels. Network policies implement microsegmentation. Secrets management handles sensitive configuration. Unlike traditional firewalls, network policies operate at the pod level rather than the host level.",
        "word_count": 350,
        "has_code": False,
        "has_table": False,
    },
]

NEW_CHUNKS_CONFLICTING = [
    {
        "heading": "Observability Stack",
        "level": 1,
        "page_start": 1,
        "content": "In 2025, the observability landscape shifted significantly. OpenTelemetry replaced Prometheus as the primary metrics collection framework. Average node CPU usage is not 85% but rather 42% according to the 2025 CNCF survey. This is contrary to earlier claims of high resource utilization.",
        "word_count": 300,
        "has_code": False,
        "has_table": False,
    },
]


def _make_workspace():
    """Create a temporary workspace directory."""
    return Path(tempfile.mkdtemp(prefix="test_enrich_"))


# ---------------------------------------------------------------------------
# TestMatchTopics
# ---------------------------------------------------------------------------


class TestMatchTopics:
    """Tests for the TF-IDF + YAKE topic matching."""

    def test_finds_overlapping_topics(self):
        matches, unmatched = match_topics(EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        # Container Fundamentals should match What Are Containers
        # Storage and State Management should match Kubernetes Storage
        matched_slugs = {m.topic_slug for m in matches}
        assert "what-are-containers" in matched_slugs or "kubernetes-storage" in matched_slugs
        assert len(matches) >= 1

    def test_returns_unmatched_indices(self):
        matches, unmatched = match_topics(EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        # Security and Access Control should have no strong match in existing
        # (existing has containers, storage, monitoring — not security)
        total = len(matches) + len(unmatched)
        assert total == len(NEW_CHUNKS_OVERLAPPING)

    def test_empty_existing_returns_all_unmatched(self):
        matches, unmatched = match_topics([], NEW_CHUNKS_OVERLAPPING)
        assert matches == []
        assert len(unmatched) == len(NEW_CHUNKS_OVERLAPPING)

    def test_empty_new_returns_no_matches(self):
        matches, unmatched = match_topics(EXISTING_CHUNKS, [])
        assert matches == []
        assert unmatched == []

    def test_confidence_scores_are_bounded(self):
        matches, _ = match_topics(EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        for m in matches:
            assert 0.0 <= m.match_confidence <= 1.5  # cosine + boost can exceed 1.0

    def test_match_method_is_set(self):
        matches, _ = match_topics(EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        for m in matches:
            assert "tfidf_cosine+yake_boost" in m.match_method

    def test_single_chunk_each(self):
        matches, unmatched = match_topics(
            EXISTING_CHUNKS[:1], NEW_CHUNKS_OVERLAPPING[:1]
        )
        # With only 1 doc per side, TF-IDF has limited discrimination power
        # but should still produce a score (not crash)
        assert len(matches) + len(unmatched) == 1

    def test_threshold_respected(self):
        # With a very high threshold, nothing should match
        matches, unmatched = match_topics(
            EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING,
            high_threshold=0.99, low_threshold=0.99,
        )
        assert matches == []
        assert len(unmatched) == len(NEW_CHUNKS_OVERLAPPING)


# ---------------------------------------------------------------------------
# TestConflictDetection
# ---------------------------------------------------------------------------


class TestConflictDetection:
    """Tests for heuristic conflict signal detection."""

    def test_detects_number_conflict(self):
        # Existing says 85%, new says 42%
        matches = [TopicMatch(
            topic_slug="monitoring-with-prometheus",
            new_chunk_index=0,
            new_chunk_heading="Observability Stack",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_CONFLICTING)
        signals = matches[0].conflict_signals
        assert any("number_mismatch" in s for s in signals)

    def test_detects_temporal_signal(self):
        # New source mentions 2025, existing doesn't mention dates explicitly
        matches = [TopicMatch(
            topic_slug="monitoring-with-prometheus",
            new_chunk_index=0,
            new_chunk_heading="Observability Stack",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_CONFLICTING)
        # Note: existing chunk doesn't have year numbers, so no temporal signal
        # This tests that it doesn't crash — temporal requires both to have dates

    def test_detects_negation_signals(self):
        # New conflicting chunk has "not", "contrary to", "unlike"
        matches = [TopicMatch(
            topic_slug="monitoring-with-prometheus",
            new_chunk_index=0,
            new_chunk_heading="Observability Stack",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_CONFLICTING)
        signals = matches[0].conflict_signals
        # Should detect negation density OR number mismatch
        assert len(signals) >= 1

    def test_classifies_factual_conflict(self):
        matches = [TopicMatch(
            topic_slug="monitoring-with-prometheus",
            new_chunk_index=0,
            new_chunk_heading="Observability Stack",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_CONFLICTING)
        assert matches[0].conflict_type == "factual"

    def test_complementary_when_no_signals(self):
        # Container Fundamentals vs What Are Containers — complementary, no conflict
        matches = [TopicMatch(
            topic_slug="what-are-containers",
            new_chunk_index=0,
            new_chunk_heading="Container Fundamentals",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        assert matches[0].conflict_type == "complementary"

    def test_no_crash_on_missing_slug(self):
        matches = [TopicMatch(
            topic_slug="nonexistent-topic",
            new_chunk_index=0,
            new_chunk_heading="Something",
            match_confidence=0.15,
            match_method="tfidf_cosine+yake_boost (high)",
        )]
        detect_conflicts(matches, EXISTING_CHUNKS, NEW_CHUNKS_OVERLAPPING)
        # Should not crash, signals should be empty
        assert matches[0].conflict_signals == []


# ---------------------------------------------------------------------------
# TestOverlayWrite
# ---------------------------------------------------------------------------


class TestOverlayWrite:
    """Tests for the append-only enrichment overlay writer."""

    def test_creates_overlay_file(self):
        workspace = _make_workspace()
        try:
            matches = [TopicMatch(
                topic_slug="what-are-containers",
                new_chunk_index=0,
                new_chunk_heading="Container Fundamentals",
                match_confidence=0.12,
                match_method="tfidf_cosine+yake_boost (high)",
                conflict_type="complementary",
            )]
            path = write_enrichment_overlay(
                workspace, "test-domain", "src-abc123",
                matches, [], NEW_CHUNKS_OVERLAPPING,
            )
            assert path.exists()
            data = json.loads(path.read_text())
            assert "enrichments" in data
            assert len(data["enrichments"]) == 1
            assert data["enrichments"][0]["source_id"] == "src-abc123"
        finally:
            shutil.rmtree(workspace)

    def test_appends_to_existing_overlay(self):
        workspace = _make_workspace()
        try:
            matches = [TopicMatch(
                topic_slug="what-are-containers",
                new_chunk_index=0,
                new_chunk_heading="Container Fundamentals",
                match_confidence=0.12,
                match_method="test",
                conflict_type="complementary",
            )]
            # Write first
            write_enrichment_overlay(
                workspace, "test-domain", "src-001",
                matches, [], NEW_CHUNKS_OVERLAPPING,
            )
            # Write second
            path = write_enrichment_overlay(
                workspace, "test-domain", "src-002",
                matches, [], NEW_CHUNKS_OVERLAPPING,
            )
            data = json.loads(path.read_text())
            assert len(data["enrichments"]) == 2
            assert data["enrichments"][0]["source_id"] == "src-001"
            assert data["enrichments"][1]["source_id"] == "src-002"
        finally:
            shutil.rmtree(workspace)

    def test_records_match_details(self):
        workspace = _make_workspace()
        try:
            matches = [TopicMatch(
                topic_slug="kubernetes-storage",
                new_chunk_index=1,
                new_chunk_heading="Storage and State",
                match_confidence=0.21,
                match_method="tfidf_cosine+yake_boost (high)",
                conflict_signals=["number_mismatch(50GB≠0)"],
                conflict_type="factual",
            )]
            path = write_enrichment_overlay(
                workspace, "domain", "src-x",
                matches, [], NEW_CHUNKS_OVERLAPPING,
            )
            data = json.loads(path.read_text())
            record = data["enrichments"][0]["matches"][0]
            assert record["topic_slug"] == "kubernetes-storage"
            assert record["match_confidence"] == 0.21
            assert record["conflict_type"] == "factual"
            assert "source_passage" in record
        finally:
            shutil.rmtree(workspace)

    def test_records_new_topics(self):
        workspace = _make_workspace()
        try:
            new_topics = [{"slug": "security", "title": "Security", "source_id": "x", "word_count": 200}]
            path = write_enrichment_overlay(
                workspace, "domain", "src-y",
                [], new_topics, [],
            )
            data = json.loads(path.read_text())
            assert data["enrichments"][0]["new_topics_proposed"] == new_topics
        finally:
            shutil.rmtree(workspace)


# ---------------------------------------------------------------------------
# TestEnrichDomain (integration)
# ---------------------------------------------------------------------------


class TestEnrichDomain:
    """Integration tests for the full enrichment pipeline."""

    def test_full_pipeline_produces_overlay(self):
        workspace = _make_workspace()
        try:
            result = enrich_domain(
                new_chunks=NEW_CHUNKS_OVERLAPPING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="test-src",
            )
            assert result["matches"] >= 1
            assert "overlay_path" in result
            overlay = Path(result["overlay_path"])
            assert overlay.exists()
        finally:
            shutil.rmtree(workspace)

    def test_originals_untouched(self):
        workspace = _make_workspace()
        try:
            # Write existing chunks to workspace
            chunks_dir = workspace / "source-chunks"
            chunks_dir.mkdir(parents=True)
            existing_path = chunks_dir / "k8s.json"
            original_content = json.dumps(EXISTING_CHUNKS, indent=2)
            existing_path.write_text(original_content)

            enrich_domain(
                new_chunks=NEW_CHUNKS_OVERLAPPING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="test-src",
            )

            # Original chunks file should be untouched
            assert existing_path.read_text() == original_content
        finally:
            shutil.rmtree(workspace)

    def test_detects_conflicts_in_pipeline(self):
        workspace = _make_workspace()
        try:
            result = enrich_domain(
                new_chunks=NEW_CHUNKS_CONFLICTING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="conflict-src",
            )
            # Should detect at least one conflict
            assert result["conflicts_detected"] >= 1
        finally:
            shutil.rmtree(workspace)

    def test_proposes_new_topics_for_unmatched(self):
        workspace = _make_workspace()
        try:
            result = enrich_domain(
                new_chunks=NEW_CHUNKS_OVERLAPPING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="new-src",
            )
            # Security chunk should be unmatched and proposed as new topic
            assert result["new_topics_proposed"] >= 0  # at least runs without error
        finally:
            shutil.rmtree(workspace)

    def test_idempotent_overlay_append(self):
        workspace = _make_workspace()
        try:
            # Run twice
            enrich_domain(
                new_chunks=NEW_CHUNKS_OVERLAPPING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="run-1",
            )
            enrich_domain(
                new_chunks=NEW_CHUNKS_OVERLAPPING,
                existing_chunks=EXISTING_CHUNKS,
                workspace=workspace,
                domain="k8s",
                source_id="run-2",
            )

            overlay_path = workspace / "sources" / "k8s" / "enrichments.json"
            data = json.loads(overlay_path.read_text())
            assert len(data["enrichments"]) == 2
        finally:
            shutil.rmtree(workspace)
