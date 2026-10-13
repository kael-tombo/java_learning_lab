# Common Mistakes: ZGC

## 1. Reading cycle totals as pauses

`0.009s` summaries span concurrent marking plus relocation; the pauses
are the `Pause ... 0.012ms` phase lines. Conflating them overstates pause
time by ~1000x. Anchor pause regexes to line-end `ms`.

## 2. Treating the warmup major as pressure

Every ZGC JVM opens with `Major Collection (Warmup)` — heap sizing and
metadata commissioning. Paging on the first major, or "fixing" it by
resizing, chases startup routine as if it were load signal.

## 3. Expecting G1 pool and collector names

ZGC registers its own MXBeans (`ZGC Minor/Major Cycles`, `ZGC Minor/Major
Pauses`, `ZGC Young/Old Generation`). Dashboards and alerts keyed on `G1
Eden Space` go blind silently. Enumerate beans per JVM (snippet 2).

## 4. Joining log tags with commas

`-Xlog:gc,phases` parses differently from `-Xlog:gc+phases` and drops the
phase detail the pause analysis needs. Join with `+`, always.

## 5. Running unpinned heaps

Young sizing and trigger points key off heap size; every snippet pins
`-Xmx` (128m/256m) so minors, majors, and timer spacing reproduce. An
unpinned experiment compares ergonomics, not collectors.

## 6. Assuming idle means collected

With the default `ZCollectionInterval=0`, an idle JVM collects nothing —
dead objects linger until pressure. Idle hygiene requires opting into the
timer; snippet 5 proves the off/on contrast on a 600 ms sleep.

## 7. Sizing ZGC like G1

Tight heaps that G1 tolerates (STW evacuation catches up in pauses)
starve ZGC's concurrent relocation and stall. Size for headroom: the
slack between allocation rate and concurrent drain is the capacity plan,
not minimal footprint.

## 8. Tuning the timer by feel instead of cadence

`ZCollectionInterval` spends one major per interval of concurrent work.
Pick it from the idle gap it must bridge (bursts every N seconds want an
interval well under N), not from round numbers — then confirm `Major
Collection (Timer)` spacing in the log matches the arithmetic.
