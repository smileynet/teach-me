"""Tests for the source ingest pipeline (chunk_text, fetch_url, ingest_source)."""

import json
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from chunk_text import chunk_markdown, chunk_html, chunk_plaintext
from ingest_source import ingest, _resolve_source


# =============================================================================
# chunk_text tests
# =============================================================================


class TestChunkMarkdown:
    def test_splits_on_headings(self):
        md = "# Chapter 1\n\nIntro text here.\n\n## Section 1.1\n\nMore content here with details."
        chunks = chunk_markdown(md)
        assert len(chunks) == 2
        assert chunks[0]["heading"] == "Chapter 1"
        assert chunks[0]["level"] == 1
        assert chunks[1]["heading"] == "Section 1.1"
        assert chunks[1]["level"] == 2

    def test_preserves_code_blocks(self):
        md = "# Code Example\n\nHere's some code:\n\n```python\ndef hello():\n    # This has a ## in a comment\n    pass\n```\n\nEnd."
        chunks = chunk_markdown(md)
        # Should NOT split on the ## inside the code block
        assert len(chunks) == 1
        assert chunks[0]["has_code"] is True
        assert "def hello" in chunks[0]["content"]

    def test_handles_no_headings(self):
        md = "Just some plain text without any headings.\n\nSecond paragraph."
        chunks = chunk_markdown(md)
        assert len(chunks) == 1
        assert chunks[0]["heading"] == "Introduction"

    def test_output_format_matches_chunk_pdf(self):
        md = "# Test\n\nContent with enough words to be meaningful."
        chunks = chunk_markdown(md)
        chunk = chunks[0]
        assert "heading" in chunk
        assert "level" in chunk
        assert "page_start" in chunk
        assert "content" in chunk
        assert "word_count" in chunk
        assert "has_code" in chunk
        assert "has_table" in chunk

    def test_detects_tables(self):
        md = "# Data\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        chunks = chunk_markdown(md)
        assert chunks[0]["has_table"] is True


class TestChunkHtml:
    def test_splits_on_heading_tags(self):
        html = "<h1>Title</h1><p>Intro content.</p><h2>Section</h2><p>More here.</p>"
        chunks = chunk_html(html)
        assert len(chunks) == 2
        assert chunks[0]["heading"] == "Title"
        assert chunks[0]["level"] == 1
        assert chunks[1]["heading"] == "Section"
        assert chunks[1]["level"] == 2

    def test_strips_nav_and_footer(self):
        html = "<nav>Menu stuff</nav><h1>Real Content</h1><p>Good text.</p><footer>Copyright</footer>"
        chunks = chunk_html(html)
        assert len(chunks) == 1
        assert "Menu" not in chunks[0]["content"]
        assert "Copyright" not in chunks[0]["content"]

    def test_extracts_from_main_tag(self):
        html = "<body><header>Nav</header><main><h1>Article</h1><p>Content here.</p></main><footer>End</footer></body>"
        chunks = chunk_html(html)
        assert len(chunks) == 1
        assert chunks[0]["heading"] == "Article"

    def test_handles_empty_html(self):
        chunks = chunk_html("")
        assert chunks == []


class TestChunkPlaintext:
    def test_splits_on_double_newlines(self):
        text = "First Block\nWith two lines.\n\nSecond Block\nAlso two lines."
        chunks = chunk_plaintext(text)
        assert len(chunks) == 2
        assert chunks[0]["heading"] == "First Block"

    def test_handles_single_block(self):
        text = "Just one paragraph with no double newlines at all."
        chunks = chunk_plaintext(text)
        assert len(chunks) == 1


# =============================================================================
# ingest_source tests
# =============================================================================


class TestResolveSource:
    def test_markdown_file(self):
        tmp = Path(tempfile.mktemp(suffix=".md"))
        tmp.write_text("# Test\n\nContent here.")
        try:
            fmt, content, path = _resolve_source(str(tmp))
            assert fmt == "markdown"
            assert "# Test" in content
        finally:
            tmp.unlink()

    def test_html_file(self):
        tmp = Path(tempfile.mktemp(suffix=".html"))
        tmp.write_text("<html><body><h1>Test</h1><p>Content</p></body></html>")
        try:
            fmt, content, path = _resolve_source(str(tmp))
            assert fmt == "html"
        finally:
            tmp.unlink()

    def test_plain_text_file(self):
        tmp = Path(tempfile.mktemp(suffix=".txt"))
        tmp.write_text("Plain text content without any markup.")
        try:
            fmt, content, path = _resolve_source(str(tmp))
            assert fmt == "text"
        finally:
            tmp.unlink()

    def test_auto_detects_markdown(self):
        tmp = Path(tempfile.mktemp(suffix=".unknown"))
        tmp.write_text("# This is markdown\n\nWith heading syntax.")
        try:
            fmt, content, path = _resolve_source(str(tmp))
            assert fmt == "markdown"
        finally:
            tmp.unlink()


class TestIngestPipeline:
    def test_full_markdown_ingest(self):
        source = Path(tempfile.mktemp(suffix=".md"))
        workspace = Path(tempfile.mkdtemp())
        source.write_text(
            "# Introduction\n\n"
            "This is a substantial introduction with enough words to pass the filter. "
            "We need at least fifty words of content to make it through the noise detection. "
            "So here are more words to fill up the chunk and make it a proper section that "
            "the system will accept as real content worth indexing.\n\n"
            "## First Topic\n\n"
            "More substantial content about the first topic. Again we need enough words "
            "to pass the filter threshold. This section discusses important concepts that "
            "build on the introduction and provide real learning value for the reader.\n\n"
            "## Second Topic\n\n"
            "Content about the second topic that references concepts from the first. "
            "As we discussed in the introduction, these foundations matter. This section "
            "has enough content to be meaningful and to generate proper prereq edges.\n"
        )
        try:
            result = ingest(str(source), workspace, "test-domain", "Test Title")
            assert "error" not in result
            assert result["chunk_count"] >= 2
            assert (workspace / "sources" / "test-domain" / "raw.md").exists()
            assert (workspace / "source-chunks" / "test-domain.json").exists()
            assert (workspace / "maps" / "test-domain.MAP.md").exists()
            assert (workspace / "sources" / "test-domain" / "manifest.json").exists()

            # Check manifest content
            manifest = json.loads(
                (workspace / "sources" / "test-domain" / "manifest.json").read_text()
            )
            assert manifest["format"] == "markdown"
            assert manifest["source_id"] == "test-domain"
            assert manifest["chunk_count"] >= 2
            assert "content_hash" in manifest
        finally:
            source.unlink()
            import shutil
            shutil.rmtree(workspace)

    def test_html_ingest(self):
        source = Path(tempfile.mktemp(suffix=".html"))
        workspace = Path(tempfile.mkdtemp())
        source.write_text(
            "<html><body>"
            "<h1>Main Topic</h1>"
            "<p>Substantial content about the main topic with enough words to satisfy "
            "the minimum word count threshold. This paragraph covers important concepts "
            "that form the foundation for subsequent sections. We discuss multiple ideas "
            "here including architecture patterns, design decisions, and implementation "
            "strategies that build upon each other in a pedagogical progression.</p>"
            "<h2>Sub Topic</h2>"
            "<p>More detailed content that builds on the main topic. This references "
            "concepts introduced above and adds new material for the learner to absorb "
            "in a structured pedagogical progression through the subject matter. Here we "
            "explore specific techniques, code examples, and real-world applications of "
            "the theoretical foundations established in the introduction above.</p>"
            "</body></html>"
        )
        try:
            result = ingest(str(source), workspace, "html-test", "HTML Test")
            assert "error" not in result
            assert result["chunk_count"] >= 1
            manifest = json.loads(
                (workspace / "sources" / "html-test" / "manifest.json").read_text()
            )
            assert manifest["format"] == "html"
        finally:
            source.unlink()
            import shutil
            shutil.rmtree(workspace)

    def test_preserves_raw_source(self):
        source = Path(tempfile.mktemp(suffix=".md"))
        workspace = Path(tempfile.mkdtemp())
        original_content = "# Test\n\nOriginal content that should be preserved exactly."
        source.write_text(original_content)
        try:
            ingest(str(source), workspace, "preserve-test", "Test")
            preserved = (workspace / "sources" / "preserve-test" / "raw.md").read_text()
            assert preserved == original_content
        finally:
            source.unlink()
            import shutil
            shutil.rmtree(workspace)


# =============================================================================
# Regression tests for Codex review findings (#158)
# =============================================================================


class TestF1PathTraversal:
    """Regression: domain with path traversal chars must not escape workspace."""

    def test_domain_sanitized(self):
        from ingest_source import _sanitize_domain
        assert _sanitize_domain("../../escaped") == "escaped"
        assert _sanitize_domain("my-domain") == "my-domain"
        assert _sanitize_domain("a/b/c") == "abc"
        assert _sanitize_domain("valid_slug-123") == "valid_slug-123"

    def test_pure_traversal_raises(self):
        from ingest_source import _sanitize_domain
        with pytest.raises(ValueError):
            _sanitize_domain("../../..")

    def test_traversal_domain_stays_in_workspace(self):
        source = Path(tempfile.mktemp(suffix=".md"))
        workspace = Path(tempfile.mkdtemp())
        source.write_text(
            "# Test\n\nContent with enough words to be meaningful for the pipeline "
            "processing and to pass any minimum word count filters in the system."
        )
        try:
            result = ingest(str(source), workspace, "../../escape-attempt", "Test")
            # Should not error — domain gets sanitized
            if "error" not in result:
                # All created files must be under workspace
                for f in workspace.rglob("*"):
                    assert f.resolve().is_relative_to(workspace.resolve()), (
                        f"File {f} escaped workspace!"
                    )
            # No files should exist outside workspace
            escaped_path = workspace / "sources" / ".." / ".." / "escape-attempt"
            assert not escaped_path.exists()
        finally:
            source.unlink()
            import shutil
            shutil.rmtree(workspace)


class TestF2ExtractedTextFormat:
    """Regression: URL-extracted plain text must not be labeled as HTML."""

    def test_plain_text_detected_as_text(self):
        from fetch_url import _detect_extracted_format
        text = "Introduction\n\nFirst section content about caching.\n\nSecond Section\n\nMore content."
        assert _detect_extracted_format(text) == "text"

    def test_html_tags_detected_as_html(self):
        from fetch_url import _detect_extracted_format
        html = "<h1>Title</h1><p>Content</p><h2>Section</h2>"
        assert _detect_extracted_format(html) == "html"

    def test_markdown_headings_detected_as_markdown(self):
        from fetch_url import _detect_extracted_format
        md = "# Title\n\nContent\n\n## Section Two\n\nMore content"
        assert _detect_extracted_format(md) == "markdown"

    def test_plain_text_chunks_preserve_structure(self):
        """Plain text routed to chunk_plaintext preserves paragraph boundaries."""
        from chunk_text import chunk_plaintext
        text = (
            "Introduction to Topic\n\nFirst paragraph with detail.\n\n"
            "Second Topic\n\nSecond paragraph with more detail.\n\n"
            "Third Topic\n\nThird paragraph."
        )
        chunks = chunk_plaintext(text)
        assert len(chunks) >= 3, f"Expected ≥3 chunks, got {len(chunks)}"


class TestF1EnrichmentPreservesOriginal:
    """Regression for #181 F1: enriching an existing domain with a second source
    must NOT overwrite the preserved original, and the enrichment path must not
    raise NameError (it referenced an undefined `file_path` instead of `raw_path`).
    """

    _CONTENT = (
        "# {title} Introduction\n\n"
        "This is a substantial introduction with enough words to pass the filter. "
        "We need at least fifty words of content to make it through the noise detection. "
        "So here are more words to fill up the chunk and make it a proper section that "
        "the system will accept as real content worth indexing.\n\n"
        "## {title} First Topic\n\n"
        "More substantial content about the first topic. Again we need enough words "
        "to pass the filter threshold. This section discusses important concepts that "
        "build on the introduction and provide real learning value for the reader.\n\n"
        "## {title} Second Topic\n\n"
        "Content about the second topic that references concepts from the first. "
        "As we discussed in the introduction, these foundations matter. This section "
        "has enough content to be meaningful and to generate proper prereq edges.\n"
    )

    def test_second_source_does_not_overwrite_first(self):
        import shutil
        workspace = Path(tempfile.mkdtemp())
        first = Path(tempfile.mktemp(suffix=".md"))
        second = Path(tempfile.mktemp(suffix=".md"))
        first_content = self._CONTENT.format(title="First Source")
        second_content = self._CONTENT.format(title="Second Source")
        first.write_text(first_content)
        second.write_text(second_content)
        try:
            r1 = ingest(str(first), workspace, "enrich-test", "First")
            assert "error" not in r1, r1

            # Second ingest into the SAME domain → enrichment path (_enrich_existing_domain).
            # Pre-fix this raised NameError: name 'file_path' is not defined.
            r2 = ingest(str(second), workspace, "enrich-test", "Second")
            assert "error" not in r2, r2

            src_dir = workspace / "sources" / "enrich-test"
            # Original preserved, unchanged
            assert (src_dir / "raw.md").read_text() == first_content
            # Enrichment source written to a distinct hashed path, not over raw.md
            enrichment_files = list(src_dir.glob("raw-*.md"))
            assert len(enrichment_files) == 1, (
                f"expected one hashed enrichment source, got {enrichment_files}"
            )
            assert enrichment_files[0].read_text() == second_content
        finally:
            first.unlink()
            second.unlink()
            shutil.rmtree(workspace)
