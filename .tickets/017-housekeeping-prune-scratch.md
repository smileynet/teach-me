---
id: "017"
title: "Housekeeping: prune .scratch/ after integration"
status: done
priority: low
blocked_by: ["013", "014", "015", "016"]
type: feature
tags: [platform]
---

# Housekeeping: prune .scratch/ after integration

## What to do

Once tickets 013-016 are complete (findings integrated into guidance), delete the raw research files in `.scratch/research/` and `.scratch/subagent-raw/`. The useful content will be in steering, skills, and tools — the raw files served their purpose.

## Files to evaluate for deletion

- `.scratch/research/*.md` (23 files)
- `.scratch/subagent-raw/*.md` (7 files)
- `.scratch/spike-results/` (1 file)
- `.scratch/browse-test/` (2 files)

Keep only:
- `.scratch/reference-extraction-mattpocock-skills.md` — ongoing reference for Matt's skill patterns

## Acceptance criteria

- [x] All actionable findings captured in steering/skills/tools
- [x] Scratch files deleted (they're gitignored anyway, but clean workspace)
- [x] No knowledge lost — anything durable is in `.memory/` or guidance files
