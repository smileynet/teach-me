---
id: "034"
title: "Research: media and rich content in SR prompts — prior art and spike recommendations"
status: open
priority: medium
blocked_by: []
type: research
---

# Research: media and rich content in SR prompts

## What to research

How do existing SR/flashcard systems handle rich content (diagrams, code, formatted text) in prompts? What libraries, formats, and rendering approaches work well in CLI + HTML hybrid environments?

## Research questions

1. **Format**: How do Anki, Mochi, Orbit, and repeater store rich content in cards? (HTML fields? Markdown? Embedded media?)
2. **CLI rendering**: What Python libraries render rich content in terminal? (rich, textual, blessed?) How do they handle code blocks, tables, images?
3. **Code-in-cards**: How do programming-focused SR tools (cert-pepper, Exercism) present code blocks? Syntax highlighting? Diff views?
4. **Diagram references**: How do tools reference/embed visuals in flashcards? (Inline SVG? Image paths? URLs?)
5. **Hybrid rendering**: When the same card renders both in terminal (review.py) and in HTML (quiz page), what abstraction handles both?

## Repos to clone and explore

- [ ] `repeater` (https://github.com/shaankhosla/repeater) — how it handles note formatting
- [ ] `cert-pepper` (https://github.com/cert-pepper/cert-pepper) — code-heavy cards + Claude explanations
- [ ] Anki source (https://github.com/ankitects/anki) — HTML field rendering, media storage
- [ ] Orbit (https://github.com/andymatuschak/orbit) — web component rendering of rich prompts
- [ ] `rich` library examples (https://github.com/Textualize/rich) — terminal rendering of code, markdown, panels

## Spikes to consider

1. **Spike: code block cards** — extend Card schema with `prompt_code` field, render via `rich` in terminal, syntax-highlighted `<pre>` in HTML
2. **Spike: diagram reference cards** — card references an SVG by lesson path, terminal shows the URL, HTML embeds inline
3. **Spike: markdown prompt rendering** — store prompts as markdown, render with `rich.markdown` in terminal + marked.js in HTML

## Acceptance criteria

- [ ] Research findings documented in `.scratch/research/034-media-in-prompts.md`
- [ ] At least 2 reference repos cloned to `.references/` and explored
- [ ] Spike recommendation with effort estimate (which approach, what deps, what tradeoffs)
- [ ] Decision: which rich content type to implement first (code blocks? diagrams? markdown?)
