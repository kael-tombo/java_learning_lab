# Distributed Locking - Real World Project

## Project: Removing a Distributed Lock Fleet from a Job Scheduler

### Objective
Audit a scheduler that uses distributed locks to guarantee single-execution, replace the
locks that can be replaced with uniqueness constraints and leases, and fence the ones that
must stay.

### Why This Is a Real Problem
Lock-based schedulers are the classic source of double execution: the lock expires during a
long job, a second worker starts, and now two runs of the same job overlap with no log entry
showing a failure. It is silent, it is rare, and it corrupts data.

### Architecture Overview
```
 Scheduler ──▶ (no lock) INSERT INTO job_run(...)  ── unique constraint ──▶ only one wins
      │
      ├─ daily report:  unique (job_id, run_date)  → constraint, not lock
      ├─ cache rebuild: lease + fencing token     → safe work, idempotent
      └─ payment capture:  fenced lease           → must be serialized, use token
```

### Phase 1: Inventory and Classify (Week 1)
1. List every lock acquisition in the codebase with its resource, TTL, and critical section
2. For each, answer: what breaks if two holders act at once?
3. Classify:
   - **Replaceable** — a uniqueness constraint or `INSERT ... ON CONFLICT` gives the same
     guarantee for free
   - **Replaceable with idempotency** — the operation is naturally repeatable
   - **Must serialize** — genuinely non-repeatable side effects
4. Expect most locks to be replaceable. That is the finding.

### Phase 2: Replace the Uniqueness Locks (Week 2)
```sql
ALTER TABLE job_run ADD CONSTRAINT uq_job_run_day UNIQUE (job_id, run_date);
```
1. Add the unique constraint. If existing data violates it, that is a latent double-execution
   bug you just discovered — investigate before proceeding
2. Replace the lock-then-insert with a plain insert and handle the constraint violation
3. Verify: run the job concurrently from two nodes and confirm exactly one run row
4. Record how many duplicate `job_run` rows already existed — that is your incident count

### Phase 3: Convert the Rest to Fenced Leases (Week 3)
1. Acquire a lease with a monotonic token; renew at TTL/3; stop immediately on renewal failure
2. Pass the token into every write; the resource tables gain a `last_fence_token` column
3. Reject any write with a token below `last_fence_token`
4. Size the TTL from measured critical-section duration p99 × 3, not from a round number
5. Test by killing the holder mid-critical-section and confirming the write is rejected

### Phase 4: Handle the Long Jobs Properly (Week 4)
Long-running jobs cannot be protected by any finite TTL you would actually choose. Fix the
problem instead:
1. Make the job **idempotent and checkpointed** — resumable from the last completed unit
2. Split it into units with a uniqueness constraint per unit (`(job_id, unit_index)`)
3. Then no lock is needed at all: overlapping execution is harmless because units are unique
   and work is idempotent
4. Add a stale-lease reaper: leases not renewed for 3× TTL are forcibly released with a
   fresh, higher token

### Phase 5: Prove It (Week 5)
1. Chaos: pause holders past their TTL for every remaining lock — assert zero double effects
2. Replay the historical duplicate `job_run` rows as regression tests
3. Alert on fencing rejections — they mean a real overlap happened, and you want to know
4. Delete the lock library usage; keep fencing, which is the part that was load-bearing

### Deliverables
1. Lock inventory with the replaceable/must-serialize classification
2. Unique constraints plus idempotent insert paths replacing the replaceable locks
3. Fenced lease implementation with token enforcement at the resource
4. Chaos results showing zero double effects, plus the fencing-rejection alert

### Success Criteria
- Zero double executions under induced TTL expiry for every remaining lock
- Historical duplicate runs identified, counted, and captured as regression tests
- Every remaining lock uses a fencing token enforced by the resource
- Lock library removed from the scheduler codebase

### Sourced field notes (fetched Oct 2026 — verify before citing)
- etcd Documentation, v3.5 —
  https://etcd.io/docs/v3.5/
  Use for: lease semantics, `CompareAndSwap`, and the documented concurrency guarantees for
  lock recipes. Verify that the lease/lock recipe you copy is from the version you run, and
  read its stated failure caveats rather than assuming mutual exclusion is unconditional.
- Kubernetes Documentation, "Leases" —
  https://kubernetes.io/docs/concepts/architecture/leases/
  Use for: the coordination Lease object and how leader election uses it in practice. This is
  a production-scale reference for TTL/renewal parameters and for the rule that a lease
  holder must treat loss of renewal as loss of the lock.

### Estimated Time
6 weeks part-time