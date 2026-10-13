# Exercises: ZGC

Runnable tasks with exact flags. Pin heaps; join tags with `+`.

## 1. Prove the opt-in

```bash
java -XX:+UseZGC -XX:+PrintFlagsFinal -version | grep -E "UseZGC|ZGenerational|ZCollectionInterval"
```

Expect `UseZGC = true`, `ZGenerational = true`,
`ZCollectionInterval = 0`. Re-run without `-XX:+UseZGC` and confirm the
first flag reads false while the other two still print their defaults.

## 2. Name the generational surface

```bash
javac ZBeans.java && java -XX:+UseZGC -Xmx256m -cp . ZBeans
```

Using the lab's `ZBeans` probe (lists collectors and `ZGC*` pools
sorted): assert minor+major Cycles and Pauses collectors plus young+old
pools. Then point the same probe at a default (G1) JVM and record how
every name differs.

## 3. Measure the sub-millisecond bar

```bash
javac ZChurn.java && java -XX:+UseZGC -Xmx128m -Xlog:gc+phases -cp . ZChurn
```

Extract `Pause ... (\d+\.\d+)ms` at line end; assert at least one pause
and max < 1.0 ms (reference 0.010-0.026 ms). Deliberately also match the
unanchored pattern once to see cycle totals pollute the sample — then
restore the anchor.

## 4. Read the reasons

```bash
java -XX:+UseZGC -Xmx128m -Xlog:gc -cp . ZChurn
```

Find `Major Collection (Warmup)` exactly once at startup, `Minor
Collection` with `(High Usage)` / `(Allocation Rate)` under churn, and
`M(...)` occupancy deltas. Write one sentence per line class: what
triggered it and what it reclaimed.

## 5. Collect an idle JVM on the timer

```bash
javac ZTimer.java && java -XX:+UseZGC -Xmx256m -XX:ZCollectionInterval=0.1 -Xlog:gc -cp . ZTimer
```

Count `Major Collection (Timer)` over the 600 ms sleep (expect >= 2,
~120 ms spacing). Re-run without the interval flag; expect zero. State
the production corollary: which of your idle services wants this flag,
and at what interval in seconds rather than 0.1.

## 6. Compare a G1 pause line

```bash
java -Xmx128m -Xlog:gc* -cp . ChurnXY
```

Run the shared churn under default G1, extract the `G1 Evacuation Pause`
milliseconds, and place them beside the ZGC maxima from exercise 3.
Assert the order-of-magnitude gap holds (10x bar) on your machine.
