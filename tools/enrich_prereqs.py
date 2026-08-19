#!/usr/bin/env python3
"""enrich_prereqs.py — Enrich MAP.md prereqs with evidence-based edges.

Takes an existing MAP.md and its source chunks, runs concept extraction,
and replaces default linear prereqs with detected dependency edges.

Safe to re-run: only overwrites auto-generated prereqs, never manual edits.

Usage:
    python tools/enrich_prereqs.py maps/domain.MAP.md --chunks chunks.json [--dry-run]
"""

from __future__ import annotations

import re
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_concepts import extract_concepts
from map_from_chunks import slugify

# Confidence thresholds (research-backed: Sato et al. 2017)
HARD_THRESHOLD = 0.7   # Directly and substantially covered → hard prereq
SOFT_THRESHOLD = 0.4   # Tangentially related → soft prereq (forward-reference)

AUTO_COMMENT = "<!-- auto: enrich_prereqs -->"


def enrich_prereqs(
    map_path: Path,
    chunks: list[dict],
    dry_run: bool = False,
) -> dict:
    """Enrich a MAP.md's prereqs with evidence-based edges from concept extraction.

    Returns a summary dict: {enriched, entry_points, preserved, changes: [{slug, old, new}]}
    """
    map_text = map_path.read_text()

    # Run concept extraction
    result = extract_concepts(chunks, top_n=8)

    # Build slug → chunk index mapping
    chunk_slugs: dict[str, int] = {}
    for i, chunk in enumerate(chunks):
        slug = slugify(chunk["heading"])
        if slug:
            chunk_slugs[slug] = i

    # Build index → slug reverse mapping
    index_to_slug: dict[int, str] = {v: k for k, v in chunk_slugs.items()}

    # Compute prereqs per topic from the concept graph
    detected_prereqs: dict[str, list[str]] = {}  # slug → [hard prereq slugs]
    detected_soft: dict[str, list[str]] = {}     # slug → [soft prereq slugs]

    for slug, chunk_idx in chunk_slugs.items():
        if chunk_idx not in result.graph:
            continue

        hard = []
        soft = []
        for pred in result.graph.predecessors(chunk_idx):
            weight = result.graph[pred][chunk_idx].get("weight", 0.5)
            pred_slug = index_to_slug.get(pred)
            if not pred_slug:
                continue
            if weight >= HARD_THRESHOLD:
                hard.append(pred_slug)
            elif weight >= SOFT_THRESHOLD:
                soft.append(pred_slug)

        detected_prereqs[slug] = hard
        detected_soft[slug] = soft

    # Parse and rewrite MAP.md
    changes = []
    enriched = 0
    entry_points = 0
    preserved = 0

    lines = map_text.split("\n")
    new_lines = []
    current_slug = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect topic heading
        if line.startswith("### "):
            current_slug = line[4:].strip()

        # Detect prereqs line
        if current_slug and line.startswith("- **prereqs:**"):
            is_auto = AUTO_COMMENT in line or (
                i + 1 < len(lines) and AUTO_COMMENT in lines[i + 1]
            )
            is_empty = "[]" in line

            if is_empty or is_auto:
                # Safe to overwrite: empty or previously auto-generated
                hard = detected_prereqs.get(current_slug, [])
                soft = detected_soft.get(current_slug, [])

                if hard:
                    prereq_str = f"[{', '.join(hard)}]"
                    new_line = f"- **prereqs:** {prereq_str}  {AUTO_COMMENT}"
                    enriched += 1
                else:
                    new_line = f"- **prereqs:** []  {AUTO_COMMENT}"
                    entry_points += 1

                changes.append({
                    "slug": current_slug,
                    "old_prereqs": _extract_prereqs_from_line(line),
                    "new_prereqs": hard,
                    "soft_prereqs": soft,
                })
                new_lines.append(new_line)

                # Add soft_prereqs line if any
                # First, skip existing soft_prereqs line if present
                if i + 1 < len(lines) and lines[i + 1].startswith("- **soft_prereqs:**"):
                    i += 1  # skip old soft line

                if soft:
                    soft_str = f"[{', '.join(soft)}]"
                    new_lines.append(f"- **soft_prereqs:** {soft_str}  {AUTO_COMMENT}")

                # Skip auto comment on next line if it exists separately
                if i + 1 < len(lines) and lines[i + 1].strip() == AUTO_COMMENT:
                    i += 1

                i += 1
                continue
            else:
                # Manual prereqs — preserve
                preserved += 1
                new_lines.append(line)
                i += 1
                continue

        new_lines.append(line)
        i += 1

    new_text = "\n".join(new_lines)

    if not dry_run:
        map_path.write_text(new_text)

    return {
        "enriched": enriched,
        "entry_points": entry_points,
        "preserved": preserved,
        "changes": changes,
        "new_text": new_text,
    }


def _extract_prereqs_from_line(line: str) -> list[str]:
    """Extract prereq slugs from a prereqs line."""
    match = re.search(r"\[([^\]]*)\]", line)
    if not match:
        return []
    inner = match.group(1).strip()
    if not inner:
        return []
    return [s.strip() for s in inner.split(",")]


# --- CLI ---


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/enrich_prereqs.py <MAP.md> --chunks <chunks.json> [--dry-run]")
        print("\nEnriches MAP.md prereqs with evidence-based edges from concept extraction.")
        print("Safe to re-run: never overwrites manual edits.")
        sys.exit(0)

    map_path = Path(args[0])
    if not map_path.exists():
        print(f"Error: MAP.md not found: {map_path}", file=sys.stderr)
        sys.exit(1)

    chunks_path = None
    dry_run = "--dry-run" in args

    if "--chunks" in args:
        idx = args.index("--chunks")
        chunks_path = Path(args[idx + 1])

    if not chunks_path or not chunks_path.exists():
        print(f"Error: chunks file not found: {chunks_path}", file=sys.stderr)
        sys.exit(1)

    chunks = json.loads(chunks_path.read_text())
    result = enrich_prereqs(map_path, chunks, dry_run=dry_run)

    # Report
    mode = "[DRY RUN] " if dry_run else ""
    print(f"{mode}Enrichment complete:")
    print(f"  Topics enriched:  {result['enriched']}")
    print(f"  Entry points:     {result['entry_points']} (no detected prereqs)")
    print(f"  Preserved:        {result['preserved']} (manual, untouched)")
    print()

    if result["changes"]:
        print("Changes:")
        for c in result["changes"]:
            old = c["old_prereqs"] or ["(empty)"]
            new = c["new_prereqs"] or ["(entry point)"]
            soft = c["soft_prereqs"]
            print(f"  {c['slug']}:")
            print(f"    prereqs: {old} → {new}")
            if soft:
                print(f"    soft_prereqs: {soft}")


if __name__ == "__main__":
    main()
