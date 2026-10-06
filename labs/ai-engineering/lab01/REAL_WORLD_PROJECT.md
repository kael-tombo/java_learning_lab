# Lab 01: LLM Serving Infrastructure — Real-World Project

## Project: Multi-Tenant LLM Serving Platform

Design and build the production serving tier: continuous batching, admission control,
chunked prefill, paged KV cache with prefix sharing, multi-tier routing, streaming,
autoscaling, quotas and fair queueing, and the SLOs and telemetry that make it
operable.

## Context

This is the system between a customer's HTTP request and the model weights. Its job is
to convert a fleet of GPUs into a service with predictable latency, bounded memory, and
a cost per token that someone can plan against.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 20 Jun 2023; v3 12 Feb 2024) —
  https://arxiv.org/abs/2309.06180 — takeaway for this lab: block-paged KV cache with
  near-zero fragmentation and copy-on-write prefix sharing is what makes high
  concurrency feasible within GPU memory, which is the cache design and the prefix hit
  rate metric in this platform.
- "Orca: A Distributed Serving System for Transformer-Based Generative Models"
  (Yu et al., submitted 29 Jun 2022) — https://arxiv.org/abs/2206.02658 — takeaway for
  this lab: iteration-level scheduling that admits a new request whenever a sequence
  finishes is the mechanism behind continuous batching, which is the core scheduler
  behavior implemented here.

## System Architecture

```
   client (HTTP / SSE / gRPC)
        |
   +----v----------------------------------------------------------------+
   |  GATEWAY                                                             |
   |  auth | tenant | quota check | rate limit | cost attribution         |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  SCHEDULER                                                          |
   |  +----------------+  +----------------+  +--------------------+     |
   |  | admission      |  | continuous     |  | prefill/decode     |     |
   |  | control        |  | batch slots    |  | lanes              |     |
   |  | (projected KV) |  | (slot recycle) |  | (chunked prefill)  |     |
   |  +-------+--------+  +-------+--------+  +--------+-----------+     |
   |          |                  |                     |                 |
   |  +-------v------------------v---------------------v-----------+     |
   |  |  KV CACHE MANAGER                                          |     |
   |  |  block-paged | prefix sharing (COW) | eviction | preemption |     |
   |  +-------------------------------+---------------------------+     |
   +----------------------------------+-------------------------------+
                                       |
   +----------------------------------v-------------------------------+
   |  MODEL RUNTIME                                                     |
   |  replicas: weights (fp16/int8/int4) | kernels | attention backend  |
   |  speculative decoding | quantized KV cache                        |
   +----------------------------------+-------------------------------+
                                       |
   +----------------------------------v-------------------------------+
   |  AUTOSCALING + ROUTING                                            |
   |  scale on queue depth | least-connections | tier routing        |
   |  warm pool | weighted by model capacity                              |
   +------------------------------------------------------------------+

   TELEMETRY
     TTFT | TPOT | throughput | batch size dist | cache hit rate
     admission rejections | preemption | finish reasons | cost per 1M tokens
```

## Component Specs

### 1. Gateway
- Auth (OIDC, service accounts), tenant resolution from credentials (never from the
  payload), quota and rate-limit checks, cost attribution header.
- Request validation: max context, allowed models, schema of parameters.
- Idempotency keys for retryable requests.

### 2. Admission Control
- Estimate peak KV bytes: `2 * layers * kvHeads * headDim * (prompt + maxNew) * bytes`
  per element, GQA-aware.
- Accept while total projected usage <= pool * safety factor (0.85-0.9); else 429 with
  `Retry-After`.
- Per-tenant share of the pool; no tenant can consume more than its share.
- Admission metrics: accept rate, reject rate by reason, utilization distribution.

### 3. Continuous Batching Scheduler
- Slot pool; slots fill from the waiting queue and free immediately on finish,
  cancel, or error.
- Iteration-level scheduling: at each step, refill free slots before running the step.
- Prefill/decode lanes: interactive decode is never blocked by prefill.
- Chunked prefill: cap chunk size (e.g. 512 tokens) so one long prompt cannot dominate
  a step; long prompts are admitted with a lower priority.
- Preemption: when the pool is full, evict the lowest-progress sequence
  (`generated / (prompt + maxNew)`) and mark it for recompute-on-resume; fail fast for
  callers who opted out.

### 4. KV Cache Manager
- Block-paged allocation (block = 16 tokens) with per-request block tables.
- Copy-on-write prefix sharing: requests sharing a system prompt or few-shot prefix
  share blocks; on divergence, copy.
- Free list with fragmentation accounting; `cache_waste = 1 - used/reserved`.
- Prefetch policy: prefetch only for blocks likely to be used (system prompt, first
  chunk), not the entire expected output.
- Eviction: LRU over completed and preempted sequences; never evict in-flight.

### 5. Model Runtime
- Weights in fp16/int8/int4 with a per-model precision policy; KV cache in fp16 or int8.
- Attention backend with fused kernels; speculative decoding for high-batch decode.
- Warmup: load weights, compile graphs, run warmup requests before reporting ready.
- Batch-invariance: numerics must not depend on batch composition, so offline eval at
  batch 1 predicts production at batch 64.

### 6. Routing and Load Balancing
- Tier routing: cheap model for simple intents, frontier for hard ones (cascade
  signals from a difficulty classifier or an outcome-based verifier).
- Least-connections balancing; latency-aware routing to avoid degraded replicas.
- Capacity-aware routing: do not route to a replica whose queue is above a threshold.
- Sticky routing for multi-turn sessions so the KV prefix cache is reused.

### 7. Autoscaling
- Scale on queue depth (leading), with a startup-delay guard for GPU cold start.
- Scale-down only after sustained low queue depth (hysteresis) to avoid flapping.
- Warm pool: keep N replicas pre-warmed so a spike is served immediately.
- Target utilization 0.6; capacity planned from measured per-replica throughput.

### 8. Streaming and Cancellation
- SSE streaming with per-token flush; TTFT is the SLO metric.
- Client disconnect detected promptly; slot freed, compute stopped, partial output
  charged (or not, per policy).
- Timeouts: idle timeout and total timeout; both free slots.

### 9. Quotas and Fair Queueing
- Per-tenant: requests/day, tokens/min, concurrent requests, cost budget.
- Weighted fair queueing across tenants with a minimum share; interactive tier
  prioritized over batch.
- Denial-of-wallet: per-user caps and anomaly detection.

### 10. Observability
- Per request: TTFT, TPOT, total latency, prompt/completion tokens, batch size over
  time, cache blocks used, preempted flag, finish reason, cost, tenant, model version.
- Aggregates: throughput, batch size distribution (not just average), prefix hit rate,
  admission rejections by reason, preemption rate, GPU utilization and memory
  high-water, cost per 1M tokens by tier.
- Traces with span-level detail for prefill, decode, cache.
- Alerts: TTFT p95 breach, admission rejection spike, preemption spike, cache hit
  rate drop, utilization saturation, per-tenant anomaly.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| TTFT p50 (interactive) | < 400 ms |
| TTFT p99 | < 2.5 s |
| TPOT p50 | < 40 ms |
| Throughput per replica | measured and capacity-planned |
| Admission rejection (steady) | < 1% |
| Cache waste | < 5% |
| Prefix hit rate | > 60% on templated traffic |
| Preemption rate | < 1% |
| Utilization | 0.6 target, < 0.8 observed |
| Availability | 99.9% |
| Cross-tenant cache leak | 0 |
| Batch-invariance | numerics independent of batch composition |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| OOM under load | admission rejection spike, memory alert | Projected-KV admission, 429 |
| p99 TTFT spike | TTFT percentile alert | Chunked prefill, separate lane |
| Throughput ceiling | batch size distribution | Continuous batching, precision policy |
| Slot leak | in-flight vs completed mismatch | Disconnect handling, heartbeats |
| Cache thrash | prefix hit rate drop | Sticky routing, stable prefix layout |
| Fragmentation | cache waste metric | Block-paged allocation |
| Hot replica | per-replica queue depth | Capacity-aware routing |
| Autoscale flapping | replica count oscillation | Hysteresis, startup delay, warm pool |
| Retry storm | attempts/request | Bounded retries, jitter, breaker |
| Tail starvation | per-tenant latency skew | Fair queueing, min share |
| Cost spike | cost per 1M tokens | Batch size, precision, cache |
| Batch-size numerics drift | eval at served batch | Batch-invariant kernels |
| Long prompt DoS | prefill queue | Max context, chunking, priority |

## Milestones

- **M1** — gateway with auth, quota, cost attribution.
- **M2** — continuous batch scheduler with slot recycling; baseline metrics.
- **M3** — projected-KV admission control; 429 behavior.
- **M4** — chunked prefill and prefill/decode lanes; p95 TTFT improvement.
- **M5** — block-paged KV cache with prefix sharing; waste and hit rate metrics.
- **M6** — model runtime with precision policy and warmup.
- **M7** — routing: tiers, least-connections, sticky sessions, capacity-aware.
- **M8** — autoscaling on queue depth with warm pool.
- **M9** — streaming, cancellation, timeouts.
- **M10** — quotas and fair queueing.
- **M11** — full observability and alerts.
- **M12** — load test at 3x mean traffic; game day with a replica kill.

## Deliverables

1. Serving engine implementation (scheduler, admission, cache, runtime hooks).
2. Capacity model validated against measurements.
3. Runbook: TTFT regression, admission spike, preemption, cache collapse.
4. `REPORT.md` — throughput/latency/cost curves, capacity plan, and the decisions.
5. Load-test report at 3x mean traffic.

## Definition of Done

- [ ] All SLO targets met at 3x mean traffic with no OOM.
- [ ] Cache waste < 5%, prefix hit rate > 60% on templated traffic.
- [ ] Zero slot leaks after fault injection and mass client disconnects.
- [ ] Admission control rejects cleanly at overload; no crash under 2x capacity
      demand.
- [ ] Autoscale handles a spike with p99 TTFT inside target.
- [ ] Cross-tenant isolation verified by randomized tests.
- [ ] Capacity model within 20% of measured per-replica throughput.
- [ ] Runbook exercised in a game day with measured time-to-mitigate.