#!/usr/bin/env python3
"""backfill-criteria.py — Normalize question criteria to numbered-point format.

Mechanically reformats criteria that are missing (1)...(2)... structure.
Does NOT rewrite content — just restructures existing text into the standard format.

Handles:
- Criteria with "Should mention:" prefix but no numbers → add (1), (2), etc.
- Criteria that are comma/semicolon separated points → split and number
- Criteria with bullet-style markers (-, •) → number them
- Short single-sentence criteria → wrap as (1) with no change

Usage:
    python tools/backfill-criteria.py --workspace workspace --dry-run
    python tools/backfill-criteria.py --workspace workspace
    python tools/backfill-criteria.py --workspace examples/iceberg-workspace
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from questions import questions_dir_for


def needs_reformat(criteria: str) -> bool:
    """Check if criteria needs reformatting (missing numbered points)."""
    if not criteria or len(criteria) < 30:
        return False
    # Already has numbered format
    if "(1)" in criteria and "(2)" in criteria:
        return False
    return True


def reformat_criteria(criteria: str) -> str:
    """Reformat criteria into (1)...(2)... standard format."""
    text = criteria.strip()

    # Remove "Should mention:" prefix if present (we'll re-add it)
    prefix_match = re.match(r'^(Should (?:mention|name|include|cover|address)[^:]*:\s*)', text, re.IGNORECASE)
    prefix = "Should mention: "
    if prefix_match:
        prefix = prefix_match.group(1)
        text = text[prefix_match.end():].strip()

    # Try to split on common separators
    points = []

    # Pattern 1: bullet points (-, •, *)
    if re.search(r'^[\-•\*]\s', text, re.MULTILINE):
        points = [p.strip().lstrip('-•* ').strip() for p in re.split(r'\n[\-•\*]\s', '\n' + text) if p.strip()]

    # Pattern 2: semicolons as separators
    elif text.count(';') >= 1:
        points = [p.strip() for p in text.split(';') if p.strip()]

    # Pattern 3: numbered without parens (1. 2. 3.)
    elif re.search(r'\d+\.\s', text):
        points = [p.strip() for p in re.split(r'\d+\.\s+', text) if p.strip()]

    # Pattern 4: commas with substantial segments (>20 chars each on average)
    elif text.count(',') >= 2:
        segments = [s.strip() for s in text.split(',') if s.strip()]
        avg_len = sum(len(s) for s in segments) / len(segments) if segments else 0
        if avg_len > 15:
            points = segments

    # Pattern 5: "and" / "also" as separators in longer text
    elif len(text) > 100:
        # Try splitting on sentence boundaries
        sentences = [s.strip() for s in re.split(r'(?<=[.!])\s+', text) if s.strip() and len(s.strip()) > 10]
        if len(sentences) >= 2:
            points = sentences

    # Fallback: keep as single point
    if not points:
        points = [text]

    # Extract bonus if last segment mentions "bonus" or "key insight"
    bonus = None
    if len(points) > 1:
        last = points[-1].lower()
        if last.startswith('bonus') or 'key insight' in last or last.startswith('the key'):
            bonus = points.pop()
            # Clean up bonus prefix
            bonus = re.sub(r'^[Bb]onus:?\s*', '', bonus).strip()
            bonus = re.sub(r'^[Kk]ey [Ii]nsight:?\s*', '', bonus).strip()

    # Rebuild with numbered format
    numbered = " ".join(f"({i+1}) {p.rstrip('.,')}" for i, p in enumerate(points))
    result = prefix + numbered

    if bonus:
        result += f". Bonus: {bonus}"

    # Clean up trailing punctuation
    result = result.rstrip('.') + '.'
    return result


def process_file(path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Process a JSONL file. Returns (total, reformatted) counts."""
    lines = path.read_text(encoding="utf-8").strip().split('\n')
    reformatted = 0
    new_lines = []

    for line in lines:
        if not line.strip():
            new_lines.append(line)
            continue
        try:
            q = json.loads(line)
        except json.JSONDecodeError:
            new_lines.append(line)
            continue

        # Skip interactive questions (no criteria field)
        if q.get('type') in ('sequence', 'match', 'fill'):
            new_lines.append(line)
            continue

        criteria = q.get('criteria', q.get('expected_answer', ''))
        if needs_reformat(criteria):
            new_criteria = reformat_criteria(criteria)
            if 'criteria' in q:
                q['criteria'] = new_criteria
            elif 'expected_answer' in q:
                q['expected_answer'] = new_criteria
            reformatted += 1
            new_lines.append(json.dumps(q, ensure_ascii=False))
        else:
            new_lines.append(line)

    if not dry_run and reformatted > 0:
        path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')

    return len([l for l in lines if l.strip()]), reformatted


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args

    workspace = Path("workspace")
    if "--workspace" in args:
        idx = args.index("--workspace")
        if idx + 1 < len(args):
            workspace = Path(args[idx + 1])

    questions_dir = questions_dir_for(workspace)
    if not questions_dir.exists():
        print(f"No questions directory at {questions_dir}")
        return

    total_questions = 0
    total_reformatted = 0

    for f in sorted(questions_dir.glob("*.jsonl")):
        count, reformatted = process_file(f, dry_run)
        total_questions += count
        total_reformatted += reformatted
        if reformatted > 0:
            action = "[dry-run]" if dry_run else "✓"
            print(f"  {action} {f.name}: {reformatted}/{count} reformatted")

    action = "Would reformat" if dry_run else "Reformatted"
    print(f"\n{action} {total_reformatted}/{total_questions} questions in {workspace}")


if __name__ == "__main__":
    main()
