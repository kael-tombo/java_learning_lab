# Lab 05: Technical Foundations (Custom Concurrent Program) — Math Foundation

## 1. Throughput and the 3-Day Problem

The target: 10,000 lines in under 1 hour.

```
Required throughput = 10,000 lines / 3,600 sec = 2.78 lines/sec = 167 lines/min
```

### Where the 3 days actually went

Manual process, 10,000 lines:

| Step | Time | Notes |
|------|------|-------|
| Manual supplier validation | 8 hrs | Lookups by hand |
| Manual site/contact creation | 6 hrs | Form entry |
| Manual price updates | 40 hrs | Row-by-row |
| Manual exception handling | 14 hrs | Chasing discrepancies |
| Reconciliation | 4 hrs | Re-typing totals |
| **Total** | **~72 hrs** | ≈ 3 working days |

**Per line: 26 seconds.** That is the number to beat.

### Automated throughput

| Operation | Per line | Total (10,000) |
|-----------|----------|----------------|
| Validation (4 rules, indexed lookups) | 8 ms | 80 sec |
| API price update | 60 ms | 600 sec |
| Audit insert | 4 ms | 40 sec |
| Stage update | 3 ms | 30 sec |
| **Total** | **75 ms** | **750 sec = 12.5 min** |

```
Improvement = 26 sec / 0.075 sec ≈ 347×
Comfortably inside the 1-hour target with 4.8× headroom
```

**The headroom is the point.** Designing to exactly 1 hour means the first
unforeseen slow query blows the target. Design to 20 minutes and you have room
to diagnose.

## 2. API Overhead — Is It Affordable?

```
Direct DML:   ~12 ms/line  → 120 sec for 10,000
API:          ~60 ms/line  → 600 sec for 10,000
Overhead:     48 ms/line   → 480 sec (8 minutes) added
```

**8 extra minutes to save 3 days.** The overhead is 1.5% of the manual baseline.
There is no business case for direct DML at this volume.

At what volume *would* direct DML tempt you?

```
Break-even consideration:
  API overhead total = N × 48ms
  Manual cost        = N × 26s

  API is always faster than manual. Direct DML never "pays for itself"
  on runtime alone — it is a correctness trade, not a performance one.
```

**This is the key insight**: direct DML is not a performance optimisation at all
when the comparison is to a manual process. Anyone framing it as one has
already lost the argument.

## 3. Batch Size Optimisation

Batch size trades commit frequency against restart cost:

```
Restart cost = (rows processed at failure / total) × total_runtime
Throughput penalty = f(batch_size)  -- more commits = slightly lower throughput
```

| Batch size | Commits (10,000) | Expected restart cost | Undo pressure |
|------------|------------------|----------------------|---------------|
| 100 | 100 | ~37 sec | Very low |
| **500** | **20** | **~3.7 min** | **Low** |
| 1,000 | 10 | ~7.5 min | Moderate |
| 10,000 | 1 | ~12.5 min | **Severe** |

### Deriving batch size from restart tolerance

```
Batch size ≈ (T × restart_tolerance) / total_runtime
```

For 10 minutes' acceptable restart on a 12.5-minute run:

```
Batch = 10,000 × (10 / 12.5) = 8,000 rows per batch
```

That contradicts the intuition that 500 is right. Why?

The calculation says **fewer commits** are better for restart cost. But it
ignores **undo growth and lock duration**, which have hard limits:

```
Single batch of 8,000 API updates:
  Undo: ~8,000 × ~2KB = 16 MB per batch   (acceptable)
  Locks held: minutes                      (NOT acceptable — blocks concurrent work)
  ORA-1555 risk: real
```

**Correct derivation — batch size is bounded by lock duration, not restart cost:**

```
Batch size ≤ (max lock duration / time per row)
```

For a 5-second lock budget at 75 ms/row:

```
Batch = 5,000 ms / 75 ms ≈ 66 rows
```

That is too small for practical reasons. The resolution is that most API calls
**commit internally or release locks per record**, so the practical batch is
governed by undo growth and restart cost, not lock duration:

```
Undo ceiling: ~200 MB per transaction
Per row: ~2 KB
Max rows per transaction = 200MB / 2KB = 100,000 rows

Restart tolerance: 5 minutes on a 12.5 min run
Batch = 10,000 × (5 / 12.5) = 4,000 rows

Balanced answer: 500–1,000 rows
  Bounded restart cost (~1–2 min)
  Undo growth trivial (~1–2 MB)
  Comfortable margin on both constraints
```

## 4. Error Rate Mathematics

Suppose validation finds 4% of lines invalid.

```
Expected errors in 10,000 = 400
```

### Error log volume

```
400 rows × ~200 bytes = 80 KB
```

Trivial. So why is error logging volume ever a concern? It isn't — the concern is
**transaction coupling**, not size. Without an autonomous transaction, 400 error
rows written inside the failing transaction are lost. The problem is not
capacity; it is **atomicity**.

### Failure impact at different error rates

| Error rate | Errors/10k | Investigation burden |
|-----------|------------|----------------------|
| 0.1% | 10 | Trivial |
| 1% | 100 | Manageable |
| 4% | 400 | Needs a summary report |
| 15% | 1,500 | The programme is misconfigured |

**Design signal**: if your error rate is above ~5%, the fix is to the *source
data or rules*, not to the logging. A program that errors on 15% of lines is
telling you the matching assumptions are wrong.

## 5. Idempotency and Duplicate Risk

The core risk on rerun:

```
P(duplicate damage) = P(rerun happens) × P(no idempotency guard)
```

If reruns are routine (failures are normal) and no guard exists:

```
P ≈ 0.30 × 1.00 = 30% chance of duplicating a price update
```

With the resume guard `(status='VALID' AND (run_id IS NULL OR run_id <> :new))`:

```
P(duplicate) ≈ 0 — processed rows are excluded by construction
```

### Rerun correctness check

```
Expected processed after rerun = original processed count
Actual processed after rerun  = ?

If actual > expected → the guard is not working. Investigate immediately.
```

## 6. MOAC Scope Error Exposure

Consider a program that omits the `org_id` filter:

```
Operating units in the instance: 6
Lines for the target org: 1,667 (1/6 of 10,000)
Lines actually processed without filter: 10,000
Wrongly processed: 8,333 lines (83%)
```

At $4,000 average price impact per line:

```
Financial exposure = 8,333 × $4,000 = $33.3M
```

**The single missing `org_id` predicate is worth $33M.** That is why
`set_moac_context` raising an error when access is absent is not defensive
programming — it is the control that prevents a nine-figure mistake.

```
P(cross-org error per run) = P(reviewer misses it) × P(it reaches production)
```

With a 5% chance of escaping review and 100% of runs executing:

```
Expected exposure per programme deployment = 0.05 × $33M = $1.67M
```

## 7. Audit Completeness — The Rollback Safety Metric

```
Rollback safety = audited changes / total changes
```

| Audited | Total | Safety | Rollback possible? |
|---------|-------|--------|---------------------|
| 10,000 | 10,000 | 100% | Yes, fully |
| 9,900 | 10,000 | 99% | Mostly — 100 rows manual |
| 5,000 | 10,000 | 50% | Partially — archaeology |
| 0 | 10,000 | 0% | **No** |

**Any gap is a permanent defect**, because a change without an audit row cannot
be reversed later. This is why the health check compares `lines_processed`
against `xx_run_audit` row counts.

```
Recovery effort estimate:
100% audited   → minutes (scripted rollback)
99%  audited   → hours (100 manual lookups)
50%  audited   → days (reconstruct what happened from logs)
0%   audited   → impossible; restore from backup, losing post-backup work
```

## 8. ROLLBACK Ordering

Audit rows are reversed in **reverse application order**:

```
Applied:  A → B → C → D
Reversed: D → C → B → A
```

Why order matters when changes are dependent:

```
Suppose B reads A's value:
  Applied:  A=100, then B=100+10=110
  Reversed B first: B=100 (references non-existent state)
  Reversed A first:  A=100 restored, then B=100+10=110 ← correct
```

For independent updates (price changes per item), order does not matter. For
**dependent** changes it is critical.

```
Rule: always reverse in DESC(audit_id) order. Costs nothing. Correct always.
```

## 9. Runtime Budget for the 1-Hour Target

```
Budget: 3,600 seconds

Validation:      80 sec  ( 2%)
API processing:  600 sec (17%)
Audit inserts:   40 sec  ( 1%)
Stage updates:   30 sec  ( 1%)
Commit overhead: 40 sec  ( 1%)
Buffer:         2,810 sec (78%)
```

The buffer is enormous, which is correct. The 1-hour target is set by the
**business commitment**, not by technical necessity. Designing to 12.5 minutes
means the commitment is met with room to diagnose problems.

```
If runtime exceeds the buffer, something is wrong:
  - Unindexed lookup on supplier/item (add index)
  - Lock contention with concurrent users (batch smaller, schedule off-peak)
  - API overhead worse than benchmarked (check for triggers on PO tables)
```

## 10. Progress Reporting

Long runs need progress visible in the log, or operators assume it has hung:

```
Progress update every batch:
  "Processed 5,000 of 10,000 (2,000 errors, 0.4%)"
```

Time-to-completion estimate:

```
Remaining time = (rows_remaining / rows_processed) × elapsed
```

At 5,000 rows in 6 minutes with 5,000 remaining:

```
ETA ≈ 6 minutes
```

**Without this, a 12-minute program looks identical to a hung one** for the
first 10 minutes, and someone restarts it — creating duplicate risk.

## 11. Cost of Missing Registration

```
P(no submit permission discovered in production) = 0.15
Cost per incident = 2 hours of escalation + an emergency grant
```

Expected annual cost:

```
Annual submissions where this bites = 2 × 0.15 = 0.3 incidents/yr
Cost = 0.3 × 2 hrs × $150/hr = $90/yr
```

Trivial in absolute terms — which is precisely why it gets skipped and why it
still happens. **Test registration with a real operator account before go-live.**
The fix is five minutes; the discovery is an escalation at 2am.