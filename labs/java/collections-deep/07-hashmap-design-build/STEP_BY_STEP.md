# Step by Step: Probing by Hand

Table n=8 (mask 7). Spreads given as already-mixed indices.

1. `put(A→1)`, idx 1. Slot 1 empty → insert. `[., A, ., ., ., ., ., .]`
2. `put(B→2)`, idx 1. Slot 1 = A ≠ B → probe 2, empty → insert.
   Run forms: slots 1–2 occupied.
3. `put(C→3)`, idx 2. Slots 2 (B), 3 empty → insert at 3. Run 1–3.
4. `get(B)`: idx 1 → A, probe 2 → hit. 2 steps.
5. `remove(A)`: probe finds A at 1 → mark DELETED. `[., ✝, B, C, ...]`
6. `get(C)`: idx 2 → B, probe 3 → hit. Passes no tombstone here.
7. `get(B)`: idx 1 → DELETED (continue!) → 2 → hit. Deletion intact.
8. `put(D→4)`, idx 1. Probe: 1 is tombstone (remember), 2 = B, 3 = C,
   4 empty → insert D at first tombstone (slot 1). Reuse ✓.
   `[., D, B, C, ...]`, tombstones back to 0.
9. Watch the trigger: with cap 0.7, n=8 allows 5 live+tombstone. The 6th
   insert doubles to 16 and rehashes only live entries — runs dissolve
   because `h & 15` spreads wider than `h & 7`.

Failure drill: skip step 5's tombstone (null the slot instead) and `get(B)`
from idx 1 hits EMPTY at 1 → false miss. That single wrong null is the
entire reason tombstones exist.
## Bonus trace: resize at n=8, cap 0.7

Live: B@2, C@3, D@1, E@5, F@6 (5 entries, 0 tombstones). Trigger:
(5+0)/8 = 0.625 — insert G hashing to 2:

1. Probe 2 (B), 3 (C), 4 empty → insert G@4. Now 6/8 = 0.75 > 0.7.
2. `resize(16)`: fresh table, rehash each live key via `h & 15`.
   Suppose new indices: D@1, B@2, G@4, C@11, E@5, F@14 — the old run
   1–4 shatters because bit 3 of the hash now participates.
3. `size` recounted to 6, tombstones 0. Old table dropped as a whole.

Note what did NOT happen: no slot copied position-for-position, no
tombstone transferred, no spread re-applied to spread values.
