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
import html
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


def generate_page(questions: list[dict], title: str, lesson_file: str, map_page: str) -> str:
    """Generate the Preact quiz page."""
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from lib.preact_page import render_page

    data = {
        "questions": questions,
        "title": title,
        "lessonFile": lesson_file,
        "mapPage": map_page,
    }

    module_script = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { QuizView } from '../../assets/components/QuizView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${QuizView} questions=${data.questions} title=${data.title} />`,
      document.getElementById('app')
    );
"""

    css_extra = """
    body { max-width: 700px; margin: 0 auto; padding: 2rem; }
    .quiz-view h1 { font-size: 1.4rem; margin-bottom: 1.5rem; }
    .quiz-card { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; }
    .quiz-progress { font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.75rem; }
    .quiz-prompt { font-size: 1rem; line-height: 1.5; margin-bottom: 1rem; }
    .quiz-answer { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); }
    .quiz-answer p { font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1rem; }
    .assess-label { font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.5rem; }
    .assess-buttons { display: flex; gap: 0.5rem; }
    .quiz-summary { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; text-align: center; }
    .quiz-summary h2 { margin-bottom: 1rem; }
    .summary-stats { display: flex; gap: 1rem; justify-content: center; margin-bottom: 1rem; }
    .stat.got { color: var(--success); }
    .stat.partial { color: var(--warning); }
    .stat.missed { color: var(--error); }
    .summary-note { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
    .summary-actions { display: flex; gap: 0.5rem; justify-content: center; }
    .empty { color: var(--text-muted); text-align: center; padding: 3rem; }
"""

    return render_page(
        title=f"Quiz: {title}",
        data=data,
        module_script=module_script,
        css_extra=css_extra,
        depth=2,  # lessons/quiz/ = 2 levels deep
    )


def main():
    parser = argparse.ArgumentParser(description="Generate a quiz page from JSONL questions")
    parser.add_argument("--lesson-id", required=True, help="Lesson ID to filter questions (filename without .html)")
    parser.add_argument("--title", required=True, help="Topic title for the page heading")
    parser.add_argument("--lesson-file", required=True, help="Filename of the lesson (for back-link)")
    parser.add_argument("--map-page", required=True, help="Filename of the parent map page")
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

    page_html = generate_page(questions, args.title, args.lesson_file, args.map_page)
    output_path.write_text(page_html, encoding="utf-8")
    print(f"Generated: {output_path} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
