---
id: "194"
title: "C# ink lesson remix (tests remix feature)"
status: backlog
blocked_by: ["193", "160"]
priority: low
type: feature
tags: [ink]
---

# C# ink lesson remix (tests remix feature)

## Context

The ink+Godot lesson track (#193) teaches integration using GDScript (via godot-ink's interop layer). A C# remix of the same lessons would:

1. **Test the lesson remix feature** (#160) — the first real use case for generating alternative-language versions of existing lessons
2. **Serve learners** who use Godot's .NET build and prefer C# (godot-ink's primary API)
3. **Show the same architecture patterns** in a different language, reinforcing the concepts

## What to build

Remix lessons 05–08 (Phase B: Godot integration) from GDScript to C#:
- Same teaching arc, same win statements, same exercises
- Different code blocks (C# syntax, direct godot-ink API instead of interop)
- Different setup steps (.NET Godot project, NuGet packages)
- MAP shows the remix relationship (variant/alternative, not prerequisite)

Phase A (01–04) is pure ink — no engine code, no remix needed.

## Acceptance criteria

- [ ] #160 (topic remixes) feature is implemented
- [ ] Lessons 05–08 have C# variants generated via the remix pipeline
- [ ] C# variants compile and run in a .NET Godot test project
- [ ] MAP.md represents the remix relationship correctly
- [ ] Existing GDScript lessons are unchanged (additive, not replacement)

## Why this is a good remix test case

- Same architecture, different syntax — the "pure language swap" remix type
- godot-ink's C# API is richer than the GDScript interop (more methods, better typing)
- The differences are substantive (not just syntax coloring) — C# has async/await, stronger typing, direct InkStory access
- Tests whether the remix feature can handle "same concept, materially different code"
