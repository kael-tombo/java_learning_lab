# References: Shenandoah GC

Real sources only. Behavior claims are [JEP]/[reported]; negative
availability is [measured] on Oracle JDK 23.

- `java -XX:+UseShenandoahGC -version` (support probe) and `java
  -XX:+PrintFlagsFinal -version` (flag-surface count: exactly one
  `Shenandoah*` row surviving) — primary evidence for compiled-out status
  [measured].
- JEP 189: Shenandoah, a Pauseless GC Algorithm (experimental, JDK 12).
  JEP 379: Shenandoah Production (JDK 15). JEP 404: Generational
  Shenandoah (experimental, 24). JEP 521: Generational Shenandoah
  productization (ongoing; single-gen default) [JEP].
- JEP 220: Modular Run-Time Images (JDK 9) — timeline context only.
- OpenJDK HotSpot source (Temurin/Semeru/RH builds that ship it):
  `src/hotspot/share/gc/shenandoah/` (Brooks barriers, forwarder CAS,
  SATB marking, pacing, heuristics, uncommit) [JEP].
- OpenJDK wiki Shenandoah logs (8 GB reference: init-mark ~1 ms,
  final-mark ~10 ms figures cited as reference, not measured here) [JEP].
- Micrometer `JvmGcMetrics` collector table mapping `"Shenandoah Cycles"`
  and `"... Pauses"` MXBean names [reported].
- Lab 08's ZGC probes (`ZBeans`, pause-gap dual regexes) as the portable
  comparison harness [measured]: G1-vs-concurrent gap ~5 ms vs ~0.02 ms.
- OpenJDK HotSpot `src/hotspot/share/gc/shared/satbMarkQueue.hpp`: the
  SATB buffer mechanics shared with G1, behind the floating-garbage
  one-cycle retention both collectors exhibit [JEP].
- JEP 189's contrast quote in full context plus the PPPJ2016 algorithm
  paper reference: the primary-source chain from paper to experimental
  integration to production [JEP].
- GC log tag reference (`-Xlog:help`) and JFR GC events: the instruments
  behind every portable probe in this lab, valid on Oracle builds where
  Shenandoah phases themselves are absent [measured].
