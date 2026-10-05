# REAL-WORLD PROJECT — Object Layout: False Sharing Halves Matching Engine

## Incident Scenario
Matching engine throughput halves after adding a "harmless" stats
counter next to the sequence cursor. CPU 100% on two cores, no locks
involved, profilers show "hot increment" — the counters share a cache
line and cores invalidate each other millions of times per second.

## Symptoms
- Throughput 1.2M → 550k msgs/s post-deploy; latency p99 8µs → 31µs;
  two cores at 100%, rest idle — coherence, not work.
- JOL post-hoc: `Sequencer { long cursor; long stats; }` = 16B header
  + 16B fields in one 64B line; `perf stat` cache-misses +9x.
- JMH on prod-shaped struct reproduces 2.2x collapse with 2 writers;
  single-thread numbers identical (sharing needs ≥2 writers).
- `List<Long>` tick buffer allocates 6.4GB/min (JFR TLAB top) + GC
  18% CPU — boxing compounds the line problem.
- Code review missed it: fields "look independent" at source level.

## Investigation Tasks
1. Layout: `ClassLayout.parseClass(Sequencer.class).toPrintable()`;
   map offsets → cache lines; confirm cursor+stats share line 0.
2. JFR: `jcmd <pid> JFR.start name=layout settings=profile
   duration=120s filename=layout.jfr`; rank
   `jdk.ObjectAllocationInNewTLAB` (boxing) + hot `increment` stacks.
3. CPU counters: async-profiler cpu + JMH `-prof perfnorm`
   (cache-misses, coherence); `Thread.print` shows spinning writers,
   no monitor contention (rules out locks).
4. Heap: `jcmd <pid> GC.heap_dump eng.hprof`; `GraphLayout` of
   `OrderBook` — boxed `Long` count × 24B vs `long` × 8B budget.
5. Repro: JMH adjacent-vs-padded pair on staging hardware; require
   2x+ delta to confirm diagnosis before patch.

## Root Cause
Cache-line sharing of independently-written hot fields plus boxed hot
data. Source-level independence ≠ hardware independence; the MESI
protocol serializes the line on every write.

## Resolution
- Immediate: pad/stripe (`@Contended` + `-XX:-RestrictContended` or
  manual pad), split stats to cold object; feature-flag the counter off.
- Short-term: `long[]`/primitive tick buffers, footprint asserts
  (JOL size test), perfnorm check in perf-sensitive CI.
- Long-term: cache-conscious design review for hot structs, layout
  lint (hot fields never adjacent without justification), quarterly
  footprint audit.

## Runbook
```
1. Capture JOL prints + JFR 120s + perfnorm/JMH pair BEFORE patch.
2. Flag off stats counter; verify throughput 550k -> ~1M (partial).
3. Deploy padded/striped + primitive-buffer patch to canary.
4. Verify: 1.2M+ msgs/s, p99 <10µs, misses -8x, alloc -70%.
5. Roll 100%; replay missed fills; reconcile book.
6. Land footprint + perfnorm gates.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| Throughput | 550k/s | 1.3M/s | Alert <1M/s |
| p99 | 31µs | 7µs | SLO 15µs |
| Cache-misses/op | 9x | 1x | perfnorm budget |
| Tick alloc | 6.4GB/min | 1.1GB/min | JFR alloc budget |
| GC CPU | 18% | 5% | Alert >10% |

## Prevention Checklist
- [ ] JOL footprint test on every hot struct
- [ ] No adjacent hot-write fields (review rule)
- [ ] Primitive-only hot buffers
- [ ] perfnorm/JMH gate on matching changes

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JOL (Java Object Layout) project: https://openjdk.org/projects/code-tools/jol/
- CompressedOops / compact headers docs: https://docs.oracle.com/en/java/javase/21/
