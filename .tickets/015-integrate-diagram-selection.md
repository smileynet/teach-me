---
id: "015"
title: "Integrate: update diagram selection table with current tools"
status: done
priority: medium
blocked_by: []
type: feature
tags: [platform]
---

# Integrate: update diagram selection table with current tools

## What's stale

`.kiro/steering/visual-teaching.md` diagram selection table still references "Mermaid sequence" and "Mermaid flowchart/state diagram" — but we've decided against Mermaid MCP (ticket 009: won't do) and our primary tools are now:

1. `draw-diagram.py` (stack, flow, hub, graph)
2. D2 CLI (auto-layout, complex diagrams)
3. Raw inline SVG (custom/annotated)
4. Graphviz backend (stretch, ticket 010)

## What to update

1. **`.kiro/steering/visual-teaching.md`** — rewrite Diagram Selection table to match actual available tools
2. **Update references** from "Mermaid" to "D2" where appropriate
3. **Add the `graph` type** (fan-out/fan-in) to the selection guide
4. **Add progressive reveal** as a technique in the Implementation section

## Acceptance criteria

- [x] Diagram selection table matches available tools (no Mermaid references)
- [x] Progressive reveal documented in steering
- [x] Graph type mentioned for fan-out/fan-in use cases
