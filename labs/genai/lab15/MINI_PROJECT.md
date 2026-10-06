# Lab 15: Building a GenAI Platform — Mini Project

## Project: Platform Control Plane in Java

Build the control plane of a multi-tenant GenAI platform: model registry with
logical names, capability-aware routing with circuit breakers and fallback, prompt
registry with gates, guardrail service, tenant quotas with fair queueing, evaluation
service, SLI reporting, and a quickstart SDK.

## Goal

A single JVM platform that 5 simulated product teams can use through one SDK, with
routing, safety, cost attribution, quotas, evaluation gates, and a measurable
adoption funnel.

## Requirements

### Phase 1: Model Registry and Routing
- [ ] Register `chat-fast`, `chat-quality`, `embed`, `rerank` with capabilities, SLOs,
      cost, health.
- [ ] Routing by capability (superset check), tier, region, health, cost ceiling.
- [ ] Verify a text-only request never lands on a vision-only deployment.
- [ ] `promote` re-points a logical name with no caller change.

### Phase 2: Resilience
- [ ] Circuit breaker with `minCalls` guard, half-open trials, and re-close.
- [ ] Fallback chain: retry timeouts/5xx/429, never 4xx.
- [ ] Verify no retry storm on validation errors.
- [ ] Scaled incident: kill 30% of primary capacity; measure the success rate.

### Phase 3: Capacity
- [ ] `CapacityPlanner` with Erlang-C for wait probability.
- [ ] Size primary and fallback; verify the plan against a simulated arrival process.
- [ ] Report p50/p95 TTFT at the planned capacity.

### Phase 4: Prompt Registry
- [ ] Immutable versions, typed variables, owner, risk tier, changelog, hash.
- [ ] `assertNoUnfilled` at render time.
- [ ] Canary ladder with an eval gate; a regressing prompt stops at the first step.

### Phase 5: Guardrails
- [ ] `classify`, `scrub`, `validateOutput` with per-tenant overrides.
- [ ] Monotone `tighten`: adding categories and lowering thresholds allowed;
      removing requires approval.
- [ ] Over-refusal measured alongside refusal.

### Phase 6: Tool Registry
- [ ] Schemas, owner, auth model, side-effect class, approval policy, timeouts.
- [ ] Registration rejects unowned tools and irreversible tools without approval.
- [ ] Contract tests run at registration.

### Phase 7: Evaluation Service
- [ ] `run(manifest, suite)`, `regression(suite, baseline)`, `compare(a, b)`.
- [ ] Per-category diff with regression flags.
- [ ] Report carries the manifest hash.

### Phase 8: Tenancy
- [ ] Tenant context with auth, quotas, data scope.
- [ ] Namespaced caches with the cross-tenant leak test.
- [ ] Retrieval index namespace with pre-filtering.
- [ ] Weighted fair queueing with a minimum share guarantee.

### Phase 9: Cost and SLI
- [ ] Cost attributed per tenant, team, feature, route, model version, cache status.
- [ ] Reconcile against a synthetic invoice within 2%.
- [ ] SLI report including the adoption funnel and `biggestDrop`.

### Phase 10: SDK and Onboarding
- [ ] `chat`, `rag`, `agent` in a small SDK with telemetry and typed errors.
- [ ] Quickstart that provisions a tenant, runs the gate, returns a snippet.
- [ ] Measure time-to-first-success for 5 simulated teams.

## Directory Layout

```
lab15/
  src/com/genai/lab15/{registry,route,fleet,guardrail,eval,tenancy,sli,integration}/
  suites/*.jsonl
  out/sli.json
  out/adoption.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — registry + routing; capability superset verified.
2. **M2** — breaker + fallback; no retry storm on 4xx.
3. **M3** — capacity plan; Erlang-C wait probability computed.
4. **M4** — prompt registry; unfilled-placeholder guard works.
5. **M5** — prompt canary; regression stopped at 1%.
6. **M6** — guardrails; monotone tighten enforced.
7. **M7** — tool registry rejects invalid registrations.
8. **M8** — eval service produces per-category regression flags.
9. **M9** — tenancy; cross-tenant leak test fails without scoping.
10. **M10** — quotas + fair queueing; no starvation.
11. **M11** — cost reconciliation within 2%; SLI report produced.
12. **M12** — 5 teams onboarded; funnel and time-to-first-success measured.

## Acceptance Criteria

- [ ] Logical-name swap requires zero caller changes.
- [ ] Capability routing is a superset check (verified with a violation).
- [ ] Breaker does not trip spuriously on a quiet healthy model.
- [ ] 4xx errors do not consume the fallback chain's retry budget.
- [ ] 30% capacity loss still serves >= 95% of requests.
- [ ] Prompt with an unfilled placeholder fails to render.
- [ ] Guardrail removal without approval is rejected.
- [ ] Cross-tenant cache leak test fails when scoping is removed.
- [ ] One tenant cannot starve another under saturation.
- [ ] Cost reconciles within 2%; SLI report includes the adoption funnel.

## Stretch Goals

- [ ] Multi-region routing with residency enforcement.
- [ ] Shadow fleet at 100% traffic; paired quality delta measured.
- [ ] Chaos test: kill replicas, indexes, and tool providers.
- [ ] Golden path vs gated path; measure both durations and escape-hatch usage.
- [ ] Tool provider contract tests rejecting non-conforming providers.
- [ ] Platform cost simulation across 10 teams.
- [ ] Layer dependency check firing on a deliberate violation.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Vision model serves text-only requests | `contains` instead of `containsAll` |
| Breaker trips constantly | Missing `minCalls` guard |
| Retry storm on 400s | Retrying non-retryable statuses |
| Cross-tenant cache leak | Tenant missing from the key |
| Unauthorized chunks retrieved | Post-filter instead of pre-filter |
| Tenant starvation | No minimum-share guarantee |
| Prompt ships with `{{var}}` | `assertNoUnfilled` not called |
| Guardrail disabled by product | Non-monotone tighten |
| Unowned tool registered | Owner not validated at registration |
| Cost never optimized | Attribution missing or distrusted |

## Definition of Done

`REPORT.md` contains: the layer diagram, the registry and routing design, the
resilience results (breaker and fallback), the capacity plan with Erlang-C, the
prompt lifecycle, the guardrail policy model, tenancy isolation results, the eval gate
output, cost attribution with reconciliation, the SLI report with the adoption funnel
and biggest drop, the SDK quickstart timing for 5 teams, and a "what we would not
build yet" section.