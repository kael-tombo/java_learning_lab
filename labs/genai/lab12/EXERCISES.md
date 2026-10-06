# Lab 12: Cost Optimization for LLMs — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Cost Breakdown Instrument (E)

Build `CostMeter` that accumulates input tokens, output tokens, embedding calls,
rerank calls, and GPU milliseconds per request, per feature, and per tenant.

**Verify**: a request's computed total matches a hand-computed total.

---

## Exercise 2: Prompt Layout for Prefix Caching (E)

Implement `splitForCaching(List<Message>)` returning `staticPrefixMsgs` and
`volatileMsgs`, hoisting system/few-shot messages into the prefix.

**Verify**: adding a user query changes only the suffix; the prefix hash is stable
across 100 renders.

---

## Exercise 3: Prefix Cache Simulator (M)

Implement an LRU prefix cache keyed by the hash of each token prefix. Simulate 1,000
requests with varying prompt structures and report hit rate.

**Expected**: high hit rate with good layout; near-zero if a timestamp sits early in
the prefix.

---

## Exercise 4: Semantic Response Cache (H)

Implement normalize-then-embed-then-threshold lookup. Store `(embedding, response,
metadata)`; return a hit only if `cos >= tau`.

**Verify**: "What's my order status?" and "whats my order status " hit the same key.

---

## Exercise 5: Cache Invalidation Matrix (M)

Define invalidation rules: model version, prompt version, corpus version, policy
version, tenant, authz scope, TTL. Implement `isValid(entry, requestContext)`.

**Verify**: a corpus version bump invalidates every RAG answer; a model bump
invalidates everything.

---

## Exercise 6: Cache Poisoning Test (M)

Simulate a cross-tenant leak: user A's cached response returned to user B. Assert the
key includes tenant/authz scope and that the test fails when scoping is removed.

---

## Exercise 7: Difficulty Classifier Router (M)

Train a small classifier on features (prompt length, has code block, has math,
question-word count, retrieval score) to predict "easy/medium/hard". Report accuracy
and the resulting cost/blended quality with a frontier plot.

---

## Exercise 8: Cascade with Escalation (H)

Implement: run the small model; escalate when (confidence < tau) OR (output fails
schema validation) OR (a verifier disagrees). Measure the escalation rate and the
cost/quality frontier.

**Expected**: a large fraction resolved by the cheap model; the escalation rate is
the number that sets your cost.

---

## Exercise 9: Extractive Context Compression (M)

Given retrieved chunks, keep only sentences scoring above a threshold against the
query. Measure tokens saved and recall/answer quality delta.

**Verify**: schema instruction and final question are never removed.

---

## Exercise 10: Conversation History Compaction (M)

Implement a history compactor: keep the last `k` turns verbatim, summarize older turns
into a typed summary record, and never compact the system message.

**Verify**: answer quality on a multi-turn eval stays within a stated delta while
tokens drop.

---

## Exercise 11: Dynamic Batch Scheduler (M)

Implement a slot-based scheduler: fill slots on arrival, release on completion, cap by
both slot count and cache budget. Simulate Poisson arrivals and report throughput,
mean TTFT, and p95 TTFT.

**Expected**: TTFT much lower than static batching at the same throughput.

---

## Exercise 12: Output Length Control (M)

Sweep `max_tokens` across tiers; measure quality per output token and truncation rate.
Choose tiers from observed output-length percentiles.

**Expected**: a truncation rate that rises sharply once you go below p95.

---

## Exercise 13: Speculative Decoding Simulator (H)

Implement a draft model (biased token predictor) and a target with a known distribution.
Run the acceptance loop; measure tokens generated per target forward pass and the
acceptance rate.

**Verify**: the output distribution matches the target exactly (lossless).

---

## Exercise 14: Batch Speedup Model vs Measurement (M)

Compare the analytic throughput model against the simulated scheduler across batch
sizes 1-64. Report the error.

---

## Exercise 15: Embedding Cache and Dedupe (E)

Implement `contentHash` dedupe plus a disk-backed `(model, hash) -> vector` cache.
Measure calls saved on a re-ingest of an unchanged corpus.

**Expected**: second ingest makes zero embedding calls.

---

## Exercise 16: Rerank k Sweep (M)

Sweep rerank `k` in {10, 25, 50, 100, 200}: measure answer quality, latency, and cost.
Mark the knee.

**Expected**: quality plateaus early; latency keeps rising.

---

## Exercise 17: Rerank Result Cache (M)

Cache rerank scores per `(queryHash, chunkId)`. Measure hit rate on a repeated-query
workload.

---

## Exercise 18: Full Optimization Sequence Simulation (M)

Implement all of the above as toggles, then run a 1,000-request workload through
configurations: baseline, + prefix caching, + batching, + routing, + semantic cache,
+ context reduction, + speculative.

**Verify**: cumulative cost falls and quality stays within budget at every step.

---

## Exercise 19: Quality-per-Cent Frontier (M)

For each configuration compute `quality_metric / cost_per_request`. Plot and mark
which configurations are dominated.

---

## Stretch A: Cost-Aware Routing with Budgets (H)

Add per-request cost ceilings; the router must decide the tier before knowing the true
cost. Implement a budget-aware policy and measure budget violations.

---

## Stretch B: Learned Compression (H)

Train a token-dropping compressor on (long context, short answer) pairs. Measure
compression ratio and answer quality.

---

## Stretch C: Multi-Candidate Speculative Tree Decoding (H)

Extend speculative decoding to a tree of drafts with a custom acceptance mask.
Measure acceptance rate versus linear k drafts.

---

## Stretch D: Cross-Request Prefix Sharing in the Scheduler (H)

Share KV cache blocks across requests with an identical prefix (copy-on-write).
Measure memory saved and hit rate under a realistic system-prompt workload.

---

## Stretch E: Provider Price-Aware Routing (M)

Route across multiple price tiers with quality expectations per tier; measure blended
cost and quality, and the cost of the quality drop at the cheap tier.

---

## Stretch F: Adaptive Batching Under Drift (H)

Adapt batch size to observed arrival rate and cache pressure; report p95 latency
versus a fixed-batch baseline.