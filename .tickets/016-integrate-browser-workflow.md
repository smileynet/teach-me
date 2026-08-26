---
id: "016"
title: "Integrate: browser agent workflow documentation"
status: done
priority: low
blocked_by: []
type: feature
tags: [platform]
---

# Integrate: browser agent workflow documentation

## Source findings

`.scratch/research/playwright-agent-patterns.md` + `.scratch/subagent-raw/playwright-mcp-deep-dive.md`

Key findings NOT yet fully integrated:

### Workflow patterns for our use case
- `browser_navigate` → `browser_find` (search for heading) → `browser_snapshot` (read section) is the canonical 3-step flow
- `browser_evaluate` can verify `document.getElementById('anchor')` directly
- Accessibility snapshots give `[ref=eN]` tags — but we don't need interaction, just reading

### Timeout tuning
- 15s navigation timeout (default 60s is too generous for docs pages)
- 300ms settle (default 500ms unnecessary for static docs)

### Lightweight fallback decision tree
- Static HTML docs (most of our sources) → `web_fetch` with `search_terms` is faster
- JS-rendered pages (some AWS docs) → Playwright needed
- The browser agent should try `web_fetch` first, escalate to Playwright only if content is empty/minimal

## What to update

1. **`.kiro/skills/browse-and-verify/SKILL.md`** — add the 3-step workflow pattern explicitly
2. **`.kiro/agents/browser.json`** — consider if we should document the fallback escalation pattern in the prompt
3. **AGENTS.md** — no changes needed (already mentions browser dispatch)

## Acceptance criteria

- [x] Browse skill documents the navigate→find→snapshot workflow
- [x] Fallback escalation (web_fetch first, Playwright if empty) documented
