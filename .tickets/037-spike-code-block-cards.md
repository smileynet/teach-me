---
id: "037"
title: "Spike: code block cards — rich CLI rendering + HTML display"
status: open
priority: medium
blocked_by: ["034"]
type: spike
---

# Spike: code block cards

## Question to answer

Can we extend SR cards to include syntax-highlighted code blocks that render well in both terminal (via Rich) and HTML (via existing quiz component)?

## What to try

1. Add `prompt_code` and `answer_code` optional fields to Card schema (language + content)
2. In `review.py`: render code via `rich.syntax.Syntax` with `ansi_dark` theme
3. In quick-check HTML page: render via `<pre><code class="language-X">` + highlight.js
4. Generate a test card with a Python code block, review it in both paths

## Dependencies

- `pip install rich` (adds Pygments transitively)
- No new deps for HTML path (highlight.js already used by quiz component or trivial to add)

## Success criteria

- [ ] Card with code block renders syntax-highlighted in terminal
- [ ] Same card renders syntax-highlighted in HTML review page
- [ ] Code theme respects terminal palette (ansi_dark/ansi_light)
- [ ] Plain-text cards still work unchanged (backward compatible)
- [ ] Effort estimate for full implementation documented

## Time box

2 hours max. If it works, write up the integration pattern. If it doesn't, document why.
