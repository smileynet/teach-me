#!/usr/bin/env python3
"""Export SR question bank to Anki .apkg format.

Uses genanki to produce importable decks with two note models:
- TeachMe Explain: open-ended cards (explain, compare, apply, predict)
- TeachMe QuickCheck: multiple-choice cards

Usage:
    python tools/export_anki.py                        # all topics
    python tools/export_anki.py iceberg-on-aws         # one topic
    python tools/export_anki.py --output ~/deck.apkg   # custom output
    python tools/export_anki.py --exclude-suspended    # skip suspended
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import genanki

# Add tools/ to path for sibling imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from questions import Card, read_cards, list_topics

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "teach-me-export.apkg"

# Stable model IDs (random, never change after first use)
EXPLAIN_MODEL_ID = 1607392319
QUICKCHECK_MODEL_ID = 1607392320
DECK_ID = 1607392321

# --- Note Models ---

EXPLAIN_MODEL = genanki.Model(
    EXPLAIN_MODEL_ID,
    "TeachMe — Explain",
    fields=[
        {"name": "CardID"},
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Source"},
        {"name": "Context"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": "{{Front}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{Back}}'
               '{{#Source}}<div class="sources">📖 {{Source}}</div>{{/Source}}'
               '{{#Context}}<div class="context">{{Context}}</div>{{/Context}}',
    }],
    css="""
    .card { font-family: system-ui, sans-serif; font-size: 16px; line-height: 1.6; padding: 1rem; }
    pre { background: #1e1e2e; color: #cdd6f4; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 14px; }
    .sources { margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid #ccc; font-size: 0.8rem; color: #666; }
    .sources a { color: #2563eb; }
    .context { font-size: 0.75rem; color: #888; margin-top: 0.5rem; }
    """,
)

QUICKCHECK_MODEL = genanki.Model(
    QUICKCHECK_MODEL_ID,
    "TeachMe — QuickCheck",
    fields=[
        {"name": "CardID"},
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Source"},
        {"name": "Context"},
    ],
    templates=[{
        "name": "Card 1",
        "qfmt": "{{Front}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{Back}}'
               '{{#Source}}<div class="sources">📖 {{Source}}</div>{{/Source}}'
               '{{#Context}}<div class="context">{{Context}}</div>{{/Context}}',
    }],
    css="""
    .card { font-family: system-ui, sans-serif; font-size: 16px; line-height: 1.6; padding: 1rem; }
    .option { padding: 0.4rem 0.8rem; margin: 0.3rem 0; border: 1px solid #ddd; border-radius: 4px; }
    .option.correct { border-color: #16a34a; background: #dcfce7; }
    .sources { margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid #ccc; font-size: 0.8rem; color: #666; }
    .sources a { color: #2563eb; }
    .context { font-size: 0.75rem; color: #888; margin-top: 0.5rem; }
    """,
)


# --- Card → Note conversion ---

def escape(text: str) -> str:
    return html.escape(text, quote=True)


def render_code_block(code_data: dict | None) -> str:
    if not code_data:
        return ""
    lang = code_data.get("language", "")
    content = escape(code_data.get("content", ""))
    return f'<pre><code class="language-{lang}">{content}</code></pre>'


def render_sources(sources: list[dict] | None) -> str:
    if not sources:
        return ""
    links = []
    for src in sources:
        url = escape(src.get("url", ""))
        label = escape(src.get("label", ""))
        section = src.get("section", "")
        link_text = f"{label} — {section}" if section else label
        links.append(f'<a href="{url}" target="_blank">{escape(link_text)}</a>')
    return "<br>".join(links)


def card_to_tags(card: Card, topic_slug: str) -> list[str]:
    tags = [
        f"topic::{topic_slug}",
        f"type::{card.question_type}",
        f"tier::{card.difficulty_tier}",
    ]
    if card.lesson_id:
        tags.append(f"lesson::{card.lesson_id}")
    return tags


def explain_card_to_note(card: Card, topic_slug: str) -> genanki.Note:
    front = f"<p><strong>{escape(card.prompt)}</strong></p>"
    front += render_code_block(card.prompt_code)

    back = f"<p>{escape(card.expected_answer)}</p>"
    back += render_code_block(card.answer_code)

    context = f"{card.lesson_id} — {card.section_heading}" if card.lesson_id else ""

    return genanki.Note(
        model=EXPLAIN_MODEL,
        fields=[card.id, front, back, render_sources(card.sources), context],
        guid=genanki.guid_for(card.id),
        tags=card_to_tags(card, topic_slug),
    )


def quickcheck_card_to_note(card: Card, topic_slug: str) -> genanki.Note:
    front = f"<p><strong>{escape(card.prompt)}</strong></p>"
    front += render_code_block(card.prompt_code)

    # Build answer with correct option highlighted
    options_html = []
    for i, opt in enumerate(card.options or []):
        cls = "option correct" if i == card.correct_index else "option"
        marker = "✓ " if i == card.correct_index else ""
        options_html.append(f'<div class="{cls}">{marker}{escape(opt)}</div>')

    back = "\n".join(options_html)
    if card.explanation:
        back += f"<p><em>{escape(card.explanation)}</em></p>"

    context = f"{card.lesson_id} — {card.section_heading}" if card.lesson_id else ""

    return genanki.Note(
        model=QUICKCHECK_MODEL,
        fields=[card.id, front, back, render_sources(card.sources), context],
        guid=genanki.guid_for(card.id),
        tags=card_to_tags(card, topic_slug),
    )


def card_to_note(card: Card, topic_slug: str) -> genanki.Note:
    if card.question_type == "quick-check" and card.options:
        return quickcheck_card_to_note(card, topic_slug)
    return explain_card_to_note(card, topic_slug)


# --- Main ---

def main() -> None:
    args = sys.argv[1:]
    exclude_suspended = "--exclude-suspended" in args
    args = [a for a in args if a != "--exclude-suspended"]

    output_path = DEFAULT_OUTPUT
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = Path(args[idx + 1]).expanduser()
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    topic_slug = args[0] if args else None
    topics = [topic_slug] if topic_slug else list_topics()

    if not topics:
        print("No topics found in learning-records/questions/.")
        sys.exit(0)

    deck_name = f"teach-me::{topic_slug}" if topic_slug else "teach-me"
    deck = genanki.Deck(DECK_ID, deck_name)

    total_cards = 0
    for slug in topics:
        cards = read_cards(slug)
        for card in cards:
            if exclude_suspended and card.suspended:
                continue
            if card.mastered:
                continue
            deck.add_note(card_to_note(card, slug))
            total_cards += 1

    if total_cards == 0:
        print("No cards to export.")
        sys.exit(0)

    package = genanki.Package(deck)
    package.write_to_file(str(output_path))
    print(f"✓ Exported {total_cards} cards to {output_path}")


if __name__ == "__main__":
    main()
