# Read-Mostly Index That Ignores Cache Sizes

Premise. A read-mostly in-memory index serves clients with unknown
caches - phones, laptops, servers - so tuning to one block size is
cheating. Van Emde Boas layout plus funnel-structured merging give
optimal cache behavior at every level without knowing B. The second
caller, a funnelsort batch job over log segments, proves the idea on
writes too.

Layout work. BST stored in vEB recursive layout: upper subtree then
lower subtrees contiguously, so any subtree of size ~B lands in O(1)
blocks. Search cost O(log_B n) memory transfers; the report demonstrates
it with cache-miss counters (perf stat or instrumented simulator) vs a
pointer-scattered tree at 1M keys.

Index caller. Point lookup plus range scan over 500k catalog rows; miss
counts and wall time compared against naive layout at three dataset
sizes. The gap should widen with size - that widening is the headline
chart.

Funnelsort caller. K-funnel merging of 64 sorted log runs into one;
merger depth chosen so base merges fit any cache. Output verified sorted
on 2M records; merge time compared against a binary-heap K-way merge.

Static discipline. Rebuilds are batched (log-structured deltas merged
periodically); point updates between rebuilds live in a small auxiliary
index with a stated merge cadence. Stale-read window documented.

Hostile shapes. Adversarial access order (stride prime to block size),
single-key hot loop (both layouts tie - reported honestly), tiny
dataset where layout barely matters (reported, not hidden).

Hand in. Layout converter, index, funnel job, miss-counter logs, charts
data. Marks: transfer analysis with counters 12, caller parity 10,
honest small-case reporting 8.
## Counter log
- Miss counts per dataset size.
- Small-case tie acknowledged.
- Merge cadence posted.
- Funnel depth choice recorded.
- Charts regenerated per release.
