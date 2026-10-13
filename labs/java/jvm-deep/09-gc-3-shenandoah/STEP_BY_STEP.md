# Step by Step: Shenandoah GC

All steps run green on the Oracle build; nothing pretends to observe
Shenandoah where it is compiled out. Labels: [measured]/[JEP]/[reported].

1. Probe availability [measured]: `java -XX:+UseShenandoahGC -version`,
   capture exit code and "not supported" text. Assert exactly one of
   supported/refused holds (`supported != refused`). Record which branch
   your JVM takes.
2. Read the flag surface [measured]: `java -XX:+PrintFlagsFinal -version`,
   count rows containing `Shenandoah` with ` = ` (expect exactly 1:
   `UseShenandoahGC`), and rows matching G1 flags (expect >5). The ratio
   1-vs-many is the compiled-out evidence.
3. Run the pause-gap probe [measured]: identical churn (`ChurnXY`, 2000 x
   128 KB bounded) under default G1 and under `-XX:+UseZGC`, both at
   `-Xmx128m -Xlog:gc*`. Extract G1 evacuation milliseconds and ZGC
   handshake milliseconds with the dual regexes; assert both >0 and
   `zgc_max * 10 < g1_max`. This gap is the design goal Shenandoah chases
   from the Brooks direction [JEP].
4. Enumerate collector names [measured]: run the `WhoAmI` MXBean probe
   under default flags (expect `G1`) and under `-XX:+UseZGC` (expect
   `ZGC`). Note Shenandoah's pair (`Shenandoah Cycles`/`Pauses`) is
   [reported] via Micrometer, not printed here.
5. Confirm warmup universality [measured]: on the `ZChurn` probe at
   `-Xmx256m -Xlog:gc`, verify G1 young work at startup and ZGC's `Major
   Collection (Warmup)`. Shenandoah's own `Pause Init Mark` opens its
   cycles the same way on shipping builds [JEP].
6. (On Temurin/Semeru/RH only): re-run steps 1-2 and watch the branches
   flip — exit 0 with `Using Shenandoah`, full tuning surface present.
   The assertions hold with booleans flipped because each branch asserts
   its documented outcome.
7. Write the one-paragraph brief: Brooks word vs color bits, concurrent
   evacuation with root-sized pauses, single-gen default [JEP], Oracle
   builds omit it [measured].
