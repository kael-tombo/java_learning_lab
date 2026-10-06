# Lab 01: EBS Multi-Tier Architecture (HA, Load Balancing, Failover) — Math Foundation

## 1. Connection Pool Sizing — Little's Law

```
Little's Law:  concurrency = throughput × time_in_system

Forms users:
  Peak-hour concurrent users:            1,200
  Clicks per user per hour:                60
  Requests per hour:                1,200 × 60 = 72,000
  Requests per second:                      20

Time in system (Forms form request):
  DB query:                180 ms
  Forms record processing: 120 ms
  Network + app tier:       35 ms
  Total:                    335 ms

Required database connections = 20 × 0.335 = 6.7
```

**Peak Forms concurrency at the database is under 10 sessions.** Pool sizing from
concurrent users is a category error: a user holds a connection for 335 ms, not
for an hour.

### Pool sizing by workload type

```
Workload                 Connections   Derivation
Forms (20 rps, 335 ms)        7       20 × 0.335
OAF self-service (8 rps)      6       8 × 0.75
Concurrent Manager (8 workers) 8       one per worker
Batch/monitoring (2 rps)       2       2 × 1.0
Admin reserve                  3       reserved for break-glass
                                    ---
Total pool:                   26
```

```
Failure test: one RAC instance lost -> 26 become 26 against one instance.
Headroom rule: pool_max = sum(per-workload) × 1.5 + admin reserve
  26 × 1.5 = 39 + 3 = 42
```

```
Sessions per instance under RAC (2 instances, 26 pooled + per-OS children):
  26 pooled services + ~30 OS-authenticated children + 4 admin = ~60
  RAC two_thread_policy = PARALLEL  -> logical CPU count = 2 × 30 = 60
  60 sessions / 60 threads = 1.0  -> no queueing headroom

  Fix: sessions_per_user = 30 (not the default 50) or reduce threads
```

## 2. Load Balancer Pool Math

```
F5 BIG-IP, HTTP pools, node pool of 4 web/app servers

Connections per node = ceil(pool_minimum / node_count)
```

```
Pool: ebs_forms_pool, pool_minimum = 400
  400 / 4 nodes = 100 per node

Pool: ebs_oaf_pool, pool_minimum = 300
  300 / 4 nodes =  75 per node

Pool: ebs_cm_pool (internal, Concurrent Manager)
  pool_minimum = 20, monitor = /pls/fndlpls/ping   (must NOT be load balanced)
  20 / 4 = 5 per node
```

| Pool | Minimum | Nodes | Per node | Monitor |
|------|---------|-------|----------|---------|
| ebs_forms_pool | 400 | 4 | 100 | `/pls/fndlpls/ping` |
| ebs_oaf_pool | 300 | 4 | 75 | `/pls/fndlpls/ping` |
| ebs_cm_pool | 20 | 4 | 5 | `/pls/fndlpls/ping` |

```
Rule: Concurrent Manager traffic must be pinned, not balanced.
  The Concurrent Manager re-registers its worker sessions on a specific host.
  Load balancing across nodes breaks session affinity for long jobs
  (a 6-hour job that reconnects to a different node loses form state).
```

## 3. Failover Time Budget

```
Database failover (Data Guard, Maximum Availability/Zero Data Loss):
  Detection:              max(10 s heartbeat, 30 s background)
  Failover:               15-30 s (RAC, no application-tier retries)
  Application reconnect:  8-15 s (Forms self-reconnect, OAF does not)
  Total DB failover:       33-75 s

Application tier failover (scripted, F5 pool disable/enable):
  Detect node failure:      5 s (HTTP monitor, 3 consecutive failures)
  Disable node:             2 s
  DNS/vip change:           1-5 s
  F5 health check recovery: 10 s
  Total app failover:       18-23 s
```

```
Observed failure times and user impact:

  Failure                Time        Impact on 1,200 users
  DB failover            55 s        all users see a 55 s error; Forms self-reconnect
  App tier node loss     22 s        users on that node error; others unaffected
  Load balancer loss     N/A (pair)  none if HA pair; 30-120 s if single

  Monthly availability budget: 99.9% = 43.2 min of downtime/year
  One 55 s failover per quarter = 220 s/year = 0.3%  -> 99.7%, misses the target
```

```
To hold 99.95% (21.6 min/yr):
  One failover per quarter at 55 s = 220 s  -> fits
  One failover per MONTH at 55 s    = 660 s  -> still fits
  Failover time budget: 21.6 min / 12 per year = 108 s per failover allowed
```

**The failover budget is a derived number.** "How fast must failover be?" is
answered by the availability target divided by the number of failures you expect.

## 4. Concurrent Manager Sizing

```
Workload profile (peak month, month-end close):
  Programs scheduled:                     420
  Average run time:                       8.5 min
  Programs that must finish before 06:00: 260
  Window:                                6 hours = 360 min

Single-threaded capacity:
  360 / 8.5 = 42 programs per worker per window
```

```
Required workers = 260 / 42 = 6.2 -> 8 workers (round up, keep a margin)

Dedicated workers:
  Payables / GL / Close:     4 workers
  Inventory / Supply Chain:  2 workers
  Custom integration jobs:   2 workers
  Total:                     8
```

```
Queue depth check:
  Programs scheduled in the 6-hour window: 260
  With 8 workers × 42 capacity = 336 slots
  Utilisation: 260 / 336 = 77.4%

  At 90% utilisation, queueing theory says the wait time
  explodes — plan for < 80%.
```

```
Retry and stuck-request cost:
  ORA-00001 / deadlock on a PO submit:
    affected programs per month:       38
    average rerun time:                11 min
    wasted worker-minutes:  38 × 11 = 418 min/month
    Capacity consumed: 418 / (336 × 30) = 4.1% of monthly capacity
```

**4% of worker capacity lost to retries is invisible until a month-end deadline.**
It must be measured, because adding workers costs real money and hiding the retry
rate hides the actual bug.

## 5. Forms Performance — Query Time Dominance

```
A single form query over 5M-row gl_balances with a 90-day period filter:

  No index on (ledger_id, period_name):
    Full scan + filter:                 5,000,000 rows read   ~2,900 ms
  Index on (ledger_id, period_name, account_id):
    Range scan:                            ~185,000 rows read   ~95 ms
```

```
Ratio: 30×

Non-sargable period filter:
  WHERE TO_CHAR(period_name) = 'SEP-26'
    Rows read: 5,000,000    -> ~3,200 ms   (function on the indexed column)

  WHERE period_name BETWEEN 'SEP-26' AND 'SEP-26'
    Rows read:   185,000    -> ~95 ms
```

```
A 3,000 ms form query at 20 rps peak:
  20 × 3.0 s = 60 concurrent form requests demanded
  Pool of 7 connections = 7 concurrent
  Queue: 53 requests waiting, at 180 ms service time -> ~1,500 ms extra latency

  Fixed (95 ms):
  20 × 0.095 = 1.9 concurrent  -> fits the pool of 7 with room to spare
```

## 6. Bind Variables and Plan Stability on the App Tier

```
Forms/OAF send literal values in generated SQL far more often than developers
realise, because the SQL is built at runtime from form parameters.

Per user per hour: 60 requests, each with 2-3 parameterised predicates
Distinct combinations per hour: ~18,000 across all users
```

```
Literal variant cost:
  18,000 distinct statements × 4 KB cursor = 72 MB of library cache
  18,000 hard parses × 1.8 ms = 32.4 s of parse CPU per hour

Bind variant:
  ~20 distinct statements (the real query shapes) × 4 KB = 80 KB
  20 hard parses × 1.8 ms = 36 ms of parse CPU per hour
  Remaining executions are soft parses at ~0.02 ms

  72 MB vs 80 KB -> 900× smaller library cache footprint
  32.4 s vs ~0.4 s parse CPU -> 80× less parse work
```

**In EBS this is not theoretical.** A Forms form with a where-item generates SQL
per session; across 1,200 users the library cache fills with statements that can
never be shared, and instance-wide performance degrades with no code change.

## 7. Data Guard Lag and Its Business Cost

```
Typical lag under normal load:        < 1 second
Lag during a month-end batch spike:   15-120 seconds
Standby apply lag with heavy redo:    up to 300 seconds (apply lag warnings)
```

```
Cost of lag during a failover:
  Data lost (RPO) = redo generated during the lag window
  Month-end close, 40,000 GL journals/minute peak, ~180 bytes each:
    15 s of lag  -> 1,000 journals    -> ~$4.2M of journal detail unrecoverable
    60 s of lag  -> 4,000 journals    -> ~$16.8M
    120 s of lag -> 8,000 journals    -> ~$33.6M

  With ASYNC standby (1-5 s typical lag):
    Max exposure at 5 s -> 200 journals -> ~$840,000
```

| Protection | Typical lag | Max RPO at peak | Exposure |
|-----------|-------------|-----------------|----------|
| Maximum Availability (sync) | 0 s | 0 | $0 |
| Maximum Performance (async) | 1-5 s | ~$840K | bounded |
| Async + apply lag alerting | 1-120 s | ~$33.6M | alerted, not prevented |

**"Zero data loss" is a measurable claim, and the measurement is the standby
apply rate against the primary redo rate.** Anything less is a stated RPO.

## 8. FS_CLONE and Rolling Cutover Duration

```
adop phases and typical durations for a 12.2.6 -> 12.2.7 patch (18 customisations):

  adop prepare:        2.5 hours
  adop clone:          1.8 hours
  adop cutover:        0.8 hours   (the downtime window)
  adop postpatch:      1.2 hours
  Total elapsed:       6.3 hours
  User downtime:       ~50 minutes (cutover only)
```

```
Rolling cutover across 2 regions to keep users on the unpatched clone:

  Region 1 available on patched clone:  hours 0-3
  Region 2 cutover:                     hours 3-3.8
  Both regions on new version:          hour  4.6
  Regional overlap required:            1.6 hours

  Downtime for a user:                  50 min (their region's window)
  Users affected at any moment:         50% of the workforce
  vs single cutover:                    100% of the workforce, 50 min
```

```
Planning the cutover window from the regression suite:
  Customisations:                  18
  Regression tests per customisation: 11 avg
  Total test executions:            198
  Average test duration:            4.2 min
  Sequential suite:                832 min = 13.9 hours

  Parallel with 8 testers:          104 min = 1.7 hours
  Must fit inside the cutover window: 50 min
  -> Cannot fit. Either extend the window to 2 hours or parallelise to 12.
```

**Cutover window sizing is a scheduling derivation, not a preference.** A
regression suite that does not fit the window is a cutover that ships untested.

## 9. NFS and Runtime Filesystem Performance

```
EBS runfile on NFS (common misconfiguration):

  Runtime file reads per form request:    ~340
  On local disk, cached:                  ~0.1 ms each -> 34 ms
  On NFS, uncached, stat + open per file:  ~0.9 ms each -> 306 ms
```

```
Uncached NFS runtime cost:
  Per form request:  306 ms of filesystem time
  Per session (25 requests):  7.65 s
  At 20 rps peak:  20 × 306 ms = 6.1 concurrent-equivalent seconds of I/O
  On the app tier's 4 nodes with 8 cores each: ~19% of CPU-equivalent on stat()
```

```
With noatime + larger rsize/wsize:
  stat() calls eliminated:       ~55% of runtime file metadata operations
  Bulk reads per request:        ~6 instead of ~12
  Per-request filesystem time:   ~90 ms  (from 306 ms)
  Form request total:            90 + 180 + 35 = 305 ms  (from 515 ms)
```

## 10. End-to-End Response Time Attribution

```
Forms request, 335 ms baseline:
  Network (client to LB):        15 ms
  Load balancer processing:        2 ms
  Web/app tier (Apache, WebAppDeployer): 35 ms
  Forms runtime + record triggers: 120 ms
  Database query:                 180 ms
                                      ---
  Total:                          352 ms

Sensitivity:
  Database query 180 -> 2,900 ms (missing index):
    Total 3,072 ms   = 8.7× worse, 94% of the time is SQL
  Database query 180 -> 95 ms (index added):
    Total 267 ms     = 1.3× better, SQL is now 35% of the time
  Forms runtime 120 -> 12 ms (records removed from a loop):
    Total 244 ms     = 1.4× better
```

```
Rule from the attribution:
  If SQL > 50% of response time, fix SQL. It always is in EBS.
  Forms record processing matters only after SQL is fixed.
```

## 11. Capacity by Data Growth

```
gl_balances current:                180,000,000 rows
Growth per year (posting volume):     42,000,000 rows

After 5 years:  390,000,000 rows
Full scan at 12 MB/s effective read throughput:
  180M rows ≈ 14.6 GB  -> ~1,220 s
  390M rows ≈ 31.6 GB  -> ~2,630 s
```

```
Indexed period-range query stays flat:
  Rows matching a 3-period range at 12 journals/row-set:
    ~1.5M rows both years -> ~95 ms

Unindexed date-range query degrades linearly:
  Year 1:  ~1,150 ms
  Year 5:  ~2,480 ms

Budget breach (2 s form-query SLA) with no new index:
  year 3.4
```

**EBS performance decays with data, not with users.** The capacity review that
matters is index coverage per data set, scheduled annually.

## 12. HA Before/After Summary

| Measure | Before | After | Change |
|---------|--------|-------|--------|
| DB connections sized from | concurrent users (1,200) | throughput × time (26) | 46× right-sized |
| RAC threads vs sessions | 1.0 (queueing) | 0.5 (headroom) | no queueing |
| Period-range form query | 2,900 ms | 95 ms | 30× |
| Library cache footprint | 72 MB | 80 KB | 900× |
| Application tier failover | manual, 4-6 hours | scripted, 22 s | 650× |
| DB failover user impact | 55 s, all users | 55 s, Forms self-reconnect | bounded |
| Concurrent Manager utilisation | 96% (queueing) | 77% | below the 80% threshold |
| Cutover downtime | 50 min, 100% of users | 50 min, 50% of users | halved blast radius |
| Uncached NFS runtime overhead | 306 ms/request | 90 ms | 3.4× |
| Regression suite in window | 13.9 h vs 50 min | 1.7 h at 12-way parallel | fits |

Every number above is derived from a throughput, a duration, or a row count —
which is what makes it arguable in a design review instead of merely assertive.
