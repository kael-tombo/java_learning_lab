# REAL_WORLD_PROJECT — GPU Platform as Code

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

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

A platform team runs 120 GPU-hours a day for 9 ML teams on one cloud account. Everything was created in consoles, nobody knows what exists, the last month's bill doubled, and a junior engineer deleted a production feature store during a cleanup.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Spend | GPU hours across 9 teams, last month's bill up 2.1x |
| State | unknown: resources created in consoles with no tags |
| Incident | a production feature store deleted during a manual cleanup |
| Utilisation | unknown; suspected well under 50% of provisioned capacity |
| Goal | everything in reviewed code, attributable, quota'd, with tested recovery |

## 3. Target Architecture

```text
 discovery scan (existing console resources)
     |
 import into code as reviewed modules
     |
 code (topology) + env config (values)
     |
 PlanDiff (typed) --> review --> apply
     |                    |
 policy checks        audit record + reviewer
 (tags, encryption,
  no public access)
     |
 drift detection (scheduled, attributed, reported)
     |
 cost allocation + idle quota report -> finance + team owners
     |
 stateful recreate drill (quarterly, sandbox, timed)
```

## 4. Component Responsibilities

### 4.1 Discovery and import

- Scan the account for unmanaged resources and tag them for ownership triage
- Import high-value resources into code as reviewed modules with an owner
- Legacy resources get an expiry date and a migration plan rather than open-ended existence
- Cost baseline captured before changes so optimisation can be measured

### 4.2 Code, policy and review

- Topology code separate from environment configuration
- Policy-as-code checks for tags, encryption and no public access at plan time
- Plan review enforced by the pipeline with a named reviewer recorded
- Destructive changes require recovery evidence naming snapshot and age

### 4.3 Governance and cost

- Per-team quotas with priority classes so serving preempts batch
- Mandatory cost and purpose tags enforced at plan time
- Idle quota detection under 20% sustained for 7 days, routed to owners
- Monthly cost allocation by team published with prior-month comparison

### 4.4 Recovery and operations

- Quarterly recreate drill in a sandbox with measured RTO against policy
- Backups and restore tested, not assumed; RPO enforced at plan validation
- Drift detected on a schedule and attributed; never auto-corrected
- Runbook covering import, review, apply, drift and recovery

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Scan and tag unmanaged resources; establish the cost baseline |
| Week 3-4 | Import production-critical resources into reviewed code with owners |
| Week 5 | Policy-as-code checks in the plan pipeline; enforce review with a named reviewer |
| Week 6-7 | Quotas, priorities and cost allocation published per team |
| Week 8-9 | First sandbox recreate drill; drift detection scheduled; runbook published |

## 6. Runbook (copy-paste)

```bash
# What exists in the account, tagged and attributed
curl -s localhost:8080/infra/discovery | jq '.[] | {type,address,owner,costTags}'

# Reviewable plan before any apply
curl -s 'localhost:8080/infra/plan?env=prod' | jq '{creates,updates,destroys,blocked}'

# Drift by team with owners
curl -s 'localhost:8080/infra/drift?window=7d' | jq '.[] | {address,kind,owner}'

# Cost allocation and idle quota by team
curl -s 'localhost:8080/infra/cost?window=30d' | jq '.byTeam,.idleQuota'

# Request a stateful recreate with recovery evidence
curl -XPOST localhost:8080/infra/recreate -d '{"resource":"feature-store-prod","snapshot":"snap-221","ageHours":2}'
```

## 7. Observability and SLOs

- Coverage: percentage of production resources in reviewed code (target 100%).
- Cost: monthly bill trend and idle quota removed, with savings tracked against the baseline.
- Safety: destructive changes without recovery evidence (target zero).
- Governance: resources missing cost or purpose tags (target zero, enforced at plan time).
- Recovery: quarterly recreate drill RTO measured against policy.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A production resource is deleted outside the pipeline | Console access still exists | Remove standing console write access; route changes through the pipeline |
| Team complains about quota despite idle capacity elsewhere | Quota set per team, not per workload class | Partition quotas by workload class and priority so serving and batch compete correctly |
| Drift report is ignored | No owner per resource | Attribute every resource to a team; route drift to the owner as a ticket |
| A recreate drill takes four times the policy RTO | Restore path untested until now | Fix the runbook; re-drill until it meets policy before allowing production changes |
| Cost drops then infrastructure capacity is needed urgently | Idle quota removed too aggressively | Keep a documented buffer; convert unused quota to on-demand with an approval |

## 9. Prevention Backlog

- Automated discovery of untagged resources with owner routing.
- Policy-as-code checks for network posture beyond tags and encryption.
- Reserved capacity modelling against historical utilisation.
- Cost allocation integrated with the experiment tracker so GPU spend attributes to model runs.
- Automated drift-to-ticket workflow with owner acknowledgement.

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

> The deliverable is nine teams and 120 GPU-hours a day where every resource is in reviewed code, every spend is attributable, and the next cleanup cannot delete production.
