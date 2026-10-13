# References: JVM Tuning

Real sources only; all values measured on JDK 23 (16 GB / 8-CPU box).

- `java -XX:+PrintFlagsFinal -version` — primary source for
  `InitialHeapSize` (RAM/64), `MaxHeapSize` (RAM/4), `NewRatio=2`,
  `SurvivorRatio=8`, `TargetSurvivorRatio=50`, `TLABSize=0`,
  `MinTLABSize=2048`, `UseCompressedOops`/`UseCompressedClassPointers`,
  `ReservedCodeCacheSize=251658240`, `CompressedClassSpaceSize=1073741824`,
  `UseLargePages=false`, Metaspace sizing flags.
- `-Xlog:gc`, `-Xlog:gc*` and JFR (`jdk.GCHeapSummary`, allocation and
  compiler events) — the baseline/verify instruments behind the
  one-flag method; heap-size lever counted via `Pause Young (` lines.
- JEP 220: Modular Run-Time Images (JDK 9) — delivery context for the
  modern ergonomics era. JEP 248: G1 default (JDK 9) — why G1 adaptivity
  absorbs the heap lever that ParallelGC exposes.
- OpenJDK HotSpot source: `src/hotspot/share/gc/` (collector
  implementations), `src/hotspot/share/gc/shared/threadLocalAllocBuffer`
  (TLAB mechanics), `src/hotspot/share/memory/` (heap sizing, Metaspace),
  `src/hotspot/share/code/` (code cache).
- `java.lang.management.MemoryPoolMXBeans` (`Metaspace`, `CodeHeap*`,
  heap pools) and `com.sun.management.OperatingSystemMXBean`
  (`getTotalMemorySize` for the RAM side of the ergonomic ratios).
- OpenJDK HotSpot `src/hotspot/share/runtime/arguments.cpp`: the ergonomic
  derivation paths (RAM/64, RAM/4) and exact-override semantics behind the
  `HeapErgo` probe's ratio-plus-exactness assertions.
- JFR event reference (`jdk.GCHeapSummary`, `jdk.ThreadAllocationStatistics`,
  compiler events): the low-overhead baseline instruments the method step
  prescribes alongside `gc*` logs.
- `Runtime.getRuntime().maxMemory()` plus `MemoryMXBean.getHeapMemoryUsage()`:
  the in-process cross-checks for what the command line and flags claim —
  quote all three together when heap posture is disputed, never one alone.
