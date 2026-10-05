# REAL-WORLD PROJECT — Concurrency: Checkout Hangs Every Friday

## Incident Scenario
Every Friday peak, checkout latency spikes to 30s then threads freeze entirely. Restarts "fix" it until next peak. No error, just silence.

## Symptoms
- `jstack` shows 200 threads `BLOCKED` on `OrderLock` then `InventoryLock`, others reverse order → classic lock-ordering deadlock.
- Pool queue grows unbounded (`LinkedBlockingQueue`) → heap climbs to 8GB before deadlock even hits; no rejection, just OOM pressure.
- `HashMap` (not concurrent) session cache corrupts under race → infinite loop in `get()` on corrupted bin (CPU 100% on 4 threads).
- `InterruptedException` swallowed in retry loop → shutdown hangs; `kill -9` required.

## Investigation Tasks
1. Threads: `jcmd <pid> Thread.print` (or `jstack`) 3x 10s apart — identical BLOCKED stacks confirm deadlock; map lock cycle.
2. Heap/JFR: `jcmd <pid> GC.heap_dump`; JFR `jdk.JavaMonitorEnter` (contention) + `jdk.ThreadPark` — longest waiters pinpoint locks.
3. Logs: `grep "RejectedExecution\|OutOfMemory\|Interrupted" app.log`; queue-depth metric graph vs latency.
4. Repro: 2-thread lock-order test + 50-thread HashMap hammer showing corruption/CPU spin.
5. Config: dump pool/queue settings; compute Little's-law mismatch (arrival >> service × threads).

## Root Cause
Inconsistent lock ordering across two code paths, unbounded queue hiding overload, non-concurrent map shared across threads, swallowed interrupts preventing drain.

## Resolution
- Immediate: single global lock order (id-ordered), replace with `ConcurrentHashMap`, bound queue (1k) + `CallerRunsPolicy` + alert, restore interrupt flag.
- Short-term: lock-ordering unit test (multithreaded stress), timeout `tryLock(2s)` on cross-service path, shutdown drill in CI.
- Long-term: lock splitting/striping, async inventory via queue, load-shed + autoscale policy, contention dashboards.

## Runbook
```
1. jstack ×3 + JFR 60s + heap dump before restart.
2. Restart; cap traffic (shed 20%); apply lock-order hotfix.
3. Bound queue + CHM patch to canary; soak 30 min.
4. Verify deadlock detector silent + queue depth flat.
5. Post-mortem: ordering rule + stress gate in CI.
```

## Metrics
- Deadlock occurrences = 0 over 2 peaks; queue depth p99 < 500; p95 checkout < 800ms at peak; clean shutdown < 15s.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.util.concurrent API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html
- Concurrency tutorial (locks/executors): https://docs.oracle.com/javase/tutorial/essential/concurrency/
