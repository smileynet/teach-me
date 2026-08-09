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

1. Add `prompt_media` optional field to Card: `{"type": "svg_ref", "lesson": "0001-...", "selector": "svg[aria-labelledby='diagram-commit-cycle']"}`
2. In HTML review page: fetch the SVG from the lesson and inline it
3. In terminal: show `[See diagram: http://localhost:8080/lessons/0001-...#diagram-commit-cycle]`
4. Generate a test card that asks "What step comes after Conflict Check in this diagram?"

## Success criteria

- [ ] HTML review page embeds the referenced SVG inline
- [ ] Terminal review shows a usable link to the diagram
- [ ] Card is answerable in both contexts (prompt text is sufficient without diagram, diagram adds context)
- [ ] Evaluate: are diagram-reference cards actually useful, or does the text prompt suffice?

## Time box

1 hour. The key question isn't "can we do it" but "should we" — does referencing a diagram in a card add enough value over a well-written text prompt?
