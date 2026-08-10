#!/usr/bin/env python3
"""Generate an HTML quick-check review page from due SR cards.

Reads quick-check cards (question_type="quick-check") that are due for review,
renders them into a self-contained HTML page using the scaffold structure.

Usage:
    python tools/quick-check.py                  # all due quick-check cards
    python tools/quick-check.py iceberg-on-aws   # one topic only
    python tools/quick-check.py --all            # all quick-check cards (ignore schedule)
"""

from __future__ import annotations

import html
import json
import random
import sys
from pathlib import Path

# Add tools/ to path for sibling imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from questions import Card, get_all_due_cards, get_due_cards, read_cards, list_topics, QUESTIONS_DIR

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "lessons" / "review"
OUTPUT_FILE = OUTPUT_DIR / "quick-check.html"
ASSETS_REL = "../../assets"


def get_quick_check_cards(topic_slug: str | None = None, all_cards: bool = False) -> list[Card]:
    """Get quick-check cards, filtered by topic and schedule."""
    if all_cards:
        if topic_slug:
            cards = read_cards(topic_slug)
        else:
            cards = []
            for slug in list_topics():
                cards.extend(read_cards(slug))
    else:
        if topic_slug:
            cards = get_due_cards(topic_slug)
        else:
            cards = get_all_due_cards()

    return [c for c in cards if c.question_type == "quick-check" and c.options and c.correct_index is not None]


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def render_card(card: Card, index: int) -> str:
    """Render a single quick-check card as HTML."""
    card_id = f"card{index}"

    # Shuffle options while tracking the correct answer
    options = list(enumerate(card.options))
    random.shuffle(options)
    correct_shuffled = next(i for i, (orig_idx, _) in enumerate(options) if orig_idx == card.correct_index)

    # Build option buttons
    option_html = []
    for i, (_, text) in enumerate(options):
        option_html.append(
            f'      <button class="qc-option" data-idx="{i}" onclick="pick(\'{card_id}\', {i}, {correct_shuffled})">'
            f'{escape(text)}</button>'
        )
    options_block = "\n".join(option_html)

    # Code block in prompt (optional)
    code_block = ""
    if card.prompt_code:
        lang = card.prompt_code.get("language", "")
        code = escape(card.prompt_code.get("content", ""))
        code_block = f'\n    <pre><code class="language-{lang}">{code}</code></pre>'

    # Explanation
    explanation = escape(card.explanation or card.expected_answer or "")

    # Tags
    tags = ", ".join(card.tags) if card.tags else ""

    return f"""<div class="card" id="{card_id}" data-card-id="{escape(card.id)}">
  <div class="card-prompt">
    <span class="card-type">quick-check</span>
    <p><strong>{escape(card.prompt)}</strong></p>{code_block}
  </div>
  <div class="qc-options">
{options_block}
  </div>
  <div class="qc-feedback" id="{card_id}-feedback"></div>
  <div class="card-meta">From: {escape(card.lesson_id)} — {escape(card.section_heading)} · Tags: {tags}</div>
</div>"""


def render_page(cards: list[Card], topic_label: str) -> str:
    """Render the full HTML page."""
    card_blocks = "\n\n".join(render_card(c, i) for i, c in enumerate(cards))

    # Build explanation data for JS
    explanations = {}
    sources_data = {}
    for i, card in enumerate(cards):
        explanations[f"card{i}"] = card.explanation or card.expected_answer or ""
        if card.sources:
            sources_data[f"card{i}"] = card.sources

    explanations_json = json.dumps(explanations, ensure_ascii=False)
    sources_json = json.dumps(sources_data, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Quick Check — {escape(topic_label)}</title>
  <link rel="stylesheet" href="{ASSETS_REL}/style.css">
  <style>
    .card {{
      border: 2px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      margin: 1.5rem 0;
      background: var(--bg-elevated);
    }}
    .card-prompt {{
      border-left: 4px solid var(--accent);
      padding-left: 1rem;
      margin-bottom: 1rem;
    }}
    .card-type {{
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      background: var(--bg-surface);
      color: var(--accent);
    }}
    .card-meta {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
    }}
    pre {{
      background: var(--code-bg);
      color: var(--text);
      padding: 1rem;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 0.85rem;
      line-height: 1.5;
    }}
    pre code {{ background: none; color: inherit; }}
    .qc-options {{
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin: 0.5rem 0;
    }}
    .qc-option {{
      text-align: left;
      padding: 0.7rem 1rem;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--bg-surface);
      color: var(--text);
      cursor: pointer;
      font-size: 0.9rem;
      transition: border-color 0.15s, background 0.15s;
    }}
    .qc-option:hover:not(:disabled) {{
      border-color: var(--accent);
      background: var(--bg-elevated);
    }}
    .qc-option:disabled {{ cursor: default; opacity: 0.85; }}
    .qc-option.correct {{
      border-color: var(--success);
      background: color-mix(in srgb, var(--success) 12%, var(--bg-surface));
    }}
    .qc-option.incorrect {{
      border-color: var(--error, #dc2626);
      background: color-mix(in srgb, var(--error, #dc2626) 8%, var(--bg-surface));
    }}
    .qc-feedback {{
      margin-top: 0.75rem;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      display: none;
      font-size: 0.9rem;
      line-height: 1.5;
    }}
    .qc-feedback.show {{ display: block; }}
    .qc-feedback.correct {{
      background: color-mix(in srgb, var(--success) 10%, var(--bg-surface));
      border-left: 4px solid var(--success);
    }}
    .qc-feedback.incorrect {{
      background: color-mix(in srgb, var(--error, #dc2626) 8%, var(--bg-surface));
      border-left: 4px solid var(--error, #dc2626);
    }}
    .summary {{
      margin-top: 2rem;
      padding: 1.5rem;
      border-radius: 8px;
      background: var(--bg-elevated);
      border: 2px solid var(--border);
      text-align: center;
      display: none;
    }}
    .summary.show {{ display: block; }}
    .summary .score {{ font-size: 1.5rem; font-weight: 700; }}
    .qc-sources {{
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px solid var(--border);
      font-size: 0.8rem;
    }}
    .qc-sources-label {{
      color: var(--text-muted);
      margin-bottom: 0.25rem;
    }}
    .qc-sources a {{
      display: block;
      color: var(--link);
      text-decoration: none;
      padding: 0.15rem 0;
    }}
    .qc-sources a:hover {{ text-decoration: underline; }}
    .qc-sources .source-section {{
      color: var(--text-muted);
      font-size: 0.75rem;
    }}
  </style>
</head>
<body>

<h1>⚡ Quick Check</h1>
<p class="lesson-meta">Topic: {escape(topic_label)} · {len(cards)} questions</p>

{card_blocks}

<div class="summary" id="summary">
  <p class="score" id="score-text"></p>
  <p id="score-msg"></p>
</div>

<script>
const explanations = {explanations_json};
const sources = {sources_json};
let total = {len(cards)}, answered = 0, correct = 0;

function pick(cardId, selectedIdx, correctIdx) {{
  const card = document.getElementById(cardId);
  const buttons = card.querySelectorAll('.qc-option');
  const feedback = document.getElementById(cardId + '-feedback');

  // Disable all buttons
  buttons.forEach(b => b.disabled = true);

  const isCorrect = selectedIdx === correctIdx;
  buttons[correctIdx].classList.add('correct');
  if (!isCorrect) buttons[selectedIdx].classList.add('incorrect');

  // Show feedback
  const prefix = isCorrect ? '✓ Correct. ' : '✗ Incorrect. ';
  feedback.textContent = prefix + (explanations[cardId] || '');

  // Render source links if available
  const cardSources = sources[cardId];
  if (cardSources && cardSources.length) {{
    const srcDiv = document.createElement('div');
    srcDiv.className = 'qc-sources';
    srcDiv.innerHTML = '<p class="qc-sources-label">📖 Go deeper:</p>' +
      cardSources.map(s =>
        '<a href="' + s.url + '" target="_blank" rel="noopener">' +
        s.label + (s.section ? ' <span class="source-section">— ' + s.section + '</span>' : '') +
        '</a>'
      ).join('');
    feedback.appendChild(srcDiv);
  }}

  feedback.classList.add('show', isCorrect ? 'correct' : 'incorrect');

  answered++;
  if (isCorrect) correct++;

  // Log for potential future integration
  console.log(JSON.stringify({{
    card_id: card.dataset.cardId,
    correct: isCorrect,
    timestamp: new Date().toISOString()
  }}));

  if (answered === total) showSummary();
}}

function showSummary() {{
  const el = document.getElementById('summary');
  document.getElementById('score-text').textContent = correct + ' / ' + total;
  const pct = Math.round(100 * correct / total);
  document.getElementById('score-msg').textContent =
    pct === 100 ? '🎯 Perfect!' :
    pct >= 70 ? '👍 Solid understanding.' :
    '📖 Some concepts need another look.';
  el.classList.add('show');
}}
</script>
<script src="{ASSETS_REL}/theme-toggle.js"></script>

</body>
</html>"""


def main() -> None:
    args = sys.argv[1:]
    all_cards = "--all" in args
    args = [a for a in args if a != "--all"]
    topic_slug = args[0] if args else None

    cards = get_quick_check_cards(topic_slug, all_cards=all_cards)

    if not cards:
        print("No quick-check cards found" + (" (due)" if not all_cards else "") + ".")
        print("Hint: add cards with question_type='quick-check' and options/correct_index fields.")
        sys.exit(0)

    topic_label = topic_slug.replace("-", " ").title() if topic_slug else "All Topics"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    page = render_page(cards, topic_label)
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"✓ Generated {OUTPUT_FILE.relative_to(PROJECT_ROOT)} ({len(cards)} cards)")


if __name__ == "__main__":
    main()
