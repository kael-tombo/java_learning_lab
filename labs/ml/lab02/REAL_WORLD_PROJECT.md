# REAL_WORLD_PROJECT — Transaction Fraud Triage Service

**Track:** ml  |  **Lab:** lab02  |  **Level:** Foundational

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

A payments processor reviews ~2M transactions/day. Manual review costs $12 and catches 60% of true fraud. You own the model that decides what a human looks at, and the audit trail that regulators and card networks will read.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Daily volume | ~2M transactions/day, ~65k transactions/minute at peak |
| Positive rate | 1.5–2.5% confirmed fraud, drifting seasonally |
| Review capacity | 1,200 analysts × 60 reviews/hour ≈ 72k reviews/day |
| Serving SLO | p99 < 60 ms, availability 99.95% |
| Success metric | Fraud dollars recovered per analyst-hour; cost per decision |

## 3. Target Architecture

```text
 Authorisation events --> Stream (Kafka) --> Feature service (velocity windows)
                                        |
                              +---------+---------+
                              |                   |
                    Scoring service            Score log (90d)
                    (Java, model in memory)         |
                              |                   |
                    threshold + reason codes        |
                              |                   |
                   +----------+---------+         |
                   |                    |         |
           Auto-decline (95%)     Review queue      |
           low score, low risk    ranked by $      |
                                        |         |
                                  Analyst UI <-----+
                                        |
                              labels fed back (delayed confirmations)
                                        |
                          drift + calibration monitor
```

## 4. Component Responsibilities

### 4.1 Feature service

- Velocity features from a streaming state store (count per card/IP/device in 1h, 24h)
- Amount features as z-score against a 30-day per-merchant baseline
- Feature values computed once and reused by scoring and by analyst UI
- Feature contract versioned; a schema change requires a dual-write window

### 4.2 Scoring service

- Model loaded from the registry at startup, hot-reloadable without dropping traffic
- Returns score, calibrated probability, and top-3 reason codes
- p99 under 60 ms with a precomputed feature lookup (no synchronous joins)
- Degrades to the previous model version if the registry is unreachable

### 4.3 Decisioning and review queue

- Threshold per risk tier, stored in config with an approver in the change log
- Auto-decline only when score, velocity and merchant risk all agree
- Review queue ranked by expected dollar loss, not raw score
- Every decision emits score, threshold version and feature values for audit

### 4.4 Delayed-label feedback and monitoring

- Chargeback labels arrive 30–120 days late; backfill them into training windows
- Weekly calibration report by tier and by acquirer
- Drift alert on score distribution and velocity features
- Champion/challenger: the challenger scores live traffic in shadow mode

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship rule-based triage with reason codes; publish the review-queue and cost dashboards |
| Week 2 | Model v1 in shadow mode only; compare against rules on live traffic, ship nothing |
| Week 3 | Calibration pass, threshold approval with the fraud team and risk committee |
| Week 4 | Canary at 5% of traffic with an instant revert switch; verify cost per review |
| Week 6 | Ramp to 50%, then 100%; retire the rule set; publish the model card and runbook |

## 6. Runbook (copy-paste)

```bash
# Is the scorer healthy and which version is live?
curl -s localhost:8080/health | jq '{version,modelAgeHours,thresholdSet}'

# Score distribution today vs last week
curl -s 'localhost:8080/admin/score-dist?window=24h' | jq '.p50,.p99,.mean'

# Freeze decisions (traffic to manual) during an incident
curl -XPOST localhost:8080/admin/mode -d '{"mode":"MANUAL_ONLY"}'

# Roll back to the previous model version
curl -XPOST localhost:8080/admin/rollback -d '{"to":"fraud-2026-09-21"}'

# Confirm the decision log is complete for the audit window
psql -c "select count(*) from decision_log where created_at > now() - interval '1 hour';"
```

## 7. Observability and SLOs

- SLO: 99.95% availability, p99 scoring < 60 ms, decision log completeness 100%.
- Business: fraud dollars recovered per analyst-hour; dollars per 1k declined.
- Model: recall at the top 1% of scores; calibration error by tier.
- Drift: PSI on score distribution and velocity features, alert at 0.2.
- Guardrails: false-positive rate on trusted merchants (auto-decline must stay rare).

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Score distribution collapses to near-constant | feature service returning stale velocity values | Fail to MANUAL_ONLY, alert on feature freshness, roll back model version |
| Recall at top 1% drops 20% week over week | new fraud pattern or an acquirer change | Compare label-lag windows, inspect drift PSI, retrain on the freshest labels |
| Review queue exceeds analyst capacity | threshold too loose after a config push | Auto-widen the threshold with an audited config change and page the ops lead |
| p99 breaches 60 ms | synchronous feature lookups during peak | Switch to the precomputed path; cap concurrency on the enrichment client |
| Regulator asks why a customer was declined | reason codes missing from the decision log | Every decision already carries score, threshold version and features — this is why that log exists |

## 9. Prevention Backlog

- Chargeback label backfill job with an explicit freshness SLA per acquirer.
- Shadow-mode challenger scoring with automatic promotion when recall improves at equal review volume.
- Per-merchant segment calibration so trusted merchants are not over-flagged.
- Chaos drill: feature store outage, registry outage and rule-engine outage, each with a documented fallback.
- Documented rollback drill every quarter, timed, with the result published.

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

> The deliverable is a decision system with an audit trail: every decline can be explained with the score, the threshold version and the feature values that produced it.
