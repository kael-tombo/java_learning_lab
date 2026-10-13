# References: G1 GC

Real sources only; defaults verified on JDK 23 in this lab.

- `java -XX:+PrintFlagsFinal -version` — primary source for `UseG1GC=true`
  (ergonomic), `MaxGCPauseMillis=200`, `InitiatingHeapOccupancyPercent=45`,
  `G1HeapRegionSize` ergonomics, `ConcGCThreads`/`ParallelGCThreads`.
- `-Xlog:gc+init`, `-Xlog:gc`, `-Xlog:gc+humongous=debug` — the three log
  views used by every snippet; tag sets join with `+`, never commas.
- JEP 248: Make G1 the Default Garbage Collector (JDK 9).
- JEP 220: Modular Run-Time Images (JDK 9) — release-train context only.
- OpenJDK HotSpot source: `src/hotspot/share/gc/g1/` (regions, RSets,
  SATB barriers, evacuation, concurrent marking), including
  `g1CollectedHeap`, `heapRegion`, `g1RemSet`, and SATB queue files.
- `java.lang.management.MemoryPoolMXBean` / `GarbageCollectorMXBean` —
  source of pool names `G1 Eden Space`, `G1 Old Gen`, `G1 Survivor Space`
  and collectors `G1 Young Generation`, `G1 Concurrent GC`,
  `G1 Old Generation` asserted in snippet 5.
- OpenJDK HotSpot `src/hotspot/share/gc/g1/g1CollectedHeap.cpp` and
  `g1ConcurrentMark.cpp`: evacuation-pause entry points and the SATB
  marking implementation behind the phase names in the logs.
- OpenJDK HotSpot `src/hotspot/share/gc/g1/heapRegion.hpp`: region roles
  (Eden/Survivor/Old/Humongous) and the half-region humongous cutoff.
- JEP 220: Modular Run-Time Images (JDK 9) — release-train context for
  the JDK 9 default switch, sharing a version number but no mechanism.
- GC log tag reference (`-Xlog:help` output on your build): the
  authoritative list of selectable tags and levels behind every `+`-joined
  selection in this lab — consult it before composing new selections.
- JFR `jdk.G1HeapRegionInformation` and `jdk.G1GarbageCollection` events:
  the structured counterparts to the text lines counted here, suited to
  fleet-wide pause and region analytics.
- `-Xlog:gc+refinement=debug` on staging: the refinement-thread backlog
  signal behind RSet-coarsening pauses — consult it when evacuation times
  grow while copied bytes stay flat.
