---
id: "005"
title: "Add Mermaid Chart MCP server to agent config"
status: open
priority: low
blocked_by: []
---

# Add Mermaid Chart MCP server to agent config

## What to build

Configure the official Mermaid Chart MCP server as an optional visualization tool for the teach agent. This gives the agent `render_diagram` and `validate_diagram` tools for iterative diagram creation.

## Implementation

Create `.kiro/agents/teach-agent.json`:
```json
{
  "name": "teach-agent",
  "description": "Teaching agent with diagram rendering capability",
  "tools": ["@builtin", "@mermaid"],
  "mcpServers": {
    "mermaid": {
      "url": "https://mcp.mermaid.ai/mcp"
    }
  },
  "resources": [
    "file://MISSION.md",
    "file://RESOURCES.md",
    "file://NOTES.md",
    "file://learning-records/*.md",
    "file://assets/svg-patterns.md",
    "skill://.kiro/skills/**/SKILL.md"
  ]
}
```

## Acceptance criteria

- [ ] Agent config validates (`kiro-cli agent validate`)
- [ ] Mermaid MCP connects and exposes tools
- [ ] Agent can render a simple Mermaid diagram via the MCP tool
- [ ] Fallback works when MCP is unavailable (inline SVG still works)
