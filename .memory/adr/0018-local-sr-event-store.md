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

## Contention note (2026-09-17, #365)

As first shipped, the predecessor read (`card_projection.last_event_id`) and the event
derivation happened BEFORE `BEGIN IMMEDIATE`, so two concurrent writers could derive
from the same predecessor. The events FK does not catch this — a stale predecessor is
still a valid event id — so both writes committed and silently forked the chain;
rebuild then failed permanently with "missing or out-of-order predecessor". A
connect-time `INSERT OR IGNORE` also held a stray read transaction that blocked other
writers' commits.

Remedied: the write transaction is now acquired BEFORE the projection read, the
reviewed result is derived inside the transaction from the projected state (matching
the replay contract in `_apply_event`), connect-time DML is gone (DDL only), writers
use an explicit busy timeout with bounded retry, and exhaustion surfaces a retryable
`EventStoreError` — never a raw `sqlite3.OperationalError`. Regression coverage:
`tools/test_sr_event_serialization.py` (same-card thread + cross-process contention,
different-card preservation, prolonged-lock retryable conflict). WAL was deliberately
NOT enabled: the store is tiny, CLI-only, and single-machine; rollback journal +
IMMEDIATE serialization is sufficient without adding `-wal`/`-shm` sidecars.
