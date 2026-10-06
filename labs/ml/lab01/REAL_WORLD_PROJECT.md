# REAL_WORLD_PROJECT — Store-Level Demand Forecast Service

**Track:** ml  |  **Lab:** lab01  |  **Level:** Foundational

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

A 400-store retail chain forecasts next-day units per SKU to drive replenishment. Today a vendor spreadsheet is emailed each morning; it is stale, unversioned, and nobody can say how good it is. You replace it with a service, and you are on call when it breaks.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Rows per training run | ~180M (400 stores × ~1.2k active SKUs × 365 days) |
| Prediction SLA | Full next-day board in < 20 min, p95 board freshness < 30 min |
| Train frequency | Nightly at 02:00 local, plus on-demand retrain |
| Consumers | Replenishment planner UI, auto-order service, finance forecast report |
| Accuracy bar | Must beat the seasonal-naive baseline by ≥ 5% MAE to promote |

## 3. Target Architecture

```text
  CSV dumps / POS events --> Ingest (validate schema + row counts)
                                        |
                        +---------------+---------------+
                        |                               |
                 Offline store (Parquet)         Validation gate (fail -> page)
                        |                          |
                 Nightly train job (02:00)            |
                        |                          |
                 Model registry (versioned) <--------+
                        |
                 Serving tier: /predict (per-SKU), /board (per-store)
                        |
       +----------------+----------------+
       |                                 |
  Planner UI                     Auto-order service
  (board view)                   (p99 < 120 ms)

  Side channels: metrics -> Prometheus, structured logs, prediction log -> drift monitor
```

## 4. Component Responsibilities

### 4.1 Ingest and validation

- Read partitioned Parquet by date; reject files with unexpected partitions
- Row-count and null-ratio assertions per partition before anything else runs
- Idempotent re-runs keyed by (date, store, sku) so a retry cannot double-count
- Emit ingestion metrics: rows, reject rate, latency

### 4.2 Feature pipeline

- Calendar features (dow, month, holiday flags) are pure functions of time
- Rolling means computed with strict lookback windows, never future values
- Price and promo features sourced from the merchandising table with a freshness SLA
- Feature definitions versioned in git; the version travels with the model

### 4.3 Training job

- Nightly Docker run on a spot pool with a hard timeout and checkpointing
- Sweep λ over a small grid, select on a rolling validation window
- Gate: reject any candidate that does not beat seasonal-naive by the agreed margin
- Register the model with coefficient vector, scaler, feature version and metrics

### 4.4 Serving tier

- `/predict` single SKU, `/board` whole store; both return the model version
- Batch predictions cached per (store, date) because boards are requested repeatedly
- P99 under 120 ms; a mean-baseline fallback returns 200 rather than failing the planner
- Prediction log retained 90 days for drift analysis and dispute resolution

### 4.5 Monitoring and governance

- Dashboards: MAE by store decile, error by SKU velocity, feature drift PSI
- Alert when 7-day rolling MAE degrades > 15% against the model's training error
- Weekly retrain trigger when drift PSI exceeds 0.2 on any feature
- Model card and approval record attached to every registry entry

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship the baseline: seasonal naive + honest metrics + dashboard, so every later claim has a reference |
| Week 2 | Time-safe feature pipeline with unit tests asserting no future reads |
| Week 3 | Train job, λ sweep, registry entry, and the promotion gate wired to fail closed |
| Week 4 | Shadow serving beside the spreadsheet, then 10% of stores on real decisions |
| Week 5 | 100% cutover, spreadsheet retired, runbook published, on-call rotation handed over |

## 6. Runbook (copy-paste)

```bash
# Is tonight's board fresh?
curl -s localhost:8080/health | jq '.boardFreshnessSeconds'

# Did the nightly train fail?
curl -s localhost:8080/admin/last-run | jq '{status,modelVersion,mae}'
docker logs --since 6h forecast-trainer | grep -i 'gate\|reject\|converg'

# Feature drift on the top features
curl -s 'localhost:8080/admin/drift?feature=rolling7' | jq '.psi,.threshold'

# Safe mitigation: pin the last known-good model
curl -XPOST localhost:8080/admin/pin -d '{"version":"forecast-2026-09-28"}'

# Confirm the board matches the pinned version
curl -s localhost:8080/board?store=0417 | jq '.modelVersion'
```

## 7. Observability and SLOs

- SLO: 99% of boards served within 30 min of the 02:00 train finishing.
- Accuracy: MAE vs seasonal-naive, tracked per store decile and per SKU velocity band.
- Freshness: `boardFreshnessSeconds` p95 and max — the single number the planner team watches.
- Promotion gate: no model reaches production without a ≥ 5% MAE improvement over baseline.
- Business: stock-out rate and over-order value in the 30 days after cutover, compared to the spreadsheet period.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Ingest rejects half the partition after a source schema change | schema assertion fires | Fail closed, keep serving yesterday's board, page the data owner |
| Overnight MAE spikes 30% | stock-out event or a bad promo file | Pin previous model version, diff the feature distributions, re-run on the affected stores |
| Planner reports stale board | train job overran its window | Serve the cached board with an explicit `stale=true` flag rather than blocking the UI |
| P99 predict latency breaches 120 ms | cache miss storm after a config change | Warm the batch cache, shed per-SKU calls to the baseline fallback |
| Coefficients flip between nightly runs | collinear price/promo features | Standardise features, report the λ chosen, alert on coefficient sign changes > 20% |

## 9. Prevention Backlog

- Add prediction intervals to the board so planners can see uncertainty, not just point estimates.
- Backfill 24 months of POS history so the seasonal-naive baseline is competitive from day one.
- Automate λ selection with a Bayesian search once nightly retrains exceed 20 minutes.
- Add a shadow evaluation job that scores every candidate against the last 7 days of actuals.
- Publish per-store fairness and accuracy audits for the board as an accessibility requirement, not an afterthought.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **scikit-learn — Linear Models user guide**: https://scikit-learn.org/stable/modules/linear_model.html
  Canonical OLS/ridge/lasso derivation and the least-squares objective; the reference for what a closed-form solution actually guarantees.
- **NumPy — linalg module reference**: https://numpy.org/doc/stable/reference/routines.linalg.html
  `linalg.solve`, `lstsq`, `pinv`, SVD — how practitioners avoid forming XᵀX explicitly and what conditioning means in practice.

> The deliverable is not the model. It is a forecast service with a baseline, a gate, a rollback command and a number the planner can verify in ten seconds.
