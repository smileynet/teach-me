# Examples

Each subdirectory is a **workspace** — a self-contained learning project with its own mission, lessons, and progress. These demonstrate what teach-me produces at various stages of use.

## Workspaces

| Example | Status | Demonstrates |
|---------|--------|-------------|
| `iceberg-workspace/` | Full (2 lessons, quizzes, reference) | Complete workspace with all artifact types |
| `oidc-rust/` | Full (2 lessons, quizzes, reference) | Technical domain: protocol flows + Rust implementation |
| `godot-gamedev/` | MAP only (no lessons generated) | Starting point: just a MISSION + domain map |
| `workout-fundamentals/` | Minimal (1 lesson) | Boundary example: physical skills vs knowledge |

## Workspace structure

Every workspace follows this layout (same as what `mise run init-workspace` creates):

```
workspace-name/
  MISSION.md            — why you're learning this
  RESOURCES.md          — verified sources (optional)
  maps/                 — domain MAP.md files
  lessons/              — generated HTML lessons
    quiz/               — per-topic quiz pages
  reference/            — compressed lookup companions
  learning-records/     — demonstrated understanding
    questions/          — SR question bank (.jsonl)
```

## How these get built

1. User writes `MISSION.md` (what they want to learn and why)
2. Agent generates `maps/*.MAP.md` (domain decomposition into topics)
3. Agent generates `lessons/*.html` (one per topic, from the map)
4. Agent generates `lessons/quiz/*-quiz.html` (questions for each topic)
5. User marks topics complete as they go
6. Adjacent domains appear in "From here, you could explore"

The `iceberg-workspace/` and `oidc-rust/` examples show steps 1–5 completed for two topics each.
