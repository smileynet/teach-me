---
id: "197"
title: "Spike: test godot-ink (C#/.NET) as alternative ink runtime"
status: backlog
blocked_by: ["193"]
priority: low
type: spike
tags: [ink]
---

# Spike: test godot-ink (C#/.NET) as alternative ink runtime

## Context

The ink+Godot lesson track (#193) uses inkgd (pure GDScript, godot4 branch) to avoid requiring .NET Godot. Once the lesson content is complete and validated, we should test the paulloz/godot-ink addon (C# wrapper around official ink-engine-runtime) as an alternative for:

1. **Performance** — native C# runtime vs GDScript port (matters at scale: 100+ stories)
2. **Maintenance** — godot-ink is actively released; inkgd godot4 branch is unreleased
3. **C# lesson remix** — feeds into #194 (C# variant of the same lessons)

## What to do

1. Download Godot 4.7.x .NET build (portable zip to `D:\tools\godot-4.7.1-dotnet\`)
2. Install .NET SDK 8.0+ if not present
3. Create a parallel `ink-test-project-dotnet/` with godot-ink installed
4. Port the spike scene from inkgd → godot-ink API
5. Compare: API ergonomics, GDScript interop quality, editor integration, compilation speed
6. Document tradeoffs for future reference

## Prerequisites

- .NET SDK 8.0+
- Godot .NET build (separate from standard Godot on PATH)
- mise.toml env override for project-specific Godot binary (see research at `.scratch/subagent-raw/research-mise-godot.md`)

## Acceptance criteria

- [ ] godot-ink addon running in Godot 4.7.x .NET
- [ ] Same ink story loads and runs via GDScript interop
- [ ] Comparison document: inkgd vs godot-ink (API, performance, DX, maintenance)
- [ ] Recommendation: stick with inkgd or migrate
