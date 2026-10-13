# Step by Step: G1 GC

1. Read the three defaults off your JVM: `java -XX:+PrintFlagsFinal
   -version`, grep `UseG1GC` (true), `MaxGCPauseMillis` (200),
   `InitiatingHeapOccupancyPercent` (45).
2. Compile the `RSize` probe and run it twice: `-Xmx256m -Xlog:gc+init`
   and `-Xmx8g -Xlog:gc+init`. Record each `Heap Region Size` line.
3. Verify the sizes satisfy heap/2048 clamped to powers of two in 1-32 MB
   (expect 1M and a multi-MB value; reference saw 1M and 4M).
4. Run the churn probe (`Churn`, 300 x 256 KB with bounded retention) at
   `-Xmx256m -Xlog:gc`. Count `Pause Young (Normal) (G1 Evacuation Pause)`
   lines; confirm at least two and zero `Full GC` lines.
5. Note one pause's `before->after(heap)` numbers and its millisecond
   reading (reference range 2-5 ms at this heap).
6. Run the `Huge` probe (20 x 2 MB retained) at `-Xmx256m
   -Xlog:gc+humongous=debug`. Confirm `Humongous region` lines with `type
   array` appear only around collections.
7. Re-run step 6 at default info logging (`-Xlog:gc`) and confirm the
   humongous lines vanish — the visibility lesson.
8. Run the `G1Pools` MXBean probe with no flags. Confirm pools `G1 Eden
   Space`, `G1 Old Gen`, `G1 Survivor Space` and collectors `G1 Young
   Generation`, `G1 Concurrent GC`, `G1 Old Generation`.
9. Deliberately mistype the tag separator (`-Xlog:gc,init`) once and watch
   the region line disappear — then never join tags with commas again.
10. Write down the pause-target sentence: "200 ms is a goal shaping young
    sizing, not a guarantee; per-pause readings are ground truth."
11. Force the mixed-phase path once: grow retained bytes past 45% of the
    pinned heap and confirm `Pause Initial Mark` plus subsequent `Pause
    Young (Mixed)` lines appear — the full young-to-mixed arc on demand.
12. Record the worker lines from the init log (`ParallelGCThreads`,
    `ConcGCThreads`, `Concurrent Refinement Workers`) beside your region
    sizes; these move with CPU count and explain pause differences across
    machines running identical heaps.
