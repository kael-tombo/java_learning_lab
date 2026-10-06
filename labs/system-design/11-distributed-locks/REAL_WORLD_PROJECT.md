# Distributed Locks - REAL WORLD PROJECT

## Project: Safe Concurrent Work in a Payments Platform

**Time**: 2-3 weeks (team of 3)

**Scenario**: A payments platform runs 60 instances that all need to perform
work on the same shared resources: daily settlement file generation,
per-merchant statement rendering, dispute auto-closing, FX rate refresh, and
nightly reconciliation against the processor.

These are long-running (30 s to 20 min), infrequent, and correctness-critical.
Naive Redis locking has already produced two incidents: a duplicate settlement
run, and a statement generated from a half-updated merchant balance.

### Step 1: Inventory Every Place Someone Wants a Lock

For each job, record: name, schedule, expected duration p50/p99, number of
instances that could run it, what happens if two run it, and whether it is
idempotent.

```
job                    p50     p99     instances  duplicate harm      idempotent?
settlement-file        4 min   9 min   60         financial           no
merchant-statement     40 s    2 min   60         customer-visible    yes (by date)
dispute-autoclose      8 s     30 s    60         financial           yes (by id)
fx-rate-refresh        200 ms  1 s     60         stale rates         yes
reconciliation         6 min   14 min  60         financial           no
```

**Key finding to write up:** two of five are naturally idempotent and do not
need a lock at all. That is the most valuable output of this project — it is
also the finding that will be hardest to get accepted, so bring numbers.

### Step 2: Eliminate Locks Where Possible (do this FIRST)

- **Dispute autoclose**: claim work with `UPDATE ... SET status='RUNNING'
  WHERE id=? AND status='PENDING'` and use the affected-row count. This is
  optimistic concurrency, exactly correct, and needs no lock.
- **FX rate refresh**: take a `READ COMMITTED` snapshot row and update it.
  Duplicate refresh is harmless; locking it is pure cost.
- **Merchant statement**: key the work item by `(merchant_id, statement_date)`
  with a `UNIQUE` constraint. Duplicate generation is impossible by
  construction.

Document the elimination with the failure mode each approach prevents. This
becomes the template the rest of the org copies.

### Step 3: Real Locks for the Irreducible Cases

Two jobs remain: `settlement-file` and `reconciliation`. Design for both:

```
Consensus-backed lock (etcd or Consul), NOT raw Redis:
  - resource = "settlement:{business_date}"
  - TTL derived from measured p99 duration, NOT a round number
      observed settlement p99 = 9 min
      plus pause budget 2 min, plus RTT 50 ms
      TTL = ~33 min with 3x safety factor
  - renewal every TTL/3 by a dedicated watchdog thread
  - holder identity = (instance_id, boot_uuid)   // boot_uuid catches restarts
  - release via compare-and-delete (txn with the expected revision)
```

Why consensus-backed rather than Redis:

| Property | Redis lease | etcd/Consul |
|----------|-------------|--------------|
| Release correctness | needs atomic compare-delete | built-in txn |
| Mutual exclusion under partition | probabilistic | guaranteed by quorum |
| Observability | key TTL | session, lease TTL, revision |
| Cost per acquire | ~1 ms | ~5-15 ms |

For two jobs per day, 10 ms is irrelevant. Choose correctness.

### Step 4: Fencing, Because Long Jobs Will Exceed Their Lease

Settlement runs longer than you will predict. So the protected resource must
reject a stale holder:

```
settlement_sink (the thing that actually writes the settlement file):
  - stores last_fencing_token
  - rejects any write with token < last_fencing_token
  - the whole write is one atomic DB operation so a partial stale write
    cannot land
```

**Required test:** simulate settlement running 2x past its lease. A new holder
acquires and writes. The original holder then attempts its final write. Assert
it is rejected and that the settlement file is correct. This is the exact
incident that already happened to you — make it a regression test.

### Step 5: Failure Drills (the real deliverable)

1. **Kill -9 the holder mid-settlement.** Measure: how long until the lock is
   reclaimable, whether the partial file is detected, whether a re-run produces
   a correct result, and whether a human is paged or the system self-heals.
   Expected answer from the math: reclaimable within `2T/3`.
2. **Partition the holder from etcd but not from the DB.** The critical case.
   Verify the holder's writes are fenced out rather than silently accepted.
3. **Clock skew of 5 s on the holder.** Verify the fencing token (not the
   clock) is what provides safety, and document that no lease-duration setting
   could have saved this.
4. **Two operators trigger the same job simultaneously.** Verify exactly one
   proceeds, and that the loser gets a clear, non-retryable "already running"
   response rather than a 500.
5. **etcd loses 2 of 3 members.** Verify existing lock holders keep their
   leases and new acquisitions fail cleanly with a bounded error.

### Step 6: Observability and Runbooks

Metrics: `lock_held_seconds`, `lock_wait_seconds` (separately),
`lock_expired_total`, `fencing_rejected_total`, `jobs_skipped_already_running`,
`lock_backend_errors`. Plus per-job: last successful run, duration p99, and a
staleness alert for the *business outcome* (settlement for date D must exist by
08:00 UTC — alert on that, not on the lock).

Write a runbook per job with: how to check who holds the lock, how to safely
force-release it (and who is authorised), what partial state to inspect, and
how to verify the business result afterwards.

### Deliverables

1. Lock inventory showing which of the five jobs needs a lock at all.
2. Documented eliminations (optimistic concurrency, `UNIQUE` constraint) with
   the failure mode each prevents.
3. Consensus-backed lock design with a TTL derived from measured data.
4. Fencing enforcement at the settlement sink plus the regression test for the
   incident you already had.
5. Five drill reports with measured timelines.
6. Per-job runbooks including authorised force-release procedure.
7. Metrics dashboard and business-outcome alerting.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Elimination | Locks all five jobs | Two locked, three explained away |
| Backend | Redis lease for a 9-min job | Consensus lock, TTL derived from p99 |
| Stale holder | "TTL is long enough" | Fencing at the sink + regression test |
| Drills | Restart the pod | Partition and clock-skew drills |
| Operability | Dashboards | Runbooks with force-release authorisation |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Redis documentation — the `SET` command's `NX` / `PX` options and the
  canonical `SET NX PX` distributed-lock recipe, including the documented
  caveats about failover and clock assumptions.
  https://redis.io/docs/latest/commands/set/
- Apache Kafka documentation — *KRaft* consensus and controller quorum: a
  production Raft-based coordination service, and the natural reference for
  justifying a consensus backend for a 9-minute critical section.
  https://kafka.apache.org/documentation/

Read the Redis `SET` page carefully and quote its "non-standard behaviour"
and failover caveats verbatim when you argue *against* Redis for long locks.
Re-verify the K8s/etcd lease semantics before quoting field-level details.