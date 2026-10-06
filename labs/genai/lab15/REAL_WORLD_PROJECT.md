# Lab 15: Building a GenAI Platform — Real-World Project

## Project: Enterprise GenAI Platform

Design and build the platform that many product teams build on: capability services,
model routing and fleet management, prompt and tool registries, guardrails, evaluation
gating, tenancy and quotas, cost governance, incident response, and an adoption
program.

## Context

The platform exists so that 30 product teams do not each build their own unsafe,
expensive, unevaluated LLM integration. Success is measured by adoption and by
quality per dollar — not by the number of features the platform ships.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Holistic Evaluation of Language Models (HELM)" (Liang et al., submitted 16 Oct 2022;
  v7 Feb 2023) — https://arxiv.org/abs/2211.09110 — takeaway for this lab: reproducible,
  multi-scenario, multi-metric evaluation with published conditions is the defensible
  standard for platform-level quality claims, which is why the platform gate bundles
  generic, safety, and cost suites behind one reproducible report keyed to a release
  manifest.
- "The Llama 3 Herd of Models" (Dubey et al., submitted 25 Apr 2024; v2 23 Jul 2024) —
  https://arxiv.org/abs/2407.21783 — takeaway for this lab: a production release
  documents its evaluation methodology, safety evaluation, and deployment practice, and
  treats them as part of the deliverable — the structure this platform requires of
  every model it promotes.

## System Architecture

```
  PRODUCT TEAMS (30)
  +------------------------------------------------------------------+
  | SDK | REST | playground | templates | eval-as-a-service           |
  +-------------------------------+----------------------------------+
                                  |
  +-------------------------------v----------------------------------+
  |  API GATEWAY                                                     |
  |  auth | tenant context | quotas | rate limits | cost attribution|
  +-------------------------------+----------------------------------+
                                  |
  +-------------------------------v----------------------------------+
  |  PLATFORM SERVICES                                               |
  |  +-------------+ +------------+ +-----------+ +----------------+ |
  |  | Router      | | Guardrails | | Prompts   | | Tools          | |
  |  | capability  | | classify   | | registry  | | registry       | |
  |  | tier/region | | scrub      | | versions  | | schemas        | |
  |  | health      | | validate   | | owners    | | side effects   | |
  |  +------+------+ +------+-----+ +-----+-----+ +--------+-------+ |
  |         |               |             |                 |         |
  |  +------v---------------v-------------v-----------------v-----+   |
  |  | EVALUATION GATE (platform + product suites)               |   |
  |  | blocks on quality / safety / latency / cost regressions  |   |
  |  +----------------------------+------------------------------+   |
  |                               |                                  |
  +-------------------------------+----------------------------------+
                                  |
  +-------------------------------v----------------------------------+
  |  MODEL SERVICES                                                  |
  |  inference fleet | batching | quantization | embedding | rerank  |
  |  training | fine-tune | adapters | eval models                  |
  +-------------------------------+----------------------------------+
                                  |
  +-------------------------------v----------------------------------+
  |  DATA SERVICES                                                   |
  |  corpora | vector indexes | freshness | lineage | redaction      |
  +------------------------------------------------------------------+

  CROSS-CUTTING
    telemetry (traces, metrics, cost) | drift | incident response
    governance (model approval, residency, access) | change management
```

## Component Specs

### 1. Model Registry and Routing
- Logical names (`chat-fast`, `chat-quality`, `embed`, `rerank`, `judge`) mapped to
  concrete deployments with capability sets, SLOs, cost, health, and data classes.
- Routing by capability (superset check), quality tier, latency tier, region
  (residency), health, and cost ceiling.
- Model promotion policy: which models are approved, for which data classes, in which
  regions; promotion requires the platform eval gate plus an approval owner.
- Deprecation process: ladder off the old version, notices, auto-pin at deadline,
  compatibility shim.
- Region pinning enforced at the gateway; a request pinned to a region never leaves it.

### 2. Fleet and Resilience
- Capacity plan per logical name from measured service rate and peak RPS at
  `utilization <= 0.6`.
- Circuit breakers with `minCalls` guards; fallback chains that retry timeouts/5xx/429
  and never 4xx.
- Fallback capacity sized for total primary failure, or a documented degraded share with
  measured quality.
- Chaos testing quarterly: kill replicas, indexes, tool providers; measure failure
  isolation and graceful degradation.

### 3. Prompt Registry
- Immutable versions with typed variables, owner, risk tier, changelog, hash.
- Evaluation required before promotion; canary ladder with rollback.
- Render-time invariant assertions (no unfilled placeholders; typed variable checks).
- Deprecation and rollback with traffic shift, no rebuild.
- Prompt changes flow through the same gate as code.

### 4. Tool Registry
- Contract: schema, owner, auth model, side-effect class, timeouts, retry policy,
  approval policy, observability hooks.
- Registration validates the contract and runs provider contract tests; unowned tools
  and irreversible tools without approvals are rejected.
- Consumers get typed access with platform-managed credentials.
- Provider-side SLAs and ownership stated per tool.

### 5. Guardrails as a Service
- `classify` (harmful, PII, injection, off-policy, jailbreak), `scrub`, `validateOutput`.
- Per-tenant thresholds that may only tighten; disabling a platform category requires
  an approval workflow.
- Fail-closed on classifier errors.
- Refusal and over-refusal both measured; per-category thresholds.

### 6. Evaluation as a Service
- Platform suites: generic capability, safety, cost/latency, multilingual.
- Product suites registered per product, required for promotion to production.
- Reports keyed to the release manifest; regression diffs with per-category flags.
- Missing telemetry counts as a failure.
- Promotion ladder with automatic rollback; shadow evaluation for low-volume products.

### 7. Tenancy, Quotas, and Isolation
- Tenant context: identity, role, quotas, data scope, cost budget.
- Isolation: namespaced caches, index namespaces with pre-filtering, tenant-tagged
  traces with retention, per-tenant training datasets with isolation tests.
- Quotas: requests/day, tokens/min, concurrent, cost budget (checked on projected cost).
- Weighted fair queueing with a minimum share guarantee; no starvation.
- Randomized cross-tenant isolation tests in CI.

### 8. Cost Governance
- Attribution by tenant, team, feature, route, model version, cache status.
- Cost per successful outcome as the north-star metric.
- Monthly reconciliation against invoices; discrepancy above 2% alerts.
- Per-team budgets with 50/80/100% alerts and a trajectory forecast.
- Chargeback/showback dashboards teams trust (accuracy is the adoption lever).

### 9. Observability and Drift
- Full traces keyed by manifest hash; PII scrubbed payloads.
- Platform SLIs plus adoption: time-to-first-success, conversion at each funnel stage.
- Drift monitoring on product traffic mix, length, language, retrieval scores.
- Drift triggers investigation and eval-suite review; quality regression triggers rollback.
- Error budgets on availability, safety, and quality with burn-rate freeze.

### 10. Incident Response
- Platform-level incident process with product escalation paths and per-product
  communication templates.
- Containment menu: safe mode, tool disable, retrieval disable, model pin, load shed.
- Runbooks with owners, first questions, decision trees, tested containment.
- Quarterly game days; measure time-to-detect and time-to-contain.

### 11. Governance
- Model approval matrix by data class and region; access RBAC to models, indexes,
  tools, dashboards.
- Change management: who approves a production change, against which gate.
- Compliance: audit logging, retention enforcement, data processing agreements.
- Transparency: published model cards and system documentation per logical name.

### 12. Enablement and Adoption
- One-command quickstart; playground; three reference templates (RAG, agent,
  extraction); a documented path to production.
- Deprecation policy with migration guides and automated codemods where possible.
- Office hours and an escalation path; support burden explicitly tiered.
- Adoption funnel reported monthly; the biggest drop is the platform team's roadmap.
- Escape hatches documented and validated, so unusual needs do not fork the platform.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Platform availability | 99.95% |
| Router overhead | < 5 ms p50 |
| Guardrail overhead | < 30 ms p50 |
| Cost attribution accuracy | >= 95% |
| Cross-tenant leakage | 0 |
| Quota violation rate | < 0.1% |
| Bad releases reaching 100% | 0 |
| Rollback time | < 5 min |
| Median time-to-first-success (new team) | < 3 days |
| Eval gate false-negative rate | < 5% |
| Adoption (requested -> production at 90d) | >= 40% |
| Invoice reconciliation | < 2% discrepancy |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Teams bypass the platform | Adoption funnel drop | Fast path, playground, visible value |
| Over-gating pushes work around it | Escape-hatch usage | Low-risk fast path |
| A product disables guardrails | Registry diff audit | Monotone tighten + approval |
| Cross-tenant data leak | Randomized isolation tests | Namespaced keys, pre-filter |
| One product starves another | Per-tenant latency skew | Weighted fair queueing |
| Routing sends wrong capability | Routing assertion tests | Superset check |
| Circuit breaker thrashing | Breaker state metrics | `minCalls` guard, tuning |
| Cost attribution distrusted | Dispute count, reconciliation | Improve gateway attribution |
| Model upgrade degrades a product | Shadow eval before promotion | Golden suites per product |
| Index rebuild fails mid-way | Freshness metric + incident | Atomic index swap with fallback |
| Platform monolith outage | Blast radius per component | Loose coupling, per-component flags |
| Prompt sprawl | Registry coverage | Unversioned prompts blocked in CI |
| Tool without an owner | Registry validation | Reject at registration |
| Support overload | Support ticket volume per team | Tiered SLOs, docs, office hours |

## Milestones

- **M1** — model registry, logical names, routing, circuit breakers, fallback.
- **M2** — capacity plan validated against measurements.
- **M3** — prompt registry with gated promotion.
- **M4** — tool registry with contract tests.
- **M5** — guardrails as a monotone service.
- **M6** — evaluation service with platform and product suites.
- **M7** — tenancy, quotas, fair queueing, isolation tests.
- **M8** — cost governance with reconciliation.
- **M9** — observability, drift, error budgets.
- **M10** — incident runbooks and first game day.
- **M11** — SDK, quickstart, templates, playground.
- **M12** — first 5 onboarded teams; adoption funnel measured.
- **M13** — chaos test; failure isolation measured.
- **M14** — deprecation of the first model version with the full process.

## Deliverables

1. Control plane implementation (routing, registries, guardrails, tenancy, cost).
2. Evaluation service and gate pipeline.
3. Quota and attribution systems with reconciliation.
4. Runbooks plus drill and chaos reports.
5. SDK, quickstart, templates, playground.
6. `REPORT.md` — adoption funnel, cost per team, quality per logical name,
   incident history, and the roadmap derived from the biggest funnel drop.
7. `PLATFORM_CHARTER.md` — what the platform owns, what teams own, and the boundary.
8. `MODEL_CARDS.md` — per logical name: capabilities, SLOs, cost, evaluation summary.

## Definition of Done

- [ ] Zero cross-tenant leakage across 10,000 randomized isolation tests.
- [ ] Zero bad releases reaching 100% traffic during the observation period.
- [ ] Rollback under 5 minutes with no rebuild.
- [ ] Cost attribution >= 95% accurate and reconciled within 2%.
- [ ] Median time-to-first-success under 3 days for 5 new teams.
- [ ] Guardrail removal impossible without an approval record.
- [ ] Chaos test shows failure isolation with no platform-wide outage.
- [ ] A full model deprecation completed with a documented migration path.