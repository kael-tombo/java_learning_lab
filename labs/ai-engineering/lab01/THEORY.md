# Lab 01: LLM Serving Infrastructure — Theory

## 1. What Serving Actually Is

A language model is a pure function. **Serving** is everything around it that turns
that function into a service: scheduling concurrent requests, managing memory,
batching, streaming, handling failures, and reporting what happened.

```
model (pure function)  +  scheduler + cache + gateway + telemetry  =  a service
```

Most of the value in serving engineering is not in the function. It is in the
scheduler and the cache.

## 2. The Two Regimes

Serving has two operationally distinct modes, and optimizing one at the expense of the
other is the classic mistake:

```
PREFILL (prompt processing)              DECODE (token generation)
  all prompt tokens in parallel            one token at a time
  compute bound                           memory-bandwidth bound
  FLOPs ~ 2 * params * tokens             FLOPs ~ 2 * params * batch
  memory ~ read weights once              memory ~ read weights every step
  latency grows ~linearly with prompt     latency flat, dominated by cache reads
  a long prompt is expensive but batched   each step is sequential
```

The consequence: **a long prompt and a long output are different problems.**
Throughput is set by the decode regime, so batching, precision, and cache design are
where throughput comes from. Latency for interactive traffic is set by prefill.

## 3. Static vs Dynamic Batching

**Static batching**: collect `B` requests, run them together, wait for all to finish.

```
[B][B][B][B][B]        -> one batch step serves all
   B=1: throughput terrible (memory bound)
   B=64: throughput good
   but: a short request waits for the longest request in its batch
   and: a finished slot idles until the batch drains
```

**Dynamic (continuous) batching**: slots are filled and released independently.

```
time ->
  [r1][r2][r3][r4][r5][r6][r7][r8]
   in   in  |  out | in   in   in  |out|
   slots fill as requests arrive and free as requests finish
   average batch size < configured max almost always
```

Why it wins: in decode, adding a sequence to a running batch costs almost nothing in
latency (the weights are already being read) but multiplies throughput. Dynamic
batching exploits that continuously instead of in bursts.

## 4. Admission Control and Prefill Chunking

Two techniques make continuous batching robust:

**Admission control**: before accepting, estimate the KV memory a request will need
over its whole lifetime and refuse if the pool would overflow.

```
kv_bytes = 2 * layers * kv_heads * head_dim * (prompt_len + max_new) * batch * bytes
accept while sum(requested) <= pool_capacity
```

**Chunked prefill**: break a long prompt into chunks and interleave with decode steps,
so one 32k prompt cannot stall the decode of everyone else.

```
step: [decode batch] [prefill chunk 1] [decode batch] [prefill chunk 2] ...
```

Prefill chunks are capped (e.g. 512 tokens) so the tail latency impact per step is
bounded.

## 5. Caching: Two Different Things

| | Prefix/KV cache | Response (semantic) cache |
|---|-----------------|---------------------------|
| What is stored | KV tensors for a token prefix | Completed answers keyed by similarity |
| Saves | Prefill computation | The entire generation |
| Key | Exact prefix token hashes | Embedding similarity threshold |
| Scope | Within and across requests (shared system prompts) | Across identical/near-identical questions |
| Risk | Version mismatch | Stale or cross-user answers |

They are complementary and both are high-value:

- **Prefix caching** is nearly free to add and helps whenever a system prompt or few-shot
  block is reused. Put stable content first.
- **Response caching** can remove an entire request from the bill on repetitive traffic
  (support, FAQ, repeated queries), but needs careful scoping (tenant, authz, TTL) or
  it becomes a correctness and security problem.

## 6. Streaming

Server-sent events or chunked transfer, one token at a time:

```
write "The" flush
write " order" flush
...
```

Why it matters: perceived latency (time-to-first-token) is what users feel, and
streaming makes TTFT the metric that matters instead of total latency. Streaming does
not change token cost or throughput — it changes the user experience and the metric you
should be optimizing.

Implementation concerns: flush per token (or batched per N ms), handle client
disconnect promptly (free the slot), and never buffer the whole response.

## 7. Load Balancing Across Replicas

| Policy | Behavior | Use when |
|--------|----------|----------|
| Round robin | Even distribution | Replicas identical, no state |
| Least connections | Fewest in-flight | Requests vary in length |
| Weighted | Fixed capacity weights | Replicas with different GPUs |
| Latency-aware | Route away from slow replicas | Heterogeneous fleet |
| Cost-aware | Route by price/latency tradeoff | Multiple model tiers |

For LLM serving, least-connections and latency-aware dominate, because request durations
vary by orders of magnitude (short answers vs long generations). A round-robin balancer
will pile long requests onto one replica and starve it.

## 8. Autoscaling

Signals, in order of usefulness:
1. **Queue depth** (waiting requests) — the earliest reliable indicator.
2. **In-flight requests** — fine-grained but noisier.
3. **GPU utilization** — coarse; LLM serving is not saturated linearly with load.
4. **TTFT** — a lagging symptom; good for alerting, bad for scaling (too late).

Autoscaling lag is the hard part: GPUs take minutes to start, so you must scale on
leading indicators (queue depth) with headroom, not on saturation.

## 9. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| OOM under load | Requests die at prefill | Batch admission too permissive | Admission control on projected KV |
| Throughput ceiling | Utilization < 100% | Static batching, batch too small | Continuous batching |
| TTFT spikes | p99 explodes | One long prompt blocking decode | Chunked prefill + separate lane |
| Tail starvation | Some requests very slow | Round-robin with mixed lengths | Least-connections, fair queueing |
| Cache thrash | Low prefix hit rate | Versioned prefixes vary per request | Stable prefix layout |
| Zombie slots | Capacity drops over time | Client disconnect not detected | Heartbeats, timeouts |
| Retry storm | Load multiplies | Naive retry on timeouts | Bounded retries with jitter |
| GPU idle | Utilization < 50% | Over-provisioned or cold replicas | Right-size, pre-warm |

## 10. Observability

Metrics that matter for an LLM serving system:

```
TTFT        time to first token (per percentile)
TPOT        time per output token (per percentile)
throughput  tokens/sec, requests/sec
batch size  distribution, not just average
cache       prefix hit rate, response hit rate
admission   accepted, rejected (429), queue depth
failures    OOM, timeout, cancellation, retry count
GPU         utilization, memory, power
```

Trace every request: which replica, which model version, batch size at each step,
prefill/decode token counts, cache hits, finish reason.

## 11. Cost Model

```
cost_per_request = (replica_gpu_cost * time_on_replica) / requests_served

requests_served_per_step = batch_size
tokens_per_second = batch_size * steps_per_second

cost_per_token = gpu_cost / tokens_per_second
```

The two levers that dominate: **batch size** (batching amortizes weight reads) and
**precision** (fewer bytes per weight). Quantization and batching together routinely
give 5-10x; either alone gives 2-4x.

## 12. Serving SLOs

Define them before you build:

```
TTFT p50 < 400 ms, p99 < 2 s      (interactive)
TPOT p50 < 40 ms                  (reading speed ~25 tok/s)
throughput > N tok/s              (per tenant or global)
error rate < 0.5%
admission rejection < 1% at steady state
```

SLOs determine the whole architecture: TPOT of 40 ms with 40-byte-per-token reads sets
the batch size you can afford; TTFT of 400 ms sets how much prefill you can admit.

## Key Equations

```
ttft = prefill_time + first_decode_step
tpot = decode_step_time = max(2*params*batch/FLOPS, (2*params + batch*cache_bytes)/BW)
throughput = batch_size / tpot
kv_bytes = 2 * layers * kv_heads * head_dim * seq_len * bytes_per_elem
cost_per_token = gpu_hourly_cost / tokens_per_second
```