---
id: "034"
title: "Research: media and rich content in SR prompts — prior art and spike recommendations"
status: done
priority: medium
blocked_by: []
type: research
tags: [platform]
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

- [x] `repeater` (https://github.com/shaankhosla/repeater) — how it handles note formatting
- [x] `cert-pepper` (https://github.com/cert-pepper/cert-pepper) — code-heavy cards + Claude explanations
- [x] Anki source (https://github.com/ankitects/anki) — HTML field rendering, media storage
- [x] Orbit (https://github.com/andymatuschak/orbit) — web component rendering of rich prompts
- [x] `rich` library examples (https://github.com/Textualize/rich) — terminal rendering of code, markdown, panels

## Spikes to consider

1. **Spike: code block cards** — extend Card schema with `prompt_code` field, render via `rich` in terminal, syntax-highlighted `<pre>` in HTML
2. **Spike: diagram reference cards** — card references an SVG by lesson path, terminal shows the URL, HTML embeds inline
3. **Spike: markdown prompt rendering** — store prompts as markdown, render with `rich.markdown` in terminal + marked.js in HTML

## Acceptance criteria

- [x] Research findings documented in `.scratch/research/034-media-in-prompts.md`
- [x] At least 2 reference repos cloned to `.references/` and explored
- [x] Spike recommendation with effort estimate (which approach, what deps, what tradeoffs)
- [x] Decision: which rich content type to implement first (code blocks? diagrams? markdown?)

## Resolution (2026-08-09)

Research complete. Findings in `.memory/034-rich-content-proposal.md`. Repos explored: repeater, cert-pepper, rich.

**Decision:** Markdown rendering first (spike 039, no schema change, 1hr). Then code blocks (037, 2hr). Diagram refs (038) last and lowest value.

**Key insight:** No schema change needed for markdown — prompts/answers already support it, we just need to upgrade the renderer to Rich. Only code blocks need a new optional field.
