---
id: "201"
title: "Index WritingWithInk.md in knowledge base"
status: open
blocked_by: []
priority: high
type: feature
---

# Index WritingWithInk.md in knowledge base

## Context

`.references/ink/Documentation/WritingWithInk.md` is the 124KB authoritative ink tutorial (6 parts, 30+ sections). Indexing it means lesson generation can cite exact official passages instead of relying on web search — same source-authority benefit as the Godot class reference XML.

## What to do

1. Add `WritingWithInk.md` and `RunningYourInk.md` to the knowledge base
2. Verify search returns relevant chunks for queries like "ink choices once-only sticky", "ink gather weave", "ink external functions"
3. Optionally index `ink_JSON_runtime_format.md` (useful for Phase B lessons)

## Acceptance criteria

- [ ] `WritingWithInk.md` indexed and searchable
- [ ] `RunningYourInk.md` indexed and searchable  
- [ ] Search for "ink gather" returns the weave/gather section
- [ ] Search for "ink external function" returns the game-side hooks section
