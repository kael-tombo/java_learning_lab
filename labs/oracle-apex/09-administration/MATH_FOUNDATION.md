# Lab 09: APEX Administration — Math Foundation

## 1. Provisioning Math — Identity, Schema, Quota

```
New application request:
  Users:              40 named, 600 potential
  Named user accounts provisioned:  40
  Authentication scheme:            internal (SSO planned in phase 2)
  Accounts per named user:          1

Account-to-user ratio: 40 / 600 = 6.7% provisioned
```

**Provisional accounts for the other 93% is a deliberate risk decision.** Each
unmanaged shared account is an unattributable actor in the audit trail:

```
Audit attribution with shared accounts:
  Actions/day:              86,400
  Actions through shared accounts:  21,600  (25%)
  Actions attributable to a named person:  64,800  (75%)

After SSO:
  Attributable actions:  100%
  Unattributable:         0
```

## 2. Session State and Memory Budget

```
Average session state per session:     14 KB
Sessions per workspace:                 1,400 peak
Workspace state total:                 1,400 × 14 KB ≈ 20 MB

APEX instance with 8 workspaces:       160 MB of session state
+ parse cache + cached query results:  ~2 GB typical
```

| Workspace | Sessions | State | Notes |
|-----------|----------|-------|-------|
| Production finance | 1,400 | 20 MB | Peak-hour |
| Production ops | 900 | 13 MB | Shift-based |
| Training | 4,000 | 56 MB | Large collections |
| Sandbox × 5 | 50 each | ~4 MB | Idle mostly |

```
Retention drives capacity, not concurrency:
  120-minute timeout, 2,880 sessions/day/workspace:
    average concurrent = 2,880 × 35 min / 120 min = 840
  Reducing the timeout does NOT reduce peak concurrency,
  it increases login churn. Peak concurrency is a demand fact.
```

## 3. Session Timeout Math for Each Tier

```
Workspace            Timeout   Working session   Abandoned   Overhead
Finance (production)   120 min    35 min           15%         37.7%
Ops (24×7 shifts)       240 min    90 min            8%         21.7%
Training                60 min     20 min           30%         43.8%
```

```
Overhead = (abandoned × timeout) / (abandoned × timeout + active × working)

Finance:  (432 × 120) / (432 × 120 + 2448 × 35) = 37.7%
Ops:      (184 × 240) / (184 × 240 + 2484 × 90) = 16.4%
Training: (1,296 × 60) / (1,296 × 60 + 2016 × 20) = 65.9%
```

**Training sessions abandon far more often and should be timed aggressively.**
A 60-minute timeout on a 20-minute working session wastes nothing real and
reclaims two thirds of the retention.

## 4. SoD Coverage Across All Workspaces

```
Total internal roles:            14
Privileged roles:                 6
Users with a privileged role:    12
Conflicting role pairs defined:  9

Assignments blocked by role design:       34 of 48
Assignments blocked by role + page auth:  43 of 48
Assignments blocked by role + page + VPD: 48 of 48

Coverage: 70.8%   ->   89.6%   ->   100%
```

```
Residual exposure at 70.8% coverage:
  14 unblocked assignments
  Users affected: ~9  (6.7% of the 130 internal users)
  Privilege reachable: AP approve own requests, 2 privileged roles
```

```
Coverage must be reported per workspace, not per instance:
  Finance: 100%
  Ops:     89.6%   <- 5 unblocked, all in the report-export role
  Sandbox: 0%      <- sandbox has no controls at all, by design
```

**An instance-wide 100% that includes a sandbox with 0% is a misleading number.**
Report the worst workspace, not the average.

## 5. Password Policy Arithmetic

```
Policy: 12 characters, 3 of 4 classes, no rotation, breach-list check

Effective entropy (order-of-magnitude):
  alphabet ~94 chars, ~70^12 typical human choice patterns
  ≈ 10^21 - 10^23

Online attack budget:
  Rate-limited login endpoint: 5 attempts / 15 min / account
  Attempts per day per account: 480
  Accounts: 640
  Daily guesses: 307,200
```

```
Time to exhaust a 10^21 space:
  10^21 / 307,200 per day = 3.3 × 10^15 days ≈ 9 × 10^12 years

Offline attack against a leaked hash is a different problem:
  SHA-1, 10^10 hashes/sec on a GPU rig:
  10^21 / 10^10 = 10^11 sec ≈ 3,200 years  -> still infeasible
  WITHOUT a breach-list check, the human-choice space is ~10^17:
  10^17 / 10^10 = 10^7 sec ≈ 3.3 hours  -> trivially cracked
```

**The breach-list check is what makes the password policy meaningful.** Length
and complexity give a large theoretical space; the breach list removes the
predictable part of it. Rotation, by contrast, mostly produces `Autumn2026!`.

## 6. Monitoring — Ratio-Based Alerts

```
Baseline per workspace:
  page views/hour (peak):      6,000
  SQL time / page:                180 ms
  p95 page time:                 940 ms
  session timeouts/hour:           12
  failed logins/hour:               4
```

| Signal | Alert condition | What it means |
|--------|-----------------|---------------|
| p95 page time | > 2,000 ms sustained 10 min | regression or data growth |
| Failed logins | distinct accounts > 50 with < 3 tries each | **spray attack** |
| Failed logins | one account with > 10 tries | credential stuffing |
| Session timeouts | > 5× baseline | auth failure loop |
| Workspace parse errors | any | broken app after deploy |
| Avg SQL per page | > baseline + 3 | region added without review |

```
Spray detection arithmetic:
  ratio = failures / distinct_accounts
  spray:   480 failures / 480 accounts = 1.0  (few tries each, wide)
  stuff:   480 failures /   4 accounts = 120  (many tries, narrow)
  typos:     4 failures /   4 accounts = 1.0  (baseline, tiny volume)

  Alert: ratio > 5 AND failures > 50 AND distinct_accounts > 20
  The volume term is what suppresses the typo baseline.
```

## 7. Password Policy Enforcement Cost

```
Failed logins caused by expiry misconfiguration:
  users:                  640
  wrong password policy:  a setting requiring change at every login
  affected per day:       ~120 (those who did not read the notice)

Lockout incidents from policy:
  30-minute lockouts:  14/day
  Admin unlocks:        14 × 2 min = 28 min/day of admin time
```

```
Policy change rollout:
  users notified:            640
  compliance within 1 week: ~480  (75%)
  non-compliant remaining:  160  (25%)

If those 160 are locked out on day 8, you have an outage of 25% of your
user base caused by a configuration change, not by an attack.
```

**Staged enforcement (warn, then enforce after a grace window) is the only safe
sequence.** Immediate enforcement converts a security improvement into an outage.

## 8. Row-Count-Driven Cost Across an Instance

```
Regions in the estate:                 412
Pages:                                 168
Estimated SQL per page render:         regions + 1 COUNT per IR
                                       ≈ 5.3 average

Page renders/day across all workspaces: 240,000
SQL executions/day:                    240,000 × 5.3 ≈ 1,272,000
```

```
Mean SQL time per execution:            18 ms
SQL time per day:                       1,272,000 × 18 ms = 22,896 s ≈ 6.4 CPU-hours
Peak hour share:                        15% of requests
Peak hour SQL time:                     3,435 s ≈ 95% of one CPU's second — trivial
```

```
The estate is not close to a database capacity limit.
Capacity planning is therefore driven by data growth, not traffic:

  orders table growth: 1.2M rows/year
  After 3 years:      3.6M rows
  Unindexed month filter cost: ~1.2 s -> ~3.6 s
  Page SLA:            2 s
  Breach date:         ~2 years after the last index review
```

**Capacity is reached by rows accumulating, not by users arriving.** The metric
to watch is rows per table, and the control is index review frequency.

## 9. Backup and Restore Duration

```
APEX application export (YAML):
  168 pages, ~2,400 regions:   ~4.2 MB
  Export time:                 ~11 s
  Import time:                 ~14 s
  Rollback by re-import:       ~14 s

Database backup (RMAN):
  2 TB database, 6-hour window:
    Full backup:      ~5.2 hours  (fills most of the window)
    Incremental:      ~18 min
```

```
Recovery scenarios:

Application rollback (YAML re-import):
  RTO: ~15 s          RPO: 0        <- always available

Single page reverted (app was exported at deploy time):
  RTO: ~5 s           RPO: 0

Schema rollback (table dropped):
  RTO: hours (restore + reconcile)   RPO: up to 24 h without flashback
  With flashback query:
    RTO: ~20 min      RPO: minutes   <- flashback query is the practical answer
```

```
Never rely on the database backup to revert an application change.
The export is the only fast, exact rollback path, which is why it belongs in
source control from the first commit.
```

## 10. Patch Cycle Math

```
Critical CVEs in the last 12 months affecting APEX:  4
Median days from disclosure to a working patch:     21

Patch test environment effort:      3 days (smoke + regression)
Production change window:            1 hour (Sunday 02:00)
Regret window if not patched:       ~15 days average

Patch compliance target: 100% within 30 days
Achievable: 21 + 3 = 24 days    -> inside target with 6 days of margin
```

```
Risk exposure:
  Days unpatched under a 15-day median: 4 CVEs × 15 = 60 CVE-days
  Days unpatched at the current rate:   4 CVEs × 24 = 96 CVE-days
  Reduction from a standing patch pipeline: 36 CVE-days per year
```

## 11. Workspace Provisioning Cost

```
Manual provisioning (current):
  Create workspace:            15 min
  Create schema + grant:        10 min
  Configure authentication:     20 min
  Create parse-as user:         10 min
  Configure session timeouts:    5 min
  Verify with a smoke test:     15 min
  Total:                        75 min per application

Requests per quarter:           6 applications, 3 environments each = 18
Manual effort:                  18 × 75 min = 22.5 hours/quarter
```

```
Scripted provisioning:  ~8 min per application
18 × 8 min = 2.4 hours/quarter

Saving: 20.1 hours/quarter = 80 hours/year
Error rate, manual:  ~1 in 8 provisioning runs leaves a misconfiguration
Error rate, scripted:  ~1 in 200, and the script is reviewable
```

```
Probability of at least one misconfiguration per year (manual):
  1 - (1 - 0.125)^72 = 99.99%

Probability with a reviewed script:
  1 - (1 - 0.005)^72 = 30.2%

Most of the value is not the hours saved. It is the error rate.
```

## 12. Administration Before/After

| Measure | Before | After | Change |
|---------|--------|-------|--------|
| SoD coverage (worst workspace) | 70.8% | 100% | +29.2 pp |
| Unattributable audit actions | 25% | 0% | full attribution |
| Provisioning time | 75 min | 8 min | 9.4× |
| Provisioning error rate | 12.5% | 0.5% | 25× lower |
| Password-policy rollout risk | outage | staged | 0 incidents |
| CVE-days per year | 96 | 60 | −36 |
| Session retention overhead (training) | 65.9% | 22.0% | −43.9 pp |
| Application rollback RTO | hours | 15 s | 240× |

Administration is measured the same way as everything else in this lab: as a
ratio or a duration, with a before and an after. "We have patched it" is not a
metric; "36 CVE-days per year" is.
