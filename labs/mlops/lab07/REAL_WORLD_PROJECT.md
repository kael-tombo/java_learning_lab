# REAL_WORLD_PROJECT — ML CI Platform for 12 Teams

**Track:** mlops  |  **Lab:** lab07  |  **Level:** Intermediate

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

Twelve teams ship models to one platform through one pipeline template. Pre-merge took 40 minutes, so engineers merged and fixed forward; last quarter two shipped models with a 6% accuracy regression that surfaced in a business review.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Teams | 12 teams, ~150 model changes per week |
| Current pre-merge | ~40 minutes, bypassed in roughly a third of merges |
| Escaped defects | 2 accuracy regressions (>5%) and 3 schema breaks in one quarter |
| Data | shared lakehouse with 9 upstream producers and no contracts |
| Goal | pre-merge under 10 minutes with gates nobody routes around |

## 3. Target Architecture

```text
 PR opened
   |
 pre-merge lane (target <10 min)
   |- build + unit (per language)
   |- data contracts (9 producers)
   |- schema + feature-view contracts
   |- smoke train on fixture
   |
 blocked/fast feedback
   |
 merge to main --> post-merge lane (async)
   |- full train (cached snapshot + features)
   |- frozen-set evaluation gate (per-slice epsilons)
   |- registry + shadow deploy
   |
 promotion via registry gate (not CI)

 platform dashboards: pre-merge duration, bypass rate,
 escaped defects, detection time
```

## 4. Component Responsibilities

### 4.1 Pipeline template and fast lane

- Shared template producing a <10-minute pre-merge lane for all 12 teams
- Content-addressed per-stage caching on a shared cache service
- Team-specific fixtures and eval sets referenced, not copied
- Pre-merge duration and bypass rate measured per team as adoption metrics

### 4.2 Contracts across 9 producers

- Data contracts per upstream table: shape, nullability, ranges, semantics
- Failing examples per contract so the contract itself is tested
- Contract failure blocks the producer's change, not the consumer's
- Breaking change process with a notice period and consumer inventory

### 4.3 Evaluation gates

- Frozen, versioned eval set per model with a recorded set id
- epsilon derived from repeat-run variance per model and metric
- Per-slice gates with declared minimum sample sizes
- Gate results written to the tracking store and linked to the run

### 4.4 Shadow and promotion separation

- Post-merge lane registers the artefact and deploys to shadow
- Promotion through the registry gate with matured-label comparison
- Bypass policy: an emergency override that is logged, expires and is reviewed
- Quarterly review of overrides and escaped defects with the platform team

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Audit current pipeline stages; move full training and evaluation out of pre-merge |
| Week 3 | Shared caching service with per-stage content keys; measure the time saving |
| Week 4-5 | Data contracts with the 9 producers, failing examples included |
| Week 6 | Evaluation gates per model with variance-derived epsilons and per-slice checks |
| Week 8 | Bypass policy and override review; publish the platform dashboard |

## 6. Runbook (copy-paste)

```bash
# Pre-merge duration and bypass rate per team
curl -s localhost:8080/ci/metrics | jq '.byTeam[] | {team,p50Minutes,bypassRate}'

# Why a specific pipeline is slow
curl -s 'localhost:8080/ci/stages?runId=ci-88421' | jq '.stages[] | {name,seconds,cacheHit}'

# Contract failures by producer
curl -s 'localhost:8080/contracts?state=failing' | jq '.[] | {producer,table,rule}'

# Gate evaluation detail for a model, with the frozen set id
curl -s 'localhost:8080/gates/model?version=42' | jq '{metric,baseline,candidate,delta,epsilon,evalSetId}'

# Emergency override audit trail
curl -s 'localhost:8080/ci/overrides?window=90d' | jq '.[] | {runId,actor,reason,expiresAt}'
```

## 7. Observability and SLOs

- Adoption: pre-merge duration p50 and p95 per team (target p50 < 10 min).
- Integrity: bypass rate under 3% and every override logged, expiring and reviewed.
- Quality: escaped defects (accuracy regressions, schema breaks) per quarter, trending to zero.
- Detection: time-to-detect including queue time, reported per gate type.
- Contracts: percentage of the 9 producers covered by failing-example contracts.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Teams bypass pre-merge again | pipeline slow, usually uncached data in the pre-merge lane | Move the slow stage post-merge, publish per-team duration, add an expiring override policy |
| A producer's breaking change lands in production | No contract at the boundary | Contract failure blocks the producer's change; require contracts before merge |
| Gates fire randomly and get ignored | epsilon below run-to-run variance | Derive epsilon from repeat runs per model; report variance alongside the gate |
| A model ships with a 6% regression | No frozen-set gate on that team | Block merge until the gate exists; backfill gates for the top 20 models first |
| Cache serving stale data after a pipeline change | Cache keyed by branch name | Content-address keys per stage; verify staleness is impossible in a test |

## 9. Prevention Backlog

- Per-slice gates with minimum sample sizes declared in the suite.
- Override review automation with an expiry and a monthly digest.
- Triggered post-merge runs keyed to data or model changes rather than schedules.
- Platform dashboard publishing escaped defects by team as a shared metric.
- Contract coverage automation discovering new upstream tables.

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

> The deliverable is a 10-minute pre-merge lane that 12 teams actually wait for, with contracts that stop upstream breakage at the boundary and gates that block accuracy regressions before merge.
