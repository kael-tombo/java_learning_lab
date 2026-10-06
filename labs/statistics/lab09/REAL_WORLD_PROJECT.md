# REAL_WORLD_PROJECT — Non-Parametric Analysis for Support Operations

**Track:** statistics  |  **Lab:** lab09  |  **Level:** Advanced

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

A support organisation compares median handle time across 40 queues, 4 regions and before/after a tooling change. Handle time is heavily skewed, groups are small, and one team applied a t-test and shipped the conclusion.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Queues | 40 queues × 4 regions, 6–80 tickets per group in weekly samples |
| Metric | handle time: heavily right-skewed, ordinal buckets in some tools |
| Current practice | t-tests and ANOVA on skewed data, median claims from p-values |
| Known failure | one team shipped a queue-mix change based on a t-test on 7 observations |
| Requirement | correct tests per design with effect sizes and localisation |

## 3. Target Architecture

```text
 ticket events (queue, region, handle time, week, tooling version)
     |
 shape diagnostics per group: skew, outliers, ordinal bucket use
     |
 test selection by design
   2 independent groups  -> Mann-Whitney
   before/after same queue -> Wilcoxon signed-rank
   40 queues across regions -> Kruskal-Wallis + Dunn (corrected)
   4 regions, same week   -> Friedman (blocked by week)
     |
 exact null for small groups; asymptotic for the 40-queue omnibus
     |
 effect size: probability of superiority / Cliff's delta with intervals
     |
 localisation with multiplicity correction; "significant" never reported alone
```

## 4. Component Responsibilities

### 4.1 Data quality and shape diagnostics

- Handle time retained in full with skew reported per group rather than binned silently
- Ordinal bucket handling where tools only record buckets, with the ordinal assumption stated
- Sample-size reporting per group, since rank tests are power-limited at small n
- Outliers retained with a note; rank tests tolerate them rather than justifying their removal

### 4.2 Test selection by design

- Before/after tooling change on the same queues: Wilcoxon signed-rank on within-queue differences
- Two queues or two regions: Mann-Whitney with the distributional null stated
- Many queues across regions: Kruskal-Wallis omnibus followed by Dunn's test with a correction
- Regions compared within week: Friedman, blocking by week so seasonality is not mistaken for a region effect

### 4.3 Inference and localisation

- Exact null enumeration for groups below about 20; asymptotic above with the tie correction applied
- Tie handling verified, since bucketed handle times produce many ties
- Post-omnibus localisation with multiplicity control; omnibus alone never reported
- Non-significant results reported with power and an effect-size interval rather than as no difference

### 4.4 Reporting and governance

- Every comparison reports the statistic, whether the p-value is exact, and an effect size with an interval
- Interpretation stated as distributional ordering or probability of superiority, never an unqualified median claim
- Analyses that would have used a parametric test are recorded so the change is auditable
- Tooling-change decisions require a rank test with localisation and an effect size above a business threshold

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Data quality and shape diagnostics; retain full handle times and report skew per group |
| Week 2 | Test selection by design implemented, replacing parametric defaults |
| Week 3 | Exact nulls for small groups; tie handling verified on bucketed data |
| Week 4 | Dunn's follow-up localisation and effect sizes with intervals |
| Week 5-6 | Reporting standard and governance for tooling-change decisions; retrospective review of prior conclusions |

## 6. Runbook (copy-paste)

```bash
# Shape diagnostics for a group's handle time
curl -s 'localhost:8083/ops/shape?queue=billing&week=2026-W37' | jq '{n,skew,outliers,ordinalBuckets}'

# Test selected for a comparison and why
curl -s 'localhost:8083/ops/test?comparison=tooling-before-after' | jq '{design,test,reason}'

# Result with exactness flag and effect size
curl -s 'localhost:8083/ops/result?comparison=tooling-before-after' | jq '{statistic,pValue,exact,probSuperiority,ci}'

# Omnibus and corrected localisation across queues
curl -s 'localhost:8083/ops/kruskal?week=2026-W37' | jq '{h,p,dunn:[.[]|{pair,pAdjusted}]}'

# Inconclusive comparisons with power and achievable effect
curl -s 'localhost:8083/ops/inconclusive?window=90d' | jq '.[] | {comparison,n,power,minDetectableEffect}'
```

## 7. Observability and SLOs

- Method: comparisons using the test matching their design (target 100%).
- Exactness: p-values from exact enumeration for groups below 20 (target 100%).
- Reporting: comparisons with an effect size and interval (target 100%).
- Localisation: significant omnibus results followed by corrected pairwise comparisons (target 100%).
- Outcome: tooling decisions with an effect size above the business threshold, tracked against outcomes.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A queue-mix change is reversed after rollout | A t-test on 7 observations | Rank test with effect size and localisation required before any tooling decision |
| Kruskal-Wallis is significant and nobody localises it | Omnibus reported alone | Dunn's follow-up is mandatory in the reporting path |
| Bucketed handle times inflate significance | Ties ignored in ranking | Average ranks with the tie correction; verified on bucketed data |
| A region is declared slower from a single week | No blocking by week | Friedman blocking by week, or region comparisons within week |
| Inconclusive results are read as no difference | Power not reported | Report power and the minimum detectable effect alongside every non-significant result |

## 9. Prevention Backlog

- Dunn's test with correction standardised across all omnibus comparisons.
- Cliff's delta with bootstrap intervals as the default effect size.
- Shape diagnostic thresholds blocking parametric tests automatically.
- Permutation framework covering designs the four named tests do not.
- Retrospective review of prior tooling decisions using the corrected methods.

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

> The deliverable is an operations analysis where every comparison uses the test its design requires, handles the ties that bucketed handle times create, and ships an effect size rather than a bare p-value.
