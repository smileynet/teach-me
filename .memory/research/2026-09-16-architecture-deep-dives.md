---
date: 2026-09-16
scope: architecture deep dives
status: partial-complete
---

# Architecture deep dives: durable conclusions

## Summary

The project has a sound intended split between committed teaching content and local learner state, but several observable implementations still cross that boundary. The highest-priority sequence is: establish an exact local workspace/map context (#332/#339), enforce local-only progress (#341), make overlay writes safe (#353), then separate SR definitions from learner state (#349). Curriculum and visual verification also found user-visible failures (#363/#364).

## Findings

### Learner state and spaced repetition

- [L1:verified] `tools/questions.py` stores shared card definitions beside mutable schedules and can fall back to committed `learning-records/`; an empty private store can also hide public definitions. This contradicts [ADR 0012](../adr/0012-public-library-private-overlay.md) and ticket #255. Tickets #349–#352 specify the repair.
- [L1:verified] Current review logs are telemetry, not replayable canonical history: they omit stable full IDs, lifecycle events, scheduler version, and sufficient projection state. The current SM-2 arithmetic matches its published shape, but analytics label an uncalibrated exponential heuristic as knowledge. Tickets #350 and #352 own these concerns.

### Local server and trust boundaries

- [L1:verified] Loopback traversal and raw `.user` state-read probes were clean. A repeated 100-update concurrent-overlay probe lost records, however; malformed JSON can create an oversized reflected response; glob-based domain selection is ambiguous; and `--lan` exposes unauthenticated status mutation. Tickets #353–#355 capture the repairs and policy decision.

### Reproducibility and provenance

- [L1:verified] Eleven MAP-to-HTML outputs were byte-identical across two runs; index drift checks and representative timezone/locale probes were stable. Lessons, MAP source, and question banks are authored inputs, not generated projections.
- [L1:verified] The site dry run remains blocked by tracked Windows text stubs, already covered by #331. Tickets #356–#358 add a non-destructive drift manifest, asset lineage, and citation-coverage validation.

### Skills, curriculum, and environment consistency

- [L1:verified] All 13 project skills received positive/negative probes. The documented Ink validation skill does not exist, `teach` and `generate-topic` lack a consistent ownership boundary, and learner-dialog skills reference tracked-looking state paths. Tickets #359–#362 capture the targeted fixes; broad skill consolidation was rejected.
- [L1:verified] `check-lesson.py --all` found navigation, quick-check, glossary, exercise, credits, read-time, and visual-token failures across shipped domains. `mise run visual-qa` fails for the lessons index because only 13/22 SVGs have non-zero rendered dimensions. Tickets #363 and #364 own these user-facing repairs.
- [L1:verified] The capability matrix is consistent only in parts: local static reading works, while library-root status/map behavior is split-brain (#332/#338), Pages remains blocked by #331, and LAN needs a policy decision (#355). The local-only progress boundary is not yet true for SR (#349/#341).

## Sources

- [L1:verified] `tools/questions.py`, `tools/sm2.py`, `tools/sr-*.py`, `tools/serve.py`, `tools/lib/overlay.py`, `tools/check-lesson.py`, and `mise.toml` — observed implementation and command behavior.
- [L2:verified] [ADR 0012](../adr/0012-public-library-private-overlay.md), [ADR 0015](../adr/0015-unified-library-root.md), tickets #255, #331, #332, #338, and #341 — governing plans and stated architecture.
- [L4:verified] [SuperMemo SM-2](https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method), [Anki documentation](https://docs.ankiweb.net/), and [FSRS documentation](https://github.com/open-spaced-repetition/fsrs4anki/wiki) — scheduler and portable-review-state reference material.

## Follow-up map

- Foundation: #331, #332, #339, #341.
- Security and persistence: #353, #354, #355.
- SR architecture: #349, #350, #351, #352.
- Provenance: #356, #357, #358.
- Skill contract: #359, #360, #361, #362.
- Learner-facing content and visuals: #363, #364.

## Coverage limits

The SR, server-security, and skill reviews are complete. The reproducibility review is blocked on #331's deploy gate. Lesson-quality and capability-matrix reviews have confirmed mechanical/runtime defects, but still need dedicated browser/device and judgment-based citation/support sampling before their research tickets can close.
