# Lab 02: GPT Architecture — Real-World Project

## Project: Production Inference Service for a Decoder-Only LLM

Design and implement the inference tier that sits between a client application and
a GPT-style model: batching, KV cache lifecycle, streaming, guardrails on sampling,
and the operational signals a real team needs.

## Context

A trained GPT model is not a deliverable — a *service* is. In production you must
reconcile three conflicting objectives:

1. **Latency**: users feel TTFT (time to first token) and inter-token latency.
2. **Throughput**: tokens/second across all concurrent users drives revenue.
3. **Memory**: KV cache, not weights, is what caps batch size.

Batching resolves the tension: adding a request to a running batch barely increases
per-token latency but amortizes the weight read that dominates decode cost. The
design below makes that trade explicit and measurable.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Language Models are Few-Shot Learners" (Brown et al., submitted 28 May 2020;
  rev. 22 Sep 2021) — https://arxiv.org/abs/2005.14165 — takeaway for this lab:
  decoder-only autoregressive conditioning (few-shot examples as context, no
  gradient updates) is exactly the inference contract the service implements.
- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: paged KV cache
  management (block-level allocation, near-zero waste, copy-on-write sharing)
  justifies the `KvManager` eviction and preemption design below.

## System Architecture

```
        client (SSE / gRPC)
              |
      +-------v--------+
      |  API Gateway    |  auth, quota, request validation
      +-------+--------+
              |
      +-------v--------+
      |  Scheduler     |  continuous batching, admission control,
      |                 |  preemption, KV block allocation
      +---+---------+---+
          |         |
   +------v--+   +--v-----------+
   | Prefill |   | Decode loop  |  KV cache (paged), logits processors,
   |  queue  |   | (batched)    |  stop criteria, streaming writer
   +---------+   +------+--------+
                       |
              +--------v---------+
              | Tokenizer       |  BPE encode/decode, cache token ids
              +-----------------+
              |
       +------v-------------------+
       | Model Runner (weights)   |  fp16 / int8, CPU fallback
       +--------------------------+
              |
      +-------v--------+
      |  Telemetry     |  TTFT, TPOT, tokens/s, cache hit rate,
      +----------------+  queue depth, preemption count
```

## Component Specs

### 1. Tokenizer Service
- BPE encode/decode with an LRU cache keyed by exact prompt string.
- Token count drives quota enforcement, so it must be exact and cheap.
- Reject requests whose prompt exceeds `maxContext - maxNewTokens`.

### 2. Scheduler (the heart)
- **Continuous batching**: a finished sequence is evicted immediately and its slot
  reused, rather than waiting for the whole batch to drain.
- **Admission control**: estimate per-request KV bytes from
  `2 * layers * kvHeads * headDim * (promptLen + maxNew) * bytesPerElem`; accept
  while total <= pool capacity.
- **Preemption**: when the pool is full, evict the request with the lowest
  `generated / generatedTotal` ratio and mark it for recompute-on-resume
  (or fail fast if the caller opted out).
- **Priority classes**: interactive traffic gets a weight; batch jobs drain at low
  priority during idle windows.

### 3. KV Cache Manager
- Paged blocks of 16 tokens; free list; per-request block table.
- Share prompt blocks across requests with an identical prefix (copy-on-write) —
  system prompts are a large fraction of real traffic.
- Expose `hitRate = sharedBlockReads / totalBlockReads` as a metric.

### 4. Decode Loop
- Forward pass for the batch's newest tokens only; read K/V from pages.
- Logits processors in a documented order: repetition penalty -> temperature ->
  top-k -> top-p -> random draw.
- Stop when: EOS generated, `maxTokens` reached, stop string matched, or the
  request is cancelled.
- Stream deltas to the client with a flush per token (or batched every N ms).

### 5. Guardrails at the Sampling Layer
- Cap `temperature <= 1.0` unless the request is explicitly non-deterministic.
- Require `seed` for non-deterministic modes; log it.
- `n > 1` requests share the prompt cache; document the cost multiplier.
- Never sample from a NaN/Inf logits vector — fall back to argmax and alert.

### 6. Telemetry
- Per request: TTFT, TPOT (inter-token), total latency, prompt/completion tokens,
  finish reason, model version.
- Aggregate: queue depth histogram, batch size distribution, cache hit rate,
  preemptions, tokens/sec by model.
- Trace id propagated from gateway through scheduler to the span writer.

## Non-Functional Targets

| Metric | Target | Why it matters |
|--------|--------|----------------|
| TTFT p50 | < 400 ms | Interactive feel |
| TTFT p99 | < 2.5 s | Tail latency drives support tickets |
| TPOT p50 | < 40 ms | Reading speed ~25 tokens/s |
| Throughput | 2,500 tok/s per replica | Cost per token target |
| Cache waste | < 5% | Direct capacity win |
| Availability | 99.9% | Single replica is a SPOF |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Cache pool exhausted | `queue_depth` saturation + high preemption | Smaller `maxTokens` default; backpressure 429 |
| One long prompt stalls batch | batch-size drop + TPOT spike | Move to prefill-only lane with chunked prefill |
| NaN logits | logit validity check | Fallback to argmax, page the on-call |
| Client disconnect mid-stream | write exception | Cancel, free pages immediately, count as `client_abort` |
| Model version mismatch in cache | key includes version | Namespace cache by model hash |
| Hot model after deploy | replica CPU saturation | Weighted routing, warm replicas before traffic shift |

## Milestones

- **M1** — single-threaded streaming endpoint with correctness tests.
- **M2** — static batching; benchmark tokens/sec vs batch size 1/4/16/64.
- **M3** — continuous batching with slot reuse; show the draining win.
- **M4** — paged KV cache with block tables and preemption.
- **M5** — admission control + 429 backpressure.
- **M6** — prefix sharing for repeated system prompts; report hit rate.
- **M7** — full telemetry + a benchmark report with the table above.

## Deliverables

1. `ServerMain.java` — the service.
2. `LoadHarness.java` — closed-loop load generator (target RPS, measure goodput).
3. `REPORT.md` — batch sweep, TTFT/TPOT percentiles, cache hit rate, preemption
   events, cost per 1M tokens.
4. `runbook.md` — what to check when TTFT degrades.

## Definition of Done

- [ ] Correctness: greedy output identical with and without the cache (1e-9).
- [ ] Load test at 200 RPS for 10 minutes without OOM or unbounded queueing.
- [ ] p50 TTFT under target at 3x mean load.
- [ ] Every metric in the telemetry table exists and is queryable.
- [ ] Runbook reviewed by someone who did not write the code.