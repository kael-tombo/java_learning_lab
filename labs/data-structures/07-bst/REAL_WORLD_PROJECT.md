# Design: Catalog Range Index on a Plain BST

Goal. An ordered product index supporting point lookup, insertion,
deletion, and range scans, built first as an unbalanced BST so the
degeneration lessons are earned before balanced trees arrive.

Interface. put, get, delete, floor, ceiling, rank, select, range(lo,hi),
plus height and size. Delete handles all three cases (leaf, single
child, two children via successor swap) with a dedicated test per case.

Ordering core. The invariant is strict: left keys < node < right keys.
A checker walks the tree with min/max bounds after every 100th mutation
in test mode; any violation aborts the run with the offending key path.

Degeneration study. Three ingest orders (random, ascending, descending)
at 100k keys each. Random should hold height near a small multiple of
log2(n); sorted orders will chain toward O(n). The report publishes all
three height series and the resulting get-latency ratios.

Range scans. Implemented as bounded inorder with early exit; cost scales
with matches plus O(log n) descent on random data. Scans are verified
against a sorted ArrayList oracle on 2k random ranges.

Deletion audit. After each delete batch, inorder must still emit sorted
order and size must reconcile: size equals inserts minus deletes. A
fuzzer runs 30k mixed ops with the checker enabled and zero tolerance.

Known limits. Worst-case O(n) height on adversarial order is documented
with the measured collapse, and the handoff note names the balanced
successor (lab 09) with the rotation idea in one paragraph.

Ship. Index, fuzzer, height series, oracle logs, handoff note. Marks:
invariant enforcement 12, delete-case coverage 10, degeneration honesty
8.
## Handoff paragraph
- Sorted ingest chains; attach the plot.
- Next lab adds rotations.
- Keep the fuzzer seed list.
- Archive height series with dates.
