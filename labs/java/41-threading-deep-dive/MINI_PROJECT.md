# MINI PROJECT — Threading Deep Dive: Bulkheaded Fetch Gateway

## Goal (2 weeks, ~8–10h)
Build a fetch gateway that fans out to 5 fake downstream services
with platform-pool (CPU), virtual-thread (I/O), bulkheads, timeouts,
and clean shutdown — surviving a chaos script without leaks.

## Requirements
### Functional
1. `Gateway.fetchAll(ids)`: I/O fan-out on
   `newVirtualThreadPerTaskExecutor()` with per-call 800ms timeout
   and global 2s deadline; partial results + error list returned.
2. CPU stage: bounded `ThreadPoolExecutor` (nCPU, bounded queue 100,
   `CallerRunsPolicy` or abort with mapped 429) for transform step.
3. Interruption-correct: `InterruptedException` restores flag or
   rethrows; no swallowed interrupts (test with forced cancel).
4. Thread hygiene: named factories (`gateway-io-%d`), no ThreadLocal
   leak (remove in finally), shutdown hook with `awaitTermination`.
5. Pinning demo: one endpoint pair — `synchronized` vs
   `ReentrantLock` — JFR run proving pinned events only on the former.
6. Chaos resilience: latency injector + failure injector; gateway
   degrades (stale cache fallback) instead of hanging.

### Non-functional
- 16+ tests: timeout, cancel, rejection, shutdown, naming, no-leak
  (thread count returns to baseline after 200 requests).
- JFR evidence: `jdk.VirtualThreadStart/End/Pinned` screenshot/note.
- Thread-dump artifact: `Thread.print` captured during chaos, annotated.
- README: pool-sizing math (Little's law) + queue/rejection rationale.

## Starter Layout
```
src/main/java/com/lab41/gateway/{Gateway,Downstream,FakeDownstream,
  TransformPool,Bulkhead}.java
src/test/java/.../{TimeoutTest,CancelTest,RejectionTest,LeakTest}.java
chaos/injector.sh (or java class)
```

## Phases
### Week 1 — Executors + Correctness (4–5h)
- Pools, futures, timeouts, interruption, naming, shutdown.
- Deliverable: all functional paths tested, dump readable.
### Week 2 — Virtual + Chaos (4–5h)
- Virtual-thread fan-out, pinning lab, chaos run, tuning report.
- Deliverable: gateway + JFR + dump annotations + sizing doc.

## Test Plan
- Soak: 200 sequential calls → thread count delta ≤ 2.
- Overload: 10x burst → bounded rejection, p99 documented, no OOM.
- Cancel: client disconnect → downstream tasks cancelled <100ms.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Fan-out design | Virtual I/O + CPU bulkhead | One pool correct | Unbounded/cached pool |
| Timeout/cancel | Both levels + flag discipline | Timeouts only | Swallowed interrupt |
| Rejection | Bounded + mapped 429/fallback | Bounded | Unbounded queue |
| JFR/dump | Pinned=0 proof + annotated dump | Dumps captured | No evidence |
| Tests + leak | 16+ tests, count flat | 10+ tests | Threads leak |

Pass ≥ 70. Stretch: `StructuredTaskScope` variant comparison; carrier
tuning (`jdk.virtualThreadScheduler.parallelism`) experiment.

## Demo Checklist
- [ ] Chaos run live: kill 2/5 downstreams, gateway still responds
- [ ] JFR pinned-event count shown (0 on fixed path)
- [ ] Thread dump: identify pool, carrier, BLOCKED entries in 2 min
- [ ] Shutdown: Ctrl-C drains <5s, no orphan non-daemon threads

## Common Traps
`Executors.newCachedThreadPool` in prod, `Future.get()` without
timeout, `catch (InterruptedException e) {}` — all auto-fail.
