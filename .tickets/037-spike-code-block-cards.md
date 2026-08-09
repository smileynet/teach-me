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

- [ ] Card with code block renders syntax-highlighted in terminal
- [ ] Same card renders syntax-highlighted in HTML review page
- [ ] Code theme respects terminal palette (ansi_dark/ansi_light)
- [ ] Plain-text cards still work unchanged (backward compatible)
- [ ] Effort estimate for full implementation documented

## Time box

2 hours max. If it works, write up the integration pattern. If it doesn't, document why.
