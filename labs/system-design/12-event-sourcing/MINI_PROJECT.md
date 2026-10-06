# Event Sourcing - MINI PROJECT

## Project: A Ledger That Rebuilds Itself

**Time**: 14-18 hours

**Goal**: Build an event-sourced ledger, then delete every read model and prove
the rebuild produces an identical result — repeatedly and automatically.

### Scope

```
Account (aggregate)     deposit, withdraw, freeze, correct
EventStore              optimistic concurrency, read, streamAll
BalanceProjector        deterministic, idempotent, checkpointing
SnapshotStore           save, load + checksum verify
EventUpcaster           v1 decimal -> v2 integer minor units
```

### Step 1: Aggregate and Store (3 h)

Implement `Account` and `EventStore`. Schema:

```sql
CREATE TABLE events (
  event_id     TEXT PRIMARY KEY,
  aggregate_id TEXT NOT NULL,
  version      BIGINT NOT NULL,
  type         TEXT NOT NULL,
  payload      TEXT NOT NULL,
  occurred_at  TIMESTAMPTZ NOT NULL,
  UNIQUE (aggregate_id, version));       -- the safety constraint
CREATE INDEX idx_events_agg_ver ON events (aggregate_id, version);

CREATE TABLE snapshots (
  aggregate_id TEXT PRIMARY KEY,
  version      BIGINT NOT NULL,
  payload      TEXT NOT NULL,
  taken_at     TIMESTAMPTZ NOT NULL,
  checksum     TEXT NOT NULL);

CREATE TABLE balances (
  account_id   TEXT PRIMARY KEY,
  balance_minor BIGINT NOT NULL,
  version      BIGINT NOT NULL);

CREATE TABLE projector_checkpoint (
  projection   TEXT PRIMARY KEY,
  last_event_id TEXT NOT NULL,
  processed_count BIGINT NOT NULL,
  processed_at TIMESTAMPTZ NOT NULL);
```

Required tests:
- Deposit, withdraw, freeze; balance is derived and correct after each.
- Withdraw beyond balance -> rejected **at decision time**, not at read time.
- **Concurrent appends**: 50 threads appending to one account. Assert no lost
  update and versions are exactly `1..50` with no gaps.
- **Conflict path**: two threads with the same expected version; exactly one
  succeeds, the other gets a conflict and retries.
- **Version gap detection**: corrupt the log (delete version 7) and assert
  rehydration fails loudly rather than producing a wrong balance.

### Step 2: Deterministic Projection with Checkpoints (3 h)

Implement `BalanceProjector`. Required tests:

- Project the whole log; balances match the aggregates exactly.
- **Redelivery idempotency**: process the same batch twice; the read model must
  be identical. This is why writes are versioned upserts, not deltas.
- **Crash mid-batch**: process half a batch, kill, restart from the checkpoint.
  Assert the final read model equals the no-crash result.
- **Checkpoint atomicity**: assert checkpoint and data are in one transaction.
  Write a test that simulates a crash between them and proves the design
  prevents the inconsistency.

### Step 3: Determinism Test (2 h)

The requirement from the theory section, enforced by test:

```
  Delete balances. Rebuild from the log. Diff must be EMPTY.
```

Then repeat 5 times, and diff against the *original* captured state each time.
Assert byte-identical balances including the `version` column.

**Now break determinism deliberately**: add `Instant.now()` into a projected
column and re-run. The diff must fail. Keep that failing test — it documents
why the rule exists.

### Step 4: Snapshots (2 h)

Implement `SnapshotStore` with checksum verification. Required tests:

- Save a snapshot at version 20; load an account from snapshot + 3 tail events
  and assert the balance matches a full replay.
- **Corrupt the snapshot payload**; assert load returns null and a full replay
  produces the correct state. This is the "snapshot is a cache" test.
- Trigger rule: snapshot when `log_bytes_since_snapshot > 2 * state_bytes`.
  Assert the trigger fires at the expected version.
- Measure: replay cost with and without snapshots, and report the speedup.
  Expect roughly the 8-minutes-versus-30-hours order of improvement in scaled
  form.

### Step 5: Schema Evolution (2 h)

The log contains v1 events; the code now speaks v2.

```
v1 Deposited:  {accountId, amount: "125.50"}
v2 Deposited:  {accountId, amountMinor: 12550, currency: "USD"}
```

Required tests:
- **Tolerant reader**: read a v1 event and compute `amountMinor` correctly.
- **Upcaster**: the same event through the upcaster produces the v2 shape.
- **Append v2, replay over v1**: mixed log rebuilds correctly, and the balance
  after both equals the sum. This mixed-history test is the real one.
- Assert the **upcaster and tolerant reader agree** on every v1 sample.

### Step 6: Temporal Query (1 h)

Implement `balanceAt(accountId, version)`.

- Answer "balance at version 30" from the log.
- Answer "balance at Instant T" using `occurred_at` (and document that ordering
  uses `version`, with `occurred_at` used only to pick a cut-off).
- Answer "list all withdrawals in a date range" — a different query shape.

**Then:** build a second projection for the range query and demonstrate read
amplification: two projections, two rebuilds, two tables.

### Step 7: Operational Metrics (1 h)

- Projection lag (offset vs. checkpoint) — **alert on this, not error rate**.
- Dead-letter count and payload.
- Checkpoint age.
- Rebuild duration and events/second.
- Aggregate version distribution (detects hot aggregates).

Create a lagging projector deliberately (sleep in the loop) and verify the lag
alert fires while the error rate stays at zero.

### Deliverables

1. Event-sourced `Account` with derived balance and decision-time invariant
   enforcement.
2. Store with a `UNIQUE (aggregate_id, version)` constraint, 50-thread
   concurrency test, and the conflict/retry path.
3. Version-gap detection that fails loudly.
4. Deterministic, idempotent, checkpointing projector with a crash-recovery test.
5. Repeated full rebuild with empty diff, plus the deliberately-broken
   determinism test that fails.
6. Snapshot store with checksum verification and the corrupt-snapshot test.
7. Mixed v1/v2 history rebuild, with upcaster and tolerant reader agreeing.
8. Temporal queries plus the read-amplification demonstration.
9. Metrics with a lag alert proven to fire at zero error rate.

### Stretch

- Blue-green projection deploy: build `projection_v2` with a different schema,
  rebuild, verify empty diff, atomically switch, then roll back to v1 to prove
  rollback works.
- Generate 10M synthetic events and measure the real rebuild rate. Compare
  against the `MATH_FOUNDATION.md` estimate and explain the gap.