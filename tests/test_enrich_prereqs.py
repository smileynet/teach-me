"""Tests for tools/enrich_prereqs.py — prerequisite edge enrichment."""

import json
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from enrich_prereqs import enrich_prereqs, AUTO_COMMENT, _extract_prereqs_from_line


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text())


def _make_map(topics: list[dict], domain: str = "test") -> str:
    """Generate a minimal MAP.md string for testing."""
    lines = [
        "---",
        f"domain: {domain}",
        f'description: "Test"',
        "generated: 2026-08-18",
        "depth: 0",
        "parent: null",
        "leads_to: []",
        "---",
        "",
        "# Test",
        "",
        "## Topics",
        "",
    ]
    for t in topics:
        prereqs = t.get("prereqs", "[]")
        lines.append(f"### {t['slug']}")
        lines.append(f"- **title:** {t.get('title', t['slug'])}")
        lines.append(f"- **why:** Test")
        lines.append(f"- **scope:** substantial")
        lines.append(f"- **prereqs:** {prereqs}")
        lines.append(f"- **status:** not-started")
        lines.append("")
    return "\n".join(lines)


class TestEnrichPrereqs:
    def test_enriches_empty_prereqs(self):
        """Topics with prereqs: [] get enriched with detected edges."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept"},
            {"slug": "bindaddress"},
            {"slug": "close"},
            {"slug": "connectaddress"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            result = enrich_prereqs(tmp, chunks, dry_run=True)
            # At least some topics should get prereqs
            assert result["enriched"] > 0 or result["entry_points"] > 0
            assert result["preserved"] == 0
        finally:
            tmp.unlink(missing_ok=True)

    def test_accept_is_entry_point(self):
        """accept() defines 'socket' — should have no prereqs (entry point)."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept"},
            {"slug": "bindaddress"},
            {"slug": "connectaddress"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            result = enrich_prereqs(tmp, chunks, dry_run=True)
            accept_change = next(c for c in result["changes"] if c["slug"] == "accept")
            assert accept_change["new_prereqs"] == []
        finally:
            tmp.unlink(missing_ok=True)

    def test_preserves_manual_prereqs(self):
        """Topics with non-empty prereqs (no auto comment) are not overwritten."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept", "prereqs": "[manual-dep]"},
            {"slug": "bindaddress", "prereqs": "[]"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            result = enrich_prereqs(tmp, chunks, dry_run=True)
            assert result["preserved"] == 1  # accept preserved
            # accept should NOT appear in changes with new prereqs
            accept_changes = [c for c in result["changes"] if c["slug"] == "accept"]
            assert len(accept_changes) == 0
        finally:
            tmp.unlink(missing_ok=True)

    def test_overwrites_auto_prereqs(self):
        """Topics with auto comment get re-enriched on subsequent runs."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept", "prereqs": f"[]  {AUTO_COMMENT}"},
            {"slug": "bindaddress", "prereqs": f"[old-dep]  {AUTO_COMMENT}"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            result = enrich_prereqs(tmp, chunks, dry_run=True)
            # Both should be overwritten (auto comment present)
            assert result["preserved"] == 0
            assert len(result["changes"]) == 2
        finally:
            tmp.unlink(missing_ok=True)

    def test_idempotent(self):
        """Running enrichment twice produces the same output."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept"},
            {"slug": "bindaddress"},
            {"slug": "connectaddress"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            # First run
            enrich_prereqs(tmp, chunks, dry_run=False)
            text_after_first = tmp.read_text()
            # Second run
            enrich_prereqs(tmp, chunks, dry_run=False)
            text_after_second = tmp.read_text()
            assert text_after_first == text_after_second
        finally:
            tmp.unlink(missing_ok=True)

    def test_output_parseable(self):
        """Enriched MAP.md is still parseable by map_parser."""
        from map_parser import load_map
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept"},
            {"slug": "bindaddress"},
            {"slug": "connectaddress"},
            {"slug": "senddata"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            enrich_prereqs(tmp, chunks, dry_run=False)
            dm = load_map(tmp)
            assert dm.domain == "test"
            assert len(dm.topics) == 4
        finally:
            tmp.unlink(missing_ok=True)

    def test_hard_prereqs_from_high_weight(self):
        """Edges with weight ≥ 0.7 become hard prereqs."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([
            {"slug": "accept"},
            {"slug": "bindaddress"},
            {"slug": "senddata"},
        ])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            result = enrich_prereqs(tmp, chunks, dry_run=True)
            # senddata should have hard prereqs (accept has weight 0.8 to most)
            send_change = next(
                (c for c in result["changes"] if c["slug"] == "senddata"), None
            )
            if send_change:
                assert len(send_change["new_prereqs"]) > 0
        finally:
            tmp.unlink(missing_ok=True)

    def test_dry_run_does_not_write(self):
        """--dry-run should not modify the file."""
        chunks = load_fixture("chunks_reference.json")
        map_text = _make_map([{"slug": "accept"}, {"slug": "bindaddress"}])
        tmp = Path(tempfile.mktemp(suffix=".MAP.md"))
        try:
            tmp.write_text(map_text)
            original = tmp.read_text()
            enrich_prereqs(tmp, chunks, dry_run=True)
            assert tmp.read_text() == original
        finally:
            tmp.unlink(missing_ok=True)


class TestHelpers:
    def test_extract_prereqs_empty(self):
        assert _extract_prereqs_from_line("- **prereqs:** []") == []

    def test_extract_prereqs_one(self):
        assert _extract_prereqs_from_line("- **prereqs:** [accept]") == ["accept"]

    def test_extract_prereqs_multiple(self):
        assert _extract_prereqs_from_line("- **prereqs:** [a, b, c]") == ["a", "b", "c"]

    def test_extract_prereqs_with_comment(self):
        line = f"- **prereqs:** [accept]  {AUTO_COMMENT}"
        assert _extract_prereqs_from_line(line) == ["accept"]
