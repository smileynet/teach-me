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
from diagram_mask import extract_svg, mask_svg, DIAGRAM_CARD_STYLES, DIAGRAM_CARD_JS

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

    return [c for c in cards if c.question_type == "quick-check" and (
        (c.options and c.correct_index is not None) or
        (c.svg_ref and c.occluded_labels)
    )]


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def render_card(card: Card, index: int) -> str:
    """Render a single quick-check card as HTML."""
    if card.svg_ref and card.occluded_labels:
        return render_diagram_card(card, index)
    return render_mc_card(card, index)


def render_diagram_card(card: Card, index: int) -> str:
    """Render a diagram card with masked labels."""
    card_id = f"card{index}"

    # Extract SVG from lesson
    svg_str = extract_svg(card.svg_ref.get("lesson_file", ""), card.svg_ref.get("svg_index", 0))
    if not svg_str:
        # Fallback to text-only if SVG not found
        return render_mc_card(card, index) if card.options else ""

    # Apply masking
    masked_svg = mask_svg(svg_str, card.occluded_labels)

    # Tags
    tags = ", ".join(card.tags) if card.tags else ""
    n_labels = len(card.occluded_labels)

    return f"""<div class="card" id="{card_id}" data-card-id="{escape(card.id)}">
  <div class="card-prompt">
    <span class="card-type">diagram</span>
    <p><strong>{escape(card.prompt)}</strong></p>
  </div>
  <div class="diagram-container">
    {masked_svg}
  </div>
  <p class="diagram-status">{n_labels} label{"s" if n_labels != 1 else ""} hidden — click each to reveal</p>
  <div class="qc-feedback" id="{card_id}-feedback"></div>
  <div class="card-meta">From: {escape(card.lesson_id)} — {escape(card.section_heading)} · Tags: {tags}</div>
</div>"""


def render_mc_card(card: Card, index: int) -> str:
    """Render a multiple-choice quick-check card as HTML."""
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


def render_page(cards: list, topic_label: str) -> str:
    """Render the Preact review page."""
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib.preact_page import render_page as _render

    card_data = []
    for c in cards:
        card_data.append({
            "prompt": c.prompt,
            "answer": c.expected_answer or "",
            "criteria": c.explanation or c.expected_answer or "",
            "topic": c.topic,
            "source": c.sources[0] if c.sources else "",
        })

    title = f"Quick Check: {topic_label}" if topic_label else "Quick Check Review"
    data = {"cards": card_data, "title": title}

    module_script = (
        "    import { h, render } from 'preact';\n"
        "    import htm from 'htm';\n"
        "    import { ReviewView } from '../../assets/components/ReviewView.js';\n"
        "\n"
        "    const html = htm.bind(h);\n"
        "    const data = JSON.parse(document.getElementById('page-data').textContent);\n"
        "\n"
        "    render(\n"
        "      html`<${ReviewView} cards=${data.cards} title=${data.title} />`,\n"
        "      document.getElementById('app')\n"
        "    );\n"
    )

    css_extra = (
        "    body { max-width: 700px; margin: 0 auto; padding: 2rem; }\n"
        "    .review-view h1 { font-size: 1.4rem; margin-bottom: 1.5rem; }\n"
        "    .review-card { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; }\n"
        "    .review-progress { font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.75rem; }\n"
        "    .review-prompt { font-size: 1rem; line-height: 1.5; margin-bottom: 1rem; }\n"
        "    .review-answer { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); }\n"
        "    .review-answer p { font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1rem; }\n"
        "    .rating-label { font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.5rem; }\n"
        "    .rating-buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; }\n"
        "    .review-summary { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; text-align: center; }\n"
        "    .review-summary h2 { margin-bottom: 1rem; }\n"
        "    .summary-stats { display: flex; gap: 1rem; justify-content: center; margin-bottom: 0.75rem; }\n"
        "    .stat.easy { color: var(--success); }\n"
        "    .stat.hard { color: var(--warning); }\n"
        "    .stat.forgot { color: var(--error); }\n"
        "    .summary-pct { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }\n"
        "    .summary-actions { display: flex; gap: 0.5rem; justify-content: center; }\n"
        "    .empty { color: var(--text-muted); text-align: center; padding: 3rem; }\n"
    )

    return _render(
        title=title,
        data=data,
        module_script=module_script,
        css_extra=css_extra,
        depth=2,
    )


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
