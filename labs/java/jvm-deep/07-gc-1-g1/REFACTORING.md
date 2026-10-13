# Refactoring: G1 GC

## Split humongous buffers out of the young churn

Before: a request path allocates 2 MB response arrays alongside 256 KB
scratch on a 1M-region heap. Every response claims two humongous regions;
mixed GCs cannot keep up and old-gen grows monotonically.

After: pool or reuse the 2 MB buffers (a bounded queue of direct or
heap buffers sized to peak concurrency), keep scratch allocation as-is.
Humongous allocation rate drops to near zero, young pauses reclaim the
scratch, and `gc+humongous=debug` goes quiet. The diff is one pool class
plus a borrow/return pair at the call site.

## Bound retention windows in caches

Before: `hold` grows unboundedly; every young pause promotes more live
bytes and the after-number climbs until mixed collections saturate.

After: cap the deque (`if (hold.size() > 40) hold.subList(0, 20).clear()`,
as the lab probe does) so live bytes plateau. Promotion rate stabilizes,
mixed phases finish their queues, and full GC stays absent. Retention
bounds are the cheapest GC tuning.

## Separate metadata churn from heap churn

Before: generated proxies or script compilations churn classes while the
heap churns objects; `Full GC` lines with metadata causes interleave with
evacuation pauses and confuse the diagnosis.

After: cache generated classes (one classloader per template, reused
Class instances) so metaspace pressure flattens. Heap logs then show pure
evacuation behavior and the two capacity planes stop masking each other.

## Size for the region rule

Before: 700 KB batches on 1M regions sit just above the 512 KB humongous
cutoff — every batch takes the humongous path by a small margin.

After: chunk to 256-384 KB so batches allocate in Eden and die young.
Crossing a region-derived cutoff by kilobytes is the most wasteful way to
be humongous; pick batch sizes against your measured region size.

## What not to refactor

Do not lower `MaxGCPauseMillis` to fix humongous fragmentation — smaller
young sets collect more often without reclaiming immovable regions. Do
not call `System.gc()` to "help" mixed collections; it routes to the
full GC you are trying to avoid.
