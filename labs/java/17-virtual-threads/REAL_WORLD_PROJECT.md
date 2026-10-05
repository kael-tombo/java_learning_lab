# REAL-WORLD PROJECT — Virtual Threads: Migration Made Tail Latency Worse

## Incident Scenario
Team migrates to virtual threads expecting 10x throughput; instead p99 doubles and carriers sit at 100% while thousands of virtual threads are parked.

## Symptoms
- Hot `synchronized fetchAndCache()` pins every virtual thread to carriers → carrier starvation; platform pool would have queued, virtual exposes the lock.
- `ThreadLocal< byte[] >` 2MB buffer per request × 50k virtual threads → heap explodes (metaspace/heap, not thread count).
- Unbounded fan-out: one request spawns 500 virtual threads with no deadline → single slow upstream cascades.
- JFR shows `jdk.VirtualThreadPinned` events spiking; `Thread.print` shows carriers BLOCKED in `synchronized`, virtual threads PARKED behind them.

## Investigation Tasks
1. JFR: record `jdk.VirtualThreadStart/End/Pinned`, `jdk.ThreadPark`, `jdk.JavaMonitorEnter` — correlate pinning with p99.
2. Threads: `jcmd <pid> Thread.print` — carrier vs virtual state census; count pinned stacks in `synchronized`.
3. Heap: `jcmd <pid> GC.heap_dump`; histogram `byte[]` — ThreadLocal buffers top consumer.
4. Logs: `grep "timeout\|deadline exceeded" gateway.log`; fan-out size histogram per request.
5. Repro: microbench `synchronized` vs `ReentrantLock` under 10k virtual threads — p99 delta.

## Root Cause
Pinned carriers (synchronized hot path), ThreadLocal-per-virtual-thread memory blowup, unbounded unstructured fan-out without deadlines/cancellation.

## Resolution
- Immediate: `synchronized` → `ReentrantLock`, cap fan-out (max 8/request) + 2s `ShutdownOnFailure` deadline, replace ThreadLocal buffer with pooled/shared `ScopedValue` config only.
- Short-term: `jdk.VirtualThreadPinned` alert, fan-out budget test in CI, memory-per-request budget.
- Long-term: structured-scope-only policy for fan-out, carrier sizing guide, chaos test with slow upstream.

## Runbook
```
1. JFR 60s + heap dump; cap ingress 30%.
2. Swap lock + add deadline/cap to canary.
3. Remove ThreadLocal buffers; redeploy.
4. Verify pinned events ≈ 0, p99 back under SLA.
5. Land pinning + fan-out gates in CI.
```

## Metrics
- Pinned events < 10/min; p99 back to baseline (−50%); heap −60% at 20k concurrency; timeout-abandoned orphan threads = 0.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JEP 444 Virtual Threads: https://openjdk.org/jeps/444
- Thread API (virtual threads): https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html
