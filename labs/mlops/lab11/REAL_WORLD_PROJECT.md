# REAL_WORLD_PROJECT — Governed Credit Decisioning

**Track:** mlops  |  **Lab:** lab11  |  **Level:** Advanced

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

A lender uses four models to make credit decisions for 2 million applicants a year. Fair-lending counsel requires reason codes and disparate-impact analysis for every model change, and the last review took three weeks because the evidence was assembled by hand each time.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Volume | 2M applications/year, ~8,000 per business day |
| Models | 4 decisioning models plus a rules engine |
| Regulatory regime | fair-lending review required for every model change |
| Current evidence | assembled manually per change, roughly 3 weeks |
| Goal | evidence produced by the pipeline in days, with every decision traceable |

## 3. Target Architecture

```text
 applications --> snapshot (point-in-time, validated)
        |
 model training --> evaluation (overall + per group, base rates first)
        |
 generated model card (data, metrics, limitations, reason codes)
        |
 governance policy (versioned) --> promotion gate
        |                          (fairness, lineage, evidence, sign-offs)
        | pass -> decisioning with reason codes
        | fail -> blocked with named reasons, owner notified
        |
 audit trail (hash chain, policy version) --> regulator export
        |
 post-launch fairness monitoring by group, continuous
```

## 4. Component Responsibilities

### 4.1 Fair-lending evaluation

- Per-group evaluation with base rates first, on protected attributes used for evaluation only
- Disparate impact ratio and gap evaluated against versioned policy thresholds
- Threshold sweep reporting how error rates and disparity move with the operating point
- Comparison against prior model versions so a change in disparity is visible

### 4.2 Generated model card and evidence

- Card generated from snapshot metadata, evaluation results and threshold settings
- Intended use, out-of-scope use and limitations written by the model owner and reviewed
- Reason-code catalogue versioned so adverse action notices remain explainable
- Parity test asserting generated card metrics equal recomputed metrics

### 4.3 Governance policy and promotion gate

- Versioned policy encoding fairness thresholds, lineage requirements and sign-offs
- Gate reports every failing check with a named reason and an owner
- Policy change blocks promotion until re-evaluated, recorded in the audit trail
- Four-fifths style screening plus absolute gap, both reported with interpretation

### 4.4 Audit and post-launch monitoring

- Hash-chained audit trail with actor, action, versions, policy version and evidence hash
- Chain verification run before every regulator export
- Continuous fairness and approval-rate monitoring by group after launch
- Regulator export package: card, evaluation, policy version and verified audit chain

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Baseline per-group evaluation on all four models with base rates and disparity |
| Week 3 | Fairness policy versioned and signed off by counsel and risk |
| Week 4-5 | Promotion gate enforcing the policy; model cards generated from the pipeline |
| Week 6-7 | Audit trail with hash chain; verification in the export path |
| Week 9 | Post-launch fairness monitoring; drill a policy-change scenario end to end |

## 6. Runbook (copy-paste)

```bash
# Fair-lending evaluation for a candidate model version
curl -s 'localhost:8088/fairness?model=income-gbm&version=13' | jq '{baseRates,disparityRatio,gap,thresholds}'

# Policy in force and the thresholds it applies
curl -s localhost:8088/governance/policy | jq '{versionId,thresholds,effectiveFrom}'

# Promotion gate result with every reason
curl -s 'localhost:8088/governance/gate?model=income-gbm&version=13' | jq '{passed,reasons}'

# Verify the audit chain before an export
curl -s 'localhost:8088/audit/verify?exportId=ex-221' | jq '{valid,entries,firstBreakAt}'

# Post-launch disparity by group, compared to the prior version
curl -s 'localhost:8088/monitoring/fairness?model=income-gbm&window=30d' | jq '.byGroup,.deltaVsPrevious'
```

## 7. Observability and SLOs

- Compliance: promotion blocked on any governance failure (target 100%).
- Evidence: regulator evidence package produced by the pipeline (target under 3 days, from 3 weeks).
- Fairness: disparity ratio and gap per group, reviewed per release.
- Integrity: audit chain verification passing on every export.
- Operations: mean time from model candidate to a compliant promotion decision.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A model ships with a disparity regression | Gate evaluated against superseded thresholds | Version the policy; block promotion until re-evaluated under the current policy |
| Evidence package assembly takes weeks again | Card and evaluation not generated by the pipeline | Generate everything from the pipeline; treat manual assembly as a defect |
| Regulator export fails chain verification | Audit log modified or truncated by a migration | Verify before export; alert on any chain break and reconcile from backups |
| A group experiences an approval-rate drop in production | Post-launch traffic differs from the training population | Pause rollout, run the threshold sweep, and escalate to counsel |
| Reason codes no longer explain adverse decisions | Model changed without regenerating the catalogue | Block promotion unless the reason-code catalogue version is updated |

## 9. Prevention Backlog

- Counterfactual fairness checks added to the standard evaluation.
- Disparity monitoring with automated thresholds and owner routing post-launch.
- Adversarial testing programme with outcomes fed into the policy review.
- Quarterly regulator dry run producing an export package end to end.
- Model version comparison view showing disparity deltas between versions.

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

> The deliverable is four credit models where every promotion carries generated evidence, a signed-off fairness policy, a verified audit chain, and reason codes that still explain the decisions being made.
