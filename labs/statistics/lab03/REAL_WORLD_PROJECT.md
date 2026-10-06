# REAL_WORLD_PROJECT — Experiment Inference for a Live Ranking Change

**Track:** statistics  |  **Lab:** lab03  |  **Level:** Intermediate

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

A marketplace tests a ranking change with a live A/B framework. The team reported 'significant at p < 0.05, ship it' and the change was reverted a week later. Nothing in the process distinguished a real improvement from a daily look.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Traffic | 18M sessions/day, peak 5k QPS |
| Primary metric | GMV per session, heavy-tailed and noisy |
| Current practice | p < 0.05 from a nightly check, no effect size, no power |
| Outcome | one revert last month, one disputed claim in the current test |
| Constraint | trading decisions must move weekly, so speed matters |

## 3. Target Architecture

```text
 experiment registry (H0, direction, alpha, power, n, horizon)
     |
 assignment (stable hash) --> telemetry
     |
 [1] assumption checks: variance, independence, heavy tails
 [2] primary test: Welch t on GMV/session (or variance reduction applied)
 [3] effect size + 95% interval, always reported
 [4] guardrails as non-inferiority checks
     |
 decision engine
   significant + interval clears business threshold -> promote
   inconclusive -> report power, extend horizon if planned, do not ship
     |
 decision memo: effect, interval, power, business translation
 monitoring: sequential re-check with alpha control
```

## 4. Component Responsibilities

### 4.1 Pre-registration and power

- Every experiment registers hypothesis, direction, alpha, power, MDE, sample size and horizon before exposure
- Sample size derived from the variance of the primary metric, measured on recent traffic rather than assumed
- Minimum detectable effect agreed with the business before the run
- Registration is required for traffic allocation; unregistered tests are not reported as decisions

### 4.2 Assumptions and inference

- Variance checked per arm; Welch's t used unless equal variance is justified
- Heavy tails addressed with a variance-reduction technique or a rank-based sensitivity analysis
- Primary effect reported with a confidence interval, never a p-value alone
- Guardrails evaluated as non-inferiority bounds with pre-agreed margins

### 4.3 Decision engine

- Ship requires the confidence interval's lower bound to clear a pre-agreed business threshold, not merely p < alpha
- Inconclusive results report power and either extend the horizon as planned or stop, with the reason recorded
- Override path is possible but logged, expiring and reviewed monthly
- Every decision produces a memo with effect, interval, power and business translation

### 4.4 Ongoing discipline

- Interim looks use a sequential design with alpha control, or are recorded as non-decisional
- Variance-reduction technique calibrated on recent traffic so its gain is known before the test
- Reverted changes reviewed to extract what the inference missed
- Experiment portfolio view: running, inconclusive, shipped, reverted

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Experiment registry with mandatory pre-registration and power from measured variance |
| Week 3 | Assumption checks and a rank-based sensitivity analysis added to the report |
| Week 4 | Decision engine requiring an interval-based business threshold |
| Week 5-6 | Sequential interim looks with alpha control; override review process |
| Week 8 | Post-incident review of the reverted change; portfolio dashboard live |

## 6. Runbook (copy-paste)

```bash
# Registered plan for an experiment
curl -s 'localhost:8088/experiments/exp-221/plan' | jq '{hypothesis,direction,alpha,power,n,horizon,mde}'

# Assumption checks and the chosen test
curl -s 'localhost:8088/experiments/exp-221/assumptions' | jq '{varianceRatio,independent,heavyTailed,test,notes}'

# Effect size with interval, plus power if inconclusive
curl -s 'localhost:8088/experiments/exp-221/result' | jq '{estimate,ci,power,clearsBusinessThreshold}'

# Guardrail status as non-inferiority bounds
curl -s 'localhost:8088/experiments/exp-221/guardrails' | jq '.[] | {metric,delta,lower,bound,status}'

# Overrides and reverts in the last 90 days
curl -s 'localhost:8088/experiments/overrides?window=90d' | jq '.[] | {id,actor,reason,expiresAt,reverted}'
```

## 7. Observability and SLOs

- Process: pre-registration compliance at 100% before exposure.
- Decision quality: fraction of shipped changes whose interval clears the business threshold.
- Reversals: reverts per quarter with a recorded cause.
- Honesty: experiments reporting power when inconclusive, versus shipping anyway.
- Speed: median time-to-decision against the planned horizon, with sequential re-check rules.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A change ships on p < 0.05 with a trivial effect | No business threshold on the interval | Require the interval's lower bound to clear a pre-agreed threshold |
| Interim looks inflate the false positive rate | Daily uncorrected significance checks | Use a sequential design with alpha control; interim looks are non-decisional |
| A test concludes 'no difference' after a short run | No power reporting | Report power and MDE; extend the horizon only as pre-registered |
| Heavy-tailed GMV/session makes the t-test unreliable | Assumptions unchecked | Variance reduction plus a rank-based sensitivity analysis reported alongside |
| Overrides become routine | No expiry or review | Overrides expire automatically and are reviewed monthly with outcomes |

## 9. Prevention Backlog

- Variance-reduction technique calibrated per metric from historical traffic.
- Sequential design with alpha spending implemented in the decision engine.
- Automated assumption checks blocking tests that violate stated requirements.
- Equivalence testing for 'no meaningful difference' questions.
- Post-hoc analysis of reverted experiments fed back into the pre-registration defaults.

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

> The deliverable is an experimentation framework where a ship decision requires an interval that clears a business threshold, inconclusive means power rather than optimism, and no interim look can manufacture a result.
