---
id: "201"
title: "Build portable ink reference from official docs"
status: done
blocked_by: []
priority: high
type: feature
---

# Build portable ink reference from official docs

## Context

`.references/ink/Documentation/WritingWithInk.md` is the 124KB authoritative ink tutorial (6 parts, 30+ sections). We need it searchable for lesson generation — but via a portable, client-agnostic approach (not locked to kiro-cli's knowledge tool).

Following the proven godot-knowledge pattern: split large docs into per-section files with frontmatter + intent preambles → commit to `.memory/ink-reference/` → import to recall wing.

## Research Findings (2026-08-25)

### godot-knowledge patterns (proven at scale: 992 classes, 67 cards, 256 guides)
- **#1 lesson: one file per topic** maximizes retrieval precision
- Heading-based splitting via stdlib Python script (no pip deps)
- Strict frontmatter contract: `type`, `slug`, `tags` enable filtering
- Intent preambles ("developers search for this when: ...") boost semantic recall
- Tab-indented code must be converted to fenced blocks for reliable chunking
- Output committed to git — self-contained, works with any tool

### WritingWithInk.md structure (3,454 lines)
- 6 Parts, 30 H2 sections, 75 H3, 58 H4
- **41% tab-indented code** (ink's example format: code → "produces:" → output)
- Wildly varying section sizes (Part 5 is 500-800+ lines; basic sections are 50-100)
- Only 2 fenced code blocks in entire file — everything is tab-indented

### Other docs
- RunningYourInk.md (454 lines, 14 H2 sections, 44 fenced csharp blocks) — copy as-is with frontmatter
- ink_JSON_runtime_format.md (255 lines, 12 H2 sections) — copy as-is with frontmatter
- ArchitectureAndDevOverview.md (small) — copy as-is with frontmatter

### Prior art
- Algolia DocSearch MCP already indexes ink docs at concept-level granularity — validates approach
- sawradip/ink-cheat-sheet (cloned to `.references/`) — symbol-indexed reference tables
- GoldenXP ink docs — use-case organized, covers gaps (testing, Godot integration)

## Implementation

### `tools/split-ink-docs.py`

Stdlib-only Python script. No pip deps. Idempotent.

**Input:** `.references/ink/Documentation/`
**Output:** `.memory/ink-reference/`

**For WritingWithInk.md:**
1. Split at `##` boundaries → one file per section (~30 files)
2. Add frontmatter: `type: ink-reference`, `part: N`, `section: title`, `tags: [relevant-terms]`
3. Add intent preamble: `<!-- search: developers look for this when ... -->`
4. Convert tab-indented examples → fenced ```ink blocks
5. Keep "produces:" output blocks as fenced ```text
6. Filename: `{part}-{NN}-{slug}.md` (e.g., `1-03-knots.md`)

**For smaller docs (RunningYourInk, JSON format, Architecture):**
- Copy as-is, prepend frontmatter only
- Already use fenced code blocks — no conversion needed

### Import

```bash
recall import .memory/ink-reference/ --wing ink_reference
```

### Portability

- Any agent can `read .memory/ink-reference/{file}.md` directly (no search needed)
- recall provides semantic search for conceptual queries
- grep/ripgrep works for exact text lookup
- Future: optional FTS5 index if needed

## Acceptance criteria

- [x] `tools/split-ink-docs.py` exists, stdlib-only, runs without errors
- [x] `.memory/ink-reference/` contains ~33 files (30 from WritingWithInk + 3 smaller docs)
- [x] Every file has valid frontmatter (type, part/section, tags)
- [x] Tab-indented code in WritingWithInk converted to fenced `ink` blocks
- [x] `recall search "ink gather weave"` returns Part 2 gather content
- [x] `recall search "ink external function"` returns RunningYourInk game-side hooks
- [x] `recall search "ink sticky choices"` returns Part 1§7 varying choices
- [x] `recall search "ink tunnel return"` returns Part 4§1 tunnel mechanics
