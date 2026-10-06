# Lab 02: EBS System Administration — Math Foundation

## 1. FND Security Coverage — Menus, Groups, Responsibilities

```
Application users:                 480
Responsibilities defined:           38
Menus assigned (direct):          1,240
Responsibility-to-role mappings:   310
Request groups used:                 12
```

```
Effective access per user = menus reachable + responsibilities held
                             + request groups with requester role

Coverage metric that matters:
  access_paths_covered / access_paths_total

  Financials (GL, AP, AR):
    1,240 menu assignments
    Properly constrained (responsibility + MOAC org + set-of-books): 1,176
    Over-privileged (broad responsibility, no org constraint):           64
    Coverage: 1,176 / 1,240 = 94.8%
```

```
94.8% coverage sounds strong. The residual 64 assignments are the ones that matter:
  Users holding a "Financial Analyst — All Orgs" responsibility: 18
  Over-privileged actions available per user: 312 (menu entries)
  Total over-exposed menu entries: 18 × 312 = 5,616

  These users can reach periods closed to them and orgs they should not see.
  A percentage hides that; "18 users can post to any org" does not.
```

## 2. SoD Coverage in the FND Model

```
Privileged roles:                    6
  AP Create, AP Approve, AR Adjust, GL Journal Create,
  GL Journal Approve, Payroll Admin

SoD conflict rules defined:           9
Users in scope:                     480
Privileged role assignments:        612
Conflicting assignments detected:    48
Blocked by design (exclusive roles): 34
```

```
SoD coverage = 34 / 48 = 70.8%

Residual 14 unblocked assignments spread across 9 users (1.9% of users).
Each unblocked pair is a specific, nameable risk:
  AP Create + AP Approve   -> 6 users can approve their own invoices
  GL Jrnl Create + Approve -> 3 users can approve their own journals
```

```
Blocking the residual is a profile-level change, not a code change:
  Profile 'GL Journal Approve' set to require a different user than the creator.
  Covered assignments: 48 / 48 = 100%

  Coverage gain: 70.8% -> 100% for 9 users.
  Effort: 1 profile + 1 verification query. This is the cheapest control in EBS.
```

## 3. Per-Row Exception Isolation

```
Custom concurrent program processing request lines:
  Lines in request:                 10,000
  Lines failing validation (est. 4%):   400
```

### Whole-transaction failure (no isolation)

```
If the program ROLLS BACK on any error:
  1 error   -> 10,000 lines lost, all work discarded
  Probability at least 1 error:        1 - (1 - 0.04)^10,000 ≈ 100%
  Expected attempts to complete:        effectively unbounded

  Time to complete: never. The program has a 100% failure probability.
```

### Per-row savepoint isolation

```
FOR each line LOOP
   SAVEPOINT before_line;
   BEGIN
      validate(line);
      apply(line);
   EXCEPTION WHEN OTHERS THEN
      ROLLBACK TO before_line;
      log_error(line, SQLERRM);
   END;
END LOOP;
COMMIT;
```

```
  400 lines logged as errors, 9,600 committed
  Completion probability:  100% (errors are data, not failures)
  Lines needing manual work: 400  (4%)
  Time to complete:          10,000 × 75 ms = 750 s = 12.5 min
```

| Strategy | Completion probability | Lines lost per error | Manual rework |
|----------|------------------------|----------------------|---------------|
| Roll back everything | ~0% | 10,000 | 10,000 |
| Per-row savepoint | 100% | 0 | 400 |
| Skip-on-error without logging | 100% | 0 | 10,000 (unexplained) |

**The third row is the trap.** Skipping an error without logging converts a
visible failure into invisible data corruption.

## 4. Error Rate Is a Design Signal

```
Error rate by validation stage (10,000-line import):
  Supplier not found:               210  (2.1%)
  Item inactive:                    145  (1.45%)
  UOM conversion missing:           118  (1.18%)
  Duplicate external reference:      87  (0.87%)
  ------------------------------------------
  Total:                            560  (5.6%)
```

```
Expected error count = 10,000 × error_rate
  1%  ->  100
  4%  ->  400
  5.6% ->  560
  15% -> 1,500   <- the matching assumptions are wrong, not the data
```

```
Threshold that separates "bad day" from "wrong program":
  < 2%   routine; investigate only if it doubles
  2-5%   a data quality issue; fix the source
  > 10%  the rules are wrong. Do not add error handling to cope — fix the rules.

  A program whose error rate is 15% has not been configured correctly.
  Adding more isolation machinery to handle 1,500 errors hides the real defect.
```

## 5. Concurrency: Requests, Locks, and Deadlocks

```
PO submit program, 8 workers, each processing a distinct org:
  Workers:              8
  PO lines/hour:        1,200
  Mean line time:       3.2 s
  Lines in flight:     8 × (1,200/3,600) × 3.2 ≈ 8.5 rows locked
```

```
Lock hold time per line:  ~0.8 s (header update + validation + insert)
Contention on gl/ po tables:
  Distinct orgs:          6
  Workers per org:        8 / 6 = 1.33  -> collisions inevitable

ORA-00001 / ORA-00060 observed: 38 per month
Failure impact:
  Failed run:             11 min of worker time lost
  Monthly worker capacity lost: 38 × 11 = 418 min
  As % of monthly capacity: 418 / (336 slots × 30) = 4.1%
```

```
Isolation fix that removes the contention entirely:
  Partition the work by org_id explicitly, so no two workers touch the same
  org's rows.

  Contention probability after partitioning: ~0 (by construction)
  Capacity recovered: 4.1%
```

**4.1% of batch capacity lost to avoidable contention is the same as buying a
worker and not using it.** It is invisible in a queue report that only shows
"completed: 260 of 260".

## 6. Request Set Sizing — Don't Put a Month in One Request

```
Month-end concurrent programs:        420
Naive: one request set containing all 420

  Problems:
    One failure -> all dependents blocked
    One user reruns the whole set
    No partial visibility of progress
    Rerun of one failed program means rerunning 420
```

```
Phase decomposition:
  Phase 1 — Subledger accounting:      68 programs,  independent
  Phase 2 — GL journal generation:      24 programs,  independent
  Phase 3 — Journal import:             12 programs,  independent
  Phase 4 — Reconciliation:             96 programs,  read-only
  Phase 5 — Consolidation:              18 programs,  dependent on 4
  Phase 6 — Close:                      42 programs,  dependent on 5

  Blast radius of a failure:
    Single set:      420 programs blocked
    Per-phase sets:  max 96 blocked (phase 4), typical 18-24
  Reduction: 420 / 96 = 4.4× worst case, and reruns become scoped
```

```
Dependency representation:
  explicit parent-child: rerun of a child reruns only that child
  implicit (by convention, in the scheduler script): reruns cascade blindly

  Rerun cost of one failed program in phase 5:
    explicit:  18 programs × avg 3.2 min = 58 min
    cascade:   420 programs × avg 3.2 min = 2,244 min = 37.4 hours
  Ratio: 37.4 h / 58 min = 38.7×
```

## 7. Profile Option Inheritance — The Credential Leak

```
Profile hierarchy:
  System  -> Site  -> Application -> Responsibility -> User
              \
               -> Server   (host-specific overrides)
```

```
Roles: 130 users
Servers in the estate: 4 (DEV, TEST, PROD-ASAP, DR)

The leak:
  Profile 'Debug Level' at the RESPONSIBILITY level = 'DEBUG'
  Server PROD-ASAP overrides it to 'ERROR'   <- a good practice
  Users on DEV and TEST still inherit DEBUG

  Users inheriting an unintended value: 32 / 130 = 24.6%
```

```
The dangerous variants:
  'Debug Level' = DEBUG            -> verbose logs, possible SQL/parameter leakage
  'Signon Audit Level' = NEVER     -> authentication events not audited
  'Concurrent Program Priority' = 1 -> user jobs compete with close jobs

  Exposure calc for DEBUG inheriting to production logs:
    32 users × 1,200 PO lines/day × 400 bytes/query logged
    = 15.4 MB/day of SQL text in logs, including bind values
```

```
Inheritance audit query — the only reliable detection:
  Count profiles where a responsibility-level value differs from the
  site/application level, then verify each difference is intentional.
  Rows found: 41. Intentional: 34. Unintentional: 7 (6.7% error rate).
```

**Profile inheritance is a feature and the leak is its price.** The audit query
is the only way to know what is actually in effect at the responsibility level.

## 8. Password Policy and Session Timeout

```
FND policy target:
  Minimum length:      8 characters (legacy) -> 10 (target)
  Reuse:               3 passwords
  Account lock:        5 failed attempts
  Signon profile timeout: 8 hours
  Idle timeout:            30 minutes (idle_time_warning)
```

```
Password entropy:
  Legacy 8 chars, no class requirement:
    effective space ≈ 10^12 - 10^14 (human patterns dominate)
  Target 10 chars, 3 of 4 classes:
    effective space ≈ 10^18 - 10^20

  Online attack, rate-limited to 5 attempts / 15 min / account:
    480 attempts/day/account
    Accounts: 130
    Daily guesses: 62,400
    Exhaustive at 10^12: 10^12 / 62,400 = 1.6 × 10^7 days = 44,000 years
    Exhaustive at 10^18: 1.6 × 10^13 days = 4.4 × 10^10 years
```

**Rate limiting dominates any password policy.** A length rule that improves
entropy by 6 orders of magnitude changes an attack duration from 44,000 years to
44 billion years — but the rate limiter is what makes both infeasible in the
first place.

```
Lockout as a denial-of-service vector:
  Cost to lock one user:  5 failed attempts, ~5 requests, 2 seconds
  Cost to lock 130 users: 650 requests, ~4 minutes
  Business cost:          130 users idle until each lockout expires

  Mitigation: alert on distinct_accounts > 20 with attempts < 5 each (spray)
              never auto-lock without a notification
```

### Session retention

```
Signon profile timeout:  8 hours (480 min)
Average working session: 45 min
Abandoned sessions:      12%
```

```
Wasted retention: 480 min timeout vs 45 min working
  Per day: 480 sessions started, 58 abandoned
  Wasted minutes: 58 × 480 = 27,840
  Useful minutes: 422 × 45  = 18,990
  Overhead: 27,840 / (27,840 + 18,990) = 59.4%

Idle timeout at 60 min:
  Wasted: 58 × 60 = 3,480 min
  Overhead: 3,480 / (3,480 + 18,990) = 15.5%

  Overhead reduction: 59.4% -> 15.5%  = 43.9 pp
  Cost: legitimate users working > 60 min must re-authenticate
        (8-hour timeout was protecting a real 3-hour analysis session)
```

**Idle timeout measured from activity, not from signon, reclaims 44 points of
retention overhead without touching the working session.** That is the whole
argument for having both settings.

## 9. Batch Concurrency Formulas

```
Workers available:  concurrent_program_type, 'Concurrent Managed',
                    service_level 'CS_MGR' -> workers = 8

Safe worker count formula:
  workers = min(
      usable_cores × 0.7,           -- leave headroom for the instance
      distinct_data_partitions,     -- else workers contend on the same rows
      cpu_cost_ratio_limit          -- DB I/O heavy work needs fewer workers
  )

  32 cores × 0.7 = 22
  distinct orgs  = 6
  For a write-heavy subledger load: use 0.3 × cores = 9
  workers = min(22, 6, 9) = 6
```

```
Throughput with 6 workers on a partition-safe program:
  Mean run time: 3.2 s
  Throughput:    6 / 3.2 = 1.875 programs/sec
  420 programs:  420 / 1.875 = 224 s = 3.7 min

Throughput with 16 workers on the same program (contending):
  Mean run time inflates to 9.8 s (lock waits, 3× )
  Throughput:    16 / 9.8 = 1.63 programs/sec  -- WORSE than 6 workers

  More workers, less throughput. The curve turns over at the contention point,
  not at the core count.
```

**Add workers only when the workload partitions cleanly.** Otherwise you are
buying contention.

## 10. Ad-Hoc Session Sizing

```
Self-service / OAF users:                480
Ad-hoc (SQL, forms) power users:          60
Ad-hoc managers:                          40
                                     -------
Ad-hoc sessions peak:                    140
```

```
Session pool by class:
  Self-service:  140 concurrent × 0.75 s mean request = 105 concurrent DB sessions
  Ad-hoc power:   40 concurrent × 2.5 s mean request = 100 concurrent
  Ad-hoc mgr:     25 concurrent × 4.0 s mean request = 100 concurrent
                                                              ---------
  Total ad-hoc demand:                            305 concurrent

Reserved pool (ad-hoc):            300   (150 per RAC instance)
  305 demanded > 300 reserved -> guaranteed queueing at peak
```

```
The correct adjustment:
  Reduce the ad-hoc concurrency itself, not just the pool:
    Ad-hoc managers: 25 -> 18 concurrent
    Ad-hoc demand: 18 × 4.0 = 72  -> total 277 vs 300 reserved
    Utilisation: 277 / 300 = 92.3%   (still high; target < 80%)

  Or raise the pool: 305 / 0.80 = 381 sessions
    + reserved admin: 20
    Total reserved: 401  -> 200 per instance with 2 instances
```

```
Rule of thumb:
  pool_size = peak_ad_hoc_concurrency × mean_request_seconds / 0.80

Sizing the pool from the number of ad-hoc USERS rather than their concurrency
over-provisions by roughly 6× and starves the main application pool.
```

## 11. Privileged Role Count Is a Blast Radius Metric

```
DBA-equivalent / profile-with-DBA roles held:  6 people
FND_SYSADMIN access:                          4 people
Payroll administrator:                        8 people

Each holder can:
  See all unencrypted profile values:        including integration passwords
  Run any concurrent program:                including custom ones
  Change any responsibility mapping:          effectively create new access
```

```
Blast radius if one account is compromised:
  6 DBA holders × 480 users' data = 100% of the estate reachable

  With 30-day audit retention on that account, detection window:
    Average detection time for a compromised privileged account: 41 days
    Probability of detection within the 30-day window:
      30 / 41 = 73.2%
    Undetected window: 26.8% of compromises persist past the audit window

  Fix: increase privileged audit retention to 400 days.
    P(detection within 400 days) ≈ 100% within the model.
```

**The blast radius of a privileged account is proportional to how many people
hold it and to what those people can reach.** Six is a lot when each can see
everything.

## 12. System Administration Before/After

| Measure | Before | After | Change |
|---------|--------|-------|--------|
| SoD coverage (FND) | 70.8% | 100% | +29.2 pp |
| Over-privileged menu assignments | 64 | 0 | residual removed |
| Users able to self-approve | 9 | 0 | eliminated |
| Program completion probability | ~0% (whole-txn rollback) | 100% (savepoint) | total |
| Lines needing rework | 10,000 | 560 (5.6%) | 17.9× less |
| Batch capacity lost to contention | 4.1% | ~0% | partitioned |
| Rerun blast radius (worst phase) | 420 programs | 96 | 4.4× smaller |
| Rerun cost of one failure | 37.4 h | 58 min | 38.7× |
| Profile inheritance leaks | 7 unintentional | 0 | audited |
| Session retention overhead | 59.4% | 15.5% | −43.9 pp |
| Ad-hoc pool utilisation | 102% | 92.3% (or 77% resized) | headroom |
| Workers vs throughput | 16 workers, 1.63/s | 6 workers, 1.875/s | 15% more throughput with fewer |

The recurring lesson: **in system administration, the arithmetic that matters is
about isolation, not throughput.** Isolating rows, phases, and profiles is what
converts a failure from an event into a data row you can count.
