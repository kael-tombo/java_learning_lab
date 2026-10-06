# Lab 01: LLM Serving Infrastructure — Mini Project

## Project: LLM Serving Engine Simulator with Continuous Batching

Build a serving engine in Java 21 that schedules simulated requests with continuous
batching, admission control, chunked prefill, prefix and response caching, streaming,
load balancing, autoscaling, and metrics — then benchmark it against a static-batching
baseline.

## Goal

An engine whose measured throughput, TTFT, and TPOT match the analytic model within a
stated tolerance, beating static batching on every metric, with no capacity leaks
under fault injection.

## Requirements

### Phase 1: Timing Model
- [ ] `TimingModel` with compute and memory terms; `crossoverBatch`.
- [ ] Validate against a manual hand calculation for one configuration.
- [ ] Sweep batch 1-256 and mark where the bottleneck flips.

### Phase 2: Request Model
- [ ] Synthetic request generator: Poisson arrivals, lognormal prompt lengths,
      lognormal output lengths, tenant labels, priority classes.
- [ ] Deterministic from a seed; three traffic profiles (steady, spiky, batch-heavy).

### Phase 3: Static Batching Baseline
- [ ] Slot-based static batching with a fixed batch size.
- [ ] Measure throughput, mean and p95 latency, average batch occupancy.

### Phase 4: Continuous Batching Engine
- [ ] `BatchScheduler` with slot fill/release per step.
- [ ] `RequestSlot` state machine with TTFT/finish tracking.
- [ ] Measure the same metrics; produce the comparison table.

### Phase 5: Admission Control
- [ ] Projected-KV admission with a safety factor; 429 on rejection.
- [ ] Test: 100 concurrent 2k-context requests against a pool sized for 40.

### Phase 6: Chunked Prefill
- [ ] Interleave prefill chunks with decode steps.
- [ ] Measure p95 TTFT for short requests with and without chunking.

### Phase 7: Caching
- [ ] `PrefixCache` keyed by prefix hash; hit rate measured.
- [ ] `ResponseCache` with normalization, threshold, TTL, tenant scoping.
- [ ] Cross-tenant leak test that fails without scoping.

### Phase 8: Streaming and Cancellation
- [ ] `StreamingWriter` flushing per token; TTFT vs buffered comparison.
- [ ] Client disconnects; verify slots freed and no memory leak.

### Phase 9: Load Balancing and Autoscaling
- [ ] Round-robin, least-connections, latency-aware policies over heterogeneous replicas.
- [ ] Queue-depth autoscaler with startup delay; verify headroom needed for a spike.

### Phase 10: Fault Injection and Retry
- [ ] Kill replicas mid-run; verify failover and no slot leaks.
- [ ] Bounded retries with jitter; verify no storm at 20% timeout rate.

### Phase 11: Reporting
- [ ] SLO dashboard: TTFT/TPOT percentiles, throughput, batch distribution,
      cache hit rates, rejections, finish-reason counters, utilization.
- [ ] Cost per 1M tokens per configuration.
- [ ] `REPORT.md` with the static-vs-continuous comparison and the analytic
      validation.

## Directory Layout

```
lab01/
  src/com/aiengineering/lab01/{engine,cache,bal,scal,stream,retry,metrics,model,sim}/
  profiles/*.json
  out/reports/dashboard.txt
  out/reports/comparison.csv
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — timing model; crossover batch identified.
2. **M2** — request generator with three profiles.
3. **M3** — static baseline measured.
4. **M4** — continuous engine; throughput and latency beat static.
5. **M5** — admission control; oversized load rejected cleanly.
6. **M6** — chunked prefill; p95 TTFT for short requests improved.
7. **M7** — caches; hit rates reported; leak test fails without scoping.
8. **M8** — streaming; TTFT improvement quantified; disconnects leak-free.
9. **M9** — balancing and autoscaling; tail latency and spike headroom measured.
10. **M10** — fault injection clean; no retry storm.
11. **M11** — analytic model validated within tolerance; report written.

## Acceptance Criteria

- [ ] Continuous batching beats static on throughput and p95 latency.
- [ ] Simulated throughput within 25% of the analytic model.
- [ ] Admission control rejects cleanly under oversized load (no crash).
- [ ] Chunked prefill reduces p95 TTFT for short requests by >= 30%.
- [ ] No capacity leak after 500 client disconnects and 50 replica kills.
- [ ] Cross-tenant cache leak test fails when scoping is removed.
- [ ] Retry amplification bounded at <= 1 + max_retries.
- [ ] Least-connections beats round-robin on tail latency for mixed lengths.
- [ ] Autoscaling on queue depth avoids the saturation cliff.

## Stretch Goals

- [ ] Prefill/decode disaggregation with KV transfer cost.
- [ ] Paged KV cache with copy-on-write prefix sharing.
- [ ] Speculative decoding inside the engine.
- [ ] Priority classes; measure batch-job latency under interactive load.
- [ ] INT8 KV cache and INT4 weights; cost/throughput frontier.
- [ ] Weighted fair queueing across tenants.
- [ ] Capacity autotuner picking batch size and replicas from a measured curve.
- [ ] Autoscaling comparison: queue-depth signal vs utilization signal.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Throughput far below model | Static batching or small batch size |
| OOM under long generations | Admission using current length |
| Slot leak over time | Disconnect not releasing slots |
| p99 TTFT huge, p50 fine | Un-chunked long prefills |
| Cache hit rate ~0 | Prefix varies per request |
| Retry amplification | No bound or no jitter |
| Tail latency uneven across replicas | Round-robin balancing |
| Autoscale flapping | No startup-delay guard |
| Simulation drifts from the model | Cache reads or FP overhead omitted |

## Definition of Done

`REPORT.md` contains: the architecture diagram, the timing model with crossover
analysis, the static-vs-continuous comparison table, the analytic-vs-simulated
validation, admission control results, chunked prefill results, cache hit rates with
the leak test, streaming TTFT comparison, load-balancing tail latency, autoscaling
spike results, fault-injection results, cost per 1M tokens per configuration, and a
"what we would tune first in production" section.