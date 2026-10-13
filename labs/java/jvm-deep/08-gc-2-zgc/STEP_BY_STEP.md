# Step by Step: ZGC

1. Confirm selection: `java -XX:+UseZGC -XX:+PrintFlagsFinal -version`,
   grep `UseZGC = true`, `ZGenerational = true`, `ZCollectionInterval = 0`.
2. Spawn a child JVM with `-XX:+UseZGC -Xmx256m` running the `ZBeans`
   probe; record collectors (`ZGC Minor/Major Cycles`, `ZGC Minor/Major
   Pauses`) and pools (`ZGC Young/Old Generation`), sorted before print.
3. Run the `ZChurn` probe (2000 x 128 KB, bounded retention) at
   `-XX:+UseZGC -Xmx128m -Xlog:gc+phases`. Extract `Pause ... ms` phase
   lines with a line-end-anchored regex; record max (reference
   0.010-0.026 ms) and assert all under 1 ms.
4. Verify the regex excludes cycle totals: any `0.009s`-style summary must
   not match, because seconds-scale spans are concurrent work, not pauses.
5. Re-run the same probe at `-Xlog:gc`. Confirm `Major Collection
   (Warmup)` appears once at startup and `Minor Collection` lines track
   churn with `(High Usage)` / `(Allocation Rate)` reasons.
6. Confirm occupancy deltas (`M(...)` figures) appear on the collection
   lines — reclamation evidence independent of pause evidence.
7. Run the `ZTimer` probe (600 ms sleep, zero allocation) with
   `-XX:ZCollectionInterval=0.1 -Xlog:gc`. Count `Major Collection
   (Timer)` lines; expect >= 2 in 600 ms (~120 ms spacing).
8. Re-run step 7 without the interval flag and confirm zero collections —
   the off-by-default control for the timer claim.
9. Write the one-paragraph distinction you will reuse: pauses are `Pause
   ... Xms` lines in tens of microseconds; cycle totals are concurrent
   spans in seconds; reasons in parentheses name triggers.
10. Negative control for tags: run once with `-Xlog:gc,phases` (comma) and
    record what the phase detail looks like when the separator is wrong —
    then restore `+` and note the difference as the muscle memory.
11. Record the `ZFragmentationLimit` default from the flag readout and
    state in one sentence what raising it would trade (eagerness to
    relocate against tolerance for fragmentation).
