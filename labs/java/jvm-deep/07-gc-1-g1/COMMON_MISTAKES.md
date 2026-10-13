# Common Mistakes: G1 GC

## 1. Joining log tags with commas

`-Xlog:gc,init` is not the init log; `-Xlog:gc+init` is. The comma form
parses as a different tag expression and yields silence. Every snippet
pins the `+` form because this mistake costs an hour the first time.

## 2. Treating 200 ms as a guarantee

`MaxGCPauseMillis=200` shapes young-set sizing through a pause model; it
never vetoes a needed collection. Allocation spikes and to-space
exhaustion blow past it. The per-pause `Xms` readings are ground truth.

## 3. Expecting humongous lines at info level

Humongous allocation is silent under `-Xlog:gc`. Visibility needs
`gc+humongous=debug` during a collection. Absence of humongous lines at
default logging proves nothing about humongous pressure.

## 4. Reading region size off documentation

Region size is heap-derived (heap/2048, 1-32 MB powers of two), not a
constant. A 256 MB heap and an 8 GB heap in this lab measured 1M and 4M.
Read `gc+init` on your heap; do not quote anyone else's number.

## 5. Running experiments without -Xmx

Region size, worker counts, and IHOP thresholds all key off heap size.
Unpinned runs pick ergonomics from whatever the machine offers that day
and do not reproduce. Every snippet pins `-Xmx` for this reason.

## 6. Asserting pool-list position

`getMemoryPoolMXBeans()` order is unspecified VM trivia. Snippet 5 sorts
and filters before asserting membership (`G1 Eden Space`, `G1 Old Gen`,
`G1 Survivor Space`). Position assertions flake across builds.

## 7. Celebrating a full GC as activity

A `Full GC` line in G1 is a fallback (fragmentation, metaspace, explicit
`System.gc()`), never routine progress. The healthy churn probe asserts
`!fullGc` — the absence is the success signal.

## 8. Sizing heaps from pause wishes instead of pause readings

Lowering `MaxGCPauseMillis` below what the live set affords shrinks young
sets without shrinking copied bytes — more pauses, same work, less
throughput. Size from the per-pause `Xms` history first; set the goal to
what the history says is reachable, not what the SLO wishes were true.
