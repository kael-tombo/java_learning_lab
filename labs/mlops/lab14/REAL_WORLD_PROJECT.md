# REAL_WORLD_PROJECT — Tuning Service for the ML Platform

**Track:** mlops  |  **Lab:** lab14  |  **Level:** Advanced

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

Nine teams submit tuning jobs to a shared cluster. Two teams run exhaustive grid searches that consume 70% of the budget and report improvements that do not reproduce, and the platform team receives 'the search said it was better' with no way to verify it.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Jobs | ~150 tuning jobs per month across 9 teams |
| Budget | shared cluster quota consumed ~70% by two teams' grid searches |
| Problem | reported improvements do not reproduce on holdout |
| Current controls | a queue and a wall-clock timeout |
| Goal | fair allocation, honest reporting and a reproducible record |

## 3. Target Architecture

```text
 submissions (team, space, objective, budget)
     |
 admission: budget quota per team + priority
     |
 search engine: random / Bayesian + successive halving
     |
 trial log (params, code version, data version, trial cost)
     |
 re-rank top-k on full budget
     |
 final estimate on a reserved holdout  --> tuning report
     |
 report published with baseline, holdout score and variance

 platform dashboard: budget share, trials-to-target, reproducibility rate
```

## 4. Component Responsibilities

### 4.1 Job admission and fairness

- Per-team budget quota and priority, with the release path reserved
- Mandatory submission fields: search space, objective definition, baseline and budget
- Submissions without a declared baseline are rejected at admission
- Queue wait time and budget share published per team

### 4.2 Search execution

- Default strategy: random or Bayesian search with successive halving
- Exhaustive grid search requires an explicit justification and a smaller budget
- Trial-level logging with parameters, code version and data version
- Wall-clock and cost budget enforced per job, with partial results returned on timeout

### 4.3 Honest evaluation

- A reserved holdout, untouched during search, used once for the final estimate
- Variance estimated across repeated seeds for the selected configuration
- Reported improvement stated as holdout minus baseline, not best-of-N
- Selection-bias diagnostics available per job for review

### 4.4 Reporting and reproducibility

- Tuning report published with space, budget, strategy, all trials, baseline and holdout score
- Re-running a published configuration reproduces the reported number
- Reproducibility rate tracked per team and published
- Platform view of trials-to-target by strategy, which steers future submissions

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Require declared baselines and budgets at admission; publish budget share per team |
| Week 3 | Default to random/Bayesian search with successive halving; keep grid behind justification |
| Week 4-5 | Reserved holdout per job, with the final estimate computed once |
| Week 6 | Variance across seeds in the report; reproducibility rate published |
| Week 8 | Platform dashboard of trials-to-target by strategy; first fairness review |

## 6. Runbook (copy-paste)

```bash
# Current queue, quota use and wait times
curl -s localhost:8080/tuning/queue | jq '.[] | {team,quota,used,pending,waitMinutes}'

# A job's trials and budget consumed
curl -s 'localhost:8080/tuning/jobs/tune-221/trials' | jq '.[] | {params,score,trialSeconds,rung}'

# Final estimate with baseline, holdout score and variance
curl -s localhost:8080/tuning/jobs/tune-221/report | jq '{baseline,selectedScore,holdoutScore,improvement,seedStdDev}'

# Selection-bias diagnostic for a job
curl -s 'localhost:8080/tuning/jobs/tune-221/diagnostics' | jq '.bestOfN,holdout,optimism}'

# Reproduce a published configuration
curl -XPOST localhost:8080/tuning/reproduce -d '{"jobId":"tune-198"}'
```

## 7. Observability and SLOs

- Fairness: budget share and queue wait time per team, with the release path visible.
- Honesty: gap between reported and holdout improvement, per team.
- Reproducibility: percentage of published configurations that reproduce within tolerance.
- Efficiency: trials-to-target by strategy, published so teams can choose better.
- Spend: cluster budget consumed by tuning, trending down per useful improvement.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A team submits grid search and consumes most of the budget | Grid allowed without limit | Require justification and a smaller budget; default to random/Bayesian |
| Reported improvement of 4% vanishes on holdout | Best-of-N reported as performance | Reserve a holdout per job and report holdout minus baseline only |
| A team waits days for quota | No priority or reservation | Per-team quotas with priority classes and a reserved release path |
| A published configuration does not reproduce | Data or code version drifted between runs | Log code and data versions per trial; fail reproduction reports loudly |
| Holdout is reused across submissions and becomes a tuning set | Holdout shared rather than reserved | Reserve per job; track holdout identifiers so reuse is detectable |

## 9. Prevention Backlog

- Warm-started surrogates across related jobs to cut trials-to-target.
- Multi-objective tuning exposing accuracy, latency and fairness jointly.
- Automated detection of holdout reuse across jobs.
- Per-team efficiency coaching using the trials-to-target view.
- Population-based tuning for robustness across seeds as a default option.

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

> The deliverable is a tuning service where 70% of the budget no longer goes to exhaustive search, every reported improvement reproduces on a reserved holdout, and fairness is a number on a dashboard rather than a complaint.
