# REAL_WORLD_PROJECT — Multi-Tenant Model Promotion Control Plane

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

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

A platform team serves 60+ models to 14 internal tenants across three regions. Promotions happen by Slack approval, rollback requires a meeting, and nobody can say which model is serving which tenant right now. You build the control plane.

**You are the on-call engineer.** The system below is the one you inherit, not a greenfield toy - the interesting work is in the seams.

## 2. Numbers That Matter

| Quantity | Value |
|---|---|
| Models | 60+ models, 14 tenants, 3 regions |
| Promotions | ~15/week, currently ad hoc and Slack-approved |
| Rollback today | median 38 minutes, dominated by finding an approver |
| Requirement | tenant-scoped promotion and rollback; region-aware pointers |
| Compliance | every promotion audited with actor, evidence and gate results |

## 3. Target Architecture

```text
 training pipelines --> registry (immutable versions, lineage)
                              |
                     promotion service (CAS + gates)
                              |
        +---------------------+---------------------+
        |                     |                     |
   tenant-A pointer     tenant-B pointer      region EU pointer
        |                     |                     |
   serving fleet          serving fleet        serving fleet
        |                     |                     |
        +---------- audit log (immutable, exported) --------+

  Shadow: challenger scored in each tenant's traffic before promotion
  Guardrails: latency, error rate, business KPI -> auto rollback per tenant
  Retention: unreachable versions archived; rollback window 90 days
```

## 4. Component Responsibilities

### 4.1 Registry and lineage

- Immutable content-hashed versions with run, data version, commit and evaluation report
- Tenant and region scoped pointers (aliases) so consumers never hardcode versions
- Lineage completeness enforced at write time; incomplete entries cannot exist
- Artifact store with regional replication and a local cache of the live champion

### 4.2 Promotion service

- Compare-and-set promotion with an expected current version
- Declarative gate: metrics within tolerance, matured shadow delta, sign-offs, latency, artifact integrity
- Per-tenant and per-region promotion; a tenant can be rolled back without touching others
- Shadow evaluation required before first promotion to any tenant

### 4.3 Guardrails and automated rollback

- Per-tenant guardrails: error rate, p99 latency, business KPI regression
- Pre-authorised automatic rollback for technical guardrails, no human in the path
- Rollback uses the locally cached champion so it works during a store outage
- Every rollback carries a reason code and opens an incident automatically

### 4.4 Audit and lifecycle

- Immutable audit log of every transition: actor, expected, actual, gate results
- Audit export to the compliance warehouse on a schedule
- Retention sweep archiving unreachable versions after the 90-day rollback window
- Quarterly access review of who can promote to which tenant

## 5. Delivery Timeline

| When | Milestone |
|---|---|
| Week 1-2 | Deploy registry and lineage; import existing deployments as version 1 with reconstructed lineage |
| Week 3 | Promotion service with CAS and gates; shadow-only mode for all tenants |
| Week 4 | Guardrails and pre-authorised rollback; first timed drill on one tenant |
| Week 5-6 | Migrate promotions to the service tenant by tenant; retire Slack approvals |
| Week 8 | Audit export, access review process, retention sweep in production |

## 6. Runbook (copy-paste)

```bash
# What is serving each tenant right now
curl -s localhost:8080/registry/pointers | jq '.[] | {tenant,region,champion,shadow}'

# Gate evaluation for a candidate on a specific tenant
curl -s 'localhost:8080/registry/gate?model=fraud&version=42&tenant=acme' | jq '.passed,.reasons'

# Shadow delta for a candidate on matured labels
curl -s 'localhost:8080/registry/shadow?model=fraud&version=42&tenant=acme' | jq '{maturedFraction,delta}'

# Roll back one tenant (pre-authorised)
curl -XPOST localhost:8080/registry/rollback -d '{"tenant":"acme","reason":"guardrail:error_rate"}'

# Audit trail for a model version
curl -s 'localhost:8080/registry/audit?model=fraud&version=42' | jq '.[] | {actor,from,to,gates}'
```

## 7. Observability and SLOs

- Operations: rollback time (target: under 5 minutes from guardrail breach to safe).
- Correctness: zero unauthorised promotions; audit completeness 100%.
- Evidence: percentage of promotions backed by a matured shadow comparison.
- Availability: guardrail-driven automatic rollbacks and false-positive rollbacks.
- Governance: quarterly access review completed; retention sweep keeps registry size bounded.

## 8. Failure Modes and the Rollback Plan

| Failure | Detection | Response |
|---|---|---|
| A tenant's serving degraded after a promotion | Guardrail breach | Automatic rollback within minutes; incident opened with the shadow comparison and gate results attached |
| Promotion request stalled waiting for an approver | Human in the rollback path | Pre-authorise technical rollback; escalate promotion approvals to a rota with a time-boxed default |
| Two teams promoted the same model to one tenant | Concurrent promotions | CAS rejects the loser; the client re-reads and must explicitly retry against the new pointer |
| Artifact store unreachable during an incident | Registry dependency down | Roll back using the locally cached champion artifact; promotion is blocked, serving is not |
| Lineage missing for an imported deployment | Legacy deployments imported without a run record | Mark lineage incomplete; block promotion until reconstructed; document the gap |

## 9. Prevention Backlog

- Statistical promotion criteria replacing fixed epsilons, with sequential testing.
- Automated shadow-label maturation tracking per tenant.
- Region-aware rollback policy: sequential vs simultaneous, with a documented choice.
- Self-service promotion for low-risk models with stricter automated gates.
- Audit export reconciliation against the compliance warehouse each month.

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

> The deliverable is 60 models across 14 tenants where every promotion is gated on evidence, every rollback is under five minutes without asking anyone, and every transition is auditable.
