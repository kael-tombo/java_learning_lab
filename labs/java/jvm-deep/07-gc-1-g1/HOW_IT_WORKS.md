# How It Works: G1 GC

The JVM starts and the `gc+init` log prints `Heap Region Size`: 1M for a
256 MB heap, 4M for an 8 GB heap. Every allocation lands in an Eden
region; each thread's TLAB absorbs the fast path without locking.

Eden fills. The JVM stops all application threads and runs `Pause Young
(Normal) (G1 Evacuation Pause)`: live objects copy to Survivor regions
(or age into Old), dead ones vanish where they stand, and the log prints
a `23M->9M(256M)`-style before/after line. Pauses here measured 2-5 ms.

The application resumes. Young pauses repeat, survivors age, and once
heap occupancy passes 45% (`InitiatingHeapOccupancyPercent`), the next
young pause doubles as `Pause Initial Mark`: roots are captured, then
concurrent threads mark the graph while the application runs. Reference
stores during marking append to SATB buffers so the snapshot stays
consistent; objects that die mid-marking float as garbage until the next
cycle rather than being missed as live.

Marking completes with remark and cleanup pauses. G1 now knows which old
regions hold the most garbage, and subsequent pauses become `Pause Young
(Mixed)`: the young set plus a few garbage-rich old regions evacuate
together, a few per cycle until reclaimed.

A 2 MB array allocated on 1M regions never enters this flow: it exceeds
half a region, so the allocator places it directly into two contiguous
humongous regions, where no young evacuation will touch it. Only
concurrent cleanup (or, failing that, a parallel-but-STW full GC)
reclaims it — which is why humongous churn is the classic G1 pathology.

Mixed collections then repeat the young-pause shape with old regions
attached (`Pause Young (Mixed)`), a few garbage-rich regions per cycle
until the marked set drains. Throughout, the young-set size adapts per
pause history against the 200 ms goal — the same churn can produce
different region counts on different runs, and that variance is the pause
model working, not nondeterminism to suppress.
