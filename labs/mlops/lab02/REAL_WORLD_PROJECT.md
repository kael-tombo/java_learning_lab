# REAL_WORLD_PROJECT — Experiment Platform for a Recommendations Team

**Track:** mlops  |  **Lab:** lab02  |  **Level:** Intermediate

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

A 40-person organisation runs 300+ modelling experiments a month across six teams on one shared cluster. Last quarter a revenue model was rebuilt from scratch because nobody knew which data version produced the winning number. You are standing up the experiment platform.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Volume | ~300 experiments/month, ~4,000 tracked runs |
| Teams | 6 teams, each with its own naming and tagging discipline |
| Metric definitions | ~40 metrics, several with historical variants |
| Storage | artifact-heavy: ~2TB/month before retention |
| Value | eliminating duplicated experiments and making rollouts auditable |

## 3. Target Architecture

```text
 CI / notebooks / schedulers
        |            |              |
        +------------+--------------+
                     |
            tracking service (runs, params, metrics, tags, artifacts)
                     |
      +--------------+---------------+
      |              |               |
  selection      dashboards      retention + cost
  (best per       (metric time    (lifecycle to cold
   team/version)    series)        storage)
                     |
        champion comparison + promotion record
                     |
               model registry (lab03)

  Governance: mandatory tags enforced at write time; quarterly audit
```

## 4. Component Responsibilities

### 4.1 Tracking service and client

- Central service with per-team experiments and enforced tag schema
- Client library with offline queue and idempotent run ids
- Metric definitions versioned in code so a renamed metric cannot silently change meaning
- Write-path validation: a run without owner, branch and dataVersion is rejected

### 4.2 Dashboards and selection

- Leaderboards per team and data version with metric time series
- Champion/challenger comparison view used by every promotion decision
- Metric time series with overfitting gap highlighted
- Saved views so a team's weekly review opens the same query every time

### 4.3 Artifact lifecycle and cost

- Artifacts written once with content hashing and size recorded
- Lifecycle policy: hot for 30 days, warm 180, cold beyond; deletion is audited
- Monthly storage report per team with the top artifact types
- Checkpoint reduction: keep best and last only, not every epoch

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Deploy the tracking service; migrate one team and audit their historical results for duplication |
| Week 2 | Enforce the tag schema at write time; publish the metric definition catalogue |
| Week 3 | Dashboards and the champion comparison view; adoption push with per-team onboarding |
| Week 4 | Artifact lifecycle and the cost report; delete policy agreed with the teams |
| Week 6 | Quarterly audit: duplicated experiments found, rollouts traced to run ids |

## 6. Runbook (copy-paste)

```bash
# Open runs (should be zero; leaked runs block audits)
curl -s localhost:8080/tracking/runs?status=RUNNING | jq '.[] | {runId,owner,started}'

# Best run per team per data version
curl -s 'localhost:8080/tracking/best?groupBy=team,dataVersion&metric=val_auc' | jq '.'

# Lineage for a promoted model version
curl -s 'localhost:8080/tracking/lineage?runId=r-99312' | jq '{commit,dataVersion,params,artifacts}'

# Storage by team this month
curl -s 'localhost:8080/tracking/storage?window=30d' | jq '.byTeam'

# Reap leaked runs and archive their logs
curl -XPOST localhost:8080/tracking/reap -d '{"olderThanHours":24,"dryRun":true}'
```

## 7. Observability and SLOs

- Adoption: percentage of experiments recorded in the platform versus local spreadsheets (target > 90%).
- Repro: number of production rollouts traceable to a run id (target 100%).
- Cost: storage per month and per team, trending down after lifecycle policy.
- Hygiene: runs missing mandatory tags (target zero, enforced at write time).
- Impact: number of duplicated experiments found and eliminated per quarter.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A team logs to local files instead of the platform | no enforced schema and no benefit for them | Enforce mandatory tags at write time; give each team a saved dashboard they actually use |
| Metric meaning changed silently after a rename | metric names versioned only informally | Version metric definitions in code and assert the catalogue before promotion |
| Storage doubles after a big sweep campaign | checkpoints logged per epoch with no lifecycle | Apply the lifecycle policy and keep best/last checkpoints only; report cost per team |
| A production rollout cannot be traced to a run | promotion happened outside the platform | Require a run id in the promotion request; the registry rejects untraced promotions |
| Leaked RUNNING runs block the audit | client crashed without closing the run | Auto-close via a heartbeat; reap stale runs on a schedule with an alert |

## 9. Prevention Backlog

- Automatic lineage join between the tracking store and the data catalogue.
- Duplicate-experiment detection that flags similar configs across teams.
- Per-team cost budgets enforced by the storage lifecycle.
- Offline replay queue with idempotency verified in CI.
- Quarterly audit report: rollouts traced, duplicates found, tags missing.

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

> The deliverable is a place where 4,000 runs a month are queryable, every production rollout traces to a run id, and the next team does not repeat the last team's experiments.
