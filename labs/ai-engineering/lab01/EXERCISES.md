# Lab 01: LLM Serving Infrastructure — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Batch Decode Timing Model (E)

Implement a function that, given params, batch size, cache bytes per sequence, FLOPS,
and bandwidth, returns compute time, memory time, and the bottleneck.

**Verify**: for 7B params, batch 1, 1 GB cache, 300 TFLOPs, 3 TB/s, memory is the
bottleneck; at batch 64 compute starts to matter.

---

## Exercise 2: Static Batching Simulator (M)

Simulate static batching with Poisson arrivals, a fixed batch size, and variable
request lengths. Report throughput, mean latency, and p95 latency.

**Verify**: a short request arriving just before a long one waits for it; average batch
occupancy < configured size.

---

## Exercise 3: Continuous Batching Simulator (M)

Simulate dynamic batching: slots fill on arrival and free on completion. Report
throughput, mean TTFT, p95 TTFT, and average batch size.

**Verify**: at the same load, throughput is higher and p95 latency lower than static.

---

## Exercise 4: Admission Control (E)

Implement admission control using the KV memory formula. Refuse (429) when the projected
pool usage exceeds capacity.

**Verify**: 100 concurrent 2k-context requests are refused on a pool sized for 40.

---

## Exercise 5: Chunked Prefill (M)

Split a long prompt into fixed-size chunks and interleave them with decode steps.
Measure the p95 TTFT impact on concurrent short requests.

**Verify**: chunked prefill reduces p95 TTFT for short requests at the same throughput.

---

## Exercise 6: Prefix Cache (M)

Implement a prefix cache keyed by the hash of each token prefix. Simulate a workload
with a shared system prompt and report hit rate by prefix length.

**Verify**: hit rate > 90% for the system prompt, 0% for unique queries.

---

## Exercise 7: Semantic Response Cache (M)

Implement embed-then-threshold lookup with TTL and tenant scoping. Simulate a support
workload with 30% near-duplicate questions.

**Verify**: hit rate ~30%; cross-tenant lookup returns nothing.

---

## Exercise 8: Streaming Versus Buffered (M)

Implement both response modes over the same workload and report TTFT and total latency.

**Verify**: streaming reduces TTFT by the full generation time; total latency is
unchanged.

---

## Exercise 9: Load Balancing Policies (M)

Implement round-robin, least-connections, and latency-aware balancing over replicas with
heterogeneous speeds. Measure tail latency.

**Verify**: least-connections beats round-robin on tail latency for mixed-length
requests.

---

## Exercise 10: Queue Depth Autoscaling (H)

Implement autoscaling on queue depth with a startup delay. Simulate a traffic spike and
measure how much headroom was needed to avoid saturation.

**Verify**: scaling on queue depth avoids the latency cliff; scaling on saturation does
not.

---

## Exercise 11: Failure Injection (H)

Kill replicas mid-run and verify: in-flight requests fail over, new ones route around,
and no slot leaks.

**Verify**: zero leaked slots after 50 kills.

---

## Exercise 12: Retry Policy with Jitter (H)

Implement bounded retries with exponential backoff and jitter. Verify a 20% timeout rate
does not produce a retry storm.

**Verify**: attempts per request <= 1 + max_retries; amplification bounded.

---

## Exercise 13: Client Disconnect Handling (M)

Simulate client disconnects at random points. Verify slots are freed and memory is
reclaimed promptly.

**Verify**: no capacity leak after 500 disconnects.

---

## Exercise 14: Cost Model (E)

Compute cost per request and cost per token for batch sizes 1-128 and precisions
fp16/int8/int4. Report the cost-quality frontier with a reference accuracy proxy.

---

## Exercise 15: SLO Dashboard (M)

Produce a dashboard: TTFT and TPOT percentiles, throughput, batch size distribution,
cache hit rate, admission rejections, and failure counts.

---

## Stretch A: Multi-Tier Routing (H)

Route simple requests to a small fast model and complex ones to a large slow model.
Measure blended cost and quality.

**Verify**: cost per request drops with quality inside budget.

---

## Stretch B: Prefill/Decode Disaggregation (H)

Model separate prefill and decode pools with KV transfer cost. Compare against a single
mixed pool.

**Verify**: disaggregation wins when prefill bursts dominate.

---

## Stretch C: Paged KV Cache (H)

Implement block-paged KV allocation with copy-on-write prefix sharing. Measure waste
reduction and hit rate.

---

## Stretch D: Speculative Decoding in the Server (H)

Add a draft model and measure end-to-end throughput gain including draft overhead.

---

## Stretch E: Priority Scheduling (H)

Implement priority classes (interactive vs batch) and measure batch-job latency under
interactive load.

---

## Stretch F: Model Warmup and Cold Start (M)

Measure replica startup time (weight load, graph compile, warmup requests) and design a
pre-warm policy.

---

## Stretch G: Fair Queueing Across Tenants (H)

Implement weighted fair queueing and verify no tenant starves.

---

## Stretch H: Capacity Autotuning (H)

Automatically pick batch size and replica count from a measured throughput curve; verify
against a fixed configuration.