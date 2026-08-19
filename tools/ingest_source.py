#!/usr/bin/env python3
"""ingest_source.py — Ingest a source document into the learning workspace.

Single command that: detects format, preserves raw source, chunks, classifies,
generates MAP.md, and enriches prereqs.

Usage:
    python tools/ingest_source.py path/to/document.pdf --workspace workspace/ --domain "my-domain" --title "My Book"
    python tools/ingest_source.py https://example.com/docs --workspace workspace/ --domain "example" --title "Example Docs"
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chunk_text import chunk_markdown, chunk_html, chunk_plaintext
from classify_document import classify_document
from enrich_prereqs import enrich_prereqs
from map_from_chunks import generate_map
from map_from_deps import generate_dependency_ordered_map


def ingest(
    source: str,
    workspace: Path,
    domain: str,
    title: str,
) -> dict:
    """Ingest a source document into the workspace.

    Args:
        source: File path or URL to ingest
        workspace: Workspace root directory
        domain: Domain slug for the generated MAP
        title: Human-readable title

    Returns:
        Summary dict with paths to generated artifacts.
    """
    # 1. Detect format and get content
    fmt, raw_content, raw_path = _resolve_source(source)

    # 2. Preserve raw source
    source_dir = workspace / "sources" / domain
    source_dir.mkdir(parents=True, exist_ok=True)
    preserved_path = _preserve_source(raw_path, raw_content, source_dir, fmt)

    # 3. Chunk
    chunks = _chunk_content(raw_content, raw_path, fmt)
    if not chunks:
        return {"error": "No chunks extracted from source"}

    # 4. Save chunks
    chunks_dir = workspace / "source-chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = chunks_dir / f"{domain}.json"
    chunks_path.write_text(json.dumps(chunks, indent=2, ensure_ascii=False))

    # 5. Classify
    classification = classify_document(chunks)

    # 6. Generate MAP
    maps_dir = workspace / "maps"
    maps_dir.mkdir(parents=True, exist_ok=True)
    map_path = maps_dir / f"{domain}.MAP.md"

    if classification["type"] == "reference":
        map_md = generate_dependency_ordered_map(chunks, domain, title)
    elif classification["type"] == "mixed" and classification.get("split_point"):
        # Use tutorial portion only
        split = classification["split_point"]
        map_md = generate_map(chunks[:split], domain, title)
    else:
        map_md = generate_map(chunks, domain, title)

    if not map_md:
        return {"error": "MAP generation produced empty output"}

    map_path.write_text(map_md)

    # 7. Enrich prereqs
    enrich_result = enrich_prereqs(map_path, chunks)

    # 8. Write manifest
    content_hash = hashlib.sha256(
        raw_content.encode() if isinstance(raw_content, str) else raw_content
    ).hexdigest()

    manifest = {
        "source_id": domain,
        "original_source": source,
        "format": fmt,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": f"sha256:{content_hash[:16]}",
        "word_count": sum(c["word_count"] for c in chunks),
        "chunk_count": len(chunks),
        "classification": classification["type"],
        "classification_confidence": classification["confidence"],
        "map_generated": str(map_path.relative_to(workspace)),
        "chunks_file": str(chunks_path.relative_to(workspace)),
    }
    manifest_path = source_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return {
        "source_preserved": str(preserved_path),
        "chunks_file": str(chunks_path),
        "chunk_count": len(chunks),
        "classification": classification["type"],
        "confidence": classification["confidence"],
        "map_file": str(map_path),
        "manifest": str(manifest_path),
        "enrichment": {
            "topics_enriched": enrich_result["enriched"],
            "entry_points": enrich_result["entry_points"],
        },
    }


def _resolve_source(source: str) -> tuple[str, str, Path | None]:
    """Resolve source to (format, content, optional_file_path).

    Returns: (format, raw_content_text, file_path_or_None)
    """
    # URL
    if source.startswith("http://") or source.startswith("https://"):
        from fetch_url import fetch_url_content
        text, fmt = fetch_url_content(source)
        if fmt == "pdf":
            # text is actually a temp file path
            return "pdf", Path(text).read_bytes().decode("latin-1"), Path(text)
        return fmt, text, None

    # Local file
    path = Path(source)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        return "pdf", path.read_bytes().decode("latin-1"), path
    elif suffix in (".md", ".markdown"):
        return "markdown", content, path
    elif suffix in (".html", ".htm"):
        return "html", content, path
    elif suffix in (".txt", ".rst", ".org"):
        return "text", content, path
    else:
        # Guess from content
        if content.strip().startswith("<!") or "<html" in content[:200].lower():
            return "html", content, path
        if re.search(r"^#{1,3}\s", content, re.MULTILINE):
            return "markdown", content, path
        return "text", content, path


def _preserve_source(
    file_path: Path | None, content: str, dest_dir: Path, fmt: str
) -> Path:
    """Copy raw source to preservation directory."""
    ext_map = {"pdf": ".pdf", "markdown": ".md", "html": ".html", "text": ".txt"}
    ext = ext_map.get(fmt, ".txt")

    if file_path and file_path.exists():
        dest = dest_dir / f"raw{file_path.suffix}"
        shutil.copy2(file_path, dest)
    else:
        dest = dest_dir / f"raw{ext}"
        dest.write_text(content, encoding="utf-8")

    return dest


def _chunk_content(content: str, file_path: Path | None, fmt: str) -> list[dict]:
    """Route to appropriate chunker based on format."""
    if fmt == "pdf" and file_path:
        from chunk_pdf import chunk_pdf
        from dataclasses import asdict
        raw_chunks = chunk_pdf(file_path)
        return [
            {
                "heading": c.heading,
                "level": c.level,
                "page_start": c.page_start,
                "content": c.content,
                "word_count": c.word_count,
                "has_code": c.has_code,
                "has_table": c.has_table,
            }
            for c in raw_chunks
        ]
    elif fmt == "markdown":
        return chunk_markdown(content)
    elif fmt == "html":
        return chunk_html(content)
    else:
        return chunk_plaintext(content)


# Need re for _resolve_source
import re


# --- CLI ---

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/ingest_source.py <source> --workspace PATH --domain SLUG --title TITLE")
        print("\nIngests a document (PDF, Markdown, HTML, URL) into the learning workspace.")
        print("Produces: preserved source, chunks, classified MAP.md with enriched prereqs.")
        print("\nExamples:")
        print("  python tools/ingest_source.py book.pdf --workspace workspace/ --domain my-book --title 'My Book'")
        print("  python tools/ingest_source.py https://docs.example.com --workspace workspace/ --domain example --title 'Example'")
        sys.exit(0)

    source = args[0]
    workspace = Path("workspace")
    domain = "untitled"
    title = "Untitled"

    if "--workspace" in args:
        workspace = Path(args[args.index("--workspace") + 1])
    if "--domain" in args:
        domain = args[args.index("--domain") + 1]
    if "--title" in args:
        title = args[args.index("--title") + 1]

    print(f"Ingesting: {source}")
    print(f"Workspace: {workspace}")
    print(f"Domain:    {domain}")
    print()

    result = ingest(source, workspace, domain, title)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print("✓ Ingest complete:")
    print(f"  Source preserved: {result['source_preserved']}")
    print(f"  Chunks:           {result['chunk_count']} ({result['chunks_file']})")
    print(f"  Classification:   {result['classification']} ({result['confidence']:.0%})")
    print(f"  MAP generated:    {result['map_file']}")
    print(f"  Enrichment:       {result['enrichment']['topics_enriched']} topics enriched, "
          f"{result['enrichment']['entry_points']} entry points")
    print(f"  Manifest:         {result['manifest']}")


if __name__ == "__main__":
    main()
