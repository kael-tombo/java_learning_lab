# REAL_WORLD_PROJECT — Experiment Decision Platform with Posterior Reporting

**Track:** statistics  |  **Lab:** lab06  |  **Level:** Advanced

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

A marketplace runs 40 experiments a month and reports binary p-values. Three teams interpret p = 0.06 differently, two shipped changes on noisy data, and nobody can say the probability that a variant actually beats control.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Experiments | ~40 per month, mostly binary conversion metrics |
| Current reporting | p-values from frequentist tests, inconsistent interpretation |
| Problem | no decision probability; teams disagree on thresholds; rare misses unquantified |
| Constraint | reporting must integrate with existing dashboards and guardrails |
| Requirement | decision probabilities with priors, diagnostics and calibrated reporting |

## 3. Target Architecture

```text
 experiment results (conversions, exposures per arm)
    |
 [1] prior predictive check per experiment type
 [2] declared prior per experiment type + sensitivity record
 [3] posterior per arm: mean, HDI, ESS (enforced)
 [4] decision layer: P(variant beats control), P(variant clears MDE)
 [5] guardrails as non-inferiority posteriors
     |
 dashboard: decision probability as headline, interval always
     |
 experiment registry: prior, diagnostic status, decision, outcome
     |
 post-hoc calibration: do decisions with P > 0.9 actually win?
```

## 4. Component Responsibilities

### 4.1 Prior and model configuration

- A declared default prior per experiment type, with its rationale recorded in the registry
- Prior predictive check run per experiment type and re-checked when traffic mix shifts
- Prior sensitivity recorded for each decision: the conclusion under two priors, not just one
- Experiment type determines the likelihood, so a metric family does not silently use the wrong model

### 4.2 Inference and diagnostics

- Conjugate update where the model allows, sampling with enforced R-hat and effective sample size otherwise
- Interval reported as an HDI with the effective sample size alongside
- Guardrails evaluated as non-inferiority posteriors rather than point comparisons
- Convergence failures block reporting rather than producing a quiet interval

### 4.3 Decision layer

- Headline metric is P(variant beats control), computed from paired posterior draws
- Secondary metric P(variant clears the minimum detectable effect) separates 'better' from 'materially better'
- Guardrail posteriors block promotion when the probability of harm exceeds a threshold
- Inconclusive outcomes report the probability and, where registered, the option to extend the horizon

### 4.4 Calibration and learning

- Post-hoc calibration: outcomes of decisions taken at P > 0.9 tracked against realised win rates
- Calibration report published quarterly per experiment type
- Decision registry linking prior, diagnostic status, probability, guardrails and final outcome
- Registry used to refine default priors and the MDE defaults

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Declare default priors per experiment type with rationales; run prior predictive checks |
| Week 3 | Posterior computation per arm with HDI and enforced diagnostics |
| Week 4 | Decision layer with P(variant beats control) and P(clears MDE) |
| Week 5-6 | Guardrail posteriors blocking promotion on probable harm |
| Week 8 | Post-hoc calibration report and registry review feeding prior defaults |

## 6. Runbook (copy-paste)

```bash
# Decision summary for an experiment
curl -s 'localhost:8087/experiments/exp-221/decision' | jq '{pBeatsControl,pClearsMde,guardrails}'

# Posterior per arm with interval and diagnostics
curl -s 'localhost:8087/experiments/exp-221/posteriors' | jq '.[] | {arm,mean,hdiLow,hdiHigh,ess,rhat}'

# Prior used, rationale, and the sensitivity conclusion
curl -s 'localhost:8087/experiments/exp-221/prior' | jq '{prior,rationale,sensitivity}'

# Guardrail posteriors and the harm probability
curl -s 'localhost:8087/experiments/exp-221/guardrails' | jq '.[] | {metric,pHarm,pNoHarm}'

# Post-hoc calibration: realised win rate by probability band
curl -s 'localhost:8087/calibration?window=180d' | jq '.bands[] | {band,predicted,realised,n}'
```

## 7. Observability and SLOs

- Coverage: 100% of experiments report a decision probability with an interval.
- Diagnostics: convergence enforced; zero reports published from unverified draws.
- Calibration: realised win rate by probability band, published quarterly per experiment type.
- Decision quality: P > 0.9 decisions that actually win, tracked against the nominal 90%.
- Discipline: sensitivity recorded for 100% of shipped decisions.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A decision with P = 0.55 is shipped as a win | Probability misread as a threshold crossing | Report the probability prominently; require P above a declared threshold tied to the cost of being wrong |
| A posterior is reported from unverified draws | Diagnostics not enforced | Block reporting on R-hat and effective sample size failures |
| Two teams reach opposite conclusions on the same data | Different priors and models used | One prior per experiment type, declared in the registry, with sensitivity recorded |
| A guardrail harm probability is ignored | Guardrails reported as point comparisons | Guardrails become non-inferiority posteriors that block promotion on probable harm |
| The calibration report shows P = 0.9 decisions winning 75% of the time | Probabilities not calibrated for the decision context | Recalibrate or re-express as frequentist intervals with a declared interpretation |

## 9. Prevention Backlog

- Automatic prior updates from the decision registry, reviewed by a statistician.
- Posterior predictive checks per experiment type in the reporting pipeline.
- Decision-theoretic expected-value layer incorporating the cost of shipping.
- Continuous metrics modelled with conjugate normal-inverse-gamma posteriors.
- Calibration dashboards per experiment type with alerting on drift from nominal.

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

> The deliverable is a platform where every experiment reports the probability that a variant wins, the probability that the win matters, and the probability that a guardrail was harmed — with calibration proving those numbers mean what they say.
