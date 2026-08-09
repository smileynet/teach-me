---
id: "034"
title: "Feature: support media and rich content in SR card prompts"
status: open
priority: low
blocked_by: []
type: feature
---

# Feature: support media and rich content in SR card prompts

## What to build

Allow SR cards to include diagrams, code blocks, and formatted text in prompts and expected answers — not just plain strings.

## Why

Many concepts are best tested visually ("annotate this diagram") or with code ("what's wrong with this query?"). Plain-text-only cards miss these modalities.

## Design sketch

Extend the Card schema to support rich content:

```json
{
  "prompt": "What layer is missing from this diagram?",
  "prompt_media": {
    "type": "svg_ref",
    "path": "lessons/0001-iceberg-metadata-tree.html#diagram-aws-layers"
  },
  "expected_answer": "The manifest list layer — it sits between metadata files and manifests.",
  "answer_media": null
}
```

Media types:
- `svg_ref` — reference to an SVG in a lesson (render during review)
- `code_block` — syntax-highlighted code snippet
- `markdown` — formatted text with inline code, bold, links

Review CLI would need to:
- Render code blocks with syntax highlighting (via `rich` library)
- Reference diagrams by pointing to the lesson URL
- Fall back to plain text if terminal doesn't support rich output

## Open questions

- How to render SVGs in terminal? Just show the lesson URL?
- Should code blocks be inline in the JSONL or referenced by path?
- Does the `rich` library add too much dependency weight?
- For agent-driven review (quiz-me skill), the agent can render anything — is CLI rendering even needed?

## Acceptance criteria

- [ ] Card schema supports `prompt_media` and `answer_media` fields
- [ ] At least code blocks render in terminal review (via rich or similar)
- [ ] SVG references show as clickable lesson links in terminal
- [ ] quiz-me skill can render rich content when presenting cards
- [ ] Backward compatible — plain-text cards still work unchanged
