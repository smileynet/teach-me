---
id: "372"
title: "Scope creds-agent MCP access away from every default agent session"
status: done
blocked_by: []
priority: high
type: review
tags: ["security", "agents", "risk-review"]
validation_criteria:
  - "Credential-tool availability per agent is a documented, deliberate decision, and every committed agent config works on a machine without the aim binary"
---

# Scope creds-agent MCP access away from every default agent session

## Intent

Make the credential-agent MCP grant an explicit, documented, minimal scope instead of a blanket default.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

Commit `03e9d77` ("wire creds-agent MCP server into default, browser, godot_editor") added to
`.kiro/agents/default.json` — which previously declared NO MCP servers at all:

```json
"tools": ["@builtin", "@creds-agent"],
"mcpServers": { "creds-agent": { "command": "aim", "args": ["mcp", "start-server", "local-creds-agent-mcp"] } },
"allowedTools": ["@creds-agent"]
```

The same server entry was added to `browser.json` and `godot_editor.json`. Consequences:

1. **Blast radius**: every routine default-agent session (lesson authoring, teaching, content
   generation) now carries tools named to serve credentials. Whether that is an actual exposure
   depends on what `aim`'s `local-creds-agent-mcp` serves (scope, auth, which secrets) — that is
   NOT verifiable from repository facts: `creds-agent`/`aim` appear nowhere else in the repo
   except one unrelated research doc. The severity must be established, not assumed.
2. **Portability**: `aim` is a machine-local binary not provided by `mise run setup`. On any
   clone without it, all three committed agent configs declare a failing MCP server. Cross-platform
   failure behavior is agent-runner-dependent (also not verifiable from the repo).

Secondary: the rewrite dropped trailing newlines from all three JSON files.

## What to build

Decide and document the intended scope: either remove `@creds-agent` from the default agent
(keep it only on specialists that demonstrably need credentials), or record an ADR naming why
the default session needs it. Make the `aim` dependency explicit (setup docs or graceful
absence) so committed agent configs don't reference a binary the project doesn't provision.

## Acceptance criteria

- [x] Each of default/browser/godot_editor either drops `@creds-agent` or carries a written justification (ADR or AGENTS.md note) naming what it is for — default DROPS it (restored to pre-`03e9d77` shape: no `mcpServers`, no `allowedTools`, `tools: ["@builtin"]`); browser/godot_editor KEEP it, justified in AGENTS.md Environment → "Agent MCP scoping (#372)" (authenticated URL validation; local editor tooling)
- [x] What `local-creds-agent-mcp` exposes (which credentials, to whom) is written down; if it cannot be established, the server is removed from the default agent — it could NOT be established from repository facts (the exposure question is stated verbatim in this ticket's Context), so the default-agent removal branch fired; the AGENTS.md note records what IS known (machine-local `aim` binary, specialist-only scope)
- [x] A fresh clone without `aim` on PATH has no agent whose declared MCP servers hard-fail at session start (or the failure is documented as expected) — documented as expected: the AGENTS.md note states the two specialists' creds-agent server fails to start without `aim` while everything else works; the default agent (the every-session path) now declares zero MCP servers
- [x] Trailing newlines restored on the three rewritten `.kiro/agents/*.json` files — yes (all three re-validated as parseable JSON after the edit)

## Resolution (2026-09-18)

Removed the `creds-agent` MCP server, `@creds-agent` tool, and `allowedTools` entry from
`.kiro/agents/default.json`, restoring its pre-`03e9d77` shape — routine teaching/content
sessions no longer carry credential tools (biggest blast radius, no demonstrated need).
`browser.json` and `godot_editor.json` keep the wiring, now justified in AGENTS.md
(Environment → "Agent MCP scoping (#372)"), which also documents the `aim` dependency and
its absent-binary failure mode. Trailing newlines restored on all three files; all three
re-validated as parseable JSON (`json.load` smoke). Ticket #372.

## References

- Commit `03e9d77` (2026-09-17), diff of `.kiro/agents/default.json`
- Related design: `#234` (godot_ai MCP authoring tooling, local-only convention)
