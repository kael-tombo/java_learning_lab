# README — G1 Garbage Collector

G1 divides the heap into equal regions and collects the garbage-richest
first. This lab measures that design on JDK 23 at pinned heap sizes.

## What you will observe [measured]

- `UseG1GC=true` ergonomic default, `MaxGCPauseMillis=200` goal,
  `InitiatingHeapOccupancyPercent=45` trigger — all read off the JVM.
- Region size follows heap/2048 clamped to 1-32 MB: 1M at `-Xmx256m`,
  4M at `-Xmx8g` in the reference runs.
- Allocation churn produces `Pause Young (Normal) (G1 Evacuation Pause)`
  lines with no full GC; young pauses measured 2-5 ms at 256 MB.
- 2 MB arrays on a 1M-region heap appear as humongous regions, visible
  only at `-Xlog:gc+humongous=debug` during a collection.
- MXBeans expose pools `G1 Eden Space`, `G1 Old Gen`, `G1 Survivor Space`
  and collectors `G1 Young Generation`, `G1 Concurrent GC`, `G1 Old Gen`.

## Cycle in one paragraph

Eden fills, young evacuation copies survivors (STW), past 45% occupancy
concurrent SATB marking runs, mixed collections evacuate the most
garbage-rich old regions alongside young ones, and full GC (parallel but
still STW) remains the last resort a healthy log never shows.

## Logging rule

Tag sets join with `+`: `-Xlog:gc+init`, `-Xlog:gc+humongous=debug`.
A comma-joined `-Xlog:gc,init` parses differently and prints nothing.

## Exit criteria

You can read a region size off `gc+init`, explain a young pause line,
state why humongous objects skip Eden, and treat the 200 ms pause value
as a goal rather than a guarantee.

## Numbers pocket reference

Defaults: `UseG1GC=true`, `MaxGCPauseMillis=200`, `IHOP=45`. Geometry:
heap/2048 clamped 1-32 MB (1M at 256m, 4M at 8g reference). Humongous:
>= half region, debug-level logging only. Young pauses: 2-5 ms measured
at 256 MB. Keep this card beside every G1 log you read.
