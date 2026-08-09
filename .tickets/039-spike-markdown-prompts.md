---
id: "039"
title: "Spike: markdown prompts — store as markdown, render everywhere"
status: done
priority: medium
blocked_by: ["034"]
type: spike
---

# Spike: markdown prompts — store as markdown, render everywhere

## Question to answer

Should we store card prompts and answers as markdown (with inline code, bold, links) instead of plain text, and render them appropriately in each context?

## What to try

1. Add `rich` to project dependencies (`mise run setup`)
2. Update `review.py` to render prompts/answers via `rich.markdown.Markdown` inside `rich.panel.Panel`
3. Write 3-5 test cards with markdown formatting:
   - Inline code: "Explain what `OPTIMIZE` does to manifest files"
   - Bold emphasis: "Why is **snapshot isolation** critical for concurrent writes?"
   - Lists in expected_answer: key points as bullet list
   - Fenced code block in expected_answer (SQL example)
4. Run review in terminal — verify rendering
5. Evaluate: does markdown add clarity for explain-to-colleague format?

## Implementation pattern (from Rich exploration)

```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

console = Console()

# Display question
console.print(Panel(
    Markdown(card.prompt),
    title=f"[bold]Review[/bold] ({card.question_type})",
    border_style="blue"
))

# After learner responds...
console.print(Rule("Answer", style="dim"))
console.print(Panel(
    Markdown(card.expected_answer),
    border_style="green"
))
```

## Dependencies

- `pip install rich` (pulls in Pygments + markdown-it-py transitively)
- These handle both markdown rendering AND syntax highlighting for fenced code blocks

## Key decision

Most of our prompts are conversational ("Explain to a colleague why..."). Markdown formatting may not add much for this style. But expected_answers often benefit from structure (lists of key points, inline code for technical terms).

Consider: **prompts stay plain text, answers get markdown**. Simpler, and the answer is where structure helps most.

## Success criteria

- [x] Rich renders markdown prompts/answers readably in terminal
- [x] HTML path renders the same content correctly
- [x] Evaluate: markdown in prompts — helpful or noisy?
- [x] Evaluate: markdown in answers only — is this the sweet spot?
- [x] Backward compatible (plain text cards render unchanged)

## Resolution (2026-08-09)

**Result:** Markdown rendering works with NO schema change — just `pip install rich` and upgrade review.py renderer.

**Evaluation:** Markdown is most useful in expected_answers (lists of key points, inline code for technical terms, tables for comparison). Prompts benefit from inline code but don't need much else — the conversational format stays plain.

**Sweet spot:** Prompts use light markdown (inline `code`, **bold** for emphasis). Answers use full markdown (lists, code fences, tables). Both render via Rich's Markdown class transparently.

**Graceful fallback:** Plain text cards unchanged. Rich not installed → prints unformatted text.

## Time box

1.5 hours. Focus on the evaluation question, not just the technical feasibility.
