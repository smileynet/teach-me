#!/usr/bin/env python3
"""
Generate a standalone quiz page from JSONL question files.

Reads questions for a specific lesson_id, produces an HTML page with:
- Navigation: ← Back to lesson, ← Back to map
- Questions: prompt + reveal answer, one card per question
- Self-rating buttons

Usage:
    python tools/generate-quiz-page.py --lesson-id 0001-iceberg-metadata-tree \
        --title "Iceberg Metadata Tree" \
        --lesson-file 0001-iceberg-metadata-tree.html \
        --map-page modern-data-analytics-stacks-map.html \
        [--output lessons/quiz/0001-iceberg-metadata-tree-quiz.html]
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = PROJECT_ROOT / "learning-records" / "questions"
OUTPUT_DIR = PROJECT_ROOT / "lessons" / "quiz"


def find_questions(lesson_id: str, questions_dir: Path | None = None) -> list[dict]:
    """Find all questions matching a lesson_id or topic across all JSONL files."""
    search_dir = questions_dir or QUESTIONS_DIR
    questions = []
    if not search_dir.exists():
        return questions
    for f in search_dir.iterdir():
        if f.suffix != ".jsonl":
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            try:
                q = json.loads(line)
                matches = (
                    q.get("lesson_id") == lesson_id
                    or q.get("topic") == lesson_id
                )
                if matches and not q.get("suspended"):
                    questions.append(q)
            except (json.JSONDecodeError, KeyError):
                continue
    return questions


def generate_page(questions: list[dict], title: str, lesson_file: str, map_page: str, domain: str = "", domain_slug: str = "") -> str:
    """Generate the Preact quiz page."""
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from lib.page_template import render_quiz_page

    return render_quiz_page(
        title=title,
        questions=questions,
        lesson_id=lesson_file.replace(".html", ""),
        lesson_file=lesson_file,
        map_page=map_page,
        domain=domain,
        domain_slug=domain_slug,
        depth=2,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate a quiz page from JSONL questions")
    parser.add_argument("--lesson-id", required=True, help="Lesson ID to filter questions (filename without .html)")
    parser.add_argument("--title", required=True, help="Topic title for the page heading")
    parser.add_argument("--lesson-file", required=True, help="Filename of the lesson (for back-link)")
    parser.add_argument("--map-page", required=True, help="Filename of the parent map page")
    parser.add_argument("--domain", default="", help="Human-readable domain name (for breadcrumb)")
    parser.add_argument("--domain-slug", default="", help="Domain slug (for breadcrumb links)")
    parser.add_argument("--output", help="Output path (default: lessons/quiz/{lesson-id}-quiz.html)")
    parser.add_argument("--workspace", help="Workspace root directory (overrides default project root for finding questions)")
    args = parser.parse_args()

    # Determine questions directory
    if args.workspace:
        workspace = Path(args.workspace)
        if not workspace.is_absolute():
            workspace = PROJECT_ROOT / workspace
        questions_dir = workspace / "learning-records" / "questions"
        default_output_dir = workspace / "lessons" / "quiz"
    else:
        questions_dir = QUESTIONS_DIR
        default_output_dir = OUTPUT_DIR

    questions = find_questions(args.lesson_id, questions_dir)
    if not questions:
        print(f"No questions found for lesson_id '{args.lesson_id}'")
        raise SystemExit(1)

    output_path = Path(args.output) if args.output else default_output_dir / f"{args.lesson_id}-quiz.html"
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_html = generate_page(questions, args.title, args.lesson_file, args.map_page, args.domain, args.domain_slug)
    output_path.write_text(page_html, encoding="utf-8")
    print(f"Generated: {output_path} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
