# REAL-WORLD PROJECT — Threading: Pool Exhaustion on Black Friday

## Incident Scenario
Checkout gateway uses one shared `newCachedThreadPool` plus a
`synchronized` inventory cache on the virtual-thread path. At peak,
threads explode to 12k, carriers pin, and checkout p99 jumps 0.3s →
8s. Autoscaler adds pods, which makes the downstream stampede worse.

## Symptoms
- Thread count 200 → 12,400 in 20 min; `VM.native_memory` + container
  OOMKills; GC healthy (not a heap issue).
- JFR `jdk.VirtualThreadPinned` 18k events/min on
  `InventoryCache.get` (synchronized); carriers BLOCKED.
- `Thread.print` shows 11k threads `WAITING on downstream socketRead`
  with no timeout; queue depth invisible (SynchronousQueue handoff).
- Downstream latency 50ms → 2s (retry amplification from new pods).
- Restart "fixes" for 15 min, then recurs — classic leak/exhaustion.

## Investigation Tasks
1. Live threads: `jcmd <pid> Thread.print > threads.txt` — histogram
   by name/state; identify cached-pool growth + socketRead waiters.
2. JFR: `jcmd <pid> JFR.start name=thr settings=profile duration=180s
   filename=thr.jfr`; inspect `jdk.VirtualThreadPinned`,
   `jdk.SocketRead`, `jdk.JavaMonitorEnter` top stacks in JMC.
3. Native memory: `jcmd <pid> VM.native_memory baseline` then
   `summary.diff`; confirm thread-stack BK (+12k × 1MB) vs heap flat.
4. Config forensics: dump executor construction via heap (`jcmd
   <pid> GC.heap_dump`) + code grep `newCachedThreadPool\|
   Executors\.newFixed.*Integer.MAX`; check for missing timeout on
   `Future.get` and HTTP client connect/read timeouts.
5. Repro: k6 burst against staging with old pool; watch thread count
   (`jcmd Thread.print | grep -c`) and pinned rate side by side.

## Root Cause
Unbounded pool + no I/O timeout + synchronized-on-virtual-thread
pinning + retry without bulkhead. Capacity scales by spawning threads
instead of shedding load, and pinning collapses carrier parallelism.

## Resolution
- Immediate: cap traffic 20%, raise downstream timeout to fail fast
  (800ms), restart one AZ at a time; synchronized cache →
  `ReentrantLock` + Caffeine with 500ms TTL.
- Short-term: split pools — virtual-thread I/O executor with deadline,
  nCPU CPU pool with bounded queue (100) + 429/fallback; add
  per-call + global timeouts; retry with jitter + circuit breaker.
- Long-term: bulkhead dashboard (threads, queue, rejection, pinned
  rate); load-shed policy; chaos test for pool exhaustion in CI.

## Runbook
```
1. Capture Thread.print + JFR 180s + NMT baseline (do NOT restart all at once).
2. Shed load: rate-limit 20%, fail-fast timeouts to canary with lock fix.
3. Swap pools (bounded + virtual I/O) one AZ at a time; watch threads/pinned/p99.
4. Drain + rolling restart; verify thread count flat 30 min at peak.
5. Replay failed checkouts idempotently; reconcile inventory holds.
6. Land alerts: threads >2k, queue >50, pinned >10/min, p99 >1s.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| Threads (peak) | 12,400 | <600 | Alert >2k |
| Pinned/min | 18k | <10 | Alert >50 |
| p99 checkout | 8.0s | 0.35s | SLO 1s |
| Rejections | OOM (crash) | clean 429 + fallback 1.2% | Dashboard |
| Pod restarts | 14/h | 0 | Alert >1/h |

## Prevention Checklist
- [ ] No unbounded executors (ArchUnit/Checkstyle ban)
- [ ] Every blocking call has timeout + deadline
- [ ] No `synchronized` on virtual-thread path (JFR pinned gate)
- [ ] Pool/queue/rejection dashboard + chaos burst test

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Java concurrency / virtual threads docs: https://docs.oracle.com/en/java/javase/21/
- OpenJDK Loom project: https://openjdk.org/projects/loom/
