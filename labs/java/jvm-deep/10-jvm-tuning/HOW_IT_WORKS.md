# How It Works: JVM Tuning

You launch `java -XX:+PrintFlagsFinal -version` on the 16 GB box and read
`InitialHeapSize` 256M, `MaxHeapSize` 4G. Those are RAM/64 and RAM/4 —
ergonomics, not constants. Inside a 1 GB-limited container the same query
prints values derived from 1 GB, because the JDK reads cgroup limits
where detected. The lesson lands before any tuning: measure inside the
deployment, not on the laptop.

You add `-Xmx256m` and re-query: `MaxHeapSize` reads exactly 268,435,456.
Explicit beats ergonomic to the byte. Setting `-Xms` equal to `-Xmx`
(fixed heap) commits the full heap up front and removes resize pauses —
the standard latency posture, paid for in committed memory.

Allocation starts. Each thread carves a TLAB from Eden and bump-allocates
3M small nodes in ~35 ms. You flip `-XX:-UseTLAB` and re-run: ~250-315 ms
of atomic CAS contention on the shared Eden top. Same objects, same heap,
~8x apart — the structural price of sharing the allocation pointer.

Reference traffic flows compressed: 32-bit shifted offsets instead of
64-bit pointers, 12-byte headers instead of 16. The JIT fills the 240 MB
code cache; class metadata fills Metaspace (first GC trigger ~21M, no
upper cap, 1 GB compressed class space). A leak in either plane surfaces
as metadata/code pressure with its own graph — heap dumps never explain
it, pool readings do.

Finally you run the one-flag experiment: identical churn under ParallelGC
at `-Xmx128m` versus `-Xmx512m`, counting `Pause Young (` lines. The
smaller heap collects more often — Eden is a fixed young fraction, so
heap size directly sets time-between-pauses. Re-run under G1 and the
counts flatten: adaptive young-sizing absorbs the lever, which is itself
the finding about adaptivity.

Container awareness threads through all of it: the same binary reports
different ergonomics under different cgroup limits, so every reading in
this narrative (heap sizes, region counts, worker pools) is qualified by
where it was taken. The query travels; the numbers stay home.
