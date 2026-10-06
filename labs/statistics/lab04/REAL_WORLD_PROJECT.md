# REAL_WORLD_PROJECT — Experiment Platform Multi-Variant Analysis

**Track:** statistics  |  **Lab:** lab04  |  **Level:** Intermediate

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

A marketplace runs weekly copy tests across 6 variants with 200,000 sessions each. The team reports 'variant 3 won, F = 6.2, p < 0.05' and last quarter they shipped a variant that was worse on revenue while better on clicks.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Variants | 6 arms, roughly equal allocation, ~200k sessions each |
| Frequency | one multi-arm test per week, plus weekly re-tests |
| Metrics | click-through, conversion, GMV per session, refund rate |
| Problem | omnibus test without effect size, and no multiplicity control across variants |
| Constraint | decisions must land within the weekly release window |

## 3. Target Architecture

```text
 experiment registry (variants, primary metric, planned contrasts)
     |
 assignment + telemetry --> per-arm summaries (n, mean, variance)
     |
 [1] assumption checks: variance ratio, residual shape, sample sizes
 [2] omnibus: one-way ANOVA with Welch fallback
     |                  + effect size with CI per arm vs control
 [3] multiplicity: Tukey for all pairs, Bonferroni for planned contrasts
 [4] guardrails as non-inferiority bounds
     |
 decision: promote only where the interval clears the business threshold
     |
 report: which variants differ, by how much, in business units
```

## 4. Component Responsibilities

### 4.1 Analysis pipeline

- Per-arm summaries computed once and shared with the test and the report
- Assumption checks recorded per test, with the test choice recorded alongside the result
- Effect size with confidence interval per arm against the control, not only a global eta-squared
- Welch's ANOVA used automatically when the variance ratio is material

### 4.2 Multiplicity control

- Tukey for all pairwise comparisons against the control arm
- Bonferroni for pre-planned contrasts declared at registration
- Multiplicity method declared in the test record, not chosen after seeing results
- A simulation harness that verifies the family's error rate on this data's variance structure

### 4.3 Guardrails and decision rules

- GMV per session as the primary business metric, with click-through and refunds as guardrails
- Guardrails evaluated as non-inferiority bounds with pre-agreed margins
- Promotion requires the effect interval to clear a pre-agreed threshold
- A variant that wins on clicks while losing on GMV is reported as a failure, with the interval shown

### 4.4 Reporting and learning

- Every test report names which variants differ, by how much, with intervals in business units
- Re-test variance tracked so repeated weekly tests on the same variant are accounted for
- Post-hoc analysis of reversed decisions feeds the pre-registration defaults
- Weekly portfolio view: tests run, variants shipped, variants reverted

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1 | Centralise per-arm summaries; add assumption checks and effect sizes with intervals |
| Week 2 | Multiplicity control in the analysis path with a declared method per test |
| Week 3 | Business-threshold promotion rule and guardrail non-inferiority checks |
| Week 4-5 | Re-test variance tracking and weekly portfolio dashboard |
| Week 6 | Post-hoc review of the reversed decision; defaults updated in registration templates |

## 6. Runbook (copy-paste)

```bash
# Per-arm summaries for a test
curl -s 'localhost:8089/tests/t-221/arms' | jq '.[] | {arm,n,mean,sd}'

# Assumption checks and the test chosen
curl -s 'localhost:8089/tests/t-221/assumptions' | jq '{varianceRatio,residualShape,test,reason}'

# Omnibus result with effect size and interval
curl -s 'localhost:8089/tests/t-221/anova' | jq '{f,df1,df2,p,etaSquared,ci}'

# Pairwise differences against control with multiplicity control
curl -s 'localhost:8089/tests/t-221/pairs?method=tukey' | jq '.[] | {arm,delta,ci,pAdjusted,clearsThreshold}'

# Guardrail status as non-inferiority bounds
curl -s 'localhost:8089/tests/t-221/guardrails' | jq '.[] | {metric,delta,bound,status}'
```

## 7. Observability and SLOs

- Process: multiplicity method declared at registration for 100% of tests.
- Decision quality: promoted variants whose effect interval clears the business threshold.
- Reversals: reverts per quarter with a recorded cause, trending down.
- Integrity: tests reporting effect sizes with intervals rather than a bare p-value.
- Learning: post-hoc reviews feeding updated registration defaults.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A variant wins on clicks and ships while GMV falls | No business metric threshold | Require the effect interval to clear a pre-agreed business threshold on the primary metric |
| A false winner is reported | Uncontrolled pairwise comparisons | Tukey across arms, method declared at registration |
| Weekly re-tests of the same variant compound error | Repeated looks across weeks | Track re-test variance and account for repeated testing of the same variant |
| The omnibus test is significant but no pair localises | Low power for pairwise comparison at this n | Report power for the pairwise step; consider pooling or extending the horizon as registered |
| Variance differences across arms distort the F test | Homogeneity violated | Automatic Welch routing with the reason recorded |

## 9. Prevention Backlog

- Variance-reduction technique applied consistently across arms.
- Automatic assumption checks that block reporting when unverified.
- Expected false discovery control offered as an alternative to family-wise error.
- Hierarchical or Bayesian model for repeated variants across weekly tests.
- Post-hoc analysis automation feeding registration defaults.

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

> The deliverable is a weekly test process where every decision names which variants differ, by how much, with intervals in business units, and no click-through win can ship against revenue.
