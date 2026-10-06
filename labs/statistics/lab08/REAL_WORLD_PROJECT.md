# REAL_WORLD_PROJECT — Experimentation Platform Design Standards

**Track:** statistics  |  **Lab:** lab08  |  **Level:** Advanced

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

A platform team runs 40 experiments a month across 9 teams. Half declare no sample size, three tests were confounded by launch timing, and a promotion decision last quarter rested on a study with 3% power.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Experiments | ~40 per month, mostly product and pricing changes |
| Current state | sample size optional; randomisation seed often unrecorded |
| Failures | 3 confounded designs, 1 decision on a 3%-power study, 2 inconclusive results explained after the fact |
| Constraint | teams move fast; the platform must not become a bottleneck |
| Requirement | defaults and guardrails that make good design the easy path |

## 3. Target Architecture

```text
 experiment intake
     |
 [1] estimand required (form refuses submission without it)
 [2] unit of randomisation declared (blocks pseudoreplication)
 [3] MDE + business threshold entered
     |
 power service: pilot variance lookup + inflation -> required n per arm
     |
 design validator: confounding check, blocking suggestion, replication check
     |
 randomisation service: seeded assignment + audit
     |
 pre-registration store (analysis plan, contrasts, stopping rule)
     |
 results: pre-specified analysis only; deviations flagged
     |
 post-hoc: inconclusive studies feed updated defaults
```

## 4. Component Responsibilities

### 4.1 Intake and estimand enforcement

- Estimand field required at submission, phrased as a quantity with a population and a contrast
- Unit of randomisation declared explicitly to prevent pseudoreplication
- Minimum effect worth detecting and business threshold entered before exposure
- Guardrails recorded with non-inferiority margins at submission

### 4.2 Power and sizing service

- Pilot variance looked up per metric from historical experiments rather than entered by hand
- Variance inflated by a documented factor with the reasoning recorded
- Required sample size per arm returned with the horizon at the team's traffic
- Achievable minimum detectable effect shown so teams see the design's resolution

### 4.3 Design validation

- Confounding check: flags factors that cannot vary independently
- Blocking suggestions based on the dominant known nuisance variables
- Replication check per factorial cell, preventing interaction-error conflation
- Validation results returned as actionable fixes rather than rejections

### 4.4 Randomisation and pre-registration

- Seeded assignment service with the seed stored alongside results
- Assignment audit reporting realised arm sizes against the design
- Analysis plan pre-registered including contrasts, interactions and stopping rule
- Post-hoc deviations flagged and reviewed rather than silently accepted

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Estimand and unit-of-randomisation requirements in the intake form |
| Week 3 | Power service with pilot variance lookup and documented inflation |
| Week 4-5 | Design validation with actionable fixes, piloted on two teams |
| Week 6 | Randomisation service and pre-registration store integrated |
| Week 8 | Full rollout; quarterly review of inconclusive studies updating the defaults |

## 6. Runbook (copy-paste)

```bash
# Submission requirements status for an experiment
curl -s 'localhost:8084/intake/exp-221/requirements' | jq '{estimand,unit,mde,businessThreshold,power}'

# Power service result with the inputs it used
curl -s 'localhost:8084/power?metric=conversion&mde=0.003' | jq '{pilotVar,inflationFactor,requiredN,horizonDays}'

# Design validation findings and suggested fixes
curl -s 'localhost:8084/validate?experiment=exp-221' | jq '{confounded,blockingSuggestion,replicationOk,fixes}'

# Randomisation audit: realised arm sizes against design
curl -s 'localhost:8084/randomisation/audit?experiment=exp-221' | jq '{seed,expected,realised,ok}'

# Inconclusive studies in the last quarter and their causes
curl -s 'localhost:8084/retrospective?window=90d' | jq '.[] | {id,cause,requiredN,achievedN}'
```

## 7. Observability and SLOs

- Compliance: submissions with a written estimand and unit of randomisation (target 100%).
- Power: studies launched below 80% power (target zero).
- Design: confounded designs caught by validation before exposure (target all).
- Outcome: inconclusive rate falling as defaults improve, tracked by cause.
- Trust: pre-registration compliance and post-hoc deviations reviewed monthly.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A team bypasses the power requirement under deadline | The requirement blocks rather than guides | Return the required n and horizon immediately; allow submission only with an override that expires |
| Pilot variance is stale for a changed metric | Variance lookup not refreshed | Refresh variance estimates on a schedule and alert when a metric's variance shifts |
| A confounded design still reaches production | Validation advisory rather than blocking | Block exposure on a confounding failure, with an override that expires |
| Randomisation seed unrecorded on legacy experiments | Migration gap | Backfill seeds where possible; require seeds for all new submissions |
| Inconclusive studies keep occurring | Defaults not updated from retrospective review | Quarterly review feeding required-n and variance defaults |

## 9. Prevention Backlog

- Automatic variance estimation per metric from historical experiment outcomes.
- Sequential design support with interim futility rules in the platform.
- Blocking suggestion engine learning which nuisance variables matter per domain.
- Multivariate designs with correlation structures for multi-metric experiments.
- Guardrail library per experiment type with standard non-inferiority margins.

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

> The deliverable is a platform where a team cannot accidentally launch an unpowered or confounded study, and where every inconclusive result improves the defaults for the next one.
