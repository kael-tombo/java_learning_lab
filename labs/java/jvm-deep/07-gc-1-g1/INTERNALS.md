# Internals: G1 GC

## Region sizing rule

`G1HeapRegionSize` is ergonomic: heap/2048 rounded to a power of two,
clamped to 1-32 MB. The two measured points (1M at 256m, 4M at 8g) both
satisfy the rule. Every threshold that keys off regions — humongous
half-region cutoff, young-set region counts — derives from this one
number, so pin `-Xmx` before reasoning.

## Humongous threshold

Half a region, inclusive. On 1M regions any object >= 512 KB is
humongous; the lab's 2 MB arrays each span two contiguous regions. They
are logged (object size, `type array`) only at `gc+humongous=debug`
during a collection — info-level logging stays silent, which misleads
anyone who greps default logs for the cause of old-gen growth.

## SATB mechanics

Snapshot-at-the-beginning: reference overwrites during concurrent marking
push the old value into a per-thread SATB buffer via the pre-write
barrier. Buffers drain as extra marking roots. Deletions therefore keep
dead objects marked (floating garbage, one cycle of retention); no live
object is ever reclaimed. Correctness over precision, one cycle of lag.

## Remembered sets and refinement

Post-write barriers log cross-region stores into dirty-card queues.
Concurrent refinement threads (visible as `Concurrent Refinement Workers`
in the init log) drain queues into per-region PRTs. Evacuation scans a
region's PRT entries as roots. If mutation outruns refinement, PRTs
coarsen (fewer, larger entries) and pauses grow — the back-pressure path.

## Pause model

Each young set is sized from a decay-averaged history of per-region
evacuation costs against `MaxGCPauseMillis=200`. The flag never vetoes a
needed pause: allocation spikes, humongous allocation, or to-space
exhaustion all blow past it, and the per-pause `Xms` readings are the
ground truth, not the flag value.

## Full GC position

Full GC exists as a parallel-workers, fully-STW fallback for
fragmentation, metaspace pressure, or forced `System.gc()`. Its absence
from a healthy log is the success signal snippet 3 asserts.
