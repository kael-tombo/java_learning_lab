# Benchmark Proposal: Median Maintenance and Merge Patterns

Question. Which heap arrangement serves streaming median queries and
K-way merges cheapest at 1M events: the classic two-heap median rig,
and what merge fan-in minimizes the merge phase of an external sort.

Rig A - running median. Max-heap of the lower half plus min-heap of the
upper half, rebalanced so sizes differ by at most one. Insert O(log n),
median peek O(1). Median answers checked against a sorted-list oracle on
100k values including duplicates and negatives.

Rig B - K-way merge. Min-heap over run heads merging sorted runs into
one stream; cost O(N log K). Fan-ins 4, 16, and 64 compared on 1M total
elements across 64 pre-sorted runs. Output verified sorted and complete.

Rig C - top-K stream. Min-heap of size K over an unbounded event flow;
per-event cost O(log K). Compared against periodic full sort at 100k
events for K in {10, 100, 1000}, quoting both time and garbage produced.

Method. Seeds fixed and published; five warmup rounds; median of seven
timed rounds; identical streams per contender; GC pause log attached.
Heaps use array backing with documented growth policy.

Failure probes. Median rig fed monotonic input (balance stress), merge
fed runs of wildly uneven length (starvation check), top-K fed
all-equal keys (comparator tie handling). Each probe has an oracle.

Verdict format. A table of measured ops/s per rig with the Big-O claim
beside each row, plus a paragraph naming the workload where two heaps
lose to sorting outright. Marks: rig correctness 12, method control 10,
verdict candor 8.
## Reading list
- Two-heap median correctness proof.
- Fan-in cost derivation.
- GC pause interpretation guide.
- Keep all three cited, paged.
Ship the verdict table with every round attached.

