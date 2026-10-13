# Architecture: G1 GC

## Heap as regions

The heap is a set of equal-sized regions (heap/2048, powers of two,
1-32 MB). Roles are fluid: any region can be Eden, Survivor, Old, or
Humongous at different times. There is no fixed young/old boundary as in
Parallel GC — the young set is a per-pause selection of regions sized to
fit the pause goal.

## Remembered sets

Each region owns a remembered set (a per-region PRT) recording which
other regions hold references into it. Cross-region writes go through a
barrier into refinement queues drained by concurrent refinement threads.
Evacuating one region then needs only its RSet plus roots, never a full
heap scan — RSet completeness is what makes partial collection sound.

## Collection stages

Young-only phase: Eden fills, `Pause Young (Normal) (G1 Evacuation
Pause)` copies live objects to Survivor/Old regions, entirely STW.
Concurrent marking past IHOP 45 uses SATB buffers to snapshot the graph.
Mixed phase replays young pauses with the most garbage-rich old regions
added (`Pause Young (Mixed)`). Full GC uses parallel workers but stops
the world throughout.

## Humongous path

Objects at or above half a region bypass Eden/Survivor and land in
contiguous humongous regions. They are never evacuated by young GC;
reclamation waits for concurrent cleanup or a full GC. A 2 MB array on a
1M-region heap therefore spans two humongous regions by construction.

## Control points

`MaxGCPauseMillis=200` shapes young-set sizing through a decay-averaged
pause model. `InitiatingHeapOccupancyPercent=45` starts marking.
`ConcGCThreads`/`ParallelGCThreads` size the concurrent and STW worker
pools ergonomically. `-Xmx` pins all of the above for reproducibility.

## Failure modes

Humongous churn fragments the heap faster than mixed GCs reclaim it.
To-space exhaustion aborts evacuation into a full GC. RSet coarsening
under extreme cross-region mutation inflates pause times.
