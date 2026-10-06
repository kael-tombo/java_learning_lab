# REAL_WORLD_PROJECT — Latency and Throughput Reporting for a Serving Fleet

**Track:** statistics  |  **Lab:** lab01  |  **Level:** Foundational

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

A 200-node serving fleet reports p50 45 ms and mean 190 ms on the same dashboard. Nobody agrees which number the SLO should use, and two outlier nodes were quietly excluded from the reporting last quarter.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Fleet | 200 nodes, ~90k requests/second aggregate |
| Reporting today | p50 45 ms and mean 190 ms on one chart |
| Dispute | no agreed primary metric, so no agreed SLO |
| Data issue | two nodes excluded from reporting without a record |
| Requirement | shape-aware reporting with segment context and stated conventions |

## 3. Target Architecture

```text
 request telemetry (path, model version, node, region)
    |
 stable streaming stats per node (Welford)
    |
 segment by: node | region | model version | endpoint | traffic class
    |
 shape classification per segment
    |
 report: symmetric -> mean +/- sd; skewed -> p50/p90/p99
    |
 exclusions require a recorded reason and an expiry
    |
 SLO defined on the primary metric with the convention stated
```

## 4. Component Responsibilities

### 4.1 Metric definition

- Primary latency metric agreed as p99 per node, with the estimator and quantile convention documented
- Secondary metrics p50, p90, mean and sd retained so disagreements can be inspected rather than argued
- Metric computed per segment: node, region, model version, endpoint and traffic class
- Throughput reported alongside latency so a latency improvement bought by rejection is visible

### 4.2 Stable computation

- Streaming Welford statistics so a 90k/s stream is summarised without retention
- Quantiles from a bounded reservoir with a declared sampling method
- Shape classification per segment so skewed segments do not inherit a symmetric summary
- Cross-checks against a full-recomputation sample to validate the streaming estimate

### 4.3 Exclusion discipline

- Excluding a node requires a recorded reason, an owner and an expiry
- Excluded nodes remain visible in a separate panel rather than vanishing
- Weekly review of exclusions with automatic expiry
- Any exclusion overlapping a bad node is flagged to the on-call engineer

### 4.4 Reporting and SLO

- One chart per segment with shape-appropriate summary selection
- SLO stated on the primary metric with its convention in the panel title
- Segment context always accompanies an aggregate, so reversals cannot hide
- Distribution-level incident detection: shape change as well as threshold breach

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Agree and document the primary metric, estimator and quantile convention |
| Week 2 | Streaming statistics per segment with cross-checks against full recomputation |
| Week 3 | Shape classification per segment; automated summary-family selection |
| Week 4 | Exclusion discipline with recorded reasons, owners and expiry |
| Week 5 | Per-segment dashboards plus a distribution-level incident detector |

## 6. Runbook (copy-paste)

```bash
# Primary metric for a segment, with the convention in the response
curl -s 'localhost:9090/latency?segment=region:eu-west&metric=p99&estimator=reservoir' | jq '.value,.unit,.convention'

# Full shape report for a segment (skewness, percentiles, mean/sd)
curl -s 'localhost:9090/latency/shape?segment=node:eu-17' | jq '{skewness,p50,p90,p99,mean,sd,classification}'

# Current exclusions with reason, owner and expiry
curl -s 'localhost:9090/exclusions' | jq '.[] | {segment,reason,owner,expiresAt}'

# Cross-check streaming stats against a full recomputation sample
curl -s 'localhost:9090/latency/verify?segment=region:eu-west' | jq '.streaming,.recomputed,.delta'

# Segment breakdown for an aggregate you are about to quote
curl -s 'localhost:9090/latency/breakdown?window=15m' | jq '.segments[] | {segment,p99,shape}'
```

## 7. Observability and SLOs

- Definition: primary metric, estimator and quantile convention documented and versioned.
- Accuracy: streaming statistic versus full recomputation delta below 1% on every segment.
- Coverage: segments with shape classification at 100%, and exclusions all with reasons and expiry.
- SLO: percentage of nodes meeting the stated p99, reported per segment and in aggregate.
- Trust: aggregate quotes accompanied by segment breakdowns (measured in reviews).

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| Aggregate p99 looks healthy while one region is degraded | Aggregate masking segment shape | Per-segment reporting is mandatory; the aggregate always ships with a breakdown |
| Streaming statistic drifts from the true value | Reservoir sampling bias or non-stationary stream | Cross-check against full recomputation on a sample; alert on the delta |
| A node is excluded without a record | No exclusion discipline | Exclusions require reason, owner and expiry, and appear in a visible panel |
| Latency improves while error rate rises | Rejections moved out of the latency path | Report throughput and error rate beside latency so the trade is visible |
| SLO disputes recur | No agreed primary metric and convention | Version the metric definition; disagreements are about estimation, not performance |

## 9. Prevention Backlog

- Distribution-level incident detection that alerts on shape change as well as thresholds.
- Per-traffic-class latency reporting so mix shift cannot hide a regression.
- Automated summary-family selection driven by measured skewness.
- Cross-region percentile aggregation that does not average averages.
- Monthly audit of exclusions and metric definition changes.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **NIST/SEMATECH e-Handbook of Statistical Methods**: https://www.itl.nist.gov/div898/handbook/
  Authoritative reference for estimators, measures of central tendency and dispersion, with the guidance on when each is appropriate.
- **SciPy — statistics module documentation**: https://docs.scipy.org/doc/scipy/reference/stats.html
  Reference implementations of distributions, hypothesis tests and descriptive statistics; the semantics this lab re-implements in plain Java.

> The deliverable is a fleet dashboard where one number is the agreed SLO, its convention is written down, its shape is known per segment, and every exclusion is visible with an expiry.
