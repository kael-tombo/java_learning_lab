# Debugging: G1 GC

## Start with the init line

Run `-Xlog:gc+init` once per heap size and record `Heap Region Size`.
Every later judgment (is this object humongous? how many regions did
that pause cover?) divides by this number. Tags join with `+` — the
comma form `-Xlog:gc,init` prints nothing and has burned a full lab of
learners before you.

## Counting young pauses

Run the workload at `-Xmx256m -Xlog:gc` and count `Pause Young (Normal)
(G1 Evacuation Pause)` lines. Expect several under churn and zero `Full
GC` lines. Each line's `before->after(heap)` triple separates real growth
(after-number rising) from mere churn (after-number flat).

## Exposing humongous pressure

Default `gc` logging never names humongous allocations. Add
`gc+humongous=debug` and look around collections for `Humongous region`
entries with object size and `type array`. The lab's 2 MB arrays on 1M
regions each claim two contiguous entries — match the sizes to your
region legend before blaming anything else for old-gen growth.

## Marking and mixed phases

Past 45% occupancy expect `Pause Initial Mark` piggybacked on a young
pause, then concurrent marking lines, then `Pause Young (Mixed)` lines
with old-region participation. Missing mixed phases under old-gen
pressure plus rising evacuation times points at marking falling behind —
check `ConcGCThreads` ergonomics before touching the IHOP flag.

## Full GC forensics

A `Full GC` line in a healthy-looking log means one of three things:
humongous fragmentation, metaspace pressure, or an explicit `System.gc()`
without `ExplicitGCInvokesConcurrent`. Read the cause token on the line
itself; it names which of the three fired. Fix the cause, not the pause.

## MXBean cross-check

When logs and dashboards disagree, enumerate `MemoryPoolMXBeans` (`G1
Eden Space`, `G1 Old Gen`, `G1 Survivor Space`) and `GarbageCollectorMXBeans`
(`G1 Young Generation`, `G1 Concurrent GC`, `G1 Old Generation`) in-process.
Assert membership, never list position — pool order is unspecified.
