# REAL-WORLD PROJECT — JVM Internals: Checkout p99 Spikes + Mysterious OOMs

## Incident Scenario
Checkout API p99 jumps 200ms -> 2.5s every 40 min, then one pod OOMs nightly
at 03:00 during the promo-batch overlap. Autoscaling adds pods but p99 stays
bad; heap dumps are 4GB and nobody opens them.

## Symptoms
- GC log: Full GC / evacuation pauses aligning with p99 spikes.
- `java.lang.OutOfMemoryError: Java heap space` at 03:00 only.
- CPU sawtooth; `Old Gen` grows monotonically between spikes.
- Restart "fixes" it for 40 min; traffic flat, so not load-driven.

## Investigation Tasks
1. Live capture (no restart first): `jcmd <pid> JFR.start duration=300s
   filename=spike.jfr settings=profile`, plus
   `jcmd <pid> GC.heap_info` and `jcmd <pid> Thread.print`.
2. GC analysis: `-Xlog:gc*` around a spike; correlate `jdk.GarbageCollection`
   pause events with p99 chart; note pause type (Young/Mixed/Full).
3. Heap: `jcmd <pid> GC.heap_dump /tmp/spike.hprof`; dominator tree —
   suspect batch cache (`PromoCache`) pinning `Order` graph.
4. Allocation: JFR `jdk.ObjectAllocationInNewTLAB` + `jdk.ObjectAllocationOutsideTLAB`;
   top allocator stack should point at batch importer creating garbage.
5. JIT/threads: `jdk.Compilation` failures/deopts; `Thread.print` for blocked
   batch threads holding locks during STW-sensitive window.
6. Flags/config: `jcmd <pid> VM.flags` + `VM.command_line`; check `-Xmx`,
   `MaxRAMPercentage`, G1 heap vs container limit mismatch.
7. Repro: replay 03:00 batch on staging with same flags; watch Old Gen slope.

## Root Cause
Promo batch caches full `Order` entities in an unbounded static map (leak)
while generating TLAB churn; undersized heap + ParallelGC on latency path
turns promotion failures into Full GCs; container limit lower than `-Xmx`
triggers OOM-kill pressure at overlap.

## Resolution
- Immediate: bound cache (Caffeine TTL + max-size), disable 03:00 overlap
  (stagger batch), roll `-XX:MaxRAMPercentage=70 + UseG1GC` canary.
- Short-term: batch streams instead of materializing lists; weak keys or
  explicit eviction; `-XX:+HeapDumpOnOutOfMemoryError` + JFR always-on.
- Long-term: leak-detection in CI (Old-Gen slope assert), allocation budget,
  GC-pause SLO alerts, heap-sizing runbook per service.

## Runbook
```
1. Do NOT restart first: JFR 5 min + heap_dump + Thread.print + VM.flags.
2. Ship dump/JFR off-box; check GC log for Full vs Mixed pauses.
3. Bound/disable leaky cache; stagger batch; canary new flags.
4. Verify Old-Gen flat + p99 back; promote fleet-wide.
5. Land pause/leak alerts + sizing doc.
```

## Metrics
- p99 back <= 250ms sustained 24h; Full GCs = 0; Mixed pauses < 100ms.
- Old Gen flat (±5%) over 6h; OOMs = 0 over 7 nights.
- JFR alloc from batch path down >= 70%.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- jcmd man page: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html
- JFR (JEP 328): https://openjdk.org/jeps/328
