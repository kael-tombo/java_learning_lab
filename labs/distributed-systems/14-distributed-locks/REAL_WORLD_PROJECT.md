# Distributed Locks (Deep) - Real World Project

## Project: Eliminating Races in a Payment Reconciliation Pipeline

### Objective
Take a reconciliation pipeline that uses distributed locks to serialise batch runs, replace
the avoidable ones with idempotent claims, fence the one that must be serialised, and prove
under chaos that no double-processing occurs.

### Why This Is a Real Problem
Reconciliation jobs read bank statements and write ledger entries. Two overlapping runs do not
error — they double-count, and the discrepancy surfaces weeks later during a financial close.
The locks that "protect" this pipeline routinely expire mid-batch because the batch duration
is longer than the TTL.

### Architecture Overview
```
  Scheduler ─▶ Claim (atomic UPDATE ... WHERE state='PENDING' RETURNING *)
                  │  no lock: the claim IS the guarantee
                  ▼
              Processor ─▶ Ledger (unique (txn_ref, account) → no duplicate posting)
                  │
                  └─▶ Fenced lease for the single non-repeatable step (FX conversion)
```

### Phase 1: Audit Every Lock (Week 1)
1. List each lock with resource, TTL, critical-section p50/p99 duration, and contention rate
2. Find every lock whose critical section is longer than its TTL — those are already broken
3. Check for duplicate ledger entries in history; that is your existing double-processing count
4. Classify each as: claimable, idempotent, or genuinely non-repeatable

### Phase 2: Replace Locks with Atomic Claims (Week 2)
```sql
-- One statement. No lock, no TTL, no expiry, no double-processing.
UPDATE statement_lines
   SET state = 'PROCESSING', claim_token = :token, claimed_at = now()
 WHERE id IN (
   SELECT id FROM statement_lines
    WHERE state = 'PENDING' AND batch_id = :batch
    ORDER BY id
    LIMIT :chunk_size
    FOR UPDATE SKIP LOCKED        -- safe concurrency, and no application lock at all
 )
RETURNING id, raw_txn;
```
1. Batch size is the throttle; multiple processors can safely run in parallel
2. Stale claims (`claimed_at` older than N minutes) are reclaimed, which is a better failure
   mode than an expiring lock
3. Add `UNIQUE (txn_ref, account_id)` on the ledger so a duplicate posting is rejected by
   the database even if every other control fails

### Phase 3: Fence the One Irreducible Step (Week 3)
Only one step is truly non-repeatable: applying an FX conversion to a rate table.
1. Lease with a monotonic token; renew at TTL/3; stop on the first renewal failure
2. The rate table stores `last_fence_token`; a write with a lower token is rejected
3. Make the step itself idempotent by storing the applied rate keyed by `(rate_date, source)`
   so a retry returns the existing rate instead of reapplying
4. Test: kill the holder mid-step, confirm the write is rejected and the rate is correct

### Phase 4: Chaos Verification (Week 4)
| Scenario | Expected | Verify |
|---|---|---|
| Two processors, same batch | disjoint claims, no duplicate ledger rows | `UNIQUE` holds |
| Processor killed mid-chunk | claim reclaimed after TTL, no double-processing | ledger count matches bank statement count |
| FX lease lost mid-write | write rejected by fence | rate unchanged, alert fired |
| Partition during claim | claim fails, retries cleanly | no orphan PROCESSING rows |
| Stale claim reclaimed | original returns, sees claim lost, discards | no double write |

Run all five against a copy of production data and reconcile the ledger to the bank statement
totals. That reconciliation is the acceptance test.

### Phase 5: Operate (Week 5+)
1. Metrics: claims per run, stale claim reclaims, unique-constraint rejections, fence
   rejections
2. Alerts: reconciliation mismatch (any discrepancy > 0), fence rejection, stale claims
3. Runbook: "reconciliation mismatch" — identify the txn, check the unique constraint and
   the claim audit trail
4. Remove the lock library from this pipeline entirely and enforce it in CI

### Deliverables
1. Lock audit with existing double-processing counts
2. Atomic claim implementation with `FOR UPDATE SKIP LOCKED` and stale-claim reclamation
3. Fenced lease for the FX step with the database-enforced token check
4. Chaos report reconciling the ledger to bank totals, plus dashboards and runbook

### Success Criteria
- Ledger reconciles to the bank statement to the cent, every run, for 30 days
- Zero duplicate postings, enforced by the unique constraint
- No lock acquisition remains in the pipeline, enforced by CI
- Every chaos scenario produces no double-processing, verified by reconciliation

### Sourced field notes (fetched Oct 2026 — verify before citing)
- etcd Documentation, v3.5 —
  https://etcd.io/docs/v3.5/
  Use for: lease TTL and keepalive semantics, and the concurrency guarantees of the lock
  recipes. Verify the recipe's stated caveats and your version's minimum TTL before adopting
  it for the FX step.
- Apache ZooKeeper Programmer's Guide —
  https://zookeeper.apache.org/doc/r3.9.2/zookeeperProgrammers.html
  Use for: ephemeral node lifetime tied to session, and why a session can expire while the
  client believes it holds a lock. This is the reference argument for fencing tokens being
  mandatory rather than optional.

### Estimated Time
6 weeks part-time