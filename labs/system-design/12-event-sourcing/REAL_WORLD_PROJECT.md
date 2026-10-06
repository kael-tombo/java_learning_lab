# Event Sourcing - REAL WORLD PROJECT

## Project: Event-Sourced Banking Ledger with Regulatory Audit

**Time**: 5-6 weeks (team of 5)

**Scenario**: You are replacing a banking core. The existing system keeps a
mutable `balance` column and cannot answer "what was this account's balance on
14 March?" — and that question is now a regulatory requirement. Requirements:

- 2.4M accounts, 1.2M ledger entries/day, 7-year retention.
- Full audit reconstruction: any account, any past instant, on demand.
- 7-year retention **and** GDPR erasure on the same data.
- 99.99% availability on the write path; reads may be eventually consistent
  within a stated bound.
- Migration from the existing system with no downtime and no unexplained
  variance.

### Step 1: Feasibility, Before Any Code

Write the feasibility document. Every number here gates the decision.

```
storage:
  1.2M events/day * 400 B compact * 1.4 = 672 MB/day
  7 years = 736 GB hot-eligible, plus cold archive

  JSON with field names would be ~1.4 TB  -> encoding choice is a 700 GB decision

rebuild (the gating number):
  full rebuild from genesis, 3.1B events (7y), 400 events/s single projector:
    2,250 hours = 94 days        NOT VIABLE
  40 parallel projectors:                    60 hours   too slow for routine use

  snapshot-seeded, 2.4M accounts, snapshot every 100 events:
    2.4M * (20us + 50 * 50us) = 2.4M * 2.52ms = 100 minutes
    -> 36x improvement. VIABLE for routine rebuilds.

projections:
  5 read shapes (balance, statement, range queries, risk feed, regulator export)
  -> 5 tables, 5 rebuilds, ~8 hours each single-threaded

conclusion: viable, PROVIDED snapshots exist from day one and encoding is compact
```
**Deliverable:** the feasibility document with the go/no-go reasoning. Note
explicitly what would have made this infeasible: no snapshots, JSON events, or
six projections.

### Step 2: Event and Aggregate Design

Aggregates: `Account` (balance, status), `Loan`, `StandingOrder`.

Event schema (compact encoding, field numbers, no field names on the wire):

```
AccountOpened    {customerRef, currency, initialMinor, openedAt}
Deposited        {amountMinor, reference, occurredAt}
Withdrawn        {amountMinor, reference, occurredAt}
TransferSent     {amountMinor, toAccountRef, reference, occurredAt}
TransferReceived {amountMinor, fromAccountRef, reference, occurredAt}
OverdraftApplied {amountMinor, occurredAt}
AccountFrozen    {reason, effectiveAt}
CorrectionApplied{amountMinor, reason, approvedBy, effectiveAt}
```

Critical design rules, each with a written reason:

1. **No erasable PII in events.** `customerRef` only. Name, address, tax id in
   a separate store with a `customerRef` FK. This resolves the GDPR conflict by
   design rather than by crypto-shredding.
2. **Effective dating on every event** (`effectiveAt` / `occurredAt`) — required
   for temporal queries.
3. **Per-account ordering by version**, never by timestamp.
4. **`reference` field** = the external business reference, so reconciliation
   against the payment processor is possible.
5. **Corrections are appended events**, with `approvedBy` — never edits.

### Step 3: Migration from the Existing System

The hard part, and where projects fail.

```
1. INVENTORY      reconcile existing balance vs. full transaction history
                 assert: for every account, sum(history) == current_balance
                 -> ANY mismatch must be explained before migrating
2. BACKFILL       emit one synthetic OpeningBalancesAdjusted event per account
                 to reconcile historical-only drift. This is not optional.
3. SHADOW         run the new system in parallel; compare its projections to the
                 legacy balances continuously for 2 weeks
4. CUTOVER       per account cohort, not all at once
5. REVERT         each cohort independently reversible for 7 days
```
**Deliverable:** the reconciliation report (the `sum(history) == balance`
assertion over all 2.4M accounts), the backfill record, and two weeks of shadow
comparison results.

### Step 4: Projections and Their Five Read Shapes

| Projection | Consumer | Consistency |
|------------|----------|--------------|
| `balance_current` | customer app | lag < 5 s |
| `statement_monthly` | customer app, PDF generation | lag < 5 s |
| `transaction_range` | internal analytics | lag < 60 s |
| `risk_feed` | fraud engine | lag < 1 s (separate, faster pipeline) |
| `regulator_export` | audits, on demand | none; on-request full recompute |

Every projection:
- Deterministic, checkpointed, idempotent (versioned upserts).
- Blue-green deployed: new projection, rebuild, verify empty diff, switch,
  retain previous for one release.
- Rebuilded from genesis **or** snapshot-seeded. Snapshot-seeded is the routine
  path; full rebuild is the audited annual check.

**Deliverable:** per-projection rebuild time (measured), and the full-rebuild
verification report for each projection.

### Step 5: Audit Reconstruction

The capability that justified the project. Implement:

```
balanceAsOf(accountId, instant)         -> balance + full entry trail
allEntriesBetween(accountId, t1, t2)     -> for dispute investigation
accountSnapshotAt(accountId, instant)    -> entire state, not just balance
```

Requirements:
- Reconstruct **any** past instant within 7 years.
- Every reconstruction is **verifiable**: return the source event ids and
  versions so an auditor can confirm no events were skipped.
- Reconstruction time budget: < 5 seconds for a single account.
- Reconstruction must not disturb the live projections (read from the log with a
  bounded query, never by rebuilding).

**Required:** an automated daily audit that reconstructs a random sample of
accounts at a random past instant, compares against the stored projection
checkpoint from that time, and alerts on mismatch. An audit nobody runs is an
audit that has never been tested.

### Step 6: GDPR Erasure (resolved at design time)

```
erasure request for customer C:
  1. delete from the personal-data store (name, address, tax id, contact)
  2. events retain customerRef only, so they remain valid and auditable
  3. retain a tombstone row proving the erasure happened and when
  4. cold-tier event archives were never encrypted with C's data, so no
     separate shredding step is required  -> this is why rule (1) mattered
```

**Deliverable:** the erasure runbook, a proof that a post-erasure account
balance is still reconstructable, and confirmation that no PII remains in any
event tier (backed by an automated scan of the cold archive).

### Step 7: Operational Discipline

- **Lag alerts**, never error-rate alerts, on every projection. A projector
  running perfectly and 20 minutes behind is broken and reports zero errors.
- **Dead-letter queue** per projection, with payload, reason, and a replay path.
- **Schema registry**: every event type and version registered; publishing a
  breaking change is blocked without a registered version.
- **Upcasting and tolerant readers** coexisting for the life of the system.
- Capacity sized on **peak** event rate, not average.
- Blue-green for projection schema changes — never in-place migration.
- Hot-aggregate detection from the version distribution; shard or redesign any
  account above 100 writes/s.

### Step 8: Failure Drills

1. **Broker outage for 2 hours.** Verify write path unaffected (the log is the
   source of truth), lag grows, the alert fires, and catch-up completes without
   losing events.
2. **Delete a projection entirely.** Verify blue-green rebuild restores it, the
   diff is empty, and the measured rebuild time matches the feasibility document.
   This is the drill that proves the architecture.
3. **Corrupt a snapshot.** Verify it is detected by checksum, discarded, and the
   account rebuilt from the log correctly.
4. **Introduce a non-deterministic projector** (`now()` in a projected column)
   in staging. Verify the diff check catches it. This drill is the reason the
   verification step exists.
5. **Rollback a cutover cohort.** Verify a cohort reverts independently, with no
   lost or duplicated entries after the revert.
6. **GDPR erasure on a live account with 7 years of history.** Verify
   completion within the regulatory window, that the balance remains
   reconstructable, and that no PII remains in any tier.
7. **Full audit reconstruction for a regulator** on a named account: measure
   end-to-end time and produce the verifiable entry trail.

### Deliverables

1. Feasibility document with the go/no-go reasoning and the gating numbers.
2. Event and aggregate design with the five design rules and their reasons.
3. Migration record: reconciliation report over 2.4M accounts, backfill record,
   and two weeks of shadow comparison.
4. Five projections with measured rebuild times and blue-green deployment
   evidence.
5. Audit reconstruction with verifiable trails, plus the daily automated audit.
6. GDPR erasure runbook with the post-erasure reconstructability proof and the
   cold-archive PII scan.
7. Operational discipline: lag alerts, dead-letter replay, schema registry.
8. Seven drill reports with measured numbers, especially the projection-delete
   and the non-deterministic-projector drills.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Feasibility | Built it, hoped it scales | Gating numbers computed first; no-go conditions stated |
| Events | JSON with field names | Compact encoding justified as a cost decision |
| PII in events | Names and emails in events | `customerRef` only; erasure proven compatible |
| Migration | Big-bang cutover | Reconciliation, backfill, shadow, per-cohort reversible |
| Projections | Five hand-built tables | Deterministic, blue-green, measured rebuilds |
| Audit | "We keep the logs" | Verifiable trails, daily automated reconstruction audit |
| Ops | Error-rate alerts | Lag alerts, proven by the lag drill |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Apache Kafka documentation — design, delivery semantics, and **log
  compaction and retention**: the reference for the append-only log's partition
  keying (per-aggregate ordering), retention settings that must satisfy 7-year
  regulatory retention, and compaction semantics that must be verified against
  your version before being relied on for an immutable ledger.
  https://kafka.apache.org/documentation/
- RFC 3339 — *Date and Time on the Internet*: the normative format for the
  `occurred_at` / `effective_at` timestamps on events. It matters here because
  temporal queries and audit reconstruction depend on unambiguous, sortable,
  timezone-qualified timestamps, and this specification defines exactly how to
  represent them.
  https://www.rfc-editor.org/rfc/rfc3339.html

Both are stable and versioned. Re-verify Kafka's exact retention and compaction
behaviour for your major version before designing a 7-year retention scheme on
it — defaults alone will not meet a regulatory requirement, and log-compaction
semantics have changed across releases.