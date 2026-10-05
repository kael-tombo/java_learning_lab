# REAL-WORLD PROJECT — GC: Promotion Failure Freezes Checkout

## Incident Scenario
After a catalog import, checkout p99 spikes 200ms → 4s in waves every
~7 min. CPU fine, downstream fine, heap "only 70% used". GC logs show
`Evacuation Failure` / `to-space exhausted` followed by full GCs —
promotion failure from humongous image buffers + survivor overflow.

## Symptoms
- Sawtooth p99: 4s spikes aligned with `Xlog:gc*` full-GC lines;
  `heap after GC` barely drops (floating garbage + humongous).
- G1 humongous allocation rate 400MB/s during import (20MB product
  images as single `byte[]` per request, retained in session cache).
- JFR `jdk.GarbageCollection` longest events 3.8s (G1 Full);
  `jdk.GCHeapSummary` shows old-gen 95% + humongous region spike.
- `jcmd GC.heap_dump` top dominators: `byte[]` via image cache +
  boxed `Long` stream churn in pricing.
- Young GC every 300ms (allocation rate 2.1GB/s) — GC spends 35% CPU.

## Investigation Tasks
1. GC log: collect `-Xlog:gc*:file=gc.log:time,level,tags`; `grep -n
   "Evacuation Failure\|to-space exhausted\|Full GC\|Humongous"
   gc.log`; align timestamps with p99 spikes.
2. JFR: `jcmd <pid> JFR.start name=gc settings=profile duration=300s
   filename=gc.jfr`; rank `jdk.GarbageCollection` by longest duration
   + `jdk.ObjectAllocationInNewTLAB` by stack in JMC.
3. Heap: `jcmd <pid> GC.heap_dump import.hprof`; histogram
   `byte[]` count/size; path-to-root of image cache (session → map).
4. Live sizing: `jcmd <pid> GC.heap_info` + `VM.native_memory
   summary`; compute allocation rate from log (MB/s) and promotion
   rate; confirm survivor too small (`-XX:SurvivorRatio` review).
5. Repro: staging import of 500 images; watch `Xlog` humongous lines
   + JFR pause histogram reproduce the 7-min wave.

## Root Cause
Humongous short-lived buffers + unbounded session cache + boxed-stream
churn. G1 cannot evacuate humongous regions; survivors overflow; full
GCs serialize the world every few minutes.

## Resolution
- Immediate: cap import concurrency 50%, stream images (chunked 64KB,
  no whole-`byte[]`), TTL + size-bound session cache (Caffeine 500
  entries / 10 min); raise `-Xmx` one step to relieve old-gen.
- Short-term: switch image path to off-heap/direct or file-backed;
  replace boxed streams with primitives; set G1
  `MaxGCPauseMillis=150` + proper region size; add allocation budget.
- Long-term: GC SLO (p99 pause <200ms) + allocation-rate alert
  (>1GB/s); import backpressure; quarterly bake-off (G1 vs ZGC).

## Runbook
```
1. Freeze import job; capture gc.log slice + JFR 300s + heap dump.
2. Deploy cache-bound + streaming-image hotfix to canary (10% import).
3. Verify: humongous MB/s 400 -> <20; full GCs 8/h -> 0; p99 4s -> 200ms.
4. Roll 100%; drain old sessions; replay failed checkouts.
5. Re-tune G1 flags; set pause + alloc-rate alerts.
6. Postmortem: allocation budget per endpoint.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| p99 checkout | 4.0s (waves) | 0.2s | Alert >0.5s |
| Full GC/h | ~8 (3.8s each) | 0 | Alert any full |
| Humongous rate | 400MB/s | <20MB/s | Alert >100MB/s |
| Alloc rate | 2.1GB/s | 0.6GB/s | Alert >1GB/s |
| Old-gen after GC | 95% | 55% | Alert >80% |

## Prevention Checklist
- [ ] Allocation-rate + humongous dashboards
- [ ] Bounded caches with TTL everywhere
- [ ] No whole-file `byte[]` on request path
- [ ] GC pause SLO + full-GC paging alert

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- GC tuning guide (G1/ZGC/flags): https://docs.oracle.com/en/java/javase/21/gctuning/
- JFR / JDK Mission Control docs: https://docs.oracle.com/javacomponents/jmc-5-4/jfr-runtime-guide/about.htm
