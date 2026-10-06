# REAL_WORLD_PROJECT — Experiment Power and Resolution Standards

**Track:** statistics  |  **Lab:** lab10  |  **Level:** Advanced

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

A platform team runs 40 experiments a month. Three were launched with no power calculation, one 'inconclusive' result was used to justify abandoning a promising direction, and the business has stopped trusting experiment readouts.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Experiments | ~40 per month across 9 teams |
| Current practice | power optional; inconclusive results read as 'no effect' |
| Failures | 3 unpowered launches; 1 promising direction abandoned on a null result |
| Constraint | traffic varies enormously by product surface, so designs are not interchangeable |
| Requirement | power and resolution reported as a standard part of every readout |

## 3. Target Architecture

```text
 experiment intake (metric, surface, traffic)
     |
 variance service: per metric x surface, from historical experiments
     |  (inflated, with a documented factor)
 power service: alpha, power, MDE -> required n per arm
     |                          -> horizon at that surface's traffic
     |
 design accepted only if the horizon fits the decision calendar
     |
 readout: effect + interval + MDE + power (retrospective, at the a priori effect)
     |
 inconclusive handled as a power statement with options
     |
 post-hoc: abandoned directions reviewed; MDE recorded against the business threshold
```

## 4. Component Responsibilities

### 4.1 Variance and power services

- Per-metric, per-surface variance estimated from historical experiment outcomes rather than entered by hand
- Variance inflated by a documented factor with the reasoning stored
- Power computed under the a priori effect, with sidedness chosen explicitly
- Required n per arm returned with the horizon at that surface's real traffic

### 4.2 Resolution reporting

- MDE published with every experiment at intake and in every readout
- MDE expressed in business units so 'what we could not detect' is meaningful to stakeholders
- Achievement against the business threshold recorded: can this surface even detect it?
- Surfaces where the threshold is undetectable at achievable n are flagged before launch

### 4.3 Inconclusive handling

- Null results reported as a power statement with the MDE, never as 'no effect'
- Retrospective power computed at the a priori effect, not the observed one
- Standard options presented: extend as pre-registered, accept a null within the MDE, or stop
- Abandoned directions recorded with their MDE so future reviews can distinguish undetectable from absent

### 4.4 Governance and learning

- Design acceptance requires a power calculation with a stated effect and variance
- Overrides for deadline pressure expire and are reviewed with outcomes
- Quarterly review comparing business thresholds against achievable MDEs per surface
- Post-hoc power critique documented so teams stop quoting it as evidence

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Variance service per metric and surface from historical experiments |
| Week 3 | Power service returning n, horizon and MDE at intake |
| Week 4 | Resolution reporting in every readout; MDE in business units |
| Week 5-6 | Inconclusive handling with standard options; override review |
| Week 8 | Quarterly review of thresholds versus achievable MDEs; post-hoc power guidance published |

## 6. Runbook (copy-paste)

```bash
# Variance for a metric on a surface, with the inflation applied
curl -s 'localhost:8082/variance?metric=conversion&surface=checkout' | jq '{raw,inflated,factor,rationale}'

# Power service result at intake
curl -s 'localhost:8082/power?metric=conversion&surface=checkout&aod=0.002&alpha=0.05&power=0.8' | jq '{requiredN,horizonDays,mde,mdeBusiness}'

# Can this surface detect the business threshold at all?
curl -s 'localhost:8082/feasibility?metric=conversion&surface=checkout&aod=0.002' | jq '{detectable,achievableN,daysAvailable,verdict}'

# Readout with resolution, including inconclusive results
curl -s 'localhost:8082/readout?experiment=exp-221' | jq '{effect,ci,mde,powerRetrospective,verdict}'

# Inconclusive experiments in the last quarter with their MDE
curl -s 'localhost:8082/inconclusive?window=90d' | jq '.[] | {id,mde,businessThreshold,option}'
```

## 7. Observability and SLOs

- Compliance: experiments launched with a power calculation (target 100%).
- Detection: experiments whose reported verdict includes an MDE (target 100%).
- Feasibility: surfaces where the business threshold is undetectable flagged before launch.
- Outcome: directions abandoned on null results reviewed with their MDE recorded.
- Trust: experiment readouts used in decisions with resolution stated; overrides reviewed monthly.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A team launches without a power calculation under deadline | Requirement blocks rather than guides | Return n, horizon and MDE instantly; allow override that expires and is reviewed |
| Reported inconclusive is read as no effect | MDE not reported | MDE and retrospective power required in every readout |
| Power computed from the observed effect | Post-hoc power habit | Power service computes at the a priori effect; post-hoc power guidance published |
| A surface cannot detect its business threshold at any achievable n | Feasibility never checked | Feasibility check at intake flags undetectable thresholds with alternatives |
| Variance drifts as the metric's implementation changes | Variance cached too long | Variance service refreshes on a schedule and alerts on material shifts |

## 9. Prevention Backlog

- Automatic effect-size priors learned from resolved business thresholds.
- Power for count and ratio metrics beyond means and proportions.
- Equivalence-testing support for 'no meaningful effect' questions.
- Budget optimiser allocating traffic across a portfolio of concurrent experiments.
- Detection of metric definition changes invalidating cached variances.

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

> The deliverable is a platform where every experiment launches with a computed sample size, every readout states the smallest effect it could have detected, and an inconclusive result is read as a resolution statement rather than a verdict.
