# Lab 12: Cost Optimization for LLMs — Mini Project

## Project: Cost Optimization Simulator with a Measured Quality Gate

Build every optimization from THEORY in one Java 21 simulator, run a controlled
workload through each configuration, and produce a cost/quality frontier where no
change ships without passing an explicit gate.

## Goal

A tool that takes a workload (request mix, prompt shapes, retrieval config) and a set
of optimization toggles, simulates each configuration end to end, and reports cost,
latency, and quality per request — with a gate that blocks regressions.

## Requirements

### Phase 1: Workload Model
- [ ] Generate 1,000 synthetic requests across 5 intents: FAQ, summarization,
      structured extraction, multi-step reasoning, open-ended writing.
- [ ] Per request: prompt length (from retrieved chunk counts), expected output
      length (from a lognormal distribution), difficulty label, tenant, feature.
- [ ] Support multiple traffic shapes: steady, spiky, batch-heavy.
- [ ] Deterministic from a seed.

### Phase 2: Stub Model and Cost Table
- [ ] `StubModel` with per-tier cost, latency, and a difficulty-dependent error
      rate; deterministic given a seed and a difficulty signal.
- [ ] `PriceTable` with per-model input/output/embedding/rerank prices.
- [ ] `CostMeter` producing per-request, per-feature, and per-tenant breakdowns.

### Phase 3: Baseline Report
- [ ] Cost per request by kind; sorted by share.
- [ ] Latency percentiles (TTFT, TPOT) from the scheduler simulation.
- [ ] Quality metric per intent.
- [ ] Save as the baseline for all diffs.

### Phase 4: Prefix Caching
- [ ] `PromptLayout.split` hoisting system/few-shot into a stable prefix.
- [ ] `PrefixCache` LRU with TTL and a max-prefix-token cap.
- [ ] Simulator for hit rate; report savings and the prefix-fraction ceiling.

### Phase 5: Semantic Response Cache
- [ ] Normalize-then-embed-then-threshold lookup with a `CacheKey` including
      model, prompt version, corpus version, tenant, authz scope, TTL.
- [ ] Deliberately test the failure mode: remove tenant scoping and demonstrate a
      cross-user leak that a test catches.
- [ ] Measure the quality delta on hits.

### Phase 6: Routing and Cascade
- [ ] `DifficultyClassifier` on prompt features; report accuracy.
- [ ] `CascadeRouter` with outcome-based escalation (schema invalid, low
      self-consistency, verifier disagreement).
- [ ] Sweep escalation thresholds; produce the cost/quality frontier.

### Phase 7: Context Compression
- [ ] `ExtractiveCompressor` filtering sentences within selected chunks.
- [ ] `HistoryCompactor` for multi-turn.
- [ ] Measure tokens saved and quality delta; verify chunk provenance for citations.

### Phase 8: Dynamic Batching and Speculative Decoding
- [ ] `DynamicBatcher` with slot pool and cache-memory cap; Poisson arrivals.
- [ ] Throughput model compared against the simulation.
- [ ] `SpeculativeDecoder` with a draft model; verify losslessness empirically by
      comparing sampled distributions.

### Phase 9: The Gate and the Frontier
- [ ] `QualityGate` with per-metric budgets; blocks regressions.
- [ ] Run every configuration; compute `quality_per_cent`.
- [ ] Mark dominated configurations.
- [ ] Emit a cumulative optimization table.

## Directory Layout

```
lab12/
  src/com/genai/lab12/{cost,prompt,cache,route,compress,batch,spec,output,eval}/
  workloads/*.jsonl
  out/reports/baseline.json
  out/reports/frontier.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — workload generator; 1,000 requests across 5 intents, deterministic.
2. **M2** — stub model + price table + cost meter; baseline report.
3. **M3** — prefix layout and cache; savings within the predicted ceiling.
4. **M4** — semantic cache; cross-tenant leak test fails when scoping is removed.
5. **M5** — difficulty classifier + cascade; escalation rate measured.
6. **M6** — context compression; tokens cut, provenance preserved.
7. **M7** — dynamic batcher; simulation within 20% of the throughput model.
8. **M8** — speculative decoder; distribution equivalence verified.
9. **M9** — gate blocks a deliberate regression.
10. **M10** — frontier produced with dominated configs marked.

## Acceptance Criteria

- [ ] Baseline cost breakdown sorted by share; documented insight about which line
      dominates.
- [ ] Prefix cache savings match the analytic prediction within 15%.
- [ ] Semantic cache never serves across tenants or authz scopes (test-enforced).
- [ ] Cascade escalation rate converges to the cheap model's measured error rate.
- [ ] Context compression reduces tokens >= 50% with quality delta inside budget.
- [ ] Dynamic batcher throughput within 20% of the analytic model.
- [ ] Speculative decoding output distribution matches the target.
- [ ] The gate blocks a configuration that exceeds a quality budget.
- [ ] Frontier marks dominated configurations correctly.

## Stretch Goals

- [ ] Cost-aware routing with per-request budgets and violation reporting.
- [ ] Learned token-dropping compressor trained on the workload.
- [ ] Tree-based multi-candidate speculative decoding.
- [ ] Cross-request KV prefix sharing with copy-on-write.
- [ ] Multi-provider price-aware routing with quality expectations per tier.
- [ ] Adaptive batching under traffic drift.
- [ ] Total cost of ownership model including retries, ingest, and continuous eval.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Prefix cache hit rate near zero | Volatile content early in the prompt |
| Semantic cache hit rate low | Not normalizing before embedding |
| Cross-user answer served | Missing tenant/authz in the cache key |
| Stale RAG answers | Corpus version not in the key |
| Cascade escalation rate 100% | Verifier too strict, or cheap model stub too weak |
| Cascade quality below baseline | Escalating on the wrong signal |
| Context compression kills recall | Dropping whole chunks instead of sentences |
| History compactor eats the system message | Compaction applied to index 0 |
| Batcher OOM | Only slot cap, no cache cap |
| Batch sim diverges from model | Cache bytes or KV reads omitted |
| Speculative output differs | Resampling from draft instead of target distribution |
| Gate always passes | Missing budget for the metric being changed |

## Definition of Done

`REPORT.md` contains: the workload description, the baseline cost breakdown with the
dominant line named, a table of every optimization with cost/latency/quality deltas,
the prefix-cache ceiling calculation, the cascade frontier with the chosen operating
point, the speculative speedup with a losslessness check, the final frontier with
dominated configs marked, a worked "what if traffic becomes 10x spiky" analysis, and
a list of optimizations you deliberately rejected with the reason.