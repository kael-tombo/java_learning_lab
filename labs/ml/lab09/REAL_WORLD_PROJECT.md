# REAL_WORLD_PROJECT — Credit Default Boosting Service

**Track:** ml  |  **Lab:** lab09  |  **Level:** Advanced

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

A lender approves 40k credit applications a day with an 8 ms scoring budget. Decisions are challenged by consumers and reviewed by fair-lending counsel, so every score needs a reason-code explanation that adds up.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Volume | ~40k applications/day, peak 60 applications/s |
| Base rate | 3.2% default within 12 months |
| Latency budget | p99 < 8 ms per decision, including feature fetch |
| Labels | 12-month delayed; backfilled weekly with a freshness SLA |
| Compliance | ECOA/FCRA reason codes required on every adverse action |

## 3. Target Architecture

```text
 applications --> bureau + internal features (point-in-time correct)
                        |
                drift + distribution checks
                        |
     champion booster (depth 3, eta 0.08, best round from validation)
                        |                                              |                       +--> challenger in shadow
                        |
              SHAP contributions -> reason codes (top 5, additive check)
                        |
        policy layer: cutoffs by product, state rules, override logic
                        |
   +----------+-----------+------------+
   |          |           |            |
 approve   refer    manual review   decline
 (67%)     (14%)       (9%)        (10%) + adverse action notice
                                        |
                                dispute / adverse action service
```

## 4. Component Responsibilities

### 4.1 Feature and point-in-time discipline

- Bureau features fetched with an as-of date so no post-decision data leaks
- Internal features versioned; a change requires a shadow window
- Missingness indicators are themselves features, not silent gaps
- Feature snapshot ID stored with every decision for replay and dispute evidence

### 4.2 Model and champion/challenger

- Champion: depth-3 boosting, eta 0.08, rounds from weekly validation with early stopping
- Challenger scores 100% of applications in shadow; promotion needs matured-label parity
- Every model card records (eta, depth, best round, subsample, lambda) and its validation curve
- Rollback to the previous champion is one command and rehearsed quarterly

### 4.3 Reason codes and explainability

- TreeSHAP contributions computed per decision; additivity asserted in production at low sample rate
- Top 5 contributions mapped to consumer-readable reason codes
- Reason-code catalogue versioned so historical decisions stay explainable
- Adverse action notices generated from the same contributions, not a separate narrative

### 4.4 Monitoring and fair-lending controls

- Approval rate, mean score and reason-code mix monitored by product and protected-class proxy
- Calibration by approval band; drift PSI on features and scores
- Weekly matured-label accuracy with a 12-month lag, published rather than alerted
- Fair-lending review sign-off recorded before every promotion

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Ship a logistic baseline with full reason codes so every later model has a reference |
| Week 2 | Champion booster in shadow with point-in-time feature discipline and replay tests |
| Week 3 | Calibration pass, reason-code catalogue review with compliance, additivity checks in production |
| Week 4 | Canary at 10% of decisions; verify adverse action notices end to end |
| Week 6 | Full cutover with rollback to the logistic baseline as the documented safe state |

## 6. Runbook (copy-paste)

```bash
# Champion model and its frozen hyperparameters
curl -s localhost:8080/admin/model | jq '{version,eta,depth,bestRound,ageHours}'

# Reason codes and additivity check for one adverse decision
curl -s 'localhost:8080/admin/explain?applicationId=a-884213' | jq '.reasonCodes,.sumCheck'

# Approval rate and reason-code mix vs last week
curl -s 'localhost:8080/admin/fairness?window=1w' | jq '.approvalRate,.byGroup,.delta'

# Roll back to the logistic baseline (documented safe state)
curl -XPOST localhost:8080/admin/rollback -d '{"to":"credit-logreg-v6"}'

# Verify the decision log is complete for the dispute window
psql -c "select count(*) from decisions where created_at > now() - interval '1 day';"
```

## 7. Observability and SLOs

- SLO: p99 decision latency < 8 ms; availability 99.95%; every decision has a stored reason code.
- Business: default rate at a fixed approval mix, versus the pre-model baseline.
- Model: matured-label AUC and calibration by approval band, published weekly.
- Compliance: 100% adverse action notices generated from the same SHAP contributions, sampled and audited.
- Fairness: approval rate and reason-code mix by group, reviewed before every promotion.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Default rate rises after a champion cutover | Model drift or a mix change in applicant flow | Roll back to the logistic baseline, compare matured labels, inspect drift PSI by product |
| Adverse action notice missing reason codes | SHAP path skipped or the catalogue version mismatched | Fail closed: fall back to logistic reason codes and page; every notice must have codes |
| SHAP additivity check fails | Baseline expectation drift after a model swap | Block promotion until additivity holds; treat as a correctness bug, not a tuning issue |
| Approval rate diverges by group | Proxy feature drift or a mix change | Pause promotion, run the fair-lending review, document the finding before resuming |
| Latency breaches 8 ms | Feature fetch moved onto the request path | Restore the cached point-in-time snapshot path; compression must not add per-request work |

## 9. Prevention Backlog

- Automate the 12-month label backfill with a freshness SLA per source.
- Shadow challenger promotion gate: parity on matured labels at equal approval mix.
- Reason-code stability monitoring so a model's explanations do not shift silently between versions.
- Scheduled rollback drill with measured detection-to-mitigation time, published to compliance.
- Counterfactual explanation tooling for consumer dispute responses.

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

> The deliverable is an 8 ms decision whose adverse action notice can be reconstructed from the stored contributions, with a rollback to a model compliance already signed off on.
