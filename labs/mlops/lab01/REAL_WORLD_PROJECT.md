# REAL_WORLD_PROJECT — Hourly Recompute Platform

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

## 1. Scenario

A retail platform retrains 40 models hourly across 6 business domains. Two engineers currently manage it with cron and a spreadsheet. You are migrating it to a DAG orchestrator while the models must keep serving.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Models | 40 models × 6 domains, hourly schedule, 167,000 runs/year |
| Warehouse | one Snowflake-like warehouse shared with analytics; ML may use 20% of it |
| GPU pool | 8 A10G-equivalent nodes shared with interactive notebooks |
| Freshness objective | 99% of models under 2h old; monthly error budget 7.3h |
| Consumers | 40 serving deployments, each pinned to a model version |

## 3. Target Architecture

```text
 CDC + batch tables --> ingest (per domain, pooled)
                              |
                        validate (schema, freshness, volume)
                              |
             +----------------+----------------+
             |                                 |
   featurise (spark)                  backfill path (throttled)
             |                                 |
        train (gpu pool) <--------------------+
             |
        evaluate (gates: AUC, calibration, latency proxy)
             |                         |             +--> shadow deploy for 24h
        promote  <------------ challenger wins on matured labels
             |
      registry + serving rollout (canary 5% -> 50% -> 100%)

  Ledger: fingerprint, timings, cost, freshness, dead letters
  Alerting: failure, staleness, queue time, cost anomaly
```

## 4. Component Responsibilities

### 4.1 DAG definition and versioning

- One templated DAG per domain, versioned in git with review required
- Data window as a parameter; backfill reuses the same tasks
- Dependency edges explicit, including the validation gate before training
- DAG changes validated by a backfill window before promotion

### 4.2 Resource governance

- Warehouse and GPU pools with hard concurrency caps per domain
- Priority classes: catch-up over backfill, backfill over interactive analytics
- Per-domain cost budget enforced by the scheduler, not by goodwill
- Pool utilisation and queue time exposed to the analytics team

### 4.3 Reliability and repair

- Idempotent tasks keyed by run id; retries bounded with dead letters
- Freshness SLO per model with alerting separate from failure alerting
- Backfill command with ordering and dedupe, used to repair gaps
- Dependency outage circuit breaker so downstream nodes fail fast

### 4.4 Lineage and rollout

- Run ledger maps model version to commit, data version, params and metrics
- Promotion gate blocks registration on metric regression
- Shadow deployment for 24h before promotion, then canary rollout
- Automatic rollback on serving guardrails with the DAG version recorded

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Migrate one low-risk domain; keep cron running in parallel and compare outputs byte for byte |
| Week 3-4 | Migrate the remaining domains; add freshness alerting and the lineage ledger |
| Week 5 | Introduce pools, priority classes and cost budgets; measure queue impact on analytics |
| Week 6-7 | Shadow deploys and promotion gates for all 40 models |
| Week 8 | Retire cron; publish the runbook; first timed rollback drill |

## 6. Runbook (copy-paste)

```bash
# Freshness and failure state for every model
curl -s localhost:8080/platform/models | jq '.[] | {name,freshness,status}'

# Which run produced a given deployed model version
curl -s 'localhost:8080/platform/lineage?model=churn&version=12' | jq '{commit,dataVersion,params,metrics}'

# Dead letters needing attention
curl -s 'localhost:8080/platform/deadletters?state=open' | jq '.[] | {runId,task,attempts}'

# Backfill a domain for a specific window (throttled)
curl -XPOST localhost:8080/platform/backfill -d '{"domain":"pricing","from":"2026-09-01","to":"2026-09-03"}'

# Freeze promotion for a domain and serve the current champion
curl -XPOST localhost:8080/platform/mode -d '{"domain":"pricing","mode":"CHAMPION_ONLY"}'
```

## 7. Observability and SLOs

- Freshness: 99% of models under 2h; monthly error budget 7.3h, tracked and published.
- Reliability: task success rate, dead-letter count, mean time to resolve a dead letter.
- Cost: warehouse credits and GPU hours per run, per domain, against budget.
- Queue: pool utilisation and p95 queue time for ML and for analytics.
- Model: promotion gate pass rate and shadow-deploy win rate as a proxy for pipeline quality.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Warehouse saturated by a 40-model backfill | backfill not throttled against the analytics pool | Pause backfill via the priority class, resume at reduced concurrency, alert the analytics owner |
| A domain's models go stale while tasks are green | upstream table stopped updating with no freshness gate | Freshness alert fires; pin the last good model version and escalate to the data owner |
| Dead letters accumulate silently | no owner or no replay command for the queue | Assign an owner, add a replay command, alert when the queue is non-empty beyond one run |
| Model accuracy drops after a promotion | gate passed on a stale validation window | Roll back via the registry; require the shadow period to complete before any promotion |
| GPU pool contention starves interactive notebooks | no priority classes between ML and interactive work | Apply priority classes and cap ML concurrency; notebooks get a reserved share |

## 9. Prevention Backlog

- Automatic backfill for gaps detected by the freshness monitor.
- Per-domain cost dashboards shared with finance and analytics.
- Shadow-deploy automation replacing the manual 24h wait.
- Content-hashed data snapshots so lineage needs no manual bookkeeping.
- Timed rollback drill quarterly with the result published to the domain owners.

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

> The deliverable is 167,000 unattended runs a year where every model is fresh, every promotion is gated, and a stale dataset pages somebody instead of quietly degrading a business metric.
