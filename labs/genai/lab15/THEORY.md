# Lab 15: Building a GenAI Platform — Theory

## 1. What a Platform Is

A GenAI platform is the layer that turns "an LLM exists" into "many teams can ship AI
features safely, cheaply, and repeatably". It is not a model server. It is:

```
capabilities (models, retrieval, tools, safety, eval)
          + interfaces (SDK, API, UI primitives)
          + operations (gating, monitoring, cost)
          + governance (security, compliance, access)
          + enablement (docs, support, examples)
```

The failure mode of platform building is building capabilities without governance, or
governance without usability. Both end with teams bypassing the platform.

## 2. Layered Architecture

```
  +---------------------------------------------------------------+
  | L6  CONSUMPTION      SDKs, REST/gRPC, chat UI, playground      |
  +---------------------------------------------------------------+
  | L5  PRODUCT SERVICES  RAG-as-a-service, agents-as-a-service,    |
  |                       prompt registry, eval-as-a-service        |
  +---------------------------------------------------------------+
  | L4  PLATFORM SERVICES model routing, batching, caching,       |
  |                       safety guardrails, tool registry, secrets |
  +---------------------------------------------------------------+
  | L3  MODEL SERVICES    inference runtime, training, quantize,   |
  |                       embedding, rerank, fine-tune             |
  +---------------------------------------------------------------+
  | L2  DATA SERVICES     corpora, vector index, feature store,    |
  |                       lineage, freshness                        |
  +---------------------------------------------------------------+
  | L1  INFRASTRUCTURE    GPUs, networking, storage, observability|
  +---------------------------------------------------------------+
```

Rule: dependencies point downward only. L3 must never call L5. A model service that
knows about product endpoints will acquire product-specific bugs in every product.

## 3. Model Routing and Registry

### Registry
```
model_id (logical name: "chat-fast", "chat-quality", "embed", "rerank")
  -> provider, model, precision, version
  -> capabilities (tools, vision, json mode, max context)
  -> SLOs (TTFT, TPOT, throughput, cost per 1k tokens)
  -> health status, current deployment
```

Logical names rather than raw model ids are the platform's most valuable abstraction:
a product requests `chat-quality`, and swapping the underlying model is a platform
change with no product code change.

### Routing dimensions
| Dimension | Example | Why |
|-----------|---------|-----|
| Capability | vision vs text-only | Functional requirement |
| Quality tier | cheap vs frontier | Cost/quality policy |
| Latency tier | interactive vs batch | SLO separation |
| Region | data residency | Compliance |
| Availability | healthy replicas only | Resilience |
| Cost ceiling | per-request budget | Finops |

## 4. Multi-Model Fleet Management

```
model A  primary      capacity: N_A   quality tier 2
model B  fallback     capacity: N_B   quality tier 1  (degraded mode)
model C  canary       5% traffic

routing policy:
  try A; on timeout/error/rate-limit -> retry B once
  never retry on 4xx validation errors (pointless)
  circuit-break A after k failures in a window
```

Sizing is the hard part: you need enough capacity for peak at the target utilization
(<= 0.6, per Lab 11), plus fallback capacity for total failure of the primary, plus
headroom for a canary.

## 5. Guardrails as a Service

Guardrails should be a platform capability, not a per-product reimplementation:

```
GuardrailService.classify(request, context) -> Verdict
  categories: harmful, PII, injection, off-policy, jailbreak
  context: tenant policy, user role, product risk tier

GuardrailService.scrub(text) -> Scrubbed
GuardrailService.validateOutput(text, schema) -> Result
```

Per-product configuration (thresholds, enabled categories) with platform defaults.
Products should be able to tighten, never to disable without an approval.

## 6. Prompt Registry and Lifecycle

Prompts are code:

```
prompt_registry
  prompt_id: "support.reply.v3"
  template (with typed variables)
  metadata: owner, intent, risk tier, created, changelog
  versions: immutable, hash-addressed
  evals: pass/fail per version against the registered suite
  rollout: 0% / 5% / 25% / 100% with rollback
```

Features that make this stick:
- Typed variables with schema (prevents the unfilled-placeholder bug from Lab 03).
- Every prompt has an **owner** and a **risk tier**.
- Every prompt version is evaluated before it can be promoted.
- Prompt changes flow through the same gate as code changes.

## 7. Tool Registry as a Platform

A shared tool catalog prevents every team from writing their own half-safe HTTP caller:

```
tool_registry
  tool_id, version
  owner (the team that maintains it)
  input/output JSON schema
  auth model (which credential the platform supplies)
  rate limits, timeout, retry policy
  side-effect class: read | reversible_write | irreversible_write
  approval policy
  observability hooks
```

Consumers get typed access with auth and observability for free. Providers get a
contract that says who is responsible for uptime.

## 8. Evaluation as a Service

```
EvalService.run(manifest, suiteId) -> EvalReport
EvalService.regression(suiteId, baselineVersion) -> Diff
EvalService.compare(variantA, variantB) -> PairedResult
```

Platform-provided suites: the generic capability suite (Lab 09), the safety suite
(Lab 10), the cost/latency suite, the multilingual suite. Product-provided: intent
suites registered with the platform.

The platform gate is: run the standard suites, plus the product's registered suite,
with the release manifest attached to the report.

## 9. Multi-Tenancy and Quotas

```
tenant
  auth (OIDC, service accounts, workload identity)
  quota: requests/day, tokens/min, concurrent, cost budget
  data scope: which corpora, which tools, which models
  rate limits per route
  billing attribution
```

Isolation strategy per component:
- **Routing/quota**: logical, per-request attribution.
- **KV cache and adapters**: namespaced by tenant; cache keys include tenant.
- **Retrieval**: index namespaces per tenant with pre-filtering (Lab 04).
- **Logs/traces**: tenant-tagged, retention per policy, PII scrubbed.
- **Training**: per-tenant datasets with isolation tests (Lab 06).

## 10. Platform SLIs

```
AVAILABILITY      per route and per model tier
LATENCY           TTFT/TPOT percentiles per tier
THROUGHPUT        tokens/s per fleet; utilization
QUALITY           pass rate on platform suites, per version
COST              $/request, $/tenant, $/feature, budget burn
FRESHNESS         index freshness, prompt rollout progress
CHANGE FAILURE    rollback rate, canary breach rate
EFFECTIVENESS     teams onboarded, time-to-first-success
```

The last one matters and is usually missing: a platform nobody uses is not a
platform. Track median time from "team requests access" to "team's first successful
production request".

## 11. Onboarding and Enablement

Platform adoption is a product problem:

```
1. Day 0:  one-command quickstart (SDK install + a working call)
2. Day 1:  a playground to see the model and compare tiers
3. Week 1: a template repo (RAG, agent, structured extraction)
4. Week 2: a documented path to production (gate + canary + monitoring)
5. Always: office hours, an escalation path, examples that are kept current
```

Anti-patterns that kill adoption:
- Requiring platform onboarding to be faster than building something bespoke.
- No playground, so teams cannot evaluate for themselves.
- Breaking changes without migration guides.
- Support burden that falls entirely on the platform team.

## 12. Governance

```
MODEL GOVERNANCE     which models are approved, in which regions, for which data classes
DATA GOVERNANCE      where data may be stored, retention, residency
ACCESS               role-based access to models, indexes, tools, dashboards
CHANGE MANAGEMENT    who approves a production change, and against what gate
INCIDENT             platform-level incident process with product escalation
COST ATTRIBUTION     chargeback/showback per team, with a dashboard they trust
COMPLIANCE           audit logging, data processing agreements, retention enforcement
```

## 13. Anti-Patterns

| Anti-pattern | Consequence | Instead |
|--------------|-------------|---------|
| Platform exposes raw model endpoints only | Every team reimplements safety, caching, cost | Offer capability services |
| One giant prompt per use case | Unreviewable, unversioned | Prompt registry with owners |
| No evaluation gate | Quality regressions ship | Platform gate blocks |
| Shared cache without tenant scoping | Cross-tenant leakage | Namespaced keys + tests |
| Platform team owns all reliability | Bottleneck, burnout | Explicit tiered SLOs per route |
| No cost attribution | Nobody optimizes | Per-team metering from day one |
| Breaking changes silently | Teams bypass the platform | Deprecation policy + migration guides |
| Over-gating | Teams route around the platform | Fast path for low-risk, gates for production |
| Golden path only | Teams with unusual needs are stuck | Documented extension points |
| Platform as a monolith | One team's outage takes out everyone | Loose coupling, independent deploys |

## 14. Build Order

```
  phase 0   ONE model, ONE route, telemetry from day one
  phase 1   Logical model names + routing (the highest-value abstraction)
  phase 2   Prompt registry with owners and versions
  phase 3   Guardrails as a service
  phase 4   Evaluation as a service + the gate
  phase 5   Cost attribution and quotas
  phase 6   Tool registry
  phase 7   Multi-model fleet, canary, self-service
  phase 8   Platform SDK and templates (adoption)
  phase 9   Governance and compliance

  Resist building a vector database in phase 0. Resist building a portal.
  Build capability + gate first; the portal is a presentation detail.
```

## Key Equations

```
capacity_replicas = ceil(peak_rps / (service_rate_per_replica * target_utilization))
fallback_required = full capacity (total primary failure must still serve)
effective_platform_success_rate = teams_first_success_within_week / teams_requesting
```