---
id: "038"
title: "Spike: diagram reference cards — SVG in HTML, URL in terminal"
status: open
priority: low
blocked_by: ["034"]
type: spike
---

# Spike: diagram reference cards

## Question to answer

Can SR cards reference inline SVG diagrams from lessons, displaying them in HTML review and gracefully degrading to a clickable URL in terminal?

## What to try

1. Add `prompt_media` optional field to Card:
   ```python
   prompt_media: dict | None = None
   # {"type": "svg_ref", "lesson": "0001-iceberg-metadata-tree",
   #  "selector": "svg[aria-labelledby='diagram-commit-cycle']",
   #  "url": "/lessons/0001-iceberg-metadata-tree.html#diagram-commit-cycle"}
   ```
2. In HTML review page: fetch the SVG from the lesson file and inline it (or use an `<object>` tag)
3. In terminal: show clickable link with context:
   ```python
   from rich.panel import Panel
   from rich.markdown import Markdown
   console.print(Panel(
       Markdown(f"{card.prompt}\n\n[See diagram]({card.prompt_media['url']})"),
       title="Question", border_style="blue"
   ))
   ```
4. Generate a test card: "What step comes after Conflict Check in this diagram?" referencing the commit cycle SVG

## Key question

Does referencing a diagram in a card add enough value over a well-written text prompt? Most explain-to-colleague questions work fine without the diagram — the learner should carry the mental model, not rely on the visual.

**Likely outcome:** Diagram refs are useful only for "annotate this" or "what's missing" type questions — a narrow use case. Most cards are better as pure text.

## Dependencies

- No new deps (rich already handles clickable links in OSC-8 terminals)
- HTML path needs lesson file access (same server that hosts lessons)

## Success criteria

- [ ] HTML review page embeds the referenced SVG inline
- [ ] Terminal review shows a usable link to the diagram
- [ ] Card is answerable in both contexts (prompt text is sufficient without diagram, diagram adds context)
- [ ] Evaluate: are diagram-reference cards actually useful, or does the text prompt suffice?

## Time box

1 hour. The key question isn't "can we do it" but "should we" — does referencing a diagram in a card add enough value over a well-written text prompt?
