# MINI PROJECT — Advanced Concurrency: Resilient Quote Pipeline

## Goal (2 weeks, ~8–10h)
Build a quote pipeline (ingest → enrich → price → publish) in two
flavors — `CompletableFuture` + bulkhead and reactive `Flux` — both
surviving a 10x burst with backpressure, hedging, and clean cancel.

## Requirements
### Functional
1. CF flavor: staged `thenCompose` chain with per-stage timeout
   (300ms), `Bulkhead` (Semaphore 50) + bounded queue, hedged
   pricing (2 providers, first-wins), typed errors, global 2s deadline.
2. Reactive flavor: `Flux` ingest with `onBackpressureBuffer(1000,
   DROP_LATEST + metric)` or `limitRate`, `flatMap(maxConcurrency=16)`,
   `timeout` + `retryWhen(backoff)` + `circuitBreaker` (Resilience4j).
3. Publisher: backpressured sink (bounded) to fake exchange; slow
   consumer test proves drop/shed (not OOM) with counters.
4. Chaos: provider latency spike + poison message + consumer stall;
   pipeline degrades (drops + DLQ) and recovers without restart.
5. Cancel: downstream disconnect cancels upstream (CF `cancel(true)`
   + reactive `dispose`); thread-count + in-flight gauge return to 0.
6. Parity: same 1k-message golden file processed identically by both
   flavors (order-insensitive compare + idempotency keys).

### Non-functional
- 16+ tests: timeout, hedge-wins, backpressure-drop, breaker-open,
  poison-DLQ, cancel-drains, parity.
- JFR + metrics: in-flight, dropped, breaker-state, hedge-win-rate
  dashboards (text or Prometheus).
- Burst: 10x 60s — zero OOM, p99 documented, drops counted.
- README: flavor trade table (when to use which) + tuning knobs.

## Starter Layout
```
src/main/java/com/lab51/pipe/{cf/QuoteChain,flux/QuoteFlux,
  Bulkhead,HedgedPricing,DeadLetter}.java
src/test/java/.../{TimeoutTest,BackpressureTest,BreakerTest,ParityTest}.java
```

## Phases
### Week 1 — CF + Bulkhead (4–5h)
- Chain, hedge, bulkhead, DLQ, cancel; burst-tested.
- Deliverable: CF pipeline surviving burst with counters.
### Week 2 — Reactive + Parity (4–5h)
- Flux port, breaker/retry, parity + comparison.
- Deliverable: both flavors + trade table + dashboards.

## Test Plan
- Burst: 10x ingress 60s → drops >0, OOM 0, recovery <10s post-burst.
- Poison: 1% bad messages → 100% in DLQ, 0 pipeline deaths.
- Breaker: downstream 100% fail → opens <5s, half-opens cleanly.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| CF design | Timeouts+hedge+bulkhead | Works | get() soup |
| Reactive | Bounded + breaker/backoff | Runs | Unbounded flatMap |
| Backpressure | Proven shed, counted | Present | OOM on burst |
| Cancel/DLQ | Drains + DLQ tested | Partial | Leaks/dies |
| Parity/tests | 16+ + golden parity | 10+ | Thin |

Pass ≥ 70. Stretch: virtual-thread scheduler for CF flavor;
rebalancing keyed actor partition (`groupBy` + per-key mailbox).

## Demo Checklist
- [ ] 10x burst live: drops counted, no death, fast recovery
- [ ] Hedged race + breaker open/close on dashboard
- [ ] Disconnect → in-flight drains to 0
- [ ] Golden-file parity diff empty

## Common Traps
`join()`/`get()` in event loop, unbounded `flatMap`, retry without
backoff/breaker, ignoring reactive cancellation signals.
