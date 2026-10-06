# REAL_WORLD_PROJECT — Churn Scoring for a Subscription Business

**Track:** ml  |  **Lab:** lab03  |  **Level:** Intermediate

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

A 900k-subscriber SaaS business loses 3.4% of subscribers monthly to churn. A retention team of 40 can make about 9,000 save calls a week. You own the model that decides who gets called, and the contractual and regulatory constraints on profiling.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Population | 900k active subscribers, ~30k events/day in the product stream |
| Label definition | cancellation within 30 days of scoring (delayed by up to 30 days) |
| Base rate | 3.4% monthly churn, rising to 5.1% in the first 30 days after signup |
| Action capacity | ~9,000 retention calls/week; the model must rank, not classify |
| SLO | Nightly score for all subscribers in < 30 min; p99 lookup < 100 ms |

## 3. Target Architecture

```text
 Product events --> Warehouse (events + billing + support)
                        |
                 Nightly feature job (30d lookback)
                        |
            +-----------+-----------+
            |                       |
     Feature snapshot          Labels (30-day delayed)
     (versioned table)               |
            |                       |
      Model training --> Registry --> Scoring service (lookup p99<100ms)
            |                       |
     validation gates        +----+----+
     (beat baseline,        |         |
      calibration)      Retention    Marketing
                       worklist     (win-back flow)
                            |         |
                    Save outcome --> labels (closing the loop)

   Side: drift + calibration monitors, weekly fairness report by plan tier
```

## 4. Component Responsibilities

### 4.1 Feature pipeline

- 30-day lookback windows: logins, feature usage, tickets, invoices, plan changes
- Snapshot written to a versioned table so any score can be replayed exactly
- Feature definitions owned by a named team; changes require a version bump and shadow run
- Late-arriving events reconciled before scoring, never after

### 4.2 Training and promotion gates

- Champion/challenger; the challenger scores live traffic in shadow for 7 days
- Gate 1: must beat the rules baseline by 15% recall at equal contact volume
- Gate 2: calibration error within tolerance across plan tiers
- Gate 3: a human approval record with the reviewer, the numbers and the date

### 4.3 Scoring and worklist

- Nightly batch scores 900k subscribers; a lookup service serves the worklist UI
- Ranked worklist of 9,000, not a binary list; capacity is a first-class input
- Every worklist row carries the top reason codes for the call script
- Contact outcomes (saved / not saved / no answer) written back with the score version

### 4.4 Monitoring and fairness

- Weekly calibration by plan tier, region and tenure band
- Drift PSI on features and on the score distribution
- Accuracy tracked on matured labels with a 30-day lag, published not alerted
- No protected attributes in features; a documented proxy review before each release

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Rules baseline plus a live worklist so every later model has a reference |
| Week 2 | Feature snapshot pipeline with replay tests; label backfill verified against known cancellations |
| Week 3 | Model v1 in shadow for 7 days; compare recall at equal volume and inspect the mis-ranked accounts |
| Week 4 | Calibration pass, fairness review, human approval; canary at 10% of worklist capacity |
| Week 5 | Full cutover with the rules baseline kept as the rollback target; runbook and on-call handover |

## 6. Runbook (copy-paste)

```bash
# Did tonight's scoring run finish, and which model?
curl -s localhost:8080/admin/last-run | jq '{status,modelVersion,rowsScored,minutes}'

# Calibration on matured labels
curl -s 'localhost:8080/admin/calibration?window=28d' | jq '.ece,.byTier'

# Freeze the worklist and fall back to rules (safe manual mode)
curl -XPOST localhost:8080/admin/mode -d '{"mode":"RULES_FALLBACK"}'

# Roll back to the previous champion
curl -XPOST localhost:8080/admin/rollback -d '{"to":"churn-2026-09-14"}'

# Verify every worklist row carries a score version
psql -c "select count(*) from worklist where score_version is null;"
```

## 7. Observability and SLOs

- Business: saves per 1,000 calls, and monthly logo churn versus the pre-model baseline.
- Model: recall at the top 9,000 of 900k (the capacity-limited operating point).
- Calibration: ECE overall and per plan tier; report, do not hide.
- Operations: nightly run completes before 05:00; worklist available before the call shift starts.
- Guardrail: no tier's recall falls more than 10% relative to the overall rate without an explicit review.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Nightly run misses the 05:00 deadline | feature job slowed by a new join | Serve yesterday's snapshot with a staleness banner; page the data owner |
| Recall at capacity collapses 25% | behaviour change or a billing migration | Roll back to the champion, inspect drift PSI, retrain on post-migration labels |
| Calibration drifts by tier | a plan mix shift over time | Retrain with recent windows; add tier-aware recalibration; document in the card |
| Worklist rows missing reason codes | feature snapshot version mismatch | Fail the run loudly rather than serving half-populated call scripts |
| A regulator asks about profiling | no approval record for the live model | Every promotion stores reviewer, metrics and date — that record is the answer |

## 9. Prevention Backlog

- Automated label backfill with a freshness SLA per cancellation reason code.
- Shadow-mode challenger with automatic promotion on recall gain at equal volume.
- Per-tenant override: a human-specified flag must be visible in the worklist and in the audit log.
- Documented rollback drill each quarter, timed, result published.

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

> The deliverable is a ranked worklist a 40-person team can act on, with every score replayable from a versioned feature snapshot and every promotion carrying an approval record.
