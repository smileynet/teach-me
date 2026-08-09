# Rich Content in SR Cards — Synthesis & Proposal

Based on exploration of repeater (Rust SRS), cert-pepper (Python + Rich + MCP), and the Rich library.

## Key Findings

### What repeater teaches us (content model)
- **Markdown-native storage**: cards are plain markdown — no separate DB for content
- **Meaning-hash identity** (BLAKE3): normalized content hash means formatting edits don't reset progress, semantic changes do. This is the right identity model.
- **Code blocks preserved**: fenced ``` tracking in parser keeps code verbatim inside cards
- **Rich terminal rendering**: pulldown_cmark → styled Text with bold, italic, code highlighting, LaTeX→Unicode conversion

### What cert-pepper teaches us (rendering + AI)
- **Uses Rich but NOT rich.markdown** — all plain text. This is a gap, not a choice.
- **Panel/Text/Table for structure**: bordered boxes per card, colored by domain/state
- **AI explanations cached in DB**: smart pattern for pre-generating rich answer content
- **MCP integration**: study-engine as a server, host model does the thinking. Interesting for future but not needed now.

### What Rich teaches us (exact API)
- **Panel(Group(Markdown(q), Rule(), Markdown(a)))** — the flashcard display pattern
- **Syntax(code, "python", theme="ansi_dark")** — code blocks with terminal-native colors
- **Console input alongside output**: `Confirm.ask()`, `IntPrompt.ask()` for review flow
- **Theme system**: custom named styles, easy to match our color vocabulary

## Proposed Changes

### 1. Card Schema Extension

Add optional `prompt_code` and `answer_code` fields (backward compatible):

```python
@dataclass
class Card:
    # ... existing fields ...
    prompt_code: dict | None = None   # {"language": "python", "content": "..."}
    answer_code: dict | None = None   # {"language": "sql", "content": "..."}
```

Cards without these fields work exactly as before. When present, review tools render them with syntax highlighting.

### 2. Review CLI Upgrade (review.py → rich)

Add `rich` as a dependency. When reviewing interactively, render cards as:

```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.rule import Rule

console = Console()

# Question
question = Markdown(card.prompt)
if card.prompt_code:
    code = Syntax(card.prompt_code["content"], card.prompt_code["language"],
                  theme="ansi_dark", padding=1)
    console.print(Panel(Group(question, code), title="Question", border_style="blue"))
else:
    console.print(Panel(question, title="Question", border_style="blue"))

# After learner responds...
answer = Markdown(card.expected_answer)
console.print(Panel(answer, title="Answer", border_style="green"))
```

### 3. Markdown in prompt/answer text (not a separate field)

Rather than a new field, allow prompt and expected_answer to contain markdown. Rich's `Markdown` class handles this transparently:
- `**bold**` → emphasized text
- `` `inline code` `` → highlighted inline
- Fenced code blocks → syntax-highlighted via Pygments
- Lists and headers → properly formatted

This means NO schema change needed for markdown support — just upgrade the renderer.

### 4. Quick-check HTML page rendering

For the HTML review page (ticket 035), markdown in prompts/answers renders via `marked.js` + `highlight.js` — both small, well-established libraries already compatible with our lesson HTML pattern.

### 5. Meaning-hash identity (future)

Adopt repeater's pattern: hash normalized content (lowercase, whitespace-collapsed) for card identity. Benefits:
- Rename/reformat without losing review progress
- Detect semantic duplicates across topics
- Stable references across exports

**Defer this** until we actually need it (multiple lessons with similar content, or lesson rewrites). UUID works fine for now.

## Implementation Priority (spike order)

| # | Spike | Why first | Effort |
|---|-------|-----------|--------|
| 1 | **039 — Markdown prompts** | No schema change, just `pip install rich` + upgrade renderer. Biggest bang for effort. | 1hr |
| 2 | **037 — Code block cards** | Adds `prompt_code` field + Syntax rendering. Natural extension of markdown support. | 2hr |
| 3 | **038 — Diagram references** | Lowest value — text prompts usually suffice. Only matters for visual-spatial concepts. | 1hr |

## Proposed mise/dependency changes

```toml
# mise.toml [tasks.setup]
run = "uv pip install drawsvg playwright graphviz rich"
```

## Proposed skill changes

**teach skill** — when generating code-heavy SR questions (e.g., SQL queries, API calls), use fenced code blocks in expected_answer:

````markdown
Expected answer includes inline code:
The `OPTIMIZE` command rewrites manifest files to merge small ones.

Or a full code block:
```sql
ALTER TABLE iceberg_table SET TBLPROPERTIES ('optimize_rewrite_data_file_group_size' = '268435456');
```
````

**quiz-me skill** — when presenting cards with code, wrap in a code fence so the terminal renderer picks it up.

## Repos to keep in .references/

| Repo | Why keep |
|------|---------|
| `repeater` | Content model, meaning-hash pattern, cloze masking, markdown parsing |
| `rich` (examples only) | API reference for Panel/Markdown/Syntax/Console patterns |
| `cert-pepper` | MCP integration pattern (future), AI explanation caching |
