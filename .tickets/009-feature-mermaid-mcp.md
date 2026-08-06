---
id: "009"
title: "Feature: Mermaid MCP agent configuration"
status: open
priority: low
blocked_by: ["005"]
type: feature
---

# Feature: Mermaid MCP agent configuration

## What to build

Add the official Mermaid Chart MCP server to a kiro-cli agent config for iterative diagram rendering. Only proceed if research (ticket 005) confirms viability.

## Implementation (proposed)

Create `.kiro/agents/teach-visual.json` with Mermaid MCP configured.

## Acceptance criteria

- [ ] Agent config validates
- [ ] Mermaid MCP connects and exposes render/validate tools
- [ ] Agent can render a Mermaid diagram via MCP
- [ ] Fallback works when MCP is unavailable
