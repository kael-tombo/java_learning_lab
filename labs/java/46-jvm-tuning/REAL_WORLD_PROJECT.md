# REAL-WORLD PROJECT — JVM Tuning: OOMKilled Despite "Free Heap"

## Incident Scenario
Payments pods OOMKill 6×/day after moving to smaller k8s limits
(2GB). Heap shows 60% used; GC logs clean; on-call keeps raising
`Xmx` — which makes kills more frequent. The killer is native memory:
thread stacks + direct buffers + metaspace outside the heap.

## Symptoms
- `kubectl describe pod` → `OOMKilled (exit 137)`, but last
  `GC.heap_info` shows heap 1.1GB/1.8GB — heap is innocent.
- NMT (when finally enabled) shows thread stacks 900MB (9k threads ×
  1MB... actually 1.8k threads) + direct 400MB + metaspace 300MB >
  cgroup headroom.
- CPU throttling 35% (2CPU quota, 24 GC/compiler threads + fat pools).
- p99 fine between kills; kills cluster at import burst (direct
  `ByteBuffer.allocateDirect` per image, never pooled).
- Raising Xmx 1.8G → 2.2G (over limit) accelerates kills — less room
  for native.

## Investigation Tasks
1. Confirm killer: `kubectl get events | grep OOMKilled`; `cat
   /sys/fs/cgroup/memory.max` vs flags (`jcmd <pid> VM.flags |
   grep -i "MaxRAM\|Xmx\|ContainerSupport"`).
2. NMT: `jcmd <pid> VM.native_memory baseline` → burst → `summary.diff`;
   rank Thread/Metaspace/Direct/Internal; `jcmd <pid> VM.native_memory
   detail.diff` excerpt saved.
3. Threads: `jcmd <pid> Thread.print | grep -c "^\""` count × stack
   (`-Xss1m`) = stack budget; list top pool names.
4. JFR: `jcmd <pid> JFR.start name=tune settings=profile duration=180s
   filename=tune.jfr`; check `jdk.ThreadStart`, `jdk.DirectBufferStatistics`,
   `jdk.MetaspaceSummary`, `jdk.GarbageCollection` (prove GC healthy).
5. Heap alibi: `jcmd <pid> GC.heap_info` + gc.log tail — heap after GC
   flat while RSS climbs (`ps -o rss`); direct unpooled confirmed via
   allocation stacks.

## Root Cause
Heap-centric tuning in a container: Xmx sized to the limit leaves no
native headroom; unbounded threads + unpooled direct + default GC
thread counts overflow the cgroup. Classic "heap is not RSS".

## Resolution
- Immediate: lower `MaxRAMPercentage` 75→55 (Xmx ~1.1GB of 2GB),
  cap pools (nCPU), pool direct buffers (or stream to file), restart
  with NMT + gc.log + JFR always on.
- Short-term: set `ActiveProcessorCount`, cap
  `ConcGCThreads/ParallelGCThreads`, `ReservedCodeCacheSize` budget,
  direct-memory limit (`MaxDirectMemorySize`) + metric; HPA on RSS.
- Long-term: sizing worksheet per service (heap+NMT+direct+stack <
  80% limit); OOMKill alert + auto-heap-dump; quarterly right-size.

## Runbook
```
1. Capture VM.flags + heap_info + NMT diff + JFR 180s BEFORE resize.
2. Deploy tuned flags (lower RAM% + pool caps + direct limit) to 1 AZ.
3. Verify: RSS headroom >20%, throttle <5%, 0 OOMKill 24h, p99 flat.
4. Roll fleet; watch kills + RSS + throttle dashboards.
5. Re-run import burst; confirm direct pooled (JFR DirectBuffer flat).
6. Land NMT + RSS + throttle alerts.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| OOMKill/day | 6 | 0 (30d) | Page on any |
| RSS vs limit | 102% (kill) | 72% p99 | Alert >85% |
| Threads | ~1,800 | ~220 | Alert >400 |
| CPU throttle | 35% | <4% | Alert >10% |
| p99 | spiky (restarts) | 180ms stable | SLO 500ms |

## Prevention Checklist
- [ ] NMT + RSS + throttle dashboards on every JVM
- [ ] No hardcoded Xmx above `MaxRAMPercentage` policy
- [ ] Pool + GC-thread caps proportional to CPU quota
- [ ] Direct-memory budget + pooling rule

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JVM tuning + container support: https://docs.oracle.com/en/java/javase/21/gctuning/
- OpenJDK HotSpot docs: https://openjdk.org/groups/hotspot/
