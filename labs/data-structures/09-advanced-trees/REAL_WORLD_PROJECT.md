# ADR-04: Balanced Index and Reservation Map

Context. The plain BST lab showed sorted ingest collapsing to chains.
The catalog needs an ordered index that survives adversarial order, and
the booking side needs an interval map for reservation windows.

Decision. Ship an AVL tree for the catalog index (strict balance, cheap
reads) with a red-black variant behind the same interface for comparison,
and a B-tree sketch for the disk note. Intervals ride an augmented
balanced map keyed by start with max-end augmentation.

Consequences for reads. Point lookup, range scan, floor/ceiling stay
O(log n) worst case on both variants; the report publishes height series
for random vs sorted ingest proving the bound holds where the BST fell.

Consequences for writes. Rotations counted per insert batch; AVL should
rotate more but stand shorter than red-black on update-heavy mixes. The
comparison workload (50/50 reads/writes, 200k keys) states which variant
wins reads and which wins writes with measured margins.

Interval duties. Insert window, delete window, query overlapping, find
free gap of length D. Overlap answers checked against a linear scan
oracle on 5k randomized windows; gap search checked by construction.

Alternatives rejected. Skip lists (covered in lab 14, cited not built);
plain BST with shuffle-only mitigation (rejected: input order is not
ours to control); database offload (rejected: this lab is the index).

Validation. Rotation audit (balance factors recomputed from scratch),
fuzz vs TreeMap with zero mismatches on 60k ops, crash-load of sorted
100k proving height stays logarithmic.

Marks: bound evidence on hostile order 12, variant comparison honesty
10, interval oracle parity 8.
## Follow-ups
- B-tree page math on real hardware.
- Delete-heavy comparison run.
- Interval stress at 50k windows.
- File results under adr-04.
