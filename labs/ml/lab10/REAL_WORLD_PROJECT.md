# REAL_WORLD_PROJECT — Online Evaluation Loop for a Ranking Model

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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

A marketplace search-and-rank model serves 40M queries a day. Offline metrics looked excellent, click-through is flat, and nobody can say which offline metric predicted anything. You build the evaluation loop that makes the answer knowable.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Query volume | ~40M queries/day, peak 12k QPS |
| Candidate set | 2M items, ranking 200 per query at p99 < 150 ms |
| Labels | clicks and orders arrive within minutes; long-term value in 14 days |
| Offline/online gap | NDCG@10 rose 4% over 6 weeks while CTR moved 0.1% |
| Release cadence | challenger scores 100% of traffic in shadow, twice weekly |

## 3. Target Architecture

```text
 query + candidates --> feature service (point-in-time)
                        |
        +---------------+----------------+
        |               |                |
  champion (live)   challenger        log store (impressions + features + scores)
        |            (shadow)                 |
        |                                    |
        +----------------+--------------------+
                         |
              offline evaluation suite (CI, versioned)
                         |
              outcome join (clicks, orders, 14d value)
                         |
        correlation dashboard: offline metric vs online delta
                         |
        promotion gate + automatic rollback
```

## 4. Component Responsibilities

### 4.1 Impression logging

- Log query id, candidate ids, features, scores, model version and position for every impression
- Sampling is documented; unsampled impressions must be reproducible from the log
- Log retention aligned to the longest label horizon (14 days for value)
- Log volume and drop rate themselves monitored — a silent gap biases every metric

### 4.2 Offline evaluation suite

- Versioned suite in CI: NDCG@k, MAP, MRR, calibration, and slice metrics per query intent
- Runs on a fixed query sample so scores are comparable week to week
- Leakage assertions: no post-click feature, no post-outcome feature
- Publishes the report as an artifact attached to the candidate model

### 4.3 Outcome joining and correlation

- Join outcomes to impressions with a documented attribution window
- Track offline/online correlation per metric over time, not once
- Segment by query intent, device and new/returning user
- Report the correlation with an interval; treat a weak correlation as a finding

### 4.4 Promotion and rollback

- Shadow evaluation with a fixed traffic slice and a minimum duration before promotion
- Promotion gate: offline metrics improve AND the online guardrails hold
- Automatic rollback on a guardrail breach (CTR, revenue per session, latency)
- Every promotion records the report artifact, the approver and the date

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Instrument impression logging; verify no gaps by sampling joins |
| Week 2 | Versioned offline suite in CI with leakage assertions and fixed query samples |
| Week 3 | Outcome join and the offline/online correlation dashboard |
| Week 4 | Promotion gate and automated rollback wired to guardrails |
| Week 6 | First two challenger cycles run end to end; document what the loop caught |

## 6. Runbook (copy-paste)

```bash
# Champion and challenger versions in flight
curl -s localhost:8080/admin/models | jq '{champion,challenger,shadowPct}'

# Impression log completeness for the last hour
curl -s 'localhost:8080/admin/loghealth?window=1h' | jq '.logged,.expected,.dropRate'

# Offline report for the challenger (CI artifact summary)
curl -s 'localhost:8080/admin/offline?version=ranker-v42' | jq '.ndcg10,.map,.calibrationEce'

# Offline/online correlation by metric, with intervals
curl -s 'localhost:8080/admin/correlation?window=28d' | jq '.ndcg,.ctr,.ci'

# Roll back to the champion (automatic on guardrail breach, manual here)
curl -XPOST localhost:8080/admin/rollback -d '{"to":"ranker-v41"}'
```

## 7. Observability and SLOs

- Business: revenue per session and CTR per query intent, with intervals, weekly.
- Reliability: impression log completeness > 99.9% and drop rate < 0.1%.
- Offline: NDCG@10 and MAP on a fixed query sample, versioned and comparable.
- Validity: offline/online correlation per metric with a confidence interval, tracked as a time series.
- Guardrails: p99 latency, result diversity, and zero-result rate per candidate set.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Offline metric improves, online metric flat | offline/online correlation is weak or the query sample drifted | Compare on intent slices, check log completeness, and treat the metric as unvalidated until correlated |
| Impression log gap during peak | Sampling or writer backpressure | Fall back to sampling-with-provenance, alert on drop rate, backfill from the query log |
| Candidate passes offline, breaches latency in shadow | feature fetch cost higher on live traffic | Promotion gate blocks; feature path optimised before retry |
| Zero-result rate spikes after a rollout | Candidate generation regression | Automatic rollback on the zero-result guardrail; investigate retrieval, not ranking |
| Ranking becomes homogeneous across users | Diversity guardrail absent | Add per-user result diversity as a hard guardrail and roll back |

## 9. Prevention Backlog

- Long-term value labels (14-day) joined automatically into the correlation dashboard.
- Per-intent metric slices with minimum sample sizes declared in the suite.
- Counterfactual logging of position bias correction so NDCG comparisons are honest.
- Automatic regression test that fails a candidate whose offline report is missing.
- Documented rollback drill with measured time-to-safe, published quarterly.

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

> The deliverable is a loop that says which offline metric earned the right to influence a decision — and rolls back automatically when one starts lying.
