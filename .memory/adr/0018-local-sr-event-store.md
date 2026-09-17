# ADR-0018: Local SQLite SR event store

**Status:** accepted
**Date:** 2026-09-17
**Deciders:** teach-me maintainers

## Context

Shared card definitions must remain publishable and free of learner progress. The
previous private JSON state plus JSONL review telemetry had a crash window between
updating the projection and appending the record, while lifecycle changes had no
history at all. Ticket #350 requires versioned, replayable local progress.

## Decision

Keep card definitions as committed JSONL and store learner events plus their
rebuildable schedule/lifecycle projection in `.user/learning-records/sr-events.sqlite3`.
Each review or lifecycle transition records its immutable event and projection update
in one SQLite transaction. The database is local-only and gitignored.

## Consequences

### Positive

- A learner action is all-or-nothing, with a canonical event ID and ordering.
- The derived projection can be discarded and rebuilt without changing shared cards.
- SQLite constraints reject duplicate event IDs and missing predecessor events.

### Negative

- Progress is binary rather than line-oriented; backups need SQLite-aware handling.
- Event schema and scheduler versions are now durable compatibility contracts.

### Neutral

- Existing `card-state.json` is imported into snapshot events when enough state
  exists; the old private files remain untouched for audit. Prefix-ID history without
  a state snapshot produces an explicit unsupported-version diagnostic.
- The status overlay remains JSON because it is a tiny replaceable document. Its
  separate contract is a retained OS-backed lock around read-modify-write plus a
  same-directory, fsynced `os.replace`; SQLite supplies those guarantees internally
  for the higher-volume SR event stream.

## Alternatives Considered

### JSONL event log plus JSON projection

- Pros: human-readable and close to the earlier layout.
- Cons: requires custom cross-file atomicity, recovery, deduplication, and locking.
- Why rejected: it adds more persistence machinery than SQLite's standard-library
  transaction model for a single-machine learner store.

### Replay events for every command

- Pros: a single persisted representation.
- Cons: status, analytics, and review commands slow as history grows.
- Why rejected: a disposable projection gives the same authority boundary without
  repeated replay on normal reads.

## References

- `.tickets/350-sr-event-projection.md`
- `.scratch/research/350-sr-event-patterns.md`
- [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html)
