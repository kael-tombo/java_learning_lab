# REAL_WORLD_PROJECT — Feature Compression for a Real-Time Risk Service

**Track:** ml  |  **Lab:** lab08  |  **Level:** Intermediate

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

A payments risk service scores authorisations in 8 ms from 480 features, many of them near-duplicates accumulated over six years of feature work. Latency budget is tight and the team wants fewer, faster features without losing accuracy.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Feature count | 480 features, median 0.3 pairwise |correlation| above 0.8 |
| Latency budget | p99 < 8 ms per authorisation, peak 4,200 auth/s |
| Retrain cadence | weekly challenger, monthly champion review |
| Downstream model | gradient-boosted trees today, a candidate linear model under evaluation |
| Constraint | explanations must remain attributable to business features for disputes |

## 3. Target Architecture

```text
 feature store (480 cols, versioned)
                        |
              drift checks + correlation census
                        |
        +---------------+----------------+
        |                                |
   PCA transform (fit weekly,     keep-all baseline
   versioned, k from validation)
        |                                |
        +---------------+----------------+
                        |
            challenger scores 100% of traffic in shadow
                        |
        +---------------+----------------+
        |               |                |
    champion        explanation      warehouse copy
   (k components)   (map back to     (full features
                      features)        for analysis)

   Guardrails: parity test, spectrum drift alert, rollback to keep-all
```

## 4. Component Responsibilities

### 4.1 Feature store and correlation census

- 480 versioned features with owners, freshness SLAs and a correlation census
- Near-duplicate groups identified and reported quarterly, independent of any model
- Null and staleness rates per feature, alerting when a feature silently dies
- Feature definition changes require a shadow window before enforcement

### 4.2 Transform tier

- PCA fit weekly on a trailing window, frozen for the week's scoring
- Mean, scale and component matrix versioned as one artifact; parity asserted on load
- k selected from downstream validation, with the curve attached to the model record
- Spectrum drift check: incoming per-feature variance compared to the fitted spectrum

### 4.3 Scoring and shadow evaluation

- Champion scores the k components; challenger scores full features
- Both evaluated on matured outcomes weekly; promotion requires parity or better
- Latency measured per path so the compression benefit is visible in p99
- Rollback to keep-all is one command and rehearsed quarterly

### 4.4 Explainability bridge

- Component contributions mapped back to the original features for disputes
- Explanations phrased as feature contributions, not component coordinates
- Component-to-feature mapping versioned alongside the transform
- Dispute path tested end to end before the transform reaches champion

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Correlation census and the keep-all baseline; publish latency and accuracy together |
| Week 2 | PCA challenger in shadow with parity tests and spectrum drift checks |
| Week 3 | k sweep with validation curves; latency comparison per path |
| Week 4 | Explainability bridge and a dispute dry run with the risk operations team |
| Week 5 | Champion cutover at 10% then 100%; rollback drill timed and documented |

## 6. Runbook (copy-paste)

```bash
# Champion version, k, and transform age
curl -s localhost:8080/admin/model | jq '{version,k,transformVersion,ageHours}'

# Latency by path (champion components vs challenger full)
curl -s 'localhost:8080/admin/latency?window=15m' | jq '.p50,.p95,.p99'

# Spectrum drift: incoming vs fitted per-feature variance
curl -s 'localhost:8080/admin/drift?spectrum=1' | jq '.features,.maxDelta,.threshold'

# Roll back to the keep-all path
curl -XPOST localhost:8080/admin/rollback -d '{"to":"risk-gb-full-v14"}'

# Explain one decision in original feature terms
curl -s 'localhost:8080/admin/explain?txnId=t-884213' | jq '.contributions,.features'
```

## 7. Observability and SLOs

- SLO: p99 authorisation scoring < 8 ms; availability 99.99%.
- Business: fraud loss basis points, measured against the pre-compression champion.
- Model: matured-outcome accuracy of champion versus challenger, weekly.
- Efficiency: p99 latency and p99 CPU per scoring path, before and after compression.
- Guardrails: parity test pass rate; spectrum drift alert volume; dispute explanation coverage.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Accuracy drops after the champion cutover | k too small, or a correlated pair was informative | Roll back to keep-all, re-sweep k on a longer window, re-promote only with parity evidence |
| Spectrum drift alert fires on a subset of merchants | A new integration changed feature semantics | Freeze the transform, investigate per-feature variance, version the feature change |
| p99 latency regresses after compression | Transform applied on the request path without caching | Precompute or cache; compression must not add per-request work |
| Dispute cannot be explained in feature terms | Mapping missing for a new component | Block promotion until the mapping and dispute test exist |
| Parity test fails intermittently | Floating-point ordering difference after serialisation | Round-trip test in CI; fix the serialisation precision, not the tolerance |

## 9. Prevention Backlog

- Automated near-duplicate feature detection with owner notification.
- Whitening experiment for the candidate linear model's coefficient stability.
- Component-to-feature explanation quality review with the disputes team each quarter.
- Incremental transform updates instead of full weekly refits.
- Documented rollback drill with measured detection-to-mitigation time.

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

> The deliverable is 8 ms scoring with parity against the full-feature path, explanations that a disputes team can read in business terms, and a rollback that has been rehearsed.
