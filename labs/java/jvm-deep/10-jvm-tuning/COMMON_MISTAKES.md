# Common Mistakes: JVM Tuning

## 1. Quoting ergonomics from memory

RAM/64 and RAM/4 hold as equations, but absolutes (256M/4G) belong to the
16 GB reference box. Containers re-derive from cgroup limits. Snippet 1
asserts ratios with tolerance plus `-Xmx` exactness — copy that pattern,
not anyone's megabytes.

## 2. Disabling TLABs outside diagnosis

`-XX:-UseTLAB` costs ~8x allocation throughput for zero production
benefit (measured ~35 vs ~250-315 ms). It is a measurement instrument for
proving contention exists, switched back on immediately after. Leaving it
off "to reduce variance" manufactures the variance it claims to study.

## 3. Treating CodeCache/Metaspace as heap

Separate planes, separate pools, separate fixes (snippet 4 asserts
Metaspace plus CodeHeap pools alongside the compression flags). Raising
`-Xmx` for a metadata leak or a compilation cliff wastes memory and hides
the real graph.

## 4. Changing two flags per experiment

Two changes confound attribution — snippet 5 changes heap size only and
prints "one variable changed: true" as the honesty label. Re-run rather
than reinterpret when tempted to bundle.

## 5. Enabling large pages without OS support

`UseLargePages=false` default; the flag alone on an unconfigured OS is
silently inert (or fails fast by version). Verify hugetlbfs/THP pools and
privilege first, then set the flag, then re-measure TLB-sensitive
throughput — in that order.

## 6. Sizing young by feel

Ratios have measured defaults (NewRatio 2, SurvivorRatio 8,
TargetSurvivorRatio 50) with observable consequences (snippet 2 plus the
pause-count probe). Read flags, compute the geometry in megabytes, run
churn, count pauses — feel never enters the procedure.

## 7. Carrying numbers across collectors

Heap-size lever that moves ParallelGC pause counts reads flat under G1
(adaptivity absorbs it) and meaningless under ZGC (no fixed young). Every
tuning claim names its collector; the same flag is a different experiment
per collector.
