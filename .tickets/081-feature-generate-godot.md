---
id: "081"
title: "Feature: generate godot-gamedev example — 2 topics + quizzes"
status: done
priority: high
blocked_by: []
type: feature
---

# Feature: generate godot-gamedev topics

## What to do

Generate 2 topics for the godot-gamedev example workspace (currently has MAP.md with 8 topics, none generated).

### Steps
1. Review existing MISSION.md and MAP.md (nodes-and-scenes is marked complete, gdscript-fundamentals in-progress)
2. Generate 2 topic lessons: "Nodes, Scenes & the Scene Tree" + "GDScript Fundamentals"
3. Generate quiz pages for both
4. Mark generated topics with correct status in MAP.md
5. Verify structure matches the workspace pattern

### Expected result
```
examples/godot-gamedev/
  MISSION.md (exists)
  maps/godot-gamedev.MAP.md (exists)
  lessons/0001-nodes-and-scenes.html (new)
  lessons/0002-gdscript-fundamentals.html (new)
  lessons/quiz/*-quiz.html (new)
  learning-records/questions/*.jsonl (new)
  reference/*.html (new)
```

## Validation

- `mise run verify` passes
- Playwright: lessons load, quiz pages have questions, nav works

## Resolution (2026-08-12)

TBD
