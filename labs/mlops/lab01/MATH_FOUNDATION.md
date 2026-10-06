# ML Pipeline Orchestration - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab01  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `T_task ≥ max(T_parents)` | Critical path - stage duration is bounded by its slowest parent |
| `SLO_sla = 1 − P(freshness > threshold)` | Freshness objective - the only pipeline SLO that matters |
| `retries = min(3, ceiling(log(1/p)/log(1/(1-e))))` | Retry budget - keep total attempts bounded |
| `cost = sum(node_cost × attempts)` | Cost model - retries are not free |
| `lineage = (code_commit, data_version, params, artifact_hash)` | Run fingerprint - what makes a run reproducible |
| `backfill_window = max(gap_detected, gap_repaired)` | Repair window - fix the whole gap, not just today |

## Why the Math Matters

Orchestration is scheduling plus state. The mathematics is critical path analysis, concurrency and the cost of retries; the engineering is making every one of those safe to run twice.


---

## 1. Critical path and stage duration

```text
T_stage = max over parents of T_parent + T_node
T_total = longest path through the DAG
```

Pipeline latency is the longest path, not the sum. Optimising an off-critical-path node buys nothing; optimising the slowest parent of a join buys a lot.

**Worked example.** ingest (20m) -> validate (5m) -> featurise (40m) -> train (90m) -> eval (10m) -> register (2m) = 167m. Shaving validate from 5m to 1m changes nothing.


---

## 2. Retry budget and attempt cost

```text
attempts = min(maxRetries, ceiling(log(p) / log(1 - e)))
total_cost = attempts x unit_cost
```

Bounded retries trade a tail of failures for higher cost. The right number depends on how often the failure is transient (network) versus deterministic (bad code).

**Worked example.** A task with p = 0.02 transient failure and maxRetries = 3: expected attempts 1.02, worst case 3. With maxRetries = 10 the worst-case cost is 3.3x for 1% more reliability.


---

## 3. Freshness as the pipeline SLO

```text
freshness = now - timestamp(output)
SLO = P(freshness < threshold) >= 0.99
for hourly data: threshold = 2 x schedule interval
```

Alerting on task failure misses the most common real failure: the pipeline is green and the data is a week old. Freshness catches it.

**Worked example.** Hourly schedule, 99% objective with a 2h threshold: 4 missed runs a month breach it, which is usually the right amount of slack.


---

## 4. Concurrency and pool utilisation

```text
throughput = min(node_rate, pool_capacity / cost_per_node)
queue_time ~ 1/(capacity - arrival_rate) as utilisation approaches 1
```

Pool utilisation queues superlinearly near 100%. That is why backfill must be throttled: it turns a latency problem into an outage for everything else sharing the pool.

**Worked example.** Pool of 20 workers, backfill of 200 tasks at 5m each: unthrottled it takes 50m of full utilisation and queues interactive runs. Throttled to 10 concurrent, interactive p99 stays flat.


---

## Cheat Sheet

- `T_task ≥ max(T_parents)` - Critical path
- `SLO_sla = 1 − P(freshness > threshold)` - Freshness objective
- `retries = min(3, ceiling(log(1/p)/log(1/(1-e))))` - Retry budget
- `cost = sum(node_cost × attempts)` - Cost model
- `lineage = (code_commit, data_version, params, artifact_hash)` - Run fingerprint
- `backfill_window = max(gap_detected, gap_repaired)` - Repair window

## Numerical Traps

- Summing node durations instead of taking the longest path.
- Treating a green DAG as proof the data is fresh.
- Unbounded retries that quietly triple the cost of a failing step.
- Fan-out without a pool quota, then blaming the scheduler.
- Backfilling only the newest window after a gap is discovered.

## Self-Check Problems

1. Draw a DAG for a nightly retrain and compute its critical path.
2. Given a p = 0.05 transient failure rate, compute expected attempts for maxRetries in {1, 3, 5}.
3. Design a freshness SLO for a 15-minute pipeline and compute its monthly error budget.
4. Compute queue time for a pool of 30 workers at 80% and 95% utilisation.
5. Given a detected 3-day data gap, write the backfill plan including ordering and idempotency.
