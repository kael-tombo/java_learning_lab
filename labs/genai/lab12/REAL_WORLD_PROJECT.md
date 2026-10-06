# Lab 12: Cost Optimization for LLMs — Real-World Project

## Project: FinOps Platform for an LLM Product

Design and build the cost and capacity system for a production LLM product: per-request
cost attribution, caching layers with correct invalidation, model routing and
cascades, context reduction, capacity planning against measured throughput, budget
enforcement, and an optimization program that ships only behind quality gates.

## Context

LLM unit economics are decided by engineering decisions, not by the vendor's price
list. A team that cannot attribute cost per feature cannot optimize it, and a team that
optimizes without gates loses quality silently. This platform is the answer to both.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: per-sequence KV cache
  capacity, prefix sharing, and continuous batching are the variables that actually
  set throughput per dollar, which is why this platform models them explicitly
  instead of treating cost as a black box.
- "Fast Inference from Transformers via Speculative Decoding" (Leviathan et al., submitted
  21 Nov 2022; v3 14 Feb 2023) — https://arxiv.org/abs/2211.17192 — takeaway for this
  lab: drafting with a small model and verifying in one target pass yields an exact
  distribution with 2-3x speedup, which is the lossless cost lever in the optimization
  sequence implemented here.

## System Architecture

```
   ALL REQUESTS
        |
   +----v---------------------------------------------------------------+
   | COST METER (every request, every stage)                            |
   |  in_tok | out_tok | embed_calls | rerank_calls | gpu_ms            |
   |  attributed by: tenant, feature, route, model, prompt_version      |
   +----+--------------------------------------------------------------+
        |
   +----v-----------+     +----------------+     +---------------------+
   | PROMPT LAYER   |     | CACHE LAYER    |     | ROUTING LAYER       |
   | stable prefix  |---->| prefix cache   |     | difficulty classifier|
   | layout audit   |     | semantic cache |     | cascade + escalation|
   +----------------+     | (scoped keys)  |     +----------+----------+
        |                  +----------------+                |
        |  hit rate                |                         | tier
        v                         v                         v
   +---------------------------------------------------------------------+
   |  RETRIEVAL & CONTEXT REDUCTION                                      |
   |  chunk selection | sentence-level compression | dedupe | rerank k  |
   +----------------------------------+----------------------------------+
                                      |
   +----------------------------------v----------------------------------+
   |  MODEL RUNTIME                                                       |
   |  continuous batching | precision | paged KV cache | speculative    |
   |  measured service rate mu  ->  capacity model                       |
   +----------------------------------+----------------------------------+
                                      |
   +----------------------------------v----------------------------------+
   |  QUALITY GATE (Lab 09 eval)  ->  block regressions                  |
   +---------------------------------------------------------------------+
        |
   +----v---------------------------------------------------------------+
   | BUDGET ENFORCEMENT & REPORTING                                      |
   |  per-tenant budget | forecast | anomaly alerts | frontier report   |
   +---------------------------------------------------------------------+
```

## Component Specs

### 1. Cost Meter
- Every stage reports units and GPU milliseconds; a single `RequestTrace` aggregates
  them.
- Attribution dimensions: tenant, feature, route/tier, model version, prompt version,
  cache-hit flag, agent-vs-direct.
- Reconcile against provider invoices monthly; a discrepancy above a threshold is an
  alert (it means the meter is wrong, and every optimization number is then suspect).
- Emit cost per request, per feature, per tenant, per route; publish a dashboard whose
  default sort is by share descending.

### 2. Prompt Layout Discipline
- Lint step in CI: fail the build if volatile content (timestamps, request ids,
  retrieved docs) appears in the cached prefix region.
- Report prefix fraction per prompt template. Templates with a low prefix fraction
  get a "low headroom" warning — prefix caching cannot help them, and the team should
  stop trying.
- Static content (policy, few-shot, rubrics) is versioned and change-controlled;
  a prefix change invalidates the cache, so schedule them.

### 3. Cache Layers
- **Prefix cache**: keyed by prefix hash, TTL, max-prefix cap, hit-rate metric,
  store-declined metric (caching beyond the provider cap creates a fictional hit rate).
- **Semantic response cache**: key = model, prompt version, corpus version, tenant,
  authz scope, TTL. Threshold tuned on the eval set. Explicit authorization review
  before enabling for any response that varies by user.
- **Embedding cache**: `(modelVersion, contentHash) -> vector`, disk-backed,
  invalidated on model change.
- **Rerank cache**: `(queryHash, chunkId) -> score`.
- Every cache reports hit rate, and hit rate is monitored for collapse (a silent
  cache bypass is invisible until the bill arrives).
- Poisoning defense: cap stored entries per tenant, TTL, and reject entries whose
  content fails output validation.

### 4. Routing and Cascades
- Difficulty classifier on prompt features plus retrieval signals; report accuracy
  and the confusion matrix by intent.
- Cascade with outcome-based escalation: schema validation, self-consistency,
  verifier disagreement. Track the realized escalation rate per intent.
- Per-intent budgets: if an intent's escalation rate exceeds a threshold, that is an
  alert (either the cheap model regressed or the classifier drifted).
- Model change behind the route is a canary, not a flag flip.

### 5. Retrieval and Context Reduction
- Sentence-level compression inside selected chunks; never drop whole chunks.
- Chunk provenance preserved so citations remain valid; citation validity rate is a
  gate metric.
- Rerank `k` per corpus, chosen from the recall/latency knee; measured, not guessed.
- Target: input tokens per request, per intent, tracked as a first-class SLO.

### 6. Runtime Cost Controls
- Batching, precision, KV cache precision, and speculative decoding configured per
  route (interactive vs batch) with measured service rates.
- Capacity model: `replicas = ceil(peak_rps / (mu * rho))` with `rho <= 0.6`,
  validated against measurements within 20%; a larger error is a planning alert.
- Prefill/decode lanes so long prompts do not wreck tail latency.

### 7. Quality Gate
Every optimization ships behind the Lab 09 gate:
- correctness per intent within budget,
- faithfulness and citation validity within budget,
- abstention behaviour within budget,
- safety regression: zero tolerance,
- latency p95 and cost per request reported for the same configuration.
A configuration that improves cost and exceeds a quality budget is blocked and
reported with the diff.

### 8. Budget Enforcement
- Per-tenant and per-feature monthly budgets with a soft alert at 50/80/100%.
- Per-request ceilings for self-serve usage; behavior when exceeded is explicit
  (degrade to a cheaper tier, queue, or refuse).
- Denial-of-wallet protection: per-user caps, anomalous volume alerts.
- Forecast end-of-month spend; alert on trajectory, not only on the fact.

### 9. Optimization Program
A quarterly review with the measured frontier:
```
configuration | cost/req | quality | latency p95 | dominated?
```
- Candidates come from the meter: the largest share lines first.
- Each candidate is a PR behind the gate, not a config change.
- Rejected candidates are recorded with the reason, so the same idea is not
  re-proposed every quarter.

### 10. Reporting
- Monthly unit-economics report: cost per request by intent, gross margin per
  feature, cost per successful outcome (not per request).
- Frontier chart with dominated configurations removed.
- List of optimizations shipped this quarter with their measured effect.
- List of optimizations rejected and why.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Meter vs invoice discrepancy | < 2% |
| Cost per request | Tracked per intent; reduced >= 40% over two quarters |
| Input tokens per request (RAG) | Reduced >= 50% |
| Prefix cache hit rate | > 70% on templated routes |
| Semantic cache hit rate | Reported; enabled only where justified |
| Quality regression per optimization | 0 outside budget |
| Safety regression | 0 tolerance |
| Latency p95 regression | <= 5% |
| Capacity model error | < 20% |
| Budget overrun | 0 (alerts at 80%) |
| Utilization | <= 0.6 |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Optimizing the wrong cost line | Meter share ordering | Require a meter-sourced proposal |
| Semantic cache cross-user leak | Authz test | Tenant + authz in the key; security review |
| Stale RAG answers | Citation freshness check | Corpus version in the key; short TTL |
| Prefix cache fictional hit rate | Store-declined metric | Respect the provider cap |
| Cache hit rate silently collapses | Hit-rate alert | Cache-miss counter in traces |
| Cache poisoning | Content validation on store | TTL, per-tenant cap, validation |
| Cascade escalation spike | Per-intent escalation alert | Investigate cheap-model regression |
| Context compression hurts recall | Recall@k and citation validity | Sentence-level only; gate |
| Over-compression | Answer quality | Budget floor on context tokens |
| Speculative acceptance collapses | Acceptance rate metric | Draft/target pairing review |
| Quality lost to cost pressure | Gate on every PR | Gate blocks; exception requires sign-off |
| Batch OOM | Memory high-water | Cache cap; admission control |
| Meter drifts from invoices | Monthly reconciliation | Alert on discrepancy |
| Budget overrun discovered late | Trajectory forecast | Alert at 80%, not 100% |
| One tenant exhausts capacity | Fair-queue metrics | Weighted fair queueing |

## Milestones

- **M1** — cost meter with attribution and invoice reconciliation.
- **M2** — prompt layout lint in CI; prefix fraction reported per template.
- **M3** — cache layers with scoped keys, invalidation, and hit-rate monitoring.
- **M4** — routing classifier and cascade with escalation metrics.
- **M5** — context reduction with citation validity preserved.
- **M6** — capacity model validated against measurements.
- **M7** — quality gate integration on every optimization PR.
- **M8** — budget enforcement, forecasts, denial-of-wallet protection.
- **M9** — monthly unit-economics report and frontier chart.
- **M10** — game day: 10x traffic spike with an artificial 2x cost regression.

## Deliverables

1. Cost metering and attribution service.
2. Cache layer with invalidation and monitoring.
3. Routing/cascade configuration with measured escalation rates.
4. Context reduction pipeline.
5. Capacity model with validation report.
6. `REPORT.md` — the measured frontier, shipped and rejected optimizations, and
   the remaining cost lines ranked.
7. `runbook.md` — cost anomaly triage (bill up 3x: where did it go?).

## Definition of Done

- [ ] Meter reconciles with invoices within 2%.
- [ ] No cache serves across tenants or authz scopes; verified by randomized tests.
- [ ] Every shipped optimization has a gate result and a measured effect.
- [ ] Quality outside budget never ships without explicit sign-off.
- [ ] Capacity model within 20% of measurement at the target config.
- [ ] Cost per request reduced by the stated target with quality held.
- [ ] Monthly unit-economics report produced and reviewed by finance.