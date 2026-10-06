# REAL_WORLD_PROJECT — Model Rollout Experimentation Platform

**Track:** mlops  |  **Lab:** lab10  |  **Level:** Advanced

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

A marketplace rolls out a new ranking model roughly monthly across 12 teams. Decisions are made from offline metrics and Slack discussion, and last quarter two rollouts had to be reverted after customer complaints the offline metrics never saw.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Sessions | ~120M/month, peak 5k QPS |
| Rollouts | ~12 model rollouts per month, each 5-30% of traffic |
| Primary metric | GMV per session, with a 30-day order attribution window |
| Current practice | Offline metric comparison plus Slack approval |
| Historical problem | 2 reverts in the last quarter; 1 rollout shipped with no guardrails |

## 3. Target Architecture

```text
 experiments service
   |
 registration: primary metric, MDE, alpha, power, horizon, guardrails
   |
 assignment (stable hash on user + session, exposure ramp 1->5->25->50%)
   |
 measurement pipeline: exposure events + outcomes (30-day attribution)
   |
 +-+------------------+------------------+
 |                  |                  |
 SRM check      primary metric     guardrails (non-inferiority)
 |                  |                  |
 +------------------+------------------+
   |
 sequential inference (alpha spending) + exposure ramp gating
   |
 decision record -> registry promotion (lab03) with the experiment attached

 platform dashboards: active experiments, time-to-decision, effect sizes
 quarterly review: experiments run, reverts, guardrail stops
```

## 4. Component Responsibilities

### 4.1 Experiment service and registry

- Pre-registration requiring primary metric, MDE, alpha, power, horizon and guardrails before exposure
- Assignment by stable hash with an exposure ramp; no assignment state to lose
- Experiment record attached to the promoted model version and the decision memo
- Templates per experiment type with pre-agreed guardrails and attribution windows

### 4.2 Measurement pipeline

- Exposure events with experiment id, arm, model version and timestamp
- Outcomes joined by user with a declared 30-day attribution window for GMV
- Join health monitored: match rate, late arrivals and duplicate attribution
- Metric definitions centralised so two experiments cannot define GMV differently

### 4.3 Inference and safety

- SRM check before every metric read, blocking the readout on mismatch
- Sequential inference with alpha control; fixed horizon for low-risk rollouts
- Guardrails as non-inferiority bounds on complaints, refunds, latency and seller-side fairness
- Automatic ramp pause on a guardrail breach, with a pre-authorised revert path

### 4.4 Operations and governance

- Decision memo template requiring effect size, interval and business translation
- Time-to-decision tracked per experiment; a stalled experiment escalates
- Quarterly review of reverts, guardrail stops and experiments never concluded
- Experimentation metrics shared with the platform team as a portfolio view

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Stand up exposure event logging and verify the outcome join with a sample audit |
| Week 3 | Experiment service with pre-registration, stable assignment and SRM checks |
| Week 4-5 | Sequential inference plus guardrail definitions agreed with support and risk |
| Week 6-7 | Migrate two teams' monthly rollouts onto the platform; measure time-to-decision |
| Week 9 | All teams migrated; revert drill; quarterly review process established |

## 6. Runbook (copy-paste)

```bash
# Active experiments and their state
curl -s localhost:8080/experiments | jq '.[] | {id,model,exposure,state,guardrails}'

# Check sample ratio mismatch BEFORE reading metrics
curl -s 'localhost:8080/experiments/exp-221/srm' | jq '{control,treatment,chi2,passed}'

# Primary metric with effect size and interval (sequential boundaries applied)
curl -s 'localhost:8080/experiments/exp-221/result' | jq '{metric,delta,ci,bounds,decision}'

# Guardrail status per metric
curl -s 'localhost:8080/experiments/exp-221/guardrails' | jq '.[] | {metric,delta,bound,status}'

# Pause the ramp and revert on a guardrail breach (pre-authorised)
curl -XPOST localhost:8080/experiments/exp-221/pause -d '{"reason":"guardrail:complaints"}'
```

## 7. Observability and SLOs

- Process: pre-registration compliance at 100% before any exposure.
- Speed: median time-to-decision, tracked against the planned horizon.
- Integrity: SRM checks passing; join match rate above 99%.
- Safety: guardrail stops and reverts per quarter, trending down.
- Impact: decision-quality review sampling concluded experiments to confirm effect sizes hold.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A rollout is reverted a week after launch | No guardrails at pre-registration | Block exposure without guardrails; migrate rollouts one team at a time |
| An experiment shows an implausible 400% lift | SRM mismatch or attribution bug | SRM check blocks the readout; audit the join before believing anything |
| Experiments never conclude because the horizon is unbounded | No MDE or sample size computed | Require MDE, power and horizon at registration; escalate stalled experiments |
| Two teams define GMV differently | Metric definitions not centralised | Central registry for metric definitions; reject experiments with ad-hoc definitions |
| Guardrail breach discovered after exposure ramp reached 50% | Ramp not gated on guardrails | Gate each ramp step on guardrail status; pause automatically and pre-authorise revert |

## 9. Prevention Backlog

- Interference-aware designs for marketplace experiments where users interact.
- Shared guardrail catalogue per experiment type, agreed with support and risk.
- Decision-quality sampling to verify concluded effects persist after launch.
- Bandit allocation for high-volume, low-cost model choices.
- Experiment portfolio view: running, stalled, concluded, reverted.

## 10. Postmortem Outline (skeleton)

1. **Impact** - who was hurt, for how long, in which numbers.
2. **Timeline** - detection, diagnosis, mitigation, resolution (UTC).
3. **Detection gap** - which signal should have fired first?
4. **Root cause** - the mechanism, not the person.
5. **What went well** - the thing that shortened the incident.
6. **Action items** - owner, date, and the alert or test that proves each one.

## 11. Sourced field notes (fetched Oct 2026 — verify before citing)

- **MLflow — Tracking and Model Registry documentation**: https://mlflow.org/docs/latest/ml/tracking/
  Reference model for experiment/run/metric lineage and the registry lifecycle (the vocabulary this lab re-implements in Java).
- **Kubernetes — ConfigMaps and Secrets**: https://kubernetes.io/docs/concepts/configuration/configmap/
  How configuration is injected into scheduled workloads — the practical lineage story for a DAG run that must be reproducible months later.
- **DVC — data and model versioning**: https://dvc.org/doc/user-guide
  Content-addressed versioning of datasets and model binaries; the standard way to make a data snapshot referenceable in a run record.

> The deliverable is 12 rollouts a month where every exposure was pre-registered, every readout passed an SRM check, every decision carried an effect size in business units, and no rollout was reverted for a problem the guardrails could have seen.
