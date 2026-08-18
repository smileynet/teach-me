#!/usr/bin/env python3
"""classify_document.py — Classify a document as tutorial or reference style.

Analyzes structural signals from chunk_pdf.py output to determine whether
a document is tutorial-style (pedagogically ordered — trust the sequence)
or reference-style (lookup-ordered — reorganize for learning).

Usage:
    python tools/classify_document.py chunks.json
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path


# --- Signal functions ---
# Each returns a float 0.0–1.0 where 0 = tutorial, 1 = reference.


def signal_heading_progression(chunks: list[dict]) -> float:
    """Detect sequential/narrative headings (tutorial) vs alphabetical/flat (reference)."""
    headings = [c["heading"] for c in chunks]
    if len(headings) < 3:
        return 0.5

    # Check for numbered chapter pattern: "Chapter 1", "1.", "1.1", etc.
    numbered = sum(
        1 for h in headings
        if re.match(r"^(chapter\s+\d|part\s+\d|\d+[\.\):]|\d+\.\d+)", h, re.IGNORECASE)
    )
    numbered_ratio = numbered / len(headings)

    # Check for alphabetical ordering (reference signal)
    # Strip common prefixes/numbers and check if remaining text is alphabetical
    stripped = [re.sub(r"^[\d\.\s\-:()]+", "", h).lower().strip() for h in headings]
    stripped = [s for s in stripped if s]
    if len(stripped) >= 4:
        sorted_version = sorted(stripped)
        # Measure how close to alphabetical the headings are
        matches = sum(1 for a, b in zip(stripped, sorted_version) if a == b)
        alpha_ratio = matches / len(stripped)
    else:
        alpha_ratio = 0.0

    # Strong numbered progression → tutorial
    if numbered_ratio > 0.4:
        return max(0.0, 0.2 - numbered_ratio * 0.3)

    # Strong alphabetical → reference
    if alpha_ratio > 0.7:
        return min(1.0, 0.5 + alpha_ratio * 0.5)

    # Same heading level throughout (flat) leans reference
    levels = [c["level"] for c in chunks]
    if len(set(levels)) == 1:
        return 0.7

    return 0.5


def signal_length_variance(chunks: list[dict]) -> float:
    """High variance in section lengths → tutorial; uniform → reference."""
    word_counts = [c["word_count"] for c in chunks]
    if len(word_counts) < 3:
        return 0.5

    mean_wc = statistics.mean(word_counts)
    if mean_wc == 0:
        return 0.5

    # Coefficient of variation (normalized std dev)
    cv = statistics.stdev(word_counts) / mean_wc

    # cv > 0.6 → high variance (tutorial), cv < 0.2 → uniform (reference)
    if cv > 0.6:
        return 0.1
    if cv < 0.2:
        return 0.9
    # Linear interpolation between 0.2 and 0.6
    return 0.9 - (cv - 0.2) * (0.8 / 0.4)


def signal_forward_references(chunks: list[dict]) -> float:
    """Detect backward/forward references between sections (tutorial signal)."""
    patterns = [
        r"as we (?:saw|covered|discussed|learned|built)",
        r"in (?:the )?(?:previous|last|earlier) (?:chapter|section)",
        r"(?:from|in) chapter \d",
        r"recall (?:from|that)",
        r"as (?:we'll|we will) see",
        r"we'll cover .+ in chapter",
        r"building on .+ from",
        r"as (?:mentioned|described|explained) (?:in|earlier|above|before)",
    ]
    combined = re.compile("|".join(patterns), re.IGNORECASE)

    total_refs = 0
    for chunk in chunks:
        total_refs += len(combined.findall(chunk.get("content", "")))

    # Normalize: 0 refs per chunk → reference, 0.3+ per chunk → tutorial
    refs_per_chunk = total_refs / max(len(chunks), 1)
    if refs_per_chunk >= 0.3:
        return 0.0
    if refs_per_chunk == 0:
        return 1.0
    return 1.0 - (refs_per_chunk / 0.3)


def signal_code_density_distribution(chunks: list[dict]) -> float:
    """Increasing code density through doc → tutorial; uniform → reference."""
    if len(chunks) < 4:
        return 0.5

    code_flags = [1 if c["has_code"] else 0 for c in chunks]

    # Split into first half and second half
    mid = len(code_flags) // 2
    first_half = code_flags[:mid]
    second_half = code_flags[mid:]

    first_density = sum(first_half) / len(first_half)
    second_density = sum(second_half) / len(second_half)

    # If code is uniform throughout → reference signal
    if abs(first_density - second_density) < 0.1:
        # Check if it's uniformly high (all have code) — strong reference signal
        overall = sum(code_flags) / len(code_flags)
        if overall > 0.8:
            return 0.8
        return 0.6

    # Increasing density → tutorial signal
    if second_density > first_density:
        diff = second_density - first_density
        return max(0.0, 0.5 - diff * 1.5)

    # Decreasing density is unusual — slight reference lean
    return 0.6


def signal_prerequisite_language(chunks: list[dict]) -> float:
    """Detect prerequisite/setup language (tutorial signal)."""
    patterns = [
        r"before (?:reading|proceeding|you begin|we (?:start|begin|dive))",
        r"(?:assumes?|requires?) (?:familiarity|knowledge|understanding)",
        r"make sure you(?:'re| are) (?:comfortable|familiar)",
        r"you(?:'ll| will) need (?:to (?:know|understand|have))",
        r"we assume",
        r"prerequisite",
    ]
    combined = re.compile("|".join(patterns), re.IGNORECASE)

    # Check first third of document (where prereqs typically appear)
    first_third = chunks[: max(len(chunks) // 3, 2)]
    found = any(combined.search(c.get("content", "")) for c in first_third)

    # Also check later chunks for "as covered in" style prereqs
    later = chunks[len(chunks) // 3 :]
    later_refs = any(
        re.search(r"as (?:covered|discussed|explained) in", c.get("content", ""), re.IGNORECASE)
        for c in later
    )

    if found and later_refs:
        return 0.0
    if found or later_refs:
        return 0.2
    return 0.8


def signal_first_paragraph_style(chunks: list[dict]) -> float:
    """Motivational/contextual opening → tutorial; definitional → reference."""
    if not chunks:
        return 0.5

    first_content = chunks[0].get("content", "")
    first_sentence = first_content.split(".")[0].lower() if first_content else ""

    # Motivational patterns (tutorial)
    motivational = [
        r"(?:let's|we'll|we will|let us)",
        r"in this (?:chapter|book|guide)",
        r"before we (?:dive|start|begin)",
        r"by the end",
        r"you(?:'ll| will) (?:learn|understand|know|be able)",
        r"imagine",
        r"why (?:does|do|is|are|should)",
    ]

    # Definitional patterns (reference)
    definitional = [
        r"^(?:the |a |an )?[\w\s]+ (?:is|are) (?:a|an|the|used)",
        r"^this (?:document|page|section|module) (?:describes|covers|lists|provides)",
        r"(?:provides|contains|documents) (?:a |the )?(?:reference|list|overview|access|interface)",
        r"^(?:the |a |an )?[\w\s]+ (?:provides|exposes|implements|defines|contains)",
        r"^(?:returns?|accepts?|creates?) ",
    ]

    motivational_re = re.compile("|".join(motivational), re.IGNORECASE)
    definitional_re = re.compile("|".join(definitional), re.IGNORECASE)

    has_motivational = bool(motivational_re.search(first_content[:500]))
    has_definitional = bool(definitional_re.search(first_content[:500]))

    if has_motivational and not has_definitional:
        return 0.1
    if has_definitional and not has_motivational:
        return 0.9
    return 0.5


# --- Scoring ---

SIGNAL_WEIGHTS = {
    "heading_progression": 0.25,
    "length_variance": 0.20,
    "forward_references": 0.20,
    "code_density_distribution": 0.15,
    "prerequisite_language": 0.10,
    "first_paragraph_style": 0.10,
}

SIGNAL_FUNCTIONS = {
    "heading_progression": signal_heading_progression,
    "length_variance": signal_length_variance,
    "forward_references": signal_forward_references,
    "code_density_distribution": signal_code_density_distribution,
    "prerequisite_language": signal_prerequisite_language,
    "first_paragraph_style": signal_first_paragraph_style,
}


def classify_document(chunks: list[dict]) -> dict:
    """Classify a document as tutorial, reference, or mixed.

    Args:
        chunks: List of chunk dicts from chunk_pdf.py output.
                Each has: heading, level, page_start, content, word_count, has_code, has_table.

    Returns:
        {
            "type": "tutorial" | "reference" | "mixed",
            "confidence": 0.0-1.0,
            "score": 0.0-1.0 (0=tutorial, 1=reference),
            "signals": {signal_name: score, ...},
            "split_point": int | None  # chunk index where style changes (for mixed)
        }
    """
    if not chunks:
        return {"type": "mixed", "confidence": 0.0, "score": 0.5, "signals": {}, "split_point": None}

    signals = {}
    for name, fn in SIGNAL_FUNCTIONS.items():
        signals[name] = fn(chunks)

    # Weighted sum
    score = sum(signals[name] * SIGNAL_WEIGHTS[name] for name in SIGNAL_WEIGHTS)

    # Check for a structural split before final classification
    split_point = _find_split_point(chunks)

    # Classification thresholds
    if score < 0.35:
        doc_type = "tutorial"
        confidence = 1.0 - (score / 0.35)  # 0.0 → 1.0, 0.35 → 0.0
    elif score > 0.65:
        doc_type = "reference"
        confidence = (score - 0.65) / 0.35  # 0.65 → 0.0, 1.0 → 1.0
    else:
        doc_type = "mixed"
        # Confidence for mixed = how far from the boundaries
        distance_from_center = abs(score - 0.5)
        confidence = 1.0 - (distance_from_center / 0.15)  # peaks at 0.5, drops at edges

    # Override: if a clear split point exists, reclassify as mixed
    if split_point is not None and doc_type != "mixed":
        doc_type = "mixed"
        confidence = 0.7  # moderate confidence — we found a structural boundary

    return {
        "type": doc_type,
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "score": round(score, 3),
        "signals": {k: round(v, 3) for k, v in signals.items()},
        "split_point": split_point,
    }


def _find_split_point(chunks: list[dict]) -> int | None:
    """Find the chunk index where a document transitions from tutorial to reference style.

    Uses a sliding window to detect where section lengths drop sharply and
    heading patterns shift from narrative to flat/alphabetical.
    """
    if len(chunks) < 6:
        return None

    word_counts = [c["word_count"] for c in chunks]
    mean_wc = statistics.mean(word_counts)

    best_split = None
    best_score = 0.0

    # Try each possible split point (at least 3 chunks on each side)
    for i in range(3, len(chunks) - 2):
        first_half_wc = word_counts[:i]
        second_half_wc = word_counts[i:]

        first_mean = statistics.mean(first_half_wc)
        second_mean = statistics.mean(second_half_wc)

        # Length drop signals transition from prose to entries
        if first_mean > 0:
            length_ratio = second_mean / first_mean
            if length_ratio < 0.4:  # second half is <40% the length of first
                score = 1.0 - length_ratio
                if score > best_score:
                    best_score = score
                    best_split = i

    return best_split


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python tools/classify_document.py <chunks.json>")
        print("\nClassifies a document as tutorial-style or reference-style")
        print("based on structural signals from chunk_pdf.py output.")
        sys.exit(0)

    path = Path(args[0])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    chunks = json.loads(path.read_text())
    result = classify_document(chunks)

    print(f"Type:       {result['type']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Score:      {result['score']:.3f} (0=tutorial, 1=reference)")
    print()
    print("Signals:")
    for name, value in result["signals"].items():
        direction = "← tutorial" if value < 0.4 else "→ reference" if value > 0.6 else "  neutral"
        print(f"  {name:<30} {value:.3f} {direction}")

    if result["split_point"] is not None:
        print(f"\nSplit point: chunk {result['split_point']} "
              f"(\"{chunks[result['split_point']]['heading']}\")")


if __name__ == "__main__":
    main()
