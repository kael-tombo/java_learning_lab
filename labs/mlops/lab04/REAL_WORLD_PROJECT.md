# REAL_WORLD_PROJECT — Feature Platform for a Payments Risk Team

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

## 1. Scenario

A risk team builds 30 models on 400 features defined across notebooks. Two teams have three different 'device fingerprint' definitions, one of them looks at future data, and a model that scored well in notebooks fell apart in production. You build the feature platform.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Features | 400 across 30 models, 6 teams, currently notebook-defined |
| Online latency | risk scoring budget p99 < 30 ms including features |
| Materialisation | hourly pull for aggregates; minute-level push for counters |
| Known issues | 3 forked definitions; 1 feature with confirmed future leakage |
| Value | kill forks, close the leak, and make a score reproducible from its feature versions |

## 3. Target Architecture

```text
 sources (CDC, billing, device, web)
        |
   feature definitions repo (versioned, reviewed, owner-tagged)
        |
   +----+----+    (pull: hourly)     +----------+
   |         |                       | offline  |--> training (point-in-time joins)
   |         +---- (push: realtime) -+----------+
   |                                 | online   |--> risk scoring (p99 < 30ms)
   |                                 +----------+
   |
 freshness + parity + usage monitoring --> alerts
   |
 adoption: reuse ratio, fork detection, deprecation workflow
```

## 4. Component Responsibilities

### 4.1 Definition registry and ownership

- Feature definitions in a reviewed repo with owner, semantics, units and lookback declared
- Registry rejects features without an owner or semantics, so forks cannot be registered
- Deprecation workflow with a notice period and consumer tracking
- Fork detection comparing feature names with divergent definitions across teams

### 4.2 Materialisation pipelines

- Pull path recomputes hourly aggregates from the lakehouse with event timestamps preserved
- Push path updates real-time counters from CDC with per-feature TTL
- Lag measured per stage (ingest, compute, write) against a budget
- Idempotent writes keyed by (entity, feature, event_ts) so retries are safe

### 4.3 Serving path

- Batched online reads: one call per entity with all required features
- p99 budget of 30 ms including features, with a measured fallback on store errors
- Parity test in CI comparing online and offline values for a sample of entities
- Feature version recorded with every decision for dispute reconstruction

### 4.4 Monitoring and migration

- Freshness per feature and staleness rate with alerts
- Adoption metrics: reuse ratio, fork count, deprecated-but-still-used features
- Migration tracker per model: which feature versions each model was trained on
- Leak audit: point-in-time correctness tests across all registered views

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Inventory 400 notebook features; identify forks and any with future leakage |
| Week 3-4 | Migrate the 30 risk models' features to registered, versioned views with owners |
| Week 5 | Stand up pull and push materialisation; parity tests and freshness monitoring live |
| Week 6-7 | Migrate serving to batched online reads; measure p99 against the 30 ms budget |
| Week 8 | Deprecate forked definitions; publish adoption and leak-audit reports |

## 6. Runbook (copy-paste)

```bash
# Freshness and staleness for the features this model needs
curl -s 'localhost:8080/features/freshness?model=risk-score-v9' | jq '.features,.staleCount'

# Parity check between online and offline for a sample
curl -s -XPOST localhost:8080/features/parity -d '{"sample":500}' | jq '.mismatches'

# Which feature versions a model was trained on
curl -s 'localhost:8080/features/versions?model=risk-score-v9' | jq '.features'

# Fork report: same name, different definitions
curl -s localhost:8080/features/forks | jq '.[] | {name,teams,owners}'

# Fall back to the previous feature view for one model
curl -XPOST localhost:8080/features/rollback -d '{"model":"risk-score-v9","toVersion":8}'
```

## 7. Observability and SLOs

- SLO: risk scoring p99 < 30 ms including features; parity mismatch rate < 0.01%.
- Freshness: staleness rate per feature against each feature's tolerance.
- Adoption: reuse ratio, fork count (target zero), deprecated-but-used count (target zero).
- Quality: point-in-time correctness tests passing for 100% of registered views.
- Repro: percentage of decisions replayable from recorded feature versions.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Risk score latency breaches 30 ms after feature migration | unbatched online reads | Enable the batched read path; keep the per-feature path as a degraded fallback |
| A feature goes 30 hours stale with the pipeline green | upstream CDC stopped; no freshness gate | Staleness alert pages the owner; fallback feature value flagged in the decision log |
| A model's offline accuracy drops after the leak fix | point-in-time join corrected | Expected: the honest number is lower. Re-baseline and document, do not revert the join |
| Two teams register different definitions of the same feature name | fork detection not enforced | Reject the second registration; route to the deprecation workflow |
| Parity mismatch appears after a transform change | skew reintroduced by a second code path | Roll back the transform; keep the parity test as a CI gate |

## 9. Prevention Backlog

- Fork detection promoted to a CI check that fails on duplicate names.
- Automated deprecation of views unused for 180 days, with notice.
- Point-in-time correctness tests added to the view registration checklist.
- Push latency reduction for the top 10 real-time counter features.
- Decision replay tooling using recorded feature versions for dispute reconstruction.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **MLflow — Tracking and Model Registry documentation**: https://mlflow.org/docs/latest/ml/tracking/
  Reference model for experiment/run/metric lineage and the registry lifecycle (the vocabulary this lab re-implements in Java).
- **Kubernetes — ConfigMaps and Secrets**: https://kubernetes.io/docs/concepts/configuration/configmap/
  How configuration is injected into scheduled workloads — the practical lineage story for a DAG run that must be reproducible months later.
- **DVC — data and model versioning**: https://dvc.org/doc/user-guide
  Content-addressed versioning of datasets and model binaries; the standard way to make a data snapshot referenceable in a run record.

> The deliverable is 400 features with one definition each, scores reproducible from their feature versions, and a freshness number paged on before users notice.
