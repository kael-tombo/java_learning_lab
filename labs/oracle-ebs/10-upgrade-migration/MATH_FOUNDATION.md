# Lab 10: Upgrade & Migration (12.1→12.2, Cloud, 11g→19c) — Math Foundation

## 1. Cutover Duration — The Critical Path

```
Tasks and their durations for a 12.1.10 -> 12.2.x upgrade:

  Task                                       Duration   Parallel?
  ------------------------------------------------------------------
  Pre-upgrade backup (RMAN consistent)       4.5 h     -
  EBS clone (storage snapshot + restore)     3.0 h     -
  Patch manager application                   2.5 h     -
  adop prepare                                2.5 h     -
  adop clone (custom code)                    1.8 h     -
  SQL version update / utlrp.sql              0.7 h     -
  Post-adop custom code fix + regression     6.0 h     -
  Critical patch apply (DB)                   2.2 h     -
  adop cutover (the downtime)                 0.8 h     -
  Data conversion verification                 1.5 h     -
  Smoke / sign-off                            2.0 h     -
  ------------------------------------------------------------------
```

```
Sequential total:   27.5 hours
```

```
The cutover window is only the adopt cutover plus verification:
  Cutover:        0.8 h  (48 min of actual downtime)
  Verification:   1.5 h
  Total offline:  2.3 h  (138 min)
```

```
The mistake: budgeting 27.5 hours of downtime.
Only 138 minutes require users to be off the system. Everything else runs on
a clone while production continues.
```

**Duration budgeting must separate offline time from elapsed time.** They differ
by an order of magnitude and conflating them is what makes upgrade windows
unacceptable to the business.

## 2. Parallelising the Task Graph

```
Dependencies:
  backup -> clone -> patch -> prepare -> clone_code -> sql_update
                                                    -> cp_db -> cutover -> verify -> signoff

Independent branches after clone:
  Branch A (code):     prepare -> adop clone -> fix+regress -> cutover
  Branch B (database): cp_db -> sql_update
  Branch C (docs):     pre-flight checklists, training material
```

```
Critical path (branch A is longest):
  backup 4.5 + clone 3.0 + patch 2.5 + prepare 2.5 + clone_code 1.8
         + fix+regress 6.0 + cutover 0.8 + verify 1.5 + signoff 2.0
  = 22.6 h   (branch B runs inside branch A)

With 2 engineers on fix+regress (regression suite parallelises):
  fix+regress: 6.0 -> 3.4 h
  Critical path: 20.0 h
  Critical path with 4 engineers: 19.2 h  (regression suite is the floor)

Elapsed: 19.2 h   vs   downtime: 2.3 h
```

```
Speed-up from adding people:
  1 engineer: 22.6 h
  2 engineers: 20.0 h  (1.13×)
  4 engineers: 19.2 h  (1.18×)

Diminishing because regression execution, not fixing, is serial
(the suite must run against a stopped copy).
```

## 3. Regression Suite Sizing

```
Customisations in the estate:              18
  Reports and forms:                         8
  Interfaces (in/out):                       6
  Workflows:                                 2
  Custom packages:                           2

Test cases per customisation (average):     11
Total test executions:                18 × 11 = 198
Mean execution time:                          4.2 min
```

```
Sequential suite:  198 × 4.2 = 831.6 min = 13.9 hours
Parallel (8 testers, copy per tester):
                  831.6 / 8 = 103.9 min = 1.7 hours

Required to fit the cutover window (2.3 h = 138 min):
  1.7 h at 8-way parallelism  -> fits with 34 min of margin
  Sequential                   -> does not fit by 11.6 hours
```

| Parallelism | Suite duration | Fits 138-min window? |
|-------------|----------------|----------------------|
| 1 | 13.9 h | No |
| 4 | 3.5 h | No |
| 8 | 1.7 h | Yes |
| 12 | 1.2 h | Yes, 62 min margin |

**The window forces the parallelism, not the other way round.** Choosing a
parallelism level that cannot fit the window is how teams discover that they need
a 14-hour outage.

## 4. ADOP and the Custom Code Long Tail

```
Customisations:                18
Directly affected by ADOP:      6   (forms on the app tier, OAF, custom packages)
Not affected:                   8   (reports run from the DB tier)
Needs review:                   4   (anything touching deprecated APIs)
```

```
Deprecated API exposure:
  Deprecated packages in the estate:        6
  Call sites:                            2,140
  Custom code call sites:                   384  (18%)
  Total:                                 2,524

  ADOP impact on those 384:
    Compile errors during adop clone:      147  (38.3%)
    Runtime behaviour changes:              61  (15.9%)
    No impact (deprecated but functional): 176  (45.8%)
```

```
Compile-error remediation:
  147 sites × 40 min average (find the replacement, change, retest)
  = 5,880 min = 98 hours of developer work
  Spread over 4 developers: 24.5 hours

  This is the number that decides the upgrade date.
  Not the patch download. Not the adop duration.
```

**ADOP changes the runtime root, which invalidates compiled custom code that
lives in the app tier.** Any plan that does not budget 98 hours of remediation
is not a plan.

## 5. Database Version Upgrade — 11g to 19c

```
Target: 11.2.0.4 -> 19c on a 2-node RAC, 2 TB database

Step                          Duration
Pre-upgrade report (CPU)          0.3 h
Restore to new home                2.8 h
datapatch (all patches)            4.6 h
Remove deprecated components       1.2 h
Run utlrp.sql (recompile invalid)  1.9 h
Post-upgrade checks                1.1 h
-------------------------------------
Sequential total:                 11.9 h
```

```
Parallelisation:
  RAC-wide steps (datapatch, utlrp) run on both instances in parallel:
    datapatch:   4.6 h  -> 4.6 h  (patching 2 instances: no saving, it is per-instance)
    utlrp.sql:   1.9 h  -> 1.1 h  (2 instances in parallel, 42% saving)

  Critical path: 11.9 - 0.8 = 11.1 h
  Downtime:      the restore is on a NEW home; production runs on the old one
                 until cutover: 0 h
```

```
The 8-hour target (from the theory):
  Achievable only if the OLD instance stays up during the upgrade:
    Cutover = DNS/vip switch + connection drain, ~15 min
    Upgrade happens on a restored copy while production serves

  If you take production down for the upgrade:
    11.1 h  ->  breaks the 8-hour target by 3.1 hours
```

**This is the single most important scheduling decision in a version upgrade:
whether the old instance keeps serving.** It is a licensing, storage, and
network question that must be answered before the plan is written.

## 6. RTO and RPO Mathematics

```
Business requirement:
  Tier-1 business functions (order entry, payroll run):   RTO 2 h, RPO 15 min
  Tier-2 (reporting, GL inquiry):                          RTO 8 h, RPO 24 h
  Tier-3 (historical analytics):                          RTO 24 h, RPO 7 days
```

```
Options against those targets:

  Option                                     RTO      RPO     Meets T1?
  ------------------------------------------------------------------
  In-place upgrade with rollback             11.1 h   15 min  NO (5.5× over)
  Blue/green with DNS cutover                0.25 h   5 min   YES
  Blue/green with Data Guard promotion       0.5 h    0 min   YES
  Full restore from backup                   9.4 h    24 h    NO
```

```
Blue/green cutover arithmetic:
  Drain existing sessions:                 15 min  (Forms must be closed cleanly)
  DNS / VIP switch:                         2 min
  Application tier revalidation:            5 min
  Smoke tests:                             10 min
  ------------------------------------
  Total RTO:                               32 min   vs 120 min target -> 3.75× margin

  RPO with Data Guard (async):
    Typical apply lag: 1-5 s  ->  RPO in practice: seconds, not 15 minutes
    Maximum observed during month-end batch: 120 s  ->  RPO 2 minutes
```

**RPO is the interval between the last committed change and the last replicated
change.** With Data Guard that is the apply lag, not the backup interval — which
means the backup schedule does not determine RPO at all when Data Guard is running.

## 7. Rollback Duration — The Missing Number

```
Rollback options and their durations:

  Application tier rollback (redeploy old scripts from a filesystem snapshot):
    Duration: 12 min
    Data impact: none (no data conversion yet at this stage)
    Reversible: yes

  Database rollback (restore from pre-upgrade backup):
    Duration: 9.4 h
    Data impact: all post-backup transactions lost
    Reversible: no (requires accepting the data loss)

  Database rollback with flashback database:
    Duration: 25 min to the point-in-time before the upgrade
    Data impact: transactions since that point are lost
    Reversible: yes, within the flashback window
```

```
Flashback window sizing:
  Undo retention at upgrade: 4 hours
  Flashback retention target:    72 hours

  Requirement: rollback within the RTO of 2 hours from the moment of failure
  Flashback must therefore retain at least: 2 h + detection time (30 min)
                                          = 2.5 hours

  72 h retention vs 2.5 h required = 28.8× more than necessary
  Storage cost of 72 h vs 2.5 h on a 2 TB database:
    Undo growth rate at month-end: ~18 GB/hour
    72 h:  1,296 GB of undo required  -> exceeds a sane undo tablespace
    2.5 h: 45 GB  -> feasible

  Correct answer: 6 h flashback retention, 4 h undo retention.
  Enough for the RTO with margin, without reserving a terabyte of undo.
```

**Rollback planning is where most upgrade plans are silent.** A plan with no
measured rollback duration has an RTO of "unknown", which is not an answer.

## 8. Load-Time vs Commit-Time Profile — Finding the Bottleneck

```
The same profile-ratio technique used in the financials lab applies to upgrade
batch processing. Sample a 30-minute window of the post-upgrade
upgrade-detection script on the cloned database:

  Commit intervals (s):     0.4  0.3  0.5  0.3  0.4  1.2  0.4  0.3
                            0.4  0.3  58.1  0.4  0.3  0.4  0.5  0.3
  Mean:                     3.96 s
  p50:                      0.4 s
  p99:                      48.8 s
```

```
Tail ratio: p99 / p50 = 48.8 / 0.4 = 122×

The 58.1-second commit is not slow SQL. It is a checkpoint or a log switch:
  Elapsed = 831 s
  Time in the tail: ~72 s  = 8.7% of elapsed
  Commits: 16  ->  throughput 16 / 831 = 0.019 commits/sec

Diagnosis: redo log switches during the run.
Fix: resize the logs for the run, not a permanent change:
  Peak redo: 62 MB/s
  15-minute target: 62 × 900 = 55,800 MB = ~56 GB across 3 group logs
  Current: 3 × 1 GB = 3 GB  -> 62 switches/hour
  Resized: 3 × 20 GB = 60 GB -> 3.7 switches/hour
```

```
Time saved: 72 s tail -> 9 s tail = 63 s of a 831 s run (7.6%)
Small in absolute terms, but the same log sizing applies to every post-upgrade
batch, and there are hundreds.
```

## 9. Data Migration Duration — Volume and Rate

```
Data migration, EBS on-premises -> Cloud (EBS Cloud / Compute):

  Data sets and volumes:
    GL balances (current + prior 4):        1.8 TB
    Subledger transactions (5 years):       2.4 TB
    Inventory / transactions:               1.1 TB
    Custom tables:                          0.3 TB
    Media and attachments:                  0.4 TB
                                       ------
    Total:                                  6.0 TB
```

```
Effective throughput for each method:

  Method                        Throughput          6 TB duration
  ---------------------------------------------------------------------
  Export/import (legacy R12)     42 MB/s           6.0e6 MB / 42
                                                        = 142,857 s = 39.7 h
  Database Link + insert/select  68 MB/s           88,235 s = 24.5 h
  GoldenGate / Data Pump         95 MB/s           63,158 s = 17.5 h
  Cross-attach + clone + refresh  180 MB/s          33,333 s =  9.3 h
  ---------------------------------------------------------------------
  Read + write amplification (cross-attach):
    Clone:  6 TB once
    Refresh: delta of 1.4 TB (7 days of changes)
    Total:  7.4 TB / 180 MB/s = 41,111 s = 11.4 h
```

```
Chained vs parallel:
  Chained (6 data sets serialised):   39.7 h  (export/import)
  Parallel, 3 streams, ~50% contention penalty:
    39.7 / 3 × 1.5 = 19.9 h

  Cross-attach, 6 data sets parallel:
    Longest single set: GL 1.8 TB + refresh = 2.2 TB / 180 MB/s = 3.4 h
    Total: 3.4 h + final delta (7 min) + verification (2 h) = 5.7 h
```

```
Reduction: 39.7 h -> 5.7 h = 7.0×
The difference is entirely the method. Volume is identical.
```

**Migration duration is a throughput selection, not a volume problem.** Any plan
that starts with "we have 6 TB, so it will take 40 hours" has already chosen the
worst method without knowing it.

## 10. Migration Verification Mathematics

```
Row counts alone prove nothing: a table can have the right count and the wrong
contents. Verification must be content-based.

  Checksums (the only content-level proof):
    Checksum over 6.0 TB at 240 MB/s (MD5, single stream):
      6,144,000 MB / 240 = 25,600 s = 7.1 h

    Parallel across 8 streams:
      7.1 / 8 = 0.89 h
```

```
Three-way verification per table:
  Row count match
  Checksum match
  Sample-value comparison on business keys (spot check, 0.1% of rows)

  Tables: 2,140
  Checks per table: 3
  Total assertions: 6,420

  Mismatch rate if the migration is correct: 0
  Mismatch rate with one missed LOB column: typically 0.3-1.2% of tables
    = 6 to 26 tables silently wrong
```

**Row counts verify that data arrived; checksums verify that it is the same
data.** Anything less than a checksum on every table is a hope, not a
verification.

## 11. Batch Concurrency During Migration

```
Post-migration EBS workloads run concurrently with legacy:
  Legacy batch:                 8 workers
  Migration refresh process:    1 worker
  New environment batch:        6 workers
  Reporting on both:            4 concurrent sessions

Concurrent program processing on the new home: 14 workers
Rule: workers <= min(cores × 0.7, distinct data partitions)
      16 cores × 0.7 = 11  ->  min(11, partitions) = 11
```

```
Using 14 workers on 16 cores (87.5% of cores for CM alone):
  CM alone wants 87.5% of CPU
  Plus the HTTP/Forms tiers, the refresh job, and the database writers
  Total demand: > 100%  ->  every program slows, and failures increase

  Correct: 11 CM workers, refresh in its own dedicated service
  Overlap window where both run: 4 h (the refresh)
  CM utilisation during the overlap: 11 / 11 = 100% of the allocation
  -> schedule the refresh to finish before the period-close batch starts
```

```
Overlap rule that falls out of this:
  migration_refresh_window + batch_window + verification < maintenance_window
  4 h + 6 h + 2 h = 12 h  ->  a 12-hour maintenance window, not 6
```

## 12. Upgrade Before/After

| Measure | Sequential / legacy | Optimised | Change |
|---------|---------------------|-----------|--------|
| Elapsed upgrade duration | 27.5 h | 19.2 h | 1.43× |
| User downtime (unoptimised) | 27.5 h | 2.3 h | 12× |
| User downtime (blue/green) | — | 0.53 h | 52× |
| Regression suite | 13.9 h sequential | 1.7 h at 8-way | 8.2× |
| ADOP remediation | unbudgeted | 98 h / 4 devs = 24.5 h | budgeted |
| 11g→19c elapsed | 11.9 h | 11.1 h | with prod up |
| Tier-1 RTO (2 h) | missed by 5.5× | met with 3.75× margin | meets |
| RPO (15 min required) | 15 min | 2 min max during batch | meets |
| Rollback duration | unknown | 12 min (app) / 25 min (flashback) | known |
| Flashback retention | 72 h (1.3 TB undo) | 6 h (108 GB) | 12× less storage |
| Migration duration (6 TB) | 39.7 h | 5.7 h | 7.0× |
| Content verification | row counts | checksums, 6,420 assertions | actual proof |
| CM workers during overlap | 14 on 16 cores | 11, refresh separated | no oversubscription |

Every one of these is a number that could have been different. The point of the
lab is not the upgrade — it is that upgrade planning is arithmetic, and the
arithmetic is usually done after the window is booked rather than before.
