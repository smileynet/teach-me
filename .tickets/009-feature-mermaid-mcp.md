---
id: "009"
title: "Feature: Mermaid MCP agent configuration"
status: done
priority: low
blocked_by: ["005"]
type: feature
tags: [platform]
---

# Feature: Mermaid MCP agent configuration

## Resolution: WON'T DO

Deep dive (2026-08-07) concluded Mermaid MCP is not worth adding:
- Puppeteer-based rendering pipeline requires ~300MB Chrome dependency
- Our inline SVG approach (draw-diagram.py + D2) produces 2-3KB diagrams with zero network dependency
- The local mermaid-mcp (fay-i) stores artifacts on disk rather than returning inline SVG strings
- If we ever need Mermaid syntax, D2 covers the same diagram types with simpler syntax and faster rendering
