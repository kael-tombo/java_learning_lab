# Feature Store Architecture - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab04  |  **Level:** Intermediate

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
| `online[entity][feature] = f(batch(source))` | Materialisation - one definition, two projections |
| `lookback = f(t_event, t_window)` | Point-in-time join - no future values in training |
| `freshness = now - max(event_ts) per feature` | Freshness - the property to alert on |
| `staleness_pct = P(freshness > threshold)` | Staleness rate - share of reads served stale |
| `materialisation_lag = write_ts - event_ts` | Lag - seconds between event and availability |
| `reuse_ratio = features reused / features defined` | Platform value - the argument for a store |

## Why the Math Matters

The feature store is where the mathematics of time and probability meet deployment: lookback windows define what a training row is allowed to see, and staleness bounds how much the serving distribution can differ from the training one.


---

## 1. Point-in-time join correctness

```text
for label at time t:
  x_i = value of feature i at time max(ts <= t - lookback)
  never any value with ts > t - lookback
```

A point-in-time join reconstructs, for each training row, the feature values that were actually available when the prediction would have been made. Without it, the training set contains information the model could never have had.

**Worked example.** Purchase at t=10:00 with a 'lifetime value' feature that includes the purchase. A naive latest-value join gives 0 leakage visible in CV; a correct join excludes it and accuracy drops to honest levels.


---

## 2. Staleness distribution

```text
freshness = now - event_ts
S = P(freshness > tau)
Expected read staleness = E[freshness]
```

Staleness is a distribution, not a boolean. Alerting on the rate P(freshness > tau) is more robust than alerting on a single sample that could be an outage or a clock skew.

**Worked example.** tau = 1h, hourly materialisation: normal freshness is 0-60min, so S is near 0. A broken upstream job pushes freshness to 26h and S goes to 1.0 within one cycle.


---

## 3. Materialisation lag budget

```text
lag = write_ts - event_ts
end-to-end budget = ingest_lag + compute_lag + write_lag
SLO: P(lag < budget) >= 0.99
```

Decomposing lag into stages tells you which stage to fix. A 4-hour budget with 3.5 hours in compute is a different problem from 3.5 hours in ingest.

**Worked example.** Budget 15min: ingest 2min, compute 8min, write 1min = 11min typical, so S is high. Moving compute to a bigger pool takes it to 5min and the SLO holds.


---

## 4. Online read cost and batching

```text
per-request cost = 1 + F features per round trip
batched cost = ceil(F / batchSize) round trips
p99 dominated by round trips, not payload
```

The latency budget for serving is mostly round trips. Batching feature reads into one call per entity is usually the single largest latency win available in a feature-store-backed service.

**Worked example.** 6 features read individually: 6 round trips at 0.5ms each = 3ms. Batched into one call: 0.6ms, a 5x p99 improvement for one code change.


---

## Cheat Sheet

- `online[entity][feature] = f(batch(source))` - Materialisation
- `lookback = f(t_event, t_window)` - Point-in-time join
- `freshness = now - max(event_ts) per feature` - Freshness
- `staleness_pct = P(freshness > threshold)` - Staleness rate
- `materialisation_lag = write_ts - event_ts` - Lag
- `reuse_ratio = features reused / features defined` - Platform value

## Numerical Traps

- Joining on the latest value instead of the label's timestamp.
- Using one global TTL when features have different staleness tolerances.
- Reading features one at a time and blowing the latency budget.
- Changing a feature definition without versioning the view.
- Alerting only on pipeline success while a feature goes stale for days.

## Self-Check Problems

1. Construct a 3-feature point-in-time join by hand on 5 events and explain what a naive join would leak.
2. Compute the staleness rate for a feature materialised hourly with tau = 2h under normal and broken jobs.
3. Decompose a 4-hour materialisation lag into ingest, compute and write stages from measured data.
4. Design an online read batching strategy for 12 features with a 0.6ms round trip and a 5ms budget.
5. Define a parity test between offline Parquet and an online Redis store for a numeric feature.
