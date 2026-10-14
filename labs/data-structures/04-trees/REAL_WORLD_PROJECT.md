# Benchmark Proposal: Catalog Index on BST Traversals

Hypothesis. For a 200k-item product catalog that fits in memory, an
in-house BST index serves point lookups and range scans competitively
with TreeMap while teaching exactly where balance matters.

Contenders. Entrant A: iterative BST with parent pointers and inorder
successor links. Entrant B: java.util.TreeMap as the red-black oracle.
Both sit behind one index interface (put, get, delete, range, size,
height) so the harness swaps them with a flag.

Workloads. W1: 100k inserts in random order, then 50k point gets. W2:
sorted-order inserts of 50k (the degeneration probe). W3: 5k range scans
of width 100 spread across the key space. W4: mixed 40/40/20 get/put/
range at 200k resident keys.

Traversal duties. Inorder must emit sorted keys; preorder, postorder, and
level-order feed the structural audit. Height after random inserts should
sit near log2(n); after sorted inserts the audit must show the collapse
and the harness must report the slowdown factor honestly.

Measures. Per-op nanos by workload, range-scan cost vs width, memory per
entry from heap deltas, rotation-free height series, and mismatch count
vs the oracle (must be zero on shared workloads).

Controls. Fixed seed list published in the repo; five warmup rounds;
median of five timed rounds; identical key streams for both entrants;
GC log attached so pauses cannot hide inside averages.

Risks. Sorted ingest degenerates the entrant to O(n) chains; the report
must show it, not hide it, and state the balance remedy per follow-up
lab. Duplicate keys need a documented policy (last-write-wins).

Deliver. Harness, seed files, result tables, height plots data, and a
verdict paragraph: where the plain BST holds up and the key order that
breaks it. Marks: method rigor 12, oracle parity 10, degeneration
analysis 8.
## Rehearsal checklist
- Draw the 15-key tree by hand first.
- Predict heights before running.
- Keep TreeMap output diffs.
