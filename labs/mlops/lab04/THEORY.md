# Feature Store Architecture

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

## 1. The Problem This Solves

Training and serving compute features from the same definition, but they read it at different times, from different stores, with different code. The gap between them is silent model decay.

Feature stores exist to close the training-serving skew gap and to make features a reusable, owned asset rather than copy-pasted logic in forty notebooks.

## 2. Learning Objectives

- Design online and offline feature stores and explain why both are needed
- Define a feature, an entity, a feature view and a materialisation
- Prevent training-serving skew by construction rather than by convention
- Reason about point-in-time correctness and lookback windows
- Compute freshness and staleness as service-level properties
- Choose between push and pull materialisation per use case

## 3. Core Concepts

### 3.1 Two stores, one definition

The offline store holds history in Parquet for training; the online store holds the latest values in Redis or DynamoDB for serving. Both are materialised from the same feature view, so the definition is the contract and the stores are projections of it.

### 3.2 Training-serving skew is the enemy

Skew appears when training reads a feature computed one way and serving computes it another: different rounding, different null handling, different time zone. The fix is one definition materialised into both stores, not two code paths that happen to agree today.

### 3.3 Point-in-time correctness

Training rows must see only the feature values that existed at the label timestamp. Joining on event time with a lookback window, rather than on the latest value, is what stops a feature from leaking the future into the training set.

### 3.4 Freshness is a feature-store property

A feature that is a week stale at serving time is a different feature than the one you trained on. Publish the max event timestamp per feature and alert on the gap, because staleness looks like drift and gets misdiagnosed for weeks.

### 3.5 Ownership and reuse

A feature without an owner becomes a fork. Named owners, documented semantics, and a deprecation path are what make a store a platform rather than a shared bucket.

### 3.6 Push versus pull materialisation

Pull (batch) recomputes on a schedule: simple and reproducible. Push updates on write: fresher, more expensive, harder to reproduce. Most teams run pull for aggregates and push for real-time counters, with both paths feeding the same definition.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `online[entity][feature] = f(batch(source))` | Materialisation | one definition, two projections |
| `lookback = f(t_event, t_window)` | Point-in-time join | no future values in training |
| `freshness = now - max(event_ts) per feature` | Freshness | the property to alert on |
| `staleness_pct = P(freshness > threshold)` | Staleness rate | share of reads served stale |
| `materialisation_lag = write_ts - event_ts` | Lag | seconds between event and availability |
| `reuse_ratio = features reused / features defined` | Platform value | the argument for a store |

## 5. How the Pieces Fit Together

1. Define the entity key, the feature semantics and the owner before writing code.

2. Write one transformation that produces the value; it feeds both stores.

3. Materialise to the offline store with the event timestamp preserved for point-in-time joins.

4. Materialise to the online store with a TTL matching the feature's staleness tolerance.

5. Test parity: read the same entity from both stores and assert the values agree.

6. Publish freshness and reuse metrics; alert on the staleness rate.

## 6. Assumptions and Invariants

- A feature has exactly one definition, versioned in code
- Entity keys are stable and shared between online and offline stores
- Event timestamps are preserved end to end for point-in-time correctness
- Online TTLs reflect each feature's staleness tolerance, not a global default
- Feature owners are named and deprecation is a supported path
- Parity between stores is tested continuously, not assumed

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Model accuracy drops after a successful migration | training-serving skew from a reimplemented transformation | one definition materialised into both stores; add a parity test |
| Offline metrics are far better than live results | point-in-time leakage in the training join | join on event time with an explicit lookback window |
| A feature silently became a month old | no freshness metric published | alert on freshness per feature, not just pipeline success |
| Two teams have a 'lifetime value' feature with different formulas | no ownership or naming discipline | named owners, documented semantics, deprecation workflow |
| Online reads time out under peak load | no batching, one round trip per feature | batch feature reads into one request per entity |
| A feature change broke training silently | no versioning on feature views | version the view; a new definition is a new view |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `record FeatureView(String name, int version, String entity, Map<String, String> semantics)` | the versioned definition |
| `Batch feature reads into one call` | the difference between a usable and an unusable online path |
| `Duration TTL per feature` | staleness tolerance is per feature, not global |
| `record FeatureValue(Object v, Instant eventTs)` | the timestamp that makes point-in-time joins possible |
| `AtomicReference<Map<String,Object>> per entity` | an in-memory online store that makes parity testable |

## 9. Where This Sits in the Larger System

- **mlops/lab09** validates the inputs before this store materialises them.
- **mlops/lab01** schedules the batch materialisation jobs.
- **labs/ml/lab01** is where a badly defined feature shows up as a coefficient problem.
- **mlops/lab11** records who used which feature version for which model.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Design online and offline feature stores and explain why both are needed
- [ ] 0 — cannot yet — Define a feature, an entity, a feature view and a materialisation
- [ ] 0 — cannot yet — Prevent training-serving skew by construction rather than by convention
- [ ] 0 — cannot yet — Reason about point-in-time correctness and lookback windows
- [ ] 0 — cannot yet — Compute freshness and staleness as service-level properties
- [ ] 0 — cannot yet — Choose between push and pull materialisation per use case

## 11. Summary Checklist

- [ ] Every feature has one definition feeding both stores.
- [ ] Training joins are point-in-time correct with an explicit lookback.
- [ ] Freshness is published and alerted on per feature.
- [ ] Online TTLs are per feature.
- [ ] Store parity is tested continuously.
- [ ] Feature views are versioned and have named owners.
