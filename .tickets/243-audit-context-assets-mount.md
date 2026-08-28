---
id: "243"
title: "Document /assets project-root mount for subagent auditors (avoid false dead-link findings)"
status: backlog
blocked_by: []
priority: low
tags: ["platform"]
---

# Document /assets project-root mount for subagent auditors (avoid false dead-link findings)

## Why

During the #219 audit, an independent subagent flagged the lesson's 3 figure images as
"dead links" because it looked for them under `examples/godot-gamedev/assets/img/`. They
actually live at **project-root** `assets/img/` and are served via the `/assets` mount
(serve.py mounts `PROJECT_ROOT/assets` at `/assets`; lessons reference `../../assets/...`).
The finding was a false positive caused by the auditor not knowing the mount. This costs
a round-trip every audit and risks a real finding being dismissed as "probably the mount
thing again."

## What to do

Make the `/assets` project-root mount explicit where auditors and agents will see it:
- Add a one-line note to any lesson/audit subagent context template (e.g. the
  `.scratch/subagent-input/*-audit.md` pattern, or the lesson-validation skill) stating:
  "Lesson `../../assets/...` paths resolve to PROJECT-ROOT `assets/`, served at `/assets`
  by serve.py — NOT to a per-workspace assets dir."
- Confirm AGENTS.md's serve.py note already covers this for humans; if not, add it.

Low effort, prevents a recurring false positive.

## Acceptance criteria

- [ ] The /assets project-root mount is documented where lesson-audit subagents receive context
- [ ] A re-run of a lesson audit does not re-raise figure images as dead links
- [ ] AGENTS.md serve.py guidance mentions the /assets project-root mount (verify or add)
