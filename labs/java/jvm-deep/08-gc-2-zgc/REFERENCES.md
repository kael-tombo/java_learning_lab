# References: ZGC

Real sources only; flag values measured on JDK 23 in this lab.

- `java -XX:+UseZGC -XX:+PrintFlagsFinal -version` — primary source for
  `UseZGC` (opt-in), `ZGenerational=true` default, `ZCollectionInterval=0.0`
  default, `ZFragmentationLimit`, and the per-generation interval flags.
- `-Xlog:gc`, `-Xlog:gc+phases` — the two log views behind every pause and
  reason claim; tags join with `+`.
- JEP 333: ZGC, a Scalable Low-Latency Garbage Collector (Experimental,
  JDK 11). JEP 377: ZGC Production (JDK 15). JEP 439: Generational ZGC
  (JDK 21).
- JEP 220: Modular Run-Time Images (JDK 9) — timeline context only.
- OpenJDK HotSpot source: `src/hotspot/share/gc/z/` (colored pointers,
  load barriers, minor/major cycle routing, phase handshakes).
- `java.lang.management.GarbageCollectorMXBean` / `MemoryPoolMXBean` —
  source of `ZGC Minor/Major Cycles`, `ZGC Minor/Major Pauses`, `ZGC Young
  Generation`, `ZGC Old Generation` asserted in snippet 2.
- JEP 333, JEP 377, JEP 439 texts (openjdk.org): the authoritative
  statements of experimental scope, production status, and generational
  routing — quote these, not secondary summaries, for status claims.
- OpenJDK HotSpot `src/hotspot/share/gc/z/zCollectionWatcher` and phase
  accounting: the source of the Cycles/Pauses bean split and the
  `gc+phases` line shapes this lab parses.
- Lab 07's `RegionSize` probe as the negative template: G1's region
  geometry versus ZGC's size-independent handshakes is the comparison
  every capacity argument in this lab rests on.
- JFR `jdk.ZAllocationStall` and `jdk.ZPageAllocation` events: the
  structured stall/headroom signals behind the capacity guidance here —
  alert on these, not on pause charts that stay flat until stalls begin.
- `-XX:ZCollectionIntervalMajor/Minor/Only` flag references: the
  per-generation timer refinements for splitting idle hygiene between
  minors and majors once the base interval proves its worth.
