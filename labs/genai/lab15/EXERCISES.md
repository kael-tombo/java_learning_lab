# Lab 15: Building a GenAI Platform — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Model Registry with Logical Names (E)

Register `chat-fast`, `chat-quality`, `embed`, `rerank` mapped to concrete model
versions. Resolve a logical name to a deployment; verify unknown names fail cleanly.

**Verify**: swapping the version behind `chat-fast` requires no caller change.

---

## Exercise 2: Capability Routing (M)

Implement routing by capability, quality tier, latency tier, region, and health.
Verify a text-only request never lands on a vision-only model.

---

## Exercise 3: Health-Aware Routing (M)

Add per-model health state (healthy/degraded/down) with a circuit breaker. Verify
traffic shifts away from a failing model within the breaker window.

---

## Exercise 4: Fallback Chain with Retry Policy (H)

Implement primary -> fallback with retries that skip 4xx validation errors. Verify
no retry storm on validation failures and a single retry on timeouts.

---

## Exercise 5: Fleet Sizing (M)

Compute replicas for a peak RPS target given service rate and utilization; include
fallback capacity. Verify against a simulated arrival process.

---

## Exercise 6: Prompt Registry (M)

Implement a registry with immutable versions, typed variables, owners, risk tiers,
and a changelog. Verify `assertNoUnfilled()` runs at render time.

---

## Exercise 7: Prompt Rollout (M)

Implement a prompt canary ladder with evaluation gates and rollback. Verify a
regressing prompt is stopped at the first step.

---

## Exercise 8: Guardrails as a Service (M)

Implement `classify`, `scrub`, `validateOutput` with per-tenant thresholds and a
platform default that products can tighten but not disable.

---

## Exercise 9: Tool Registry Contract (H)

Register tools with schemas, owner, auth model, side-effect class, and approval
policy. Verify a consumer cannot register a tool with no owner or an undeclared
side-effect class.

---

## Exercise 10: Evaluation as a Service (M)

Implement `run(manifest, suite)` and `regression(suite, baseline)` producing the Lab
09 report plus a per-category diff. Verify a deliberate regression is caught.

---

## Exercise 11: Multi-Tenancy: Namespaced Cache (M)

Namespace prefix cache, semantic cache, and adapter keys by tenant. Write the
cross-tenant leak test and verify it fails without scoping.

---

## Exercise 12: Quotas and Rate Limits (H)

Implement per-tenant requests/day, tokens/min, concurrent, and cost budgets with
weighted fair queueing across tenants.

**Verify**: one tenant cannot starve another.

---

## Exercise 13: Retrieval Isolation (M)

Index namespace per tenant with pre-filtering. Verify an unauthorized tenant's query
returns zero chunks from another tenant's corpus.

---

## Exercise 14: Cost Attribution End to End (M)

Attribute cost per tenant, team, feature, and route through the whole platform.
Reconcile against a synthetic invoice within 2%.

---

## Exercise 15: Platform SLI Dashboard (M)

Produce the SLI report: availability, latency, throughput, quality pass rate, cost,
freshness, rollback rate, and time-to-first-success.

---

## Exercise 16: Canary Across Platform Components (H)

Roll a change to the retrieval tier only, with gates; verify the canary controller
isolates the fault to that component.

---

## Exercise 17: Dependency Direction Check (M)

Static analysis over the module graph: assert no lower layer imports a higher one.
Verify with a deliberately violating import that the check fires.

---

## Exercise 18: Platform Quickstart SDK (E)

Build a 20-line SDK: `chat(prompt)`, `rag(question)`, `agent(goal)` with retries,
telemetry, and typed errors. Measure time-to-first-success for a new consumer.

---

## Exercise 19: Adapter Deprecation (M)

Model deprecation: route traffic off an old model version over a period with gates;
verify no quality regression and a clean end state.

---

## Exercise 20: Platform Incident (H)

Stage an incident (index rebuild fails mid-way) and run the platform incident process
with product escalation. Measure time-to-detect and time-to-contain.

## Exercise 21: Self-Service Onboarding (M)

Implement a quickstart that provisions a tenant, runs the eval gate, and returns a
working SDK snippet; measure the elapsed time.

---

## Exercise 22: Extension Points (M)

Document and implement the platform's extension mechanism (custom tools, custom
prompts, custom scorers) with validation, so unusual needs are supported without
forking the platform.

---

## Stretch A: Multi-Region Routing (H)

Route by data residency; verify a request pinned to region A never leaves region A.

---

## Stretch B: Shadow Fleet (H)

Run a shadow model at 100% traffic for evaluation without serving it; measure the
paired quality delta and the cost of shadow evaluation.

---

## Stretch C: Cost-Aware Auto-Scaling (M)

Scale replicas on a combined signal of utilization and cost budget burn; report the
trade against utilization-only scaling.

---

## Stretch D: Platform SLO Tiers (M)

Define per-route SLO tiers and verify the alerting differentiates them.

---

## Stretch E: Golden Path vs Escape Hatch (H)

Implement the fast path for low-risk products and the gated path for production; measure
the time each takes and the escape-hatch usage rate.

---

## Stretch F: Chaos Test (H)

Randomly kill model replicas, indexes, and tool providers; verify graceful
degradation and measure the failure isolation rate.

---

## Stretch G: Model Deprecation Communication (M)

Generate deprecation notices and migration guidance; measure adoption of the new
version by deadline.

---

## Stretch H: Platform Cost Simulation (H)

Simulate 10 product teams on the platform with different traffic profiles; produce a
cost breakdown per team and the platform's own overhead.

---

## Stretch I: Contract Tests for Tool Providers (M)

Implement contract tests that a tool provider must pass to be registered; verify a
non-conforming provider is rejected at registration time.