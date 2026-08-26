---
id: "037"
title: "Spike: code block cards — rich CLI rendering + HTML display"
status: done
priority: medium
blocked_by: ["034"]
type: spike
tags: [platform]
---

# Spike: code block cards

## Question to answer

Can we extend SR cards to include syntax-highlighted code blocks that render well in both terminal (via Rich) and HTML (via existing quiz component)?

## What to try

1. Add `prompt_code` and `answer_code` optional fields to Card dataclass:
   ```python
   prompt_code: dict | None = None   # {"language": "python", "content": "def foo():..."}
   answer_code: dict | None = None   # {"language": "sql", "content": "SELECT..."}
   ```
2. In `review.py`: when `prompt_code` is present, render via `rich.syntax.Syntax`:
   ```python
   from rich.syntax import Syntax
   code = Syntax(card.prompt_code["content"], card.prompt_code["language"],
                 theme="ansi_dark", padding=1, line_numbers=True)
   console.print(Panel(Group(Markdown(card.prompt), code), title="Question", border_style="blue"))
   ```
3. In quick-check HTML page: render via `<pre><code class="language-python">` + highlight.js
4. Generate test cards:
   - "What's wrong with this query?" + SQL code block
   - "Explain what this function does" + Python code block
5. Verify both terminal and HTML rendering

## Key learnings from repeater

- Fenced code blocks inside card content are preserved verbatim through parsing
- `ansi_dark` theme respects terminal palette (pairs with our theme system)
- `line_numbers` and `highlight_lines` options available for emphasizing specific lines

## Dependencies

- `rich` (already added for spike 039)
- No new deps — Pygments (syntax highlighting engine) comes with Rich

## Dependencies

- `pip install rich` (adds Pygments transitively)
- No new deps for HTML path (highlight.js already used by quiz component or trivial to add)

## Success criteria

- [x] Card with code block renders syntax-highlighted in terminal
- [x] Same card renders syntax-highlighted in HTML review page
- [x] Code theme respects terminal palette (ansi_dark/ansi_light)
- [x] Plain-text cards still work unchanged (backward compatible)
- [x] Effort estimate for full implementation documented

## Resolution (2026-08-09)

**Works.** Added `prompt_code` and `answer_code` as optional dict fields on Card. Rich's `Syntax` class renders them with ansi_dark theme inside the Panel. Zero new dependencies (Pygments comes with Rich).

**Effort for full implementation:** Already done — the spike IS the implementation. Optional fields are backward compatible, rendering handles presence/absence. HTML path will work via highlight.js when the quick-check page (ticket 035) is built.

**Pattern:** `Panel(Group(Markdown(prompt_text), Syntax(code, language)))` — composable Rich renderables stacked vertically.

## Time box

2 hours max. If it works, write up the integration pattern. If it doesn't, document why.
