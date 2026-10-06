# Lab 13: CI/CD Pipelines & Release Engineering — Math Foundation

Release engineering is risk arithmetic: how much is deployed, how fast, how long the rollback window is, and how long a lock is held. These are the numbers.

---

## 1. Blast radius as a function of rollout speed

```
fraction_of_traffic_on_new_version(t)   ≈ rollout_progress(t)
blast_radius = users_affected ≈ traffic_share_deployed × user_base
```

Canary steps, per service, 30,000 rps:

| Step | Share | rps on new | Users at risk (2M daily) |
|---|---|---|---|
| instant | 100% | 30,000 | 2,000,000 |
| 1% → 25% → 100%, 8 min each | during 1% | 300 | 20,000 |
| rolling, `maxUnavailable: 0`, 6 replicas, `maxSurge: 1` | 1/6 ≈ 17% | 5,000 | 333,000 |

**Conclusion**: a rolling update and a "1% canary, all the way to 100%" have the same total traffic but a very different *time-weighted* exposure. Total users affected by a rolling update that is wrong for 10 minutes is small; a canary that catches it in 8 minutes affects 0.8% of the change-window traffic. Risk is exposure × detection delay.

---

## 2. Rollout time and detection window

```
T_exposure = T_detect + T_decide + T_rollout_rest_of_fleet
```

Detection requires statistical power. For a canary, the minimum time to distinguish a real error-rate regression from noise:

```
n_min ≈ 16 × p(1−p) / δ²          (normal approximation for two proportions)
```

Baseline error rate `p = 0.001`, minimum detectable regression `δ = 0.004` (0.1% → 0.5%):
```
n_min ≈ 16 × 0.001 × 0.999 / 0.000016 = 999 ≈ 1,000 requests per variant
```
At `30,000 rps`, a 1% canary receives `300 rps` → `3.3 s` to reach `n_min`. But a latency comparison needs minutes, not seconds, because p99 needs volume in the tail bucket:

```
p99 needs ~100 samples in the 99th-percentile bucket
p99 bucket gets 1% of traffic  →  100 / 0.01 = 10,000 requests in the bucket → 100,000 total per variant
1% canary at 300 rps  →  333 s ≈ 5.5 min
```

So a defensible canary step is **~5 minutes at 1%**, which then inverts the earlier estimate. This is why canary step durations are set by the *tail* metric, not the mean.

---

## 3. Rollback window and the `expand-contract` timeline

```
schema_unsafe_window = time_from_first_app_release_using_new_schema
                       until_previous_release_is_no_longer_deployable
```

Policy: previous release stays deployable for 30 days.

| Day | Release | Schema state | Safe to drop old column? |
|---|---|---|---|
| 0 | R1: adds `new_col` (nullable), dual-writes | both columns | no |
| 7 | R2: reads `new_col` | both written, new read | no |
| 14 | backfill complete | both identical | no (R1 still deployable) |
| 30 | — | R1 removed from the deployable set | **yes** |
| 31 | R3: drop `old_col` | single column | — |

`DROP COLUMN` shipped at day 7 would break `rollout undo` for 23 days — the rollback *looks* available and is not. This timeline is the artefact a review must check.

---

## 4. Migration lock time and queueing

```
blocked_write_time = DDL_duration
queue_growth       = arrival_rate × blocked_write_time   (every query queues behind the lock)
```

`ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT 0` on a 400M-row table:
```
rewrite duration ≈ 8–40 min depending on version and hardware (verify for YOUR database)
at 4,000 writes/s, a 10-minute lock queues 4,000 × 600 = 2.4M queries
```
Connection pool exhaustion follows: each pooled connection blocks on the lock, so at 200 pooled connections, everything stalls and callers time out in seconds while the DDL is still running for minutes.

Safe form:
```
lock_timeout = '2s'        →  fail fast in 2s instead of queueing
ALTER TABLE orders ADD COLUMN new_col text;              -- nullable, metadata-only
CREATE INDEX CONCURRENTLY idx_orders_new_col ON orders(new_col);   -- non-blocking
```

Verification rule for reviews: **any DDL must come with a `lock_timeout` and a stated expected duration.**

---

## 5. Backfill rate

```
backfill_throughput = batch_size / (transaction_time + pause)
replication_lag_growth = write_lag_per_row × write_rate − apply_rate
```

`batch_size = 1,000`, `transaction = 300 ms`, `pause = 200 ms`:
```
throughput = 1,000 / 0.5 s = 2,000 rows/s
400M rows → 400e6 / 2,000 = 200,000 s ≈ 55 h  →  not acceptable in one release
```
Over 7 days it is fine (`55/168 = 33% duty cycle`). This is the number that determines whether a backfill is a release event or a multi-week project — and it should be computed *before* the code is written.

Replication impact: each row written to the primary is replicated; a backfill at 2,000 rows/s with 200-byte rows adds `400 KB/s` of WAL. If the replica apply rate is 300 KB/s, the backfill alone creates unbounded replication lag. **Verify replica capacity before starting.**

---

## 6. Pipeline latency budget

```
pipeline_time = queue_wait + Σ stage_duration(stage)   with parallelisable stages in max()
```

Badly ordered pipeline: 3 unit-test modules sequential, SAST, dependency scan, integration suite:
```
sequential = 2 + 2 + 3 + 4 + 8 + 6 = 25 min
```
Goodly ordered, parallel where independent, only blocking checks pre-merge:
```
pre-merge  = compile(2) + max(unit A 3, unit B 3, unit C 4) + max(SAST 4, SCA 2, secret 0.5) = 10 min
post-merge = max(integration 12, image build 4, deploy staging 3, smoke 2) = 12 min
total feedback to author = 10 min  (was 25)
```
The rule: **developer-blocking feedback = compile + unit + fast static analysis; everything else post-merge.**

Queue wait is frequently larger than execution. `p95(pipeline_total) = 42 min` with `p95(stage_sum) = 15 min` means you need more concurrency or smaller runners, not a faster build.

---

## 7. Release change-failure rate and lead time

```
change_failure_rate = failed_deployments / total_deployments
lead_time_for_changes = commit_to_production_time (median and p85)
time_to_restore = detect + decide + restore
```

Current: 40 deploys/month, 6 rolled back, `p85` lead time 3 days, TTR 95 min.
```
CFR = 15%
```

After progressive delivery:
```
canary_catches = P(regression is user-visible) × P(canary detects before 100%) ≈ 0.8 × 0.9 = 72%
rollback at 1–25% instead of 100%
deployments_reaching_100% = 40 × (1 − 0.72 × regression_rate)
```

Cost framing that survives a business conversation:
```
cost_of_a_rollback_event = engineering_hours × rate + customer_impact + trust
expected_value_of_canary = P(bad_release) × (blast_radius_at_100% − blast_radius_at_1%)
```

---

## 8. Feature flag accumulation

```
flag_count grows ~linearly; flag_removal is manual  →  flag_debt grows quadratically in cognitive cost
flag_combinatorial_states = Π (states_i)
```

4 flags with 2 states each = 16 combinations. 8 flags = 256. 14 flags = 16,384.

```
P(some untested combination exists in production) ≈ 1 − Π p_tested_i
with p_tested = 0.7 and n = 14:  1 − 0.7^14 = 99.97%
```

This is the quantitative case for flag expiry: every flag permanently multiplies the state space you cannot test.

---

## 9. Database connection budget during a rolling update

```
max_connections_during_rollout = replicas_max + maxSurge = R + 1
```

`R = 20` replicas, pool 10, `maxSurge: 1`:
```
peak connections = 21 × 10 = 210 vs 20 × 10 = 200 during steady state  (+5%)
```
Blue/green with full environment duplication:
```
peak = 40 × 10 = 400  (+100%)
```
Against a database with `max_connections = 250`:
```
rolling:   210 / 250 = 84%  →  feasible
blue/green: 400 / 250 = 160% →  cannot deploy without a pooler or more capacity
```
**Conclusion**: the deployment strategy has a database budget consequence that must be in the deployment decision, not discovered during it (Lab 06 arithmetic, applied to a release decision).

---

## 10. Rollback time budget

```
T_rollback = detect + decide + command + rollout_to_100%_old + verification
```

Pipeline with GitOps/Argo (digest revert) vs Helm/image-tag rollback:
```
image-tag rollback: detect 3 + decide 8 + command 1 + rollout 6 = 18 min
GitOps digest revert: detect 3 + decide 3 + command 1 + auto-sync 1 + verify 2 = 10 min
```
Two consequences:
1. A rollback path that takes 18 minutes needs a *shorter* detection path or a lower-risk rollout, because `T_exposure` includes it.
2. If `T_rollback > T_fixforward`, write the fix-forward path down in advance (who, how, in what order) and say so in the runbook.

---

## 11. Test suite economics

```
CI_minutes_saved_per_day = (unit_suite_minutes × runs/day) + (integration_suite_minutes × runs/day)
cost_per_minute = runner_minute_price
flaky_retry_cost = P(flake) × suite_minutes × runs/day
```

A 12-minute integration suite run 30×/day with 6% flake rate:
```
wasted = 0.06 × 12 × 30 = 21.6 min/day
developer_override_rate after repeated flakes = rises sharply
```
Quarantining the 3 known-flaky tests and removing the retry mask recovers ~20 min/day and, more importantly, restores trust. **Trust is the real currency: a pipeline people override has negative value.**

---

## 12. Canary SLO comparison

```
relative_increase = (canary_error_rate − control_error_rate) / control_error_rate
gate iff canary_error_rate > max(absolute_threshold, control × (1 + tolerance))
```

`control error rate = 0.10%`, `tolerance = 50%` relative, absolute threshold `0.5%`:
```
relative gate = 0.001 × 1.5 = 0.15%
absolute gate = 0.5%
→ effective gate = max(0.15%, 0.5%) = 0.5%
```

At 1% canary of 30,000 rps = 300 rps, a 0.5% error rate = 1.5 errors/s, so the gate trips within seconds of the true level. But a 0.15% canary error rate is only distinguishable after enough samples (§2), which is why the gate is `min_samples AND threshold`.

Latency gate (the one that matters for tail work):
```
gate iff canary_p99 > SLO_p99 × 1.25  OR  canary_p99 > control_p99 × 1.3
```
Dual condition: absolute (SLO-based, meaningful to users) and relative (catches regressions that are still inside the SLO).

---

## 13. Quick drills

1. Baseline error rate 0.1%, detect a +0.4 pp regression. Samples per variant? **Answer: ~1,000 (`16p(1−p)/δ²`). But p99 needs ~100,000 → ~5.5 min at a 1% canary of 30k rps.**
2. `DROP COLUMN` shipped 7 days after the last release that used it; rollback window is 30 days. **Answer: unsafe — `rollout undo` would break for 23 days. Move the drop to day 31.**
3. 400M-row backfill, batch 1,000, 500 ms cycle. Throughput and duration? **Answer: 2,000 rows/s → ~55 h. Plan as a multi-day job with a duty cycle.**
4. 4,000 writes/s, 10-minute DDL lock. Queries queued? **Answer: 2.4M. Use `lock_timeout` + nullable add + `CONCURRENTLY`.**
5. Pipeline stage sum 25 min sequential, parallelisable to 10 min pre-merge. Feedback improvement? **Answer: 15 min saved per run; ~40 min/day at 3 runs/developer.**
6. 4 two-state flags. State space? **Answer: 16. With 14 flags: 16,384 combinations — the flag-debt argument.**
7. 20 replicas, pool 10, `maxSurge: 1`, DB max 250. Rolling vs blue/green peak connections? **Answer: 210 (84%) vs 400 (160%, infeasible).**
8. Tag rollback 18 min vs digest revert 10 min, detection 3 min. Exposure? **Answer: 21 min vs 13 min. Prefer GitOps digest revert.**
9. `control=0.1%`, tolerance +50%, absolute floor 0.5%. Effective gate? **Answer: 0.5%.**
10. 15% change-failure rate, 40 deploys/month. **Answer: 6 failed deploys/month; with canary catching 72% of visible regressions, most of those stop at 1–25%.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `n_min ≈ 16p(1−p)/δ²` | sample size for a canary error-rate comparison |
| `T_exposure = T_detect + T_decide + T_rollout` | why slow detection needs a smaller canary |
| `schema_unsafe_window = days previous release remains deployable` | expand-contract timeline |
| `queue_growth = arrival_rate × lock_duration` | why DDL needs `lock_timeout` |
| `backfill_rate = batch/(txn + pause)` | whether a backfill fits in a release |
| `feedback = compile + max(unit) + max(static)` | pipeline ordering |
| `connections_peak = (R + surge) × pool` | deployment strategy has a DB budget |
| `T_rollback = detect + decide + command + rollout` | measure and publish it |
| `states = Π flags` | flag debt is combinatorial |
| `CFR = failed/total`; `lead time`, `TTR` | the four DORA measures |
