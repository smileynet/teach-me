---
id: "039"
title: "Spike: markdown prompts — store as markdown, render everywhere"
status: open
priority: medium
blocked_by: ["034"]
type: spike
---

# Spike: markdown prompts — store as markdown, render everywhere

## Question to answer

Should we store card prompts and answers as markdown (with inline code, bold, links) instead of plain text, and render them appropriately in each context?

## What to try

1. Write 3-5 test cards with markdown formatting:
   - Inline code: "Explain what `OPTIMIZE` does to manifest files"
   - Bold emphasis: "Why is **snapshot isolation** critical for concurrent writes?"
   - Code fence: multi-line code in expected_answer
2. In terminal: render via `rich.markdown.Markdown` (subset: bold, code, lists, headers)
3. In HTML: render via `marked.js` or server-side `markdown-it`
4. Evaluate: does markdown add clarity, or is it noise for explain-to-colleague questions?

## Key decision

Most of our prompts are conversational ("Explain to a colleague why..."). Markdown formatting may not add much for this style. But expected_answers often benefit from structure (lists of key points, inline code for technical terms).

Consider: **prompts stay plain text, answers get markdown**. Simpler, and the answer is where structure helps most.

## Success criteria

- [ ] Rich renders markdown prompts/answers readably in terminal
- [ ] HTML path renders the same content correctly
- [ ] Evaluate: markdown in prompts — helpful or noisy?
- [ ] Evaluate: markdown in answers only — is this the sweet spot?
- [ ] Backward compatible (plain text cards render unchanged)

## Time box

1.5 hours. Focus on the evaluation question, not just the technical feasibility.
