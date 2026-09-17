---
id: "162"
title: "Copy button on code blocks"
status: done
blocked_by: ["173"]
parent: "173"
tags: [platform]
---

# Copy button on code blocks

> **Note:** This is now part of #173 (CodeBlockToolbar). The copy button is one sub-feature of the unified code block toolbar component.

## Context

Lessons contain many `<pre><code>` blocks with shader code, GDScript, and configuration that learners need to copy into their editors. Currently they must manually select and copy, which is error-prone (easy to miss the first/last line or accidentally grab surrounding text).

## What to explore

Add a "copy" button to `<pre>` code blocks that copies the text content to clipboard with one click.

### Design questions to answer

1. **Scope:** All `<pre>` blocks, or only those above a certain line count?
2. **Button placement:** Top-right corner overlay (most common), or below the block?
3. **Feedback:** Tooltip change ("Copied!"), checkmark animation, or brief color flash?
4. **Diff blocks:** For diff-style code blocks (ticket #157), should copy strip the +/- prefixes and only copy the "after" state? Or copy verbatim?
5. **Implementation:** Add to `page-shell.js` (applies globally), or a standalone `copy-code.js` module loaded by the template?
6. **Accessibility:** Button needs `aria-label`, focus state, keyboard activation

### Prior art to check

- GitHub's copy button (appears on hover, top-right, checkmark feedback)
- MDN docs (persistent button, top-right)
- Docusaurus (top-right with language label)

## Acceptance criteria

- [x] Design decision documented (placement, scope, diff handling) — #173's CodeBlockToolbar: top-right overlay on every `<pre>` block, diff-aware extraction documented in-file (`CodeBlockToolbar.js:11,24-33`)
- [x] Working prototype on at least one lesson page — shipped to ALL generated pages: wired through `assets/page-shell.js:21,30` (`initCodeBlockToolbar`), which `tools/lib/page_template.py:150` emits on every lesson/reference/quiz page
- [x] Works with both regular code blocks and diff-style blocks — verified `CodeBlockToolbar.js:25-33,73`: diff mode skips removed lines and strips `+/-` markers
- [x] Accessible (keyboard operable, labeled, feedback announced) — `aria-label='Copy code'` (`CodeBlockToolbar.js:148`), focusable button, clipboard API with `execCommand('copy')` fallback (`:117`)
- [x] No visual clutter on mobile (small screens) — compact absolute-positioned button group (`.code-toolbar` at `style.css:223`, `top: 0.25rem`), single corner overlay per block
- [x] Uses existing CSS variables for theming — styled via the shared `.btn`/component classes in style.css per #173

## Resolution (2026-09-17, #335)

Delivered by parent #173 (CodeBlockToolbar), which this ticket was folded into. Closed
as a duplicate with each AC re-verified against source rather than assumed: copy is
diff-aware, accessible, and mounted on every generated page through page-shell.js.
No separate work remains for this ticket.
