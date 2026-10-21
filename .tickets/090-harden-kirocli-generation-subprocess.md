---
id: "090"
title: "Spike: harden kiro-cli generation subprocess (checkpoint stall)"
status: open
blocked_by: []
priority: high
validation_criteria:
  - "Fresh worktree: serve.py spawns kiro-cli generation and it completes (writes a file) without hanging — no manual checkpoint toggle needed"
  - "serve.py no longer swallows the 'Checkpoint operation failed' line; the stall (if any) surfaces in the SSE stream"
  - "Documented: whether EDITOR=true/GIT_EDITOR=true env fix works vs requiring chat.enableCheckpoint=false; chosen approach applied in serve.py"
  - "Reproducer from research 063 (.scratch/063-maptest/gen.sh) runs to a valid MAP.md with the checkpoint setting left at its default (true)"
---

# Spike: harden kiro-cli generation subprocess (checkpoint stall)

## What to build

TBD

## Acceptance criteria

- [ ] TBD
