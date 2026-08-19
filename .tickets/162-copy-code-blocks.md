---
id: "162"
title: "Copy button on code blocks"
status: open
blocked_by: ["173"]
parent: "173"
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

- [ ] Design decision documented (placement, scope, diff handling)
- [ ] Working prototype on at least one lesson page
- [ ] Works with both regular code blocks and diff-style blocks
- [ ] Accessible (keyboard operable, labeled, feedback announced)
- [ ] No visual clutter on mobile (small screens)
- [ ] Uses existing CSS variables for theming
