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
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = PROJECT_ROOT / "learning-records" / "questions"
OUTPUT_DIR = PROJECT_ROOT / "lessons" / "quiz"


def find_questions(lesson_id: str) -> list[dict]:
    """Find all questions matching a lesson_id across all JSONL files."""
    questions = []
    if not QUESTIONS_DIR.exists():
        return questions
    for f in QUESTIONS_DIR.iterdir():
        if f.suffix != ".jsonl":
            continue
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            try:
                q = json.loads(line)
                if q.get("lesson_id") == lesson_id and not q.get("suspended"):
                    questions.append(q)
            except (json.JSONDecodeError, KeyError):
                continue
    return questions


def generate_page(questions: list[dict], title: str, lesson_file: str, map_page: str) -> str:
    """Generate the quiz HTML page."""
    cards_html = ""
    for i, q in enumerate(questions, 1):
        prompt = html.escape(q.get("prompt", ""))
        answer = html.escape(q.get("expected_answer", ""))
        q_type = html.escape(q.get("question_type", "explain"))
        section = html.escape(q.get("section_heading", ""))
        tags = ", ".join(q.get("tags", []))

        cards_html += f"""
    <div class="card" id="card{i}">
      <div class="card-prompt">
        <span class="card-type">{q_type}</span>
        <p><strong>{prompt}</strong></p>
      </div>
      <button class="reveal-btn" onclick="reveal('card{i}')">Show Answer</button>
      <div class="card-answer">
        <p>{answer}</p>
      </div>
      <div class="rating" id="card{i}-rating">
        <p>How well could you explain this?</p>
        <button onclick="rate('card{i}', 1)">Not at all</button>
        <button onclick="rate('card{i}', 3)">Roughly</button>
        <button onclick="rate('card{i}', 5)">Confidently</button>
      </div>
      <div class="card-meta">Section: {section} · Tags: {tags}</div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quiz: {html.escape(title)}</title>
  <link rel="stylesheet" href="../../assets/style.css">
  <style>
    .quiz-container {{ max-width: 700px; margin: 0 auto; padding: 1rem; }}
    .quiz-nav {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 0.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid var(--border);
      font-size: 0.85rem;
    }}
    .quiz-nav a {{ color: var(--link); text-decoration: none; }}
    .quiz-nav a:hover {{ text-decoration: underline; }}
    .quiz-progress {{ color: var(--text-muted); }}
    .card {{
      border: 2px solid var(--border); border-radius: 8px;
      padding: 1.5rem; margin: 1.5rem 0; background: var(--bg-elevated);
    }}
    .card-prompt {{
      border-left: 4px solid var(--accent); padding-left: 1rem; margin-bottom: 1rem;
    }}
    .card-answer {{
      border-left: 4px solid var(--success, #16a34a); padding-left: 1rem;
      display: none;
    }}
    .card-answer.revealed {{ display: block; }}
    .card-meta {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem; }}
    .card-type {{
      display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
      font-size: 0.75rem; font-weight: 600; background: var(--bg-surface); color: var(--accent);
      margin-bottom: 0.5rem;
    }}
    .reveal-btn {{
      background: var(--accent); color: var(--bg); border: none;
      padding: 0.5rem 1.2rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem;
    }}
    .reveal-btn:hover {{ opacity: 0.85; }}
    .rating {{ margin-top: 1rem; display: none; }}
    .rating.revealed {{ display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }}
    .rating p {{ margin: 0; font-size: 0.85rem; color: var(--text-muted); }}
    .rating button {{
      padding: 0.4rem 0.8rem; border: 1px solid var(--border); border-radius: 4px;
      cursor: pointer; background: var(--bg-surface); color: var(--text); font-size: 0.8rem;
    }}
    .rating button:hover {{ background: var(--bg-elevated); border-color: var(--accent); }}
    .rating button.selected {{ background: color-mix(in srgb, var(--accent) 15%, var(--bg)); border-color: var(--accent); }}
    .quiz-done {{
      margin-top: 2rem; padding: 1.25rem; border-radius: 8px;
      background: var(--bg-elevated); border: 1px solid var(--border);
      text-align: center;
    }}
    .quiz-done a {{
      display: inline-block; margin: 0.5rem; padding: 0.6rem 1rem;
      border-radius: 6px; text-decoration: none; font-size: 0.9rem;
      border: 1px solid var(--accent); color: var(--accent);
    }}
    .quiz-done a:hover {{ background: var(--bg-surface); }}
  </style>
</head>
<body>

<div class="quiz-container">
  <nav class="quiz-nav">
    <a href="../{html.escape(lesson_file)}">← Back to lesson</a>
    <span class="quiz-progress">{len(questions)} questions</span>
    <a href="../{html.escape(map_page)}">← Back to map</a>
  </nav>

  <h1>Quiz: {html.escape(title)}</h1>
  <p style="color:var(--text-muted); margin-bottom:1.5rem;">Read each question, form your answer, then reveal to check. Rate your confidence honestly.</p>

{cards_html}

  <div class="quiz-done">
    <h3>Done!</h3>
    <p>Review complete. How did you do?</p>
    <a href="../{html.escape(lesson_file)}">← Review the lesson</a>
    <a href="../{html.escape(map_page)}">← Back to map</a>
  </div>
</div>

<script>
function reveal(cardId) {{
  document.querySelector(`#${{cardId}} .card-answer`).classList.add('revealed');
  document.querySelector(`#${{cardId}} .reveal-btn`).style.display = 'none';
  document.querySelector(`#${{cardId}}-rating`).classList.add('revealed');
}}
function rate(cardId, quality) {{
  const buttons = document.querySelectorAll(`#${{cardId}}-rating button`);
  buttons.forEach(b => b.classList.remove('selected'));
  event.target.classList.add('selected');
}}
</script>
<script src="../../assets/theme-toggle.js"></script>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate a quiz page from JSONL questions")
    parser.add_argument("--lesson-id", required=True, help="Lesson ID to filter questions (filename without .html)")
    parser.add_argument("--title", required=True, help="Topic title for the page heading")
    parser.add_argument("--lesson-file", required=True, help="Filename of the lesson (for back-link)")
    parser.add_argument("--map-page", required=True, help="Filename of the parent map page")
    parser.add_argument("--output", help="Output path (default: lessons/quiz/{lesson-id}-quiz.html)")
    args = parser.parse_args()

    questions = find_questions(args.lesson_id)
    if not questions:
        print(f"No questions found for lesson_id '{args.lesson_id}'")
        raise SystemExit(1)

    output_path = Path(args.output) if args.output else OUTPUT_DIR / f"{args.lesson_id}-quiz.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    page_html = generate_page(questions, args.title, args.lesson_file, args.map_page)
    output_path.write_text(page_html, encoding="utf-8")
    print(f"Generated: {output_path} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
