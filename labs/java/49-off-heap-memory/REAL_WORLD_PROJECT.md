# REAL-WORLD PROJECT — Off-Heap: Direct-Buffer Leak OOMKills Thumbnails

## Incident Scenario
Thumbnail service renders images with `ByteBuffer.allocateDirect`
per request plus an FFM scratch segment never closed on the error
path. RSS climbs 800MB → 3.4GB/day; heap healthy; pods OOMKill at
night when traffic is lowest (Cleaner never catches up).

## Symptoms
- RSS monotonic climb; heap after GC flat 45%; GC logs pristine —
  classic native leak shape.
- `BufferPoolMXBean` direct count 12 → 48,000; NMT Internal/direct
  +2.6GB; `jcmd VM.native_memory detail.diff` fingers direct.
- JFR `jdk.DirectBufferStatistics` maxDirect rises unbounded;
  `jdk.JavaExceptionThrow` on error path precedes each jump (arena
  skipped on exception).
- Slices/dupes of a parent buffer released while children still
  referenced → use-after-free `IllegalStateException` in 0.3% renders.
- Night OOMKills (low RPS → fewer GCs → Cleaner backlog never drains).

## Investigation Tasks
1. Native census: `jcmd <pid> VM.native_memory baseline` → load →
   `summary.diff` + `detail.diff`; record direct/thread/metaspace
   split; `BufferPoolMXBean` direct count/memory trend.
2. JFR: `jcmd <pid> JFR.start name=native settings=profile
   duration=300s filename=native.jfr`; inspect
   `jdk.DirectBufferStatistics`, `jdk.ObjectAllocationInNewTLAB`
   (heap alibi), `jdk.JavaExceptionThrow` (error-path leak trigger).
3. Heap (negative proof): `jcmd <pid> GC.heap_dump` — heap small;
   path-to-root shows few direct parents (already GC'd) while NMT
   still counts bytes (cleaner lag / unclosed arena).
4. Code forensics: grep `allocateDirect\|MemorySegment\|Arena\.of`
   without try-with-resources/finally; flag slice-retention and
   exception-path skips.
5. Repro: error-injection (5% corrupt images) on staging; direct
   count climbs only on error path pre-fix, flat post-fix.

## Root Cause
Manual lifecycle without scope discipline: per-request direct alloc
with no pool, FFM arena closed only on success, slices outliving
parents. Low-traffic periods starve the Cleaner, turning lag into OOM.

## Resolution
- Immediate: pool direct buffers (size classes + leak detector),
  wrap every arena in try-with-resources (close on exception), cap
  direct (`MaxDirectMemorySize`) + alert.
- Short-term: mmap thumbnails >1MB instead of direct-copy; fix
  slice contract (retain parent or copy); add NMT + direct dashboards.
- Long-term: ownership map per buffer type, leak-detector in CI soak,
  FFM-only rule (no Unsafe), RSS-based HPA + OOMKill runbook.

## Runbook
```
1. Capture NMT baseline/diff + JFR 300s + BufferPoolMXBean trend (don't just bump heap).
2. Deploy pool + arena-close fix to canary with error injection on.
3. Verify: direct count flat, NMT delta ~0, night-RSS flat 24h.
4. Roll 100%; drain zombie pods; replay failed thumbnails.
5. Set direct/RSS alerts + MaxDirectMemorySize guard.
6. Postmortem: ownership map + soak gate.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| RSS growth | +2.6GB/day | flat ±50MB | Alert +200MB/6h |
| Direct buffers | 48,000 | <300 | Alert >1k |
| Night OOMKills | 2–3 | 0 (30d) | Page on any |
| Render errors | 0.3% (use-after-free) | 0 | Slice-contract test |
| p99 render | 1.2s (GC/Cleaner stalls) | 0.3s | SLO |

## Prevention Checklist
- [ ] Every native alloc has named owner + close site
- [ ] Arenas/buffers in try-with-resources always
- [ ] NMT + direct dashboards + alerts
- [ ] Error-path leak test in CI (fault injection)

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- ByteBuffer / FFM (MemorySegment/Arena) API docs: https://docs.oracle.com/en/java/javase/21/docs/api/
- OpenJDK Panama project: https://openjdk.org/projects/panama/
